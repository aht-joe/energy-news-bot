#!/usr/bin/env python3
"""Test script for DELETE /api/companies/{company_id} endpoint."""

import uvicorn
import threading
import time
import requests
import sys
import os
import logging

sys.path.append(os.getcwd())

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from api import app

def test_delete_endpoint():
    """Test the DELETE endpoint functionality."""
    
    def run_server():
        uvicorn.run(app, host='127.0.0.1', port=8001, log_level='info')

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    time.sleep(3)

    print('=== Testing local DELETE endpoint ===')

    try:
        print('1. Adding test company...')
        response = requests.post('http://127.0.0.1:8001/api/companies/', json={'name': 'Test Delete Company'})
        print(f'POST response: {response.status_code} - {response.json()}')
        
        if response.status_code != 200:
            print('Failed to add test company')
            return
            
        company_id = response.json()['id']

        print(f'2. Deleting company ID {company_id}...')
        response = requests.delete(f'http://127.0.0.1:8001/api/companies/{company_id}')
        print(f'DELETE response: {response.status_code} - {response.json()}')
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('message') == 'deleted':
                print('✅ DELETE endpoint returns correct message format')
            else:
                print(f'❌ DELETE endpoint returns wrong message: {response_data}')

        print('3. Trying to delete non-existent company...')
        response = requests.delete('http://127.0.0.1:8001/api/companies/999')
        print(f'DELETE response: {response.status_code} - {response.json()}')
        
        if response.status_code == 404:
            print('✅ DELETE endpoint correctly returns 404 for non-existent company')
        else:
            print(f'❌ DELETE endpoint should return 404, got {response.status_code}')

        print('=== Local testing completed ===')
        
    except Exception as e:
        print(f'Error during testing: {e}')

if __name__ == '__main__':
    test_delete_endpoint()
