"""
Signal Index Score Calculator

THE ALGORITHM:
Final Score = (60% × X Engagement Score) + (40% × YouTube Momentum Score)

WHY THIS FORMULA?
- X engagement shows IMMEDIATE fan excitement (likes/retweets happen fast)
- YouTube views show SUSTAINED interest (videos accumulate views over days)
- 60/40 split because X is more reactive to real-time trends

This is a simplified MVP. Future versions might include:
- Spotify monthly listeners
- Reddit mention volume
- TikTok engagement
- Time-based weighting (recent activity counts more)
"""

import pandas as pd


def calculate_signal_score(x_df, yt_df):
    """
    Calculate Signal Index scores for all artists

    Input:
        x_df: DataFrame from X collector (tweets and engagement)
        yt_df: DataFrame from YouTube collector (videos and views)

    Output:
        DataFrame with columns:
            - celebrity: Artist name
            - category: K-pop, Western, etc.
            - signal_score: 0-100 score (higher = more influential)
            - x_engagement_rate: Engagement per follower (%)
            - youtube_views: Total recent video views
            - product_mentions: How many tweets mentioned products
            - x_component: Contribution from X (max 100)
            - yt_component: Contribution from YouTube (max 100)

    HOW IT WORKS:
    1. Calculate engagement rate for each artist on X
    2. Calculate total recent views on YouTube
    3. Normalize both to 0-100 scale
    4. Combine with 60/40 weighting
    """

    scores = []

    # Get unique list of all artists from both data sources
    # Using set() removes duplicates, then | combines both sets
    # Handle empty DataFrames gracefully
    x_celebs = set(x_df['celebrity'].unique()) if not x_df.empty else set()
    yt_celebs = set(yt_df['celebrity'].unique()) if not yt_df.empty else set()
    all_celebs = x_celebs | yt_celebs

    for celebrity in all_celebs:
        # Determine category (some artists might only be on one platform)
        category = 'Other'
        if not x_df.empty and not x_df[x_df['celebrity'] == celebrity].empty:
            category = x_df[x_df['celebrity'] == celebrity]['category'].iloc[0]
        elif not yt_df.empty and not yt_df[yt_df['celebrity'] == celebrity].empty:
            category = yt_df[yt_df['celebrity'] == celebrity]['category'].iloc[0]

        # ========================================
        # X METRICS CALCULATION
        # ========================================

        celeb_x = x_df[x_df['celebrity'] == celebrity] if not x_df.empty else pd.DataFrame()

        if not celeb_x.empty:
            # Average engagement across their recent tweets
            avg_engagement = celeb_x['engagement'].mean()

            # Get follower count
            follower_count = celeb_x['follower_count'].iloc[0]

            # Calculate engagement RATE (not just raw numbers)
            # Why? An artist with 100M followers getting 10K likes (0.01%)
            # is less engaged than one with 1M followers getting 50K likes (5%)
            if follower_count > 0:
                engagement_rate = (avg_engagement / follower_count * 100)
            else:
                engagement_rate = 0

            # Normalize to 0-100 scale
            # Multiply by 20 because typical engagement rates are 0-5%
            # Use min() to cap at 100
            x_score = min(engagement_rate * 20, 100)

            # Count product mentions
            product_mentions = celeb_x['has_product_mention'].sum()

        else:
            # No X data for this artist
            x_score = 0
            engagement_rate = 0
            product_mentions = 0

        # ========================================
        # YOUTUBE METRICS CALCULATION
        # ========================================

        celeb_yt = yt_df[yt_df['celebrity'] == celebrity] if not yt_df.empty else pd.DataFrame()

        if not celeb_yt.empty:
            # Sum all recent video views
            total_views = celeb_yt['views'].sum()

            # Normalize to 0-100 scale
            # Divide by 1M and multiply by 10 means:
            # - 10M views = score of 100
            # - 5M views = score of 50
            # - 1M views = score of 10
            yt_score = min(total_views / 1_000_000 * 10, 100)

        else:
            # No YouTube data for this artist
            total_views = 0
            yt_score = 0

        # ========================================
        # FINAL WEIGHTED SCORE
        # ========================================

        # 60% X + 40% YouTube
        signal_score = (0.6 * x_score) + (0.4 * yt_score)

        # Store results
        scores.append({
            'celebrity': celebrity,
            'category': category,
            'signal_score': round(signal_score, 1),
            'x_engagement_rate': round(engagement_rate, 3) if not celeb_x.empty else 0,
            'youtube_views': int(total_views),
            'product_mentions': int(product_mentions),
            'x_component': round(x_score, 1),
            'yt_component': round(yt_score, 1)
        })

    # Convert to DataFrame and sort by score (highest first)
    results = pd.DataFrame(scores).sort_values('signal_score', ascending=False)

    return results


# ========================================
# EDUCATIONAL NOTE: Data Normalization
# ========================================
#
# WHY NORMALIZE?
# You can't directly compare "1M YouTube views" to "5% engagement rate"
# They're different units! Like comparing apples to oranges.
#
# SOLUTION:
# Convert both to the same 0-100 scale, then we can combine them
#
# ANALOGY:
# Think of grading in school:
# - Math test: 95/100 points
# - English essay: 8/10 points
# To calculate GPA, we normalize both to 0-100 scale first
#
# HOW TO ADJUST:
# If you notice all scores are too low (e.g., max is 30), increase the multiplier
# If all scores hit 100, decrease the multiplier
#
# Current multipliers:
# - X: engagement_rate × 20 (assumes 5% is excellent)
# - YouTube: views / 1M × 10 (assumes 10M is excellent)
#
# ========================================
