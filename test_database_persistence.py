#!/usr/bin/env python3
"""Test script for database persistence across restarts."""

import sys
import os
sys.path.append(os.getcwd())

import requests
import time
import json

BASE_URL = "https://energy-news-bot.onrender.com/api"

def test_database_persistence():
    """Test database operations and persistence."""
    
    print("=== Database Persistence Test ===")
    
    print("\n1. Testing GET endpoints (initial state)")
    
    keywords_response = requests.get(f"{BASE_URL}/keywords")
    companies_response = requests.get(f"{BASE_URL}/companies")
    
    print(f"Keywords status: {keywords_response.status_code}")
    print(f"Keywords count: {len(keywords_response.json()) if keywords_response.status_code == 200 else 'Error'}")
    
    print(f"Companies status: {companies_response.status_code}")
    print(f"Companies count: {len(companies_response.json()) if companies_response.status_code == 200 else 'Error'}")
    
    print("\n2. Adding test data")
    
    test_keyword = {"word": "テスト用キーワード"}
    test_company = {"name": "テスト会社"}
    
    keyword_post = requests.post(f"{BASE_URL}/keywords/", json=test_keyword)
    company_post = requests.post(f"{BASE_URL}/companies/", json=test_company)
    
    print(f"Keyword POST status: {keyword_post.status_code}")
    print(f"Company POST status: {company_post.status_code}")
    
    if keyword_post.status_code == 200:
        print(f"Added keyword: {keyword_post.json()}")
    if company_post.status_code == 200:
        print(f"Added company: {company_post.json()}")
    
    print("\n3. Verifying data was added")
    
    keywords_after = requests.get(f"{BASE_URL}/keywords")
    companies_after = requests.get(f"{BASE_URL}/companies")
    
    print(f"Keywords after POST: {len(keywords_after.json()) if keywords_after.status_code == 200 else 'Error'}")
    print(f"Companies after POST: {len(companies_after.json()) if companies_after.status_code == 200 else 'Error'}")
    
    print("\n4. Test completed")
    print("To test persistence:")
    print("1. Wait for or trigger a Render service restart")
    print("2. Run this script again to check if data persists")
    print("3. Check application logs for database path information")

if __name__ == "__main__":
    test_database_persistence()
