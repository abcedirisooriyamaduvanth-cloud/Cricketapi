#!/usr/bin/env python3
"""
Ultimate cricket stream scraper - captures EVERYTHING
"""
import os
import json
import time
import re
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
    """Ultimate scraping - capture EVERYTHING"""
    print(f"\nScraping: {stream_config['url']}")
    
    # Store ALL URLs
    all_requests = []
    all_responses = []
    m3u8_candidates = []
    
    try:
        browser = playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--autoplay-policy=no-user-gesture-required'
            ]
        )
        
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            ignore_https_errors=True,
            java_script_enabled=True
        )
        
        page = context.new_page()
        
        # Capture EVERYTHING
        def on_request(request):
            url = request.url
            all_requests.append(url)
            
            # Check for m3u8 in URL (case insensitive)
            if 'm3u8' in url.lower() or '.ts' in url.lower():
                headers = request.headers
                m3u8_candidates.append({
                    'type': 'request',
                    'link': url,
                    'headers': {
                        'Origin': headers.get('origin', headers.get('Origin', '')),
                        'Referer': headers.get('referer', headers.get('Referer', '')),
                        'User-Agent': headers.get('user-agent', headers.get('User-Agent', ''))
                    },
                    'timestamp': time.time()
                })
                print(f"   🎯 REQUEST: {url[:100]}")
        
        def on_response(response):
            url = response.url
            all_responses.append(url)
            
            # Check URL and content-type
            if 'm3u8' in url.lower() or '.ts' in url.lower():
                request = response.request
                headers = request.headers
                content_type = response.headers.get('content-type', '')
                
                m3u8_candidates.append({
                    'type': 'response',
                    'link': url,
                    'content_type': content_type,
                    'headers': {
                        'Origin': headers.get('origin', headers.get('Origin', '')),
                        'Referer': headers.get('referer', headers.get('Referer', '')),
                        'User-Agent': headers.get('user-agent', headers.get('User-Agent', ''))
                    },
                    'timestamp': time.time()
                })
                print(f"   🎯 RESPONSE: {url[:100]}")
            
            # Also check content-type for HLS
            if 'mpegurl' in response.headers.get('content-type', '').lower():
                request = response.request
                headers = request.headers
                m3u8_candidates.append({
                    'type': 'response-content-type',
                    'link': url,
                    'content_type': response.headers.get('content-type', ''),
                    'headers': {
                        'Origin': headers.get('origin', headers.get('Origin', '')),
                        'Referer': headers.get('referer', headers.get('Referer', '')),
                        'User-Agent': headers.get('user-agent', headers.get('User-Agent', ''))
                    },
                    'timestamp': time.time()
                })
                print(f"   🎯 HLS CONTENT-TYPE: {url[:100]}")
        
        page.on('request', on_request)
        page.on('response', on_response)
        
        # Navigate
        print("   Loading page...")
        page.goto(stream_config['url'], wait_until='networkidle', timeout=60000)
        
        print("   Initial wait (10s)...")
        time.sleep(10)
        
        # Interact with page
        print("   Interacting with page...")
        frames = page.frames
        print(f"   Found {len(frames)} frames")
        
        for idx, frame in enumerate(frames):
            try:
                # Execute aggressive JavaScript
                frame.evaluate("""
                    () => {
                        // Play all videos
                        document.querySelectorAll('video').forEach(v => {
                            v.muted = true;
                            v.play().catch(() => {});
                            v.click();
                        });
                        
                        // Click everything
                        document.querySelectorAll('button, [role="button"], [class*="play"], [id*="play"]').forEach(el => {
                            try { el.click(); } catch(e) {}
                        });
                    }
                """)
            except:
                pass
        
        # Long wait with progress
        print("   Waiting for streams (60s)...")
        for i in range(12):  # 12 x 5s = 60s
            time.sleep(5)
            if m3u8_candidates:
                print(f"   Found {len(m3u8_candidates)} candidate(s) after {(i+1)*5}s!")
            else:
                print(f"   Still waiting... ({(i+1)*5}s)")
        
        browser.close()
        
        # Debug output
        print(f"\n   📊 Debug Info:")
        print(f"   Total requests: {len(all_requests)}")
        print(f"   Total responses: {len(all_responses)}")
        print(f"   M3U8 candidates: {len(m3u8_candidates)}")
        
        # Show ALL m3u8 candidates
        if m3u8_candidates:
            print(f"\n   🎯 All M3U8/TS URLs found:")
            for idx, candidate in enumerate(m3u8_candidates, 1):
                print(f"   {idx}. [{candidate['type']}] {candidate['link']}")
        
        # Filter for actual m3u8 playlists (not .ts segments)
        m3u8_playlists = [c for c in m3u8_candidates if '.m3u8' in c['link'].lower()]
        
        if m3u8_playlists:
            print(f"\n   ✅ Found {len(m3u8_playlists)} m3u8 playlist(s)")
            
            # Prefer master playlists, then any m3u8
            master = [m for m in m3u8_playlists if 'master' in m['link'].lower()]
            if master:
                latest = master[-1]
                print(f"   Using master playlist")
            else:
                latest = m3u8_playlists[-1]
                print(f"   Using latest m3u8")
            
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
            
            print(f"\n✅ SUCCESS!")
            print(f"   Link: {latest['link']}")
            print(f"   Headers: {list(latest['headers'].keys())}")
            return result
        else:
            print(f"\n❌ No m3u8 playlists found")
            if m3u8_candidates:
                print(f"   Found {len(m3u8_candidates)} .ts segments but no .m3u8 playlist")
                print(f"   This might mean the playlist loaded before we started listening")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main scraper function"""
    print("=" * 70)
    print("Cricket Stream Scraper - ULTIMATE MODE")
    print("Captures ALL network traffic including .m3u8 and .ts files")
    print("=" * 70)
    print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 70)
    
    results = []
    
    with sync_playwright() as playwright:
        for idx, stream_config in enumerate(STREAM_URLS):
            print(f"\n[{idx + 1}/{len(STREAM_URLS)}]")
            result = scrape_stream(stream_config, playwright)
            
            if result:
                server_key = f"{idx + 1}ndserverlink" if idx == 0 else f"{idx + 1}rdserverlink"
                if idx >= 2:
                    server_key = f"{idx + 1}thserverlink"
                
                save_to_firebase(result, server_key)
                results.append(result)
    
    print("\n" + "=" * 70)
    print(f"Scraping complete. Found {len(results)}/{len(STREAM_URLS)} streams.")
    print("=" * 70)
    
    if results:
        with open('scrape_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n✅ Results saved to: scrape_results.json")
        
        for r in results:
            print(f"\n✅ {r['name']}")
            print(f"   Link: {r['link']}")
            print(f"   Headers: {list(r['headers'].keys())}")
    else:
        print("\n❌ No m3u8 playlists captured")
        print("\nIf you saw .ts segments in the output above,")
        print("the .m3u8 playlist may have loaded before we started listening.")
        print("\nTry:")
        print("  1. Increase initial wait time before interaction")
        print("  2. Reload page after setting up listeners")
        print("  3. Check if site uses dynamic m3u8 generation")

if __name__ == '__main__':
    main()
