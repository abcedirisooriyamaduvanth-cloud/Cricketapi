#!/usr/bin/env python3
"""
Cricket stream scraper using Playwright - more reliable for automation
"""
import os
import json
import time
import re
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Firebase configuration
FIREBASE_URL = os.getenv('FIREBASE_URL', 'https://cricket-stream-portal-default-rtdb.firebaseio.com')
FIREBASE_AUTH = os.getenv('FIREBASE_AUTH', '')

# Stream URLs to scrape
STREAM_URLS = [
    {
        "url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
        "name": "Willow Cricket Extra",
        "title": "Watch Stream Live Cricket on Willow Tv - CricHD"
    }
]

def save_to_firebase(data, server_key):
    """Save scraped data to Firebase RTDB"""
    try:
        url = f"{FIREBASE_URL}/{server_key}.json"
        if FIREBASE_AUTH:
            url += f"?auth={FIREBASE_AUTH}"
        
        response = requests.put(url, json=data)
        
        if response.status_code == 200:
            print(f"✅ Saved to Firebase: {server_key}")
            return True
        else:
            print(f"❌ Firebase error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving to Firebase: {str(e)}")
        return False

def scrape_stream(stream_config, playwright):
    """Scrape a single stream URL for m3u8 links"""
    print(f"\nScraping: {stream_config['url']}")
    
    # Store captured m3u8 requests
    m3u8_requests = []
    
    def handle_request(request):
        """Capture m3u8 requests"""
        url = request.url
        if '.m3u8' in url.lower():
            headers = request.headers
            m3u8_requests.append({
                'link': url,
                'headers': {
                    'Origin': headers.get('origin', ''),
                    'Referer': headers.get('referer', ''),
                    'User-Agent': headers.get('user-agent', '')
                },
                'timestamp': time.time()
            })
            print(f"   Found m3u8: {url[:80]}...")
    
    try:
        # Launch browser
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        # Listen to network requests
        page.on('request', handle_request)
        
        # Navigate to page
        print("   Loading page...")
        page.goto(stream_config['url'], wait_until='domcontentloaded', timeout=30000)
        
        # Wait for initial load
        time.sleep(5)
        
        # Check for iframes
        print("   Checking for iframes...")
        iframes = page.frames
        print(f"   Found {len(iframes)} frame(s)")
        
        # Try to click play button in any frame
        print("   Looking for play button...")
        for frame in iframes:
            try:
                # Try multiple selectors
                selectors = [
                    'button.play',
                    '.play-button',
                    '[class*="play"]',
                    'button[aria-label*="play" i]',
                    '.vjs-big-play-button',
                    'video'
                ]
                
                for selector in selectors:
                    try:
                        element = frame.query_selector(selector)
                        if element and element.is_visible():
                            element.click()
                            print(f"   Clicked: {selector}")
                            time.sleep(2)
                            break
                    except:
                        continue
            except:
                continue
        
        # Wait for stream to load
        print("   Waiting for stream to load...")
        time.sleep(20)
        
        # Close browser
        browser.close()
        
        # Process results
        if m3u8_requests:
            # Get the most recent m3u8 link
            latest = max(m3u8_requests, key=lambda x: x['timestamp'])
            
            result = {
                'source_url': stream_config['url'],
                'title': stream_config['title'],
                'name': stream_config['name'],
                'link': latest['link'],
                'headers': latest['headers'],
                'status': 'OK',
                'thumblink': '',
                'createdAt': int(time.time() * 1000),
                'createdAtISO': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'lastCheckedAt': int(time.time() * 1000)
            }
            
            print(f"✅ Success! Found m3u8 link")
            print(f"   Link: {latest['link'][:80]}...")
            return result
        else:
            print(f"❌ No m3u8 link found")
            return None
            
    except Exception as e:
        print(f"❌ Error scraping: {str(e)}")
        return None

def main():
    """Main scraper function"""
    print("=" * 60)
    print("Cricket Stream Scraper (Playwright)")
    print("=" * 60)
    print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 60)
    
    # Load custom URLs from environment if provided
    custom_urls = os.getenv('STREAM_URLS_JSON')
    if custom_urls:
        try:
            STREAM_URLS.extend(json.loads(custom_urls))
        except:
            pass
    
    print(f"\nStreams to scrape: {len(STREAM_URLS)}")
    
    results = []
    
    with sync_playwright() as playwright:
        for idx, stream_config in enumerate(STREAM_URLS):
            print(f"\n[{idx + 1}/{len(STREAM_URLS)}]")
            result = scrape_stream(stream_config, playwright)
            
            if result:
                # Save to Firebase with server key
                server_key = f"{idx + 1}ndserverlink" if idx == 0 else f"{idx + 1}rdserverlink"
                if idx >= 2:
                    server_key = f"{idx + 1}thserverlink"
                
                save_to_firebase(result, server_key)
                results.append(result)
            
            # Wait between requests
            if idx < len(STREAM_URLS) - 1:
                print(f"\nWaiting 5 seconds before next stream...")
                time.sleep(5)
    
    print("\n" + "=" * 60)
    print(f"Scraping complete. Found {len(results)}/{len(STREAM_URLS)} streams.")
    print("=" * 60)
    
    # Save results to file
    if results:
        with open('scrape_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: scrape_results.json")
        
        print("\nSuccessful streams:")
        for r in results:
            print(f"  - {r['name']}: {r['link'][:60]}...")

if __name__ == '__main__':
    main()
