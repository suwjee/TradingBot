#!/usr/bin/env python3
"""Generate interactive graph.html from graph.json (self-contained, offline)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1]).resolve()
GRAPH = OUT / "graph.json"
HTML = OUT / "graph.html"


def main() -> None:
    data = json.loads(GRAPH.read_text(encoding="utf-8"))
    # Keep graph payload compact enough for browser
    payload = {
        "meta": data.get("meta", {}),
        "stats": data.get("stats", {}),
        "subsystems": data.get("subsystems", []),
        "nodes": data.get("nodes", []),
        "edges": data.get("edges", []),
        "analysis": {
            "uncovered_production_sources": data.get("analysis", {}).get(
                "uncovered_production_sources", []
            ),
            "orphan_tests": data.get("analysis", {}).get("orphan_tests", []),
            "orphan_nodes": data.get("analysis", {}).get("orphan_nodes", []),
            "circular_dependencies": data.get("analysis", {}).get("circular_dependencies", []),
            "broken_doc_references": data.get("analysis", {}).get("broken_doc_references", []),
            "duplicates_basename": data.get("analysis", {}).get("duplicates_basename", [])[:40],
        },
    }
    blob = json.dumps(payload, ensure_ascii=False)
    # Escape </script> sequences
    blob = blob.replace("</", "<\\/")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>TradingBot Repository Graphify</title>
<style>
  :root {{
    --bg: #0b1220; --panel: #121a2b; --ink: #e7eefc; --muted: #93a4c3;
    --accent: #4cc2ff; --ok: #3ddc97; --warn: #ffb020; --bad: #ff6b6b;
    --line: #27324a;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; height: 100%; background: var(--bg); color: var(--ink);
    font: 13px/1.45 -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; }}
  #app {{ display: grid; grid-template-columns: 280px 1fr 320px; grid-template-rows: 56px 1fr;
    height: 100vh; }}
  header {{ grid-column: 1 / -1; display: flex; align-items: center; gap: 12px; padding: 0 16px;
    border-bottom: 1px solid var(--line); background: #0e1628; }}
  header h1 {{ font-size: 15px; margin: 0; font-weight: 650; }}
  header .stats {{ color: var(--muted); font-size: 12px; }}
  aside, main, section {{ min-height: 0; }}
  aside {{ background: var(--panel); border-right: 1px solid var(--line); padding: 12px; overflow: auto; }}
  section {{ background: var(--panel); border-left: 1px solid var(--line); padding: 12px; overflow: auto; }}
  main {{ position: relative; overflow: hidden; }}
  #canvas {{ width: 100%; height: 100%; display: block; cursor: grab; }}
  #canvas.dragging {{ cursor: grabbing; }}
  .label {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; margin: 12px 0 6px; }}
  input[type="search"], select, button {{
    width: 100%; border: 1px solid var(--line); background: #0d1526; color: var(--ink);
    border-radius: 8px; padding: 8px 10px; outline: none;
  }}
  button {{ cursor: pointer; margin-top: 8px; }}
  button:hover {{ border-color: var(--accent); }}
  .chip-row {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .chip {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 8px; font-size: 11px;
    color: var(--muted); cursor: pointer; user-select: none; }}
  .chip.active {{ color: var(--ink); border-color: var(--accent); background: rgba(76,194,255,.12); }}
  .detail h2 {{ font-size: 13px; margin: 0 0 8px; word-break: break-all; }}
  .kv {{ display: grid; grid-template-columns: 96px 1fr; gap: 4px 8px; font-size: 12px; margin-bottom: 12px; }}
  .kv span:nth-child(odd) {{ color: var(--muted); }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 11px;
    border: 1px solid var(--line); }}
  .legend {{ display: grid; gap: 6px; font-size: 11px; color: var(--muted); }}
  .legend i {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 6px; }}
  .list {{ display: grid; gap: 4px; max-height: 180px; overflow: auto; }}
  .list div {{ padding: 4px 6px; border-radius: 6px; background: #0d1526; border: 1px solid #1b2740;
    font-size: 11px; word-break: break-all; cursor: pointer; }}
  .list div:hover {{ border-color: var(--accent); }}
  .modebar {{ display:flex; gap:6px; margin-top:8px; }}
  .modebar button {{ margin: 0; width: auto; flex: 1; padding: 6px 8px; font-size: 11px; }}
  .modebar button.active {{ border-color: var(--accent); color: var(--accent); }}
  .hint {{ color: var(--muted); font-size: 11px; margin-top: 8px; }}
</style>
</head>
<body>
<div id="app">
  <header>
    <h1>TradingBot Repository Graphify</h1>
    <div class="stats" id="stats"></div>
  </header>
  <aside>
    <div class="label">Search</div>
    <input id="search" type="search" placeholder="file, module, subsystem..." />
    <div class="label">View</div>
    <div class="modebar">
      <button id="mode-cluster" class="active" type="button">Cluster</button>
      <button id="mode-degree" type="button">Degree</button>
      <button id="mode-impact" type="button">Impact</button>
    </div>
    <div class="label">Subsystem filter</div>
    <div class="chip-row" id="subsystems"></div>
    <div class="label">Edge types</div>
    <div class="chip-row" id="edgetypes"></div>
    <div class="label">Node type</div>
    <div class="chip-row" id="nodetypes"></div>
    <button id="reset" type="button">Reset view</button>
    <button id="fit" type="button">Fit graph</button>
    <div class="hint">Drag to pan · wheel to zoom · click node for details. Classification is rule-based and durable across repository evolution.</div>
    <div class="label">Legend</div>
    <div class="legend" id="legend"></div>
    <div class="label">Health highlights</div>
    <div class="list" id="health"></div>
  </aside>
  <main>
    <canvas id="canvas"></canvas>
  </main>
  <section class="detail">
    <div class="label">Node details</div>
    <div id="details">Select a node to inspect ownership, lifecycle, subsystem, and relationships.</div>
    <div class="label">Neighbors</div>
    <div class="list" id="neighbors"></div>
    <div class="label">Analysis excerpts</div>
    <div id="analysis"></div>
  </section>
</div>
<script>
const DATA = {blob};

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const statsEl = document.getElementById('stats');
const detailsEl = document.getElementById('details');
const neighborsEl = document.getElementById('neighbors');
const analysisEl = document.getElementById('analysis');
const healthEl = document.getElementById('health');
const subsystemsEl = document.getElementById('subsystems');
const edgetypesEl = document.getElementById('edgetypes');
const nodetypesEl = document.getElementById('nodetypes');
const legendEl = document.getElementById('legend');

const SUBSYS_COLORS = {{}};
const PALETTE = [
  '#4cc2ff','#3ddc97','#ffb020','#ff6b6b','#c792ea','#f78c6c','#82aaff','#c3e88d',
  '#ffcb6b','#89ddff','#f07178','#7fdbca','#bb80b3','#6a9fb5','#d6d6d6','#e6b8c2'
];
DATA.subsystems.forEach((s, i) => {{ SUBSYS_COLORS[s] = PALETTE[i % PALETTE.length]; }});

const EDGE_COLOR = {{
  imports: '#4cc2ff',
  tests: '#3ddc97',
  documentation: '#ffb020',
  dependency: '#c792ea',
  external: '#5b6b8c',
  ownership: '#2a3854',
  impact: '#ff6b6b'
}};

const state = {{
  scale: 1, tx: 0, ty: 0,
  search: '',
  subsystems: new Set(DATA.subsystems),
  edgeTypes: new Set(DATA.edges.map(e => e.type)),
  nodeTypes: new Set(DATA.nodes.map(n => n.type)),
  mode: 'cluster',
  selected: null,
  hover: null
}};

function resize() {{
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * devicePixelRatio;
  canvas.height = rect.height * devicePixelRatio;
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
}}
window.addEventListener('resize', () => {{ resize(); draw(); }});

function visibleNodes() {{
  return DATA.nodes.filter(n =>
    state.subsystems.has(n.subsystem) &&
    state.nodeTypes.has(n.type) &&
    (!state.search || (n.id || '').toLowerCase().includes(state.search))
  );
}}

function nodeKey(n) {{ return n.id; }}

function layout(nodes, mode) {{
  // Deterministic radial cluster layout by subsystem; degree/impact adjust radius.
  const bySub = {{}};
  nodes.forEach(n => {{ (bySub[n.subsystem] ||= []).push(n); }});
  const subs = Object.keys(bySub).sort();
  const pos = {{}};
  const cx = 0, cy = 0;
  const outer = Math.min(canvas.clientWidth, canvas.clientHeight) * 0.36;
  subs.forEach((s, si) => {{
    const angle = (si / Math.max(1, subs.length)) * Math.PI * 2 - Math.PI / 2;
    const sx = cx + Math.cos(angle) * outer;
    const sy = cy + Math.sin(angle) * outer;
    const list = bySub[s];
    list.forEach((n, i) => {{
      const a = (i / Math.max(1, list.length)) * Math.PI * 2;
      let r = 28 + (i % 7) * 10;
      if (mode === 'degree') r += Math.min(70, (n.relationship_count || 0) * 3);
      if (mode === 'impact') r += n.importance === 'critical' ? 60 : n.importance === 'high' ? 35 : 0;
      pos[nodeKey(n)] = {{
        x: sx + Math.cos(a) * r,
        y: sy + Math.sin(a) * r,
        r: n.type === 'subsystem' ? 10 : n.type === 'folder' ? 5 : 3.2
      }};
    }});
    pos['subsystem:' + s] = {{ x: sx, y: sy, r: 12 }};
  }});
  return pos;
}}

let positions = {{}};

function rebuildPositions() {{
  positions = layout(visibleNodes(), state.mode);
}}

function toScreen(x, y) {{
  return {{ x: x * state.scale + state.tx, y: y * state.scale + state.ty }};
}}
function toWorld(x, y) {{
  return {{ x: (x - state.tx) / state.scale, y: (y - state.ty) / state.scale }};
}}

function draw() {{
  const w = canvas.clientWidth, h = canvas.clientHeight;
  ctx.clearRect(0, 0, w, h);
  const nodes = visibleNodes();
  const nodeIds = new Set(nodes.map(n => n.id));
  // edges
  for (const e of DATA.edges) {{
    if (!state.edgeTypes.has(e.type)) continue;
    if (!nodeIds.has(e.source) || !nodeIds.has(e.target)) continue;
    const a = positions[e.source], b = positions[e.target];
    if (!a || !b) continue;
    const A = toScreen(a.x, a.y), B = toScreen(b.x, b.y);
    ctx.beginPath();
    ctx.moveTo(A.x, A.y);
    ctx.lineTo(B.x, B.y);
    ctx.strokeStyle = EDGE_COLOR[e.type] || '#445';
    ctx.globalAlpha = e.type === 'ownership' ? 0.08 : e.type === 'impact' ? 0.12 : 0.28;
    ctx.lineWidth = e.type === 'impact' ? 1.2 : 1;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }}
  // nodes
  for (const n of nodes) {{
    const p = positions[n.id];
    if (!p) continue;
    const S = toScreen(p.x, p.y);
    const color = SUBSYS_COLORS[n.subsystem] || '#888';
    ctx.beginPath();
    ctx.arc(S.x, S.y, Math.max(1.5, p.r * Math.min(2.2, state.scale)), 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.globalAlpha = n.type === 'subsystem' ? 0.95 : n.lifecycle === 'archive' ? 0.35 : 0.85;
    ctx.fill();
    if (state.selected === n.id) {{
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#fff';
      ctx.stroke();
    }}
    ctx.globalAlpha = 1;
    if ((state.search && n.id.toLowerCase().includes(state.search)) || state.hover === n.id) {{
      ctx.fillStyle = '#dbe9ff';
      ctx.font = '11px sans-serif';
      ctx.fillText(n.id, S.x + 8, S.y + 3);
    }}
  }}
  // cluster labels
  if (state.mode === 'cluster') {{
    const bySub = {{}};
    visibleNodes().forEach(n => {{ bySub[n.subsystem] = true; }});
    for (const s of Object.keys(bySub)) {{
      const p = positions['subsystem:' + s] || positions[Object.keys(positions).find(k => k.startsWith(s))] ;
      const sp = positions['subsystem:' + s];
      if (!sp) continue;
      const S = toScreen(sp.x, sp.y);
      ctx.fillStyle = SUBSYS_COLORS[s] || '#888';
      ctx.font = '600 12px sans-serif';
      ctx.fillText(s, S.x + 14, S.y + 4);
    }}
  }}
}}

function hitTest(sx, sy) {{
  const nodes = visibleNodes();
  let best = null, bestD = 14;
  for (const n of nodes) {{
    const p = positions[n.id];
    if (!p) continue;
    const S = toScreen(p.x, p.y);
    const d = Math.hypot(S.x - sx, S.y - sy);
    if (d < bestD) {{ bestD = d; best = n; }}
  }}
  return best;
}}

function showDetails(n) {{
  if (!n) {{
    detailsEl.textContent = 'Select a node to inspect ownership, lifecycle, subsystem, and relationships.';
    neighborsEl.innerHTML = '';
    return;
  }}
  detailsEl.innerHTML = `
    <h2>${{n.id}}</h2>
    <div class="kv">
      <span>type</span><span class="badge">${{n.type}}</span>
      <span>language</span><span>${{n.language || '—'}}</span>
      <span>subsystem</span><span class="badge">${{n.subsystem}}</span>
      <span>ownership</span><span class="badge">${{n.ownership}}</span>
      <span>lifecycle</span><span class="badge">${{n.lifecycle}}</span>
      <span>importance</span><span class="badge">${{n.importance}}</span>
      <span>degree</span><span>${{n.relationship_count}}</span>
    </div>`;
  const neigh = [];
  for (const e of DATA.edges) {{
    if (e.source === n.id) neigh.push({{ dir: '→', e }});
    if (e.target === n.id && e.source !== n.id) neigh.push({{ dir: '←', e }});
  }}
  neighborsEl.innerHTML = neigh.slice(0, 40).map(x =>
    `<div data-id="${{x.e.source === n.id ? x.e.target : x.e.source}}">
      ${{x.dir}} [${{x.e.type}}] ${{x.e.source === n.id ? x.e.target : x.e.source}}
    </div>`).join('') || '<div class="hint">No relationship edges</div>';
  neighborsEl.querySelectorAll('div[data-id]').forEach(el => {{
    el.onclick = () => {{
      const id = el.getAttribute('data-id');
      const node = DATA.nodes.find(x => x.id === id);
      if (node) {{ state.selected = id; showDetails(node); draw(); }}
    }};
  }});
}}

function renderFilters() {{
  subsystemsEl.innerHTML = DATA.subsystems.map(s =>
    `<div class="chip active" data-s="${{s}}">${{s}}</div>`).join('');
  subsystemsEl.querySelectorAll('.chip').forEach(el => {{
    el.onclick = () => {{
      const s = el.getAttribute('data-s');
      if (state.subsystems.has(s)) {{ state.subsystems.delete(s); el.classList.remove('active'); }}
      else {{ state.subsystems.add(s); el.classList.add('active'); }}
      rebuildPositions(); draw();
    }};
  }});
  const et = [...new Set(DATA.edges.map(e => e.type))].sort();
  edgetypesEl.innerHTML = et.map(t => `<div class="chip active" data-t="${{t}}">${{t}}</div>`).join('');
  edgetypesEl.querySelectorAll('.chip').forEach(el => {{
    el.onclick = () => {{
      const t = el.getAttribute('data-t');
      if (state.edgeTypes.has(t)) {{ state.edgeTypes.delete(t); el.classList.remove('active'); }}
      else {{ state.edgeTypes.add(t); el.classList.add('active'); }}
      draw();
    }};
  }});
  const nt = [...new Set(DATA.nodes.map(n => n.type))].sort();
  nodetypesEl.innerHTML = nt.map(t => `<div class="chip active" data-n="${{t}}">${{t}}</div>`).join('');
  nodetypesEl.querySelectorAll('.chip').forEach(el => {{
    el.onclick = () => {{
      const t = el.getAttribute('data-n');
      if (state.nodeTypes.has(t)) {{ state.nodeTypes.delete(t); el.classList.remove('active'); }}
      else {{ state.nodeTypes.add(t); el.classList.add('active'); }}
      rebuildPositions(); draw();
    }};
  }});
  legendEl.innerHTML = Object.entries(EDGE_COLOR).map(([k,v]) =>
    `<div><i style="background:${{v}}"></i>${{k}}</div>`).join('');
}}

function renderHealth() {{
  const a = DATA.analysis || {{}};
  const items = [];
  (a.broken_doc_references || []).slice(0, 8).forEach(x =>
    items.push(`broken doc: ${{x.source}}:${{x.line}} → ${{x.target}}`));
  (a.orphan_tests || []).slice(0, 8).forEach(x => items.push(`orphan test: ${{x}}`));
  (a.orphan_nodes || []).slice(0, 8).forEach(x => items.push(`orphan file: ${{x}}`));
  (a.circular_dependencies || []).slice(0, 5).forEach(c => items.push(`cycle: ${{c.join(' → ')}}`));
  healthEl.innerHTML = items.map(t => `<div>${{t}}</div>`).join('') || '<div>Graph health: no major flags</div>';
}}

function renderAnalysis() {{
  const a = DATA.analysis || {{}};
  analysisEl.innerHTML = `
    <div class="kv">
      <span>files</span><span>${{DATA.stats.files_scanned}}</span>
      <span>nodes</span><span>${{DATA.stats.nodes}}</span>
      <span>edges</span><span>${{DATA.stats.edges}}</span>
      <span>subsystems</span><span>${{DATA.stats.subsystems}}</span>
      <span>uncovered</span><span>${{(a.uncovered_production_sources || []).length}}</span>
      <span>orphan tests</span><span>${{(a.orphan_tests || []).length}}</span>
    </div>
    <div class="hint">Full detail in GRAPH_REPORT.md / GRAPH_HEALTH.md / graph.json</div>`;
}}

// interaction
let dragging = false, lastX = 0, lastY = 0;
canvas.addEventListener('mousedown', e => {{
  dragging = true;
  lastX = e.clientX; lastY = e.clientY;
  canvas.classList.add('dragging');
}});
window.addEventListener('mouseup', () => {{
  dragging = false;
  canvas.classList.remove('dragging');
}});
canvas.addEventListener('mousemove', e => {{
  const rect = canvas.getBoundingClientRect();
  const sx = e.clientX - rect.left, sy = e.clientY - rect.top;
  if (dragging) {{
    state.tx += e.clientX - lastX;
    state.ty += e.clientY - lastY;
    lastX = e.clientX; lastY = e.clientY;
    draw();
    return;
  }}
  const n = hitTest(sx, sy);
  state.hover = n ? n.id : null;
  draw();
}});
canvas.addEventListener('click', e => {{
  const rect = canvas.getBoundingClientRect();
  const n = hitTest(e.clientX - rect.left, e.clientY - rect.top);
  state.selected = n ? n.id : null;
  showDetails(n);
  draw();
}});
canvas.addEventListener('wheel', e => {{
  e.preventDefault();
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left, my = e.clientY - rect.top;
  const before = toWorld(mx, my);
  const factor = e.deltaY < 0 ? 1.12 : 0.9;
  state.scale = Math.max(0.15, Math.min(8, state.scale * factor));
  const after = toWorld(mx, my);
  state.tx += (after.x - before.x) * state.scale;
  state.ty += (after.y - before.y) * state.scale;
  draw();
}}, {{ passive: false }});

document.getElementById('search').addEventListener('input', e => {{
  state.search = e.target.value.trim().toLowerCase();
  rebuildPositions(); draw();
}});
document.getElementById('reset').onclick = () => {{
  state.scale = 1; state.tx = canvas.clientWidth / 2; state.ty = canvas.clientHeight / 2;
  state.search = '';
  document.getElementById('search').value = '';
  state.subsystems = new Set(DATA.subsystems);
  state.edgeTypes = new Set(DATA.edges.map(e => e.type));
  state.nodeTypes = new Set(DATA.nodes.map(n => n.type));
  state.mode = 'cluster';
  document.querySelectorAll('.chip').forEach(c => c.classList.add('active'));
  document.querySelectorAll('.modebar button').forEach(b => b.classList.remove('active'));
  document.getElementById('mode-cluster').classList.add('active');
  rebuildPositions(); draw();
}};
document.getElementById('fit').onclick = () => {{
  state.scale = 1; state.tx = canvas.clientWidth / 2; state.ty = canvas.clientHeight / 2;
  draw();
}};
document.getElementById('mode-cluster').onclick = () => setMode('cluster');
document.getElementById('mode-degree').onclick = () => setMode('degree');
document.getElementById('mode-impact').onclick = () => setMode('impact');
function setMode(m) {{
  state.mode = m;
  document.querySelectorAll('.modebar button').forEach(b => b.classList.remove('active'));
  document.getElementById('mode-' + m).classList.add('active');
  rebuildPositions(); draw();
}}

function init() {{
  statsEl.textContent = `${{DATA.stats.files_scanned}} files · ${{DATA.stats.nodes}} nodes · ${{DATA.stats.edges}} edges · ${{DATA.stats.subsystems}} subsystems`;
  resize();
  state.tx = canvas.clientWidth / 2;
  state.ty = canvas.clientHeight / 2;
  renderFilters();
  renderHealth();
  renderAnalysis();
  rebuildPositions();
  draw();
}}
init();
</script>
</body>
</html>
"""
    HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {HTML} ({HTML.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
