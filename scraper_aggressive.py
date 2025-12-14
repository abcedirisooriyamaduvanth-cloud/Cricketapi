#!/usr/bin/env python3
"""
Aggressive cricket stream scraper - waits longer, tries harder
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
    """Aggressive scraping with multiple attempts"""
    print(f"\nScraping: {stream_config['url']}")
    
    m3u8_links = []
    all_urls = []
    
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
        
        # Capture ALL network activity
        def on_request(request):
            url = request.url
            all_urls.append(url)
            if '.m3u8' in url.lower():
                headers = request.headers
                m3u8_links.append({
                    'link': url,
                    'headers': {
                        'Origin': headers.get('origin', headers.get('Origin', '')),
                        'Referer': headers.get('referer', headers.get('Referer', '')),
                        'User-Agent': headers.get('user-agent', headers.get('User-Agent', ''))
                    },
                    'timestamp': time.time()
                })
                print(f"   ✅ FOUND M3U8: {url}")
        
        def on_response(response):
            url = response.url
            if '.m3u8' in url.lower() and url not in [m['link'] for m in m3u8_links]:
                request = response.request
                headers = request.headers
                m3u8_links.append({
                    'link': url,
                    'headers': {
                        'Origin': headers.get('origin', headers.get('Origin', '')),
                        'Referer': headers.get('referer', headers.get('Referer', '')),
                        'User-Agent': headers.get('user-agent', headers.get('User-Agent', ''))
                    },
                    'timestamp': time.time()
                })
                print(f"   ✅ FOUND M3U8 (response): {url}")
        
        page.on('request', on_request)
        page.on('response', on_response)
        
        # Navigate with long timeout
        print("   Loading page (60s timeout)...")
        page.goto(stream_config['url'], wait_until='networkidle', timeout=60000)
        
        print("   Initial wait (10s)...")
        time.sleep(10)
        
        # Get all iframes
        print("   Analyzing page structure...")
        frames = page.frames
        print(f"   Found {len(frames)} frames")
        
        # Try to interact with EVERY frame
        for idx, frame in enumerate(frames):
            try:
                print(f"   Checking frame {idx + 1}...")
                
                # Try to find video elements
                videos = frame.query_selector_all('video')
                if videos:
                    print(f"     Found {len(videos)} video element(s)")
                    for v_idx, video in enumerate(videos):
                        try:
                            video.click(timeout=1000)
                            print(f"     Clicked video {v_idx + 1}")
                            time.sleep(2)
                        except:
                            pass
                
                # Try to find and click ANY button
                buttons = frame.query_selector_all('button, [role="button"], .play, [class*="play"]')
                if buttons:
                    print(f"     Found {len(buttons)} button(s)")
                    for b_idx, button in enumerate(buttons[:5]):  # Try first 5 buttons
                        try:
                            if button.is_visible():
                                button.click(timeout=1000)
                                print(f"     Clicked button {b_idx + 1}")
                                time.sleep(2)
                        except:
                            pass
                
                # Execute JavaScript to force play
                try:
                    frame.evaluate("""
                        () => {
                            // Find all videos and try to play
                            document.querySelectorAll('video').forEach(v => {
                                v.muted = true;
                                v.play().catch(e => console.log('Play failed:', e));
                            });
                            
                            // Click everything that might be a play button
                            document.querySelectorAll('[class*="play"], [id*="play"], button').forEach(el => {
                                try { el.click(); } catch(e) {}
                            });
                        }
                    """)
                    print(f"     Executed play script in frame {idx + 1}")
                except Exception as e:
                    print(f"     Script execution failed: {e}")
                
            except Exception as e:
                print(f"     Frame {idx + 1} error: {e}")
        
        # Long wait for stream to start
        print("   Waiting for stream to load (45s)...")
        for i in range(9):  # 9 x 5s = 45s
            time.sleep(5)
            if m3u8_links:
                print(f"   Found m3u8 after {(i+1)*5}s!")
                break
            print(f"   Still waiting... ({(i+1)*5}s)")
        
        # Debug info
        print(f"\n   Debug Info:")
        print(f"   Total URLs captured: {len(all_urls)}")
        
        # Show video-related URLs
        video_urls = [u for u in all_urls if any(x in u.lower() for x in ['.m3u8', '.ts', '.mp4', 'video', 'stream', 'hls', 'manifest'])]
        if video_urls:
            print(f"   Video-related URLs: {len(video_urls)}")
            for vu in video_urls[:10]:
                print(f"     - {vu}")
        
        # Show unique domains
        domains = set()
        for u in all_urls:
            try:
                from urllib.parse import urlparse
                domain = urlparse(u).netloc
                if domain:
                    domains.add(domain)
            except:
                pass
        print(f"   Unique domains: {len(domains)}")
        for d in list(domains)[:10]:
            print(f"     - {d}")
        
        browser.close()
        
        # Process results
        if m3u8_links:
            latest = max(m3u8_links, key=lambda x: x['timestamp'])
            
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
            
            print(f"\n✅ SUCCESS! Found m3u8 link")
            print(f"   Link: {latest['link']}")
            return result
        else:
            print(f"\n❌ No m3u8 link found after aggressive scraping")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main scraper function"""
    print("=" * 70)
    print("Cricket Stream Scraper - AGGRESSIVE MODE")
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
        print(f"\nResults saved to: scrape_results.json")
        
        for r in results:
            print(f"\n✅ {r['name']}")
            print(f"   Link: {r['link']}")
            print(f"   Headers: {list(r['headers'].keys())}")
    else:
        print("\n❌ No streams captured")
        print("\nThe debug info above shows what URLs were found.")
        print("If you see video-related URLs but no .m3u8, the site may use:")
        print("  - DASH (.mpd)")
        print("  - WebRTC")
        print("  - Direct .ts segments")
        print("  - Encrypted streams")

if __name__ == '__main__':
    main()
