// App.js - Main application JavaScript
console.log('App.js loaded successfully');

// Global error handler
window.addEventListener('error', function(event) {
    console.error('App.js caught error:', event.error);
});

// DOM ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('App.js: DOM ready');
    // Initialize any app functionality here
    initializeApp();
});

function initializeApp() {
    console.log('App.js: Initializing application');
    
    // Initialize quick movers functionality
    initializeQuickMovers();
    
    // Initialize cache status monitoring
    initializeCacheMonitoring();
    
    // Initialize auto-refresh functionality
    initializeAutoRefresh();
    
    console.log('App.js: Application initialized');
}

function initializeQuickMovers() {
    console.log('App.js: Initializing quick movers');
    
    // Add click handlers to quick mover cards
    const quickMoverCards = document.querySelectorAll('.quick-movers .stock-card');
    quickMoverCards.forEach(card => {
        card.addEventListener('click', function() {
            const symbol = this.querySelector('.stock-symbol').textContent;
            console.log('Quick mover clicked:', symbol);
            
            // Add visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
            
            // You can add more functionality here, like:
            // - Opening detailed view
            // - Adding to watchlist
            // - Showing news
        });
    });
    
    // Add hover effects
    quickMoverCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
        });
    });
}

function initializeCacheMonitoring() {
    console.log('App.js: Initializing cache monitoring');
    
    // Check cache status every 30 seconds
    setInterval(async function() {
        try {
            const response = await fetch('/api/cache_status');
            const data = await response.json();
            
            // Update cache status display if it exists
            const cacheStatusElement = document.querySelector('.cache-status');
            if (cacheStatusElement) {
                const ageMinutes = data.age_minutes || 0;
                const status = data.status || 'Unknown';
                
                if (ageMinutes < 2) {
                    cacheStatusElement.innerHTML = '🟢 Fresh Data';
                    cacheStatusElement.className = 'cache-status fresh';
                } else if (ageMinutes < 5) {
                    cacheStatusElement.innerHTML = '🟡 Getting Stale';
                    cacheStatusElement.className = 'cache-status stale';
                } else {
                    cacheStatusElement.innerHTML = '🔴 Stale Data';
                    cacheStatusElement.className = 'cache-status very-stale';
                }
            }
            
            // If data is very stale, show refresh suggestion
            if (ageMinutes > 10) {
                showRefreshSuggestion();
            }
            
        } catch (error) {
            console.error('Error checking cache status:', error);
        }
    }, 30000);
}

function initializeAutoRefresh() {
    console.log('App.js: Initializing auto-refresh');
    
    // Auto-refresh every 3 minutes (180000ms)
    setTimeout(function() {
        console.log('App.js: Auto-refreshing page');
        window.location.reload();
    }, 180000);
    
    // Add manual refresh button functionality
    const refreshButtons = document.querySelectorAll('.btn-primary, .btn-success');
    refreshButtons.forEach(button => {
        if (button.textContent.includes('Live Updates') || button.textContent.includes('Refresh')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                console.log('App.js: Manual refresh triggered');
                
                // Add loading state
                const originalText = this.textContent;
                this.textContent = '🔄 Refreshing...';
                this.disabled = true;
                
                // Refresh the page
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            });
        }
    });
}

function showRefreshSuggestion() {
    // Check if we already showed the suggestion
    if (document.getElementById('refresh-suggestion')) {
        return;
    }
    
    const suggestion = document.createElement('div');
    suggestion.id = 'refresh-suggestion';
    suggestion.className = 'alert alert-warning alert-dismissible fade show';
    suggestion.innerHTML = `
        <strong>⚠️ Data is getting stale!</strong> 
        Consider refreshing the page or starting the background scanner for live updates.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the page
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(suggestion, container.firstChild);
    
    // Auto-dismiss after 10 seconds
    setTimeout(() => {
        if (suggestion.parentNode) {
            suggestion.remove();
        }
    }, 10000);
}

// Utility function to format numbers
function formatNumber(num) {
    if (num >= 1e9) {
        return (num / 1e9).toFixed(1) + 'B';
    } else if (num >= 1e6) {
        return (num / 1e6).toFixed(1) + 'M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(1) + 'K';
    }
    return num.toString();
}

// Export for module systems if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        initializeApp, 
        initializeQuickMovers, 
        initializeCacheMonitoring, 
        initializeAutoRefresh,
        formatNumber 
    };
} 