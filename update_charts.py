"""
Signal Index - Chart Data Collection Script

RUN THIS SCRIPT MULTIPLE TIMES PER DAY FOR FRESH CHART DATA

What it does:
1. Scrapes chart positions from multiple sources
2. Collects Spotify, Billboard, Melon, and other chart data
3. Saves to data/chart_data.csv
4. Fast execution (15-30 minutes vs 7-8 hours for X API)

How to run:
    python update_charts.py

When to run:
    - Multiple times per day for fresh chart data
    - Before posting rankings to @SignalIndex
    - After update_data.py completes (for full picture)

Outputs:
    data/chart_data.csv - Chart positions and streaming data
"""

import pandas as pd
from datetime import datetime
from collectors.chart_collector import collect_chart_data
import os


def main():
    """
    Main chart data collection pipeline

    PIPELINE STAGES:
    1. Scrape charts from multiple sources
    2. Save to CSV
    3. Display summary

    Tech note: This runs independently of update_data.py, so you can
    refresh chart data without waiting for X API rate limits.
    """

    # Header
    print("=" * 60)
    print(f"📊 SIGNAL INDEX - Chart Data Collection")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # ========================================
    # STAGE 1: Collect Chart Data
    # ========================================

    print("\n🌐 Scraping chart data from multiple sources...")
    print("   Sources: Spotify (Kworb), Billboard, Melon")
    print()

    chart_df = collect_chart_data()

    if chart_df.empty:
        print("\n❌ No chart data collected.")
        print("   This could mean:")
        print("   • Network issues")
        print("   • Chart sites are down")
        print("   • HTML structure changed (needs code update)")
        return

    # ========================================
    # STAGE 2: Save Data
    # ========================================

    chart_df.to_csv('data/chart_data.csv', index=False)
    print(f"\n💾 Saved {len(chart_df)} artist chart records → data/chart_data.csv")

    # ========================================
    # STAGE 3: Display Summary
    # ========================================

    print("\n" + "=" * 60)
    print("📈 CHART DATA SUMMARY")
    print("=" * 60)

    # Count artists with data from each source
    spotify_count = chart_df['spotify_position'].notna().sum() if 'spotify_position' in chart_df.columns else 0
    billboard_hot100_count = chart_df['billboard_hot100'].notna().sum() if 'billboard_hot100' in chart_df.columns else 0
    billboard_200_count = chart_df['billboard_200'].notna().sum() if 'billboard_200' in chart_df.columns else 0
    melon_count = chart_df['melon_position'].notna().sum() if 'melon_position' in chart_df.columns else 0

    print(f"\n📊 Artists charting:")
    print(f"   • Spotify (via Kworb): {spotify_count} artists")
    print(f"   • Billboard Hot 100: {billboard_hot100_count} artists")
    print(f"   • Billboard 200: {billboard_200_count} artists")
    print(f"   • Melon: {melon_count} artists")

    # Show top 5 on Spotify
    if spotify_count > 0:
        print(f"\n🎵 Top 5 on Spotify:")
        top_spotify = chart_df[chart_df['spotify_position'].notna()].nsmallest(5, 'spotify_position')
        for idx, row in top_spotify.iterrows():
            pos = row['spotify_position']
            name = row['celebrity']
            streams = row.get('spotify_streams', 0)
            if streams:
                streams_formatted = f"{int(streams):,}" if pd.notna(streams) else "N/A"
                print(f"   #{int(pos):>2}. {name:<20} {streams_formatted} streams")
            else:
                print(f"   #{int(pos):>2}. {name}")

    # Show top 5 on Billboard Hot 100
    if billboard_hot100_count > 0:
        print(f"\n🔥 Top 5 on Billboard Hot 100:")
        top_billboard = chart_df[chart_df['billboard_hot100'].notna()].nsmallest(5, 'billboard_hot100')
        for idx, row in top_billboard.iterrows():
            pos = row['billboard_hot100']
            name = row['celebrity']
            print(f"   #{int(pos):>2}. {name}")

    print("\n✨ Chart data collection complete!")
    print("▶️  Next: Run 'python update_data.py' for X/YouTube data")
    print("▶️  Or: Run 'streamlit run dashboard.py' to view rankings")
    print("=" * 60)


# ========================================
# SCRIPT ENTRY POINT
# ========================================

if __name__ == "__main__":
    main()


# ========================================
# EDUCATIONAL NOTE: Why Separate Scripts?
# ========================================
#
# CHART DATA (update_charts.py):
# - Fast: 15-30 minutes
# - No rate limits
# - Updates multiple times per day
# - Web scraping-based
#
# SOCIAL MEDIA DATA (update_data.py):
# - Slow: 7-8 hours
# - Rate limited (X API)
# - Once per day is enough
# - API-based
#
# By separating them, you get:
# 1. Fresh chart data throughout the day
# 2. Don't wait 8 hours just to update charts
# 3. Can run charts even if X API is down
# 4. Better debugging (isolate issues)
#
# TYPICAL WORKFLOW:
# - Morning: python update_data.py & (runs in background)
# - Anytime: python update_charts.py (quick refresh)
# - Before posting: python update_charts.py (latest data)
#
# ========================================
