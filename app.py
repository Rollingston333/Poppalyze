from flask import Flask, render_template, request, jsonify
import json
import time
import os
import subprocess
import threading
import signal
import sys
import sqlite3
import uuid
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dotenv import load_dotenv
from cache_manager import cache_manager

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
CACHE_FILE = "stock_cache.json"
background_scanner_process = None
SCANNER_PID_FILE = "background_scanner.pid"
TRAFFIC_DB = "traffic_analytics.db"

# =====================================================
# TRAFFIC ANALYTICS
# =====================================================

class TrafficAnalytics:
    def __init__(self, db_path=TRAFFIC_DB):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the traffic analytics database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
                        visit_count INTEGER DEFAULT 1
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
                        referrer TEXT
                    )
                ''')
                
                # Create api_calls table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        endpoint TEXT,
                        timestamp TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT
                    )
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"⚠️  Error initializing traffic database: {e}")
    
    def track_visitor(self, session_id, ip_address, user_agent):
        """Track a visitor session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                # Check if session exists
                cursor.execute('SELECT visit_count, last_visit FROM visitors WHERE session_id = ?', (session_id,))
                result = cursor.fetchone()
                
                if result:
                    # Update existing session
                    visit_count = result[0] + 1
                    cursor.execute('''
                        UPDATE visitors 
                        SET visit_count = ?, last_visit = ? 
                        WHERE session_id = ?
                    ''', (visit_count, now, session_id))
                else:
                    # Create new session
                    cursor.execute('''
                        INSERT INTO visitors (session_id, ip_address, user_agent, first_visit, last_visit)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (session_id, ip_address, user_agent, now, now))
                
                conn.commit()
        except Exception as e:
            print(f"⚠️  Error tracking visitor: {e}")
    
    def track_page_view(self, session_id, page_url, ip_address, user_agent, referrer=None):
        """Track a page view"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                cursor.execute('''
                    INSERT INTO page_views (session_id, page_url, timestamp, ip_address, user_agent, referrer)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (session_id, page_url, now, ip_address, user_agent, referrer))
                
                conn.commit()
        except Exception as e:
            print(f"⚠️  Error tracking page view: {e}")
    
    def track_api_call(self, session_id, endpoint, ip_address, user_agent):
        """Track an API call"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                cursor.execute('''
                    INSERT INTO api_calls (session_id, endpoint, timestamp, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?)
                ''', (session_id, endpoint, now, ip_address, user_agent))
                
                conn.commit()
        except Exception as e:
            print(f"⚠️  Error tracking API call: {e}")
    
    def get_traffic_stats(self, days=1):
        """Get traffic statistics for the specified number of days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_date = datetime.now() - timedelta(days=days)
                
                # Get page views today
                cursor.execute('''
                    SELECT COUNT(*) FROM page_views 
                    WHERE timestamp >= ?
                ''', (cutoff_date,))
                page_views_today = cursor.fetchone()[0]
                
                # Get API calls today
                cursor.execute('''
                    SELECT COUNT(*) FROM api_calls 
                    WHERE timestamp >= ?
                ''', (cutoff_date,))
                api_calls_today = cursor.fetchone()[0]
                
                # Get unique visitors today
                cursor.execute('''
                    SELECT COUNT(DISTINCT session_id) FROM page_views 
                    WHERE timestamp >= ?
                ''', (cutoff_date,))
                unique_visitors_today = cursor.fetchone()[0]
                
                # Get average visits per visitor
                cursor.execute('''
                    SELECT AVG(visit_count) FROM visitors 
                    WHERE last_visit >= ?
                ''', (cutoff_date,))
                avg_visits = cursor.fetchone()[0] or 0
                
                # Get daily page views for chart
                cursor.execute('''
                    SELECT DATE(timestamp), COUNT(*) 
                    FROM page_views 
                    WHERE timestamp >= ?
                    GROUP BY DATE(timestamp)
                    ORDER BY DATE(timestamp)
                ''', (cutoff_date,))
                daily_page_views = dict(cursor.fetchall())
                
                # Get top pages
                cursor.execute('''
                    SELECT page_url, COUNT(*) 
                    FROM page_views 
                    WHERE timestamp >= ?
                    GROUP BY page_url 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                ''', (cutoff_date,))
                top_pages = cursor.fetchall()
                
                # Get top IPs
                cursor.execute('''
                    SELECT ip_address, COUNT(*) 
                    FROM page_views 
                    WHERE timestamp >= ?
                    GROUP BY ip_address 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                ''', (cutoff_date,))
                top_ips = cursor.fetchall()
                
                # Get top API endpoints
                cursor.execute('''
                    SELECT endpoint, COUNT(*) 
                    FROM api_calls 
                    WHERE timestamp >= ?
                    GROUP BY endpoint 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                ''', (cutoff_date,))
                top_endpoints = cursor.fetchall()
                
                return {
                    'page_views_today': page_views_today,
                    'api_calls_today': api_calls_today,
                    'unique_visitors_today': unique_visitors_today,
                    'avg_visits': round(avg_visits, 1),
                    'daily_page_views': daily_page_views,
                    'top_pages': top_pages,
                    'top_ips': top_ips,
                    'top_endpoints': top_endpoints
                }
        except Exception as e:
            print(f"⚠️  Error getting traffic stats: {e}")
            return {}
    
    def get_real_time_stats(self):
        """Get real-time traffic statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                now = datetime.now()
                
                # Online users (last 5 minutes)
                online_cutoff = now - timedelta(minutes=5)
                cursor.execute('''
                    SELECT COUNT(DISTINCT session_id) FROM page_views 
                    WHERE timestamp >= ?
                ''', (online_cutoff,))
                online_users = cursor.fetchone()[0]
                
                # Active sessions (last 30 minutes)
                active_cutoff = now - timedelta(minutes=30)
                cursor.execute('''
                    SELECT COUNT(DISTINCT session_id) FROM page_views 
                    WHERE timestamp >= ?
                ''', (active_cutoff,))
                active_sessions = cursor.fetchone()[0]
                
                # Page views in last hour
                hour_cutoff = now - timedelta(hours=1)
                cursor.execute('''
                    SELECT COUNT(*) FROM page_views 
                    WHERE timestamp >= ?
                ''', (hour_cutoff,))
                page_views_hour = cursor.fetchone()[0]
                
                # API calls in last hour
                cursor.execute('''
                    SELECT COUNT(*) FROM api_calls 
                    WHERE timestamp >= ?
                ''', (hour_cutoff,))
                api_calls_hour = cursor.fetchone()[0]
                
                return {
                    'online_users': online_users,
                    'active_sessions': active_sessions,
                    'page_views_hour': page_views_hour,
                    'api_calls_hour': api_calls_hour
                }
        except Exception as e:
            print(f"⚠️  Error getting real-time stats: {e}")
            return {}
    
    def generate_session_id(self):
        """Generate a unique session ID"""
        return str(uuid.uuid4())

# Initialize traffic analytics
traffic_analytics = TrafficAnalytics()

# =====================================================
# REQUEST TRACKING MIDDLEWARE
# =====================================================

@app.before_request
def track_request():
    """Track all incoming requests for analytics"""
    try:
        # Skip tracking for static files and admin dashboard
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return
        
        # Get or create session ID
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = traffic_analytics.generate_session_id()
        
        # Get request details
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        referrer = request.headers.get('Referer')
        
        # Track visitor
        traffic_analytics.track_visitor(session_id, ip_address, user_agent)
        
        # Track page view or API call
        if request.path.startswith('/api/'):
            traffic_analytics.track_api_call(session_id, request.path, ip_address, user_agent)
        else:
            traffic_analytics.track_page_view(session_id, request.path, ip_address, user_agent, referrer)
        
        # Store session ID in request context for later use
        request.session_id = session_id
            
    except Exception as e:
        print(f"⚠️  Error tracking request: {e}")

@app.after_request
def add_session_cookie(response):
    """Add session cookie after response is generated"""
    try:
        if hasattr(request, 'session_id') and not request.cookies.get('session_id'):
            response.set_cookie('session_id', request.session_id, max_age=86400)  # 24 hours
    except Exception as e:
        print(f"⚠️  Error adding session cookie: {e}")
    return response

# =====================================================
# BACKGROUND SCANNER MANAGEMENT
# =====================================================

def is_scanner_running():
    """Check if background scanner is already running using PID file"""
    if os.path.exists(SCANNER_PID_FILE):
        try:
            with open(SCANNER_PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                return True
            except OSError:
                # Process doesn't exist, clean up stale PID file
                os.remove(SCANNER_PID_FILE)
                return False
        except (ValueError, IOError):
            # Invalid PID file, remove it
            os.remove(SCANNER_PID_FILE)
            return False
    return False

def cleanup_stale_scanners():
    """Kill any existing background scanner processes"""
    try:
        # Kill any existing background scanner processes
        result = subprocess.run(['pkill', '-f', 'background_scanner.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🧹 Cleaned up existing background scanner processes")
        
        # Remove stale PID file if it exists
        if os.path.exists(SCANNER_PID_FILE):
            os.remove(SCANNER_PID_FILE)
            print("🧹 Removed stale PID file")
            
    except Exception as e:
        print(f"⚠️  Warning: Could not cleanup stale scanners: {e}")

def start_background_scanner():
    """Start the background scanner process with singleton protection"""
    global background_scanner_process
    
    try:
        # First, cleanup any stale processes
        cleanup_stale_scanners()
        
        # Check if background scanner is already running
        if is_scanner_running():
            print("🔄 Background scanner already running (detected via PID file)")
            return True
        
        if background_scanner_process and background_scanner_process.poll() is None:
            print("🔄 Background scanner already running (detected via process)")
            return True
        
        print("🚀 Starting background scanner...")
        
        # Start the background scanner process
        background_scanner_process = subprocess.Popen(
            [sys.executable, 'background_scanner.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(3)
        
        if background_scanner_process.poll() is None:
            print("✅ Background scanner started successfully")
            return True
        else:
            print("❌ Failed to start background scanner")
            return False
            
    except Exception as e:
        print(f"❌ Error starting background scanner: {e}")
        return False

def stop_background_scanner():
    """Stop the background scanner process"""
    global background_scanner_process
    
    print("🛑 Stopping background scanner...")
    
    # Stop the managed process
    if background_scanner_process and background_scanner_process.poll() is None:
        background_scanner_process.terminate()
        try:
            background_scanner_process.wait(timeout=5)
            print("✅ Background scanner stopped")
        except subprocess.TimeoutExpired:
            background_scanner_process.kill()
            print("⚠️  Force killed background scanner")
        background_scanner_process = None
    
    # Also kill any other background scanner processes
    try:
        result = subprocess.run(['pkill', '-f', 'background_scanner.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("🧹 Killed additional background scanner processes")
    except Exception as e:
        print(f"⚠️  Warning: Could not kill additional processes: {e}")
    
    # Clean up PID file
    if os.path.exists(SCANNER_PID_FILE):
        os.remove(SCANNER_PID_FILE)
        print("🧹 Removed PID file")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down...")
    stop_background_scanner()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# =====================================================
# INPUT VALIDATION & ERROR HANDLING
# =====================================================

def validate_numeric_input(value, param_name, min_val=None, max_val=None, default=None):
    """Validate and convert numeric input with proper error handling"""
    if not value or value.strip() == '':
        return default
    
    try:
        numeric_value = float(value)
        
        if min_val is not None and numeric_value < min_val:
            raise ValueError(f"{param_name} must be >= {min_val}")
        
        if max_val is not None and numeric_value > max_val:
            raise ValueError(f"{param_name} must be <= {max_val}")
            
        return numeric_value
        
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(f"{param_name} must be a valid number")
        raise e

def validate_filters(request_args):
    """Validate all filter parameters and return sanitized values"""
    try:
        filters = {
            'min_price': validate_numeric_input(request_args.get('min_price', '0.01'), 'Min Price', 0.01, 10000, 0.01),
            'max_price': validate_numeric_input(request_args.get('max_price', '1000'), 'Max Price', 0.01, 100000, 1000),
            'min_gap_pct': validate_numeric_input(request_args.get('min_gap_pct', '-100'), 'Min Gap %', -1000, 1000, -100),
            'min_rel_vol': validate_numeric_input(request_args.get('min_rel_vol', '0'), 'Min Relative Volume', 0, 1000, 0),
            'max_float': validate_numeric_input(request_args.get('max_float', ''), 'Max Float', 0, 1e12),
            'min_market_cap': validate_numeric_input(request_args.get('min_market_cap', ''), 'Min Market Cap', 0, 1e15),
            'max_market_cap': validate_numeric_input(request_args.get('max_market_cap', ''), 'Max Market Cap', 0, 1e15),
            'min_pe_ratio': validate_numeric_input(request_args.get('min_pe_ratio', ''), 'Min P/E Ratio', -1000, 1000),
            'max_pe_ratio': validate_numeric_input(request_args.get('max_pe_ratio', ''), 'Max P/E Ratio', -1000, 1000),
            'min_premarket_volume': validate_numeric_input(request_args.get('min_premarket_volume', ''), 'Min Premarket Volume', 0, 1e12),
        }
        
        # Validate sector filter
        valid_sectors = ['All', 'Technology', 'Healthcare', 'Financial', 'Energy', 'Consumer', 'Industrial', 'Materials', 'Utilities', 'Real Estate', 'Communication']
        sector = request_args.get('sector_filter', 'All')
        if sector not in valid_sectors:
            filters['sector_filter'] = 'All'
        else:
            filters['sector_filter'] = sector
            
        # Logical validation
        if filters['min_price'] > filters['max_price']:
            raise ValueError("Min Price cannot be greater than Max Price")
            
        if filters['min_market_cap'] and filters['max_market_cap'] and filters['min_market_cap'] > filters['max_market_cap']:
            raise ValueError("Min Market Cap cannot be greater than Max Market Cap")
            
        return filters, None
        
    except ValueError as e:
        return None, str(e)

@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return render_template('screener.html',
                          stocks=[], 
                          error="Bad request: Invalid parameters provided",
                          market_info=get_default_market_info(),
                          cache_info={'successful_count': 0, 'total_count': 0, 'last_update': 'Never', 'is_fresh': False},
                          cache_status={'status': 'Error', 'message': 'Bad request', 'age_minutes': 0, 'is_fresh': False},
                          filters={'min_price': 1.0, 'max_price': 100.0, 'min_gap_pct': 0.0, 'min_rel_vol': 0.0, 'max_float': '', 'sector_filter': 'All'}), 400

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return render_template('screener.html',
                          stocks=[], 
                          error="Internal server error: Please try again later",
                          market_info=get_default_market_info(),
                          cache_info={'successful_count': 0, 'total_count': 0, 'last_update': 'Never', 'is_fresh': False},
                          cache_status={'status': 'Error', 'message': 'Server error', 'age_minutes': 0, 'is_fresh': False},
                          filters={'min_price': 1.0, 'max_price': 100.0, 'min_gap_pct': 0.0, 'min_rel_vol': 0.0, 'max_float': '', 'sector_filter': 'All'}), 500

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def safe_float(value, default):
    """Safely convert value to float, return default if conversion fails"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def format_volume(volume):
    """Format volume numbers to human-readable format (K, M, B)"""
    try:
        if not volume or volume == 0:
            return "0"
        
        volume = float(volume)
        
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.1f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        else:
            return f"{int(volume)}"
    except (ValueError, TypeError):
        return "—"

def format_time_ago(seconds):
    """Format seconds into human-readable time ago string"""
    if seconds < 60:
        return f"{int(seconds)}s ago"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    else:
        hours = int(seconds / 3600)
        return f"{hours}h ago"

def get_default_market_info():
    """Get default market info when no cache is available"""
    return {
        'session': 'UNKNOWN',
        'current_time_et': 'Unknown',
        'market_open': '9:30 ET',
        'market_close': '16:00 ET',
        'is_trading_day': True
    }

def get_unique_sectors(stocks_data):
    """Get list of unique sectors from stocks data"""
    sectors = set()
    for stock_data in stocks_data.values():
        category = stock_data.get('category', 'Other')
        if category and category != '—':
            sectors.add(category)
    return sorted(list(sectors))

def filter_cached_stocks(stocks_data, min_price=1, max_price=20, min_rel_vol=None, max_float=None, min_gap_pct=None, require_news=False, sector_filter=None, min_pre_market=None, max_pre_market=None, min_post_market=None, max_post_market=None, min_market_cap=None, max_market_cap=None, min_pe_ratio=None, max_pe_ratio=None, min_pre_market_change=None, max_pre_market_change=None, min_post_market_change=None, max_post_market_change=None, min_premarket_volume=None):
    """Apply filters to cached stock data"""
    results = []
    
    for symbol, stock_data in stocks_data.items():
        try:
            current = stock_data.get('price', 0)
            pre_market_price = stock_data.get('pre_market_price', 0)
            post_market_price = stock_data.get('post_market_price', 0)
            float_shares = stock_data.get('float_shares_raw', 0)
            rel_vol = stock_data.get('relative_volume', 0)  # Fixed: use relative_volume instead of rel_vol
            gap_pct = stock_data.get('gap_pct', 0)
            has_news = stock_data.get('has_news', False)
            category = stock_data.get('category', 'Other')
            market_state = stock_data.get('market_state', 'UNKNOWN')
            market_cap = stock_data.get('market_cap', 0)
            pe_ratio = stock_data.get('pe_ratio')
            pre_market_change_pct = stock_data.get('pre_market_change_pct')
            post_market_change_pct = stock_data.get('post_market_change_pct')
            volume = stock_data.get('volume', 0)
            
            # Basic validation - stock must have a price
            if not current or current <= 0:
                continue
                
            # Price filters (current price)
            if current < min_price or current > max_price:
                continue
                
            # Pre-market price filters - only apply if values are provided
            if min_pre_market and pre_market_price and pre_market_price < float(min_pre_market):
                continue
            if max_pre_market and pre_market_price and pre_market_price > float(max_pre_market):
                continue
                
            # After-market price filters - only apply if values are provided
            if min_post_market and post_market_price and post_market_price < float(min_post_market):
                continue
            if max_post_market and post_market_price and post_market_price > float(max_post_market):
                continue
            
            # Market cap filters - only apply if values are provided
            if min_market_cap and market_cap and market_cap < float(min_market_cap):
                continue
            if max_market_cap and market_cap and market_cap > float(max_market_cap):
                continue
                
            # PE ratio filters - only apply if values are provided
            if min_pe_ratio and pe_ratio and pe_ratio < float(min_pe_ratio):
                continue
            if max_pe_ratio and pe_ratio and pe_ratio > float(max_pe_ratio):
                continue
                
            # Pre-market change percentage filters
            if min_pre_market_change and pre_market_change_pct and pre_market_change_pct < float(min_pre_market_change):
                continue
            if max_pre_market_change and pre_market_change_pct and pre_market_change_pct > float(max_pre_market_change):
                continue
                
            # Post-market change percentage filters
            if min_post_market_change and post_market_change_pct and post_market_change_pct < float(min_post_market_change):
                continue
            if max_post_market_change and post_market_change_pct and post_market_change_pct > float(max_post_market_change):
                continue
                
            # Pre-market volume filter
            if min_premarket_volume and volume and volume < float(min_premarket_volume):
                continue
            
            # Relative volume filter
            if min_rel_vol and rel_vol < min_rel_vol:
                continue
                
            # Float filter - only apply if value is provided
            if max_float and float_shares and float_shares > (float(max_float) * 1000000):
                continue
            
            # Gap percentage filter - FIXED: Only apply minimum when meaningful
            if min_gap_pct is not None and min_gap_pct > 0 and abs(gap_pct) < min_gap_pct:
                continue
                
            # News filter
            if require_news and not has_news:
                continue
                
            # Category filter
            if sector_filter and sector_filter != 'All' and category != sector_filter:
                continue
            
            # Format the data for display
            results.append({
                'symbol': symbol,
                'price': float(current),
                'price_display': f"${current:.2f}",
                'pre_market_price': float(pre_market_price) if pre_market_price else 0,
                'pre_market_price_display': f"${pre_market_price:.2f}" if pre_market_price else '—',
                'post_market_price': float(post_market_price) if post_market_price else 0,
                'post_market_price_display': f"${post_market_price:.2f}" if post_market_price else '—',
                'pre_market_change_pct': float(pre_market_change_pct) if pre_market_change_pct else None,
                'post_market_change_pct': float(post_market_change_pct) if post_market_change_pct else None,
                'market_state': market_state,
                'pct_change': float(stock_data.get('pct_change', 0)),
                'pct_change_display': f"{float(stock_data.get('pct_change', 0)):.2f}%",
                'gap_pct': float(gap_pct),
                'gap_pct_display': f"{gap_pct:.2f}%",
                'rel_vol': float(rel_vol),
                'rel_vol_display': f"{rel_vol:.2f}x",
                'volume': format_volume(stock_data.get('volume', 0)),
                'float': stock_data.get('float', '—'),
                'market_cap': stock_data.get('market_cap_display', '—'),
                'pe_ratio': stock_data.get('pe_display', '—'),
                'category': category,
                'gap_classification': stock_data.get('gap_classification', '📊 REGULAR')
            })
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue
            
    # Sort by gap percentage (descending)
    results.sort(key=lambda x: x['gap_pct'], reverse=True)
    return results

def get_cache_status():
    """Get information about cache freshness"""
    return cache_manager.get_cache_status()

def get_top_positive_gappers(stocks_data, limit=5):
    """Get the top positive gappers for the highlight section"""
    positive_gappers = []
    
    # Handle both dictionary and list formats
    if isinstance(stocks_data, list):
        # List format (from filtered stocks)
        for stock_data in stocks_data:
            symbol = stock_data.get('symbol', '')
            try:
                gap_pct = stock_data.get('gap_pct', 0)
                
                # Only include positive gappers
                if gap_pct > 0:
                    rel_vol = stock_data.get('relative_volume', 0)  # Fixed: use relative_volume instead of rel_vol
                    positive_gappers.append({
                        'symbol': symbol,
                        'price': stock_data.get('price', 0),
                        'pct_change': stock_data.get('pct_change', 0),
                        'pct_change_display': f"{float(stock_data.get('pct_change', 0)):.2f}%",
                        'gap_pct': gap_pct,
                        'gap_pct_display': f"{float(gap_pct):.2f}%",
                        'rel_vol': rel_vol,
                        'rel_vol_display': f"{float(rel_vol):.1f}x",
                        'volume': format_volume(stock_data.get('volume', 0)),
                        'float': stock_data.get('float', '—'),
                        'market_cap': stock_data.get('market_cap_display', '—'),  # Use display version
                        'pe': stock_data.get('pe_display', '—'),  # Use display version
                        'has_news': stock_data.get('has_news', False),
                        'source': stock_data.get('source', 'cache'),
                        'timestamp': stock_data.get('timestamp', 0)
                    })
                
            except Exception as e:
                print(f"⚠️  Error processing {symbol} for top gappers: {e}")
                continue
    else:
        # Dictionary format (from original cache)
        for symbol, stock_data in stocks_data.items():
            try:
                gap_pct = stock_data.get('gap_pct', 0)
                
                # Only include positive gappers
                if gap_pct > 0:
                    rel_vol = stock_data.get('relative_volume', 0)  # Fixed: use relative_volume instead of rel_vol
                    positive_gappers.append({
                        'symbol': symbol,
                        'price': stock_data.get('price', 0),
                        'pct_change': stock_data.get('pct_change', 0),
                        'pct_change_display': f"{float(stock_data.get('pct_change', 0)):.2f}%",
                        'gap_pct': gap_pct,
                        'gap_pct_display': f"{float(gap_pct):.2f}%",
                        'rel_vol': rel_vol,
                        'rel_vol_display': f"{float(rel_vol):.1f}x",
                        'volume': format_volume(stock_data.get('volume', 0)),
                        'float': stock_data.get('float', '—'),
                        'market_cap': stock_data.get('market_cap_display', '—'),  # Use display version
                        'pe': stock_data.get('pe_display', '—'),  # Use display version
                        'has_news': stock_data.get('has_news', False),
                        'source': stock_data.get('source', 'cache'),
                        'timestamp': stock_data.get('timestamp', 0)
                    })
                
            except Exception as e:
                print(f"⚠️  Error processing {symbol} for top gappers: {e}")
                continue
    
    # Sort by gap percentage (highest first) and limit results
    return sorted(positive_gappers, key=lambda x: x['gap_pct'], reverse=True)[:limit]

def get_quick_movers(stocks_data, limit=5):
    """Get the fastest moving stocks based on price velocity and volume"""
    quick_movers = []
    
    # Handle both dictionary and list formats
    if isinstance(stocks_data, list):
        # List format (from filtered stocks)
        for stock_data in stocks_data:
            symbol = stock_data.get('symbol', '')
            try:
                gap_pct = abs(stock_data.get('gap_pct', 0))  # Use gap_pct instead of pct_change
                rel_vol = stock_data.get('relative_volume', 0)  # Fixed: use relative_volume instead of rel_vol
                price = stock_data.get('price', 0)
                
                # Only include stocks with significant movement and volume (lowered thresholds for real market data)
                if gap_pct >= 0.5 and rel_vol >= 0.5 and price >= 1:
                    # Calculate "movement score" combining % change and relative volume
                    movement_score = gap_pct * (1 + (rel_vol - 1) * 0.5)
                    
                    quick_movers.append({
                        'symbol': symbol,
                        'price': price,
                        'pct_change': stock_data.get('gap_pct', 0),  # Use gap_pct as pct_change
                        'pct_change_display': f"{float(stock_data.get('gap_pct', 0)):.2f}%",
                        'abs_pct_change': gap_pct,
                        'gap_pct': stock_data.get('gap_pct', 0),
                        'gap_pct_display': f"{float(stock_data.get('gap_pct', 0)):.2f}%",
                        'rel_vol': rel_vol,
                        'rel_vol_display': f"{float(rel_vol):.1f}x",
                        'volume': format_volume(stock_data.get('volume', 0)),
                        'float': stock_data.get('float_shares', '—'),  # Use float_shares
                        'market_cap': stock_data.get('market_cap', '—'),  # Use market_cap
                        'pe': stock_data.get('pe_ratio', '—'),  # Use pe_ratio
                        'has_news': stock_data.get('has_news', False),
                        'source': stock_data.get('source', 'cache'),
                        'timestamp': stock_data.get('timestamp', 0),
                        'movement_score': movement_score
                    })
                
            except Exception as e:
                print(f"⚠️  Error processing {symbol} for quick movers: {e}")
                continue
    else:
        # Dictionary format (from original cache)
        for symbol, stock_data in stocks_data.items():
            try:
                gap_pct = abs(stock_data.get('gap_pct', 0))  # Use gap_pct instead of pct_change
                rel_vol = stock_data.get('relative_volume', 0)  # Fixed: use relative_volume instead of rel_vol
                price = stock_data.get('price', 0)
                
                # Only include stocks with significant movement and volume (lowered thresholds for real market data)
                if gap_pct >= 0.5 and rel_vol >= 0.5 and price >= 1:
                    # Calculate "movement score" combining % change and relative volume
                    movement_score = gap_pct * (1 + (rel_vol - 1) * 0.5)
                    
                    quick_movers.append({
                        'symbol': symbol,
                        'price': price,
                        'pct_change': stock_data.get('gap_pct', 0),  # Use gap_pct as pct_change
                        'pct_change_display': f"{float(stock_data.get('gap_pct', 0)):.2f}%",
                        'abs_pct_change': gap_pct,
                        'gap_pct': stock_data.get('gap_pct', 0),
                        'gap_pct_display': f"{float(stock_data.get('gap_pct', 0)):.2f}%",
                        'rel_vol': rel_vol,
                        'rel_vol_display': f"{float(rel_vol):.1f}x",
                        'volume': format_volume(stock_data.get('volume', 0)),
                        'float': stock_data.get('float_shares', '—'),  # Use float_shares
                        'market_cap': stock_data.get('market_cap', '—'),  # Use market_cap
                        'pe': stock_data.get('pe_ratio', '—'),  # Use pe_ratio
                        'has_news': stock_data.get('has_news', False),
                        'source': stock_data.get('source', 'cache'),
                        'timestamp': stock_data.get('timestamp', 0),
                        'movement_score': movement_score
                    })
                
            except Exception as e:
                print(f"⚠️  Error processing {symbol} for quick movers: {e}")
                continue
    
    # Sort by movement score (highest first) and limit results
    return sorted(quick_movers, key=lambda x: x['movement_score'], reverse=True)[:limit]

@app.route("/")
def screener():
    """Main screener page with filters and timing info"""
    try:
        cache_data = cache_manager.load_cache()
        
        if not cache_data or 'stocks' not in cache_data:
            # Try to start the background scanner if it's not running
            if not is_scanner_running():
                print("🔄 No cache data found - starting background scanner...")
                start_background_scanner()
            
            # Create default cache_info for error case
            default_cache_info = {
                'successful_count': 0,
                'total_count': 0,
                'last_update': 'Never',
                'is_fresh': False
            }
            return render_template('screener.html', 
                                   stocks=[], 
                                   error="📊 No stock data available. Background scanner is starting... Please refresh in a few minutes.",
                                   market_info=get_default_market_info(),
                                   cache_info=default_cache_info,
                                   cache_status=get_cache_status(),
                                   filters={
                                       'min_price': 1.0,
                                       'max_price': 100.0,
                                       'min_gap_pct': 0.0,
                                       'min_rel_vol': 0.0,
                                       'max_float': '',
                                       'sector_filter': 'All'
                                   })

        # Calculate data age and freshness
        last_update = cache_data.get('last_update', 0)
        
        # Convert ISO string to timestamp if needed
        if isinstance(last_update, str):
            try:
                from datetime import datetime
                last_update_dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                last_update = last_update_dt.timestamp()
            except:
                last_update = time.time()  # Fallback to current time
        
        data_age_minutes = (time.time() - last_update) / 60
        market_session = cache_data.get('market_session', {})
        scan_summary = cache_data.get('scan_summary', {})

        # Extract filter parameters with input validation
        try:
            # Use new validation system
            validated_filters, validation_error = validate_filters(request.args)
            
            if validation_error:
                return render_template('screener.html',
                                     stocks=[], 
                                     error=f"Invalid filter parameters: {validation_error}",
                                     market_info=get_default_market_info(),
                                     cache_info={
                                         'successful_count': 0,
                                         'total_count': 0,
                                         'last_update': 'Never',
                                         'is_fresh': False
                                     },
                                     cache_status=get_cache_status(),
                                     filters={
                                         'min_price': 1.0,
                                         'max_price': 2000.0,  # Increased from 100.0 to accommodate higher-priced stocks
                                         'min_gap_pct': 0.0,
                                         'min_rel_vol': 0.0,
                                         'max_float': '',
                                         'sector_filter': 'All'
                                     })
            
            # Extract validated parameters
            min_price = validated_filters['min_price']
            max_price = validated_filters['max_price']
            min_gap_pct = validated_filters['min_gap_pct']
            min_rel_vol = validated_filters['min_rel_vol']
            max_float = validated_filters['max_float']
            sector_filter = validated_filters['sector_filter']
            min_market_cap = validated_filters['min_market_cap']
            max_market_cap = validated_filters['max_market_cap']
            min_pe_ratio = validated_filters['min_pe_ratio']
            max_pe_ratio = validated_filters['max_pe_ratio']
            min_premarket_volume = validated_filters['min_premarket_volume']
            
            # Legacy parameters for backward compatibility
            min_pre_market = request.args.get('min_pre_market', '')
            max_pre_market = request.args.get('max_pre_market', '')
            min_post_market = request.args.get('min_post_market', '')
            max_post_market = request.args.get('max_post_market', '')
            min_pre_market_change = request.args.get('min_pre_market_change', '')
            max_pre_market_change = request.args.get('max_pre_market_change', '')
            min_post_market_change = request.args.get('min_post_market_change', '')
            max_post_market_change = request.args.get('max_post_market_change', '')
            
            # Apply filters
            filtered_stocks = filter_cached_stocks(
                cache_data['stocks'], 
                min_price=min_price,
                max_price=max_price, 
                min_gap_pct=min_gap_pct,
                min_rel_vol=min_rel_vol,
                max_float=max_float,
                sector_filter=sector_filter,
                min_pre_market=min_pre_market,
                max_pre_market=max_pre_market,
                min_post_market=min_post_market,
                max_post_market=max_post_market,
                min_market_cap=min_market_cap,
                max_market_cap=max_market_cap,
                min_pe_ratio=min_pe_ratio,
                max_pe_ratio=max_pe_ratio,
                min_pre_market_change=min_pre_market_change,
                max_pre_market_change=max_pre_market_change,
                min_post_market_change=min_post_market_change,
                max_post_market_change=max_post_market_change,
                min_premarket_volume=min_premarket_volume
            )
            
            # Add data age to each stock for display
            for stock in filtered_stocks:
                if 'data_fetch_time' in stock:
                    try:
                        fetch_time = datetime.fromisoformat(stock['data_fetch_time'].replace('Z', '+00:00'))
                        stock['data_age_seconds'] = int((datetime.now() - fetch_time.replace(tzinfo=None)).total_seconds())
                        stock['data_age_display'] = format_time_ago(stock['data_age_seconds'])
                    except:
                        stock['data_age_seconds'] = int(data_age_minutes * 60)
                        stock['data_age_display'] = f"{data_age_minutes:.1f}m ago"
                else:
                    stock['data_age_seconds'] = int(data_age_minutes * 60)
                    stock['data_age_display'] = f"{data_age_minutes:.1f}m ago"
            
            # Sort by gap percentage (descending)
            filtered_stocks.sort(key=lambda x: x.get('gap_pct', 0), reverse=True)
            
            # Check if Quick Movers should be independent of filters
            quick_movers_independent = request.args.get('quick_movers_independent', 'true').lower() == 'true'
            
            # Get Quick Movers based on mode
            if quick_movers_independent:
                # Use all stocks from cache for Quick Movers (independent of filters)
                quick_movers = get_quick_movers(cache_data['stocks'])
                print(f"🔍 Quick Movers (Independent): {len(quick_movers)} found from all stocks")
            else:
                # Use filtered stocks for Quick Movers (respects current filters)
                if filtered_stocks:
                    quick_movers = get_quick_movers(filtered_stocks)
                    print(f"🔍 Quick Movers (Filtered): {len(quick_movers)} found from {len(filtered_stocks)} filtered stocks")
                else:
                    quick_movers = []
                    print(f"🔍 Quick Movers (Filtered): 0 found - no stocks meet filter criteria")
            
            # Check if Top Gappers should be independent of filters
            top_gappers_independent = request.args.get('top_gappers_independent', 'true').lower() == 'true'
            
            # Get Top Positive Gappers based on mode
            if top_gappers_independent:
                # Use all stocks from cache for Top Gappers (independent of filters)
                top_positive_gappers = get_top_positive_gappers(cache_data['stocks'])
                print(f"🔍 Top Gappers (Independent): {len(top_positive_gappers)} found from all stocks")
            else:
                # Use filtered stocks for Top Gappers (respects current filters)
                top_positive_gappers = get_top_positive_gappers(filtered_stocks)
                print(f"🔍 Top Gappers (Filtered): {len(top_positive_gappers)} found from {len(filtered_stocks)} filtered stocks")
            print(f"🔍 Top Positive Gappers: {len(top_positive_gappers)} found")
            
            # Get unique sectors for filter dropdown
            sectors = get_unique_sectors(cache_data['stocks'])
            
            # Format numbers for display
            total_stocks = len(cache_data['stocks'])
            filtered_count = len(filtered_stocks)
            
            # Status indicators
            freshness_status = "🟢 Fresh" if data_age_minutes < 2 else "🟡 Getting stale" if data_age_minutes < 5 else "🔴 Stale"
            
            # Get cache status for template
            cache_status_raw = get_cache_status()
            cache_status = {
                'status': cache_status_raw['status'],
                'message': f"Data is {cache_status_raw['status']} ({cache_status_raw['age_minutes']:.1f} minutes old)",
                'age_minutes': cache_status_raw['age_minutes'],
                'is_fresh': cache_status_raw['is_fresh'],
                'last_update_str': cache_status_raw.get('last_update_str', 'Unknown')
            }
            
            # Create cache_info object that matches template expectations
            cache_info = {
                'successful_count': cache_data.get('successful_count', 0),
                'total_count': cache_data.get('total_count', 0),
                'last_update': cache_data.get('last_update_str', 'Unknown'),
                'is_fresh': cache_status['is_fresh']
            }
            
            return render_template('screener.html',
                                 stocks=filtered_stocks,
                                 data=filtered_stocks,  # Template expects both 'stocks' and 'data'
                                 total_stocks=total_stocks,
                                 filtered_count=filtered_count,
                                 data_age_minutes=data_age_minutes,
                                 last_update=cache_data.get('last_update_str', 'Unknown'),
                                 freshness_status=freshness_status,
                                 cache_status=cache_status,
                                 cache_info=cache_info,
                                 quick_movers=quick_movers,
                                 quick_movers_independent=quick_movers_independent,
                                 top_positive_gappers=top_positive_gappers,
                                 top_gappers_independent=top_gappers_independent,
                                 sectors=sectors,
                                 
                                 # NEW: Market session and timing info
                                 market_session=market_session,
                                 scan_summary=scan_summary,
                                 scan_duration=cache_data.get('scan_duration_seconds', 0),
                                 filters={
                                     'min_price': min_price,
                                     'max_price': max_price,
                                     'min_gap_pct': min_gap_pct,
                                     'min_rel_vol': min_rel_vol,
                                     'max_float': max_float,  # Keep original string for form inputs
                                     'sector_filter': sector_filter,
                                     'min_market_cap': min_market_cap,
                                     'max_market_cap': max_market_cap,
                                     'min_pe_ratio': min_pe_ratio,
                                     'max_pe_ratio': max_pe_ratio,
                                     'min_premarket_volume': min_premarket_volume
                                 })
        except ValueError as e:
            return render_template('screener.html',
                                   stocks=[], 
                                   error=f"Invalid input for filter: {e}. Please enter valid numbers.",
                                   market_info=get_default_market_info(),
                                   cache_info={
                                       'successful_count': 0,
                                       'total_count': 0,
                                       'last_update': 'Never',
                                       'is_fresh': False
                                   },
                                   cache_status=get_cache_status(),
                                   filters={
                                       'min_price': 1.0,
                                       'max_price': 100.0,
                                       'min_gap_pct': 0.0,
                                       'min_rel_vol': 0.0,
                                       'max_float': '',
                                       'sector_filter': 'All'
                                   })
        except Exception as e:
            return render_template('screener.html',
                                   stocks=[], 
                                   error=f"An unexpected error occurred: {e}",
                                   market_info=get_default_market_info(),
                                   cache_info={
                                       'successful_count': 0,
                                       'total_count': 0,
                                       'last_update': 'Never',
                                       'is_fresh': False
                                   },
                                   cache_status=get_cache_status(),
                                   filters={
                                       'min_price': 1.0,
                                       'max_price': 100.0,
                                       'min_gap_pct': 0.0,
                                       'min_rel_vol': 0.0,
                                       'max_float': '',
                                       'sector_filter': 'All'
                                   })
    except Exception as e:
        return render_template('screener.html',
                               stocks=[], 
                               error=f"An unexpected error occurred during cache loading: {e}",
                               market_info=get_default_market_info(),
                               cache_info={
                                   'successful_count': 0,
                                   'total_count': 0,
                                   'last_update': 'Never',
                                   'is_fresh': False
                               },
                               cache_status=get_cache_status(),
                               filters={
                                   'min_price': 1.0,
                                   'max_price': 100.0,
                                   'min_gap_pct': 0.0,
                                   'min_rel_vol': 0.0,
                                   'max_float': '',
                                   'sector_filter': 'All'
                               })

@app.route("/api/cache_status")
def api_cache_status():
    """API endpoint to check cache status"""
    cache = cache_manager.load_cache()
    cache_status = get_cache_status()
    
    return jsonify({
        'cache_status': cache_status,
        'successful_count': cache.get('successful_count', 0),
        'total_count': cache.get('total_count', 0),
        'last_update': cache.get('last_update_str', 'Never'),
        'stocks_available': len(cache.get('stocks', {}))
    })

@app.route("/analytics-test")
def analytics_test():
    """Test page for analytics tracking"""
    return render_template("analytics_test.html")

@app.route("/health")
def health():
    """Health check endpoint"""
    cache_status = get_cache_status()
    managed_running = (background_scanner_process and background_scanner_process.poll() is None)
    pid_file_running = is_scanner_running()
    scanner_status = "running" if (managed_running or pid_file_running) else "stopped"
    
    return jsonify({
        'status': 'healthy',
        'cache_status': cache_status['status'],
        'cache_age_minutes': cache_status['age_minutes'],
        'scanner_status': scanner_status,
        'scanner_managed': managed_running,
        'scanner_pid_detected': pid_file_running,
        'timestamp': datetime.now().isoformat()
    })

@app.route("/api/scanner/start", methods=['POST'])
def start_scanner():
    """Manually start the background scanner"""
    try:
        if start_background_scanner():
            return jsonify({'status': 'success', 'message': 'Background scanner started'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to start background scanner'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/scanner/stop", methods=['POST'])
def stop_scanner():
    """Manually stop the background scanner"""
    try:
        stop_background_scanner()
        return jsonify({'status': 'success', 'message': 'Background scanner stopped'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route("/api/scanner/status")
def scanner_status():
    """Get background scanner status"""
    # Check both managed process and PID file
    managed_running = (background_scanner_process and background_scanner_process.poll() is None)
    pid_file_running = is_scanner_running()
    
    is_running = managed_running or pid_file_running
    
    return jsonify({
        'running': is_running,
        'managed_process': managed_running,
        'pid_file_detected': pid_file_running,
        'pid': background_scanner_process.pid if managed_running else None
    })

@app.route("/api/event", methods=['POST'])
def analytics_event():
    """Handle analytics events from client-side tracker"""
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        # Validate required fields
        if not data or 'event' not in data:
            return jsonify({'error': 'Missing event type'}), 400
        
        event_type = data.get('event')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        
        # Prepare log entry
        log_entry = {
            'timestamp': timestamp,
            'event': event_type,
            'url': data.get('url', ''),
            'domain': data.get('domain', ''),
            'referrer': data.get('referrer'),
            'user_agent': data.get('user_agent', request.headers.get('User-Agent', '')),
            'ip': request.remote_addr
        }
        
        # Add event-specific data
        if event_type == 'engagement':
            log_entry.update({
                'engagement_time': data.get('engagement_time', 0),
                'scroll_depth': data.get('scroll_depth', 0)
            })
        
        # Log to console
        if event_type == 'pageview':
            print(f"📊 ANALYTICS [PAGEVIEW] {log_entry['url']} | IP: {log_entry['ip']} | Referrer: {log_entry['referrer'] or 'Direct'}")
        elif event_type == 'engagement':
            engagement_time = log_entry.get('engagement_time', 0)
            scroll_depth = log_entry.get('scroll_depth', 0)
            print(f"📊 ANALYTICS [ENGAGEMENT] {log_entry['url']} | Time: {engagement_time}s | Scroll: {scroll_depth}% | IP: {log_entry['ip']}")
        
        # Optionally save to file (uncomment if you want persistent logs)
        # try:
        #     with open('analytics.log', 'a', encoding='utf-8') as f:
        #         f.write(json.dumps(log_entry) + '\n')
        # except Exception as e:
        #     print(f"⚠️  Error writing analytics log: {e}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        print(f"⚠️  Error processing analytics event: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/api/traffic")
def api_traffic():
    """Get traffic analytics data"""
    try:
        days = request.args.get('days', 1, type=int)
        stats = traffic_analytics.get_traffic_stats(days)
        return jsonify(stats)
    except Exception as e:
        print(f"⚠️  Error getting traffic stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/api/traffic/realtime")
def api_traffic_realtime():
    """Get real-time traffic statistics"""
    try:
        stats = traffic_analytics.get_real_time_stats()
        return jsonify(stats)
    except Exception as e:
        print(f"⚠️  Error getting real-time stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Poppalyze Stock Screener")
    print(f"📁 Cache file: {CACHE_FILE}")
    
    # ALWAYS start the background scanner on initialization
    print("🔄 Starting background scanner...")
    scanner_started = start_background_scanner()
    
    if scanner_started:
        print("✅ Background scanner is running")
    else:
        print("⚠️  Background scanner failed to start - will retry on first request")
    
    print("🎉 Poppalyze is ready!")
    print("📊 Background scanner will continuously update stock data")
    
    # Get port from environment (Render sets PORT)
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting Poppalyze on port {port}")
    print(f"🌐 App will be available at: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 