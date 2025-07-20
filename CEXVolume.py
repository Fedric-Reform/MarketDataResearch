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

# Convert BTC to USD (approx.)
BTC_PRICE = 30000  # Adjust based on real-time price if needed
volume_usd = [v * BTC_PRICE / 1e9 for v in volumes]  # USD billions

# Create DataFrame
df = pd.DataFrame({
    "Exchange": exchanges,
    "24h Volume (B USD)": volume_usd,
    "Trust Score": trust_scores,
    "Founded Year": coins,
    "Country": pairs
})

# Save to CSV
df.to_csv("coingecko_cex_volume.csv", index=False)
print("✅ Data saved to 'coingecko_cex_volume.csv'.")

# Plot top 15 by volume
df_sorted = df.sort_values(by="24h Volume (B USD)", ascending=False).head(15)

plt.figure(figsize=(14, 7))
plt.barh(df_sorted["Exchange"], df_sorted["24h Volume (B USD)"], color='cyan')
plt.xlabel("24h Volume (USD Billions)")
plt.title("Top 15 Centralized Exchanges by 24h Volume (CoinGecko)")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.grid(True, linestyle="--", alpha=0.3)
plt.show()
