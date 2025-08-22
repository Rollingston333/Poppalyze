#!/usr/bin/env python3
"""
Production Reliability Test Suite
=================================
Comprehensive testing for real-world production scenarios
Tests stability, performance, and data consistency under various conditions
"""

import asyncio
import aiohttp
import time
import statistics
import json
import concurrent.futures
import threading
from datetime import datetime, timedelta
from tabulate import tabulate
import random

class ProductionReliabilityTests:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = {}
        self.test_start_time = None
        
    async def test_scenario(self, name, url_pattern, concurrent_users, duration_minutes, request_interval=1.0):
        """Test a specific usage scenario"""
        print(f"\n🧪 Testing: {name}")
        print(f"   👥 Users: {concurrent_users}")
        print(f"   ⏱️  Duration: {duration_minutes} minutes")
        print(f"   🔄 Request interval: {request_interval}s")
        
        # Metrics collection
        response_times = []
        status_codes = []
        errors = []
        data_consistency_checks = []
        
        # Semaphore for concurrent control
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def simulate_user():
            """Simulate a single user's behavior"""
            connector = aiohttp.TCPConnector(limit=100)
            timeout = aiohttp.ClientTimeout(total=30)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                end_time = time.time() + (duration_minutes * 60)
                user_requests = 0
                
                while time.time() < end_time:
                    async with semaphore:
                        start_time = time.time()
                        
                        try:
                            # Simulate realistic user behavior
                            url = self._generate_realistic_url(url_pattern)
                            
                            async with session.get(url) as response:
                                response_time = time.time() - start_time
                                content = await response.text()
                                
                                # Collect metrics
                                response_times.append(response_time)
                                status_codes.append(response.status)
                                
                                # Data consistency checks
                                if response.status == 200:
                                    consistency_check = self._check_data_consistency(content, url)
                                    data_consistency_checks.append(consistency_check)
                                
                                user_requests += 1
                                
                        except Exception as e:
                            response_time = time.time() - start_time
                            response_times.append(response_time)
                            status_codes.append(0)  # Connection error
                            errors.append(str(e))
                    
                    # Realistic user think time
                    await asyncio.sleep(request_interval + random.uniform(-0.5, 0.5))
                
                return user_requests
        
        # Run concurrent users
        tasks = [simulate_user() for _ in range(concurrent_users)]
        user_request_counts = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate metrics
        successful_requests = len([s for s in status_codes if s == 200])
        total_requests = len(status_codes)
        error_rate = (total_requests - successful_requests) / total_requests * 100 if total_requests > 0 else 0
        
        avg_response_time = statistics.mean(response_times) if response_times else 0
        p95_response_time = sorted(response_times)[int(0.95 * len(response_times))] if response_times else 0
        p99_response_time = sorted(response_times)[int(0.99 * len(response_times))] if response_times else 0
        
        throughput = successful_requests / (duration_minutes * 60) if duration_minutes > 0 else 0
        
        # Data consistency score
        consistency_score = (sum(data_consistency_checks) / len(data_consistency_checks) * 100) if data_consistency_checks else 0
        
        # Performance rating
        if avg_response_time < 0.1 and error_rate < 1 and consistency_score > 95:
            rating = "🌟 EXCELLENT"
        elif avg_response_time < 0.5 and error_rate < 5 and consistency_score > 90:
            rating = "✅ GOOD"
        elif avg_response_time < 1.0 and error_rate < 10 and consistency_score > 85:
            rating = "⚠️ ACCEPTABLE"
        else:
            rating = "❌ POOR"
        
        result = {
            'scenario': name,
            'concurrent_users': concurrent_users,
            'duration_minutes': duration_minutes,
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'p95_response_time': p95_response_time,
            'p99_response_time': p99_response_time,
            'throughput_req_sec': throughput,
            'consistency_score': consistency_score,
            'rating': rating,
            'errors': list(set(errors))[:5],  # Top 5 unique errors
            'user_request_counts': [c for c in user_request_counts if isinstance(c, int)]
        }
        
        print(f"   📊 Results: {rating}")
        print(f"      • {successful_requests}/{total_requests} requests successful ({100-error_rate:.1f}%)")
        print(f"      • Avg response: {avg_response_time:.3f}s | P95: {p95_response_time:.3f}s")
        print(f"      • Throughput: {throughput:.1f} req/sec")
        print(f"      • Data consistency: {consistency_score:.1f}%")
        
        return result
    
    def _generate_realistic_url(self, pattern):
        """Generate realistic URLs based on usage patterns"""
        if pattern == "main_page":
            # Simulate different filter combinations
            filters = [
                "",
                "?min_price=1&max_price=50",
                "?min_gap_pct=2&min_rel_vol=1.5",
                "?sector_filter=Technology",
                "?min_price=5&max_price=20&min_gap_pct=1",
                "?min_market_cap=1000000000&max_market_cap=50000000000"
            ]
            return f"{self.base_url}/{random.choice(filters)}"
        
        elif pattern == "api_stocks":
            limits = ["", "?limit=10", "?limit=50", "?limit=100"]
            return f"{self.base_url}/api/stocks{random.choice(limits)}"
        
        elif pattern == "cache_status":
            return f"{self.base_url}/api/cache_status"
        
        else:
            return f"{self.base_url}/"
    
    def _check_data_consistency(self, content, url):
        """Check data consistency and completeness"""
        try:
            # Check for basic content presence
            if "error" in content.lower() and "500" in content:
                return 0  # Server error
            
            if len(content) < 1000:  # Suspiciously small response
                return 0.5
            
            # Check for expected elements
            expected_elements = ["Pop-Off Finder", "stocks", "filter"]
            elements_found = sum(1 for element in expected_elements if element.lower() in content.lower())
            
            if "/api/" in url:
                # API response checks
                try:
                    if content.strip():
                        data = json.loads(content)
                        if isinstance(data, dict) and ("success" in data or "stocks" in data):
                            return 1.0
                        return 0.7
                except:
                    return 0.3
            else:
                # HTML response checks
                consistency_score = elements_found / len(expected_elements)
                
                # Bonus points for specific components
                if "quick_movers" in content.lower() or "positive_gappers" in content.lower():
                    consistency_score += 0.1
                
                return min(consistency_score, 1.0)
            
        except Exception:
            return 0.5  # Partial consistency on parsing errors
    
    async def run_comprehensive_tests(self):
        """Run comprehensive reliability test suite"""
        self.test_start_time = datetime.now()
        
        print("🚀 PRODUCTION RELIABILITY TEST SUITE")
        print("=" * 60)
        print(f"🕐 Started: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Target: {self.base_url}")
        
        # Check if app is running
        try:
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status != 200:
                        raise Exception("Health check failed")
        except Exception as e:
            print(f"❌ App not accessible at {self.base_url}")
            print(f"💡 Make sure the app is running: python3 app.py")
            return
        
        print("✅ App is accessible, starting tests...\n")
        
        # Test scenarios simulating real production usage
        test_scenarios = [
            {
                'name': 'Light Usage - Office Hours',
                'url_pattern': 'main_page',
                'concurrent_users': 5,
                'duration_minutes': 2,
                'request_interval': 3.0
            },
            {
                'name': 'Normal Usage - Market Open Rush',
                'url_pattern': 'main_page',
                'concurrent_users': 25,
                'duration_minutes': 3,
                'request_interval': 2.0
            },
            {
                'name': 'Heavy Usage - News Event Spike',
                'url_pattern': 'main_page',
                'concurrent_users': 100,
                'duration_minutes': 2,
                'request_interval': 1.0
            },
            {
                'name': 'API Load Test - Integration Partners',
                'url_pattern': 'api_stocks',
                'concurrent_users': 50,
                'duration_minutes': 2,
                'request_interval': 0.5
            },
            {
                'name': 'Cache Status Monitoring',
                'url_pattern': 'cache_status',
                'concurrent_users': 20,
                'duration_minutes': 1,
                'request_interval': 1.0
            },
            {
                'name': 'Extreme Load - Black Friday Event',
                'url_pattern': 'main_page',
                'concurrent_users': 500,
                'duration_minutes': 1,
                'request_interval': 0.3
            }
        ]
        
        results = []
        
        for scenario in test_scenarios:
            try:
                result = await self.test_scenario(**scenario)
                results.append(result)
                
                # Cool down between tests
                print(f"   💤 Cooling down for 10 seconds...")
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"   ❌ Test failed: {e}")
                results.append({
                    'scenario': scenario['name'],
                    'rating': '❌ FAILED',
                    'error': str(e)
                })
        
        self._display_comprehensive_results(results)
    
    def _display_comprehensive_results(self, results):
        """Display comprehensive test results"""
        test_end_time = datetime.now()
        total_duration = test_end_time - self.test_start_time
        
        print("\n" + "=" * 80)
        print("📊 PRODUCTION RELIABILITY TEST RESULTS")
        print("=" * 80)
        
        # Summary table
        table_data = []
        for result in results:
            if 'error' not in result:
                table_data.append([
                    result['scenario'],
                    f"{result['concurrent_users']} users",
                    f"{result['avg_response_time']:.3f}s",
                    f"{result['p95_response_time']:.3f}s",
                    f"{100 - result['error_rate']:.1f}%",
                    f"{result['throughput_req_sec']:.1f}/s",
                    f"{result['consistency_score']:.1f}%",
                    result['rating']
                ])
            else:
                table_data.append([
                    result['scenario'],
                    "N/A",
                    "FAILED",
                    "FAILED",
                    "0%",
                    "0/s",
                    "0%",
                    result['rating']
                ])
        
        headers = [
            "Test Scenario",
            "Load",
            "Avg Response",
            "P95 Response",
            "Success Rate",
            "Throughput",
            "Data Quality",
            "Rating"
        ]
        
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Detailed analysis
        print(f"\n⏱️  Total test duration: {total_duration}")
        
        successful_tests = [r for r in results if 'error' not in r and 'EXCELLENT' in r.get('rating', '') or 'GOOD' in r.get('rating', '')]
        acceptable_tests = [r for r in results if 'ACCEPTABLE' in r.get('rating', '')]
        failed_tests = [r for r in results if 'POOR' in r.get('rating', '') or 'FAILED' in r.get('rating', '')]
        
        print(f"\n📈 TEST SUMMARY:")
        print(f"   ✅ Excellent/Good: {len(successful_tests)}/{len(results)} tests")
        print(f"   ⚠️  Acceptable: {len(acceptable_tests)}/{len(results)} tests")
        print(f"   ❌ Poor/Failed: {len(failed_tests)}/{len(results)} tests")
        
        # Performance insights
        valid_results = [r for r in results if 'error' not in r]
        if valid_results:
            avg_response_times = [r['avg_response_time'] for r in valid_results]
            avg_throughput = [r['throughput_req_sec'] for r in valid_results]
            avg_consistency = [r['consistency_score'] for r in valid_results]
            
            print(f"\n📊 PERFORMANCE INSIGHTS:")
            print(f"   ⚡ Average response time: {statistics.mean(avg_response_times):.3f}s")
            print(f"   🚀 Peak throughput: {max(avg_throughput):.1f} requests/second")
            print(f"   📈 Average data consistency: {statistics.mean(avg_consistency):.1f}%")
        
        # Reliability assessment
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        
        if len(failed_tests) == 0 and len(successful_tests) >= len(results) * 0.8:
            print(f"   🌟 PRODUCTION READY: Excellent performance under all test conditions")
        elif len(failed_tests) <= 1 and len(successful_tests) >= len(results) * 0.6:
            print(f"   ✅ PRODUCTION READY: Good performance with minor optimization opportunities")
        elif len(failed_tests) <= 2:
            print(f"   ⚠️  NEEDS OPTIMIZATION: Acceptable performance but requires improvements")
        else:
            print(f"   ❌ NOT PRODUCTION READY: Significant performance issues detected")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        
        if any(r.get('avg_response_time', 0) > 1.0 for r in valid_results):
            print(f"   🐌 Optimize response times - consider caching improvements")
        
        if any(r.get('error_rate', 0) > 5 for r in valid_results):
            print(f"   🛡️  Improve error handling and rate limiting")
        
        if any(r.get('consistency_score', 100) < 90 for r in valid_results):
            print(f"   📊 Enhance data consistency and validation")
        
        max_successful_load = max([r['concurrent_users'] for r in successful_tests], default=0)
        print(f"   👥 Current capacity: ~{max_successful_load} concurrent users")
        print(f"   🔧 For higher loads, consider horizontal scaling")

async def main():
    """Run the production reliability test suite"""
    tester = ProductionReliabilityTests()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main()) 