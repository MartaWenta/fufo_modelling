"""
build_registry.py
=================
Future Forests C3 — Model Registry Builder

Reads models.yml and renders a static HTML dashboard (registry.html).
Run:  python build_registry.py
Output: registry.html  (ready for GitHub Pages)

Dependencies: pyyaml (pip install pyyaml)
"""

import yaml
from pathlib import Path
from datetime import date

# ── Load data ──────────────────────────────────────────────
with open("models.yml") as f:
    data = yaml.safe_load(f)

groups = data["groups"]

LAYER_LABELS = {
    1: "Layer 1 — Observations & Forcing",
    2: "Layer 2 — Biophysical Engine",
    3: "Layer 3 — Social & Economic",
}

LAYER_COLORS = {
    1: ("#1a7a4a", "#dcfce7", "#f0fdf7"),   # green
    2: ("#1a4f8a", "#dbeafe", "#eff6ff"),   # blue
    3: ("#8a4a0a", "#fed7aa", "#fffbeb"),   # amber
}

STATUS_BADGE = {
    "planned":        ("#94a3b8", "#f1f5f9", "Planned"),
    "in_development": ("#d97706", "#fffbeb", "In Development"),
    "operational":    ("#1a7a4a", "#dcfce7", "Operational"),
    "deprecated":     ("#c0392b", "#fee2e2", "Deprecated"),
}

def badge(status):
    c, bg, label = STATUS_BADGE.get(status, ("#64748b", "#f8fafc", status))
    return (f'<span style="background:{bg};color:{c};border:1px solid {c};'
            f'border-radius:4px;padding:2px 7px;font-size:11px;'
            f'font-family:IBM Plex Mono,monospace;font-weight:600;">{label}</span>')

def pill_list(items, color="#475569"):
    if not items:
        return '<span style="color:#94a3b8">—</span>'
    return " ".join(
        f'<span style="background:#f1f5f9;color:{color};border-radius:3px;'
        f'padding:1px 6px;font-size:11px;margin:1px;display:inline-block;">{i}</span>'
        for i in items
    )

def io_rows(items):
    if not items:
        return '<span style="color:#94a3b8">—</span>'
    rows = []
    for item in items:
        name = item.get("name", "")
        fmt  = item.get("format", "")
        src  = item.get("source", item.get("consumers", ""))
        if isinstance(src, list):
            src = ", ".join(src)
        rows.append(
            f'<div style="margin-bottom:3px;">'
            f'<span style="font-weight:600;font-size:11.5px">{name}</span>'
            f'<span style="color:#94a3b8;font-size:10.5px;margin-left:6px">{fmt}</span>'
            + (f'<span style="color:#64748b;font-size:10px;margin-left:6px">← {src}</span>' if src else "")
            + "</div>"
        )
    return "".join(rows)

def card(g):
    layer = g.get("layer", 1)
    accent, light, bg = LAYER_COLORS[layer]
    lid = g["id"]
    hire_name  = g.get("hire", {}).get("name", "TBD")
    hire_start = g.get("hire", {}).get("start", "TBD")
    hire_html  = (
        f'<span style="color:#1a7a4a;font-weight:600">{hire_name}</span>'
        if hire_name not in ("TBD", "", None)
        else '<span style="color:#94a3b8">TBD</span>'
    )
    notes = g.get("notes", "")
    langs = pill_list(g.get("language", []), accent)

    return f"""
<div class="card" id="card-{lid}"
     data-layer="{layer}"
     data-status="{g.get('status','')}"
     style="border-left:4px solid {accent};background:{bg};border-radius:8px;
            padding:16px 18px;margin-bottom:12px;transition:box-shadow .15s;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;">
    <div>
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.15em;
                  color:{accent};text-transform:uppercase;margin-bottom:3px;">
        {LAYER_LABELS[layer]}
      </div>
      <div style="font-size:17px;font-weight:700;color:#1e293b;letter-spacing:-.02em;">
        {g.get('pi','')}
        <span style="font-size:13px;font-weight:400;color:#64748b;margin-left:8px">
          {g.get('model_name','')}
        </span>
      </div>
      <div style="font-size:12px;color:#475569;margin-top:3px;">{g.get('short_description','')}</div>
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:flex-start;">
      {badge(g.get('status','planned'))}
      <span style="background:{light};color:{accent};border:1px solid {accent};border-radius:4px;
                   padding:2px 7px;font-size:11px;font-family:'IBM Plex Mono',monospace;">
        {g.get('type','').split('/')[0].strip()}
      </span>
    </div>
  </div>

  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:14px;flex-wrap:wrap;">

    <div>
      <div class="col-head">Inputs</div>
      {io_rows(g.get('inputs',[]))}
    </div>

    <div>
      <div class="col-head">Outputs</div>
      {io_rows(g.get('outputs',[]))}
    </div>

    <div>
      <div class="col-head">Languages</div>
      <div style="margin-bottom:8px">{langs}</div>
      <div class="col-head">Researcher / Start</div>
      <div style="font-size:12px">{hire_html}
        <span style="color:#94a3b8;font-size:11px;margin-left:6px">{hire_start}</span>
      </div>
      {f'<div style="margin-top:8px;font-size:11px;color:#64748b;font-style:italic">{notes}</div>' if notes else ''}
    </div>

  </div>
</div>
"""

# ── Build full page ────────────────────────────────────────
cards_by_layer = {}
for g in groups:
    l = g.get("layer", 1)
    cards_by_layer.setdefault(l, []).append(g)

sections_html = ""
for layer in sorted(cards_by_layer.keys()):
    accent, light, bg = LAYER_COLORS[layer]
    label = LAYER_LABELS[layer]
    sections_html += f"""
<div style="margin-bottom:8px;padding:6px 14px;background:{light};border-radius:6px;">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;
               letter-spacing:.14em;color:{accent};text-transform:uppercase;">{label}</span>
</div>
"""
    for g in cards_by_layer[layer]:
        sections_html += card(g)
    sections_html += "<div style='height:20px'></div>"

total = len(groups)
ops   = sum(1 for g in groups if g.get("status") == "operational")
dev   = sum(1 for g in groups if g.get("status") == "in_development")
pln   = sum(1 for g in groups if g.get("status") == "planned")
hired = sum(1 for g in groups if g.get("hire", {}).get("name") not in ("TBD", "", None))

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Future Forests C3 — Model Registry</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{
    font-family: 'IBM Plex Sans', sans-serif;
    background: #f8fafc;
    color: #1e293b;
    padding: 24px 32px;
    max-width: 1200px;
    margin: 0 auto;
  }}
  .col-head {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 9px;
    letter-spacing: .15em;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 5px;
    font-weight: 700;
  }}
  .card:hover {{ box-shadow: 0 4px 18px rgba(0,0,0,.08); }}
  .filter-bar {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 20px;
    align-items: center;
  }}
  .filter-btn {{
    background: #fff;
    border: 1.5px solid #e2e8f0;
    border-radius: 6px;
    padding: 5px 14px;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    cursor: pointer;
    transition: all .15s;
    color: #475569;
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: #1e3a5f;
    color: #fff;
    border-color: #1e3a5f;
  }}
  @media (max-width: 700px) {{
    .card > div:last-child > div[style*="grid"] {{ grid-template-columns: 1fr !important; }}
    body {{ padding: 12px 14px; }}
  }}
</style>
</head>
<body>

<div style="border-bottom:2.5px solid #1e3a5f;padding-bottom:10px;margin-bottom:20px;">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.18em;
              color:#1a7a4a;text-transform:uppercase;margin-bottom:4px;">
    Future Forests Excellence Cluster · Universität Freiburg · Research Area C3
  </div>
  <div style="font-size:24px;font-weight:700;color:#1e3a5f;letter-spacing:-.02em;">
    C3 Integrated Modelling Framework — Model Registry
  </div>
  <div style="font-size:12px;color:#64748b;margin-top:3px;">
    Models, data, formats, and researcher status across all eleven modelling groups
    · Generated {date.today().strftime("%-d %B %Y")}
  </div>
</div>

<!-- Summary stats -->
<div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px;">
  {''.join([
    f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 18px;text-align:center;">'
    f'<div style="font-size:22px;font-weight:700;color:{c}">{v}</div>'
    f'<div style="font-size:11px;color:#64748b;font-family:IBM Plex Mono,monospace">{l}</div></div>'
    for v, l, c in [
        (total, "Total Groups", "#1e3a5f"),
        (ops,   "Operational",  "#1a7a4a"),
        (dev,   "In Development","#d97706"),
        (pln,   "Planned",      "#94a3b8"),
        (hired, "Hires Confirmed","#5b50c4"),
    ]
  ])}
</div>

<!-- Filter bar -->
<div class="filter-bar">
  <span style="font-size:11px;color:#94a3b8;font-family:'IBM Plex Mono',monospace">FILTER:</span>
  <button class="filter-btn active" onclick="filterCards('all',this)">All</button>
  <button class="filter-btn" onclick="filterCards('layer-1',this)">Layer 1</button>
  <button class="filter-btn" onclick="filterCards('layer-2',this)">Layer 2</button>
  <button class="filter-btn" onclick="filterCards('layer-3',this)">Layer 3</button>
  <button class="filter-btn" onclick="filterCards('operational',this)">Operational</button>
  <button class="filter-btn" onclick="filterCards('in_development',this)">In Development</button>
  <button class="filter-btn" onclick="filterCards('planned',this)">Planned</button>
</div>

{sections_html}

<div style="text-align:center;font-size:10px;color:#94a3b8;font-family:'IBM Plex Mono',monospace;
            margin-top:20px;padding-top:12px;border-top:1px solid #e2e8f0;">
  Source: models.yml · Scientific Modelling Coordinator · Future Forests C3
  · <a href="FuFo_Original_Fullpage.html" style="color:#1a4f8a">↗ Connection Map</a>
</div>

<script>
function filterCards(filter, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {{
    if (filter === 'all') {{
      card.style.display = '';
    }} else if (filter.startsWith('layer-')) {{
      const layer = filter.replace('layer-', '');
      card.style.display = card.dataset.layer === layer ? '' : 'none';
    }} else {{
      card.style.display = card.dataset.status === filter ? '' : 'none';
    }}
  }});
  // show/hide section headers
  document.querySelectorAll('[data-section]').forEach(sec => {{
    const visible = [...sec.nextElementSibling?.querySelectorAll?.('.card') || []].some(c => c.style.display !== 'none');
  }});
}}
</script>

</body>
</html>
"""

out = Path("registry.html")
out.write_text(html, encoding="utf-8")
print(f"✓ Written {out} ({out.stat().st_size // 1024} KB) — {total} groups, {date.today()}")
