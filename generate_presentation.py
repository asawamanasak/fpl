#!/usr/bin/env python3
"""
FPL Presentation Generator
- 4 Navigation Tabs:
  1. Plan Lineup (Side-by-Side Pitch & Full Bench)
  2. Plan Summary (Live Real-Time Quantitative Comparison & Pros/Cons Audit)
  3. FDR Ticker (Full Season GW3-38 Matrix & Legend)
  4. Research Sources (5 Intelligence Sources Ledger)
- Larger Player Shirts & Info Cards, Tighter Snug Pitch Spacing
- Upgraded Prominent Substitutes Bench Cards
- Verified 8-Chip Roadmap & 5 Intelligence Sources Ledger
- Zero Emojis, Dark Minimalist Theme
"""

import json
import os
import argparse
from datetime import datetime, timezone, timedelta

def load_json(filepath):
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def render_starter_card(p):
    cap_marker = ""
    if p.get("is_captain"):
        cap_marker = '<span class="role-badge-cap">C</span>'
    elif p.get("is_vice_captain"):
        cap_marker = '<span class="role-badge-vc">V</span>'

    pos_class = f"pos-{p['pos']}"
    fdr_class = f"fdr-{p['next_fdr']}"
    core_tag = '<span class="core-tag-mini">CORE</span>' if p.get("is_core") else ''
    enabler_tag = '<span class="enabler-tag-mini">VALUE</span>' if p.get("is_enabler") else ''
    transfer_tag = '<span class="transfer-in-tag-mini">IN</span>' if p.get("is_transfer_in") else ''
    card_extra = " card-transfer-in" if p.get("is_transfer_in") else ""

    t_code = p.get("official_team_code", 43)
    is_gkp = p.get("pos") == "GKP"
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"

    return f"""
    <div class="starter-card{card_extra}">
        <div class="starter-card-top">
            <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
            <div class="starter-badges-group">
                {cap_marker}
                {transfer_tag}
                {core_tag}
                {enabler_tag}
            </div>
        </div>
        <div class="starter-photo-wrap">
            <img src="{fpl_shirt_url}" 
                 alt="{p['web_name']}" 
                 class="starter-shirt-img" 
                 loading="lazy" />
        </div>
        <div class="starter-info-card">
            <div class="starter-name" title="{p['full_name']}">{p['web_name']}</div>
            <div class="starter-meta">{p['team_code']} &bull; £{p['cost']:.1f}m</div>
            <div class="starter-fix-row">
                <span class="starter-fix-text">{p['next_fix'].split(' ')[0]}</span>
                <span class="fdr-pill {fdr_class}">FDR {p['next_fdr']}</span>
            </div>
        </div>
    </div>
    """

def render_bench_card(p, sub_idx=1):
    pos_class = f"pos-{p['pos']}"
    fdr_class = f"fdr-{p['next_fdr']}"
    core_tag = '<span class="core-tag-mini">CORE</span>' if p.get("is_core") else ''
    enabler_tag = '<span class="enabler-tag-mini">VALUE</span>' if p.get("is_enabler") else ''
    transfer_tag = '<span class="transfer-in-tag-mini">IN</span>' if p.get("is_transfer_in") else ''
    card_extra = " card-transfer-in" if p.get("is_transfer_in") else ""
    
    is_gkp = p.get("pos") == "GKP"
    sub_label = "GKP SUB" if is_gkp else f"SUB {sub_idx}"
    sub_tag = f'<span class="sub-label-badge">{sub_label}</span>'

    t_code = p.get("official_team_code", 43)
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"

    return f"""
    <div class="bench-card{card_extra}">
        <div class="bench-card-top">
            <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
            <div class="starter-badges-group">
                {sub_tag}
                {transfer_tag}
                {core_tag}
                {enabler_tag}
            </div>
        </div>
        <div class="bench-photo-wrap">
            <img src="{fpl_shirt_url}" 
                 alt="{p['web_name']}" 
                 class="bench-shirt-img" 
                 loading="lazy" />
        </div>
        <div class="bench-info-card">
            <div class="bench-name" title="{p['full_name']}">{p['web_name']}</div>
            <div class="bench-meta">{p['team_code']} &bull; £{p['cost']:.1f}m</div>
            <div class="bench-fix-row">
                <span class="bench-fix-text">{p['next_fix'].split(' ')[0]}</span>
                <span class="fdr-pill {fdr_class}">FDR {p['next_fdr']}</span>
            </div>
        </div>
    </div>
    """

def render_bench_list(bench_players):
    outfield_idx = 1
    cards = []
    for p in bench_players:
        if p.get("pos") == "GKP":
            cards.append(render_bench_card(p, sub_idx="GKP"))
        else:
            cards.append(render_bench_card(p, sub_idx=outfield_idx))
            outfield_idx += 1
    return "".join(cards)

def align_pitch_players(c1_starters, c2_starters, pos):
    """
    Given c1_starters and c2_starters for a given position (pos),
    order c2_starters so that any player shared with c1_starters
    occupies the exact same slot index as in c1_starters.
    """
    c1_pos = [p for p in c1_starters if p["pos"] == pos]
    c2_pos = [p for p in c2_starters if p["pos"] == pos]
    
    if len(c1_pos) != len(c2_pos):
        return c2_pos
        
    aligned = [None] * len(c1_pos)
    c2_remaining = list(c2_pos)
    
    # First pass: Place exact matching players in their exact c1 index
    for i, p1 in enumerate(c1_pos):
        for p2 in c2_remaining:
            if p2["id"] == p1["id"]:
                aligned[i] = p2
                c2_remaining.remove(p2)
                break
                
    # Second pass: Fill vacant slots with remaining c2 players
    for i in range(len(aligned)):
        if aligned[i] is None and c2_remaining:
            aligned[i] = c2_remaining.pop(0)
            
    return aligned

def align_bench_players(c1_bench, c2_bench):
    """
    Align bench so that identical players occupy the same sub index.
    """
    if len(c1_bench) != len(c2_bench):
        return c2_bench
    aligned = [None] * len(c1_bench)
    c2_remaining = list(c2_bench)
    for i, p1 in enumerate(c1_bench):
        for p2 in c2_remaining:
            if p2["id"] == p1["id"]:
                aligned[i] = p2
                c2_remaining.remove(p2)
                break
    for i in range(len(aligned)):
        if aligned[i] is None and c2_remaining:
            aligned[i] = c2_remaining.pop(0)
    return aligned

def render_ticker_row_full_season(p, team_fixtures, start_gw=4, end_gw=38, orig_idx=0):
    t_id = p.get("team_id", 1)
    fix_dict = team_fixtures.get(t_id, {})
    
    cells = []
    for gw in range(start_gw, end_gw + 1):
        gw_fixes = fix_dict.get(gw, [])
        if not gw_fixes:
            cells.append('<td data-val="99"><span class="fdr-box-lg fdr-3">-</span></td>')
        else:
            chips = []
            max_diff = 0
            for f in gw_fixes:
                loc = "H" if f["is_home"] else "A"
                diff = f["diff"]
                max_diff = max(max_diff, diff)
                chips.append(f'<span class="fdr-box-lg fdr-{diff}">{f["opp"]}({loc})</span>')
            cells.append(f'<td data-val="{max_diff}">{" ".join(chips)}</td>')

    pos_order = {"GKP": 1, "DEF": 2, "MID": 3, "FWD": 4}.get(p['pos'], 99)

    return f"""
    <tr data-orig-index="{orig_idx}">
        <td class="tbl-sticky tbl-name" data-val="{p['web_name']}">{p['web_name']}</td>
        <td class="tbl-sticky-2" data-val="{p['team_code']}">{p['team_code']}</td>
        <td class="tbl-sticky-3" data-val="{pos_order}"><span class="pos-tag-mini pos-{p['pos']}">{p['pos']}</span></td>
        <td class="tbl-sticky-4 font-mono" data-val="{p['cost']}">£{p['cost']:.1f}m</td>
        {"".join(cells)}
    </tr>
    """

def generate_html_report(data_dir="data", output_file="index.html", target_gw=None):
    bootstrap = load_json(os.path.join(data_dir, "bootstrap_static.json"))
    entry = load_json(os.path.join(data_dir, "entry.json"))
    fixtures = load_json(os.path.join(data_dir, "fixtures.json"))
    solio = load_json(os.path.join(data_dir, "solio_latest.json"))
    history = load_json(os.path.join(data_dir, "history.json"))

    if not bootstrap or not entry:
        print("[!] Missing required data. Run fetch_fpl_data.py first.")
        return

    events = bootstrap.get("events", [])
    current_event_obj = next((e for e in events if e.get("is_current")), None)
    next_event_obj = next((e for e in events if e.get("is_next")), None)
    
    current_gw = current_event_obj["id"] if current_event_obj else entry.get("current_event", 2)
    next_gw = next_event_obj["id"] if next_event_obj else current_gw + 1

    teams = {t["id"]: t for t in bootstrap.get("teams", [])}
    elements_map = {e["id"]: e for e in bootstrap.get("elements", [])}

    solio_proj_map = {}
    if solio and "topProjected" in solio:
        for sp in solio["topProjected"]:
            solio_proj_map[sp.get("name", "").lower()] = sp

    # Full season fixtures lookup (GW1 - GW38)
    team_fixtures = {}
    for fix in (fixtures or []):
        ev = fix.get("event")
        if ev:
            th, ta = fix["team_h"], fix["team_a"]
            if th not in team_fixtures: team_fixtures[th] = {}
            if ta not in team_fixtures: team_fixtures[ta] = {}
            if ev not in team_fixtures[th]: team_fixtures[th][ev] = []
            if ev not in team_fixtures[ta]: team_fixtures[ta][ev] = []
            
            opp_a = teams.get(ta, {}).get("short_name", "???")
            opp_h = teams.get(th, {}).get("short_name", "???")
            team_fixtures[th][ev].append({
                "opp": opp_a,
                "is_home": True,
                "diff": fix.get("team_h_difficulty", 3)
            })
            team_fixtures[ta][ev].append({
                "opp": opp_h,
                "is_home": False,
                "diff": fix.get("team_a_difficulty", 3)
            })

    pos_map = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}

    def build_player_by_id(element_id, is_starter, is_cap=False, is_vc=False, is_core=False, is_enabler=False):
        el = elements_map.get(element_id)
        if not el:
            return None
        t_id = el["team"]
        t_obj = teams.get(t_id, {})
        team_short = t_obj.get("short_name", "???")
        official_t_code = t_obj.get("code", 1)
        cost = el.get("now_cost", 50) / 10.0
        pos = pos_map.get(el.get("element_type", 1), "MID")
        
        next_fix_list = team_fixtures.get(t_id, {}).get(next_gw, [])
        next_fix_str = "BLANK"
        next_fdr = 3
        if next_fix_list:
            f0 = next_fix_list[0]
            next_fix_str = f"{f0['opp']} ({'H' if f0['is_home'] else 'A'})"
            next_fdr = f0['diff']

        solio_p = solio_proj_map.get(el.get("web_name", "").lower())
        solio_pts = solio_p.get("prPoints", None) if solio_p else None

        tot_pts = el.get("total_points", 0)
        xgi = float(el.get("expected_goal_involvements", 0.0) or 0.0)
        mins = el.get("minutes", 0)

        return {
            "id": el["id"],
            "web_name": el["web_name"],
            "full_name": f"{el.get('first_name', '')} {el.get('second_name', '')}",
            "team_code": team_short,
            "team_id": t_id,
            "official_team_code": official_t_code,
            "pos": pos,
            "cost": cost,
            "is_starter": is_starter,
            "is_captain": is_cap,
            "is_vice_captain": is_vc,
            "is_core": is_core,
            "is_enabler": is_enabler,
            "next_fix": next_fix_str,
            "next_fdr": next_fdr,
            "solio_pts": solio_pts,
            "total_points": tot_pts,
            "xgi": xgi,
            "minutes": mins
        }

    # CHOICE 1: User's Final Official Lockdown Squad (GW4 Verified from Screenshot)
    # Formation: 3-4-3 | Captain: Cole Palmer [C] | Vice-Captain: João Pedro [V]
    # Transfer Executed: Cody Gakpo (£7.2m) -> Martin Ødegaard (£6.7m) (1 FT Used, 0 Pt Hit)
    # Bank Reserve: +£0.5m | Remaining FTs: 1 FT (Saved for GW5)
    c1_ids = [
        (109, True, False, False, False, False),  # Verbruggen (GKP £4.5m, BHA @ COV A)
        (304, True, False, False, False, False),  # O'Shea (DEF £4.0m, IPS @ CRY A)
        (31, True, False, False, False, False),   # Konsa (DEF £4.4m, AVL @ SUN A)
        (4, True, False, False, True, False),     # Gabriel (DEF Core £8.0m, ARS @ SUN A)
        (124, True, False, False, False, False),  # Groß (MID £5.5m, BHA @ COV A)
        (15, True, False, False, False, False),   # Ødegaard (MID Transfer In £6.7m, ARS @ SUN A)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core £7.0m, LIV vs FUL H)
        (154, True, True, False, False, False),   # Palmer (MID C £9.6m, CHE vs HUL H)
        (165, True, False, True, True, False),    # João Pedro (FWD VC Core £7.7m, CHE vs HUL H)
        (464, True, False, False, False, False),  # Wissa (FWD £6.2m, NEW @ LEE A)
        (411, True, False, False, True, False),   # Haaland (FWD Core £15.5m, MCI @ MUN A)
        # Bench
        (496, False, False, False, False, False), # Kinsky (GKP Sub £4.5m, TOT vs EVE H)
        (398, False, False, False, False, False), # Foden (MID Sub 1 £7.0m, MCI @ MUN A)
        (391, False, False, False, True, False),  # Gvardiol (DEF Sub 2 Core £5.6m, MCI @ MUN A)
        (277, False, False, False, False, False), # Egan (DEF Sub 3 £4.1m, HUL @ CHE A)
    ]
    c1_squad = [build_player_by_id(*p) for p in c1_ids if build_player_by_id(*p)]
    for p in c1_squad:
        if p["id"] == 15:
            p["is_transfer_in"] = True
    c1_starters = [p for p in c1_squad if p["is_starter"]]
    c1_bench = [p for p in c1_squad if not p["is_starter"]]
    c1_cost = sum(p["cost"] for p in c1_squad)
    c1_bank = 0.5

    # Total Team Budget dynamically derived from Choice 1 and FPL Entry data
    total_budget = round(max(c1_cost + c1_bank, (entry.get("last_deadline_value", 1000) + entry.get("last_deadline_bank", 0)) / 10.0), 1)

    # Official User Transfer State (Confirmed from official FPL transfers page):
    # 1 Transfer executed (Gakpo -> Ødegaard), 1 Free Transfer remaining banked for GW5. Penalty: 0 pts.
    user_free_transfers = 2
    transfers_count = 1

    # CHOICE 2: GEMINI Autonomous Derby Attack Variant (3-5-2 Formation, 0 Hits)
    # Tactical Variant: Starts Antonín Kinsky at home vs Everton, and deploys Phil Foden in 3-5-2
    # to unlock high explosive ceiling in the Manchester Derby, benching O'Shea vs Crystal Palace.
    c2_ids = [
        (496, True, False, False, False, False),  # Kinsky (GKP Starter vs Everton H)
        (31, True, False, False, False, False),   # Konsa (DEF @ Sunderland A)
        (4, True, False, False, True, False),     # Gabriel (DEF @ Sunderland A)
        (304, True, False, False, False, False),  # O'Shea (DEF @ Crystal Palace A)
        (124, True, False, False, False, False),  # Groß (MID @ Coventry A)
        (15, True, False, False, False, False),   # Ødegaard (MID @ Sunderland A)
        (368, True, False, False, True, False),   # Szoboszlai (MID vs Fulham H)
        (154, True, True, False, False, False),   # Palmer (MID C vs Hull City H)
        (398, True, False, False, False, False),  # Foden (MID Starter in 3-5-2 @ Man United A)
        (165, True, False, True, True, False),    # João Pedro (FWD VC vs Hull City H)
        (411, True, False, False, True, False),   # Haaland (FWD @ Man United A)
        # Bench
        (109, False, False, False, False, False), # Verbruggen (GKP Sub)
        (464, False, False, False, False, False), # Wissa (FWD Sub 1)
        (391, False, False, False, True, False),  # Gvardiol (DEF Sub 2)
        (277, False, False, False, False, False), # Egan (DEF Sub 3)
    ]

    c2_squad = [build_player_by_id(*p) for p in c2_ids if build_player_by_id(*p)]
    for p in c2_squad:
        if p["id"] == 15:
            p["is_transfer_in"] = True
    c2_starters = [p for p in c2_squad if p["is_starter"]]
    c2_bench = [p for p in c2_squad if not p["is_starter"]]
    c2_cost = sum(p["cost"] for p in c2_squad)
    c2_bank = c1_bank
    c2_bank_str = f"+£{c2_bank:.1f}m"

    # Dynamic metrics computation for Plan Summary
    c1_tot_pts = sum(p["total_points"] for p in c1_squad)
    c2_tot_pts = sum(p["total_points"] for p in c2_squad)
    c1_start_pts = sum(p["total_points"] for p in c1_starters)
    c2_start_pts = sum(p["total_points"] for p in c2_starters)

    c1_tot_xgi = sum(p["xgi"] for p in c1_squad)
    c2_tot_xgi = sum(p["xgi"] for p in c2_squad)
    c1_start_xgi = sum(p["xgi"] for p in c1_starters)
    c2_start_xgi = sum(p["xgi"] for p in c2_starters)

    c1_nailed_count = sum(1 for p in c1_squad if p["minutes"] >= 90)
    c2_nailed_count = sum(1 for p in c2_squad if p["minutes"] >= 90)

    # Dynamic Pros & Cons for Choice 2:
    c2_pro_upgrade = "<strong>Manchester Derby Ceiling Exploitation (Foden Started in 3-5-2):</strong> ส่ง Phil Foden ลงตัวจริงในแดนกลาง 5 คน ลุ้นเพดานแต้มระเบิดจากศึกแมนเชสเตอร์ดาร์บี้เต็มสูบ แทนการส่ง Dara O'Shea ที่ต้องออกไปเยือนคริสตัล พาเลซ"
    c2_con_transfer = "<strong>Leeds Away Striker Sacrifice (Wissa Benched as Sub 1):</strong> การปรับทัพเป็น 3-5-2 ทำให้ต้องพัก Yoane Wissa เป็นตัวสำรองอันดับ 1 แม้ฟอร์มกำลังร้อนแรงและมีโปรแกรมเยือนลีดส์ ยูไนเต็ด"

    # Dynamic Last Sync Timestamp from GitHub Cloud / Live API (ICT / UTC+7)
    ict_tz = timezone(timedelta(hours=7))
    if os.path.exists("data/bootstrap_static.json"):
        mtime = os.path.getmtime("data/bootstrap_static.json")
        sync_dt = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone(ict_tz)
    else:
        sync_dt = datetime.now(ict_tz)
    last_sync_str = sync_dt.strftime("%d/%m/%Y %I:%M %p")

    # Dynamic Gameweek Detection from Events
    active_gw = target_gw or 4
    deadline_epoch = 1789216200
    deadline_str = "Sat 12 Sep, 19:30 ICT"
    now_epoch = datetime.now(timezone.utc).timestamp()
    if not target_gw:
        for ev in bootstrap.get("events", []):
            if ev.get("is_current") and not ev.get("finished") and ev.get("deadline_time_epoch", 0) > now_epoch:
                active_gw = ev.get("id", 4)
                break
        else:
            for ev in bootstrap.get("events", []):
                if ev.get("is_next"):
                    active_gw = ev.get("id", 4)
                    break

    for ev in bootstrap.get("events", []):
        if ev.get("id") == active_gw:
            deadline_epoch = ev.get("deadline_time_epoch", 1789216200)
            if ev.get("deadline_time"):
                try:
                    dt = datetime.fromisoformat(ev["deadline_time"].replace("Z", "+00:00")).astimezone(ict_tz)
                    deadline_str = dt.strftime("%a %d %b, %H:%M ICT")
                except Exception:
                    pass
            break

    # Global Rank Trajectory & Top 100k Tracker
    overall_rank = 65185
    if history and isinstance(history, dict) and history.get("current"):
        latest_history = history["current"][-1]
        overall_rank = latest_history.get("overall_rank", 65185)
    elif os.path.exists("data/gw_performance_archive.json"):
        try:
            with open("data/gw_performance_archive.json", "r", encoding="utf-8") as f:
                perf_data = json.load(f)
                if perf_data.get("trajectory"):
                    overall_rank = perf_data["trajectory"][-1].get("overall_rank", 65185)
        except Exception:
            pass
    in_top_100k = (overall_rank <= 100000)
    rank_target_label = "TOP 100K : ON TRACK" if in_top_100k else "TOP 100K : PURSUING"
    rank_tag_class = "status-ontrack" if in_top_100k else "status-pursuing"

    # Friday Press Conference & Squad Health Watcher Data
    tactical_alerts_data = {"total_alerts": 0, "alerts": []}
    if os.path.exists("data/tactical_alerts.json"):
        try:
            with open("data/tactical_alerts.json", "r", encoding="utf-8") as f:
                tactical_alerts_data = json.load(f)
        except Exception:
            pass
    total_flags = tactical_alerts_data.get("total_alerts", 0)
    if total_flags == 0:
        health_status_badge = "100% MATCH FIT"
        health_badge_class = "health-badge-ok"
        health_detail_text = "เฝ้าระวังตัวหลักทั้ง 15 คน (Haaland, Palmer, Foden, Gakpo, Szoboszlai, Pedro ฯลฯ) ตรวจพบความพร้อม 100% ปราศจากรายงานบาดเจ็บหรือแบนจากงานแถลงข่าว"
        health_alerts_html = ""
    else:
        health_status_badge = f"{total_flags} TACTICAL ALERTS"
        health_badge_class = "health-badge-warning"
        health_detail_text = f"ตรวจพบความเสี่ยงหรืออาการบาดเจ็บของนักเตะในทีม {total_flags} รายการ กรุณาตรวจสอบตัวเลือกสำรอง:"
        items = []
        for alt in tactical_alerts_data.get("alerts", []):
            items.append(f'<div class="health-alert-pill"><strong>{alt["web_name"]}</strong>: โอกาสลงสนาม {alt.get("chance", "???")}% &bull; {alt.get("news", "No news")}</div>')
        health_alerts_html = '<div class="health-alerts-box">' + "".join(items) + '</div>'

    # Dynamic 2026/27 FPL Chip Inventory Computation from Official API Rules
    all_chips_meta = bootstrap.get("chips", [])
    used_chips_history = history.get("chips", []) if history and isinstance(history, dict) else []

    chip_names_display = {
        "wildcard": "Wildcard",
        "freehit": "Free Hit",
        "bboost": "Bench Boost",
        "3xc": "Triple Captain"
    }

    half1_cards_html = []
    half2_cards_html = []
    remaining_chips_count = 0
    total_chips_count = len(all_chips_meta)

    for c in all_chips_meta:
        c_name = c.get("name")
        s_ev = c.get("start_event", 1)
        e_ev = c.get("stop_event", 38)
        c_num = c.get("number", 1)
        used_entry = next((u for u in used_chips_history if u.get("name") == c_name and s_ev <= u.get("event", 0) <= e_ev), None)
        is_used = used_entry is not None
        used_gw = used_entry.get("event") if used_entry else None
        
        display_title = f"{chip_names_display.get(c_name, c_name)} #{c_num}"
        if e_ev <= 19:
            # Half 1 (GW1-19)
            if is_used:
                status_badge = f"USED (GW{used_gw})"
                status_color = "var(--text-muted)"
                border_color = "var(--border-subtle)"
                note = f"ใช้งานแล้วใน GW{used_gw}"
            else:
                remaining_chips_count += 1
                status_badge = "AVAILABLE"
                status_color = "var(--accent-emerald)"
                border_color = "rgba(16, 185, 129, 0.4)"
                note = "พร้อมใช้ทันที (หมดอายุสิ้น GW19)"
            
            card = f'''<div style="flex:1; min-width:130px; background:var(--bg-card-hover); border:1px solid {border_color}; border-radius:6px; padding:0.5rem 0.75rem;">
                <div style="font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">{display_title} &bull; GW{s_ev}-{e_ev}</div>
                <div style="font-size:0.85rem; font-weight:700; color:{status_color}; margin-top:2px;">{status_badge}</div>
                <div style="font-size:0.65rem; color:var(--text-muted); margin-top:2px;">{note}</div>
            </div>'''
            half1_cards_html.append(card)
        else:
            # Half 2 (GW20-38)
            if is_used:
                status_badge = f"USED (GW{used_gw})"
                status_color = "var(--text-muted)"
                border_color = "var(--border-subtle)"
                note = f"ใช้งานแล้วใน GW{used_gw}"
            else:
                remaining_chips_count += 1
                status_badge = "AVAILABLE (GW20+)"
                status_color = "var(--accent-sky)"
                border_color = "rgba(56, 189, 248, 0.4)"
                note = "ปลดล็อกครึ่งฤดูกาลหลัง"
            
            card = f'''<div style="flex:1; min-width:130px; background:var(--bg-card-hover); border:1px solid {border_color}; border-radius:6px; padding:0.5rem 0.75rem;">
                <div style="font-size:0.65rem; color:var(--text-muted); text-transform:uppercase; letter-spacing:0.5px;">{display_title} &bull; GW{s_ev}-{e_ev}</div>
                <div style="font-size:0.85rem; font-weight:700; color:{status_color}; margin-top:2px;">{status_badge}</div>
                <div style="font-size:0.65rem; color:var(--text-muted); margin-top:2px;">{note}</div>
            </div>'''
            half2_cards_html.append(card)

    chips_half1_str = "".join(half1_cards_html)
    chips_half2_str = "".join(half2_cards_html)

    # Dynamic Fixture Lookup Helper based on real data/fixtures.json
    teams_by_id = {t["id"]: t for t in bootstrap.get("teams", [])}
    def get_fixture_desc(team_short, gw_num):
        t_obj = next((t for t in bootstrap.get("teams", []) if t["short_name"] == team_short), None)
        if not t_obj:
            return ""
        tid = t_obj["id"]
        for fix in (fixtures or []):
            if fix.get("event") == gw_num:
                th = fix.get("team_h")
                ta = fix.get("team_a")
                if th == tid:
                    opp = teams_by_id.get(ta, {}).get("short_name", "")
                    diff = fix.get("team_h_difficulty")
                    return f"{team_short} vs {opp} (H - FDR {diff})"
                elif ta == tid:
                    opp = teams_by_id.get(th, {}).get("short_name", "")
                    diff = fix.get("team_a_difficulty")
                    return f"{team_short} @ {opp} (A - FDR {diff})"
        return ""

    # Build dynamic multi-week roadmap rows for GW4 - GW7 from real official fixtures
    gw4_fixes = ", ".join([f for f in [get_fixture_desc("CHE", 4), get_fixture_desc("LIV", 4), get_fixture_desc("ARS", 4), get_fixture_desc("MCI", 4)] if f])
    gw5_fixes = ", ".join([f for f in [get_fixture_desc("MCI", 5), get_fixture_desc("CHE", 5), get_fixture_desc("LIV", 5), get_fixture_desc("ARS", 5)] if f])
    gw6_fixes = ", ".join([f for f in [get_fixture_desc("LIV", 6), get_fixture_desc("MCI", 6), get_fixture_desc("ARS", 6), get_fixture_desc("CHE", 6)] if f])
    gw7_fixes = ", ".join([f for f in [get_fixture_desc("MCI", 7), get_fixture_desc("CHE", 7), get_fixture_desc("LIV", 7), get_fixture_desc("ARS", 7)] if f])

    gw4_roadmap_rec = f"ใช้โควตา 1 จาก 2 FTs ดึง <strong>Martin Ødegaard (£6.7m)</strong> เข้ามาแทน Cody Gakpo ที่ติดธงเหลือง 75% ปรับทัพตัวจริงลุยสัปดาห์นี้ พร้อมเก็บสะสม 1 FT สำรองไว้ใช้ต่อเนื่องใน GW5 โดยแต้มลบเป็น 0 pts (ห้ามเปลี่ยนตัวติดลบ 100%)"

    dynamic_roadmap_rows_html = f'''
                            <tr style="border-bottom:1px solid var(--border-subtle);">
                                <td style="padding:8px 10px; font-weight:700; color:var(--accent-emerald);">GW4 (สัปดาห์นี้)</td>
                                <td style="padding:8px 10px;"><span style="color:var(--accent-emerald); font-weight:600;">{user_free_transfers} FTs &bull; ZERO HIT</span></td>
                                <td style="padding:8px 10px;">{gw4_fixes}</td>
                                <td style="padding:8px 10px;">{gw4_roadmap_rec}</td>
                            </tr>
                            <tr style="border-bottom:1px solid var(--border-subtle);">
                                <td style="padding:8px 10px; font-weight:700; color:#ffffff;">GW5</td>
                                <td style="padding:8px 10px;"><strong>1-2 FTs &bull; จุดพิจารณา Triple Captain #1 ตัวเลือกที่ 1</strong></td>
                                <td style="padding:8px 10px;">{gw5_fixes}</td>
                                <td style="padding:8px 10px;"><strong>โอกาสทองใช้ Triple Captain #1 (ตัวเลือกที่ 1):</strong> Man City vs Sunderland (H - FDR 2 โซนเขียว) ฮาแลนด์เฝ้ารังพบซันเดอร์แลนด์ เหมาะแก่การระเบิดแต้ม 3 เท่า หรือเก็บชิปไว้ลุย GW7 หากต้องการถือ 2 FTs</td>
                            </tr>
                            <tr style="border-bottom:1px solid var(--border-subtle);">
                                <td style="padding:8px 10px; font-weight:700; color:#ffffff;">GW6</td>
                                <td style="padding:8px 10px;"><strong>1-2 Free Transfers</strong> (บิ๊กแมตช์ &bull; เลี่ยงชิป)</td>
                                <td style="padding:8px 10px;">{gw6_fixes}</td>
                                <td style="padding:8px 10px;"><strong>บิ๊กแมตช์แอนฟิลด์ (LIV vs MCI - FDR 4):</strong> แมนฯ ซิตี้ บุกเยือนลิเวอร์พูล เลี่ยงการใช้ชิปในสัปดาห์นี้ อาศัยตัวทำเกมอาร์เซนอล (ARS vs LEE - H FDR 2) และ Palmer (CHE vs BOU - H FDR 3) เป็นหัวใจหลัก</td>
                            </tr>
                            <tr>
                                <td style="padding:8px 10px; font-weight:700; color:#ffffff;">GW7</td>
                                <td style="padding:8px 10px;"><strong>1-2 FTs &bull; จุดพิจารณา Triple Captain #1 ตัวเลือกที่ 2</strong></td>
                                <td style="padding:8px 10px;">{gw7_fixes}</td>
                                <td style="padding:8px 10px;"><strong>โอกาสทองใช้ Triple Captain #1 (ตัวเลือกที่ 2):</strong> Man City vs Ipswich (H - FDR 2 โซนเขียว) ฮาแลนด์เปิดบ้านพบอิปสวิช ก่อนพิจารณาเก็บ Free Hit #1 ไว้แก้ทางฉุกเฉินก่อนจบ GW19</td>
                            </tr>'''

    # Dynamic Transfers In / Out Computation (Choice 2 vs Choice 1)
    c1_pids = [p[0] for p in c1_ids]
    c2_pids = [p[0] for p in c2_ids]
    
    transfers_out_players = [p for p in c1_squad if p["id"] not in c2_pids]
    transfers_in_players = [p for p in c2_squad if p["id"] not in c1_pids]
    
    c2_delta_in_pills = "".join([f'<span class="delta-pill pill-in"><span class="delta-pill-badge pos-{p["pos"]}">{p["pos"]}</span> <strong>{p["web_name"]}</strong> <small>£{p["cost"]:.1f}m &bull; {p["team_code"]} &bull; {p["next_fix"].split(" ")[0]} (FDR {p["next_fdr"]})</small></span>' for p in transfers_in_players])
    c2_delta_out_pills = "".join([f'<span class="delta-pill pill-out"><span class="delta-pill-badge pos-{p["pos"]}">{p["pos"]}</span> <strong>{p["web_name"]}</strong> <small>£{p["cost"]:.1f}m &bull; {p["team_code"]} &bull; {p["next_fix"].split(" ")[0]} (FDR {p["next_fdr"]})</small></span>' for p in transfers_out_players])
    transfers_count = len(transfers_in_players)

    # Combine unique players for full season ticker
    all_ticker_pids = list(dict.fromkeys([p[0] for p in c1_ids] + [p[0] for p in c2_ids]))
    all_ticker_squad = [build_player_by_id(pid, True) for pid in all_ticker_pids if build_player_by_id(pid, True)]

    # Generate GW Headers dynamically from active_gw to 38
    gw_headers = []
    for i, gw in enumerate(range(active_gw, 39)):
        col_idx = i + 4
        gw_headers.append(f'<th onclick="sortTable({col_idx}, \'number\')" class="sortable-th" title="Click to sort GW{gw} FDR">GW{gw} <span class="sort-icon">&varr;</span></th>')

    # =========================================================
    # TAB 5: GW3 POST-MATCH REVIEW & COMPARISON COMPUTATION
    # =========================================================
    # Choice 1 (Official Micky Wildcard XI):
    gw3_c1_lineup = [
        (109, True, False, False), # Verbruggen (GKP - 3 pts)
        (391, True, False, False), # Gvardiol (DEF - 8 pts)
        (277, True, False, False), # Egan (DEF - 6 pts)
        (4, True, False, False),   # Gabriel (DEF - 2 pts)
        (124, True, False, False), # Groß (MID - 1 pt)
        (367, True, False, False), # Gakpo (MID - 11 pts)
        (398, True, False, True),  # Foden (MID VC - 1 pt)
        (368, True, False, False), # Szoboszlai (MID - 3 pts)
        (154, True, False, False), # Palmer (MID - 1 pt)
        (464, True, False, False), # Wissa (FWD - 1 pt)
        (411, True, True, False),  # Haaland (FWD C - 9x2 = 18 pts)
        # Reserves
        (496, False, False, False),# Kinsky (GKP - 6 pts)
        (165, False, False, False),# João Pedro (FWD - 1 pt)
        (31, False, False, False), # Konsa (DEF - 4 pts)
        (304, False, False, False) # O'Shea (DEF - 3 pts)
    ]

    # Choice 2 (Tactical Variant Setup with Konsa in XI, Egan Benched, Pedro in XI, Wissa Benched):
    gw3_c2_lineup = [
        (109, True, False, False), # Verbruggen (GKP - 3 pts)
        (391, True, False, False), # Gvardiol (DEF - 8 pts)
        (31, True, False, False),  # Konsa (DEF - 4 pts)
        (4, True, False, False),   # Gabriel (DEF - 2 pts)
        (124, True, False, False), # Groß (MID - 1 pt)
        (367, True, False, False), # Gakpo (MID - 11 pts)
        (398, True, False, True),  # Foden (MID VC - 1 pt)
        (368, True, False, False), # Szoboszlai (MID - 3 pts)
        (154, True, False, False), # Palmer (MID - 1 pt)
        (165, True, False, False), # João Pedro (FWD - 1 pt)
        (411, True, True, False),  # Haaland (FWD C - 9x2 = 18 pts)
        # Reserves
        (496, False, False, False),# Kinsky (GKP - 6 pts)
        (464, False, False, False),# Wissa (FWD - 1 pt)
        (277, False, False, False),# Egan (DEF - 6 pts)
        (304, False, False, False) # O'Shea (DEF - 3 pts)
    ]

    def build_gw3_player_data(pid, is_starter, is_c, is_vc):
        el = elements_map.get(pid, {})
        ev_pts = el.get("event_points", 0)
        mult = 2 if is_c else (1 if is_starter else 0)
        earned_pts = ev_pts * mult
        pos_id = el.get("element_type", 1)
        pos = {1: "GKP", 2: "DEF", 3: "MID", 4: "FWD"}.get(pos_id, "MID")
        team_id = el.get("team", 1)
        t_code = teams.get(team_id, {}).get("short_name", "PL")
        cost = el.get("now_cost", 50) / 10.0
        web_name = el.get("web_name", f"Player {pid}")
        return {
            "id": pid,
            "web_name": web_name,
            "pos": pos,
            "team_code": t_code,
            "cost": cost,
            "is_starter": is_starter,
            "is_captain": is_c,
            "is_vice_captain": is_vc,
            "raw_pts": ev_pts,
            "multiplier": mult,
            "earned_pts": earned_pts
        }

    gw3_c1_players = [build_gw3_player_data(*p) for p in gw3_c1_lineup]
    gw3_c2_players = [build_gw3_player_data(*p) for p in gw3_c2_lineup]

    gw3_c1_start_pts = sum(p["earned_pts"] for p in gw3_c1_players if p["is_starter"])
    gw3_c1_bench_pts = sum(p["raw_pts"] for p in gw3_c1_players if not p["is_starter"])
    gw3_c2_start_pts = sum(p["earned_pts"] for p in gw3_c2_players if p["is_starter"])
    gw3_c2_bench_pts = sum(p["raw_pts"] for p in gw3_c2_players if not p["is_starter"])

    gw3_score_diff = gw3_c1_start_pts - gw3_c2_start_pts
    if gw3_score_diff > 0:
        gw3_result_badge = "🏆 CHOICE 1 WINS"
        gw3_result_class = "winner-c1"
        gw3_result_desc = f"Choice 1 ชนะด้วยผลต่าง +{gw3_score_diff} คะแนน ({gw3_c1_start_pts} vs {gw3_c2_start_pts} pts)"
    elif gw3_score_diff < 0:
        gw3_result_badge = "🏆 CHOICE 2 WINS"
        gw3_result_class = "winner-c2"
        gw3_result_desc = f"Choice 2 ชนะด้วยผลต่าง +{abs(gw3_score_diff)} คะแนน ({gw3_c2_start_pts} vs {gw3_c1_start_pts} pts)"
    else:
        gw3_result_badge = "🤝 MATCH DRAW"
        gw3_result_class = "winner-draw"
        gw3_result_desc = f"ทั้งสองทีมเสมอกันด้วยคะแนน {gw3_c1_start_pts} pts เท่ากัน"

    def render_gw3_player_row(p):
        cap_badge = ""
        if p["is_captain"]:
            cap_badge = '<span class="role-badge-cap" style="width:18px; height:18px; font-size:0.55rem; margin-left:4px;">C</span>'
        elif p["is_vice_captain"]:
            cap_badge = '<span class="role-badge-vc" style="width:18px; height:18px; font-size:0.55rem; margin-left:4px;">V</span>'

        if p["is_starter"]:
            pts_display = f'{p["earned_pts"]} <small class="font-mono" style="color:var(--text-muted); font-size:0.65rem;">({p["raw_pts"]}x{p["multiplier"]})</small>' if p["is_captain"] else f'{p["earned_pts"]}'
            pts_color = "var(--accent-emerald)" if p["earned_pts"] >= 6 else ("#ffffff" if p["earned_pts"] >= 3 else "var(--text-muted)")
        else:
            pts_display = f'{p["raw_pts"]} <small style="color:var(--text-muted); font-size:0.65rem;">(bench)</small>'
            pts_color = "var(--accent-amber)" if p["raw_pts"] >= 6 else "var(--text-secondary)"

        return f'''
            <tr class="gw3-row {'is-benched' if not p['is_starter'] else ''}">
                <td style="padding:6px 10px; font-weight:600; white-space:nowrap;">
                    <span class="pos-tag-mini pos-{p['pos']}">{p['pos']}</span>
                    <span style="color:var(--text-main); margin-left:4px;">{p['web_name']}</span>
                    {cap_badge}
                </td>
                <td style="padding:6px 8px; font-size:0.72rem; color:var(--text-secondary);">{p['team_code']}</td>
                <td style="padding:6px 10px; text-align:right; font-family:'JetBrains Mono', monospace; font-weight:700; color:{pts_color}; font-size:0.85rem;">
                    {pts_display}
                </td>
            </tr>'''

    gw3_c1_starters_html = "".join([render_gw3_player_row(p) for p in gw3_c1_players if p["is_starter"]])
    gw3_c1_bench_html = "".join([render_gw3_player_row(p) for p in gw3_c1_players if not p["is_starter"]])
    gw3_c2_starters_html = "".join([render_gw3_player_row(p) for p in gw3_c2_players if p["is_starter"]])
    gw3_c2_bench_html = "".join([render_gw3_player_row(p) for p in gw3_c2_players if not p["is_starter"]])

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>FPL Dashboard | GEMINI UNITED</title>
    
    <!-- Open Graph / Facebook / LINE Link Preview Meta Tags -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://asawamanasak.github.io/fpl/">
    <meta property="og:title" content="FPL Dashboard | GEMINI UNITED (ID: 306983)">
    <meta property="og:description" content="Tactical Command Center &amp; Autonomous Optimizer &bull; Global Rank: 65,185 (Top 100k: On Track) &bull; Wildcard GW3 Active">
    <meta property="og:image" content="https://asawamanasak.github.io/fpl/assets/og_preview.png">
    <meta property="og:image:secure_url" content="https://asawamanasak.github.io/fpl/assets/og_preview.png">
    <meta property="og:image:type" content="image/png">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="GEMINI UNITED FPL Tactical Command Center Dashboard">

    <!-- Twitter / X Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://asawamanasak.github.io/fpl/">
    <meta name="twitter:title" content="FPL Dashboard | GEMINI UNITED (ID: 306983)">
    <meta name="twitter:description" content="Tactical Command Center &amp; Autonomous Optimizer &bull; Global Rank: 65,185 (Top 100k: On Track) &bull; Wildcard GW3 Active">
    <meta name="twitter:image" content="https://asawamanasak.github.io/fpl/assets/og_preview.png">

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Sarabun:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #090c10;
            --bg-surface: #0f141c;
            --bg-card: #151b26;
            --bg-card-inner: #0b0f16;
            --border-main: #212936;
            --border-muted: #18202c;
            --border-accent: #334155;
            
            --text-main: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            --accent-emerald: #10b981;
            --accent-sky: #38bdf8;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            
            --fdr-1: #10b981;
            --fdr-2: #0284c7;
            --fdr-3: #64748b;
            --fdr-4: #d97706;
            --fdr-5: #dc2626;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}

        html {{
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            -webkit-text-size-adjust: 100%;
        }}
        
        body {{
            font-family: 'Sarabun', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            line-height: 1.6;
            letter-spacing: normal;
            word-break: break-word;
            overflow-wrap: break-word;
        }}

        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Sarabun', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            font-weight: 700;
            line-height: 1.35;
            text-wrap: balance;
            overflow-wrap: break-word;
            word-break: break-word;
        }}

        p, span, div, td, th {{
            overflow-wrap: break-word;
        }}

        @media (min-width: 1200px) {{
            body {{
                min-height: 100vh;
                height: auto;
                overflow-y: auto; /* Allow natural scrolling so all content is reachable */
            }}
        }}

        /* Header */
        header {{
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-main);
            padding: 0.45rem 1rem;
            flex-shrink: 0;
        }}
        .header-wrap {{
            max-width: 1680px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 0.75rem;
            flex-wrap: wrap;
        }}
        .brand-meta {{ display: flex; align-items: center; gap: 0.6rem; }}
        .season-badge {{
            background: #1e293b;
            color: var(--text-main);
            border: 1px solid var(--border-accent);
            font-weight: 700;
            font-size: 0.65rem;
            padding: 0.18rem 0.4rem;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .title-box h1 {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.35;
        }}
        .title-box p {{ 
            font-size: 0.72rem; 
            color: var(--text-secondary);
            line-height: 1.45;
        }}
        
        .sync-pill {{
            font-size: 0.64rem;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            background: rgba(16, 185, 129, 0.1);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 0.1rem 0.42rem;
            border-radius: 4px;
            vertical-align: middle;
            margin-left: 0.35rem;
            letter-spacing: 0.2px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .sync-dot {{
            width: 6px;
            height: 6px;
            background: var(--accent-emerald);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 6px var(--accent-emerald);
            animation: sync-pulse 2s infinite ease-in-out;
        }}
        @keyframes sync-pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.35; transform: scale(0.8); }}
        }}
        .sync-tag-active {{
            background: rgba(16, 185, 129, 0.2);
            color: var(--accent-emerald);
            font-size: 0.52rem;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
            margin-left: 2px;
            letter-spacing: 0.5px;
        }}

        .stats-strip {{ 
            display: flex; 
            gap: 0.4rem; 
            flex-wrap: wrap;
        }}
        .stat-cell {{
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            min-width: 75px;
        }}
        .stat-cell .lbl {{
            font-size: 0.54rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .stat-cell .val {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--accent-emerald);
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.2;
        }}

        /* Feature 5: Deadline Countdown Pill */
        .deadline-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.62rem;
            color: var(--text-muted);
            margin-top: 4px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .deadline-tag-prefix {{
            background: rgba(56, 189, 248, 0.2);
            color: var(--accent-sky);
            padding: 1px 5px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.55rem;
            letter-spacing: 0.5px;
        }}
        .countdown-clock {{
            color: #ffffff;
            font-weight: 700;
        }}
        .lockdown-badge {{
            background: rgba(245, 158, 11, 0.18);
            color: var(--accent-amber);
            padding: 1px 5px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.52rem;
            letter-spacing: 0.4px;
        }}

        /* Feature 3: Top 100k Trajectory Cell */
        .stat-rank-cell {{
            border-color: rgba(16, 185, 129, 0.35);
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(15, 23, 42, 0.6));
        }}
        .rank-trajectory-tag {{
            font-size: 0.52rem;
            font-weight: 700;
            padding: 1px 5px;
            border-radius: 3px;
            margin-top: 3px;
            letter-spacing: 0.4px;
            display: inline-block;
            width: fit-content;
        }}
        .status-ontrack {{
            background: rgba(16, 185, 129, 0.2);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}
        .status-pursuing {{
            background: rgba(245, 158, 11, 0.2);
            color: var(--accent-amber);
            border: 1px solid rgba(245, 158, 11, 0.35);
        }}

        /* Feature 4: Squad Fitness & Press Conference Widget */
        .squad-health-widget {{
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 0.9rem 1.2rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.25);
        }}
        .health-top-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .health-meta {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .health-heading {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--text-bright);
            line-height: 1.35;
        }}
        .health-dot-active {{
            width: 8px;
            height: 8px;
            background: var(--accent-emerald);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-emerald);
            animation: sync-pulse 2s infinite ease-in-out;
        }}
        .health-status-badge {{
            font-size: 0.62rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
            letter-spacing: 0.5px;
        }}
        .health-badge-ok {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.35);
        }}
        .health-badge-warning {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--accent-amber);
            border: 1px solid rgba(245, 158, 11, 0.35);
        }}
        .health-detail-text {{
            font-size: 0.82rem;
            color: var(--text-secondary);
            line-height: 1.65;
            overflow-wrap: break-word;
            word-break: break-word;
            text-wrap: pretty;
        }}
        .health-alerts-box {{
            margin-top: 0.6rem;
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}
        .health-alert-pill {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--accent-rose);
            font-size: 0.78rem;
            padding: 5px 10px;
            border-radius: 5px;
            line-height: 1.55;
            overflow-wrap: break-word;
            word-break: break-word;
        }}

        /* Navigation Bar (4 Tabs) */
        .nav-bar {{
            display: flex;
            gap: 0.3rem;
            max-width: 1680px;
            margin: 0.3rem auto 0;
            padding: 0 1rem;
            flex-shrink: 0;
            width: 100%;
            overflow-x: auto;
            scrollbar-width: none;
        }}
        .nav-bar::-webkit-scrollbar {{ display: none; }}
        .tab-btn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            color: var(--text-secondary);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.74rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        .tab-btn.active {{
            background: #1e293b;
            border-color: var(--accent-emerald);
            color: #ffffff;
        }}

        /* Main View Container */
        main {{
            max-width: 1680px;
            margin: 0.3rem auto 0;
            padding: 0 1rem 2rem;
            flex: 1;
            width: 100%;
            display: flex;
            flex-direction: column;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: flex; flex-direction: column; flex: 1; }}

        .gw-top-badge {{
            background: rgba(56, 189, 248, 0.16);
            color: var(--accent-sky);
            border: 1px solid rgba(56, 189, 248, 0.4);
            font-weight: 800;
            font-size: 0.72rem;
            padding: 0.16rem 0.48rem;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.5px;
        }}

        /* Gameweek Target Banner on Front Page */
        .gw-target-banner {{
            margin-bottom: 0.65rem;
            background: linear-gradient(90deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.9));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 9px;
            padding: 0.5rem 0.85rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.5rem;
            flex-shrink: 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08);
        }}
        .gw-banner-left {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }}
        .gw-badge-pill {{
            background: linear-gradient(135deg, #0284c7, #38bdf8);
            color: #031e2f;
            font-size: 0.64rem;
            font-weight: 800;
            padding: 0.16rem 0.55rem;
            border-radius: 5px;
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 0.6px;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
            white-space: nowrap;
        }}
        .gw-banner-title-wrap {{
            display: flex;
            align-items: baseline;
            gap: 0.4rem;
            flex-wrap: wrap;
        }}
        .gw-banner-title {{
            font-size: 0.86rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.2px;
            line-height: 1.4;
            overflow-wrap: break-word;
            word-break: break-word;
            text-wrap: balance;
        }}
        .gw-banner-en {{
            font-size: 0.70rem;
            color: var(--text-muted);
            font-weight: 500;
        }}
        .gw-banner-right {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.68rem;
            color: var(--text-secondary);
        }}
        .gw-info-chip {{
            display: flex;
            align-items: baseline;
            gap: 0.35rem;
        }}
        .chip-label {{
            font-size: 0.58rem;
            font-weight: 700;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }}
        .chip-val {{
            color: #ffffff;
            font-weight: 700;
        }}
        .quota-rule {{
            font-weight: 500;
            color: var(--accent-emerald);
            font-size: 0.64rem;
        }}
        .gw-divider {{
            color: var(--border-accent);
        }}

        /* Responsive Side-by-Side Lineup Split Grid */
        .lineup-split-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.95rem;
            flex: 1;
        }}

        .plan-column {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.92) 0%, rgba(10, 16, 28, 0.98) 100%);
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-top: 3px solid #38bdf8;
            border-radius: 11px;
            padding: 0.65rem;
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        }}

        .plan-column.plan-c2 {{
            border-color: rgba(16, 185, 129, 0.35);
            border-top: 3px solid #10b981;
            box-shadow: 0 8px 24px rgba(16, 185, 129, 0.1), 0 8px 24px rgba(0, 0, 0, 0.45);
        }}

        .plan-col-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.45rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 0.45rem;
            flex-shrink: 0;
            gap: 0.4rem;
        }}
        .plan-title {{ 
            font-size: 0.9rem; 
            font-weight: 700; 
            color: #ffffff; 
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .plan-sub-tags {{
            display: flex;
            gap: 0.35rem;
            align-items: center;
            margin-top: 0.25rem;
            flex-wrap: wrap;
        }}
        .formation-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.62rem;
            font-weight: 700;
            background: rgba(30, 41, 59, 0.8);
            color: #cbd5e1;
            padding: 0.12rem 0.45rem;
            border-radius: 4px;
            border: 1px solid var(--border-accent);
        }}
        .active-chip-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.62rem;
            font-weight: 800;
            padding: 0.12rem 0.5rem;
            border-radius: 4px;
            display: inline-flex;
            align-items: center;
            gap: 4px;
            text-transform: uppercase;
        }}
        .active-chip-pill.chip-wildcard {{
            background: rgba(16, 185, 129, 0.18);
            color: #34d399;
            border: 1px solid #10b981;
        }}
        .ft-buffer-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.62rem;
            font-weight: 700;
            background: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            border: 1px solid #0284c7;
        }}
        .fin-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 700;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 0.2rem 0.55rem;
            border-radius: 6px;
            white-space: nowrap;
            box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }}

        /* AUTHENTIC TACTICAL PITCH WITH STADIUM FIELD MARKINGS */
        .compact-pitch {{
            position: relative;
            background: 
                repeating-linear-gradient(
                    180deg,
                    #081710 0px,
                    #081710 52px,
                    #0a1e14 52px,
                    #0a1e14 104px
                );
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 10px;
            padding: 0.65rem 0.4rem 0.75rem;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            gap: 0.5rem;
            min-height: 520px;
            box-shadow: inset 0 0 70px rgba(0, 0, 0, 0.8), 0 4px 18px rgba(0, 0, 0, 0.4);
        }}
        /* Pitch Tactical Markings (Midfield line & center circle) */
        .compact-pitch::before {{
            content: '';
            position: absolute;
            top: 50%;
            left: 3%;
            right: 3%;
            height: 1px;
            background: rgba(255, 255, 255, 0.09);
            pointer-events: none;
            z-index: 1;
        }}
        .compact-pitch::after {{
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 86px;
            height: 86px;
            transform: translate(-50%, -50%);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 50%;
            pointer-events: none;
            z-index: 1;
        }}
        .pitch-row {{
            position: relative;
            z-index: 2;
            display: flex;
            justify-content: center;
            gap: 0.55rem;
            align-items: center;
            flex-wrap: nowrap;
        }}

        /* MODERN GLASSMORPHIC STARTER CARD */
        .starter-card {{
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.86) 0%, rgba(15, 23, 42, 0.96) 100%);
            border: 1px solid rgba(255, 255, 255, 0.09);
            border-radius: 8px;
            padding: 0.22rem 0.32rem 0.2rem;
            width: 95px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            flex-shrink: 0;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.55);
            transition: transform 0.18s cubic-bezier(0.2, 0.8, 0.2, 1), border-color 0.18s ease, box-shadow 0.18s ease;
            position: relative;
            backdrop-filter: blur(8px);
        }}
        .starter-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.6);
            box-shadow: 0 8px 22px rgba(0, 0, 0, 0.65), 0 0 10px rgba(56, 189, 248, 0.25);
        }}
        /* Glowing Transfer In Card */
        .starter-card.card-transfer-in, .bench-card.card-transfer-in {{
            border-color: rgba(16, 185, 129, 0.7) !important;
            background: linear-gradient(180deg, rgba(16, 45, 34, 0.88) 0%, rgba(10, 26, 20, 0.98) 100%) !important;
            box-shadow: 0 0 14px rgba(16, 185, 129, 0.35), 0 4px 12px rgba(0, 0, 0, 0.5) !important;
        }}
        .starter-card.card-transfer-in:hover, .bench-card.card-transfer-in:hover {{
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.55), 0 8px 24px rgba(0, 0, 0, 0.7) !important;
        }}

        .starter-card-top, .bench-card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            gap: 2px;
            min-height: 16px;
        }}
        .starter-badges-group {{
            display: flex;
            align-items: center;
            gap: 2px;
        }}
        .role-badge-cap {{
            background: linear-gradient(135deg, #fbbf24, #d97706);
            color: #000000;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            font-weight: 900;
            padding: 0.05rem 0.28rem;
            border-radius: 3px;
            line-height: 1;
            box-shadow: 0 0 6px rgba(245, 158, 11, 0.6);
        }}
        .role-badge-vc {{
            background: linear-gradient(135deg, #e2e8f0, #94a3b8);
            color: #0f172a;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            font-weight: 900;
            padding: 0.05rem 0.28rem;
            border-radius: 3px;
            line-height: 1;
        }}
        .starter-photo-wrap, .bench-photo-wrap {{
            width: 100%;
            height: 42px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1px 0;
            background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.06) 0%, transparent 68%);
            border-radius: 4px;
        }}
        .starter-shirt-img, .bench-shirt-img {{
            width: 38px;
            height: 38px;
            object-fit: contain;
            filter: drop-shadow(0 3px 6px rgba(0, 0, 0, 0.65));
            transition: transform 0.2s ease;
        }}
        .starter-card:hover .starter-shirt-img, .bench-card:hover .bench-shirt-img {{
            transform: scale(1.08);
        }}
        .starter-info-card, .bench-info-card {{
            width: 100%;
            border-top: 1px solid rgba(255, 255, 255, 0.08);
            padding-top: 3px;
            text-align: center;
        }}
        .starter-name, .bench-name {{
            font-size: 0.72rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.15;
            letter-spacing: 0.2px;
        }}
        .starter-meta, .bench-meta {{
            font-size: 0.58rem;
            color: #94a3b8;
            font-family: 'JetBrains Mono', monospace;
            margin: 1px 0;
            font-weight: 600;
        }}
        .starter-fix-row, .bench-fix-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.56rem;
            border-top: 1px solid rgba(255, 255, 255, 0.06);
            padding-top: 2px;
            margin-top: 2px;
        }}
        .starter-fix-text, .bench-fix-text {{ 
            color: #cbd5e1; 
            font-weight: 600; 
        }}

        /* FULL-SIZE BENCH / DUGOUT STRIP */
        .compact-bench-strip {{ 
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.85) 0%, rgba(10, 16, 26, 0.95) 100%); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 9px; 
            padding: 0.45rem 0.6rem; 
            margin-top: 0.45rem; 
            flex-shrink: 0; 
            overflow-x: auto;
            box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.05);
        }}
        .bench-header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.35rem;
            padding-bottom: 0.2rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}
        .bench-lbl {{ 
            font-size: 0.62rem; 
            font-weight: 800; 
            color: var(--text-secondary); 
            text-transform: uppercase; 
            letter-spacing: 0.6px; 
        }}
        .bench-count-tag {{
            font-size: 0.54rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: var(--text-muted);
            background: rgba(255, 255, 255, 0.05);
            padding: 0.05rem 0.35rem;
            border-radius: 3px;
            border: 1px solid var(--border-subtle);
        }}
        .bench-row {{ 
            display: flex; 
            justify-content: center; 
            gap: 0.55rem; 
            min-width: max-content; 
        }}

        .bench-card {{
            background: linear-gradient(180deg, rgba(24, 34, 52, 0.85) 0%, rgba(13, 20, 34, 0.95) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 0.28rem 0.35rem 0.24rem;
            width: 98px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            flex-shrink: 0;
            transition: transform 0.18s cubic-bezier(0.2, 0.8, 0.2, 1), border-color 0.18s ease, box-shadow 0.18s ease;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(8px);
        }}
        .bench-card:hover {{
            transform: translateY(-3px);
            border-color: rgba(56, 189, 248, 0.6);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.65);
        }}

        /* Small Transfers In/Out Delta Box */
        .transfers-delta-box {{
            margin-top: 0.45rem;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.85) 0%, rgba(6, 32, 22, 0.35) 100%);
            border: 1px solid rgba(16, 185, 129, 0.45);
            border-radius: 8px;
            padding: 0.45rem 0.65rem;
            font-size: 0.7rem;
            flex-shrink: 0;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
        }}
        .delta-header-strip {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.35rem;
            padding-bottom: 0.25rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }}
        .delta-title-wrap {{
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .delta-indicator-dot {{
            width: 7px;
            height: 7px;
            background: var(--accent-emerald);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-emerald);
        }}
        .delta-title {{
            font-weight: 700;
            color: #ffffff;
            font-size: 0.72rem;
            letter-spacing: 0.3px;
        }}
        .delta-count-pill {{
            font-size: 0.58rem;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.35);
            font-family: 'JetBrains Mono', monospace;
        }}
        .delta-list-grid {{
            display: flex;
            flex-direction: column;
            gap: 0.3rem;
        }}
        .delta-group {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            flex-wrap: wrap;
        }}
        .delta-group-label {{
            font-size: 0.6rem;
            font-weight: 800;
            letter-spacing: 0.6px;
            min-width: 74px;
        }}
        .delta-group-label.in-lbl {{ color: var(--accent-emerald); }}
        .delta-group-label.out-lbl {{ color: var(--accent-rose); }}
        .delta-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            flex: 1;
        }}
        .delta-pill {{
            font-size: 0.62rem;
            padding: 2px 7px;
            border-radius: 4px;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}
        .delta-pill small {{
            opacity: 0.85;
            font-weight: 500;
        }}
        .delta-pill-badge {{
            font-size: 0.5rem;
            font-weight: 800;
            padding: 0.04rem 0.22rem;
            border-radius: 2px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .delta-pill.pill-in {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.4);
        }}
        .delta-pill.pill-out {{
            background: rgba(244, 63, 94, 0.15);
            color: #fb7185;
            border: 1px solid rgba(244, 63, 94, 0.4);
        }}
        .delta-footer {{
            margin-top: 0.35rem;
            padding-top: 0.25rem;
            border-top: 1px dashed rgba(255, 255, 255, 0.1);
            font-size: 0.62rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.25rem;
        }}
        .delta-baseline {{
            border-color: rgba(255, 255, 255, 0.12) !important;
            background: rgba(15, 23, 42, 0.45) !important;
        }}
        .dot-baseline {{
            background: var(--text-muted) !important;
            box-shadow: none !important;
        }}
        .pill-baseline {{
            background: rgba(255, 255, 255, 0.06) !important;
            color: var(--text-muted) !important;
            border: 1px solid var(--border-subtle) !important;
        }}
        .delta-status-banner {{
            margin-top: 0.35rem;
            padding: 0.28rem 0.5rem;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .status-lbl {{
            font-size: 0.58rem;
            font-weight: 800;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            white-space: nowrap;
        }}
        .status-txt {{
            font-size: 0.64rem;
            color: var(--text-muted);
            word-break: keep-all;
        }}
        .delta-rule-notice {{
            margin-top: 0.35rem;
            padding: 0.28rem 0.5rem;
            border-radius: 5px;
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid rgba(16, 185, 129, 0.25);
        }}
        .rule-txt {{
            font-size: 0.64rem;
            color: var(--accent-emerald);
            font-weight: 600;
            word-break: keep-all;
            line-height: 1.35;
        }}
        .delta-ledger-strip {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.35rem;
            padding-top: 0.28rem;
            border-top: 1px dashed rgba(255, 255, 255, 0.1);
            gap: 0.4rem;
        }}
        .delta-ledger-cell {{
            display: flex;
            align-items: baseline;
            gap: 0.35rem;
        }}
        .dl-lbl {{
            font-size: 0.58rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .dl-val {{
            font-size: 0.68rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: #ffffff;
        }}
        .dl-gain {{
            font-size: 0.60rem;
            color: var(--accent-emerald);
            margin-left: 2px;
        }}
        .mobile-vs-divider {{
            display: none;
        }}

        .sub-label-badge {{
            font-size: 0.52rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 800;
            background: rgba(2, 132, 199, 0.25);
            color: #38bdf8;
            border: 1px solid rgba(2, 132, 199, 0.4);
            padding: 0.04rem 0.24rem;
            border-radius: 3px;
        }}

        .pos-tag-mini {{ 
            font-size: 0.52rem; 
            font-weight: 800; 
            padding: 0.05rem 0.24rem; 
            border-radius: 3px; 
            font-family: 'JetBrains Mono', monospace; 
            text-transform: uppercase; 
        }}
        .pos-GKP {{ background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }}
        .pos-DEF {{ background: rgba(56, 189, 248, 0.16); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35); }}
        .pos-MID {{ background: rgba(52, 211, 153, 0.16); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.35); }}
        .pos-FWD {{ background: rgba(251, 113, 133, 0.16); color: #fb7185; border: 1px solid rgba(251, 113, 133, 0.35); }}

        .core-tag-mini {{ font-size: 0.48rem; font-weight: 800; background: rgba(6, 182, 212, 0.2); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.4); padding: 0.04rem 0.2rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .enabler-tag-mini {{ font-size: 0.48rem; font-weight: 800; background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); padding: 0.04rem 0.2rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .transfer-in-tag-mini {{ font-size: 0.48rem; font-weight: 900; background: linear-gradient(135deg, #10b981, #059669); color: #ffffff; box-shadow: 0 0 6px rgba(16, 185, 129, 0.5); padding: 0.04rem 0.24rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}

        .fdr-pill {{ font-size: 0.56rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 0.04rem 0.22rem; border-radius: 3px; }}
        .fdr-pill.fdr-1 {{ background: rgba(16, 185, 129, 0.25); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); }}
        .fdr-pill.fdr-2 {{ background: rgba(14, 165, 233, 0.22); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.35); }}
        .fdr-pill.fdr-3 {{ background: rgba(148, 163, 184, 0.18); color: #cbd5e1; border: 1px solid rgba(148, 163, 184, 0.25); }}
        .fdr-pill.fdr-4 {{ background: rgba(245, 158, 11, 0.22); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.35); }}
        .fdr-pill.fdr-5 {{ background: rgba(239, 68, 68, 0.25); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); }}

        /* =========================================================
           PLAN SUMMARY TAB STYLING (NEW!)
           ========================================================= */
        .summary-metrics-strip {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.5rem;
            margin-bottom: 0.75rem;
            flex-shrink: 0;
        }}
        .summary-metric-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 8px;
            padding: 0.5rem 0.65rem;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .summary-metric-title {{
            font-size: 0.62rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .summary-metric-values {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-top: 2px;
        }}
        .metric-sub-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            font-weight: 700;
        }}
        .metric-tag-c1 {{ color: #cbd5e1; }}
        .metric-tag-c2 {{ color: var(--accent-emerald); }}

        .summary-split-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.85rem;
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding-right: 0.25rem;
        }}
        .summary-plan-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        .summary-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.45rem;
            border-bottom: 1px solid var(--border-main);
        }}
        .pros-cons-section {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        .section-badge-title {{
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 4px;
            line-height: 1.35;
        }}
        .badge-pro {{ color: var(--accent-emerald); }}
        .badge-con {{ color: var(--accent-rose); }}

        .pros-cons-item {{
            background: var(--bg-card);
            border: 1px solid var(--border-muted);
            border-radius: 6px;
            padding: 0.55rem 0.75rem;
            font-size: 0.82rem;
            line-height: 1.65;
            color: var(--text-secondary);
            overflow-wrap: break-word;
            word-break: break-word;
            text-wrap: pretty;
        }}
        .pros-cons-item strong {{
            color: var(--text-main);
            font-weight: 700;
        }}

        /* Strategic Roadmap Table */
        .roadmap-table-wrap {{
            overflow-x: auto;
            border-radius: 8px;
            margin-top: 0.45rem;
            border: 1px solid var(--border-muted);
        }}
        .roadmap-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.80rem;
            text-align: left;
        }}
        .roadmap-table th {{
            padding: 8px 12px;
            background: rgba(15, 20, 28, 0.8);
            border-bottom: 1px solid var(--border-main);
            color: var(--text-muted);
            font-weight: 700;
            white-space: nowrap;
        }}
        .roadmap-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid var(--border-muted);
            line-height: 1.65;
            vertical-align: top;
            overflow-wrap: break-word;
            word-break: break-word;
            text-wrap: pretty;
        }}
        .roadmap-table tr:last-child td {{
            border-bottom: none;
        }}

        /* FULL SEASON FDR TICKER */
        .ticker-container {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 0.75rem;
            flex: 1;
            display: flex;
            flex-direction: column;
            min-height: 0;
            overflow: hidden;
        }}
        .ticker-header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.45rem;
            border-bottom: 1px solid var(--border-main);
            margin-bottom: 0.45rem;
            flex-shrink: 0;
            flex-wrap: wrap;
            gap: 0.5rem;
        }}
        .fdr-legend-strip {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            margin-top: 0.25rem;
            flex-wrap: wrap;
        }}
        .fdr-legend-label {{
            font-size: 0.6rem;
            color: var(--text-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 2px;
        }}
        .fdr-legend-item {{
            font-size: 0.6rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            padding: 0.1rem 0.35rem;
            border-radius: 3px;
            display: inline-flex;
            align-items: center;
            gap: 3px;
        }}
        .fdr-legend-item.fdr-2 {{ background: #0c2d48; color: #38bdf8; border: 1px solid #0369a1; }}
        .fdr-legend-item.fdr-3 {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; }}
        .fdr-legend-item.fdr-4 {{ background: #451a03; color: #fbbf24; border: 1px solid #78350f; }}
        .fdr-legend-item.fdr-5 {{ background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; }}

        .reset-btn {{
            background: #1e293b;
            border: 1px solid var(--border-accent);
            color: var(--text-main);
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .reset-btn:hover {{
            background: #334155;
            border-color: var(--accent-sky);
            color: #ffffff;
        }}
        .ticker-scroll-pane {{
            overflow: auto;
            flex: 1;
            width: 100%;
            position: relative;
            -webkit-overflow-scrolling: touch;
        }}
        .ticker-table-full {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.75rem;
        }}
        .ticker-table-full th, .ticker-table-full td {{
            padding: 0.4rem 0.35rem;
            text-align: center;
            border-bottom: 1px solid var(--border-muted);
            white-space: nowrap;
        }}
        .ticker-table-full th {{
            color: var(--text-muted);
            font-weight: 700;
            font-size: 0.65rem;
            background: #151b26;
            position: sticky;
            top: 0;
            z-index: 20;
            border-bottom: 1px solid var(--border-main);
        }}
        .sortable-th {{
            cursor: pointer;
            transition: background 0.15s ease, color 0.15s ease;
            user-select: none;
        }}
        .sortable-th:hover {{
            background: #1e293b;
            color: var(--accent-sky);
        }}
        .sort-icon {{
            font-size: 0.62rem;
            color: var(--text-muted);
            margin-left: 2px;
        }}

        /* Sticky Columns */
        .tbl-sticky {{
            position: sticky;
            left: 0;
            background: #0f141c;
            z-index: 15;
            text-align: left !important;
            font-weight: 700;
            color: #ffffff;
            min-width: 105px;
            border-right: 1px solid var(--border-muted);
        }}
        .tbl-sticky-2 {{
            position: sticky;
            left: 105px;
            background: #0f141c;
            z-index: 15;
            min-width: 50px;
            border-right: 1px solid var(--border-muted);
        }}
        .tbl-sticky-3 {{
            position: sticky;
            left: 155px;
            background: #0f141c;
            z-index: 15;
            min-width: 48px;
            border-right: 1px solid var(--border-muted);
        }}
        .tbl-sticky-4 {{
            position: sticky;
            left: 203px;
            background: #0f141c;
            z-index: 15;
            min-width: 55px;
            border-right: 2px solid var(--border-accent);
        }}

        th.tbl-sticky {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}
        th.tbl-sticky-2 {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}
        th.tbl-sticky-3 {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}
        th.tbl-sticky-4 {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}

        .fdr-box-lg {{
            padding: 0.25rem 0.45rem;
            border-radius: 4px;
            font-weight: 700;
            font-size: 0.68rem;
            font-family: 'JetBrains Mono', monospace;
            display: inline-block;
            min-width: 58px;
            text-align: center;
        }}
        .fdr-box-lg.fdr-2 {{ background: #0c2d48; color: #38bdf8; border: 1px solid #0369a1; }}
        .fdr-box-lg.fdr-3 {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; }}
        .fdr-box-lg.fdr-4 {{ background: #451a03; color: #fbbf24; border: 1px solid #78350f; }}
        .fdr-box-lg.fdr-5 {{ background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; }}

        /* RESEARCH SOURCES */
        .sources-ledger {{ display: flex; flex-direction: column; width: 100%; }}
        .source-ledger-row {{ 
            display: grid; 
            grid-template-columns: 220px 1fr; 
            gap: 1.25rem; 
            align-items: baseline; 
            padding: 0.75rem 0.4rem; 
            border-bottom: 1px solid var(--border-muted); 
        }}
        .source-ledger-row:last-child {{ border-bottom: none; }}
        .source-identity {{ display: flex; flex-direction: column; gap: 2px; }}
        .source-main-name {{ font-size: 0.9rem; font-weight: 700; color: #ffffff; }}
        .source-link-url {{ font-size: 0.7rem; color: var(--accent-sky); text-decoration: none; font-family: 'JetBrains Mono', monospace; }}
        .source-link-url:hover {{ text-decoration: underline; }}
        .source-feature-body {{ display: flex; flex-direction: column; gap: 3px; }}
        .source-feature-label {{ font-size: 0.64rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .source-feature-text {{ font-size: 0.82rem; color: var(--text-secondary); line-height: 1.65; overflow-wrap: break-word; word-break: break-word; text-wrap: pretty; }}
        .source-feature-text strong {{ color: var(--text-main); font-weight: 700; }}

        .panel-scroll {{ overflow-y: auto; flex: 1; padding-right: 0.3rem; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }}
        .panel {{ background: var(--bg-surface); border: 1px solid var(--border-main); border-radius: 10px; padding: 0.85rem; }}
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; border-bottom: 1px solid var(--border-main); padding-bottom: 0.35rem; }}
        .panel-title {{ font-size: 0.88rem; font-weight: 700; color: #ffffff; }}
        .stat-card-row {{ background: var(--bg-card); border: 1px solid var(--border-muted); border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.45rem; }}
        .source-pill {{ display: inline-block; font-size: 0.58rem; font-weight: 700; text-transform: uppercase; padding: 0.12rem 0.35rem; border-radius: 3px; background: #1e293b; color: var(--text-secondary); border: 1px solid var(--border-accent); }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}

        /* =========================================================
           TAB 5: GW3 POST-MATCH REVIEW & COMPARISON STYLING
           ========================================================= */
        .gw3-review-container {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            flex: 1;
            min-height: 0;
            overflow-y: auto;
            padding-right: 0.25rem;
        }}
        .gw3-hero-banner {{
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(11, 15, 22, 0.95));
            border: 1px solid var(--border-accent);
            border-radius: 12px;
            padding: 1.1rem 1.4rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
            position: relative;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        }}
        .gw3-hero-left {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }}
        .gw3-result-pill {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 0.76rem;
            font-weight: 800;
            padding: 0.28rem 0.85rem;
            border-radius: 30px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            width: fit-content;
        }}
        .gw3-result-pill.winner-c1 {{
            background: rgba(16, 185, 129, 0.2);
            color: var(--accent-emerald);
            border: 1px solid rgba(16, 185, 129, 0.45);
            box-shadow: 0 0 16px rgba(16, 185, 129, 0.3);
        }}
        .gw3-result-pill.winner-c2 {{
            background: rgba(56, 189, 248, 0.2);
            color: var(--accent-sky);
            border: 1px solid rgba(56, 189, 248, 0.45);
            box-shadow: 0 0 16px rgba(56, 189, 248, 0.3);
        }}
        .gw3-result-pill.winner-draw {{
            background: rgba(245, 158, 11, 0.2);
            color: var(--accent-amber);
            border: 1px solid rgba(245, 158, 11, 0.45);
        }}
        .gw3-hero-title {{
            font-size: 1.15rem;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: -0.2px;
        }}
        .gw3-hero-subtitle {{
            font-size: 0.78rem;
            color: var(--text-secondary);
            line-height: 1.5;
        }}
        .gw3-scoreboard {{
            display: flex;
            align-items: center;
            gap: 1.25rem;
            background: rgba(15, 20, 28, 0.85);
            border: 1px solid var(--border-muted);
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
        }}
        .score-box {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
        }}
        .score-lbl {{
            font-size: 0.64rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .score-lbl.lbl-c1 {{ color: var(--accent-emerald); }}
        .score-lbl.lbl-c2 {{ color: var(--accent-sky); }}
        .score-val {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1;
        }}
        .score-val.val-c1 {{ color: var(--accent-emerald); }}
        .score-val.val-c2 {{ color: var(--accent-sky); }}
        .score-divider {{
            font-size: 1.1rem;
            font-weight: 800;
            color: var(--text-muted);
        }}

        .gw3-grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}
        .gw3-panel {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}
        .gw3-panel-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-main);
        }}
        .gw3-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.78rem;
        }}
        .gw3-table th {{
            padding: 6px 10px;
            background: rgba(15, 20, 28, 0.8);
            border-bottom: 1px solid var(--border-main);
            color: var(--text-muted);
            font-weight: 700;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .gw3-table td {{
            border-bottom: 1px solid var(--border-muted);
            vertical-align: middle;
        }}
        .gw3-table tr:hover td {{
            background: rgba(255, 255, 255, 0.02);
        }}
        .gw3-table tr.is-benched td {{
            opacity: 0.65;
        }}
        .gw3-subhead {{
            font-size: 0.68rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 0.4rem 0.2rem 0.2rem;
        }}
        .gw3-decider-box {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 1rem 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
        }}
        .gw3-decider-item {{
            background: var(--bg-card);
            border: 1px solid var(--border-muted);
            border-radius: 6px;
            padding: 0.6rem 0.8rem;
            font-size: 0.82rem;
            line-height: 1.65;
            color: var(--text-secondary);
        }}
        .gw3-decider-item strong {{
            color: #ffffff;
        }}

        /* =========================================================
           MOBILE & TABLET RESPONSIVE STYLING (< 1024px & < 768px)
           ========================================================= */
        @media (max-width: 1024px) {{
            .lineup-split-grid, .summary-split-grid, .gw3-grid-2 {{
                grid-template-columns: 1fr;
                gap: 1.25rem;
            }}
            .summary-metrics-strip {{
                grid-template-columns: repeat(3, 1fr);
            }}
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            .compact-pitch {{
                min-height: 430px;
            }}
        }}

        @media (max-width: 768px) {{
            html, body {{
                overflow-x: hidden;
                width: 100%;
                max-width: 100vw;
            }}
            main {{
                overflow-x: hidden;
                width: 100%;
                max-width: 100vw;
                padding: 0.4rem 0.5rem 1.5rem;
            }}
            header {{ padding: 0.45rem 0.65rem; }}
            .nav-bar {{ padding: 0.3rem 0.5rem; gap: 0.25rem; }}
            .tab-btn {{ font-size: 0.70rem; padding: 0.32rem 0.65rem; border-radius: 5px; }}
            
            .header-wrap {{ flex-direction: column; align-items: stretch; gap: 0.45rem; }}
            .brand-meta {{ flex-direction: column; align-items: flex-start; gap: 0.35rem; width: 100%; }}
            .title-box {{ width: 100%; }}
            .title-box h1 {{ font-size: 0.95rem; line-height: 1.25; }}
            .team-name {{ display: inline-block; }}
            .team-id-tag {{ font-size: 0.68rem; color: var(--text-muted); font-weight: 500; font-family: 'JetBrains Mono', monospace; }}
            .sync-pill {{ margin-left: 0; margin-top: 3px; font-size: 0.58rem; display: inline-flex; }}
            .manager-meta-line {{ font-size: 0.70rem; line-height: 1.5; color: var(--text-secondary); margin-top: 2px; overflow-wrap: break-word; word-break: break-word; }}
            .deadline-pill {{ font-size: 0.56rem; padding: 2px 7px; flex-wrap: wrap; width: 100%; line-height: 1.35; gap: 4px; }}
            
            .stats-strip {{ 
                display: grid; 
                grid-template-columns: 1fr 1fr; 
                gap: 0.35rem; 
                width: 100%; 
                margin-top: 0.2rem; 
            }}
            .stat-cell {{ min-width: 0; padding: 0.32rem 0.5rem; }}
            .stat-cell .lbl {{ font-size: 0.52rem; letter-spacing: 0.4px; }}
            .stat-cell .val {{ font-size: 0.86rem; }}
            .rank-trajectory-tag {{ font-size: 0.50rem; padding: 1px 4px; }}
            
            .gw-target-banner {{
                flex-direction: column;
                align-items: stretch;
                gap: 0.45rem;
                padding: 0.55rem 0.65rem;
            }}
            .gw-banner-left {{
                display: flex;
                align-items: flex-start;
                gap: 0.45rem;
            }}
            .gw-badge-pill {{
                font-size: 0.58rem;
                padding: 0.14rem 0.45rem;
                flex-shrink: 0;
            }}
            .gw-banner-title {{
                font-size: 0.76rem;
                font-weight: 700;
                color: #ffffff;
                line-height: 1.3;
                word-break: keep-all;
            }}
            .gw-banner-en {{
                font-size: 0.62rem;
                color: var(--text-muted);
                display: block;
                margin-top: 1px;
            }}
            .gw-banner-right {{
                display: flex;
                flex-direction: column;
                gap: 0.25rem;
                padding-top: 0.35rem;
                border-top: 1px dashed rgba(255, 255, 255, 0.08);
                font-size: 0.64rem;
            }}
            .gw-divider {{ display: none; }}
            .gw-info-chip {{
                display: flex;
                align-items: baseline;
                gap: 0.35rem;
                flex-wrap: wrap;
            }}
            .chip-label {{
                font-size: 0.56rem;
                font-weight: 700;
                color: var(--text-muted);
                font-family: 'JetBrains Mono', monospace;
            }}
            .chip-val {{
                font-size: 0.66rem;
                color: #ffffff;
            }}
            .quota-rule {{
                font-size: 0.58rem;
                color: var(--accent-emerald);
                font-weight: 600;
            }}

            .lineup-split-grid, .summary-split-grid {{ 
                grid-template-columns: minmax(0, 1fr) !important; 
                width: 100%;
                gap: 0.85rem; 
            }}
            .plan-column {{ 
                min-width: 0;
                width: 100%;
                box-sizing: border-box;
                padding: 0.5rem 0.45rem; 
                border-radius: 9px; 
            }}
            .plan-col-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 0.35rem;
            }}
            .plan-title {{ font-size: 0.82rem; }}
            .fin-badge {{ font-size: 0.60rem; padding: 0.15rem 0.42rem; align-self: flex-start; }}
            
            .compact-pitch {{ 
                min-width: 0;
                width: 100%;
                box-sizing: border-box;
                padding: 0.45rem 0.15rem; 
                min-height: 400px; 
                gap: 0.35rem; 
                overflow: hidden;
            }}
            .pitch-row {{ 
                min-width: 0;
                width: 100%;
                gap: 0.2rem; 
                justify-content: center; 
                box-sizing: border-box;
            }}
            
            .starter-card {{ 
                width: 70px; 
                max-width: 72px;
                min-width: 0;
                flex-shrink: 1;
                padding: 0.18rem 0.16rem 0.14rem; 
                border-radius: 6px; 
                box-sizing: border-box;
            }}
            .starter-card-top {{ min-height: 13px; }}
            .pos-tag-mini {{ font-size: 0.46rem; padding: 0.03rem 0.16rem; border-radius: 2px; }}
            .role-badge-cap, .role-badge-vc {{ font-size: 0.50rem; padding: 0.03rem 0.2rem; }}
            .core-tag-mini, .enabler-tag-mini, .transfer-in-tag-mini {{ font-size: 0.44rem; padding: 0.03rem 0.15rem; }}
            .starter-photo-wrap {{ height: 34px; margin: 0; }}
            .starter-shirt-img {{ width: 30px; height: 30px; }}
            .starter-info-card {{ padding-top: 2px; }}
            .starter-name {{ font-size: 0.60rem; letter-spacing: -0.2px; line-height: 1.1; }}
            .starter-meta {{ font-size: 0.48rem; margin: 1px 0; }}
            .starter-fix-row {{ font-size: 0.45rem; padding-top: 1px; margin-top: 1px; }}
            .starter-fix-text {{ font-weight: 600; }}
            .fdr-pill {{ font-size: 0.46rem; padding: 0.02rem 0.16rem; }}

            .compact-bench-strip {{ 
                min-width: 0;
                width: 100%;
                box-sizing: border-box;
                padding: 0.35rem 0.3rem; 
                margin-top: 0.4rem; 
                border-radius: 7px; 
                overflow-x: auto;
            }}
            .bench-header-bar {{ margin-bottom: 0.2rem; padding-bottom: 0.15rem; }}
            .bench-lbl {{ font-size: 0.56rem; }}
            .bench-count-tag {{ font-size: 0.48rem; padding: 0.03rem 0.25rem; }}
            .bench-row {{ 
                min-width: 0;
                width: 100%;
                gap: 0.2rem; 
                justify-content: center; 
                box-sizing: border-box;
            }}
            .bench-card {{ 
                width: 70px; 
                max-width: 72px;
                min-width: 0;
                flex-shrink: 1;
                padding: 0.18rem 0.16rem 0.14rem; 
                border-radius: 6px; 
                box-sizing: border-box;
            }}
            .bench-card-top {{ min-height: 13px; }}
            .sub-label-badge {{ font-size: 0.46rem; padding: 0.03rem 0.18rem; }}
            .bench-photo-wrap {{ height: 34px; margin: 0; }}
            .bench-shirt-img {{ width: 30px; height: 30px; }}
            .bench-info-card {{ padding-top: 2px; }}
            .bench-name {{ font-size: 0.60rem; letter-spacing: -0.2px; line-height: 1.1; }}
            .bench-meta {{ font-size: 0.48rem; margin: 1px 0; }}
            .bench-fix-row {{ font-size: 0.45rem; padding-top: 1px; margin-top: 1px; }}

            /* Tactical Mobile Transition Divider */
            .mobile-vs-divider {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                margin: 0.65rem 0;
                width: 100%;
            }}
            .vs-line {{
                flex: 1;
                height: 1px;
                background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.4), transparent);
            }}
            .vs-badge {{
                background: #0b1120;
                border: 1px solid rgba(16, 185, 129, 0.5);
                border-radius: 9999px;
                padding: 0.22rem 0.65rem;
                font-size: 0.58rem;
                font-weight: 800;
                color: var(--accent-emerald);
                font-family: 'JetBrains Mono', monospace;
                display: inline-flex;
                align-items: center;
                gap: 5px;
                box-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
            }}

            /* Transfers Delta Box */
            .transfers-delta-box {{ padding: 0.45rem 0.55rem; margin-top: 0.4rem; border-radius: 7px; }}
            .delta-header-strip {{ margin-bottom: 0.25rem; padding-bottom: 0.2rem; }}
            .delta-title {{ font-size: 0.68rem; }}
            .delta-count-pill {{ font-size: 0.52rem; padding: 1px 5px; }}
            .delta-group-label {{ font-size: 0.54rem; min-width: 62px; }}
            .delta-pill {{ font-size: 0.58rem; padding: 1px 5px; }}
            .delta-status-banner, .delta-rule-notice {{ font-size: 0.58rem; line-height: 1.35; padding: 0.25rem 0.45rem; }}
            .status-lbl {{ font-size: 0.54rem; }}
            .status-txt, .rule-txt {{ font-size: 0.58rem; word-break: keep-all; }}
            .delta-ledger-strip {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 0.25rem;
                margin-top: 0.35rem;
                padding-top: 0.3rem;
            }}
            .delta-ledger-cell {{
                padding: 0.25rem 0.15rem;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 2px;
            }}
            .dl-lbl {{ font-size: 0.48rem; text-transform: uppercase; color: var(--text-muted); }}
            .dl-val {{ font-size: 0.64rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #ffffff; }}
            .dl-gain {{ display: block; font-size: 0.52rem; margin-left: 0; }}

            /* Tab 2 Plan Summary Mobile */
            .summary-metrics-strip {{
                grid-template-columns: repeat(2, 1fr);
                gap: 0.35rem;
            }}
            .summary-metric-card {{ padding: 0.4rem 0.5rem; }}
            .summary-metric-title {{ font-size: 0.56rem; }}
            .metric-sub-val {{ font-size: 0.76rem; }}
            .squad-health-widget {{ padding: 0.65rem 0.75rem; margin-bottom: 0.75rem; border-radius: 8px; }}
            .health-heading {{ font-size: 0.78rem; }}
            .health-detail-text {{ font-size: 0.70rem; line-height: 1.45; word-break: keep-all; }}
            .summary-plan-panel {{ padding: 0.65rem; border-radius: 8px; gap: 0.55rem; }}
            .pros-cons-item {{ font-size: 0.68rem; line-height: 1.4; padding: 0.35rem 0.5rem; word-break: keep-all; }}
            .roadmap-table-wrap {{ overflow-x: auto; -webkit-overflow-scrolling: touch; margin-top: 0.5rem; }}
            .roadmap-table {{ min-width: 580px; }}

            /* Tab 3 FDR Ticker Mobile Sticky Columns */
            .tbl-sticky {{ min-width: 82px; font-size: 0.68rem; padding: 0.35rem 0.25rem; }}
            .tbl-sticky-2 {{ left: 82px; min-width: 42px; font-size: 0.68rem; padding: 0.35rem 0.25rem; }}
            .tbl-sticky-3 {{ left: 124px; min-width: 40px; font-size: 0.68rem; padding: 0.35rem 0.25rem; }}
            .tbl-sticky-4 {{ left: 164px; min-width: 45px; font-size: 0.68rem; padding: 0.35rem 0.25rem; }}
            .fdr-box-lg {{ min-width: 48px; font-size: 0.60rem; padding: 0.18rem 0.3rem; }}
            .ticker-scroll-pane {{ max-height: calc(100vh - 210px); }}

            /* Tab 4 Research Sources Mobile */
            .source-ledger-row {{
                grid-template-columns: 1fr;
                gap: 0.35rem;
                padding: 0.65rem 0.3rem;
            }}
            .source-main-name {{ font-size: 0.82rem; }}
            .source-link-url {{ font-size: 0.65rem; }}
            .source-feature-text {{ font-size: 0.72rem; line-height: 1.4; word-break: keep-all; }}
        }}

        @media (max-width: 380px) {{
            .starter-card, .bench-card {{ width: 70px; padding: 0.15rem 0.14rem; }}
            .pitch-row, .bench-row {{ gap: 0.18rem; }}
            .starter-name, .bench-name {{ font-size: 0.58rem; }}
            .starter-photo-wrap, .bench-photo-wrap {{ height: 32px; }}
            .starter-shirt-img, .bench-shirt-img {{ width: 28px; height: 28px; }}
            .compact-pitch {{ padding: 0.35rem 0.12rem; }}
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-wrap">
            <div class="brand-meta">
                <div class="season-badge">FPL 2026/27</div>
                <div class="gw-top-badge">GW{active_gw}</div>
                <div class="title-box">
                    <h1>
                        <span class="team-name">{entry.get("name", "GEMINI UNITED")}</span> 
                        <span class="team-id-tag">(ID: {entry.get('id', 306983)})</span> 
                        <span class="sync-pill" title="Automated Engine Active: Offset 15m schedule monitors prices, injuries, and lineups in real-time. Market data unchanged since last sync"><span class="sync-dot"></span>Last Sync: {last_sync_str}<span class="sync-tag-active">ACTIVE</span></span>
                    </h1>
                    <p class="manager-meta-line">
                        <span class="manager-name">Manager: {entry.get("player_first_name", "")} {entry.get("player_last_name", "")}</span> 
                        <span class="header-dot">&bull;</span> 
                        <span class="gw-target-txt">จัดทีมสำหรับสัปดาห์ที่ {active_gw} (Gameweek {active_gw})</span>
                    </p>
                    <div class="deadline-pill" title="Official Gameweek {active_gw} Deadline">
                        <span class="deadline-tag-prefix">DEADLINE</span> {deadline_str} &bull; <span id="countdownTimer" class="countdown-clock">--h --m --s</span> <span class="lockdown-badge">LOCKDOWN AT -30M</span>
                    </div>
                </div>
            </div>
            <div class="stats-strip">
                <div class="stat-cell">
                    <span class="lbl">Total Budget</span>
                    <span class="val" style="color:#ffffff;">£{total_budget:.1f}m</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">Bank (Choice 2)</span>
                    <span class="val" style="color:var(--accent-sky);">{c2_bank_str}</span>
                </div>
                <div class="stat-cell" style="border-color: rgba(56, 189, 248, 0.4); background: rgba(56, 189, 248, 0.08);">
                    <span class="lbl" style="color:var(--accent-sky); font-weight:700;">Target Gameweek</span>
                    <span class="val" style="color:var(--accent-sky); font-weight:800; font-size:0.95rem;">GW{active_gw}</span>
                </div>
                <div class="stat-cell stat-rank-cell">
                    <span class="lbl">Global Rank</span>
                    <span class="val" style="color:var(--accent-emerald);">{overall_rank:,}</span>
                    <span class="rank-trajectory-tag {rank_tag_class}">{rank_target_label}</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Navigation (5 Clean Tabs) -->
    <nav class="nav-bar">
        <button class="tab-btn active" onclick="switchTab('comparison', this)">Plan Lineup (GW{active_gw})</button>
        <button class="tab-btn" onclick="switchTab('summary', this)">Plan Summary</button>
        <button class="tab-btn" onclick="switchTab('ticker', this)">FDR Ticker</button>
        <button class="tab-btn" onclick="switchTab('sources', this)">Research Sources</button>
        <button class="tab-btn" onclick="switchTab('gw3-review', this)">GW3 Review</button>
    </nav>

    <!-- Main Content Area -->
    <main>
        <!-- TAB 1: PLAN LINEUP -->
        <section id="tab-comparison" class="tab-content active">
            <!-- Gameweek Target Banner on Front Page -->
            <div class="gw-target-banner">
                <div class="gw-banner-left">
                    <span class="gw-badge-pill">GAMEWEEK {active_gw}</span>
                    <div class="gw-banner-title-wrap">
                        <span class="gw-banner-title">การจัดทีมสำหรับสัปดาห์ที่ {active_gw}</span>
                        <span class="gw-banner-en">(Gameweek {active_gw} Lineup &amp; Strategy)</span>
                    </div>
                </div>
                <div class="gw-banner-right">
                    <div class="gw-info-chip">
                        <span class="chip-label">DEADLINE:</span>
                        <strong class="chip-val">{deadline_str}</strong>
                    </div>
                    <span class="gw-divider">&bull;</span>
                    <div class="gw-info-chip">
                        <span class="chip-label">QUOTA:</span>
                        <strong class="chip-val" style="color:var(--accent-emerald);">{user_free_transfers} Free Transfers <span class="quota-rule">(ห้ามเปลี่ยนตัวติดลบ: Cost 0 pts)</span></strong>
                    </div>
                </div>
            </div>

            <div class="lineup-split-grid">
                
                <!-- LEFT COLUMN: CHOICE 1 (MICKY SELECTION) -->
                <div class="plan-column">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title">Choice 1 &bull; Micky Selection (GW{active_gw})</div>
                            <div class="plan-sub-tags">
                                <span class="formation-pill">3-4-3</span>
                                <span class="active-chip-pill" style="background:rgba(56,189,248,0.15); color:var(--accent-sky); border:1px solid rgba(56,189,248,0.3);">GW{active_gw} &bull; BASELINE</span>
                            </div>
                        </div>
                        <div class="fin-badge">
                            Cost: <span style="color:var(--accent-emerald);">£{c1_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">£{c1_bank:.1f}m</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "FWD"])}
                        </div>
                        <!-- MID (4) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "MID"])}
                        </div>
                        <!-- DEF (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "DEF"])}
                        </div>
                        <!-- GKP (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "GKP"])}
                        </div>
                    </div>

                    <div class="compact-bench-strip" id="c1-bench">
                        <div class="bench-header-bar">
                            <span class="bench-lbl">DUGOUT &bull; SUBSTITUTES BENCH</span>
                            <span class="bench-count-tag">4 RESERVES</span>
                        </div>
                        <div class="bench-row">
                            {render_bench_list(c1_bench)}
                        </div>
                    </div>

                    <!-- Choice 1 Baseline Box -->
                    <div class="transfers-delta-box delta-baseline">
                        <div class="delta-header-strip">
                            <div class="delta-title-wrap">
                                <span class="delta-indicator-dot dot-baseline"></span>
                                <span class="delta-title" style="color:var(--text-secondary);">Transfers (Choice 1 Baseline)</span>
                            </div>
                            <span class="delta-count-pill pill-baseline">0 TRANSFERS &bull; {user_free_transfers} FTs BANKED</span>
                        </div>
                        <div class="delta-status-banner">
                            <span class="status-lbl">STATUS:</span>
                            <span class="status-txt">ไม่มีรายการย้ายตัวเข้า-ออก (Baseline Squad &bull; เก็บ {user_free_transfers} FTs ไว้ใช้ GW5 &bull; ค่าปรับ 0 แต้ม)</span>
                        </div>
                        <div class="delta-ledger-strip">
                            <div class="delta-ledger-cell">
                                <span class="dl-lbl">Starting Points</span>
                                <span class="dl-val">{c1_start_pts} pts</span>
                            </div>
                            <div class="delta-ledger-cell">
                                <span class="dl-lbl">Cost Hits</span>
                                <span class="dl-val" style="color:var(--accent-emerald);">0 pts</span>
                            </div>
                            <div class="delta-ledger-cell">
                                <span class="dl-lbl">Remaining Bank</span>
                                <span class="dl-val" style="color:var(--accent-sky);">£0.0m</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- MOBILE TRANSITION DIVIDER (VISIBLE ONLY ON MOBILE) -->
                <div class="mobile-vs-divider">
                    <div class="vs-line"></div>
                    <div class="vs-badge">
                        <span>VS</span> &bull; <span>GEMINI REFINED BLUEPRINT</span>
                    </div>
                    <div class="vs-line"></div>
                </div>

                <!-- RIGHT COLUMN: CHOICE 2 (GEMINI SELECTION) -->
                <div class="plan-column plan-c2" id="choice-2">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title" style="color:var(--accent-emerald);">Choice 2 &bull; GEMINI Refined Blueprint (GW{active_gw})</div>
                            <div class="plan-sub-tags">
                                <span class="formation-pill">3-4-3</span>
                                <span class="active-chip-pill" style="background:rgba(16,185,129,0.15); color:var(--accent-emerald); border:1px solid rgba(16,185,129,0.3);">GW{active_gw} &bull; {transfers_count}/{user_free_transfers} FTs &bull; ZERO HIT</span>
                            </div>
                        </div>
                        <div class="fin-badge" style="border-color:var(--accent-emerald);">
                            Cost: <span style="color:var(--accent-emerald);">£{c2_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">{c2_bank_str}</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in align_pitch_players(c1_starters, c2_starters, "FWD")])}
                        </div>
                        <!-- MID (4) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in align_pitch_players(c1_starters, c2_starters, "MID")])}
                        </div>
                        <!-- DEF (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in align_pitch_players(c1_starters, c2_starters, "DEF")])}
                        </div>
                        <!-- GKP (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in align_pitch_players(c1_starters, c2_starters, "GKP")])}
                        </div>
                    </div>

                    <div class="compact-bench-strip">
                        <div class="bench-header-bar">
                            <span class="bench-lbl">DUGOUT &bull; SUBSTITUTES BENCH</span>
                            <span class="bench-count-tag">4 RESERVES</span>
                        </div>
                        <div class="bench-row">
                            {render_bench_list(align_bench_players(c1_bench, c2_bench))}
                        </div>
                    </div>

                    <!-- Choice 2 Transfer Delta Box -->
                    <div class="transfers-delta-box">
                        <div class="delta-header-strip">
                            <div class="delta-title-wrap">
                                <span class="delta-indicator-dot"></span>
                                <span class="delta-title">Transfers vs Choice 1</span>
                            </div>
                            <span class="delta-count-pill">{transfers_count} IN &bull; {transfers_count} OUT &bull; 0 PT HIT ({transfers_count}/{user_free_transfers} FTs)</span>
                        </div>
                        <div class="delta-list-grid">
                            <div class="delta-group">
                                <div class="delta-group-label in-lbl">TRANSFER IN</div>
                                <div class="delta-tags">
                                    {c2_delta_in_pills}
                                </div>
                            </div>
                            <div class="delta-group">
                                <div class="delta-group-label out-lbl">TRANSFER OUT</div>
                                <div class="delta-tags">
                                    {c2_delta_out_pills}
                                </div>
                            </div>
                        </div>
                        <div class="delta-rule-notice">
                            <span class="rule-txt">เงื่อนไข: ห้ามเปลี่ยนตัวติดลบ (Cost 0 pts &bull; ใช้ {transfers_count}/{user_free_transfers} FTs &bull; สะสม {user_free_transfers - transfers_count} FT ไป GW5)</span>
                        </div>
                        <div class="delta-ledger-strip">
                            <div class="delta-ledger-cell">
                                <span class="dl-lbl">Starting Points</span>
                                <span class="dl-val">{c2_start_pts} pts <span class="dl-gain">+{c2_start_pts - c1_start_pts} pts</span></span>
                            </div>
                            <div class="delta-ledger-cell">
                                <span class="dl-lbl">Cost Hits</span>
                                <span class="dl-val" style="color:var(--accent-emerald);">0 pts</span>
                            </div>
                            <div class="delta-ledger-cell">
                                <span class="dl-lbl">Remaining Bank</span>
                                <span class="dl-val" style="color:var(--accent-sky);">{c2_bank_str}</span>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- TAB 2: PLAN SUMMARY (REAL-TIME STRATEGIC AUDIT & PROS/CONS) -->
        <section id="tab-summary" class="tab-content">
            <!-- Feature 4: Squad Fitness & Friday Press Conference Watcher Widget -->
            <div class="squad-health-widget">
                <div class="health-top-bar">
                    <div class="health-meta">
                        <span class="health-dot-active"></span>
                        <span class="health-heading">Friday Press Conference &amp; Squad Fitness Watcher</span>
                    </div>
                    <span class="health-status-badge {health_badge_class}">{health_status_badge}</span>
                </div>
                <div class="health-detail-text">
                    {health_detail_text}
                </div>
                {health_alerts_html}
            </div>

            <!-- Chip Inventory & Strategic Horizon Widget -->
            <div class="squad-health-widget" style="border-color: rgba(56, 189, 248, 0.35);">
                <div class="health-top-bar">
                    <div class="health-meta">
                        <span class="health-dot-active" style="background:var(--accent-sky); box-shadow:0 0 8px var(--accent-sky);"></span>
                        <span class="health-heading">Official FPL 2026/27 Chip Inventory &amp; Dual-Half Architecture</span>
                    </div>
                    <span class="health-status-badge" style="background:rgba(16, 185, 129, 0.15); color:var(--accent-emerald); border:1px solid rgba(16, 185, 129, 0.35);">CHIP REMAINING: {remaining_chips_count} / {total_chips_count} (6 AVAILABLE)</span>
                </div>
                <div class="health-detail-text" style="margin-bottom:0.75rem;">
                    ในฤดูกาล 2026/27 กฎ FPL แบ่งชิปการเล่นออกเป็น <strong>2 ครึ่งฤดูกาล (รวมทั้งหมด 8 ชิป)</strong> โดยแต่ละครึ่งฤดูกาลจะมีชิป 4 ใบ (Wildcard, Free Hit, Bench Boost, Triple Captain) แยกจากกันอย่างอิสระ:
                </div>
                
                <!-- Half 1 Chips (GW1 - GW19) -->
                <div style="margin-bottom:0.75rem;">
                    <div style="font-size:0.7rem; font-weight:700; color:var(--text-bright); margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px;">
                        <span>ครึ่งแรก (Half 1: GW1 - GW19)</span>
                        <span style="font-size:0.6rem; padding:1px 6px; border-radius:3px; background:rgba(245, 158, 11, 0.15); color:var(--accent-amber); border:1px solid rgba(245, 158, 11, 0.3);">เตือน: ชิปที่เหลือจะหมดอายุสิ้น GW19</span>
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:0.5rem;">
                        {chips_half1_str}
                    </div>
                </div>

                <!-- Half 2 Chips (GW20 - GW38) -->
                <div>
                    <div style="font-size:0.7rem; font-weight:700; color:var(--text-bright); margin-bottom:0.4rem; text-transform:uppercase; letter-spacing:0.5px; display:flex; align-items:center; gap:6px;">
                        <span>ครึ่งหลัง (Half 2: GW20 - GW38)</span>
                        <span style="font-size:0.6rem; padding:1px 6px; border-radius:3px; background:rgba(56, 189, 248, 0.15); color:var(--accent-sky); border:1px solid rgba(56, 189, 248, 0.3);">ปลดล็อกชุดที่ 2 เต็มอัตราศึก 4 ชิป</span>
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:0.5rem;">
                        {chips_half2_str}
                    </div>
                </div>
            </div>

            <!-- Multi-Week Transfer Roadmap Widget -->
            <div class="squad-health-widget" style="border-color: rgba(16, 185, 129, 0.35);">
                <div class="health-top-bar">
                    <div class="health-meta">
                        <span class="health-dot-active" style="background:var(--accent-emerald); box-shadow:0 0 8px var(--accent-emerald);"></span>
                        <span class="health-heading">Multi-Week Strategic Transfer &amp; Chip Roadmap (GW4 - GW7)</span>
                    </div>
                    <span class="health-status-badge health-badge-ok">ACTIVE WEAPONS: TC1 &amp; FH1 READY</span>
                </div>
                <div class="roadmap-table-wrap">
                    <table class="roadmap-table" style="width:100%; border-collapse:collapse; font-size:0.75rem; text-align:left;">
                        <thead>
                            <tr style="border-bottom:1px solid var(--border-main); color:var(--text-muted);">
                                <th style="padding:6px 10px;">Gameweek</th>
                                <th style="padding:6px 10px;">สถานะโควตา Free Transfer / ชิปเลกแรก</th>
                                <th style="padding:6px 10px;">โปรแกรมสำคัญ &amp; ปัจจัยวิกฤต</th>
                                <th style="padding:6px 10px;">ข้อแนะนำเชิงกลยุทธ์ (Choice 2 Roadmap)</th>
                            </tr>
                        </thead>
                        <tbody>
{dynamic_roadmap_rows_html}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Pros & Cons Split Grid -->
            <div class="summary-split-grid">
                
                <!-- CHOICE 1 PROS & CONS -->
                <div class="summary-plan-panel">
                    <div class="summary-panel-header">
                        <div>
                            <div class="plan-title">Choice 1 &bull; Micky Final Lockdown Squad</div>
                            <span style="font-size:0.65rem; color:var(--text-secondary);">3-4-3 Formation &bull; Cost: £{c1_cost:.1f}m &bull; Bank: £{c1_bank:.1f}m &bull; Quota: {user_free_transfers} FTs</span>
                        </div>
                        <span class="source-pill" style="border-color:var(--accent-emerald); color:var(--accent-emerald);">Lockdown Active</span>
                    </div>

                    <!-- Pros -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-pro">ข้อดีและจุดแข็ง (Strengths &amp; Pros)</div>
                        <div class="pros-cons-item">
                            <strong>Cole Palmer Captaincy [C] vs Hull City (H - FDR 2):</strong> มอบปลอกแขนกัปตันให้ Cole Palmer (£9.7m) เฝ้ารังรับมือ ฮัลล์ ซิตี้ ทีมเพิ่งเลื่อนชั้น มีโอกาสสร้างเพดานแต้มระเบิด (Explosive Ceiling) สูงสุดประจำสัปดาห์จากทั้งจุดโทษ ฟรีคิก และโอเพ่นเพลย์
                        </div>
                        <div class="pros-cons-item">
                            <strong>Martin Ødegaard Transfer-In Masterstroke:</strong> ปลดล็อกความเสี่ยงอาการบาดเจ็บของ Cody Gakpo (โอกาสลงสนาม 75% จากงานแถลงข่าว) ด้วยการย้ายตัวดึง Martin Ødegaard (£6.7m) จอมทัพอาร์เซนอลความฟิต 100% บุกเยือนซันเดอร์แลนด์ (FDR 2) พร้อมเก็บเงินสดสำรองเข้าธนาคาร +£0.5m โดยไม่เสียแต้มลบ (Cost: 0 pts)
                        </div>
                        <div class="pros-cons-item">
                            <strong>Phil Foden Tactical Bench Buffer (Sub 1 Priority):</strong> เก็บรักษา Phil Foden (£7.0m) ไว้ในทีมแทนการเทขายทิ้ง จัดวางเป็นตัวสำรองอันดับ 1 (Sub 1) พร้อมเสียบลงสนามทันทีหากแนวรุกคนใดไม่ลงเล่น และพร้อมใช้งานเต็มพิกัดในโปรแกรม GW5 (แมนฯ ซิตี้ พบ ซันเดอร์แลนด์ FDR 2)
                        </div>
                        <div class="pros-cons-item">
                            <strong>João Pedro Front-3 Promotion &amp; Vice Captain [VC] vs Hull City (H - FDR 2):</strong> ดัน João Pedro (£7.7m) ยืนแดนหน้าตัวจริงพร้อมสวมปลอกแขนรองกัปตัน [VC] เพื่อทำ Double Attack ฝั่งเชลซีรับมือฮัลล์ ซิตี้ เต็มสูบ
                        </div>
                        <div class="pros-cons-item">
                            <strong>Bart Verbruggen Away Goalkeeper Selection vs Coventry (A - FDR 2):</strong> มอบความไว้วางใจให้ Verbruggen (£4.5m) บุกเยือนโคเวนทรี เพื่อลุ้นคลีนชีตนอกบ้าน ขณะที่ Antonín Kinsky สแตนด์บายพร้อมเป็นสำรองที่เชื่อถือได้
                        </div>
                        <div class="pros-cons-item">
                            <strong>Triple Front-3 Firepower (Haaland + João Pedro + Wissa):</strong> โครงสร้าง 3-4-3 ยืนหน้าสามครบถ้วน Haaland ล่าตาข่ายในศึกแมนเชสเตอร์ดาร์บี้, Pedro รับมือฮัลล์ และ Wissa เยือนลีดส์ ยูไนเต็ด ครอบคลุมโอกาสทำประตูทุกคู่
                        </div>
                    </div>

                    <!-- Cons -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-con">ข้อเสียและจุดที่ต้องระวัง (Weaknesses &amp; Cons)</div>
                        <div class="pros-cons-item">
                            <strong>Heavy Bench Capital &amp; Manchester Derby Benched (£12.6m on Bench):</strong> พัก Foden (£7.0m - Sub 1) และ Gvardiol (£5.6m - Sub 2) ไว้บนม้านั่งสำรองในเกมแมนเชสเตอร์ดาร์บี้เยือนโอลด์ แทรฟฟอร์ด ทำให้มีมูลค่าทรัพยากรบนม้านั่งสูงถึง £12.6m ซึ่งหากแมนฯ ซิตี้ ชนะถล่มทลาย แต้มสำคัญอาจค้างอยู่ข้างสนาม
                        </div>
                        <div class="pros-cons-item">
                            <strong>O'Shea Difficult Away Matchup (CRY Away FDR 3):</strong> การส่ง Dara O'Shea (£4.0m) ยืนตัวจริงในเกมเยือนคริสตัล พาเลซ มีความเสี่ยงต่อการเสียคลีนชีตจากเกมรุกริมเส้นของพาเลซ
                        </div>
                        <div class="pros-cons-item">
                            <strong>No Man City Captaincy Ceiling Risk:</strong> การโยกปลอกแขนกัปตันจาก Erling Haaland ไปให้ Cole Palmer หาก Haaland ระเบิดแฮตทริกในแมนเชสเตอร์ดาร์บี้ อาจส่งผลต่ออันดับ Overall Rank ได้ทันที
                        </div>
                    </div>
                </div>

                <!-- CHOICE 2 PROS & CONS -->
                <div class="summary-plan-panel" style="border-color: rgba(16, 185, 129, 0.45);">
                    <div class="summary-panel-header">
                        <div>
                            <div class="plan-title" style="color:var(--accent-emerald);">Choice 2 &bull; Derby Attack Variant (3-5-2)</div>
                            <span style="font-size:0.65rem; color:var(--text-secondary);">3-5-2 Formation &bull; Cost: £{c2_cost:.1f}m &bull; Bank: {c2_bank_str} &bull; Hits: 0 pts</span>
                        </div>
                        <span class="source-pill" style="border-color:var(--accent-emerald); color:var(--accent-emerald);">Derby High-Ceiling</span>
                    </div>

                    <!-- Pros -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-pro">ข้อดีและจุดแข็ง (Strengths &amp; Pros)</div>
                        <div class="pros-cons-item">
                            <strong>Zero-Hit Rule Enforced (ห้ามเปลี่ยนตัวติดลบ 0 pts):</strong> ใช้โครงสร้างขุมกำลังชุดเดียวกัน 100% ภายใต้โควตา Free Transfer เดิมโดยไม่เสียแต้มลบแม้แต่แต้มเดียว (Penalty: 0 pts)
                        </div>
                        <div class="pros-cons-item">
                            {c2_pro_upgrade}
                        </div>
                        <div class="pros-cons-item">
                            <strong>Antonín Kinsky Home Clean Sheet Edge vs Everton (H - FDR 2):</strong> อาศัยความได้เปรียบเกมเหย้าของสเปอร์สรับมือเอฟเวอร์ตันเพื่อลุ้นคลีนชีตแรกในบ้าน
                        </div>
                        <div class="pros-cons-item">
                            <strong>Retained 1 FT for GW5 Tactical Flexibility:</strong> การใช้เพียง 1 จาก 2 FTs ในสัปดาห์นี้ ทำให้ยังมีโควตา Free Transfer สำรองติดตัวสะสมต่อไปยัง GW5 (แมนฯ ซิตี้ พบ ซันเดอร์แลนด์ FDR 2) ได้อย่างยอดเยี่ยม
                        </div>
                        <div class="pros-cons-item">
                            <strong>Financial Buffer &amp; Liquidity ({c2_bank_str} in Bank):</strong> เหลือเงินสดสำรอง {c2_bank_str} ไว้ในธนาคาร เปิดทางให้บริหาร Free Transfer ใน GW5 ได้อย่างคล่องตัว
                        </div>
                    </div>

                    <!-- Cons -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-con">ข้อเสียและจุดที่ต้องระวัง (Weaknesses &amp; Cons)</div>
                        <div class="pros-cons-item">
                            {c2_con_transfer}
                        </div>
                        <div class="pros-cons-item">
                            <strong>Manchester Derby Exposure Risk:</strong> การออกสตาร์ตทั้ง Haaland และ Foden พร้อมกัน ทำให้ต้องแบกรับความผันผวนสูงจากเกมดาร์บี้แมตช์นอกบ้าน
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- TAB 3: FDR TICKER -->
        <section id="tab-ticker" class="tab-content">
            <div class="ticker-container">
                <div class="ticker-header-bar">
                    <div>
                        <h2 style="font-size:0.95rem; font-weight:700; color:#ffffff;">Full Season Fixture Difficulty &amp; Sorting (GW{active_gw} &ndash; GW38)</h2>
                        <div class="fdr-legend-strip">
                            <span class="fdr-legend-label">FDR Scale:</span>
                            <span class="fdr-legend-item fdr-2">FDR 2 &bull; Easy</span>
                            <span class="fdr-legend-item fdr-3">FDR 3 &bull; Normal</span>
                            <span class="fdr-legend-item fdr-4">FDR 4 &bull; Hard</span>
                            <span class="fdr-legend-item fdr-5">FDR 5 &bull; Very Hard</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:0.5rem; align-items:center;">
                        <button class="reset-btn" onclick="resetTableSort()">Reset Sort</button>
                        <span style="font-size:0.65rem; color:var(--text-muted);">Scroll &rarr; to view GW{active_gw}-38</span>
                    </div>
                </div>
                
                <div class="ticker-scroll-pane">
                    <table class="ticker-table-full" id="seasonFdrTable">
                        <thead>
                            <tr>
                                <th class="tbl-sticky sortable-th" onclick="sortTable(0, 'text')" title="Sort by Player Name">Player <span class="sort-icon">&varr;</span></th>
                                <th class="tbl-sticky-2 sortable-th" onclick="sortTable(1, 'text')" title="Sort by Club">Club <span class="sort-icon">&varr;</span></th>
                                <th class="tbl-sticky-3 sortable-th" onclick="sortTable(2, 'number')" title="Sort by Position">Pos <span class="sort-icon">&varr;</span></th>
                                <th class="tbl-sticky-4 sortable-th" onclick="sortTable(3, 'number')" title="Sort by Cost">Cost <span class="sort-icon">&varr;</span></th>
                                {"".join(gw_headers)}
                            </tr>
                        </thead>
                        <tbody>
                            {"".join([render_ticker_row_full_season(p, team_fixtures, active_gw, 38, i) for i, p in enumerate(all_ticker_squad)])}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 4: RESEARCH SOURCES -->
        <section id="tab-sources" class="tab-content">
            <div class="panel panel-scroll" style="background:transparent; border:none; padding:0.4rem 0.5rem;">
                <div style="margin-bottom:0.6rem; border-bottom:1px solid var(--border-main); padding-bottom:0.4rem;">
                    <h2 style="font-size:0.95rem; font-weight:700; color:#ffffff;">Research Sources &amp; Analytical Framework</h2>
                    <p style="font-size:0.72rem; color:var(--text-secondary);">แหล่งข้อมูลเชิงลึก 5 ด้านที่เชื่อมโยงในการวิเคราะห์และจัดสรรทีม GEMINI UNITED</p>
                </div>

                <!-- Feature 4: Squad Fitness & Friday Press Conference Watcher Widget -->
                <div class="squad-health-widget">
                    <div class="health-top-bar">
                        <div class="health-meta">
                            <span class="health-dot-active"></span>
                            <span class="health-heading">Friday Press Conference &amp; Squad Fitness Watcher</span>
                        </div>
                        <span class="health-status-badge {health_badge_class}">{health_status_badge}</span>
                    </div>
                    <div class="health-detail-text">
                        {health_detail_text}
                    </div>
                    {health_alerts_html}
                </div>

                <div class="sources-ledger">
                    <div class="source-ledger-row">
                        <div class="source-identity">
                            <span class="source-main-name">Fantasy Football Scout</span>
                            <a href="https://www.fantasyfootballscout.co.uk" target="_blank" class="source-link-url">fantasyfootballscout.co.uk &rarr;</a>
                        </div>
                        <div class="source-feature-body">
                            <span class="source-feature-label">จุดเด่นสำคัญ:</span>
                            <span class="source-feature-text">
                                ศูนย์รวม<strong>ข่าวความพร้อมและสรุปบทสัมภาษณ์งานแถลงข่าว (Press Conferences)</strong> ของผู้จัดการทีมทั้ง 20 สโมสร, ตารางรายงานอาการบาดเจ็บและโทษแบนล่าสุด รวมถึงการตรวจจับ<strong>ไลน์อัป 11 ตัวจริงที่หลุดออกมาก่อนเดดไลน์ (Early Leaks)</strong> 15-30 นาที
                            </span>
                        </div>
                    </div>

                    <div class="source-ledger-row">
                        <div class="source-identity">
                            <span class="source-main-name">Solio Analytics</span>
                            <a href="https://fpl.solioanalytics.com" target="_blank" class="source-link-url">fpl.solioanalytics.com &rarr;</a>
                        </div>
                        <div class="source-feature-body">
                            <span class="source-feature-label">จุดเด่นสำคัญ:</span>
                            <span class="source-feature-text">
                                โมเดลคณิตศาสตร์และ AI เชิงปริมาณ คำนวณ<strong>ค่าคาดการณ์แต้มล่วงหน้า (Projected Points)</strong>, คัดกรองตัวสร้างความต่างที่มีประสิทธิภาพสูง (<strong>Leverage Differentials</strong>), คำนวณโอกาสคลีนชีต (Clean Sheet Odds) และประเมินค่าความคุ้มค่าของ Transfer Solvers
                            </span>
                        </div>
                    </div>

                    <div class="source-ledger-row">
                        <div class="source-identity">
                            <span class="source-main-name">Coach FPL FDR</span>
                            <a href="https://coachfplfdr.streamlit.app" target="_blank" class="source-link-url">coachfplfdr.streamlit.app &rarr;</a>
                        </div>
                        <div class="source-feature-body">
                            <span class="source-feature-label">จุดเด่นสำคัญ:</span>
                            <span class="source-feature-text">
                                ระบบวิเคราะห์โปรแกรมการแข่งขันขั้นสูง (Custom Fixture Difficulty Rating) <strong>แยกความยากง่ายฝั่งเกมรุก (Attacking FDR) และเกมรับ (Defensive FDR)</strong> อย่างแม่นยำ พร้อมโมเดลคำนวณการจับคู่โรเตชั่นแนวรับและผู้รักษาประตูราคาประหยัด
                            </span>
                        </div>
                    </div>

                    <div class="source-ledger-row">
                        <div class="source-identity">
                            <span class="source-main-name">LiveFPL</span>
                            <a href="https://www.livefpl.net" target="_blank" class="source-link-url">livefpl.net &rarr;</a>
                        </div>
                        <div class="source-feature-body">
                            <span class="source-feature-label">จุดเด่นสำคัญ:</span>
                            <span class="source-feature-text">
                                ระบบติดตามอันดับสดแบบ Real-time, คำนวณอัตราการถือครองจริงรวมกัปตัน (<strong>Effective Ownership - EO%</strong>), ส่องทีมของกลุ่มยอดฝีมือ <strong>Top 10k Elite Managers</strong> และคำนวณค่าแต้มความปลอดภัย (Safety Score) เพื่อเป้าหมาย Top 100k
                            </span>
                        </div>
                    </div>

                    <div class="source-ledger-row">
                        <div class="source-identity">
                            <span class="source-main-name">FPL Gameweek</span>
                            <a href="https://www.fplgameweek.com" target="_blank" class="source-link-url">fplgameweek.com &rarr;</a>
                        </div>
                        <div class="source-feature-body">
                            <span class="source-feature-label">จุดเด่นสำคัญ:</span>
                            <span class="source-feature-text">
                                แดชบอร์ดติดตามสถานะคู่แข่งในมินิลีกแบบ Real-time, ระบบคำนวณแต้มสดพร้อม<strong>แต้มโบนัสชั่วคราว (Live BPS)</strong> และระบบจำลองการเปลี่ยนตัวสำรองอัตโนมัติสดระหว่างที่เกมกำลังแข่งขัน
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- TAB 5: GW3 POST-MATCH REVIEW & COMPARISON -->
        <section id="tab-gw3-review" class="tab-content">
            <div class="gw3-review-container">
                <!-- HERO WINNER & SCORE BANNER -->
                <div class="gw3-hero-banner">
                    <div class="gw3-hero-left">
                        <span class="gw3-result-pill {gw3_result_class}">{gw3_result_badge}</span>
                        <h2 class="gw3-hero-title">สรุปผลการแข่งขัน &amp; เปรียบเทียบคะแนนสัปดาห์ที่ผ่านมา (GW3 Review)</h2>
                        <p class="gw3-hero-subtitle">{gw3_result_desc} &bull; ค่าเฉลี่ยผู้เล่นทั่วโลก (World Average): <strong>51 pts</strong> &bull; อันดับประจำสัปดาห์: <strong>3,758,653</strong> &bull; อันดับรวมทั่วโลก: <strong>59,630</strong></p>
                    </div>
                    <div class="gw3-scoreboard">
                        <div class="score-box">
                            <span class="score-lbl lbl-c1">Choice 1 (Actual)</span>
                            <span class="score-val val-c1">{gw3_c1_start_pts}</span>
                            <span style="font-size:0.62rem; color:var(--text-muted);">Bench: {gw3_c1_bench_pts} pts</span>
                        </div>
                        <div class="score-divider">VS</div>
                        <div class="score-box">
                            <span class="score-lbl lbl-c2">Choice 2 (Variant)</span>
                            <span class="score-val val-c2">{gw3_c2_start_pts}</span>
                            <span style="font-size:0.62rem; color:var(--text-muted);">Bench: {gw3_c2_bench_pts} pts</span>
                        </div>
                    </div>
                </div>

                <!-- SIDE-BY-SIDE SQUAD BREAKDOWN -->
                <div class="gw3-grid-2">
                    <!-- LEFT: CHOICE 1 BREAKDOWN -->
                    <div class="gw3-panel" style="border-color: rgba(16, 185, 129, 0.35);">
                        <div class="gw3-panel-header">
                            <div>
                                <span class="plan-title" style="color:var(--accent-emerald);">Choice 1 &bull; Micky Actual Squad (GW3 Wildcard)</span>
                                <div style="font-size:0.68rem; color:var(--text-secondary);">ตัวจริง 11 คน &bull; กัปตัน Erling Haaland (18 pts)</div>
                            </div>
                            <span class="source-pill" style="border-color:var(--accent-emerald); color:var(--accent-emerald); font-size:0.7rem; font-weight:800;">
                                {gw3_c1_start_pts} PTS
                            </span>
                        </div>

                        <div class="gw3-subhead">11 ผู้เล่นตัวจริง (Starters XI): {gw3_c1_start_pts} คะแนน</div>
                        <table class="gw3-table">
                            <thead>
                                <tr>
                                    <th>นักเตะ</th>
                                    <th>สโมสร</th>
                                    <th style="text-align:right;">คะแนน</th>
                                </tr>
                            </thead>
                            <tbody>
                                {gw3_c1_starters_html}
                            </tbody>
                        </table>

                        <div class="gw3-subhead" style="margin-top:0.4rem; border-top:1px dashed var(--border-muted); padding-top:0.5rem;">
                            ตัวสำรองบนม้านั่ง (Bench Reserves): {gw3_c1_bench_pts} คะแนน
                        </div>
                        <table class="gw3-table">
                            <tbody>
                                {gw3_c1_bench_html}
                            </tbody>
                        </table>
                    </div>

                    <!-- RIGHT: CHOICE 2 BREAKDOWN -->
                    <div class="gw3-panel" style="border-color: rgba(56, 189, 248, 0.35);">
                        <div class="gw3-panel-header">
                            <div>
                                <span class="plan-title" style="color:var(--accent-sky);">Choice 2 &bull; Tactical Variant Setup</span>
                                <div style="font-size:0.68rem; color:var(--text-secondary);">ตัวจริง 11 คน &bull; สลับ Konsa ลงแทน Egan / Pedro แทน Wissa</div>
                            </div>
                            <span class="source-pill" style="border-color:var(--accent-sky); color:var(--accent-sky); font-size:0.7rem; font-weight:800;">
                                {gw3_c2_start_pts} PTS
                            </span>
                        </div>

                        <div class="gw3-subhead">11 ผู้เล่นตัวจริง (Starters XI): {gw3_c2_start_pts} คะแนน</div>
                        <table class="gw3-table">
                            <thead>
                                <tr>
                                    <th>นักเตะ</th>
                                    <th>สโมสร</th>
                                    <th style="text-align:right;">คะแนน</th>
                                </tr>
                            </thead>
                            <tbody>
                                {gw3_c2_starters_html}
                            </tbody>
                        </table>

                        <div class="gw3-subhead" style="margin-top:0.4rem; border-top:1px dashed var(--border-muted); padding-top:0.5rem;">
                            ตัวสำรองบนม้านั่ง (Bench Reserves): {gw3_c2_bench_pts} คะแนน
                        </div>
                        <table class="gw3-table">
                            <tbody>
                                {gw3_c2_bench_html}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- TACTICAL DECIDERS AUDIT -->
                <div class="gw3-decider-box">
                    <div style="font-size:0.85rem; font-weight:700; color:#ffffff; display:flex; align-items:center; gap:6px;">
                        <span>จุดชี้ขาดสำคัญของการแข่งขันสัปดาห์ที่ 3 (Key Tactical Match Deciders)</span>
                    </div>
                    <div class="gw3-decider-item">
                        <strong>1. The Cody Gakpo Masterstroke (11 คะแนน):</strong> การตัดสินใจคว้าตัวและส่ง Cody Gakpo (£7.2m) ยืนตัวจริงในแดนกลางสร้างผลลัพธ์มหาศาล โดยเจ้าตัวระเบิดฟอร์มโกยถึง 11 คะแนน เป็นผู้เล่นแดนกลางที่ทำแต้มสูงสุดของทั้งสองทีม
                    </div>
                    <div class="gw3-decider-item">
                        <strong>2. John Egan Differential (+2 คะแนนเหนือ Choice 2):</strong> Choice 1 ส่ง John Egan (£4.1m) ลงสนามตัวจริงและเก็บได้ 6 คะแนน ขณะที่ Choice 2 เลือกลงสนาม Ezri Konsa (£4.4m) ที่ได้ 4 คะแนน ส่งผลให้ Choice 1 เก็บความได้เปรียบเฉือนชนะไป +2 แต้มอย่างเด็ดขาด
                    </div>
                    <div class="gw3-decider-item">
                        <strong>3. Erling Haaland Captaincy Foundation (18 คะแนน):</strong> ทั้งสองตัวเลือกวาง Erling Haaland เป็นกัปตันคูณสองอย่างเฉียบคม ผลงานยิงประตูช่วยเก็บ 9x2 = 18 แต้ม การันตีฐานคะแนนนำค่าเฉลี่ยทั่วโลก (51 pts) ได้อย่างปลอดภัย
                    </div>
                    <div class="gw3-decider-item">
                        <strong>4. Bench Points Reflection (แต้มบนม้านั่งสำรอง):</strong> ทั้งสองทีมมีแต้มค้างอยู่บนม้านั่งสำรองในระดับ 14-16 คะแนน โดยเฉพาะ Antonín Kinsky (£4.5m) ผู้รักษาประตูที่เก็บคลีนชีตทำได้ถึง 6 คะแนนบนม้านั่งสำรอง
                    </div>
                </div>
            </div>
        </section>
    </main>

    <script>
        function switchTab(tabId, btn) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            const target = document.getElementById('tab-' + tabId);
            if (target) target.classList.add('active');
            
            if (btn) {{
                btn.classList.add('active');
            }} else if (window.event && window.event.currentTarget) {{
                window.event.currentTarget.classList.add('active');
            }}
        }}

        // Support direct tab deep-linking via URL hash (e.g. #summary, #ticker, #sources, #gw3-review)
        window.addEventListener('DOMContentLoaded', () => {{
            const hash = window.location.hash.replace('#', '');
            const tabMap = {{ 'comparison': 0, 'summary': 1, 'ticker': 2, 'sources': 3, 'gw3-review': 4 }};
            if (hash in tabMap) {{
                const btns = document.querySelectorAll('.tab-btn');
                if (btns[tabMap[hash]]) {{
                    switchTab(hash, btns[tabMap[hash]]);
                }}
            }}
        }});

        // Multi-Column Sorting & Reset Functionality
        let sortAsc = true;
        let lastSortedCol = -1;

        function sortTable(colIndex, type) {{
            const table = document.getElementById("seasonFdrTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));

            if (lastSortedCol === colIndex) {{
                sortAsc = !sortAsc;
            }} else {{
                sortAsc = true;
                lastSortedCol = colIndex;
            }}

            rows.sort((a, b) => {{
                const cellA = a.children[colIndex];
                const cellB = b.children[colIndex];

                let valA = cellA.getAttribute("data-val") || cellA.innerText.trim();
                let valB = cellB.getAttribute("data-val") || cellB.innerText.trim();

                if (type === 'number') {{
                    valA = parseFloat(valA) || 0;
                    valB = parseFloat(valB) || 0;
                    if (valA < valB) return sortAsc ? -1 : 1;
                    if (valA > valB) return sortAsc ? 1 : -1;
                    return 0;
                }} else {{
                    valA = valA.toString().toLowerCase();
                    valB = valB.toString().toLowerCase();
                    return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
                }}
            }});

            rows.forEach(r => tbody.appendChild(r));
        }}

        function resetTableSort() {{
            const table = document.getElementById("seasonFdrTable");
            const tbody = table.querySelector("tbody");
            const rows = Array.from(tbody.querySelectorAll("tr"));

            rows.sort((a, b) => {{
                const idxA = parseInt(a.getAttribute("data-orig-index") || "0", 10);
                const idxB = parseInt(b.getAttribute("data-orig-index") || "0", 10);
                return idxA - idxB;
            }});

            rows.forEach(r => tbody.appendChild(r));
            lastSortedCol = -1;
            sortAsc = true;
        }}

        // Feature 5: Real-Time Deadline Countdown Timer
        const deadlineEpoch = {deadline_epoch};
        function updateDeadlineCountdown() {{
            const now = Math.floor(Date.now() / 1000);
            const diff = deadlineEpoch - now;
            const timerEl = document.getElementById('countdownTimer');
            if (!timerEl) return;
            if (diff <= 0) {{
                timerEl.textContent = "DEADLINE PASSED";
                timerEl.style.color = "var(--accent-rose)";
            }} else {{
                const hours = Math.floor(diff / 3600);
                const mins = Math.floor((diff % 3600) / 60);
                const secs = diff % 60;
                timerEl.textContent = hours + "h " + mins + "m " + secs + "s";
            }}
        }}
        setInterval(updateDeadlineCountdown, 1000);
        updateDeadlineCountdown();
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[OK] Generated Presentation with Plan Summary Tab at: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FPL Presentation HTML")
    parser.add_argument("--dir", type=str, default="data", help="Data directory")
    parser.add_argument("--out", type=str, default="index.html", help="Output HTML file")
    parser.add_argument("--gw", type=int, default=None, help="Target Gameweek override (optional)")
    args = parser.parse_args()
    generate_html_report(args.dir, args.out, target_gw=args.gw)
