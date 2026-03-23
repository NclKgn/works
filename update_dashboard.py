#!/usr/bin/env python3
"""
update_dashboard.py
────────────────────────────────────────────────────────────────────────────
Reads données_phd.xlsx and generates dashboard.html in the same folder.
Usage:  python3 update_dashboard.py
────────────────────────────────────────────────────────────────────────────
"""

import os
import sys
from datetime import datetime, date

# ── Dependency check ────────────────────────────────────────────────────────
try:
    import openpyxl
except ImportError:
    print("⚠️  openpyxl manquant. Installation en cours…")
    os.system(f"{sys.executable} -m pip install openpyxl --quiet")
    import openpyxl

# ── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
EXCEL_FILE   = os.path.join(SCRIPT_DIR, "données_phd.xlsx")
OUTPUT_HTML  = os.path.join(SCRIPT_DIR, "dashboard.html")

# ── Section metadata ────────────────────────────────────────────────────────
SECTIONS = {
    "Biologie":         {"color": "#2d8a4e", "light": "#e8f5ec", "icon": "🔬"},
    "Biomécanique":     {"color": "#e07b2a", "light": "#fef3ea", "icon": "⚙️"},
    "Données Humaines": {"color": "#c0392b", "light": "#fdecea", "icon": "🧑‍⚕️"},
}

STATUS_STYLE = {
    "Non démarré": ("status-pending",  "Non démarré"),
    "En cours":    ("status-progress", "En cours"),
    "Terminé":     ("status-done",     "Terminé"),
    "Bloqué":      ("status-blocked",  "Bloqué"),
}

# ── Read Excel ──────────────────────────────────────────────────────────────
def read_data(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[0] or str(row[0]).startswith("ℹ️"):
            continue
        partie, sous, statut, pct, deadline, notes = (
            row[0], row[1], row[2] or "Non démarré",
            int(row[3] or 0), row[4], row[5] or ""
        )
        rows.append({
            "partie":   partie,
            "sous":     sous,
            "statut":   statut,
            "pct":      max(0, min(100, pct)),
            "deadline": deadline,
            "notes":    notes,
        })
    return rows

# ── Deadline helpers ────────────────────────────────────────────────────────
def deadline_class(dl):
    if dl is None:
        return ""
    d = dl.date() if isinstance(dl, datetime) else dl
    today = date.today()
    if d < today:
        return "dl-past"
    if (d - today).days <= 30:
        return "dl-soon"
    return ""

def fmt_deadline(dl):
    if dl is None:
        return "—"
    d = dl.date() if isinstance(dl, datetime) else dl
    return d.strftime("%d/%m/%Y")

# ── Build section summaries ─────────────────────────────────────────────────
def summarise(rows):
    sections = {}
    for r in rows:
        p = r["partie"]
        if p not in sections:
            sections[p] = {"rows": [], "done": 0}
        sections[p]["rows"].append(r)
        if r["statut"] == "Terminé":
            sections[p]["done"] += 1
    for p, s in sections.items():
        avg = sum(r["pct"] for r in s["rows"]) / len(s["rows"]) if s["rows"] else 0
        s["avg"] = round(avg, 1)
        s["total"] = len(s["rows"])
    return sections

# ── Subsection table rows HTML ──────────────────────────────────────────────
def sub_rows_html(rows, color):
    html = ""
    for r in rows:
        css_cls, label = STATUS_STYLE.get(r["statut"], ("status-pending", r["statut"]))
        dl_cls = deadline_class(r["deadline"])
        dl_str = fmt_deadline(r["deadline"])
        notes_escaped = (r["notes"] or "").replace('"', '&quot;').replace('<', '&lt;')
        notes_short = notes_escaped[:60] + ("…" if len(notes_escaped) > 60 else "")
        html += f"""
        <tr>
          <td class="sub-name">{r['sous']}</td>
          <td><span class="badge {css_cls}">{label}</span></td>
          <td class="pct-cell">
            <div class="bar-wrap"><div class="bar-fill" style="width:{r['pct']}%;background:{color}"></div></div>
            <span class="pct-num">{r['pct']}%</span>
          </td>
          <td class="dl-cell {''+dl_cls if dl_cls else ''}">{dl_str}</td>
          <td class="notes-cell" title="{notes_escaped}">{notes_short or '—'}</td>
        </tr>"""
    return html

# ── Section cards HTML ──────────────────────────────────────────────────────
def cards_html(sections):
    html = '<div class="cards">'
    for p, s in sections.items():
        meta = SECTIONS.get(p, {"color": "#555", "light": "#f5f5f5", "icon": "📋"})
        color = meta["color"]
        light = meta["light"]
        icon  = meta["icon"]
        html += f"""
      <div class="card" style="border-top:4px solid {color}">
        <div class="card-header">
          <span class="card-icon">{icon}</span>
          <span class="card-title" style="color:{color}">{p}</span>
        </div>
        <div class="card-prog-label">Progression globale</div>
        <div class="card-bar-wrap">
          <div class="card-bar-fill" style="width:{s['avg']}%;background:{color}"></div>
        </div>
        <div class="card-stats">
          <span class="card-pct" style="color:{color}">{s['avg']}%</span>
          <span class="card-count">{s['done']}/{s['total']} terminée{'s' if s['done']!=1 else ''}</span>
        </div>
      </div>"""
    html += "</div>"
    return html

# ── Accordion panels HTML ───────────────────────────────────────────────────
def panels_html(sections):
    html = '<div class="panels">'
    for i, (p, s) in enumerate(sections.items()):
        meta = SECTIONS.get(p, {"color": "#555", "light": "#f5f5f5", "icon": "📋"})
        color = meta["color"]
        light = meta["light"]
        icon  = meta["icon"]
        panel_id = f"panel-{i}"
        html += f"""
      <div class="panel">
        <button class="panel-toggle" onclick="toggle('{panel_id}')" style="border-left:5px solid {color}">
          <span>{icon} {p}</span>
          <span class="panel-meta" style="color:{color}">{s['avg']}% · {s['done']}/{s['total']} terminée{'s' if s['done']!=1 else ''}</span>
          <span class="chevron" id="chev-{panel_id}">▼</span>
        </button>
        <div class="panel-body" id="{panel_id}">
          <table class="sub-table">
            <thead>
              <tr>
                <th style="width:38%">Sous-partie</th>
                <th style="width:14%">Statut</th>
                <th style="width:22%">Progression</th>
                <th style="width:10%">Deadline</th>
                <th style="width:16%">Notes</th>
              </tr>
            </thead>
            <tbody>{sub_rows_html(s['rows'], color)}</tbody>
          </table>
        </div>
      </div>"""
    html += "</div>"
    return html

# ── Overall progress circle ─────────────────────────────────────────────────
def circle_svg(pct, color="#2d8a4e"):
    r = 70
    circ = 2 * 3.14159 * r
    dash = circ * pct / 100
    gap  = circ - dash
    return f"""
    <svg viewBox="0 0 160 160" width="160" height="160">
      <circle cx="80" cy="80" r="{r}" fill="none" stroke="#e8ecf0" stroke-width="14"/>
      <circle cx="80" cy="80" r="{r}" fill="none" stroke="{color}" stroke-width="14"
        stroke-dasharray="{dash:.1f} {gap:.1f}"
        stroke-dashoffset="{circ/4:.1f}"
        stroke-linecap="round"/>
      <text x="80" y="75" text-anchor="middle" font-size="28" font-weight="700" fill="#1a2c42">{pct}%</text>
      <text x="80" y="98" text-anchor="middle" font-size="12" fill="#7f8c8d">complété</text>
    </svg>"""

# ── Full HTML ────────────────────────────────────────────────────────────────
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PhD Dashboard — Suivi de la collecte de données</title>
<style>
/* ── Reset & Base ── */
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, Arial, sans-serif;
  background: #f0f4f8;
  color: #1a2c42;
  min-height: 100vh;
}}

/* ── Header ── */
.site-header {{
  background: linear-gradient(135deg, #1a2c42 0%, #243b55 100%);
  color: #fff;
  padding: 28px 40px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 20px rgba(0,0,0,.25);
}}
.site-header h1 {{
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -.3px;
}}
.site-header .subtitle {{
  font-size: .85rem;
  opacity: .65;
  margin-top: 4px;
}}
.header-right {{
  text-align: right;
  font-size: .8rem;
  opacity: .6;
}}

/* ── Layout ── */
.main {{ max-width: 1200px; margin: 0 auto; padding: 36px 28px 60px; }}

/* ── Overview strip ── */
.overview {{
  display: flex;
  align-items: center;
  gap: 40px;
  background: #fff;
  border-radius: 16px;
  padding: 28px 36px;
  margin-bottom: 32px;
  box-shadow: 0 2px 16px rgba(26,44,66,.08);
}}
.overview-text h2 {{ font-size: 1.1rem; color: #7f8c8d; font-weight: 500; margin-bottom: 6px; }}
.overview-text .big {{ font-size: 2.6rem; font-weight: 800; color: #1a2c42; line-height: 1; }}
.overview-text .sub {{ font-size: .9rem; color: #95a5a6; margin-top: 6px; }}
.overview-stats {{
  display: flex; gap: 28px; margin-left: auto;
}}
.stat-box {{
  text-align: center;
  padding: 14px 20px;
  border-radius: 12px;
  background: #f7f9fb;
  min-width: 90px;
}}
.stat-box .val {{ font-size: 1.8rem; font-weight: 700; }}
.stat-box .lbl {{ font-size: .72rem; color: #7f8c8d; margin-top: 3px; text-transform: uppercase; letter-spacing: .5px; }}

/* ── Cards ── */
.cards {{
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}}
.card {{
  background: #fff;
  border-radius: 14px;
  padding: 22px 24px;
  box-shadow: 0 2px 14px rgba(26,44,66,.07);
  transition: transform .18s ease, box-shadow .18s ease;
  cursor: default;
}}
.card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 28px rgba(26,44,66,.13); }}
.card-header {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }}
.card-icon {{ font-size: 1.4rem; }}
.card-title {{ font-size: 1.05rem; font-weight: 700; }}
.card-prog-label {{ font-size: .75rem; color: #7f8c8d; margin-bottom: 6px; text-transform: uppercase; letter-spacing: .5px; }}
.card-bar-wrap {{ height: 8px; background: #edf0f3; border-radius: 999px; overflow: hidden; margin-bottom: 10px; }}
.card-bar-fill {{ height: 100%; border-radius: 999px; transition: width .6s ease; }}
.card-stats {{ display: flex; justify-content: space-between; align-items: baseline; }}
.card-pct {{ font-size: 1.5rem; font-weight: 700; }}
.card-count {{ font-size: .8rem; color: #7f8c8d; }}

/* ── Section label ── */
.section-label {{
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #7f8c8d;
  margin-bottom: 14px;
}}

/* ── Accordion panels ── */
.panels {{ display: flex; flex-direction: column; gap: 10px; }}
.panel {{ background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(26,44,66,.06); }}
.panel-toggle {{
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: #fff;
  border: none;
  cursor: pointer;
  font-size: .98rem;
  font-weight: 600;
  color: #1a2c42;
  text-align: left;
  gap: 12px;
  transition: background .15s;
}}
.panel-toggle:hover {{ background: #f7f9fb; }}
.panel-meta {{ font-size: .82rem; font-weight: 500; margin-left: auto; }}
.chevron {{ font-size: .75rem; transition: transform .25s; color: #95a5a6; }}
.chevron.open {{ transform: rotate(180deg); }}
.panel-body {{ display: none; border-top: 1px solid #edf0f3; overflow-x: auto; }}
.panel-body.open {{ display: block; }}

/* ── Subsection table ── */
.sub-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: .88rem;
}}
.sub-table thead th {{
  background: #f7f9fb;
  padding: 10px 14px;
  text-align: left;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .5px;
  color: #7f8c8d;
  border-bottom: 1px solid #edf0f3;
}}
.sub-table tbody tr {{ border-bottom: 1px solid #f3f5f7; transition: background .12s; }}
.sub-table tbody tr:hover {{ background: #f9fbfc; }}
.sub-table td {{ padding: 11px 14px; vertical-align: middle; }}
.sub-name {{ font-weight: 500; }}

/* ── Badges ── */
.badge {{
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: .72rem;
  font-weight: 700;
  letter-spacing: .3px;
  white-space: nowrap;
}}
.status-pending  {{ background: #edf0f3; color: #636e72; }}
.status-progress {{ background: #dbeafe; color: #1d4ed8; }}
.status-done     {{ background: #dcfce7; color: #166534; }}
.status-blocked  {{ background: #fee2e2; color: #991b1b; }}

/* ── Progress bar in table ── */
.pct-cell {{ display: flex; align-items: center; gap: 8px; }}
.bar-wrap {{ flex: 1; height: 6px; background: #edf0f3; border-radius: 999px; overflow: hidden; min-width: 70px; }}
.bar-fill {{ height: 100%; border-radius: 999px; transition: width .5s ease; }}
.pct-num {{ font-size: .78rem; font-weight: 600; color: #1a2c42; min-width: 34px; text-align: right; }}

/* ── Deadline ── */
.dl-cell {{ white-space: nowrap; font-size: .85rem; }}
.dl-past {{ color: #c0392b; font-weight: 700; }}
.dl-soon {{ color: #e07b2a; font-weight: 600; }}

/* ── Notes ── */
.notes-cell {{ color: #636e72; font-size: .82rem; max-width: 200px; cursor: help; }}

/* ── Footer ── */
.footer {{
  text-align: center;
  margin-top: 48px;
  font-size: .75rem;
  color: #aab2bd;
  padding-bottom: 24px;
}}

@media (max-width: 820px) {{
  .cards {{ grid-template-columns: 1fr; }}
  .overview {{ flex-direction: column; gap: 20px; }}
  .overview-stats {{ flex-wrap: wrap; justify-content: center; }}
}}
</style>
</head>
<body>

<header class="site-header">
  <div>
    <h1>PhD Dashboard — Suivi de la collecte de données</h1>
    <div class="subtitle">Tableau de bord de recherche doctorale</div>
  </div>
  <div class="header-right">
    Dernière mise à jour<br>
    <strong>{updated}</strong>
  </div>
</header>

<main class="main">

  <!-- ── Overview ── -->
  <div class="overview">
    {circle}
    <div class="overview-text">
      <h2>Avancement global</h2>
      <div class="big">{global_pct}%</div>
      <div class="sub">{done_count} sous-partie{done_pl} terminée{done_pl} sur {total_count}</div>
    </div>
    <div class="overview-stats">
      <div class="stat-box">
        <div class="val" style="color:#2d8a4e">{stat_bio}</div>
        <div class="lbl">Biologie</div>
      </div>
      <div class="stat-box">
        <div class="val" style="color:#e07b2a">{stat_biom}</div>
        <div class="lbl">Biomécanique</div>
      </div>
      <div class="stat-box">
        <div class="val" style="color:#c0392b">{stat_hum}</div>
        <div class="lbl">Données<br>Humaines</div>
      </div>
    </div>
  </div>

  <!-- ── Cards ── -->
  <div class="section-label">Avancement par section</div>
  {cards}

  <!-- ── Panels ── -->
  <div class="section-label">Détail par sous-partie</div>
  {panels}

</main>

<div class="footer">Généré automatiquement par update_dashboard.py · {updated}</div>

<script>
function toggle(id) {{
  const body = document.getElementById(id);
  const chev = document.getElementById('chev-' + id);
  const open = body.classList.contains('open');
  body.classList.toggle('open', !open);
  chev.classList.toggle('open', !open);
}}
// Open all panels by default
document.querySelectorAll('.panel-body').forEach(p => {{
  p.classList.add('open');
  const chev = document.getElementById('chev-' + p.id);
  if (chev) chev.classList.add('open');
}});
</script>
</body>
</html>
"""

# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"❌  Fichier introuvable : {EXCEL_FILE}")
        sys.exit(1)

    print(f"📖  Lecture de {os.path.basename(EXCEL_FILE)}…")
    rows = read_data(EXCEL_FILE)
    sections = summarise(rows)

    total_count = len(rows)
    done_count  = sum(1 for r in rows if r["statut"] == "Terminé")
    global_pct  = round(sum(r["pct"] for r in rows) / total_count) if total_count else 0

    stat_bio  = f"{sections.get('Biologie',         {}).get('avg', 0):.0f}%"
    stat_biom = f"{sections.get('Biomécanique',     {}).get('avg', 0):.0f}%"
    stat_hum  = f"{sections.get('Données Humaines', {}).get('avg', 0):.0f}%"

    # Pick circle color based on progress
    circ_color = "#2d8a4e" if global_pct >= 50 else "#e07b2a" if global_pct >= 25 else "#c0392b"

    done_pl = "s" if done_count != 1 else ""

    html = HTML_TEMPLATE.format(
        updated    = datetime.now().strftime("%d/%m/%Y à %H:%M"),
        circle     = circle_svg(global_pct, circ_color),
        global_pct = global_pct,
        done_count = done_count,
        done_pl    = done_pl,
        total_count= total_count,
        stat_bio   = stat_bio,
        stat_biom  = stat_biom,
        stat_hum   = stat_hum,
        cards      = cards_html(sections),
        panels     = panels_html(sections),
    )

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅  Dashboard généré : {OUTPUT_HTML}")
    print(f"    → Ouvrez dashboard.html dans votre navigateur pour visualiser.")

if __name__ == "__main__":
    main()
