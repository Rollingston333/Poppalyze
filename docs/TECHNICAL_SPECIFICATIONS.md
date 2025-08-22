# Technical Specifications - Gap Screener Dashboard

## 🔧 System Requirements

### Minimum Requirements
- **OS**: macOS 10.15+, Ubuntu 18.04+, Windows 10+
- **Python**: 3.9 or higher
- **RAM**: 512MB available memory
- **Storage**: 100MB free disk space
- **Network**: Stable internet connection (500Kbps+)

### Recommended Requirements
- **OS**: macOS 12+, Ubuntu 20.04+
- **Python**: 3.11+
- **RAM**: 2GB available memory
- **Storage**: 1GB free disk space
- **Network**: Broadband connection (5Mbps+)

## 📡 API Specifications

### REST Endpoints

#### 1. Main Dashboard
```http
GET /
Content-Type: text/html
```
**Query Parameters:**
- `min_price` (float): Minimum stock price (default: 1.0)
- `max_price` (float): Maximum stock price (default: 20.0)
- `min_rel_vol` (float): Minimum relative volume (default: 5.0)
- `max_float` (string): Maximum float shares (default: 50000000)
- `min_gap_pct` (float): Minimum gap percentage (default: 0.0)
- `require_news` (boolean): Filter for stocks with news (default: false)

**Response:** HTML page with filtered gap data

#### 2. Cache Status API
```http
GET /api/cache_status
Content-Type: application/json
```
**Response Example:**
```json
{
  "cache_status": {
    "status": "fresh",
    "message": "Data is fresh (2.3 minutes old)",
    "age_minutes": 2.3,
    "is_fresh": true,
    "last_update_str": "2025-01-08 14:30:15"
  },
  "successful_count": 15,
  "total_count": 15,
  "last_update": "2025-01-08 14:30:15",
  "stocks_available": 15
}
```

#### 3. Health Check
```http
GET /health
Content-Type: application/json
```
**Response Example:**
```json
{
  "status": "healthy",
  "cache_status": "fresh",
  "cache_age_minutes": 2.3,
  "timestamp": "2025-01-08T14:32:45.123456"
}
```

## 🗄️ Data Schema

### Cache File Structure (`stock_cache.json`)
```json
{
  "stocks": {
    "SYMBOL": {
      "symbol": "string",
      "price": "number",
      "pct_change": "number",
      "gap_pct": "number",
      "rel_vol": "number",
      "volume": "integer",
      "float_shares_raw": "integer",
      "float": "string",
      "market_cap": "string",
      "pe": "number|string",
      "has_news": "boolean",
      "source": "string",
      "timestamp": "number"
    }
  },
  "last_update": "number (unix_timestamp)",
  "last_update_str": "string (ISO_format)",
  "successful_count": "integer",
  "total_count": "integer",
  "scan_type": "string"
}
```

### Stock Data Fields
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `symbol` | string | Stock ticker symbol | "AAPL" |
| `price` | number | Current stock price | 150.25 |
| `pct_change` | number | Percentage change from previous close | 5.47 |
| `gap_pct` | number | Gap percentage (current vs previous close) | 5.47 |
| `rel_vol` | number | Relative volume (current/average) | 2.34 |
| `volume` | integer | Current day volume | 25847293 |
| `float_shares_raw` | integer | Shares outstanding (raw number) | 15204400000 |
| `float` | string | Formatted shares outstanding | "15.2B" |
| `market_cap` | string | Market capitalization | "$2.3T" |
| `pe` | number/string | Price-to-earnings ratio | 25.4 or "—" |
| `has_news` | boolean | Recent news indicator | true/false |
| `source` | string | Data source identifier | "yahoo_screener" |
| `timestamp` | number | Unix timestamp of data fetch | 1704722415.123 |

## 🔄 Process Architecture

### Background Scanner Process
```python
# Process Flow
1. Initialize Yahoo Finance screener
2. Fetch day_gainers (positive gappers)
3. Fetch day_losers (negative gappers)
4. Calculate gap percentages
5. Sort and select top movers
6. Update cache file atomically
7. Sleep for UPDATE_INTERVAL
8. Repeat from step 2
```

### Flask Application Process
```python
# Request Flow
1. Receive HTTP request
2. Load cache file
3. Parse query parameters
4. Apply filters to cached data
5. Calculate top positive gappers
6. Render template with data
7. Return HTML response
```

## 🔧 Configuration Parameters

### Background Scanner Configuration
```python
# background_scanner.py settings
CACHE_FILE = "stock_cache.json"
UPDATE_INTERVAL = 180  # seconds
MAX_POSITIVE_GAPPERS = 8
MAX_NEGATIVE_GAPPERS = 7
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5  # seconds
LOG_LEVEL = "INFO"
```

### Flask Application Configuration
```python
# app.py settings
HOST = "0.0.0.0"
PORT = 5001
DEBUG = True
CACHE_FRESH_THRESHOLD = 5 * 60  # 5 minutes
CACHE_STALE_THRESHOLD = 15 * 60  # 15 minutes
```

### Filter Default Values
```python
# Default filter settings
DEFAULT_MIN_PRICE = 1.0
DEFAULT_MAX_PRICE = 20.0
DEFAULT_MIN_REL_VOL = 5.0
DEFAULT_MAX_FLOAT = 50_000_000
DEFAULT_MIN_GAP_PCT = 0.0
DEFAULT_REQUIRE_NEWS = False
```

## 🎯 Yahoo Finance Integration

### Screener Queries Used
1. **Day Gainers**: `yf.screen('day_gainers')`
   - Criteria: >3% gain, US region, >$2B market cap, >$5 price, >15K volume
   
2. **Day Losers**: `yf.screen('day_losers')`
   - Criteria: <-2.5% loss, US region, >$2B market cap, >$5 price, >20K volume

### Data Processing Pipeline
```python
# Gap Calculation Logic
def calculate_gap(current_price, previous_close):
    """
    Calculate gap percentage between current price and previous close
    """
    if previous_close and previous_close > 0:
        gap_pct = ((current_price - previous_close) / previous_close) * 100
        return round(gap_pct, 2)
    return 0.0
```

### Error Handling
- **Network Timeouts**: 30-second timeout with retry logic
- **API Rate Limits**: Exponential backoff (1s, 2s, 4s, 8s)
- **Data Validation**: Schema validation for all fetched data
- **Fallback Mechanisms**: Use cached data if fetch fails

## 🔒 Security Implementation

### Input Validation
```python
# Parameter sanitization
def validate_float_param(value, default, min_val=None, max_val=None):
    try:
        float_val = float(value) if value and value.strip() else default
        if min_val is not None and float_val < min_val:
            return default
        if max_val is not None and float_val > max_val:
            return default
        return float_val
    except (ValueError, TypeError):
        return default
```

### XSS Prevention
- All template variables properly escaped using Jinja2 auto-escaping
- User inputs validated and sanitized before processing
- No direct HTML insertion from user data

### File System Security
- Cache file written atomically to prevent corruption
- Proper file permissions (644) for cache file
- No direct file system access from web requests

## 📊 Performance Optimization

### Caching Strategy
```python
# Cache hit optimization
1. In-memory cache loading (JSON deserialization)
2. Single file read per request
3. No database queries during request handling
4. Pre-computed filter-ready data structure
```

### Memory Management
- Minimal memory footprint (~50MB typical)
- Garbage collection for old cache data
- Efficient JSON serialization/deserialization
- No memory leaks in background processes

### Response Time Targets
- **Cache Hit**: < 50ms response time
- **Filter Processing**: < 10ms additional time
- **Template Rendering**: < 25ms render time
- **Total Response**: < 100ms end-to-end

## 🔧 Error Codes & Handling

### HTTP Status Codes
- `200 OK`: Successful request with data
- `404 Not Found`: Invalid endpoint
- `500 Internal Server Error`: Application error

### Application Error Types
```python
class GapScreenerError(Exception):
    """Base exception for Gap Screener"""
    pass

class CacheError(GapScreenerError):
    """Cache-related errors"""
    pass

class DataFetchError(GapScreenerError):
    """Data fetching errors"""
    pass

class ValidationError(GapScreenerError):
    """Input validation errors"""
    pass
```

### Logging Levels
- **DEBUG**: Detailed execution flow
- **INFO**: Normal operations and updates
- **WARNING**: Non-critical issues
- **ERROR**: Application errors requiring attention
- **CRITICAL**: System failures

## 🔄 Deployment Specifications

### Production Deployment
```bash
# Recommended production setup
1. Use gunicorn WSGI server instead of Flask dev server
2. Set up nginx reverse proxy
3. Configure systemd services for auto-restart
4. Implement log rotation
5. Set up monitoring and alerting
```

### Environment Variables
```bash
# Optional environment configuration
export FLASK_ENV=production
export FLASK_DEBUG=0
export GAP_SCREENER_PORT=5001
export GAP_SCREENER_HOST=0.0.0.0
export GAP_SCREENER_UPDATE_INTERVAL=180
```

### Service Configuration
```ini
# systemd service example (gap-screener.service)
[Unit]
Description=Gap Screener Dashboard
After=network.target

[Service]
Type=simple
User=screener
WorkingDirectory=/opt/gap-screener
ExecStart=/opt/gap-screener/start_screener.sh start
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## 📈 Monitoring & Metrics

### Key Performance Indicators
- **Data Freshness**: Age of cached data
- **Update Success Rate**: Percentage of successful cache updates
- **Response Time**: Average HTTP response time
- **Error Rate**: Application error frequency
- **Uptime**: Service availability percentage

### Health Check Implementation
```python
def health_check():
    checks = {
        'cache_file_exists': os.path.exists(CACHE_FILE),
        'cache_file_readable': check_cache_readable(),
        'cache_data_fresh': check_cache_freshness(),
        'background_process_running': check_scanner_process()
    }
    return all(checks.values()), checks
```

### Alerting Thresholds
- **Cache Age > 15 minutes**: Warning alert
- **Cache Age > 30 minutes**: Critical alert
- **Update Failures > 3 consecutive**: Critical alert
- **Response Time > 500ms**: Warning alert
- **Error Rate > 5%**: Critical alert

## 🧪 Testing Specifications

### Unit Testing
```python
# Test coverage areas
- Filter parameter validation
- Cache loading and parsing
- Gap calculation logic
- Template rendering
- Error handling paths
```

### Integration Testing
```python
# Integration test scenarios
- End-to-end request processing
- Cache update and reload cycle
- Background scanner integration
- Error recovery mechanisms
```

### Performance Testing
- Load testing with 100 concurrent users
- Cache performance under heavy load
- Memory usage profiling
- Response time validation

## 🔄 Backup & Recovery

### Data Backup Strategy
- **Cache File**: Automatic backup before each update
- **Logs**: Rotated and archived daily
- **Configuration**: Version controlled
- **Recovery Time**: < 5 minutes for full restoration

### Disaster Recovery
1. **Cache Corruption**: Automatic regeneration from Yahoo Finance
2. **Process Failure**: Automatic restart via systemd/supervisor
3. **Data Loss**: Restore from backup and regenerate cache
4. **System Failure**: Deploy to backup server with synchronized data

---

**Document Version**: 2.0  
**Last Updated**: January 2025  
**API Version**: v1  
**Schema Version**: 2.0 