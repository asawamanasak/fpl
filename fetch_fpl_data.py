#!/usr/bin/env python3
"""
FPL Data Fetcher
Fetches official Fantasy Premier League data for a given team ID and saves JSON snapshots to the data directory.
"""

import os
import json
import urllib.request
import argparse

TEAM_ID_DEFAULT = 306983
BASE_URL = "https://fantasy.premierleague.com/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def fetch_json(url: str, save_path: str):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data

def sync_all(team_id: int = TEAM_ID_DEFAULT, data_dir: str = "data"):
    print(f"[+] Fetching FPL static & fixture database...")
    bootstrap = fetch_json(f"{BASE_URL}/bootstrap-static/", os.path.join(data_dir, "bootstrap_static.json"))
    fixtures = fetch_json(f"{BASE_URL}/fixtures/", os.path.join(data_dir, "fixtures.json"))

    print(f"[+] Fetching Solio Analytics AI projections...")
    try:
        solio = fetch_json("https://fpl.solioanalytics.com/api/data/latest.json", os.path.join(data_dir, "solio_latest.json"))
        print(f"[✔] Solio Analytics projections updated.")
    except Exception as e:
        print(f"[!] Warning: Could not fetch Solio projections: {e}")

    print(f"[+] Fetching Team ID {team_id} profile & history...")
    entry = fetch_json(f"{BASE_URL}/entry/{team_id}/", os.path.join(data_dir, "entry.json"))
    history = fetch_json(f"{BASE_URL}/entry/{team_id}/history/", os.path.join(data_dir, "history.json"))
    transfers = fetch_json(f"{BASE_URL}/entry/{team_id}/transfers/", os.path.join(data_dir, "transfers.json"))

    current_event = entry.get("current_event", 1)
    print(f"[+] Fetching picks for Gameweeks 1 to {current_event}...")
    for gw in range(1, current_event + 1):
        fetch_json(f"{BASE_URL}/entry/{team_id}/event/{gw}/picks/", os.path.join(data_dir, f"picks_gw{gw}.json"))

    print(f"[✔] Successfully synchronized all FPL & research data into '{data_dir}/' folder.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch FPL Data")
    parser.add_argument("--team-id", type=int, default=TEAM_ID_DEFAULT, help="Your FPL Team ID")
    parser.add_argument("--dir", type=str, default="data", help="Output directory")
    args = parser.parse_args()
    sync_all(args.team_id, args.dir)
