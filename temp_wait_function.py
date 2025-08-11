def wait_for_cache(timeout=10):
    """Wait for cache file to be created by background scanner"""
    for _ in range(timeout):
        if os.path.exists(CACHE_FILE):
            print(f"✅ Cache file found at {CACHE_FILE}")
            return True
        print("⌛ Waiting for cache...")
        time.sleep(1)
    print("⚠️ Cache file still missing after wait.")
    return False
