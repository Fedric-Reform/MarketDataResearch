import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fetch category performance from CoinGecko API
url = "https://api.coingecko.com/api/v3/coins/categories"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data)
df = df[["name", "market_cap", "volume_24h", "market_cap_change_24h"]]
df.columns = ["Category", "Market Cap", "24h Volume", "24h % Change"]

# Clean up and sort
df["Market Cap"] = df["Market Cap"].round(0)
df["24h Volume"] = df["24h Volume"].round(0)
df["24h % Change"] = df["24h % Change"].round(2)
df = df.sort_values("Market Cap", ascending=False).head(10)

#Save to CSV
df.to_csv("CategoryPerformance.csv", index=False)
print("✅ Saved to CategoryPerformance.csv")
