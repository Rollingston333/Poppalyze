# Multiple Background Scanner Prevention Solution

## Problem
Multiple background scanner processes were running simultaneously, causing:
- **Rate limiting conflicts** - Yahoo Finance blocking requests due to too many concurrent API calls
- **Cache corruption** - Multiple processes writing to the same cache file
- **Resource waste** - Unnecessary CPU and memory usage
- **Inconsistent data** - Different processes scanning different stocks

## Solution Implemented

### 1. PID File-Based Singleton Pattern

**Background Scanner (`background_scanner.py`):**
- Creates a PID file (`background_scanner.pid`) on startup
- Checks for existing PID file before starting
- Validates that the PID in the file corresponds to a running process
- Cleans up stale PID files automatically
- Removes PID file on graceful shutdown

**Key Functions:**
```python
def check_existing_instance():
    """Check if another instance is already running"""
    
def create_pid_file():
    """Create PID file to prevent multiple instances"""
    
def remove_pid_file():
    """Remove PID file on shutdown"""
```

### 2. Enhanced Process Management

**Flask App (`app.py`):**
- Detects existing processes using both managed process and PID file
- Cleans up stale processes on startup
- Provides comprehensive status reporting
- Handles graceful shutdown of both app and scanner

**Key Functions:**
```python
def is_scanner_running():
    """Check if background scanner is already running using PID file"""
    
def cleanup_stale_scanners():
    """Kill any existing background scanner processes"""
    
def start_background_scanner():
    """Start the background scanner process with singleton protection"""
```

### 3. API Endpoints for Control

**Enhanced Status Endpoints:**
- `GET /api/scanner/status` - Detailed scanner status
- `POST /api/scanner/start` - Start scanner (with protection)
- `POST /api/scanner/stop` - Stop scanner (with cleanup)
- `GET /health` - Enhanced health check with scanner status

**Status Response Example:**
```json
{
    "running": true,
    "managed_process": true,
    "pid_file_detected": true,
    "pid": 41664
}
```

## How It Works

### Startup Process
1. **Background Scanner Starts:**
   - Checks for existing PID file
   - If found, validates process is running
   - If stale, removes PID file
   - Creates new PID file with current PID
   - Begins scanning

2. **Flask App Starts:**
   - Cleans up any existing background scanner processes
   - Removes stale PID files
   - Starts new background scanner with protection
   - Monitors both managed process and PID file

### Conflict Prevention
- **PID File Lock:** Only one process can create the PID file
- **Process Validation:** Ensures PID file corresponds to actual running process
- **Stale Cleanup:** Automatically removes orphaned PID files
- **Graceful Shutdown:** Proper cleanup on Ctrl+C or termination

### Status Monitoring
- **Dual Detection:** Checks both managed process and PID file
- **Comprehensive Reporting:** Shows all relevant status information
- **Real-time Updates:** Status reflects current state accurately

## Usage

### Starting the Application
```bash
# Start Flask app (automatically starts background scanner)
python app.py

# Or start background scanner manually
python background_scanner.py
```

### API Control
```bash
# Check scanner status
curl http://localhost:5001/api/scanner/status

# Start scanner
curl -X POST http://localhost:5001/api/scanner/start

# Stop scanner
curl -X POST http://localhost:5001/api/scanner/stop

# Health check
curl http://localhost:5001/health
```

### Cleanup Script
```bash
# Clean up all processes and PID files
python cleanup_scanners.py
```

## Benefits

### ✅ **Eliminates Conflicts**
- Only one background scanner process runs at a time
- No more rate limiting from multiple API calls
- Consistent cache data

### ✅ **Improved Reliability**
- Automatic cleanup of stale processes
- Graceful shutdown handling
- Process validation

### ✅ **Better Monitoring**
- Detailed status reporting
- Real-time process tracking
- Enhanced health checks

### ✅ **Easy Management**
- Simple API endpoints for control
- Automatic startup with protection
- Comprehensive cleanup tools

## Testing

### Test Single Instance
```bash
# Start background scanner
python background_scanner.py

# Try to start second instance (should be blocked)
python background_scanner.py
# Output: "❌ Another background scanner is already running. Exiting."
```

### Test Flask Integration
```bash
# Start Flask app
python app.py

# Check status
curl http://localhost:5001/api/scanner/status

# Try to start second scanner (should be blocked)
curl -X POST http://localhost:5001/api/scanner/start
```

### Test Cleanup
```bash
# Clean up all processes
python cleanup_scanners.py

# Verify no processes running
ps aux | grep background_scanner.py
```

## Troubleshooting

### If Multiple Processes Still Running
```bash
# Force kill all background scanner processes
pkill -9 -f "background_scanner.py"

# Remove PID file
rm -f background_scanner.pid

# Restart application
python app.py
```

### If PID File Stuck
```bash
# Remove PID file manually
rm -f background_scanner.pid

# Restart application
python app.py
```

### If Scanner Won't Start
```bash
# Check for existing processes
ps aux | grep background_scanner.py

# Clean up and restart
python cleanup_scanners.py
python app.py
```

## Implementation Files

- `app.py` - Enhanced Flask app with process management
- `background_scanner.py` - Background scanner with PID file protection
- `cleanup_scanners.py` - Cleanup utility script
- `MULTIPLE_SCANNER_SOLUTION.md` - This documentation

## Future Enhancements

- **Process Monitoring Dashboard** - Web interface for process management
- **Automatic Recovery** - Restart failed processes automatically
- **Logging Integration** - Enhanced logging for process management
- **Configuration Management** - Configurable process limits and timeouts 