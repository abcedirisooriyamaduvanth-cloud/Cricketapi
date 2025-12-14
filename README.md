# Cricket Stream Scraper

Automated scraper that extracts m3u8 streaming links from cricket streaming sites and saves them to Firebase RTDB.

## Features

- Scrapes m3u8 links from cricket streaming sites
- Captures network headers (Origin, Referer, User-Agent)
- Saves to Firebase Realtime Database
- Runs automatically every 40 minutes via GitHub Actions
- Handles ads and redirections

## Setup

### 1. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `FIREBASE_URL`: Your Firebase RTDB URL (e.g., `https://cricket-stream-portal-default-rtdb.firebaseio.com`)
- `FIREBASE_AUTH`: Your Firebase authentication token (optional, if database requires auth)

### 2. Add Stream URLs

Edit `scraper.py` and modify the `STREAM_URLS` list:

```python
STREAM_URLS = [
    {
        "url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
        "name": "Willow Cricket Extra",
        "title": "Watch Stream Live Cricket on Willow Tv - CricHD"
    },
    # Add more URLs here
]
```

### 3. Enable GitHub Actions

The workflow runs automatically every 40 minutes. You can also trigger it manually:

1. Go to Actions tab in your repository
2. Select "Scrape Cricket Streams"
3. Click "Run workflow"

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FIREBASE_URL="https://cricket-stream-portal-default-rtdb.firebaseio.com"
export FIREBASE_AUTH="your_auth_token"

# Run scraper
python scraper.py
```

## Firebase Data Structure

Data is saved to Firebase with the following structure:

```json
{
  "2ndserverlink": {
    "source_url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
    "title": "Watch Stream Live Cricket on Willow Tv - CricHD",
    "name": "Willow Cricket Extra",
    "link": "https://example.com/stream.m3u8",
    "headers": {
      "Origin": "https://bhalocast.com",
      "Referer": "https://bhalocast.com/",
      "User-Agent": "Mozilla/5.0..."
    },
    "status": "OK",
    "thumblink": "",
    "createdAt": 1760138418232,
    "createdAtISO": "2025-10-10T23:20:18Z",
    "lastCheckedAt": 1760138418232
  }
}
```

## How It Works

1. Uses Selenium with headless Chrome to navigate streaming sites
2. Captures network traffic using Chrome DevTools Protocol
3. Extracts m3u8 URLs and associated headers from network logs
4. Saves data to Firebase RTDB with timestamp
5. Runs every 40 minutes via GitHub Actions cron schedule

## Troubleshooting

- **No m3u8 links found**: Site may have changed structure or requires additional wait time
- **Firebase save fails**: Check FIREBASE_URL and FIREBASE_AUTH secrets
- **Workflow not running**: Ensure GitHub Actions is enabled in repository settings