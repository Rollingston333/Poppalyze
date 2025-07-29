#!/usr/bin/env python3
"""
Poppalyze - Streamlined Production App
Catch the pop. Own the trade.

A streamlined stock screener with elegant conditional handling.
"""

from __future__ import annotations
import os
import json
import time
import signal
import sqlite3
import uuid
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
from contextlib import contextmanager
import yfinance as yf
from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import time
import uuid
import logging
import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
import yfinance as yf
from flask import Flask, render_template, request, jsonify, Response
import concurrent.futures
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Constants
CACHE_FILE = Path('stock_cache.json')
TRAFFIC_DB = Path('traffic_analytics.db')
SCANNER_INTERVAL = 300  # 5 minutes

# =====================================================
# ENUMERATIONS
# =====================================================

class CacheStatus(Enum):
    FRESH = "fresh"
    STALE = "stale"
    MISSING = "missing"
    ERROR = "error"

class Sector(Enum):
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    FINANCIAL = "Financial"
    CONSUMER = "Consumer"
    ENERGY = "Energy"
    INDUSTRIAL = "Industrial"
    MATERIALS = "Materials"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    COMMUNICATION = "Communication"

# =====================================================
# DATACLASSES
# =====================================================

@dataclass
class StockData:
    symbol: str
    price: float
    previous_close: float
    gap_pct: float
    volume: int
    relative_volume: float
    market_cap_formatted: str
    volume_formatted: str
    category: str
    pre_market_price: Optional[float] = None
    pre_market_change_pct: Optional[float] = None
    post_market_price: Optional[float] = None
    post_market_change_pct: Optional[float] = None
    gap_classification: str = "REGULAR"

@dataclass
class FilterParams:
    min_price: float = 0.01  # Allow penny stocks
    max_price: float = 1000.0  # Allow higher priced stocks
    min_gap_pct: float = -100.0  # Allow all gap percentages
    min_rel_vol: float = 0.0
    sector_filter: str = "All"
    max_float: Optional[float] = None
    min_market_cap: Optional[float] = None
    max_market_cap: Optional[float] = None
    min_premarket_volume: Optional[float] = None
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
        """Validate filter parameters - only apply reasonable bounds, don't override user input"""
        # Only validate if values are completely unreasonable, not if they're just outside normal ranges
        if self.min_price < 0:
            self.min_price = 0.0
        if self.max_price <= 0:
            self.max_price = 1000.0
        # Don't override min_gap_pct - let users set any reasonable value
        # Don't override min_rel_vol - let users set any reasonable value

@dataclass
class CacheInfo:
    status: CacheStatus
    last_update: Optional[float] = None
    stock_count: int = 0
    message: str = ""
    age_minutes: float = 0.0

# =====================================================
# STRATEGY PATTERNS
# =====================================================

class MarketCapFormatter:
    @staticmethod
    def format(market_cap: Optional[float]) -> str:
        if not market_cap or market_cap <= 0:
            return "N/A"
        
        if market_cap >= 1e12:
            return f"${market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"${market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"${market_cap/1e6:.1f}M"
        else:
            return f"${market_cap:,.0f}"

class VolumeFormatter:
    @staticmethod
    def format(volume: Optional[int]) -> str:
        if not volume or volume <= 0:
            return "N/A"
        return f"{volume:,}"

class GapClassifier:
    @staticmethod
    def classify(gap_pct: float) -> str:
        if gap_pct >= 20:
            return "EXPLOSIVE"
        elif gap_pct >= 10:
            return "HUGE"
        elif gap_pct >= 5:
            return "BIG"
        elif gap_pct <= -10:
            return "DOWN"
        elif gap_pct <= -5:
            return "LOSER"
        else:
            return "REGULAR"

# =====================================================
# TRAFFIC ANALYTICS
# =====================================================

class GeolocationTracker:
    """Track visitor geolocation using IP addresses"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    def get_location(self, ip_address: str) -> Dict[str, str]:
        """Get location data for an IP address"""
        # Skip localhost and private IPs
        if self._is_private_ip(ip_address):
            return {'country': 'Local', 'city': 'Local', 'region': 'Local'}
        
        # Check cache first
        if ip_address in self.cache:
            cache_time, location_data = self.cache[ip_address]
            if time.time() - cache_time < self.cache_ttl:
                return location_data
        
        try:
            # Use free IP geolocation service
            response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    location_data = {
                        'country': data.get('country', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'region': data.get('regionName', 'Unknown'),
                        'timezone': data.get('timezone', 'Unknown'),
                        'isp': data.get('isp', 'Unknown')
                    }
                    # Cache the result
                    self.cache[ip_address] = (time.time(), location_data)
                    return location_data
        except Exception as e:
            logger.warning(f"⚠️ Geolocation lookup failed for {ip_address}: {e}")
        
        return {'country': 'Unknown', 'city': 'Unknown', 'region': 'Unknown'}
    
    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP address is private/local"""
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return True
        
        # Check for private IP ranges
        try:
            parts = ip_address.split('.')
            if len(parts) == 4:
                first_octet = int(parts[0])
                if first_octet == 10 or (first_octet == 172 and 16 <= int(parts[1]) <= 31) or (first_octet == 192 and int(parts[1]) == 168):
                    return True
        except:
            pass
        
        return False

class TrafficAnalytics:
    def __init__(self, db_path=TRAFFIC_DB):
        self.db_path = db_path
        self.geolocation = GeolocationTracker()
        self.init_database()
    
    def init_database(self):
        """Initialize the traffic analytics database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create visitors table with geolocation columns
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS visitors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE,
                        ip_address TEXT,
                        user_agent TEXT,
                        country TEXT,
                        city TEXT,
                        region TEXT,
                        first_visit TIMESTAMP,
                        last_visit TIMESTAMP,
                        visit_count INTEGER DEFAULT 1
                    )
                ''')
                
                # Create page_views table with geolocation columns
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS page_views (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        page_url TEXT,
                        timestamp TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT,
                        referrer TEXT,
                        country TEXT,
                        city TEXT,
                        region TEXT
                    )
                ''')
                
                # Create api_calls table with geolocation columns
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_calls (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT,
                        endpoint TEXT,
                        timestamp TIMESTAMP,
                        ip_address TEXT,
                        user_agent TEXT,
                        country TEXT,
                        city TEXT,
                        region TEXT
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
                
                # Add geolocation columns to existing tables if they don't exist
                try:
                    cursor.execute('ALTER TABLE visitors ADD COLUMN country TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE visitors ADD COLUMN city TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE visitors ADD COLUMN region TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE page_views ADD COLUMN country TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE page_views ADD COLUMN city TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE page_views ADD COLUMN region TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE api_calls ADD COLUMN country TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE api_calls ADD COLUMN city TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                try:
                    cursor.execute('ALTER TABLE api_calls ADD COLUMN region TEXT')
                except sqlite3.OperationalError:
                    pass  # Column already exists
                
                conn.commit()
                logger.info("✅ Traffic analytics database initialized")
                
        except Exception as e:
            logger.error(f"❌ Error initializing traffic analytics database: {e}")
    
    def track_visitor(self, session_id, ip_address, user_agent):
        """Track a visitor session"""
        try:
            # Get geolocation data
            location = self.geolocation.get_location(ip_address)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if visitor already exists
                cursor.execute('''
                    SELECT id, visit_count FROM visitors WHERE session_id = ?
                ''', (session_id,))
                
                result = cursor.fetchone()
                current_time = datetime.now()
                
                if result:
                    # Update existing visitor
                    visitor_id, visit_count = result
                    cursor.execute('''
                        UPDATE visitors 
                        SET last_visit = ?, visit_count = ?, ip_address = ?, user_agent = ?, 
                            country = ?, city = ?, region = ?
                        WHERE id = ?
                    ''', (current_time, visit_count + 1, ip_address, user_agent, 
                          location['country'], location['city'], location['region'], visitor_id))
                else:
                    # Create new visitor
                    cursor.execute('''
                        INSERT INTO visitors (session_id, ip_address, user_agent, country, city, region, 
                                            first_visit, last_visit, visit_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (session_id, ip_address, user_agent, location['country'], location['city'], 
                          location['region'], current_time, current_time))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error tracking visitor: {e}")
    
    def track_page_view(self, session_id, page_url, ip_address, user_agent, referrer=None):
        """Track a page view"""
        try:
            # Get geolocation data
            location = self.geolocation.get_location(ip_address)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO page_views (session_id, page_url, timestamp, ip_address, user_agent, 
                                          referrer, country, city, region)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, page_url, datetime.now(), ip_address, user_agent, 
                      referrer, location['country'], location['city'], location['region']))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error tracking page view: {e}")
    
    def track_api_call(self, session_id, endpoint, ip_address, user_agent):
        """Track an API call"""
        try:
            # Get geolocation data
            location = self.geolocation.get_location(ip_address)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO api_calls (session_id, endpoint, timestamp, ip_address, user_agent,
                                         country, city, region)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, endpoint, datetime.now(), ip_address, user_agent,
                      location['country'], location['city'], location['region']))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")

# Initialize traffic analytics
traffic_analytics = TrafficAnalytics()

# =====================================================
# FUNCTIONAL COMPONENTS
# =====================================================

class StockFilter:
    @staticmethod
    def apply(stocks: List[StockData], filters: FilterParams) -> List[StockData]:
        """Apply filters to stock data"""
        return list(filter(lambda stock: StockFilter._matches_filters(stock, filters), stocks))
    
    @staticmethod
    def _matches_filters(stock: StockData, filters: FilterParams) -> bool:
        """Check if stock matches all filters"""
        # Price filter
        if not (filters.min_price <= stock.price <= filters.max_price):
            return False
        
        # Gap percentage filter
        if stock.gap_pct < filters.min_gap_pct:
            return False
        
        # Relative volume filter
        if stock.relative_volume < filters.min_rel_vol:
            return False
        
        # Sector filter
        if filters.sector_filter != "All" and stock.category != filters.sector_filter:
            return False
        
        return True

class StockSorter:
    @staticmethod
    def by_gap_pct(stocks: List[StockData], reverse: bool = True) -> List[StockData]:
        """Sort stocks by gap percentage"""
        return sorted(stocks, key=lambda x: x.gap_pct, reverse=reverse)
    
    @staticmethod
    def by_relative_volume(stocks: List[StockData], reverse: bool = True) -> List[StockData]:
        """Sort stocks by relative volume"""
        return sorted(stocks, key=lambda x: x.relative_volume, reverse=reverse)

class CacheStatusCalculator:
    @staticmethod
    def calculate(cache_data: Optional[Dict]) -> CacheInfo:
        """Calculate cache status"""
        if not cache_data:
            return CacheInfo(status=CacheStatus.MISSING, message="No cache data")
        
        last_update = cache_data.get('last_update')
        if not last_update:
            return CacheInfo(status=CacheStatus.ERROR, message="Invalid cache format")
        
        age = time.time() - last_update
        age_minutes = age / 60
        stock_count = len(cache_data.get('stocks', []))
        
        if age < 300:  # 5 minutes
            return CacheInfo(
                status=CacheStatus.FRESH,
                last_update=last_update,
                stock_count=stock_count,
                age_minutes=age_minutes,
                message=f"Data is fresh ({age_minutes:.1f} minutes old)"
            )
        else:
            return CacheInfo(
                status=CacheStatus.STALE,
                last_update=last_update,
                stock_count=stock_count,
                age_minutes=age_minutes,
                message=f"Data is stale ({age_minutes:.1f} minutes old)"
            )

class StockSelector:
    @staticmethod
    def get_top_gappers(stocks: List[StockData], limit: int = 5) -> List[StockData]:
        """Get top gappers (both positive and negative)"""
        return StockSorter.by_gap_pct(stocks)[:limit]
    
    @staticmethod
    def get_top_positive_gappers(stocks: List[StockData], limit: int = 5) -> List[StockData]:
        """Get top positive gappers only"""
        positive_stocks = [s for s in stocks if s.gap_pct > 0]
        return StockSorter.by_gap_pct(positive_stocks)[:limit]
    
    @staticmethod
    def get_quick_movers(stocks: List[StockData], limit: int = 5) -> List[StockData]:
        """Get stocks with high relative volume"""
        return StockSorter.by_relative_volume(stocks)[:limit]

# =====================================================
# STOCK SCANNER CLASS
# =====================================================

class StockScanner:
    def __init__(self):
        self.cache: Dict = {}
        self.cache_lock = threading.RLock()
        self.last_scan_time: float = 0
        self.scanner_running: bool = False
        self.scan_count: int = 0
        
        # Load existing cache
        self.load_cache()
        
        # Start background scanner
        self.start_background_scanner()
    
    def load_cache(self) -> None:
        """Load cache from file"""
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, 'r') as f:
                    cache_data = json.load(f)
                
                # Reconstruct StockData objects from dictionaries
                stocks_dict = cache_data.get('stocks', {})
                reconstructed_stocks = {}
                
                for symbol, stock_dict in stocks_dict.items():
                    if isinstance(stock_dict, dict):
                        # Filter out any fields that don't belong in StockData
                        valid_fields = {
                            'symbol', 'price', 'previous_close', 'gap_pct', 'volume', 
                            'relative_volume', 'market_cap_formatted', 'volume_formatted', 
                            'category', 'pre_market_price', 'pre_market_change_pct', 
                            'post_market_price', 'post_market_change_pct', 'gap_classification'
                        }
                        
                        # Only include valid fields
                        filtered_dict = {k: v for k, v in stock_dict.items() if k in valid_fields}
                        
                        # Convert dictionary back to StockData object
                        try:
                            stock_data = StockData(**filtered_dict)
                            reconstructed_stocks[symbol] = stock_data
                        except Exception as e:
                            logger.warning(f"⚠️ Error reconstructing {symbol}: {e}")
                            continue
                    else:
                        # Already a StockData object (from old cache format)
                        reconstructed_stocks[symbol] = stock_dict
                
                # Update cache with reconstructed data
                self.cache = {
                    'stocks': reconstructed_stocks,
                    'last_update': cache_data.get('last_update'),
                    'scan_count': cache_data.get('scan_count'),
                    'scan_type': cache_data.get('scan_type')
                }
                
                logger.info(f"✅ Cache loaded with {len(reconstructed_stocks)} stocks")
            else:
                logger.warning("⚠️ No cache file found")
                self.cache = {'stocks': {}, 'last_update': None, 'scan_count': 0, 'scan_type': None}
                
        except Exception as e:
            logger.error(f"⚠️ Error loading cache: {e}")
            self.cache = {'stocks': {}, 'last_update': None, 'scan_count': 0, 'scan_type': None}
    
    def save_cache(self) -> None:
        """Save cache to file"""
        try:
            # Convert StockData objects to dictionaries for JSON serialization
            cache_dict = {
                'last_update': self.cache.get('last_update'),
                'scan_count': self.cache.get('scan_count'),
                'scan_type': self.cache.get('scan_type'),
                'stocks': {}
            }
            
            # Convert each StockData object to a dictionary
            for symbol, stock_data in self.cache.get('stocks', {}).items():
                if hasattr(stock_data, '__dict__'):
                    cache_dict['stocks'][symbol] = stock_data.__dict__
                else:
                    cache_dict['stocks'][symbol] = stock_data
            
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_dict, f, indent=2)
            logger.info("✅ Cache saved successfully")
        except Exception as e:
            logger.error(f"⚠️ Error saving cache: {e}")
    
    def scan_stocks(self) -> None:
        """Scan stocks and update cache"""
        logger.info("🔍 Starting stock scan...")
        start_time = time.perf_counter()
        
        try:
            # Use a comprehensive list of stocks that are likely to have gaps
            # This includes popular stocks, meme stocks, and stocks that frequently gap
            comprehensive_symbols = [
                # Major Tech Stocks
                'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE',
                'CRM', 'ORCL', 'INTC', 'AMD', 'QCOM', 'TXN', 'AVGO', 'MU', 'ADI', 'KLAC',
                
                # EV and Auto Stocks
                'RIVN', 'LCID', 'NIO', 'XPEV', 'LI', 'F', 'GM', 'TM', 'HMC', 'TSLA',
                
                # Meme Stocks and High Volatility
                'GME', 'AMC', 'BBBY', 'SNDL', 'TLRY', 'HEXO', 'ACB', 'CGC', 'APHA', 'CRON',
                'MARA', 'RIOT', 'COIN', 'HOOD', 'PLTR', 'WISH', 'CLOV', 'WKHS', 'NKLA', 'HYLN',
                
                # Chinese Tech Stocks
                'BABA', 'JD', 'PDD', 'BIDU', 'TME', 'NTES', 'IQ', 'BILI', 'DOYU', 'ZTO',
                
                # Growth and Speculative Stocks
                'SPCE', 'RBLX', 'SNAP', 'PINS', 'ZM', 'DASH', 'UBER', 'LYFT', 'SQ', 'PYPL',
                'SHOP', 'ROKU', 'ZM', 'DOCU', 'TWLO', 'OKTA', 'CRWD', 'ZS', 'NET', 'DDOG',
                
                # Biotech and Healthcare
                'MRNA', 'BNTX', 'PFE', 'JNJ', 'UNH', 'ABBV', 'TMO', 'DHR', 'BMY', 'AMGN',
                'GILD', 'REGN', 'VRTX', 'BIIB', 'ILMN', 'DXCM', 'ISRG', 'ABT', 'TXN', 'MDT',
                
                # Financial and Banking
                'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'TFC', 'COF',
                
                # Energy and Commodities
                'XOM', 'CVX', 'COP', 'EOG', 'SLB', 'HAL', 'BKR', 'VLO', 'MPC', 'PSX',
                
                # ETFs and Index Funds
                'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'TQQQ', 'SQQQ', 'UVXY', 'VXX', 'VIXY',
                
                # Penny Stocks and Small Caps
                'TNFA', 'HCTI', 'PROK', 'BMBL', 'BTCM', 'VWAV', 'IREN', 'EBON', 'STEM',
                
                # Additional Popular Stocks
                'DIS', 'NKE', 'SBUX', 'MCD', 'KO', 'PEP', 'WMT', 'HD', 'LOW', 'COST',
                'TGT', 'CVS', 'WBA', 'ABT', 'TMO', 'DHR', 'BMY', 'AMGN', 'GILD', 'REGN'
            ]
            
            stocks_data = {}
            successful_scans = 0
            failed_scans = 0
            
            logger.info(f"🎯 Scanning {len(comprehensive_symbols)} symbols")
            
            for symbol in comprehensive_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    stock_data = self._create_stock_data(symbol, info)
                    if stock_data:
                        stocks_data[symbol] = stock_data
                        successful_scans += 1
                    else:
                        failed_scans += 1
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.05)  # Reduced delay for faster scanning
                    
                except Exception as e:
                    failed_scans += 1
                    # Only log specific errors, not all 404s
                    if "404" not in str(e):
                        logger.warning(f"⚠️ Error scanning {symbol}: {e}")
                    continue
            
            # Update cache
            with self.cache_lock:
                self.cache = {
                    'stocks': stocks_data,
                    'last_update': time.time(),
                    'scan_count': self.scan_count + 1,
                    'scan_type': 'comprehensive_scan'
                }
                self.scan_count += 1
            
            # Save cache
            self.save_cache()
            
            elapsed_time = time.perf_counter() - start_time
            logger.info(f"🎉 Stock scan completed: {successful_scans}/{len(comprehensive_symbols)} stocks in {elapsed_time:.1f}s")
            if failed_scans > 0:
                logger.info(f"⚠️ Failed scans: {failed_scans}")
            
        except Exception as e:
            logger.error(f"⚠️ Error during stock scan: {e}")
            # Don't update cache on error, keep existing data
    
    def _create_stock_data(self, symbol: str, info: Dict[str, Any]) -> Optional[StockData]:
        """Create stock data with comprehensive information"""
        try:
            current_price = info.get('currentPrice', 0)
            previous_close = info.get('regularMarketPreviousClose', current_price)
            open_price = info.get('regularMarketOpen', current_price)
            market_state = info.get('marketState', 'REGULAR')
            
            if not (current_price and previous_close):
                return None
            
            # Calculate gap percentage - always use current price vs previous close
            gap_pct = ((current_price - previous_close) / previous_close) * 100
            
            volume = info.get('volume', 0)
            avg_volume = info.get('averageVolume', volume)
            
            # Get pre/post market data
            pre_market_price = info.get('preMarketPrice')
            post_market_price = info.get('postMarketPrice')
            
            pre_market_change_pct = None
            if pre_market_price and previous_close:
                pre_market_change_pct = ((pre_market_price - previous_close) / previous_close) * 100
            
            post_market_change_pct = None
            if post_market_price and previous_close:
                post_market_change_pct = ((post_market_price - previous_close) / previous_close) * 100
            
            # Create stock data
            stock_data = StockData(
                symbol=symbol,
                price=current_price,
                previous_close=previous_close,
                gap_pct=round(gap_pct, 2),
                volume=volume,
                relative_volume=round(volume / avg_volume, 1) if avg_volume else 0,
                market_cap_formatted=MarketCapFormatter.format(info.get('marketCap')),
                volume_formatted=VolumeFormatter.format(volume),
                category=self._get_stock_category(symbol, info.get('sector')),
                pre_market_price=pre_market_price,
                pre_market_change_pct=round(pre_market_change_pct, 2) if pre_market_change_pct else None,
                post_market_price=post_market_price,
                post_market_change_pct=round(post_market_change_pct, 2) if post_market_change_pct else None,
                gap_classification=GapClassifier.classify(gap_pct)
            )
            
            return stock_data
            
        except Exception as e:
            logger.warning(f"⚠️ Error creating stock data for {symbol}: {e}")
            return None
    
    def _get_stock_category(self, symbol: str, sector_from_api: Optional[str] = None) -> str:
        """Determine stock category using API sector data or fallback mapping"""
        # First try to use the sector from the API
        if sector_from_api:
            # Map API sectors to our enum values
            sector_mapping = {
                'Technology': Sector.TECHNOLOGY.value,
                'Healthcare': Sector.HEALTHCARE.value,
                'Financial Services': Sector.FINANCIAL.value,
                'Consumer Cyclical': Sector.CONSUMER.value,
                'Consumer Defensive': Sector.CONSUMER.value,
                'Energy': Sector.ENERGY.value,
                'Industrials': Sector.INDUSTRIAL.value,
                'Basic Materials': Sector.MATERIALS.value,
                'Utilities': Sector.UTILITIES.value,
                'Real Estate': Sector.REAL_ESTATE.value,
                'Communication Services': Sector.COMMUNICATION.value,
            }
            return sector_mapping.get(sector_from_api, sector_from_api)
        
        # Fallback to symbol-based mapping
        symbol_mapping = {
            # Technology
            'AAPL': Sector.TECHNOLOGY.value, 'MSFT': Sector.TECHNOLOGY.value, 'GOOGL': Sector.TECHNOLOGY.value,
            'AMZN': Sector.TECHNOLOGY.value, 'TSLA': Sector.TECHNOLOGY.value, 'NVDA': Sector.TECHNOLOGY.value,
            'META': Sector.TECHNOLOGY.value, 'NFLX': Sector.TECHNOLOGY.value, 'AMD': Sector.TECHNOLOGY.value,
            'INTC': Sector.TECHNOLOGY.value, 'PLTR': Sector.TECHNOLOGY.value, 'SQ': Sector.TECHNOLOGY.value,
            
            # Healthcare
            'JNJ': Sector.HEALTHCARE.value, 'PFE': Sector.HEALTHCARE.value, 'UNH': Sector.HEALTHCARE.value,
            'ABBV': Sector.HEALTHCARE.value, 'TMO': Sector.HEALTHCARE.value, 'ABT': Sector.HEALTHCARE.value,
            
            # Financial
            'JPM': Sector.FINANCIAL.value, 'BAC': Sector.FINANCIAL.value, 'WFC': Sector.FINANCIAL.value,
            'GS': Sector.FINANCIAL.value, 'MS': Sector.FINANCIAL.value, 'C': Sector.FINANCIAL.value,
            'SOFI': Sector.FINANCIAL.value, 'HOOD': Sector.FINANCIAL.value, 'COIN': Sector.FINANCIAL.value,
            
            # Consumer
            'KO': Sector.CONSUMER.value, 'PG': Sector.CONSUMER.value, 'WMT': Sector.CONSUMER.value,
            'HD': Sector.CONSUMER.value, 'MCD': Sector.CONSUMER.value, 'NKE': Sector.CONSUMER.value,
            
            # Energy
            'XOM': Sector.ENERGY.value, 'CVX': Sector.ENERGY.value, 'COP': Sector.ENERGY.value,
            'EOG': Sector.ENERGY.value, 'SLB': Sector.ENERGY.value,
            
            # Industrial
            'BA': Sector.INDUSTRIAL.value, 'CAT': Sector.INDUSTRIAL.value, 'MMM': Sector.INDUSTRIAL.value,
            'GE': Sector.INDUSTRIAL.value, 'HON': Sector.INDUSTRIAL.value,
            
            # Materials
            'LIN': Sector.MATERIALS.value, 'APD': Sector.MATERIALS.value, 'FCX': Sector.MATERIALS.value,
            'NEM': Sector.MATERIALS.value, 'DOW': Sector.MATERIALS.value,
            
            # Utilities
            'DUK': Sector.UTILITIES.value, 'SO': Sector.UTILITIES.value, 'D': Sector.UTILITIES.value,
            'NEE': Sector.UTILITIES.value, 'AEP': Sector.UTILITIES.value,
            
            # Real Estate
            'PLD': Sector.REAL_ESTATE.value, 'AMT': Sector.REAL_ESTATE.value, 'CCI': Sector.REAL_ESTATE.value,
            'EQIX': Sector.REAL_ESTATE.value, 'PSA': Sector.REAL_ESTATE.value,
            
            # Communication
            'T': Sector.COMMUNICATION.value, 'VZ': Sector.COMMUNICATION.value, 'CMCSA': Sector.COMMUNICATION.value,
            'CHTR': Sector.COMMUNICATION.value, 'TMUS': Sector.COMMUNICATION.value,
            
            # EVs and Auto
            'RIVN': Sector.TECHNOLOGY.value, 'LCID': Sector.TECHNOLOGY.value, 'NIO': Sector.TECHNOLOGY.value,
            'XPEV': Sector.TECHNOLOGY.value, 'LI': Sector.TECHNOLOGY.value,
            
            # Meme stocks
            'GME': Sector.CONSUMER.value, 'AMC': Sector.CONSUMER.value, 'BBBY': Sector.CONSUMER.value,
            
            # Cannabis
            'SNDL': Sector.HEALTHCARE.value, 'TLRY': Sector.HEALTHCARE.value, 'HEXO': Sector.HEALTHCARE.value,
            'ACB': Sector.HEALTHCARE.value, 'CGC': Sector.HEALTHCARE.value, 'APHA': Sector.HEALTHCARE.value,
            'CRON': Sector.HEALTHCARE.value,
            
            # ETFs
            'SPY': Sector.FINANCIAL.value, 'QQQ': Sector.FINANCIAL.value, 'IWM': Sector.FINANCIAL.value,
            'TQQQ': Sector.FINANCIAL.value, 'SQQQ': Sector.FINANCIAL.value, 'UVXY': Sector.FINANCIAL.value,
            'VXX': Sector.FINANCIAL.value, 'VIXY': Sector.FINANCIAL.value,
        }
        
        return symbol_mapping.get(symbol, Sector.TECHNOLOGY.value)
    
    def start_background_scanner(self) -> None:
        """Start background scanner thread"""
        if self.scanner_running:
            return
        
        self.scanner_running = True
        
        def background_scan_loop():
            while self.scanner_running:
                try:
                    self.scan_stocks()
                    time.sleep(SCANNER_INTERVAL)
                except Exception as e:
                    logger.error(f"⚠️ Error in background scanner: {e}")
                    time.sleep(60)  # Wait 1 minute on error
        
        scanner_thread = threading.Thread(target=background_scan_loop, daemon=True)
        scanner_thread.start()
        logger.info("🚀 Background scanner thread started")
    
    def stop_scanner(self) -> None:
        """Stop background scanner"""
        self.scanner_running = False
        logger.info("🛑 Background scanner stopped")
    
    @contextmanager
    def get_cache(self):
        """Thread-safe cache access"""
        with self.cache_lock:
            yield self.cache

# =====================================================
# FLASK APP INITIALIZATION
# =====================================================

app = Flask(__name__)

# Initialize scanner
scanner = StockScanner()

# =====================================================
# REQUEST TRACKING
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
        
        # Skip tracking for static files, API calls, and health checks
        if (request.path.startswith('/static/') or 
            request.path.startswith('/api/') or 
            request.path == '/health' or
            request.path == '/favicon.ico' or
            '.js' in request.path or
            '.css' in request.path or
            '.ico' in request.path or
            '.png' in request.path or
            '.jpg' in request.path or
            '.gif' in request.path):
            return
        
        # Track page view for actual page visits only
        traffic_analytics.track_page_view(
            session_id, request.path, ip_address, user_agent, 
            request.headers.get('Referer')
        )
            
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
        with scanner.get_cache() as cache_data:
            if not cache_data or not cache_data.get('stocks'):
                logger.warning("⚠️ No cache data available for main page")
                return render_template('screener.html', 
                                     stocks=[],
                                     cache_status={'status': 'No data', 'stock_count': 0, 'age_minutes': 0.0},
                                     sectors=['Unknown'],
                                     quick_movers_independent=True,
                                     top_gappers_independent=True,
                                     show_loading=True,
                                     total_stocks=0,
                                     filtered_count=0,
                                     filters=FilterParams())
            
            stocks = list(cache_data['stocks'].values())
            
            # Get filter parameters
            min_gap_pct_raw = request.args.get('min_gap_pct', '0.0')
            logger.info(f"🔍 Raw min_gap_pct from URL: '{min_gap_pct_raw}'")
            
            # Create default FilterParams and override with URL parameters
            filters = FilterParams()
            if request.args.get('min_price'):
                filters.min_price = float(request.args.get('min_price'))
            if request.args.get('max_price'):
                filters.max_price = float(request.args.get('max_price'))
            if request.args.get('min_gap_pct'):
                filters.min_gap_pct = float(request.args.get('min_gap_pct'))
            if request.args.get('min_rel_vol'):
                filters.min_rel_vol = float(request.args.get('min_rel_vol'))
            if request.args.get('sector_filter'):
                filters.sector_filter = request.args.get('sector_filter')
            
            # Process advanced filter parameters
            if request.args.get('max_float'):
                filters.max_float = float(request.args.get('max_float'))
            if request.args.get('min_market_cap'):
                filters.min_market_cap = float(request.args.get('min_market_cap'))
            if request.args.get('max_market_cap'):
                filters.max_market_cap = float(request.args.get('max_market_cap'))
            if request.args.get('min_premarket_volume'):
                filters.min_premarket_volume = float(request.args.get('min_premarket_volume'))
            if request.args.get('min_pe_ratio'):
                filters.min_pe_ratio = float(request.args.get('min_pe_ratio'))
            if request.args.get('max_pe_ratio'):
                filters.max_pe_ratio = float(request.args.get('max_pe_ratio'))
            if request.args.get('min_pre_market'):
                filters.min_pre_market = float(request.args.get('min_pre_market'))
            if request.args.get('max_pre_market'):
                filters.max_pre_market = float(request.args.get('max_pre_market'))
            if request.args.get('min_pre_market_change'):
                filters.min_pre_market_change = float(request.args.get('min_pre_market_change'))
            if request.args.get('max_pre_market_change'):
                filters.max_pre_market_change = float(request.args.get('max_pre_market_change'))
            if request.args.get('min_post_market'):
                filters.min_post_market = float(request.args.get('min_post_market'))
            if request.args.get('max_post_market'):
                filters.max_post_market = float(request.args.get('max_post_market'))
            if request.args.get('min_post_market_change'):
                filters.min_post_market_change = float(request.args.get('min_post_market_change'))
            if request.args.get('max_post_market_change'):
                filters.max_post_market_change = float(request.args.get('max_post_market_change'))
            
            logger.info(f"🔍 Processed min_gap_pct: {filters.min_gap_pct}")
            logger.info(f"🔍 Filters dict: {filters.__dict__}")
            
            # Get independent filter settings (default to True = sliders OFF)
            quick_movers_independent = request.args.get('quick_movers_independent', 'true').lower() == 'true'
            top_gappers_independent = request.args.get('top_gappers_independent', 'true').lower() == 'true'
            
            # Apply filters
            filtered_stocks = StockFilter.apply(stocks, filters)
            
            # Get cache status
            cache_status = CacheStatusCalculator.calculate(cache_data)
            
            # Get unique sectors
            sectors = list(set(stock.category for stock in stocks if stock.category))
            sectors.insert(0, 'All')
            
            # Get top performers based on independent settings
            if quick_movers_independent:
                quick_movers = StockSelector.get_quick_movers(stocks, 5)  # Use all stocks
            else:
                quick_movers = StockSelector.get_quick_movers(filtered_stocks, 5)  # Use filtered stocks
                
            if top_gappers_independent:
                top_gappers = StockSelector.get_top_gappers(stocks, 5)  # Use all stocks
            else:
                top_gappers = StockSelector.get_top_gappers(filtered_stocks, 5)  # Use filtered stocks
            
            # Convert to dictionaries for template
            stocks_dict = [stock.__dict__ for stock in filtered_stocks]
            quick_movers_dict = [stock.__dict__ for stock in quick_movers]
            top_gappers_dict = [stock.__dict__ for stock in top_gappers]
            
            logger.info(f"✅ Main page rendered with {len(filtered_stocks)} filtered stocks")
            
            # Format last update time for display
            last_update_display = None
            if cache_status.last_update:
                last_update_display = datetime.fromtimestamp(cache_status.last_update).strftime('%Y-%m-%d %H:%M:%S')
            
            return render_template('screener.html',
                                 stocks=stocks_dict,
                                 cache_status=cache_status.__dict__,
                                 last_update=last_update_display,
                                 sectors=sectors,
                                 quick_movers_independent=quick_movers_independent,
                                 top_gappers_independent=top_gappers_independent,
                                 show_loading=False,
                                 total_stocks=len(stocks),
                                 filtered_count=len(filtered_stocks),
                                 filters=filters.__dict__,
                                 quick_movers=quick_movers_dict,
                                 top_positive_gappers=top_gappers_dict)
                                 
    except Exception as e:
        logger.error(f"⚠️ Error rendering main page: {e}")
        return render_template('screener.html', 
                             stocks=[],
                             cache_status={'status': 'Error', 'stock_count': 0, 'message': str(e), 'age_minutes': 0.0},
                             sectors=['Unknown'],
                             quick_movers_independent=True,
                             top_gappers_independent=True,
                             show_loading=False,
                             total_stocks=0,
                             filtered_count=0,
                             filters=FilterParams().__dict__)

@app.route("/api/cache_status")
def api_cache_status():
    """Get cache status"""
    try:
        with scanner.get_cache() as cache_data:
            cache_status = CacheStatusCalculator.calculate(cache_data)
            # Convert enum to string for JSON serialization
            status_dict = cache_status.__dict__.copy()
            status_dict['status'] = cache_status.status.value
            return jsonify(status_dict)
    except Exception as e:
        logger.error(f"⚠️ Error getting cache status: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
            logger.info(f"📊 ANALYTICS [PAGEVIEW] {log_entry['url']} | IP: {log_entry['ip']} | Referrer: {log_entry['referrer'] or 'Direct'}")
        elif event_type == 'engagement':
            engagement_time = log_entry.get('engagement_time', 0)
            scroll_depth = log_entry.get('scroll_depth', 0)
            logger.info(f"📊 ANALYTICS [ENGAGEMENT] {log_entry['url']} | Time: {engagement_time}s | Scroll: {scroll_depth}% | IP: {log_entry['ip']}")
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"⚠️ Error processing analytics event: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route("/api/geolocation/stats")
def api_geolocation_stats():
    """Get geolocation statistics"""
    try:
        with sqlite3.connect(TRAFFIC_DB) as conn:
            cursor = conn.cursor()
            
            # Exclude localhost and local network IPs
            excluded_ips = ['127.0.0.1', 'localhost', '::1', '192.168.1.88']
            excluded_ips_placeholders = ','.join(['?' for _ in excluded_ips])
            
            # Get country statistics (excluding local IPs)
            cursor.execute(f'''
                SELECT pv.country, COUNT(*) as visits, COUNT(DISTINCT pv.session_id) as unique_visitors
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.country IS NOT NULL 
                AND pv.country != 'Local'
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY pv.country 
                ORDER BY visits DESC 
                LIMIT 20
            ''', excluded_ips)
            countries = [{'country': row[0], 'visits': row[1], 'unique_visitors': row[2]} for row in cursor.fetchall()]
            
            # Get city statistics (excluding local IPs)
            cursor.execute(f'''
                SELECT pv.city, pv.country, COUNT(*) as visits, COUNT(DISTINCT pv.session_id) as unique_visitors
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.city IS NOT NULL 
                AND pv.city != 'Local'
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY pv.city, pv.country 
                ORDER BY visits DESC 
                LIMIT 15
            ''', excluded_ips)
            cities = [{'city': row[0], 'country': row[1], 'visits': row[2], 'unique_visitors': row[3]} for row in cursor.fetchall()]
            
            # Get region statistics (excluding local IPs)
            cursor.execute(f'''
                SELECT pv.region, pv.country, COUNT(*) as visits, COUNT(DISTINCT pv.session_id) as unique_visitors
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.region IS NOT NULL 
                AND pv.region != 'Local'
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY pv.region, pv.country 
                ORDER BY visits DESC 
                LIMIT 15
            ''', excluded_ips)
            regions = [{'region': row[0], 'country': row[1], 'visits': row[2], 'unique_visitors': row[3]} for row in cursor.fetchall()]
            
            # Get total statistics (excluding local IPs)
            cursor.execute(f'''
                SELECT 
                    COUNT(DISTINCT pv.session_id) as total_unique_visitors,
                    COUNT(*) as total_visits,
                    COUNT(DISTINCT pv.country) as total_countries,
                    COUNT(DISTINCT pv.city) as total_cities
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.country IS NOT NULL 
                AND pv.country != 'Local'
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
            ''', excluded_ips)
            total_stats = cursor.fetchone()
            
            return jsonify({
                'countries': countries,
                'cities': cities,
                'regions': regions,
                'total_stats': {
                    'unique_visitors': total_stats[0],
                    'total_visits': total_stats[1],
                    'total_countries': total_stats[2],
                    'total_cities': total_stats[3]
                }
            })
            
    except Exception as e:
        logger.error(f"⚠️ Error getting geolocation stats: {e}")
        return jsonify({'error': 'Failed to get geolocation statistics'}), 500

@app.route("/api/geolocation/countries")
def api_geolocation_countries():
    """Get detailed country statistics"""
    try:
        with sqlite3.connect(TRAFFIC_DB) as conn:
            cursor = conn.cursor()
            
            # Exclude localhost and local network IPs
            excluded_ips = ['127.0.0.1', 'localhost', '::1', '192.168.1.88']
            excluded_ips_placeholders = ','.join(['?' for _ in excluded_ips])
            
            cursor.execute(f'''
                SELECT 
                    pv.country,
                    COUNT(*) as total_visits,
                    COUNT(DISTINCT pv.session_id) as unique_visitors,
                    COUNT(DISTINCT pv.city) as cities_visited,
                    MIN(pv.timestamp) as first_visit,
                    MAX(pv.timestamp) as last_visit
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.country IS NOT NULL 
                AND pv.country != 'Local'
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY pv.country 
                ORDER BY total_visits DESC
            ''', excluded_ips)
            
            countries = []
            for row in cursor.fetchall():
                countries.append({
                    'country': row[0],
                    'total_visits': row[1],
                    'unique_visitors': row[2],
                    'cities_visited': row[3],
                    'first_visit': row[4],
                    'last_visit': row[5]
                })
            
            return jsonify({'countries': countries})
            
    except Exception as e:
        logger.error(f"⚠️ Error getting country stats: {e}")
        return jsonify({'error': 'Failed to get country statistics'}), 500

@app.route("/api/geolocation/cities")
def api_geolocation_cities():
    """Get detailed city statistics"""
    try:
        with sqlite3.connect(TRAFFIC_DB) as conn:
            cursor = conn.cursor()
            
            # Exclude localhost and local network IPs
            excluded_ips = ['127.0.0.1', 'localhost', '::1', '192.168.1.88']
            excluded_ips_placeholders = ','.join(['?' for _ in excluded_ips])
            
            cursor.execute(f'''
                SELECT 
                    pv.city,
                    pv.country,
                    pv.region,
                    COUNT(*) as total_visits,
                    COUNT(DISTINCT pv.session_id) as unique_visitors,
                    MIN(pv.timestamp) as first_visit,
                    MAX(pv.timestamp) as last_visit
                FROM page_views pv
                JOIN visitors v ON pv.session_id = v.session_id
                WHERE pv.city IS NOT NULL 
                AND pv.city != 'Local'
                AND v.ip_address NOT IN ({excluded_ips_placeholders})
                GROUP BY pv.city, pv.country, pv.region 
                ORDER BY total_visits DESC
                LIMIT 50
            ''', excluded_ips)
            
            cities = []
            for row in cursor.fetchall():
                cities.append({
                    'city': row[0],
                    'country': row[1],
                    'region': row[2],
                    'total_visits': row[3],
                    'unique_visitors': row[4],
                    'first_visit': row[5],
                    'last_visit': row[6]
                })
            
            return jsonify({'cities': cities})
            
    except Exception as e:
        logger.error(f"⚠️ Error getting city stats: {e}")
        return jsonify({'error': 'Failed to get city statistics'}), 500

# =====================================================
# INITIALIZATION
# =====================================================

def initialize_app():
    """Initialize the application"""
    logger.info("🚀 Initializing Flask app...")
    
    # Ensure cache directory exists
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Initial scan if no cache exists
    if not CACHE_FILE.exists():
        logger.info("🔄 No cache found, performing initial scan...")
        scanner.scan_stocks()
    
    logger.info("✅ Flask app initialization complete")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Screener App')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on (default: 5001)')
    args = parser.parse_args()
    
    initialize_app()
    
    logger.info("🌐 Starting Flask development server...")
    logger.info(f"📊 App will be available at: http://localhost:{args.port}")
    logger.info(f"🔄 Background scanner interval: {SCANNER_INTERVAL} seconds")
    logger.info("🛑 Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=args.port, debug=True) 