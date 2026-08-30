#!/usr/bin/env python3
"""
FPL Presentation Generator
- Fully Responsive Design: Optimized for Desktop, iPad, and Mobile Phones (iOS & Android)
- Side-by-Side Comparison on Desktop, Clean Stacked & Scaled View on Mobile
- Clean Official FPL Team Kit Shirts from https://fantasy.premierleague.com
- FDR Ticker Legend Strip: Easy (FDR 2), Normal (FDR 3), Hard (FDR 4), Very Hard (FDR 5)
- Full Season Ticker (GW3 - GW38) Multi-Column Sorting + Reset Button
- Verified 8-Chip Roadmap & 5 Intelligence Sources Ledger
- Zero Emojis, Dark Minimalist Theme
"""

import json
import os
import argparse
from datetime import datetime

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
        cap_marker = '<span class="role-badge-starter cap">C</span>'
    elif p.get("is_vice_captain"):
        cap_marker = '<span class="role-badge-starter vc">V</span>'

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
        <div class="starter-photo-wrap">
            <img src="{fpl_shirt_url}" 
                 alt="{p['web_name']}" 
                 class="starter-shirt-img" 
                 loading="lazy" />
            {cap_marker}
            <div class="starter-badges-overlay">
                <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
                {core_tag}
                {enabler_tag}
            </div>
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

def render_bench_chip(p, sub_idx=1):
    pos_class = f"pos-{p['pos']}"
    fdr_class = f"fdr-{p['next_fdr']}"
    core_tag = '<span class="core-tag-mini">CORE</span>' if p.get("is_core") else ''
    enabler_tag = '<span class="enabler-tag-mini">VALUE</span>' if p.get("is_enabler") else ''
    sub_tag = f'<span class="sub-label-mini">S{sub_idx}</span>'

    t_code = p.get("official_team_code", 43)
    is_gkp = p.get("pos") == "GKP"
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"

    return f"""
    <div class="player-chip bench-chip">
        <div class="chip-top">
            <div style="display:flex; align-items:center; gap:2px;">
                <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
                {sub_tag}
                {core_tag}
                {enabler_tag}
            </div>
        </div>
        <div class="chip-center">
            <img src="{fpl_shirt_url}" 
                 alt="{p['web_name']}" 
                 class="bench-shirt-img" 
                 loading="lazy" />
            <div class="chip-name-box">
                <div class="chip-name" title="{p['full_name']}">{p['web_name']}</div>
                <div class="chip-team-cost">{p['team_code']} &bull; £{p['cost']:.1f}m</div>
            </div>
        </div>
        <div class="chip-meta">
            <span>FDR {p['next_fdr']}</span>
            <span class="fdr-pill {fdr_class}">{p['next_fix'].split(' ')[0]}</span>
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
            "xgi": xgi
        }

    # CHOICE 1: User's Dynamic Selection from Screenshot (Bruno Fernandes £12.0m, Egan £4.0m, Xhaka £5.5m)
    c1_ids = [
        (109, True, False, False, False, False),  # Verbruggen (GKP £4.5m)
        (391, True, False, False, True, False),   # Gvardiol (DEF Core £5.6m)
        (593, True, False, False, False, False),  # Dedić (DEF £4.5m)
        (31, True, False, False, False, False),   # Konsa (DEF £4.5m)
        (277, True, False, True, False, True),    # Egan (DEF VC £4.0m - 17 pts)
        (426, True, False, False, False, False),  # B.Fernandes (MID £12.0m - 25 pts)
        (124, True, False, False, False, True),   # Groß (MID Value £5.5m)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core £7.0m)
        (154, True, False, False, False, False),  # Palmer (MID £9.6m)
        (544, True, False, False, False, False),  # Xhaka (MID £5.5m)
        (411, True, True, False, True, False),    # Haaland (FWD C Core £15.5m)
        # Bench
        (496, False, False, False, False, False), # Kinsky (GKP Sub £4.5m)
        (165, False, False, False, True, False),  # João Pedro (FWD Sub 1 Core £7.6m)
        (10, False, False, False, False, False),  # White (DEF Sub 2 £5.5m)
        (321, False, False, False, False, True),  # Walle Egeli (FWD Sub 3 £4.5m)
    ]
    c1_squad = [build_player_by_id(*p) for p in c1_ids if build_player_by_id(*p)]
    c1_starters = [p for p in c1_squad if p["is_starter"]]
    c1_bench = [p for p in c1_squad if not p["is_starter"]]
    c1_cost = sum(p["cost"] for p in c1_squad)
    c1_bank = round(100.2 - c1_cost, 2)
    if c1_bank < 0: c1_bank = 0.0

    # CHOICE 2: Antigravity's Master Fortress Blueprint (Elanga £6.0m, De Cuyper £4.6m, Barry £5.5m Sub 1, 100% Nailed)
    c2_ids = [
        (109, True, False, False, False, True),   # Verbruggen (GKP £4.5m)
        (391, True, False, False, True, False),   # Gvardiol (DEF Core £5.6m)
        (10, True, False, False, False, False),   # White (DEF £5.5m)
        (115, True, False, False, False, False),  # De Cuyper (DEF £4.6m - xGI 1.68)
        (154, True, False, True, False, False),   # Palmer (MID VC £9.6m)
        (399, True, False, False, False, False),  # Cherki (MID £7.6m)
        (40, True, False, False, False, False),   # Rogers (MID £7.5m)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core £7.0m)
        (463, True, False, False, False, False),  # Anthony Elanga (MID £6.0m - 17 pts)
        (411, True, True, False, True, False),    # Haaland (FWD C Core £15.5m)
        (165, True, False, False, True, False),   # João Pedro (FWD Core £7.6m)
        # Bench (100% 90-Minute Starters)
        (497, False, False, False, False, False), # Dubravka (GKP Sub £4.0m)
        (249, False, False, False, False, True),  # Louie Barry (FWD Sub 1 - £5.5m / xGI 2.02)
        (204, False, False, False, False, False), # Tyrick Mitchell (DEF Sub 2 - £4.5m / 180 mins)
        (593, False, False, False, False, False), # Amar Dedić (DEF Sub 3 - £4.5m / 180 mins)
    ]
    c2_squad = [build_player_by_id(*p) for p in c2_ids if build_player_by_id(*p)]
    c2_starters = [p for p in c2_squad if p["is_starter"]]
    c2_bench = [p for p in c2_squad if not p["is_starter"]]
    c2_cost = sum(p["cost"] for p in c2_squad)
    c2_bank = 0.0

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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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

        /* Desktop specific height control */
        @media (min-width: 1025px) {{
            body {{
                height: 100vh;
                overflow: hidden; /* App mode on desktop */
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
            max-width: 1600px;
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
        
        .stats-strip {{ 
            display: flex; 
            gap: 0.4rem; 
            flex-wrap: wrap;
        }}
        .stat-cell {{
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            padding: 0.2rem 0.5rem;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            min-width: 72px;
        }}
        .stat-cell .lbl {{
            font-size: 0.54rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .stat-cell .val {{
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent-emerald);
            font-family: 'JetBrains Mono', monospace;
            line-height: 1.2;
        }}

        /* Navigation Bar */
        .nav-bar {{
            display: flex;
            gap: 0.3rem;
            max-width: 1600px;
            margin: 0.35rem auto 0;
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
            padding: 0.35rem 0.7rem;
            border-radius: 6px;
            font-size: 0.72rem;
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
            max-width: 1600px;
            margin: 0.35rem auto 0;
            padding: 0 1rem 0.75rem;
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
            margin-bottom: 0.35rem;
            flex-shrink: 0;
            gap: 0.4rem;
        }}
        .plan-title {{ font-size: 0.84rem; font-weight: 700; color: #ffffff; }}
        .fin-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 700;
            background: var(--bg-card);
            border: 1px solid var(--border-muted);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            white-space: nowrap;
        }}

        /* Compact Pitch */
        .compact-pitch {{
            background: #09130e;
            border: 1px solid #163324;
            border-radius: 8px;
            padding: 0.35rem;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            min-height: 480px;
            box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.7);
        }}
        .pitch-row {{
            display: flex;
            justify-content: center;
            gap: 0.4rem;
            align-items: flex-start;
            flex-wrap: nowrap;
        }}

        /* STARTER CARD */
        .starter-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 88px;
            transition: transform 0.15s ease;
            flex-shrink: 0;
        }}
        .starter-card:hover {{
            transform: translateY(-2px);
        }}
        .starter-photo-wrap {{
            position: relative;
            width: 88px;
            height: 64px;
            display: flex;
            justify-content: center;
            align-items: center;
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid var(--border-main);
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            overflow: hidden;
            z-index: 1;
        }}
        .starter-shirt-img {{
            width: 48px;
            height: 48px;
            object-fit: contain;
            filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));
        }}
        .starter-badges-overlay {{
            position: absolute;
            bottom: 2px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 2px;
            align-items: center;
            white-space: nowrap;
            z-index: 4;
        }}
        .role-badge-starter {{
            position: absolute;
            top: 2px;
            right: 3px;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.58rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid #000;
            z-index: 5;
        }}
        .role-badge-starter.cap {{ background: var(--accent-amber); color: #000; }}
        .role-badge-starter.vc {{ background: #cbd5e1; color: #000; }}

        .starter-info-card {{
            background: rgba(21, 27, 38, 0.98);
            border: 1px solid var(--border-main);
            border-top: none;
            border-radius: 0 0 6px 6px;
            padding: 0.2rem 0.25rem;
            width: 88px;
            text-align: center;
            z-index: 2;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        }}
        .starter-name {{
            font-size: 0.68rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.15;
        }}
        .starter-meta {{
            font-size: 0.54rem;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            margin: 1px 0;
        }}
        .starter-fix-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.52rem;
            border-top: 1px solid var(--border-muted);
            padding-top: 2px;
            margin-top: 1px;
        }}
        .starter-fix-text {{ color: var(--text-secondary); font-weight: 600; }}

        /* Bench Chip */
        .player-chip.bench-chip {{
            background: rgba(15, 20, 28, 0.95);
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 0.2rem 0.3rem;
            width: 90px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 1px;
            flex-shrink: 0;
        }}
        .chip-top {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.52rem; }}
        .chip-center {{ display: flex; align-items: center; gap: 0.3rem; margin: 1px 0; }}
        .bench-shirt-img {{ width: 24px; height: 24px; object-fit: contain; flex-shrink: 0; }}
        .chip-name-box {{ text-align: left; overflow: hidden; flex: 1; }}
        .chip-name {{ font-size: 0.68rem; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1; }}
        .chip-team-cost {{ font-size: 0.54rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }}
        .chip-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.54rem; color: var(--text-muted); border-top: 1px solid var(--border-muted); padding-top: 1px; }}

        .pos-tag-mini {{ font-size: 0.48rem; font-weight: 700; padding: 0.04rem 0.18rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }}
        .pos-GKP {{ background: #27272a; color: #fbbf24; }}
        .pos-DEF {{ background: #1e293b; color: #38bdf8; }}
        .pos-MID {{ background: #14532d; color: #4ade80; }}
        .pos-FWD {{ background: #4c0519; color: #fb7185; }}

        .core-tag-mini {{ font-size: 0.46rem; font-weight: 800; background: #0f766e; color: #ccfbf1; padding: 0.04rem 0.16rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .enabler-tag-mini {{ font-size: 0.46rem; font-weight: 800; background: #78350f; color: #fef3c7; padding: 0.04rem 0.16rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .sub-label-mini {{ font-size: 0.5rem; font-family: 'JetBrains Mono', monospace; color: var(--accent-sky); font-weight: 700; }}

        .fdr-pill {{ font-size: 0.52rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 0.04rem 0.18rem; border-radius: 2px; }}
        .fdr-pill.fdr-2 {{ background: rgba(2, 132, 199, 0.25); color: #38bdf8; }}
        .fdr-pill.fdr-3 {{ background: rgba(100, 116, 139, 0.25); color: #94a3b8; }}

        .compact-bench-strip {{ 
            background: var(--bg-card-inner); 
            border: 1px solid var(--border-muted); 
            border-radius: 6px; 
            padding: 0.3rem 0.4rem; 
            margin-top: 0.35rem; 
            flex-shrink: 0; 
            overflow-x: auto;
        }}
        .bench-lbl {{ font-size: 0.56rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.2rem; }}
        .bench-row {{ display: flex; justify-content: center; gap: 0.3rem; min-width: max-content; }}

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

        /* CHIP ROADMAP */
        .chips-section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.35rem;
        }}
        .chips-half-label {{
            font-size: 0.6rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .chip-status-strip {{
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 0.4rem;
            margin-bottom: 0.75rem;
            flex-shrink: 0;
        }}
        .chip-mini-card {{
            padding: 0.35rem 0.25rem;
            border-radius: 6px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .chip-mini-card.chip-used {{
            background: #141923;
            border: 1px solid #283141;
        }}
        .chip-mini-card.chip-used .chip-mini-title {{
            color: #64748b;
            font-size: 0.65rem;
            font-weight: 700;
            text-decoration: line-through;
        }}
        .chip-mini-card.chip-used .chip-mini-status {{
            color: #475569;
            font-size: 0.54rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .chip-mini-card.chip-avail {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid var(--accent-emerald);
        }}
        .chip-mini-card.chip-avail .chip-mini-title {{
            color: #ffffff;
            font-size: 0.65rem;
            font-weight: 700;
        }}
        .chip-mini-card.chip-avail .chip-mini-status {{
            color: var(--accent-emerald);
            font-size: 0.54rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}

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
            .lineup-split-grid {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}
            .grid-2 {{
                grid-template-columns: 1fr;
            }}
            .chip-status-strip {{
                grid-template-columns: repeat(4, 1fr);
            }}
            .compact-pitch {{
                min-height: 440px;
            }}
        }}

        @media (max-width: 768px) {{
            header {{ padding: 0.4rem 0.75rem; }}
            main {{ padding: 0 0.5rem 1rem; }}
            .nav-bar {{ padding: 0 0.5rem; }}
            
            .header-wrap {{ flex-direction: column; align-items: flex-start; gap: 0.4rem; }}
            .stats-strip {{ width: 100%; justify-content: space-between; }}
            .stat-cell {{ flex: 1; min-width: 65px; padding: 0.18rem 0.35rem; }}
            
            .starter-card {{ width: 68px; }}
            .starter-photo-wrap {{ width: 68px; height: 52px; }}
            .starter-shirt-img {{ width: 36px; height: 36px; }}
            .starter-info-card {{ width: 68px; padding: 0.15rem 0.2rem; }}
            .starter-name {{ font-size: 0.62rem; }}
            .starter-meta {{ font-size: 0.5rem; }}
            .starter-fix-row {{ font-size: 0.48rem; }}
            
            .pitch-row {{ gap: 0.2rem; }}
            .compact-pitch {{ padding: 0.25rem 0.15rem; min-height: 410px; }}

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
                    <h1>{entry.get("name", "GEMINI UNITED")}</h1>
                    <p>Manager: {entry.get("player_first_name", "")} {entry.get("player_last_name", "")} | Wildcard GW3 Options</p>
                </div>
            </div>
            <div class="stats-strip">
                <div class="stat-cell">
                    <span class="lbl">Comparison</span>
                    <span class="val" style="color:#ffffff;">Choice 1 vs 2</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">Squad Depth</span>
                    <span class="val" style="color:var(--accent-sky);">100% Starters</span>
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

    <!-- Navigation -->
    <nav class="nav-bar">
        <button class="tab-btn active" onclick="switchTab('comparison')">Plan Lineup</button>
        <button class="tab-btn" onclick="switchTab('ticker')">FDR Ticker</button>
        <button class="tab-btn" onclick="switchTab('chips')">Chip Roadmap</button>
        <button class="tab-btn" onclick="switchTab('sources')">Research Sources</button>
    </nav>

    <!-- Main Content Area -->
    <main>
        <!-- TAB 1: PLAN LINEUP (RESPONSIVE SPLIT GRID) -->
        <section id="tab-comparison" class="tab-content active">
            <div class="lineup-split-grid">
                
                <!-- LEFT COLUMN: CHOICE 1 (MANAGER'S DYNAMIC LINEUP) -->
                <div class="plan-column">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title">Choice 1: Manager Dynamic Selection</div>
                            <span style="font-size:0.65rem; color:var(--text-secondary);">Audit Mode: Strengths &amp; Weaknesses Evaluation</span>
                        </div>
                        <div class="fin-badge">
                            Cost: <span style="color:var(--accent-emerald);">£{c1_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">£{c1_bank:.1f}m</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (2) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in c1_starters if p["pos"] == "FWD"])}
                        </div>
                        <!-- MID (5) -->
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

                    <div class="compact-bench-strip">
                        <div class="bench-lbl">Substitutes Bench</div>
                        <div class="bench-row">
                            {"".join([render_bench_chip(p, sub_idx=i+1) for i, p in enumerate(c1_bench)])}
                        </div>
                    </div>
                </div>

                <!-- RIGHT COLUMN: CHOICE 2 (THE MASTER FORTRESS BLUEPRINT) -->
                <div class="plan-column" style="border-color: rgba(16, 185, 129, 0.45);">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title" style="color:var(--accent-emerald);">Choice 2: The Master Fortress Blueprint</div>
                            <span style="font-size:0.65rem; color:var(--text-secondary);">AI Autonomous Optimization &bull; 100% Starters &bull; 2-FT Buffer</span>
                        </div>
                        <div class="fin-badge" style="border-color:var(--accent-emerald);">
                            Cost: <span style="color:var(--accent-emerald);">£{c2_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">£{c2_bank:.1f}m</span>
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
                            {"".join([render_bench_chip(p, sub_idx=i+1) for i, p in enumerate(c2_bench)])}
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- TAB 2: FDR TICKER -->
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

        <!-- TAB 3: CHIP ROADMAP -->
        <section id="tab-chips" class="tab-content">
            <div class="panel-scroll" style="display:flex; flex-direction:column; gap:0.6rem;">
                
                <!-- 8 Official Season Chips Strip -->
                <div class="chips-section-header">
                    <span class="chips-half-label">First Half (GW1 - GW19)</span>
                    <span class="chips-half-label">Second Half (GW20 - GW38)</span>
                </div>
                <div class="chip-status-strip">
                    <div class="chip-mini-card chip-used" title="Used in Gameweek 1">
                        <span class="chip-mini-title">Bench Boost 1</span>
                        <span class="chip-mini-status">USED (GW1)</span>
                    </div>
                    <div class="chip-mini-card chip-used" title="Active in Gameweek 3">
                        <span class="chip-mini-title">Wildcard 1</span>
                        <span class="chip-mini-status">USED (GW3)</span>
                    </div>
                    <div class="chip-mini-card chip-avail" title="Available for GW10-15">
                        <span class="chip-mini-title">Triple Cap 1</span>
                        <span class="chip-mini-status">AVAILABLE (GW10-15)</span>
                    </div>
                    <div class="chip-mini-card chip-avail" title="Available for Festive GW17-19">
                        <span class="chip-mini-title">Free Hit 1</span>
                        <span class="chip-mini-status">AVAILABLE (GW17-19)</span>
                    </div>

                    <div class="chip-mini-card chip-avail" title="Available from GW20">
                        <span class="chip-mini-title">Wildcard 2</span>
                        <span class="chip-mini-status">AVAILABLE (GW20+)</span>
                    </div>
                    <div class="chip-mini-card chip-avail" title="Available for DGW34/37">
                        <span class="chip-mini-title">Bench Boost 2</span>
                        <span class="chip-mini-status">AVAILABLE (DGW)</span>
                    </div>
                    <div class="chip-mini-card chip-avail" title="Available for DGW34/37">
                        <span class="chip-mini-title">Triple Cap 2</span>
                        <span class="chip-mini-status">AVAILABLE (GW34/37)</span>
                    </div>
                    <div class="chip-mini-card chip-avail" title="Available for Blank GW29/32">
                        <span class="chip-mini-title">Free Hit 2</span>
                        <span class="chip-mini-status">AVAILABLE (GW29/32)</span>
                    </div>
                </div>

                <!-- Strategic Panels -->
                <div class="grid-2">
                    <div class="panel">
                        <div class="panel-header">
                            <div class="panel-title">Master Chip Strategy (38 Gameweeks Schedule)</div>
                            <span class="source-pill">AI Roadmap</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:0.45rem; font-size:0.78rem; color:var(--text-secondary);">
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW1 : Bench Boost 1 [USED]</strong>
                                <p style="font-size:0.7rem; color:var(--text-muted); margin-top:2px;">ใช้เก็บแต้มสำรองสัปดาห์เปิดฤดูกาล</p>
                            </div>
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW3 : Wildcard 1 [ACTIVE / IN-USE]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-emerald); margin-top:2px;">สร้างฐานทัพ 15 ตัวจริง Zero Deadweight &bull; ปรัชญา 2-FT Buffer</p>
                            </div>
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW7 / GW13 / GW16 : Triple Captain 1 [TARGET]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-sky); margin-top:2px;">ล็อกเป้า Haaland เกมเหย้าพบทีมน้องใหม่ (IPS / LEE / HUL)</p>
                            </div>
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW18 / GW19 : Free Hit 1 [TARGET]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-amber); margin-top:2px;">ช่วง Boxing Day & Festive Period ป้องกันการโรเตชันหนัก 3 นัด/สัปดาห์</p>
                            </div>
                        </div>
                    </div>

                    <div class="panel">
                        <div class="panel-header">
                            <div class="panel-title">Second Half Double Gameweek Strategy (GW20-38)</div>
                            <span class="source-pill">Endgame Surge</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:0.45rem; font-size:0.78rem; color:var(--text-secondary);">
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW29 : Free Hit 2 [BLANK GW]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-amber); margin-top:2px;">สัปดาห์ FA Cup ชนโปรแกรมลีก (เตะ 4-5 คู่) จัด 11 ตัวจริงเฉพาะกิจ</p>
                            </div>
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW30 / GW31 : Wildcard 2 [RESTRUCTURE]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-emerald); margin-top:2px;">ยกเครื่อง 15 ผู้เล่นเพื่อเตรียมทีมรับศึก Double Gameweeks</p>
                            </div>
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW34 : Triple Captain 2 [DGW34]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-sky); margin-top:2px;">ใช้กับกัปตันตัวท็อปที่มีโปรแกรมเตะเบิ้ล 2 แมตช์ในสัปดาห์เดียว</p>
                            </div>
                            <div class="stat-card-row">
                                <strong style="color:#fff;">GW37 : Bench Boost 2 [MEGA DGW37]</strong>
                                <p style="font-size:0.7rem; color:var(--accent-emerald); margin-top:2px;">สัปดาห์ Double Gameweek ใหญ่ที่สุด 15 ผู้เล่นเตะ 30 แมตช์เต็มอัตรา</p>
                            </div>
                        </div>
                    </div>
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
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            const target = document.getElementById('tab-' + tabId);
            if (target) target.classList.add('active');
            
            event.currentTarget.classList.add('active');
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
    print(f"[✔] Generated Responsive Presentation successfully at: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FPL Presentation HTML")
    parser.add_argument("--dir", type=str, default="data", help="Data directory")
    parser.add_argument("--out", type=str, default="index.html", help="Output HTML file")
    args = parser.parse_args()
    generate_html_report(args.dir, args.out)
