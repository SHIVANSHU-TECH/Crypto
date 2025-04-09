import time

def fetch_crypto_data(retries=3, delay=10):
    """Fetch cryptocurrency data with rate limiting."""
    for attempt in range(retries):
        try:
            response = requests.get(COINGECKO_API_URL, params=API_PARAMS)
            if response.status_code == 429:  # Too Many Requests
                print("Rate limit exceeded. Retrying in", delay, "seconds...")
                time.sleep(delay)  # Wait before retrying
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data (Attempt {attempt+1}): {e}")
            time.sleep(delay)  # Wait before retrying
    return None  # Return None if all retries fail
