#!/usr/bin/env python3
"""
Production-ready Stock Screener Application
Optimized for deployment on cloud platforms
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for
import yfinance as yf
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
import json
import sqlite3
import threading
import time
import requests
from urllib.parse import urlparse
import psutil

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Production configuration
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'traffic_analytics.db')
    CACHE_FILE = os.environ.get('CACHE_FILE', 'stock_cache.json')
    SCAN_INTERVAL = int(os.environ.get('SCAN_INTERVAL', '300'))  # 5 minutes
    PORT = int(os.environ.get('PORT', 5000))
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Stock data structure
@dataclass
class StockData:
    symbol: str
    name: str
    price: float
    change: float
    change_pct: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    float: Optional[float] = None
    premarket_price: Optional[float] = None
    premarket_change: Optional[float] = None
    premarket_change_pct: Optional[float] = None
    premarket_volume: Optional[int] = None
    postmarket_price: Optional[float] = None
    postmarket_change: Optional[float] = None
    postmarket_change_pct: Optional[float] = None
    postmarket_volume: Optional[int] = None
    last_updated: Optional[str] = None

@dataclass
class FilterParams:
    min_price: float = 0.01
    max_price: float = 1000.0
    min_gap_pct: float = -100.0
    min_rel_vol: float = 0.0
    sector_filter: str = 'All'
    max_float: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    min_premarket_volume: Optional[int] = None
    min_pe_ratio: Optional[float] = None
    max_pe_ratio: Optional[float] = None
    min_pre_market: Optional[float] = None
    max_pre_market: Optional[float] = None
    min_pre_market_change: Optional[float] = None
    max_pre_market_change: Optional[float] = None
    min_post_market: Optional[float] = None
    max_post_market: Optional[float] = None
    min_post_market_change: Optional[float] = None
    max_post_market_change: Optional[float] = None

    def __post_init__(self):
        # Validate and set defaults
        if self.min_price < 0:
            self.min_price = 0.01
        if self.max_price <= 0:
            self.max_price = 1000.0
        if self.min_rel_vol < 0:
            self.min_rel_vol = 0.0

# Global variables
stock_cache: Dict[str, StockData] = {}
last_update: Optional[datetime] = None
scanner_running = False
scanner_thread = None

# Traffic Analytics
class TrafficAnalytics:
    def __init__(self, db_path='traffic_analytics.db'):
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
                        session_id TEXT UNIQUE NOT NULL,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT,
                        country TEXT,
                        city TEXT,
                        region TEXT,
                        first_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_visit TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create page_views table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS page_views (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        page_url TEXT NOT NULL,
                        response_time REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES visitors (session_id)
                    )
                ''')
                
                # Create api_calls table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        endpoint TEXT NOT NULL,
                        response_time REAL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES visitors (session_id)
                    )
                ''')
                
                conn.commit()
                logger.info("✅ Traffic analytics database initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing database: {e}")

    def track_visitor(self, session_id, ip_address, user_agent, country=None, city=None, region=None):
        """Track a visitor"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO visitors 
                    (session_id, ip_address, user_agent, country, city, region, last_visit)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (session_id, ip_address, user_agent, country, city, region))
                conn.commit()
        except Exception as e:
            logger.error(f"Error tracking visitor: {e}")

    def track_page_view(self, session_id, page_url, response_time=None):
        """Track a page view"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO page_views (session_id, page_url, response_time)
                    VALUES (?, ?, ?)
                ''', (session_id, page_url, response_time))
                conn.commit()
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")

    def track_api_call(self, session_id, endpoint, response_time=None):
        """Track an API call"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_calls (session_id, endpoint, response_time)
                    VALUES (?, ?, ?)
                ''', (session_id, endpoint, response_time))
                conn.commit()
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")

# Initialize traffic analytics
traffic_analytics = TrafficAnalytics()

# Stock Scanner
class StockScanner:
    def __init__(self, cache_file='stock_cache.json'):
        self.cache_file = cache_file
        self.categories = [
            'most_active', 'day_gainers', 'day_losers', 'growth_technology_stocks',
            'undervalued_growth_stocks', 'aggressive_small_caps', 'small_cap_gainers',
            'day_most_actives', 'growth_stocks', 'value_stocks'
        ]
        self.load_cache()
    
    def load_cache(self):
        """Load stock data from cache"""
        global stock_cache, last_update
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    stock_cache = {}
                    for symbol, stock_data in data.items():
                        # Filter out unexpected fields
                        filtered_data = {k: v for k, v in stock_data.items() 
                                       if k in StockData.__annotations__}
                        try:
                            stock_cache[symbol] = StockData(**filtered_data)
                        except Exception as e:
                            logger.warning(f"⚠️ Error reconstructing {symbol}: {e}")
                            continue
                    
                    last_update = datetime.fromisoformat(data.get('last_update', datetime.now().isoformat()))
                    logger.info(f"✅ Cache loaded with {len(stock_cache)} stocks")
                return True
            else:
                logger.warning("⚠️ No cache file found")
                return False
        except Exception as e:
            logger.error(f"❌ Error loading cache: {e}")
            return False
    
    def save_cache(self):
        """Save stock data to cache"""
        global last_update
        try:
            data = {
                'last_update': datetime.now().isoformat(),
                **{symbol: {
                    'symbol': stock.symbol,
                    'name': stock.name,
                    'price': stock.price,
                    'change': stock.change,
                    'change_pct': stock.change_pct,
                    'volume': stock.volume,
                    'market_cap': stock.market_cap,
                    'pe_ratio': stock.pe_ratio,
                    'sector': stock.sector,
                    'industry': stock.industry,
                    'float': stock.float,
                    'premarket_price': stock.premarket_price,
                    'premarket_change': stock.premarket_change,
                    'premarket_change_pct': stock.premarket_change_pct,
                    'premarket_volume': stock.premarket_volume,
                    'postmarket_price': stock.postmarket_price,
                    'postmarket_change': stock.postmarket_change,
                    'postmarket_change_pct': stock.postmarket_change_pct,
                    'postmarket_volume': stock.postmarket_volume,
                    'last_updated': stock.last_updated
                } for symbol, stock in stock_cache.items()}
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            last_update = datetime.now()
            logger.info("✅ Cache saved successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving cache: {e}")
            return False
    
    def scan_stocks(self):
        """Scan stocks from multiple categories"""
        global stock_cache
        start_time = time.time()
        all_symbols = set()
        
        # Collect symbols from all categories
        for category in self.categories:
            try:
                logger.info(f"🔍 Scanning category: {category}")
                tickers = yf.Tickers(category)
                symbols = list(tickers.tickers.keys())
                all_symbols.update(symbols)
                logger.info(f"✅ Found {len(symbols)} symbols in {category}")
                time.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.error(f"❌ Error scanning {category}: {e}")
                continue
        
        # Convert to list and remove duplicates
        symbols_list = list(all_symbols)
        logger.info(f"🎯 Scanning {len(symbols_list)} unique symbols")
        
        # Fetch data for all symbols
        successful_scans = 0
        failed_scans = 0
        
        for symbol in symbols_list:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get current price data
                hist = ticker.history(period="2d")
                if hist.empty:
                    continue
                
                current_price = hist['Close'].iloc[-1]
                prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                change = current_price - prev_price
                change_pct = (change / prev_price) * 100 if prev_price > 0 else 0
                
                # Get premarket/postmarket data
                premarket_data = ticker.history(period="1d", interval="1m")
                premarket_price = None
                premarket_change = None
                premarket_change_pct = None
                premarket_volume = None
                
                if not premarket_data.empty:
                    latest = premarket_data.iloc[-1]
                    if latest.name.hour < 9 or (latest.name.hour == 9 and latest.name.minute < 30):
                        premarket_price = latest['Close']
                        premarket_change = premarket_price - prev_price
                        premarket_change_pct = (premarket_change / prev_price) * 100 if prev_price > 0 else 0
                        premarket_volume = latest['Volume']
                
                # Create stock data object
                stock_data = StockData(
                    symbol=symbol,
                    name=info.get('longName', symbol),
                    price=current_price,
                    change=change,
                    change_pct=change_pct,
                    volume=info.get('volume', 0),
                    market_cap=info.get('marketCap'),
                    pe_ratio=info.get('trailingPE'),
                    sector=info.get('sector'),
                    industry=info.get('industry'),
                    float=info.get('sharesOutstanding'),
                    premarket_price=premarket_price,
                    premarket_change=premarket_change,
                    premarket_change_pct=premarket_change_pct,
                    premarket_volume=premarket_volume,
                    last_updated=datetime.now().isoformat()
                )
                
                stock_cache[symbol] = stock_data
                successful_scans += 1
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                failed_scans += 1
                logger.error(f"HTTP Error 404: {e}")
                continue
        
        # Save cache
        self.save_cache()
        
        elapsed_time = time.time() - start_time
        logger.info(f"🎉 Stock scan completed: {successful_scans}/{len(symbols_list)} stocks in {elapsed_time:.1f}s")
        if failed_scans > 0:
            logger.info(f"⚠️ Failed scans: {failed_scans}")

# Initialize scanner
scanner = StockScanner()

def background_scanner():
    """Background thread for continuous stock scanning"""
    global scanner_running
    while scanner_running:
        try:
            scanner.scan_stocks()
            time.sleep(app.config['SCAN_INTERVAL'])
        except Exception as e:
            logger.error(f"❌ Background scanner error: {e}")
            time.sleep(60)  # Wait 1 minute on error

def start_background_scanner():
    """Start the background scanner thread"""
    global scanner_running, scanner_thread
    if not scanner_running:
        scanner_running = True
        scanner_thread = threading.Thread(target=background_scanner, daemon=True)
        scanner_thread.start()
        logger.info("🚀 Background scanner thread started")

# Request tracking middleware
@app.before_request
def track_request():
    """Track all requests for analytics"""
    # Skip static files and API calls
    if request.path.startswith('/static/') or request.path.startswith('/api/'):
        return
    
    # Generate session ID
    session_id = request.cookies.get('session_id')
    if not session_id:
        session_id = str(hash(request.remote_addr + str(time.time())))
    
    # Get IP address
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip_address and ',' in ip_address:
        ip_address = ip_address.split(',')[0].strip()
    
    # Get user agent
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    # Track visitor
    traffic_analytics.track_visitor(session_id, ip_address, user_agent)
    
    # Track page view
    traffic_analytics.track_page_view(session_id, request.path)

# Routes
@app.route('/')
def screener():
    """Main stock screener page"""
    logger.info("📄 Main screener page requested")
    
    # Get filter parameters from URL
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_gap_pct = request.args.get('min_gap_pct', type=str)
    min_rel_vol = request.args.get('min_rel_vol', type=float)
    sector_filter = request.args.get('sector_filter', 'All')
    
    # Additional filters
    max_float = request.args.get('max_float', type=float)
    min_market_cap = request.args.get('min_market_cap', type=float)
    max_market_cap = request.args.get('max_market_cap', type=float)
    min_premarket_volume = request.args.get('min_premarket_volume', type=int)
    min_pe_ratio = request.args.get('min_pe_ratio', type=float)
    max_pe_ratio = request.args.get('max_pe_ratio', type=float)
    min_pre_market = request.args.get('min_pre_market', type=float)
    max_pre_market = request.args.get('max_pre_market', type=float)
    min_pre_market_change = request.args.get('min_pre_market_change', type=float)
    max_pre_market_change = request.args.get('max_pre_market_change', type=float)
    min_post_market = request.args.get('min_post_market', type=float)
    max_post_market = request.args.get('max_post_market', type=float)
    min_post_market_change = request.args.get('min_post_market_change', type=float)
    max_post_market_change = request.args.get('max_post_market_change', type=float)
    
    # Process min_gap_pct (handle special case for 0.0)
    if min_gap_pct == '0.0':
        min_gap_pct = -100.0
    elif min_gap_pct is not None:
        min_gap_pct = float(min_gap_pct)
    
    logger.info(f"🔍 Raw min_gap_pct from URL: '{min_gap_pct}'")
    logger.info(f"🔍 Processed min_gap_pct: {min_gap_pct}")
    
    # Create filter parameters
    filters = FilterParams(
        min_price=min_price if min_price is not None else 0.01,
        max_price=max_price if max_price is not None else 1000.0,
        min_gap_pct=min_gap_pct if min_gap_pct is not None else -100.0,
        min_rel_vol=min_rel_vol if min_rel_vol is not None else 0.0,
        sector_filter=sector_filter,
        max_float=max_float,
        min_market_cap=min_market_cap,
        max_market_cap=max_market_cap,
        min_premarket_volume=min_premarket_volume,
        min_pe_ratio=min_pe_ratio,
        max_pe_ratio=max_pe_ratio,
        min_pre_market=min_pre_market,
        max_pre_market=max_pre_market,
        min_pre_market_change=min_pre_market_change,
        max_pre_market_change=max_pre_market_change,
        min_post_market=min_post_market,
        max_post_market=max_post_market,
        min_post_market_change=min_post_market_change,
        max_post_market_change=max_post_market_change
    )
    
    logger.info(f"🔍 Filters dict: {filters.__dict__}")
    
    # Filter stocks
    filtered_stocks = []
    for stock in stock_cache.values():
        # Basic price filter
        if not (filters.min_price <= stock.price <= filters.max_price):
            continue
        
        # Gap percentage filter
        if stock.change_pct < filters.min_gap_pct:
            continue
        
        # Relative volume filter
        if stock.volume < filters.min_rel_vol:
            continue
        
        # Sector filter
        if filters.sector_filter != 'All' and stock.sector != filters.sector_filter:
            continue
        
        # Additional filters
        if filters.max_float and stock.float and stock.float > filters.max_float:
            continue
        if filters.min_market_cap and stock.market_cap and stock.market_cap < filters.min_market_cap:
            continue
        if filters.max_market_cap and stock.market_cap and stock.market_cap > filters.max_market_cap:
            continue
        if filters.min_premarket_volume and stock.premarket_volume and stock.premarket_volume < filters.min_premarket_volume:
            continue
        if filters.min_pe_ratio and stock.pe_ratio and stock.pe_ratio < filters.min_pe_ratio:
            continue
        if filters.max_pe_ratio and stock.pe_ratio and stock.pe_ratio > filters.max_pe_ratio:
            continue
        if filters.min_pre_market and stock.premarket_price and stock.premarket_price < filters.min_pre_market:
            continue
        if filters.max_pre_market and stock.premarket_price and stock.premarket_price > filters.max_pre_market:
            continue
        if filters.min_pre_market_change and stock.premarket_change and stock.premarket_change < filters.min_pre_market_change:
            continue
        if filters.max_pre_market_change and stock.premarket_change and stock.premarket_change > filters.max_pre_market_change:
            continue
        if filters.min_post_market and stock.postmarket_price and stock.postmarket_price < filters.min_post_market:
            continue
        if filters.max_post_market and stock.postmarket_price and stock.postmarket_price > filters.max_post_market:
            continue
        if filters.min_post_market_change and stock.postmarket_change and stock.postmarket_change < filters.min_post_market_change:
            continue
        if filters.max_post_market_change and stock.postmarket_change and stock.postmarket_change > filters.max_post_market_change:
            continue
        
        filtered_stocks.append(stock)
    
    # Sort by gap percentage (descending)
    filtered_stocks.sort(key=lambda x: x.change_pct, reverse=True)
    
    # Prepare last update display
    last_update_display = "Never"
    if last_update:
        last_update_display = last_update.strftime("%Y-%m-%d %H:%M:%S")
    
    logger.info(f"✅ Main page rendered with {len(filtered_stocks)} filtered stocks")
    
    return render_template('screener.html', 
                         stocks=filtered_stocks, 
                         filters=filters,
                         last_update=last_update_display,
                         total_stocks=len(stock_cache))

@app.route('/api/cache_status')
def cache_status():
    """API endpoint for cache status"""
    return jsonify({
        'total_stocks': len(stock_cache),
        'last_update': last_update.isoformat() if last_update else None,
        'scanner_running': scanner_running
    })

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'stocks_loaded': len(stock_cache),
        'scanner_running': scanner_running
    })

# Initialize app
if __name__ == '__main__':
    # Load initial cache
    scanner.load_cache()
    
    # Start background scanner
    start_background_scanner()
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
else:
    # For production deployment (gunicorn)
    # Load initial cache
    scanner.load_cache()
    
    # Start background scanner
    start_background_scanner() 