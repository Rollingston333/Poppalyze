# 🚀 Poppalyze Deployment Checklist

## Pre-Deployment Testing

### ✅ **1. Run System Tests**
```bash
python3 test_system.py
```
- [ ] All configuration tests pass
- [ ] Cache manager tests pass
- [ ] Utility function tests pass
- [ ] Background scanner tests pass
- [ ] Flask app tests pass

### ✅ **2. Local Environment Test**
```bash
# Start background scanner
python3 background_scanner_fast.py &

# Start Flask app
python3 app.py

# Test endpoints
curl http://localhost:5001/health
curl http://localhost:5001/api/cache_status
```
- [ ] Background scanner starts without errors
- [ ] Cache file is created in `data/stock_cache.json`
- [ ] Flask app starts on correct port
- [ ] Health endpoint returns 200
- [ ] Cache status shows data

### ✅ **3. File Structure Validation**
```
project_root/
├── app.py                    # Main Flask application
├── cache_manager.py          # Cache management
├── background_scanner_fast.py # Background data scanner
├── config.py                 # Centralized configuration
├── utils.py                  # Utility functions
├── test_system.py           # System tests
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment config
├── Procfile                 # Process configuration
├── data/                    # Cache directory
│   └── stock_cache.json     # Stock data cache
└── templates/               # HTML templates
    └── screener.html        # Main page template
```

## Configuration Validation

### ✅ **4. Environment Variables**
- [ ] `PORT` - Set by Render automatically
- [ ] `FLASK_DEBUG` - Set to 'false' for production
- [ ] `SCAN_INTERVAL` - Set to 60 (1 minute)
- [ ] `MAX_STOCKS` - Set to 15
- [ ] `RATE_LIMIT_DELAY` - Set to 0.1

### ✅ **5. Path Configuration**
- [ ] All paths use `Config.BASE_DIR`
- [ ] Cache directory is `data/`
- [ ] Cache file is `data/stock_cache.json`
- [ ] PID file is `background_scanner_fast.pid`

## Code Quality Checks

### ✅ **6. Import Validation**
- [ ] No circular imports
- [ ] All imports use absolute paths
- [ ] Config is imported first
- [ ] Utils are imported where needed

### ✅ **7. Error Handling**
- [ ] All file operations use safe utilities
- [ ] JSON operations use custom serializer
- [ ] Background scanner has proper error handling
- [ ] Flask app has proper error handling

### ✅ **8. Data Validation**
- [ ] Cache data structure is validated
- [ ] Stock data format is consistent
- [ ] JSON serialization handles numpy types
- [ ] File operations are atomic

## Deployment Steps

### ✅ **9. Git Operations**
```bash
# Check current status
git status

# Add all files
git add .

# Commit with descriptive message
git commit -m "Fix: [specific issue] - [description]"

# Push to main branch
git push origin main
```

### ✅ **10. Render Deployment**
- [ ] Monitor deployment logs
- [ ] Check for build errors
- [ ] Verify health endpoint responds
- [ ] Confirm background scanner starts
- [ ] Test cache data loading

## Post-Deployment Validation

### ✅ **11. Live Site Testing**
```bash
# Test health endpoint
curl https://your-app.onrender.com/health

# Test cache status
curl https://your-app.onrender.com/api/cache_status

# Test main page
curl https://your-app.onrender.com/
```

### ✅ **12. Performance Validation**
- [ ] Health endpoint responds < 1 second
- [ ] Cache status responds < 1 second
- [ ] Main page loads < 5 seconds
- [ ] Background scanner updates every minute

### ✅ **13. Data Validation**
- [ ] Cache contains stock data
- [ ] Quick Movers section shows data
- [ ] Top Gappers section shows data
- [ ] Filter controls work correctly

## Common Issues & Solutions

### ❌ **JSON Serialization Error**
**Problem**: `Object of type int64 is not JSON serializable`
**Solution**: Use `utils.json_serializer` in all JSON operations

### ❌ **Path Confusion**
**Problem**: Different paths in local vs production
**Solution**: Always use `Config.BASE_DIR` and `Config.get_absolute_path()`

### ❌ **Missing Method Error**
**Problem**: `'CacheManager' object has no attribute 'method_name'`
**Solution**: Define all methods in CacheManager class

### ❌ **Cache Not Loading**
**Problem**: Flask app can't find cache data
**Solution**: Ensure both app and scanner use same Config

### ❌ **Background Scanner Not Starting**
**Problem**: Scanner fails to start on Render
**Solution**: Use `use_reloader=False` and proper PID file handling

## Monitoring & Maintenance

### ✅ **14. Log Monitoring**
- [ ] Check Render logs for errors
- [ ] Monitor background scanner output
- [ ] Verify cache updates regularly
- [ ] Check for memory leaks

### ✅ **15. Performance Monitoring**
- [ ] Monitor response times
- [ ] Check cache hit rates
- [ ] Monitor API rate limits
- [ ] Track error rates

### ✅ **16. Data Quality**
- [ ] Verify stock data freshness
- [ ] Check for missing symbols
- [ ] Validate price data
- [ ] Monitor gap calculations

## Emergency Procedures

### 🚨 **17. Rollback Plan**
```bash
# Revert to previous commit
git revert HEAD

# Or checkout specific commit
git checkout <commit-hash>

# Push rollback
git push origin main
```

### 🚨 **18. Manual Cache Reset**
```bash
# Clear cache manually
python3 -c "from cache_manager import cache_manager; cache_manager.clear_cache()"

# Restart scanner
pkill -f background_scanner_fast.py
python3 background_scanner_fast.py &
```

### 🚨 **19. Emergency Contact**
- [ ] Document issue in GitHub issues
- [ ] Check Render status page
- [ ] Review recent changes
- [ ] Test locally if possible

---

**Remember**: Always test locally before deploying, and monitor the live site after deployment! 