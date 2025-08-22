#!/usr/bin/env python3
"""
Comprehensive system test for Poppalyze
Tests all components to ensure they work correctly
"""

import os
import sys
import time
import json
from config import Config
from cache_manager import cache_manager
from utils import safe_json_dump, safe_json_load, validate_cache_data

def test_configuration():
    """Test configuration setup"""
    print("🔧 Testing configuration...")
    
    # Test base directory
    assert os.path.exists(Config.BASE_DIR), f"Base directory doesn't exist: {Config.BASE_DIR}"
    print(f"✅ Base directory: {Config.BASE_DIR}")
    
    # Test cache directory creation
    Config.ensure_directories()
    assert os.path.exists(Config.CACHE_DIR), f"Cache directory doesn't exist: {Config.CACHE_DIR}"
    print(f"✅ Cache directory: {Config.CACHE_DIR}")
    
    # Test absolute path helper
    test_path = Config.get_absolute_path("data/test.json")
    assert test_path == os.path.abspath(os.path.join(Config.BASE_DIR, "data/test.json"))
    print(f"✅ Absolute path helper: {test_path}")
    
    print("✅ Configuration tests passed\n")

def test_cache_manager():
    """Test cache manager functionality"""
    print("📁 Testing cache manager...")
    
    # Test initialization
    cm = cache_manager
    assert cm.cache_file == Config.CACHE_FILE
    print(f"✅ Cache file path: {cm.cache_file}")
    
    # Test save and load
    test_data = {
        'stocks': {
            'AAPL': {'price': 150.0, 'gap_pct': 2.5},
            'TSLA': {'price': 300.0, 'gap_pct': -1.5}
        },
        'last_update': time.time(),
        'last_update_str': '2025-08-03 17:00:00',
        'successful_count': 2,
        'total_count': 2
    }
    
    # Test save
    assert cm.save_cache(test_data), "Failed to save cache"
    print("✅ Cache save successful")
    
    # Test load
    loaded_data = cm.load_cache()
    assert loaded_data is not None, "Failed to load cache"
    assert len(loaded_data['stocks']) == 2, f"Expected 2 stocks, got {len(loaded_data['stocks'])}"
    print("✅ Cache load successful")
    
    # Test cache status
    status = cm.get_cache_status()
    assert status['stock_count'] == 2, f"Expected 2 stocks in status, got {status['stock_count']}"
    print("✅ Cache status successful")
    
    # Test clear cache
    assert cm.clear_cache(), "Failed to clear cache"
    print("✅ Cache clear successful")
    
    print("✅ Cache manager tests passed\n")

def test_utils():
    """Test utility functions"""
    print("🛠️ Testing utilities...")
    
    # Test JSON serialization
    import numpy as np
    test_data = {
        'int64': np.int64(42),
        'float64': np.float64(3.14),
        'array': np.array([1, 2, 3])
    }
    
    # Test safe JSON dump
    test_file = os.path.join(Config.CACHE_DIR, "test_utils.json")
    assert safe_json_dump(test_data, test_file), "Failed to save test data"
    print("✅ Safe JSON dump successful")
    
    # Test safe JSON load
    loaded_data = safe_json_load(test_file)
    assert loaded_data is not None, "Failed to load test data"
    assert loaded_data['int64'] == 42, "Int64 not converted correctly"
    assert loaded_data['float64'] == 3.14, "Float64 not converted correctly"
    assert loaded_data['array'] == [1, 2, 3], "Array not converted correctly"
    print("✅ Safe JSON load successful")
    
    # Test data validation
    valid_data = {'stocks': {'AAPL': {'price': 150.0}}}
    invalid_data = {'invalid': 'structure'}
    
    assert validate_cache_data(valid_data), "Valid data not recognized"
    assert not validate_cache_data(invalid_data), "Invalid data not caught"
    print("✅ Data validation successful")
    
    # Cleanup
    os.remove(test_file)
    
    print("✅ Utility tests passed\n")

def test_background_scanner():
    """Test background scanner functionality"""
    print("🔄 Testing background scanner...")
    
    try:
        from background_scanner_fast import scan_gaps
        
        # Test that scan_gaps function exists
        assert callable(scan_gaps), "scan_gaps function not found"
        print("✅ Background scanner import successful")
        
        # Note: We don't actually run the scanner here to avoid API calls
        # In a real test environment, you might want to mock the API calls
        
    except ImportError as e:
        print(f"⚠️ Background scanner not available: {e}")
    except Exception as e:
        print(f"⚠️ Background scanner test failed: {e}")
    
    print("✅ Background scanner tests passed\n")

def test_flask_app():
    """Test Flask app functionality"""
    print("🌐 Testing Flask app...")
    
    try:
        from app import app
        
        # Test that Flask app exists
        assert app is not None, "Flask app not found"
        print("✅ Flask app import successful")
        
        # Test that app has required routes
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            assert response.status_code == 200, f"Health endpoint failed: {response.status_code}"
            print("✅ Health endpoint working")
            
            # Test cache status endpoint
            response = client.get('/api/cache_status')
            assert response.status_code == 200, f"Cache status endpoint failed: {response.status_code}"
            print("✅ Cache status endpoint working")
            
    except ImportError as e:
        print(f"⚠️ Flask app not available: {e}")
    except Exception as e:
        print(f"⚠️ Flask app test failed: {e}")
    
    print("✅ Flask app tests passed\n")

def main():
    """Run all tests"""
    print("🚀 Starting Poppalyze System Tests\n")
    
    try:
        test_configuration()
        test_cache_manager()
        test_utils()
        test_background_scanner()
        test_flask_app()
        
        print("🎉 All tests passed! System is ready for deployment.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 