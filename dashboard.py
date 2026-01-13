"""
Signal Index Dashboard - MVP Version

WHAT IS STREAMLIT?
Streamlit is a Python library that turns scripts into web apps.
You write Python, it creates the HTML/CSS/JavaScript for you.

HOW TO RUN:
    streamlit run dashboard.py

WHAT YOU'LL SEE:
- Page 1: Top Influencers (rankings and charts)
- Page 2: Spending Signals (product mentions)
- Page 3: Post Generator (create X/Twitter posts)
- Page 4: Manage Artists (add/disable artists)

TECHNICAL NOTES:
- @st.cache_data: Prevents re-loading CSV files on every click (performance boost)
- st.columns: Creates side-by-side layout (like newspaper columns)
- st.form: Groups inputs together (submits all at once)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import json
from config import load_artists, add_artist, toggle_artist, save_artists

# ========================================
# PAGE CONFIGURATION
# ========================================

# This must be the FIRST Streamlit command
st.set_page_config(
    page_title="Signal Index",  # Browser tab title
    page_icon="📊",  # Browser tab icon (emoji)
    layout="wide"  # Use full width (vs centered narrow column)
)

# ========================================
# CUSTOM STYLING
# ========================================

# CSS (Cascading Style Sheets) controls how things look
# We inject it using st.markdown with unsafe_allow_html=True
st.markdown("""
<style>
    .big-title {
        font-size: 36px;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 20px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ========================================
# DATA LOADING FUNCTION
# ========================================

@st.cache_data(ttl=3600)  # Cache for 1 hour (3600 seconds)
def load_data():
    """
    Load all data files

    @st.cache_data decorator means: "Remember this result for 1 hour"
    Why? So we don't re-read CSV files on every button click

    Returns: (rankings_df, x_data_df, yt_data_df, chart_data_df)
    """
    try:
        rankings = pd.read_csv('data/rankings.csv')

        # Check if other files exist (they might not on first run)
        if os.path.exists('data/x_data.csv'):
            x_data = pd.read_csv('data/x_data.csv')
        else:
            x_data = pd.DataFrame()

        if os.path.exists('data/youtube_data.csv'):
            yt_data = pd.read_csv('data/youtube_data.csv')
        else:
            yt_data = pd.DataFrame()

        if os.path.exists('data/chart_data.csv'):
            chart_data = pd.read_csv('data/chart_data.csv')
        else:
            chart_data = pd.DataFrame()

        return rankings, x_data, yt_data, chart_data

    except Exception as e:
        # If any error (file not found, corrupted CSV, etc.)
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()


# Load data
rankings, x_data, yt_data, chart_data = load_data()

# Merge chart data into rankings if available
if not chart_data.empty and not rankings.empty:
    rankings = rankings.merge(
        chart_data[['celebrity', 'spotify_position', 'billboard_hot100', 'billboard_200', 'melon_position']],
        on='celebrity',
        how='left'
    )

# ========================================
# HEADER
# ========================================

st.markdown('<div class="big-title">📊 SIGNAL INDEX</div>', unsafe_allow_html=True)
st.markdown("**Tracking Celebrity Influence on Consumer Behavior**")

# Show last update date if we have data
if not rankings.empty:
    last_update = rankings['date'].iloc[0]
    st.info(f"📅 Last updated: {last_update}")

# ========================================
# SIDEBAR NAVIGATION
# ========================================

# Sidebar stays visible on the left while pages change
page = st.sidebar.radio("📍 Navigate", [
    "🏆 Top Influencers",
    "💰 Spending Signals",
    "✍️ Post Generator",
    "⚙️ Manage Artists"
])

# ========================================
# PAGE 1: TOP INFLUENCERS
# ========================================

if page == "🏆 Top Influencers":

    # Check if we have data
    if rankings.empty:
        st.warning("⚠️ No data available. Run: `python update_data.py`")
        st.stop()  # Stop rendering the page

    st.header("TOP INFLUENCING ARTISTS THIS WEEK")

    # Category filter dropdown
    categories = ['All'] + sorted(rankings['category'].unique().tolist())
    selected_category = st.selectbox("Filter by Category", categories)

    # Filter data based on selection
    if selected_category != 'All':
        filtered_rankings = rankings[rankings['category'] == selected_category]
    else:
        filtered_rankings = rankings

    # Get top 10
    top_10 = filtered_rankings.head(10).copy()
    top_10.insert(0, 'Rank', range(1, len(top_10) + 1))  # Add rank column

    # ========================================
    # STYLED TABLE (using Plotly)
    # ========================================

    # Plotly creates interactive charts/tables
    # go.Table creates a styled table (better than st.dataframe)

    # Helper function to format chart positions
    def format_chart_position(pos):
        if pd.isna(pos) or pos is None:
            return '-'
        return f"#{int(pos)}"

    # Helper function to format best chart with source
    def format_best_chart(row):
        positions = []
        if pd.notna(row.get('spotify_position')):
            positions.append(('Spotify', row['spotify_position']))
        if pd.notna(row.get('billboard_hot100')):
            positions.append(('BB Hot 100', row['billboard_hot100']))
        if pd.notna(row.get('billboard_200')):
            positions.append(('BB 200', row['billboard_200']))
        if pd.notna(row.get('melon_position')):
            positions.append(('Melon', row['melon_position']))

        if positions:
            best = min(positions, key=lambda x: x[1])
            return f"#{int(best[1])} ({best[0]})"
        return '-'

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['<b>Rank</b>', '<b>Artist</b>', '<b>Category</b>', '<b>Signal Score</b>',
                   '<b>Best Chart</b>', '<b>Spotify</b>', '<b>BB Hot 100</b>', '<b>BB 200</b>',
                   '<b>Melon</b>', '<b>X Engagement</b>', '<b>YouTube Views</b>'],
            fill_color='#1f77b4',  # Blue header
            font=dict(color='white', size=12),
            align='left',
            height=40
        ),
        cells=dict(
            values=[
                top_10['Rank'],
                top_10['celebrity'],
                top_10['category'],
                top_10['signal_score'].apply(lambda x: f"{x:.1f}"),
                top_10.apply(format_best_chart, axis=1),
                top_10.get('spotify_position', pd.Series([None]*len(top_10))).apply(format_chart_position),
                top_10.get('billboard_hot100', pd.Series([None]*len(top_10))).apply(format_chart_position),
                top_10.get('billboard_200', pd.Series([None]*len(top_10))).apply(format_chart_position),
                top_10.get('melon_position', pd.Series([None]*len(top_10))).apply(format_chart_position),
                top_10['x_engagement_rate'].apply(lambda x: f"{x:.2%}"),  # Format as percentage
                top_10['youtube_views'].apply(lambda x: f"{x:,}")  # Format with commas
            ],
            fill_color=[['#f0f2f6', 'white'] * 11],  # Alternating row colors
            font=dict(size=11),
            align='left',
            height=35
        )
    )])

    fig.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # ========================================
    # KEY METRICS
    # ========================================

    st.subheader("📈 This Week's Highlights")

    # Create 4 columns for side-by-side metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        top_artist = top_10.iloc[0]  # First row (highest ranked)
        st.metric(
            "👑 Current Leader",
            top_artist['celebrity'],
            f"Score: {top_artist['signal_score']:.1f}"
        )

    with col2:
        # Find best chart position
        if 'chart_position' in top_10.columns:
            chart_artists = top_10[top_10['chart_position'].notna()]
            if not chart_artists.empty:
                best_chart = chart_artists.loc[chart_artists['chart_position'].idxmin()]
                st.metric(
                    "📊 Top Chart Position",
                    best_chart['celebrity'],
                    f"#{int(best_chart['chart_position'])}"
                )

    with col3:
        if top_10['x_engagement_rate'].max() > 0:
            most_engaged = top_10.loc[top_10['x_engagement_rate'].idxmax()]
            st.metric(
                "🔥 Highest X Engagement",
                most_engaged['celebrity'],
                f"{most_engaged['x_engagement_rate']:.2%}"
            )

    with col4:
        if top_10['youtube_views'].max() > 0:
            most_views = top_10.loc[top_10['youtube_views'].idxmax()]
            st.metric(
                "📺 Most YouTube Views",
                most_views['celebrity'],
                f"{most_views['youtube_views']:,}"
            )

    # ========================================
    # CHART 1: INDIVIDUAL CHART RANKINGS
    # ========================================

    st.subheader("📊 Individual Chart Rankings")

    chart_cols = [
        ('spotify_position', 'Spotify'),
        ('billboard_hot100', 'Billboard Hot 100'),
        ('billboard_200', 'Billboard 200'),
        ('melon_position', 'Melon')
    ]
    available_chart_cols = [col for col, _ in chart_cols if col in top_10.columns]
    chart_rankings = top_10[['celebrity'] + available_chart_cols].melt(
        id_vars='celebrity',
        var_name='chart',
        value_name='position'
    )
    chart_rankings = chart_rankings.dropna()

    if not chart_rankings.empty:
        chart_label_map = dict(chart_cols)
        chart_rankings['chart'] = chart_rankings['chart'].map(chart_label_map)

        fig_chart = px.bar(
            chart_rankings,
            x='celebrity',
            y='position',
            color='chart',
            barmode='group',
            labels={'celebrity': '', 'position': 'Chart Position (lower is better)', 'chart': 'Chart'}
        )
        fig_chart.update_layout(height=420)
        fig_chart.update_yaxes(autorange='reversed')
        st.plotly_chart(fig_chart, use_container_width=True)
    else:
        st.info("No chart rankings available yet. Run `python update_charts.py`.")

    # ========================================
    # CHART 2: KEY METRIC CATEGORIES
    # ========================================

    st.subheader("🧭 Key Metric Categories")

    metric_components = top_10[['celebrity', 'x_component', 'yt_component']].copy()
    if 'chart_component' in top_10.columns:
        metric_components['chart_component'] = top_10['chart_component']

    metric_long = metric_components.melt(
        id_vars='celebrity',
        var_name='metric',
        value_name='score'
    )
    metric_labels = {
        'x_component': 'X Engagement',
        'yt_component': 'YouTube Views',
        'chart_component': 'Chart Performance'
    }
    metric_long['metric'] = metric_long['metric'].map(metric_labels)

    fig_metrics = px.bar(
        metric_long,
        x='celebrity',
        y='score',
        color='metric',
        barmode='group',
        labels={'celebrity': '', 'score': 'Component Score', 'metric': 'Metric'}
    )
    fig_metrics.update_layout(height=420)
    st.plotly_chart(fig_metrics, use_container_width=True)

    # ========================================
    # CHART 3: FULL SIGNAL INDEX SCORE
    # ========================================

    st.subheader("🏁 Full Signal Index Score")

    fig_score = px.bar(
        top_10,
        x='celebrity',
        y='signal_score',
        color='signal_score',
        color_continuous_scale='Blues',
        labels={'celebrity': '', 'signal_score': 'Signal Index Score'}
    )
    fig_score.update_layout(height=420, showlegend=False)
    st.plotly_chart(fig_score, use_container_width=True)

# ========================================
# PAGE 2: SPENDING SIGNALS
# ========================================

elif page == "💰 Spending Signals":

    if rankings.empty:
        st.warning("⚠️ No data available. Run: `python update_data.py`")
        st.stop()

    st.header("SPENDING POWER SIGNALS")

    # Check if we have product mention data
    if not x_data.empty and 'has_product_mention' in x_data.columns:

        # Group by artist and count product mentions
        product_mentions = x_data.groupby('celebrity')['has_product_mention'].sum().sort_values(ascending=False)

        st.subheader("🛍️ Product Mentions This Week")

        # Bar chart of product mentions
        fig = px.bar(
            x=product_mentions.index[:10],
            y=product_mentions.values[:10],
            labels={'x': '', 'y': 'Product Mentions'},
            color=product_mentions.values[:10],
            color_continuous_scale='Viridis'  # Color gradient
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # ========================================
        # RECENT PRODUCT POSTS
        # ========================================

        st.subheader("💬 Recent Product-Related Posts")

        # Filter for tweets with product mentions, sort by engagement
        product_posts = x_data[x_data['has_product_mention'] == True].sort_values('engagement', ascending=False).head(5)

        # Display each post in an expandable box
        for _, post in product_posts.iterrows():
            with st.expander(f"**{post['celebrity']}** - {post['engagement']:,} engagements"):
                st.write(post['text_preview'])
                st.caption(f"❤️ {post['likes']:,} | 🔄 {post['retweets']:,} | 💬 {post['replies']:,}")

    else:
        st.info("No spending signal data available yet. Run data collection first!")

# ========================================
# PAGE 3: POST GENERATOR
# ========================================

elif page == "✍️ Post Generator":

    if rankings.empty:
        st.warning("⚠️ No data available. Run: `python update_data.py`")
        st.stop()

    st.header("X POST GENERATOR")

    # Dropdown to select post type
    post_type = st.selectbox("Select Post Type", [
        "🏆 Top Influencers Ranking",
        "📊 Category Leaders",
        "🔥 Engagement Champion"
    ])

    # Generate different post formats based on selection
    if post_type == "🏆 Top Influencers Ranking":
        top_5 = rankings.head(5)

        post = "🔥 TOP INFLUENCING ARTISTS THIS WEEK\n\n"
        for idx, row in top_5.iterrows():
            post += f"{idx+1}. {row['celebrity']} (Signal Score: {row['signal_score']:.0f})\n"
        post += "\nBased on X engagement + YouTube momentum\n\n#SignalIndex #FandomPower"

    elif post_type == "📊 Category Leaders":
        post = "👑 CATEGORY LEADERS THIS WEEK\n\n"

        # Get top artist in each category
        for category in rankings['category'].unique():
            top_in_cat = rankings[rankings['category'] == category].iloc[0]
            post += f"🏆 {category}: {top_in_cat['celebrity']} ({top_in_cat['signal_score']:.0f})\n"

        post += "\n#SignalIndex"

    else:  # Engagement Champion
        top = rankings.iloc[0]
        post = f"🔥 ENGAGEMENT CHAMPION\n\n"
        post += f"{top['celebrity'].upper()}\n\n"
        post += f"📊 Signal Score: {top['signal_score']:.0f}\n"
        post += f"💬 X Engagement Rate: {top['x_engagement_rate']:.2%}\n"
        post += f"📺 YouTube Views: {top['youtube_views']:,}\n\n"
        post += f"Leading the {top['category']} influence game 👑\n\n#SignalIndex"

    # Display generated post
    st.text_area("Generated Post (Copy & Paste)", post, height=250)

    # Fun button with celebration
    if st.button("📋 Copy to Clipboard"):
        st.success("✅ Post ready to tweet!")
        st.balloons()  # Streamlit's celebratory animation

# ========================================
# PAGE 4: MANAGE ARTISTS
# ========================================

elif page == "⚙️ Manage Artists":

    st.header("ARTIST MANAGEMENT")

    # Load current artists from JSON file
    with open('artists.json', 'r') as f:
        artists_data = json.load(f)

    # ========================================
    # CURRENT ARTISTS TABLE
    # ========================================

    st.subheader("📋 Current Artists")

    # Display each artist in a row with buttons
    for idx, artist in enumerate(artists_data['artists']):

        # Create 5 columns for layout
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 1, 1])

        with col1:
            # Show status emoji
            status = "✅" if artist.get('active', True) else "❌"
            st.write(f"{status} **{artist['name']}**")

        with col2:
            st.write(f"📁 {artist.get('category', 'Other')}")

        with col3:
            st.write(f"🐦 @{artist['twitter']}")

        with col4:
            # Toggle button (Disable/Enable)
            if artist.get('active', True):
                if st.button("Disable", key=f"disable_{idx}"):
                    toggle_artist(artist['name'], False)
                    st.rerun()  # Refresh the page
            else:
                if st.button("Enable", key=f"enable_{idx}"):
                    toggle_artist(artist['name'], True)
                    st.rerun()

        with col5:
            # Show if they have YouTube
            has_yt = "📺" if artist.get('youtube_channel_id') else "❌"
            st.write(has_yt)

    # ========================================
    # ADD NEW ARTIST FORM
    # ========================================

    st.subheader("➕ Add New Artist")

    # st.form groups inputs together
    # All inputs submit when button is clicked (prevents page refresh on each keystroke)
    with st.form("add_artist_form"):

        col1, col2 = st.columns(2)

        with col1:
            new_name = st.text_input("Artist Name*", placeholder="e.g. IU")
            new_twitter = st.text_input("Twitter Username*", placeholder="e.g. _IUofficial")

        with col2:
            new_category = st.selectbox("Category*", ["K-pop", "Western", "Other"])
            new_youtube = st.text_input("YouTube Channel ID (optional)", placeholder="e.g. UC3SyT...")

        # Form submit button
        submitted = st.form_submit_button("Add Artist")

        if submitted:
            # Validation
            if not new_name or not new_twitter:
                st.error("❌ Name and Twitter username are required!")
            else:
                # Call our config.py function
                success, message = add_artist(
                    new_name,
                    new_category,
                    new_twitter,
                    new_youtube if new_youtube else None
                )

                if success:
                    st.success(f"✅ {message}")
                    st.rerun()  # Refresh to show new artist
                else:
                    st.error(f"❌ {message}")

    # ========================================
    # HELP SECTION
    # ========================================

    # st.expander creates a collapsible section
    with st.expander("ℹ️ How to find YouTube Channel IDs"):
        st.markdown("""
        **Method 1: From Channel URL**
        1. Go to the artist's YouTube channel
        2. Look at the URL: `youtube.com/channel/[CHANNEL_ID]`
        3. Copy the ID after `/channel/`

        **Method 2: From About Page**
        1. Go to channel → About tab
        2. Click "Share Channel" → "Copy Channel ID"

        **Example:**
        - Channel URL: `youtube.com/channel/UCdZlB77W6p-qx08FaZG_0kw`
        - Channel ID: `UCdZlB77W6p-qx08FaZG_0kw`
        """)

    # Quick stats
    st.divider()  # Horizontal line
    active_count = len([a for a in artists_data['artists'] if a.get('active', True)])
    total_count = len(artists_data['artists'])
    st.metric("Active Artists", f"{active_count} / {total_count}")

# ========================================
# SIDEBAR FOOTER & QUICK ACTIONS
# ========================================

st.sidebar.markdown("---")
st.sidebar.markdown("**Signal Index MVP**")
st.sidebar.caption("Data sources: X API + YouTube API")

# Quick actions
st.sidebar.markdown("### 🚀 Quick Actions")

# Button to clear cache and reload data
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()  # Clear cached data
    st.rerun()  # Reload the page


# ========================================
# EDUCATIONAL NOTE: Streamlit Execution Model
# ========================================
#
# HOW STREAMLIT WORKS:
# 1. Every interaction (button click, dropdown change) re-runs the ENTIRE script
# 2. That's why we use @st.cache_data - to avoid re-loading files every time
# 3. st.rerun() explicitly refreshes the page (useful after database changes)
#
# WHY THIS MATTERS:
# - Don't do expensive operations (API calls, file writes) outside functions
# - Use st.session_state to persist data between runs (advanced topic)
# - Be mindful of what code runs on every interaction
#
# DEBUGGING TIP:
# Add print() statements - they show in your terminal (where you ran streamlit)
#
# ========================================
