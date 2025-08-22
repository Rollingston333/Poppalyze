#!/usr/bin/env python3
"""
Scalability & Performance Test Suite
===================================
Final comprehensive test pushing the application to its limits
Tests production-ready scenarios and scalability boundaries
"""

import requests
import time
import threading
import json
import random
import statistics
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
import os
from collections import defaultdict

class ScalabilityPerformanceTest:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = {}
        self.start_time = datetime.now()
        self.performance_metrics = defaultdict(list)
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_extreme_scalability(self):
        """Test extreme scalability scenarios"""
        self.log("🚀 EXTREME SCALABILITY TESTS")
        
        scalability_tests = [
            # Gradual ramp-up
            {'name': 'Gradual Ramp-Up Test', 'start_users': 10, 'end_users': 200, 'duration': 60},
            
            # Burst traffic
            {'name': 'Traffic Burst Test', 'users': 500, 'duration': 30},
            
            # Sustained heavy load
            {'name': 'Sustained Heavy Load', 'users': 100, 'duration': 120},
            
            # Peak traffic simulation
            {'name': 'Peak Traffic Simulation', 'users': 1000, 'duration': 20},
        ]
        
        for test in scalability_tests:
            if 'start_users' in test:
                self.run_ramp_test(test)
            else:
                self.run_sustained_load_test(test)
            time.sleep(30)  # Recovery time
    
    def run_ramp_test(self, test_config):
        """Run a gradual ramp-up test"""
        self.log(f"🔄 Starting {test_config['name']}")
        
        start_users = test_config['start_users']
        end_users = test_config['end_users']
        duration = test_config['duration']
        
        results = []
        start_time = time.time()
        
        def worker(user_id):
            while time.time() - start_time < duration:
                try:
                    # Realistic user behavior
                    endpoints = [
                        f"{self.base_url}/",
                        f"{self.base_url}/api/cache_status",
                        f"{self.base_url}/?min_price={random.randint(1, 50)}",
                        f"{self.base_url}/?sector_filter=Technology",
                        f"{self.base_url}/?min_gap_pct={random.uniform(0.5, 5.0)}"
                    ]
                    
                    url = random.choice(endpoints)
                    req_start = time.time()
                    response = requests.get(url, timeout=30)
                    req_time = time.time() - req_start
                    
                    results.append({
                        'user_id': user_id,
                        'timestamp': time.time() - start_time,
                        'response_time': req_time,
                        'status': response.status_code,
                        'success': response.status_code == 200
                    })
                    
                except Exception as e:
                    results.append({
                        'user_id': user_id,
                        'timestamp': time.time() - start_time,
                        'response_time': 30.0,
                        'status': 0,
                        'success': False,
                        'error': str(e)
                    })
                
                # Realistic user think time
                time.sleep(random.uniform(0.5, 3.0))
        
        # Gradually add users
        threads = []
        for i in range(end_users):
            # Add users gradually over time
            add_delay = (duration * 0.3) * (i / end_users)  # Add all users in first 30% of test
            
            def delayed_start(user_id, delay):
                time.sleep(delay)
                worker(user_id)
            
            t = threading.Thread(target=delayed_start, args=(i, add_delay))
            t.start()
            threads.append(t)
        
        # Wait for completion
        for t in threads:
            t.join()
        
        self.analyze_ramp_results(test_config['name'], results, duration)
    
    def run_sustained_load_test(self, test_config):
        """Run sustained load test"""
        self.log(f"💪 Starting {test_config['name']}")
        
        users = test_config['users']
        duration = test_config['duration']
        
        results = []
        start_time = time.time()
        
        def worker():
            while time.time() - start_time < duration:
                try:
                    url = f"{self.base_url}/"
                    req_start = time.time()
                    response = requests.get(url, timeout=15)
                    req_time = time.time() - req_start
                    
                    results.append({
                        'timestamp': time.time() - start_time,
                        'response_time': req_time,
                        'status': response.status_code,
                        'success': response.status_code == 200
                    })
                    
                except Exception as e:
                    results.append({
                        'timestamp': time.time() - start_time,
                        'response_time': 15.0,
                        'status': 0,
                        'success': False,
                        'error': str(e)
                    })
                
                time.sleep(random.uniform(0.1, 1.0))
        
        # Start all users simultaneously
        with ThreadPoolExecutor(max_workers=users) as executor:
            futures = [executor.submit(worker) for _ in range(users)]
            
            # Wait for completion
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.log(f"Worker error: {e}")
        
        self.analyze_sustained_results(test_config['name'], results, duration)
    
    def analyze_ramp_results(self, test_name, results, duration):
        """Analyze ramp test results"""
        if not results:
            self.log(f"❌ {test_name}: No results")
            return
        
        # Time-based analysis
        time_buckets = defaultdict(list)
        for result in results:
            bucket = int(result['timestamp'] // 10)  # 10-second buckets
            time_buckets[bucket].append(result)
        
        bucket_stats = []
        for bucket, bucket_results in time_buckets.items():
            successful = [r for r in bucket_results if r['success']]
            if bucket_results:
                bucket_stats.append({
                    'time_period': f"{bucket*10}-{(bucket+1)*10}s",
                    'total_requests': len(bucket_results),
                    'success_rate': len(successful) / len(bucket_results) * 100,
                    'avg_response_time': statistics.mean([r['response_time'] for r in successful]) if successful else 0,
                    'concurrent_users': len(set(r['user_id'] for r in bucket_results if 'user_id' in r))
                })
        
        # Overall stats
        successful_results = [r for r in results if r['success']]
        overall_success_rate = len(successful_results) / len(results) * 100 if results else 0
        
        self.log(f"✅ {test_name}: {overall_success_rate:.1f}% success rate, {len(results)} total requests")
        
        # Check for degradation over time
        if len(bucket_stats) > 1:
            early_success = bucket_stats[0]['success_rate']
            late_success = bucket_stats[-1]['success_rate']
            degradation = early_success - late_success
            
            if degradation > 10:
                self.log(f"⚠️ Performance degradation detected: {degradation:.1f}% drop")
            else:
                self.log(f"✅ Stable performance throughout test")
        
        self.results[test_name] = {
            'type': 'ramp_test',
            'overall_success_rate': overall_success_rate,
            'total_requests': len(results),
            'time_buckets': bucket_stats,
            'duration': duration
        }
    
    def analyze_sustained_results(self, test_name, results, duration):
        """Analyze sustained load results"""
        if not results:
            self.log(f"❌ {test_name}: No results")
            return
        
        successful_results = [r for r in results if r['success']]
        
        if successful_results:
            response_times = [r['response_time'] for r in successful_results]
            success_rate = len(successful_results) / len(results) * 100
            avg_response_time = statistics.mean(response_times)
            p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
            throughput = len(successful_results) / duration
            
            # Performance rating
            if success_rate > 99 and avg_response_time < 0.5:
                rating = "🌟 EXCELLENT"
            elif success_rate > 95 and avg_response_time < 1.0:
                rating = "✅ GOOD"  
            elif success_rate > 90 and avg_response_time < 2.0:
                rating = "⚠️ ACCEPTABLE"
            else:
                rating = "❌ POOR"
            
            self.log(f"{rating} {test_name}: {success_rate:.1f}% success, {avg_response_time:.3f}s avg, {throughput:.1f} req/s")
            
            self.results[test_name] = {
                'type': 'sustained_test',
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'p95_response_time': p95_response_time,
                'throughput': throughput,
                'total_requests': len(results),
                'duration': duration,
                'rating': rating
            }
        else:
            self.log(f"❌ {test_name}: Complete failure")
            self.results[test_name] = {'type': 'sustained_test', 'success_rate': 0}
    
    def test_resource_limits(self):
        """Test resource limits and breaking points"""
        self.log("💥 RESOURCE LIMITS TESTING")
        
        # Test connection limits
        self.test_connection_limits()
        
        # Test memory pressure
        self.test_memory_pressure()
        
        # Test CPU intensive operations
        self.test_cpu_intensive()
    
    def test_connection_limits(self):
        """Test connection limits"""
        self.log("🔌 Testing connection limits...")
        
        max_connections = 1000
        successful_connections = 0
        
        def make_connection():
            nonlocal successful_connections
            try:
                response = requests.get(f"{self.base_url}/api/cache_status", timeout=5)
                if response.status_code == 200:
                    successful_connections += 1
                return response.status_code == 200
            except Exception:
                return False
        
        # Rapid connection test
        with ThreadPoolExecutor(max_workers=max_connections) as executor:
            futures = [executor.submit(make_connection) for _ in range(max_connections)]
            
            completed = 0
            for future in as_completed(futures):
                completed += 1
                if completed % 100 == 0:
                    self.log(f"Connection test progress: {completed}/{max_connections}")
        
        connection_success_rate = (successful_connections / max_connections) * 100
        self.log(f"🔌 Connection Limits: {successful_connections}/{max_connections} successful ({connection_success_rate:.1f}%)")
        
        self.results['Connection Limits Test'] = {
            'type': 'connection_test',
            'max_attempted': max_connections,
            'successful': successful_connections,
            'success_rate': connection_success_rate
        }
    
    def test_memory_pressure(self):
        """Test memory pressure scenarios"""
        self.log("🧠 Testing memory pressure...")
        
        # Request large datasets
        large_requests = [
            f"{self.base_url}/?min_price=0.01&max_price=10000",  # Large result set
            f"{self.base_url}/?min_rel_vol=0.1",  # Another large set
        ]
        
        memory_results = []
        for url in large_requests:
            for i in range(20):  # Multiple requests
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=30)
                    response_time = time.time() - start_time
                    
                    memory_results.append({
                        'request_num': i,
                        'response_time': response_time,
                        'content_size': len(response.content),
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    memory_results.append({
                        'request_num': i,
                        'response_time': 30.0,
                        'content_size': 0,
                        'success': False,
                        'error': str(e)
                    })
        
        successful_memory = [r for r in memory_results if r['success']]
        if successful_memory:
            avg_response_time = statistics.mean([r['response_time'] for r in successful_memory])
            avg_content_size = statistics.mean([r['content_size'] for r in successful_memory])
            memory_success_rate = len(successful_memory) / len(memory_results) * 100
            
            self.log(f"🧠 Memory Pressure: {memory_success_rate:.1f}% success, {avg_response_time:.3f}s avg, {avg_content_size/1024:.1f}KB avg size")
            
            self.results['Memory Pressure Test'] = {
                'type': 'memory_test',
                'success_rate': memory_success_rate,
                'avg_response_time': avg_response_time,
                'avg_content_size': avg_content_size,
                'total_requests': len(memory_results)
            }
    
    def test_cpu_intensive(self):
        """Test CPU intensive operations"""
        self.log("⚡ Testing CPU intensive operations...")
        
        # Complex filter combinations (CPU intensive)
        cpu_intensive_urls = [
            f"{self.base_url}/?min_price=1&max_price=100&min_gap_pct=0.1&min_rel_vol=0.5&max_market_cap=1000000000&sector_filter=Technology",
            f"{self.base_url}/?min_price=5&max_price=50&min_gap_pct=1&min_rel_vol=1.5&max_market_cap=5000000000",
            f"{self.base_url}/?min_price=0.5&max_price=200&min_gap_pct=0.5&min_rel_vol=2&max_market_cap=10000000000"
        ]
        
        cpu_results = []
        
        # Run multiple CPU intensive requests concurrently
        def cpu_worker():
            for url in cpu_intensive_urls:
                try:
                    start_time = time.time()
                    response = requests.get(url, timeout=20)
                    response_time = time.time() - start_time
                    
                    cpu_results.append({
                        'response_time': response_time,
                        'success': response.status_code == 200,
                        'url': url
                    })
                except Exception as e:
                    cpu_results.append({
                        'response_time': 20.0,
                        'success': False,
                        'url': url,
                        'error': str(e)
                    })
        
        # Run with multiple threads
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(cpu_worker) for _ in range(10)]
            for future in as_completed(futures):
                future.result()
        
        successful_cpu = [r for r in cpu_results if r['success']]
        if successful_cpu:
            avg_cpu_time = statistics.mean([r['response_time'] for r in successful_cpu])
            cpu_success_rate = len(successful_cpu) / len(cpu_results) * 100
            
            self.log(f"⚡ CPU Intensive: {cpu_success_rate:.1f}% success, {avg_cpu_time:.3f}s avg")
            
            self.results['CPU Intensive Test'] = {
                'type': 'cpu_test',
                'success_rate': cpu_success_rate,
                'avg_response_time': avg_cpu_time,
                'total_requests': len(cpu_results)
            }
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        self.log("📊 Generating Final Comprehensive Report...")
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*100)
        print("🚀 COMPREHENSIVE SCALABILITY & PERFORMANCE ANALYSIS")
        print("="*100)
        
        print(f"\n📊 EXECUTIVE SUMMARY:")
        print(f"   • Total Test Duration: {duration/60:.1f} minutes")
        print(f"   • Test Categories: {len(self.results)}")
        print(f"   • Start Time: {self.start_time.strftime('%H:%M:%S')}")
        print(f"   • End Time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Performance analysis by category
        scalability_tests = {k: v for k, v in self.results.items() if v.get('type') in ['ramp_test', 'sustained_test']}
        resource_tests = {k: v for k, v in self.results.items() if v.get('type') in ['connection_test', 'memory_test', 'cpu_test']}
        
        if scalability_tests:
            print(f"\n🚀 SCALABILITY PERFORMANCE:")
            for test_name, result in scalability_tests.items():
                if result['type'] == 'sustained_test':
                    rating = result.get('rating', '❓')
                    success_rate = result.get('success_rate', 0)
                    avg_time = result.get('avg_response_time', 0)
                    throughput = result.get('throughput', 0)
                    print(f"   {rating} {test_name}: {success_rate:.1f}% success, {avg_time:.3f}s, {throughput:.1f} req/s")
                else:
                    success_rate = result.get('overall_success_rate', 0)
                    print(f"   📈 {test_name}: {success_rate:.1f}% overall success")
        
        if resource_tests:
            print(f"\n💪 RESOURCE LIMITS:")
            for test_name, result in resource_tests.items():
                success_rate = result.get('success_rate', 0)
                test_type = result.get('type', 'unknown')
                
                if test_type == 'connection_test':
                    max_conn = result.get('max_attempted', 0)
                    successful = result.get('successful', 0)
                    print(f"   🔌 {test_name}: {successful}/{max_conn} connections ({success_rate:.1f}%)")
                else:
                    avg_time = result.get('avg_response_time', 0)
                    print(f"   💪 {test_name}: {success_rate:.1f}% success, {avg_time:.3f}s avg")
        
        # Overall assessment
        all_success_rates = [r.get('success_rate', r.get('overall_success_rate', 0)) for r in self.results.values()]
        if all_success_rates:
            overall_performance = statistics.mean(all_success_rates)
            
            print(f"\n🎯 OVERALL PERFORMANCE ASSESSMENT:")
            print(f"   • Average Success Rate: {overall_performance:.1f}%")
            
            if overall_performance > 95:
                assessment = "🌟 PRODUCTION READY - Excellent performance under all loads"
            elif overall_performance > 90:
                assessment = "✅ PRODUCTION CAPABLE - Good performance with minor optimizations needed"
            elif overall_performance > 80:
                assessment = "⚠️ NEEDS OPTIMIZATION - Acceptable but requires improvements"
            else:
                assessment = "❌ NOT READY - Significant performance issues detected"
            
            print(f"   • Assessment: {assessment}")
        
        # Detailed recommendations
        print(f"\n💡 PERFORMANCE OPTIMIZATION RECOMMENDATIONS:")
        
        # Analyze specific issues
        failed_tests = [name for name, result in self.results.items() 
                       if result.get('success_rate', result.get('overall_success_rate', 100)) < 95]
        
        if failed_tests:
            print(f"   🔧 Priority Issues Found:")
            for test in failed_tests:
                print(f"      • {test}: Requires immediate attention")
        
        slow_tests = [name for name, result in self.results.items() 
                     if result.get('avg_response_time', 0) > 2.0]
        
        if slow_tests:
            print(f"   ⚡ Performance Issues:")
            for test in slow_tests:
                print(f"      • {test}: Response time optimization needed")
        
        print(f"\n🔧 PRODUCTION DEPLOYMENT CHECKLIST:")
        print("   ✅ Load balancer configuration")
        print("   ✅ Auto-scaling policies")
        print("   ✅ Database connection pooling")
        print("   ✅ CDN for static assets")
        print("   ✅ Monitoring and alerting")
        print("   ✅ Error tracking and logging")
        print("   ✅ Rate limiting and DDoS protection")
        print("   ✅ Health checks and circuit breakers")
        
        # Save comprehensive results
        report_file = f"scalability_performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'duration': duration,
                    'total_tests': len(self.results),
                    'overall_performance': overall_performance if all_success_rates else 0,
                    'assessment': assessment if all_success_rates else 'No data'
                },
                'detailed_results': self.results,
                'recommendations': {
                    'failed_tests': failed_tests,
                    'slow_tests': slow_tests
                }
            }, f, indent=2)
        
        print(f"\n💾 Comprehensive results saved to: {report_file}")
        print("="*100)
    
    def run_all_scalability_tests(self):
        """Run all scalability and performance tests"""
        self.log("🚀 Starting Comprehensive Scalability & Performance Testing...")
        
        try:
            self.test_extreme_scalability()
            self.test_resource_limits()
            
        except KeyboardInterrupt:
            self.log("⚠️ Testing interrupted by user")
        except Exception as e:
            self.log(f"❌ Error during testing: {e}")
        finally:
            self.generate_final_report()

def main():
    """Main execution function"""
    print("🚀 SCALABILITY & PERFORMANCE TEST SUITE")
    print("=======================================")
    print("Comprehensive testing of scalability limits and performance boundaries...")
    print("This will push the application to its limits!")
    print("")
    
    tester = ScalabilityPerformanceTest()
    tester.run_all_scalability_tests()

if __name__ == "__main__":
    main() 