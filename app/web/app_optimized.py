#!/usr/bin/env python3
"""
Poppalyze - Optimized Production App
Catch the pop. Own the trade.

A streamlined stock screener with minimal, efficient code.
"""

from flask import Flask, render_template, request, jsonify
import json
import time
import os
import threading
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
CACHE_FILE = "stock_cache.json"
SCAN_INTERVAL = 300

class StockScanner:
    """Handles stock data scanning and caching"""
    
    def __init__(self):
        self.cache = {}
        self.cache_lock = threading.RLock()
        self.scanner_running = False
    
    def load_cache(self):
        """Load cache from file"""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        return None
    
    def save_cache(self, data):
        """Save cache to file"""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False
    
    def format_market_cap(self, market_cap):
        """Format market cap for display"""
        if not market_cap:
            return 'N/A'
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.1f}M"
        return f"${market_cap:,.0f}"
    
    def scan_stocks(self):
        """Fetch stock data from yfinance"""
        try:
            logger.info("Starting stock scan...")
            start_time = time.time()
            
            import yfinance as yf
            
            # Define stocks to scan
            stocks = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
                'PLTR', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'SOFI', 'HOOD', 'COIN', 'SQ',
                'GME', 'AMC', 'BBBY', 'SNDL', 'TLRY', 'HEXO', 'ACB', 'CGC', 'APHA', 'CRON',
                'SPY', 'QQQ', 'IWM', 'TQQQ', 'SQQQ', 'UVXY', 'VXX', 'VIXY'
            ]
            
            stock_data = {}
            
            for symbol in stocks:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    current_price = info.get('currentPrice', 0)
                    previous_close = info.get('previousClose', current_price)
                    
                    if current_price and previous_close:
                        gap_pct = ((current_price - previous_close) / previous_close) * 100
                        volume = info.get('volume', 0)
                        avg_volume = info.get('averageVolume', 0)
                        
                        stock_data[symbol] = {
                            'symbol': symbol,
                            'price': current_price,
                            'gap_pct': round(gap_pct, 2),
                            'volume': volume,
                            'relative_volume': round(volume / avg_volume, 1) if avg_volume else 0,
                            'market_cap_formatted': self.format_market_cap(info.get('marketCap', 0)),
                            'category': 'Technology' if symbol in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC'] else 'Other'
                        }
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching {symbol}: {e}")
                    continue
            
            scan_duration = time.time() - start_time
            
            # Create cache data
            cache_data = {
                'stocks': stock_data,
                'last_update': time.time(),
                'scan_duration': round(scan_duration, 1),
                'total_stocks': len(stock_data)
            }
            
            # Save to cache
            with self.cache_lock:
                self.cache = cache_data
            
            self.save_cache(cache_data)
            
            logger.info(f"Stock scan completed: {len(stock_data)}/{len(stocks)} stocks in {scan_duration:.1f}s")
            return cache_data
            
        except Exception as e:
            logger.error(f"Error in stock scan: {e}")
            return None
    
    def start_background_scanner(self):
        """Start background scanning thread"""
        if not self.scanner_running:
            self.scanner_running = True
            thread = threading.Thread(target=self._background_scan_loop, daemon=True)
            thread.start()
            logger.info("Background scanner started")
    
    def _background_scan_loop(self):
        """Background scanning loop"""
        while self.scanner_running:
            try:
                self.scan_stocks()
                time.sleep(SCAN_INTERVAL)
            except Exception as e:
                logger.error(f"Background scanner error: {e}")
                time.sleep(60)

# Initialize scanner
scanner = StockScanner()

def get_cache_status():
    """Get cache status information"""
    with scanner.cache_lock:
        if not scanner.cache:
            return {
                'status': 'No data',
                'message': 'No cache data available',
                'age_minutes': float('inf'),
                'is_fresh': False,
                'stock_count': 0
            }
        
        age_minutes = (time.time() - scanner.cache.get('last_update', 0)) / 60
        
        return {
            'status': 'Fresh' if age_minutes < 5 else 'Stale' if age_minutes < 30 else 'Old',
            'message': f"Data is {'fresh' if age_minutes < 5 else 'stale' if age_minutes < 30 else 'old'} ({age_minutes:.1f} minutes old)",
            'age_minutes': age_minutes,
            'is_fresh': age_minutes < 5,
            'stock_count': len(scanner.cache.get('stocks', {}))
        }

def filter_stocks(stocks_data, **filters):
    """Filter stocks based on criteria"""
    if not stocks_data:
        return []
    
    filtered = []
    
    for symbol, stock in stocks_data.items():
        # Apply filters
        if (filters.get('min_price') and stock['price'] < filters['min_price'] or
            filters.get('max_price') and stock['price'] > filters['max_price'] or
            filters.get('min_gap_pct') and stock['gap_pct'] < filters['min_gap_pct'] or
            filters.get('max_gap_pct') and stock['gap_pct'] > filters['max_gap_pct'] or
            filters.get('min_rel_vol') and stock['relative_volume'] < filters['min_rel_vol'] or
            filters.get('sector_filter') and filters['sector_filter'] != 'All' and stock['category'] != filters['sector_filter']):
            continue
        
        filtered.append(stock)
    
    # Sort by gap percentage (absolute value)
    filtered.sort(key=lambda x: abs(x['gap_pct']), reverse=True)
    return filtered

def get_top_stocks(stocks_data, key_func, limit=5):
    """Generic function to get top stocks by any criteria"""
    if not stocks_data:
        return []
    
    stocks = list(stocks_data.values())
    stocks.sort(key=key_func, reverse=True)
    return stocks[:limit]

@app.route("/")
def screener():
    """Main screener page"""
    # Get filter parameters
    filters = {
        'min_price': float(request.args.get('min_price', 1.0)),
        'max_price': float(request.args.get('max_price', 2000.0)),
        'min_gap_pct': float(request.args.get('min_gap_pct', -100.0)),
        'max_gap_pct': float(request.args.get('max_gap_pct', 100.0)),
        'min_rel_vol': float(request.args.get('min_rel_vol', 0.0)),
        'sector_filter': request.args.get('sector_filter', 'All')
    }
    
    # Get independent filter states
    quick_movers_independent = request.args.get('quick_movers_independent', 'true') == 'true'
    top_gappers_independent = request.args.get('top_gappers_independent', 'true') == 'true'
    
    # Get cache data
    with scanner.cache_lock:
        stocks_data = scanner.cache.get('stocks', {})
        cache_status = get_cache_status()
    
    # Filter stocks
    filtered_stocks = filter_stocks(stocks_data, **filters)
    
    # Get top sections using generic function
    stocks_for_quick_movers = stocks_data if quick_movers_independent else filtered_stocks
    stocks_for_top_gappers = stocks_data if top_gappers_independent else filtered_stocks
    
    quick_movers = get_top_stocks(stocks_for_quick_movers, lambda x: x['relative_volume'], 5)
    top_gappers = get_top_stocks(stocks_for_top_gappers, lambda x: abs(x['gap_pct']), 5)
    top_positive_gappers = get_top_stocks(stocks_data, lambda x: x['gap_pct'], 5)
    
    # Get unique sectors
    sectors = sorted(set(stock['category'] for stock in stocks_data.values()))
    
    return render_template('screener.html',
        stocks=filtered_stocks,
        quick_movers=quick_movers,
        top_gappers=top_gappers,
        top_positive_gappers=top_positive_gappers,
        filters=filters,
        quick_movers_independent=quick_movers_independent,
        top_gappers_independent=top_gappers_independent,
        sectors=sectors,
        total_stocks=len(stocks_data),
        filtered_count=len(filtered_stocks),
        cache_status=cache_status
    )

@app.route("/api/cache_status")
def api_cache_status():
    """API endpoint for cache status"""
    return jsonify(get_cache_status())

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_status': get_cache_status()
    })

def initialize_app():
    """Initialize the application"""
    logger.info("Initializing Poppalyze...")
    
    # Load existing cache
    existing_cache = scanner.load_cache()
    if existing_cache:
        with scanner.cache_lock:
            scanner.cache = existing_cache
        logger.info(f"Loaded existing cache with {len(existing_cache.get('stocks', {}))} stocks")
    
    # Start background scanner
    scanner.start_background_scanner()
    
    logger.info("Poppalyze initialized successfully")

if __name__ == "__main__":
    initialize_app()
    app.run(host='0.0.0.0', port=5001, debug=False) 