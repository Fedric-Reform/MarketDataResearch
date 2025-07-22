import requests
import pandas as pd
import matplotlib.pyplot as plt

# CoinGecko API endpoint
url = "https://api.coingecko.com/api/v3/coins/categories"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"❌ Failed to fetch data: {e}")
    exit()

# Ensure data is a list
if not isinstance(data, list) or len(data) == 0:
    print("❌ Unexpected response format or no data returned.")
    exit()

# Print available keys to confirm structure (first object in list)
print("✅ Available keys:", list(data[0].keys()))

# Convert to DataFrame
df = pd.DataFrame(data)

# Check and extract required columns
required_columns = ["name", "market_cap", "volume_24h", "market_cap_change_24h"]
missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    print(f"❌ Missing columns in response: {missing_cols}")
    exit()

# Select and rename
df = df[required_columns]
df.columns = ["Category", "Market Cap", "24h Volume", "24h % Change"]

# Clean and format
df["Market Cap"] = pd.to_numeric(df["Market Cap"], errors='coerce').round(0)
df["24h Volume"] = pd.to_numeric(df["24h Volume"], errors='coerce').round(0)
df["24h % Change"] = pd.to_numeric(df["24h % Change"], errors='coerce').round(2)

# Sort by market cap and take top 10
df = df.sort_values("Market Cap", ascending=False).head(10)

# Save to CSV
df.to_csv("CategoryPerformance.csv", index=False)
print("✅ Saved to CategoryPerformance.csv")
