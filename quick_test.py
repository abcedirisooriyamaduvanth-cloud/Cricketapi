#!/usr/bin/env python3
"""
Quick test - simulates scraper without browser automation
"""
import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

FIREBASE_URL = os.getenv('FIREBASE_URL', 'https://cricket-stream-portal-default-rtdb.firebaseio.com')
FIREBASE_AUTH = os.getenv('FIREBASE_AUTH', '')

def save_to_firebase(data, server_key):
    """Save data to Firebase"""
    try:
        url = f"{FIREBASE_URL}/{server_key}.json"
        if FIREBASE_AUTH:
            url += f"?auth={FIREBASE_AUTH}"
        
        response = requests.put(url, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Saved to Firebase: {server_key}")
            print(f"   Link: {data['link']}")
            return True
        else:
            print(f"❌ Firebase error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Quick Test - Simulating Scraper Output")
    print("=" * 60)
    
    # Simulate scraped data (like what the real scraper would find)
    test_streams = [
        {
            'server_key': '2ndserverlink',
            'data': {
                'source_url': 'https://crichdplayer.com/willow-cricket-extra-live-stream-play-01',
                'title': 'Watch Stream Live Cricket on Willow Tv - CricHD',
                'name': 'Willow Cricket Extra',
                'link': 'https://jan.player0003.com:8099/hls/asportsd.m3u8?md6=test123&expires=1762859505',
                'headers': {
                    'Origin': 'https://bhalocast.com',
                    'Referer': 'https://bhalocast.com/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                'status': 'OK',
                'thumblink': '',
                'createdAt': int(time.time() * 1000),
                'createdAtISO': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'lastCheckedAt': int(time.time() * 1000)
            }
        },
        {
            'server_key': '3rdserverlink',
            'data': {
                'source_url': 'https://crichd.one/stream.php?id=willow',
                'title': 'Sri Lanka Vs Pakistan ODI',
                'name': 'Sri Lanka Vs Pakistan ODI',
                'link': 'https://jan.player0003.com:8099/hls/tenspk.m3u8?md6=test456&expires=1762859629',
                'headers': {
                    'Origin': 'https://bhalocast.com',
                    'Referer': 'https://bhalocast.com/',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                'status': 'OK',
                'thumblink': 'https://img-s-msn-com.akamaized.net/tenant/amp/entityid/AA1QaGWE.img',
                'createdAt': int(time.time() * 1000),
                'createdAtISO': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'lastCheckedAt': int(time.time() * 1000)
            }
        }
    ]
    
    print(f"\nFirebase URL: {FIREBASE_URL}")
    print(f"Testing with {len(test_streams)} simulated streams...\n")
    
    success_count = 0
    for stream in test_streams:
        print(f"\nSaving {stream['server_key']}...")
        if save_to_firebase(stream['data'], stream['server_key']):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{len(test_streams)} streams saved")
    print("=" * 60)
    
    if success_count == len(test_streams):
        print("\n✅ SUCCESS! Firebase integration working!")
        print("\nYou can now:")
        print("1. Check your Firebase database for the test data")
        print("2. Run the full scraper: python scraper.py")
        print("3. Push to GitHub when ready")
    else:
        print("\n⚠️  Some saves failed. Check Firebase permissions.")

if __name__ == '__main__':
    main()
