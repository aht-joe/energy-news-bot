#!/usr/bin/env python3
"""Test database persistence on Render deployment after PR merge."""

import requests
import time
import json
from datetime import datetime

BASE_URL = "https://energy-news-bot.onrender.com/api"

def test_render_persistence():
    """Test database persistence on Render after deployment."""
    
    print("=== Render Database Persistence Test ===")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    print("\n1. Checking initial state...")
    try:
        keywords_response = requests.get(f"{BASE_URL}/keywords", timeout=10)
        companies_response = requests.get(f"{BASE_URL}/companies", timeout=10)
        
        if keywords_response.status_code == 200:
            initial_keywords = keywords_response.json()
            print(f"✅ Initial keywords count: {len(initial_keywords)}")
            for kw in initial_keywords:
                print(f"   - {kw['word']} (id: {kw['id']})")
        else:
            print(f"❌ Keywords endpoint error: {keywords_response.status_code}")
            return False
            
        if companies_response.status_code == 200:
            initial_companies = companies_response.json()
            print(f"✅ Initial companies count: {len(initial_companies)}")
            for co in initial_companies:
                print(f"   - {co['name']} (id: {co['id']})")
        else:
            print(f"❌ Companies endpoint error: {companies_response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking initial state: {e}")
        return False
    
    timestamp = int(time.time())
    test_keyword = {"word": f"永続化テスト_{timestamp}"}
    test_company = {"name": f"テスト会社_{timestamp}"}
    
    print(f"\n2. Adding test data with timestamp {timestamp}...")
    try:
        keyword_post = requests.post(f"{BASE_URL}/keywords/", json=test_keyword, timeout=10)
        company_post = requests.post(f"{BASE_URL}/companies/", json=test_company, timeout=10)
        
        if keyword_post.status_code == 200:
            added_keyword = keyword_post.json()
            print(f"✅ Added keyword: {added_keyword}")
        else:
            print(f"❌ Keyword POST failed: {keyword_post.status_code} - {keyword_post.text}")
            return False
            
        if company_post.status_code == 200:
            added_company = company_post.json()
            print(f"✅ Added company: {added_company}")
        else:
            print(f"❌ Company POST failed: {company_post.status_code} - {company_post.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        return False
    
    print("\n3. Verifying test data was added...")
    try:
        keywords_after = requests.get(f"{BASE_URL}/keywords", timeout=10)
        companies_after = requests.get(f"{BASE_URL}/companies", timeout=10)
        
        if keywords_after.status_code == 200:
            keywords_list = keywords_after.json()
            test_keyword_found = any(kw['word'] == test_keyword['word'] for kw in keywords_list)
            print(f"✅ Keywords after POST: {len(keywords_list)} (test keyword found: {test_keyword_found})")
        else:
            print(f"❌ Keywords verification failed: {keywords_after.status_code}")
            return False
            
        if companies_after.status_code == 200:
            companies_list = companies_after.json()
            test_company_found = any(co['name'] == test_company['name'] for co in companies_list)
            print(f"✅ Companies after POST: {len(companies_list)} (test company found: {test_company_found})")
        else:
            print(f"❌ Companies verification failed: {companies_after.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying test data: {e}")
        return False
    
    print(f"\n4. 🔄 PERSISTENCE TEST INSTRUCTIONS:")
    print(f"   Test data added at: {datetime.now().isoformat()}")
    print(f"   Test keyword: {test_keyword['word']}")
    print(f"   Test company: {test_company['name']}")
    print(f"")
    print(f"   TO COMPLETE THE PERSISTENCE TEST:")
    print(f"   1. Wait for or trigger a Render service restart")
    print(f"   2. Run this script again after restart")
    print(f"   3. Check if the test data with timestamp {timestamp} still exists")
    print(f"   4. Verify that seeded data is present if database was reset")
    print(f"")
    print(f"   EXPECTED SEEDED DATA (if database reset):")
    print(f"   Keywords: 太陽光発電, CPPA, PPA, 系統用蓄電池")
    print(f"   Companies: Tesla, 出光興産, ENEOS")
    
    print(f"\n5. Checking for expected seeded data...")
    expected_keywords = ["太陽光発電", "CPPA", "PPA", "系統用蓄電池"]
    expected_companies = ["Tesla", "出光興産", "ENEOS"]
    
    current_keyword_words = [kw['word'] for kw in keywords_list]
    current_company_names = [co['name'] for co in companies_list]
    
    seeded_keywords_found = [kw for kw in expected_keywords if kw in current_keyword_words]
    seeded_companies_found = [co for co in expected_companies if co in current_company_names]
    
    print(f"   Seeded keywords found: {len(seeded_keywords_found)}/{len(expected_keywords)}")
    for kw in seeded_keywords_found:
        print(f"     ✅ {kw}")
    for kw in expected_keywords:
        if kw not in seeded_keywords_found:
            print(f"     ❌ Missing: {kw}")
    
    print(f"   Seeded companies found: {len(seeded_companies_found)}/{len(expected_companies)}")
    for co in seeded_companies_found:
        print(f"     ✅ {co}")
    for co in expected_companies:
        if co not in seeded_companies_found:
            print(f"     ❌ Missing: {co}")
    
    print(f"\n✅ Pre-restart test completed successfully!")
    print(f"📋 Save this output and compare with post-restart results.")
    
    return True

if __name__ == "__main__":
    success = test_render_persistence()
    if not success:
        print("\n❌ Test failed - check API connectivity and endpoints")
        exit(1)
    else:
        print("\n🎯 Ready for persistence testing after Render restart")
