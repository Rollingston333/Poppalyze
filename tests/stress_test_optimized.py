#!/usr/bin/env python3
"""
Stress Test for Optimized Stock Screener
=======================================
Tests the production-optimized Flask application under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class TestResult:
    url: str
    response_time: float
    status_code: int
    success: bool
    error: str = None

class StressTestRunner:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        
    async def make_request(self, session: aiohttp.ClientSession, url: str) -> TestResult:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                await response.text()  # Read response body
                response_time = time.time() - start_time
                return TestResult(
                    url=url,
                    response_time=response_time,
                    status_code=response.status,
                    success=response.status == 200
                )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                url=url,
                response_time=response_time,
                status_code=0,
                success=False,
                error=str(e)
            )
    
    async def concurrent_requests(self, url: str, num_requests: int, max_concurrent: int = 50):
        """Make concurrent requests to test scalability"""
        print(f"🚀 Testing {num_requests} concurrent requests (max {max_concurrent} at once)")
        
        connector = aiohttp.TCPConnector(limit=max_concurrent, limit_per_host=max_concurrent)
        async with aiohttp.ClientSession(connector=connector) as session:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def limited_request():
                async with semaphore:
                    return await self.make_request(session, url)
            
            tasks = [limited_request() for _ in range(num_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and add to results
            valid_results = [r for r in results if isinstance(r, TestResult)]
            self.results.extend(valid_results)
            
            return valid_results
    
    def analyze_results(self, results: List[TestResult], test_name: str):
        """Analyze and display test results"""
        if not results:
            print(f"❌ {test_name}: No valid results")
            return
        
        response_times = [r.response_time for r in results if r.success]
        success_count = len([r for r in results if r.success])
        total_count = len(results)
        
        if not response_times:
            print(f"❌ {test_name}: All requests failed")
            return
        
        # Calculate statistics
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        p95_time = sorted(response_times)[int(0.95 * len(response_times))] if len(response_times) > 0 else 0
        p99_time = sorted(response_times)[int(0.99 * len(response_times))] if len(response_times) > 0 else 0
        success_rate = (success_count / total_count) * 100
        
        print(f"\n📊 {test_name} Results:")
        print(f"   Total requests: {total_count}")
        print(f"   Successful: {success_count} ({success_rate:.1f}%)")
        print(f"   Average response time: {avg_time:.3f}s")
        print(f"   Median response time: {median_time:.3f}s")
        print(f"   95th percentile: {p95_time:.3f}s")
        print(f"   99th percentile: {p99_time:.3f}s")
        print(f"   Requests/second: {success_count / sum(response_times):.1f}")
        
        # Status breakdown
        status_codes = {}
        for result in results:
            status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1
        
        print(f"   Status codes: {status_codes}")
        
        # Performance rating
        if avg_time < 0.1 and success_rate > 99:
            print("   🌟 EXCELLENT performance!")
        elif avg_time < 0.5 and success_rate > 95:
            print("   ✅ Good performance")
        elif avg_time < 1.0 and success_rate > 90:
            print("   ⚠️  Acceptable performance")
        else:
            print("   ❌ Poor performance")
    
    async def run_progressive_load_test(self):
        """Run tests with progressively increasing load"""
        print("🎯 Running Progressive Load Test")
        print("=" * 50)
        
        test_scenarios = [
            (10, 5, "Light Load"),
            (50, 10, "Medium Load"),
            (100, 20, "Heavy Load"),
            (500, 50, "Stress Load"),
            (1000, 100, "Maximum Load"),
        ]
        
        base_endpoints = [
            "/",
            "/api/cache_status",
            "/health",
            "/?min_price=5&max_price=20&min_rel_vol=2",
            "/?max_market_cap=1000000000&min_gap_pct=5",
        ]
        
        for num_requests, max_concurrent, test_name in test_scenarios:
            print(f"\n🔄 {test_name}: {num_requests} requests, {max_concurrent} concurrent")
            
            # Test main page
            url = f"{self.base_url}/"
            results = await self.concurrent_requests(url, num_requests, max_concurrent)
            self.analyze_results(results, f"{test_name} - Main Page")
            
            # Brief pause between tests
            await asyncio.sleep(1)
    
    async def run_endpoint_stress_test(self):
        """Test different endpoints under stress"""
        print("\n🎯 Running Endpoint-Specific Stress Tests")
        print("=" * 50)
        
        endpoints = [
            ("/", "Main Page"),
            ("/api/cache_status", "Cache Status API"),
            ("/health", "Health Check"),
            ("/?min_price=5&max_price=20", "Filtered Results"),
            ("/?max_market_cap=100000000&min_rel_vol=3", "Complex Filter"),
        ]
        
        for endpoint, name in endpoints:
            url = f"{self.base_url}{endpoint}"
            results = await self.concurrent_requests(url, 200, 40)
            self.analyze_results(results, name)
            await asyncio.sleep(0.5)
    
    async def run_sustained_load_test(self, duration_minutes: int = 2):
        """Run sustained load for a specific duration"""
        print(f"\n🎯 Running Sustained Load Test ({duration_minutes} minutes)")
        print("=" * 50)
        
        end_time = time.time() + (duration_minutes * 60)
        request_count = 0
        
        while time.time() < end_time:
            batch_results = await self.concurrent_requests(f"{self.base_url}/", 50, 20)
            request_count += len(batch_results)
            
            # Real-time progress
            remaining = int(end_time - time.time())
            print(f"   ⏱️  {remaining}s remaining, {request_count} requests sent", end='\r')
            
            await asyncio.sleep(2)  # Brief pause between batches
        
        print(f"\n   ✅ Sustained test completed: {request_count} total requests")

def check_app_status(base_url: str) -> bool:
    """Check if the application is running"""
    import requests
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

async def main():
    parser = argparse.ArgumentParser(description="Stress test the optimized stock screener")
    parser.add_argument("--url", default="http://localhost:5001", help="Base URL to test")
    parser.add_argument("--quick", action="store_true", help="Run quick test only")
    parser.add_argument("--sustained", type=int, default=2, help="Sustained test duration (minutes)")
    
    args = parser.parse_args()
    
    # Check if app is running
    print(f"🔍 Checking if app is running at {args.url}...")
    if not check_app_status(args.url):
        print(f"❌ App not responding at {args.url}")
        print("💡 Start the optimized app with: gunicorn --config gunicorn_config.py app_optimized:app")
        sys.exit(1)
    
    print(f"✅ App is running at {args.url}")
    
    # Initialize stress tester
    tester = StressTestRunner(args.url)
    
    if args.quick:
        # Quick test
        print("\n🏃 Running Quick Stress Test")
        results = await tester.concurrent_requests(f"{args.url}/", 100, 20)
        tester.analyze_results(results, "Quick Test")
    else:
        # Full test suite
        await tester.run_progressive_load_test()
        await tester.run_endpoint_stress_test()
        
        if args.sustained > 0:
            await tester.run_sustained_load_test(args.sustained)
    
    print("\n🎉 Stress testing completed!")
    print("\n💡 To compare with before optimization:")
    print("   - Development app typically handles ~100 concurrent users")
    print("   - Optimized app should handle 1000+ concurrent users")
    print("   - Response times should be <100ms under load")

if __name__ == "__main__":
    asyncio.run(main()) 