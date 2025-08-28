#!/usr/bin/env python3
"""
Test script to verify API endpoints are returning explanations correctly.
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5000"
    
    try:
        # Test the records endpoint
        print("Testing /api/records endpoint...")
        response = requests.get(f"{base_url}/api/records")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Records endpoint working")
            print(f"Number of records: {len(data.get('records', []))}")
            
            if data.get('records'):
                record = data['records'][0]
                print(f"Sample record ID: {record.get('id')}")
                print(f"Company: {record.get('group_name')}")
                print(f"Has penalty_a_explanation: {'penalty_a_explanation' in record}")
                print(f"Has penalty_b_explanation: {'penalty_b_explanation' in record}")
                
                if 'penalty_a_explanation' in record:
                    print(f"Explanation A length: {len(record['penalty_a_explanation'])}")
                    print(f"Explanation A preview: {record['penalty_a_explanation'][:100]}...")
                
                if 'penalty_b_explanation' in record:
                    print(f"Explanation B length: {len(record['penalty_b_explanation'])}")
                    print(f"Explanation B preview: {record['penalty_b_explanation'][:100]}...")
            else:
                print("❌ No records found")
        else:
            print(f"❌ Records endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the backend is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error testing API: {e}")

if __name__ == "__main__":
    test_api()
