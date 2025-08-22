# Analytics Tracking System

A lightweight client-side analytics tracker similar to Plausible Analytics, designed specifically for the Gap Screener Dashboard.

## Features

- **Pageview Tracking**: Automatically logs page visits with URL, domain, and referrer information
- **Engagement Tracking**: Measures time spent on page (only when tab is focused) and scroll depth
- **Privacy Focused**: Automatically skips tracking on localhost, automated browsers, and when users opt-out
- **Real-time Events**: Sends data immediately via fetch() API to Flask backend

## Files Added

### 1. `/static/js/analytics.js`
Client-side JavaScript tracker that handles:
- Automatic pageview detection
- Focus/blur tracking for engagement time
- Scroll depth measurement
- URL change detection (for SPAs)
- Privacy controls and opt-out mechanisms

### 2. Flask Route: `/api/event`
Server-side endpoint in `app.py` that:
- Receives analytics events via POST requests
- Validates event data
- Logs events to console
- Optionally saves to file (commented out by default)

### 3. Test Page: `/analytics-test`
Demo page at `http://localhost:5001/analytics-test` with:
- Manual event triggers
- Long content for scroll testing
- Privacy controls demonstration

## How It Works

### Automatic Tracking

```javascript
// Pageview event is sent automatically when page loads
{
  "event": "pageview",
  "url": "http://localhost:5001/",
  "domain": "localhost",
  "referrer": "https://google.com",
  "user_agent": "Mozilla/5.0...",
  "timestamp": "2024-07-08T21:45:30.123Z"
}

// Engagement event is sent when user switches tabs or leaves page
{
  "event": "engagement", 
  "url": "http://localhost:5001/analytics-test",
  "domain": "localhost",
  "referrer": null,
  "engagement_time": 45,  // seconds with tab focused
  "scroll_depth": 85,     // percentage of page scrolled
  "timestamp": "2024-07-08T21:46:15.456Z"
}
```

### Privacy Controls

The tracker automatically ignores:
- **Localhost**: `localhost`, `127.0.0.1`, `[::1]`
- **Automated Browsers**: Selenium, Phantom, Nightmare, Cypress
- **User Opt-out**: When `localStorage.plausible_ignore = 'true'`

### Manual Controls

Users can control tracking via browser console:
```javascript
Analytics.ignore()    // Disable tracking
Analytics.enable()    // Re-enable tracking
Analytics.track()     // Send manual pageview
Analytics.engagement() // Send manual engagement event
```

## Server Logs

When events are received, you'll see logs like:
```
📊 ANALYTICS [PAGEVIEW] http://localhost:5001/ | IP: 127.0.0.1 | Referrer: Direct
📊 ANALYTICS [ENGAGEMENT] http://localhost:5001/analytics-test | Time: 45s | Scroll: 85% | IP: 127.0.0.1
```

## Testing

1. **Start your Flask app**: `python3 app.py`
2. **Visit test page**: `http://localhost:5001/analytics-test`
3. **Check browser console**: Look for analytics logs
4. **Check Flask logs**: Watch for analytics events in terminal
5. **Test engagement**: Scroll, switch tabs, click buttons

**Note**: Since tracking is disabled on localhost by default, you'll see warning messages in the console. For production testing, either:
- Access via a different hostname (not localhost)
- Temporarily comment out the localhost check in `analytics.js`

## Integration

The analytics tracker is automatically included in your main screener template (`templates/screener.html`) and will track:
- Page visits to your stock screener
- Time users spend analyzing stocks
- How much of the results table they scroll through
- Navigation patterns between filtered views

## Persistence (Optional)

To save analytics data to a file instead of just console logging, uncomment these lines in the `/api/event` route in `app.py`:

```python
# try:
#     with open('analytics.log', 'a', encoding='utf-8') as f:
#         f.write(json.dumps(log_entry) + '\n')
# except Exception as e:
#     print(f"⚠️  Error writing analytics log: {e}")
```

Each line in the log file will be a JSON object representing one analytics event.

## Configuration

You can modify the analytics behavior by editing `static/js/analytics.js`:

```javascript
var config = {
    endpoint: '/api/event',        // Where to send events
    domain: window.location.hostname,
    logging: true                  // Enable console logging
};
```

## Security

- All data is sent to your own Flask server (no third-party services)
- No cookies or persistent identifiers are used
- IP addresses are logged but can be easily removed if desired
- Users can opt-out at any time

This system gives you insight into how users interact with your gap screener while respecting privacy and keeping all data on your own server. 