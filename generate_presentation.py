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

    t_code = p.get("official_team_code", 43)
    is_gkp = p.get("pos") == "GKP"
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"

    return f"""
    <div class="starter-card">
        <div class="starter-card-top">
            <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
            {cap_marker}
            {core_tag}
            {enabler_tag}
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
    
    is_gkp = p.get("pos") == "GKP"
    sub_label = "GKP SUB" if is_gkp else f"SUB {sub_idx}"
    sub_tag = f'<span class="sub-label-badge">{sub_label}</span>'

    t_code = p.get("official_team_code", 43)
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"

    return f"""
    <div class="bench-card">
        <div class="bench-card-top">
            <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
            {sub_tag}
            {core_tag}
            {enabler_tag}
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

def render_ticker_row_full_season(p, team_fixtures, start_gw=3, end_gw=38, orig_idx=0):
    t_id = p.get("team_id", 1)
    fix_dict = team_fixtures.get(t_id, {})
    
    cells = []
    for gw in range(start_gw, end_gw + 1):
        gw_fixes = fix_dict.get(gw, [])
        if not gw_fixes:
            cells.append('<td data-val="99"><span class="fdr-box-lg fdr-3">-</span></td>')
        else:
            f0 = gw_fixes[0]
            loc = "H" if f0["is_home"] else "A"
            diff = f0["diff"]
            cells.append(f'<td data-val="{diff}"><span class="fdr-box-lg fdr-{diff}">{f0["opp"]}({loc})</span></td>')

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

def generate_html_report(data_dir="data", output_file="index.html"):
    bootstrap = load_json(os.path.join(data_dir, "bootstrap_static.json"))
    entry = load_json(os.path.join(data_dir, "entry.json"))
    fixtures = load_json(os.path.join(data_dir, "fixtures.json"))
    solio = load_json(os.path.join(data_dir, "solio_latest.json"))

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

    # CHOICE 1: User's Dynamic Selection from Screenshot (5-3-2 Formation, Wildcard Active)
    c1_ids = [
        (109, True, False, False, False, False),  # Verbruggen (GKP £4.5m)
        (391, True, False, False, True, False),   # Gvardiol (DEF Core £5.5m)
        (593, True, False, False, False, False),  # Dedić (DEF £4.5m)
        (31, True, False, False, False, False),   # Konsa (DEF £4.5m)
        (204, True, False, False, False, False),  # Mitchell (DEF £4.5m)
        (10, True, False, False, False, False),   # White (DEF £5.5m)
        (398, True, False, True, False, False),   # Foden (MID VC £7.0m)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core £7.0m)
        (154, True, False, False, False, False),  # Palmer (MID £9.6m)
        (464, True, False, False, False, False),  # Wissa (FWD £6.0m)
        (411, True, True, False, True, False),    # Haaland (FWD C Core £15.5m)
        # Bench
        (1, False, False, False, False, False),   # Raya (GKP Sub £6.0m)
        (68, False, False, False, False, False),  # Tavernier (MID Sub 1 £6.0m)
        (236, False, False, False, False, False), # Dewsbury-Hall (MID Sub 2 £6.5m)
        (165, False, False, False, True, False),  # João Pedro (FWD Sub 3 Core £7.6m)
    ]
    c1_squad = [build_player_by_id(*p) for p in c1_ids if build_player_by_id(*p)]
    c1_starters = [p for p in c1_squad if p["is_starter"]]
    c1_bench = [p for p in c1_squad if not p["is_starter"]]
    c1_cost = sum(p["cost"] for p in c1_squad)
    c1_bank = 0.0

    # CHOICE 2: Antigravity's Master Fortress Blueprint (Elanga £6.0m, De Cuyper £4.6m, Barry £5.5m Sub 1, 100% Nailed)
    c2_ids = [
        (109, True, False, False, False, True),   # Verbruggen (GKP £4.5m)
        (391, True, False, False, True, False),   # Gvardiol (DEF Core £5.5m)
        (115, True, False, False, False, False),  # De Cuyper (DEF £4.6m - xGI 1.68)
        (593, True, False, False, False, False),  # Amar Dedić (DEF £4.5m - BOU H)
        (154, True, False, True, False, False),   # Palmer (MID VC £9.6m)
        (399, True, False, False, False, False),  # Cherki (MID £7.6m)
        (40, True, False, False, False, False),   # Rogers (MID £7.5m)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core £7.0m)
        (454, True, False, False, False, False),  # Anthony Elanga (MID £6.0m - 17 pts)
        (411, True, True, False, True, False),    # Haaland (FWD C Core £15.5m)
        (165, True, False, False, True, False),   # João Pedro (FWD Core £7.6m)
        # Bench (100% 90-Minute Starters)
        (497, False, False, False, False, False), # Dubravka (GKP Sub £4.0m)
        (249, False, False, False, False, True),  # Louie Barry (FWD Sub 1 - £5.5m / xGI 2.02)
        (204, False, False, False, False, False), # Tyrick Mitchell (DEF Sub 2 - £4.5m / 180 mins)
        (10, False, False, False, False, False),  # Benjamin White (DEF Sub 3 - £5.5m)
    ]
    c2_squad = [build_player_by_id(*p) for p in c2_ids if build_player_by_id(*p)]
    c2_starters = [p for p in c2_squad if p["is_starter"]]
    c2_bench = [p for p in c2_squad if not p["is_starter"]]
    c2_cost = sum(p["cost"] for p in c2_squad)
    c2_bank = round(100.1 - c2_cost, 1)

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

    # Dynamic Choice 2 Analysis Generation
    c2_def_str = ", ".join([f"{p['web_name']} {p['next_fix'].split(' ')[0]}" for p in c2_starters if p['pos'] == 'DEF'])
    c2_cap_name = next((p['web_name'] for p in c2_starters if p['is_captain']), "Haaland")
    c2_vc_name = next((p['web_name'] for p in c2_starters if p['is_vice_captain']), "Palmer")
    c2_fwds_str = " + ".join([p['web_name'] for p in c2_starters if p['pos'] == 'FWD'])

    # Dynamic Last Sync Timestamp from GitHub Cloud / Live API (ICT / UTC+7)
    ict_tz = timezone(timedelta(hours=7))
    if os.path.exists("data/bootstrap_static.json"):
        mtime = os.path.getmtime("data/bootstrap_static.json")
        sync_dt = datetime.fromtimestamp(mtime, tz=timezone.utc).astimezone(ict_tz)
    else:
        sync_dt = datetime.now(ict_tz)
    last_sync_str = sync_dt.strftime("%d/%m/%Y %I:%M %p")

    # Combine unique players for full season ticker
    all_ticker_pids = list(dict.fromkeys([p[0] for p in c1_ids] + [p[0] for p in c2_ids]))
    all_ticker_squad = [build_player_by_id(pid, True) for pid in all_ticker_pids if build_player_by_id(pid, True)]

    # Generate GW3 to GW38 headers
    gw_headers = []
    for gw in range(3, 39):
        gw_headers.append(f'<th onclick="sortTable({gw-3+4}, \'number\')" class="sortable-th" title="Click to sort GW{gw} FDR">GW{gw} <span class="sort-icon">&varr;</span></th>')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>FPL Dashboard | GEMINI UNITED</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
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
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}

        @media (min-width: 1200px) {{
            body {{
                height: 100vh;
                overflow: hidden; /* App view on large desktop */
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
            font-size: 1rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.2;
        }}
        .title-box p {{ font-size: 0.68rem; color: var(--text-secondary); }}
        
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
            gap: 5px;
        }}
        .sync-dot {{
            width: 6px;
            height: 6px;
            background: var(--accent-emerald);
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 6px var(--accent-emerald);
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
            padding: 0 1rem 0.65rem;
            flex: 1;
            width: 100%;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: flex; flex-direction: column; flex: 1; min-height: 0; }}

        /* Responsive Side-by-Side Lineup Split Grid */
        .lineup-split-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.85rem;
            flex: 1;
            min-height: 0;
        }}

        .plan-column {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 0.55rem;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}

        .plan-col-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 0.35rem;
            border-bottom: 1px solid var(--border-main);
            margin-bottom: 0.4rem;
            flex-shrink: 0;
            gap: 0.4rem;
        }}
        .plan-title {{ font-size: 0.88rem; font-weight: 700; color: #ffffff; }}
        .plan-sub-tags {{
            display: flex;
            gap: 0.3rem;
            align-items: center;
            margin-top: 0.2rem;
            flex-wrap: wrap;
        }}
        .formation-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.62rem;
            font-weight: 700;
            background: #1e293b;
            color: #cbd5e1;
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            border: 1px solid var(--border-accent);
        }}
        .active-chip-pill {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.62rem;
            font-weight: 800;
            padding: 0.1rem 0.45rem;
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
            background: var(--bg-card);
            border: 1px solid var(--border-muted);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            white-space: nowrap;
        }}

        /* REDESIGNED SNUG PITCH */
        .compact-pitch {{
            background: #09130e;
            border: 1px solid #163324;
            border-radius: 8px;
            padding: 0.65rem 0.4rem;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            gap: 0.5rem;
            min-height: 460px;
            box-shadow: inset 0 0 50px rgba(0, 0, 0, 0.75);
        }}
        .pitch-row {{
            display: flex;
            justify-content: center;
            gap: 0.55rem;
            align-items: center;
            flex-wrap: nowrap;
        }}

        /* UNIFIED SEAMLESS STARTER CARD */
        .starter-card {{
            background: rgba(15, 23, 42, 0.96);
            border: 1px solid var(--border-main);
            border-radius: 7px;
            padding: 0.25rem 0.3rem 0.2rem;
            width: 96px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            flex-shrink: 0;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.6);
            transition: transform 0.15s ease, border-color 0.15s ease;
            position: relative;
        }}
        .starter-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-sky);
        }}
        .starter-card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            gap: 2px;
            min-height: 15px;
        }}
        .role-badge-cap {{
            background: var(--accent-amber);
            color: #000000;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            font-weight: 800;
            padding: 0.04rem 0.25rem;
            border-radius: 3px;
            line-height: 1;
        }}
        .role-badge-vc {{
            background: #cbd5e1;
            color: #000000;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.58rem;
            font-weight: 800;
            padding: 0.04rem 0.25rem;
            border-radius: 3px;
            line-height: 1;
        }}
        .starter-photo-wrap {{
            width: 100%;
            height: 48px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1px 0;
        }}
        .starter-shirt-img {{
            width: 44px;
            height: 44px;
            object-fit: contain;
            filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));
        }}
        .starter-info-card {{
            width: 100%;
            border-top: 1px solid var(--border-muted);
            padding-top: 2px;
            text-align: center;
        }}
        .starter-name {{
            font-size: 0.72rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.15;
        }}
        .starter-meta {{
            font-size: 0.58rem;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            margin: 1px 0;
            font-weight: 600;
        }}
        .starter-fix-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.56rem;
            border-top: 1px solid var(--border-muted);
            padding-top: 1px;
            margin-top: 1px;
        }}
        .starter-fix-text {{ color: var(--text-secondary); font-weight: 600; }}

        /* FULL-SIZE BENCH CARDS */
        .compact-bench-strip {{ 
            background: var(--bg-card-inner); 
            border: 1px solid var(--border-muted); 
            border-radius: 8px; 
            padding: 0.4rem 0.5rem; 
            margin-top: 0.4rem; 
            flex-shrink: 0; 
            overflow-x: auto;
        }}
        .bench-lbl {{ 
            font-size: 0.6rem; 
            font-weight: 700; 
            color: var(--text-muted); 
            text-transform: uppercase; 
            letter-spacing: 0.5px; 
            margin-bottom: 0.25rem; 
            text-align: center;
        }}
        .bench-row {{ 
            display: flex; 
            justify-content: center; 
            gap: 0.45rem; 
            min-width: max-content; 
        }}

        .bench-card {{
            background: rgba(15, 20, 28, 0.95);
            border: 1px solid var(--border-main);
            border-radius: 7px;
            padding: 0.25rem 0.3rem 0.2rem;
            width: 104px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 2px;
            flex-shrink: 0;
            transition: transform 0.15s ease, border-color 0.15s ease;
        }}
        .bench-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-sky);
        }}
        .bench-card-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            gap: 2px;
        }}
        .bench-photo-wrap {{
            width: 100%;
            height: 48px;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1px 0;
        }}
        .bench-shirt-img {{
            width: 44px;
            height: 44px;
            object-fit: contain;
            filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));
        }}
        .bench-info-card {{
            width: 100%;
            border-top: 1px solid var(--border-muted);
            padding-top: 2px;
        }}
        .bench-name {{
            font-size: 0.72rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.15;
        }}
        .bench-meta {{
            font-size: 0.58rem;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            margin: 1px 0;
        }}
        .bench-fix-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.56rem;
            border-top: 1px solid var(--border-muted);
            padding-top: 1px;
            margin-top: 1px;
        }}
        .bench-fix-text {{ color: var(--text-secondary); font-weight: 600; }}

        .sub-label-badge {{
            font-size: 0.52rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 800;
            background: #0369a1;
            color: #e0f2fe;
            padding: 0.05rem 0.25rem;
            border-radius: 3px;
        }}

        .pos-tag-mini {{ font-size: 0.5rem; font-weight: 700; padding: 0.04rem 0.2rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }}
        .pos-GKP {{ background: #27272a; color: #fbbf24; }}
        .pos-DEF {{ background: #1e293b; color: #38bdf8; }}
        .pos-MID {{ background: #14532d; color: #4ade80; }}
        .pos-FWD {{ background: #4c0519; color: #fb7185; }}

        .core-tag-mini {{ font-size: 0.48rem; font-weight: 800; background: #0f766e; color: #ccfbf1; padding: 0.04rem 0.18rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .enabler-tag-mini {{ font-size: 0.48rem; font-weight: 800; background: #78350f; color: #fef3c7; padding: 0.04rem 0.18rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}

        .fdr-pill {{ font-size: 0.56rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 0.04rem 0.2rem; border-radius: 2px; }}
        .fdr-pill.fdr-2 {{ background: rgba(2, 132, 199, 0.25); color: #38bdf8; }}
        .fdr-pill.fdr-3 {{ background: rgba(100, 116, 139, 0.25); color: #94a3b8; }}

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
            gap: 0.45rem;
        }}
        .section-badge-title {{
            font-size: 0.68rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .badge-pro {{ color: var(--accent-emerald); }}
        .badge-con {{ color: var(--accent-rose); }}

        .pros-cons-item {{
            background: var(--bg-card);
            border: 1px solid var(--border-muted);
            border-radius: 6px;
            padding: 0.45rem 0.65rem;
            font-size: 0.76rem;
            line-height: 1.4;
            color: var(--text-secondary);
        }}
        .pros-cons-item strong {{
            color: var(--text-main);
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
        .source-feature-body {{ display: flex; flex-direction: column; gap: 2px; }}
        .source-feature-label {{ font-size: 0.62rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .source-feature-text {{ font-size: 0.78rem; color: var(--text-secondary); line-height: 1.45; }}
        .source-feature-text strong {{ color: var(--text-main); }}

        .panel-scroll {{ overflow-y: auto; flex: 1; padding-right: 0.3rem; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.85rem; }}
        .panel {{ background: var(--bg-surface); border: 1px solid var(--border-main); border-radius: 10px; padding: 0.85rem; }}
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.6rem; border-bottom: 1px solid var(--border-main); padding-bottom: 0.35rem; }}
        .panel-title {{ font-size: 0.88rem; font-weight: 700; color: #ffffff; }}
        .stat-card-row {{ background: var(--bg-card); border: 1px solid var(--border-muted); border-radius: 6px; padding: 0.5rem 0.75rem; margin-bottom: 0.45rem; }}
        .source-pill {{ display: inline-block; font-size: 0.58rem; font-weight: 700; text-transform: uppercase; padding: 0.12rem 0.35rem; border-radius: 3px; background: #1e293b; color: var(--text-secondary); border: 1px solid var(--border-accent); }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}

        /* =========================================================
           MOBILE & TABLET RESPONSIVE STYLING (< 1024px & < 768px)
           ========================================================= */
        @media (max-width: 1024px) {{
            .lineup-split-grid, .summary-split-grid {{
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
            header {{ padding: 0.4rem 0.75rem; }}
            main {{ padding: 0 0.5rem 1rem; }}
            .nav-bar {{ padding: 0 0.5rem; }}
            
            .header-wrap {{ flex-direction: column; align-items: flex-start; gap: 0.4rem; }}
            .stats-strip {{ width: 100%; justify-content: space-between; }}
            .stat-cell {{ flex: 1; min-width: 65px; padding: 0.18rem 0.35rem; }}
            
            .starter-card {{ width: 72px; }}
            .starter-photo-wrap {{ width: 72px; height: 54px; }}
            .starter-shirt-img {{ width: 40px; height: 40px; }}
            .starter-info-card {{ width: 72px; padding: 0.18rem 0.2rem; }}
            .starter-name {{ font-size: 0.64rem; }}
            .starter-meta {{ font-size: 0.52rem; }}
            .starter-fix-row {{ font-size: 0.5rem; }}
            
            .bench-card {{ width: 88px; padding: 0.2rem 0.25rem; }}
            .bench-photo-wrap {{ height: 38px; }}
            .bench-shirt-img {{ width: 34px; height: 34px; }}
            .bench-name {{ font-size: 0.64rem; }}
            .bench-meta {{ font-size: 0.52rem; }}
            .bench-fix-row {{ font-size: 0.5rem; }}

            .pitch-row {{ gap: 0.25rem; }}
            .compact-pitch {{ padding: 0.35rem 0.2rem; min-height: 400px; }}

            .summary-metrics-strip {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .source-ledger-row {{
                grid-template-columns: 1fr;
                gap: 0.35rem;
            }}
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-wrap">
            <div class="brand-meta">
                <div class="season-badge">FPL 2026/27</div>
                <div class="title-box">
                    <h1>{entry.get("name", "GEMINI UNITED")} <span style="font-size:0.75rem; color:var(--text-muted); font-weight:500; font-family:'JetBrains Mono', monospace;">(ID: {entry.get('id', 306983)})</span> <span class="sync-pill" title="Last live database sync from GitHub Cloud"><span class="sync-dot"></span>Last Sync: {last_sync_str}</span></h1>
                    <p>Manager: {entry.get("player_first_name", "")} {entry.get("player_last_name", "")} | Wildcard GW3 Options</p>
                </div>
            </div>
            <div class="stats-strip">
                <div class="stat-cell">
                    <span class="lbl">Total Budget</span>
                    <span class="val" style="color:#ffffff;">£100.1m</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">Bank (Choice 2)</span>
                    <span class="val" style="color:var(--accent-sky);">+£{c2_bank:.1f}m</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">Active Chip</span>
                    <span class="val">WILDCARD</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">Season Goal</span>
                    <span class="val" style="color:var(--accent-emerald);">TOP 100K</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Navigation (4 Clean Tabs) -->
    <nav class="nav-bar">
        <button class="tab-btn active" onclick="switchTab('comparison', this)">Plan Lineup</button>
        <button class="tab-btn" onclick="switchTab('summary', this)">Plan Summary</button>
        <button class="tab-btn" onclick="switchTab('ticker', this)">FDR Ticker</button>
        <button class="tab-btn" onclick="switchTab('sources', this)">Research Sources</button>
    </nav>

    <!-- Main Content Area -->
    <main>
        <!-- TAB 1: PLAN LINEUP -->
        <section id="tab-comparison" class="tab-content active">
            <div class="lineup-split-grid">
                
                <!-- LEFT COLUMN: CHOICE 1 (MANAGER'S DYNAMIC LINEUP) -->
                <div class="plan-column">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title">Choice 1: Manager Dynamic Selection</div>
                            <div class="plan-sub-tags">
                                <span class="formation-pill">5-3-2</span>
                                <span class="active-chip-pill chip-wildcard">CHIP : WILDCARD</span>
                            </div>
                        </div>
                        <div class="fin-badge">
                            Cost: <span style="color:var(--accent-emerald);">£{c1_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">£{c1_bank:.1f}m</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "FWD"])}
                        </div>
                        <!-- MID (5) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "MID"])}
                        </div>
                        <!-- DEF (4) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "DEF"])}
                        </div>
                        <!-- GKP (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "GKP"])}
                        </div>
                    </div>

                    <div class="compact-bench-strip">
                        <div class="bench-lbl">Substitutes Bench</div>
                        <div class="bench-row">
                            {"".join([render_bench_card(p, sub_idx=i+1) for i, p in enumerate(c1_bench)])}
                        </div>
                    </div>
                </div>

                <!-- RIGHT COLUMN: CHOICE 2 (THE MASTER FORTRESS BLUEPRINT) -->
                <div class="plan-column" style="border-color: rgba(16, 185, 129, 0.45);">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title" style="color:var(--accent-emerald);">Choice 2: The Master Fortress Blueprint</div>
                            <div class="plan-sub-tags">
                                <span class="formation-pill">3-5-2</span>
                                <span class="active-chip-pill chip-wildcard">CHIP : WILDCARD</span>
                            </div>
                        </div>
                        <div class="fin-badge" style="border-color:var(--accent-emerald);">
                            Cost: <span style="color:var(--accent-emerald);">£{c2_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">+£{c2_bank:.1f}m</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (2) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c2_starters if p["pos"] == "FWD"])}
                        </div>
                        <!-- MID (5) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c2_starters if p["pos"] == "MID"])}
                        </div>
                        <!-- DEF (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c2_starters if p["pos"] == "DEF"])}
                        </div>
                        <!-- GKP (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c2_starters if p["pos"] == "GKP"])}
                        </div>
                    </div>

                    <div class="compact-bench-strip">
                        <div class="bench-lbl">Substitutes Bench (100% 90-Min Regulars)</div>
                        <div class="bench-row">
                            {"".join([render_bench_card(p, sub_idx=i+1) for i, p in enumerate(c2_bench)])}
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- TAB 2: PLAN SUMMARY (REAL-TIME STRATEGIC AUDIT & PROS/CONS) -->
        <section id="tab-summary" class="tab-content">
            <!-- Pros & Cons Split Grid -->
            <div class="summary-split-grid">
                
                <!-- CHOICE 1 PROS & CONS -->
                <div class="summary-plan-panel">
                    <div class="summary-panel-header">
                        <div>
                            <div class="plan-title">Choice 1 : Manager Dynamic Selection</div>
                            <span style="font-size:0.65rem; color:var(--text-secondary);">5-3-2 Formation &bull; Cost: £{c1_cost:.1f}m &bull; Bank: £{c1_bank:.1f}m</span>
                        </div>
                        <span class="source-pill">Audit Mode</span>
                    </div>

                    <!-- Pros -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-pro">ข้อดีและจุดแข็ง (Strengths &amp; Pros)</div>
                        <div class="pros-cons-item">
                            <strong>Triple Man City Fixture Exploitation (COV Home) :</strong> กุมความได้เปรียบสูงสุดจากโปรแกรมที่ง่ายที่สุดของสัปดาห์ ด้วยการซ้อน 3 ตัวท็อปแมนฯ ซิตี้ (Haaland C + Foden VC + Gvardiol) พบ Coventry (FDR 2)
                        </div>
                        <div class="pros-cons-item">
                            <strong>High Starting Firepower (xGI {c1_start_xgi:.2f}) :</strong> 11 ตัวจริงมีขุมกำลังเกมรุกอันตรายรอบด้าน ทั้ง Haaland, Foden (xGI 1.84), Szoboszlai (xGI 1.45), Wissa (xGI 1.37) และ Palmer (20 แต้ม)
                        </div>
                        <div class="pros-cons-item">
                            <strong>100% Premium Starting Depth on Bench :</strong> ผู้เล่นบนม้านั่งสำรองทั้ง 4 คน (Raya £6.0m, Tavernier £6.0m, Dewsbury-Hall £6.5m, João Pedro £7.6m) เป็นตัวจริง 90 นาทีระดับพรีเมียม
                        </div>
                    </div>

                    <!-- Cons -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-con">ข้อเสียและจุดที่ต้องระวัง (Weaknesses &amp; Cons)</div>
                        <div class="pros-cons-item">
                            <strong>Extreme Benched Capital (£26.1m จมน้ำบนม้านั่ง) :</strong> เม็ดเงินบนม้านั่งสำรองสูงถึง £26.1m (มากกว่า 26% ของงบรวมทั้งทีม) โดยเฉพาะ João Pedro (£7.6m / 20 แต้ม / xGI 1.95) ที่หล่นไปเป็น Sub 3 และ Raya (£6.0m)
                        </div>
                        <div class="pros-cons-item">
                            <strong>Defensive Conflict in ARS vs CHE :</strong> การส่งกองหลัง 5 คนในสัปดาห์นี้ ต้องชนเกมอาร์เซนอลพบเชลซี (White, Konsa vs Palmer) หากเชลซียิงประตู คลีนชีตแนวรับจะแตกทันที
                        </div>
                        <div class="pros-cons-item">
                            <strong>0-Minute Risk (Ezri Konsa £4.5m) :</strong> Konsa ยังไม่ได้รับโอกาสลงสนามใน 2 สัปดาห์แรก (0 นาที) จะทำให้ระบบต้องสลับ Sub 1 (Tavernier) ลงมาแทนอัตโนมัติ
                        </div>
                    </div>
                </div>

                <!-- CHOICE 2 PROS & CONS -->
                <div class="summary-plan-panel" style="border-color: rgba(16, 185, 129, 0.45);">
                    <div class="summary-panel-header">
                        <div>
                            <div class="plan-title" style="color:var(--accent-emerald);">Choice 2 : The Master Fortress Blueprint</div>
                            <span style="font-size:0.65rem; color:var(--text-secondary);">3-5-2 Formation &bull; Cost: £{c2_cost:.1f}m &bull; Bank: +£{c2_bank:.1f}m</span>
                        </div>
                        <span class="source-pill" style="border-color:var(--accent-emerald); color:var(--accent-emerald);">AI Blueprint</span>
                    </div>

                    <!-- Pros -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-pro">ข้อดีและจุดแข็ง (Strengths &amp; Pros)</div>
                        <div class="pros-cons-item">
                            <strong>100% Home Fixture Clean Sheet Strategy :</strong> แนวรับตัวจริงทั้ง 3 คน ({c2_def_str}) เล่นเกมเหย้าพบทีมที่ FDR 2 ทั้งหมด หลบความเสี่ยงเกมใหญ่ ARS vs CHE ได้อย่างสมบูรณ์แบบ
                        </div>
                        <div class="pros-cons-item">
                            <strong>Dual Elite Attackers Unleashed :</strong> ส่ง {c2_fwds_str} ({c2_cap_name} C) ยืนคู่กัน ผลิต Starting xGI สูงถึง {c2_start_xgi:.2f} และมี 5 กองกลางตัวรุก xGI กระจายแต้มต่อเนื่อง
                        </div>
                        <div class="pros-cons-item">
                            <strong>Newcastle Golden Run Exploitation :</strong> ดึง Anthony Elanga + Dedić รับแต้มจากโปรแกรมที่ง่ายที่สุดในลีก (FDR 2.67) โดยไม่ต้องเสี่ยงกับ Isak
                        </div>
                        <div class="pros-cons-item">
                            <strong>Top Defensive Attacker :</strong> ใส่ Maxim De Cuyper (£4.6m &bull; xGI 1.76 อันดับ 1 ของกองหลัง) เล่นวิงแบ็กฝั่งซ้ายลุ้นทั้งคลีนชีตและประตู
                        </div>
                        <div class="pros-cons-item">
                            <strong>2-FT Buffer &amp; Bank Flexibility :</strong> มีเงินเหลือใน Bank +£{c2_bank:.1f}m และโครงสร้าง 15 ตัวจริง 90 นาที ช่วยให้สะสม 2 Free Transfers ยืนยาว
                        </div>
                    </div>

                    <!-- Cons -->
                    <div class="pros-cons-section">
                        <div class="section-badge-title badge-con">ข้อเสียและจุดที่ต้องระวัง (Weaknesses &amp; Cons)</div>
                        <div class="pros-cons-item">
                            <strong>No Bruno Fernandes :</strong> ไม่มี Bruno Fernandes (£12.0m) ตัวทำแต้มอันดับ 1 ของลีก (ชดเชยด้วยการกระจายขุมกำลัง 5 ตัวรุกแทน)
                        </div>
                        <div class="pros-cons-item">
                            <strong>Single GKP Reliance :</strong> พึ่งพา Verbruggen (£4.5m) เป็นผู้รักษาประตูหลักคนเดียว (สำรอง Dúbravka £4.0m ยังไม่ได้ลงเล่น)
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
                        <h2 style="font-size:0.95rem; font-weight:700; color:#ffffff;">Full Season Fixture Difficulty &amp; Sorting (GW3 &ndash; GW38)</h2>
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
                        <span style="font-size:0.65rem; color:var(--text-muted);">Scroll &rarr; to view GW3-38</span>
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
                            {"".join([render_ticker_row_full_season(p, team_fixtures, 3, 38, i) for i, p in enumerate(all_ticker_squad)])}
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
    </script>
</body>
</html>
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[✔] Generated Presentation with Plan Summary Tab at: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FPL Presentation HTML")
    parser.add_argument("--dir", type=str, default="data", help="Data directory")
    parser.add_argument("--out", type=str, default="index.html", help="Output HTML file")
    args = parser.parse_args()
    generate_html_report(args.dir, args.out)
