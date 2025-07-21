import requests
import pandas as pd
import matplotlib.pyplot as plt

# ========== Config ==========
COINS = ["bitcoin", "ethereum"]
DAYS = 90
VS_CURRENCY = "usd"
INDICATOR_WINDOW = 14

# ========== Helper Functions ==========
def fetch_market_chart(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": VS_CURRENCY, "days": DAYS, "interval": "daily"}
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

def fetch_summary_data(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": VS_CURRENCY,
        "ids": coin_id,
        "price_change_percentage": "24h,7d,30d"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()[0]

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# ========== Main ==========
plt.style.use("dark_background")
fig, axs = plt.subplots(len(COINS), 2, figsize=(14, 6 * len(COINS)))
all_data = []  # 🧠 Fix: Define the list to hold all coin data

for i, coin in enumerate(COINS):
    # Fetch data
    df = fetch_market_chart(coin)
    info = fetch_summary_data(coin)

    # Indicators
    df["MA_50"] = df["price"].rolling(window=50).mean()
    df["MA_200"] = df["price"].rolling(window=30).mean()
    df["RSI_14"] = calculate_rsi(df["price"])
    df["coin"] = coin  # Label the coin

    # Store to list for CSV
    all_data.append(df.reset_index())

    # Plot price and MA
    axs[i, 0].plot(df.index, df["price"], label="Price", color="cyan")
    axs[i, 0].plot(df.index, df["MA_50"], label="MA 50", color="yellow", linestyle='--')
    axs[i, 0].plot(df.index, df["MA_200"], label="MA 200", color="orange", linestyle='--')
    axs[i, 0].set_title(f"{coin.upper()} Price Chart + MA", fontsize=13)
    axs[i, 0].legend()
    axs[i, 0].grid(True, alpha=0.3)

    # Plot RSI
    axs[i, 1].plot(df.index, df["RSI_14"], label="RSI (14)", color="lime")
    axs[i, 1].axhline(70, color='red', linestyle='--', alpha=0.7)
    axs[i, 1].axhline(30, color='blue', linestyle='--', alpha=0.7)
    axs[i, 1].set_title(f"{coin.upper()} RSI (14)", fontsize=13)
    axs[i, 1].legend()
    axs[i, 1].grid(True, alpha=0.3)

    # Print key stats
    print(f"\n🔹 {coin.upper()} Summary")
    print(f"Current Price: ${info['current_price']:,}")
    print(f"24h Change: {info['price_change_percentage_24h_in_currency']:.2f}%")
    print(f"7d Change: {info['price_change_percentage_7d_in_currency']:.2f}%")
    print(f"30d Change: {info['price_change_percentage_30d_in_currency']:.2f}%")
    print(f"24h Volume: ${info['total_volume']:,}")
    print(f"Market Cap: ${info['market_cap']:,}")

plt.tight_layout()
plt.show()

# ========== Save to CSV ==========
combined_df = pd.concat(all_data, ignore_index=True)
combined_df.to_csv("BTC_ETH_price_indicators.csv", index=False)
print("✅ Saved to BTC_ETH_price_indicators.csv")
