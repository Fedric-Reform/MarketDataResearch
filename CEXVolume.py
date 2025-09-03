import requests
import pandas as pd
import matplotlib.pyplot as plt

# Set dark theme for charts
plt.style.use("dark_background")

# CoinGecko API endpoint
url = "https://api.coingecko.com/api/v3/exchanges"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"❌ Error fetching data from CoinGecko: {e}")
    exit()

# Extract and prepare data
exchanges = []
volumes = []
trust_scores = []
coins = []
pairs = []

for item in data:
    exchanges.append(item.get("name", "Unknown"))
    volumes.append(item.get("trade_volume_24h_btc", 0))  # BTC volume
    trust_scores.append(item.get("trust_score", 0))
    coins.append(item.get("year_established", 0))
    pairs.append(item.get("country", "Unknown"))


# Create DataFrame
df = pd.DataFrame({
    "Exchange": exchanges,
    "24h Volume (B USD)": volumes,
    "Trust Score": trust_scores,
    "Founded Year": coins,
    "Country": pairs
})

# Save to CSV
df.to_csv("CEX_Volume.csv", index=False)
print("✅ Data saved to 'CEX_Volume.csv'.")
