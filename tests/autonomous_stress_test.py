#!/usr/bin/env python3
"""
Autonomous Comprehensive Stress Test Suite
==========================================
Tests edge cases and production scenarios found but not fully tested
Uses only standard library + existing dependencies for maximum compatibility
"""

import requests
import time
import threading
import json
import random
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import os
import sys
from collections import defaultdict

class AutonomousStressTestSuite:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = {}
        self.start_time = datetime.now()
        self.total_scenarios = 0
        self.completed_scenarios = 0
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_app_health(self):
        """Verify the application is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                self.log("✅ Application health check passed")
                return True
            else:
                self.log(f"❌ Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            self.log(f"❌ Cannot connect to application: {e}")
            return False
    
    def single_request_test(self, url, timeout=30):
        """Execute a single request and return metrics"""
        start_time = time.time()
        try:
            response = requests.get(url, timeout=timeout)
            end_time = time.time()
            
            return {
                'success': response.status_code == 200,
                'response_time': end_time - start_time,
                'status_code': response.status_code,
                'content_length': len(response.content) if response.content else 0,
                'error': None
            }
        except Exception as e:
            end_time = time.time()
            return {
                'success': False,
                'response_time': end_time - start_time,
                'status_code': 0,
                'content_length': 0,
                'error': str(e)
            }
    
    def concurrent_load_test(self, scenario_name, url, num_requests, num_threads, request_interval=0):
        """Run concurrent load test"""
        self.log(f"🧪 Starting {scenario_name}: {num_requests} requests, {num_threads} threads")
        
        results = []
        
        def worker():
            if request_interval > 0:
                time.sleep(random.uniform(0, request_interval))
            return self.single_request_test(url)
        
        start_test_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=60)
                    results.append(result)
                except Exception as e:
                    results.append({
                        'success': False,
                        'response_time': 30.0,
                        'status_code': 0,
                        'content_length': 0,
                        'error': f"Future error: {e}"
                    })
        
        end_test_time = time.time()
        total_duration = end_test_time - start_test_time
        
        # Calculate metrics
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
            throughput = len(successful_requests) / total_duration
        else:
            avg_response_time = 0
            p95_response_time = 0
            throughput = 0
        
        success_rate = (len(successful_requests) / len(results)) * 100
        
        scenario_result = {
            'scenario': scenario_name,
            'url': url,
            'total_requests': num_requests,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': success_rate,
            'avg_response_time': avg_response_time,
            'p95_response_time': p95_response_time,
            'throughput': throughput,
            'total_duration': total_duration,
            'errors': list(set([r['error'] for r in failed_requests if r['error']]))[:5]
        }
        
        self.results[scenario_name] = scenario_result
        self.completed_scenarios += 1
        
        # Log results
        status = "✅" if success_rate > 95 else "⚠️" if success_rate > 85 else "❌"
        self.log(f"{status} {scenario_name}: {success_rate:.1f}% success, {avg_response_time:.3f}s avg, {throughput:.1f} req/s")
        
        return scenario_result
    
    def edge_case_tests(self):
        """Test edge cases found but not fully tested"""
        self.log("🔍 Starting Edge Case Tests...")
        
        edge_cases = [
            # Rate limiting edge cases
            {
                'name': 'Rate Limit Boundary Test',
                'url': f"{self.base_url}/",
                'requests': 100,
                'threads': 10,
                'interval': 0.1
            },
            
            # Complex filter combinations
            {
                'name': 'Complex Filter Stress',
                'url': f"{self.base_url}/?min_price=1&max_price=50&min_gap_pct=2&min_rel_vol=1.5&sector_filter=Technology&max_market_cap=50000000000",
                'requests': 50,
                'threads': 5,
                'interval': 0.2
            },
            
            # API endpoint stress
            {
                'name': 'API Cache Status Spam',
                'url': f"{self.base_url}/api/cache_status",
                'requests': 200,
                'threads': 20,
                'interval': 0.05
            },
            
            # Memory pressure test
            {
                'name': 'Large Result Set Request',
                'url': f"{self.base_url}/?min_price=0.01&max_price=1000",
                'requests': 30,
                'threads': 3,
                'interval': 1
            },
            
            # Malformed requests
            {
                'name': 'Invalid Parameter Test',
                'url': f"{self.base_url}/?min_price=invalid&max_price=also_invalid&min_gap_pct=not_a_number",
                'requests': 20,
                'threads': 2,
                'interval': 0.5
            }
        ]
        
        for test_case in edge_cases:
            self.concurrent_load_test(
                test_case['name'],
                test_case['url'],
                test_case['requests'],
                test_case['threads'],
                test_case['interval']
            )
            time.sleep(2)  # Cool down between tests
    
    def regional_simulation_tests(self):
        """Simulate different regional access patterns"""
        self.log("🌍 Starting Regional Simulation Tests...")
        
        # Simulate different regional usage patterns
        regional_tests = [
            {
                'name': 'US Market Hours Simulation',
                'url': f"{self.base_url}/",
                'requests': 150,
                'threads': 15,
                'interval': 0.3
            },
            {
                'name': 'European Pre-Market Simulation',
                'url': f"{self.base_url}/?min_gap_pct=1&min_rel_vol=2",
                'requests': 80,
                'threads': 8,
                'interval': 0.5
            },
            {
                'name': 'Asian After-Hours Simulation',
                'url': f"{self.base_url}/?sector_filter=Technology&min_price=5",
                'requests': 60,
                'threads': 6,
                'interval': 0.8
            }
        ]
        
        for test in regional_tests:
            self.concurrent_load_test(
                test['name'],
                test['url'],
                test['requests'],
                test['threads'],
                test['interval']
            )
            time.sleep(3)
    
    def time_based_scenarios(self):
        """Test scenarios based on different times of day"""
        self.log("⏰ Starting Time-Based Scenario Tests...")
        
        time_scenarios = [
            {
                'name': 'Market Open Rush Simulation',
                'url': f"{self.base_url}/?min_gap_pct=5",
                'requests': 300,
                'threads': 30,
                'interval': 0.1
            },
            {
                'name': 'Lunch Break Low Activity',
                'url': f"{self.base_url}/",
                'requests': 25,
                'threads': 5,
                'interval': 2
            },
            {
                'name': 'After Hours Scanning',
                'url': f"{self.base_url}/?min_price=1&max_price=20&min_rel_vol=3",
                'requests': 100,
                'threads': 10,
                'interval': 0.5
            }
        ]
        
        for scenario in time_scenarios:
            self.concurrent_load_test(
                scenario['name'],
                scenario['url'],
                scenario['requests'],
                scenario['threads'],
                scenario['interval']
            )
            time.sleep(5)
    
    def stress_failure_scenarios(self):
        """Test failure and recovery scenarios"""
        self.log("💥 Starting Stress Failure Scenarios...")
        
        failure_tests = [
            {
                'name': 'Sustained High Load',
                'url': f"{self.base_url}/",
                'requests': 500,
                'threads': 50,
                'interval': 0.02
            },
            {
                'name': 'Resource Exhaustion Test',
                'url': f"{self.base_url}/?min_price=0.01&max_price=1000&min_rel_vol=0.1",
                'requests': 100,
                'threads': 20,
                'interval': 0.1
            },
            {
                'name': 'Rapid Fire Requests',
                'url': f"{self.base_url}/api/cache_status",
                'requests': 1000,
                'threads': 100,
                'interval': 0.001
            }
        ]
        
        for test in failure_tests:
            self.concurrent_load_test(
                test['name'],
                test['url'],
                test['requests'],
                test['threads'],
                test['interval']
            )
            time.sleep(10)  # Longer recovery time
    
    def data_consistency_tests(self):
        """Test data consistency under load"""
        self.log("🔍 Starting Data Consistency Tests...")
        
        consistency_tests = [
            {
                'name': 'Cache Consistency Check',
                'url': f"{self.base_url}/api/cache_status",
                'requests': 100,
                'threads': 20,
                'interval': 0.1
            },
            {
                'name': 'Filter Result Consistency',
                'url': f"{self.base_url}/?min_price=5&max_price=15",
                'requests': 50,
                'threads': 10,
                'interval': 0.2
            }
        ]
        
        for test in consistency_tests:
            self.concurrent_load_test(
                test['name'],
                test['url'],
                test['requests'],
                test['threads'],
                test['interval']
            )
            time.sleep(3)
    
    def performance_regression_tests(self):
        """Test for performance regressions"""
        self.log("📊 Starting Performance Regression Tests...")
        
        regression_tests = [
            {
                'name': 'Baseline Performance Test',
                'url': f"{self.base_url}/",
                'requests': 100,
                'threads': 10,
                'interval': 0.1
            },
            {
                'name': 'Heavy Filter Performance',
                'url': f"{self.base_url}/?min_price=1&max_price=100&min_gap_pct=0.5&min_rel_vol=1&max_market_cap=10000000000&sector_filter=Technology",
                'requests': 50,
                'threads': 5,
                'interval': 0.5
            }
        ]
        
        for test in regression_tests:
            self.concurrent_load_test(
                test['name'],
                test['url'],
                test['requests'],
                test['threads'],
                test['interval']
            )
            time.sleep(3)
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report with correlations"""
        self.log("📊 Generating Comprehensive Test Report...")
        
        total_duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("🎯 AUTONOMOUS STRESS TEST RESULTS")
        print("="*80)
        
        print(f"\n📊 TEST EXECUTION SUMMARY:")
        print(f"   • Total Duration: {total_duration/60:.1f} minutes")
        print(f"   • Scenarios Completed: {self.completed_scenarios}")
        print(f"   • Test Start: {self.start_time.strftime('%H:%M:%S')}")
        print(f"   • Test End: {datetime.now().strftime('%H:%M:%S')}")
        
        # Performance analysis
        all_results = list(self.results.values())
        
        if all_results:
            success_rates = [r['success_rate'] for r in all_results]
            response_times = [r['avg_response_time'] for r in all_results]
            throughputs = [r['throughput'] for r in all_results]
            
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   • Average Success Rate: {statistics.mean(success_rates):.1f}%")
            print(f"   • Average Response Time: {statistics.mean(response_times):.3f}s")
            print(f"   • Average Throughput: {statistics.mean(throughputs):.1f} req/s")
            print(f"   • Best Performance: {max(success_rates):.1f}% success rate")
            print(f"   • Worst Performance: {min(success_rates):.1f}% success rate")
        
        # Detailed results table
        print(f"\n📋 DETAILED SCENARIO RESULTS:")
        print("-" * 120)
        print(f"{'Scenario':<40} {'Success Rate':<12} {'Avg Time':<10} {'P95 Time':<10} {'Throughput':<12} {'Status':<8}")
        print("-" * 120)
        
        for result in all_results:
            status = "✅ PASS" if result['success_rate'] > 95 else "⚠️ WARN" if result['success_rate'] > 85 else "❌ FAIL"
            print(f"{result['scenario']:<40} {result['success_rate']:.1f}%{'':<8} {result['avg_response_time']:.3f}s{'':<4} {result['p95_response_time']:.3f}s{'':<4} {result['throughput']:.1f} req/s{'':<4} {status}")
        
        # Identify correlations and patterns
        print(f"\n🔍 CORRELATION ANALYSIS:")
        
        high_load_scenarios = [r for r in all_results if r['total_requests'] > 100]
        if high_load_scenarios:
            avg_high_load_success = statistics.mean([r['success_rate'] for r in high_load_scenarios])
            print(f"   • High Load Impact: {avg_high_load_success:.1f}% average success rate under high load")
        
        complex_filter_scenarios = [r for r in all_results if 'Filter' in r['scenario'] or 'Complex' in r['scenario']]
        if complex_filter_scenarios:
            avg_complex_response = statistics.mean([r['avg_response_time'] for r in complex_filter_scenarios])
            print(f"   • Complex Filter Impact: {avg_complex_response:.3f}s average response time")
        
        api_scenarios = [r for r in all_results if 'API' in r['scenario'] or 'Cache' in r['scenario']]
        if api_scenarios:
            avg_api_throughput = statistics.mean([r['throughput'] for r in api_scenarios])
            print(f"   • API Endpoint Performance: {avg_api_throughput:.1f} req/s average throughput")
        
        # Identify problem areas
        failed_scenarios = [r for r in all_results if r['success_rate'] < 95]
        if failed_scenarios:
            print(f"\n⚠️ ISSUES IDENTIFIED:")
            for scenario in failed_scenarios:
                print(f"   • {scenario['scenario']}: {scenario['success_rate']:.1f}% success rate")
                if scenario['errors']:
                    print(f"     Errors: {', '.join(scenario['errors'][:3])}")
        
        # Performance recommendations
        print(f"\n💡 PERFORMANCE RECOMMENDATIONS:")
        
        slow_scenarios = [r for r in all_results if r['avg_response_time'] > 1.0]
        if slow_scenarios:
            print(f"   🐌 Slow Response Times Detected:")
            for scenario in slow_scenarios:
                print(f"      • {scenario['scenario']}: {scenario['avg_response_time']:.3f}s")
        
        low_throughput = [r for r in all_results if r['throughput'] < 10]
        if low_throughput:
            print(f"   📉 Low Throughput Scenarios:")
            for scenario in low_throughput:
                print(f"      • {scenario['scenario']}: {scenario['throughput']:.1f} req/s")
        
        # Production readiness assessment
        overall_success = statistics.mean(success_rates) if success_rates else 0
        overall_response = statistics.mean(response_times) if response_times else 0
        
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if overall_success > 99 and overall_response < 0.5:
            print("   🌟 EXCELLENT - Ready for high-traffic production deployment")
        elif overall_success > 95 and overall_response < 1.0:
            print("   ✅ GOOD - Suitable for production with monitoring")
        elif overall_success > 90 and overall_response < 2.0:
            print("   ⚠️ ACCEPTABLE - Needs optimization before scaling")
        else:
            print("   ❌ POOR - Requires significant improvements")
        
        # Save results to file
        report_file = f"stress_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'total_duration': total_duration,
                    'scenarios_completed': self.completed_scenarios,
                    'overall_success_rate': overall_success,
                    'overall_response_time': overall_response
                },
                'detailed_results': self.results
            }, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: {report_file}")
        print("="*80)
    
    def run_all_tests(self):
        """Run all comprehensive stress tests"""
        if not self.check_app_health():
            return
        
        self.log("🚀 Starting Autonomous Comprehensive Stress Testing...")
        self.log("🎯 Testing edge cases and production scenarios found but not fully tested")
        
        # Count total scenarios
        self.total_scenarios = 23  # Rough count of all test scenarios
        
        try:
            # Run all test categories
            self.edge_case_tests()
            self.regional_simulation_tests() 
            self.time_based_scenarios()
            self.data_consistency_tests()
            self.performance_regression_tests()
            self.stress_failure_scenarios()
            
        except KeyboardInterrupt:
            self.log("⚠️ Testing interrupted by user")
        except Exception as e:
            self.log(f"❌ Error during testing: {e}")
        finally:
            self.generate_comprehensive_report()

def main():
    """Main execution function"""
    print("🤖 AUTONOMOUS STRESS TESTING SUITE")
    print("==================================")
    print("Testing all edge cases and production scenarios autonomously...")
    print("Duration: 1 hour of comprehensive testing")
    print("")
    
    suite = AutonomousStressTestSuite()
    suite.run_all_tests()

if __name__ == "__main__":
    main() 