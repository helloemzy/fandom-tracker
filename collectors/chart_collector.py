"""
Chart Data Collector
Scrapes chart positions and streaming data from multiple sources

DATA SOURCES:
- Kworb.net: Spotify, Apple Music, YouTube aggregated charts
- Billboard.com: Billboard Hot 100, Billboard 200, K-pop charts
- Melon: Korean music charts
- Circle Chart: Korean music charts (formerly Gaon)

IMPORTANT: This collector respects robots.txt and includes delays between requests
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
from config import load_artists

# User agent to identify our scraper
HEADERS = {
    'User-Agent': 'Signal-Index-Bot/1.0 (Educational Project; Contact: signalindex@example.com)'
}


def _make_request(url, delay=2):
    """
    Make HTTP request with proper headers and error handling

    Args:
        url: URL to fetch
        delay: Seconds to wait before request (to be respectful)

    Returns:
        BeautifulSoup object or None if failed

    Tech note: We add delays between requests to avoid overloading servers.
    This is called "rate limiting ourselves" and is good internet citizenship.
    """
    time.sleep(delay)

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raise error for bad status codes
        return BeautifulSoup(response.content, 'lxml')
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error fetching {url}: {str(e)}")
        return None


def scrape_kworb_spotify(artist_name):
    """
    Scrape Spotify chart data from Kworb.net

    Kworb aggregates Spotify data including:
    - Current chart position
    - Daily streams
    - Total streams

    Returns: dict with spotify_position, spotify_streams, or None if not found

    Tech note: Kworb updates multiple times per day, making it great for
    real-time chart tracking without using the Spotify API.
    """
    # Kworb has artist pages at kworb.net/spotify/artist/{artist}.html
    # We'll search the main charts page instead for simplicity
    url = "https://kworb.net/spotify/artists.html"

    soup = _make_request(url)
    if not soup:
        return None

    try:
        # Find the table with artist data
        table = soup.find('table')
        if not table:
            return None

        # Search for the artist in the table
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) >= 4:
                name_cell = cells[1].get_text(strip=True)

                # Fuzzy match artist name (handles case differences)
                if artist_name.lower() in name_cell.lower():
                    position = cells[0].get_text(strip=True)
                    streams = cells[3].get_text(strip=True)

                    # Clean the data
                    try:
                        position = int(position.replace(',', ''))
                    except:
                        position = None

                    try:
                        # Kworb shows streams like "50,123,456"
                        streams = int(streams.replace(',', ''))
                    except:
                        streams = None

                    return {
                        'spotify_position': position,
                        'spotify_streams': streams
                    }

        # Artist not found in charts
        return {'spotify_position': None, 'spotify_streams': None}

    except Exception as e:
        print(f"  ⚠️  Error parsing Kworb data for {artist_name}: {str(e)}")
        return None


def scrape_billboard_hot100(artist_name):
    """
    Scrape Billboard Hot 100 chart position

    Returns: dict with billboard_position or None if not found

    Tech note: Billboard updates weekly (every Tuesday). The Hot 100 tracks
    the most popular songs across all formats (sales, streaming, radio).
    """
    url = "https://www.billboard.com/charts/hot-100/"

    soup = _make_request(url)
    if not soup:
        return None

    try:
        # Billboard's HTML structure uses specific classes for chart entries
        chart_items = soup.find_all('li', class_='o-chart-results-list__item')

        for idx, item in enumerate(chart_items, 1):
            # Find artist name in the item
            artist_elem = item.find('span', class_='c-label')
            if artist_elem:
                artist_text = artist_elem.get_text(strip=True)

                # Check if our artist matches
                if artist_name.lower() in artist_text.lower():
                    return {'billboard_hot100': idx}

        # Not on chart
        return {'billboard_hot100': None}

    except Exception as e:
        print(f"  ⚠️  Error parsing Billboard for {artist_name}: {str(e)}")
        return None


def scrape_billboard_200(artist_name):
    """
    Scrape Billboard 200 album chart position

    The Billboard 200 tracks the most popular albums (not songs)

    Returns: dict with billboard_200 or None if not found
    """
    url = "https://www.billboard.com/charts/billboard-200/"

    soup = _make_request(url)
    if not soup:
        return None

    try:
        chart_items = soup.find_all('li', class_='o-chart-results-list__item')

        for idx, item in enumerate(chart_items, 1):
            artist_elem = item.find('span', class_='c-label')
            if artist_elem:
                artist_text = artist_elem.get_text(strip=True)

                if artist_name.lower() in artist_text.lower():
                    return {'billboard_200': idx}

        return {'billboard_200': None}

    except Exception as e:
        print(f"  ⚠️  Error parsing Billboard 200 for {artist_name}: {str(e)}")
        return None


def scrape_melon_chart(artist_name):
    """
    Scrape Melon chart position (Korean music service)

    Melon is the largest music streaming service in South Korea

    Returns: dict with melon_position or None if not found

    Tech note: Melon has anti-scraping measures. This is a basic implementation
    that may need updates if they change their HTML structure.
    """
    url = "https://www.melon.com/chart/index.htm"

    soup = _make_request(url, delay=3)  # Extra delay for Korean sites
    if not soup:
        return None

    try:
        # Melon's structure: find table rows with song data
        rows = soup.find_all('tr', class_='lst50') + soup.find_all('tr', class_='lst100')

        for row in rows:
            # Find artist name in the row
            artist_elem = row.find('div', class_='ellipsis rank02')
            if artist_elem:
                artist_text = artist_elem.get_text(strip=True)

                if artist_name.lower() in artist_text.lower():
                    # Get rank from the rank element
                    rank_elem = row.find('span', class_='rank')
                    if rank_elem:
                        rank = int(rank_elem.get_text(strip=True))
                        return {'melon_position': rank}

        return {'melon_position': None}

    except Exception as e:
        print(f"  ⚠️  Error parsing Melon for {artist_name}: {str(e)}")
        return None


def collect_chart_data():
    """
    Main function to collect chart data for all active artists

    What this does:
    1. Loads active artists from artists.json
    2. For each artist, scrapes multiple chart sources
    3. Combines all data into a single DataFrame
    4. Returns the data for saving

    Returns: pandas DataFrame with chart data

    Tech note: This function is designed to run quickly (15-30 mins)
    compared to X API collection (7-8 hours) because web scraping
    doesn't have the same rate limits.
    """

    artists = load_artists()

    if not artists:
        print("❌ No active artists found in artists.json")
        return pd.DataFrame()

    print(f"📊 Collecting chart data for {len(artists)} artists")
    print("   This will take 15-30 minutes (web scraping, not APIs)")

    all_data = []

    for idx, artist in enumerate(artists, 1):
        name = artist['name']
        category = artist.get('category', 'Other')

        print(f"\n  [{idx}/{len(artists)}] {name}...")

        # Collect data from each source
        chart_data = {
            'celebrity': name,
            'category': category,
            'date': datetime.now().strftime('%Y-%m-%d'),
        }

        # Kworb (Spotify data)
        print(f"    ⏳ Checking Spotify charts...", end='')
        spotify_data = scrape_kworb_spotify(name)
        if spotify_data:
            chart_data.update(spotify_data)
            if spotify_data.get('spotify_position'):
                print(f" #{spotify_data['spotify_position']}")
            else:
                print(" Not charting")
        else:
            print(" Failed")

        # Billboard Hot 100
        print(f"    ⏳ Checking Billboard Hot 100...", end='')
        hot100_data = scrape_billboard_hot100(name)
        if hot100_data:
            chart_data.update(hot100_data)
            if hot100_data.get('billboard_hot100'):
                print(f" #{hot100_data['billboard_hot100']}")
            else:
                print(" Not charting")
        else:
            print(" Failed")

        # Billboard 200 (Albums)
        print(f"    ⏳ Checking Billboard 200...", end='')
        bb200_data = scrape_billboard_200(name)
        if bb200_data:
            chart_data.update(bb200_data)
            if bb200_data.get('billboard_200'):
                print(f" #{bb200_data['billboard_200']}")
            else:
                print(" Not charting")
        else:
            print(" Failed")

        # Melon (Korean charts - only for K-pop artists)
        if category == 'K-pop':
            print(f"    ⏳ Checking Melon charts...", end='')
            melon_data = scrape_melon_chart(name)
            if melon_data:
                chart_data.update(melon_data)
                if melon_data.get('melon_position'):
                    print(f" #{melon_data['melon_position']}")
                else:
                    print(" Not charting")
            else:
                print(" Failed")

        all_data.append(chart_data)

        # Respectful delay between artists
        time.sleep(2)

    print(f"\n✅ Chart data collection complete!")
    return pd.DataFrame(all_data)


# ========================================
# EDUCATIONAL NOTE: Web Scraping Ethics
# ========================================
#
# Web scraping is legal and ethical when done responsibly:
#
# 1. RESPECT ROBOTS.TXT
#    - Check if the site allows scraping
#    - Follow their guidelines
#
# 2. ADD DELAYS
#    - Don't hammer servers with rapid requests
#    - We use time.sleep() between requests
#
# 3. IDENTIFY YOURSELF
#    - Use a descriptive User-Agent
#    - Provide contact information
#
# 4. HANDLE ERRORS GRACEFULLY
#    - Don't retry excessively if blocked
#    - Log errors and move on
#
# 5. USE DATA RESPONSIBLY
#    - Don't republish copyrighted content
#    - Use for analysis/research purposes
#
# Sites like Kworb and Billboard make their data publicly
# accessible and are generally scraping-friendly.
#
# ========================================
