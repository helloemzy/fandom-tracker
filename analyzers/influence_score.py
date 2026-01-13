"""
Signal Index Score Calculator

THE ALGORITHM (Updated with Chart Data):
Final Score = (30% × X Engagement) + (20% × YouTube Momentum) + (50% × Chart Performance)

WHY THIS FORMULA?
- X engagement shows IMMEDIATE fan excitement (likes/retweets happen fast) - 30%
- YouTube views show SUSTAINED interest (videos accumulate over days) - 20%
- Chart positions show COMMERCIAL SUCCESS (what's actually selling/streaming) - 50%

CHART COMPONENT BREAKDOWN:
- Spotify position (via Kworb) - 40%
- Billboard Hot 100 - 30%
- Billboard 200 - 15%
- Melon (for K-pop) - 15%

Future additions might include:
- Brand reputation indices
- Reddit/TikTok engagement
- Sales data (Hanteo, Circle Chart)
"""

import pandas as pd


def calculate_signal_score(x_df, yt_df, chart_df=None):
    """
    Calculate Signal Index scores for all artists

    Input:
        x_df: DataFrame from X collector (tweets and engagement)
        yt_df: DataFrame from YouTube collector (videos and views)
        chart_df: DataFrame from chart collector (chart positions) - OPTIONAL

    Output:
        DataFrame with columns:
            - celebrity: Artist name
            - category: K-pop, Western, etc.
            - signal_score: 0-100 score (higher = more influential)
            - x_engagement_rate: Engagement per follower (%)
            - youtube_views: Total recent video views
            - chart_position: Best chart position across all charts
            - product_mentions: How many tweets mentioned products
            - x_component: Contribution from X (max 100)
            - yt_component: Contribution from YouTube (max 100)
            - chart_component: Contribution from charts (max 100)

    HOW IT WORKS:
    1. Calculate engagement rate for each artist on X
    2. Calculate total recent views on YouTube
    3. Calculate weighted chart score from multiple sources
    4. Normalize all to 0-100 scale
    5. Combine with 30/20/50 weighting
    """

    scores = []

    # Get unique list of all artists from all data sources
    x_celebs = set(x_df['celebrity'].unique()) if not x_df.empty else set()
    yt_celebs = set(yt_df['celebrity'].unique()) if not yt_df.empty else set()
    chart_celebs = set(chart_df['celebrity'].unique()) if chart_df is not None and not chart_df.empty else set()

    all_celebs = x_celebs | yt_celebs | chart_celebs

    for celebrity in all_celebs:
        # Determine category
        category = 'Other'
        if not x_df.empty and not x_df[x_df['celebrity'] == celebrity].empty:
            category = x_df[x_df['celebrity'] == celebrity]['category'].iloc[0]
        elif not yt_df.empty and not yt_df[yt_df['celebrity'] == celebrity].empty:
            category = yt_df[yt_df['celebrity'] == celebrity]['category'].iloc[0]
        elif chart_df is not None and not chart_df.empty and not chart_df[chart_df['celebrity'] == celebrity].empty:
            category = chart_df[chart_df['celebrity'] == celebrity]['category'].iloc[0]

        # ========================================
        # X METRICS CALCULATION
        # ========================================

        celeb_x = x_df[x_df['celebrity'] == celebrity] if not x_df.empty else pd.DataFrame()

        if not celeb_x.empty:
            avg_engagement = celeb_x['engagement'].mean()
            follower_count = celeb_x['follower_count'].iloc[0]

            if follower_count > 0:
                engagement_rate = (avg_engagement / follower_count * 100)
            else:
                engagement_rate = 0

            # Normalize to 0-100 scale
            # Multiply by 20 because typical engagement rates are 0-5%
            x_score = min(engagement_rate * 20, 100)

            product_mentions = celeb_x['has_product_mention'].sum()

        else:
            x_score = 0
            engagement_rate = 0
            product_mentions = 0

        # ========================================
        # YOUTUBE METRICS CALCULATION
        # ========================================

        celeb_yt = yt_df[yt_df['celebrity'] == celebrity] if not yt_df.empty else pd.DataFrame()

        if not celeb_yt.empty:
            total_views = celeb_yt['views'].sum()

            # Normalize to 0-100 scale
            # 10M views = score of 100
            yt_score = min(total_views / 1_000_000 * 10, 100)

        else:
            total_views = 0
            yt_score = 0

        # ========================================
        # CHART METRICS CALCULATION (NEW!)
        # ========================================

        celeb_chart = chart_df[chart_df['celebrity'] == celebrity] if chart_df is not None and not chart_df.empty else pd.DataFrame()

        if not celeb_chart.empty:
            # Get chart positions (lower number = better position)
            spotify_pos = celeb_chart['spotify_position'].iloc[0] if 'spotify_position' in celeb_chart.columns else None
            billboard_hot100 = celeb_chart['billboard_hot100'].iloc[0] if 'billboard_hot100' in celeb_chart.columns else None
            billboard_200 = celeb_chart['billboard_200'].iloc[0] if 'billboard_200' in celeb_chart.columns else None
            melon_pos = celeb_chart['melon_position'].iloc[0] if 'melon_position' in celeb_chart.columns else None

            # Convert chart positions to 0-100 scores
            # Formula: score = 100 - (position - 1)
            # #1 = 100 points, #2 = 99 points, #50 = 51 points, #100 = 1 point
            # If not charting (position > 100 or None), score = 0

            def position_to_score(position, max_position=100):
                """Convert chart position to 0-100 score"""
                if pd.isna(position) or position is None:
                    return 0
                if position > max_position:
                    return 0
                return max(100 - (position - 1), 0)

            spotify_score = position_to_score(spotify_pos, 200)  # Spotify has larger charts
            billboard_hot100_score = position_to_score(billboard_hot100, 100)
            billboard_200_score = position_to_score(billboard_200, 200)
            melon_score = position_to_score(melon_pos, 100)

            # Weighted average of chart scores
            # Spotify (40%), Billboard Hot 100 (30%), Billboard 200 (15%), Melon (15%)
            chart_weights = []
            chart_scores = []

            if spotify_score > 0:
                chart_weights.append(0.40)
                chart_scores.append(spotify_score)

            if billboard_hot100_score > 0:
                chart_weights.append(0.30)
                chart_scores.append(billboard_hot100_score)

            if billboard_200_score > 0:
                chart_weights.append(0.15)
                chart_scores.append(billboard_200_score)

            # Melon only counts for K-pop artists
            if category == 'K-pop' and melon_score > 0:
                chart_weights.append(0.15)
                chart_scores.append(melon_score)

            # Calculate weighted average
            if chart_weights:
                total_weight = sum(chart_weights)
                chart_score = sum(w * s for w, s in zip(chart_weights, chart_scores)) / total_weight
            else:
                chart_score = 0

            # Track best position for display
            best_position = None
            for pos in [spotify_pos, billboard_hot100, billboard_200, melon_pos]:
                if pd.notna(pos) and (best_position is None or pos < best_position):
                    best_position = pos

        else:
            # No chart data for this artist
            chart_score = 0
            best_position = None

        # ========================================
        # FINAL WEIGHTED SCORE
        # ========================================

        # 30% X + 20% YouTube + 50% Charts
        signal_score = (0.3 * x_score) + (0.2 * yt_score) + (0.5 * chart_score)

        # Store results
        scores.append({
            'celebrity': celebrity,
            'category': category,
            'signal_score': round(signal_score, 1),
            'x_engagement_rate': round(engagement_rate, 3) if not celeb_x.empty else 0,
            'youtube_views': int(total_views),
            'chart_position': int(best_position) if best_position is not None else None,
            'product_mentions': int(product_mentions),
            'x_component': round(x_score, 1),
            'yt_component': round(yt_score, 1),
            'chart_component': round(chart_score, 1)
        })

    # Convert to DataFrame and sort by score (highest first)
    results = pd.DataFrame(scores).sort_values('signal_score', ascending=False)

    return results


# ========================================
# EDUCATIONAL NOTE: Why Charts Get 50%?
# ========================================
#
# CHART POSITIONS = COMMERCIAL SUCCESS
# - Reflect actual purchasing/streaming behavior
# - Aggregate data from millions of users
# - Less prone to bot manipulation than social metrics
# - Industry standard for measuring popularity
#
# SOCIAL MEDIA (X + YouTube) = 50%
# - Shows fan engagement and excitement
# - More reactive to trends and moments
# - Important for influence, but can be inflated
#
# BALANCED APPROACH:
# We weight both aspects to capture:
# 1. Commercial success (charts)
# 2. Fan engagement (social media)
#
# This gives a more complete picture of influence
# than either metric alone.
#
# ========================================


# ========================================
# EDUCATIONAL NOTE: Chart Score Calculation
# ========================================
#
# WHY CONVERT POSITIONS TO SCORES?
# Chart position #1 should be worth way more than #100
# But we can't just use the raw numbers (1 vs 100)
#
# OUR FORMULA:
# Score = 100 - (position - 1)
#
# EXAMPLES:
# Position #1  → Score 100
# Position #10 → Score 91
# Position #50 → Score 51
# Position #100 → Score 1
# Not charting → Score 0
#
# THEN WE WEIGHT:
# - Spotify: 40% (largest streaming platform)
# - Billboard Hot 100: 30% (most prestigious singles chart)
# - Billboard 200: 15% (albums chart)
# - Melon: 15% (dominant in Korea, K-pop only)
#
# ========================================
