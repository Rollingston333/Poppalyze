# Poppalyze - Simplified Version

**Catch the pop. Own the trade.**

A streamlined stock screener that identifies gap opportunities with real-time data and intelligent filtering.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements_simplified.txt

# Start the app
python start_simplified.py
```

### Production Deployment
```bash
# Deploy to Render
# 1. Connect your GitHub repository
# 2. Use render_simplified.yaml for configuration
# 3. Deploy automatically
```

## ✨ Features

- **Real-time Stock Data**: Live price and gap information
- **Smart Filtering**: Filter by price, gap percentage, volume, and sector
- **Top Movers**: Quick access to highest gap movers and volume leaders
- **Background Scanning**: Automatic data updates every 5 minutes
- **Responsive UI**: Modern, mobile-friendly interface
- **Production Ready**: Optimized for cloud deployment

## 🏗️ Architecture

### Simplified Structure
```
app_simplified.py          # Main Flask application
start_simplified.py        # Startup script
requirements_simplified.txt # Dependencies
render_simplified.yaml     # Deployment config
templates/screener.html    # UI template
static/                    # CSS/JS assets
```

### Key Components

1. **StockScanner Class**: Handles all stock data operations
   - Background scanning thread
   - Cache management
   - Data formatting

2. **Filter Functions**: Clean, efficient filtering logic
   - Price range filtering
   - Gap percentage filtering
   - Volume and sector filtering

3. **Flask Routes**: Simple, focused endpoints
   - Main screener page
   - Cache status API
   - Health check

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Add to .env file
FLASK_ENV=production
PORT=5001
```

### Cache Settings
- **Scan Interval**: 5 minutes (configurable)
- **Cache File**: `stock_cache.json`
- **Stocks Scanned**: 30+ high-volume stocks

## 📊 Data Sources

- **yfinance**: Real-time stock data
- **Stocks Covered**: AAPL, MSFT, GOOGL, TSLA, NVDA, and more
- **Data Points**: Price, gap %, volume, market cap, sector

## 🚀 Deployment

### Render (Recommended)
1. Fork this repository
2. Connect to Render
3. Use `render_simplified.yaml` for configuration
4. Deploy automatically

### Other Platforms
- **Heroku**: Use `Procfile` with `gunicorn app_simplified:app`
- **Railway**: Direct deployment from GitHub
- **VPS**: Run with `python start_simplified.py`

## 🔍 Usage

1. **View All Stocks**: See all scanned stocks with current data
2. **Apply Filters**: Use price, gap, volume, and sector filters
3. **Quick Movers**: Toggle between all stocks and filtered results
4. **Top Gappers**: View highest percentage movers
5. **Positive Gappers**: Focus on upward movers only

## 🛠️ Development

### Adding New Stocks
Edit the `stocks` list in `app_simplified.py`:
```python
stocks = [
    'AAPL', 'MSFT', 'GOOGL',  # Add your symbols here
    # ... existing stocks
]
```

### Modifying Scan Interval
Change `SCAN_INTERVAL` in `app_simplified.py`:
```python
SCAN_INTERVAL = 300  # 5 minutes (in seconds)
```

### Custom Filters
Add new filter logic in the `filter_stocks` function:
```python
def filter_stocks(stocks_data, **filters):
    # Add your custom filter logic here
    pass
```

## 📈 Performance

- **Startup Time**: ~5 seconds
- **Memory Usage**: ~50MB
- **Response Time**: <100ms for cached data
- **Scan Duration**: ~5-10 seconds for 30 stocks

## 🔒 Security

- No sensitive data stored
- Rate limiting on API calls
- Input validation on filters
- Error handling throughout

## 📝 Logging

- Console logging for development
- Structured log format
- Error tracking and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Issues**: GitHub Issues
- **Documentation**: This README
- **Deployment**: Render documentation

---

**Poppalyze** - Simplified, powerful, production-ready stock screening. 