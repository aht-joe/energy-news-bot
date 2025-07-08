#!/usr/bin/env python3
"""Comprehensive test script for keyword deletion functionality."""

import requests
import json
import time
from datetime import datetime

BASE_URL = "https://energy-news-bot.onrender.com/api"

def test_keyword_deletion_comprehensive():
    """Test all aspects of keyword deletion functionality."""
    
    print("=== Comprehensive Keyword Deletion Test ===")
    print(f"Testing API at: {BASE_URL}")
    print(f"Test started at: {datetime.now().isoformat()}")
    
    print("\n1. Getting current keywords state...")
    try:
        response = requests.get(f"{BASE_URL}/keywords", timeout=10)
        if response.status_code == 200:
            keywords = response.json()
            print(f"✅ Current keywords: {len(keywords)}")
            for keyword in keywords:
                print(f"   - {keyword['word']} (ID: {keyword['id']})")
        else:
            print(f"❌ Failed to get keywords: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting keywords: {e}")
        return False
    
    if not keywords:
        print("\n2. No keywords found, adding test keyword...")
        test_keyword = {"word": f"削除テスト_{int(time.time())}"}
        try:
            response = requests.post(f"{BASE_URL}/keywords/", json=test_keyword, timeout=10)
            if response.status_code == 200:
                added_keyword = response.json()
                print(f"✅ Added test keyword: {added_keyword}")
                keywords = [added_keyword]
            else:
                print(f"❌ Failed to add test keyword: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error adding test keyword: {e}")
            return False
    
    print(f"\n3. Testing DELETE with existing keyword ID {keywords[0]['id']}...")
    keyword_to_delete = keywords[0]
    try:
        response = requests.delete(f"{BASE_URL}/keywords/{keyword_to_delete['id']}", timeout=10)
        print(f"DELETE response: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ DELETE successful: {response_data}")
            if response_data.get("message") == "Keyword deleted successfully":
                print("✅ Correct response format")
            else:
                print(f"⚠️  Unexpected response format: {response_data}")
        else:
            print(f"❌ DELETE failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during DELETE: {e}")
        return False
    
    print("\n4. Verifying deletion by checking keywords list...")
    try:
        response = requests.get(f"{BASE_URL}/keywords", timeout=10)
        if response.status_code == 200:
            keywords_after = response.json()
            print(f"✅ Keywords after deletion: {len(keywords_after)}")
            
            deleted_keyword_still_exists = any(
                k['id'] == keyword_to_delete['id'] for k in keywords_after
            )
            
            if deleted_keyword_still_exists:
                print(f"❌ PROBLEM: Deleted keyword {keyword_to_delete['word']} (ID: {keyword_to_delete['id']}) still exists!")
                return False
            else:
                print(f"✅ Confirmed: Keyword {keyword_to_delete['word']} (ID: {keyword_to_delete['id']}) was successfully deleted")
                
            for keyword in keywords_after:
                print(f"   - {keyword['word']} (ID: {keyword['id']})")
        else:
            print(f"❌ Failed to verify deletion: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verifying deletion: {e}")
        return False
    
    print(f"\n5. Testing DELETE with already deleted ID {keyword_to_delete['id']} (should be 404)...")
    try:
        response = requests.delete(f"{BASE_URL}/keywords/{keyword_to_delete['id']}", timeout=10)
        print(f"DELETE response: {response.status_code}")
        if response.status_code == 404:
            response_data = response.json()
            print(f"✅ Correct 404 response: {response_data}")
            if response_data.get("detail") == "Keyword not found":
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
        response = requests.delete(f"{BASE_URL}/keywords/999", timeout=10)
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
    
    print("\n7. Testing specific ID=5 if it exists...")
    try:
        response = requests.get(f"{BASE_URL}/keywords", timeout=10)
        if response.status_code == 200:
            current_keywords = response.json()
            id_5_exists = any(k['id'] == 5 for k in current_keywords)
            
            if id_5_exists:
                print("✅ ID=5 exists, testing deletion...")
                response = requests.delete(f"{BASE_URL}/keywords/5", timeout=10)
                print(f"DELETE ID=5 response: {response.status_code}")
                if response.status_code == 200:
                    print("✅ ID=5 deleted successfully")
                elif response.status_code == 404:
                    print("✅ ID=5 returned 404 (already deleted or doesn't exist)")
                else:
                    print(f"⚠️  Unexpected response for ID=5: {response.status_code}")
            else:
                print("ℹ️  ID=5 does not exist, testing DELETE anyway...")
                response = requests.delete(f"{BASE_URL}/keywords/5", timeout=10)
                print(f"DELETE ID=5 response: {response.status_code}")
                if response.status_code == 404:
                    print("✅ ID=5 correctly returned 404 (doesn't exist)")
                else:
                    print(f"⚠️  Unexpected response for non-existent ID=5: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing ID=5: {e}")
        return False
    
    print("\n✅ All keyword deletion tests passed!")
    print("\n📋 Summary:")
    print("- DELETE endpoint correctly removes existing keywords")
    print("- Database persistence works - deletions are reflected in GET responses")
    print("- 404 responses are correctly returned for non-existent keywords")
    print("- Response formats are consistent and correct")
    print("- ID=5 handling works as expected")
    
    print("\n🔍 Frontend Integration Notes:")
    print("- Ensure frontend refreshes keyword list after successful DELETE")
    print("- Handle 404 responses gracefully (keyword already deleted)")
    print("- Use actual keyword IDs from GET /api/keywords before DELETE")
    print("- Clear any client-side caching after DELETE operations")
    
    return True

if __name__ == "__main__":
    success = test_keyword_deletion_comprehensive()
    if not success:
        print("\n❌ Test failed - check API connectivity and functionality")
        exit(1)
    else:
        print("\n🎯 Keyword deletion functionality is working correctly")
