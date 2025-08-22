# Gap Screener - Production Deployment Guide

## 🚀 Production-Ready Features

This application is now production-ready with the following improvements:

### ✅ Fixed Issues
- **Syntax Errors**: Resolved all Python syntax errors in `app.py`
- **Process Management**: Proper cleanup of stale processes and port conflicts
- **Cache Management**: Robust cache creation and validation
- **Error Handling**: Comprehensive error handling and logging
- **Startup Reliability**: Consistent startup process with health checks

### 🛡️ Production Features
- **Process Monitoring**: Automatic restart of failed processes
- **Health Checks**: Built-in health monitoring endpoints
- **Logging**: Structured logging with file and console output
- **Configuration Management**: Environment-based configuration
- **Docker Support**: Containerized deployment with security
- **Rollback Capability**: Automatic rollback on deployment failures
- **Backup System**: Automatic backup of data and configurations

## 📋 Prerequisites

### System Requirements
- **Python 3.13+**
- **Docker & Docker Compose** (for containerized deployment)
- **4GB+ RAM** (recommended)
- **2+ CPU cores** (recommended)
- **10GB+ disk space**

### Dependencies
```bash
# Install production dependencies
pip install -r requirements_production.txt
```

## 🚀 Quick Start (Local Production)

### Option 1: Direct Python Deployment
```bash
# Start with production startup script
python3 start_production.py
```

### Option 2: Docker Deployment
```bash
# Build and run with Docker
./deploy_production.sh
```

## 📊 Application Status

### Health Check
```bash
curl http://localhost:5001/health
```

### Cache Status
```bash
curl http://localhost:5001/api/cache_status
```

### Scanner Status
```bash
curl http://localhost:5001/api/scanner/status
```

## 🔧 Configuration

### Environment Variables
```bash
# Production settings
export FLASK_ENV=production
export DISABLE_AUTO_SCANNER=1
export SECRET_KEY=your-secure-secret-key

# Optional: Custom settings
export SCAN_INTERVAL_SECONDS=900  # 15 minutes
export MAX_STOCKS=50
export CACHE_FRESHNESS_MINUTES=60
```

### Configuration Files
- `config.py` - Centralized configuration management
- `start_production.py` - Production startup script
- `Dockerfile.production` - Production Docker configuration

## 🐳 Docker Deployment

### Build Image
```bash
docker build -f Dockerfile.production -t gap-screener:latest .
```

### Run Container
```bash
docker run -d \
  --name gap-screener-prod \
  -p 5001:5001 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/cache:/app/cache \
  -e FLASK_ENV=production \
  -e DISABLE_AUTO_SCANNER=1 \
  gap-screener:latest
```

### Using Docker Compose
```bash
# Start with docker-compose
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

## 🔄 Deployment Scripts

### Full Production Deployment
```bash
# Deploy with automatic backup and rollback
./deploy_production.sh

# Rollback to previous version
./deploy_production.sh rollback

# Check health status
./deploy_production.sh health

# Cleanup old images
./deploy_production.sh cleanup
```

### Manual Deployment Steps
1. **Backup current deployment**
2. **Stop existing services**
3. **Build new image**
4. **Start new deployment**
5. **Wait for health checks**
6. **Verify functionality**

## 📈 Monitoring & Logging

### Log Files
- `production.log` - Application logs
- `logs/` - Directory for additional log files
- `cache/` - Cache and data files

### Health Monitoring
- **Health Endpoint**: `/health`
- **Cache Status**: `/api/cache_status`
- **Scanner Status**: `/api/scanner/status`

### Performance Metrics
- Response time monitoring
- Cache hit/miss rates
- Scanner performance metrics
- Error rate tracking

## 🔒 Security Considerations

### Production Security
- **Non-root user**: Application runs as non-root in Docker
- **Environment variables**: Sensitive data in environment variables
- **Input validation**: All user inputs validated
- **Rate limiting**: Built-in API rate limiting
- **Error handling**: No sensitive data in error messages

### Security Checklist
- [ ] Change default secret key
- [ ] Configure firewall rules
- [ ] Set up SSL/TLS certificates
- [ ] Enable HTTPS
- [ ] Configure backup encryption
- [ ] Set up monitoring alerts

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check for port conflicts
lsof -i :5001

# Check for syntax errors
python3 -m py_compile app.py

# Check logs
tail -f production.log
```

#### Cache Issues
```bash
# Recreate cache
python3 create_mixed_price_cache.py

# Check cache file
python3 -c "import json; print(json.load(open('stock_cache.json')))"
```

#### Process Conflicts
```bash
# Clean up processes
pkill -f "python.*app.py"
pkill -f "python.*background_scanner.py"

# Remove PID files
rm -f background_scanner.pid
```

### Debug Mode
```bash
# Enable debug mode
export FLASK_ENV=development
export DEBUG=1

# Start with debug
python3 app.py
```

## 📊 Performance Optimization

### Recommended Settings
- **Cache freshness**: 30-60 minutes
- **Scan interval**: 10-15 minutes
- **Max stocks**: 50-100
- **Rate limiting**: 10-15 seconds between API calls

### Scaling Considerations
- **Horizontal scaling**: Multiple app instances behind load balancer
- **Vertical scaling**: Increase CPU/memory for single instance
- **Database scaling**: Consider Redis for caching
- **CDN**: Static asset delivery

## 🔄 Maintenance

### Regular Tasks
- **Log rotation**: Rotate log files weekly
- **Cache cleanup**: Clean old cache files monthly
- **Security updates**: Update dependencies regularly
- **Backup verification**: Test backup restoration monthly

### Update Process
1. **Create backup**
2. **Deploy new version**
3. **Run health checks**
4. **Monitor performance**
5. **Rollback if needed**

## 📞 Support

### Log Locations
- Application logs: `production.log`
- Docker logs: `docker logs gap-screener-prod`
- System logs: `/var/log/syslog`

### Health Check Commands
```bash
# Basic health
curl -f http://localhost:5001/health

# Detailed status
curl -s http://localhost:5001/api/cache_status | jq

# Process status
ps aux | grep python
```

### Emergency Procedures
1. **Stop application**: `pkill -f "python.*app.py"`
2. **Restart services**: `python3 start_production.py`
3. **Rollback**: `./deploy_production.sh rollback`
4. **Contact support**: Check logs and error messages

## ✅ Production Checklist

Before going live, ensure:

- [ ] All tests pass
- [ ] Health checks working
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Backup system tested
- [ ] Security measures implemented
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Support procedures defined
- [ ] Rollback plan tested

---

**🎉 Your Gap Screener is now production-ready!**

The application includes:
- ✅ Robust startup and shutdown procedures
- ✅ Comprehensive error handling and logging
- ✅ Health monitoring and automatic recovery
- ✅ Docker containerization with security
- ✅ Backup and rollback capabilities
- ✅ Production-grade configuration management
- ✅ Performance optimization and monitoring

For additional support or questions, refer to the troubleshooting section or check the application logs. 