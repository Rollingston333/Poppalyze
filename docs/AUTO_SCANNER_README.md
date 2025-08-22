# Automatic Background Scanner Integration

## Overview

The Gap Screener Dashboard now automatically starts the background scanner when the Flask app is launched. This eliminates the need to manually start two separate processes.

## New Features

### 🚀 Automatic Startup
- When you run `python app.py`, the background scanner starts automatically
- No need to manually run `python background_scanner.py`
- Both processes are managed together

### 🔧 Manual Control
The app provides API endpoints for manual scanner control:

#### Start Scanner
```bash
curl -X POST http://localhost:5001/api/scanner/start
```

#### Stop Scanner
```bash
curl -X POST http://localhost:5001/api/scanner/stop
```

#### Check Scanner Status
```bash
curl http://localhost:5001/api/scanner/status
```

#### Enhanced Health Check
```bash
curl http://localhost:5001/health
```
Now includes scanner status in the response.

## Usage

### Simple Startup
```bash
# Just run the app - scanner starts automatically
python app.py
```

### Using the Startup Script
```bash
# Use the provided startup script
python start_app.py
```

### Manual Control via API
```bash
# Check if scanner is running
curl http://localhost:5001/api/scanner/status

# Stop the scanner
curl -X POST http://localhost:5001/api/scanner/stop

# Start the scanner again
curl -X POST http://localhost:5001/api/scanner/start
```

## Process Management

### Automatic Cleanup
- When you stop the Flask app (Ctrl+C), the background scanner is automatically stopped
- Signal handlers ensure clean shutdown of both processes

### Process Monitoring
- The app monitors the background scanner process
- If the scanner crashes, you can restart it via the API
- Health endpoint shows scanner status

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with scanner status |
| `/api/scanner/status` | GET | Get scanner running status and PID |
| `/api/scanner/start` | POST | Manually start background scanner |
| `/api/scanner/stop` | POST | Manually stop background scanner |

## Response Examples

### Health Check Response
```json
{
  "status": "healthy",
  "cache_status": "Fresh",
  "cache_age_minutes": 2.5,
  "scanner_status": "running",
  "timestamp": "2025-07-27T00:45:36.473291"
}
```

### Scanner Status Response
```json
{
  "running": true,
  "pid": 29061
}
```

## Benefits

1. **Simplified Deployment**: One command starts everything
2. **Automatic Management**: No need to remember to start the scanner
3. **Clean Shutdown**: Both processes stop together
4. **Manual Control**: API endpoints for fine-grained control
5. **Status Monitoring**: Easy to check if scanner is running

## Troubleshooting

### Scanner Won't Start
- Check if `background_scanner.py` exists in the same directory
- Verify Python environment and dependencies
- Check console output for error messages

### Multiple Scanner Processes
- Use `pkill -f "background_scanner.py"` to clean up
- Restart the app with `python app.py`

### Manual Restart
If the automatic startup fails:
```bash
# Stop the app
pkill -f "app.py"

# Start manually
python background_scanner.py &
python app.py
``` 