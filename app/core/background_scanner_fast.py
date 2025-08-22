#!/usr/bin/env python3
"""
Fast Background Gap Scanner - Instant Data Version
Finds the biggest gappers dynamically using yfinance screener
Optimized for speed with minimal delays
"""

import json
import time
import os
import sys
from datetime import datetime, timedelta
import yfinance as yf
from dotenv import load_dotenv
import threading
import signal
from cache_manager import cache_manager
import numpy as np
import os

# Ensure cache directory exists with absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
cache_dir = os.path.abspath(os.path.join(BASE_DIR, "data"))
os.makedirs(cache_dir, exist_ok=True)
print(f"📁 Scanner cache directory: {cache_dir}")

# Try to import pytz, fallback to datetime if not available
try:
    import pytz
    PYTZ_AVAILABLE = True
except ImportError:
    PYTZ_AVAILABLE = False
    print("⚠️  pytz not available, using basic timezone handling")

# Load environment variables
load_dotenv()

# ULTRA-FAST Configuration - Instant data
SCAN_INTERVAL = 60  # 1 minute for instant updates
MAX_STOCKS = 15  # Focused on top movers
RATE_LIMIT_DELAY = 0.1  # Ultra-fast requests
PID_FILE = "background_scanner_fast.pid"

# Global variables
running = True
last_scan_time = 0

def json_serializer(obj):
    """Custom JSON serializer for numpy types"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def get_market_session_info():
    """Get current market session information with proper timezone handling"""
    try:
        if PYTZ_AVAILABLE:
            # US Eastern Time (where NYSE/NASDAQ operate)
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
        else:
            # Fallback: assume we're in ET or use UTC offset
            now_et = datetime.now()
            et_offset = -5  # EST offset
            now_et = now_et + timedelta(hours=et_offset)
        
        # Market hours (9:30 AM - 4:00 PM ET)
        market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
        
        # Pre-market (4:00 AM - 9:30 AM ET)
        pre_market_open = now_et.replace(hour=4, minute=0, second=0, microsecond=0)
        
        # After-hours (4:00 PM - 8:00 PM ET)
        after_hours_close = now_et.replace(hour=20, minute=0, second=0, microsecond=0)
        
        # Determine session
        if now_et.weekday() >= 5:  # Weekend
            session = "CLOSED (Weekend)"
        elif pre_market_open <= now_et < market_open:
            session = "PRE-MARKET"
        elif market_open <= now_et < market_close:
            session = "REGULAR"
        elif market_close <= now_et < after_hours_close:
            session = "AFTER-HOURS"
        else:
            session = "CLOSED"
            
        return {
            'current_time_et': now_et.strftime('%Y-%m-%d %H:%M:%S'),
            'session': session,
            'market_open': market_open.strftime('%H:%M ET'),
            'market_close': market_close.strftime('%H:%M ET'),
            'is_trading_day': now_et.weekday() < 5
        }
    except Exception as e:
        print(f"⚠️  Error getting market session info: {e}")
        return {
            'current_time_et': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'session': 'UNKNOWN',
            'market_open': '9:30 ET',
            'market_close': '16:00 ET',
            'is_trading_day': True
        }

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

def format_market_cap(market_cap):
    """Format market cap numbers to human-readable format (B, M, K)"""
    try:
        if not market_cap or market_cap == 0:
            return "—"
        
        market_cap = float(market_cap)
        
        if market_cap >= 1_000_000_000:
            return f"${market_cap / 1_000_000_000:.1f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap / 1_000_000:.1f}M"
        elif market_cap >= 1_000:
            return f"${market_cap / 1_000:.1f}K"
        else:
            return f"${int(market_cap)}"
    except (ValueError, TypeError):
        return "—"

def create_pid_file():
    """Create PID file to track running instance"""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        print(f"❌ Failed to create PID file: {e}")
        return False

def remove_pid_file():
    """Remove PID file"""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception as e:
        print(f"⚠️  Failed to remove PID file: {e}")

def check_existing_instance():
    """Check if another instance is already running"""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                return True
            except OSError:
                # Process doesn't exist, remove stale PID file
                remove_pid_file()
                return False
    except Exception as e:
        print(f"⚠️  Error checking existing instance: {e}")
    
    return False

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    running = False

def get_biggest_gappers():
    """Get biggest gappers using yfinance screener - FAST VERSION"""
    try:
        print("🔍 Fetching biggest gappers...")
        
        # Use yfinance screener for biggest gainers
        screener = yf.Tickers("^GSPC ^DJI ^IXIC")  # Just get major indices for symbols
        
        # Get top gainers from various sources
        symbols = []
        
        # Add some popular high-volume stocks that often gap
        popular_gappers = [
            "TSLA", "NVDA", "AMD", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "NFLX", "SPY",
            "QQQ", "IWM", "TQQQ", "SQQQ", "UVXY", "VXX", "XLE", "XLF", "XLV", "XLK"
        ]
        symbols.extend(popular_gappers)
        
        # Add some penny stocks that often gap
        penny_stocks = [
            "HCTI", "SNDL", "HEXO", "ACB", "TLRY", "CGC", "CRON", "APHA", "OGI", "VFF",
            "GNUS", "IDEX", "MARK", "SHIP", "TOPS", "ZOM", "CIDM", "CTRM", "NAKD", "SENS"
        ]
        symbols.extend(penny_stocks)
        
        # Remove duplicates
        unique_symbols = list(dict.fromkeys(symbols))
        
        print(f"📊 Found {len(unique_symbols)} symbols to scan")
        return unique_symbols[:MAX_STOCKS]
        
    except Exception as e:
        print(f"❌ Error getting gappers: {e}")
        # Fallback to basic symbols
        return ["TSLA", "NVDA", "AMD", "AAPL", "MSFT", "HCTI", "SNDL", "SPY", "QQQ"]

def filter_valid_symbols(symbols):
    """Filter out invalid symbols"""
    valid_symbols = []
    for symbol in symbols:
        # Basic validation
        if symbol and len(symbol) <= 5 and symbol.isalnum():
            valid_symbols.append(symbol.upper())
    return valid_symbols

def categorize_stock(sector, industry):
    """Categorize stock by sector and industry"""
    if not sector or not industry:
        return "Unknown"
    
    sector = sector.lower()
    industry = industry.lower()
    
    # Technology
    if any(tech in sector or tech in industry for tech in ['technology', 'software', 'semiconductor', 'internet']):
        return "Technology"
    
    # Healthcare
    if any(health in sector or health in industry for health in ['healthcare', 'medical', 'biotechnology', 'pharmaceutical']):
        return "Healthcare"
    
    # Finance
    if any(finance in sector or finance in industry for finance in ['financial', 'banking', 'insurance']):
        return "Finance"
    
    # Energy
    if any(energy in sector or energy in industry for energy in ['energy', 'oil', 'gas', 'renewable']):
        return "Energy"
    
    # Consumer
    if any(consumer in sector or consumer in industry for consumer in ['consumer', 'retail', 'automotive']):
        return "Consumer"
    
    # Industrial
    if any(industrial in sector or industrial in industry for industrial in ['industrial', 'manufacturing']):
        return "Industrial"
    
    # Real Estate
    if any(real_estate in sector or real_estate in industry for real_estate in ['real estate', 'reit']):
        return "Real Estate"
    
    # Materials
    if any(materials in sector or materials in industry for materials in ['materials', 'mining', 'chemical']):
        return "Materials"
    
    # Utilities
    if any(utilities in sector or utilities in industry for utilities in ['utilities', 'electric', 'water']):
        return "Utilities"
    
    # Communication
    if any(comm in sector or comm in industry for comm in ['communication', 'telecom', 'media']):
        return "Communication"
    
    return "Other"

def fetch_stock_data(symbol, max_retries=1, base_delay=1.0):
    """Fetch stock data with minimal delays - FAST VERSION"""
    try:
        # Create ticker object
        ticker = yf.Ticker(symbol)
        
        # Get basic info
        info = ticker.info
        
        # Get current price and previous close
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2]
        
        # Calculate gap percentage
        if prev_close > 0:
            gap_pct = ((current_price - prev_close) / prev_close) * 100
        else:
            gap_pct = 0
        
        # Get volume data
        volume = hist['Volume'].iloc[-1] if len(hist) > 0 else 0
        avg_volume = info.get('averageVolume', 0)
        
        # Calculate relative volume
        rel_volume = (volume / avg_volume) if avg_volume > 0 else 0
        
        # Get market cap
        market_cap = info.get('marketCap', 0)
        
        # Get float
        shares_outstanding = info.get('sharesOutstanding', 0)
        float_shares = info.get('floatShares', shares_outstanding)
        
        # Get sector and industry
        sector = info.get('sector', '')
        industry = info.get('industry', '')
        category = categorize_stock(sector, industry)
        
        # Get PE ratio
        pe_ratio = info.get('trailingPE', 0)
        
        # Get pre/post market data if available
        try:
            # Try to get extended hours data
            extended_hist = ticker.history(period="1d", interval="1m")
            if len(extended_hist) > 0:
                latest_price = extended_hist['Close'].iloc[-1]
                pre_market_change = ((latest_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
            else:
                pre_market_change = gap_pct
        except:
            pre_market_change = gap_pct
        
        # Create stock data object
        stock_data = {
            'symbol': symbol,
            'price': round(current_price, 2),
            'prev_close': round(prev_close, 2),
            'gap_pct': round(gap_pct, 2),
            'volume': volume,
            'avg_volume': avg_volume,
            'rel_volume': round(rel_volume, 2),
            'market_cap': market_cap,
            'market_cap_formatted': format_market_cap(market_cap),
            'float': float_shares,
            'float_formatted': format_volume(float_shares),
            'sector': sector,
            'industry': industry,
            'category': category,
            'pe_ratio': round(pe_ratio, 2) if pe_ratio else 0,
            'volume_formatted': format_volume(volume),
            'avg_volume_formatted': format_volume(avg_volume),
            'pre_market_change': round(pre_market_change, 2),
            'last_updated': datetime.now().strftime('%H:%M:%S')
        }
        
        return stock_data
        
    except Exception as e:
        print(f"❌ Error fetching data for {symbol}: {e}")
        return None

def scan_gaps():
    """Scan for gap opportunities with ultra-fast optimization"""
    global last_scan_time
    
    try:
        print("🚀 Starting FAST gap scan...")
        start_time = time.time()
        
        # Get market session info
        market_info = get_market_session_info()
        print(f"📅 Market Session: {market_info['session']} | Time: {market_info['current_time_et']}")
        
        # Get biggest gappers
        print("🔍 Fetching biggest gappers...")
        gapper_symbols = get_biggest_gappers()
        
        if not gapper_symbols:
            print("❌ No gapper symbols found")
            return
        
        print(f"📊 Found {len(gapper_symbols)} symbols to scan")
        
        # Limit to MAX_STOCKS for speed
        unique_symbols = list(set(gapper_symbols))[:MAX_STOCKS]
        print(f"📊 Total unique symbols to scan: {len(unique_symbols)}")
        
        # Load existing cache for comparison
        existing_cache = load_existing_cache()
        existing_stocks = existing_cache.get('stocks', []) if existing_cache else []
        existing_symbols = {stock['symbol'] for stock in existing_stocks}
        
        # Track results
        successful_stocks = []
        failed_stocks = []
        
        # Scan each symbol with minimal delays
        for i, symbol in enumerate(unique_symbols, 1):
            if i > 1 and i % 5 == 0: # Only delay every 5th request
                time.sleep(RATE_LIMIT_DELAY)
                
            print(f"📊 Scanning {symbol} ({i}/{len(unique_symbols)})...")
            
            try:
                stock_data = fetch_stock_data(symbol)
                if stock_data:
                    successful_stocks.append(stock_data)
                    print(f"✅ {symbol}: ${stock_data['price']:.2f} ({stock_data['gap_pct']:.2f}% gap)")
                else:
                    failed_stocks.append(symbol)
                    print(f"❌ {symbol}: Failed to fetch data")
            except Exception as e:
                failed_stocks.append(symbol)
                print(f"❌ {symbol}: Error - {e}")
        
        # Create cache data with proper JSON serialization
        cache_data = {
            'stocks': successful_stocks,
            'last_update': datetime.now().isoformat(),
            'market_session': market_info,
            'scan_summary': {
                'successful_count': len(successful_stocks),
                'failed_count': len(failed_stocks),
                'total_scanned': len(unique_symbols),
                'scan_duration_seconds': round(time.time() - start_time, 1)
            },
            'successful_count': len(successful_stocks),
            'total_count': len(unique_symbols),
            'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Use custom JSON serializer to handle numpy types
        try:
            # Serialize with custom serializer to handle numpy types
            cache_data_clean = json.loads(json.dumps(cache_data, default=json_serializer))
            
            # Save using cache manager
            if cache_manager.save_cache(cache_data_clean):
                print(f"✅ Saved {len(successful_stocks)} stocks to cache")
            else:
                print("❌ Failed to save cache")
                
        except Exception as e:
            print(f"❌ Error saving cache: {e}")
        
        # Update last scan time
        last_scan_time = time.time()
        
        print(f"✅ FAST Scan Complete!")
        print(f"📊 Success: {len(successful_stocks)}")
        print(f"❌ Failed: {len(failed_stocks)}")
        print(f"⏱️  Duration: {time.time() - start_time:.1f}s")
        print(f"📊 Market Session: {market_info['session']}")
        
    except Exception as e:
        print(f"❌ Critical error in scan_gaps: {e}")
        import traceback
        traceback.print_exc()

def load_existing_cache():
    """Load existing cache if available"""
    try:
        cache_data = cache_manager.load_cache()
        if cache_data and cache_data.get('stocks'):
            last_update = cache_data.get('last_update', 0)
            age_minutes = (time.time() - last_update) / 60
            
            print(f"📁 Found existing cache from {cache_data.get('last_update_str', 'unknown')} ({age_minutes:.1f} minutes ago)")
            
            # If cache is fresh (less than 2 minutes old), preserve it
            if age_minutes < 2:
                print(f"✅ Cache is fresh ({age_minutes:.1f} minutes old) - preserving existing data")
                return cache_data
            else:
                print(f"🔄 Cache is stale ({age_minutes:.1f} minutes old) - will refresh")
                return None
    except Exception as e:
        print(f"⚠️  Could not load existing cache: {e}")
    
    return None

def main():
    """Main background gap scanner loop - FAST VERSION"""
    global running, last_scan_time
    
    print("🚀 Starting FAST Background Gap Scanner")
    print(f"🎯 Finding biggest gappers dynamically")
    print(f"📊 Max stocks: {MAX_STOCKS}")
    print(f"⏱️  Scan interval: {SCAN_INTERVAL} seconds ({SCAN_INTERVAL/60:.1f} minutes)")
    print(f"💾 Cache file: {cache_manager.cache_file}")
    
    # Check for existing instance
    if check_existing_instance():
        print("❌ Another background scanner is already running. Exiting.")
        sys.exit(1)
    
    # Create PID file
    if not create_pid_file():
        print("❌ Failed to create PID file. Exiting.")
        sys.exit(1)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Load existing cache
    existing_cache = load_existing_cache()
    if existing_cache:
        last_scan_time = existing_cache.get('last_update', 0)
        print(f"✅ Using existing cache data - next scan in {SCAN_INTERVAL/60:.1f} minutes")
    else:
        print(f"🔄 No fresh cache found - will start initial scan immediately")
    
    print(f"\n🎯 FAST Gap scanner started. Press Ctrl+C to stop.")
    
    # Main loop
    while running:
        try:
            current_time = time.time()
            time_since_last = current_time - last_scan_time
            
            if time_since_last >= SCAN_INTERVAL:
                print(f"\n🔍 Starting FAST scan cycle...")
                scan_gaps()
                last_scan_time = current_time  # Update scan time after successful scan
            else:
                remaining = SCAN_INTERVAL - time_since_last
                print(f"⏳ Next FAST gap scan in {remaining:.0f} seconds...", end='\r')
            
            time.sleep(1)  # Check every 1 second for more responsive timing
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in main loop: {e}")
            print(f"🔄 Retrying in 5 seconds...")
            time.sleep(5)  # Wait before retrying
    
    print("\n✅ FAST Gap scanner stopped gracefully")
    remove_pid_file()

if __name__ == "__main__":
    main() 