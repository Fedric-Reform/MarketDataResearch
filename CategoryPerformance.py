import requests
import pandas as pd
import matplotlib.pyplot as plt

# Fetch category performance from CoinGecko API
url = "https://api.coingecko.com/api/v3/coins/categories"
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(url, headers=headers)
data = response.json()

# Inspect keys to avoid KeyError
if data:
    print("✅ Keys available:", data[0].keys())

# Convert to DataFrame
df = pd.DataFrame(data)

# Check for correct key names
required_columns = ["name", "market_cap", "volume_24h", "market_cap_change_24h"]
for col in required_columns:
    if col not in df.columns:
        raise KeyError(f"❌ Column '{col}' not found in API response")

# Select and rename columns
df = df[required_columns]
df.columns = ["Category", "Market Cap", "24h Volume", "24h % Change"]

# Clean up and sort
df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors='coerce').round(0)
df["24h Volume"] = pd.to_numeric(df["24h Volume"], errors='coerce').round(0)
df["24h % Change"] = pd.to_numeric(df["24h % Change"], errors='coerce').round(2)
df = df.sort_values("Market Cap", ascending=False).head(10)

# Save to CSV
df.to_csv("CategoryPerformance.csv", index=False)
print("✅ Saved to CategoryPerformance.csv")
