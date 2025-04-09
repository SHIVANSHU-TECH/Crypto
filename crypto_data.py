import requests

# Fetch top 100 coins data
url = "https://api.coingecko.com/api/v3/coins/markets"
params = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 100,
    "page": 1,
    "sparkline": "false",
    "price_change_percentage": "24h"
}

response = requests.get(url, params=params)
data = response.json()

# Sort coins by 24h percentage change
sorted_data = sorted(data, key=lambda x: x["price_change_percentage_24h"], reverse=True)

# Get top 5 gainers and losers
top_gainers = sorted_data[:5]
top_losers = sorted_data[-5:]

print("\n🔼 Top 5 Gainers (24h) 🔼")
for coin in top_gainers:
    print(f"{coin['name']} ({coin['symbol'].upper()}): +{coin['price_change_percentage_24h']:.2f}%")

print("\n🔽 Top 5 Losers (24h) 🔽")
for coin in top_losers:
    print(f"{coin['name']} ({coin['symbol'].upper()}): {coin['price_change_percentage_24h']:.2f}%")
