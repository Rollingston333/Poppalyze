#!/usr/bin/env python3
"""
Stock Screener Stress Test
===========================
Progressive load testing: 100 → 1,000 → 10,000 → 1,000,000 users

Usage:
    locust -f stress_test.py --host=http://localhost:5001
"""

import random
from locust import HttpUser, task, between, events
import time

class StockScreenerUser(HttpUser):
    """Simulates realistic user behavior on the stock screener"""
    
    # Wait between 1-3 seconds between requests (realistic user behavior)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts - simulate user landing on homepage"""
        self.client.get("/")
    
    @task(30)  # 30% of requests - users browse main page frequently
    def view_homepage(self):
        """User views the main homepage"""
        self.client.get("/")
    
    @task(25)  # 25% of requests - most popular filter combinations
    def apply_common_filters(self):
        """Apply commonly used filter combinations"""
        common_filters = [
            "/?max_market_cap=1000000000&min_price=1&max_price=20",
            "/?max_market_cap=50000000000&min_rel_vol=2",
            "/?min_price=5&max_price=50&min_rel_vol=1",
            "/?max_market_cap=500000000&min_price=1&max_price=10",
            "/?min_rel_vol=3&min_pre_market_change=2",
        ]
        filter_url = random.choice(common_filters)
        self.client.get(filter_url)
    
    @task(20)  # 20% of requests - complex multi-filter scenarios
    def apply_complex_filters(self):
        """Apply complex filter combinations that users might use"""
        complex_filters = [
            "/?max_market_cap=10000000000&min_price=1&max_price=20&min_rel_vol=5&min_pre_market_change=4&max_float=2000000000",
            "/?max_market_cap=1000000000&min_price=5&max_price=100&min_rel_vol=2&min_gap_pct=5",
            "/?min_price=10&max_price=50&min_rel_vol=3&min_pre_market_change=3&max_float=100000000",
            "/?max_market_cap=500000000&min_price=1&max_price=30&min_rel_vol=2&min_pre_market_change=2&max_float=50000000",
        ]
        filter_url = random.choice(complex_filters)
        self.client.get(filter_url)
    
    @task(15)  # 15% of requests - check cache status (monitoring behavior)
    def check_cache_status(self):
        """Users checking cache/system status"""
        self.client.get("/api/cache_status")
    
    @task(5)   # 5% of requests - load static assets
    def load_static_assets(self):
        """Load static JavaScript files"""
        self.client.get("/static/js/analytics.js")
    
    @task(3)   # 3% of requests - single parameter filters
    def apply_single_filters(self):
        """Apply single parameter filters"""
        single_filters = [
            "/?max_market_cap=100000000",
            "/?min_price=10",
            "/?max_price=50",
            "/?min_rel_vol=2",
            "/?min_gap_pct=5",
        ]
        filter_url = random.choice(single_filters)
        self.client.get(filter_url)
    
    @task(2)   # 2% of requests - extreme filters (edge cases)
    def apply_extreme_filters(self):
        """Apply extreme filter values to test edge cases"""
        extreme_filters = [
            "/?max_market_cap=100000000&min_price=100&max_price=1000",  # High price range
            "/?min_rel_vol=10&min_pre_market_change=10",                # High volume/change
            "/?max_market_cap=10000000&max_float=1000000",              # Very small caps
        ]
        filter_url = random.choice(extreme_filters)
        self.client.get(filter_url)


class PowerUser(HttpUser):
    """Simulates power users who make rapid requests (API-like behavior)"""
    wait_time = between(0.1, 0.5)  # Very fast requests
    weight = 1  # Only 1/11 of users are power users
    
    @task(40)
    def rapid_filter_changes(self):
        """Power users rapidly changing filters"""
        self.client.get("/?max_market_cap=1000000000")
        self.client.get("/?min_price=5&max_price=20")
        self.client.get("/?min_rel_vol=3")
    
    @task(30)
    def api_monitoring(self):
        """Power users monitoring API status"""
        self.client.get("/api/cache_status")
    
    @task(30)
    def complex_queries(self):
        """Power users running complex queries"""
        self.client.get("/?max_market_cap=5000000000&min_price=1&max_price=100&min_rel_vol=5&min_pre_market_change=5")


class CasualUser(HttpUser):
    """Simulates casual users with slower, simpler behavior"""
    wait_time = between(3, 8)  # Slower browsing
    weight = 10  # 10/11 of users are casual users
    
    @task(50)
    def browse_slowly(self):
        """Casual users browse slowly"""
        self.client.get("/")
        time.sleep(random.uniform(2, 5))  # Reading time
    
    @task(30)
    def simple_filters(self):
        """Casual users use simple filters"""
        simple_filters = [
            "/?max_market_cap=1000000000",
            "/?min_price=5",
            "/?min_rel_vol=2",
        ]
        self.client.get(random.choice(simple_filters))
    
    @task(20)
    def occasional_complex_filter(self):
        """Occasionally use a more complex filter"""
        self.client.get("/?max_market_cap=1000000000&min_price=5&max_price=50")


# Event listeners for monitoring during tests
@events.request.add_listener
def my_request_handler(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    if exception:
        print(f"❌ Request failed: {name} - {exception}")
    elif response_time > 5000:  # Log slow requests (>5 seconds)
        print(f"⚠️  Slow request: {name} - {response_time}ms")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("🚀 Starting stress test...")
    print(f"🎯 Target: {environment.host}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("🏁 Stress test completed!")
    
# Custom test scenarios for different load levels
class LoadTestConfig:
    """Configuration for different load test scenarios"""
    
    SCENARIOS = {
        "100_users": {
            "users": 100,
            "spawn_rate": 10,
            "duration": "2m",
            "description": "Light load - 100 concurrent users"
        },
        "1000_users": {
            "users": 1000,
            "spawn_rate": 50,
            "duration": "3m", 
            "description": "Medium load - 1,000 concurrent users"
        },
        "10000_users": {
            "users": 10000,
            "spawn_rate": 100,
            "duration": "5m",
            "description": "Heavy load - 10,000 concurrent users"
        },
        "1000000_users": {
            "users": 1000000,
            "spawn_rate": 1000,
            "duration": "10m",
            "description": "EXTREME load - 1,000,000 concurrent users (requires cluster setup)"
        }
    }

if __name__ == "__main__":
    print("🔥 Stock Screener Stress Test Script")
    print("=====================================")
    print("Available test scenarios:")
    for name, config in LoadTestConfig.SCENARIOS.items():
        print(f"  📊 {name}: {config['description']}")
    print("\nTo run a specific test:")
    print("  locust -f stress_test.py --host=http://localhost:5001 -u 100 -r 10 -t 2m")
    print("\nFor web UI:")
    print("  locust -f stress_test.py --host=http://localhost:5001") 