# 🔐 Poppalyze Admin Panel Setup Guide

This guide will help you set up and secure the admin panel for your Poppalyze stock screener deployed on Render.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Security Features](#security-features)
3. [Setup Instructions](#setup-instructions)
4. [Accessing the Admin Panel](#accessing-the-admin-panel)
5. [Admin Features](#admin-features)
6. [Security Best Practices](#security-best-practices)
7. [Troubleshooting](#troubleshooting)

## 🎯 Overview

The admin panel provides secure access to manage your Poppalyze stock screener application. It includes:

- **Dashboard**: Overview of system status and recent stocks
- **Cache Management**: Monitor and manage stock data cache
- **Settings**: View application configuration and security info
- **Secure Authentication**: Username/password protected access

## 🔒 Security Features

- **Session-based authentication** with secure cookies
- **Password hashing** using SHA-256
- **Environment variable configuration** for credentials
- **Login required decorator** for protected routes
- **Automatic logout** functionality
- **CSRF protection** through Flask sessions

## 🚀 Setup Instructions

### Step 1: Generate Secure Credentials

1. **Generate a password hash** (replace `your_secure_password` with your actual password):

```python
import hashlib
password = "your_secure_password"
hashed = hashlib.sha256(password.encode()).hexdigest()
print(hashed)
```

2. **Generate a secret key**:

```python
import secrets
secret_key = secrets.token_hex(32)
print(secret_key)
```

### Step 2: Configure Render Environment Variables

In your Render dashboard, go to your web service and add these environment variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `ADMIN_USERNAME` | `your_admin_username` | Your admin username |
| `ADMIN_PASSWORD_HASH` | `generated_hash_from_step_1` | SHA-256 hash of your password |
| `ADMIN_SECRET_KEY` | `generated_secret_from_step_1` | Secret key for session management |

### Step 3: Deploy to Render

1. Push your code to GitHub
2. Connect your repository to Render
3. Use the `render_combined.yaml` configuration
4. Deploy both web and worker services

## 🌐 Accessing the Admin Panel

### URLs

- **Main Screener**: `https://your-app-name.onrender.com/`
- **Admin Login**: `https://your-app-name.onrender.com/admin/login`
- **Admin Dashboard**: `https://your-app-name.onrender.com/admin`
- **Health Check**: `https://your-app-name.onrender.com/health`

### Login Process

1. Navigate to `/admin/login`
2. Enter your admin username and password
3. You'll be redirected to the dashboard upon successful login
4. Use the navigation menu to access different admin sections

## 🔧 Admin Features

### Dashboard (`/admin`)
- **System Statistics**: Total stocks, last update, scan count
- **Recent Stocks**: Top 10 stocks with gap percentages
- **Quick Actions**: Refresh cache button
- **Real-time Updates**: Live data from cache

### Cache Management (`/admin/cache`)
- **Cache Information**: File status, size, modification time
- **Stock Data**: Total stocks, last update, scan count
- **Cache Actions**:
  - Refresh cache from file
  - Download cache file
  - Clear cache (dangerous - removes all data)

### Settings (`/admin/settings`)
- **Application Configuration**: View current settings
- **Security Information**: Environment variable documentation
- **Deployment Info**: URLs and file structure
- **Password Security**: Instructions for generating hashes

## 🛡️ Security Best Practices

### 1. Strong Passwords
- Use a strong, unique password for admin access
- Consider using a password manager
- Change passwords regularly

### 2. Environment Variables
- Never commit credentials to version control
- Use Render's environment variable system
- Rotate secrets periodically

### 3. Access Control
- Limit admin access to trusted users only
- Monitor admin panel access logs
- Consider IP whitelisting for additional security

### 4. Regular Updates
- Keep your application dependencies updated
- Monitor for security vulnerabilities
- Update admin credentials periodically

### 5. Monitoring
- Check the health endpoint regularly
- Monitor cache status and updates
- Set up alerts for system issues

## 🔍 Troubleshooting

### Common Issues

#### 1. "Invalid username or password" error
- **Cause**: Incorrect credentials or hash mismatch
- **Solution**: 
  - Verify username matches `ADMIN_USERNAME` environment variable
  - Regenerate password hash and update `ADMIN_PASSWORD_HASH`
  - Ensure no extra spaces in environment variables

#### 2. Session errors or login loops
- **Cause**: Invalid or missing `ADMIN_SECRET_KEY`
- **Solution**:
  - Generate a new secret key
  - Update the `ADMIN_SECRET_KEY` environment variable
  - Restart the application

#### 3. Admin panel not accessible
- **Cause**: Route not found or application error
- **Solution**:
  - Check application logs in Render dashboard
  - Verify the web service is running
  - Check health endpoint: `/health`

#### 4. Cache not updating
- **Cause**: Worker service not running or cache file issues
- **Solution**:
  - Check worker service status in Render
  - Verify cache file permissions
  - Use admin panel to refresh cache manually

### Debugging Steps

1. **Check Render Logs**:
   - Go to your Render dashboard
   - Click on your web service
   - Check the "Logs" tab for errors

2. **Test Health Endpoint**:
   ```bash
   curl https://your-app-name.onrender.com/health
   ```

3. **Verify Environment Variables**:
   - Check all required variables are set in Render
   - Ensure no typos in variable names or values

4. **Test Local Development**:
   ```bash
   # Set environment variables locally
   export ADMIN_USERNAME=admin
   export ADMIN_PASSWORD_HASH=your_hash
   export ADMIN_SECRET_KEY=your_secret
   
   # Run the application
   python app_web.py
   ```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review Render application logs
3. Verify environment variable configuration
4. Test with the health endpoint
5. Check the cache status in the admin panel

## 🔄 Maintenance

### Regular Tasks
- Monitor cache freshness and stock data updates
- Check worker service status
- Review admin panel access logs
- Update dependencies and security patches
- Backup cache data periodically

### Security Updates
- Rotate admin credentials quarterly
- Update secret keys periodically
- Monitor for security vulnerabilities
- Keep Flask and dependencies updated

---

**⚠️ Important**: Always change the default credentials provided in the example configuration before deploying to production! 