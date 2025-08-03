import streamlit as st

st.set_page_config(
    page_title="Stock News Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    '''
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stSidebar"], [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"], [data-testid="stBlock"], [data-testid="stSidebarContent"], [data-testid="stSidebarNav"], [data-testid="stSidebarUserContent"], [data-testid="stSidebarFooter"], [data-testid="stSidebarCollapseControl"], .main, .block-container, .stApp {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
    }
    * {
        color: #000000 !important;
        border-color: #000000 !important;
    }
    input, select, textarea {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
    }
    .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stSelectbox [data-baseweb="input"] {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
    }
    .stNumberInput, .stSelectbox, .stTextInput {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
    }
    [data-baseweb="select"] [role="listbox"], [data-baseweb="select"] [role="option"],
    [data-baseweb="popover"] > div, [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"],
    [data-baseweb="menu"] {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
    }
    [data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] {
        background-color: #e0d8c3 !important;
        color: #000000 !important;
    }
    .stSelectbox [data-baseweb="popover"] {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
        box-shadow: none !important;
    }
    div[data-baseweb="popover"] > div {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
        box-shadow: none !important;
    }
    /* Steve Jobs-inspired number input and select styling */
    .stNumberInput {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        display: flex !important;
        align-items: center !important;
        padding: 0 !important;
    }
    .stNumberInput input {
        background: #f5f0e6 !important;
        color: #000 !important;
        border: 1.5px solid #007bff !important;
        border-right: none !important;
        border-radius: 0.5rem 0 0 0.5rem !important;
        padding: 0.5rem 1rem !important;
        font-size: 1rem !important;
        box-shadow: none !important;
        outline: none !important;
        width: 3.5rem !important;
        min-width: 2.5rem !important;
        text-align: center !important;
    }
    .stNumberInput > div[role='group'] {
        display: flex !important;
        flex-direction: row !important;
        margin: 0 !important;
        padding: 0 !important;
        border-radius: 0 0.5rem 0.5rem 0 !important;
        overflow: hidden !important;
        border: 1.5px solid #007bff !important;
        border-left: none !important;
        background: none !important;
    }
    .stNumberInput button:first-child {
        background: #007bff !important;
        color: #fff !important;
        border: none !important;
        border-radius: 0 !important;
        width: 2.2rem !important;
        height: 2.2rem !important;
        font-size: 1.2rem !important;
        margin: 0 !important;
        box-shadow: none !important;
        transition: background 0.2s;
        border-right: 1px solid #f5f0e6 !important;
    }
    .stNumberInput button:last-child {
        background: #007bff !important;
        color: #fff !important;
        border: none !important;
        border-radius: 0 0.5rem 0.5rem 0 !important;
        width: 2.2rem !important;
        height: 2.2rem !important;
        font-size: 1.2rem !important;
        margin: 0 !important;
        box-shadow: none !important;
        transition: background 0.2s;
    }
    .stNumberInput button:active,
    .stNumberInput button:focus {
        background: #0056b3 !important;
        outline: 2px solid #222 !important;
    }
    /* Sort by date selectbox styling */
    .stSelectbox div[data-baseweb="select"], .stSelectbox [data-baseweb="input"], .stSelectbox input {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border: 1.5px solid #007bff !important;
        border-radius: 0.5rem !important;
        font-size: 1rem !important;
        box-shadow: none !important;
        padding: 0.5rem 1rem !important;
        min-height: 2.2rem !important;
    }
    [data-baseweb="select"] [role="listbox"], [data-baseweb="select"] [role="option"],
    [data-baseweb="popover"] > div, [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"],
    [data-baseweb="menu"] {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
    }
    [data-baseweb="option"]:hover, [data-baseweb="option"][aria-selected="true"] {
        background-color: #e0d8c3 !important;
        color: #000000 !important;
    }
    .stSelectbox [data-baseweb="popover"] {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
        box-shadow: none !important;
    }
    div[data-baseweb="popover"] > div {
        background-color: #f5f0e6 !important;
        color: #000000 !important;
        border-radius: 0.5rem !important;
        border: 1px solid #000000 !important;
        box-shadow: none !important;
    }
    /* Align sort by date and results per page controls */
    .sort-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        gap: 2rem;
        margin-bottom: 1.5rem;
    }
    .sort-row .stSelectbox, .sort-row .stNumberInput {
        flex: 1 1 0;
        min-width: 180px;
        max-width: 320px;
        margin-bottom: 0 !important;
    }
    .sort-row label {
        margin-bottom: 0.25rem !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
    }
    .nuntius-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 5.5rem;
        background: #f5f0e6 !important;
        z-index: 99999 !important;
        display: flex;
        align-items: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-bottom: 2px solid #007bff;
    }
    .nuntius-title {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 900;
        font-size: 2.8rem;
        letter-spacing: 0.18em;
        color: #000 !important;
        margin-left: 2.5rem;
        user-select: none;
        text-shadow: 0 1px 0 #fff, 0 2px 8px rgba(0,0,0,0.04);
    }
    </style>
    ''',
    unsafe_allow_html=True
)

import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
import hmac
import json
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import base64
from utils import load_watchlists
import xml.etree.ElementTree as ET
import urllib.request
import subprocess

# Password check
def check_password():
    """Returns `True` if the user had the correct password."""
    
    # Initialize session state for password check if not exists
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    # If already authenticated, return immediately
    if st.session_state["password_correct"]:
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["PASSWORD"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    # Only show password input if not authenticated
    if not st.session_state["password_correct"]:
        st.text_input(
            "Please enter the password", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        if "password" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Password incorrect")
        return False
    
    return True

# Cache the password check result
if not check_password():
    st.stop()

EMPTY_ICON = "https://img.icons8.com/ios-filled/100/000000/news.png"

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
    st.session_state['watchlists'] = load_watchlists()

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

def fetch_news_yahoo_puppeteer(ticker):
    try:
        result = subprocess.run(
            ['node', 'yahoo_news_scrape.js', ticker],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            st.error(f"Puppeteer error: {result.stderr}")
            return []
    except Exception as e:
        st.error(f"Puppeteer exception: {e}")
        return []

def fetch_news_google(ticker):
    api_key = st.secrets.get("GNEWS_API_KEY", "2c2ca85e5cb940c7bc91e25c561ded9c")
    url = f"https://gnews.io/api/v4/search?q={ticker}&lang=en&token={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Normalize to match other sources
        articles = []
        for a in data.get("articles", []):
            articles.append({
                'title': a.get('title'),
                'url': a.get('url'),
                'description': a.get('description', ''),
                'published_at': a.get('publishedAt', '')
            })
        return articles
    else:
        return []

def fetch_rss_news(ticker):
    """Fetch news from Yahoo Finance RSS feed using XML parsing instead of feedparser"""
    url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
    articles = []
    try:
        with urllib.request.urlopen(url) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            
            # Find all item elements in the RSS feed
            for item in root.findall('.//item'):
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                pubDate = item.find('pubDate')
                
                if title is not None and link is not None:
                    article = {
                        'title': title.text,
                        'url': link.text,
                        'description': description.text if description is not None else '',
                        'published_at': pubDate.text if pubDate is not None else '',
                        'source': 'Yahoo RSS'
                    }
                    articles.append(article)
    except Exception as e:
        st.error(f"Error fetching RSS feed: {str(e)}")
    
    return articles

def fetch_news(ticker):
    news_marketaux = fetch_news_marketaux(ticker)
    for a in news_marketaux:
        a['source'] = 'MarketAux'
    news_yahoo = fetch_news_yahoo_puppeteer(ticker)
    for a in news_yahoo:
        a['source'] = 'Yahoo (Puppeteer)'
    news_google = fetch_news_google(ticker)
    for a in news_google:
        a['source'] = 'Google News'
    news_rss = fetch_rss_news(ticker)
    all_articles = news_marketaux + news_yahoo + news_google + news_rss
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        url = article.get('url')
        if url and url not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(url)
    return unique_articles

def display_news(ticker, articles):
    if not articles:
        st.markdown(f"""
            <div style='text-align: center; padding: 3rem 2rem; background: #fff; border-radius: 12px; box-shadow: 0 4px 16px rgba(220,193,171,0.1); width: 100vw; max-width: 100vw;'>
                <img src='{EMPTY_ICON}' width='60' style='margin-bottom: 1rem;'/>
                <h3 style='color: #DCC1AB; margin-bottom: 0.5rem;'>No news articles found for {ticker}</h3>
                <p style='color: #888;'>Try a different ticker or check your spelling.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    valid_articles = [a for a in articles if 'title' in a and 'url' in a]
    if not valid_articles:
        st.markdown(f"""
            <div style='text-align: center; padding: 3rem 2rem; background: #fff; border-radius: 12px; box-shadow: 0 4px 16px rgba(220,193,171,0.1); width: 100vw; max-width: 100vw;'>
                <img src='{EMPTY_ICON}' width='60' style='margin-bottom: 1rem;'/>
                <h3 style='color: #DCC1AB; margin-bottom: 0.5rem;'>No valid news articles found for {ticker}</h3>
                <p style='color: #888;'>Try a different ticker or check your spelling.</p>
            </div>
        """, unsafe_allow_html=True)
        return
    for article in valid_articles:
        st.markdown(f"""
            <div class="news-article">
                <div style='display: flex; justify-content: space-between; align-items: flex-start; width: 100%;'>
                    <div style='flex: 1;'>
                        <h3 style='color: #111; margin-bottom: 0.5rem; font-weight: 700;'>{article['title']}</h3>
                        {f"<p style='color: #666; margin-bottom: 1rem;'><em>{article['description'][:300]}...</em></p>" if 'description' in article else ""}
                        <a href='{article['url']}' style='color: #007bff; text-decoration: none; font-weight: 500; display: inline-block; margin-top: 0.5rem;'>Read full article →</a>
                    </div>
                    <div style='text-align: right; margin-left: 1rem;'>
                        {f"<p style='color: #666; margin-bottom: 0.5rem;'>{get_time_ago(article['published_at'])}</p>" if 'published_at' in article else ""}
                        {f"<span style='color: #888; font-size: 0.9em; background: #f7f3ef; border-radius: 6px; padding: 4px 12px; display: inline-block;'>{article['source']}</span>" if 'source' in article else ""}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

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

# Place this after other function definitions, before UI code
def process_watchlist_tickers(tickers):
    """Fetch news for multiple tickers in parallel and return a dict of results."""
    results = {}
    def fetch(ticker):
        return ticker, fetch_news(ticker)
    with ThreadPoolExecutor(max_workers=5) as executor:
        for ticker, articles in executor.map(fetch, tickers):
            results[ticker] = articles
    return results

# Use custom CSS to improve layout
st.markdown("""
    <style>
    html, body {
        width: 100vw !important;
        min-width: 100vw !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        background: #f5f0e6 !important;
        color: #000000 !important;
        font-size: 16px !important;
        box-sizing: border-box !important;
        overflow-x: hidden !important;
    }
    .main-content-container {
        max-width: 1200px;
        width: 100%;
        margin: 0 auto;
        padding-left: 2vw;
        padding-right: 2vw;
        box-sizing: border-box;
        background: #f5f0e6 !important;
        color: #000000 !important;
    }
    .news-article {
        width: 100%;
        margin: 0 0 2rem 0;
        padding: 1.5rem 0;
        border-radius: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        background: #f5f0e6 !important;
        color: #000000 !important;
        box-sizing: border-box;
    }
    .news-article a {
        color: #007bff !important;
        text-decoration: none;
        font-weight: 600;
    }
    .news-article a:hover {
        text-decoration: underline;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div {
        width: 100%;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        background: #f5f0e6 !important;
        color: #000000 !important;
        box-sizing: border-box;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        background: #007bff !important;
        color: #000000 !important;
        border: none !important;
        font-weight: 600 !important;
        margin: 0 !important;
        box-sizing: border-box !important;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .stButton > button:hover {
        background: #0056b3 !important;
    }
    .add-watchlist-btn {
        background: #007bff !important;
        color: #fff !important;
        border: none !important;
        border-radius: 0.5rem !important;
        height: 38px !important;
        font-size: 0.9rem !important;
        cursor: pointer !important;
        transition: background 0.2s !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 1rem !important;
        white-space: nowrap !important;
    }
    .add-watchlist-btn:hover {
        background: #0056b3 !important;
    }
    .custom-multiselect {
        position: relative !important;
        z-index: 1000 !important;
    }
    .custom-multiselect .stMultiSelect, .custom-multiselect .stMultiSelect div[data-baseweb="select"] {
        background-color: #f5f0e6 !important;
        color: #000 !important;
        border: 1.5px solid #007bff !important;
        border-radius: 0.5rem !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        padding: 0.5rem 1rem !important;
        min-height: 2.2rem !important;
    }
    .custom-multiselect [data-baseweb="popover"] {
        background-color: #f5f0e6 !important;
        border: 1.5px solid #007bff !important;
        border-radius: 0.5rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        margin-top: 0.5rem !important;
    }
    .add-watchlist-label, h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 900 !important;
        letter-spacing: 0.01em !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .stTextInput label, .stSelectbox label, .stMultiSelect label, .stRadio label, .stCheckbox label, .stRadio > div > label, .stRadio > label, .stRadio span, .stRadio div {
        color: #000000 !important;
    }
    .stExpander, .stInfo, .stWarning, .stError {
        width: 100%;
        border-radius: 0.5rem;
        border: 1px solid #ddd;
        background: #f5f0e6 !important;
        color: #000000 !important;
        margin: 0 0 1rem 0;
        padding: 0 1rem;
        box-sizing: border-box;
    }
    ::placeholder {
        color: #000000 !important;
        opacity: 1 !important;
    }
    @media (max-width: 600px) {
        .main-content-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .news-article {
            padding: 1rem 0;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Remove columns for watchlist news, use full-width tabs and containers
# (No code change needed if you use st.tabs and display_news as before, but ensure no st.columns is wrapping the news)

# Remove columns, use a single main container
st.markdown("""
    <div class="nuntius-header">
        <span class="nuntius-title">NUNTIUS</span>
    </div>
    <div style='height:6.5rem;'></div>
""", unsafe_allow_html=True)

option = st.radio("Choose input method:", ["Single Ticker", "Watchlist Manager"])
if option == "Single Ticker":
    ticker_col, plus_col = st.columns([8,1])
    with ticker_col:
        ticker = st.text_input("Enter stock ticker (e.g., AAPL)", "", key="single_ticker_input").upper()
    with plus_col:
        st.markdown("""
        <style>
        .stButton > button {
            background-color: #007bff !important;
            color: #fff !important;
            border: none !important;
            border-radius: 0.5rem !important;
            height: 38px !important;
            font-size: 0.9rem !important;
            cursor: pointer !important;
            transition: background 0.2s !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            margin: 0 !important;
            padding: 0 1rem !important;
            white-space: nowrap !important;
        }
        .stButton > button:hover {
            background-color: #0056b3 !important;
        }
        .custom-multiselect {
            position: relative !important;
            z-index: 1000 !important;
        }
        .custom-multiselect .stMultiSelect, .custom-multiselect .stMultiSelect div[data-baseweb="select"] {
            background-color: #f5f0e6 !important;
            color: #000 !important;
            border: 1.5px solid #007bff !important;
            border-radius: 0.5rem !important;
            font-size: 1rem !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            padding: 0.5rem 1rem !important;
            min-height: 2.2rem !important;
        }
        .custom-multiselect [data-baseweb="popover"] {
            background-color: #f5f0e6 !important;
            border: 1.5px solid #007bff !important;
            border-radius: 0.5rem !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            margin-top: 0.5rem !important;
        }
        </style>
        """, unsafe_allow_html=True)
        show_add = st.button("Add to watchlist", key="show_add_to_watchlist", help="Add to watchlist", use_container_width=True)
    # Only show the add-to-watchlist multiselect if + is clicked and there are watchlists
    if show_add and st.session_state.watchlists:
        st.markdown('<div class="custom-multiselect">', unsafe_allow_html=True)
        selected_watchlists = st.multiselect(
            "",
            options=list(st.session_state.watchlists.keys()),
            key="add_to_watchlists_multiselect",
            label_visibility="collapsed"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("Add Ticker to Selected Watchlists", key="add_ticker_confirm"):
            added_to = []
            for wl in selected_watchlists:
                if ticker and ticker not in st.session_state.watchlists[wl]:
                    st.session_state.watchlists[wl].append(ticker)
                    added_to.append(wl)
            if added_to:
                save_watchlists(st.session_state.watchlists)
                st.success(f"Added {ticker} to: {', '.join(added_to)}")
    if ticker:
        tab1, tab2 = st.tabs(["News", "Calendar"])
        with tab1:
            st.markdown('<div class="sort-row">', unsafe_allow_html=True)
            col_sort, col_size = st.columns([1,1])
            with col_sort:
                order = st.radio(
                    "",
                    ["Newest First", "Oldest First"],
                    key="sort_order",
                    horizontal=True,
                    label_visibility="collapsed"
                )
            with col_size:
                page_size = st.number_input("Results per page", min_value=1, max_value=50, value=st.session_state.get('page_size', 10), step=1, key="page_size")
            st.markdown('</div>', unsafe_allow_html=True)
            # --- Fetch and process news ---
            if st.button("Get News", key="single_ticker"):
                news = fetch_news(ticker)
                def parse_date(article):
                    try:
                        return pd.to_datetime(article.get('published_at', ''), errors='coerce')
                    except Exception:
                        return pd.NaT
                news = sorted(news, key=parse_date, reverse=(order == "Newest First"))
                page = st.session_state.get('page_num', 1)
                total_results = len(news)
                total_pages = (total_results + page_size - 1) // page_size
                start_idx = (page-1)*page_size
                end_idx = start_idx + page_size
                paged_news = news[start_idx:end_idx]
                display_news(ticker, paged_news)
                # --- Page numbers at the bottom ---
                st.markdown("<div style='display: flex; justify-content: center; gap: 0.5rem; margin-top: 2rem;'>", unsafe_allow_html=True)
                page_buttons = []
                for i in range(1, total_pages+1):
                    if i == page:
                        page_buttons.append(f"<button style='background:#007bff;color:#fff;border:none;border-radius:6px;padding:0.5rem 1rem;font-weight:bold;cursor:default;'>{i}</button>")
                    else:
                        page_buttons.append(f"<form style='display:inline;' action='' method='post'><button name='page_btn' value='{i}' style='background:#e0e0e0;color:#000;border:none;border-radius:6px;padding:0.5rem 1rem;cursor:pointer;'>{i}</button></form>")
                st.markdown(''.join(page_buttons), unsafe_allow_html=True)
                # Handle page button clicks
                if 'page_btn' in st.session_state:
                    st.session_state.page_num = int(st.session_state.page_btn)
                    st.experimental_rerun()
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; margin-top: 0.5rem;'><b>Page {page} of {total_pages} | {total_results} results</b></div>", unsafe_allow_html=True)
        with tab2:
            if st.button("Show Calendar", key="single_calendar"):
                events = fetch_calendar_events(ticker)
                display_calendar(ticker, events)
elif option == "Watchlist Manager":
    st.subheader("Manage Watchlists")
    with st.expander("Create New Watchlist"):
        new_list_name = st.text_input("Watchlist Name")
        new_tickers = st.text_input("Enter comma-separated tickers (e.g., MSFT,NVDA,TSLA)")
        if st.button("Create Watchlist") and new_list_name and new_tickers:
            ticker_list = [t.strip().upper() for t in new_tickers.split(",")]
            st.session_state.watchlists[new_list_name] = ticker_list
            save_watchlists(st.session_state.watchlists)
            st.success(f"Watchlist '{new_list_name}' created!")
    if st.session_state.watchlists:
        selected_list = st.selectbox(
            "Select Watchlist",
            options=list(st.session_state.watchlists.keys())
        )
        if selected_list:
            current_tickers = st.session_state.watchlists[selected_list]
            edited_tickers = st.multiselect("Edit Tickers", options=current_tickers, default=current_tickers, key="edit_multiselect")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Update", key="update_btn"):
                    st.session_state.watchlists[selected_list] = edited_tickers
                    save_watchlists(st.session_state.watchlists)
                    st.success("Watchlist updated!")
            with col2:
                if st.button("Delete Watchlist", key="delete_btn"):
                    del st.session_state.watchlists[selected_list]
                    save_watchlists(st.session_state.watchlists)
                    st.success(f"Watchlist '{selected_list}' deleted!")
                    st.rerun()
            with col3:
                if st.button("Get News", key="watchlist_news"):
                    if selected_list and selected_list in st.session_state.watchlists:
                        news_results = process_watchlist_tickers(st.session_state.watchlists[selected_list])
                        if news_results:
                            tabs = st.tabs(list(news_results.keys()))
                            for i, ticker in enumerate(news_results):
                                with tabs[i]:
                                    st.header(f"News for {ticker}")
                                    display_news(ticker, news_results[ticker])
                    else:
                        st.warning("Please select a valid watchlist.")
            with col4:
                if st.button("Show Calendar", key="show_calendar_btn"):
                    if selected_list and selected_list in st.session_state.watchlists:
                        process_watchlist_tickers(st.session_state.watchlists[selected_list], "calendar")
                    else:
                        st.warning("Please select a valid watchlist.")
    else:
        st.info("No watchlists created yet. Create your first watchlist above!")

# Wrap all main content in a centered container
def main_content():
    st.markdown('<div class="main-content-container">', unsafe_allow_html=True)
    # ... all main content code (UI, forms, news, etc.) ...
    # This includes everything that was previously in the main body
    # Place the rest of your Streamlit code here
    # ...
    if "add_success" in st.session_state:
        st.success(st.session_state["add_success"])
        # Optionally, clear the message after showing it once:
        # del st.session_state["add_success"]
    st.markdown('</div>', unsafe_allow_html=True)

# Replace the main body code with a call to main_content()
main_content() 