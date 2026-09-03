#!/usr/bin/env python3
"""
auto_sync_choice2.py
--------------------
Hybrid Autonomous Engine for Choice 2 (The Master Fortress Blueprint).
Runs on an offset 15-minute schedule via GitHub Actions.

Smart Commit & Resilience Architecture:
1. Re-fetches Official FPL API with Exponential Backoff & Retry (handles network flakiness).
2. Computes an exact cryptographic data fingerprint (SHA256) across player prices (now_cost),
   injury flags (status/news), points, and fixture progress.
3. Checks proximity to Gameweek deadline (< 2 hours triggers Final Lockdown mode).
4. Detects current active Gameweek dynamically for multi-gameweek roll-over (GW3 -> GW38).
5. Only compiles presentation and touches files if substantive changes exist or forced,
   preventing git commit spam and eliminating GitHub Actions queue throttling.
"""

import json
import urllib.request
import ssl
import sys
import os
import time
import subprocess
import hashlib
from datetime import datetime, timezone

def fetch_json_with_retry(url, headers, timeout=15, max_retries=3, backoff_factor=2):
    """
    Resilient HTTP JSON fetcher with exponential backoff.
    Attempts max_retries with progressive delays [2s, 4s, 8s] to gracefully handle FPL API rate limits.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    last_error = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                sleep_sec = backoff_factor * (attempt + 1)
                print(f"[Network Retry] Attempt {attempt + 1} failed for {url}: {e}. Retrying in {sleep_sec}s...")
                time.sleep(sleep_sec)
    raise last_error

def extract_data_fingerprint(bs, fix):
    """
    Generate a deterministic SHA256 hash of all fields that impact FPL decisions:
    - Player prices (now_cost)
    - Injury/availability statuses and news
    - Player points
    - Fixture kickoff, scores, and status
    """
    elements_sig = [
        (
            e.get('id'),
            e.get('now_cost'),
            e.get('status'),
            e.get('chance_of_playing_next_round'),
            e.get('news'),
            e.get('total_points')
        )
        for e in bs.get('elements', [])
    ]
    fixtures_sig = [
        (
            f.get('id'),
            f.get('started'),
            f.get('finished'),
            f.get('team_h_score'),
            f.get('team_a_score')
        )
        for f in fix
    ] if isinstance(fix, list) else []

    payload = json.dumps({'el': elements_sig, 'fix': fixtures_sig}, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def check_deadline_status(bs):
    """
    Returns (is_urgent, seconds_remaining, next_gw_id)
    Urgent if within 2 hours (7200s) of next gameweek deadline.
    """
    events = bs.get('events', [])
    for ev in events:
        if ev.get('is_next'):
            deadline_epoch = ev.get('deadline_time_epoch')
            if deadline_epoch:
                now_epoch = datetime.now(timezone.utc).timestamp()
                diff_sec = deadline_epoch - now_epoch
                is_urgent = (0 <= diff_sec <= 7200)
                return is_urgent, diff_sec, ev.get('id')
    return False, None, None

def get_active_gameweek(bs):
    """
    Detect the active Gameweek for squad planning:
    1. If a gameweek is currently in play (is_current=True and finished=False), use it.
    2. Otherwise, use the upcoming deadline gameweek (is_next=True).
    3. Fallback to is_current.
    """
    events = bs.get('events', []) if isinstance(bs, dict) else []
    for ev in events:
        if ev.get('is_current') and not ev.get('finished'):
            return ev.get('id', 3)
    for ev in events:
        if ev.get('is_next'):
            return ev.get('id', 3)
    for ev in events:
        if ev.get('is_current'):
            return ev.get('id', 3)
    return 3

def fetch_live_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    os.makedirs('data', exist_ok=True)

    bs = None
    fix = None

    # 1. bootstrap-static
    try:
        bs = fetch_json_with_retry('https://fantasy.premierleague.com/api/bootstrap-static/', headers=headers)
    except Exception as e:
        print(f"Warning fetching live bootstrap-static after retries: {e}")
        if os.path.exists('data/bootstrap_static.json'):
            with open('data/bootstrap_static.json', 'r', encoding='utf-8') as f:
                bs = json.load(f)

    # 2. fixtures
    try:
        fix = fetch_json_with_retry('https://fantasy.premierleague.com/api/fixtures/', headers=headers)
    except Exception as e:
        print(f"Warning fetching live fixtures after retries: {e}")
        if os.path.exists('data/fixtures.json'):
            with open('data/fixtures.json', 'r', encoding='utf-8') as f:
                fix = json.load(f)

    # 3. entry & history
    for endpoint, filename in [('entry/306983/', 'data/entry.json'), ('entry/306983/history/', 'data/history.json')]:
        try:
            data = fetch_json_with_retry(f'https://fantasy.premierleague.com/api/{endpoint}', headers=headers)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            print(f"Notice fetching {endpoint}: {e}")

    return bs, fix

def main():
    force_run = '--force' in sys.argv
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Choice 2 Smart Real-Time Engine...")

    bs, fix = fetch_live_data()
    if not bs:
        print("Error: Could not retrieve bootstrap-static data. Aborting.")
        return

    # Check data fingerprint
    current_fp = extract_data_fingerprint(bs, fix)
    fp_file = 'data/data_fingerprint.txt'
    previous_fp = ''
    if os.path.exists(fp_file):
        with open(fp_file, 'r', encoding='utf-8') as f:
            previous_fp = f.read().strip()

    is_urgent, seconds_left, next_gw = check_deadline_status(bs)
    data_changed = (current_fp != previous_fp)

    if not data_changed and not is_urgent and not force_run:
        print(f"[Smart Commit] Data identical (Fingerprint: {current_fp[:10]}...). No market price or injury changes detected.")
        print("[Smart Commit] Skipped presentation compilation to prevent unnecessary git commits and avoid GitHub Actions throttling.")
        return

    # Data changed or near deadline: Save data files and update fingerprint
    reason = []
    if data_changed:
        reason.append("Substantive market data / price / injury updates")
    if is_urgent:
        reason.append(f"Deadline countdown active (GW{next_gw} deadline in {int(seconds_left // 60)} mins)")
    if force_run:
        reason.append("Force execution flag passed")

    print(f"[Smart Commit] Proceeding with synchronization: {', '.join(reason)}")

    with open('data/bootstrap_static.json', 'w', encoding='utf-8') as f:
        json.dump(bs, f, ensure_ascii=False)

    if fix is not None:
        with open('data/fixtures.json', 'w', encoding='utf-8') as f:
            json.dump(fix, f, ensure_ascii=False)

    with open(fp_file, 'w', encoding='utf-8') as f:
        f.write(current_fp)

    active_gw = get_active_gameweek(bs)

    # Re-run presentation generator for main dashboard and dynamic gameweek archive
    cmd = [sys.executable, "generate_presentation.py", "--out", "index.html"]
    subprocess.run(cmd, check=True)

    cmd_dyn = [sys.executable, "generate_presentation.py", "--out", f"fpl_gw{active_gw}_presentation.html"]
    subprocess.run(cmd_dyn, check=True)

    if active_gw != 3:
        cmd_gw3 = [sys.executable, "generate_presentation.py", "--out", "fpl_gw3_presentation.html"]
        subprocess.run(cmd_gw3, check=True)

    print(f"[{datetime.now(timezone.utc).isoformat()}] Choice 2 Optimization & Presentation Compilation Complete (Active GW{active_gw}).")

if __name__ == "__main__":
    main()
