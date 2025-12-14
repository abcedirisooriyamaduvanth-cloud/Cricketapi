# Quick Start Guide

Get your cricket stream scraper running in 5 minutes!

## 📋 Prerequisites

- GitHub account
- Firebase Realtime Database URL
- Git installed locally (or use GitHub web interface)

## 🚀 Setup (5 Steps)

### Step 1: Add GitHub Secrets (2 min)

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add:
   - Name: `FIREBASE_URL`
   - Value: `https://cricket-stream-portal-default-rtdb.firebaseio.com`
5. Click **Add secret**

### Step 2: Push Code to GitHub (1 min)

```bash
git add .
git commit -m "Add cricket stream scraper"
git push origin main
```

Or use GitHub web interface to upload files.

### Step 3: Enable GitHub Actions (30 sec)

1. Go to **Settings** → **Actions** → **General**
2. Select **Allow all actions and reusable workflows**
3. Click **Save**

### Step 4: Run First Test (30 sec)

1. Go to **Actions** tab
2. Click **Scrape Cricket Streams**
3. Click **Run workflow** → **Run workflow**

### Step 5: Check Results (1 min)

Wait 3-5 minutes, then:
- ✅ Check workflow logs for success messages
- ✅ Visit Firebase URL to see scraped data
- ✅ Download artifacts for JSON results

## 🎉 Done!

Your scraper now runs automatically every 40 minutes!

## 📊 What Happens Next?

Every 40 minutes, the scraper will:
1. Visit cricket streaming sites
2. Extract m3u8 links and headers
3. Save to Firebase with timestamp
4. Store results as artifacts

## 🔍 Monitor Your Scraper

### View Logs
```
Actions tab → Scrape Cricket Streams → Latest run → View logs
```

### Check Firebase
```
https://cricket-stream-portal-default-rtdb.firebaseio.com/.json
```

### Download Results
```
Actions tab → Completed run → Artifacts section → Download
```

## ➕ Add More Streams

Edit `scraper_playwright.py`:

```python
STREAM_URLS = [
    {
        "url": "https://your-stream-url.com",
        "name": "Stream Name",
        "title": "Stream Title"
    }
]
```

Commit and push:
```bash
git add scraper_playwright.py
git commit -m "Add new stream"
git push
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| No m3u8 found | Increase wait time in scraper (line 120) |
| Workflow not running | Check Actions is enabled in Settings |
| Firebase error | Verify FIREBASE_URL secret is correct |

## 📚 More Info

- **Full Documentation**: See [README.md](README.md)
- **Testing Guide**: See [TESTING.md](TESTING.md)
- **Deployment Details**: See [DEPLOYMENT.md](DEPLOYMENT.md)

## 💡 Tips

- First scheduled run takes up to 40 minutes after push
- Check workflow logs for detailed debugging info
- Artifacts are kept for 7 days
- You can manually trigger runs anytime from Actions tab
