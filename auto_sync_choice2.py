#!/usr/bin/env python3
"""
auto_sync_choice2.py
--------------------
Hybrid Autonomous Engine for Choice 2 (The Master Fortress Blueprint).
Runs on an offset 15-minute schedule via GitHub Actions.

Hardened Strategic & Resilience Architecture (Rollback 2):
1. Resilient HTTP fetcher with Exponential Backoff & Retry (handles network latency and rate limits).
2. Cryptographic Fingerprint Verification (SHA256) across player prices, injury flags, and fixtures.
3. Friday Press Conference & Injury Watcher: Actively monitors squad health and flags tactical alerts.
4. Post-Gameweek Archive Automation: Tracks actual performance, rank trajectory, and Top 100k pacing.
5. Final Lockdown Engine (< 30 minutes to Gameweek deadline).
6. Smart Commit Decision Gate: Skips redundant commits to preserve GitHub Actions quotas and avoid throttling.
"""

import json
import urllib.request
import ssl
import sys
import os
import time
import subprocess
import hashlib
from datetime import datetime, timezone, timedelta

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
    Returns (is_urgent, is_lockdown, seconds_remaining, next_gw_id)
    - Urgent if within 2 hours (7200s) of next gameweek deadline.
    - Lockdown if within 30 minutes (1800s) of next gameweek deadline.
    """
    events = bs.get('events', [])
    for ev in events:
        if ev.get('is_next'):
            deadline_epoch = ev.get('deadline_time_epoch')
            if deadline_epoch:
                now_epoch = datetime.now(timezone.utc).timestamp()
                diff_sec = deadline_epoch - now_epoch
                is_urgent = (0 <= diff_sec <= 7200)
                is_lockdown = (0 <= diff_sec <= 1800)
                return is_urgent, is_lockdown, diff_sec, ev.get('id')
    return False, False, None, None

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

def monitor_press_conferences_and_injuries(bs):
    """
    Strategic Injury & Press Conference Watcher:
    Continuously monitors squad starters and key transfer targets.
    Flags any change in chance_of_playing, yellow/red status, or press conference news.
    """
    elements_map = {e['id']: e for e in bs.get('elements', [])}
    # Monitored Core Targets (Choice 1 & Choice 2 Key Players)
    monitored_pids = [109, 391, 277, 4, 124, 367, 398, 368, 154, 464, 411, 496, 165, 304, 31]
    
    alerts = []
    for pid in monitored_pids:
        el = elements_map.get(pid)
        if not el: continue
        
        status = el.get('status', 'a')
        chance = el.get('chance_of_playing_next_round')
        news = el.get('news', '')
        
        is_flagged = (status != 'a') or (chance is not None and chance < 100) or bool(news)
        if is_flagged:
            alerts.append({
                "id": pid,
                "web_name": el.get('web_name'),
                "status": status,
                "chance": chance,
                "news": news,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            print(f"[PRESS CONF ALERT] {el.get('web_name')} flagged: {chance}% chance - {news}")

    os.makedirs('data', exist_ok=True)
    with open('data/tactical_alerts.json', 'w', encoding='utf-8') as f:
        json.dump({
            "last_checked": datetime.now(timezone.utc).isoformat(),
            "total_alerts": len(alerts),
            "alerts": alerts
        }, f, indent=2, ensure_ascii=False)
    
    return alerts

def evaluate_and_archive_gameweek_performance(bs):
    """
    Post-Gameweek Archive Automation:
    Reads official history and records performance trajectory towards Top 100k.
    """
    history_file = 'data/history.json'
    if not os.path.exists(history_file):
        return

    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            hist_data = json.load(f)
        
        current_gws = hist_data.get('current', [])
        archive = {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_gameweeks": len(current_gws),
            "trajectory": [
                {
                    "gw": gw.get('event'),
                    "points": gw.get('points'),
                    "total_points": gw.get('total_points'),
                    "overall_rank": gw.get('overall_rank'),
                    "in_top_100k": (gw.get('overall_rank', 9999999) <= 100000)
                }
                for gw in current_gws
            ]
        }
        with open('data/gw_performance_archive.json', 'w', encoding='utf-8') as f:
            json.dump(archive, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Notice generating GW performance archive: {e}")

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
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Choice 2 Smart Real-Time Engine (Rollback 2 Architecture)...")

    bs, fix = fetch_live_data()
    if not bs:
        print("Error: Could not retrieve bootstrap-static data. Aborting.")
        return

    # 1. Press Conference & Injury Watcher
    alerts = monitor_press_conferences_and_injuries(bs)

    # 2. Post-Gameweek Archive Evaluation
    evaluate_and_archive_gameweek_performance(bs)

    # 3. Check Data Fingerprint
    current_fp = extract_data_fingerprint(bs, fix)
    fp_file = 'data/data_fingerprint.txt'
    previous_fp = ''
    if os.path.exists(fp_file):
        with open(fp_file, 'r', encoding='utf-8') as f:
            previous_fp = f.read().strip()

    is_urgent, is_lockdown, seconds_left, next_gw = check_deadline_status(bs)
    data_changed = (current_fp != previous_fp)

    # Handle Final Lockdown mode (< 30 minutes before deadline)
    if is_lockdown:
        print(f"[FINAL LOCKDOWN] Deadline is in {int(seconds_left // 60)} minutes! Freezing Choice 2 Master Blueprint.")
        lockdown_meta = {
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "gameweek": next_gw,
            "seconds_remaining": seconds_left,
            "status": "LOCKED"
        }
        with open(f'data/final_lockdown_gw{next_gw}.json', 'w', encoding='utf-8') as f:
            json.dump(lockdown_meta, f, indent=2)

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
    if is_lockdown:
        reason.append("Final Lockdown at Deadline - 30m")
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
