#!/usr/bin/env python3
"""
Fix Database Schema
Recreates the traffic analytics database with correct schema
"""

import os
import sqlite3
from datetime import datetime

def fix_database():
    """Fix the traffic analytics database schema"""
    db_path = "traffic_analytics.db"
    
    print("🔧 Fixing traffic analytics database...")
    
    # Backup existing database if it exists
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            os.rename(db_path, backup_path)
            print(f"📁 Backed up existing database to {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not backup database: {e}")
            return False
    
    try:
        # Create new database with correct schema
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create visitors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE,
                    ip_address TEXT,
                    user_agent TEXT,
                    first_visit TIMESTAMP,
                    last_visit TIMESTAMP,
                    visit_count INTEGER DEFAULT 1
                )
            ''')
            
            # Create page_views table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS page_views (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    page_url TEXT,
                    timestamp TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT,
                    referrer TEXT
                )
            ''')
            
            # Create api_calls table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    endpoint TEXT,
                    timestamp TIMESTAMP,
                    ip_address TEXT,
                    user_agent TEXT
                )
            ''')
            
            conn.commit()
            print("✅ Database schema fixed successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    fix_database() 