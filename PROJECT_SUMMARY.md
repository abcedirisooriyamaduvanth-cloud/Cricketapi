# Cricket Stream Scraper - Project Summary

## 🎯 What Was Built

An automated cricket stream scraper that:
- Extracts m3u8 streaming links from cricket websites
- Captures network headers (Origin, Referer, User-Agent)
- Saves data to Firebase Realtime Database
- Runs automatically every 40 minutes via GitHub Actions
- Handles ads, redirects, and iframes

## 📁 Project Structure

```
Cricketapi/
├── .github/
│   └── workflows/
│       └── scrape-streams.yml      # GitHub Actions workflow (40-min schedule)
├── scraper_playwright.py           # Main scraper using Playwright
├── quick_test.py                   # Firebase connection test
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore patterns
├── README.md                       # Main documentation
├── QUICKSTART.md                   # 5-minute setup guide
├── TESTING.md                      # Testing instructions
└── DEPLOYMENT.md                   # Deployment guide
```

## 🔧 Technology Stack

- **Language**: Python 3.11
- **Browser Automation**: Playwright (Chromium)
- **Database**: Firebase Realtime Database
- **CI/CD**: GitHub Actions
- **Schedule**: Cron (every 40 minutes)

## 🌊 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Every 40 min)            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              scraper_playwright.py                          │
│  1. Launch headless Chromium browser                        │
│  2. Navigate to cricket streaming site                      │
│  3. Handle iframes and redirects                            │
│  4. Capture network requests                                │
│  5. Extract m3u8 URLs + headers                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Firebase Realtime Database                     │
│  {                                                          │
│    "2ndserverlink": {                                       │
│      "link": "https://...m3u8",                             │
│      "headers": {...},                                      │
│      "status": "OK",                                        │
│      "createdAt": 1765715426393                             │
│    }                                                        │
│  }                                                          │
└─────────────────────────────────────────────────────────────┘
```

## 📊 Output Format

Each scraped stream is saved to Firebase with this structure:

```json
{
  "2ndserverlink": {
    "source_url": "https://crichdplayer.com/willow-cricket-extra-live-stream-play-01",
    "title": "Watch Stream Live Cricket on Willow Tv - CricHD",
    "name": "Willow Cricket Extra",
    "link": "https://d10.merichunidya.com:1686/hls/willowextra.m3u8?md5=...",
    "headers": {
      "Origin": "https://profamouslife.com",
      "Referer": "https://profamouslife.com/",
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    },
    "status": "OK",
    "thumblink": "",
    "createdAt": 1765715426393,
    "createdAtISO": "2025-12-14T12:30:26Z",
    "lastCheckedAt": 1765715426393
  }
}
```

## ✅ Features

### Core Features
- ✅ Automated scraping every 40 minutes
- ✅ Headless browser automation with Playwright
- ✅ Network request interception for m3u8 detection
- ✅ Header extraction (Origin, Referer, User-Agent)
- ✅ Firebase RTDB integration
- ✅ Iframe and redirect handling
- ✅ Manual workflow trigger support

### Reliability Features
- ✅ Error handling and logging
- ✅ Artifact storage (7-day retention)
- ✅ Detailed debug output
- ✅ Multiple selector fallbacks for play buttons
- ✅ Configurable wait times

### Developer Features
- ✅ Local testing script (quick_test.py)
- ✅ Environment variable configuration
- ✅ Comprehensive documentation
- ✅ Easy stream URL addition
- ✅ Customizable schedule

## 🚀 Deployment Checklist

- [ ] Add GitHub secrets (FIREBASE_URL, FIREBASE_AUTH)
- [ ] Push code to GitHub
- [ ] Enable GitHub Actions
- [ ] Run manual test
- [ ] Verify Firebase data
- [ ] Monitor first scheduled run

## 📈 Usage Statistics

- **Scraping Frequency**: Every 40 minutes (36 times/day)
- **Execution Time**: ~30-60 seconds per run
- **Data Retention**: Artifacts kept for 7 days
- **Browser**: Chromium (headless)
- **Wait Time**: 20 seconds for stream loading

## 🔐 Security

- ✅ Secrets stored in GitHub (not in code)
- ✅ .env file excluded from git
- ✅ No hardcoded credentials
- ✅ Firebase auth token optional

## 📝 Configuration

### Add Stream URLs
Edit `scraper_playwright.py`:
```python
STREAM_URLS = [
    {
        "url": "https://your-stream.com",
        "name": "Stream Name",
        "title": "Stream Title"
    }
]
```

### Change Schedule
Edit `.github/workflows/scrape-streams.yml`:
```yaml
schedule:
  - cron: '*/40 * * * *'  # Every 40 minutes
```

### Adjust Wait Times
Edit `scraper_playwright.py`:
```python
time.sleep(20)  # Increase if streams load slowly
```

## 🎓 Learning Resources

- **Playwright Docs**: https://playwright.dev/python/
- **GitHub Actions**: https://docs.github.com/actions
- **Firebase RTDB**: https://firebase.google.com/docs/database
- **Cron Syntax**: https://crontab.guru/

## 🆘 Support

See documentation files:
- **Quick Setup**: [QUICKSTART.md](QUICKSTART.md)
- **Testing**: [TESTING.md](TESTING.md)
- **Deployment**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Main Docs**: [README.md](README.md)

## 🎉 Success Criteria

Your scraper is working when:
1. ✅ Workflow runs every 40 minutes
2. ✅ Logs show "Found m3u8" messages
3. ✅ Firebase contains updated data
4. ✅ Artifacts are generated
5. ✅ No error messages in logs

## 🔮 Future Enhancements

Potential improvements:
- Add multiple stream sources
- Implement retry logic for failed scrapes
- Add Discord/Slack notifications
- Store historical data
- Add stream quality detection
- Implement rate limiting
- Add proxy support
- Create web dashboard

## 📊 Monitoring

### Check Workflow Status
```
GitHub → Actions → Scrape Cricket Streams
```

### View Firebase Data
```
https://cricket-stream-portal-default-rtdb.firebaseio.com/.json
```

### Download Results
```
Actions → Completed Run → Artifacts → Download
```

---

**Built with**: Python, Playwright, GitHub Actions, Firebase
**License**: Use as needed
**Maintenance**: Update stream URLs as needed
