import requests
import pandas as pd
import time
import os
from concurrent.futures import ThreadPoolExecutor

DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_IDS = os.getenv("DUNE_QUERY_IDS","").split(",")  # comma-separated in .env or GitHub Actions

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
        return

    # Wait for completion
    while True:
        status_url = f"https://api.dune.com/api/v1/execution/{execution_id}/status"
        status_resp = requests.get(status_url, headers=headers).json()
        state = status_resp.get("state")
        if state == "QUERY_STATE_COMPLETED":
            break
        elif state == "QUERY_STATE_FAILED":
            print(f"❌ Query {query_id} failed.")
            return
        time.sleep(5)

    # Fetch results
    results_url = f"https://api.dune.com/api/v1/execution/{execution_id}/results"
    try:
        results = requests.get(results_url, headers=headers).json()
        rows = results["result"]["rows"]
        df = pd.DataFrame(rows)
        filename = f"BTCETH_ETF.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Saved query {query_id} to {filename}")
    except Exception as e:
        print(f"❌ Failed to fetch results for query {query_id}: {e}")

if __name__ == "__main__":
    if not DUNE_API_KEY or len(QUERY_IDS) != 2:
        print("❌ Please set DUNE_API_KEY and DUNE_QUERY_IDS with two query IDs (comma-separated).")
        exit(1)

    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.map(run_dune_query, QUERY_IDS)
