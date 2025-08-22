# Poppalyze - Render Deployment Guide

## 🚀 Quick Deploy to Render

### Step 1: Prepare Your Repository

Make sure your GitHub repository contains these files:
- `app_streamlined.py` (main Flask app)
- `requirements_production.txt` (dependencies)
- `render.yaml` (Render configuration)
- `Procfile` (process configuration)
- `runtime.txt` (Python version)
- `templates/` folder (HTML templates)
- `static/` folder (CSS/JS files)

### Step 2: Deploy to Render

1. **Go to [render.com](https://render.com)** and sign up/login
2. **Click "New +"** → **"Web Service"**
3. **Connect your GitHub repository**
4. **Configure the service:**
   - **Name**: `poppalyze`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements_production.txt`
   - **Start Command**: `gunicorn app_streamlined:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Plan**: Free (or choose paid for better performance)

5. **Click "Create Web Service"**

### Step 3: Environment Variables (Optional)

Add these environment variables in Render dashboard:
- `FLASK_ENV=production`
- `FLASK_DEBUG=false`
- `PYTHON_VERSION=3.9`

### Step 4: Monitor Deployment

- **Build logs** will show installation progress
- **Deploy logs** will show app startup
- **Health check** at `/health` endpoint

## 🔧 Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: poppalyze
    env: python
    plan: free
    buildCommand: pip install -r requirements_production.txt
    startCommand: gunicorn app_streamlined:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
    envVars:
      - key: PYTHON_VERSION
        value: 3.9
      - key: FLASK_ENV
        value: production
    healthCheckPath: /health
```

### Procfile
```
web: gunicorn app_streamlined:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

### requirements_production.txt
```
Flask==3.0.2
yfinance==0.2.28
pandas==2.1.4
gunicorn==21.2.0
# ... other dependencies
```

## 📊 Features Available in Production

✅ **Stock Screening** - Real-time stock data
✅ **Background Scanning** - Continuous data updates
✅ **Advanced Filtering** - All filter options
✅ **Top Gappers** - Biggest movers
✅ **Quick Movers** - High volume stocks
✅ **Cache Management** - Efficient data storage
✅ **Traffic Analytics** - Visitor tracking
✅ **Admin Dashboard** - Traffic analytics

## 🚨 Important Notes

### Free Tier Limitations:
- **Sleep after 15 minutes** of inactivity
- **Limited bandwidth** and storage
- **Background processes** may be limited

### Production Considerations:
- **Upgrade to paid plan** for better performance
- **Monitor logs** for errors
- **Set up alerts** for downtime
- **Backup cache data** regularly

## 🔍 Troubleshooting

### Common Issues:

1. **Build fails**:
   - Check `requirements_production.txt` for missing dependencies
   - Verify Python version in `runtime.txt`

2. **App won't start**:
   - Check `Procfile` syntax
   - Verify `app_streamlined.py` exists
   - Check logs for import errors

3. **Background scanner not working**:
   - Free tier may limit background processes
   - Consider upgrading to paid plan

4. **Cache not persisting**:
   - Render free tier has ephemeral storage
   - Cache will reset on restarts

### Logs to Check:
- **Build logs**: Installation issues
- **Deploy logs**: Startup problems
- **Runtime logs**: Application errors

## 🎯 Next Steps

1. **Deploy to Render** using the guide above
2. **Test all features** once deployed
3. **Monitor performance** and logs
4. **Upgrade to paid plan** if needed
5. **Set up custom domain** (optional)

## 📞 Support

If you encounter issues:
1. **Check Render documentation**
2. **Review build/deploy logs**
3. **Verify all files are in repository**
4. **Test locally first**

---

**Your Poppalyze stock screener will be live at:**
`https://poppalyze.onrender.com` (or your custom URL) 