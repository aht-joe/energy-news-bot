#!/usr/bin/env python3
"""Test the database persistence solution locally."""

import sys
import os
sys.path.append('.')

import logging
from api import get_db_connection, init_database

def test_database_persistence_locally():
    """Test database persistence solution locally."""
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print('=== Testing Database Persistence Solution Locally ===')
    
    print('\n1. Testing get_db_connection() with path logging...')
    try:
        conn = get_db_connection()
        print('✅ Database connection successful')
        
        db_path = conn.execute("PRAGMA database_list").fetchone()[2]
        print(f'📁 Database file location: {os.path.abspath(db_path)}')
        conn.close()
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False
    
    print('\n2. Testing init_database() with automatic seeding...')
    try:
        init_database()
        print('✅ Database initialization completed')
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')
        return False
    
    print('\n3. Verifying seeded data...')
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        keywords = c.execute('SELECT * FROM keywords').fetchall()
        companies = c.execute('SELECT * FROM companies').fetchall()
        
        print(f'📊 Keywords found: {len(keywords)}')
        print(f'📊 Companies found: {len(companies)}')
        
        if keywords:
            print('   Keywords:')
            for kw in keywords:
                print(f'     - {kw[1]} (id: {kw[0]})')
        
        if companies:
            print('   Companies:')
            for co in companies:
                print(f'     - {co[1]} (id: {co[0]})')
        
        conn.close()
        
        expected_keywords = ["太陽光発電", "CPPA", "PPA", "系統用蓄電池"]
        expected_companies = ["Tesla", "出光興産", "ENEOS"]
        
        keyword_words = [kw[1] for kw in keywords]
        company_names = [co[1] for co in companies]
        
        missing_keywords = [kw for kw in expected_keywords if kw not in keyword_words]
        missing_companies = [co for co in expected_companies if co not in company_names]
        
        if missing_keywords:
            print(f'⚠️  Missing expected keywords: {missing_keywords}')
        else:
            print('✅ All expected keywords found')
            
        if missing_companies:
            print(f'⚠️  Missing expected companies: {missing_companies}')
        else:
            print('✅ All expected companies found')
            
    except Exception as e:
        print(f'❌ Data verification failed: {e}')
        return False
    
    print('\n4. Testing that seeding preserves existing data...')
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO keywords (word) VALUES (?)", ("テスト専用キーワード",))
        conn.commit()
        
        initial_count = c.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        conn.close()
        
        init_database()
        
        conn = get_db_connection()
        c = conn.cursor()
        final_count = c.execute("SELECT COUNT(*) FROM keywords").fetchone()[0]
        conn.close()
        
        if final_count >= initial_count:
            print('✅ Existing data preserved during re-initialization')
        else:
            print(f'❌ Data lost during re-initialization: {initial_count} -> {final_count}')
            return False
            
    except Exception as e:
        print(f'❌ Data preservation test failed: {e}')
        return False
    
    print('\n✅ All local database persistence tests passed!')
    print('\n📋 Next steps:')
    print('1. Merge PR #9 to deploy changes to Render')
    print('2. Test data persistence on Render after deployment')
    print('3. Monitor Render logs for database path information')
    
    return True

if __name__ == '__main__':
    success = test_database_persistence_locally()
    sys.exit(0 if success else 1)
