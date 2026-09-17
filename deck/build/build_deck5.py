"""DOMINO — M#26 · P05 · Round 1.

Five sections, matching the sample template: Manipal Hackathon 2026 / Solution /
Technical Implementation / Feasibility / Business Strategy.
Palette and white background taken from the template's own "Simple Light" scheme.

Every number on these slides is produced by the engine in /proto or by our
separate study on real population data. The two sources are labelled apart.
"""
from pptx import Presentation
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from dsys import *
import dsys as D
D.use_light()
from dsys import C

TEAM     = "mossad.exe"
TRACK    = "[Track]"
MEMBERS  = "[Member 1]   ·   [Member 2]   ·   [Member 3]   ·   [Member 4]   ·   [Member 5]"
PS_ID    = "P05"
PS_TITLE = "Cascading Failure: When One Failure Becomes Many"
SOLUTION = "DOMINO"

prs = Presentation()
prs.slide_width, prs.slide_height = I(SW), I(SH)
BLANK = prs.slide_layouts[6]
def new():
    s = prs.slides.add_slide(BLANK); canvas(s); return s

def pic(sl, path, x, y, w=None, h=None):
    from PIL import Image
    iw, ih = Image.open(path).size
    if w and not h: h = w * ih / iw
    if h and not w: w = h * iw / ih
    return sl.shapes.add_picture(path, I(x), I(y), I(w), I(h))

def sq(sl, x, y, w, h, **kw): return panel(sl, x, y, w, h, **kw)
def klabel(sl, x, y, w, t, col="ink3", size=9.5):
    return text(sl, x, y, w, 0.22, [(t, {})], size=size, font=F_BODY, color=col,
                bold=True, spc=0.8, lh=1.0)
def ptitle(sl, x, y, w, t, col="ink", size=13):
    return text(sl, x, y, w, 0.26, [(t, {})], size=size, font=F_DISP, color=col,
                bold=True, lh=1.0)
def body(sl, x, y, w, h, t, size=10, col="ink2", lh=1.22, align=PP_ALIGN.LEFT):
    return text(sl, x, y, w, h, [(t, {})], size=size, font=F_BODY, color=col,
                lh=lh, align=align)
def chip_(sl, x, y, w, h, t, col, fill_alpha=0.12, size=9):
    rect(sl, x, y, w, h, fill=col, alpha=fill_alpha, line=col, line_alpha=0.75, lw=1.0)
    text(sl, x, y, w, h, [(t, {})], size=size, font=F_BODY, color=col, bold=True,
         spc=0.6, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, lh=1.0)

# ═════════════════════════════════════════════ 1 · MANIPAL HACKATHON 2026
s = new()
pic(s, "assets/map_plate_lt.png", 0, 0, w=SW, h=SH)
rect(s, 0, 0, SW, 0.62, fill="bg", alpha=0.88)
_sh = rect(s, 0, 0.56, 6.05, 3.95, fill="bg")
set_grad(_sh, [(0.0, "bg", 0.94), (0.72, "bg", 0.80), (1.0, "bg", 0.0)], angle=0)
_sh.line.fill.background()
rect(s, 0, 4.42, SW, 1.205, fill="bg", alpha=0.94)

text(s, M, 0.20, 5.6, 0.28, [("Manipal Hackathon 2026", {})], size=16, font=F_DISP,
     color="ink", bold=True, lh=1.0)
logo(s, x=LOGO_X, y=LOGO_Y, w=LOGO_W)
rect(s, 0, 0.62, SW, 0.014, fill="line")
rect(s, 0, 0.62, 1.62, 0.014, fill="amber")

rect(s, M, 0.86, 0.06, 0.26, fill="amber")
text(s, M + 0.18, 0.855, 5.3, 0.22,
     [("Problem Statement %s  ·  Cascading Failure" % PS_ID, {})],
     size=11, font=F_BODY, color="amber", bold=True, spc=0.3, lh=1.0)

text(s, M, 1.20, 5.40, 1.22,
     [("When one bridge fails,", {}), "BR", ("what breaks next?", {"color": "amber"})],
     size=35, font=F_DISP, color="ink", bold=True, lh=1.10, spc=-0.6)

rect(s, M, 2.52, 5.40, 0.012, fill="line2")
text(s, M, 2.66, 3.6, 0.68, [("DOMINO", {})], size=44, font=F_DISP, color="ink",
     bold=True, spc=2.4, lh=1.0)
text(s, M, 3.34, 5.40, 0.24,
     [("Explainable Infrastructure Cascade & Intervention Engine", {})],
     size=12.5, font=F_BODY, color="ink2", lh=1.0)
rect(s, M, 3.70, 5.40, 0.48, fill="amber", alpha=0.11, line="amber",
     line_alpha=0.55, lw=1.1)
rect(s, M, 3.70, 0.05, 0.48, fill="amber")
text(s, M + 0.20, 3.84, 5.15, 0.24,
     [("Find the next domino. Stop the cascade. Protect the dark zones.", {})],
     size=11, font=F_BODY, color="amber", bold=True, lh=1.0)

CX, CWID = 6.20, 3.38
klabel(s, CX, 0.85, CWID, "ONE BRIDGE, TRACED THROUGH OUR ENGINE")
ladder = [("bridge", "Bridge B07 fails", "89% can still reach help", "red"),
          ("road", "Coastal road N2", "jumps to 1.3× capacity", "amber"),
          ("hospital", "Hospital & fire routes", "87% of them use that road", "amber"),
          ("tower", "Tower T-04 is down", "no signal on the coast", "violet"),
          ("people", "Malpe ward, 5,200 people", "no road, no signal: dark", "violetLt")]
ly, lh_, lgap = 1.14, 0.545, 0.105
for i, (ic, nm, desc, col) in enumerate(ladder):
    y = ly + i * (lh_ + lgap)
    rect(s, CX, y, CWID, lh_, fill="panel", alpha=1.0, line=col, line_alpha=0.50, lw=1.1)
    rect(s, CX, y, 0.05, lh_, fill=col)
    put_icon(s, ic, CX + 0.22, y + lh_ / 2 - 0.14, 0.28, col, sw=1.7)
    text(s, CX + 0.64, y + 0.105, CWID - 0.78, 0.24, [(nm, {})], size=12,
         font=F_DISP, color="ink", bold=True, lh=1.0)
    text(s, CX + 0.64, y + 0.335, CWID - 0.78, 0.20, [(desc, {})], size=9.5,
         font=F_BODY, color="ink3", lh=1.0)
    if i < 4:
        line(s, CX + 0.40, y + lh_ + 0.010, CX + 0.40, y + lh_ + lgap - 0.010,
             col="line2", lw=1.4, arrow=True, aw="sm", al="sm")

rect(s, 0, 4.50, SW, 0.012, fill="line")
fields = [("TEAM NAME", TEAM, 0.0, 2.00),
          ("TRACK", TRACK, 2.18, 1.70),
          ("PROBLEM STATEMENT", "%s · Cascading Failure" % PS_ID, 4.06, 3.40),
          ("SOLUTION TITLE", SOLUTION, 7.62, 1.54)]
for lbl, val, dx, w in fields:
    x = M + dx
    text(s, x, 4.66, w, 0.20, [(lbl, {})], size=9, font=F_BODY, color="ink4",
         bold=True, spc=0.7, lh=1.0)
    text(s, x, 4.89, w, 0.28, [(val, {})], size=12.5, font=F_DISP, color="ink",
         bold=True, lh=1.0)
    if dx: rect(s, x - 0.17, 4.66, 0.008, 0.48, fill="line")
text(s, M, 5.28, 1.4, 0.20, [("TEAM MEMBERS", {})], size=9, font=F_BODY,
     color="ink4", bold=True, spc=0.7, lh=1.0)
text(s, M + 1.34, 5.275, 7.9, 0.22, [(MEMBERS, {})], size=10, font=F_BODY,
     color="ink2", lh=1.0)

# ═════════════════════════════════════════════ 2 · SOLUTION
s = new()
header(s, "", "Solution")

rect(s, M, 0.92, 2.86, 0.46, fill="panel", alpha=1.0, line="line", lw=0.9)
text(s, M + 0.16, 1.015, 0.80, 0.20, [("TODAY", {})], size=9, font=F_BODY,
     color="ink4", bold=True, spc=0.8, lh=1.0)
text(s, M + 0.92, 0.995, 1.86, 0.24, [("What gets affected?", {})], size=12,
     font=F_DISP, color="ink3", bold=True, lh=1.0)
put_icon(s, "arrowr", 3.40, 1.00, 0.28, "amber", sw=2.2)
rect(s, 3.80, 0.92, 5.78, 0.46, fill="amber", alpha=0.11, line="amber",
     line_alpha=1.0, lw=1.2)
rect(s, 3.80, 0.92, 0.05, 0.46, fill="amber")
text(s, 3.98, 1.015, 1.00, 0.20, [("DOMINO", {})], size=9, font=F_BODY,
     color="amber", bold=True, spc=0.8, lh=1.0)
text(s, 4.90, 0.995, 4.58, 0.24,
     [("Where can we intervene before the cascade grows?", {})],
     size=12, font=F_DISP, color="ink", bold=True, lh=1.0)

# ---- worked example, four moments
klabel(s, M, 1.50, 6.0, "ONE FAILURE, WALKED THROUGH BY OUR ENGINE")
panels = [
    ("1", "amber", "Bridge B07 fails",
     "89% can still reach a hospital or fire station. On an ordinary damage map nothing looks wrong.",
     "NOTHING VISIBLE YET", "ink3"),
    ("2", "red", "Traffic reroutes",
     "Coastal road N2 is suddenly at 1.3× the traffic it was built for. That is the next domino.",
     "DOMINO FOUND", "red"),
    ("3", "teal", "Four actions tested",
     "Three fail. Reopening a closed crossing holds the chain, and it takes 60 minutes.",
     "CASCADE STOPPED", "teal"),
    ("4", "violet", "Now break B12",
     "Same engine, different answer. Nothing holds it. 17,794 people lose their route to help.",
     "ONLY HARDENING HELPS", "violet"),
]
pw_ = (CW - 3 * 0.13) / 4
for i, (num, col, title, txt, verdict, vcol) in enumerate(panels):
    x = M + i * (pw_ + 0.13)
    sq(s, x, 1.74, pw_, 1.60, alpha=1.0, rule=col, rule_w=0.05)
    rect(s, x + 0.16, 1.86, 0.22, 0.22, fill=col)
    text(s, x + 0.16, 1.885, 0.22, 0.18, [(num, {})], size=9.5, font=F_BODY,
         color="bg", bold=True, align=PP_ALIGN.CENTER, lh=1.0)
    text(s, x + 0.46, 1.865, pw_ - 0.60, 0.24, [(title, {})], size=11.5,
         font=F_DISP, color="ink", bold=True, lh=1.0)
    body(s, x + 0.16, 2.20, pw_ - 0.32, 0.76, txt, size=9.5, col="ink2", lh=1.18)
    chip_(s, x + 0.16, 3.02, pw_ - 0.32, 0.22, verdict, vcol, size=8.5)
    if i < 3:
        put_icon(s, "arrowr", x + pw_ + 0.005, 2.42, 0.12, "ink4", sw=2.6)

# ---- why that road
sq(s, M, 3.42, 5.42, 1.06, alpha=1.0, rule="blue", rule_w=0.05)
ptitle(s, M + 0.22, 3.52, 5.0, "Why that road, and not another", size=12)
comps = [("Overloaded right now", 0.89, "amber"), ("Network runs through it", 0.33, "blue"),
         ("Ambulance routes use it", 0.87, "red"), ("People living behind it", 0.27, "teal")]
cw_ = (5.42 - 0.44 - 3 * 0.10) / 4
for i, (t, v, col) in enumerate(comps):
    x = M + 0.22 + i * (cw_ + 0.10)
    body(s, x, 3.82, cw_, 0.32, t, size=8.5, col="ink3", lh=1.08)
    rect(s, x, 4.16, cw_, 0.10, fill="panel2")
    rect(s, x, 4.16, cw_ * v, 0.10, fill=col)
    text(s, x, 4.28, cw_, 0.16, [("%d%%" % round(v * 100), {})], size=9.5,
         font=F_DISP, color=col, bold=True, lh=1.0)

# ---- dark zone
sq(s, 6.02, 3.42, 3.56, 1.06, fill="violet", alpha=0.08, border="violet",
   border_alpha=0.50, lw=1.2, rule="violet", rule_w=0.05)
ptitle(s, 6.24, 3.52, 3.2, "Dark zones: both, never either", col="violet", size=12)
body(s, 6.24, 3.80, 3.14, 0.40,
     "No road to help AND no phone signal. Malpe goes dark at once, "
     "Kadiyali 25 minutes later.", size=9.5, col="ink2", lh=1.16)
text(s, 6.24, 4.26, 3.14, 0.20,
     [("T dark  =  max ( T phys ,  T comm )", {})], size=11, font=F_DISP,
     color="violet", bold=True, lh=1.0)

# ---- the loop, small
klabel(s, M, 4.56, 6.0, "THE ENGINE BEHIND IT, IN ORDER")
loop = [("Map the city", "line2"), ("Break one asset", "red"), ("Reassign traffic", "amber"),
        ("Score what breaks next", "amber"), ("Test every action", "teal"),
        ("Stop, or repeat", "teal")]
lw_ = (CW - 5 * 0.16) / 6
for i, (t, col) in enumerate(loop):
    x = M + i * (lw_ + 0.16)
    rect(s, x, 4.78, lw_, 0.34, fill="panel", alpha=1.0, line=col, line_alpha=0.6, lw=1.0)
    text(s, x + 0.04, 4.78, lw_ - 0.08, 0.34, [(t, {})], size=9, font=F_BODY,
         color="ink2", bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, lh=1.05)
    if i < 5:
        put_icon(s, "arrowr", x + lw_ + 0.015, 4.88, 0.13, "ink4", sw=2.6)
footer(s, 2, "Everything above is computed, not illustrated.")

# ═════════════════════════════════════════════ 3 · TECHNICAL IMPLEMENTATION
s = new()
header(s, "", "Technical Implementation")

klabel(s, M, 0.92, 6.0, "OUR PROTOTYPE, RUNNING — NOT A MOCK-UP")
pic(s, "assets/demo1.png", M, 1.18, w=5.60)

RX3, RW3 = 6.14, 3.44
klabel(s, RX3, 0.92, RW3, "THE STACK")
stack = [("db", "WorldPop + OpenStreetMap", "data"),
         ("layers", "PostGIS", "spatial store"),
         ("graph", "NetworkX + Dijkstra", "routing and reassignment"),
         ("target", "Domino detector", "four-part score"),
         ("shield", "Intervention engine", "counterfactual re-runs"),
         ("moon", "Dark-zone engine", "isolation and countdowns"),
         ("map", "React map and alerts", "what an operator sees")]
cols3 = ["ink3", "ink3", "amber", "amber", "teal", "violet", "ink3"]
sy = 1.18
for (ic, nm, kind), col in zip(stack, cols3):
    rect(s, RX3, sy, RW3, 0.34, fill="panel", alpha=1.0, line="line", lw=0.8)
    rect(s, RX3, sy, 0.045, 0.34, fill=col)
    put_icon(s, ic, RX3 + 0.14, sy + 0.075, 0.19, col, sw=1.8)
    text(s, RX3 + 0.42, sy + 0.035, 2.0, 0.20, [(nm, {})], size=9.5, font=F_DISP,
         color="ink", bold=True, lh=1.0)
    text(s, RX3 + 0.42, sy + 0.195, RW3 - 0.50, 0.16, [(kind, {})], size=8.5,
         font=F_BODY, color="ink4", lh=1.0)
    sy += 0.40

sq(s, RX3, 4.02, RW3, 1.16, alpha=1.0, rule="teal", rule_w=0.05)
ptitle(s, RX3 + 0.20, 4.12, 3.0, "Real, and honestly scoped", col="teal", size=11.5)
body(s, RX3 + 0.20, 4.38, RW3 - 0.40, 0.74,
     "Real: routing, reassignment, the score, the counterfactuals, 17 failures and 5 "
     "budgets precomputed. Synthetic: the corridor itself. A live OSM extract replaces "
     "one loader function.", size=8.8, col="ink2", lh=1.16)
footer(s, 3, "Open it, click any road, and it recomputes.")

# ═════════════════════════════════════════════ 4 · FEASIBILITY
s = new()
header(s, "", "Feasibility", accent="teal")

# --- evidence 1
sq(s, M, 0.92, 4.46, 2.50, alpha=1.0, rule="teal", rule_w=0.055)
klabel(s, M + 0.24, 1.02, 4.0, "EVIDENCE 1 — REAL POPULATION DATA", col="teal")
ptitle(s, M + 0.24, 1.26, 4.0, "Remove a hospital, then put one action back", size=12.5)
body(s, M + 0.24, 1.54, 3.98, 0.20,
     "570,509 people in the study area, WorldPop plus mapped service locations",
     size=8.5, col="ink3", lh=1.0)
st4 = [("81.1%", "reach a critical\nservice", "ink"),
       ("68.3%", "after the hospital\nis lost", "red"),
       ("83.3%", "after our\nintervention", "teal")]
bw4 = (4.46 - 0.48 - 2 * 0.14) / 3
for i, (big, sub, col) in enumerate(st4):
    x = M + 0.24 + i * (bw4 + 0.14)
    text(s, x, 1.80, bw4, 0.38, [(big, {})], size=22, font=F_DISP,
         color=col, bold=True, spc=-0.6, lh=1.0)
    body(s, x, 2.22, bw4, 0.34, sub.replace("\n", " "), size=8.5, col="ink3", lh=1.10)
    if i < 2:
        put_icon(s, "arrowr", x + bw4 + 0.005, 1.86, 0.13, "ink4", sw=2.6)
rect(s, M + 0.24, 2.62, 3.98, 0.012, fill="line")
body(s, M + 0.24, 2.72, 3.98, 0.56,
     "83.3% is above the 81.1% we started from, so the action that contains the cascade "
     "was worth taking anyway. 47.2% of the newly cut-off population is recovered, "
     "against 26.2% for random placement.", size=9, col="ink2", lh=1.16)

# --- evidence 2
sq(s, 5.12, 0.92, 4.46, 2.50, alpha=1.0, rule="amber", rule_w=0.055)
klabel(s, 5.36, 1.02, 4.0, "EVIDENCE 2 — OUR ENGINE, RUNNING", col="amber")
ptitle(s, 5.36, 1.26, 4.0, "Same budget, two ways to spend it", size=12.5)
bars = [("The standard method", "reinforce the most central roads", 1993, 7.6, "ink4"),
        ("DOMINO", "buy back the most service per rupee", 4092, 8.9, "teal")]
by4 = 1.60
for nm, sub, val, spent, col in bars:
    text(s, 5.36, by4, 2.2, 0.20, [(nm, {})], size=10.5, font=F_DISP, color="ink",
         bold=True, lh=1.0)
    body(s, 5.36, by4 + 0.19, 2.3, 0.18, sub, size=8.5, col="ink4", lh=1.0)
    rect(s, 7.72, by4 + 0.02, 1.40, 0.22, fill="panel2")
    rect(s, 7.72, by4 + 0.02, 1.40 * val / 4092, 0.22, fill=col)
    text(s, 7.72, by4 + 0.26, 1.40, 0.18, [("%s people · ₹%s cr" % ("{:,}".format(val), spent), {})],
         size=8.5, font=F_BODY, color=col, bold=True, lh=1.0)
    by4 += 0.58
rect(s, 5.36, 2.76, 3.98, 0.012, fill="line")
body(s, 5.36, 2.86, 3.98, 0.46,
     "2.05× more people protected, for less money — and DOMINO stops at ₹8.9 crore "
     "because nothing else it could buy wins back another person. Corridor resilience "
     "goes 82.7 → 91.3 out of 100.", size=9, col="ink2", lh=1.16)

# --- bottom strip
c3 = (CW - 0.30) / 3
strips = [
    ("teal", "What ships first",
     "Roads, bridges, services, towers and population on one graph, with the next-domino "
     "detector, the explainable score and the dark-zone clock."),
    ("red", "What we do not claim",
     "Access, not treatment. Topology and capacity, not human behaviour. Modelled "
     "population, not a building-level census. Costs are indicative rates."),
    ("amber", "How we will test it",
     "Replay the Udupi–Manipal road closure of 20 May 2025 and check whether the roads "
     "DOMINO ranks next are the ones traffic actually moved onto."),
]
for i, (col, t, d) in enumerate(strips):
    x = M + i * (c3 + 0.15)
    sq(s, x, 3.54, c3, 1.64, alpha=1.0, rule=col, rule_w=0.05)
    ptitle(s, x + 0.20, 3.66, c3 - 0.36, t, col=col, size=12)
    body(s, x + 0.20, 3.98, c3 - 0.40, 1.10, d, size=9.5, col="ink2", lh=1.20)
footer(s, 4, "Two separate evidence bases, kept apart on purpose.")

# ═════════════════════════════════════════════ 5 · BUSINESS STRATEGY
s = new()
header(s, "", "Business Strategy")

sq(s, M, 0.92, 5.66, 0.86, fill="amber", alpha=0.10, border="amber",
   border_alpha=0.50, lw=1.2, rule="amber", rule_w=0.06)
text(s, M + 0.28, 1.10, 5.20, 0.48,
     [("“We have a fixed budget. Where do we spend it?”", {})],
     size=16, font=F_DISP, color="ink", bold=True, lh=1.0, spc=-0.2)

sq(s, 6.26, 0.92, 3.32, 0.86, alpha=1.0, rule="teal", rule_w=0.055)
klabel(s, 6.48, 1.00, 3.0, "WHAT WE SELL THEM", col="teal")
text(s, 6.48, 1.22, 3.0, 0.24, [("A resilience score, per corridor", {})],
     size=11.5, font=F_DISP, color="ink", bold=True, lh=1.0)
text(s, 6.48, 1.46, 3.0, 0.20,
     [("82.7", {"color": "ink3"}), ("  →  ", {"color": "ink4"}),
      ("91.3", {"color": "teal"}), ("  out of 100", {"color": "ink3", "size": 9})],
     size=13, font=F_DISP, color="ink", bold=True, lh=1.0)

sq(s, M, 1.90, 4.46, 1.52, alpha=1.0)
klabel(s, M + 0.24, 2.00, 4.0, "WHO BUYS IT, AND HOW")
for i, t in enumerate(["Municipal authorities", "District disaster management",
                       "Emergency services", "Infrastructure operators"]):
    x = M + 0.24 + (i % 2) * 2.02
    y = 2.24 + (i // 2) * 0.34
    rect(s, x, y, 1.92, 0.28, fill="panel2", line="line2", lw=0.9)
    text(s, x + 0.06, y, 1.80, 0.28, [(t, {})], size=9, font=F_BODY, color="ink2",
         bold=True, lh=1.0, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
text(s, M + 0.24, 2.98, 4.0, 0.24,
     [("B2G / B2B SaaS, plus deployment and integration", {})],
     size=11.5, font=F_DISP, color="ink", bold=True, lh=1.0)

sq(s, 5.12, 1.90, 4.46, 1.52, alpha=1.0)
klabel(s, 5.36, 2.00, 4.0, "ROADMAP, ONE LAYER AT A TIME")
fut = [("route", "Live traffic", "observed load, not modelled reroute"),
       ("wave", "Tower telemetry", "real coverage state during an event"),
       ("phone", "Peer-to-peer relay", "store-and-forward between nearby devices")]
fy = 2.26
for ic, t, d in fut:
    put_icon(s, ic, 5.36, fy + 0.015, 0.17, "ink3", sw=1.9)
    text(s, 5.62, fy - 0.01, 3.8, 0.20, [(t, {})], size=10.5, font=F_DISP,
         color="ink", bold=True, lh=1.0)
    body(s, 5.62, fy + 0.185, 3.76, 0.20, d, size=9, col="ink3", lh=1.06)
    fy += 0.38

sq(s, M, 3.56, 4.46, 1.10, fill="magenta", alpha=0.11, border="magenta",
   border_alpha=0.55, lw=1.2, rule="magenta", rule_w=0.055)
klabel(s, M + 0.24, 3.66, 4.0, "THE ASK")
body(s, M + 0.24, 3.92, 4.46 - 0.48, 0.66,
     "One corridor, one monsoon season, with the Udupi city municipal council and the "
     "district disaster management authority, replaying last year's closures.",
     size=9.5, col="ink", lh=1.18)

sq(s, 5.12, 3.56, 4.46, 1.10, alpha=1.0, rule="teal", rule_w=0.055)
klabel(s, 5.36, 3.66, 4.0, "WHY THEY KEEP PAYING", col="teal")
body(s, 5.36, 3.92, 4.46 - 0.48, 0.66,
     "The horizon changes every time the city builds something. A resilience score has "
     "to be recomputed each year, which turns a one-off disaster purchase into a line "
     "in the annual capital budget.", size=9.5, col="ink", lh=1.18)

rect(s, M, 4.74, 0.055, 0.42, fill="amber")
text(s, M + 0.24, 4.72, 6.2, 0.46,
     [("Don’t just predict the cascade.", {}), "BR",
      ("Find where it can still be stopped.", {"color": "amber"})],
     size=15, font=F_DISP, color="ink", bold=True, lh=1.12, spc=-0.2)
text(s, SW - M - 2.6, 4.84, 2.6, 0.26, [("DOMINO", {})], size=17, font=F_DISP,
     color="ink", bold=True, spc=1.6, lh=1.0, align=PP_ALIGN.RIGHT)
footer(s, 5, "One corridor, one season, one number a city can act on.")

NOTES = {
1: "Open on the question, not the technology. One bridge goes down, everyone can picture that bridge, almost nobody can picture what happens three steps later. Read the chain on the right out loud, because those are our engine's real numbers, not an illustration. Forty seconds, then move.",
2: "This slide is the whole idea in one worked example. Walk the four panels left to right: the bridge fails and nothing looks wrong, the traffic moves and a road hits 1.3 times capacity, we test four actions and one of them holds in sixty minutes, and then the same engine on a different bridge says nothing holds at all. That last panel is the point. Same tool, two completely different kinds of decision: one you make in ninety minutes, one you make years earlier with capital. Then the score breakdown, so they know it is never a black box, and the dark zone AND.",
3: "Thirty seconds. The stack is deliberately ordinary. What matters is the screenshot: this runs, you can click any road in it and it recomputes. Be first to say the corridor is synthetic and that swapping in real OpenStreetMap geometry replaces one function.",
4: "Two separate evidence bases, and say that out loud so nobody thinks we blurred them. First, real population data: remove a hospital, access falls to 68.3, our action takes it to 83.3, which is above where we started. Second, our engine on the prototype corridor answering the budget question: twice the people protected, for less money, and it tells the city to stop spending at 8.9 crore. Then name our own limits before a judge finds them.",
5: "Lead with the buyer's question. What we actually sell is a number they can put in a report and watch move. Keep the ask small and checkable. Then read the last line and stop.",
}
for i, sl in enumerate(prs.slides, 1):
    if i in NOTES:
        sl.notes_slide.notes_text_frame.text = NOTES[i]

prs.save("DOMINO_M26_Round1.pptx")
print("saved", len(prs.slides._sldIdLst), "slides")
