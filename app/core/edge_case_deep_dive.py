#!/usr/bin/env python3
"""
Edge Case Deep Dive Test Suite
==============================
Deep analysis of edge cases found but not fully tested
Focus on error handling, boundary conditions, and advanced scenarios
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
from collections import defaultdict

class EdgeCaseDeepDive:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = {}
        self.start_time = datetime.now()
        self.error_patterns = defaultdict(int)
        
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def analyze_error_handling(self):
        """Deep dive into error handling scenarios"""
        self.log("🔍 DEEP DIVE: Error Handling Analysis")
        
        error_scenarios = [
            # SQL injection attempts
            {
                'name': 'SQL Injection Test',
                'url': f"{self.base_url}/?min_price=' OR 1=1 --&max_price='; DROP TABLE stocks; --",
                'expected': 'error_handled'
            },
            
            # XSS attempts
            {
                'name': 'XSS Test',
                'url': f"{self.base_url}/?sector_filter=<script>alert('xss')</script>",
                'expected': 'error_handled'
            },
            
            # Buffer overflow attempts
            {
                'name': 'Buffer Overflow Test',
                'url': f"{self.base_url}/?min_price={'A' * 10000}",
                'expected': 'error_handled'
            },
            
            # Negative boundary tests
            {
                'name': 'Negative Values Test',
                'url': f"{self.base_url}/?min_price=-999999&max_price=-1&min_gap_pct=-100",
                'expected': 'handled_gracefully'
            },
            
            # Zero division potential
            {
                'name': 'Zero Division Test',
                'url': f"{self.base_url}/?min_price=0&max_price=0&min_rel_vol=0",
                'expected': 'handled_gracefully'
            },
            
            # Unicode/encoding tests
            {
                'name': 'Unicode Test',
                'url': f"{self.base_url}/?sector_filter=🚀💰📈💎🌙",
                'expected': 'handled_gracefully'
            },
            
            # Path traversal
            {
                'name': 'Path Traversal Test',
                'url': f"{self.base_url}/../../../etc/passwd",
                'expected': 'blocked'
            }
        ]
        
        for scenario in error_scenarios:
            self.test_error_scenario(scenario)
            time.sleep(1)
    
    def test_error_scenario(self, scenario):
        """Test individual error scenario"""
        try:
            response = requests.get(scenario['url'], timeout=10)
            
            result = {
                'scenario': scenario['name'],
                'status_code': response.status_code,
                'response_size': len(response.content),
                'response_time': response.elapsed.total_seconds(),
                'contains_error_page': 'error' in response.text.lower() or 'exception' in response.text.lower(),
                'contains_traceback': 'traceback' in response.text.lower() or 'line ' in response.text.lower(),
                'security_headers': {
                    'x_frame_options': response.headers.get('X-Frame-Options'),
                    'x_content_type_options': response.headers.get('X-Content-Type-Options'),
                    'x_xss_protection': response.headers.get('X-XSS-Protection')
                }
            }
            
            # Analyze response
            if result['contains_traceback']:
                status = "❌ CRITICAL - Traceback exposed"
            elif result['status_code'] in [400, 422, 500] and result['contains_error_page']:
                status = "✅ GOOD - Error handled properly"
            elif result['status_code'] == 200:
                status = "⚠️ WARNING - Request succeeded (may be vulnerable)"
            else:
                status = "🤔 UNKNOWN - Needs investigation"
            
            self.log(f"{status} {scenario['name']}: {result['status_code']} ({result['response_time']:.3f}s)")
            
            self.results[scenario['name']] = result
            
        except Exception as e:
            self.log(f"❌ {scenario['name']}: Exception - {str(e)}")
            self.results[scenario['name']] = {'error': str(e)}
    
    def test_boundary_conditions(self):
        """Test mathematical and logical boundary conditions"""
        self.log("🔢 DEEP DIVE: Boundary Conditions")
        
        boundaries = [
            # Extreme numeric values
            {'name': 'Max Integer Test', 'url': f"{self.base_url}/?min_price={sys.maxsize}"},
            {'name': 'Min Integer Test', 'url': f"{self.base_url}/?min_price={-sys.maxsize}"},
            {'name': 'Float Precision Test', 'url': f"{self.base_url}/?min_price=0.000000001&max_price=0.000000002"},
            {'name': 'Scientific Notation Test', 'url': f"{self.base_url}/?min_price=1e-10&max_price=1e10"},
            
            # Logic boundary tests
            {'name': 'Inverted Range Test', 'url': f"{self.base_url}/?min_price=100&max_price=1"},
            {'name': 'Equal Boundaries Test', 'url': f"{self.base_url}/?min_price=50&max_price=50"},
            
            # Empty and null tests
            {'name': 'Empty String Test', 'url': f"{self.base_url}/?min_price=&max_price=&sector_filter="},
            {'name': 'Null Test', 'url': f"{self.base_url}/?min_price=null&max_price=null"},
            
            # Special float values
            {'name': 'Infinity Test', 'url': f"{self.base_url}/?min_price=inf&max_price=inf"},
            {'name': 'NaN Test', 'url': f"{self.base_url}/?min_price=nan&max_price=nan"},
        ]
        
        for boundary in boundaries:
            self.test_single_boundary(boundary)
    
    def test_single_boundary(self, boundary):
        """Test single boundary condition"""
        try:
            start_time = time.time()
            response = requests.get(boundary['url'], timeout=15)
            response_time = time.time() - start_time
            
            # Check if app crashed or hung
            if response_time > 10:
                status = "⚠️ SLOW - Potential performance issue"
            elif response.status_code == 500:
                status = "❌ ERROR - Server error"
            elif response.status_code == 200:
                status = "✅ HANDLED - Request completed"
            else:
                status = f"🤔 STATUS - {response.status_code}"
            
            self.log(f"{status} {boundary['name']}: {response_time:.3f}s")
            
        except requests.exceptions.Timeout:
            self.log(f"⏰ TIMEOUT {boundary['name']}: Request timed out (>15s)")
        except Exception as e:
            self.log(f"❌ ERROR {boundary['name']}: {str(e)}")
    
    def test_concurrent_edge_cases(self):
        """Test edge cases under concurrent load"""
        self.log("🔄 DEEP DIVE: Concurrent Edge Cases")
        
        concurrent_scenarios = [
            # Mixed valid/invalid requests
            {
                'name': 'Mixed Valid/Invalid Requests',
                'valid_url': f"{self.base_url}/",
                'invalid_url': f"{self.base_url}/?min_price=invalid",
                'threads': 20,
                'duration': 10
            },
            
            # Cache invalidation race conditions
            {
                'name': 'Cache Race Condition Test',
                'url': f"{self.base_url}/api/cache_status",
                'threads': 50,
                'duration': 5
            },
            
            # Memory pressure with large responses
            {
                'name': 'Memory Pressure Test',
                'url': f"{self.base_url}/?min_price=0.01&max_price=10000",
                'threads': 10,
                'duration': 15
            }
        ]
        
        for scenario in concurrent_scenarios:
            self.run_concurrent_scenario(scenario)
    
    def run_concurrent_scenario(self, scenario):
        """Run concurrent scenario test"""
        self.log(f"🔄 Starting {scenario['name']}")
        
        results = []
        start_time = time.time()
        
        def worker():
            while time.time() - start_time < scenario['duration']:
                try:
                    if 'valid_url' in scenario:
                        # Mixed requests
                        url = random.choice([scenario['valid_url'], scenario['invalid_url']])
                    else:
                        url = scenario['url']
                    
                    response = requests.get(url, timeout=5)
                    results.append({
                        'status': response.status_code,
                        'time': time.time() - start_time,
                        'success': response.status_code == 200
                    })
                except Exception as e:
                    results.append({
                        'status': 0,
                        'time': time.time() - start_time,
                        'success': False,
                        'error': str(e)
                    })
                time.sleep(0.1)
        
        # Run concurrent workers
        threads = []
        for _ in range(scenario['threads']):
            t = threading.Thread(target=worker)
            t.start()
            threads.append(t)
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Analyze results
        if results:
            success_rate = sum(1 for r in results if r['success']) / len(results) * 100
            avg_response_time = sum(r.get('time', 0) for r in results) / len(results)
            
            self.log(f"✅ {scenario['name']}: {success_rate:.1f}% success, {len(results)} total requests")
        else:
            self.log(f"❌ {scenario['name']}: No results collected")
    
    def test_api_edge_cases(self):
        """Test API-specific edge cases"""
        self.log("📡 DEEP DIVE: API Edge Cases")
        
        api_tests = [
            # HTTP method tests
            {'name': 'POST Method Test', 'method': 'POST', 'url': f"{self.base_url}/"},
            {'name': 'PUT Method Test', 'method': 'PUT', 'url': f"{self.base_url}/"},
            {'name': 'DELETE Method Test', 'method': 'DELETE', 'url': f"{self.base_url}/"},
            
            # Header tests
            {'name': 'Missing User Agent', 'headers': {}},
            {'name': 'Malformed Accept Header', 'headers': {'Accept': 'invalid/malformed'}},
            {'name': 'Large Header Test', 'headers': {'X-Large-Header': 'A' * 8192}},
            
            # Content type tests
            {'name': 'JSON Content Type', 'headers': {'Content-Type': 'application/json'}},
            {'name': 'XML Content Type', 'headers': {'Content-Type': 'application/xml'}},
        ]
        
        for test in api_tests:
            self.test_api_method(test)
    
    def test_api_method(self, test):
        """Test specific API method or header configuration"""
        try:
            url = test.get('url', f"{self.base_url}/")
            method = test.get('method', 'GET')
            headers = test.get('headers', {'User-Agent': 'StressTest/1.0'})
            
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            status = "✅ HANDLED" if response.status_code in [200, 405, 404] else f"⚠️ {response.status_code}"
            self.log(f"{status} {test['name']}: {response.status_code}")
            
        except Exception as e:
            self.log(f"❌ {test['name']}: {str(e)}")
    
    def test_session_and_state(self):
        """Test session handling and state management"""
        self.log("🔐 DEEP DIVE: Session & State Management")
        
        # Test session persistence
        session = requests.Session()
        
        # Multiple requests in same session
        urls = [
            f"{self.base_url}/",
            f"{self.base_url}/api/cache_status",
            f"{self.base_url}/?min_price=5",
            f"{self.base_url}/?sector_filter=Technology"
        ]
        
        session_results = []
        for i, url in enumerate(urls):
            try:
                response = session.get(url, timeout=10)
                session_results.append({
                    'request_num': i+1,
                    'status': response.status_code,
                    'cookies': len(response.cookies),
                    'session_id': response.cookies.get('session', 'none')
                })
            except Exception as e:
                self.log(f"❌ Session request {i+1}: {str(e)}")
        
        if session_results:
            self.log(f"✅ Session Test: {len(session_results)} requests completed")
            # Check for session consistency
            session_ids = [r['session_id'] for r in session_results]
            if len(set(session_ids)) == 1:
                self.log("✅ Session consistency maintained")
            else:
                self.log("⚠️ Session inconsistency detected")
    
    def analyze_caching_behavior(self):
        """Analyze caching behavior under edge conditions"""
        self.log("💾 DEEP DIVE: Cache Behavior Analysis")
        
        # Test cache consistency
        cache_urls = [
            f"{self.base_url}/api/cache_status",
            f"{self.base_url}/?min_price=1&max_price=10",
            f"{self.base_url}/?min_price=1&max_price=10"  # Same query
        ]
        
        cache_results = []
        for url in cache_urls:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=10)
                response_time = time.time() - start_time
                
                cache_results.append({
                    'url': url,
                    'response_time': response_time,
                    'cache_headers': response.headers.get('X-Cache', 'unknown'),
                    'content_hash': hash(response.text) if response.text else 0
                })
            except Exception as e:
                self.log(f"❌ Cache test error: {str(e)}")
        
        if len(cache_results) >= 3:
            # Check if identical queries return same content
            if cache_results[1]['content_hash'] == cache_results[2]['content_hash']:
                self.log("✅ Cache consistency: Identical queries return same content")
            else:
                self.log("⚠️ Cache inconsistency: Identical queries differ")
            
            # Check response time improvement
            if cache_results[2]['response_time'] < cache_results[1]['response_time']:
                self.log("✅ Cache performance: Second query faster")
            else:
                self.log("📊 Cache performance: No significant speed improvement")
    
    def generate_edge_case_report(self):
        """Generate comprehensive edge case analysis report"""
        self.log("📊 Generating Edge Case Analysis Report...")
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*80)
        print("🔍 EDGE CASE DEEP DIVE ANALYSIS")
        print("="*80)
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   • Analysis Duration: {duration/60:.1f} minutes")
        print(f"   • Tests Completed: {len(self.results)}")
        print(f"   • Start Time: {self.start_time.strftime('%H:%M:%S')}")
        print(f"   • End Time: {datetime.now().strftime('%H:%M:%S')}")
        
        print(f"\n🛡️ SECURITY ANALYSIS:")
        security_issues = []
        
        for test_name, result in self.results.items():
            if isinstance(result, dict):
                if result.get('contains_traceback'):
                    security_issues.append(f"Information disclosure in {test_name}")
                if result.get('status_code') == 200 and 'injection' in test_name.lower():
                    security_issues.append(f"Potential injection vulnerability in {test_name}")
        
        if security_issues:
            for issue in security_issues:
                print(f"   ❌ {issue}")
        else:
            print("   ✅ No critical security issues detected")
        
        print(f"\n🔧 ERROR HANDLING ASSESSMENT:")
        error_handling_good = sum(1 for r in self.results.values() 
                                if isinstance(r, dict) and not r.get('contains_traceback', False))
        total_tests = len([r for r in self.results.values() if isinstance(r, dict)])
        
        if total_tests > 0:
            error_score = (error_handling_good / total_tests) * 100
            print(f"   • Error Handling Score: {error_score:.1f}%")
            
            if error_score > 90:
                print("   ✅ Excellent error handling")
            elif error_score > 75:
                print("   ⚠️ Good error handling with room for improvement")
            else:
                print("   ❌ Poor error handling - needs attention")
        
        print(f"\n💡 RECOMMENDATIONS:")
        print("   🔧 Implement proper input validation for all parameters")
        print("   🛡️ Add security headers (X-Frame-Options, X-Content-Type-Options)")
        print("   📝 Ensure error pages don't expose sensitive information")
        print("   ⚡ Consider implementing rate limiting for invalid requests")
        print("   🔍 Add monitoring for unusual request patterns")
        
        # Save detailed results
        report_file = f"edge_case_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                'summary': {
                    'duration': duration,
                    'tests_completed': len(self.results),
                    'security_issues': security_issues,
                    'error_handling_score': error_score if total_tests > 0 else 0
                },
                'detailed_results': self.results
            }, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: {report_file}")
        print("="*80)
    
    def run_all_edge_tests(self):
        """Run all edge case tests"""
        self.log("🚀 Starting Edge Case Deep Dive Analysis...")
        
        try:
            self.analyze_error_handling()
            self.test_boundary_conditions()
            self.test_concurrent_edge_cases()
            self.test_api_edge_cases()
            self.test_session_and_state()
            self.analyze_caching_behavior()
            
        except KeyboardInterrupt:
            self.log("⚠️ Analysis interrupted by user")
        except Exception as e:
            self.log(f"❌ Error during analysis: {e}")
        finally:
            self.generate_edge_case_report()

def main():
    """Main execution function"""
    print("🔍 EDGE CASE DEEP DIVE ANALYSIS")
    print("===============================")
    print("Deep analysis of edge cases and security vulnerabilities...")
    print("")
    
    analyzer = EdgeCaseDeepDive()
    analyzer.run_all_edge_tests()

if __name__ == "__main__":
    main() 