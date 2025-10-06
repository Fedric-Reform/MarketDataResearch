import requests
import pandas as pd
import time
from datetime import datetime

# =========================
# 1. Fetch market data (with rate-limit retry)
# =========================
def fetch_market_data(vs_currency="usd", per_page=50, page=1, retries=3):
    """
    Mengambil data pasar dari CoinGecko dengan penanganan batas laju (rate limit).
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": False,
        "price_change_percentage": "24h,7d" 
    }

    headers = {
        "Accept": "application/json",
        "User-Agent": "TopMoversBot/1.0"
    }

    for attempt in range(retries):
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            time.sleep(1.25) 
            return response.json()

        elif response.status_code == 429:
            wait_time = 10 * (attempt + 1)
            print(f"⚠️ Batas laju (429). Mencoba lagi dalam {wait_time}s...")
            time.sleep(wait_time)

        else:
            print(f"❌ Permintaan gagal dengan {response.status_code}: {response.text}")
            break

    raise Exception("❌ Gagal setelah percobaan ulang karena batas laju.")

# =========================
# 2. Process and label gainers & losers
# =========================
def get_movers_for_timeframe(df, timeframe, top_n=20):
    """
    Memproses DataFrame untuk mendapatkan top N gainers dan losers
    untuk kerangka waktu tertentu (misalnya, '24h' atau '7d').
    """
    change_col = f"{timeframe}_change_%"
    
    # Gainers sort
    gainers = df.sort_values(by=change_col, ascending=False).head(top_n).copy()
    gainers["type"] = f"gainer_{timeframe}"

    # Losers sort
    losers = df.sort_values(by=change_col, ascending=True).head(top_n).copy()
    losers["type"] = f"loser_{timeframe}"

    return gainers, losers

def process_data(data):
    """
    Mengubah data JSON menjadi DataFrame dan menyiapkan kolom.
    """
    df = pd.DataFrame(data)
    
    # Columns
    required_columns = [
        "id", 
        "symbol", 
        "name", 
        "current_price",
        "price change 24h",
        "price change 7d"
    ]
    
    # # Normalize Column Name
    # df = df.rename(columns={
    #     "price_change_percentage_24h_in_currency": "24h_change_%",
    #     "price_change_percentage_7d_in_currency": "7d_change_%"
    # })
    
    # Filter dan hanya pilih kolom yang relevan
    df = df.dropna(subset=["price change 24h", "price change 7d"])
    df = df[["id", "symbol", "name", "current_price", "price change 24h", "price change 7d"]]
    
    return df

# =========================
# 3. Save and Display Results
# =========================
def save_and_display_results(df_24h, df_7d, filename):
    """
    Menggabungkan 24h dan 7d movers, menyimpan ke CSV, dan mencetak ringkasan.
    """
    combined = pd.concat([df_24h, df_7d], ignore_index=True)
    combined.to_csv(filename, index=False)
    
    print(f"✅ Combined movers (24h & 7d) saved to {filename}")
    print("\n--- Ringkasan Performa ---")
    
    # Tampilkan 24h Top 3
    print("📈 Top 3 Gainers (24h):")
    print(df_24h[df_24h['type'] == 'gainer_24h'].head(3)[['name', '24h_change_%']].to_string(index=False))
    print("📉 Top 3 Losers (24h):")
    print(df_24h[df_24h['type'] == 'loser_24h'].head(3)[['name', '24h_change_%']].to_string(index=False))
    
    print("\n---")
    
    # Tampilkan 7d Top 3
    print("🚀 Top 3 Gainers (7d):")
    print(df_7d[df_7d['type'] == 'gainer_7d'].head(3)[['name', '7d_change_%']].to_string(index=False))
    print("🔻 Top 3 Losers (7d):")
    print(df_7d[df_7d['type'] == 'loser_7d'].head(3)[['name', '7d_change_%']].to_string(index=False))

# =========================
# 4. Main execution
# =========================
if __name__ == "__main__":
    try:
        print("📡 Mengambil data pasar CoinGecko (termasuk performa 24h & 7d)...")
        data = fetch_market_data(per_page=100) # Ambil 100 koin untuk hasil yang lebih bervariasi
        
        # 1. Memproses Data
        df_processed = process_data(data)
        print(f"📦 Mengambil {len(df_processed)} koin. Memproses pergerakan...")

        # 2. Mendapatkan Pergerakan 24 Jam
        gainers_24h, losers_24h = get_movers_for_timeframe(df_processed, '24h', top_n=10)
        df_24h = pd.concat([gainers_24h, losers_24h])
        
        # 3. Mendapatkan Pergerakan 7 Hari
        gainers_7d, losers_7d = get_movers_for_timeframe(df_processed, '7d', top_n=10)
        df_7d = pd.concat([gainers_7d, losers_7d])
        
        # 4. Menyimpan dan Menampilkan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"TopMovers_24h_7d_{timestamp}.csv"

        save_and_display_results(df_24h, df_7d, filename)

    except Exception as e:
        print(f"❌ Kesalahan Kritis: {str(e)}")
        print("💡 Coba perbaikan ini:")
        print("1. Periksa koneksi internet")
        print("2. Verifikasi status CoinGecko API: https://status.coingecko.com")
        print("3. Kurangi parameter 'per_page' jika batas laju dialami")
