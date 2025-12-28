"""
NUBEAUX Collective Instagram Automation - Configuration
"""
import os
from pathlib import Path

# =============================================================================
# API KEYS (Set these as environment variables or replace with your keys)
# =============================================================================

# Apify API key - Get from https://apify.com/account/integrations
APIFY_API_KEY = os.getenv("APIFY_API_KEY", "your-apify-api-key-here")

# Claude API key - Get from https://console.anthropic.com/
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your-anthropic-api-key-here")

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = BASE_DIR / "templates"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
TEMPLATES_DIR.mkdir(exist_ok=True)

# =============================================================================
# INSTAGRAM TARGETS
# =============================================================================

# Competitor accounts to analyze
COMPETITOR_ACCOUNTS = [
    "blacktraveljourney",
    "tabortravel",
    "africanluxurymag",
    "travelnoire",
    "blacktravelfeed",
]

# Hashtags to monitor
TARGET_HASHTAGS = [
    "luxuryafricantravel",
    "blacktravel",
    "heritagetourism",
    "safariluxury",
    "africandiaspora",
    "blackluxurytravel",
    "africansafari",
]

# =============================================================================
# BRAND SETTINGS
# =============================================================================

BRAND = {
    "name": "NUBEAUX Collective",
    "handle": "@nubeauxcollective",
    "tagline": "Africa's finest properties. Africa's finest creators.",
    "voice": "Sophisticated, editorial, authoritative yet accessible. Data-driven with emotional resonance.",
    "colors": {
        "charcoal": "#1a1a1a",
        "bone": "#faf8f5",
        "ecru": "#f5f1eb",
        "terracotta": "#c2703e",
        "gold": "#b8953f",
        "warm_grey": "#8a8278",
    },
    "fonts": {
        "headline": "Playfair Display",
        "body": "Inter",
    },
}

# =============================================================================
# CONTENT STRATEGY
# =============================================================================

CONTENT_PILLARS = {
    "market_intelligence": {
        "weight": 0.40,
        "description": "Stats, insights about representation gap, diaspora travel market",
        "examples": [
            "The $4.2 trillion diaspora opportunity",
            "Heritage travel growth statistics",
            "Why representation drives bookings",
        ],
    },
    "creator_campaign": {
        "weight": 0.35,
        "description": "Behind-the-scenes, creator spotlights, campaign previews",
        "examples": [
            "Meet our creators",
            "Campaign behind-the-scenes",
            "Creator success stories",
        ],
    },
    "aspirational_travel": {
        "weight": 0.25,
        "description": "Luxury property features, destination inspiration",
        "examples": [
            "Property spotlights",
            "Destination guides",
            "Luxury experience showcases",
        ],
    },
}

# Posting schedule (day of week -> content pillar)
POSTING_SCHEDULE = {
    "Monday": "market_intelligence",
    "Wednesday": "creator_campaign",
    "Friday": "aspirational_travel",
    "Sunday": "carousel",  # Educational or listicle
}

# =============================================================================
# HASHTAG SETS
# =============================================================================

HASHTAG_SETS = {
    "core": [
        "#nubeauxcollective",
        "#africanexcellence",
        "#luxuryafricantravel",
    ],
    "market": [
        "#representationmatters",
        "#diasporatravel",
        "#blackluxurytravel",
        "#diversityintravel",
    ],
    "creator": [
        "#creatorsofcolour",
        "#travelcreators",
        "#influencermarketing",
        "#contentcreator",
    ],
    "travel": [
        "#safarilodge",
        "#africanluxury",
        "#boutiquehotels",
        "#luxurytravel",
    ],
    "location": [
        "#southafrica",
        "#namibia",
        "#zanzibar",
        "#botswana",
        "#kenya",
    ],
}

# =============================================================================
# APIFY SETTINGS
# =============================================================================

APIFY_SETTINGS = {
    # Instagram Profile Scraper actor
    "profile_scraper_id": "apify/instagram-profile-scraper",
    # Instagram Hashtag Scraper actor
    "hashtag_scraper_id": "apify/instagram-hashtag-scraper",
    # Results per run
    "results_limit": 50,
}

# =============================================================================
# CONTENT GENERATION SETTINGS
# =============================================================================

GENERATION_SETTINGS = {
    "posts_per_week": 4,
    "caption_max_length": 2200,
    "caption_ideal_length": 150,  # For engagement
    "hashtags_per_post": 15,
    "model": "claude-sonnet-4-20250514",
}
