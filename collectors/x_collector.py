"""
X/Twitter Data Collector
Fetches recent tweets and engagement metrics for tracked artists

DATA FLOW: X API → This script → CSV file → Dashboard

RATE LIMIT HANDLING:
This collector automatically handles X API rate limits by:
1. Detecting when rate limit is hit (TooManyRequests exception)
2. Saving progress so far
3. Waiting 15 minutes (with countdown display)
4. Resuming collection automatically
"""

import tweepy
import pandas as pd
from datetime import datetime
import time
import os
from config import X_BEARER_TOKEN, load_artists, PRODUCT_KEYWORDS


def collect_x_data():
    """
    Collect latest tweets from all active artists

    What this does:
    1. Loads active artists from artists.json
    2. For each artist, fetches their last 3 tweets
    3. Calculates engagement (likes + retweets)
    4. Checks if tweets mention products
    5. Returns everything as a DataFrame (like an Excel table)

    NEW: Automatically handles rate limits by:
    - Saving progress incrementally
    - Waiting 15 minutes when rate limit hits
    - Resuming from where it left off

    Returns: pandas DataFrame with columns:
        - celebrity: Artist name
        - category: K-pop, Western, etc.
        - platform: Always 'X' for this collector
        - date: When we collected the data
        - engagement: Total likes + retweets
        - likes, retweets, replies: Individual metrics
        - has_product_mention: True if tweet mentions merch/albums/etc.
        - follower_count: How many followers the artist has
        - text_preview: First 100 characters of the tweet
    """

    # Check if API token is configured
    if not X_BEARER_TOKEN:
        print("❌ X API token not configured")
        print("   👉 Copy .env.example to .env and add your API key")
        return pd.DataFrame()  # Return empty DataFrame

    # Load active artists from artists.json
    artists = load_artists()

    if not artists:
        print("❌ No active artists found in artists.json")
        return pd.DataFrame()

    print(f"📱 Tracking {len(artists)} active artists on X")

    # Initialize X/Twitter API client
    # Think of this as "logging into Twitter"
    client = tweepy.Client(bearer_token=X_BEARER_TOKEN)

    # This list will store all our collected data
    all_data = []

    # Track which artists we've successfully collected
    collected_artists = set()

    # Loop through each artist
    artist_index = 0
    while artist_index < len(artists):
        artist = artists[artist_index]
        name = artist['name']
        username = artist['twitter']

        # Skip if we already collected this artist (after a rate limit wait)
        if name in collected_artists:
            artist_index += 1
            continue

        try:
            # Step 1: Get user information
            # This is like looking up someone's profile page
            user = client.get_user(
                username=username,
                user_fields=['public_metrics']  # Request follower count, etc.
            )

            if not user.data:
                print(f"  ⚠️  User not found: @{username}")
                collected_artists.add(name)  # Mark as processed (even though failed)
                artist_index += 1
                continue  # Skip to next artist

            # Step 2: Get their recent tweets
            # We get 5 tweets (Twitter API minimum is 5)
            tweets = client.get_users_tweets(
                id=user.data.id,
                max_results=5,  # Minimum allowed by Twitter API
                tweet_fields=['created_at', 'public_metrics', 'text']
            )

            if tweets.data:
                # Process each tweet
                for tweet in tweets.data:
                    # Check if tweet mentions products
                    # Convert to lowercase for case-insensitive matching
                    text_lower = tweet.text.lower()
                    has_product = any(kw in text_lower for kw in PRODUCT_KEYWORDS)

                    # Get engagement metrics from the tweet
                    metrics = tweet.public_metrics

                    # Calculate total engagement
                    # Why likes + retweets? These show active fan engagement
                    total_engagement = metrics['like_count'] + metrics['retweet_count']

                    # Store everything in a dictionary (like a spreadsheet row)
                    all_data.append({
                        'celebrity': name,
                        'category': artist.get('category', 'Other'),
                        'platform': 'X',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'engagement': total_engagement,
                        'likes': metrics['like_count'],
                        'retweets': metrics['retweet_count'],
                        'replies': metrics['reply_count'],
                        'has_product_mention': has_product,
                        'follower_count': user.data.public_metrics['followers_count'],
                        'text_preview': tweet.text[:100]  # First 100 chars
                    })

                print(f"  ✅ {name}: {len(tweets.data)} tweets collected")

            # Mark this artist as successfully collected
            collected_artists.add(name)
            artist_index += 1

            # RATE LIMITING: Wait 2 seconds between artists
            # Why? Twitter limits how many requests we can make per minute
            # Think of it like: "Don't refresh the page too fast or you'll get blocked"
            time.sleep(2)

        except tweepy.TooManyRequests:
            # Oops, we hit the rate limit!
            print(f"\n⚠️  Rate limit hit after collecting {len(collected_artists)}/{len(artists)} artists")

            # Save progress so far
            if all_data:
                _save_progress(all_data)

            # Calculate remaining artists
            remaining = len(artists) - len(collected_artists)
            print(f"   📊 Progress: {len(collected_artists)} collected, {remaining} remaining")
            print(f"   ⏳ Waiting 15 minutes for rate limit to reset...")
            print(f"   💡 This is automatic - no need to do anything!")

            # Wait 15 minutes with progress updates
            _wait_for_rate_limit_reset()

            print(f"   ✅ Rate limit reset! Resuming collection...")
            # Don't increment artist_index - we'll retry this artist

        except Exception as e:
            # Something else went wrong (network error, account suspended, etc.)
            print(f"  ❌ Error fetching @{username}: {str(e)}")
            collected_artists.add(name)  # Mark as processed to avoid retry loop
            artist_index += 1
            continue  # Skip this artist but keep going

    # Convert list of dictionaries to a pandas DataFrame
    # This is like converting a stack of index cards into a spreadsheet
    print(f"\n✅ X collection complete: {len(collected_artists)}/{len(artists)} artists collected")
    return pd.DataFrame(all_data)


def _save_progress(all_data):
    """
    Save collected data to CSV so progress isn't lost

    This creates a temporary file that gets overwritten by the final save
    in update_data.py, but ensures we don't lose data if something crashes
    """
    os.makedirs('data', exist_ok=True)
    df = pd.DataFrame(all_data)
    df.to_csv('data/x_data.csv', index=False)
    print(f"   💾 Progress saved: {len(all_data)} data points → data/x_data.csv")


def _wait_for_rate_limit_reset():
    """
    Wait 15 minutes (900 seconds) with a user-friendly countdown

    Shows progress every minute so you know it's working
    """
    wait_time = 900  # 15 minutes in seconds

    for remaining in range(wait_time, 0, -60):
        minutes = remaining // 60
        seconds = remaining % 60

        if minutes > 0:
            print(f"   ⏰ {minutes} min {seconds} sec remaining...", end='\r')
        else:
            print(f"   ⏰ {seconds} sec remaining...      ", end='\r')

        # Sleep for 60 seconds (or less if we're in the final minute)
        time.sleep(min(60, remaining))

    print("\n")  # New line after countdown
