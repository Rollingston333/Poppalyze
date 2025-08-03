import json
import requests
import streamlit as st

def load_watchlists():
    try:
        with open('watchlists.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def fetch_news_from_source(url):
    try:
        st.write(f"Fetching from: {url}")
        response = requests.get(url, timeout=10)
        st.write(f"Status code: {response.status_code}")
        st.write(f"Raw response: {response.text[:500]}")  # Limit output

        # Check for HTTP errors
        response.raise_for_status()

        try:
            data = response.json()
        except Exception as json_err:
            st.error(f"Response is not valid JSON: {json_err}")
            return []

        if not data or 'articles' not in data or not data['articles']:
            st.warning("No articles returned.")
            return []

        return data.get('articles', [])
    except requests.exceptions.RequestException as req_err:
        st.error(f"Request error: {req_err}")
        return []
    except Exception as e:
        st.error(f"Error fetching from {url}: {e}")
        return [] 