#!/usr/bin/env python3
"""
Cricket stream scraper - extracts m3u8 links from streaming sites
"""
import os
import json
import time
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

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

def setup_driver():
    """Setup headless Chrome driver for scraping"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36')
    
    # Enable performance logging to capture network requests
    chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_m3u8_from_logs(driver):
    """Extract m3u8 links and headers from browser network logs"""
    logs = driver.get_log('performance')
    m3u8_data = []
    
    for entry in logs:
        try:
            log = json.loads(entry['message'])['message']
            
            # Look for network responses
            if log['method'] == 'Network.responseReceived':
                response = log['params']['response']
                url = response['url']
                
                # Check if URL contains m3u8
                if '.m3u8' in url:
                    headers = response.get('requestHeaders', {})
                    
                    # Extract relevant headers
                    extracted_headers = {}
                    for key in ['Origin', 'Referer', 'User-Agent']:
                        if key in headers:
                            extracted_headers[key] = headers[key]
                    
                    m3u8_data.append({
                        'link': url,
                        'headers': extracted_headers,
                        'timestamp': time.time()
                    })
                    
        except Exception as e:
            continue
    
    return m3u8_data

def scrape_stream(stream_config):
    """Scrape a single stream URL for m3u8 links"""
    driver = None
    try:
        print(f"Scraping: {stream_config['url']}")
        driver = setup_driver()
        
        # Navigate to the page
        driver.get(stream_config['url'])
        
        # Wait for page to load and potential redirects
        time.sleep(10)
        
        # Try to find and click play button if exists
        try:
            play_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.play, .play-button, [class*="play"]'))
            )
            play_button.click()
            time.sleep(5)
        except:
            pass
        
        # Extract m3u8 links from network logs
        m3u8_data = extract_m3u8_from_logs(driver)
        
        if m3u8_data:
            # Get the most recent m3u8 link
            latest = max(m3u8_data, key=lambda x: x['timestamp'])
            
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
            
            print(f"✅ Found m3u8: {latest['link']}")
            return result
        else:
            print(f"❌ No m3u8 link found for {stream_config['url']}")
            return None
            
    except Exception as e:
        print(f"❌ Error scraping {stream_config['url']}: {str(e)}")
        return None
    finally:
        if driver:
            driver.quit()

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

def main():
    """Main scraper function"""
    print("=" * 60)
    print("Cricket Stream Scraper")
    print("=" * 60)
    
    # Load custom URLs from environment if provided
    custom_urls = os.getenv('STREAM_URLS_JSON')
    if custom_urls:
        try:
            STREAM_URLS.extend(json.loads(custom_urls))
        except:
            pass
    
    results = []
    
    for idx, stream_config in enumerate(STREAM_URLS):
        result = scrape_stream(stream_config)
        
        if result:
            # Save to Firebase with server key
            server_key = f"{idx + 1}ndserverlink" if idx == 0 else f"{idx + 1}rdserverlink"
            save_to_firebase(result, server_key)
            results.append(result)
        
        # Wait between requests to avoid rate limiting
        if idx < len(STREAM_URLS) - 1:
            time.sleep(5)
    
    print("=" * 60)
    print(f"Scraping complete. Found {len(results)} streams.")
    print("=" * 60)
    
    # Save results to file for debugging
    with open('scrape_results.json', 'w') as f:
        json.dump(results, f, indent=2)

if __name__ == '__main__':
    main()
