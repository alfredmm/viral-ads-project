import os

# GCP Configuration
PROJECT_ID = "test-alfred-mwangangi-qedxiq"
GCP_REGION = "us-central1"

# Secret Names
SECRET_NAMES = {
    "openai": "openai-api-key",
    "twitter_api_key": "twitterapi-io-api-key",
    "twitter_user_id": "twitterapi-io-user-id",
    "elevenlabs": "eleven-labs-api-key",
    "gcp_credentials": "gcp-credentials"
}

# API Endpoints
TWITTER_API_BASE = "https://twitterapi.io/api/v1"

# Virality Metrics
VIRAL_KEYWORDS = [
    "viral", "trending", "challenge", "hack", "secret", "shocking",
    "amazing", "unbelievable", "gone wrong", "prank", "life hack",
    "try not to laugh", "satisfying", "oddly satisfying", "fail",
    "win", "epic", "ultimate", "mind blowing", "game changing"
]

# Video Settings
MIN_DURATION = 8  # seconds
MAX_DURATION = 30  # seconds

# Create directories
os.makedirs("static/videos", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)
os.makedirs("static/thumbnails", exist_ok=True)