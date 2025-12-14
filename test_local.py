#!/usr/bin/env python3
"""
Local test script - tests Firebase connection without browser automation
"""
import os
import json
import time
from datetime import datetime
import requests

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

FIREBASE_URL = os.getenv('FIREBASE_URL', 'https://cricket-stream-portal-default-rtdb.firebaseio.com')
FIREBASE_AUTH = os.getenv('FIREBASE_AUTH', '')

def test_firebase_connection():
    """Test Firebase connection by reading data"""
    print("Testing Firebase connection...")
    
    try:
        url = f"{FIREBASE_URL}/.json"
        if FIREBASE_AUTH:
            url += f"?auth={FIREBASE_AUTH}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Firebase connection successful!")
            print(f"   Status: {response.status_code}")
            data = response.json()
            if data:
                print(f"   Existing keys: {list(data.keys())}")
            else:
                print(f"   Database is empty (this is OK)")
            return True
        else:
            print(f"❌ Firebase connection failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to Firebase: {str(e)}")
        return False

def test_firebase_write():
    """Test writing data to Firebase"""
    print("\nTesting Firebase write...")
    
    test_data = {
        'source_url': 'https://test.example.com',
        'title': 'Test Stream',
        'name': 'Test',
        'link': 'https://test.example.com/stream.m3u8',
        'headers': {
            'Origin': 'https://test.com',
            'Referer': 'https://test.com/',
            'User-Agent': 'Mozilla/5.0 Test'
        },
        'status': 'TEST',
        'thumblink': '',
        'createdAt': int(time.time() * 1000),
        'createdAtISO': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'lastCheckedAt': int(time.time() * 1000)
    }
    
    try:
        url = f"{FIREBASE_URL}/testserverlink.json"
        if FIREBASE_AUTH:
            url += f"?auth={FIREBASE_AUTH}"
        
        response = requests.put(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Firebase write successful!")
            print(f"   Data written to: testserverlink")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Firebase write failed!")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error writing to Firebase: {str(e)}")
        return False

def test_firebase_read_specific():
    """Read the test data we just wrote"""
    print("\nReading test data from Firebase...")
    
    try:
        url = f"{FIREBASE_URL}/testserverlink.json"
        if FIREBASE_AUTH:
            url += f"?auth={FIREBASE_AUTH}"
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Read successful!")
            print(f"   Data: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"❌ Read failed!")
            print(f"   Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading from Firebase: {str(e)}")
        return False

def cleanup_test_data():
    """Delete test data"""
    print("\nCleaning up test data...")
    
    try:
        url = f"{FIREBASE_URL}/testserverlink.json"
        if FIREBASE_AUTH:
            url += f"?auth={FIREBASE_AUTH}"
        
        response = requests.delete(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Test data cleaned up")
            return True
        else:
            print(f"⚠️  Could not clean up test data (status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"⚠️  Error cleaning up: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Cricket Stream Scraper - Local Test")
    print("=" * 60)
    print(f"\nFirebase URL: {FIREBASE_URL}")
    print(f"Firebase Auth: {'Set' if FIREBASE_AUTH else 'Not set (public database)'}")
    print()
    
    # Run tests
    tests_passed = 0
    tests_total = 4
    
    if test_firebase_connection():
        tests_passed += 1
    
    if test_firebase_write():
        tests_passed += 1
    
    if test_firebase_read_specific():
        tests_passed += 1
    
    if cleanup_test_data():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    print("=" * 60)
    
    if tests_passed == tests_total:
        print("\n✅ All tests passed! Ready to run full scraper.")
        print("\nNext steps:")
        print("1. Run: python scraper.py")
        print("2. Check Firebase for scraped data")
        print("3. If successful, push to GitHub")
    else:
        print("\n❌ Some tests failed. Check Firebase configuration.")
        print("\nTroubleshooting:")
        print("1. Verify FIREBASE_URL in .env file")
        print("2. Check if database requires authentication")
        print("3. If auth required, add FIREBASE_AUTH token to .env")

if __name__ == '__main__':
    main()
