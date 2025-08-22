#!/usr/bin/env python3
"""
Error Handling Test Suite
========================
Tests all the critical error handling improvements
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class ErrorHandlingTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.results = {}
    
    async def test_input_validation(self):
        """Test input validation with invalid parameters"""
        print("\n🧪 Testing Input Validation...")
        
        test_cases = [
            # Invalid numeric inputs
            {"min_price": "invalid", "name": "Invalid min_price"},
            {"max_price": "not_a_number", "name": "Invalid max_price"}, 
            {"min_rel_vol": "abc", "name": "Invalid min_rel_vol"},
            {"min_gap_pct": "xyz", "name": "Invalid min_gap_pct"},
            
            # Out of range values
            {"min_price": "-10", "name": "Negative min_price"},
            {"max_price": "999999", "name": "Excessive max_price"},
            {"min_rel_vol": "-5", "name": "Negative relative volume"},
            
            # Logical inconsistencies
            {"min_price": "100", "max_price": "50", "name": "Min > Max price"},
            {"min_market_cap": "1000000000", "max_market_cap": "500000000", "name": "Min > Max market cap"},
            
            # Edge cases
            {"min_price": "0", "name": "Zero min_price"},
            {"sector_filter": "InvalidSector", "name": "Invalid sector"},
            {"max_float": "not_numeric", "name": "Invalid float value"},
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                try:
                    params = {k: v for k, v in test_case.items() if k != 'name'}
                    
                    async with session.get(f"{self.base_url}/", params=params) as response:
                        content = await response.text()
                        
                        # Check if error is handled gracefully
                        if response.status == 200:
                            if "Invalid" in content or "error" in content.lower():
                                print(f"✅ {test_case['name']}: Graceful error handling")
                                success_count += 1
                            else:
                                print(f"⚠️  {test_case['name']}: No error message shown")
                        else:
                            print(f"❌ {test_case['name']}: HTTP {response.status}")
                            
                except Exception as e:
                    print(f"❌ {test_case['name']}: Exception - {e}")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📊 Input Validation Success Rate: {success_rate:.1f}% ({success_count}/{len(test_cases)})")
        return success_rate
    
    async def test_cache_error_handling(self):
        """Test cache-related error scenarios"""
        print("\n🧪 Testing Cache Error Handling...")
        
        test_cases = [
            {"endpoint": "/api/cache_status", "name": "Cache Status API"},
            {"endpoint": "/health", "name": "Health Check"},
            {"endpoint": "/", "name": "Main Page (no cache)"},
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                try:
                    async with session.get(f"{self.base_url}{test_case['endpoint']}") as response:
                        if response.status == 200:
                            content = await response.text()
                            if test_case['endpoint'] == '/api/cache_status':
                                # Should return JSON
                                data = await response.json()
                                if 'cache_status' in data or 'successful_count' in data:
                                    print(f"✅ {test_case['name']}: Valid JSON response")
                                    success_count += 1
                                else:
                                    print(f"⚠️  {test_case['name']}: Unexpected JSON structure")
                            else:
                                # Should return HTML without errors
                                if "Traceback" not in content and "KeyError" not in content:
                                    print(f"✅ {test_case['name']}: Clean response")
                                    success_count += 1
                                else:
                                    print(f"❌ {test_case['name']}: Contains error traces")
                        else:
                            print(f"❌ {test_case['name']}: HTTP {response.status}")
                            
                except Exception as e:
                    print(f"❌ {test_case['name']}: Exception - {e}")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📊 Cache Error Handling Success Rate: {success_rate:.1f}% ({success_count}/{len(test_cases)})")
        return success_rate
    
    async def test_security_error_handling(self):
        """Test security-related error scenarios"""
        print("\n🧪 Testing Security Error Handling...")
        
        test_cases = [
            # SQL Injection attempts
            {"min_price": "1'; DROP TABLE stocks; --", "name": "SQL Injection in min_price"},
            {"sector_filter": "'; DELETE FROM cache; --", "name": "SQL Injection in sector"},
            
            # XSS attempts
            {"min_price": "<script>alert('xss')</script>", "name": "XSS in min_price"},
            {"sector_filter": "<img src=x onerror=alert(1)>", "name": "XSS in sector"},
            
            # Buffer overflow attempts
            {"min_price": "A" * 10000, "name": "Buffer overflow min_price"},
            {"sector_filter": "X" * 5000, "name": "Buffer overflow sector"},
            
            # Malformed requests
            {"min_price": "1.2.3.4.5", "name": "Malformed decimal"},
            {"max_float": "1e999999", "name": "Scientific notation overflow"},
        ]
        
        success_count = 0
        
        async with aiohttp.ClientSession() as session:
            for test_case in test_cases:
                try:
                    params = {k: v for k, v in test_case.items() if k != 'name'}
                    
                    async with session.get(f"{self.base_url}/", params=params) as response:
                        content = await response.text()
                        
                        # Security test passes if:
                        # 1. No 5xx errors (server doesn't crash)
                        # 2. No script execution (content doesn't contain unescaped input)
                        # 3. Graceful error handling
                        
                        if response.status < 500:
                            if ("Invalid" in content or "error" in content.lower() or 
                                not any(bad in content for bad in ["<script>", "alert(", "DROP TABLE"])):
                                print(f"✅ {test_case['name']}: Handled securely")
                                success_count += 1
                            else:
                                print(f"⚠️  {test_case['name']}: Potential security issue")
                        else:
                            print(f"❌ {test_case['name']}: Server error {response.status}")
                            
                except Exception as e:
                    print(f"❌ {test_case['name']}: Exception - {e}")
        
        success_rate = (success_count / len(test_cases)) * 100
        print(f"\n📊 Security Error Handling Success Rate: {success_rate:.1f}% ({success_count}/{len(test_cases)})")
        return success_rate
    
    async def test_rate_limiting(self):
        """Test rate limiting error handling"""
        print("\n🧪 Testing Rate Limiting...")
        
        # Make rapid requests to test rate limiting
        request_count = 20
        success_count = 0
        rate_limited_count = 0
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(request_count):
                tasks.append(session.get(f"{self.base_url}/"))
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"❌ Request {i+1}: Exception - {response}")
                else:
                    if response.status == 200:
                        success_count += 1
                    elif response.status == 429:  # Too Many Requests
                        rate_limited_count += 1
                        print(f"✅ Request {i+1}: Rate limited (429) - Working as expected")
                    else:
                        print(f"⚠️  Request {i+1}: Unexpected status {response.status}")
                    response.close()
        
        print(f"\n📊 Rate Limiting Results:")
        print(f"   • Successful requests: {success_count}/{request_count}")
        print(f"   • Rate limited: {rate_limited_count}/{request_count}")
        print(f"   • Rate limiting working: {'✅ YES' if rate_limited_count > 0 else '❌ NO'}")
        
        return (success_count + rate_limited_count) / request_count * 100
    
    async def run_all_tests(self):
        """Run all error handling tests"""
        print("🚀 Starting Comprehensive Error Handling Tests")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test if app is running
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status != 200:
                        raise Exception("App not healthy")
        except Exception:
            print(f"❌ App not running at {self.base_url}")
            print("💡 Start it with: python3 app.py")
            return
        
        print(f"✅ App is running at {self.base_url}")
        
        # Run all test suites
        results = {}
        results['input_validation'] = await self.test_input_validation()
        results['cache_handling'] = await self.test_cache_error_handling()
        results['security_handling'] = await self.test_security_error_handling()
        results['rate_limiting'] = await self.test_rate_limiting()
        
        # Calculate overall score
        overall_score = sum(results.values()) / len(results)
        
        duration = time.time() - start_time
        
        # Final summary
        print("\n" + "=" * 60)
        print("🎯 ERROR HANDLING TEST SUMMARY")
        print("=" * 60)
        
        for test_name, score in results.items():
            status = "✅ PASS" if score >= 80 else "⚠️ FAIR" if score >= 60 else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title():.<30} {score:>5.1f}% {status}")
        
        print("-" * 60)
        print(f"{'OVERALL ERROR HANDLING SCORE':.<30} {overall_score:>5.1f}%")
        
        if overall_score >= 90:
            status = "🌟 EXCELLENT"
        elif overall_score >= 80:
            status = "✅ GOOD"
        elif overall_score >= 70:
            status = "⚠️ ACCEPTABLE"
        else:
            status = "❌ NEEDS WORK"
        
        print(f"{'STATUS':.<30} {status}")
        print(f"{'TEST DURATION':.<30} {duration:>5.1f}s")
        
        print(f"\n💡 Next Steps:")
        if results['input_validation'] < 80:
            print("   • Improve input validation error messages")
        if results['cache_handling'] < 80:
            print("   • Fix cache error handling")
        if results['security_handling'] < 80:
            print("   • Enhance security input sanitization")
        if results['rate_limiting'] < 60:
            print("   • Check rate limiting configuration")
        
        return results

async def main():
    """Run the error handling test suite"""
    tester = ErrorHandlingTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 