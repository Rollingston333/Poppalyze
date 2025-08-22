# 🔧 Admin Dashboard - Gap Screener

## Overview

The Admin Dashboard provides comprehensive monitoring, tracking, and management capabilities for the Gap Screener application. It runs on a separate port (5002) and provides real-time insights into system health, performance, and operational status.

## 🚀 Quick Start

### 1. Start the Admin Dashboard

```bash
# Start admin dashboard only
python3 admin_dashboard.py

# Or start everything together (recommended)
python3 start_with_admin.py
```

### 2. Access the Dashboard

- **URL**: http://localhost:5002/admin
- **Default Credentials**: 
  - Username: `admin`
  - Password: `admin123`

### 3. Health Check

```bash
curl http://localhost:5002/admin/health
```

## 📊 Dashboard Features

### 🔍 System Monitoring

#### Real-time System Metrics
- **CPU Usage**: Current CPU utilization percentage
- **Memory Usage**: RAM usage and available memory
- **Disk Usage**: Storage utilization and free space
- **Process Status**: Running processes and their resource usage

#### Service Status
- **Main Application**: Status of the Flask web app (port 5001)
- **Background Scanner**: Status of the stock data scanner
- **Cache Status**: Stock cache file health and age

### ⚡ Quick Actions

#### Service Management
- **Restart Main App**: Restart the Flask application
- **Restart Scanner**: Restart the background scanner
- **Clear Cache**: Remove all cached stock data
- **Refresh Data**: Update dashboard metrics

#### Process Monitoring
- **Process List**: View all running Python processes
- **Resource Usage**: CPU and memory usage per process
- **Process Status**: Running, stopped, or error states

### 📝 Log Management

#### Real-time Logs
- **Recent Logs**: Last 20 log entries (configurable)
- **Log Levels**: INFO, WARNING, ERROR with color coding
- **Auto-refresh**: Logs update every 30 seconds
- **Manual Refresh**: Refresh logs on demand

#### Log Files Supported
- `production.log` (default)
- `admin.log`
- `background_scanner.log`

## 🛡️ Security Features

### Authentication
- **Login Required**: All dashboard pages require authentication
- **Session Management**: Secure session handling with Flask-Login
- **Logout**: Secure logout functionality

### Access Control
- **Protected Routes**: All API endpoints require authentication
- **CSRF Protection**: Built-in CSRF protection
- **Secure Headers**: Security headers for production

## 🔧 Configuration

### Environment Variables

```bash
# Admin dashboard secret key (change in production)
export ADMIN_SECRET_KEY="your-secure-secret-key"

# Disable auto-scanner for main app
export DISABLE_AUTO_SCANNER=1
```

### Port Configuration

```python
# Default ports (configurable in admin_dashboard.py)
MAIN_APP_PORT = 5001
ADMIN_PORT = 5002
```

## 📈 API Endpoints

### Health Check
```bash
GET /admin/health
# Returns: {"status": "healthy", "admin_dashboard": true, "timestamp": "..."}
```

### System Status
```bash
GET /admin/api/status
# Returns: Complete system status including CPU, memory, services, cache
```

### Process Information
```bash
GET /admin/api/processes
# Returns: List of running processes with resource usage
```

### Log Entries
```bash
GET /admin/api/logs?lines=50&file=production.log
# Returns: Recent log entries with timestamps and levels
```

### Service Management
```bash
POST /admin/api/restart/main_app
POST /admin/api/restart/background_scanner
POST /admin/api/clear-cache
```

## 🚨 Monitoring & Alerts

### Status Indicators
- 🟢 **Green**: Healthy/Operating normally
- 🟡 **Yellow**: Warning/Stale data
- 🔴 **Red**: Error/Service down

### Auto-refresh
- **Dashboard**: Updates every 30 seconds
- **Logs**: Real-time log monitoring
- **Processes**: Live process status

### Error Handling
- **Graceful Degradation**: Dashboard continues working even if some services fail
- **Error Messages**: Clear error reporting for troubleshooting
- **Retry Logic**: Automatic retry for failed operations

## 🔄 Process Management

### Automatic Restart
The admin dashboard can automatically restart failed services:

```python
# In start_with_admin.py
def monitor_processes(main_app_process, admin_process, scanner_process):
    # Monitors processes and restarts if they fail
    # Checks every 30 seconds
```

### Manual Control
- **Restart Services**: One-click service restart
- **Process Cleanup**: Automatic cleanup of stale processes
- **Resource Monitoring**: Track CPU and memory usage

## 📊 Cache Management

### Cache Status Monitoring
- **File Age**: How old the cache data is
- **Stock Count**: Number of stocks in cache
- **File Size**: Cache file size in MB
- **Status**: Fresh, stale, or old

### Cache Operations
- **Clear Cache**: Remove all cached data
- **Cache Health**: Monitor cache file integrity
- **Auto-refresh**: Automatic cache status updates

## 🛠️ Troubleshooting

### Common Issues

#### Admin Dashboard Won't Start
```bash
# Check dependencies
python3 -c "import flask_login, psutil; print('Dependencies OK')"

# Install missing dependencies
python3 -m pip install Flask-Login psutil --break-system-packages
```

#### Can't Access Dashboard
```bash
# Check if port 5002 is available
lsof -i :5002

# Kill existing processes
pkill -f admin_dashboard.py
```

#### Authentication Issues
```bash
# Default credentials
Username: admin
Password: admin123

# Check admin.log for errors
tail -f admin.log
```

### Log Files
- `admin.log`: Admin dashboard logs
- `production.log`: Main application logs
- `background_scanner.log`: Scanner logs

## 🔒 Production Security

### Before Deployment
1. **Change Default Credentials**:
   ```python
   # In admin_dashboard.py, change the authentication
   if username == 'your_admin_user' and password == 'your_secure_password':
   ```

2. **Set Secure Secret Key**:
   ```bash
   export ADMIN_SECRET_KEY="your-very-secure-secret-key"
   ```

3. **Use HTTPS**: Configure SSL/TLS for production

4. **Restrict Access**: Use firewall rules to limit access to admin port

### Security Best Practices
- Use strong, unique passwords
- Enable HTTPS in production
- Regularly rotate credentials
- Monitor access logs
- Use environment variables for secrets

## 📋 Usage Examples

### Start Complete System
```bash
# Start everything with admin dashboard
python3 start_with_admin.py
```

### Monitor System Health
```bash
# Check system status via API
curl -u admin:admin123 http://localhost:5002/admin/api/status

# Check health endpoint
curl http://localhost:5002/admin/health
```

### Restart Services
```bash
# Restart main application
curl -X POST -u admin:admin123 http://localhost:5002/admin/api/restart/main_app

# Restart background scanner
curl -X POST -u admin:admin123 http://localhost:5002/admin/api/restart/background_scanner
```

### Clear Cache
```bash
# Clear all cached data
curl -X POST -u admin:admin123 http://localhost:5002/admin/api/clear-cache
```

## 🎯 Integration

### With Main Application
The admin dashboard is designed to work alongside the main Gap Screener application:

- **Separate Port**: Runs on port 5002 (main app on 5001)
- **Shared Resources**: Monitors the same cache and processes
- **Independent Operation**: Can run even if main app is down

### With Monitoring Tools
The admin dashboard provides API endpoints that can be integrated with:

- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **Nagios**: System monitoring
- **Custom Scripts**: Automated monitoring

## 📞 Support

### Getting Help
1. Check the logs: `tail -f admin.log`
2. Verify dependencies: `python3 -c "import flask_login, psutil"`
3. Check port availability: `lsof -i :5002`
4. Review this documentation

### Common Commands
```bash
# Start admin dashboard
python3 admin_dashboard.py

# Check status
curl http://localhost:5002/admin/health

# View logs
tail -f admin.log

# Restart everything
python3 start_with_admin.py
```

---

**Note**: This admin dashboard is designed for development and production use. Always change default credentials and use proper security measures in production environments. 