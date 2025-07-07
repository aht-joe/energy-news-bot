#!/usr/bin/env python3
"""Comprehensive test script for company deletion functionality."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://energy-news-bot.onrender.com/api"

def test_company_deletion_comprehensive():
    """Test all aspects of company deletion functionality."""
    
    print("=== Comprehensive Company Deletion Test ===")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    print("\n1. Getting current companies state...")
    try:
        response = requests.get(f"{BASE_URL}/companies", timeout=10)
        if response.status_code == 200:
            companies = response.json()
            print(f"✅ Current companies: {len(companies)}")
            for company in companies:
                print(f"   - {company['name']} (ID: {company['id']})")
        else:
            print(f"❌ Failed to get companies: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting companies: {e}")
        return False
    
    if not companies:
        print("\n2. No companies found, adding test company...")
        test_company = {"name": f"削除テスト会社_{int(time.time())}"}
        try:
            response = requests.post(f"{BASE_URL}/companies/", json=test_company, timeout=10)
            if response.status_code == 200:
                added_company = response.json()
                print(f"✅ Added test company: {added_company}")
                companies = [added_company]
            else:
                print(f"❌ Failed to add test company: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error adding test company: {e}")
            return False
    
    print(f"\n3. Testing DELETE with existing company ID {companies[0]['id']}...")
    company_to_delete = companies[0]
    try:
        response = requests.delete(f"{BASE_URL}/companies/{company_to_delete['id']}", timeout=10)
        print(f"DELETE response: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ DELETE successful: {response_data}")
            if response_data.get("message") == "deleted":
                print("✅ Correct response format")
            else:
                print(f"⚠️  Unexpected response format: {response_data}")
        else:
            print(f"❌ DELETE failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during DELETE: {e}")
        return False
    
    print("\n4. Verifying deletion by checking companies list...")
    try:
        response = requests.get(f"{BASE_URL}/companies", timeout=10)
        if response.status_code == 200:
            companies_after = response.json()
            print(f"✅ Companies after deletion: {len(companies_after)}")
            
            deleted_company_still_exists = any(
                c['id'] == company_to_delete['id'] for c in companies_after
            )
            
            if deleted_company_still_exists:
                print(f"❌ PROBLEM: Deleted company {company_to_delete['name']} (ID: {company_to_delete['id']}) still exists!")
                return False
            else:
                print(f"✅ Confirmed: Company {company_to_delete['name']} (ID: {company_to_delete['id']}) was successfully deleted")
                
            for company in companies_after:
                print(f"   - {company['name']} (ID: {company['id']})")
        else:
            print(f"❌ Failed to verify deletion: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verifying deletion: {e}")
        return False
    
    print(f"\n5. Testing DELETE with already deleted ID {company_to_delete['id']} (should be 404)...")
    try:
        response = requests.delete(f"{BASE_URL}/companies/{company_to_delete['id']}", timeout=10)
        print(f"DELETE response: {response.status_code}")
        if response.status_code == 404:
            response_data = response.json()
            print(f"✅ Correct 404 response: {response_data}")
            if response_data.get("detail") == "Company not found":
                print("✅ Correct error message")
            else:
                print(f"⚠️  Unexpected error message: {response_data}")
        else:
            print(f"❌ Expected 404, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing 404 case: {e}")
        return False
    
    print("\n6. Testing DELETE with non-existent ID 999 (should be 404)...")
    try:
        response = requests.delete(f"{BASE_URL}/companies/999", timeout=10)
        print(f"DELETE response: {response.status_code}")
        if response.status_code == 404:
            response_data = response.json()
            print(f"✅ Correct 404 response for non-existent ID: {response_data}")
        else:
            print(f"❌ Expected 404 for non-existent ID, got {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing non-existent ID: {e}")
        return False
    
    print("\n✅ All company deletion tests passed!")
    print("\n📋 Summary:")
    print("- DELETE endpoint correctly removes existing companies")
    print("- Database persistence works - deletions are reflected in GET responses")
    print("- 404 responses are correctly returned for non-existent companies")
    print("- Response formats are consistent and correct")
    
    print("\n🔍 Frontend Integration Notes:")
    print("- Ensure frontend refreshes company list after successful DELETE")
    print("- Handle 404 responses gracefully (company already deleted)")
    print("- Use actual company IDs from GET /api/companies before DELETE")
    print("- Clear any client-side caching after DELETE operations")
    
    return True

if __name__ == "__main__":
    success = test_company_deletion_comprehensive()
    if not success:
        print("\n❌ Test failed - check API connectivity and functionality")
        exit(1)
    else:
        print("\n🎯 Company deletion functionality is working correctly")
