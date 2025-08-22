#!/usr/bin/env python3
"""
Poppalyze - Modern Production App
Catch the pop. Own the trade.

A streamlined stock screener using modern Python patterns.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
from contextlib import contextmanager
from functools import lru_cache
import asyncio
import json
import time
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
CACHE_FILE = Path("stock_cache.json")
SCAN_INTERVAL = 300

@dataclass
class StockData:
    """Stock data structure"""
    symbol: str
    price: float
    gap_pct: float
    volume: int
    relative_volume: float
    market_cap_formatted: str
    category: str

@dataclass
class FilterParams:
    """Filter parameters"""
    min_price: float = 1.0
    max_price: float = 2000.0
    min_gap_pct: float = -100.0
    max_gap_pct: float = 100.0
    min_rel_vol: float = 0.0
    sector_filter: str = "All"

@dataclass
class CacheStatus:
    """Cache status information"""
    status: str
    message: str
    age_minutes: float
    is_fresh: bool
    stock_count: int

class StockScanner:
    """Modern stock data scanner with type hints and efficient patterns"""
    
    def __init__(self) -> None:
        self.cache: Dict[str, Any] = {}
        self.cache_lock = threading.RLock()
        self.scanner_running = False
        self._scan_count = 0
    
    @contextmanager
    def cache_context(self):
        """Context manager for thread-safe cache access"""
        with self.cache_lock:
            yield self.cache
    
    def load_cache(self) -> Optional[Dict[str, Any]]:
        """Load cache from file using pathlib"""
        try:
            if CACHE_FILE.exists():
                return json.loads(CACHE_FILE.read_text())
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        return None
    
    def save_cache(self, data: Dict[str, Any]) -> bool:
        """Save cache to file using pathlib"""
        try:
            CACHE_FILE.write_text(json.dumps(data, indent=2))
            return True
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
            return False
    
    @staticmethod
    def format_market_cap(market_cap: Optional[float]) -> str:
        """Format market cap using modern f-string patterns"""
        if not market_cap:
            return 'N/A'
        
        # Use match statement for cleaner logic (Python 3.10+)
        match market_cap:
            case cap if cap >= 1e12:
                return f"${cap/1e12:.1f}T"
            case cap if cap >= 1e9:
                return f"${cap/1e9:.1f}B"
            case cap if cap >= 1e6:
                return f"${cap/1e6:.1f}M"
            case _:
                return f"${market_cap:,.0f}"
    
    def scan_stocks(self) -> Optional[Dict[str, Any]]:
        """Fetch stock data using modern patterns"""
        try:
            logger.info("Starting stock scan...")
            start_time = time.perf_counter()
            
            import yfinance as yf
            
            # Define stocks using set for O(1) lookup
            stocks = {
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC',
                'PLTR', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'SOFI', 'HOOD', 'COIN', 'SQ',
                'GME', 'AMC', 'BBBY', 'SNDL', 'TLRY', 'HEXO', 'ACB', 'CGC', 'APHA', 'CRON',
                'SPY', 'QQQ', 'IWM', 'TQQQ', 'SQQQ', 'UVXY', 'VXX', 'VIXY'
            }
            
            # Use dict comprehension for cleaner code
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
                        
                        stock_data[symbol] = StockData(
                            symbol=symbol,
                            price=current_price,
                            gap_pct=round(gap_pct, 2),
                            volume=volume,
                            relative_volume=round(volume / avg_volume, 1) if avg_volume else 0,
                            market_cap_formatted=self.format_market_cap(info.get('marketCap')),
                            category='Technology' if symbol in {'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'AMD', 'INTC'} else 'Other'
                        )
                    
                    time.sleep(0.1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching {symbol}: {e}")
                    continue
            
            scan_duration = time.perf_counter() - start_time
            
            # Create cache data using dataclass-like structure
            cache_data = {
                'stocks': {symbol: stock.__dict__ for symbol, stock in stock_data.items()},
                'last_update': time.time(),
                'scan_duration': round(scan_duration, 1),
                'total_stocks': len(stock_data)
            }
            
            # Use context manager for thread-safe access
            with self.cache_context() as cache:
                cache.update(cache_data)
            
            self.save_cache(cache_data)
            
            logger.info(f"Stock scan completed: {len(stock_data)}/{len(stocks)} stocks in {scan_duration:.1f}s")
            return cache_data
            
        except Exception as e:
            logger.error(f"Error in stock scan: {e}")
            return None
    
    def start_background_scanner(self) -> None:
        """Start background scanning thread"""
        if not self.scanner_running:
            self.scanner_running = True
            thread = threading.Thread(target=self._background_scan_loop, daemon=True)
            thread.start()
            logger.info("Background scanner started")
    
    def _background_scan_loop(self) -> None:
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

@lru_cache(maxsize=1)
def get_cache_status() -> CacheStatus:
    """Get cache status with caching for performance"""
    with scanner.cache_context() as cache:
        if not cache:
            return CacheStatus(
                status='No data',
                message='No cache data available',
                age_minutes=float('inf'),
                is_fresh=False,
                stock_count=0
            )
        
        age_minutes = (time.time() - cache.get('last_update', 0)) / 60
        
        return CacheStatus(
            status='Fresh' if age_minutes < 5 else 'Stale' if age_minutes < 30 else 'Old',
            message=f"Data is {'fresh' if age_minutes < 5 else 'stale' if age_minutes < 30 else 'old'} ({age_minutes:.1f} minutes old)",
            age_minutes=age_minutes,
            is_fresh=age_minutes < 5,
            stock_count=len(cache.get('stocks', {}))
        )

def filter_stocks(stocks_data: Dict[str, Any], filters: FilterParams) -> List[Dict[str, Any]]:
    """Filter stocks using modern patterns"""
    if not stocks_data:
        return []
    
    # Use list comprehension with walrus operator for efficiency
    filtered = [
        stock for stock in stocks_data.values()
        if (filters.min_price <= stock['price'] <= filters.max_price and
            filters.min_gap_pct <= stock['gap_pct'] <= filters.max_gap_pct and
            stock['relative_volume'] >= filters.min_rel_vol and
            (filters.sector_filter == 'All' or stock['category'] == filters.sector_filter))
    ]
    
    # Sort by gap percentage (absolute value) using key function
    filtered.sort(key=lambda x: abs(x['gap_pct']), reverse=True)
    return filtered

def get_top_stocks(stocks_data: Dict[str, Any], key_func: callable, limit: int = 5) -> List[Dict[str, Any]]:
    """Generic function to get top stocks by any criteria"""
    if not stocks_data:
        return []
    
    stocks = list(stocks_data.values())
    stocks.sort(key=key_func, reverse=True)
    return stocks[:limit]

def parse_filters() -> FilterParams:
    """Parse filter parameters using modern patterns"""
    return FilterParams(
        min_price=float(request.args.get('min_price', 1.0)),
        max_price=float(request.args.get('max_price', 2000.0)),
        min_gap_pct=float(request.args.get('min_gap_pct', -100.0)),
        max_gap_pct=float(request.args.get('max_gap_pct', 100.0)),
        min_rel_vol=float(request.args.get('min_rel_vol', 0.0)),
        sector_filter=request.args.get('sector_filter', 'All')
    )

@app.route("/")
def screener() -> str:
    """Main screener page using modern patterns"""
    # Parse filters using dataclass
    filters = parse_filters()
    
    # Get independent filter states
    quick_movers_independent = request.args.get('quick_movers_independent', 'true') == 'true'
    top_gappers_independent = request.args.get('top_gappers_independent', 'true') == 'true'
    
    # Get cache data using context manager
    with scanner.cache_context() as cache:
        stocks_data = cache.get('stocks', {})
        cache_status = get_cache_status()
    
    # Filter stocks
    filtered_stocks = filter_stocks(stocks_data, filters)
    
    # Get top sections using generic function
    stocks_for_quick_movers = stocks_data if quick_movers_independent else {s['symbol']: s for s in filtered_stocks}
    stocks_for_top_gappers = stocks_data if top_gappers_independent else {s['symbol']: s for s in filtered_stocks}
    
    quick_movers = get_top_stocks(stocks_for_quick_movers, lambda x: x['relative_volume'], 5)
    top_gappers = get_top_stocks(stocks_for_top_gappers, lambda x: abs(x['gap_pct']), 5)
    top_positive_gappers = get_top_stocks(stocks_data, lambda x: x['gap_pct'], 5)
    
    # Get unique sectors using set comprehension
    sectors = sorted({stock['category'] for stock in stocks_data.values()})
    
    return render_template('screener.html',
        stocks=filtered_stocks,
        quick_movers=quick_movers,
        top_gappers=top_gappers,
        top_positive_gappers=top_positive_gappers,
        filters=filters.__dict__,
        quick_movers_independent=quick_movers_independent,
        top_gappers_independent=top_gappers_independent,
        sectors=sectors,
        total_stocks=len(stocks_data),
        filtered_count=len(filtered_stocks),
        cache_status=cache_status.__dict__
    )

@app.route("/api/cache_status")
def api_cache_status() -> Dict[str, Any]:
    """API endpoint for cache status"""
    return jsonify(get_cache_status().__dict__)

@app.route("/health")
def health() -> Dict[str, Any]:
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'cache_status': get_cache_status().__dict__
    })

def initialize_app() -> None:
    """Initialize the application using modern patterns"""
    logger.info("Initializing Poppalyze...")
    
    # Load existing cache
    if existing_cache := scanner.load_cache():
        with scanner.cache_context() as cache:
            cache.update(existing_cache)
        logger.info(f"Loaded existing cache with {len(existing_cache.get('stocks', {}))} stocks")
    
    # Start background scanner
    scanner.start_background_scanner()
    
    logger.info("Poppalyze initialized successfully")

if __name__ == "__main__":
    initialize_app()
    app.run(host='0.0.0.0', port=5001, debug=False) 