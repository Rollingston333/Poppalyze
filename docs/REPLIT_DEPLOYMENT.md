# Stock Gap Screener - Replit Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the Stock Gap Screener on Replit using Streamlit.

## 📋 Prerequisites

1. A Replit account (free at [replit.com](https://replit.com))
2. Basic knowledge of Python

## 🛠️ Setup Instructions

### Step 1: Create a New Replit

1. Go to [replit.com](https://replit.com) and sign in
2. Click "Create Repl"
3. Choose "Python" as the template
4. Give your project a name (e.g., "Stock Gap Screener")
5. Click "Create Repl"

### Step 2: Upload Files

1. **Upload `streamlit_app.py`** as your main file
2. **Upload `requirements_streamlit.txt`** and rename it to `requirements.txt`
3. **Upload `stock_cache.json`** (optional - for initial data)

### Step 3: Configure Replit

1. In the Replit shell, run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Important**: Set the run command in Replit:
   - Click on the "Tools" button in the left sidebar
   - Go to "Secrets" 
   - Add a new secret with key `REPL_SLUG` and value `your-repl-name`

### Step 4: Run the App

1. In the Replit shell, run:
   ```bash
   streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   ```

2. Or use the "Run" button and set the command to:
   ```
   streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
   ```

## 🔧 Configuration

### Customizing Stock Symbols

Edit the `DEFAULT_SYMBOLS` list in `streamlit_app.py` to include the stocks you want to monitor:

```python
DEFAULT_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC',
    # Add your preferred stocks here
]
```

### Adjusting Refresh Intervals

The app includes rate limiting to avoid hitting API limits. You can adjust the sleep time in the `scan_stocks` method:

```python
time.sleep(0.1)  # Rate limiting - adjust as needed
```

## 📊 Features

### Real-time Stock Data
- Fetches live data from Yahoo Finance
- Calculates gap percentages
- Shows relative volume and market cap

### Interactive Filters
- Gap percentage range
- Price range
- Relative volume threshold
- Sector filtering

### Visual Dashboard
- Color-coded gap percentages (green for positive, red for negative)
- Top gappers display
- Real-time metrics

## 🚨 Important Notes

### Rate Limiting
- Yahoo Finance has rate limits
- The app includes built-in delays to avoid hitting limits
- Don't refresh too frequently

### Data Accuracy
- Data is sourced from Yahoo Finance
- May have delays during market hours
- Pre-market and after-hours data availability varies

### Replit Limitations
- Free tier has usage limits
- App may sleep after inactivity
- Consider upgrading for production use

## 🔍 Troubleshooting

### Common Issues

1. **"No module named 'streamlit'"**
   - Run: `pip install -r requirements.txt`

2. **Port already in use**
   - Change the port in the run command: `--server.port 8502`

3. **Data not loading**
   - Check internet connection
   - Verify stock symbols are valid
   - Try refreshing manually

4. **App not starting**
   - Check the run command is correct
   - Ensure all files are uploaded
   - Check the Replit console for errors

### Performance Tips

1. **Reduce stock list size** for faster loading
2. **Increase sleep time** between API calls if hitting rate limits
3. **Use cache** - the app automatically caches data
4. **Limit concurrent users** on free tier

## 📈 Advanced Usage

### Adding Custom Indicators

You can extend the app by adding custom technical indicators:

```python
def calculate_rsi(prices, period=14):
    # Add RSI calculation
    pass

def calculate_macd(prices):
    # Add MACD calculation
    pass
```

### Custom Alerts

Add notification features:

```python
def send_alert(symbol, gap_pct):
    # Add email/SMS alerts
    pass
```

### Data Export

Add export functionality:

```python
def export_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
```

## 🆘 Support

If you encounter issues:

1. Check the Replit console for error messages
2. Verify all dependencies are installed
3. Test with a smaller stock list first
4. Check Yahoo Finance API status

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🔄 Updates

The app will automatically:
- Cache data to reduce API calls
- Handle rate limiting
- Provide real-time updates when refreshed

---

**Happy Trading! 📈** 