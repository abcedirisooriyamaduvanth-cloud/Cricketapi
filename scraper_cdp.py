#!/usr/bin/env python3
"""
Cricket stream scraper using Chrome DevTools Protocol for better network capture
"""
import os
import json
import time
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright

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
    """Scrape using CDP for network monitoring"""
    print(f"\nScraping: {stream_config['url']}")
    
    m3u8_requests = []
    
    try:
        # Launch browser with CDP
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True
        )
        
        # Create CDP session
        page = context.new_page()
        cdp = page.context.new_cdp_session(page)
        
        # Enable network tracking
        cdp.send('Network.enable')
        
        # Store network requests
        network_requests = []
        
        def on_request(params):
            url = params.get('request', {}).get('url', '')
            if '.m3u8' in url.lower():
                headers = params.get('request', {}).get('headers', {})
                network_requests.append({
                    'url': url,
                    'headers': headers,
                    'timestamp': time.time()
                })
                print(f"   ✅ CDP captured m3u8: {url[:80]}...")
        
        cdp.on('Network.requestWillBeSent', on_request)
        
        # Navigate to page
        print("   Loading page...")
        page.goto(stream_config['url'], wait_until='networkidle', timeout=60000)
        
        print("   Waiting for stream...")
        time.sleep(10)
        
        # Try to interact with page
        print("   Looking for video elements...")
        try:
            # Try to find and click video or play button
            page.evaluate("""
                () => {
                    // Try to find video elements
                    const videos = document.querySelectorAll('video');
                    videos.forEach(v => {
                        try {
                            v.play();
                            v.click();
                        } catch(e) {}
                    });
                    
                    // Try to find play buttons
                    const buttons = document.querySelectorAll('button, [class*="play"]');
                    buttons.forEach(b => {
                        try {
                            b.click();
                        } catch(e) {}
                    });
                    
                    // Try iframes
                    const iframes = document.querySelectorAll('iframe');
                    iframes.forEach(iframe => {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            const iframeVideos = iframeDoc.querySelectorAll('video');
                            iframeVideos.forEach(v => {
                                try {
                                    v.play();
                                    v.click();
                                } catch(e) {}
                            });
                        } catch(e) {}
                    });
                }
            """)
            print("   Triggered play actions")
        except Exception as e:
            print(f"   Play trigger error: {e}")
        
        # Wait more for stream to load
        print("   Waiting for m3u8 requests...")
        time.sleep(30)
        
        # Process captured requests
        if network_requests:
            latest = max(network_requests, key=lambda x: x['timestamp'])
            
            result = {
                'source_url': stream_config['url'],
                'title': stream_config['title'],
                'name': stream_config['name'],
                'link': latest['url'],
                'headers': {
                    'Origin': latest['headers'].get('origin', latest['headers'].get('Origin', '')),
                    'Referer': latest['headers'].get('referer', latest['headers'].get('Referer', '')),
                    'User-Agent': latest['headers'].get('user-agent', latest['headers'].get('User-Agent', ''))
                },
                'status': 'OK',
                'thumblink': '',
                'createdAt': int(time.time() * 1000),
                'createdAtISO': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'lastCheckedAt': int(time.time() * 1000)
            }
            
            print(f"✅ Success! Found m3u8 link")
            print(f"   Link: {latest['url'][:80]}...")
            
            browser.close()
            return result
        else:
            print(f"❌ No m3u8 link found")
            browser.close()
            return None
            
    except Exception as e:
        print(f"❌ Error scraping: {str(e)}")
        return None

def main():
    """Main scraper function"""
    print("=" * 60)
    print("Cricket Stream Scraper (CDP Method)")
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
    else:
        print("\n⚠️  No m3u8 links found.")
        print("\nThis could mean:")
        print("  1. No live stream currently active")
        print("  2. Site requires manual interaction")
        print("  3. Stream uses different technology")
        print("\nTry:")
        print("  - Visit URL manually to check if stream works")
        print("  - Run during live cricket match")
        print("  - Try different stream URL")

if __name__ == '__main__':
    main()
