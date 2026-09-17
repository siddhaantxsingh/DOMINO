"""Illustrations for the added slides: horizon, time-to-dark, two clocks, playbook."""
import os, math, random
import cairosvg
from dsys import C
from graphics import _road_net, hx, _write


# ─────────────────────────────────────────── containment horizon
def horizon_chart(name="horizon_chart", W=1500, H=620):
    """cascade steps; a vertical horizon after which no action holds the chain"""
    n = 6
    x0, x1 = 0.09 * W, 0.94 * W
    step = (x1 - x0) / (n - 1)
    base = 0.74 * H
    hz = 2
    parts = []
    bx, by, bw, bh = x0 - 0.035 * W, 0.16 * H, step * hz + 0.075 * W, 0.62 * H
    parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="10" '
                 f'fill="{hx("teal")}" fill-opacity="0.10" stroke="{hx("teal")}" '
                 f'stroke-width="3" stroke-dasharray="10 7"/>')
    hxl = bx + bw
    parts.append(f'<line x1="{hxl}" y1="{0.14*H}" x2="{hxl}" y2="{0.80*H}" stroke="{hx("red")}" stroke-width="4"/>')
    parts.append(f'<text x="{bx}" y="{0.095*H}" font-family="Libre Franklin" font-size="30" '
                 f'font-weight="700" fill="{hx("teal")}" letter-spacing="1.2">STILL CONTAINABLE</text>')
    parts.append(f'<text x="{hxl+16}" y="{0.095*H}" font-family="Libre Franklin" font-size="30" '
                 f'font-weight="700" fill="{hx("red")}" letter-spacing="1.2">PAST THE HORIZON</text>')
    parts.append(f'<line x1="0" y1="{base}" x2="{W}" y2="{base}" stroke="{hx("line2")}" stroke-width="3"/>')
    for i in range(n):
        x = x0 + i * step
        h = (0.10 + i * 0.085) * H
        col = "teal" if i <= hz else "red"
        parts.append(f'<rect x="{x-0.024*W}" y="{base-h}" width="{0.048*W}" height="{h}" rx="6" '
                     f'fill="{hx(col)}" fill-opacity="{0.95 if i <= hz else 0.80}"/>')
        parts.append(f'<text x="{x}" y="{0.875*H}" font-family="Libre Franklin" font-size="30" '
                     f'font-weight="700" fill="{hx("ink3")}" text-anchor="middle">{i}</text>')
    parts.append(f'<text x="{(x0+x1)/2}" y="{0.965*H}" font-family="Libre Franklin" font-size="27" '
                 f'fill="{hx("ink4")}" text-anchor="middle" letter-spacing="1.2">CASCADE STEP</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ─────────────────────────────────────────── time to dark
def time_to_dark(name="time_to_dark", W=1320, H=760):
    """map fragment: three zones going dark at different times after the seed failure"""
    parts = [f'<rect width="{W}" height="{H}" fill="{hx("bg")}"/>', _road_net(W, H, seed=31)]
    fx, fy = 0.12 * W, 0.13 * H
    # surviving coverage
    parts.append(f'<circle cx="{0.13*W}" cy="{0.70*H}" r="{0.30*W}" fill="{hx("teal")}" fill-opacity="0.05" '
                 f'stroke="{hx("teal")}" stroke-opacity="0.40" stroke-width="3"/>')
    # failed tower
    parts.append(f'<circle cx="{0.74*W}" cy="{0.52*H}" r="{0.31*W}" fill="none" stroke="{hx("red")}" '
                 f'stroke-opacity="0.40" stroke-width="3" stroke-dasharray="12 9"/>')
    zones = [
        ("D-01", "T+40 min", 0.50, 0.30, 0.90),
        ("D-02", "T+70 min", 0.74, 0.58, 0.62),
        ("D-03", "T+95 min", 0.42, 0.78, 0.38),
    ]
    for label, t, cx, cy, op in zones:
        cx, cy = cx * W, cy * H
        w, h = 0.20 * W, 0.20 * H
        poly = (f"M {cx-w*0.5} {cy-h*0.42} L {cx+w*0.42} {cy-h*0.52} L {cx+w*0.55} {cy+h*0.30} "
                f"L {cx+w*0.05} {cy+h*0.58} L {cx-w*0.52} {cy+h*0.36} Z")
        parts.append(f'<path d="{poly}" fill="{hx("violet")}" fill-opacity="{0.52*op:.2f}" '
                     f'stroke="{hx("violetLt")}" stroke-opacity="{op:.2f}" stroke-width="4"/>')
        parts.append(f'<text x="{cx}" y="{cy-6}" font-family="Source Serif 4" font-size="36" '
                     f'font-weight="700" fill="{hx("ink")}" text-anchor="middle">{label}</text>')
        parts.append(f'<rect x="{cx-86}" y="{cy+12}" width="172" height="44" rx="22" fill="{hx("bg")}" '
                     f'fill-opacity="0.85" stroke="{hx("violetLt")}" stroke-width="3"/>')
        parts.append(f'<text x="{cx}" y="{cy+43}" font-family="Libre Franklin" font-size="28" '
                     f'font-weight="700" fill="{hx("violetLt")}" text-anchor="middle" letter-spacing="1">{t}</text>')
    # the seed
    parts.append(f'<circle cx="{fx}" cy="{fy}" r="58" fill="{hx("red")}" fill-opacity="0.13"/>')
    parts.append(f'<circle cx="{fx}" cy="{fy}" r="33" fill="{hx("red")}" fill-opacity="0.22" '
                 f'stroke="{hx("red")}" stroke-width="4"/>')
    parts.append(f'<path d="M {fx-13} {fy-13} l 26 26 M {fx+13} {fy-13} l -26 26" stroke="{hx("red")}" '
                 f'stroke-width="5" stroke-linecap="round"/>')
    parts.append(f'<text x="{fx+52}" y="{fy+12}" font-family="Libre Franklin" font-size="30" '
                 f'font-weight="700" fill="{hx("red")}" letter-spacing="1.2">T+0  SEED FAILURE</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ─────────────────────────────────────────── two clocks
def two_clocks(name="two_clocks", W=2000, H=300):
    """one timeline, two action windows either side of the failure"""
    mid = 0.50 * W
    y = 0.50 * H
    parts = [
        f'<rect x="0" y="{y-6}" width="{mid-70}" height="12" rx="6" fill="{hx("teal")}" fill-opacity="0.35"/>',
        f'<rect x="{mid+70}" y="{y-6}" width="{W-mid-70}" height="12" rx="6" fill="{hx("amber")}" fill-opacity="0.35"/>',
        f'<circle cx="{mid}" cy="{y}" r="46" fill="{hx("red")}" fill-opacity="0.16" stroke="{hx("red")}" stroke-width="5"/>',
        f'<path d="M {mid-17} {y-17} l 34 34 M {mid+17} {y-17} l -34 34" stroke="{hx("red")}" stroke-width="6" stroke-linecap="round"/>',
        f'<text x="{mid}" y="{y-72}" font-family="Libre Franklin" font-size="34" font-weight="700" '
        f'fill="{hx("red")}" text-anchor="middle" letter-spacing="1.4">FAILURE</text>',
    ]
    for lbl, sub, cx, col, anc in [("HARDEN", "months  ·  capital budget", 0.20*W, "teal", "middle"),
                                   ("RESPOND", "minutes  ·  operations", 0.80*W, "amber", "middle")]:
        parts.append(f'<text x="{cx}" y="{y-58}" font-family="Source Serif 4" font-size="46" '
                     f'font-weight="700" fill="{hx(col)}" text-anchor="{anc}">{lbl}</text>')
        parts.append(f'<text x="{cx}" y="{y+72}" font-family="Libre Franklin" font-size="30" '
                     f'fill="{hx("ink3")}" text-anchor="{anc}" letter-spacing="0.8">{sub}</text>')
    for cx, col in [(0.08*W, "teal"), (0.20*W, "teal"), (0.32*W, "teal"),
                    (0.68*W, "amber"), (0.80*W, "amber"), (0.92*W, "amber")]:
        parts.append(f'<circle cx="{cx}" cy="{y}" r="13" fill="{hx(col)}"/>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ─────────────────────────────────────────── playbook cards
def playbook(name="playbook", W=1290, H=690):
    """precomputed response cards; the front one is filled in"""
    parts = []
    backs = [("IF TOWER T-11 DROPS", "teal", 0.01, 0.07),
             ("IF ROAD R24 CLOSES", "violet", 0.125, 0.035)]
    for title, col, fy, fx in backs:
        x, y = fx * W, fy * H
        cw = W - x - 0.03 * W
        parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{0.30*H}" rx="12" fill="{hx("panel")}" '
                     f'stroke="{hx(col)}" stroke-opacity="0.70" stroke-width="3"/>')
        parts.append(f'<rect x="{x}" y="{y}" width="9" height="{0.30*H}" rx="4" fill="{hx(col)}"/>')
        parts.append(f'<text x="{x+38}" y="{y+62}" font-family="Source Serif 4" font-size="46" '
                     f'font-weight="700" fill="{hx("ink3")}">{title}</text>')
    x, y = 0.0, 0.255 * H
    cw, ch = W - 0.05 * W, 0.735 * H
    parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" rx="12" fill="{hx("panel2")}" '
                 f'stroke="{hx("amber")}" stroke-width="4"/>')
    parts.append(f'<rect x="{x}" y="{y}" width="9" height="{ch}" rx="4" fill="{hx("amber")}"/>')
    parts.append(f'<text x="{x+38}" y="{y+76}" font-family="Source Serif 4" font-size="56" '
                 f'font-weight="700" fill="{hx("ink")}">IF BRIDGE B07 FAILS</text>')
    rows = [("NEXT DOMINO", "Road R24, score 0.87", "amber"),
            ("ACTION", "contraflow on R31, open the service road", "teal"),
            ("DEADLINE", "within 90 min, horizon = 2 steps", "red"),
            ("DARK ZONE", "D-01 goes dark at T+40 min", "violetLt"),
            ("OWNER", "traffic control room, city engineer on call", "ink3")]
    ry = y + 150
    for k, v, c in rows:
        parts.append(f'<text x="{x+38}" y="{ry}" font-family="Libre Franklin" font-size="36" '
                     f'font-weight="700" fill="{hx(c)}" letter-spacing="0.8">{k}</text>')
        parts.append(f'<text x="{x+420}" y="{ry}" font-family="Libre Franklin" font-size="36" '
                     f'fill="{hx("ink2")}">{v}</text>')
        ry += 62
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


# ─────────────────────────────────────────── better-than-baseline
def baseline_step(name="baseline_step", W=1500, H=330):
    """81.1 -> 68.3 -> 83.3, with the baseline drawn through so the overshoot is visible"""
    def y(v): return H - (v - 62) / 26.0 * H * 0.72 - 0.14 * H
    x0, x1, x2 = 0.12 * W, 0.50 * W, 0.88 * W
    d = (f"M {x0} {y(81.1)} C {x0+0.13*W} {y(81.1)}, {x1-0.13*W} {y(68.3)}, {x1} {y(68.3)} "
         f"C {x1+0.13*W} {y(68.3)}, {x2-0.13*W} {y(83.3)}, {x2} {y(83.3)}")
    parts = [
        f'<line x1="0" y1="{y(81.1)}" x2="{W}" y2="{y(81.1)}" stroke="{hx("ink3")}" stroke-width="3" stroke-dasharray="9 7"/>',
        f'<text x="{0.012*W}" y="{y(81.1)-16}" font-family="Libre Franklin" font-size="26" '
        f'font-weight="700" fill="{hx("ink3")}" letter-spacing="1">ORIGINAL BASELINE</text>',
        f'<rect x="{x2-0.09*W}" y="{y(83.3)-10}" width="{0.18*W}" height="{y(81.1)-y(83.3)+20}" '
        f'fill="{hx("teal")}" fill-opacity="0.22"/>',
        f'<path d="{d}" fill="none" stroke="{hx("teal")}" stroke-width="6" stroke-linecap="round"/>',
    ]
    for xx, vv, col in [(x0, 81.1, "ink2"), (x1, 68.3, "red"), (x2, 83.3, "teal")]:
        parts.append(f'<circle cx="{xx}" cy="{y(vv)}" r="17" fill="{hx("bg")}" stroke="{hx(col)}" stroke-width="6"/>')
    parts.append(f'<text x="{x2}" y="{y(83.3)-34}" font-family="Libre Franklin" font-size="28" '
                 f'font-weight="700" fill="{hx("teal")}" text-anchor="middle" letter-spacing="1">ABOVE BASELINE</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    return _write(svg, name, W, H)


if __name__ == "__main__":
    for f in (horizon_chart, time_to_dark, two_clocks, playbook, baseline_step):
        print(f())
