"""Inline the precomputed data into a single self-contained dashboard.html."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA  = json.load(open(os.path.join(HERE, "demo_data.json")))
PLANS = json.load(open(os.path.join(HERE, "plans.json")))

HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DOMINO — see a failure spread, and where to stop it</title>
<style>
:root{
  --bg:#080B10; --panel:#111922; --panel2:#18222E; --line:#22303F; --line2:#31465C;
  --ink:#EAF2F9; --ink2:#A4B6C7; --ink3:#78899B; --ink4:#55footerX;
  --ink4:#5A6B7C;
  --amber:#FF8A3D; --red:#FF5449; --teal:#2FD6A8; --violet:#A98BFF; --blue:#5FA0FF;
  --glow:0 0 22px rgba(255,138,61,.20);
}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);
  background:
    radial-gradient(1100px 620px at 78% -8%, rgba(255,138,61,.09), transparent 62%),
    radial-gradient(900px 560px at 4% 106%, rgba(169,139,255,.09), transparent 60%),
    var(--bg);
  background-attachment:fixed;
  font-family:"Libre Franklin",-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:15px;line-height:1.5}
.disp,h1,h2{font-family:"Source Serif 4",Georgia,"Times New Roman",serif}
.shell{max-width:1320px;margin:0 auto;padding:0 20px 40px}

.top{display:flex;align-items:center;gap:14px;padding:14px 0;border-bottom:1px solid var(--line)}
.top .bar{width:5px;height:26px;background:var(--amber);border-radius:2px}
.top h1{margin:0;font-size:22px;letter-spacing:.05em}
.top .sub{color:var(--ink3);font-size:13px}
.top .right{margin-left:auto;color:var(--ink4);font-size:12px;letter-spacing:.06em}

.intro{margin:16px 0 0;padding:14px 18px;border:1px solid var(--line);
  border-left:4px solid var(--amber);border-radius:6px;
  background:linear-gradient(90deg,rgba(255,138,61,.07),var(--panel) 45%)}
.intro b{color:var(--ink)}
.intro .k{display:inline-block;margin-right:18px;color:var(--ink2);font-size:13.5px}

.tabs{display:flex;gap:6px;margin:18px 0 0;border-bottom:1px solid var(--line)}
.tab{padding:10px 16px;border:1px solid transparent;border-bottom:none;cursor:pointer;
  font-size:14px;color:var(--ink3);border-radius:4px 4px 0 0}
.tab.on{background:var(--panel);border-color:var(--line);color:var(--ink);font-weight:700;
  margin-bottom:-1px}
.tab .n{display:inline-block;width:20px;height:20px;line-height:20px;text-align:center;
  border-radius:50%;background:var(--panel2);font-size:11px;margin-right:7px;font-weight:700}
.tab.on .n{background:var(--amber);color:#0B1017}
.page{display:none;padding-top:18px}
.page.on{display:block}

.grid{display:grid;grid-template-columns:1.25fr 1fr;gap:20px;align-items:start}
@media (max-width:1050px){.grid{grid-template-columns:1fr}}
.card{border:1px solid var(--line);background:var(--panel);border-radius:6px;padding:16px 18px}
.lbl{font-size:11px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink3);font-weight:700}
svg{width:100%;height:auto;display:block;background:#0B1017;border:1px solid var(--line);border-radius:6px}
svg .hit{cursor:pointer}

.bar-ctl{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
button,select{font:inherit;font-size:14px;padding:8px 14px;border:1px solid var(--line2);
  background:var(--panel2);border-radius:4px;color:var(--ink);cursor:pointer;
  transition:border-color .15s, color .15s, background .15s}
button:hover:not(:disabled){border-color:var(--amber);color:var(--amber)}
button:disabled{opacity:.35;cursor:default}
button.primary{background:var(--amber);border-color:var(--amber);color:#0B1017;font-weight:700}
button.primary:hover{background:#ff9d5e;color:#0B1017}
button.primary{box-shadow:var(--glow)}
button.on{background:var(--amber);border-color:var(--amber);color:#0B1017;font-weight:700;box-shadow:var(--glow)}
.stepdots{display:flex;gap:6px;align-items:center;margin-left:auto;color:var(--ink4);font-size:12.5px}
.dot{width:9px;height:9px;border-radius:50%;background:var(--line2)}
.dot.on{background:var(--amber);box-shadow:0 0 9px rgba(255,138,61,.7)}

.say{border:1px solid var(--line2);border-left:5px solid var(--amber);border-radius:6px;
  padding:16px 18px;background:linear-gradient(180deg,var(--panel2),var(--panel))}
.say .h{font-family:"Source Serif 4",Georgia,serif;font-size:21px;font-weight:700;line-height:1.25}
.say .b{margin-top:8px;color:var(--ink2);font-size:14.5px}
.say.good{border-left-color:var(--teal)} .say.bad{border-left-color:var(--red)}
.say.dark{border-left-color:var(--violet)}

.num{display:flex;align-items:baseline;gap:12px;margin-top:14px}
.num .v{font-family:"Source Serif 4",Georgia,serif;font-size:42px;font-weight:700;line-height:1}
.num .t{color:var(--ink3);font-size:13.5px}
.meter{height:10px;background:var(--panel2);border-radius:5px;overflow:hidden;margin-top:8px}
.meter i{display:block;height:100%;background:var(--teal);border-radius:5px;
  transition:width .4s;box-shadow:0 0 12px rgba(47,214,168,.45)}

.why{margin-top:6px}
.why .r{display:flex;justify-content:space-between;font-size:13px;color:var(--ink2);margin-top:9px}
.track{height:8px;background:var(--panel2);border-radius:4px;overflow:hidden;margin-top:3px}
.track i{display:block;height:100%;border-radius:4px}
.opt{display:flex;justify-content:space-between;gap:10px;padding:9px 11px;border:1px solid var(--line);
  border-radius:4px;margin-top:7px;font-size:13.5px;background:var(--panel2)}
.opt.holds{border-color:var(--teal);background:rgba(47,214,168,.10);
  box-shadow:0 0 16px rgba(47,214,168,.12)}
.opt .s{font-size:11.5px;color:var(--ink4)}
.tag{font-size:11px;letter-spacing:.05em;text-transform:uppercase;padding:2px 8px;border-radius:99px;
  border:1px solid currentColor;font-weight:700;white-space:nowrap}

.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:820px){.two{grid-template-columns:1fr}}
.plan{border:1px solid var(--line);border-radius:6px;padding:16px 18px;background:var(--panel)}
.plan.win{border-color:var(--teal);border-width:2px;background:rgba(47,214,168,.07);
  box-shadow:0 0 30px rgba(47,214,168,.10)}
.plan h3{margin:0;font-size:17px}
.buy{display:flex;justify-content:space-between;font-size:13px;padding:6px 0;
  border-bottom:1px dashed var(--line);color:var(--ink2)}
.vs{display:flex;align-items:flex-end;gap:18px;margin-top:8px}
.vs .col{flex:1}
.vs .bx{height:26px;border-radius:3px}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{text-align:left;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink3);
  padding:8px;border-bottom:1px solid var(--line2)}
td{padding:8px;border-bottom:1px solid var(--line)}
tr.sel td{background:rgba(255,138,61,.12)}
tbody tr:hover td{background:var(--panel2);cursor:pointer}
details{margin-top:14px;font-size:13px;color:var(--ink2)}
summary{cursor:pointer;color:var(--ink3);font-weight:700;font-size:12.5px;
  letter-spacing:.06em;text-transform:uppercase}
.foot{margin-top:26px;padding-top:14px;border-top:1px solid var(--line);
  color:var(--ink4);font-size:12px}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-top:10px;font-size:12.5px;color:var(--ink3)}
.legend span{display:flex;align-items:center;gap:6px}
.sw{width:22px;height:5px;border-radius:3px}
</style></head><body><div class="shell">

<style>
@keyframes pulse{0%{opacity:.55;r:14}70%{opacity:0;r:30}100%{opacity:0;r:30}}
#map .pulse{animation:pulse 2.2s ease-out infinite}
.top h1{background:linear-gradient(92deg,var(--ink),var(--amber));
  -webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
</style>
<div class="top">
  <div class="bar"></div>
  <div><h1>DOMINO</h1>
    <div class="sub">See a failure spread through a city, and find where you can still stop it.</div></div>
  <div class="right">M#26 · P05 CASCADING FAILURE · TEAM MOSSAD.EXE</div>
</div>

<div class="intro">
  <b>What you are looking at.</b> A small coastal city corridor, drawn as a map below.
  Everything here is computed live by our engine, not drawn by hand.
  <div style="margin-top:8px">
    <span class="k">🏘 <b id="i-wards">8</b> neighbourhoods</span>
    <span class="k">👥 <b id="i-pop"></b> people</span>
    <span class="k">🏥 1 hospital · 🚒 1 fire station</span>
    <span class="k">🌉 3 river bridges</span>
    <span class="k">📡 5 phone towers</span>
  </div>
</div>

<div class="tabs">
  <div class="tab on" data-p="p1"><span class="n">1</span>Watch a failure spread</div>
  <div class="tab" data-p="p2"><span class="n">2</span>Where to spend the money</div>
  <div class="tab" data-p="p3"><span class="n">3</span>Every asset at a glance</div>
</div>

<!-- ───────────────────────────────── TAB 1 -->
<div class="page on" id="p1">
  <div class="grid">
    <div class="card">
      <div class="bar-ctl">
        <span class="lbl">Break something</span>
        <select id="seed" style="font:inherit;padding:8px 10px;border:1px solid var(--line2);border-radius:3px"></select>
        <button id="prev">◀</button>
        <button id="next" class="primary">Next step ▶</button>
        <button id="play">▶ Play</button>
        <button id="reset">Reset</button>
        <div class="stepdots" id="dots"></div>
      </div>
      <svg id="map" viewBox="0 0 520 590" role="img" aria-label="corridor map"></svg>
      <div class="legend">
        <span><i class="sw" style="background:#35485C"></i> road, quiet</span>
        <span><i class="sw" style="background:#FF8A3D"></i> road, filling up</span>
        <span><i class="sw" style="background:#FF5449"></i> road, over capacity</span>
        <span><i class="sw" style="height:0;border-top:3px dashed #FF5449"></i> jammed, unusable</span>
        <span>◯ neighbourhood, with its distance to help</span>
        <span style="color:var(--violet)">◯ dark zone</span>
      </div>
      <div style="margin-top:8px;font-size:12.5px;color:var(--ink4)">
        Tip: click any road on the map to break that one instead.
      </div>
    </div>

    <div>
      <div class="say" id="say"><div class="h"></div><div class="b"></div></div>

      <div class="card" style="margin-top:16px">
        <div class="lbl">People who can still reach a hospital or fire station</div>
        <div class="num"><div class="v" id="acc">—</div><div class="t" id="accT"></div></div>
        <div class="meter"><i id="accBar" style="width:0%"></i></div>
      </div>

      <div class="card" style="margin-top:16px" id="domCard">
        <div class="lbl">What breaks next, and why</div>
        <div id="domBody" style="color:var(--ink4);margin-top:8px">
          Press <b>Next step</b> to begin.</div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="lbl">Could it have been stopped?</div>
        <div class="num"><div class="v" id="hz">—</div><div class="t" id="hzT"></div></div>
      </div>

      <div class="card" style="margin-top:16px">
        <div class="lbl">Neighbourhoods that go dark</div>
        <div style="font-size:13px;color:var(--ink3);margin-top:4px">
          Dark means both things at once: no road to help, and no phone signal.</div>
        <div id="dz" style="margin-top:8px;color:var(--ink4)">None yet.</div>
      </div>
    </div>
  </div>
</div>

<!-- ───────────────────────────────── TAB 2 -->
<div class="page" id="p2">
  <div class="card">
    <div class="disp" style="font-size:21px;font-weight:700">
      “We have a fixed resilience budget this year. Where do we spend it?”</div>
    <div style="color:var(--ink2);margin-top:8px;max-width:78ch">
      We answer it by running every possible failure, measuring how many people lose
      access to help on average, then buying the repairs that win back the most people
      per rupee. The standard way to do this is to reinforce the most central roads
      first. Both plans below are computed by the same engine, on the same budget.
    </div>
    <div class="bar-ctl" style="margin-top:16px">
      <span class="lbl">Budget</span><span id="budgets"></span>
    </div>

    <div class="two" style="margin-top:6px">
      <div class="plan" id="planC">
        <h3>The standard method</h3>
        <div style="font-size:13px;color:var(--ink3)">Reinforce the most central roads first.</div>
        <div id="cBuys" style="margin-top:12px"></div>
        <div class="num"><div class="v" id="cProt" style="font-size:34px;color:var(--ink3)"></div>
          <div class="t">more people protected<br><span id="cSpent" style="color:var(--ink4)"></span></div></div>
      </div>
      <div class="plan win" id="planD">
        <h3 style="color:var(--teal)">DOMINO</h3>
        <div style="font-size:13px;color:var(--ink3)">Buy back the most service per rupee.</div>
        <div id="dBuys" style="margin-top:12px"></div>
        <div class="num"><div class="v" id="dProt" style="font-size:34px;color:var(--teal)"></div>
          <div class="t">more people protected<br><span id="dSpent" style="color:var(--ink4)"></span></div></div>
      </div>
    </div>

    <div class="card" style="margin-top:18px;background:var(--panel2)">
      <div class="lbl">Same budget, side by side</div>
      <div class="vs">
        <div class="col"><div class="bx" id="barC" style="background:var(--ink3)"></div>
          <div style="font-size:12.5px;color:var(--ink3);margin-top:5px">Standard method</div></div>
        <div class="col"><div class="bx" id="barD" style="background:var(--teal)"></div>
          <div style="font-size:12.5px;color:var(--ink3);margin-top:5px">DOMINO</div></div>
      </div>
      <div class="disp" id="verdict" style="font-size:19px;font-weight:700;margin-top:16px"></div>
      <div id="verdict2" style="color:var(--ink2);font-size:14px;margin-top:6px"></div>
    </div>

    <details>
      <summary>How the money number is worked out</summary>
      <p>Hardening an asset means reinforcing and widening it, the same action the engine
      tests during a cascade. Costs are indicative unit rates
      (₹1.2 crore per km of road, ₹6 crore per km of bridge) and would be replaced by the
      city's own schedule of rates. Expected loss is the average number of people who end
      up outside 5 km of a hospital or fire station, taken across every single-asset
      failure in the corridor. The resilience score is simply how much of the population
      keeps its access in that average failure.</p>
    </details>
  </div>
</div>

<!-- ───────────────────────────────── TAB 3 -->
<div class="page" id="p3">
  <div class="card">
    <div class="lbl">Every asset, with what happens if it fails</div>
    <div style="color:var(--ink2);margin-top:6px;max-width:78ch">
      Run once, offline, ahead of time. During an emergency nobody has time to start a
      simulation, so the answers are already on the shelf. Click any row to watch it.
    </div>
    <div style="margin-top:14px;overflow:auto">
      <table id="pb"><thead><tr>
        <th>If this fails</th><th>Can we stop it?</th>
        <th>People who lose access to help</th><th>What to do</th>
      </tr></thead><tbody></tbody></table>
    </div>
  </div>
</div>

<div class="foot" id="foot"></div>
</div>

<script>
const DATA = __DATA__, PLANS = __PLANS__;
const G = DATA.graph, META = DATA.meta;
const NODE = Object.fromEntries(G.nodes.map(n => [n.id, n]));
const $ = s => document.querySelector(s);
const fmt = n => n.toLocaleString();

let seed = "B07", frame = 0, timer = null, budget = "10";
const scen  = () => DATA.scenarios[seed];
const frames= () => scen().frames;
const seedLabel = () => (G.edges.find(e => e.id === seed) || {}).label || seed;

/* ─────────── map geometry ─────────── */
const PAD = 48, W = 520, H = 590;
const xs = G.nodes.map(n=>n.x), ys = G.nodes.map(n=>n.y);
const x0=Math.min(...xs), x1=Math.max(...xs), y0=Math.min(...ys), y1=Math.max(...ys);
const sc = Math.min((W-2*PAD)/(x1-x0), (H-2*PAD)/(y1-y0));
const px = x => PAD + (x-x0)*sc, py = y => H - PAD - (y-y0)*sc;

const P = {ink:"#EAF2F9", ink2:"#A4B6C7", ink3:"#78899B", ink4:"#5A6B7C",
           panel:"#111922", panel2:"#18222E", line2:"#31465C", bg:"#0B1017",
           amber:"#FF8A3D", red:"#FF5449", teal:"#2FD6A8", violet:"#A98BFF",
           road:"#4A6480", roadQuiet:"#35485C"};

function roadColour(r, alive){
  if(!alive) return P.red;
  if(r > 1.0) return P.red;
  if(r > .85) return P.amber;
  if(r > .6)  return P.road;
  return P.roadQuiet;
}

function drawMap(){
  const f = frames()[frame];
  const showDark = f.phase !== "baseline";
  const dz = {}; scen().dark_zones.forEach(z => dz[z.node] = z);
  const dead = new Set(f.dead_towers);
  let s = `<defs><filter id="gl" x="-60%" y="-60%" width="220%" height="220%">
    <feGaussianBlur stdDeviation="4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter></defs>`;

  G.nodes.filter(n=>n.kind==="tower").forEach(n=>{
    if(dead.has(n.id)) return;
    s += `<circle cx="${px(n.x)}" cy="${py(n.y)}" r="${META.tower_radius_km*sc}"
      fill="${P.teal}" fill-opacity=".035" stroke="${P.teal}" stroke-opacity=".20"
      stroke-width="1.3" stroke-dasharray="5 4"/>`;
  });

  G.edges.forEach(e=>{
    const st = f.edges[e.id] || {alive:e.alive, ratio:0};
    const a = NODE[e.u], b = NODE[e.v];
    const closed = e.kind==="service" && !st.alive;
    const col = closed ? P.line2 : roadColour(st.ratio, st.alive);
    const hot = st.alive && st.ratio > 1;
    const w = st.alive ? (st.ratio>1?7:st.ratio>.85?6:5) : 4;
    const dash = st.alive ? (e.kind==="service" ? "6 5" : "") : "8 6";
    s += `<line class="hit" data-e="${e.id}" x1="${px(a.x)}" y1="${py(a.y)}"
      x2="${px(b.x)}" y2="${py(b.y)}" stroke="${col}" stroke-width="${w}"
      stroke-linecap="round" stroke-dasharray="${dash}" stroke-opacity="${closed?.55:1}"
      ${hot?'filter="url(#gl)"':""}>
      <title>${e.label}${st.alive?` — carrying ${Math.round(st.ratio*100)}% of what it was built for`:" — jammed"}</title></line>`;
    if(st.alive && st.ratio > 1){
      const mx=(px(a.x)+px(b.x))/2, my=(py(a.y)+py(b.y))/2;
      s += `<rect x="${mx-20}" y="${my-19}" width="40" height="16" rx="8" fill="${P.bg}"
        stroke="${P.red}" stroke-width="1.4"/>
        <text x="${mx}" y="${my-7}" font-size="11" font-weight="700" fill="${P.red}"
        text-anchor="middle">${st.ratio}×</text>`;
    }
    if(e.id===seed && !st.alive){
      const mx=(px(a.x)+px(b.x))/2, my=(py(a.y)+py(b.y))/2;
      s += `<circle class="pulse" cx="${mx}" cy="${my}" r="14" fill="${P.red}" fill-opacity=".45"/>
        <circle cx="${mx}" cy="${my}" r="10" fill="${P.bg}" stroke="${P.red}" stroke-width="2.8"/>
        <path d="M ${mx-4.5} ${my-4.5} l 9 9 M ${mx+4.5} ${my-4.5} l -9 9"
          stroke="${P.red}" stroke-width="2.6" stroke-linecap="round"/>`;
    }
  });

  G.nodes.filter(n=>n.population>0).forEach(n=>{
    const d = f.wards[n.id] ?? 99, far = d > META.threshold_km;
    const z = showDark ? dz[n.id] : null;
    const r = 8 + Math.sqrt(n.population)/26;
    if(z) s += `<circle cx="${px(n.x)}" cy="${py(n.y)}" r="${r+13}" fill="${P.violet}"
      fill-opacity=".22" filter="url(#gl)"/>`;
    s += `<circle cx="${px(n.x)}" cy="${py(n.y)}" r="${r}" fill="${P.panel}"
      stroke="${z?P.violet:far?P.red:P.ink3}" stroke-width="${z?3:2}"/>
      <text x="${px(n.x)}" y="${py(n.y)-r-7}" font-size="11.5" font-weight="600"
        fill="${P.ink}" text-anchor="middle">${n.label.replace(" ward","")}</text>`;
    s += z
      ? `<text x="${px(n.x)}" y="${py(n.y)+r+15}" font-size="11" font-weight="700"
          fill="${P.violet}" text-anchor="middle">dark in ${z.t_dark_min} min</text>`
      : `<text x="${px(n.x)}" y="${py(n.y)+r+14}" font-size="10.5"
          fill="${far?P.red:P.ink4}" text-anchor="middle">${d.toFixed(1)} km to help</text>`;
  });

  G.nodes.forEach(n=>{
    if(n.kind==="hospital"||n.kind==="fire"){
      const t = n.kind==="hospital" ? "H" : "F";
      s += `<rect x="${px(n.x)-13}" y="${py(n.y)-13}" width="26" height="26" rx="7"
        fill="${P.panel}" stroke="${P.teal}" stroke-width="2.8" filter="url(#gl)"/>
        <text x="${px(n.x)}" y="${py(n.y)+5}" font-size="15" font-weight="700" fill="${P.teal}"
          text-anchor="middle">${t}</text>
        <text x="${px(n.x)}" y="${py(n.y)-19}" font-size="11" font-weight="700" fill="${P.teal}"
          text-anchor="middle">${n.label}</text>`;
    }
    if(n.kind==="tower"){
      const out = dead.has(n.id), c = out ? P.red : P.ink4;
      s += `<path d="M ${px(n.x)} ${py(n.y)-8} L ${px(n.x)+7} ${py(n.y)+6}
        L ${px(n.x)-7} ${py(n.y)+6} Z" fill="${P.panel}" stroke="${c}" stroke-width="1.8"/>`;
      if(out) s += `<path d="M ${px(n.x)-6} ${py(n.y)-8} l 12 12 M ${px(n.x)+6} ${py(n.y)-8}
        l -12 12" stroke="${P.red}" stroke-width="2" stroke-linecap="round"/>
        <text x="${px(n.x)}" y="${py(n.y)+19}" font-size="10" font-weight="700" fill="${P.red}"
          text-anchor="middle">tower down</text>`;
    }
  });
  $("#map").innerHTML = s;
  $("#map").querySelectorAll(".hit").forEach(el => el.onclick = () => {
    const id = el.dataset.e;
    if(DATA.scenarios[id]){ seed = id; frame = 0; stop(); $("#seed").value = id; render(); }
  });
}

/* ─────────── plain-English narration ─────────── */
function narrate(){
  const tr = scen(), f = frames()[frame], base = tr.baseline_accessibility;
  const st = f.step ? tr.steps.find(s=>s.step===f.step) : null;
  const lost = Math.round(META.population * (base - f.accessibility)/100);

  if(f.phase==="baseline") return {tone:"", h:`Everything is working.`,
    b:`${base}% of the ${fmt(META.population)} people here can reach a hospital or a fire
       station within ${META.threshold_km} km. Press <b>Next step</b> to break something.`};

  if(f.phase==="failure"){
    const over = overloaded(f);
    const moved = Math.abs(f.accessibility - base) > 0.05;
    return {tone:"bad", h:`${seedLabel()} has just failed.`,
      b: (moved
          ? `A phone tower went down with it, and ${fmt(lost)} people are already outside
             ${META.threshold_km} km of help. `
          : `A phone tower went down with it. Look at the number below — it has not moved.
             Everybody can still reach help, so on an ordinary damage map this looks
             survivable. That is the trap. `)
        + (over.length
          ? `The traffic that used ${seedLabel()} had to go somewhere, and
             <b>${over.length} road${over.length>1?"s are":" is"} now carrying more than
             ${over.length>1?"they were":"it was"} built for</b> — worst is
             ${over[0].label} at ${over[0].ratio}×. Press Next step to see which one goes
             first, and whether anything can stop it.`
          : `No road has been pushed past its capacity, so this one stops here.`)};
  }

  if(f.phase==="stopped") return {tone:"good",
    h:`The chain stops here.`,
    b:`${st ? st.action.label : "An action"} works, and it can be done in
       ${st && st.action.window_min ? st.action.window_min+" minutes" : "advance"}.
       Access stays at ${f.accessibility}%. Nobody is cut off.`};

  const nxt = st ? st.domino : null;
  return {tone:"bad",
    h:`${nxt ? nxt.label : "A road"} has jammed, and ${fmt(lost)} people just lost their route to help.`,
    b:`Nothing we could do in time held it. The traffic pushed onto ${nxt?nxt.label:"it"}
       was ${nxt?nxt.load_ratio:""}× what it was built for, so it gridlocked too. Access is
       down to ${f.accessibility}%, ${(base-f.accessibility).toFixed(1)} points below where
       we started.`};
}

function overloaded(f){
  return Object.entries(f.edges)
    .filter(([id,s]) => s.alive && s.ratio > 1)
    .map(([id,s]) => ({id, ratio:s.ratio,
                       label:(G.edges.find(e=>e.id===id)||{}).label || id}))
    .sort((a,b) => b.ratio - a.ratio);
}

const PLAIN = {
  load_stress:"How overloaded it is right now",
  network_dependency:"How much of the network runs through it",
  emergency_impact:"Whether ambulances and fire engines use it",
  population_exposure:"How many people live behind it"};
const COL = {load_stress:"var(--amber)", network_dependency:"var(--blue)",
             emergency_impact:"var(--red)", population_exposure:"var(--teal)"};

function render(){
  const tr = scen(), f = frames()[frame], base = tr.baseline_accessibility;
  $("#i-pop").textContent = fmt(META.population);

  $("#dots").innerHTML = frames().map((_,i)=>`<i class="dot ${i<=frame?"on":""}"></i>`).join("")
    + `<span style="margin-left:8px">step ${frame+1} of ${frames().length}</span>`;

  const n = narrate();
  $("#say").className = "say " + n.tone;
  $("#say .h").innerHTML = n.h;
  $("#say .b").innerHTML = n.b;

  $("#acc").textContent = f.accessibility.toFixed(1) + "%";
  $("#acc").style.color = f.accessibility < base-0.05 ? "var(--red)" : "var(--ink)";
  const lost = Math.round(META.population*(base-f.accessibility)/100);
  $("#accT").innerHTML = lost > 0
    ? `<b style="color:var(--red)">${fmt(lost)} people</b> have no route within
       ${META.threshold_km} km<br>started at ${base}%`
    : `everyone who could reach help before, still can<br>started at ${base}%`;
  $("#accBar").style.width = f.accessibility + "%";
  $("#accBar").style.background = f.accessibility < base-0.05 ? "var(--red)" : "var(--teal)";

  const st = f.step ? tr.steps.find(s=>s.step===f.step) : null;
  if(!st){
    const over = overloaded(f);
    $("#domBody").innerHTML =
      f.phase==="baseline" ? `<div style="color:var(--ink4)">Press <b>Next step</b> to begin.</div>`
      : over.length ? `<div style="font-size:13.5px;color:var(--ink2);margin-top:6px">
          Not decided yet. ${over.length} road${over.length>1?"s are":" is"} over capacity:</div>`
          + over.map(o=>`<div class="opt"><div>${o.label}</div>
              <div><b style="color:var(--red)">${o.ratio}×</b></div></div>`).join("")
          + `<div style="font-size:12.5px;color:var(--ink3);margin-top:8px">
             The engine picks the one with the highest score as the next domino.</div>`
      : `<div style="color:var(--ink4)">No road is over capacity at this point.</div>`;
  } else {
    const d = st.domino;
    let h = `<div style="font-family:'Source Serif 4',Georgia,serif;font-size:19px;
        font-weight:700;margin-top:6px">${d.label}</div>
      <div style="font-size:13.5px;color:var(--ink2)">It is now carrying
        <b>${d.load_ratio}×</b> the traffic it was built for.</div>
      <div class="lbl" style="margin-top:14px">Why this one, and not another road</div><div class="why">`;
    for(const k in d.components){
      const v = d.components[k];
      h += `<div class="r"><span>${PLAIN[k]}</span><span>${Math.round(v*100)}%</span></div>
        <div class="track"><i style="width:${v*100}%;background:${COL[k]}"></i></div>`;
    }
    h += `</div><div class="lbl" style="margin-top:16px">What we tried, before it broke</div>`;
    st.interventions.forEach(o=>{
      h += `<div class="opt ${o.holds?"holds":""}">
        <div><div>${o.label}</div><div class="s">${
          o.window_min ? "can be done in "+o.window_min+" minutes" : "months of work, capital budget"}</div></div>
        <div style="text-align:right"><span class="tag" style="color:${
          o.holds?"var(--teal)":"var(--ink4)"}">${o.holds?"works":"not enough"}</span></div></div>`;
    });
    $("#domBody").innerHTML = h;
  }

  const hz = tr.containment_horizon, any = tr.steps.some(s=>s.domino);
  $("#hz").textContent = !any ? "—" : hz>0 ? "Yes" : "No";
  $("#hz").style.color = hz>0 ? "var(--teal)" : any ? "var(--red)" : "var(--ink3)";
  $("#hzT").innerHTML = !any
    ? "This failure never spreads. The corridor absorbs it."
    : hz>0
      ? `We can stop it, but only at step ${hz}. After that, every option is too late.<br>
         <b>That step number is the thing a city can put in a report.</b>`
      : `Nothing available on the day holds this chain.<br>
         <b>The only fix is to reinforce it before it ever fails — a capital decision.</b>`;

  $("#dz").innerHTML = tr.dark_zones.length===0
    ? `<span style="color:var(--ink4)">None under this failure.</span>`
    : tr.dark_zones.map(z=>{
        const pre = (frames()[0].wards[z.node] ?? 0) > META.threshold_km;
        return `<div class="opt" style="border-color:var(--violet);
        background:rgba(94,53,177,.07)">
        <div><div><b>${z.label}</b></div>
          <div class="s">${fmt(z.population)} people · no road to help after
            ${z.t_phys_min} min · no signal after ${z.t_comm_min} min${
            pre ? ` · <i>already outside ${META.threshold_km} km before anything failed —
                   losing the tower is what makes it dark</i>` : ""}</div></div>
        <div style="text-align:right;font-family:'Source Serif 4',Georgia,serif;
          font-size:19px;font-weight:700;color:var(--violet);white-space:nowrap">${z.t_dark_min} min</div></div>`;
      }).join("")
      + `<div style="font-size:12.5px;color:var(--ink3);margin-top:10px">
         A neighbourhood is only dark when <b>both</b> are true, so it goes dark at the later
         of the two times. The gap in between is your window to get people there first.</div>`;

  document.querySelectorAll("#pb tbody tr").forEach(r=>
    r.classList.toggle("sel", r.dataset.seed===seed));
  $("#prev").disabled = frame===0;
  $("#next").disabled = frame>=frames().length-1;
  drawMap();
}

/* ─────────── tab 2 ─────────── */
function renderPlan(){
  const p = PLANS.budgets[budget], tot = PLANS.population;
  const buys = st => st.length
    ? st.map(s=>`<div class="buy"><span>${s.label}</span>
        <span>₹${s.cost} cr</span></div>`).join("")
    : `<div style="font-size:13px;color:var(--ink4)">Nothing affordable helps.</div>`;
  $("#cBuys").innerHTML = buys(p.conventional.steps);
  $("#dBuys").innerHTML = buys(p.domino.steps);
  $("#cProt").textContent = fmt(p.conventional.protected);
  $("#dProt").textContent = fmt(p.domino.protected);
  $("#cSpent").textContent = `spent ₹${p.conventional.spent} cr of ₹${budget} cr`;
  $("#dSpent").textContent = `spent ₹${p.domino.spent} cr of ₹${budget} cr`;
  const mx = Math.max(p.conventional.protected, p.domino.protected, 1);
  $("#barC").style.boxShadow="none"; $("#barC").style.width = (p.conventional.protected/mx*100)+"%";
  $("#barD").style.boxShadow="0 0 22px rgba(47,214,168,.35)"; $("#barD").style.width = (p.domino.protected/mx*100)+"%";
  const adv = p.advantage;
  $("#verdict").innerHTML = adv
    ? `Same budget. DOMINO protects ${fmt(p.domino.protected)} people,
       the standard method protects ${fmt(p.conventional.protected)}.
       <span style="color:var(--teal)">${adv}× more.</span>`
    : `At this budget the standard method protects almost nobody.`;
  $("#verdict2").innerHTML =
    `And DOMINO stops spending at ₹${p.domino.spent} crore, because nothing else it could
     buy would win back another person. Resilience goes from
     <b>${PLANS.baseline_resilience}</b> to <b>${p.domino.resilience}</b> out of 100,
     against <b>${p.conventional.resilience}</b> for the standard plan.`;
  document.querySelectorAll("#budgets button").forEach(b=>
    b.classList.toggle("on", b.dataset.b===budget));
}

/* ─────────── tab 3 ─────────── */
function playbook(){
  const tot = META.population;
  $("#pb tbody").innerHTML = DATA.playbook.map(c=>{
    const stop = c.outcome==="contained" ? `<span class="tag" style="color:var(--teal)">yes, at step ${c.horizon}</span>`
      : c.outcome==="uncontained" ? `<span class="tag" style="color:var(--red)">no</span>`
      : `<span class="tag" style="color:var(--ink4)">never spreads</span>`;
    const lost = Math.round(tot*(DATA.scenarios[c.seed].baseline_accessibility - c.final_accessibility)/100);
    return `<tr data-seed="${c.seed}"><td style="font-weight:600">${c.seed_label}</td>
      <td>${stop}</td><td>${lost>0?fmt(lost):"—"}</td>
      <td style="color:var(--ink2)">${c.action ||
        (c.outcome==="no cascade" ? "nothing needed" : "reinforce it before it fails")}</td></tr>`;
  }).join("");
  $("#pb tbody").querySelectorAll("tr").forEach(r => r.onclick = ()=>{
    seed = r.dataset.seed; frame = 0; stop(); $("#seed").value = seed;
    document.querySelector('.tab[data-p="p1"]').click(); render();
  });
}

/* ─────────── wiring ─────────── */
function stop(){ if(timer){clearInterval(timer); timer=null; $("#play").textContent="▶ Play";} }
$("#next").onclick = ()=>{ if(frame<frames().length-1){frame++; render();} };
$("#prev").onclick = ()=>{ if(frame>0){frame--; render();} };
$("#reset").onclick = ()=>{ frame=0; stop(); render(); };
$("#play").onclick = ()=>{
  if(timer) return stop();
  if(frame>=frames().length-1) frame=0;
  $("#play").textContent="❚❚ Pause";
  timer=setInterval(()=>{ frame<frames().length-1 ? (frame++, render()) : stop(); }, 2600);
};
$("#seed").innerHTML = DATA.playbook.map(c=>
  `<option value="${c.seed}">${c.seed_label}</option>`).join("");
$("#seed").value = seed;
$("#seed").onchange = e => { seed=e.target.value; frame=0; stop(); render(); };
document.querySelectorAll(".tab").forEach(t => t.onclick = ()=>{
  document.querySelectorAll(".tab").forEach(x=>x.classList.remove("on"));
  document.querySelectorAll(".page").forEach(x=>x.classList.remove("on"));
  t.classList.add("on"); document.getElementById(t.dataset.p).classList.add("on");
});
$("#budgets").innerHTML = Object.keys(PLANS.budgets).map(b=>
  `<button data-b="${b}">₹${b} cr</button>`).join(" ");
$("#budgets").querySelectorAll("button").forEach(b=> b.onclick = ()=>{
  budget=b.dataset.b; renderPlan(); });

$("#foot").innerHTML =
  `Everything on this page is computed by our engine: shortest-path access against a
   ${META.threshold_km} km threshold, traffic reassigned after every failure, a four-part
   score for what breaks next, and each possible action re-run as a counterfactual.
   ${META.scenario_count} failures and 5 budget levels are precomputed.
   <b>The corridor is synthetic</b>, shaped like Udupi–Manipal: the machine this was built on
   had no internet access to pull a real OpenStreetMap extract. Swapping real geometry in
   replaces one loader function and nothing else. The 570,509 / 81.1% / 68.3% / 83.3%
   figures in our deck come from a separate study on real population data and are not
   produced by this prototype.`;

playbook(); renderPlan(); render();
</script></body></html>
"""

out = (HTML.replace("__DATA__", json.dumps(DATA, separators=(",", ":")))
           .replace("__PLANS__", json.dumps(PLANS, separators=(",", ":"))))
p = os.path.join(HERE, "..", "docs", "index.html")
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p, "w").write(out)
print(f"wrote {os.path.relpath(p, HERE)}  ({len(out)/1024:.0f} KB)")
