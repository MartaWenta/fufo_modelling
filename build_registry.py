"""
build_registry.py  —  Future Forests C3 Model Registry Builder
Reads models.yml → renders registry.html
Dependencies: pyyaml
"""

import yaml
from pathlib import Path
from datetime import date

with open("models.yml") as f:
    data = yaml.safe_load(f)

groups = data["groups"]

CLUSTERS = {
    'conceptual': {
        'label': 'C1 & C2 — Conceptual Framework & Scenarios',
        'intro': 'The theoretical and scenario backbone. C1 provides shared social-ecological systems definitions, indicators, and terminology. C2 develops the hydro-climatic and socio-economic scenarios that all C3 models run on.',
        'accent': '#5b50c4', 'light': '#ede9fe', 'bg': '#f5f3ff',
    },
    'climate_hydrology': {
        'label': 'Climate & Hydrology',
        'intro': 'Climate forcing, hydro-climatic modelling, sensor networks, and drought response — the observational and climatic inputs to the biophysical simulation layer.',
        'accent': '#1a7a4a', 'light': '#dcfce7', 'bg': '#f0fdf7',
    },
    'forest_ecology': {
        'label': 'Forest Ecology & Structure',
        'intro': 'Forest structure, growth, mortality, and disturbance — the core biophysical simulation of forest dynamics and the structural data that initialises and validates it.',
        'accent': '#1a4f8a', 'light': '#dbeafe', 'bg': '#eff6ff',
    },
    'socio_economic': {
        'label': 'Socio-Economic',
        'intro': 'Forest management decisions, markets, governance, and land use — how social and economic actors interact with forest systems and what futures they produce.',
        'accent': '#8a4a0a', 'light': '#fed7aa', 'bg': '#fffbeb',
    },
}

LAYER_TO_CLUSTER = {0: 'conceptual', 1: 'climate_hydrology', 2: 'forest_ecology', 3: 'socio_economic'}

def get_cluster(g):
    if g.get('cluster') and g['cluster'] in CLUSTERS:
        return g['cluster']
    return LAYER_TO_CLUSTER.get(g.get('layer', 1), 'climate_hydrology')

def io_rows(items, arrow):
    if not items: return '<span style="color:#94a3b8">—</span>'
    rows = []
    for item in items:
        name = item.get("name","")
        fmt  = item.get("format","")
        src  = item.get("source", item.get("consumers",""))
        if isinstance(src, list): src = ", ".join(src)
        rows.append(
            f'<div style="margin-bottom:6px;">'
            f'<span style="font-weight:600;font-size:11.5px">{name}</span>'
            + (f'<span style="color:#94a3b8;font-size:10.5px;margin-left:6px">{fmt}</span>' if fmt else '')
            + (f'<br><span style="color:#64748b;font-size:10px;margin-left:2px">{arrow} {src}</span>' if src else '')
            + "</div>")
    return "".join(rows)

def card(g):
    ckey    = get_cluster(g)
    c       = CLUSTERS[ckey]
    accent  = c['accent']
    bg      = c['bg']
    lid     = g['id']
    topic   = g.get('topic', '')
    pi      = g.get('pi', '')
    model   = g.get('model_name', '')
    methods = g.get('methods', '')
    desc    = g.get('short_description', '')
    is_conceptual = ckey == 'conceptual'

    collab = ""
    for field in ["pi_applicants","pi_collaborators"]:
        if g.get(field):
            names = " · ".join(g[field])
            collab += f'<div style="font-size:10.5px;color:#64748b;margin-top:1px">Also: {names}</div>'

    methods_html = (
        f'<span style="background:#f1f5f9;color:#475569;border-radius:3px;'
        f'padding:2px 8px;font-size:10.5px;font-family:IBM Plex Mono,monospace;">'
        f'Methods: {methods}</span>'
    ) if methods else ''

    topic_html = (
        f'<div style="font-size:18px;font-weight:700;color:{accent};letter-spacing:-.01em;margin-bottom:3px;">{topic}</div>'
    ) if topic else ''

    pi_size   = '13px'
    pi_weight = '400'

    return f"""
<div class="card" id="card-{lid}"
     data-cluster="{ckey}" data-layer="{g.get('layer',1)}"
     style="border-left:4px solid {accent};background:{bg};border-radius:8px;
            padding:16px 18px;margin-bottom:12px;transition:box-shadow .15s;">
  <div style="display:flex;align-items:flex-start;gap:12px;flex-wrap:wrap;">
    <div style="flex:1;min-width:0;">
      {topic_html}
      <div style="font-size:{pi_size};font-weight:{pi_weight};color:#1e293b;">
        {pi}<span style="font-size:12px;font-weight:400;color:#64748b;margin-left:6px">{model}</span>
      </div>
      {collab}
      {f'<div style="margin-top:5px;">{methods_html}</div>' if methods_html else ''}
    </div>
  </div>
  <div style="font-size:12px;color:#475569;margin-top:10px;line-height:1.55;">{desc}</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px;">
    <div>
      <div class="col-head">Inputs</div>
      {io_rows(g.get('inputs',[]), "←")}
    </div>
    <div>
      <div class="col-head">Outputs</div>
      {io_rows(g.get('outputs',[]), "→")}
    </div>
  </div>
</div>
"""

cluster_order = ['conceptual', 'climate_hydrology', 'forest_ecology', 'socio_economic']
cards_by_cluster = {k: [] for k in cluster_order}
for g in groups:
    cards_by_cluster[get_cluster(g)].append(g)

sections_html = ""
for ckey in cluster_order:
    if not cards_by_cluster[ckey]:
        continue
    c = CLUSTERS[ckey]
    sections_html += f"""
<div style="margin-bottom:6px;padding:10px 14px;background:{c['light']};
            border-radius:6px;border-left:4px solid {c['accent']};">
  <span style="font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;
               letter-spacing:.14em;color:{c['accent']};text-transform:uppercase;">{c['label']}</span>
  <div style="font-size:11.5px;color:#475569;margin-top:3px;">{c['intro']}</div>
</div>
"""
    for g in cards_by_cluster[ckey]:
        sections_html += card(g)
    sections_html += "<div style='height:20px'></div>"

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
  body {{ font-family:'IBM Plex Sans',sans-serif; background:#f8fafc; color:#1e293b; padding:24px 32px; max-width:1300px; margin:0 auto; }}
  .col-head {{ font-family:'IBM Plex Mono',monospace; font-size:9px; letter-spacing:.15em; text-transform:uppercase; color:#94a3b8; margin-bottom:5px; font-weight:700; }}
  .card:hover {{ box-shadow:0 4px 18px rgba(0,0,0,.08); }}
  .filter-bar {{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px; align-items:center; }}
  .filter-btn {{ background:#fff; border:1.5px solid #e2e8f0; border-radius:6px; padding:5px 14px; font-size:12px; font-family:'IBM Plex Mono',monospace; cursor:pointer; transition:all .15s; color:#475569; }}
  .filter-btn:hover, .filter-btn.active {{ background:#1e3a5f; color:#fff; border-color:#1e3a5f; }}
  @media(max-width:700px) {{ .card > div > div[style*="grid"] {{ grid-template-columns:1fr !important; }} body {{ padding:12px 14px; }} }}
</style>
</head>
<body>
<div style="border-bottom:2.5px solid #1e3a5f;padding-bottom:10px;margin-bottom:12px;">
  <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;letter-spacing:.18em;color:#1a7a4a;text-transform:uppercase;margin-bottom:4px;">Future Forests Excellence Cluster · Universität Freiburg · Research Area C3</div>
  <div style="font-size:24px;font-weight:700;color:#1e3a5f;letter-spacing:-.02em;">C3 Integrated Modelling Framework — Model Registry</div>
  <div style="font-size:12px;color:#64748b;margin-top:4px;max-width:800px;line-height:1.5;">This registry describes modelling groups contributing to Future Forests Research Area C3. For each group: the scientific topic, the PI, their approach, what data they need and what they produce. · Generated {date.today().strftime("%-d %B %Y")}</div>
</div>
<div class="filter-bar">
  <span style="font-size:11px;color:#94a3b8;font-family:'IBM Plex Mono',monospace">FILTER:</span>
  <button class="filter-btn active" onclick="filterCards('all',this)">All</button>
  <button class="filter-btn" onclick="filterCards('conceptual',this)">C1 / C2</button>
  <button class="filter-btn" onclick="filterCards('climate_hydrology',this)">Climate &amp; Hydrology</button>
  <button class="filter-btn" onclick="filterCards('forest_ecology',this)">Forest Ecology &amp; Structure</button>
  <button class="filter-btn" onclick="filterCards('socio_economic',this)">Socio-Economic</button>
</div>
{sections_html}
<div style="text-align:center;font-size:10px;color:#94a3b8;font-family:'IBM Plex Mono',monospace;margin-top:20px;padding-top:12px;border-top:1px solid #e2e8f0;">
  SES-ModelLab · Future Forests C3 · <a href="FuFo_Interactive.html" style="color:#1a4f8a">↗ Interactive Connection Map</a>
</div>
<script>
function filterCards(filter, btn) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.card').forEach(card => {{
    if (filter === 'all') card.style.display = '';
    else card.style.display = card.dataset.cluster === filter ? '' : 'none';
  }});
}}
</script>
</body>
</html>
"""

out = Path("registry.html")
out.write_text(html, encoding="utf-8")
print(f"✓ Written {out} ({out.stat().st_size//1024} KB) — {len(groups)} groups")
