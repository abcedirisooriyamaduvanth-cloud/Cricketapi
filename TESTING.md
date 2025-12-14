# Testing Guide

## Local Testing (Completed)

✅ **Firebase Integration Test** - `quick_test.py`
- Successfully saved test data to Firebase
- Verified data structure matches requirements
- Confirmed write permissions work

## GitHub Actions Testing (Required)

The scraper requires a full browser environment which is available in GitHub Actions but not in this dev container.

### Steps to Test on GitHub:

1. **Add GitHub Secrets**:
   ```
   Repository Settings → Secrets and variables → Actions
   
   Add:
   - FIREBASE_URL: https://cricket-stream-portal-default-rtdb.firebaseio.com
   - FIREBASE_AUTH: (leave empty if not needed)
   ```

2. **Push Code to GitHub**:
   ```bash
   git add .
   git commit -m "Add cricket stream scraper with Playwright"
   git push
   ```

3. **Manual Test Run**:
   - Go to: Actions tab
   - Click: "Scrape Cricket Streams"
   - Click: "Run workflow" button
   - Select: main branch
   - Click: "Run workflow"

4. **Check Results** (after ~3-5 minutes):
   - View workflow logs for scraping output
   - Check Firebase database for new data
   - Download artifacts to see `scrape_results.json`

5. **Verify Automation**:
   - Workflow will run automatically every 40 minutes
   - Check Actions tab for scheduled runs
   - Monitor Firebase for updated data

## Expected Output

When successful, you should see in logs:
```
Scraping: https://crichdplayer.com/willow-cricket-extra-live-stream-play-01
   Loading page...
   Checking for iframes...
   Found X frame(s)
   Looking for play button...
   Waiting for stream to load...
   Found m3u8: https://d10.merichunidya.com:1686/hls/willowextra.m3u8...
✅ Success! Found m3u8 link
✅ Saved to Firebase: 2ndserverlink
```

## Troubleshooting

If no m3u8 links found:
1. Increase wait time in `scraper_playwright.py` (line with `time.sleep(20)`)
2. Check if website structure changed
3. Add more stream URLs to test different sources

## Adding More Streams

Edit `scraper_playwright.py`:
```python
STREAM_URLS = [
    {
        "url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
        "name": "Willow Cricket Extra",
        "title": "Watch Stream Live Cricket on Willow Tv - CricHD"
    },
    {
        "url": "https://your-stream-url-here.com",
        "name": "Stream Name",
        "title": "Stream Title"
    }
]
```
