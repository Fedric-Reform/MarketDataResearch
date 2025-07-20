# DEX VOLUME #

import requests
import pandas as pd

# Fetch data
url = "https://api.llama.fi/overview/dexs?excludeTotalDataChart=true&excludeTotalDataChartBreakdown=true"
response = requests.get(url)
response.raise_for_status()
data = response.json()

# Extract protocols and create DataFrame
dex_data = data["protocols"]
df = pd.DataFrame(dex_data)

# Select and clean relevant columns
df = df[["name", "chains", "category", "total24h", "total7d", "total30d", "change_1d", "change_7d", "change_1m"]]
df["total24h"] = df["total24h"].round(0)
df["total7d"] = df["total7d"].round(0)
df["total30d"] = df["total30d"].round(0)
df[["change_1d", "change_7d", "change_1m"]] = df[["change_1d", "change_7d", "change_1m"]].round(2)

# Sort by 24h volume
top_dexes = df.sort_values("total24h", ascending=False)

# Display
print(top_dexes)

# Save to CSV
top_dexes.to_csv("DEX_Volume.csv", index=False)
