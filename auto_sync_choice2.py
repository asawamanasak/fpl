#!/usr/bin/env python3
"""
auto_sync_choice2.py
--------------------
Hybrid Autonomous Engine for Choice 2 (The Master Fortress Blueprint).
Runs every 15 minutes via GitHub Actions.

Workflow:
1. Re-fetches Official FPL API & Quantitative Intelligence Sources.
2. Identifies current active/next Gameweek and exact deadline.
3. Dynamically optimizes Choice 2 Starting 11, Captain (C), Vice Captain (VC), and Substitutes Bench (Sub 1, 2, 3).
4. Synchronizes Plan Summary Pros & Cons, valuations, and FDR ticker.
5. Re-compiles index.html and fpl_gw3_presentation.html.
"""

import json
import urllib.request
import ssl
import sys
import os
import subprocess
from datetime import datetime, timezone

def fetch_live_data():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {'User-Agent': 'Mozilla/5.0'}

    os.makedirs('data', exist_ok=True)

    # 1. bootstrap-static
    req = urllib.request.Request('https://fantasy.premierleague.com/api/bootstrap-static/', headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        bs = json.loads(resp.read().decode('utf-8'))
        with open('data/bootstrap_static.json', 'w', encoding='utf-8') as f:
            json.dump(bs, f, ensure_ascii=False)

    # 2. entry
    try:
        req = urllib.request.Request('https://fantasy.premierleague.com/api/entry/306983/', headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            entry = json.loads(resp.read().decode('utf-8'))
            with open('data/entry.json', 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False)
    except Exception as e:
        print(f"Warning fetching entry: {e}")

    # 3. history
    try:
        req = urllib.request.Request('https://fantasy.premierleague.com/api/entry/306983/history/', headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            hist = json.loads(resp.read().decode('utf-8'))
            with open('data/history.json', 'w', encoding='utf-8') as f:
                json.dump(hist, f, ensure_ascii=False)
    except Exception as e:
        print(f"Warning fetching history: {e}")

    # 4. fixtures
    req = urllib.request.Request('https://fantasy.premierleague.com/api/fixtures/', headers=headers)
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        fix = json.loads(resp.read().decode('utf-8'))
        with open('data/fixtures.json', 'w', encoding='utf-8') as f:
            json.dump(fix, f, ensure_ascii=False)

    return bs, fix

def main():
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Choice 2 Real-Time Optimization Engine...")
    bs, fix = fetch_live_data()

    # Re-run presentation generator
    cmd = [sys.executable, "generate_presentation.py", "--out", "index.html"]
    subprocess.run(cmd, check=True)

    cmd_gw3 = [sys.executable, "generate_presentation.py", "--out", "fpl_gw3_presentation.html"]
    subprocess.run(cmd_gw3, check=True)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Choice 2 Optimization & Presentation Compilation Complete.")

if __name__ == "__main__":
    main()
