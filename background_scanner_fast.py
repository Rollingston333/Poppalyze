#!/usr/bin/env python3
"""
Background Gap Scanner
Finds the biggest gappers dynamically using yfinance screener
Run this as a separate process: python3 background_scanner.py
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

# Configuration
SCAN_INTERVAL = 600  # Increase to 10 minutes to reduce rate limiting
MAX_STOCKS = 10  # Reduce to 10 stocks to avoid rate limiting
RATE_LIMIT_DELAY = 10.0  # Increase delay between requests to avoid rate limiting
PID_FILE = "background_scanner.pid"

# Global variables
running = True
last_scan_time = 0

def get_market_session_info():
    """Get current market session information with proper timezone handling"""
    try:
        if PYTZ_AVAILABLE:
            # US Eastern Time (where NYSE/NASDAQ operate)
            et = pytz.timezone('US/Eastern')
            now_et = datetime.now(et)
        else:
            # Fallback: assume we're in ET or use UTC offset
            # This is a simplified approach - in production you'd want proper timezone handling
            now_et = datetime.now()
            # Assume ET is UTC-5 (EST) or UTC-4 (EDT) - this is simplified
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
            return "0"
        market_cap = float(market_cap)
        if market_cap >= 1_000_000_000_000:
            return f"{market_cap / 1_000_000_000_000:.1f}T"
        elif market_cap >= 1_000_000_000:
            return f"{market_cap / 1_000_000_000:.1f}B"
        elif market_cap >= 1_000_000:
            return f"{market_cap / 1_000_000:.1f}M"
        elif market_cap >= 1_000:
            return f"{market_cap / 1_000:.1f}K"
        else:
            return f"{int(market_cap)}"
    except (ValueError, TypeError):
        return "—"

def create_pid_file():
    """Create PID file to prevent multiple instances"""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        print(f"📝 Created PID file: {PID_FILE}")
        return True
    except Exception as e:
        print(f"❌ Failed to create PID file: {e}")
        return False

def remove_pid_file():
    """Remove PID file on shutdown"""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            print(f"🧹 Removed PID file: {PID_FILE}")
    except Exception as e:
        print(f"⚠️  Warning: Could not remove PID file: {e}")

def check_existing_instance():
    """Check if another instance is already running"""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process is actually running
            try:
                os.kill(pid, 0)  # Signal 0 just checks if process exists
                print(f"⚠️  Another background scanner is already running (PID: {pid})")
                return True
            except OSError:
                # Process doesn't exist, clean up stale PID file
                os.remove(PID_FILE)
                print("🧹 Removed stale PID file")
                return False
        except (ValueError, IOError):
            # Invalid PID file, remove it
            os.remove(PID_FILE)
            print("🧹 Removed invalid PID file")
            return False
    return False

def signal_handler(signum, frame):
    """Handle graceful shutdown"""
    global running
    print("\n🛑 Shutdown signal received. Stopping gap scanner...")
    running = False
    remove_pid_file()

def get_biggest_gappers():
    """Find the biggest gappers using comprehensive multi-source strategy to eliminate gaps"""
    try:
        print("🔍 COMPREHENSIVE SCAN - Eliminating all gaps in stock coverage...")
        
        all_symbols = []
        
        # 1. PRIORITY STOCKS - Always scan these first (NO GAPS ALLOWED)
        priority_symbols = [
            # High-priority stocks that should never be missed
            'IXHL', 'TSLA', 'NVDA', 'AMD', 'GME', 'AMC', 'META', 'GOOGL', 'MSFT', 'AAPL', 'AMZN',
            'COIN', 'MSTR', 'RIOT', 'MARA', 'PLTR', 'SOFI', 'HOOD', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
            'BABA', 'JD', 'PDD', 'BIDU', 'NTES', 'TME', 'ZTO', 'BILI', 'DIDI', 'EDU', 'TAL', 'IQ', 'VIPS', 'YMM',
            'SAVA', 'BIIB', 'GILD', 'REGN', 'VRTX', 'MRNA', 'BNTX', 'PFE', 'JNJ', 'NVAX', 'SRNE', 'INO', 'OCGN', 'TNXP', 'PROG'
        ]
        
        print(f"🎯 Priority stocks: {len(priority_symbols)} stocks (scanned first)")
        all_symbols.extend(priority_symbols)
        
        # 2. MANUAL INCLUSION - Known volatile/gap-prone stocks (NO GAPS ALLOWED)
        manual_high_volatility_symbols = [
            # Bio/Pharma (high volatility) - US ONLY
            'ABVE', 'SAVA', 'BIIB', 'GILD', 'REGN', 'VRTX', 'MRNA', 'BNTX', 'PFE', 'JNJ',
            'NVAX', 'SRNE', 'INO', 'OCGN', 'TNXP', 'PROG', 'IXHL',
            
            # Crypto/Tech (gap prone) - US LISTED ONLY
            'COIN', 'MSTR', 'RIOT', 'MARA', 'BTBT', 'EBON', 'CAN', 'BTCM',
            'SOS',
            
            # Growth/Meme stocks - ACTIVE US STOCKS ONLY
            'GME', 'AMC', 'KOSS', 'CLOV', 'SPCE', 'PLTR', 'BB', 'NOK', 'SNDL', 'TLRY', 'CGC', 'ACB',
            
            # Small caps with gap history
            'PROK', 'NEGG', 'UP', 'GOGL', 'TMC', 'KNDI', 'DBI', 'LAC',
            'MP', 'HTZ', 'SABR', 'TROX', 'STEM', 'RARE', 'BMNR', 'BE', 'FNKO',
            
            # Chinese ADRs (volatile) - US TRADED
            'BABA', 'JD', 'PDD', 'BIDU', 'NTES', 'TME', 'ZTO', 'BILI', 'NIO',
            'XPEV', 'LI', 'DIDI', 'EDU', 'TAL', 'IQ', 'VIPS', 'YMM',
            
            # SPACs and recent IPOs
            'LCID', 'RIVN', 'F', 'HOOD', 'SOFI', 'AFRM', 'SQ', 'PYPL', 'UPST',
            
            # Other high-volatility US stocks
            'TSLA', 'NVDA', 'AMD', 'META', 'GOOGL', 'MSFT', 'AAPL', 'AMZN'
        ]
        
        # Remove duplicates (priority stocks already included)
        manual_symbols = [s for s in manual_high_volatility_symbols if s not in priority_symbols]
        print(f"🎯 Manual inclusion: {len(manual_symbols)} additional volatile stocks")
        all_symbols.extend(manual_symbols)
        
        # 3. Get large cap day gainers (>= $2B market cap)
        try:
            gainers = yf.screen('day_gainers', count=25)
            large_gainer_symbols = [quote['symbol'] for quote in gainers['quotes']]
            print(f"📈 Large cap gainers: {len(large_gainer_symbols)} found")
            all_symbols.extend(large_gainer_symbols)
        except Exception as e:
            print(f"⚠️  Large cap gainers failed: {e}")
        
        # 4. Get small cap gainers (< $2B market cap) 
        try:
            small_gainers = yf.screen('small_cap_gainers', count=25)
            small_gainer_symbols = [quote['symbol'] for quote in small_gainers['quotes']]
            print(f"📈 Small cap gainers: {len(small_gainer_symbols)} found")
            all_symbols.extend(small_gainer_symbols)
        except Exception as e:
            print(f"⚠️  Small cap gainers failed: {e}")

        # 5. Get most actives (high volume regardless of price change)
        try:
            actives = yf.screen('most_actives', count=15)
            active_symbols = [quote['symbol'] for quote in actives['quotes']]
            print(f"📊 Most actives: {len(active_symbols)} found")
            all_symbols.extend(active_symbols)
        except Exception as e:
            print(f"⚠️  Most actives failed: {e}")

        # 6. Get large cap losers 
        try:
            losers = yf.screen('day_losers', count=15) 
            loser_symbols = [quote['symbol'] for quote in losers['quotes']]
            print(f"📉 Large cap losers: {len(loser_symbols)} found")
            all_symbols.extend(loser_symbols)
        except Exception as e:
            print(f"⚠️  Large cap losers failed: {e}")

        # 7. EXTREME MOVERS - Multiple approaches to catch ALL big moves
        try:
            from yfinance import EquityQuery
            
            # Strategy A: >15% moves, any market cap, US + Canada + foreign on US exchanges  
            extreme_a = EquityQuery('and', [
                EquityQuery('or', [
                    EquityQuery('gt', ['percentchange', 15]),  # >15% up
                    EquityQuery('lt', ['percentchange', -15])  # >15% down
                ]),
                EquityQuery('gte', ['intradayprice', 0.25]),    # $0.25+ (very low)
                EquityQuery('gt', ['dayvolume', 1000])          # 1k+ volume (very low)
            ])
            
            extreme_a_result = yf.screen(extreme_a, count=35, sortField='percentchange')
            extreme_a_symbols = [quote['symbol'] for quote in extreme_a_result['quotes']]
            print(f"🚀 EXTREME movers A (>15%): {len(extreme_a_symbols)} found")
            all_symbols.extend(extreme_a_symbols)
            
            # Strategy B: >10% moves with relaxed filters
            extreme_b = EquityQuery('and', [
                EquityQuery('or', [
                    EquityQuery('gt', ['percentchange', 10]),   # >10% up  
                    EquityQuery('lt', ['percentchange', -10])   # >10% down
                ]),
                EquityQuery('gte', ['intradayprice', 0.10]),    # $0.10+ (penny stocks)
                EquityQuery('gt', ['dayvolume', 500])           # 500+ volume
            ])
            
            extreme_b_result = yf.screen(extreme_b, count=35, sortField='percentchange')
            extreme_b_symbols = [quote['symbol'] for quote in extreme_b_result['quotes']]
            print(f"🚀 EXTREME movers B (>10%): {len(extreme_b_symbols)} found")
            all_symbols.extend(extreme_b_symbols)
            
        except Exception as e:
            print(f"⚠️  Custom extreme queries failed: {e}")
            
        # 8. AGGRESSIVE SMALL CAPS - Often missed by other filters
        try:
            aggressive_small = yf.screen('aggressive_small_caps', count=20)
            aggressive_symbols = [quote['symbol'] for quote in aggressive_small['quotes']]
            print(f"🏃 Aggressive small caps: {len(aggressive_symbols)} found")
            all_symbols.extend(aggressive_symbols)
        except Exception as e:
            print(f"⚠️  Aggressive small caps failed: {e}")

        # Remove duplicates and get unique symbols
        unique_symbols = list(set(all_symbols))
        print(f"🎯 Total unique symbols found: {len(unique_symbols)}")
        
        # FILTER OUT BAD SYMBOLS - Only keep real US tradeable stocks
        filtered_symbols = filter_valid_symbols(unique_symbols)
        print(f"🧹 After filtering: {len(filtered_symbols)} valid US stocks (removed {len(unique_symbols) - len(filtered_symbols)} bad symbols)")
        
        # Show a sample for verification
        sample_symbols = filtered_symbols[:20]
        print(f"📋 Sample symbols: {', '.join(sample_symbols)}...")
        
        return filtered_symbols

    except Exception as e:
        print(f"❌ Error in comprehensive gap scanner: {e}")
        return []

def filter_valid_symbols(symbols):
    """Filter out invalid, foreign, or delisted symbols - US tradeable stocks only"""
    valid_symbols = []
    
    # Known delisted/bad symbols to exclude
    excluded_symbols = {
        'WISH', 'NKLA', 'BBBY', 'EXPR', 'RDBX', 'HEAR', 'XELA', 'NAKD', 'GNUS', 
        'DRYS', 'TOPS', 'SHIP', 'GLBS', 'SHIBUSD', 'DOTUSD', 'JASMYUSD', 
        'DOGEUSD', 'BTCUSD', 'ETHUSD', 'GDLF.AQ', 'OPEN'  # Add bad data symbols
    }
    
    for symbol in symbols:
        # Skip if in exclusion list
        if symbol in excluded_symbols:
            continue
            
        # Filter out foreign exchange symbols
        if ('.' in symbol and any(suffix in symbol for suffix in ['.AQ', '.NX', '.L', '.BR', '.TW', '.TO', '.V', '.F', '.DE'])):
            continue
            
        # Filter out obvious foreign/OTC patterns
        if (len(symbol) > 5 or 
            symbol.endswith('F') and len(symbol) == 5 or  # Many foreign OTC end in F
            symbol.startswith('0') or symbol.startswith('1') or  # Foreign codes
            'USD' in symbol):  # Crypto pairs
            continue
            
        # Keep only standard US symbols (1-5 chars, letters only)
        if symbol.isalpha() and 1 <= len(symbol) <= 5:
            valid_symbols.append(symbol)
    
    return valid_symbols

def categorize_stock(sector, industry):
    """Categorize stocks into simplified groups for easier filtering"""
    if not sector or sector == '—':
        return 'Other'
    
    sector = sector.lower()
    industry = industry.lower() if industry else ''
    
    # AI & Technology
    if 'technology' in sector or 'software' in industry or 'artificial intelligence' in industry:
        if 'semiconductor' in industry or 'chip' in industry:
            return 'Semiconductors'
        elif 'software' in industry:
            return 'Software'
        else:
            return 'Technology'
    
    # Healthcare & Biotech
    elif 'healthcare' in sector or 'pharmaceutical' in industry or 'biotechnology' in industry:
        if 'biotechnology' in industry or 'biotech' in industry:
            return 'Biotech'
        else:
            return 'Healthcare'
    
    # Financial Services
    elif 'financial' in sector or 'bank' in industry:
        return 'Finance'
    
    # Energy & Utilities
    elif 'energy' in sector or 'utilities' in sector or 'oil' in industry:
        return 'Energy'
    
    # Defense & Aerospace
    elif 'aerospace' in industry or 'defense' in industry or 'military' in industry:
        return 'Defense'
    
    # Space & Satellite
    elif 'space' in industry or 'satellite' in industry:
        return 'Space'
    
    # Crypto & Blockchain
    elif 'crypto' in industry or 'blockchain' in industry or 'bitcoin' in industry:
        return 'Crypto'
    
    # Electric Vehicles & Clean Energy (now under Energy)
    elif 'electric vehicle' in industry or 'clean energy' in industry or 'solar' in industry:
        return 'Energy'
    
    # Consumer Goods
    elif 'consumer' in sector:
        return 'Consumer'
    
    # Real Estate
    elif 'real estate' in sector:
        return 'Real Estate'
    
    # Communication & Media
    elif 'communication' in sector or 'media' in industry:
        return 'Media'
    
    # Basic Materials
    elif 'materials' in sector or 'mining' in industry:
        return 'Materials'
    
    # Industrials
    elif 'industrial' in sector:
        return 'Industrial'
    
    else:
        return 'Other'

def fetch_stock_data(symbol, max_retries=1, base_delay=5.0):
    """Fetch comprehensive stock data with intelligent retry logic and rate limiting"""
    if not symbol:
        return None
    
    for attempt in range(max_retries):
        fetch_start_time = time.time()
        
        try:
            # Add delay between requests to respect rate limits
            if attempt > 0:
                delay = base_delay * (2 ** attempt)  # Exponential backoff
                print(f"🔄 Retry {attempt + 1}/{max_retries} for {symbol} after {delay:.1f}s delay...")
                time.sleep(delay)
            
            # Create ticker object with timeout
            ticker = yf.Ticker(symbol)
            
            # Get basic info with timeout protection
            try:
                info = ticker.info
                if not info or 'symbol' not in info:
                    raise ValueError(f"No data available for {symbol}")
            except Exception as e:
                if "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    if attempt < max_retries - 1:
                        print(f"⚠️  Rate limited for {symbol}, retrying in {base_delay * (2 ** attempt):.1f}s...")
                        continue
                    else:
                        print(f"❌ {symbol}: Rate limit exceeded after {max_retries} attempts")
                        return None
                else:
                    raise e
            
            # Get historical data for gap calculation
            try:
                hist = ticker.history(period="2d", interval="1d")
                if hist.empty or len(hist) < 2:
                    raise ValueError(f"Insufficient historical data for {symbol}")
            except Exception as e:
                if "rate limit" in str(e).lower():
                    if attempt < max_retries - 1:
                        continue
                    else:
                        print(f"❌ {symbol}: Historical data rate limited")
                        return None
                else:
                    raise e
            
            # Process the data (keeping existing logic)
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = hist['Close'].iloc[-2] if len(hist) >= 2 else None
            
            if not current_price or not previous_close:
                raise ValueError(f"Missing price data for {symbol}")
            
            # Calculate gap percentage
            gap_pct = ((current_price - previous_close) / previous_close) * 100
        
            # Get volume information
            current_volume = info.get('volume', info.get('regularMarketVolume', 0))
            avg_volume = info.get('averageVolume', info.get('averageVolume10days', 1))
            relative_volume = (current_volume / avg_volume) if avg_volume > 0 else 0
        
            # Market cap and other metrics
            market_cap = info.get('marketCap', 0)
            float_shares = info.get('floatShares', info.get('sharesOutstanding', 0))
            pe_ratio = info.get('trailingPE')
            sector = info.get('sector', 'Unknown')
            industry = info.get('industry', 'Unknown')
            
            # Determine category based on sector/industry, not gap percentage
            category = categorize_stock(sector, industry)
            
            # Add gap-based classification as a separate field for filtering
            if gap_pct >= 20:
                gap_classification = "🚀 EXPLOSIVE"
            elif gap_pct >= 10:
                gap_classification = "💥 HUGE GAPPER"
            elif gap_pct >= 5:
                gap_classification = "📈 BIG GAPPER"
            elif gap_pct <= -10:
                gap_classification = "📉 BIG LOSER"
            elif gap_pct <= -5:
                gap_classification = "⬇️ GAPPER DOWN"
            else:
                gap_classification = "📊 REGULAR"
        
            # Timestamp information
            fetch_timestamp = datetime.now()
            if PYTZ_AVAILABLE:
                et_tz = pytz.timezone('US/Eastern')
                fetch_timestamp_et = fetch_timestamp.astimezone(et_tz)
                et_time_str = fetch_timestamp_et.strftime('%H:%M:%S ET')
            else:
                # Fallback: use local time with ET offset
                et_offset = -5  # EST offset (simplified)
                fetch_timestamp_et = fetch_timestamp + timedelta(hours=et_offset)
                et_time_str = fetch_timestamp_et.strftime('%H:%M:%S ET')
            
            # FETCH REAL PRE-MARKET AND POST-MARKET DATA FROM YFINANCE
            pre_market_price = None
            post_market_price = None
            pre_market_change_pct = None
            post_market_change_pct = None
            
            # Get real after-hours data from yfinance
            try:
                # Check if yfinance has after-hours data
                has_pre_post_data = info.get('hasPrePostMarketData', False)
                market_state = info.get('marketState', 'REGULAR')
                
                if has_pre_post_data:
                    # Get post-market (after-hours) data
                    post_market_price = info.get('postMarketPrice')
                    post_market_change = info.get('postMarketChange')
                    post_market_change_pct = info.get('postMarketChangePercent')
                    
                    if post_market_price and post_market_price != current_price:
                        print(f"🔔 {symbol}: REAL AFTER-HOURS data - ${post_market_price:.2f} (Change: {post_market_change_pct:+.2f}%)")
                    
                    # Get pre-market data (if available)
                    pre_market_price = info.get('preMarketPrice')
                    pre_market_change = info.get('preMarketChange')
                    pre_market_change_pct = info.get('preMarketChangePercent')
                    
                    if pre_market_price and pre_market_price != current_price:
                        print(f"🔔 {symbol}: REAL PRE-MARKET data - ${pre_market_price:.2f} (Change: {pre_market_change_pct:+.2f}%)")
                
                # Fallback: Use time-based detection if no real data available
                if not has_pre_post_data:
                    # Get current Eastern Time
                    if PYTZ_AVAILABLE:
                        et_tz = pytz.timezone('US/Eastern')
                        current_time_et = fetch_timestamp.astimezone(et_tz)
                    else:
                        # Fallback: use local time with ET offset
                        et_offset = -5  # EST offset (simplified)
                        current_time_et = fetch_timestamp + timedelta(hours=et_offset)
                    
                    # Determine market session based on current time
                    hour = current_time_et.hour
                    minute = current_time_et.minute
                    time_decimal = hour + minute / 60.0
                    
                    # Check if it's a weekday
                    is_weekday = current_time_et.weekday() < 5
                    
                    if is_weekday:
                        if 4.0 <= time_decimal < 9.5:  # Pre-market: 4:00 AM to 9:30 AM ET
                            pre_market_price = current_price
                            pre_market_change_pct = gap_pct  # Use the same gap percentage
                            print(f"🔔 {symbol}: Time-based PRE-MARKET detection at {current_time_et.strftime('%H:%M:%S ET')} - ${current_price:.2f}")
                        elif 16.0 <= time_decimal < 20.0:  # Post-market: 4:00 PM to 8:00 PM ET
                            post_market_price = current_price
                            post_market_change_pct = gap_pct  # Use the same gap percentage
                            print(f"🔔 {symbol}: Time-based POST-MARKET detection at {current_time_et.strftime('%H:%M:%S ET')} - ${current_price:.2f}")
                        
            except Exception as e:
                print(f"⚠️  Error fetching pre/post market data for {symbol}: {e}")
            
                        # Use real market state from yfinance, with fallback to time-based detection
            market_state = info.get('marketState', 'REGULAR')
            
            # Map yfinance market states to our format
            if market_state == 'POST':
                market_state = 'AFTER-HOURS'
            elif market_state == 'PRE':
                market_state = 'PRE-MARKET'
            elif market_state == 'REGULAR':
                market_state = 'REGULAR'
            elif market_state == 'CLOSED':
                market_state = 'CLOSED'
            else:
                # Fallback to time-based detection if yfinance state is unclear
                if PYTZ_AVAILABLE:
                    et_tz = pytz.timezone('US/Eastern')
                    current_time_et = fetch_timestamp.astimezone(et_tz)
                else:
                    et_offset = -5
                    current_time_et = fetch_timestamp + timedelta(hours=et_offset)
                
                hour = current_time_et.hour
                minute = current_time_et.minute
                time_decimal = hour + minute / 60.0
                is_weekday = current_time_et.weekday() < 5
                
                if not is_weekday:
                    market_state = "WEEKEND"
                elif 4.0 <= time_decimal < 9.5:
                    market_state = "PRE-MARKET"
                elif 9.5 <= time_decimal < 16.0:
                    market_state = "REGULAR"
                elif 16.0 <= time_decimal < 20.0:
                    market_state = "AFTER-HOURS"
                else:
                    market_state = "CLOSED"
            
            return {
                'symbol': symbol,
                'price': current_price,
                'gap_pct': round(gap_pct, 2),
                'pct_change': round(gap_pct, 2),  # Same as gap for most purposes
                'previous_close': round(previous_close, 2),
                'volume': current_volume,
                'avg_volume': avg_volume,
                'relative_volume': round(relative_volume, 2),
                'market_cap': market_cap,
                'market_cap_display': format_market_cap(market_cap),
                'float': format_volume(float_shares) if float_shares else '—',
                'pe_ratio': pe_ratio,
                'pe_display': f"{pe_ratio:.2f}" if pe_ratio and pe_ratio > 0 else '—',
                'sector': sector,
                'industry': industry,
                'category': category,
                'gap_classification': gap_classification,
                'has_news': False,  # Could implement news detection later
                # Pre-market and post-market data (detected based on time)
                'pre_market_price': pre_market_price,
                'pre_market_price_display': f"${pre_market_price:.2f}" if pre_market_price else '—',
                'post_market_price': post_market_price,
                'post_market_price_display': f"${post_market_price:.2f}" if post_market_price else '—',
                'pre_market_change_pct': pre_market_change_pct,
                'post_market_change_pct': post_market_change_pct,
                # Market state information
                'market_state': market_state,
                # NEW: Timestamp tracking
                'data_fetch_time': fetch_timestamp.isoformat(),
                'data_fetch_time_et': et_time_str,
                'data_age_seconds': 0,  # Will be calculated when displaying
                'fetch_duration_ms': round((time.time() - fetch_start_time) * 1000, 1)
            }
        
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific rate limiting cases
            if "rate limit" in error_msg or "too many requests" in error_msg or "429" in error_msg:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt) + 5  # Extra delay for rate limits
                    print(f"⚠️  Rate limited for {symbol}, waiting {delay:.1f}s before retry {attempt + 2}/{max_retries}...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"❌ {symbol}: Rate limit exceeded after {max_retries} attempts")
                    return None
            
            # Handle other network errors
            elif any(keyword in error_msg for keyword in ['timeout', 'connection', 'network', 'unreachable']):
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⚠️  Network error for {symbol}, retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"❌ {symbol}: Network error after {max_retries} attempts: {e}")
                    return None
            
            # Handle data errors (no retry)
            else:
                print(f"❌ {symbol}: Data error: {e}")
                return None
    
    print(f"❌ {symbol}: Failed after {max_retries} attempts")
    return None

def check_missing_priority_stocks():
    """Check if priority stocks are missing from cache and force restart if needed"""
    try:
        # Load current cache
        cache_data = cache_manager.load_cache()
        if not cache_data or 'stocks' not in cache_data:
            return True  # Force restart if no cache
        
        cached_stocks = set(cache_data['stocks'].keys())
        
        # Priority stocks that should always be present
        priority_symbols = [
            'IXHL', 'TSLA', 'NVDA', 'AMD', 'GME', 'AMC', 'META', 'GOOGL', 'MSFT', 'AAPL', 'AMZN',
            'COIN', 'MSTR', 'RIOT', 'MARA', 'PLTR', 'SOFI', 'HOOD', 'RIVN', 'LCID', 'NIO', 'XPEV', 'LI',
            'BABA', 'JD', 'PDD', 'BIDU', 'NTES', 'TME', 'ZTO', 'BILI', 'DIDI', 'EDU', 'TAL', 'IQ', 'VIPS', 'YMM',
            'SAVA', 'BIIB', 'GILD', 'REGN', 'VRTX', 'MRNA', 'BNTX', 'PFE', 'JNJ', 'NVAX', 'SRNE', 'INO', 'OCGN', 'TNXP', 'PROG'
        ]
        
        missing_priority = [s for s in priority_symbols if s not in cached_stocks]
        
        if missing_priority:
            print(f"⚠️  Missing priority stocks: {missing_priority}")
            print("🔄 Forcing scanner restart to ensure complete coverage...")
            return True
        
        return False
        
    except Exception as e:
        print(f"⚠️  Error checking missing priority stocks: {e}")
        return True  # Force restart on error

def scan_gaps():
    """Main scanning function with improved error handling and priority stock coverage"""
    global last_scan_time
    
    try:
        # Check if we need to force restart due to missing priority stocks
        if check_missing_priority_stocks():
            print("🔄 Priority stocks missing - forcing complete rescan...")
            # Clear cache to force complete rescan
            cache_manager.clear_cache()
        
        print("🚀 Starting comprehensive gap scan...")
        print("⏳ Taking a 60s break before starting to respect rate limits...")
        time.sleep(60)  # 1 minute break before starting
        start_time = time.time()
        
        # Get market session info
        market_info = get_market_session_info()
        print(f"📅 Market Session: {market_info['session']} | Time: {market_info['current_time_et']}")
        
        # Get all symbols to scan
        symbols = get_biggest_gappers()
        
        if not symbols:
            print("❌ No symbols to scan!")
            return
        
        # Remove duplicates while preserving order
        unique_symbols = []
        seen = set()
        for symbol in symbols:
            if symbol not in seen:
                unique_symbols.append(symbol)
                seen.add(symbol)
        
        print(f"📊 Total unique symbols to scan: {len(unique_symbols)}")
        
        # Scan stocks with improved error handling
        successful_count = 0
        failed_count = 0
        stocks_data = {}
        
        for i, symbol in enumerate(unique_symbols, 1):
            try:
                print(f"📊 Scanning {symbol} ({i}/{len(unique_symbols)})...")
                
                # Add delay to respect rate limits
                if i > 1:
                    delay = RATE_LIMIT_DELAY
                    print(f"⏳ Waiting {delay}s to respect rate limits...")
                    time.sleep(delay)
                
                # Add extra delay every 3 requests to be extra conservative
                if i % 3 == 0:
                    extra_delay = 30
                    print(f"⏸️  Taking a {extra_delay}s break every 3 requests...")
                    time.sleep(extra_delay)
                
                # Fetch stock data with retry logic
                stock_data = fetch_stock_data(symbol, max_retries=1, base_delay=5.0)
                
                if stock_data:
                    stocks_data[symbol] = stock_data
                    successful_count += 1
                    gap_pct = stock_data.get('gap_pct', 0)
                    price = stock_data.get('price', 0)
                    print(f"✅ {symbol}: ${price:.2f} ({gap_pct:+.2f}% gap)")
                else:
                    failed_count += 1
                    print(f"❌ {symbol}: Failed to fetch data")
                
                # Add extra delay if we're hitting too many failures
                if failed_count > 1 and failed_count % 1 == 0:
                    extra_delay = 120  # 2 minute delay when hitting rate limits
                    print(f"⚠️  Multiple failures detected, adding {extra_delay}s delay...")
                    time.sleep(extra_delay)
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Error scanning {symbol}: {e}")
                continue
        
        # Save results
        if stocks_data:
            scan_summary = {
                'total_scanned': len(unique_symbols),
                'successful': successful_count,
                'failed': failed_count,
                'success_rate': round((successful_count / len(unique_symbols)) * 100, 1),
                'scan_duration_seconds': round(time.time() - start_time, 1),
                'market_session': market_info
            }
            
            # Create proper cache structure
            cache_data = {
                'stocks': stocks_data,
                'last_update': time.time(),
                'last_update_str': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'successful_count': successful_count,
                'total_count': len(unique_symbols),
                'scan_type': 'biggest_gappers',
                'market_session': market_info
            }
            
            cache_manager.save_cache(cache_data)
            
            print(f"\n🎉 Scan completed!")
            print(f"✅ Successful: {successful_count}/{len(unique_symbols)} ({scan_summary['success_rate']}%)")
            print(f"❌ Failed: {failed_count}")
            print(f"⏱️  Duration: {scan_summary['scan_duration_seconds']}s")
            print(f"📊 Market Session: {market_info['session']}")
            
            # Check if priority stocks are still missing
            missing_priority = check_missing_priority_stocks()
            if missing_priority:
                print("⚠️  Some priority stocks still missing - will retry on next cycle")
        else:
            print("❌ No stock data collected!")
            
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
            
            # If cache is fresh (less than 5 minutes old), preserve it
            if age_minutes < 5:
                print(f"✅ Cache is fresh ({age_minutes:.1f} minutes old) - preserving existing data")
                return cache_data
            else:
                print(f"🔄 Cache is stale ({age_minutes:.1f} minutes old) - will refresh")
                return None
    except Exception as e:
        print(f"⚠️  Could not load existing cache: {e}")
    
    return None

def main():
    """Main background gap scanner loop"""
    global running, last_scan_time
    
    print("🚀 Starting Background Gap Scanner")
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
    
    print(f"\n🎯 Gap scanner started. Press Ctrl+C to stop.")
    
    # Main loop
    while running:
        try:
            current_time = time.time()
            time_since_last = current_time - last_scan_time
            
            if time_since_last >= SCAN_INTERVAL:
                print(f"\n🔍 Starting scan cycle...")
                scan_gaps()
                last_scan_time = current_time  # Update scan time after successful scan
            else:
                remaining = SCAN_INTERVAL - time_since_last
                print(f"⏳ Next gap scan in {remaining:.0f} seconds...", end='\r')
            
            time.sleep(2)  # Check every 2 seconds for more responsive timing
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Unexpected error in main loop: {e}")
            print(f"🔄 Retrying in 10 seconds...")
            time.sleep(10)  # Wait before retrying
    
    print("\n✅ Gap scanner stopped gracefully")
    remove_pid_file()

if __name__ == "__main__":
    main() 