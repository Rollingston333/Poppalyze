# 🚀 Poppalyze Stock Screener

**Catch the pop. Own the trade.**

A real-time stock screener that identifies high-potential stocks with gap-ups, volume spikes, and momentum indicators.

## ✨ Features

- **Real-time Stock Scanning** - Live data from Yahoo Finance
- **Advanced Filtering** - Price, volume, gap percentage, market cap, and more
- **Auto-refresh** - Background scanner updates every 5 minutes
- **Responsive Design** - Works on desktop and mobile
- **Analytics Dashboard** - Track usage and performance

## 🛠️ Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Poppalyze-Stock-Screener
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

4. **Open in browser**
   ```
   http://localhost:5001
   ```

### Production Deployment

The app is configured for deployment on:
- **Render** - Use `render.yaml` configuration
- **Heroku** - Use `Procfile` configuration
- **Railway** - Use `railway.json` configuration

## 📊 Stock Data

The screener tracks 159+ stocks including:
- **Meme Stocks** - GME, AMC, BBBY, etc.
- **Tech Giants** - AAPL, GOOGL, TSLA, etc.
- **Growth Stocks** - NVDA, AMD, META, etc.
- **Penny Stocks** - High-volume low-price stocks

## 🔧 Configuration

Key configuration files:
- `config.py` - App settings and constants
- `cache_manager.py` - Data caching system
- `background_scanner.py` - Stock scanning engine

## 📈 API Endpoints

- `GET /` - Main screener interface
- `GET /api/cache_status` - Cache status and health
- `GET /health` - Application health check
- `GET /api/geolocation/stats` - Analytics data

## 🚀 Deployment Status

- ✅ **Local Development** - Working
- ✅ **Render Deployment** - Configured
- ✅ **Background Scanner** - Active
- ✅ **Auto-refresh** - Enabled

## 📝 License

MIT License - See LICENSE file for details.

---

**Built with ❤️ for traders who want to catch the next big move.** 