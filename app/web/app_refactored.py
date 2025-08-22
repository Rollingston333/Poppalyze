#!/usr/bin/env python3
"""
Refactored Gap Screener Flask App
- Background thread for stock scanning
- Thread-safe global cache
- Graceful fallbacks for empty cache
- Comprehensive logging
"""

from flask import Flask, render_template, request, jsonify
import json
import time
import os
import threading
import signal
import sys
import sqlite3
import uuid
import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dotenv import load_dotenv
from cache_manager import cache_manager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
CACHE_FILE = "stock_cache.json"
TRAFFIC_DB = "traffic_analytics.db"
SCAN_INTERVAL = 300  # 5 minutes
BACKGROUND_SCANNER_RUNNING = False
SCANNER_THREAD = None

# Global cache and scanner state
class GlobalState:
    def __init__(self):
        self.cache = {}
        self.cache_lock = threading.RLock()
        self.last_scan_time = 0
        self.scanner_running = False
        self.scan_count = 0
        self.last_scan_duration = 0

# Initialize global state
global_state = GlobalState()

# =====================================================
# STOCK SCANNING FUNCTIONS
# =====================================================

def scan_stocks():
    """
    Main stock scanning function that fetches stock data
    Returns a dictionary of stock data
    """
    try:
        logger.info("🔍 Starting stock scan...")
        start_time = time.time()
        
        # Import yfinance for stock data
        import yfinance as yf
        
        # Define stocks to scan (mix of different price ranges)
        symbols = [
            # Low-priced stocks
            'SNDL', 'PLUG', 'NIO', 'XPEV', 'LI', 'WKHS', 'LYFT', 'SNAP',
            # Mid-priced stocks
            'AMD', 'INTC', 'UBER', 'PINS', 'ROKU', 'ZM', 'CRWD',
            # High-priced stocks
            'AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX', 'SPY', 'QQQ'
        ]
        
        stocks_data = {}
        successful_count = 0
        
        for symbol in symbols:
            try:
                logger.debug(f"📊 Scanning {symbol}...")
                
                # Get stock data
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get current price
                current_price = info.get('currentPrice', 0)
                if not current_price:
                    current_price = info.get('regularMarketPrice', 0)
                
                # Get previous close
                previous_close = info.get('previousClose', current_price)
                
                # Calculate gap percentage
                if previous_close and previous_close > 0:
                    gap_pct = ((current_price - previous_close) / previous_close) * 100
                else:
                    gap_pct = 0
                
                # Get volume data
                volume = info.get('volume', 0)
                avg_volume = info.get('averageVolume', volume)
                relative_volume = volume / avg_volume if avg_volume > 0 else 0
                
                # Get market cap
                market_cap = info.get('marketCap', 0)
                
                # Get PE ratio
                pe_ratio = info.get('trailingPE', 0)
                
                # Get sector
                sector = info.get('sector', 'Unknown')
                
                # Create stock data
                stock_data = {
                    'symbol': symbol,
                    'price': current_price,
                    'previous_close': previous_close,
                    'gap_pct': gap_pct,
                    'volume': volume,
                    'relative_volume': relative_volume,
                    'market_cap': market_cap,
                    'pe_ratio': pe_ratio,
                    'sector': sector,
                    'data_fetch_time': datetime.now().isoformat()
                }
                
                stocks_data[symbol] = stock_data
                successful_count += 1
                
                logger.debug(f"✅ {symbol}: ${current_price:.2f} (Gap: {gap_pct:+.2f}%)")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"❌ Error scanning {symbol}: {e}")
                continue
        
        scan_duration = time.time() - start_time
        
        # Create cache data
        cache_data = {
            'stocks': stocks_data,
            'successful_count': successful_count,
            'total_count': len(symbols),
            'last_update': time.time(),
            'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'scan_duration_seconds': round(scan_duration, 1),
            'scan_type': 'background_scanner'
        }
        
        logger.info(f"🎉 Stock scan completed: {successful_count}/{len(symbols)} stocks in {scan_duration:.1f}s")
        return cache_data
        
    except Exception as e:
        logger.error(f"❌ Critical error in stock scan: {e}")
        return None

def background_scanner():
    """
    Background thread that continuously scans stocks at fixed intervals
    """
    global global_state
    
    logger.info("🚀 Background scanner thread started")
    global_state.scanner_running = True
    
    while global_state.scanner_running:
        try:
            logger.info(f"🔍 Background scan #{global_state.scan_count + 1} starting...")
            
            # Perform stock scan
            cache_data = scan_stocks()
            
            if cache_data:
                # Update global cache thread-safely
                with global_state.cache_lock:
                    global_state.cache = cache_data
                    global_state.last_scan_time = time.time()
                    global_state.scan_count += 1
                    global_state.last_scan_duration = cache_data['scan_duration_seconds']
                
                # Save to file using cache manager
                cache_manager.save_cache(cache_data)
                logger.info("💾 Cache updated successfully")
            else:
                logger.warning("⚠️ Stock scan returned no data")
            
            # Wait for next scan interval
            logger.info(f"⏳ Next scan in {SCAN_INTERVAL} seconds...")
            time.sleep(SCAN_INTERVAL)
            
        except Exception as e:
            logger.error(f"❌ Error in background scanner: {e}")
            time.sleep(60)  # Wait 1 minute before retrying
    
    logger.info("🛑 Background scanner thread stopped")

def start_background_scanner():
    """Start the background scanner thread"""
    global SCANNER_THREAD, global_state
    
    if global_state.scanner_running:
        logger.info("⚠️ Background scanner already running")
        return True
    
    try:
        SCANNER_THREAD = threading.Thread(target=background_scanner, daemon=True)
        SCANNER_THREAD.start()
        logger.info("✅ Background scanner started successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to start background scanner: {e}")
        return False

def stop_background_scanner():
    """Stop the background scanner thread"""
    global global_state
    
    if not global_state.scanner_running:
        logger.info("⚠️ Background scanner not running")
        return True
    
    try:
        global_state.scanner_running = False
        logger.info("🛑 Background scanner stop signal sent")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to stop background scanner: {e}")
        return False

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
                logger.info("✅ Traffic analytics database initialized")
        except Exception as e:
            logger.error(f"⚠️ Error initializing traffic database: {e}")
    
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
            logger.error(f"⚠️ Error tracking visitor: {e}")
    
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
            logger.error(f"⚠️ Error tracking page view: {e}")
    
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
            logger.error(f"⚠️ Error tracking API call: {e}")

# Initialize traffic analytics
traffic_analytics = TrafficAnalytics()

# =====================================================
# UTILITY FUNCTIONS
# =====================================================

def get_cache_data():
    """Get cache data thread-safely with fallback"""
    with global_state.cache_lock:
        if global_state.cache and global_state.cache.get('stocks'):
            return global_state.cache
        else:
            # Try to load from file as fallback
            try:
                file_cache = cache_manager.load_cache()
                if file_cache and file_cache.get('stocks'):
                    global_state.cache = file_cache
                    return file_cache
            except Exception as e:
                logger.warning(f"Could not load cache from file: {e}")
            
            return None

def get_cache_status():
    """Get cache status information"""
    cache_data = get_cache_data()
    
    if not cache_data:
        return {
            'status': 'No data',
            'age_minutes': float('inf'),
            'is_fresh': False,
            'last_update_str': 'Never',
            'stock_count': 0
        }
    
    last_update = cache_data.get('last_update', 0)
    if last_update == 0:
        return {
            'status': 'No data',
            'age_minutes': float('inf'),
            'is_fresh': False,
            'last_update_str': 'Never',
            'stock_count': 0
        }
    
    age_minutes = (time.time() - last_update) / 60
    stock_count = len(cache_data.get('stocks', {}))
    
    return {
        'status': 'Fresh' if age_minutes < 5 else 'Stale' if age_minutes < 60 else 'Very stale',
        'age_minutes': round(age_minutes, 1),
        'is_fresh': age_minutes < 10,
        'last_update_str': cache_data.get('last_update_str', 'Unknown'),
        'stock_count': stock_count
    }

def safe_float(value, default):
    """Safely convert value to float with fallback"""
    try:
        return float(value) if value else default
    except (ValueError, TypeError):
        return default

def format_volume(volume):
    """Format volume numbers to human-readable format"""
    try:
        if not volume or volume == 0:
            return "0"
        
        volume = float(volume)
        
        if volume >= 1e9:
            return f"{volume/1e9:.1f}B"
        elif volume >= 1e6:
            return f"{volume/1e6:.1f}M"
        elif volume >= 1e3:
            return f"{volume/1e3:.1f}K"
        else:
            return f"{volume:.0f}"
    except:
        return "0"

def format_market_cap(market_cap):
    """Format market cap numbers to human-readable format"""
    try:
        if not market_cap or market_cap == 0:
            return "N/A"
        
        market_cap = float(market_cap)
        
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.1f}M"
        elif market_cap >= 1e3:
            return f"${market_cap/1e3:.1f}K"
        else:
            return f"${market_cap:.0f}"
    except:
        return "N/A"

def format_time_ago(seconds):
    """Format time ago in human-readable format"""
    try:
        if seconds < 60:
            return f"{int(seconds)}s ago"
        elif seconds < 3600:
            return f"{int(seconds/60)}m ago"
        elif seconds < 86400:
            return f"{int(seconds/3600)}h ago"
        else:
            return f"{int(seconds/86400)}d ago"
    except:
        return "Unknown"

def get_unique_sectors(stocks_data):
    """Get unique sectors from stock data"""
    sectors = set()
    for stock in stocks_data.values():
        sector = stock.get('sector', 'Unknown')
        if sector and sector != '—':
            sectors.add(sector)
    return sorted(list(sectors))

def filter_cached_stocks(stocks_data, **filters):
    """Filter stocks based on criteria"""
    if not stocks_data:
        return []
    
    filtered_stocks = []
    
    for symbol, stock in stocks_data.items():
        # Apply filters
        price = stock.get('price', 0)
        gap_pct = stock.get('gap_pct', 0)
        relative_volume = stock.get('relative_volume', 0)
        market_cap = stock.get('market_cap', 0)
        pe_ratio = stock.get('pe_ratio', 0)
        sector = stock.get('sector', 'Unknown')
        
        # Price filter
        if 'min_price' in filters and price < safe_float(filters['min_price'], 0):
            continue
        if 'max_price' in filters and price > safe_float(filters['max_price'], float('inf')):
            continue
        
        # Gap filter
        if 'min_gap_pct' in filters and gap_pct < safe_float(filters['min_gap_pct'], -float('inf')):
            continue
        if 'max_gap_pct' in filters and gap_pct > safe_float(filters['max_gap_pct'], float('inf')):
            continue
        
        # Volume filter
        if 'min_rel_vol' in filters and relative_volume < safe_float(filters['min_rel_vol'], 0):
            continue
        
        # Market cap filter
        if 'min_market_cap' in filters and market_cap < safe_float(filters['min_market_cap'], 0):
            continue
        if 'max_market_cap' in filters and market_cap > safe_float(filters['max_market_cap'], float('inf')):
            continue
        
        # PE ratio filter
        if 'min_pe_ratio' in filters and pe_ratio < safe_float(filters['min_pe_ratio'], 0):
            continue
        if 'max_pe_ratio' in filters and pe_ratio > safe_float(filters['max_pe_ratio'], float('inf')):
            continue
        
        # Sector filter
        if 'sector_filter' in filters and filters['sector_filter'] != 'All':
            if sector != filters['sector_filter']:
                continue
        
        # Add symbol to stock data for template
        stock['symbol'] = symbol
        filtered_stocks.append(stock)
    
    return filtered_stocks

def get_top_positive_gappers(stocks_data, limit=5):
    """Get top positive gappers"""
    if not stocks_data:
        return []
    
    # Filter for positive gaps and sort by gap percentage
    positive_gappers = [
        stock for stock in stocks_data.values() 
        if stock.get('gap_pct', 0) > 0
    ]
    
    # Sort by gap percentage (descending)
    positive_gappers.sort(key=lambda x: x.get('gap_pct', 0), reverse=True)
    
    return positive_gappers[:limit]

def get_quick_movers(stocks_data, limit=5):
    """Get quick movers (high relative volume)"""
    if not stocks_data:
        return []
    
    # Filter for stocks with relative volume > 1 and sort by relative volume
    quick_movers = [
        stock for stock in stocks_data.values() 
        if stock.get('relative_volume', 0) > 1
    ]
    
    # Sort by relative volume (descending)
    quick_movers.sort(key=lambda x: x.get('relative_volume', 0), reverse=True)
    
    return quick_movers[:limit]

# =====================================================
# REQUEST HANDLERS
# =====================================================

@app.before_request
def track_request():
    """Track all requests for analytics"""
    try:
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Track visitor
        traffic_analytics.track_visitor(session_id, ip_address, user_agent)
        
        # Track page view for non-API routes
        if not request.path.startswith('/api/'):
            traffic_analytics.track_page_view(
                session_id, request.path, ip_address, user_agent, 
                request.headers.get('Referer')
            )
        
        # Track API calls
        if request.path.startswith('/api/'):
            traffic_analytics.track_api_call(session_id, request.path, ip_address, user_agent)
            
    except Exception as e:
        logger.error(f"Error tracking request: {e}")

@app.after_request
def add_session_cookie(response):
    """Add session cookie if not present"""
    if 'session_id' not in request.cookies:
        session_id = str(uuid.uuid4())
        response.set_cookie('session_id', session_id, max_age=86400)
    return response

# =====================================================
# ROUTES
# =====================================================

@app.route("/")
def screener():
    """Main screener page"""
    logger.info("📄 Main screener page requested")
    
    try:
        # Get cache data
        cache_data = get_cache_data()
        
        if not cache_data or not cache_data.get('stocks'):
            logger.warning("⚠️ No cache data available for main page")
            return render_template('screener.html', 
                                 stocks_data={},
                                 cache_status={'status': 'No data', 'stock_count': 0},
                                 sectors=['Unknown'],
                                 quick_movers_independent=True,
                                 top_gappers_independent=True,
                                 show_loading=True)
        
        # Get filter parameters
        min_price = request.args.get('min_price', '1')
        max_price = request.args.get('max_price', '20')
        min_gap_pct = request.args.get('min_gap_pct', '-100.0')
        min_rel_vol = request.args.get('min_rel_vol', '0.0')
        sector_filter = request.args.get('sector_filter', 'All')
        
        # Get independent filter settings (default to True = sliders OFF)
        quick_movers_independent = request.args.get('quick_movers_independent', 'true').lower() == 'true'
        top_gappers_independent = request.args.get('top_gappers_independent', 'true').lower() == 'true'
        
        # Apply filters
        filtered_stocks = filter_cached_stocks(
            cache_data['stocks'],
            min_price=min_price,
            max_price=max_price,
            min_gap_pct=min_gap_pct,
            min_rel_vol=min_rel_vol,
            sector_filter=sector_filter
        )
        
        # Get cache status
        cache_status = get_cache_status()
        
        # Get unique sectors
        sectors = get_unique_sectors(cache_data['stocks'])
        
        # Get top performers based on independent settings
        if quick_movers_independent:
            quick_movers = get_quick_movers(cache_data['stocks'], 5)  # Use all stocks
        else:
            quick_movers = get_quick_movers(filtered_stocks, 5)  # Use filtered stocks
            
        if top_gappers_independent:
            top_gappers = get_top_positive_gappers(cache_data['stocks'], 5)  # Use all stocks
        else:
            top_gappers = get_top_positive_gappers(filtered_stocks, 5)  # Use filtered stocks
        
        # Add formatted market cap to stock data for display
        for stock in quick_movers:
            stock['market_cap_formatted'] = format_market_cap(stock.get('market_cap', 0))
        
        for stock in top_gappers:
            stock['market_cap_formatted'] = format_market_cap(stock.get('market_cap', 0))
        
        # Add formatted market cap to filtered stocks for main table
        for stock in filtered_stocks:
            stock['market_cap_formatted'] = format_market_cap(stock.get('market_cap', 0))
        
        logger.info(f"✅ Main page rendered with {len(filtered_stocks)} filtered stocks")
        
        # Add message field to cache_status for template compatibility
        cache_status['message'] = cache_status.get('status', 'Unknown')
        
        # Create filters object for template
        filters = {
            'min_price': float(min_price),
            'max_price': float(max_price),
            'min_gap_pct': float(min_gap_pct),
            'min_rel_vol': float(min_rel_vol),
            'sector_filter': sector_filter
        }
        
        return render_template('screener.html',
                             stocks=filtered_stocks,
                             stocks_data=filtered_stocks,
                             filtered_count=len(filtered_stocks),
                             total_stocks=cache_status.get('stock_count', 0),
                             cache_status=cache_status,
                             sectors=sectors,
                             filters=filters,
                             top_positive_gappers=top_gappers,
                             quick_movers=quick_movers,
                             quick_movers_independent=quick_movers_independent,
                             top_gappers_independent=top_gappers_independent,
                             show_loading=False)
                             
    except Exception as e:
        logger.error(f"❌ Error rendering main page: {e}")
        error_cache_status = {'status': 'Error', 'stock_count': 0, 'message': 'Error'}
        
        # Create default filters object for error case
        default_filters = {
            'min_price': 1.0,
            'max_price': 2000.0,
            'min_gap_pct': -100.0,
            'min_rel_vol': 0.0,
            'sector_filter': 'All'
        }
        
        return render_template('screener.html',
                             stocks={},
                             stocks_data={},
                             filtered_count=0,
                             total_stocks=0,
                             cache_status=error_cache_status,
                             sectors=['Unknown'],
                             filters=default_filters,
                             quick_movers_independent=True,
                             top_gappers_independent=True,
                             show_loading=False)

@app.route("/api/cache_status")
def api_cache_status():
    """Get cache status API endpoint"""
    logger.debug("📊 Cache status API requested")
    
    try:
        cache_status = get_cache_status()
        
        # Add scanner status
        scanner_status = {
            'running': global_state.scanner_running,
            'scan_count': global_state.scan_count,
            'last_scan_duration': global_state.last_scan_duration
        }
        
        response = {
            'cache_status': cache_status['status'],
            'age_minutes': cache_status['age_minutes'],
            'stock_count': cache_status['stock_count'],
            'last_update_str': cache_status['last_update_str'],
            'scanner_status': scanner_status,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"❌ Error in cache status API: {e}")
        return jsonify({
            'error': 'Internal server error',
            'cache_status': 'Error',
            'age_minutes': float('inf'),
            'stock_count': 0
        }), 500

@app.route("/health")
def health():
    """Health check endpoint"""
    logger.debug("🏥 Health check requested")
    
    try:
        cache_status = get_cache_status()
        
        return jsonify({
            'status': 'healthy',
            'cache_status': cache_status['status'],
            'cache_age_minutes': cache_status['age_minutes'],
            'scanner_running': global_state.scanner_running,
            'scan_count': global_state.scan_count,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route("/api/scanner/start", methods=['POST'])
def start_scanner():
    """Start background scanner API endpoint"""
    logger.info("🚀 Start scanner API requested")
    
    try:
        success = start_background_scanner()
        return jsonify({
            'success': success,
            'message': 'Scanner started successfully' if success else 'Failed to start scanner'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting scanner: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/scanner/stop", methods=['POST'])
def stop_scanner():
    """Stop background scanner API endpoint"""
    logger.info("🛑 Stop scanner API requested")
    
    try:
        success = stop_background_scanner()
        return jsonify({
            'success': success,
            'message': 'Scanner stopped successfully' if success else 'Failed to stop scanner'
        })
        
    except Exception as e:
        logger.error(f"❌ Error stopping scanner: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/scanner/status")
def scanner_status():
    """Get scanner status API endpoint"""
    logger.debug("📊 Scanner status API requested")
    
    try:
        return jsonify({
            'running': global_state.scanner_running,
            'scan_count': global_state.scan_count,
            'last_scan_time': global_state.last_scan_time,
            'last_scan_duration': global_state.last_scan_duration,
            'scan_interval': SCAN_INTERVAL
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting scanner status: {e}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

# =====================================================
# ERROR HANDLERS
# =====================================================

@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"400 Bad Request: {error}")
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# =====================================================
# SIGNAL HANDLERS
# =====================================================

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"🛑 Received signal {signum}, shutting down...")
    stop_background_scanner()
    sys.exit(0)

# =====================================================
# INITIALIZATION
# =====================================================

def initialize_app():
    """Initialize the Flask app"""
    logger.info("🚀 Initializing Flask app...")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load existing cache if available
    try:
        existing_cache = cache_manager.load_cache()
        if existing_cache and existing_cache.get('stocks'):
            with global_state.cache_lock:
                global_state.cache = existing_cache
                global_state.last_scan_time = existing_cache.get('last_update', 0)
            logger.info(f"✅ Loaded existing cache with {len(existing_cache.get('stocks', {}))} stocks")
        else:
            logger.info("📁 No existing cache found")
    except Exception as e:
        logger.warning(f"⚠️ Could not load existing cache: {e}")
    
    # Start background scanner
    logger.info("🔄 Starting background scanner...")
    start_background_scanner()
    
    logger.info("✅ Flask app initialization complete")

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    initialize_app()
    
    logger.info("🌐 Starting Flask development server...")
    logger.info(f"📊 App will be available at: http://localhost:5001")
    logger.info(f"🔄 Background scanner interval: {SCAN_INTERVAL} seconds")
    logger.info("🛑 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=5001) 