# Troubleshooting Guide

## Issue: No m3u8 Links Found

### Possible Causes

1. **No Active Stream**
   - The streaming site may not have a live stream at the moment
   - Cricket streams are typically only active during live matches
   
2. **Site Structure Changed**
   - Streaming sites frequently change their structure
   - May require scraper updates

3. **Timing Issues**
   - Stream may take longer to load than current wait time
   - Network conditions may vary

4. **Different Streaming Technology**
   - Site may use WebRTC, DASH, or other protocols instead of HLS/m3u8

## Solutions

### 1. Verify Stream is Active

**Manual Test:**
1. Visit the URL in your browser: `https://crichdplayer.com/willow-cricket-extra-live-stream-play-01`
2. Open Developer Tools (F12)
3. Go to Network tab
4. Filter by "m3u8"
5. Play the video
6. Check if m3u8 requests appear

**If you see m3u8 requests manually:**
- The scraper should work, try increasing wait times
- Note the exact URL pattern and headers

**If you don't see m3u8 requests:**
- Stream may not be active
- Try during a live cricket match
- Site may use different streaming method

### 2. Increase Wait Times

Edit `scraper_playwright.py` or `scraper_cdp.py`:

```python
# Line ~120 - Increase from 30 to 45 seconds
time.sleep(45)
```

### 3. Try Alternative Scraper

We have two scraper versions:

**Standard Playwright** (`scraper_playwright.py`):
```bash
python scraper_playwright.py
```

**CDP Method** (`scraper_cdp.py`):
```bash
python scraper_cdp.py
```

Update workflow to use CDP version:
```yaml
- name: Run scraper
  run: |
    python scraper_cdp.py
```

### 4. Test with Different URLs

Add more stream sources in the scraper:

```python
STREAM_URLS = [
    {
        "url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
        "name": "Willow Cricket Extra",
        "title": "Watch Stream Live Cricket on Willow Tv - CricHD"
    },
    {
        "url": "https://crichd.one/stream.php?id=willow",
        "name": "CricHD Willow",
        "title": "Willow Cricket Stream"
    },
    {
        "url": "https://your-alternative-stream.com",
        "name": "Alternative Stream",
        "title": "Alternative Cricket Stream"
    }
]
```

### 5. Debug Network Requests

The improved scraper shows debug info:

```
Total requests captured: 150
Video-related requests: 5
  - https://example.com/video.m3u8
  - https://example.com/stream.ts
```

If you see video-related requests but no m3u8:
- Site may use .ts segments directly
- May need to modify detection logic

### 6. Check During Live Match

**Best Time to Test:**
- During live cricket matches
- Peak viewing hours
- When you can manually verify stream works

**Schedule Considerations:**
- Workflow runs every 40 minutes
- May catch streams during matches
- Will fail when no match is live (this is expected)

## Common Error Messages

### "No m3u8 link found"

**Meaning**: Scraper ran but didn't detect m3u8 requests

**Solutions**:
1. Verify stream is active manually
2. Increase wait time
3. Try during live match
4. Use alternative scraper (CDP version)

### "Failed to install browser dependencies"

**Meaning**: System packages missing

**Solution**: Already fixed in workflow with t64 packages

### "Firebase error: 401"

**Meaning**: Firebase authentication issue

**Solutions**:
1. Check FIREBASE_URL is correct
2. Add FIREBASE_AUTH if database requires it
3. Verify Firebase rules allow writes

### "Timeout waiting for page"

**Meaning**: Page took too long to load

**Solutions**:
1. Increase timeout in goto():
   ```python
   page.goto(url, timeout=90000)  # 90 seconds
   ```
2. Check if site is accessible
3. May need proxy if site blocks datacenter IPs

## Advanced Debugging

### Enable Verbose Logging

Add to scraper:

```python
# At top of file
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Save Page Screenshot

Add before closing browser:

```python
page.screenshot(path='debug_screenshot.png')
print("Screenshot saved: debug_screenshot.png")
```

### Save Page HTML

```python
html = page.content()
with open('debug_page.html', 'w') as f:
    f.write(html)
print("HTML saved: debug_page.html")
```

### Capture All Network Requests

```python
def log_all_requests(request):
    print(f"Request: {request.url}")

page.on('request', log_all_requests)
```

## Site-Specific Issues

### CricHD Sites

**Known Issues:**
- Multiple redirects through different domains
- Heavy ad injection
- May require specific referer headers

**Solutions:**
- Wait longer for redirects to complete
- Disable ad blockers (they may interfere)
- Ensure referer header is set correctly

### Iframe-Heavy Sites

**Known Issues:**
- Stream may be in nested iframes
- Cross-origin restrictions

**Solutions:**
- Scraper already handles iframes
- May need to disable web security (already done)

## When to Give Up

If after trying all solutions:
1. Manual browser test shows no m3u8
2. Multiple stream URLs fail
3. Site uses WebRTC or other non-HLS tech

**Alternative Approaches:**
- Use different streaming sites
- Look for sites that use HLS/m3u8
- Consider using official streaming APIs if available

## Success Indicators

You know it's working when you see:

```
✅ Found m3u8: https://d10.merichunidya.com:1686/hls/willowextra.m3u8...
✅ Success! Found m3u8 link
   Link: https://d10.merichunidya.com:1686/hls/willowextra.m3u8...
   Headers: ['Origin', 'Referer', 'User-Agent']
✅ Saved to Firebase: 2ndserverlink
```

## Getting Help

If still stuck:

1. **Check workflow logs** for exact error messages
2. **Test manually** in browser during live match
3. **Try different URLs** from working cricket streaming sites
4. **Verify Firebase** connection with `quick_test.py`
5. **Check timing** - run during live cricket matches

## Expected Behavior

**Normal Operation:**
- ✅ Finds m3u8 during live matches
- ❌ Fails when no stream active (expected)
- ✅ Saves to Firebase when successful
- ⚠️ May have intermittent failures (sites change frequently)

**This is OK:**
- Some runs fail (no active stream)
- Different URLs work at different times
- Need to update URLs occasionally

**This needs fixing:**
- All runs fail during known live matches
- Firebase saves fail
- Workflow doesn't run at all
