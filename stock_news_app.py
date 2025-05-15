import streamlit as st
import requests
import os
import json
from datetime import datetime, timezone

def check_password():
    """Check if the password is correct"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Enter password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password")
        return False
    else:
        return True

# Set page config to wide mode
st.set_page_config(
    page_title="Stock News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Check password before showing any content
if not check_password():
    st.stop()

# Get API key from Streamlit secrets
API_KEY = st.secrets["MARKETAUX_API_KEY"]

def get_time_ago(published_time_str):
    """Convert timestamp to 'time ago' format"""
    try:
        # Parse the ISO format timestamp
        published_time = datetime.strptime(published_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        published_time = published_time.replace(tzinfo=timezone.utc)
        
        # Get current time in UTC
        now = datetime.now(timezone.utc)
        
        # Calculate the time difference
        diff = now - published_time
        
        # Convert to total seconds
        seconds = int(diff.total_seconds())
        
        # Define time intervals
        intervals = [
            ('year', seconds // (365 * 24 * 60 * 60)),
            ('month', seconds // (30 * 24 * 60 * 60)),
            ('week', seconds // (7 * 24 * 60 * 60)),
            ('day', seconds // (24 * 60 * 60)),
            ('hour', seconds // (60 * 60)),
            ('minute', seconds // 60),
            ('second', seconds)
        ]
        
        # Find the appropriate time interval
        for interval, count in intervals:
            if count > 0:
                # Handle plural forms
                if count == 1:
                    return f"{count} {interval} ago"
                else:
                    return f"{count} {interval}s ago"
        
        return "just now"
        
    except Exception:
        return published_time_str  # Return original string if parsing fails

# Check if API key is loaded
if not API_KEY:
    st.error("⚠️ MarketAux API key not found. Please check your .streamlit/secrets.toml file.")
    st.stop()

# Initialize session state for watchlists if it doesn't exist
if 'watchlists' not in st.session_state:
    st.session_state.watchlists = {}

def load_watchlists():
    """Load watchlists from JSON file"""
    try:
        with open('watchlists.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_watchlists(watchlists):
    """Save watchlists to JSON file"""
    with open('watchlists.json', 'w') as f:
        json.dump(watchlists, f)

def fetch_news_marketaux(ticker):
    url = f"https://api.marketaux.com/v1/news/all"
    params = {
        "api_token": API_KEY,
        "symbols": ticker,
        "language": "en",
        "limit": 5
    }
    
    try:
        st.info(f"Fetching news for {ticker}...")
        response = requests.get(url, params=params)
        
        # Debug information
        if response.status_code != 200:
            st.error(f"API Error: Status Code {response.status_code}")
            st.error(f"Error Message: {response.text}")
            return []
            
        data = response.json()
        
        # Check if we got a valid response
        if 'data' not in data:
            st.warning(f"Unexpected API response format for {ticker}. Response: {data}")
            return []
            
        if not data['data']:
            st.info(f"No news articles found for {ticker} in the API response.")
            return []
            
        return data['data']
        
    except requests.exceptions.RequestException as e:
        st.error(f"Request Error: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        st.error(f"JSON Parsing Error: {str(e)}")
        return []
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return []

def display_news(ticker, articles):
    st.subheader(f"📰 News for {ticker}")
    if not articles:
        st.warning(f"No news articles found for {ticker}")
        return
    
    # Use columns for better layout
    for article in articles:
        try:
            with st.container():
                # Title and metadata row
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {article['title']}")
                with col2:
                    time_ago = get_time_ago(article['published_at'])
                    st.markdown(f"<p style='text-align: right; color: #666; margin-top: 20px;'>{time_ago}</p>", unsafe_allow_html=True)
                
                # Description and link
                st.markdown(f"*{article.get('description', '')[:300]}...*")
                st.markdown(f"[Read full article →]({article['url']})")
                
                # Add some space between articles
                st.markdown("---")
        except KeyError as e:
            st.error(f"Error displaying article: Missing field {e}")
            continue

# Use custom CSS to improve layout
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    </style>
    """, unsafe_allow_html=True)

# Create two columns for the main layout
sidebar_col, main_col = st.columns([1, 3])

with sidebar_col:
    st.title("📈 Dashboard")
    
    # Display API key status
    if API_KEY:
        st.success("✅ API Key loaded")
    else:
        st.error("❌ API Key missing")
    
    option = st.radio("Choose input method:", ["Single Ticker", "Watchlist Manager"])
    
    if option == "Single Ticker":
        ticker = st.text_input("Enter stock ticker (e.g., AAPL)", "").upper()
        if ticker and st.button("Get News", key="single_ticker"):
            with main_col:
                news = fetch_news_marketaux(ticker)
                display_news(ticker, news)

    elif option == "Watchlist Manager":
        st.subheader("Manage Watchlists")
        
        # Create new watchlist
        with st.expander("Create New Watchlist"):
            new_list_name = st.text_input("Watchlist Name")
            new_tickers = st.text_input("Enter comma-separated tickers (e.g., MSFT,NVDA,TSLA)")
            if st.button("Create Watchlist") and new_list_name and new_tickers:
                ticker_list = [t.strip().upper() for t in new_tickers.split(",")]
                st.session_state.watchlists[new_list_name] = ticker_list
                save_watchlists(st.session_state.watchlists)
                st.success(f"Watchlist '{new_list_name}' created!")

        # View and manage existing watchlists
        if st.session_state.watchlists:
            selected_list = st.selectbox(
                "Select Watchlist",
                options=list(st.session_state.watchlists.keys())
            )
            
            if selected_list:
                # Display and edit selected watchlist
                current_tickers = ",".join(st.session_state.watchlists[selected_list])
                edited_tickers = st.text_input("Edit Tickers", value=current_tickers)
                
                update_col, delete_col = st.columns(2)
                
                with update_col:
                    if st.button("Update"):
                        ticker_list = [t.strip().upper() for t in edited_tickers.split(",")]
                        st.session_state.watchlists[selected_list] = ticker_list
                        save_watchlists(st.session_state.watchlists)
                        st.success("Watchlist updated!")
                
                with delete_col:
                    if st.button("Delete Watchlist"):
                        del st.session_state.watchlists[selected_list]
                        save_watchlists(st.session_state.watchlists)
                        st.success(f"Watchlist '{selected_list}' deleted!")
                        st.rerun()
                
                if st.button("Get News", key="watchlist"):
                    with main_col:
                        for ticker in st.session_state.watchlists[selected_list]:
                            news = fetch_news_marketaux(ticker)
                            display_news(ticker, news)
        else:
            st.info("No watchlists created yet. Create your first watchlist above!")

with main_col:
    st.title("Stock News")
    st.markdown("Select a ticker or watchlist from the sidebar to view news.") 