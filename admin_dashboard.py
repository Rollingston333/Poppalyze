#!/usr/bin/env python3
"""
Admin Dashboard for Gap Screener
Provides comprehensive monitoring, tracking, and issue management
"""

import os
import sys
import json
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import logging
from collections import defaultdict, Counter
import threading
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('admin.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get('ADMIN_SECRET_KEY', 'admin-secret-key-change-in-production')

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Simple user management (in production, use proper database)
class AdminUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return AdminUser(user_id)

# Configuration
CACHE_FILE = "stock_cache.json"
SCANNER_PID_FILE = "background_scanner.pid"
MAIN_APP_PORT = 5002  # Updated to match streamlined app
ADMIN_PORT = 5003     # Changed to avoid conflict

# Traffic Analytics Database
TRAFFIC_DB = "traffic_analytics.db"

class TrafficAnalytics:
    def __init__(self):
        self.db_path = TRAFFIC_DB
        self.init_database()
        self.session_data = {}
        self.lock = threading.Lock()
    
    def init_database(self):
        """Initialize the traffic analytics database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create visitors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    ip_address TEXT,
                    user_agent TEXT,
                    first_visit TIMESTAMP,
                    last_visit TIMESTAMP,
                    visit_count INTEGER DEFAULT 1,
                    total_duration INTEGER DEFAULT 0
                )
            ''')
            
            # Create page_views table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS page_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    page_url TEXT,
                    timestamp TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT,
                    response_time REAL
                )
            ''')
            
            # Create api_calls table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint TEXT,
                    method TEXT,
                    timestamp TIMESTAMP,
                    ip_address TEXT,
                    response_time REAL,
                    status_code INTEGER
                )
            ''')
            
            # Create daily_stats table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE,
                    total_visitors INTEGER DEFAULT 0,
                    unique_visitors INTEGER DEFAULT 0,
                    total_page_views INTEGER DEFAULT 0,
                    total_api_calls INTEGER DEFAULT 0,
                    avg_session_duration REAL DEFAULT 0
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Traffic analytics database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing traffic database: {e}")
    
    def track_visitor(self, request):
        """Track a new visitor or update existing visitor"""
        try:
            session_id = request.cookies.get('session_id') or self.generate_session_id()
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            current_time = datetime.now()
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if visitor exists
                cursor.execute('''
                    SELECT id, visit_count, first_visit FROM visitors 
                    WHERE session_id = ? OR ip_address = ?
                ''', (session_id, ip_address))
                
                result = cursor.fetchone()
                
                if result:
                    # Update existing visitor
                    visitor_id, visit_count, first_visit = result
                    cursor.execute('''
                        UPDATE visitors 
                        SET last_visit = ?, visit_count = visit_count + 1
                        WHERE id = ?
                    ''', (current_time, visitor_id))
                else:
                    # Create new visitor
                    cursor.execute('''
                        INSERT INTO visitors (session_id, ip_address, user_agent, first_visit, last_visit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (session_id, ip_address, user_agent, current_time, current_time))
                
                conn.commit()
                conn.close()
                
                return session_id
                
        except Exception as e:
            logger.error(f"Error tracking visitor: {e}")
            return None
    
    def track_page_view(self, request, response_time=0.0):
        """Track a page view"""
        try:
            session_id = request.cookies.get('session_id')
            if not session_id:
                return
            
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            referrer = request.headers.get('Referer', '')
            current_time = datetime.now()
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO page_views (session_id, page_url, timestamp, ip_address, user_agent, referrer, response_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, request.path, current_time, ip_address, user_agent, referrer, response_time))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
    
    def track_api_call(self, request, response_time=0.0, status_code=200):
        """Track an API call"""
        try:
            ip_address = request.remote_addr
            current_time = datetime.now()
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO api_calls (endpoint, method, timestamp, ip_address, response_time, status_code)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (request.path, request.method, current_time, ip_address, response_time, status_code))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")
    
    def get_traffic_stats(self, days=7):
        """Get comprehensive traffic statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Exclude localhost and local network IPs
            excluded_ips = ['127.0.0.1', 'localhost', '::1', '192.168.1.88']
            excluded_ips_placeholders = ','.join(['?' for _ in excluded_ips])
            
            # Total visitors (excluding local IPs)
            cursor.execute(f'''
                SELECT COUNT(*) FROM visitors 
                WHERE first_visit >= ? 
                AND ip_address NOT IN ({excluded_ips_placeholders})
            ''', [start_date] + excluded_ips)
            total_visitors = cursor.fetchone()[0]
            
            # Unique visitors today (excluding local IPs)
            today = datetime.now().date()
            cursor.execute(f'''
                SELECT COUNT(DISTINCT pv.session_id) FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE DATE(pv.timestamp) = ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [today] + excluded_ips)
            unique_visitors_today = cursor.fetchone()[0]
            
            # Total page views today (excluding local IPs)
            cursor.execute(f'''
                SELECT COUNT(*) FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE DATE(pv.timestamp) = ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [today] + excluded_ips)
            page_views_today = cursor.fetchone()[0]
            
            # Total API calls today (excluding local IPs)
            cursor.execute(f'''
                SELECT COUNT(*) FROM api_calls ac
                JOIN visitors v ON ac.session_id = v.session_id
                WHERE DATE(ac.timestamp) = ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [today] + excluded_ips)
            api_calls_today = cursor.fetchone()[0]
            
            # Page views by day (last 7 days) - excluding local IPs
            cursor.execute(f'''
                SELECT DATE(pv.timestamp) as date, COUNT(*) as count
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY DATE(pv.timestamp)
                ORDER BY date DESC
            ''', [start_date] + excluded_ips)
            daily_page_views = dict(cursor.fetchall())
            
            # API calls by day (last 7 days) - excluding local IPs
            cursor.execute(f'''
                SELECT DATE(ac.timestamp) as date, COUNT(*) as count
                FROM api_calls ac
                JOIN visitors v ON ac.session_id = v.session_id
                WHERE ac.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY DATE(ac.timestamp)
                ORDER BY date DESC
            ''', [start_date] + excluded_ips)
            daily_api_calls = dict(cursor.fetchall())
            
            # Top pages (excluding local IPs)
            cursor.execute(f'''
                SELECT pv.page_url, COUNT(*) as count
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY pv.page_url
                ORDER BY count DESC
                LIMIT 10
            ''', [start_date] + excluded_ips)
            top_pages = cursor.fetchall()
            
            # Top API endpoints (excluding local IPs)
            cursor.execute(f'''
                SELECT ac.endpoint, COUNT(*) as count
                FROM api_calls ac
                JOIN visitors v ON ac.session_id = v.session_id
                WHERE ac.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY ac.endpoint
                ORDER BY count DESC
                LIMIT 10
            ''', [start_date] + excluded_ips)
            top_endpoints = cursor.fetchall()
            
            # Visitor locations (by IP) - excluding local IPs
            cursor.execute(f'''
                SELECT ip_address, COUNT(*) as count
                FROM visitors 
                WHERE first_visit >= ? 
                AND ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY ip_address
                ORDER BY count DESC
                LIMIT 10
            ''', [start_date] + excluded_ips)
            top_ips = cursor.fetchall()
            
            # Average session duration (excluding local IPs)
            cursor.execute(f'''
                SELECT AVG(visit_count) as avg_visits
                FROM visitors 
                WHERE first_visit >= ? 
                AND ip_address NOT IN ({excluded_ips_placeholders})
            ''', [start_date] + excluded_ips)
            avg_visits = cursor.fetchone()[0] or 0
            
            # Recent activity (last 24 hours) - excluding local IPs
            yesterday = datetime.now() - timedelta(days=1)
            cursor.execute(f'''
                SELECT COUNT(*) FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [yesterday] + excluded_ips)
            recent_activity = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_visitors': total_visitors,
                'unique_visitors_today': unique_visitors_today,
                'page_views_today': page_views_today,
                'api_calls_today': api_calls_today,
                'daily_page_views': daily_page_views,
                'daily_api_calls': daily_api_calls,
                'top_pages': top_pages,
                'top_endpoints': top_endpoints,
                'top_ips': top_ips,
                'avg_visits': round(avg_visits, 2),
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            logger.error(f"Error getting traffic stats: {e}")
            return {}
    
    def get_real_time_stats(self):
        """Get real-time traffic statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Exclude localhost and local network IPs
            excluded_ips = ['127.0.0.1', 'localhost', '::1', '192.168.1.88']
            excluded_ips_placeholders = ','.join(['?' for _ in excluded_ips])
            
            # Active sessions (last 30 minutes) - excluding local IPs
            active_threshold = datetime.now() - timedelta(minutes=30)
            cursor.execute(f'''
                SELECT COUNT(DISTINCT pv.session_id) FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [active_threshold] + excluded_ips)
            active_sessions = cursor.fetchone()[0]
            
            # Page views in last hour - excluding local IPs
            hour_ago = datetime.now() - timedelta(hours=1)
            cursor.execute(f'''
                SELECT COUNT(*) FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [hour_ago] + excluded_ips)
            page_views_hour = cursor.fetchone()[0]
            
            # API calls in last hour - excluding local IPs
            cursor.execute(f'''
                SELECT COUNT(*) FROM api_calls ac
                JOIN visitors v ON ac.session_id = v.session_id
                WHERE ac.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [hour_ago] + excluded_ips)
            api_calls_hour = cursor.fetchone()[0]
            
            # Current online users (last 5 minutes) - excluding local IPs
            online_threshold = datetime.now() - timedelta(minutes=5)
            cursor.execute(f'''
                SELECT COUNT(DISTINCT pv.session_id) FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.timestamp >= ? 
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', [online_threshold] + excluded_ips)
            online_users = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'active_sessions': active_sessions,
                'page_views_hour': page_views_hour,
                'api_calls_hour': api_calls_hour,
                'online_users': online_users
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time stats: {e}")
            return {}
    
    def generate_session_id(self):
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4())

class AdminMonitor:
    def __init__(self):
        self.cache_file = CACHE_FILE
        self.scanner_pid_file = SCANNER_PID_FILE
        self.traffic_analytics = TrafficAnalytics()
        
    def get_system_status(self):
        """Get overall system status"""
        try:
            # CPU and Memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process status
            main_app_running = self.is_port_in_use(MAIN_APP_PORT)
            scanner_running = self.is_scanner_running()
            
            # Cache status
            cache_status = self.get_cache_status()
            
            # Traffic stats
            traffic_stats = self.traffic_analytics.get_traffic_stats()
            real_time_stats = self.traffic_analytics.get_real_time_stats()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': round(memory.available / (1024**3), 2),
                    'disk_percent': disk.percent,
                    'disk_free_gb': round(disk.free / (1024**3), 2)
                },
                'services': {
                    'main_app': {
                        'running': main_app_running,
                        'port': MAIN_APP_PORT,
                        'url': f'http://localhost:{MAIN_APP_PORT}'
                    },
                    'background_scanner': {
                        'running': scanner_running,
                        'pid_file': self.scanner_pid_file
                    }
                },
                'cache': cache_status,
                'traffic': traffic_stats,
                'real_time': real_time_stats,
                'overall_status': 'healthy' if main_app_running and scanner_running else 'warning'
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
    
    def is_port_in_use(self, port):
        """Check if port is in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def is_scanner_running(self):
        """Check if background scanner is running"""
        try:
            if os.path.exists(self.scanner_pid_file):
                with open(self.scanner_pid_file, 'r') as f:
                    pid = int(f.read().strip())
                return psutil.pid_exists(pid)
            return False
        except:
            return False
    
    def get_cache_status(self):
        """Get cache file status"""
        try:
            if not os.path.exists(self.cache_file):
                return {
                    'exists': False,
                    'age_minutes': None,
                    'stock_count': 0,
                    'status': 'missing'
                }
            
            # Get file stats
            stat = os.stat(self.cache_file)
            age_seconds = time.time() - stat.st_mtime
            age_minutes = age_seconds / 60
            
            # Read cache content
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
            
            stock_count = len(data.get('stocks', {}))
            
            # Determine status
            if age_minutes < 5:
                status = 'fresh'
            elif age_minutes < 30:
                status = 'stale'
            else:
                status = 'old'
            
            return {
                'exists': True,
                'age_minutes': round(age_minutes, 1),
                'stock_count': stock_count,
                'status': status,
                'size_mb': round(stat.st_size / (1024**2), 2)
            }
        except Exception as e:
            logger.error(f"Error getting cache status: {e}")
            return {'error': str(e)}
    
    def get_process_info(self):
        """Get detailed process information"""
        try:
            processes = []
            
            # Find Python processes related to our app
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'app.py' in cmdline or 'background_scanner.py' in cmdline:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline[:100] + '...' if len(cmdline) > 100 else cmdline,
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'status': proc.status()
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
        except Exception as e:
            logger.error(f"Error getting process info: {e}")
            return []
    
    def get_log_entries(self, log_file='production.log', lines=50):
        """Get recent log entries"""
        try:
            if not os.path.exists(log_file):
                return []
            
            with open(log_file, 'r') as f:
                lines_list = f.readlines()
            
            # Get last N lines
            recent_lines = lines_list[-lines:] if len(lines_list) > lines else lines_list
            
            # Parse log entries
            log_entries = []
            for line in recent_lines:
                try:
                    # Simple log parsing (adjust based on your log format)
                    if ' - ' in line:
                        parts = line.split(' - ', 2)
                        if len(parts) >= 3:
                            timestamp = parts[0]
                            level = parts[1]
                            message = parts[2].strip()
                            
                            log_entries.append({
                                'timestamp': timestamp,
                                'level': level,
                                'message': message
                            })
                except:
                    continue
            
            return log_entries[::-1]  # Reverse to show newest first
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            return []
    
    def restart_service(self, service_name):
        """Restart a specific service"""
        try:
            if service_name == 'main_app':
                # Kill existing app processes
                subprocess.run(['pkill', '-f', 'python.*app.py'], capture_output=True)
                time.sleep(2)
                
                # Start new app process
                subprocess.Popen(['python3', 'app.py'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
                
            elif service_name == 'background_scanner':
                # Kill existing scanner processes
                subprocess.run(['pkill', '-f', 'python.*background_scanner.py'], capture_output=True)
                time.sleep(2)
                
                # Start new scanner process
                subprocess.Popen(['python3', 'background_scanner.py'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
            
            return {'success': True, 'message': f'{service_name} restarted successfully'}
        except Exception as e:
            logger.error(f"Error restarting {service_name}: {e}")
            return {'success': False, 'error': str(e)}
    
    def clear_cache(self):
        """Clear the cache file"""
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
                return {'success': True, 'message': 'Cache cleared successfully'}
            else:
                return {'success': True, 'message': 'Cache file not found'}
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return {'success': False, 'error': str(e)}

# Initialize monitor
monitor = AdminMonitor()

# Middleware to track all requests
@app.before_request
def track_request():
    """Track all incoming requests"""
    if request.path.startswith('/admin'):
        # Track admin dashboard requests
        monitor.traffic_analytics.track_visitor(request)
        monitor.traffic_analytics.track_page_view(request)
    else:
        # Track API calls
        monitor.traffic_analytics.track_api_call(request)

# Routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Main admin dashboard"""
    return render_template('admin_dashboard.html')

@app.route('/admin/traffic')
@login_required
def traffic_dashboard():
    """Traffic analytics dashboard"""
    return render_template('traffic_dashboard.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in production, use proper auth)
        if username == 'admin' and password == 'admin123':
            user = AdminUser(username)
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    """Admin logout"""
    logout_user()
    return redirect(url_for('admin_login'))

@app.route('/admin/api/status')
@login_required
def api_status():
    """API endpoint for system status"""
    return jsonify(monitor.get_system_status())

@app.route('/admin/api/traffic')
@login_required
def api_traffic():
    """API endpoint for traffic statistics"""
    days = request.args.get('days', 7, type=int)
    return jsonify(monitor.traffic_analytics.get_traffic_stats(days))

@app.route('/admin/api/traffic/realtime')
@login_required
def api_traffic_realtime():
    """API endpoint for real-time traffic statistics"""
    return jsonify(monitor.traffic_analytics.get_real_time_stats())

@app.route('/admin/api/processes')
@login_required
def api_processes():
    """API endpoint for process information"""
    return jsonify(monitor.get_process_info())

@app.route('/admin/api/logs')
@login_required
def api_logs():
    """API endpoint for log entries"""
    lines = request.args.get('lines', 50, type=int)
    log_file = request.args.get('file', 'production.log')
    return jsonify(monitor.get_log_entries(log_file, lines))

@app.route('/admin/api/restart/<service>', methods=['POST'])
@login_required
def api_restart_service(service):
    """API endpoint to restart services"""
    if service in ['main_app', 'background_scanner']:
        result = monitor.restart_service(service)
        return jsonify(result)
    else:
        return jsonify({'success': False, 'error': 'Invalid service'})

@app.route('/admin/api/clear-cache', methods=['POST'])
@login_required
def api_clear_cache():
    """API endpoint to clear cache"""
    result = monitor.clear_cache()
    return jsonify(result)

@app.route('/admin/health')
def admin_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'admin_dashboard': True
    })

if __name__ == '__main__':
    print("🔧 Starting Admin Dashboard...")
    print(f"🌐 Admin Dashboard: http://localhost:{ADMIN_PORT}/admin")
    print(f"📊 Traffic Dashboard: http://localhost:{ADMIN_PORT}/admin/traffic")
    print(f"🔑 Default credentials: admin / admin123")
    print("🛑 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=ADMIN_PORT) 