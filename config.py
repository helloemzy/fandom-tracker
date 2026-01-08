"""
Configuration file for Signal Index
Handles API keys and artist management
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
# This is like opening your password manager - keeps secrets secure
load_dotenv()

# API Keys (loaded from .env file)
X_BEARER_TOKEN = os.getenv('X_BEARER_TOKEN')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# ========================================
# ARTIST MANAGEMENT FUNCTIONS
# ========================================

def load_artists():
    """
    Load artist configuration from artists.json

    Think of this as: Opening your contact list and filtering for "favorites only"
    Returns: List of active artists (those with "active": true)
    """
    try:
        with open('artists.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Only return active artists (filter out disabled ones)
            return [artist for artist in data['artists'] if artist.get('active', True)]
    except FileNotFoundError:
        # If file doesn't exist, create a default one
        print("⚠️  artists.json not found. Creating default file...")
        create_default_artists_file()
        return load_artists()  # Try again
    except Exception as e:
        print(f"❌ Error loading artists.json: {e}")
        return []


def create_default_artists_file():
    """
    Create default artists.json if it doesn't exist

    This is your starter pack - one artist to get you going
    """
    default_artists = {
        "artists": [
            {
                "name": "NewJeans",
                "category": "K-pop",
                "twitter": "newjeans_official",
                "youtube_channel_id": "UCdZlB77W6p-qx08FaZG_0kw",
                "active": True
            }
        ]
    }
    with open('artists.json', 'w', encoding='utf-8') as f:
        json.dump(default_artists, f, indent=2, ensure_ascii=False)
    print("✅ Created default artists.json with NewJeans")


def save_artists(artists_list):
    """
    Save updated artists list to JSON

    Like hitting "Save" on a Word document
    """
    data = {"artists": artists_list}
    with open('artists.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_artist(name, category, twitter, youtube_channel_id=None):
    """
    Add a new artist to tracking

    Parameters:
        name: Artist's display name (e.g., "Taylor Swift")
        category: "K-pop", "Western", or "Other"
        twitter: Twitter username WITHOUT @ (e.g., "taylorswift13")
        youtube_channel_id: Optional YouTube channel ID

    Returns: (success: bool, message: str)
    """
    # Load all artists (including inactive) to preserve them
    try:
        with open('artists.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"artists": []}

    # Check if artist already exists (prevent duplicates)
    if any(a['name'] == name for a in data['artists']):
        return False, f"Artist '{name}' already exists"

    # Create new artist entry
    new_artist = {
        "name": name,
        "category": category,
        "twitter": twitter,
        "youtube_channel_id": youtube_channel_id,
        "active": True
    }

    # Add to list and save
    data['artists'].append(new_artist)

    with open('artists.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return True, f"✅ Added {name} successfully"


def toggle_artist(name, active_status):
    """
    Enable or disable artist tracking

    Like muting/unmuting a contact - they're still there, just not active

    Parameters:
        name: Artist name to toggle
        active_status: True to enable, False to disable
    """
    with open('artists.json', 'r') as f:
        data = json.load(f)

    # Find the artist and update their status
    for artist in data['artists']:
        if artist['name'] == name:
            artist['active'] = active_status
            break

    # Save changes
    with open('artists.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return True


# ========================================
# PRODUCT MENTION KEYWORDS
# ========================================

# These words indicate an artist is promoting something
# Think of this as "shopping trigger words"
PRODUCT_KEYWORDS = [
    'merch', 'album', 'vinyl', 'buy', 'sold out', 'pre-order',
    'drop', 'collection', 'tour', 'tickets', 'concert', 'shop',
    'limited edition', 'exclusive', 'purchase', 'store'
]

# You can add more keywords here as you discover patterns!
# For example: 'collaboration', 'launch', 'available now', etc.
