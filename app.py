from flask import Flask, render_template, request
from flask_caching import Cache
import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure cache
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache for 5 minutes
cache = Cache(app)
cache.init_app(app)

# API URLs
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
COIN_DETAILS_URL = "https://api.coingecko.com/api/v3/coins/"
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Load API keys from environment variables
NEWS_API_KEY = "b05e52beee754ff19dc5c5521a64b495"

# API Parameters
API_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 20,  
    "page": 1,
    "sparkline": "false",
    "price_change_percentage": "24h"
}

# Store last updated timestamp
last_updated_time = None

@cache.cached(timeout=300, key_prefix='crypto_data')  # Cache for 5 minutes
def fetch_crypto_data():
    """Fetch top cryptocurrency market data from CoinGecko API with rate limiting."""
    global last_updated_time
    retries = 3
    delay = 10  # Wait 10 seconds before retrying if rate limit is exceeded

    for attempt in range(retries):
        try:
            response = requests.get(COINGECKO_API_URL, params=API_PARAMS)
            
            # Handle rate limiting
            if response.status_code == 429:
                print(f"Rate limit exceeded. Retrying in {delay} seconds...")
                time.sleep(delay)
                continue

            response.raise_for_status()
            data = response.json()

            # Extract BTC & ETH dominance
            btc_market_cap = next((coin["market_cap"] for coin in data if coin["symbol"] == "btc"), 0)
            eth_market_cap = next((coin["market_cap"] for coin in data if coin["symbol"] == "eth"), 0)
            total_market_cap = sum(coin["market_cap"] for coin in data if coin["market_cap"])

            btc_dominance = round((btc_market_cap / total_market_cap) * 100, 2) if total_market_cap else 0
            eth_dominance = round((eth_market_cap / total_market_cap) * 100, 2) if total_market_cap else 0

            # Fetch top 20 coins
            top_coins = data[:20]

            # Fetch categories for each coin
            for coin in top_coins:
                try:
                    coin_details = requests.get(f"{COIN_DETAILS_URL}{coin['id']}").json()
                    categories = coin_details.get("categories", [])
                    coin["category"] = categories[0] if categories else "N/A"  # Get first category or "N/A"
                except:
                    coin["category"] = "N/A"

            # Top 5 gainers & losers based on 24h change
            sorted_data = sorted(data, key=lambda x: x.get("price_change_percentage_24h", 0), reverse=True)
            top_gainers = sorted_data[:5]
            top_losers = sorted_data[-5:]

            # Update last refreshed time
            last_updated_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            return {
                "btc_dominance": btc_dominance,
                "eth_dominance": eth_dominance,
                "top_coins": top_coins,
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "last_updated": last_updated_time  # Include timestamp
            }

        except requests.exceptions.RequestException as e:
            print(f"Error fetching crypto data (Attempt {attempt+1}): {e}")
            time.sleep(delay)

    return {"btc_dominance": 0, "eth_dominance": 0, "top_coins": [], "top_gainers": [], "top_losers": [], "last_updated": "N/A"}

def fetch_coin_details(coin_id):
    """Fetch detailed information of a specific coin."""
    try:
        response = requests.get(f"{COIN_DETAILS_URL}{coin_id}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coin details: {e}")
        return None

def fetch_crypto_news(coin_name):
    """Fetch trending news related to a specific cryptocurrency."""
    try:
        params = {
            "q": coin_name,  
            "apiKey": NEWS_API_KEY,
            "language": "en",
            "sortBy": "publishedAt"
        }
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        news_data = response.json()
        return news_data.get("articles", [])[:5]  # Get top 5 news articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news for {coin_name}: {e}")
        return []

@app.route("/")
def home():
    """Render the homepage with cryptocurrency data."""
    category_filter = request.args.get("category", None)  # Allow category filtering
    crypto_data = fetch_crypto_data()

    return render_template("index.html",
                           btc_dominance=crypto_data["btc_dominance"],
                           eth_dominance=crypto_data["eth_dominance"],
                           top_coins=crypto_data["top_coins"],
                           gainers=crypto_data["top_gainers"],
                           losers=crypto_data["top_losers"],
                           category_filter=category_filter,
                           last_updated=crypto_data["last_updated"])  # Pass last updated time

@app.route("/coin/<coin_id>")
def coin_page(coin_id):
    """Render a detailed page for a specific cryptocurrency with news updates."""
    coin_data = fetch_coin_details(coin_id)

    if not coin_data:  
        return render_template("error.html", message="Coin data not found!"), 404
    
    news = fetch_crypto_news(coin_data["name"]) if coin_data else []  

    return render_template("coin.html", coin=coin_data, news=news)  

if __name__ == "__main__":
    app.run(debug=True)
