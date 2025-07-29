# 📈 Poppalyze

**Catch the pop. Own the trade.**

Real-time stock gap analysis and market movers platform built with Flask and Python.

## 🚀 Features

- **Real-time Stock Scanning** - Continuous background scanning of 25+ stocks
- **Gap Analysis** - Identify stocks with significant price gaps
- **Market Movers** - Track stocks with high relative volume
- **Advanced Filtering** - Filter by price, gap percentage, volume, sector
- **Live Updates** - Background scanner updates data every 5 minutes
- **Modern UI** - Clean, responsive interface with Poppins font
- **Traffic Analytics** - Built-in visitor tracking and analytics

## 🛠️ Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Data**: yfinance API
- **Database**: SQLite (traffic analytics)
- **Deployment**: Render (production-ready)

## 📊 Stock Categories

### Low-Priced Stocks ($1-20)
- SNDL, PLUG, NIO, XPEV, LI, WKHS, LYFT, SNAP

### Mid-Priced Stocks ($20-100)
- AMD, INTC, UBER, PINS, ROKU, ZM, CRWD

### High-Priced Stocks ($100+)
- AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN, META, NFLX, SPY, QQQ

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd poppalyze
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**
   ```bash
   python3 app_production.py
   ```

4. **Open in browser**
   ```
   http://localhost:5001
   ```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions to Render.

## 📁 Project Structure

```
poppalyze/
├── app_production.py      # Main Flask application
├── cache_manager.py       # Cache management utilities
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── render.yaml           # Render service configuration
├── templates/
│   └── screener.html     # Main UI template
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
└── DEPLOYMENT.md         # Deployment guide
```

## 🔧 Configuration

### Environment Variables

- `PORT` - Server port (default: 5001)
- `SCAN_INTERVAL` - Background scan interval in seconds (default: 300)

### Cache Management

The app uses a JSON-based cache system:
- **Cache File**: `stock_cache.json`
- **Update Interval**: Every 5 minutes
- **Data Persistence**: Survives app restarts

## 📈 API Endpoints

- `GET /` - Main screener page
- `GET /api/cache_status` - Cache status information
- `GET /health` - Health check endpoint

## 🎯 Usage

1. **View All Stocks** - See all scanned stocks in the main table
2. **Apply Filters** - Use the filter panel to narrow down results
3. **Quick Movers** - View stocks with high relative volume
4. **Top Gappers** - View stocks with the biggest positive gaps
5. **Independent Filters** - Toggle whether filters apply to quick movers/gappers

## 🔍 Filter Options

- **Price Range**: Min/max stock price
- **Gap Percentage**: Minimum gap percentage
- **Relative Volume**: Minimum relative volume
- **Sector**: Filter by stock sector
- **Market Cap**: Min/max market capitalization

## 📊 Analytics

Built-in traffic analytics track:
- **Visitors**: Unique session tracking
- **Page Views**: Page visit analytics
- **API Calls**: Endpoint usage statistics

## 🚀 Deployment

### Render (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Deploy with one click
4. Get HTTPS URL automatically

### Other Platforms

- **Heroku**: Use `Procfile` and `requirements.txt`
- **Railway**: Direct GitHub integration
- **DigitalOcean**: App Platform deployment

## 🔧 Development

### Adding New Stocks

Edit the `symbols` list in `app_production.py`:

```python
symbols = [
    'NEW_STOCK',  # Add your stock here
    # ... existing stocks
]
```

### Customizing Scan Interval

Modify the `SCAN_INTERVAL` constant:

```python
SCAN_INTERVAL = 300  # 5 minutes
```

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Check the [deployment guide](DEPLOYMENT.md)
- Review the logs in your hosting platform
- Open an issue on GitHub

---

**Poppalyze** - Catch the pop. Own the trade. 📈 