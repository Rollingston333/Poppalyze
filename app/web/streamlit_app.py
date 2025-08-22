import streamlit as st
import yfinance as yf
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import threading
import os
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Poppalyze",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .positive-gap {
        color: #28a745;
        font-weight: bold;
    }
    .negative-gap {
        color: #dc3545;
        font-weight: bold;
    }
    .stock-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Data classes
class StockData:
    def __init__(self, symbol: str, current_price: float, previous_close: float, 
                 open_price: float, volume: int, market_cap: float, 
                 sector: str, gap_pct: float, rel_volume: float,
                 pre_market_price: float = None, pre_market_change_pct: float = None,
                 post_market_price: float = None, post_market_change_pct: float = None,
                 pe_ratio: float = None, float_shares: float = None):
        self.symbol = symbol
        self.current_price = current_price
        self.previous_close = previous_close
        self.open_price = open_price
        self.volume = volume
        self.market_cap = market_cap
        self.sector = sector
        self.gap_pct = gap_pct
        self.rel_volume = rel_volume
        self.pre_market_price = pre_market_price
        self.pre_market_change_pct = pre_market_change_pct
        self.post_market_price = post_market_price
        self.post_market_change_pct = post_market_change_pct
        self.pe_ratio = pe_ratio
        self.float_shares = float_shares
        
        # Format market cap
        if market_cap:
            if market_cap >= 1e12:
                self.market_cap_formatted = f"${market_cap/1e12:.1f}T"
            elif market_cap >= 1e9:
                self.market_cap_formatted = f"${market_cap/1e9:.1f}B"
            elif market_cap >= 1e6:
                self.market_cap_formatted = f"${market_cap/1e6:.1f}M"
            else:
                self.market_cap_formatted = f"${market_cap:,.0f}"
        else:
            self.market_cap_formatted = "N/A"
        
        # Format volume
        if volume:
            if volume >= 1e9:
                self.volume_formatted = f"{volume/1e9:.1f}B"
            elif volume >= 1e6:
                self.volume_formatted = f"{volume/1e6:.1f}M"
            elif volume >= 1e3:
                self.volume_formatted = f"{volume/1e3:.1f}K"
            else:
                self.volume_formatted = f"{volume:,}"
        else:
            self.volume_formatted = "N/A"

class StockScanner:
    def __init__(self):
        self.cache_file = "stock_cache.json"
        self.stocks = []
        self.last_update = None
        self.load_cache()
    
    def load_cache(self):
        """Load stock data from cache"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    logger.info(f"Cache file contents: {data}")
                    
                    # Handle different cache formats
                    if isinstance(data, dict):
                        if 'stocks' in data:
                            # New format
                            self.stocks = data.get('stocks', [])
                        else:
                            # Old format - convert to new format
                            self.stocks = list(data.values()) if data else []
                    else:
                        # Direct list format
                        self.stocks = data if isinstance(data, list) else []
                    
                    last_update_str = data.get('last_update') if isinstance(data, dict) else None
                    if last_update_str:
                        try:
                            self.last_update = datetime.fromisoformat(last_update_str)
                        except:
                            self.last_update = None
                    else:
                        self.last_update = None
                    
                    logger.info(f"Loaded {len(self.stocks)} stocks from cache")
                    
                    # If no stocks loaded, try to load from existing stock_cache.json
                    if not self.stocks and os.path.exists('stock_cache.json'):
                        logger.info("Trying to load from existing stock_cache.json...")
                        with open('stock_cache.json', 'r') as f:
                            existing_data = json.load(f)
                            if isinstance(existing_data, dict) and 'stocks' in existing_data:
                                self.stocks = list(existing_data['stocks'].values())
                                logger.info(f"Loaded {len(self.stocks)} stocks from existing cache")
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
            self.stocks = []
            self.last_update = None
    
    def save_cache(self):
        """Save stock data to cache"""
        try:
            data = {
                'stocks': self.stocks,
                'last_update': datetime.now().isoformat()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info("Cache saved successfully")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def fetch_stock_data(self, symbol: str) -> Optional[Dict]:
        """Fetch stock data from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current market data first (more reliable)
            hist = ticker.history(period="2d")
            if len(hist) < 2:
                return None
            
            # Get basic info with error handling
            try:
                info = ticker.info
            except Exception as e:
                logger.warning(f"Could not get info for {symbol}, using historical data only: {e}")
                info = {}
            
            current_price = info.get('currentPrice', hist.iloc[-1]['Close'])
            previous_close = hist.iloc[-2]['Close']
            open_price = hist.iloc[-1]['Open']
            volume = info.get('volume', hist.iloc[-1]['Volume'])
            market_cap = info.get('marketCap', 0)
            sector = info.get('sector', 'Unknown')
            
            # Get pre-market and post-market data
            pre_market_price = info.get('preMarketPrice')
            pre_market_change_pct = info.get('preMarketChangePercent')
            post_market_price = info.get('postMarketPrice')
            post_market_change_pct = info.get('postMarketChangePercent')
            
            # Get additional metrics
            pe_ratio = info.get('trailingPE')
            float_shares = info.get('floatShares')
            
            # Calculate gap percentage
            gap_pct = ((current_price - previous_close) / previous_close) * 100
            
            # Calculate relative volume (simplified)
            avg_volume = info.get('averageVolume', volume)
            rel_volume = (volume / avg_volume) if avg_volume > 0 else 1.0
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'previous_close': previous_close,
                'open_price': open_price,
                'volume': volume,
                'market_cap': market_cap,
                'sector': sector,
                'gap_pct': gap_pct,
                'rel_volume': rel_volume,
                'pre_market_price': pre_market_price,
                'pre_market_change_pct': pre_market_change_pct,
                'post_market_price': post_market_price,
                'post_market_change_pct': post_market_change_pct,
                'pe_ratio': pe_ratio,
                'float_shares': float_shares
            }
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def scan_stocks(self, symbols: List[str]):
        """Scan multiple stocks and update cache"""
        logger.info(f"Starting scan of {len(symbols)} stocks")
        new_stocks = []
        
        for symbol in symbols:
            try:
                data = self.fetch_stock_data(symbol)
                if data:
                    new_stocks.append(data)
                time.sleep(0.5)  # Increased rate limiting to avoid 429 errors
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                time.sleep(1.0)  # Extra delay on error
        
        self.stocks = new_stocks
        self.last_update = datetime.now()
        self.save_cache()
        logger.info(f"Scan completed: {len(self.stocks)} stocks updated")

# Initialize scanner
@st.cache_resource
def get_scanner():
    scanner = StockScanner()
    
    # If no cache data, try to load from existing files
    if not scanner.stocks:
        logger.info("No cache data found, checking for existing cache files...")
        
        # Try to load from existing stock_cache.json
        if os.path.exists('stock_cache.json'):
            try:
                with open('stock_cache.json', 'r') as f:
                    existing_data = json.load(f)
                    if isinstance(existing_data, dict) and 'stocks' in existing_data:
                        scanner.stocks = list(existing_data['stocks'].values())
                        logger.info(f"Loaded {len(scanner.stocks)} stocks from existing stock_cache.json")
                    elif isinstance(existing_data, dict):
                        # Convert old format
                        scanner.stocks = list(existing_data.values())
                        logger.info(f"Loaded {len(scanner.stocks)} stocks from old format cache")
            except Exception as e:
                logger.error(f"Error loading existing cache: {e}")
    
    return scanner

scanner = get_scanner()

# Stock symbols to scan (you can modify this list)
DEFAULT_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
    'CRM', 'ADBE', 'PYPL', 'UBER', 'LYFT', 'ZM', 'SQ', 'SHOP', 'ROKU', 'SPOT',
    'SNAP', 'TWTR', 'PINS', 'BYND', 'PLTR', 'SNOW', 'CRWD', 'ZS', 'OKTA', 'TEAM',
    'HCTI', 'GME', 'AMC', 'BBBY', 'NOK', 'BB', 'EXPR', 'NAKD', 'SNDL', 'TLRY'
]

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Poppalyze</h1>
        <p>Real-time stock gap analysis and screening</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.header("🔧 Controls")
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data", type="primary"):
        with st.spinner("Scanning stocks (this may take a few minutes due to rate limiting)..."):
            scanner.scan_stocks(DEFAULT_SYMBOLS)
        st.success("Data refreshed!")
        st.rerun()
    
    # Quick load button for testing
    if st.sidebar.button("⚡ Quick Load (Sample Data)", type="secondary"):
        with st.spinner("Loading sample data..."):
            # Create sample data for testing
            sample_stocks = [
                {
                    'symbol': 'HCTI',
                    'current_price': 12.50,
                    'previous_close': 10.00,
                    'open_price': 11.00,
                    'volume': 1500000,
                    'market_cap': 50000000,
                    'sector': 'Technology',
                    'gap_pct': 25.0,
                    'rel_volume': 2.5,
                    'pre_market_price': 12.75,
                    'pre_market_change_pct': 27.5,
                    'post_market_price': None,
                    'post_market_change_pct': None,
                    'pe_ratio': 15.5,
                    'float_shares': 8000000
                },
                {
                    'symbol': 'AAPL',
                    'current_price': 175.50,
                    'previous_close': 170.00,
                    'open_price': 172.00,
                    'volume': 50000000,
                    'market_cap': 2750000000000,
                    'sector': 'Technology',
                    'gap_pct': 3.24,
                    'rel_volume': 1.2,
                    'pre_market_price': None,
                    'pre_market_change_pct': None,
                    'post_market_price': None,
                    'post_market_change_pct': None,
                    'pe_ratio': 28.5,
                    'float_shares': 15500000000
                }
            ]
            scanner.stocks = sample_stocks
            scanner.last_update = datetime.now()
            scanner.save_cache()
        st.success("Sample data loaded!")
        st.rerun()
    
    # Filter controls
    st.sidebar.header("📊 Filters")
    
    min_gap = st.sidebar.slider("Min Gap %", -50.0, 50.0, -10.0, 0.5)
    min_price = st.sidebar.number_input("Min Price", 0.0, 1000.0, 1.0, 0.1)
    max_price = st.sidebar.number_input("Max Price", 0.0, 1000.0, 100.0, 0.1)
    min_rel_volume = st.sidebar.number_input("Min Relative Volume", 0.0, 10.0, 0.5, 0.1)
    
    # Advanced filters
    st.sidebar.header("🔧 Advanced Filters")
    
    min_market_cap = st.sidebar.number_input("Min Market Cap (M)", 0.0, 10000.0, 0.0, 100.0) * 1e6
    max_market_cap = st.sidebar.number_input("Max Market Cap (B)", 0.0, 1000.0, 1000.0, 10.0) * 1e9
    max_float = st.sidebar.number_input("Max Float (M)", 0.0, 10000.0, 10000.0, 100.0) * 1e6
    min_pe_ratio = st.sidebar.number_input("Min PE Ratio", 0.0, 100.0, 0.0, 1.0)
    max_pe_ratio = st.sidebar.number_input("Max PE Ratio", 0.0, 1000.0, 1000.0, 10.0)
    
    # Pre-market filters
    st.sidebar.header("🌅 Pre-Market")
    min_pre_market = st.sidebar.number_input("Min Pre-Market Price", 0.0, 1000.0, 0.0, 0.1)
    max_pre_market = st.sidebar.number_input("Max Pre-Market Price", 0.0, 1000.0, 1000.0, 0.1)
    min_pre_market_change = st.sidebar.slider("Min Pre-Market Change %", -50.0, 50.0, -50.0, 0.5)
    max_pre_market_change = st.sidebar.slider("Max Pre-Market Change %", -50.0, 50.0, 50.0, 0.5)
    
    # Post-market filters
    st.sidebar.header("🌙 Post-Market")
    min_post_market = st.sidebar.number_input("Min Post-Market Price", 0.0, 1000.0, 0.0, 0.1)
    max_post_market = st.sidebar.number_input("Max Post-Market Price", 0.0, 1000.0, 1000.0, 0.1)
    min_post_market_change = st.sidebar.slider("Min Post-Market Change %", -50.0, 50.0, -50.0, 0.5)
    max_post_market_change = st.sidebar.slider("Max Post-Market Change %", -50.0, 50.0, 50.0, 0.5)
    
    # Sector filter
    sectors = ['All'] + list(set([stock.get('sector', 'Unknown') for stock in scanner.stocks]))
    selected_sector = st.sidebar.selectbox("Sector", sectors)
    
    # Independent vs Filtered modes
    st.sidebar.header("🎯 Display Modes")
    quick_movers_independent = st.sidebar.checkbox("Quick Movers: Show All Stocks", value=True)
    top_gappers_independent = st.sidebar.checkbox("Top Gappers: Show All Stocks", value=True)
    
    # Cache status info
    st.sidebar.header("💾 Cache Info")
    if scanner.stocks:
        st.sidebar.success(f"✅ Cache loaded: {len(scanner.stocks)} stocks")
        if scanner.last_update and isinstance(scanner.last_update, datetime):
            st.sidebar.info(f"📅 Last update: {scanner.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.sidebar.warning("⚠️ No cache data available")
        st.sidebar.info("Click 'Quick Load' for sample data or 'Refresh Data' for real data")
    
    # Debug info
    if st.sidebar.checkbox("🔍 Show Debug Info"):
        st.sidebar.header("🐛 Debug Info")
        st.sidebar.text(f"Cache file: {scanner.cache_file}")
        st.sidebar.text(f"Cache exists: {os.path.exists(scanner.cache_file)}")
        st.sidebar.text(f"Stock cache exists: {os.path.exists('stock_cache.json')}")
        st.sidebar.text(f"Stocks loaded: {len(scanner.stocks)}")
        if scanner.stocks:
            st.sidebar.text(f"First stock: {scanner.stocks[0].get('symbol', 'Unknown')}")
    
    # Main content
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Stocks", len(scanner.stocks))
    
    with col2:
        if scanner.last_update and isinstance(scanner.last_update, datetime):
            st.metric("Last Update", scanner.last_update.strftime("%H:%M:%S"))
        else:
            st.metric("Last Update", "Never")
    
    with col3:
        positive_gaps = len([s for s in scanner.stocks if s.get('gap_pct', 0) > 0])
        st.metric("Positive Gaps", positive_gaps)
    
    with col4:
        negative_gaps = len([s for s in scanner.stocks if s.get('gap_pct', 0) < 0])
        st.metric("Negative Gaps", negative_gaps)
    
    # Filter stocks
    filtered_stocks = []
    for stock in scanner.stocks:
        gap_pct = stock.get('gap_pct', 0)
        current_price = stock.get('current_price', 0)
        rel_volume = stock.get('rel_volume', 0)
        sector = stock.get('sector', 'Unknown')
        market_cap = stock.get('market_cap', 0)
        pe_ratio = stock.get('pe_ratio')
        float_shares = stock.get('float_shares')
        pre_market_price = stock.get('pre_market_price')
        pre_market_change_pct = stock.get('pre_market_change_pct')
        post_market_price = stock.get('post_market_price')
        post_market_change_pct = stock.get('post_market_change_pct')
        
        # Basic filters
        if (gap_pct >= min_gap and
            min_price <= current_price <= max_price and
            rel_volume >= min_rel_volume and
            (selected_sector == 'All' or sector == selected_sector)):
            
            # Advanced filters
            if market_cap and (market_cap < min_market_cap or market_cap > max_market_cap):
                continue
            if pe_ratio and (pe_ratio < min_pe_ratio or pe_ratio > max_pe_ratio):
                continue
            if float_shares and max_float and float_shares > max_float:
                continue
            if pre_market_price and (pre_market_price < min_pre_market or pre_market_price > max_pre_market):
                continue
            if pre_market_change_pct and (pre_market_change_pct < min_pre_market_change or pre_market_change_pct > max_pre_market_change):
                continue
            if post_market_price and (post_market_price < min_post_market or post_market_price > max_post_market):
                continue
            if post_market_change_pct and (post_market_change_pct < min_post_market_change or post_market_change_pct > max_post_market_change):
                continue
            
            filtered_stocks.append(stock)
    
    # Sort by gap percentage
    filtered_stocks.sort(key=lambda x: abs(x.get('gap_pct', 0)), reverse=True)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Stock Results", "🔥 Top Gappers", "⚡ Quick Movers"])
    
    with tab1:
        st.header("📊 Stock Results")
        st.write(f"Showing {len(filtered_stocks)} stocks (filtered from {len(scanner.stocks)} total)")
        
        if filtered_stocks:
            # Convert to DataFrame for better display
            df_data = []
            for stock in filtered_stocks:
                df_data.append({
                    'Symbol': stock.get('symbol', ''),
                    'Current Price': f"${stock.get('current_price', 0):.2f}",
                    'Previous Close': f"${stock.get('previous_close', 0):.2f}",
                    'Gap %': f"{stock.get('gap_pct', 0):.2f}%",
                    'Volume': f"{stock.get('volume', 0):,}",
                    'Rel Volume': f"{stock.get('rel_volume', 0):.2f}",
                    'Market Cap': stock.get('market_cap_formatted', 'N/A'),
                    'Sector': stock.get('sector', 'Unknown')
                })
            
            df = pd.DataFrame(df_data)
            
            # Apply styling to gap column
            def color_gap(val):
                try:
                    gap = float(val.replace('%', ''))
                    if gap > 0:
                        return 'background-color: #d4edda; color: #155724;'
                    elif gap < 0:
                        return 'background-color: #f8d7da; color: #721c24;'
                    else:
                        return ''
                except:
                    return ''
            
            styled_df = df.style.applymap(color_gap, subset=['Gap %'])
            st.dataframe(styled_df, use_container_width=True)
        else:
            st.warning("No stocks match your current filters. Try adjusting the filter criteria.")
    
    with tab2:
        st.header("🔥 Top Gappers")
        
        # Get top gappers based on independent setting
        if top_gappers_independent:
            source_stocks = scanner.stocks  # Use all stocks
            st.info("Showing top gappers from ALL stocks (independent mode)")
        else:
            source_stocks = filtered_stocks  # Use filtered stocks
            st.info("Showing top gappers from FILTERED stocks only")
        
        top_gappers = sorted(source_stocks, key=lambda x: abs(x.get('gap_pct', 0)), reverse=True)[:10]
        
        if top_gappers:
            gapper_data = []
            for stock in top_gappers:
                gapper_data.append({
                    'Symbol': stock.get('symbol', ''),
                    'Current Price': f"${stock.get('current_price', 0):.2f}",
                    'Gap %': f"{stock.get('gap_pct', 0):.2f}%",
                    'Volume': f"{stock.get('volume', 0):,}",
                    'Rel Volume': f"{stock.get('rel_volume', 0):.2f}",
                    'Market Cap': stock.get('market_cap_formatted', 'N/A'),
                    'Sector': stock.get('sector', 'Unknown')
                })
            
            gapper_df = pd.DataFrame(gapper_data)
            styled_gapper_df = gapper_df.style.applymap(color_gap, subset=['Gap %'])
            st.dataframe(styled_gapper_df, use_container_width=True)
        else:
            st.info("No gapper data available. Refresh the data to see top gappers.")
    
    with tab3:
        st.header("⚡ Quick Movers")
        
        # Get quick movers based on independent setting
        if quick_movers_independent:
            source_stocks = scanner.stocks  # Use all stocks
            st.info("Showing quick movers from ALL stocks (independent mode)")
        else:
            source_stocks = filtered_stocks  # Use filtered stocks
            st.info("Showing quick movers from FILTERED stocks only")
        
        quick_movers = sorted(source_stocks, key=lambda x: x.get('rel_volume', 0), reverse=True)[:10]
        
        if quick_movers:
            mover_data = []
            for stock in quick_movers:
                mover_data.append({
                    'Symbol': stock.get('symbol', ''),
                    'Current Price': f"${stock.get('current_price', 0):.2f}",
                    'Gap %': f"{stock.get('gap_pct', 0):.2f}%",
                    'Volume': f"{stock.get('volume', 0):,}",
                    'Rel Volume': f"{stock.get('rel_volume', 0):.2f}",
                    'Market Cap': stock.get('market_cap_formatted', 'N/A'),
                    'Sector': stock.get('sector', 'Unknown')
                })
            
            mover_df = pd.DataFrame(mover_data)
            styled_mover_df = mover_df.style.applymap(color_gap, subset=['Gap %'])
            st.dataframe(styled_mover_df, use_container_width=True)
        else:
            st.info("No quick mover data available. Refresh the data to see quick movers.")
    
    # Auto-refresh option
    st.sidebar.header("⚙️ Settings")
    auto_refresh = st.sidebar.checkbox("Auto-refresh every 5 minutes", value=False)
    
    if auto_refresh:
        st.sidebar.info("Auto-refresh is enabled. Data will update automatically.")
        # In a real implementation, you'd use st.empty() and time.sleep() for auto-refresh
        # For now, we'll just show a message

if __name__ == "__main__":
    main() 