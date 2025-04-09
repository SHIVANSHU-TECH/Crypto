import tweepy
import os
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
api = tweepy.API(auth)

# Test: Get your Twitter account details
try:
    user = api.verify_credentials()
    print(f"Authenticated as: {user.screen_name}")
except Exception as e:
    print("Error:", e)
