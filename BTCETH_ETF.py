import requests
import pandas as pd
import time
import os

DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_IDS_RAW = os.getenv("DUNE_QUERY_IDS")  # Example: "3430945,4208557"
QUERY_IDS = QUERY_IDS_RAW.split(",") if QUERY_IDS_RAW else []

headers = {
    "x-dune-api-key": DUNE_API_KEY,
    "Content-Type": "application/json"
}

def run_dune_query(query_id):
    # Trigger execution
    exec_url = f"https://api.dune.com/api/v1/query/{query_id}/execute"
    try:
        resp = requests.post(exec_url, headers=headers)
        resp.raise_for_status()
        execution_id = resp.json()["execution_id"]
    except Exception as e:
        print(f"❌ Failed to trigger query {query_id}: {e}")
        return None

    # Wait until query finishes
    while True:
        status_url = f"https://api.dune.com/api/v1/execution/{execution_id}/status"
        status_resp = requests.get(status_url, headers=headers).json()
        state = status_resp.get("state")
        if state == "QUERY_STATE_COMPLETED":
            break
        elif state == "QUERY_STATE_FAILED":
            print(f"❌ Query {query_id} failed.")
            return None
        time.sleep(5)

    # Fetch results
    results_url = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
    try:
        results = requests.get(results_url, headers=headers).json()
        rows = results["result"]["rows"]
        df = pd.DataFrame(rows)
        df["QueryID"] = query_id  # Add label
        return df
    except Exception as e:
        print(f"❌ Failed to fetch results for query {query_id}: {e}")
        return None

if __name__ == "__main__":
    if not DUNE_API_KEY or not QUERY_IDS:
        print("❌ Please set DUNE_API_KEY and DUNE_QUERY_IDS with at least one query ID.")
        exit(1)

    combined_df = pd.DataFrame()

    for query_id in QUERY_IDS:
        df = run_dune_query(query_id.strip())
        if df is not None:
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    if not combined_df.empty:
        combined_df.to_csv("BTCETH_ETF_Combined.csv", index=False)
        print("✅ Combined results saved to BTCETH_ETF_Combined.csv")
    else:
        print("❌ No data to save.")
