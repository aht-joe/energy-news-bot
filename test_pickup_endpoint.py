#!/usr/bin/env python3
"""Test script for the new /api/pickup-results endpoint."""

import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from api import app

def test_pickup_results_endpoint():
    """Test the new pickup-results endpoint functionality."""
    
    client = TestClient(app)
    
    print('=== Testing new pickup-results endpoint locally ===')
    
    try:
        response = client.get('/api/pickup-results')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Response type: {type(data)}')
            print(f'Number of results: {len(data)}')
            
            if data:
                print('Sample result:')
                sample = data[0]
                print(f'  Title: {sample.get("title", "N/A")}')
                print(f'  Matched Keywords: {sample.get("matched_keywords", [])}')
                print(f'  Matched Companies: {sample.get("matched_companies", [])}')
                print(f'  Importance: {sample.get("importance", "N/A")}')
                print(f'  Summary length: {len(sample.get("summary", ""))}')
                print(f'  URL: {sample.get("url", "N/A")}')
            else:
                print('No results returned (empty array)')
                
        else:
            print(f'Error response: {response.text}')
            
    except Exception as e:
        print(f'Error during testing: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_pickup_results_endpoint()
