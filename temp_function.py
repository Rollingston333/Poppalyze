def load_cached_stocks():
    """Load cached stocks from file with retry logic"""
    import time
    
    # Try multiple times with delays to allow scanner to write
    for attempt in range(3):
        try:
            if not os.path.exists(CACHE_FILE):
                if attempt == 0:
                    print("⚠️ No cache file found, waiting for scanner...")
                time.sleep(2)  # Wait 2 seconds for scanner to write
                continue
                
            with open(CACHE_FILE) as f:
                data = json.load(f)
                
            # Verify we have actual stock data
            if data and isinstance(data, dict) and "stocks" in data and data["stocks"]:
                print(f"✅ Loaded {len(data["stocks"])} stocks from cache")
                return data
            else:
                print(f"⚠️ Cache file exists but no stock data (attempt {attempt + 1}/3)")
                if attempt < 2:
                    time.sleep(3)  # Wait 3 seconds before retry
                    
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error reading cache (attempt {attempt + 1}/3): {e}")
            if attempt < 2:
                time.sleep(2)
        except Exception as e:
            print(f"❌ Unexpected error reading cache: {e}")
            break
    
    print("❌ Failed to load cache after 3 attempts")
    return []
