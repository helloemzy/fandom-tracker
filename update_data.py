"""
Signal Index - Main Data Collection Script

RUN THIS SCRIPT DAILY TO UPDATE YOUR DASHBOARD

What it does:
1. Loads your artist list from artists.json
2. Collects data from X (Twitter) API
3. Collects data from YouTube API
4. Calculates Signal Index scores
5. Saves everything to CSV files in data/
6. Shows you the top 5 influencers

How to run:
    python update_data.py

When to run:
    Once per day (or whenever you want fresh data)
    Recommended: Early morning before posting rankings to @SignalIndex

Outputs:
    data/x_data.csv - Raw X/Twitter metrics
    data/youtube_data.csv - Raw YouTube metrics
    data/rankings.csv - Final Signal Index scores

After running:
    streamlit run dashboard.py
"""

import pandas as pd
from datetime import datetime
from collectors.x_collector import collect_x_data
from collectors.youtube_collector import collect_youtube_data
from analyzers.influence_score import calculate_signal_score
from config import load_artists
import os


def main():
    """
    Main data collection pipeline

    PIPELINE STAGES:
    1. Load artists
    2. Collect X data
    3. Collect YouTube data
    4. Calculate scores
    5. Save results
    6. Display summary
    """

    # Header
    print("=" * 60)
    print(f"🚀 SIGNAL INDEX - Data Collection")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ========================================
    # STAGE 1: Load Artists
    # ========================================

    artists = load_artists()

    if not artists:
        print("\n❌ No active artists found!")
        print("   👉 Add artists to artists.json or use the dashboard")
        return

    print(f"\n👥 Tracking {len(artists)} active artists:")
    for artist in artists:
        # Show artist name and category
        print(f"  • {artist['name']} ({artist.get('category', 'Other')})")

    # Create data directory if it doesn't exist
    # os.makedirs with exist_ok=True means: "create if needed, no error if exists"
    os.makedirs('data', exist_ok=True)

    # ========================================
    # STAGE 2: Collect X (Twitter) Data
    # ========================================

    print("\n" + "=" * 60)
    print("📱 COLLECTING X (TWITTER) DATA")
    print("=" * 60)

    x_df = collect_x_data()

    # ========================================
    # STAGE 3: Collect YouTube Data
    # ========================================

    print("\n" + "=" * 60)
    print("📺 COLLECTING YOUTUBE DATA")
    print("=" * 60)

    yt_df = collect_youtube_data()

    print("=" * 60)

    # Check if we got any data
    if x_df.empty and yt_df.empty:
        print("\n❌ No data collected. Check API configuration.")
        print("   👉 Make sure .env file has valid API keys")
        print("   👉 Copy .env.example to .env if you haven't yet")
        return

    # ========================================
    # STAGE 4: Save Raw Data
    # ========================================

    if not x_df.empty:
        # Save to CSV file
        x_df.to_csv('data/x_data.csv', index=False)
        print(f"\n💾 Saved {len(x_df)} X data points → data/x_data.csv")

    if not yt_df.empty:
        yt_df.to_csv('data/youtube_data.csv', index=False)
        print(f"💾 Saved {len(yt_df)} YouTube data points → data/youtube_data.csv")

    # ========================================
    # STAGE 5: Load Chart Data (if available)
    # ========================================

    # Try to load chart data if it exists
    # Chart data is collected separately via update_charts.py
    chart_df = pd.DataFrame()
    if os.path.exists('data/chart_data.csv'):
        try:
            chart_df = pd.read_csv('data/chart_data.csv')
            print(f"\n📊 Loaded chart data: {len(chart_df)} artists")
        except Exception as e:
            print(f"\n⚠️  Could not load chart data: {str(e)}")
            chart_df = pd.DataFrame()
    else:
        print(f"\n💡 No chart data found. Run 'python update_charts.py' to collect chart data.")

    # ========================================
    # STAGE 6: Calculate Rankings
    # ========================================

    print("\n📊 Calculating Signal Index scores...")

    rankings = calculate_signal_score(x_df, yt_df, chart_df if not chart_df.empty else None)

    # Add today's date to the rankings
    rankings['date'] = datetime.now().strftime('%Y-%m-%d')

    # Save rankings
    rankings.to_csv('data/rankings.csv', index=False)

    # ========================================
    # STAGE 6: Display Results
    # ========================================

    print("\n" + "=" * 60)
    print("🏆 TOP 5 INFLUENCERS")
    print("=" * 60)

    # Display top 5 with formatted output
    for idx, row in rankings.head(5).iterrows():
        # Format: "1. Taylor Swift        Score: 85.3 (Western)"
        # :<20 means left-align with 20 characters of space
        # :>5.1f means right-align with 5 characters, 1 decimal place
        rank = idx + 1
        name = row['celebrity']
        score = row['signal_score']
        category = row['category']

        print(f"{rank}. {name:<20} Score: {score:>5.1f} ({category})")

    # Success message
    print("\n✨ Data collection complete!")
    print("▶️  Run dashboard: streamlit run dashboard.py")
    print("=" * 60)


# ========================================
# SCRIPT ENTRY POINT
# ========================================

# This is Python's way of saying: "Only run main() if this script
# is executed directly (not if it's imported by another script)"
if __name__ == "__main__":
    main()


# ========================================
# EDUCATIONAL NOTE: CSV Files
# ========================================
#
# WHY USE CSV FILES?
# - Simple: You can open them in Excel/Google Sheets
# - Debuggable: Easy to inspect what data was collected
# - Portable: Works on any computer, no database setup
# - Version controllable: Can track changes over time
#
# WHEN TO UPGRADE TO A DATABASE?
# - When you have 100,000+ rows (CSVs get slow)
# - When you need complex queries (filtering, joining)
# - When multiple users access simultaneously
# - For now: CSV is perfect for your MVP!
#
# ========================================
