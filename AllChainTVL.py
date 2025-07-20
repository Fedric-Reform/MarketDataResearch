# ALL TVL
import requests
import pandas as pd
import time
from datetime import datetime

# Base URLs
CHAINS_URL = "https://api.llama.fi/v2/chains"
CHAIN_TVL_URL = "https://api.llama.fi/v2/historicalChainTvl/{}"

# Rate limit: 40 requests/minute = 1 request per 1.5 seconds
RATE_LIMIT_SECONDS = 0.8

def fetch_all_chain_tvl():
    try:
        chains_resp = requests.get(CHAINS_URL)
        chains_resp.raise_for_status()
        chains = chains_resp.json()
    except Exception as e:
        print(f"❌ Error fetching chain list: {e}")
        return

    print(f"🔍 Found {len(chains)} chains. Fetching TVL data with 40 req/min limit...")

    all_data = []

    for i, chain in enumerate(chains):
        name = chain.get("name")

        try:
            url = CHAIN_TVL_URL.format(name)
            r = requests.get(url)
            r.raise_for_status()
            tvl_data = r.json()

            for entry in tvl_data:
                all_data.append({
                    "Chain": name,
                    "Date": datetime.utcfromtimestamp(entry["date"]).strftime("%Y-%m-%d"),
                    "TVL (USD)": entry["tvl"]
                })

            print(f"[{i+1}/{len(chains)}] ✅ {name} fetched successfully.")

        except Exception as e:
            print(f"[{i+1}/{len(chains)}] ⚠️ Error fetching {name}: {e}")

        time.sleep(RATE_LIMIT_SECONDS)

    # Save to CSV
    df = pd.DataFrame(all_data)
    df.to_csv("Chain_TVL.csv", index=False)
    print("📁 Data saved to historical_chain_tvl.csv")

if __name__ == "__main__":
    fetch_all_chain_tvl()
