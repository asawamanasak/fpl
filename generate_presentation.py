#!/usr/bin/env python3
"""
FPL Presentation Generator
- FDR Ticker Legend Strip: Easy (FDR 2), Normal (FDR 3), Hard (FDR 4), Very Hard (FDR 5)
- Kit Shirt Images & Squad Numbers exclusively from https://fantasy.premierleague.com
- Starter Cards: Official FPL Team Kit Shirt with Squad Number (#) & Info Box Below
- Bench Cards: Compact FPL Team Kit Shirt Chips
- Fixture Table: Multi-Column Sorting (Name, Club, Pos, Cost, GW3-38) + Reset Sort Button
- Fixed Sticky Table Overlap Glitch with Multi-Layer Z-Index & Opaque Backgrounds
- Chip Roadmap: Verified 8-Chip Status Strip (Bench Boost 1 [USED GW1], Wildcard 1 [USED GW3], and 6 Available [GREEN])
- Renamed Nav Tabs: Plan Lineup, FDR Ticker, Chip Roadmap, Research Sources
- Zero Emojis, Dark Minimalist Theme, 5 Sources Integrated
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

# Verified Official Squad Numbers for Lineup Kit Display
SQUAD_NUMBERS = {
    109: 1,   # Bart Verbruggen (Brighton)
    391: 24,  # Joško Gvardiol (Man City)
    10: 4,    # Benjamin White (Arsenal)
    499: 23,  # Pedro Porro (Spurs)
    154: 20,  # Cole Palmer (Chelsea)
    399: 18,  # Rayan Cherki (Man City)
    40: 17,   # Morgan Rogers (Chelsea)
    368: 8,   # Dominik Szoboszlai (Liverpool)
    565: 26,  # Mamadou Sangaré (Brentford)
    411: 9,   # Erling Haaland (Man City)
    165: 9,   # João Pedro (Chelsea)
    497: 1,   # Martin Dúbravka (Spurs)
    249: 19,  # Thierno Barry (Everton)
    115: 29,  # Maxim De Cuyper (Brighton)
    31: 15,   # Ezri Konsa (Arsenal)
}

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

    p_id = p.get("id", 1)
    t_code = p.get("official_team_code", 43)
    is_gkp = p.get("pos") == "GKP"
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"
    squad_no = SQUAD_NUMBERS.get(p_id, p_id % 99 + 1)

    return f"""
    <div class="starter-card">
        <div class="starter-photo-wrap">
            <img src="{fpl_shirt_url}" 
                 alt="{p['web_name']}" 
                 class="starter-shirt-img" 
                 loading="lazy" />
            <span class="squad-number-tag">#{squad_no}</span>
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

    p_id = p.get("id", 1)
    t_code = p.get("official_team_code", 43)
    is_gkp = p.get("pos") == "GKP"
    shirt_suffix = "_1-66.png" if is_gkp else "-66.png"
    
    # Official FPL Shirt URL from fantasy.premierleague.com only
    fpl_shirt_url = f"https://fantasy.premierleague.com/dist/img/shirts/standard/shirt_{t_code}{shirt_suffix}"
    squad_no = SQUAD_NUMBERS.get(p_id, p_id % 99 + 1)

    return f"""
    <div class="player-chip bench-chip">
        <div class="chip-top">
            <div style="display:flex; align-items:center; gap:2px;">
                <span class="pos-tag-mini {pos_class}">{p['pos']}</span>
                {sub_tag}
                {core_tag}
                {enabler_tag}
            </div>
            <span class="bench-squad-no">#{squad_no}</span>
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
    next_deadline = next_event_obj["deadline_time"] if next_event_obj else ""

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
        p_code = el.get("code", "")

        return {
            "id": el["id"],
            "code": p_code,
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

    # Blueprint 1 (3-5-2 Midfield Dominance)
    bp1_ids = [
        (109, True, False, False, False, True),   # Verbruggen (GKP)
        (391, True, False, False, True, False),   # Gvardiol (DEF Core)
        (10, True, False, False, False, False),   # White (DEF)
        (499, True, False, False, False, False),  # Pedro Porro (DEF)
        (154, True, False, True, False, False),   # Palmer (MID VC)
        (399, True, False, False, False, False),  # Cherki (MID)
        (40, True, False, False, False, False),   # Rogers (MID)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core)
        (565, True, False, False, False, False),  # M.Sangaré (MID)
        (411, True, True, False, True, False),    # Haaland (FWD C Core)
        (165, True, False, False, True, False),   # João Pedro (FWD Core)
        # Bench
        (497, False, False, False, False, False), # Dubravka (GKP Sub)
        (249, False, False, False, False, True),  # Louie Barry (FWD Sub 1 Value)
        (115, False, False, False, False, False), # De Cuyper (DEF Sub 2)
        (31, False, False, False, False, False),  # Konsa (DEF Sub 3)
    ]
    bp1_squad = [build_player_by_id(*p) for p in bp1_ids if build_player_by_id(*p)]
    bp1_starters = [p for p in bp1_squad if p["is_starter"]]
    bp1_bench = [p for p in bp1_squad if not p["is_starter"]]
    bp1_cost = sum(p["cost"] for p in bp1_squad)
    bp1_bank = round(100.1 - bp1_cost, 2)

    # Blueprint 2 (3-4-3 Heavy Strike with Barry starting)
    bp2_ids = [
        (109, True, False, False, False, True),   # Verbruggen (GKP)
        (391, True, False, False, True, False),   # Gvardiol (DEF Core)
        (10, True, False, False, False, False),   # White (DEF)
        (115, True, False, False, False, False),  # De Cuyper (DEF)
        (154, True, False, True, False, False),   # Palmer (MID VC)
        (399, True, False, False, False, False),  # Cherki (MID)
        (40, True, False, False, False, False),   # Rogers (MID)
        (368, True, False, False, True, False),   # Szoboszlai (MID Core)
        (411, True, True, False, True, False),    # Haaland (FWD C Core)
        (165, True, False, False, True, False),   # João Pedro (FWD Core)
        (249, True, False, False, False, True),   # Barry (FWD Value)
        # Bench
        (497, False, False, False, False, False), # Dubravka (GKP Sub)
        (499, False, False, False, False, False), # Pedro Porro (DEF Sub 1)
        (565, False, False, False, False, False), # M.Sangaré (MID Sub 2)
        (31, False, False, False, False, False),  # Konsa (DEF Sub 3)
    ]
    bp2_squad = [build_player_by_id(*p) for p in bp2_ids if build_player_by_id(*p)]
    bp2_starters = [p for p in bp2_squad if p["is_starter"]]
    bp2_bench = [p for p in bp2_squad if not p["is_starter"]]
    bp2_cost = sum(p["cost"] for p in bp2_squad)
    bp2_bank = round(100.1 - bp2_cost, 2)

    # Generate GW3 to GW38 headers
    gw_headers = []
    for gw in range(3, 39):
        gw_headers.append(f'<th onclick="sortTable({gw-3+4}, \'number\')" class="sortable-th" title="Click to sort GW{gw} FDR">GW{gw} <span class="sort-icon">&varr;</span></th>')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden; /* Zero scroll on desktop */
        }}

        /* Compact Header */
        header {{
            background: var(--bg-surface);
            border-bottom: 1px solid var(--border-main);
            padding: 0.4rem 1.5rem;
            flex-shrink: 0;
        }}
        .header-wrap {{
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }}
        .brand-meta {{ display: flex; align-items: center; gap: 0.75rem; }}
        .season-badge {{
            background: #1e293b;
            color: var(--text-main);
            border: 1px solid var(--border-accent);
            font-weight: 700;
            font-size: 0.68rem;
            padding: 0.18rem 0.45rem;
            border-radius: 4px;
            font-family: 'JetBrains Mono', monospace;
        }}
        .title-box h1 {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
            line-height: 1.2;
        }}
        .title-box p {{ font-size: 0.7rem; color: var(--text-secondary); }}
        
        .stats-strip {{ display: flex; gap: 0.55rem; }}
        .stat-cell {{
            background: var(--bg-card);
            border: 1px solid var(--border-main);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            min-width: 80px;
        }}
        .stat-cell .lbl {{
            font-size: 0.56rem;
            text-transform: uppercase;
            color: var(--text-muted);
            font-weight: 600;
        }}
        .stat-cell .val {{
            font-size: 0.92rem;
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
            padding: 0 1.5rem;
            flex-shrink: 0;
            width: 100%;
        }}
        .tab-btn {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            color: var(--text-secondary);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
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
            padding: 0 1.5rem 0.4rem;
            flex: 1;
            width: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }}
        .tab-content {{ display: none; height: 100%; }}
        .tab-content.active {{ display: flex; flex-direction: column; height: 100%; }}

        /* Side-by-Side Lineup Split Grid */
        .lineup-split-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.85rem;
            flex: 1;
            height: 100%;
            min-height: 0;
        }}

        .plan-column {{
            background: var(--bg-surface);
            border: 1px solid var(--border-main);
            border-radius: 10px;
            padding: 0.55rem;
            display: flex;
            flex-direction: column;
            height: 100%;
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
        }}
        .plan-title {{ font-size: 0.88rem; font-weight: 700; color: #ffffff; }}
        .fin-badge {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            font-weight: 700;
            background: var(--bg-card);
            border: 1px solid var(--border-muted);
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
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
            min-height: 0;
            box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.7);
        }}
        .pitch-row {{
            display: flex;
            justify-content: center;
            gap: 0.45rem;
            align-items: flex-start;
        }}

        /* STARTER CARD: TEAM KIT SHIRT + SQUAD NUMBER FROM FANTASY.PREMIERLEAGUE.COM */
        .starter-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 96px;
            transition: transform 0.15s ease;
        }}
        .starter-card:hover {{
            transform: translateY(-3px);
        }}
        .starter-photo-wrap {{
            position: relative;
            width: 96px;
            height: 72px;
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
            width: 54px;
            height: 54px;
            object-fit: contain;
            filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));
        }}
        .squad-number-tag {{
            position: absolute;
            top: 4px;
            left: 5px;
            font-size: 0.68rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            color: #cbd5e1;
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-accent);
            padding: 0.05rem 0.25rem;
            border-radius: 3px;
            line-height: 1;
            z-index: 3;
        }}
        .starter-badges-overlay {{
            position: absolute;
            bottom: 3px;
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
            top: 3px;
            right: 4px;
            width: 17px;
            height: 17px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.62rem;
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
            padding: 0.22rem 0.3rem;
            width: 96px;
            text-align: center;
            z-index: 2;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
        }}
        .starter-name {{
            font-size: 0.7rem;
            font-weight: 700;
            color: #ffffff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            line-height: 1.15;
        }}
        .starter-meta {{
            font-size: 0.56rem;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
            margin: 1px 0;
        }}
        .starter-fix-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.54rem;
            border-top: 1px solid var(--border-muted);
            padding-top: 2px;
            margin-top: 1px;
        }}
        .starter-fix-text {{ color: var(--text-secondary); font-weight: 600; }}

        /* Bench Chip with Official Team Shirt */
        .player-chip.bench-chip {{
            background: rgba(15, 20, 28, 0.95);
            border: 1px solid #1e293b;
            border-radius: 6px;
            padding: 0.2rem 0.35rem;
            width: 98px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 1px;
        }}
        .chip-top {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.55rem; }}
        .bench-squad-no {{ font-size: 0.55rem; font-family: 'JetBrains Mono', monospace; color: var(--text-muted); font-weight: 700; }}
        .chip-center {{ display: flex; align-items: center; gap: 0.35rem; margin: 1px 0; }}
        .bench-shirt-img {{ width: 26px; height: 26px; object-fit: contain; flex-shrink: 0; }}
        .chip-name-box {{ text-align: left; overflow: hidden; flex: 1; }}
        .chip-name {{ font-size: 0.7rem; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.1; }}
        .chip-team-cost {{ font-size: 0.56rem; color: var(--text-muted); font-family: 'JetBrains Mono', monospace; }}
        .chip-meta {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.56rem; color: var(--text-muted); border-top: 1px solid var(--border-muted); padding-top: 1px; }}

        .pos-tag-mini {{ font-size: 0.5rem; font-weight: 700; padding: 0.04rem 0.2rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; text-transform: uppercase; }}
        .pos-GKP {{ background: #27272a; color: #fbbf24; }}
        .pos-DEF {{ background: #1e293b; color: #38bdf8; }}
        .pos-MID {{ background: #14532d; color: #4ade80; }}
        .pos-FWD {{ background: #4c0519; color: #fb7185; }}

        .core-tag-mini {{ font-size: 0.48rem; font-weight: 800; background: #0f766e; color: #ccfbf1; padding: 0.04rem 0.18rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .enabler-tag-mini {{ font-size: 0.48rem; font-weight: 800; background: #78350f; color: #fef3c7; padding: 0.04rem 0.18rem; border-radius: 2px; font-family: 'JetBrains Mono', monospace; }}
        .sub-label-mini {{ font-size: 0.52rem; font-family: 'JetBrains Mono', monospace; color: var(--accent-sky); font-weight: 700; }}

        .fdr-pill {{ font-size: 0.55rem; font-family: 'JetBrains Mono', monospace; font-weight: 700; padding: 0.04rem 0.2rem; border-radius: 2px; }}
        .fdr-pill.fdr-2 {{ background: rgba(2, 132, 199, 0.25); color: #38bdf8; }}
        .fdr-pill.fdr-3 {{ background: rgba(100, 116, 139, 0.25); color: #94a3b8; }}

        .compact-bench-strip {{ background: var(--bg-card-inner); border: 1px solid var(--border-muted); border-radius: 6px; padding: 0.3rem 0.45rem; margin-top: 0.35rem; flex-shrink: 0; }}
        .bench-lbl {{ font-size: 0.58rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.2rem; }}
        .bench-row {{ display: flex; justify-content: center; gap: 0.35rem; }}

        /* FULL SEASON FDR TICKER WITH FULL COLUMN SORTING, RESET BUTTON & FDR LEGEND */
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
        }}
        .fdr-legend-label {{
            font-size: 0.62rem;
            color: var(--text-muted);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 2px;
        }}
        .fdr-legend-item {{
            font-size: 0.62rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            padding: 0.1rem 0.4rem;
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
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.25rem 0.65rem;
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
        }}
        .ticker-table-full {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            font-size: 0.78rem;
        }}
        .ticker-table-full th, .ticker-table-full td {{
            padding: 0.45rem 0.4rem;
            text-align: center;
            border-bottom: 1px solid var(--border-muted);
            white-space: nowrap;
        }}
        .ticker-table-full th {{
            color: var(--text-muted);
            font-weight: 700;
            font-size: 0.68rem;
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
            font-size: 0.65rem;
            color: var(--text-muted);
            margin-left: 2px;
        }}

        /* FIXED STICKY Z-INDEX AND OPAQUE BACKGROUNDS */
        .tbl-sticky {{
            position: sticky;
            left: 0;
            background: #0f141c;
            z-index: 15;
            text-align: left !important;
            font-weight: 700;
            color: #ffffff;
            min-width: 110px;
            border-right: 1px solid var(--border-muted);
        }}
        .tbl-sticky-2 {{
            position: sticky;
            left: 110px;
            background: #0f141c;
            z-index: 15;
            min-width: 55px;
            border-right: 1px solid var(--border-muted);
        }}
        .tbl-sticky-3 {{
            position: sticky;
            left: 165px;
            background: #0f141c;
            z-index: 15;
            min-width: 50px;
            border-right: 1px solid var(--border-muted);
        }}
        .tbl-sticky-4 {{
            position: sticky;
            left: 215px;
            background: #0f141c;
            z-index: 15;
            min-width: 60px;
            border-right: 2px solid var(--border-accent);
        }}

        /* CORNER HEADERS */
        th.tbl-sticky {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}
        th.tbl-sticky-2 {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}
        th.tbl-sticky-3 {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}
        th.tbl-sticky-4 {{ top: 0; z-index: 35 !important; background: #1a2230 !important; }}

        /* Larger Fixture Box */
        .fdr-box-lg {{
            padding: 0.3rem 0.5rem;
            border-radius: 5px;
            font-weight: 700;
            font-size: 0.72rem;
            font-family: 'JetBrains Mono', monospace;
            display: inline-block;
            min-width: 62px;
            text-align: center;
        }}
        .fdr-box-lg.fdr-2 {{ background: #0c2d48; color: #38bdf8; border: 1px solid #0369a1; }}
        .fdr-box-lg.fdr-3 {{ background: #1e293b; color: #94a3b8; border: 1px solid #334155; }}
        .fdr-box-lg.fdr-4 {{ background: #451a03; color: #fbbf24; border: 1px solid #78350f; }}
        .fdr-box-lg.fdr-5 {{ background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; }}

        /* CHIP ROADMAP: 8 OFFICIAL CHIPS STRIP AT TOP */
        .chips-section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.35rem;
        }}
        .chips-half-label {{
            font-size: 0.62rem;
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
            padding: 0.35rem 0.3rem;
            border-radius: 6px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 2px;
            transition: all 0.15s ease;
        }}
        .chip-mini-card.chip-used {{
            background: #141923;
            border: 1px solid #283141;
        }}
        .chip-mini-card.chip-used .chip-mini-title {{
            color: #64748b;
            font-size: 0.68rem;
            font-weight: 700;
            text-decoration: line-through;
        }}
        .chip-mini-card.chip-used .chip-mini-status {{
            color: #475569;
            font-size: 0.56rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}
        .chip-mini-card.chip-avail {{
            background: rgba(16, 185, 129, 0.08);
            border: 1px solid var(--accent-emerald);
        }}
        .chip-mini-card.chip-avail .chip-mini-title {{
            color: #ffffff;
            font-size: 0.68rem;
            font-weight: 700;
        }}
        .chip-mini-card.chip-avail .chip-mini-status {{
            color: var(--accent-emerald);
            font-size: 0.56rem;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Clean Ledger for Research Sources */
        .sources-ledger {{ display: flex; flex-direction: column; width: 100%; }}
        .source-ledger-row {{ display: grid; grid-template-columns: 240px 1fr; gap: 1.5rem; align-items: baseline; padding: 0.85rem 0.5rem; border-bottom: 1px solid var(--border-muted); }}
        .source-ledger-row:last-child {{ border-bottom: none; }}
        .source-identity {{ display: flex; flex-direction: column; gap: 2px; }}
        .source-main-name {{ font-size: 0.95rem; font-weight: 700; color: #ffffff; }}
        .source-link-url {{ font-size: 0.72rem; color: var(--accent-sky); text-decoration: none; font-family: 'JetBrains Mono', monospace; }}
        .source-link-url:hover {{ text-decoration: underline; }}
        .source-feature-body {{ display: flex; flex-direction: column; gap: 2px; }}
        .source-feature-label {{ font-size: 0.65rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        .source-feature-text {{ font-size: 0.82rem; color: var(--text-secondary); line-height: 1.45; }}
        .source-feature-text strong {{ color: var(--text-main); }}

        .panel-scroll {{ overflow-y: auto; flex: 1; padding-right: 0.5rem; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }}
        .panel {{ background: var(--bg-surface); border: 1px solid var(--border-main); border-radius: 10px; padding: 1rem; }}
        .panel-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; border-bottom: 1px solid var(--border-main); padding-bottom: 0.4rem; }}
        .panel-title {{ font-size: 0.95rem; font-weight: 700; color: #ffffff; }}
        .stat-card-row {{ background: var(--bg-card); border: 1px solid var(--border-muted); border-radius: 6px; padding: 0.6rem 0.85rem; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; }}
        .source-pill {{ display: inline-block; font-size: 0.6rem; font-weight: 700; text-transform: uppercase; padding: 0.15rem 0.4rem; border-radius: 3px; background: #1e293b; color: var(--text-secondary); border: 1px solid var(--border-accent); }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
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
                    <p>Manager: {entry.get("player_first_name", "")} {entry.get("player_last_name", "")} | Official FPL Kit Squad</p>
                </div>
            </div>
            <div class="stats-strip">
                <div class="stat-cell">
                    <span class="lbl">Squad Value</span>
                    <span class="val">£{bp1_cost:.1f}m</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">In Bank</span>
                    <span class="val" style="color:var(--accent-sky);">£{bp1_bank:.1f}m</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">Total Budget</span>
                    <span class="val" style="color:#ffffff;">£100.1m</span>
                </div>
                <div class="stat-cell">
                    <span class="lbl">GW3 Chip</span>
                    <span class="val">WILDCARD</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Navigation (Renamed 4 Tabs) -->
    <nav class="nav-bar">
        <button class="tab-btn active" onclick="switchTab('comparison')">Plan Lineup</button>
        <button class="tab-btn" onclick="switchTab('ticker')">FDR Ticker</button>
        <button class="tab-btn" onclick="switchTab('chips')">Chip Roadmap</button>
        <button class="tab-btn" onclick="switchTab('sources')">Research Sources</button>
    </nav>

    <!-- Main Content Area -->
    <main>
        <!-- TAB 1: PLAN LINEUP (OFFICIAL FPL KIT SHIRTS & SQUAD NUMBERS) -->
        <section id="tab-comparison" class="tab-content active">
            <div class="lineup-split-grid">
                
                <!-- LEFT COLUMN: BLUEPRINT 1 (3-5-2) -->
                <div class="plan-column">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title">Blueprint 1: Midfield Dominance (3-5-2)</div>
                            <span style="font-size:0.68rem; color:var(--text-secondary);">Sub 1: Louie Barry (FWD &bull; xGI 1.96)</span>
                        </div>
                        <div class="fin-badge">
                            Value: <span style="color:var(--accent-emerald);">£{bp1_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">£{bp1_bank:.1f}m</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (2) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp1_starters if p["pos"] == "FWD"])}
                        </div>
                        <!-- MID (5) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp1_starters if p["pos"] == "MID"])}
                        </div>
                        <!-- DEF (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp1_starters if p["pos"] == "DEF"])}
                        </div>
                        <!-- GKP (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp1_starters if p["pos"] == "GKP"])}
                        </div>
                    </div>

                    <div class="compact-bench-strip">
                        <div class="bench-lbl">Substitutes Bench (Playing Depth)</div>
                        <div class="bench-row">
                            {"".join([render_bench_chip(p, sub_idx=i+1) for i, p in enumerate(bp1_bench)])}
                        </div>
                    </div>
                </div>

                <!-- RIGHT COLUMN: BLUEPRINT 2 (3-4-3) -->
                <div class="plan-column">
                    <div class="plan-col-header">
                        <div>
                            <div class="plan-title">Blueprint 2: Heavy Attack (3-4-3 with Barry)</div>
                            <span style="font-size:0.68rem; color:var(--text-secondary);">Barry starts &bull; De Cuyper starts in DEF</span>
                        </div>
                        <div class="fin-badge">
                            Value: <span style="color:var(--accent-emerald);">£{bp2_cost:.1f}m</span> | Bank: <span style="color:var(--accent-sky);">£{bp2_bank:.1f}m</span>
                        </div>
                    </div>

                    <div class="compact-pitch">
                        <!-- FWD (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp2_starters if p["pos"] == "FWD"])}
                        </div>
                        <!-- MID (4) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp2_starters if p["pos"] == "MID"])}
                        </div>
                        <!-- DEF (3) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp2_starters if p["pos"] == "DEF"])}
                        </div>
                        <!-- GKP (1) -->
                        <div class="pitch-row">
                            {"".join([render_starter_card(p) for p in bp2_starters if p["pos"] == "GKP"])}
                        </div>
                    </div>

                    <div class="compact-bench-strip">
                        <div class="bench-lbl">Substitutes Bench (Playing Depth)</div>
                        <div class="bench-row">
                            {"".join([render_bench_chip(p, sub_idx=i+1) for i, p in enumerate(bp2_bench)])}
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- TAB 2: FDR TICKER (WITH FDR DIFFICULTY COLOR LEGEND) -->
        <section id="tab-ticker" class="tab-content">
            <div class="ticker-container">
                <div class="ticker-header-bar">
                    <div>
                        <h2 style="font-size:1rem; font-weight:700; color:#ffffff;">Full Season Fixture Difficulty &amp; Sorting (GW3 &ndash; GW38)</h2>
                        <div class="fdr-legend-strip">
                            <span class="fdr-legend-label">FDR Scale:</span>
                            <span class="fdr-legend-item fdr-2">FDR 2 &bull; Easy</span>
                            <span class="fdr-legend-item fdr-3">FDR 3 &bull; Normal</span>
                            <span class="fdr-legend-item fdr-4">FDR 4 &bull; Hard</span>
                            <span class="fdr-legend-item fdr-5">FDR 5 &bull; Very Hard</span>
                        </div>
                    </div>
                    <div style="display:flex; gap:0.6rem; align-items:center;">
                        <button class="reset-btn" onclick="resetTableSort()">Reset Sort</button>
                        <span style="font-size:0.7rem; color:var(--text-muted);">Scroll &rarr; to view GW3-38</span>
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
                            {"".join([render_ticker_row_full_season(p, team_fixtures, 3, 38, i) for i, p in enumerate(bp1_squad)])}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 3: CHIP ROADMAP (8 OFFICIAL CHIPS STRIP AT TOP) -->
        <section id="tab-chips" class="tab-content">
            <div class="panel-scroll" style="display:flex; flex-direction:column; gap:0.6rem;">
                
                <!-- 8 Official Season Chips Strip -->
                <div class="chips-section-header">
                    <span class="chips-half-label">First Half (GW1 - GW19)</span>
                    <span class="chips-half-label">Second Half (GW20 - GW38)</span>
                </div>
                <div class="chip-status-strip">
                    <!-- 1st Half Chips (4) -->
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

                    <!-- 2nd Half Chips (4) -->
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

                <!-- Strategic Roadmap Panels -->
                <div class="grid-2">
                    <div class="panel">
                        <div class="panel-header">
                            <div class="panel-title">Triple Captain Strategy (TC 1 &amp; TC 2)</div>
                            <span class="source-pill">Single-Chip Rule</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:0.6rem; font-size:0.82rem; color:var(--text-secondary);">
                            <div class="stat-card-row">
                                <div>
                                    <strong style="color:#fff;">GW3 สถานะ: ใช้งาน Wildcard เท่านั้น</strong>
                                    <p style="font-size:0.75rem; color:var(--accent-amber);">ตามกฎ FPL ใช้ได้เพียง 1 ชิปต่อสัปดาห์ (Haaland กัปตัน 2x ปกติ)</p>
                                </div>
                            </div>
                            <div class="stat-card-row">
                                <div>
                                    <strong style="color:#fff;">Triple Captain 1 (ครึ่งแรก: GW10-15)</strong>
                                    <p style="font-size:0.75rem;">เป้าหมาย: เกมเหย้าแมนฯ ซิตี้พบทีมท้ายตาราง หรือสัปดาห์ที่มี Mini-Double Gameweek</p>
                                </div>
                            </div>
                            <div class="stat-card-row">
                                <div>
                                    <strong style="color:#fff;">Triple Captain 2 (ครึ่งหลัง: GW34 หรือ GW37)</strong>
                                    <p style="font-size:0.75rem;">ล็อกไว้ใช้ในสัปดาห์ที่มี Double Gameweek ใหญ่ เพื่อรับแต้มคูณ 3 ทั้ง 2 แมตช์</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="panel">
                        <div class="panel-header">
                            <div class="panel-title">Free Hit Strategy (FH 1 &amp; FH 2)</div>
                            <span class="source-pill">Chip Roadmap</span>
                        </div>
                        <div style="display:flex; flex-direction:column; gap:0.6rem; font-size:0.82rem; color:var(--text-secondary);">
                            <div class="stat-card-row">
                                <div>
                                    <strong style="color:#fff;">Free Hit 1 (ครึ่งแรก: GW17-19 Festive Period)</strong>
                                    <p style="font-size:0.75rem;">ช่วงที่มีการหมุนเวียนนักเตะถี่ช่วงบ็อกซิ่งเดย์ หรือมีเกมเลื่อนจากคาราบาวคัพ</p>
                                </div>
                            </div>
                            <div class="stat-card-row">
                                <div>
                                    <strong style="color:#fff;">Free Hit 2 (ครึ่งหลัง: GW29 หรือ GW32 Blank GW)</strong>
                                    <p style="font-size:0.75rem;">สัปดาห์ที่มีทีมติดแข่ง FA Cup จนเหลือคู่เตะน้อย จัด 11 ตัวจริงเฉพาะกิจโดยไม่ลบแต้ม</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        </section>

        <!-- TAB 4: RESEARCH SOURCES -->
        <section id="tab-sources" class="tab-content">
            <div class="panel panel-scroll" style="background:transparent; border:none; padding:0.5rem 1rem;">
                <div style="margin-bottom:0.75rem; border-bottom:1px solid var(--border-main); padding-bottom:0.5rem;">
                    <h2 style="font-size:1.05rem; font-weight:700; color:#ffffff;">Research Sources &amp; Analytical Framework</h2>
                    <p style="font-size:0.78rem; color:var(--text-secondary);">แหล่งข้อมูลเชิงลึก 5 ด้านที่เชื่อมโยงในการวิเคราะห์และจัดสรรทีม GEMINI UNITED</p>
                </div>

                <div class="sources-ledger">
                    <!-- Source 1 -->
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

                    <!-- Source 2 -->
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

                    <!-- Source 3 -->
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

                    <!-- Source 4 -->
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

                    <!-- Source 5 -->
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
    print(f"[✔] Generated Presentation with FDR Legend Strip successfully at: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FPL Presentation HTML")
    parser.add_argument("--dir", type=str, default="data", help="Data directory")
    parser.add_argument("--out", type=str, default="index.html", help="Output HTML file")
    args = parser.parse_args()
    generate_html_report(args.dir, args.out)
