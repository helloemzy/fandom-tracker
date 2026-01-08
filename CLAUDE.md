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
