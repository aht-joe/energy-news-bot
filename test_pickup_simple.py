#!/usr/bin/env python3
"""Simple test for /api/pickup-results endpoint structure."""

import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from api import app

def test_pickup_results_structure():
    """Test the pickup-results endpoint returns correct structure."""
    
    client = TestClient(app)
    
    print('=== Testing pickup-results endpoint structure ===')
    
    try:
        response = client.get('/api/pickup-results')
        print(f'Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            print(f'Response type: {type(data)}')
            print(f'Number of results: {len(data)}')
            
            if data:
                print('Sample result structure:')
                sample = data[0]
                required_fields = ['title', 'matched_keywords', 'matched_companies', 'importance', 'summary', 'url']
                for field in required_fields:
                    if field in sample:
                        print(f'  ✅ {field}: {type(sample[field])}')
                    else:
                        print(f'  ❌ Missing field: {field}')
                        
                importance = sample.get('importance', '')
                if importance in ['High', 'Medium', 'Low']:
                    print(f'  ✅ Importance classification valid: {importance}')
                else:
                    print(f'  ❌ Invalid importance: {importance}')
                    
            print('✅ Endpoint structure test completed')
                
        else:
            print(f'❌ Error response: {response.text}')
            
    except Exception as e:
        print(f'❌ Error during testing: {e}')

if __name__ == '__main__':
    test_pickup_results_structure()
