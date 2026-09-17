"""Generated SVG illustrations for the DOMINO deck."""
import os, math, random
import cairosvg
from dsys import C

OUT = "assets"
os.makedirs(OUT, exist_ok=True)

def _write(svg, name, w, h):
    p = f"{OUT}/{name}.png"
    cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=w, output_height=h)
    return p

def hx(k): return "#" + C.get(k, k)

# ---------------------------------------------------------------- road network
def _road_net(W, H, seed=7):
    """returns (svg_fragment, river_path, bridge_pts, node_positions)"""
    rnd = random.Random(seed)
    parts = []
    # --- river: a sinuous band running top-left to bottom-right
    rp = f"M {-0.05*W} {0.30*H} C {0.22*W} {0.20*H}, {0.30*W} {0.62*H}, {0.52*W} {0.58*H} " \
         f"S {0.82*W} {0.42*H}, {1.06*W} {0.52*H}"
    parts.append(f'<path d="{rp}" fill="none" stroke="{hx("blue")}" stroke-opacity="0.16" stroke-width="{0.055*H}" stroke-linecap="round"/>')
    parts.append(f'<path d="{rp}" fill="none" stroke="{hx("blue")}" stroke-opacity="0.30" stroke-width="{0.006*H}"/>')

    # --- arterials (thick curved roads)
    arterials = [
        f"M {-0.04*W} {0.78*H} C {0.20*W} {0.72*H}, {0.28*W} {0.40*H}, {0.48*W} {0.34*H} S {0.80*W} {0.26*H}, {1.05*W} {0.16*H}",
        f"M {0.10*W} {-0.05*H} C {0.16*W} {0.28*H}, {0.32*W} {0.48*H}, {0.38*W} {1.05*H}",
        f"M {1.04*W} {0.72*H} C {0.80*W} {0.76*H}, {0.70*W} {0.60*H}, {0.50*W} {0.60*H} S {0.22*W} {0.90*H}, {0.05*W} {1.04*H}",
        f"M {0.72*W} {-0.04*H} C {0.70*W} {0.30*H}, {0.80*W} {0.52*H}, {0.76*W} {1.04*H}",
    ]
    for a in arterials:
        parts.append(f'<path d="{a}" fill="none" stroke="{hx("road")}" stroke-opacity="0.95" stroke-width="{0.016*H}" stroke-linecap="round"/>')
    # --- secondary grid, clipped organically
    for i in range(16):
        x = rnd.uniform(-0.02, 1.0) * W
        y0 = rnd.uniform(-0.05, 0.4) * H
        y1 = y0 + rnd.uniform(0.25, 0.75) * H
        k = rnd.uniform(-0.08, 0.08) * W
        parts.append(f'<path d="M {x:.1f} {y0:.1f} C {x+k:.1f} {(y0+y1)/2:.1f}, {x+k:.1f} {(y0+y1)/2:.1f}, {x+k*1.5:.1f} {y1:.1f}" '
                     f'fill="none" stroke="{hx("road")}" stroke-opacity="0.45" stroke-width="{0.0055*H}"/>')
    for i in range(13):
        y = rnd.uniform(0, 1.0) * H
        x0 = rnd.uniform(-0.05, 0.45) * W
        x1 = x0 + rnd.uniform(0.25, 0.7) * W
        k = rnd.uniform(-0.05, 0.05) * H
        parts.append(f'<path d="M {x0:.1f} {y:.1f} C {(x0+x1)/2:.1f} {y+k:.1f}, {(x0+x1)/2:.1f} {y+k:.1f}, {x1:.1f} {y+k*1.4:.1f}" '
                     f'fill="none" stroke="{hx("road")}" stroke-opacity="0.45" stroke-width="{0.0055*H}"/>')
    # --- city blocks (very faint)
    for i in range(38):
        bw = rnd.uniform(0.03, 0.09) * W
        bh = rnd.uniform(0.05, 0.13) * H
        bx = rnd.uniform(0, 1) * W - bw / 2
        by = rnd.uniform(0, 1) * H - bh / 2
        parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{0.004*H}" '
                     f'fill="{hx("ink")}" fill-opacity="0.018"/>')
    return "\n".join(parts)


def map_hero(name="map_hero", W=1780, H=1001, seed=7):
    """dark road-network plate used as slide background"""
    g = _road_net(W, H, seed)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
 <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
   <stop offset="0" stop-color="{hx('amber')}" stop-opacity="0.30"/>
   <stop offset="1" stop-color="{hx('amber')}" stop-opacity="0"/>
 </radialGradient>
 <radialGradient id="vg" cx="0.5" cy="0.5" r="0.62">
   <stop offset="0.45" stop-color="{hx('bg')}" stop-opacity="0"/>
   <stop offset="1" stop-color="{hx('bg')}" stop-opacity="0.92"/>
 </radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="{hx('bg')}"/>
{g}
<circle cx="{0.50*W}" cy="{0.575*H}" r="{0.30*H}" fill="url(#glow)"/>
<rect width="{W}" height="{H}" fill="url(#vg)"/>
</svg>'''
    return _write(svg, name, W, H)


# ---------------------------------------------------------------- slide 1 cascade chain
def cascade_chain(name="cascade_chain", W=1400, H=430):
    """5 tilted domino tiles falling, joined by an energy line — no text"""
    cols = ["red", "amber", "amber", "violet", "violetLt"]
    n = 5
    tw, th = 0.105 * W, 0.62 * H
    gap = (W - n * tw) / (n + 1)
    parts = [f'<rect width="{W}" height="{H}" fill="none"/>']
    pts = []
    for i in range(n):
        x = gap + i * (tw + gap)
        y = 0.16 * H
        rot = -3 - i * 11
        cx, cy = x + tw / 2, y + th
        col = hx(cols[i])
        parts.append(f'''<g transform="rotate({rot} {cx} {cy})">
  <rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="{0.018*W}" fill="{hx('panel2')}" stroke="{col}" stroke-width="3"/>
  <rect x="{x}" y="{y}" width="{tw}" height="{th}" rx="{0.018*W}" fill="{col}" fill-opacity="0.10"/>
  <line x1="{x+tw*0.18}" y1="{y+th*0.5}" x2="{x+tw*0.82}" y2="{y+th*0.5}" stroke="{col}" stroke-opacity="0.55" stroke-width="2"/>
  <circle cx="{x+tw*0.5}" cy="{y+th*0.27}" r="{tw*0.11}" fill="{col}" fill-opacity="0.9"/>
  <circle cx="{x+tw*0.5}" cy="{y+th*0.73}" r="{tw*0.11}" fill="{col}" fill-opacity="0.45"/>
</g>''')
        pts.append((cx, y + th * 0.10))
    # energy path through the tops
    d = "M " + " L ".join(f"{p[0]:.0f} {p[1]:.0f}" for p in pts)
    parts.insert(1, f'<path d="{d}" fill="none" stroke="{hx("amber")}" stroke-opacity="0.22" stroke-width="10" stroke-linecap="round"/>')
    # ground line
    parts.append(f'<line x1="0" y1="{0.80*H}" x2="{W}" y2="{0.80*H}" stroke="{hx("line2")}" stroke-width="2"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ---------------------------------------------------------------- slide 2 dependency web
def dep_web(name="dep_web", W=1180, H=900):
    """labelled dependency web; label type sized to stay legible at ~3.5in wide"""
    nodes = {
        "bridge": (0.50, 0.19, "red",    48, "BRIDGE", "seed failure", "above"),
        "r11":    (0.25, 0.40, "amber",  35, "ROAD R11", "", "below"),
        "r07":    (0.77, 0.29, "road",   32, "ROAD R07", "", "above"),
        "r24":    (0.44, 0.50, "amber",  43, "ROAD R24", "overloaded", "right"),
        "hosp":   (0.17, 0.75, "teal",   39, "HOSPITAL", "", "below"),
        "fire":   (0.50, 0.85, "teal",   36, "FIRE STATION", "", "below"),
        "tower":  (0.85, 0.67, "violet", 34, "TOWER", "", "above"),
    }
    edges = [("bridge","r11",1),("bridge","r07",1),("r11","r24",1),
             ("r24","hosp",1),("r24","fire",1),("r07","r24",0),
             ("r07","tower",0),("tower","fire",0)]
    parts = []
    for a_, b_, hot in edges:
        ax, ay = nodes[a_][0]*W, nodes[a_][1]*H
        bx, by = nodes[b_][0]*W, nodes[b_][1]*H
        mx, my = (ax+bx)/2 + (by-ay)*0.09, (ay+by)/2 - (bx-ax)*0.09
        col = hx("amber") if hot else hx("line2")
        parts.append(f'<path d="M {ax:.0f} {ay:.0f} Q {mx:.0f} {my:.0f} {bx:.0f} {by:.0f}" fill="none" '
                     f'stroke="{col}" stroke-opacity="{0.92 if hot else 0.65}" stroke-width="{7 if hot else 3.4}"/>')
    for k, (x, y, c, r, lbl, note, pos) in nodes.items():
        x, y = x*W, y*H
        col = hx(c)
        if k == "bridge":
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r*2.4}" fill="{col}" fill-opacity="0.09"/>')
            parts.append(f'<circle cx="{x}" cy="{y}" r="{r*1.6}" fill="{col}" fill-opacity="0.15"/>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hx("bg2")}" stroke="{col}" stroke-width="5"/>')
        parts.append(f'<circle cx="{x}" cy="{y}" r="{r*0.38}" fill="{col}"/>')
        if pos == "above":
            anc, lx, ly = "middle", x, y - r - 58
        elif pos == "below":
            anc, lx, ly = "middle", x, y + r + 48
        elif pos == "left":
            anc, lx, ly = "end", x - r - 26, y + 14
        else:
            anc, lx, ly = "start", x + r + 26, y + 14
        parts.append(f'<text x="{lx:.0f}" y="{ly:.0f}" font-family="Libre Franklin" font-size="42" '
                     f'font-weight="700" fill="{hx("ink2")}" text-anchor="{anc}" letter-spacing="1.0">{lbl}</text>')
        if note:
            parts.append(f'<text x="{lx:.0f}" y="{ly+44:.0f}" font-family="Libre Franklin" font-size="40" '
                         f'fill="{col}" text-anchor="{anc}">{note}</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ---------------------------------------------------------------- slide 4 mini visuals
def mini_earliest(name="mini_earliest", W=760, H=185):
    """timeline of dominoes with an intervention window marked early"""
    parts = []
    n = 7
    for i in range(n):
        x = 0.06*W + i*(0.88*W/(n-1))
        col = hx("teal") if i < 2 else (hx("amber") if i < 4 else hx("red"))
        op = 1.0 if i < 2 else (0.75 if i < 4 else 0.5)
        h = 0.34*H + i*0.055*H
        parts.append(f'<rect x="{x-0.022*W}" y="{0.78*H-h}" width="{0.044*W}" height="{h}" rx="4" fill="{col}" fill-opacity="{op}"/>')
    parts.insert(0, f'<rect x="{0.03*W}" y="{0.06*H}" width="{0.285*W}" height="{0.86*H}" rx="8" fill="{hx("teal")}" fill-opacity="0.12" stroke="{hx("teal")}" stroke-width="2" stroke-dasharray="7 5"/>')
    parts.append(f'<line x1="0" y1="{0.80*H}" x2="{W}" y2="{0.80*H}" stroke="{hx("line2")}" stroke-width="2"/>')
    parts.append(f'<path d="M {0.40*W} {0.30*H} L {0.96*W} {0.30*H}" stroke="{hx("red")}" stroke-opacity="0.35" stroke-width="2" stroke-dasharray="4 4"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)

def mini_score(name="mini_score", W=760, H=185):
    """stacked contribution bar — four explainable components"""
    segs = [(0.30, "amber"), (0.26, "blue"), (0.26, "red"), (0.18, "teal")]
    x = 0.04*W; y = 0.34*H; h = 0.38*H; tot = 0.92*W
    parts = []
    for frac, col in segs:
        w = tot*frac
        parts.append(f'<rect x="{x}" y="{y}" width="{w-5}" height="{h}" rx="5" fill="{hx(col)}" fill-opacity="0.85"/>')
        x += w
    parts.append(f'<rect x="{0.04*W}" y="{0.11*H}" width="{tot}" height="{0.075*H}" rx="4" fill="{hx("line")}"/>')
    parts.append(f'<rect x="{0.04*W}" y="{0.11*H}" width="{tot*0.78}" height="{0.075*H}" rx="4" fill="{hx("ink2")}" fill-opacity="0.55"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)

def mini_priority(name="mini_priority", W=760, H=185):
    """emergency route given priority through a road grid"""
    parts = []
    for i in range(5):
        y = 0.12*H + i*0.19*H
        parts.append(f'<line x1="{0.03*W}" y1="{y}" x2="{0.97*W}" y2="{y}" stroke="{hx("road")}" stroke-width="3"/>')
    for i in range(8):
        x = 0.05*W + i*0.13*W
        parts.append(f'<line x1="{x}" y1="{0.06*H}" x2="{x}" y2="{0.94*H}" stroke="{hx("road")}" stroke-width="3"/>')
    d = f"M {0.05*W} {0.88*H} L {0.31*W} {0.88*H} L {0.31*W} {0.50*H} L {0.70*W} {0.50*H} L {0.70*W} {0.12*H} L {0.96*W} {0.12*H}"
    parts.append(f'<path d="{d}" fill="none" stroke="{hx("teal")}" stroke-opacity="0.25" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append(f'<path d="{d}" fill="none" stroke="{hx("teal")}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
    parts.append(f'<circle cx="{0.05*W}" cy="{0.88*H}" r="{0.055*H*2}" fill="{hx("bg2")}" stroke="{hx("teal")}" stroke-width="4"/>')
    parts.append(f'<path d="M {0.96*W-16} {0.12*H} l 32 0 M {0.96*W} {0.12*H-16} l 0 32" stroke="{hx("teal")}" stroke-width="6" stroke-linecap="round"/>')
    parts.append(f'<circle cx="{0.96*W}" cy="{0.12*H}" r="26" fill="none" stroke="{hx("teal")}" stroke-width="4"/>')
    parts.append(f'<circle cx="{0.51*W}" cy="{0.50*H}" r="17" fill="{hx("bg")}" stroke="{hx("red")}" stroke-width="4"/>')
    parts.append(f'<path d="M {0.51*W-7} {0.50*H-7} l 14 14 M {0.51*W+7} {0.50*H-7} l -14 14" stroke="{hx("red")}" stroke-width="4" stroke-linecap="round"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)

def mini_darkzone(name="mini_darkzone", W=760, H=185):
    """a patch of map that is unreachable AND uncovered"""
    parts = [f'<rect width="{W}" height="{H}" fill="none"/>']
    for i in range(5):
        y = 0.10*H + i*0.20*H
        parts.append(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{hx("road")}" stroke-width="3"/>')
    for i in range(9):
        x = 0.04*W + i*0.115*W
        parts.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{H}" stroke="{hx("road")}" stroke-width="3"/>')
    # surviving tower coverage on the left
    parts.append(f'<circle cx="{0.10*W}" cy="{0.50*H}" r="{0.62*H}" fill="{hx("teal")}" fill-opacity="0.08" '
                 f'stroke="{hx("teal")}" stroke-opacity="0.55" stroke-width="3"/>')
    # failed tower coverage on the right
    parts.append(f'<circle cx="{0.90*W}" cy="{0.50*H}" r="{0.58*H}" fill="none" '
                 f'stroke="{hx("red")}" stroke-opacity="0.45" stroke-width="3" stroke-dasharray="10 8"/>')
    parts.append(f'<path d="M {0.90*W-16} {0.50*H-16} l 32 32 M {0.90*W+16} {0.50*H-16} l -32 32" '
                 f'stroke="{hx("red")}" stroke-width="5" stroke-linecap="round"/>')
    # the dark zone patch
    dz = (f"M {0.40*W} {0.16*H} L {0.62*W} {0.12*H} L {0.70*W} {0.54*H} "
          f"L {0.58*W} {0.90*H} L {0.38*W} {0.82*H} Z")
    parts.append(f'<path d="{dz}" fill="{hx("violet")}" fill-opacity="0.55" stroke="{hx("violetLt")}" stroke-width="4"/>')
    # blocked route to the hospital
    parts.append(f'<path d="M {0.30*W} {0.50*H} L {0.10*W} {0.50*H}" stroke="{hx("amber")}" '
                 f'stroke-width="5" stroke-dasharray="12 8"/>')
    parts.append(f'<circle cx="{0.245*W}" cy="{0.50*H}" r="20" fill="{hx("bg")}" stroke="{hx("red")}" stroke-width="4"/>')
    parts.append(f'<path d="M {0.245*W-8} {0.50*H-8} l 16 16 M {0.245*W+8} {0.50*H-8} l -16 16" '
                 f'stroke="{hx("red")}" stroke-width="4" stroke-linecap="round"/>')
    parts.append(f'<rect x="{0.055*W}" y="{0.36*H}" width="46" height="46" rx="8" fill="{hx("bg2")}" '
                 f'stroke="{hx("teal")}" stroke-width="4"/>')
    parts.append(f'<text x="{0.055*W+23}" y="{0.36*H+35}" font-family="Libre Franklin" font-size="30" '
                 f'font-weight="700" fill="{hx("teal")}" text-anchor="middle">H</text>')
    parts.append(f'<text x="{0.535*W}" y="{0.58*H}" font-family="Libre Franklin" font-size="27" '
                 f'font-weight="700" fill="{hx("ink")}" text-anchor="middle" letter-spacing="1.6">DARK ZONE</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ---------------------------------------------------------------- slide 6 dashboard mockup
def dashboard(name="dashboard", W=1320, H=860):
    g = _road_net(W, H, seed=21)
    fx, fy = 0.34*W, 0.26*H          # failed bridge
    dz = f"M {0.39*W} {0.58*H} L {0.545*W} {0.545*H} L {0.60*W} {0.73*H} L {0.50*W} {0.89*H} L {0.375*W} {0.81*H} Z"
    parts = [f'<rect width="{W}" height="{H}" fill="{hx("bg")}"/>', g]
    # tower coverage circles
    for (tx, ty, r, ok) in [(0.12*W,0.22*H,0.185*W,1),(0.20*W,0.72*H,0.16*W,1),(0.52*W,0.74*H,0.175*W,0)]:
        col = hx("teal") if ok else hx("red")
        parts.append(f'<circle cx="{tx}" cy="{ty}" r="{r}" fill="{col}" fill-opacity="{0.055 if ok else 0.03}" stroke="{col}" stroke-opacity="{0.35 if ok else 0.30}" stroke-width="2" stroke-dasharray="{"0" if ok else "8 6"}"/>')
    # dark zone polygon
    parts.append(f'<path d="{dz}" fill="{hx("violet")}" fill-opacity="0.30" stroke="{hx("violetLt")}" stroke-width="3"/>')
    parts.append(f'<text x="{0.487*W}" y="{0.725*H}" font-family="Libre Franklin" font-size="34" font-weight="700" fill="{hx("violetLt")}" text-anchor="middle" letter-spacing="1.6">DARK ZONE</text>')
    # cascade path highlight
    cp = f"M {fx} {fy} C {0.40*W} {0.36*H}, {0.33*W} {0.44*H}, {0.28*W} {0.56*H} S {0.24*W} {0.76*H}, {0.185*W} {0.88*H}"
    parts.append(f'<path d="{cp}" fill="none" stroke="{hx("amber")}" stroke-opacity="0.30" stroke-width="18" stroke-linecap="round"/>')
    parts.append(f'<path d="{cp}" fill="none" stroke="{hx("amber")}" stroke-width="5" stroke-linecap="round"/>')
    # failed asset marker
    parts.append(f'<circle cx="{fx}" cy="{fy}" r="60" fill="{hx("red")}" fill-opacity="0.14"/>')
    parts.append(f'<circle cx="{fx}" cy="{fy}" r="34" fill="{hx("red")}" fill-opacity="0.22" stroke="{hx("red")}" stroke-width="3.5"/>')
    parts.append(f'<path d="M {fx-14} {fy-14} l 28 28 M {fx+14} {fy-14} l -28 28" stroke="{hx("red")}" stroke-width="4" stroke-linecap="round"/>')
    # domino markers
    for i, (mx, my) in enumerate([(0.28*W,0.56*H),(0.185*W,0.88*H)]):
        parts.append(f'<circle cx="{mx}" cy="{my}" r="34" fill="{hx("bg2")}" stroke="{hx("amber")}" stroke-width="4"/>')
        parts.append(f'<text x="{mx}" y="{my+11}" font-family="Libre Franklin" font-size="32" font-weight="700" fill="{hx("amber")}" text-anchor="middle">{i+1}</text>')
    # hospital + fire markers
    for (mx, my, sym) in [(0.095*W,0.46*H,"H"),(0.44*W,0.40*H,"F")]:
        parts.append(f'<rect x="{mx-27}" y="{my-27}" width="54" height="54" rx="11" fill="{hx("bg2")}" stroke="{hx("teal")}" stroke-width="3"/>')
        parts.append(f'<text x="{mx}" y="{my+12}" font-family="Libre Franklin" font-size="34" font-weight="700" fill="{hx("teal")}" text-anchor="middle">{sym}</text>')

    # ---- UI chrome overlay (type sized to stay legible at ~5.4in wide)
    pw = 0.365*W
    px = W - pw - 18
    parts.append(f'<rect x="{px}" y="18" width="{pw}" height="{H-36}" rx="10" fill="{hx("panel")}" fill-opacity="0.97" stroke="{hx("line2")}" stroke-width="2"/>')
    parts.append(f'<text x="{px+22}" y="62" font-family="Libre Franklin" font-size="28" font-weight="700" fill="{hx("ink3")}" letter-spacing="1.6">CASCADE QUEUE</text>')
    rows = [("BRIDGE UDP-B07", "FAILED", "red", "SEED"),
            ("ROAD R24",  "DOMINO 1", "amber", "0.87"),
            ("ROAD R31",  "DOMINO 2", "amber", "0.64"),
            ("ROAD R09",  "CANDIDATE", "ink3", "0.41")]
    iw = pw - 44
    ry = 84
    for lbl, st, col, sc in rows:
        parts.append(f'<rect x="{px+22}" y="{ry}" width="{iw}" height="82" rx="8" fill="{hx("panel2")}" stroke="{hx(col)}" stroke-opacity="0.55" stroke-width="2"/>')
        parts.append(f'<rect x="{px+22}" y="{ry}" width="6" height="82" rx="3" fill="{hx(col)}"/>')
        parts.append(f'<text x="{px+42}" y="{ry+34}" font-family="Libre Franklin" font-size="29" font-weight="700" fill="{hx("ink")}">{lbl}</text>')
        parts.append(f'<text x="{px+42}" y="{ry+64}" font-family="Libre Franklin" font-size="24" fill="{hx(col)}" letter-spacing="1">{st}</text>')
        parts.append(f'<text x="{px+iw+6}" y="{ry+54}" font-family="Source Serif 4" font-size="33" font-weight="700" fill="{hx(col)}" text-anchor="end">{sc}</text>')
        ry += 94
    ry += 8
    parts.append(f'<rect x="{px+22}" y="{ry}" width="{iw}" height="132" rx="9" fill="{hx("teal")}" fill-opacity="0.11" stroke="{hx("teal")}" stroke-width="2.5"/>')
    parts.append(f'<text x="{px+42}" y="{ry+38}" font-family="Libre Franklin" font-size="24" font-weight="700" fill="{hx("teal")}" letter-spacing="1.4">INTERVENTION TEST</text>')
    parts.append(f'<text x="{px+42}" y="{ry+82}" font-family="Source Serif 4" font-size="38" font-weight="700" fill="{hx("teal")}">CASCADE STOPPED</text>')
    parts.append(f'<text x="{px+42}" y="{ry+114}" font-family="Libre Franklin" font-size="23" fill="{hx("ink2")}">reinforce R24, 2 dominoes averted</text>')
    dy = ry + 154
    parts.append(f'<rect x="{px+22}" y="{dy}" width="{iw}" height="126" rx="9" fill="{hx("violet")}" fill-opacity="0.16" stroke="{hx("violet")}" stroke-width="2.5"/>')
    parts.append(f'<text x="{px+42}" y="{dy+38}" font-family="Libre Franklin" font-size="24" font-weight="700" fill="{hx("violetLt")}" letter-spacing="1.4">DARK ZONE, PRIORITY 1</text>')
    parts.append(f'<text x="{px+42}" y="{dy+80}" font-family="Source Serif 4" font-size="38" font-weight="700" fill="{hx("ink")}">ZONE D-03</text>')
    parts.append(f'<text x="{px+42}" y="{dy+110}" font-family="Libre Franklin" font-size="22" fill="{hx("ink2")}">no route to hospital, no tower coverage</text>')
    parts.append(f'<rect x="18" y="18" width="{0.40*W}" height="66" rx="9" fill="{hx("panel")}" fill-opacity="0.95" stroke="{hx("line2")}" stroke-width="2"/>')
    parts.append(f'<circle cx="50" cy="51" r="10" fill="{hx("red")}"/>')
    parts.append(f'<text x="74" y="61" font-family="Libre Franklin" font-size="28" font-weight="700" fill="{hx("ink")}" letter-spacing="1.2">SCENARIO: BRIDGE FAILURE</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ---------------------------------------------------------------- slide 8 backdrop
def domino_field(name="domino_field", W=1500, H=845, seed=3):
    rnd = random.Random(seed)
    parts = [f'<rect width="{W}" height="{H}" fill="{hx("bg")}"/>', _road_net(W, H, seed=13)]
    for i in range(26):
        x = rnd.uniform(0.02, 0.98) * W
        y = rnd.uniform(0.05, 0.95) * H
        h = rnd.uniform(0.05, 0.10) * H
        w = h * 0.42
        rot = rnd.uniform(-70, -8)
        col = hx(rnd.choice(["amber", "amber", "violet", "red", "teal"]))
        op = rnd.uniform(0.12, 0.40)
        parts.append(f'<g transform="rotate({rot:.0f} {x:.0f} {y+h:.0f})"><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="3" fill="{col}" fill-opacity="{op*0.35:.2f}" stroke="{col}" stroke-opacity="{op:.2f}" stroke-width="2"/></g>')
    parts.append(f'''<defs><radialGradient id="v2" cx="0.42" cy="0.5" r="0.7">
      <stop offset="0.25" stop-color="{hx('bg')}" stop-opacity="0.96"/>
      <stop offset="1" stop-color="{hx('bg')}" stop-opacity="0.60"/></radialGradient></defs>
      <rect width="{W}" height="{H}" fill="url(#v2)"/>''')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ---------------------------------------------------------------- slide 5 recovery ribbon
def recovery_ribbon(name="recovery_ribbon", W=1500, H=300):
    """baseline -> drop -> recovery, as a filled area curve, no text"""
    y = lambda v: H - (v - 60) / 30.0 * H * 0.80 - 0.10 * H
    x0, x1, x2 = 0.10*W, 0.50*W, 0.90*W
    d = (f"M {x0} {y(81.1)} C {x0+0.13*W} {y(81.1)}, {x1-0.13*W} {y(68.3)}, {x1} {y(68.3)} "
         f"C {x1+0.13*W} {y(68.3)}, {x2-0.13*W} {y(83.3)}, {x2} {y(83.3)}")
    area = d + f" L {x2} {H} L {x0} {H} Z"
    parts = [
      f'<defs><linearGradient id="rg" x1="0" y1="0" x2="0" y2="1">'
      f'<stop offset="0" stop-color="{hx("teal")}" stop-opacity="0.26"/>'
      f'<stop offset="1" stop-color="{hx("teal")}" stop-opacity="0"/></linearGradient></defs>',
      f'<path d="{area}" fill="url(#rg)"/>',
      f'<line x1="0" y1="{y(81.1)}" x2="{W}" y2="{y(81.1)}" stroke="{hx("line2")}" stroke-width="2" stroke-dasharray="6 6"/>',
      f'<path d="{d}" fill="none" stroke="{hx("teal")}" stroke-width="5" stroke-linecap="round"/>',
    ]
    for xx, vv, col in [(x0, 81.1, "ink2"), (x1, 68.3, "red"), (x2, 83.3, "teal")]:
        parts.append(f'<circle cx="{xx}" cy="{y(vv)}" r="16" fill="{hx("bg")}" stroke="{hx(col)}" stroke-width="5"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


if __name__ == "__main__":
    for f in (map_hero, cascade_chain, dep_web, mini_earliest, mini_score,
              mini_priority, mini_darkzone, dashboard, domino_field, recovery_ribbon):
        print(f())
