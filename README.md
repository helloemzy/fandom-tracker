# 📊 Signal Index

**Track celebrity influence on consumer behavior using X (Twitter) and YouTube data.**

Daily-updated rankings you can screenshot and post to [@SignalIndex](https://twitter.com/SignalIndex).

---

## 🎯 What This Does

**Problem:** Which celebrities are actually driving consumer behavior right now?

**Solution:** Signal Index combines X engagement metrics + YouTube momentum to calculate an influence score.

**Output:** Daily rankings, spending signals, and auto-generated social media posts.

---

## 🚀 Quick Start (5 Minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**What this does:** Downloads all the libraries you need (Streamlit, Tweepy, Pandas, etc.)

### 2. Set Up API Keys

```bash
# Copy the template file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or open in any text editor
```

**You need:**
- **X (Twitter) API keys** → Get at [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
- **YouTube API key** → Get at [console.cloud.google.com](https://console.cloud.google.com/apis/credentials)
- **Korea chart API base URL (optional)** → Defaults to the hosted API, override in `.env` if needed

**See "Getting API Keys" section below for detailed instructions.**

### 3. Customize Your Artist List (Optional)

Edit `artists.json` to add/remove artists, or use the dashboard's "Manage Artists" page.

### 4. Collect Data

```bash
python update_data.py
```

**What this does:**
- Fetches recent tweets from all active artists
- Fetches recent YouTube videos
- Calculates Signal Index scores
- Saves everything to CSV files in `data/`

**Expected output:**
```
🚀 SIGNAL INDEX - Data Collection
📅 2024-01-07 10:30:15
============================================================

👥 Tracking 9 active artists:
  • NewJeans (K-pop)
  • BTS (K-pop)
  • Taylor Swift (Western)
  ...

📱 COLLECTING X (TWITTER) DATA
============================================================
  ✅ NewJeans: 3 tweets collected
  ✅ BTS: 3 tweets collected
  ...

📺 COLLECTING YOUTUBE DATA
============================================================
  ✅ NewJeans: 2 videos collected
  ...

💾 Saved 27 X data points → data/x_data.csv
💾 Saved 18 YouTube data points → data/youtube_data.csv

📊 Calculating Signal Index scores...

🏆 TOP 5 INFLUENCERS
============================================================
1. Taylor Swift        Score:  87.3 (Western)
2. NewJeans            Score:  82.1 (K-pop)
3. BTS                 Score:  79.5 (K-pop)
4. BLACKPINK           Score:  76.8 (K-pop)
5. Sabrina Carpenter   Score:  71.2 (Western)

✨ Data collection complete!
▶️  Run dashboard: streamlit run dashboard.py
```

### 5. Launch Dashboard

```bash
streamlit run dashboard.py
```

**What this does:**
- Opens a web app in your browser (usually http://localhost:8501)
- Shows interactive charts and rankings
- Lets you manage artists without touching code

---

## 📁 Project Structure

```
fandom-tracker/
├── .env                  # Your API keys (NEVER commit this!)
├── .env.example          # Template for .env
├── .gitignore            # Files to exclude from version control
├── requirements.txt      # Python dependencies
├── config.py             # Settings and artist management functions
├── artists.json          # Artist database (human-editable!)
├── collectors/
│   ├── __init__.py       # Makes this a Python package
│   ├── x_collector.py    # Fetches X/Twitter data
│   └── youtube_collector.py  # Fetches YouTube data
├── analyzers/
│   ├── __init__.py
│   └── influence_score.py    # Calculates Signal Index scores
├── data/
│   ├── x_data.csv        # Raw X metrics (generated)
│   ├── youtube_data.csv  # Raw YouTube metrics (generated)
│   └── rankings.csv      # Final scores (generated)
├── update_data.py        # Main data collection script
├── dashboard.py          # Streamlit web dashboard
└── README.md             # This file!
```

**Key Files to Know:**
- **artists.json** → Add/remove artists here
- **update_data.py** → Run this daily to refresh data
- **dashboard.py** → Run this to see visualizations
- **config.py** → Tweak settings (keywords, scoring weights, etc.)

---

## 🌐 Live Chart APIs (Dashboard)

The Streamlit dashboard pulls live chart data directly from these APIs:

### Korea Chart API
- **URL template:** `https://korea-music-chart-api-autumn-sun-1261.fly.dev/{platform}/chart`
- **Env override:** `KOREA_CHART_API_BASE_URL`
- **Sample response (trimmed):**
```json
{
  "data": [
    {
      "rank": 1,
      "artistName": "화사 (HWASA)",
      "title": "Good Goodbye",
      "albumName": "Good Goodbye",
      "albumArt": "https://cdnimg.melon.co.kr/...",
      "songNumber": "600287375"
    }
  ]
}
```

### Billboard Charts API
- **URL template:** `https://billboard-charts.fly.dev/chart/{chart_name}?date=YYYY-MM-DD|year=YYYY`
- **Env override:** `BILLBOARD_CHART_API_BASE_URL`
- **Sample response (trimmed):**
```json
{
  "name": "hot-100",
  "title": "Billboard Hot 100™",
  "date": "2024-08-10",
  "entries": [
    {
      "rank": 1,
      "title": "A Bar Song (Tipsy)",
      "artist": "Shaboozey",
      "weeks": 16,
      "lastPos": 1,
      "peakPos": 1,
      "isNew": false,
      "image": null
    }
  ]
}
```

### YouTube Music Charts (YouTube Data API)
- **URL:** `https://www.googleapis.com/youtube/v3/videos`
- **Params:** `part=snippet,statistics&chart=mostPopular&videoCategoryId=10&regionCode=US&maxResults=50`
- **Env:** `YOUTUBE_API_KEY`
- **Sample response (trimmed):**
```json
{
  "data": [
    {
      "rank": 1,
      "title": "Video Title",
      "artist": "Channel Title",
      "video_id": "abcd1234",
      "views": 1234567,
      "likes": 8901,
      "published_at": "2024-08-01T12:34:56Z",
      "thumbnail": "https://i.ytimg.com/..."
    }
  ]
}
```

---

## 🔑 Getting API Keys

### X (Twitter) API

**Free Tier:** 1,500 tweets/month (enough for ~15 artists × 3 tweets each × 30 days)

**Steps:**
1. Go to [developer.twitter.com](https://developer.twitter.com/en/portal/dashboard)
2. Apply for a developer account (takes 1-2 days)
3. Create a new App
4. Go to "Keys and Tokens"
5. Copy **Bearer Token** (you only need this one!)
6. Paste into `.env`:
   ```
   X_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAABcdef...
   ```

**Troubleshooting:**
- "403 Forbidden" → Your bearer token is wrong or app doesn't have permissions
- "429 Too Many Requests" → You hit the rate limit, wait 15 minutes

### YouTube API

**Free Tier:** 10,000 units/day (enough for ~100 artists)

**Steps:**
1. Go to [console.cloud.google.com](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy the API key
6. Paste into `.env`:
   ```
   YOUTUBE_API_KEY=AIzaSyBcdef1234567890abcdef...
   ```

**Troubleshooting:**
- "API key not valid" → Check for typos, make sure YouTube API is enabled
- "Quota exceeded" → You hit daily limit, resets at midnight Pacific Time

---

## 👥 Managing Artists

### Method 1: Use the Dashboard (Recommended)

1. Run `streamlit run dashboard.py`
2. Go to "⚙️ Manage Artists" page
3. Fill out the form and click "Add Artist"

### Method 2: Edit `artists.json` Directly

Open `artists.json` in any text editor and add an entry:

```json
{
  "name": "IU",
  "category": "K-pop",
  "twitter": "_IUofficial",
  "youtube_channel_id": "UC3SyT4_WLHzN7JmHQwKQZww",
  "active": true
}
```

**Field Guide:**
- **name:** Display name (appears on dashboard)
- **category:** "K-pop", "Western", or "Other"
- **twitter:** Username WITHOUT the @ symbol
- **youtube_channel_id:** See below for how to find this
- **active:** `true` to track, `false` to temporarily disable

### Finding YouTube Channel IDs

**Method 1: From URL**
1. Go to the artist's YouTube channel
2. Look at the URL:
   - If it's `youtube.com/channel/UCxxx...` → copy `UCxxx...`
   - If it's `youtube.com/@username` → see Method 2

**Method 2: From About Page**
1. Go to channel → "About" tab
2. Click "Share Channel"
3. Click "Copy Channel ID"

**Example:**
- URL: `https://www.youtube.com/channel/UCdZlB77W6p-qx08FaZG_0kw`
- Channel ID: `UCdZlB77W6p-qx08FaZG_0kw`

### Disabling Artists (Without Deleting Them)

**Option 1:** Use dashboard's "Disable" button

**Option 2:** In `artists.json`, change:
```json
"active": true  →  "active": false
```

They'll stay in your file but won't be tracked during data collection.

---

## 🧮 How the Scoring Works

### The Algorithm

```
Signal Score = (60% × X Engagement Score) + (40% × YouTube Momentum Score)
```

**X Engagement Score (0-100):**
- Calculates engagement rate: `(likes + retweets) / followers × 100`
- Normalizes to 0-100 scale
- **Why engagement rate?** An artist with 1M followers getting 50K likes (5% rate) is more influential than one with 100M followers getting 100K likes (0.1% rate)

**YouTube Momentum Score (0-100):**
- Sums views from recent videos (last 30 days)
- Normalizes to 0-100 scale (10M views = 100 points)
- **Why recent videos?** Old viral hits don't reflect current influence

**Why 60/40 weighting?**
- X shows immediate fan excitement (real-time)
- YouTube shows sustained interest (accumulates over days)
- X is more reactive to trends → weighted higher

### Example Calculation

**Taylor Swift:**
- Recent tweets: 150K likes avg, 90M followers
- Engagement rate: 150,000 / 90,000,000 = 0.167%
- X Score: 0.167% × 20 = **33.4 points**
- Recent YouTube views: 50M
- YouTube Score: 50M / 1M × 10 = **100 points** (capped at 100)
- **Final Score: (0.6 × 33.4) + (0.4 × 100) = 60.0**

### Adjusting the Algorithm

**To change weights:**

Edit `analyzers/influence_score.py`:

```python
# Change this line:
signal_score = (0.6 * x_score) + (0.4 * yt_score)

# Example: Make YouTube count more
signal_score = (0.4 * x_score) + (0.6 * yt_score)
```

**To adjust normalization:**

```python
# If scores are too low, increase multipliers:
x_score = min(engagement_rate * 30, 100)  # Was 20
yt_score = min(total_views / 500_000 * 10, 100)  # Was 1M
```

---

## 📊 Using the Dashboard

### Page 1: Top Influencers

**Features:**
- Top 10 rankings table
- Category filter dropdown
- Key metrics (current leader, highest engagement, most views)
- Score breakdown chart (shows X vs YouTube contribution)

**Use Case:** Screenshot this for your @SignalIndex posts!

### Page 2: Spending Signals

**Features:**
- Bar chart of product mentions by artist
- Recent tweets mentioning products (merch, albums, tours, etc.)
- Engagement metrics for each post

**Use Case:** Identify which artists are actively promoting products

**Product Keywords** (defined in `config.py`):
```python
PRODUCT_KEYWORDS = [
    'merch', 'album', 'vinyl', 'buy', 'sold out', 'pre-order',
    'drop', 'collection', 'tour', 'tickets', 'concert', 'shop',
    'limited edition', 'exclusive', 'purchase', 'store'
]
```

Add more keywords by editing this list!

### Page 3: Post Generator

**Features:**
- Auto-generates X/Twitter posts from your data
- Three templates:
  1. Top Influencers Ranking (top 5 list)
  2. Category Leaders (best in K-pop, Western, etc.)
  3. Engagement Champion (spotlight on #1 artist)

**Use Case:** Copy-paste directly to @SignalIndex account

### Page 4: Manage Artists

**Features:**
- View all artists (active and disabled)
- Enable/disable artists with one click
- Add new artists via form
- See which artists have YouTube channels

**Use Case:** Add trending artists without touching code

---

## 🔄 Daily Workflow

**Morning Routine (5 minutes):**

1. **Collect fresh data:**
   ```bash
   python update_data.py
   ```

2. **Review rankings:**
   ```bash
   streamlit run dashboard.py
   ```
   Go to "🏆 Top Influencers" page

3. **Generate post:**
   Go to "✍️ Post Generator" page
   Select post type → Copy text

4. **Post to @SignalIndex:**
   Paste into X/Twitter
   Optionally: Screenshot the rankings table

5. **Check spending signals:**
   Go to "💰 Spending Signals" page
   Note any interesting product mentions for future posts

**Weekly Maintenance:**
- Check "⚙️ Manage Artists" page
- Add new trending artists
- Disable artists who've gone quiet

---

## 🐛 Troubleshooting

### "No module named 'tweepy'"

**Problem:** Python libraries not installed

**Solution:**
```bash
pip install -r requirements.txt
```

### "X API token not configured"

**Problem:** `.env` file missing or incorrect

**Solution:**
1. Check if `.env` file exists (not `.env.example`)
2. Open `.env` and verify API keys have no spaces or quotes
3. Correct format: `X_BEARER_TOKEN=AAAAAxxxx...` (no quotes!)

### "Rate limit hit"

**Problem:** Too many API requests

**Solution:**
- **X/Twitter:** Wait 15 minutes, then try again
- **YouTube:** Wait until next day (quota resets at midnight PT)
- **Long-term:** Reduce number of artists or increase `time.sleep()` delays

### "⚠️ No data available"

**Problem:** Dashboard can't find CSV files

**Solution:**
1. Run `python update_data.py` first
2. Check that `data/rankings.csv` exists
3. If error during data collection, check API keys

### Data looks wrong

**Problem:** Stale data or cache issue

**Solution:**
1. Click "🔄 Refresh Data" button in dashboard sidebar
2. Or manually delete `data/*.csv` and re-run `python update_data.py`

### Streamlit won't start

**Problem:** Port already in use

**Solution:**
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use a different port
streamlit run dashboard.py --server.port 8502
```

---

## 🔐 Security & Privacy

### ⚠️ NEVER Commit `.env` File

Your `.env` file contains API keys (essentially passwords). **Never share it or commit it to GitHub!**

**Protection:**
- `.gitignore` already excludes `.env`
- Before committing, double-check: `git status` should NOT show `.env`

### API Key Best Practices

1. **Use read-only tokens when possible**
   - X Bearer Token is read-only by default ✅
   - YouTube API key is read-only ✅

2. **Regenerate if compromised**
   - If you accidentally commit `.env`, regenerate keys immediately

3. **Set usage limits**
   - X: Enable rate limiting in developer portal
   - YouTube: Set quota alerts in Google Cloud Console

### Data Privacy

**What data is stored:**
- Public tweets (already public)
- Public YouTube metrics (already public)
- No user data, no private information

**Data files:**
- All CSV files in `data/` contain only public metrics
- Safe to commit to private repos (but excluded by default)

---

## 🚢 Next Steps (Future Versions)

**Milestone 2: Historical Trends**
- Track week-over-week changes
- Show momentum arrows (↑↓) in rankings
- Line charts showing score history

**Milestone 3: More Data Sources**
- Reddit mention volume (r/kpop, r/popheads, etc.)
- Spotify monthly listeners
- TikTok engagement

**Milestone 4: Automation**
- Cron job for daily data collection
- Auto-post to @SignalIndex (using X API v2)
- Email alerts for big movements

**Milestone 5: Deployment**
- Cloud hosting (AWS/GCP/Heroku)
- Public dashboard (optional)
- Database migration (SQLite → PostgreSQL)

---

## 🤝 Contributing & Customization

### Adding a New Data Source

**Example: Adding Spotify**

1. Create `collectors/spotify_collector.py`
2. Add `SPOTIFY_API_KEY` to `.env.example` and `config.py`
3. Update `analyzers/influence_score.py` to include Spotify metrics
4. Adjust weighting formula

### Modifying the Scoring Algorithm

**Current formula is in `analyzers/influence_score.py`:**

```python
signal_score = (0.6 * x_score) + (0.4 * yt_score)
```

**Ideas to try:**
- Add recency weighting (recent activity counts more)
- Include product mention bonus (+5 points per mention)
- Category-specific weighting (K-pop values YouTube more)

### Custom Visualizations

**Streamlit + Plotly make it easy!**

Add to `dashboard.py`:

```python
# Example: Line chart of scores over time
import plotly.express as px

fig = px.line(rankings, x='date', y='signal_score', color='celebrity')
st.plotly_chart(fig)
```

**Resources:**
- [Streamlit Gallery](https://streamlit.io/gallery)
- [Plotly Examples](https://plotly.com/python/)

---

## 📚 Learning Resources

### If you want to understand the code better:

**Python Basics:**
- [Python for Everybody](https://www.py4e.com/) - Free course
- [Automate the Boring Stuff](https://automatetheboringstuff.com/) - Practical Python

**Data Analysis:**
- [Pandas Cookbook](https://pandas.pydata.org/docs/user_guide/cookbook.html)
- [Real Python - Pandas](https://realpython.com/pandas-python-explore-dataset/)

**APIs:**
- [Tweepy Documentation](https://docs.tweepy.org/)
- [YouTube API Guide](https://developers.google.com/youtube/v3/getting-started)

**Streamlit:**
- [Streamlit Docs](https://docs.streamlit.io/)
- [30 Days of Streamlit](https://30days.streamlit.app/)

---

## 💬 Support

**Found a bug?**
- Check "Troubleshooting" section first
- Review error messages in terminal
- Google the error message

**Have a question?**
- Check `CLAUDE.md` for development guidelines
- Read code comments (they're educational!)
- Try modifying one thing at a time

**Want a feature?**
- Check "Next Steps" section
- Start with smallest version (MVP)
- Test thoroughly before adding complexity

---

## 📄 License

This is your personal project - use it however you want!

**Suggested attribution if you open-source it:**
```
Built with Python, Streamlit, and ☕
Data from X (Twitter) API and YouTube API
```

---

## 🎉 You're Ready!

**Quick Start Recap:**
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add API keys
3. `python update_data.py`
4. `streamlit run dashboard.py`
5. Go to http://localhost:8501

**Daily Routine:**
- Run `update_data.py` each morning
- Screenshot rankings
- Post to @SignalIndex

**Questions?** Read the code comments - they're there to teach you!

---

**Happy tracking! 🚀**
# fandom-tracker
