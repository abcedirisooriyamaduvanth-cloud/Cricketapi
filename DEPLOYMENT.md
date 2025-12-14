# Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] Firebase integration tested and working
- [x] Scraper script created with Playwright
- [x] GitHub Actions workflow configured for 40-minute intervals
- [x] Documentation complete

## 🚀 Deployment Steps

### 1. Configure GitHub Secrets

Go to your repository on GitHub:
```
Settings → Secrets and variables → Actions → New repository secret
```

Add these secrets:

| Name | Value | Required |
|------|-------|----------|
| `FIREBASE_URL` | `https://cricket-stream-portal-default-rtdb.firebaseio.com` | Yes |
| `FIREBASE_AUTH` | Your Firebase auth token | No (only if database requires auth) |

### 2. Push Code to GitHub

```bash
git add .
git commit -m "Add cricket stream scraper automation"
git push origin main
```

### 3. Enable GitHub Actions

1. Go to repository **Settings** → **Actions** → **General**
2. Under "Actions permissions", select **Allow all actions and reusable workflows**
3. Click **Save**

### 4. Test the Workflow

#### Manual Test:
1. Go to **Actions** tab
2. Click **"Scrape Cricket Streams"** workflow
3. Click **"Run workflow"** dropdown
4. Select branch (usually `main`)
5. Click **"Run workflow"** button

#### Monitor Progress:
- Click on the running workflow
- View real-time logs
- Wait ~3-5 minutes for completion

#### Check Results:
1. **Workflow Logs**: See scraping output and any errors
2. **Firebase Console**: Check for new data at your Firebase URL
3. **Artifacts**: Download `scrape-results-X` to see JSON output

### 5. Verify Automation

The workflow will now run automatically every 40 minutes.

Check scheduled runs:
- Go to **Actions** tab
- Look for runs with ⏰ icon (scheduled)
- Verify they run every 40 minutes

## 📊 Monitoring

### Check Workflow Status
```
Actions tab → Scrape Cricket Streams → View runs
```

### Check Firebase Data
Visit: `https://cricket-stream-portal-default-rtdb.firebaseio.com/.json`

Expected structure:
```json
{
  "2ndserverlink": {
    "source_url": "...",
    "link": "https://...m3u8",
    "headers": {...},
    "status": "OK",
    "createdAt": 1765715426393,
    ...
  }
}
```

### Download Artifacts
Each workflow run saves results as artifacts (kept for 7 days):
- Go to completed workflow run
- Scroll to **Artifacts** section
- Download `scrape-results-X.zip`

## 🔧 Troubleshooting

### No m3u8 Links Found

**Solution 1**: Increase wait time
Edit `scraper_playwright.py`, line ~120:
```python
time.sleep(20)  # Increase to 30 or 40
```

**Solution 2**: Add debug output
The scraper already prints detailed logs. Check workflow logs for:
- Page loading status
- Iframe detection
- Play button clicks
- Network requests

### Workflow Not Running

**Check**:
1. GitHub Actions is enabled (Settings → Actions)
2. Workflow file is in `.github/workflows/`
3. Cron syntax is correct: `*/40 * * * *`

**Note**: First scheduled run may take up to 40 minutes after push

### Firebase Save Fails

**Check**:
1. `FIREBASE_URL` secret is correct
2. Firebase database allows writes
3. Check workflow logs for error messages

### Rate Limiting

If scraping multiple URLs, add delays:
```python
time.sleep(10)  # Between each stream
```

## 📝 Adding More Streams

Edit `scraper_playwright.py`:

```python
STREAM_URLS = [
    {
        "url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
        "name": "Willow Cricket Extra",
        "title": "Watch Stream Live Cricket on Willow Tv - CricHD"
    },
    {
        "url": "https://your-new-stream.com/live",
        "name": "New Stream Name",
        "title": "New Stream Title"
    }
]
```

Commit and push:
```bash
git add scraper_playwright.py
git commit -m "Add new stream URL"
git push
```

## 🔄 Changing Schedule

Edit `.github/workflows/scrape-streams.yml`:

```yaml
schedule:
  - cron: '*/40 * * * *'  # Every 40 minutes
  # - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 * * * *'     # Every hour
  # - cron: '0 */2 * * *'   # Every 2 hours
```

Cron syntax: `minute hour day month weekday`

## 📞 Support

If issues persist:
1. Check workflow logs for detailed error messages
2. Verify website structure hasn't changed
3. Test with different stream URLs
4. Increase wait times for slow-loading sites
