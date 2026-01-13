"""
YouTube Data Collector
Fetches recent video metrics for tracked artists

DATA FLOW: YouTube API → This script → CSV file → Dashboard
"""

from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime, timedelta
import time
from config import YOUTUBE_API_KEY, load_artists


def collect_youtube_data():
    """
    Collect latest video metrics from all active artists

    What this does:
    1. Loads active artists from artists.json
    2. For each artist with a YouTube channel, finds their latest 3 videos
    3. Gets view count, likes, and comments for each video
    4. Returns everything as a DataFrame

    Why only videos from the last 90 days?
    - Recent videos show current momentum
    - 90-day window captures artists who don't post as frequently
    - Old viral videos don't reflect current influence

    Returns: pandas DataFrame with columns:
        - celebrity: Artist name
        - category: K-pop, Western, etc.
        - platform: Always 'YouTube' for this collector
        - date: When we collected the data
        - video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
        - title: Video title
        - views: Total view count
        - likes: Total likes
        - comments: Total comments
        - published: When the video was uploaded
    """

    # Check if API key is configured
    if not YOUTUBE_API_KEY:
        print("❌ YouTube API key not configured")
        print("   👉 Copy .env.example to .env and add your API key")
        return pd.DataFrame()

    # Load active artists from artists.json
    artists = load_artists()

    if not artists:
        print("❌ No active artists found in artists.json")
        return pd.DataFrame()

    # Count artists with YouTube channels
    # Some artists (like Hailey Bieber) might not have YouTube
    yt_artists = [a for a in artists if a.get('youtube_channel_id')]
    print(f"📺 Tracking {len(yt_artists)} artists on YouTube")

    # Initialize YouTube API client
    # This is like opening the YouTube app
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

    # Storage for collected data
    all_data = []

    # Loop through each artist
    for artist in artists:
        name = artist['name']
        channel_id = artist.get('youtube_channel_id')

        # Skip if no YouTube channel
        if not channel_id:
            print(f"  ⏭️  {name}: No YouTube channel")
            continue

        try:
            # Calculate date 90 days ago
            # YouTube API requires this in ISO format (e.g., "2024-01-07T00:00:00Z")
            # Changed from 30 to 90 days to capture more artists who don't post as frequently
            ninety_days_ago = (datetime.now() - timedelta(days=90)).isoformat() + 'Z'

            # Step 1: Search for recent videos from this channel
            search_response = youtube.search().list(
                part='id,snippet',  # Get video IDs and basic info
                channelId=channel_id,
                maxResults=3,  # Last 3 videos
                order='date',  # Most recent first
                type='video',  # Only videos (not playlists or channels)
                publishedAfter=ninety_days_ago  # Extended to 90 days for better coverage
            ).execute()

            # Step 2: For each video, get detailed statistics
            for item in search_response.get('items', []):
                video_id = item['id']['videoId']

                # Get view count, likes, comments
                stats_response = youtube.videos().list(
                    part='statistics,snippet',
                    id=video_id
                ).execute()

                if stats_response['items']:
                    video = stats_response['items'][0]
                    stats = video['statistics']

                    # Store video data
                    all_data.append({
                        'celebrity': name,
                        'category': artist.get('category', 'Other'),
                        'platform': 'YouTube',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'video_id': video_id,
                        'title': video['snippet']['title'][:100],  # Truncate long titles
                        'views': int(stats.get('viewCount', 0)),
                        'likes': int(stats.get('likeCount', 0)),
                        'comments': int(stats.get('commentCount', 0)),
                        'published': video['snippet']['publishedAt'][:10]  # Just the date
                    })

            video_count = len(search_response.get('items', []))
            print(f"  ✅ {name}: {video_count} videos collected")

            # RATE LIMITING: Wait 1 second between artists
            # YouTube API is more generous than Twitter, but still has limits
            time.sleep(1)

        except Exception as e:
            # Handle errors gracefully
            print(f"  ❌ Error fetching YouTube for {name}: {str(e)}")
            continue  # Skip this artist but keep going

    # Convert to DataFrame
    return pd.DataFrame(all_data)


# ========================================
# EDUCATIONAL NOTE: YouTube API Quotas
# ========================================
#
# YouTube API has a daily quota limit (10,000 units/day for free tier)
# Each search costs ~100 units, each video details call costs ~1 unit
#
# For 10 artists × 3 videos each:
# - 10 search calls = 1,000 units
# - 30 video detail calls = 30 units
# - Total = ~1,030 units (well within daily limit)
#
# You can check your quota usage at:
# https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas
#
# ========================================
