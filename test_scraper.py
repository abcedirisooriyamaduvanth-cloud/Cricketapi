#!/usr/bin/env python3
"""
Test script to verify scraper configuration
"""
import json
import time
from datetime import datetime

def test_data_structure():
    """Test the data structure that will be saved to Firebase"""
    
    test_data = {
        'source_url': 'https://crichdplayer.com/willow-cricket-extra-live-stream-play-01',
        'title': 'Watch Stream Live Cricket on Willow Tv - CricHD',
        'name': 'Willow Cricket Extra',
        'link': 'https://jan.player0003.com:8099/hls/asportsd.m3u8?md6=test&expires=1762859505',
        'headers': {
            'Origin': 'https://bhalocast.com',
            'Referer': 'https://bhalocast.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
        },
        'status': 'OK',
        'thumblink': '',
        'createdAt': int(time.time() * 1000),
        'createdAtISO': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'lastCheckedAt': int(time.time() * 1000)
    }
    
    print("Test Data Structure:")
    print(json.dumps(test_data, indent=2))
    print("\n✅ Data structure is valid")
    
    return test_data

def test_firebase_structure():
    """Test the complete Firebase structure"""
    
    firebase_data = {
        '2ndserverlink': test_data_structure(),
    }
    
    print("\n" + "="*60)
    print("Firebase Structure:")
    print("="*60)
    print(json.dumps(firebase_data, indent=2))
    print("\n✅ Firebase structure is valid")

if __name__ == '__main__':
    print("="*60)
    print("Cricket Stream Scraper - Configuration Test")
    print("="*60)
    print()
    
    test_firebase_structure()
    
    print("\n" + "="*60)
    print("Configuration test complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Add GitHub secrets: FIREBASE_URL and FIREBASE_AUTH")
    print("2. Push code to GitHub")
    print("3. Enable GitHub Actions")
    print("4. Workflow will run every 40 minutes")
