#!/usr/bin/env python3
"""Test script for database persistence fixes."""

import os
import sys
import sqlite3
import tempfile
import shutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_db_path_environment_variable():
    """Test that DB_PATH environment variable is respected."""
    print("\n=== Testing DB_PATH Environment Variable ===")
    
    test_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(test_dir, "test_persistence.db")
    
    try:
        os.environ['DB_PATH'] = test_db_path
        
        from api import get_db_connection, init_database
        
        print(f"Testing with DB_PATH={test_db_path}")
        
        init_database()
        
        if os.path.exists(test_db_path):
            print("✅ Database created at specified DB_PATH location")
        else:
            print("❌ Database NOT created at specified DB_PATH location")
            return False
        
        conn = get_db_connection()
        c = conn.cursor()
        
        tables = c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table_names = [table[0] for table in tables]
        expected_tables = ['articles', 'keywords', 'companies', 'pickup_results']
        
        for table in expected_tables:
            if table in table_names:
                print(f"✅ Table '{table}' exists")
            else:
                print(f"❌ Table '{table}' missing")
                return False
        
        conn.close()
        return True
        
    finally:
        if 'DB_PATH' in os.environ:
            del os.environ['DB_PATH']
        shutil.rmtree(test_dir, ignore_errors=True)

def test_disable_seeding():
    """Test that DISABLE_SEEDING environment variable works."""
    print("\n=== Testing DISABLE_SEEDING Environment Variable ===")
    
    test_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(test_dir, "test_no_seeding.db")
    
    try:
        os.environ['DB_PATH'] = test_db_path
        os.environ['DISABLE_SEEDING'] = 'true'
        
        from api import get_db_connection, init_database
        
        print(f"Testing with DISABLE_SEEDING=true")
        
        init_database()
        
        conn = get_db_connection()
        c = conn.cursor()
        
        company_count = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        if company_count == 0:
            print("✅ Companies table is empty (seeding disabled)")
        else:
            print(f"❌ Companies table has {company_count} entries (seeding should be disabled)")
            return False
        
        keyword_count = c.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        if keyword_count == 0:
            print("✅ Keywords table is empty (seeding disabled)")
        else:
            print(f"❌ Keywords table has {keyword_count} entries (seeding should be disabled)")
            return False
        
        conn.close()
        return True
        
    finally:
        if 'DB_PATH' in os.environ:
            del os.environ['DB_PATH']
        if 'DISABLE_SEEDING' in os.environ:
            del os.environ['DISABLE_SEEDING']
        shutil.rmtree(test_dir, ignore_errors=True)

def test_seeding_enabled():
    """Test that seeding works when DISABLE_SEEDING is not set."""
    print("\n=== Testing Seeding Enabled (Default Behavior) ===")
    
    test_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(test_dir, "test_with_seeding.db")
    
    try:
        os.environ['DB_PATH'] = test_db_path
        
        from api import get_db_connection, init_database
        
        print(f"Testing with seeding enabled (default)")
        
        init_database()
        
        conn = get_db_connection()
        c = conn.cursor()
        
        company_count = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        if company_count == 3:  # Tesla, 出光興産, ENEOS
            print("✅ Companies table has 3 seed entries")
            
            companies = c.execute("SELECT name FROM companies ORDER BY name").fetchall()
            company_names = [company[0] for company in companies]
            expected_companies = ["ENEOS", "Tesla", "出光興産"]
            
            if sorted(company_names) == sorted(expected_companies):
                print("✅ Correct seed companies found")
            else:
                print(f"❌ Unexpected companies: {company_names}")
                return False
        else:
            print(f"❌ Companies table has {company_count} entries (expected 3)")
            return False
        
        keyword_count = c.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        if keyword_count == 4:  # 太陽光発電, CPPA, PPA, 系統用蓄電池
            print("✅ Keywords table has 4 seed entries")
        else:
            print(f"❌ Keywords table has {keyword_count} entries (expected 4)")
            return False
        
        conn.close()
        return True
        
    finally:
        if 'DB_PATH' in os.environ:
            del os.environ['DB_PATH']
        shutil.rmtree(test_dir, ignore_errors=True)

def test_directory_creation():
    """Test that database directories are created automatically."""
    print("\n=== Testing Directory Creation ===")
    
    test_dir = tempfile.mkdtemp()
    nested_path = os.path.join(test_dir, "data", "persistent", "news.db")
    
    try:
        os.environ['DB_PATH'] = nested_path
        
        from api import get_db_connection
        
        print(f"Testing directory creation for path: {nested_path}")
        
        conn = get_db_connection()
        
        if os.path.exists(os.path.dirname(nested_path)):
            print("✅ Database directory created successfully")
        else:
            print("❌ Database directory NOT created")
            return False
        
        if os.path.exists(nested_path):
            print("✅ Database file created in nested directory")
        else:
            print("❌ Database file NOT created in nested directory")
            return False
        
        conn.close()
        return True
        
    finally:
        if 'DB_PATH' in os.environ:
            del os.environ['DB_PATH']
        shutil.rmtree(test_dir, ignore_errors=True)

def main():
    """Run all tests."""
    print("🧪 Testing Database Persistence Fixes")
    print("=" * 50)
    
    tests = [
        test_db_path_environment_variable,
        test_disable_seeding,
        test_seeding_enabled,
        test_directory_creation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print("✅ PASSED")
            else:
                failed += 1
                print("❌ FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Database persistence fixes are working correctly.")
        return True
    else:
        print("💥 Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
