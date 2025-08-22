# 🚀 Deploying Poppalyze to Render

## Quick Deployment Guide

### Step 1: Prepare Your Repository
1. Make sure all files are committed to your Git repository
2. Ensure you have these files in your repo:
   - `app_production.py` (main Flask app)
   - `requirements.txt` (dependencies)
   - `Procfile` (startup command)
   - `templates/screener.html` (HTML template)
   - `static/` folder (CSS, JS files)

### Step 2: Deploy to Render

1. **Go to [render.com](https://render.com)** and sign up/login

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing Poppalyze

3. **Configure the Service**
   - **Name**: `poppalyze` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app_production:app --bind 0.0.0.0:$PORT`
   - **Plan**: Free (for testing)

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app
   - Wait for the build to complete (usually 2-3 minutes)

### Step 3: Access Your App

Once deployed, you'll get a URL like:
```
https://poppalyze.onrender.com
```

### Step 4: Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain (e.g., `poppalyze.com`)
4. Update your DNS settings as instructed

## Features

✅ **Automatic HTTPS** - Secure by default
✅ **Global CDN** - Fast loading worldwide
✅ **Auto-deploy** - Updates when you push to Git
✅ **Free tier** - No cost for basic usage
✅ **Custom domains** - Use your own domain
✅ **Environment variables** - Secure configuration

## Monitoring

- **Logs**: View real-time logs in the Render dashboard
- **Metrics**: Monitor performance and usage
- **Health checks**: Automatic uptime monitoring

## Troubleshooting

### Common Issues:

1. **Build fails**: Check `requirements.txt` for correct dependencies
2. **App won't start**: Verify `Procfile` has correct start command
3. **No data showing**: Background scanner may need time to populate cache

### Support:
- Render documentation: https://render.com/docs
- Community forum: https://community.render.com

## Next Steps

After deployment, consider:
- Setting up environment variables for configuration
- Adding a custom domain
- Setting up monitoring and alerts
- Optimizing for production performance 