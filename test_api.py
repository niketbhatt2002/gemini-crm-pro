"""
GeminiCRM Pro - API Test Script
Tests basic API functionality
"""
import requests
import json
import time

BASE_URL = 'http://localhost:5000'

def test_api():
    """Run API tests"""
    
    print("=" * 60)
    print("GeminiCRM Pro - API Test Suite")
    print("=" * 60)
    
    # Test 1: Config Status
    print("\n✓ Testing API Configuration Status...")
    try:
        res = requests.get(f'{BASE_URL}/api/config/status')
        data = res.json()
        print(f"  Status: {res.status_code}")
        print(f"  Configured: {data.get('configured')}")
        print(f"  Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 2: Dashboard Stats
    print("\n✓ Testing Dashboard Stats...")
    try:
        res = requests.get(f'{BASE_URL}/api/dashboard/stats')
        data = res.json()
        print(f"  Status: {res.status_code}")
        print(f"  Total Contacts: {data.get('total_contacts')}")
        print(f"  Total Leads: {data.get('total_leads')}")
        print(f"  Total Deals: {data.get('total_deals')}")
        print(f"  Pipeline Value: ${data.get('total_pipeline'):,}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 3: Get All Contacts
    print("\n✓ Testing Contacts List...")
    try:
        res = requests.get(f'{BASE_URL}/api/contacts')
        data = res.json()
        print(f"  Status: {res.status_code}")
        print(f"  Total Contacts: {len(data.get('contacts', []))}")
        if data.get('contacts'):
            contact = data['contacts'][0]
            print(f"  Sample: {contact.get('first_name')} {contact.get('last_name')} ({contact.get('email')})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 4: Get All Leads
    print("\n✓ Testing Leads List...")
    try:
        res = requests.get(f'{BASE_URL}/api/leads')
        data = res.json()
        print(f"  Status: {res.status_code}")
        print(f"  Total Leads: {len(data.get('leads', []))}")
        if data.get('leads'):
            lead = data['leads'][0]
            print(f"  Sample: {lead.get('name')} (Score: {lead.get('score')}/100)")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 5: Get All Deals
    print("\n✓ Testing Deals List...")
    try:
        res = requests.get(f'{BASE_URL}/api/deals')
        data = res.json()
        print(f"  Status: {res.status_code}")
        print(f"  Total Deals: {len(data.get('deals', []))}")
        if data.get('deals'):
            deal = data['deals'][0]
            print(f"  Sample: {deal.get('name')} (${deal.get('value'):,})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 6: Search
    print("\n✓ Testing Global Search...")
    try:
        res = requests.get(f'{BASE_URL}/api/search?q=tech')
        data = res.json()
        print(f"  Status: {res.status_code}")
        print(f"  Results found: {len(data.get('results', []))}")
        for result in data.get('results', [])[:3]:
            print(f"    - {result.get('title')} ({result.get('type')})")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Test 7: Create Contact
    print("\n✓ Testing Create Contact...")
    try:
        new_contact = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'company': 'Test Corp',
            'phone': '+1-555-0000'
        }
        res = requests.post(f'{BASE_URL}/api/contacts', json=new_contact)
        data = res.json()
        print(f"  Status: {res.status_code}")
        if data.get('success'):
            print(f"  Created: {data['contact']['first_name']} {data['contact']['last_name']}")
            contact_id = data['contact']['id']
            
            # Test Update
            print("\n✓ Testing Update Contact...")
            update_data = {'phone': '+1-555-1111'}
            res = requests.put(f'{BASE_URL}/api/contacts/{contact_id}', json=update_data)
            data = res.json()
            print(f"  Status: {res.status_code}")
            if data.get('success'):
                print(f"  Updated: {data['contact']['phone']}")
            
            # Test Delete
            print("\n✓ Testing Delete Contact...")
            res = requests.delete(f'{BASE_URL}/api/contacts/{contact_id}')
            data = res.json()
            print(f"  Status: {res.status_code}")
            print(f"  Deleted: {data.get('success')}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API Tests Complete!")
    print("=" * 60)

if __name__ == '__main__':
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("Press Enter to start tests...")
    input()
    
    test_api()
