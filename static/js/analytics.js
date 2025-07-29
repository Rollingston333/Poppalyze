!function() {
    // Configuration
    var config = {
        endpoint: '/api/event',
        domain: window.location.hostname,
        logging: true
    };

    // State variables
    var isIgnored = false;
    var currentUrl = location.href;
    var pageStartTime = 0;
    var engagementTime = 0;
    var maxScrollDepth = 0;
    var isVisible = true;
    var sessionData = {};

    // Check if tracking should be ignored
    function shouldIgnore() {
        // Skip localhost
        if (/^localhost$|^127(\.[0-9]+){0,2}\.[0-9]+$|^\[::1?\]$/.test(location.hostname) || 
            location.protocol === 'file:') {
            return 'localhost';
        }

        // Skip automated browsers
        if (window._phantom || window.__nightmare || window.navigator.webdriver || window.Cypress) {
            return 'automated browser';
        }

        // Skip static file requests (JS, CSS, images)
        if (location.pathname.startsWith('/static/') || 
            location.pathname.includes('.js') || 
            location.pathname.includes('.css') || 
            location.pathname.includes('.ico') ||
            location.pathname.includes('.png') ||
            location.pathname.includes('.jpg') ||
            location.pathname.includes('.gif')) {
            return 'static file';
        }

        // Skip API calls
        if (location.pathname.startsWith('/api/') || 
            location.pathname === '/health') {
            return 'api call';
        }

        // Check localStorage ignore flag
        try {
            if (window.localStorage.plausible_ignore === 'true') {
                return 'localStorage flag';
            }
        } catch (e) {}

        return false;
    }

    // Send event to server
    function sendEvent(eventData, callback) {
        if (isIgnored) return;

        if (window.fetch) {
            fetch(config.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                keepalive: true,
                body: JSON.stringify(eventData)
            }).then(function(response) {
                if (callback) callback({ status: response.status });
            }).catch(function(error) {
                if (callback) callback({ error: error });
            });
        }
    }

    // Get document height
    function getDocumentHeight() {
        var body = document.body || {};
        var html = document.documentElement || {};
        return Math.max(
            body.scrollHeight || 0, 
            body.offsetHeight || 0, 
            body.clientHeight || 0,
            html.scrollHeight || 0, 
            html.offsetHeight || 0, 
            html.clientHeight || 0
        );
    }

    // Get current scroll position
    function getScrollPosition() {
        var body = document.body || {};
        var html = document.documentElement || {};
        var viewportHeight = window.innerHeight || html.clientHeight || 0;
        var scrollTop = window.scrollY || html.scrollTop || body.scrollTop || 0;
        return scrollTop + viewportHeight;
    }

    // Calculate scroll depth percentage
    function getScrollDepth() {
        var documentHeight = getDocumentHeight();
        var currentPosition = getScrollPosition();
        
        if (documentHeight <= window.innerHeight) {
            return 100; // Page fits in viewport
        }
        
        return Math.min(100, Math.round((currentPosition / documentHeight) * 100));
    }

    // Update engagement tracking
    function updateEngagement() {
        if (isVisible && pageStartTime > 0) {
            engagementTime += Date.now() - pageStartTime;
            pageStartTime = Date.now();
        }
    }

    // Handle visibility changes
    function handleVisibilityChange() {
        if (document.visibilityState === 'visible' && document.hasFocus()) {
            if (!isVisible) {
                isVisible = true;
                pageStartTime = Date.now();
            }
        } else {
            if (isVisible) {
                updateEngagement();
                isVisible = false;
                pageStartTime = 0;
                
                // Send engagement event when user leaves
                sendEngagementEvent();
            }
        }
    }

    // Handle scroll events
    function handleScroll() {
        var currentDepth = getScrollDepth();
        if (currentDepth > maxScrollDepth) {
            maxScrollDepth = currentDepth;
        }
    }

    // Send engagement event
    function sendEngagementEvent() {
        if (engagementTime < 1000) return; // Ignore very short visits

        var eventData = {
            event: 'engagement',
            url: currentUrl,
            domain: config.domain,
            referrer: document.referrer || null,
            engagement_time: Math.round(engagementTime / 1000), // seconds
            scroll_depth: maxScrollDepth,
            timestamp: new Date().toISOString()
        };

        if (config.logging) {
            console.log('📊 Analytics: Engagement event', eventData);
        }

        sendEvent(eventData);
    }

    // Send pageview event
    function sendPageview(url) {
        var eventData = {
            event: 'pageview',
            url: url || currentUrl,
            domain: config.domain,
            referrer: document.referrer || null,
            user_agent: navigator.userAgent,
            timestamp: new Date().toISOString()
        };

        if (config.logging) {
            console.log('📊 Analytics: Pageview event', eventData);
        }

        sendEvent(eventData);

        // Reset engagement tracking for new page
        engagementTime = 0;
        maxScrollDepth = getScrollDepth();
        pageStartTime = Date.now();
        isVisible = true;
    }

    // Handle URL changes (for SPAs)
    function setupUrlChangeTracking() {
        var lastUrl = currentUrl;

        function checkUrlChange() {
            if (currentUrl !== location.href) {
                // Send engagement for previous page
                updateEngagement();
                sendEngagementEvent();

                // Track new page
                currentUrl = location.href;
                sendPageview(currentUrl);
            }
        }

        // Override pushState and replaceState
        var originalPushState = history.pushState;
        var originalReplaceState = history.replaceState;

        history.pushState = function() {
            originalPushState.apply(this, arguments);
            setTimeout(checkUrlChange, 0);
        };

        history.replaceState = function() {
            originalReplaceState.apply(this, arguments);
            setTimeout(checkUrlChange, 0);
        };

        // Handle back/forward navigation
        window.addEventListener('popstate', checkUrlChange);
    }

    // Initialize tracking
    function init() {
        var ignoreReason = shouldIgnore();
        if (ignoreReason) {
            isIgnored = true;
            if (config.logging) {
                console.warn('📊 Analytics: Ignoring tracking -', ignoreReason);
            }
            return;
        }

        if (config.logging) {
            console.log('📊 Analytics: Initialized for', config.domain);
        }

        // Set up event listeners
        document.addEventListener('visibilitychange', handleVisibilityChange);
        window.addEventListener('blur', handleVisibilityChange);
        window.addEventListener('focus', handleVisibilityChange);
        window.addEventListener('scroll', handleScroll);

        // Handle page unload
        window.addEventListener('beforeunload', function() {
            updateEngagement();
            sendEngagementEvent();
        });

        // Set up URL change tracking
        setupUrlChangeTracking();

        // Send initial pageview
        if (document.visibilityState === 'visible') {
            sendPageview();
        } else {
            // Wait for page to become visible
            document.addEventListener('visibilitychange', function() {
                if (document.visibilityState === 'visible' && pageStartTime === 0) {
                    sendPageview();
                }
            });
        }
    }

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose public API
    window.Analytics = {
        track: sendPageview,
        engagement: sendEngagementEvent,
        ignore: function() {
            try {
                localStorage.plausible_ignore = 'true';
                isIgnored = true;
                console.log('📊 Analytics: Tracking disabled');
            } catch (e) {
                console.warn('📊 Analytics: Could not disable tracking');
            }
        },
        enable: function() {
            try {
                localStorage.removeItem('plausible_ignore');
                isIgnored = false;
                console.log('📊 Analytics: Tracking enabled');
            } catch (e) {
                console.warn('📊 Analytics: Could not enable tracking');
            }
        }
    };
}(); 