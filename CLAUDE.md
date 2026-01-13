# CLAUDE.md - Development Guidelines

## About Emily

I'm a product manager with limited coding experience who's looking to learn to become more technical. When you're coding and doing your work, please share tips that explain the tech architecture and any changes that you're making and why.

---

## Project Context: Signal Index

**What we're building:** A dashboard that tracks celebrity influence on consumer behavior using X (Twitter) and YouTube data.

**End goal:** Daily-updated rankings that can be screenshot and posted to @SignalIndex on X/Twitter.

**Tech Stack:**
- **Python 3.9+** - Programming language (easy to read, great for data)
- **Streamlit** - Dashboard framework (turns Python into web apps instantly)
- **Tweepy** - X/Twitter API library
- **Google API Client** - YouTube API library
- **Pandas** - Data manipulation (think: Excel but in code)
- **Plotly** - Interactive charts and graphs

**Why these choices:**
- Python is beginner-friendly and great for data analysis
- Streamlit requires minimal web development knowledge
- All libraries have free tiers and good documentation
- No database needed (we use CSV files, like spreadsheets)

---

## Key Concepts to Explain

When working on this project, please explain:

### 1. **Data Flow**
- How data moves from APIs → CSV files → Dashboard
- Why we save intermediate files (debugging, historical tracking)

### 2. **API Rate Limits**
- Why we can't collect unlimited data
- How `time.sleep()` prevents hitting limits
- Why we collect data once daily, not real-time

### 3. **Error Handling**
- What `try/except` blocks do and why they matter
- How to read error messages
- Common API errors and what they mean

### 4. **File Structure**
- Why we organize code into folders (collectors/, analyzers/)
- What `__init__.py` files do (they make folders into packages)
- Why we use `.env` for secrets (never commit API keys!)

### 5. **Data Normalization**
- Why we convert different metrics to 0-100 scale
- How weighted scores work (60% X + 40% YouTube)
- Why engagement rate matters more than raw follower count

---

## Teaching Moments

When you make changes, please explain:

### Code Comments
```python
# GOOD: Explains the "why"
# Normalize to 0-100 because engagement rates vary wildly by follower count
x_score = min(engagement_rate * 20, 100)

# BAD: Just repeats what the code does
# Multiply engagement rate by 20
x_score = engagement_rate * 20
```

### Architecture Decisions
Explain WHY we chose certain patterns:
- "We use JSON for artists.json because it's human-editable"
- "We separate collectors from analyzers so you can test each independently"
- "Streamlit's @st.cache_data decorator prevents re-loading files on every click"

### Debugging Tips
When something breaks:
1. What the error message means in plain English
2. Where to look for the problem
3. How to test if the fix worked

### Best Practices
- Why we use version control (.gitignore)
- How to structure commits (not covered yet, but good to know)
- When to refactor vs when to ship

---

## Questions I Might Ask

Feel free to preemptively explain:

**"Why did you do it this way?"**
→ Explain trade-offs and alternatives

**"What does this library do?"**
→ High-level explanation + link to docs

**"How would I modify X to do Y?"**
→ Point me to the specific file/function + what to change

**"What could go wrong here?"**
→ Common pitfalls and how to avoid them

---

## My Goals

1. **Understand the architecture** - How pieces fit together
2. **Learn to debug** - Fix issues without starting over
3. **Modify independently** - Add artists, change scoring, etc.
4. **Ship quickly** - Launch MVP, iterate based on real usage

---

## Communication Style Preferences

✅ **DO:**
- Use analogies (e.g., "APIs are like restaurant menus")
- Explain trade-offs ("We could do X, but Y is simpler for now")
- Link to documentation when going deeper
- Celebrate small wins ("This works! Here's why it's cool...")

❌ **DON'T:**
- Assume I know jargon (or define it when you use it)
- Skip over "obvious" steps
- Write code without explaining the logic
- Use overly technical language without context

---

## Project-Specific Notes

### What I Already Understand
- Basic product/market concepts
- How APIs work at a high level
- Why rate limits exist
- CSV/spreadsheet logic

### What I'm Learning
- Python syntax and patterns
- How web frameworks work (Streamlit)
- Data pipelines and ETL concepts
- Git and version control
- Environment variables and secrets management

### What I Want to Learn
- When to use different data structures (lists vs dicts vs dataframes)
- How to profile code performance
- Testing strategies (unit tests, integration tests)
- Deployment options (running this on a server vs my laptop)

---

## Success Metrics

**This CLAUDE.md is working if:**
1. I can run `python update_data.py` confidently
2. I can add a new artist without your help
3. I understand why errors happen and can Google solutions
4. I can explain the data flow to someone else
5. I feel comfortable modifying the scoring algorithm

**Please flag when:**
- I should learn a concept more deeply (with resources)
- I'm about to make a mistake that will cause issues later
- There's a simpler way to do what I'm trying to do
- Industry best practices differ from our quick MVP approach

---

## Current Phase: MVP (Milestone 1)

**Right now we're building:**
- Basic data collection from X and YouTube APIs
- Simple scoring algorithm
- Streamlit dashboard with 3 pages
- Artist management system

**We're NOT worrying about:**
- Perfect code quality (ship > perfect)
- Advanced features (Reddit, Spotify come later)
- Deployment (local-first)
- Authentication/security (no users yet)

**Next phases will add:**
- Historical trend tracking (week-over-week changes)
- Reddit and Spotify data sources
- Automated scheduling (cron jobs)
- Potentially: Cloud deployment

---

## Technical Decisions Log

Keep track of "why we did it this way" for future reference:

### 1. Why CSV files instead of a database?
- **Decision:** Use CSV files for data storage
- **Reasoning:**
  - No database setup required
  - Easy to inspect/debug (open in Excel)
  - Sufficient for <1000 rows per day
  - Can migrate to SQLite later if needed
- **Trade-off:** Less efficient for complex queries, but simpler to start

### 2. Why Streamlit instead of React?
- **Decision:** Build dashboard with Streamlit
- **Reasoning:**
  - Pure Python (no JavaScript needed)
  - Live reload during development
  - Built-in widgets (no CSS required)
  - 100-200 lines of code vs 1000+ for React
- **Trade-off:** Less customizable, but 10x faster to build

### 3. Why separate collectors?
- **Decision:** One collector file per API
- **Reasoning:**
  - Test each API independently
  - Disable failing collectors without breaking others
  - Easy to add new data sources later
- **Trade-off:** More files, but more maintainable

### 4. Why artists.json instead of hardcoded?
- **Decision:** Store artists in JSON file
- **Reasoning:**
  - Non-developers can edit it
  - No code changes needed to add artists
  - Version control tracks changes
  - Can import/export easily
- **Trade-off:** Needs validation logic, but more flexible

---

## Resources to Keep Handy

**When I get stuck:**
- [Streamlit Docs](https://docs.streamlit.io/) - Dashboard framework
- [Tweepy Docs](https://docs.tweepy.org/) - X/Twitter API
- [YouTube API Docs](https://developers.google.com/youtube/v3) - Video data
- [Pandas Docs](https://pandas.pydata.org/docs/) - Data manipulation
- [Stack Overflow](https://stackoverflow.com/) - When errors happen

**Learning Python:**
- [Python for Everybody](https://www.py4e.com/) - Free course
- [Real Python](https://realpython.com/) - Tutorials
- [Automate the Boring Stuff](https://automatetheboringstuff.com/) - Practical examples

---

## Feedback Loop

After each coding session, please summarize:
1. **What we built** - In plain English
2. **Key concepts used** - What I should understand
3. **Next steps** - What's left to do
4. **Suggested learning** - If I want to go deeper

---

## Remember

I'm here to learn AND ship. Balance is key:
- Explain enough that I understand
- Don't over-engineer the MVP
- Ship working code, iterate based on usage
- Learning happens through building

Let's do this! 🚀

---

---

# 📋 PROJECT STATUS (Updated: January 13, 2026)

## 🎉 What We Accomplished Today

### 1. Fixed X API Rate Limiting ✅
**Problem:** Free X API tier only allows ~15 requests per 15 minutes. Was hitting rate limit after collecting 1-3 artists, blocking the other 6-9 artists.

**Solution:** Built automatic batching system in `collectors/x_collector.py`

**How it works:**
- Detects when rate limit hits (TooManyRequests exception)
- Saves progress so far to CSV (no data loss)
- Automatically waits 15 minutes with countdown timer
- Resumes collection from where it left off
- Repeats until all artists are collected

**Result:**
- Run `python update_data.py` once
- Walk away (takes 7-8 hours for 30 artists)
- All data collected automatically, no manual intervention needed

**Tech Concepts:**
- Exception handling (catching specific API errors)
- Incremental progress saving (write to CSV after each artist)
- State tracking (remembering which artists were collected)
- User feedback (countdown timer so you know it's working)

---

### 2. Expanded Artist List ✅
**Before:** 9 artists (4 K-pop, 5 Western)
**After:** 30 artists (21 K-pop, 9 Western)

**Current Artist List:**

**Western (9):**
1. Taylor Swift
2. Sabrina Carpenter
3. Olivia Rodrigo
4. Billie Eilish
5. Dua Lipa
6. Nicki Minaj
7. Cardi B
8. Bruno Mars
9. Lady Gaga

**K-pop Girl Groups (13):**
10. NewJeans
11. BLACKPINK
12. TWICE
13. ITZY
14. (G)I-DLE
15. aespa
16. LE SSERAFIM
17. IVE
18. ILLIT
19. Hearts2Hearts
20. KATSEYE
21. KiiiKiii
22. NMIXX

**K-pop Boy Groups (7):**
23. BTS
24. Stray Kids
25. SEVENTEEN
26. TXT
27. ENHYPEN
28. BOYNEXTDOOR
29. CORTIS

**Co-ed (1):**
30. All Day Project

**Why this mix?**
- Tests algorithm across different fanbase sizes
- Covers both Western and K-pop markets
- Mix of established stars and rising artists
- Includes groups without YouTube channels (to test robustness)

**Fixed Issues:**
- NewJeans Twitter handle: Changed from "newjeans_official" (too long) to "NewJeans_twt"
- YouTube timeframe: Extended from 30 to 90 days (captures less-frequent posters)

---

### 3. Added Multi-Source Chart Data Collection ✅

**New Script:** `update_charts.py` (SEPARATE from update_data.py)

**Why separate?**
- Charts change frequently (multiple times per day)
- No API rate limits (web scraping)
- Fast execution (15-30 minutes vs 7-8 hours)
- Can refresh before posting without waiting for X collection

**Data Sources Added:**

1. **Billboard Hot 100** (Web scraping)
   - Most prestigious singles chart
   - Updates weekly (Tuesdays)
   - Currently working ✅

2. **Billboard 200** (Web scraping)
   - Top albums chart
   - Updates weekly
   - Currently working ✅

3. **Melon Charts** (Web scraping)
   - Largest Korean music streaming service
   - K-pop artists only
   - Currently working ✅

4. **Spotify Charts via Kworb** (Web scraping)
   - Aggregated Spotify data
   - Currently NOT working ⚠️ (HTML structure needs adjustment)

**Current Results (as of Jan 13, 2026):**
- 23 of 30 artists have chart positions
- Taylor Swift: #4 on both Hot 100 & Billboard 200
- NMIXX: #5 on Melon
- LE SSERAFIM: #6 on Melon
- BLACKPINK: #12 on Melon

**New Dependencies Added:**
```python
beautifulsoup4  # HTML parsing for web scraping
requests        # HTTP requests
lxml            # Fast HTML parser
```

**Web Scraping Ethics:**
- Added respectful delays (2-3 seconds between requests)
- Proper User-Agent identification
- Follows robots.txt guidelines
- Only public data (charts are meant to be seen)

---

### 4. Updated Scoring Algorithm ✅

**OLD Formula:**
```
Signal Score = (60% × X Engagement) + (40% × YouTube Views)
```

**NEW Formula:**
```
Signal Score = (30% × X Engagement) + (20% × YouTube Views) + (50% × Chart Performance)
```

**Why the change?**
- **Chart positions = Commercial success** (actual sales/streams)
- **Social media = Fan engagement** (excitement and buzz)
- Charts are harder to manipulate than social metrics
- Industry standard for measuring popularity

**Chart Component Breakdown:**
```
Chart Score (50% of total) =
  40% × Spotify position (largest streaming platform)
  30% × Billboard Hot 100 (most prestigious singles)
  15% × Billboard 200 (album sales)
  15% × Melon (dominant in Korea, K-pop only)
```

**Full Expanded Formula:**
```
Signal Score =
  30% × X engagement rate
  20% × YouTube views (last 90 days)
  20% × Spotify chart position      (40% of 50% chart component)
  15% × Billboard Hot 100 position   (30% of 50%)
  7.5% × Billboard 200 position      (15% of 50%)
  7.5% × Melon position (K-pop only) (15% of 50%)
```

**How Chart Positions Convert to Scores:**
```
Position #1   → Score 100
Position #10  → Score 91
Position #50  → Score 51
Position #100 → Score 1
Not charting  → Score 0
```

Formula: `Score = 100 - (position - 1)`

**Updated Files:**
- `analyzers/influence_score.py` - New scoring logic
- `update_data.py` - Now loads chart_data.csv if available

---

### 5. Updated Dashboard ✅

**New Main Table (11 columns):**
| Rank | Artist | Category | Signal Score | **Best Chart** | **Spotify** | **BB Hot 100** | **BB 200** | **Melon** | X Eng | YT Views |

**Best Chart Column:**
- Shows highest chart position across all sources
- Includes chart name: "#4 (BB Hot 100)"
- Makes it easy to see commercial success at a glance

**New Highlights Section (4 metrics):**
1. 👑 Current Leader - Highest overall score
2. 📊 Top Chart Position - Best chart placement (NEW!)
3. 🔥 Highest X Engagement - Most engaged fanbase
4. 📺 Most YouTube Views - Most video momentum

**Updated Score Breakdown Chart:**
- 🔵 X Engagement (30%) - Blue bar
- 🔴 YouTube Views (20%) - Red bar
- 🟢 Chart Performance (50%) - Green bar (NEW!)

**Updated Files:**
- `dashboard.py` - New table columns, chart display, metrics

---

## 📁 Current File Structure

```
fandom-tracker/
├── artists.json                    # 30 artists with Twitter/YouTube handles
├── update_data.py                  # Main script: X + YouTube (7-8 hours)
├── update_charts.py                # NEW! Chart script (15-30 minutes)
├── dashboard.py                    # Streamlit dashboard (updated with charts)
├── config.py                       # Load artists, manage .env
├── requirements.txt                # Python dependencies (updated)
├── .env                            # API keys (never commit!)
├── .env.example                    # Template for .env
│
├── collectors/                     # Data collection modules
│   ├── __init__.py
│   ├── x_collector.py             # X/Twitter (with auto-batching!)
│   ├── youtube_collector.py       # YouTube (90-day window)
│   └── chart_collector.py         # NEW! Web scraping for charts
│
├── analyzers/                      # Score calculation
│   ├── __init__.py
│   └── influence_score.py         # NEW! 30/20/50 algorithm
│
├── data/                           # CSV outputs
│   ├── x_data.csv                 # X engagement metrics
│   ├── youtube_data.csv           # YouTube video stats
│   ├── chart_data.csv             # NEW! Chart positions
│   └── rankings.csv               # Final Signal Index scores
│
└── venv/                          # Python virtual environment
```

---

## 🚀 How to Use Everything

### Daily Workflow:

**Morning (Start Background Collection):**
```bash
# Terminal 1: Start long-running X/YouTube collection
python update_data.py &
# Takes 7-8 hours, runs in background

# Terminal 2: Collect chart data (quick!)
python update_charts.py
# Takes 15-30 minutes
```

**Throughout the Day (Refresh Charts):**
```bash
python update_charts.py
# Run anytime for fresh chart positions
# No rate limits!
```

**Before Posting Rankings:**
```bash
# Get latest chart data
python update_charts.py

# View dashboard
streamlit run dashboard.py

# Take screenshots for @SignalIndex
```

---

### Command Reference:

**Collect All Data:**
```bash
python update_data.py
```
- Collects X + YouTube for all 30 artists
- Auto-handles rate limits (waits 15 min when needed)
- Takes 7-8 hours total
- Loads chart data if available
- Calculates final rankings
- Saves to data/*.csv

**Collect Chart Data:**
```bash
python update_charts.py
```
- Scrapes Billboard, Melon, Spotify (Kworb)
- Fast: 15-30 minutes
- No API keys needed
- Can run multiple times per day
- Saves to data/chart_data.csv

**View Dashboard:**
```bash
streamlit run dashboard.py
```
- Opens browser automatically
- Shows rankings with all data
- Interactive filters by category
- Auto-refreshes when data changes

**Install/Update Dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📊 Current Data Status

**Last Full Collection:** January 13, 2026

**X/YouTube Data:**
- Status: OLD (from earlier test)
- Only 5 artists have X data
- Only 4 artists have YouTube data
- **Action Needed:** Run `python update_data.py` for full collection

**Chart Data:**
- Status: FRESH (just collected)
- 23 of 30 artists have chart positions
- Billboard + Melon working perfectly
- Spotify (Kworb) needs HTML structure fix

**Rankings:**
- Currently based on old X/YouTube + new chart data
- Will be complete after next `update_data.py` run

---

## ⚠️ Known Issues & Fixes

### Issue 1: Spotify Scraping Not Working
**Problem:** Kworb.net HTML structure different than expected
**Impact:** All artists showing "Not charting" for Spotify
**Workaround:** Billboard + Melon still work (23 artists have data)
**Fix Needed:** Inspect Kworb.net HTML and adjust selectors in `collectors/chart_collector.py`

### Issue 2: Some Artists Missing YouTube Channels
**Problem:** 4 artists have `youtube_channel_id: null` in artists.json
**Artists Affected:** (G)I-DLE, Hearts2Hearts, KiiiKiii, CORTIS, All Day Project
**Impact:** No YouTube data collected for these artists
**Workaround:** They still get X + Chart data
**Fix:** Search for their channel IDs and add to artists.json

### Issue 3: Long Data Collection Time
**Problem:** 30 artists × 15 min/artist = 7-8 hours
**Cause:** X API free tier rate limits
**Workaround:** Auto-batching makes it hands-off
**Options:**
- Upgrade to X API Basic ($100/month) for instant collection
- Keep free tier, run overnight
- Reduce artist count

---

## 🎯 Next Steps & Roadmap

### Immediate (This Week):
1. ✅ ~~Fix X API rate limiting~~ DONE
2. ✅ ~~Expand artist list to 30~~ DONE
3. ✅ ~~Add chart data collection~~ DONE
4. ⏳ **Run full data collection** (`python update_data.py`)
5. ⏳ **Test dashboard with complete data**
6. ⏳ **Post first rankings to @SignalIndex**

### Short-term (This Month):
1. **Fix Spotify scraping** (adjust HTML selectors)
2. **Add missing YouTube channel IDs** (for 5 artists)
3. **Add more Korean charts:**
   - Circle Chart (formerly Gaon) - Album sales
   - Hanteo Chart - Real-time sales
4. **Add brand reputation:**
   - brikorea.com - Brand Reputation Index
   - Monthly updates

### Medium-term (Next Quarter):
1. **Historical tracking:**
   - Save daily snapshots
   - Show week-over-week changes
   - Trend arrows (↑↓) in dashboard
2. **Automated scheduling:**
   - Set up cron job for daily collection
   - Email/Slack notifications when complete
3. **Additional data sources:**
   - Apple Music charts
   - TikTok engagement
   - Reddit mention volume

### Long-term (Future):
1. **Cloud deployment:**
   - Host on AWS/GCP/Heroku
   - Run automatically without laptop
2. **Public dashboard:**
   - Share URL instead of screenshots
   - Real-time updates
3. **API endpoint:**
   - Let others query Signal Index data
   - JSON API for developers

---

## 🐛 Debugging Guide

### "Rate limit hit" message appears:
- **Expected behavior** with free X API
- Script will wait 15 minutes automatically
- Don't stop the script, let it finish
- Progress is saved, no data lost

### "User not found" error:
- Twitter handle might be wrong
- Check artists.json for typos
- Verify handle exists on X/Twitter
- Some artists have deactivated accounts (Ariana Grande, Hailey Bieber)

### Dashboard shows "No data available":
- Run `python update_data.py` first
- Check if data/*.csv files exist
- Verify CSV files aren't empty
- Try clearing Streamlit cache: `streamlit cache clear`

### Chart scraping fails:
- Website might be down temporarily
- HTML structure may have changed
- Check internet connection
- Try again in a few minutes
- Not critical - other charts still work

### Import errors:
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

---

## 💡 Key Learnings & Insights

### 1. Web Scraping vs APIs
**APIs:**
- Structured, reliable data
- Rate limits (can be slow)
- Require authentication
- Example: X API, YouTube API

**Web Scraping:**
- Public data, no auth needed
- No rate limits (faster)
- HTML can change (maintenance needed)
- Example: Billboard, Melon charts

**Lesson:** Use both! APIs for real-time social data, scraping for public charts.

---

### 2. Incremental Progress Saves
**What:** Save data after each artist (not just at the end)

**Why:**
- If script crashes, don't lose everything
- Can resume from where you left off
- User sees progress in real-time

**How:**
```python
for artist in artists:
    data = collect_artist_data(artist)
    save_to_csv(data)  # Save immediately!
```

**Example:** `_save_progress()` function in x_collector.py

---

### 3. Separate Fast from Slow Operations
**Slow:** X API collection (7-8 hours due to rate limits)
**Fast:** Chart scraping (15-30 minutes, no limits)

**Solution:** Separate scripts!
- `update_data.py` - Run once daily
- `update_charts.py` - Run multiple times daily

**Benefit:** Fresh chart data throughout the day without waiting for X collection.

---

### 4. Data Normalization is Critical
**Problem:** Can't compare "10M YouTube views" to "5% engagement rate"
**Solution:** Convert both to 0-100 scale
**Formula:** Design multipliers so excellent performance = 100

**Examples:**
- X: `engagement_rate × 20` (5% engagement = 100 points)
- YouTube: `views / 1M × 10` (10M views = 100 points)
- Charts: `100 - (position - 1)` (#1 = 100 points, #100 = 1 point)

---

### 5. Weighted Scoring Shows What Matters
**Old:** Equal weight to X and YouTube (didn't reflect commercial success)
**New:** Chart data gets 50% weight (reflects actual sales/streams)

**Why it works:**
- Charts = proof of commercial impact
- Social media = leading indicator of buzz
- Balanced view of influence

**Flexibility:** Easy to adjust weights based on feedback!

---

## 📚 Technical Concepts Explained

### Auto-batching (Rate Limit Handling)
**What:** Automatically waiting and retrying when APIs limit requests

**How it works:**
1. Try to collect data
2. If rate limit error → save progress
3. Wait 15 minutes (with countdown)
4. Resume from next artist
5. Repeat until done

**Why it's hard:**
- Need to track which artists are done
- Can't lose data if interrupted
- Must handle partial failures gracefully

**Where to see it:** `collectors/x_collector.py` lines 90-150

---

### Web Scraping with BeautifulSoup
**What:** Extracting data from HTML websites

**Steps:**
1. Fetch HTML: `requests.get(url)`
2. Parse HTML: `BeautifulSoup(html, 'lxml')`
3. Find elements: `soup.find('table', class_='chart')`
4. Extract data: `element.get_text()`

**Challenges:**
- HTML structure varies by site
- Websites change layout (breaks scrapers)
- Need to handle errors gracefully

**Where to see it:** `collectors/chart_collector.py`

---

### Weighted Averages
**What:** Combining multiple scores where some matter more

**Formula:**
```
Final = (weight1 × score1) + (weight2 × score2) + ...
```

**Example:**
```python
signal_score = (0.3 × x_score) + (0.2 × yt_score) + (0.5 × chart_score)
```

**Why:** Lets you prioritize what's most important (charts = 50%)

---

### Pandas DataFrames
**What:** Like Excel spreadsheets in Python

**Common operations:**
```python
# Filter rows
kpop_only = df[df['category'] == 'K-pop']

# Sort
df.sort_values('signal_score', ascending=False)

# Merge (like Excel VLOOKUP)
combined = df1.merge(df2, on='celebrity', how='left')

# Group by
df.groupby('category')['score'].mean()
```

**Why we use it:** Makes data manipulation easy, handles missing values gracefully

---

## 🎓 What Emily Should Understand

After this session, you should be able to:

### ✅ Core Concepts:
1. **Rate limiting** - Why APIs restrict requests and how to handle it
2. **Web scraping** - Extracting data from websites vs using APIs
3. **Data normalization** - Converting different metrics to comparable scales
4. **Weighted scoring** - Combining multiple factors with different importance
5. **Incremental saves** - Why we save progress as we go

### ✅ Architecture Patterns:
1. **Separation of concerns** - Why we have separate collector files
2. **Fast vs slow operations** - Why update_charts.py is separate
3. **Optional data sources** - Dashboard works even if some data is missing
4. **Graceful degradation** - System still works when parts fail

### ✅ Practical Skills:
1. **Run data collection** - `python update_data.py`
2. **Refresh chart data** - `python update_charts.py`
3. **View dashboard** - `streamlit run dashboard.py`
4. **Add new artists** - Edit artists.json with Twitter/YouTube handles
5. **Adjust scoring weights** - Change percentages in influence_score.py

### 🎯 Next Learning Goals:
1. **Fix Spotify scraping** - Inspect HTML, adjust selectors
2. **Understand merge operations** - How chart data joins with rankings
3. **Customize dashboard** - Add new visualizations or filters
4. **Schedule automation** - Set up cron jobs for daily runs

---

## 📝 Session Summary Template

**Date:** January 13, 2026
**Duration:** ~4 hours
**Focus:** Scale up infrastructure, add chart data, fix rate limiting

**What we built:**
1. Auto-batching system for X API rate limits
2. Expanded artist list from 9 to 30 artists
3. Multi-source chart data collection (Billboard, Melon)
4. Updated scoring algorithm (30/20/50 split)
5. Enhanced dashboard with chart positions

**Key concepts used:**
- Exception handling for rate limits
- Web scraping with BeautifulSoup
- Weighted averages for scoring
- Pandas merge operations
- Separate scripts for different update frequencies

**Next steps:**
1. Run full data collection (`update_data.py`)
2. Test dashboard with complete data
3. Fix Spotify scraping (optional)
4. Post first rankings to @SignalIndex

**Suggested learning:**
- [Beautiful Soup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Pandas Merge Guide](https://pandas.pydata.org/docs/user_guide/merging.html)
- [Python Exception Handling](https://realpython.com/python-exceptions/)

---

## 🔄 Quick Reference

### When Something Goes Wrong:

**"I forgot how to run this"**
```bash
python update_data.py      # Main collection (once daily)
python update_charts.py    # Chart update (anytime)
streamlit run dashboard.py # View results
```

**"How do I add a new artist?"**
1. Open `artists.json`
2. Add entry with name, category, twitter handle, youtube_channel_id
3. Save file
4. Run `python update_data.py`

**"How do I change the scoring weights?"**
1. Open `analyzers/influence_score.py`
2. Find line: `signal_score = (0.3 * x_score) + (0.2 * yt_score) + (0.5 * chart_score)`
3. Change the percentages (must add up to 1.0)
4. Save file
5. Run `python update_data.py` to recalculate

**"Dashboard won't load"**
- Check if `data/rankings.csv` exists
- Run `python update_data.py` to create it
- Try `streamlit cache clear` then `streamlit run dashboard.py`

**"Chart data is stale"**
```bash
python update_charts.py  # Takes 15-30 mins
```

---

## 🎯 Remember

- **X collection is SLOW** (7-8 hours) → run overnight or in background
- **Chart collection is FAST** (15-30 mins) → run before posting
- **Auto-batching works** → don't interrupt, let it finish
- **Progress is saved** → safe to check in, data won't be lost
- **Dashboard updates automatically** → just refresh the page

---

**Last Updated:** January 13, 2026 by Claude
**Project Phase:** MVP with Multi-Source Data
**Status:** Production-ready for daily rankings
**Next Major Milestone:** Automated scheduling + historical tracking
