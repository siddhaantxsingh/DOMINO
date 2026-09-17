"""Light-theme plates for the 5-slide deck (M#26 'Simple Light' scheme)."""
import os, random
import cairosvg
from dsys import C
OUT = "assets"

def hx(k): return "#" + C.get(k, k)
def _w(svg, name, w, h):
    p = f"{OUT}/{name}.png"
    cairosvg.svg2png(bytestring=svg.encode(), write_to=p, output_width=w, output_height=h)
    return p


def _roads(W, H, seed=7, road_op=0.55, blk=0.030):
    rnd = random.Random(seed)
    p = []
    rp = (f"M {-0.05*W} {0.30*H} C {0.22*W} {0.20*H}, {0.30*W} {0.62*H}, {0.52*W} {0.58*H} "
          f"S {0.82*W} {0.42*H}, {1.06*W} {0.52*H}")
    p.append(f'<path d="{rp}" fill="none" stroke="{hx("blue")}" stroke-opacity="0.14" '
             f'stroke-width="{0.055*H}" stroke-linecap="round"/>')
    arterials = [
        f"M {-0.04*W} {0.78*H} C {0.20*W} {0.72*H}, {0.28*W} {0.40*H}, {0.48*W} {0.34*H} S {0.80*W} {0.26*H}, {1.05*W} {0.16*H}",
        f"M {0.10*W} {-0.05*H} C {0.16*W} {0.28*H}, {0.32*W} {0.48*H}, {0.38*W} {1.05*H}",
        f"M {1.04*W} {0.72*H} C {0.80*W} {0.76*H}, {0.70*W} {0.60*H}, {0.50*W} {0.60*H} S {0.22*W} {0.90*H}, {0.05*W} {1.04*H}",
        f"M {0.72*W} {-0.04*H} C {0.70*W} {0.30*H}, {0.80*W} {0.52*H}, {0.76*W} {1.04*H}",
    ]
    for a in arterials:
        p.append(f'<path d="{a}" fill="none" stroke="{hx("road")}" stroke-opacity="{road_op}" '
                 f'stroke-width="{0.016*H}" stroke-linecap="round"/>')
    for i in range(16):
        x = rnd.uniform(-0.02, 1.0) * W
        y0 = rnd.uniform(-0.05, 0.4) * H
        y1 = y0 + rnd.uniform(0.25, 0.75) * H
        k = rnd.uniform(-0.08, 0.08) * W
        p.append(f'<path d="M {x:.1f} {y0:.1f} C {x+k:.1f} {(y0+y1)/2:.1f}, {x+k:.1f} '
                 f'{(y0+y1)/2:.1f}, {x+k*1.5:.1f} {y1:.1f}" fill="none" stroke="{hx("road")}" '
                 f'stroke-opacity="{road_op*0.55}" stroke-width="{0.0055*H}"/>')
    for i in range(13):
        y = rnd.uniform(0, 1.0) * H
        x0 = rnd.uniform(-0.05, 0.45) * W
        x1 = x0 + rnd.uniform(0.25, 0.7) * W
        k = rnd.uniform(-0.05, 0.05) * H
        p.append(f'<path d="M {x0:.1f} {y:.1f} C {(x0+x1)/2:.1f} {y+k:.1f}, {(x0+x1)/2:.1f} '
                 f'{y+k:.1f}, {x1:.1f} {y+k*1.4:.1f}" fill="none" stroke="{hx("road")}" '
                 f'stroke-opacity="{road_op*0.55}" stroke-width="{0.0055*H}"/>')
    for i in range(34):
        bw = rnd.uniform(0.03, 0.09) * W
        bh = rnd.uniform(0.05, 0.13) * H
        bx = rnd.uniform(0, 1) * W - bw / 2
        by = rnd.uniform(0, 1) * H - bh / 2
        p.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
                 f'rx="{0.004*H}" fill="{hx("road")}" fill-opacity="{blk}"/>')
    return "".join(p)


def map_plate(name="map_plate_lt", W=1780, H=1001, seed=7):
    """near-white watermark map for the title slide"""
    g = _roads(W, H, seed, road_op=0.22, blk=0.020)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><radialGradient id="v" cx="0.62" cy="0.42" r="0.66">
 <stop offset="0.30" stop-color="#FFFFFF" stop-opacity="0"/>
 <stop offset="1" stop-color="#FFFFFF" stop-opacity="0.92"/></radialGradient></defs>
<rect width="{W}" height="{H}" fill="#FFFFFF"/>{g}
<rect width="{W}" height="{H}" fill="url(#v)"/></svg>'''
    return _w(svg, name, W, H)


def dashboard(name="dashboard_lt", W=1000, H=650):
    """light operator view, typed for display at roughly 4.5 inches wide"""
    g = _roads(W, H, seed=21, road_op=0.50, blk=0.035)
    fx, fy = 0.30 * W, 0.24 * H
    pw = 0.40 * W
    px = W - pw - 14
    dz = (f"M {0.36*W} {0.58*H} L {0.50*W} {0.545*H} L {0.555*W} {0.73*H} "
          f"L {0.455*W} {0.89*H} L {0.345*W} {0.81*H} Z")
    p = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>', g]
    for tx, ty, r, ok in [(0.10*W, 0.22*H, 0.19*W, 1), (0.17*W, 0.74*H, 0.16*W, 1),
                          (0.47*W, 0.76*H, 0.17*W, 0)]:
        c = hx("teal") if ok else hx("red")
        p.append(f'<circle cx="{tx}" cy="{ty}" r="{r}" fill="{c}" fill-opacity="0.05" '
                 f'stroke="{c}" stroke-opacity="0.35" stroke-width="2" '
                 f'stroke-dasharray="{"0" if ok else "7 5"}"/>')
    p.append(f'<path d="{dz}" fill="{hx("violet")}" fill-opacity="0.22" '
             f'stroke="{hx("violet")}" stroke-width="2.5"/>')
    p.append(f'<text x="{0.448*W}" y="{0.725*H}" font-family="Libre Franklin" font-size="24" '
             f'font-weight="700" fill="{hx("violet")}" text-anchor="middle" letter-spacing="1.2">DARK ZONE</text>')
    cp = (f"M {fx} {fy} C {0.36*W} {0.34*H}, {0.30*W} {0.42*H}, {0.25*W} {0.55*H} "
          f"S {0.21*W} {0.75*H}, {0.16*W} {0.87*H}")
    p.append(f'<path d="{cp}" fill="none" stroke="{hx("amber")}" stroke-opacity="0.22" stroke-width="13" stroke-linecap="round"/>')
    p.append(f'<path d="{cp}" fill="none" stroke="{hx("amber")}" stroke-width="4" stroke-linecap="round"/>')
    p.append(f'<circle cx="{fx}" cy="{fy}" r="40" fill="{hx("red")}" fill-opacity="0.10"/>')
    p.append(f'<circle cx="{fx}" cy="{fy}" r="23" fill="#FFFFFF" stroke="{hx("red")}" stroke-width="3"/>')
    p.append(f'<path d="M {fx-9} {fy-9} l 18 18 M {fx+9} {fy-9} l -18 18" stroke="{hx("red")}" stroke-width="3.4" stroke-linecap="round"/>')
    for i, (mx, my) in enumerate([(0.25*W, 0.55*H), (0.16*W, 0.87*H)]):
        p.append(f'<circle cx="{mx}" cy="{my}" r="22" fill="#FFFFFF" stroke="{hx("amber")}" stroke-width="3"/>')
        p.append(f'<text x="{mx}" y="{my+8}" font-family="Libre Franklin" font-size="23" '
                 f'font-weight="700" fill="{hx("amber")}" text-anchor="middle">{i+1}</text>')
    for mx, my, sym in [(0.075*W, 0.46*H, "H"), (0.40*W, 0.38*H, "F")]:
        p.append(f'<rect x="{mx-19}" y="{my-19}" width="38" height="38" rx="8" fill="#FFFFFF" '
                 f'stroke="{hx("teal")}" stroke-width="3"/>')
        p.append(f'<text x="{mx}" y="{my+9}" font-family="Libre Franklin" font-size="25" '
                 f'font-weight="700" fill="{hx("teal")}" text-anchor="middle">{sym}</text>')

    p.append(f'<rect x="{px}" y="14" width="{pw}" height="{H-28}" rx="9" fill="{hx("bg2")}" '
             f'fill-opacity="0.97" stroke="{hx("line2")}" stroke-width="2"/>')
    p.append(f'<text x="{px+18}" y="46" font-family="Libre Franklin" font-size="21" '
             f'font-weight="700" fill="{hx("ink3")}" letter-spacing="1.4">CASCADE QUEUE</text>')
    iw = pw - 36
    ry = 62
    for lbl, st, col, sc in [("BRIDGE UDP-B07", "FAILED", "red", "SEED"),
                             ("ROAD R24", "DOMINO 1", "amber", "0.87"),
                             ("ROAD R31", "DOMINO 2", "amber", "0.64")]:
        p.append(f'<rect x="{px+18}" y="{ry}" width="{iw}" height="62" rx="7" fill="#FFFFFF" '
                 f'stroke="{hx(col)}" stroke-opacity="0.55" stroke-width="2"/>')
        p.append(f'<rect x="{px+18}" y="{ry}" width="5" height="62" rx="2.5" fill="{hx(col)}"/>')
        p.append(f'<text x="{px+34}" y="{ry+27}" font-family="Libre Franklin" font-size="22" '
                 f'font-weight="700" fill="{hx("ink")}">{lbl}</text>')
        p.append(f'<text x="{px+34}" y="{ry+50}" font-family="Libre Franklin" font-size="18" '
                 f'fill="{hx(col)}" letter-spacing="0.8">{st}</text>')
        p.append(f'<text x="{px+iw+10}" y="{ry+41}" font-family="Source Serif 4" font-size="26" '
                 f'font-weight="700" fill="{hx(col)}" text-anchor="end">{sc}</text>')
        ry += 72
    ry += 6
    p.append(f'<rect x="{px+18}" y="{ry}" width="{iw}" height="100" rx="8" fill="{hx("teal")}" '
             f'fill-opacity="0.08" stroke="{hx("teal")}" stroke-width="2.2"/>')
    p.append(f'<text x="{px+34}" y="{ry+28}" font-family="Libre Franklin" font-size="18" '
             f'font-weight="700" fill="{hx("teal")}" letter-spacing="1.1">INTERVENTION TEST</text>')
    p.append(f'<text x="{px+34}" y="{ry+62}" font-family="Source Serif 4" font-size="29" '
             f'font-weight="700" fill="{hx("teal")}">CASCADE STOPPED</text>')
    p.append(f'<text x="{px+34}" y="{ry+86}" font-family="Libre Franklin" font-size="17" '
             f'fill="{hx("ink2")}">reinforce R24, 2 averted</text>')
    dy = ry + 116
    p.append(f'<rect x="{px+18}" y="{dy}" width="{iw}" height="94" rx="8" fill="{hx("violet")}" '
             f'fill-opacity="0.10" stroke="{hx("violet")}" stroke-width="2.2"/>')
    p.append(f'<text x="{px+34}" y="{dy+28}" font-family="Libre Franklin" font-size="18" '
             f'font-weight="700" fill="{hx("violet")}" letter-spacing="1.1">DARK ZONE, PRIORITY 1</text>')
    p.append(f'<text x="{px+34}" y="{dy+60}" font-family="Source Serif 4" font-size="29" '
             f'font-weight="700" fill="{hx("ink")}">ZONE D-03</text>')
    p.append(f'<text x="{px+34}" y="{dy+83}" font-family="Libre Franklin" font-size="17" '
             f'fill="{hx("ink2")}">no route, no coverage</text>')
    p.append(f'<rect x="14" y="14" width="{0.375*W}" height="48" rx="8" fill="#FFFFFF" '
             f'fill-opacity="0.95" stroke="{hx("line2")}" stroke-width="2"/>')
    p.append(f'<circle cx="40" cy="38" r="8" fill="{hx("red")}"/>')
    p.append(f'<text x="58" y="46" font-family="Libre Franklin" font-size="21" font-weight="700" '
             f'fill="{hx("ink")}" letter-spacing="0.9">SCENARIO: BRIDGE FAILURE</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(p)}</svg>'
    return _w(svg, name, W, H)


if __name__ == "__main__":
    import dsys
    dsys.use_light()
    print(map_plate())
    print(dashboard())
