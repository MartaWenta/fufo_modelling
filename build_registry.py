"""
build_registry.py  —  Future Forests C3 Model Registry Builder
Reads models.yml → renders registry.html (GitHub Pages ready)
Dependencies: pyyaml
"""

import yaml
from pathlib import Path
from datetime import date

with open("models.yml") as f:
    data = yaml.safe_load(f)

groups = data["groups"]

LAYER_LABELS = {
    0:  "C1 — Conceptual & Theoretical Framework",
    1:  "Layer 1 — Observations & Climate Forcing",
    2:  "Layer 2 — Biophysical Engine",
    3:  "Layer 3 — Social-Ecological Feedbacks & Governance",
    99: "Cross-cutting — Methodology & Uncertainty",
}
LAYER_INTROS = {
    0:  "The theoretical backbone. C1 provides the shared social-ecological systems definitions, indicators, and terminology that all other models build on.",
    1:  "These models and datasets describe what is happening in and above the forest — climate, soil, tree structure, mortality — providing the inputs all other models need.",
    2:  "The core simulation engine. These models simulate how forests grow, die, and interact with water over time, driven by Layer 1 inputs.",
    3:  "These models represent human decisions, markets, and governance — how people manage forests and respond to changing conditions.",
    99: "Not a standalone model but methodological infrastructure. Provides calibration, validation, and uncertainty quantification that cuts across all groups.",
}
LAYER_COLORS = {
    0:  ("#5b50c4", "#ede9fe", "#f5f3ff"),   # violet — conceptual
    1:  ("#1a7a4a", "#dcfce7", "#f0fdf7"),   # green
    2:  ("#1a4f8a", "#dbeafe", "#eff6ff"),   # blue
    3:  ("#8a4a0a", "#fed7aa", "#fffbeb"),   # amber
    99: ("#374151", "#f3f4f6", "#f9fafb"),   # grey — cross-cutting
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

def approach_badge(approach):
    if not approach: return ''
    return (f'<span style="background:#1e3a5f;color:#e2e8f0;'
            f'border-radius:4px;padding:2px 8px;font-size:11px;'
            f'font-family:IBM Plex Mono,monospace;font-weight:600;">{approach}</span>')

def pill_list(items, color="#475569"):
    if not items: return '<span style="color:#94a3b8">—</span>'
    return " ".join(
        f'<span style="background:#f1f5f9;color:{color};border-radius:3px;'
        f'padding:1px 6px;font-size:11px;margin:1px;display:inline-block;">{i}</span>'
        for i in items)

def io_rows(items, arrow="←"):
    if not items: return '<span style="color:#94a3b8">—</span>'
    rows = []
    for item in items:
        name = item.get("name","")
        fmt  = item.get("format","")
        src  = item.get("source", item.get("consumers",""))
        if isinstance(src, list): src = ", ".join(src)
        rows.append(
            f'<div style="margin-bottom:4px;">'
            f'<span style="font-weight:600;font-size:11.5px">{name}</span>'
            + (f'<span style="color:#94a3b8;font-size:10.5px;margin-left:6px">{fmt}</span>' if fmt else '')
            + (f'<span style="color:#64748b;font-size:10px;margin-left:6px">{arrow} {src}</span>' if src else '')
            + "</div>")
    return "".join(rows)

def card(g):
    layer   = g.get("layer", 1)
    is_cc   = g.get("cross_cutting", False)
    accent, light, bg = LAYER_COLORS.get(layer, LAYER_COLORS[1])
    lid     = g["id"]
    kq      = g.get("key_question","")
    mapp    = g.get("modelling_approach","")
    hire_name  = g.get("hire", {}).get("name", "TBD") or "TBD"
    hire_start = g.get("hire", {}).get("start", "TBD") or "TBD"
    hire_html  = (
        f'<span style="color:#1a7a4a;font-weight:600">{hire_name}</span>'
        if hire_name not in ("TBD","",None)
        else '<span style="color:#94a3b8">TBD</span>')
    notes   = g.get("notes","")
    langs   = pill_list(g.get("language",[]), accent)
    border_style = f"border:2px dashed {accent}" if is_cc else f"border-left:4px solid {accent}"

    collab = ""
    for field in ["pi_applicants","pi_collaborators"]:
        if g.get(field):
            names = " · ".join(g[field])
            collab += f'<div style="font-size:10.5px;color:#64748b;margin-top:2px">Also: {names}</div>'

    return f"""
<div class="card" id="card-{lid}"
     data-layer="{layer}" data-status="{g.get('status','')}"
     style="{border_style};background:{bg};border-radius:8px;
            padding:16px 18px;margin-bottom:12px;transition:box-shadow .15s;">

  <!-- Header row -->
  <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;">
    <div style="flex:1;min-width:0;">
      <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.15em;
                  color:{accent};text-transform:uppercase;margin-bottom:3px;">
        {LAYER_LABELS.get(layer,'')}{"  ·  CROSS-CUTTING" if is_cc else ""}
      </div>
      <div style="font-size:17px;font-weight:700;color:#1e293b;letter-spacing:-.02em;">
        {g.get('pi','')}
        <span style="font-size:13px;font-weight:400;color:#64748b;margin-left:8px">
          {g.get('model_name','')}
        </span>
      </div>
      {collab}
    </div>
    <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:flex-start;flex-shrink:0;">
      {badge(g.get('status','planned'))}
      {approach_badge(mapp)}
    </div>
  </div>

  <!-- Key question — most prominent for social scientists -->
  {f'<div style="margin-top:10px;padding:8px 12px;background:rgba(255,255,255,.7);border-radius:6px;border-left:3px solid {accent};">'
   f'<span style="font-family:IBM Plex Mono,monospace;font-size:8.5px;color:{accent};text-transform:uppercase;letter-spacing:.12em;font-weight:700;">Key Question</span>'
   f'<div style="font-size:12.5px;color:#1e293b;margin-top:3px;font-style:italic;">{kq}</div>'
   f'</div>' if kq else ''}

  <!-- Description -->
  <div style="font-size:12px;color:#475569;margin-top:8px;line-height:1.55;">
    {g.get('short_description','')}
  </div>

  <!-- Three columns: inputs / outputs / researcher -->
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:14px;">
    <div>
      <div class="col-head">Inputs</div>
      {io_rows(g.get('inputs',[]), "←")}
    </div>
    <div>
      <div class="col-head">Outputs</div>
      {io_rows(g.get('outputs',[]), "→")}
    </div>
    <div>
      <div class="col-head">Languages</div>
      <div style="margin-bottom:8px">{langs}</div>
      <div class="col-head">Researcher / Start</div>
      <div style="font-size:12px">{hire_html}
        <span style="color:#94a3b8;font-size:11px;margin-left:6px">{hire_start}</span>
      </div>
      {f'<div style="margin-top:8px;font-size:11px;color:#64748b;font-style:italic;">{notes}</div>' if notes else ''}
    </div>
  </div>
</div>
"""

# ── Build sections ──────────────────────────────────────────
cards_by_layer = {}
for g in groups:
    l = g.get("layer",1)
    cards_by_layer.setdefault(l, []).append(g)

sections_html = ""
for layer in sorted(cards_by_layer.keys()):
    accent, light, bg = LAYER_COLORS.get(layer, LAYER_COLORS[1])
    label = LAYER_LABELS.get(layer,'')
    intro = LAYER_INTROS.get(layer,'')
    is_cc = (layer == 99)
    border = "border:2px dashed" if is_cc else "border-left:4px solid"
    sections_html += f"""
<div style="margin-bottom:6px;padding:10px 14px;background:{light};
            border-radius:6px;{border} {accent};">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;
               letter-spacing:.14em;color:{accent};text-transform:uppercase;">{label}</span>
  <div style="font-size:11.5px;color:#475569;margin-top:3px;">{intro}</div>
</div>
"""
    for g in cards_by_layer[layer]:
        sections_html += card(g)
    sections_html += "<div style='height:20px'></div>"

# ── Stats ───────────────────────────────────────────────────
total  = len(groups)
ops    = sum(1 for g in groups if g.get("status")=="operational")
dev    = sum(1 for g in groups if g.get("status")=="in_development")
pln    = sum(1 for g in groups if g.get("status")=="planned")
hired  = sum(1 for g in groups if g.get("hire",{}).get("name") not in ("TBD","",None))
approaches = sorted(set(g.get("modelling_approach","") for g in groups if g.get("modelling_approach","")))

# ── Full page ───────────────────────────────────────────────
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
    font-family:'IBM Plex Sans',sans-serif;
    background:#f8fafc; color:#1e293b;
    padding:24px 32px; max-width:1300px; margin:0 auto;
  }}
  .col-head {{
    font-family:'IBM Plex Mono',monospace;
    font-size:9px; letter-spacing:.15em; text-transform:uppercase;
    color:#94a3b8; margin-bottom:5px; font-weight:700;
  }}
  .card:hover {{ box-shadow:0 4px 18px rgba(0,0,0,.08); }}
  .filter-bar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; align-items:center; }}
  .filter-btn {{
    background:#fff; border:1.5px solid #e2e8f0; border-radius:6px;
    padding:5px 14px; font-size:12px; font-family:'IBM Plex Mono',monospace;
    cursor:pointer; transition:all .15s; color:#475569;
  }}
  .filter-btn:hover, .filter-btn.active {{ background:#1e3a5f; color:#fff; border-color:#1e3a5f; }}
  @media(max-width:700px) {{
    .card > div > div[style*="grid"] {{ grid-template-columns:1fr !important; }}
    body {{ padding:12px 14px; }}
  }}
</style>
</head>
<body>

<div style="border-bottom:2.5px solid #1e3a5f;padding-bottom:10px;margin-bottom:12px;">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.18em;
              color:#1a7a4a;text-transform:uppercase;margin-bottom:4px;">
    Future Forests Excellence Cluster · Universität Freiburg · Research Area C3
  </div>
  <div style="font-size:24px;font-weight:700;color:#1e3a5f;letter-spacing:-.02em;">
    C3 Integrated Modelling Framework — Model Registry
  </div>
  <div style="font-size:12px;color:#64748b;margin-top:4px;max-width:800px;line-height:1.5;">
    This registry describes all modelling groups contributing to Future Forests Research Area C3.
    For each group you will find: the scientific question they address, their modelling approach,
    what data they need and what they produce, and the current status of hiring.
    It is designed to be readable for researchers from all disciplines — natural science and social science alike.
    · Generated {date.today().strftime("%-d %B %Y")}
  </div>
</div>

<!-- Summary stats -->
<div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:20px;">
  {''.join([
    f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:8px;padding:10px 16px;text-align:center;">'
    f'<div style="font-size:22px;font-weight:700;color:{c}">{v}</div>'
    f'<div style="font-size:11px;color:#64748b;font-family:IBM Plex Mono,monospace">{l}</div></div>'
    for v,l,c in [
      (total,"Total Groups","#1e3a5f"),
      (ops,"Operational","#1a7a4a"),
      (dev,"In Development","#d97706"),
      (pln,"Planned","#94a3b8"),
      (hired,"Hires Confirmed","#5b50c4"),
    ]
  ])}
</div>

<!-- Filter bar -->
<div class="filter-bar">
  <span style="font-size:11px;color:#94a3b8;font-family:'IBM Plex Mono',monospace">FILTER BY LAYER:</span>
  <button class="filter-btn active" onclick="filterCards('all',this)">All</button>
  <button class="filter-btn" onclick="filterCards('layer-0',this)">C1 Conceptual</button>
  <button class="filter-btn" onclick="filterCards('layer-1',this)">Observations</button>
  <button class="filter-btn" onclick="filterCards('layer-2',this)">Biophysical</button>
  <button class="filter-btn" onclick="filterCards('layer-3',this)">Social-Economic</button>
  <button class="filter-btn" onclick="filterCards('layer-99',this)">Cross-cutting</button>
  <span style="font-size:11px;color:#94a3b8;font-family:'IBM Plex Mono',monospace;margin-left:8px">STATUS:</span>
  <button class="filter-btn" onclick="filterCards('operational',this)">Operational</button>
  <button class="filter-btn" onclick="filterCards('in_development',this)">In Development</button>
  <button class="filter-btn" onclick="filterCards('planned',this)">Planned</button>
</div>

{sections_html}

<div style="text-align:center;font-size:10px;color:#94a3b8;font-family:'IBM Plex Mono',monospace;
            margin-top:20px;padding-top:12px;border-top:1px solid #e2e8f0;">
  Source: models.yml · Scientific Modelling Coordinator · SES-ModelLab · Future Forests C3
  · <a href="FuFo_Interactive.html" style="color:#1a4f8a">↗ Interactive Connection Map</a>
  · <a href="FuFo_Original_Fullpage.html" style="color:#1a4f8a">↗ Static Connection Map</a>
</div>

<script>
function filterCards(filter, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {{
    if (filter === 'all') card.style.display = '';
    else if (filter.startsWith('layer-')) {{
      const layer = filter.replace('layer-','');
      card.style.display = card.dataset.layer === layer ? '' : 'none';
    }} else {{
      card.style.display = card.dataset.status === filter ? '' : 'none';
    }}
  }});
}}
</script>
</body>
</html>
"""

out = Path("registry.html")
out.write_text(html, encoding="utf-8")
print(f"✓ Written {out} ({out.stat().st_size//1024} KB) — {total} groups")
