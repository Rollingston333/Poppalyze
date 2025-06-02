import streamlit as st
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import hmac
import json
import time
from bs4 import BeautifulSoup

# Password check
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password
        st.text_input(
            "Please enter the password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "Please enter the password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()

# Set page config to wide mode
st.set_page_config(
    page_title="Stock News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_time_ago(published_time):
    """Convert timestamp or string to a clean, user-friendly date/time format."""
    try:
        # If already a datetime object
        if isinstance(published_time, datetime):
            dt = published_time
        # If it's a float or int (timestamp)
        elif isinstance(published_time, (float, int)):
            dt = datetime.fromtimestamp(published_time, tz=timezone.utc)
        # If it's a string, try parsing ISO 8601 or Yahoo format
        elif isinstance(published_time, str):
            try:
                dt = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                try:
                    dt = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    try:
                        dt = datetime.strptime(published_time, "%Y-%m-%dT%H:%M:%S%z")
                    except ValueError:
                        try:
                            dt = datetime.strptime(published_time, "%Y-%m-%d")
                        except Exception:
                            return "Invalid date"
        else:
            return "Invalid date"

        # Always return a clean, readable date
        return dt.strftime("%b %d, %Y, %I:%M %p")
    except Exception:
        return "Invalid date"

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

# Add rate limiting
def rate_limited_call(func):
    """Decorator to add rate limiting to API calls"""
    last_call_time = {}
    
    def wrapper(ticker, *args, **kwargs):
        current_time = time.time()
        if ticker in last_call_time:
            time_since_last_call = current_time - last_call_time[ticker]
            if time_since_last_call < 2:  # Wait at least 2 seconds between calls for the same ticker
                time.sleep(2 - time_since_last_call)
        last_call_time[ticker] = time.time()
        return func(ticker, *args, **kwargs)
    return wrapper

# Get MarketAux API key from Streamlit secrets
def get_marketaux_api_key():
    return st.secrets.get("MARKETAUX_API_KEY")

# MarketAux news fetcher
def fetch_news_marketaux(ticker):
    api_key = get_marketaux_api_key()
    if not api_key:
        st.error("MarketAux API key not found. Please check your Streamlit secrets.")
        return []
    url = "https://api.marketaux.com/v1/news/all"
    params = {
        "api_token": api_key,
        "symbols": ticker,
        "language": "en",
        "limit": 5
    }
    try:
        st.info(f"Fetching news for {ticker}...")
        response = requests.get(url, params=params)
        if response.status_code != 200:
            st.error(f"API Error: Status Code {response.status_code}")
            st.error(f"Error Message: {response.text}")
            return []
        data = response.json()
        if 'data' not in data or not data['data']:
            st.info(f"No news articles found for {ticker} in the API response.")
            return []
        return data['data']
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

def fetch_news_yahoo_scrape(ticker):
    """Scrape Yahoo Finance news for a given ticker as a fallback."""
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}/news?p={ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        articles = []
        for item in soup.select('li.js-stream-content'):
            title_tag = item.find('h3')
            link_tag = item.find('a')
            summary_tag = item.find('p')
            time_tag = item.find('time')
            if not title_tag or not link_tag:
                continue
            article = {
                'title': title_tag.get_text(strip=True),
                'url': f"https://finance.yahoo.com{link_tag['href']}" if link_tag['href'].startswith('/') else link_tag['href'],
                'description': summary_tag.get_text(strip=True) if summary_tag else '',
                'published_at': time_tag['datetime'] if time_tag and time_tag.has_attr('datetime') else ''
            }
            articles.append(article)
        return articles
    except Exception as e:
        st.error(f"Yahoo Finance scraping error: {str(e)}")
        return []

# Update fetch_news logic to use Yahoo scrape as fallback

def fetch_news(ticker):
    news = fetch_news_marketaux(ticker)
    if not news:
        st.info("No news from MarketAux, trying Yahoo Finance scrape...")
        news = fetch_news_yahoo_scrape(ticker)
    return news

def display_news(ticker, articles):
    st.subheader(f"📰 News for {ticker}")
    if not articles:
        st.warning(f"No news articles found for {ticker}")
        return
    valid_articles = [a for a in articles if 'title' in a and 'url' in a]
    if not valid_articles:
        st.warning(f"No valid news articles found for {ticker}")
        return
    for article in valid_articles:
        try:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"### {article['title']}")
                with col2:
                    if 'published_at' in article:
                        time_ago = get_time_ago(article['published_at'])
                        st.markdown(f"<p style='text-align: right; color: #666; margin-top: 20px;'>{time_ago}</p>", unsafe_allow_html=True)
                if 'description' in article:
                    st.markdown(f"*{article['description'][:300]}...*")
                st.markdown(f"[Read full article →]({article['url']})")
                st.markdown("---")
        except Exception as e:
            st.error(f"Error displaying article: {str(e)}")
            continue

@rate_limited_call
def fetch_calendar_events(ticker):
    """Fetch calendar events for a given ticker using Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        calendar = stock.calendar
        
        if calendar is None or calendar.empty:
            return None
            
        # Convert the calendar to a more readable format
        events = []
        for index, row in calendar.iterrows():
            event = {
                'date': index.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'earnings_date': row.get('Earnings Date', 'N/A'),
                'earnings_average': row.get('Earnings Average', 'N/A'),
                'earnings_low': row.get('Earnings Low', 'N/A'),
                'earnings_high': row.get('Earnings High', 'N/A'),
                'revenue_average': row.get('Revenue Average', 'N/A'),
                'revenue_low': row.get('Revenue Low', 'N/A'),
                'revenue_high': row.get('Revenue High', 'N/A')
            }
            events.append(event)
            
        return events
    except Exception as e:
        if "Too Many Requests" in str(e):
            st.error("Rate limit reached. Please wait a moment and try again.")
        else:
            st.error(f"Error fetching calendar events: {str(e)}")
        return None

def display_calendar(ticker, events):
    """Display calendar events in a formatted way"""
    if not events:
        st.info(f"No upcoming events found for {ticker}")
        return
        
    st.subheader(f"📅 Upcoming Events for {ticker}")
    
    for event in events:
        with st.expander(f"📆 {get_time_ago(event['date'])}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Earnings Estimates**")
                st.markdown(f"Average: {event['earnings_average']}")
                st.markdown(f"Low: {event['earnings_low']}")
                st.markdown(f"High: {event['earnings_high']}")
            
            with col2:
                st.markdown("**Revenue Estimates**")
                st.markdown(f"Average: {event['revenue_average']}")
                st.markdown(f"Low: {event['revenue_low']}")
                st.markdown(f"High: {event['revenue_high']}")

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
    
    option = st.radio("Choose input method:", ["Single Ticker", "Watchlist Manager"])
    
    if option == "Single Ticker":
        ticker = st.text_input("Enter stock ticker (e.g., AAPL)", "").upper()
        if ticker:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Get News", key="single_ticker"):
                    with main_col:
                        news = fetch_news(ticker)
                        display_news(ticker, news)
            with col2:
                if st.button("Show Calendar", key="single_calendar"):
                    with main_col:
                        events = fetch_calendar_events(ticker)
                        display_calendar(ticker, events)

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
            
            if selected_list and selected_list in st.session_state.watchlists:
                process_watchlist_tickers(st.session_state.watchlists[selected_list], "news")
            else:
                st.warning("Please select a valid watchlist.")

with main_col:
    st.title("Stock News & Calendar")
    st.markdown("Select a ticker or watchlist from the sidebar to view news and upcoming events.")

# Modify the watchlist section to add delays between multiple ticker requests
def process_watchlist_tickers(tickers, action_type):
    """Process multiple tickers with rate limiting"""
    for i, ticker in enumerate(tickers):
        if i > 0:  # Add delay between tickers
            time.sleep(2)
        if action_type == "news":
            news = fetch_news(ticker)
            display_news(ticker, news)
        else:  # calendar
            events = fetch_calendar_events(ticker)
            display_calendar(ticker, events) 