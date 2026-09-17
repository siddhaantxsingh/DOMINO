"""DOMINO deck — dark ops-console design system."""
import os, hashlib
import cairosvg
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from lxml import etree

EMU_IN = 914400
def I(v): return Emu(int(round(v * EMU_IN)))

SW, SH = 10.0, 5.625          # slide size, inches

# ---------------------------------------------------------------- palette
C = dict(
    bg        = "0A0E13",
    bg2       = "0E141B",
    panel     = "141C25",
    panel2    = "19232E",
    panelHi   = "1E2A37",
    line      = "24313F",
    line2     = "2E3E4F",
    ink       = "EDF2F7",
    ink2      = "9AACBE",
    ink3      = "657787",
    ink4      = "44545F",
    amber     = "FF7A2F",     # cascade
    amberDim  = "7A3B17",
    red       = "F0413B",     # critical / failure
    redDim    = "72211F",
    teal      = "2ED3A7",     # contained / recovered
    tealDim   = "135745",
    violet    = "8B5CF6",     # dark zone
    violetLt  = "C4B5FD",
    violetDim = "3B2A6B",
    magenta   = "EC4899",     # M#26 brand accent
    blue      = "4C8DF6",
    road      = "34455A",
    yellow    = "FFC53D",
)
def rgb(k): return RGBColor.from_string(C.get(k, k))

F_DISP = "Source Serif 4"      # editorial serif, display + titles
F_BODY = "Libre Franklin"      # Franklin Gothic lineage, civic/signage body
F_MONO = "Libre Franklin"      # labels and data readouts

ICON_DIR = "assets/icons"
os.makedirs(ICON_DIR, exist_ok=True)



# ---------------------------------------------------------------- light theme
# Derived from the M#26 sample template's own "Simple Light" colour scheme:
# lt1 FFFFFF · dk1 000000 · dk2 595959 · lt2 EEEEEE
# accent1 4285F4 · accent3 78909C · accent4 FFAB40 · accent5 0097A7
LIGHT = dict(
    bg        = "FFFFFF",
    bg2       = "F7F8FA",
    panel     = "FAFBFC",
    panel2    = "EFF1F3",
    panelHi   = "E3E7EA",
    line      = "DCE1E5",
    line2     = "BCC5CB",
    ink       = "14181B",
    ink2      = "44505A",
    ink3      = "5F6A72",
    ink4      = "97A1A8",
    amber     = "BF5B12",
    red       = "C62828",
    teal      = "00798A",
    violet    = "5E35B1",
    violetLt  = "7E57C2",
    magenta   = "AD1457",
    blue      = "2F6FD0",
    road      = "93A4B0",
    yellow    = "E08C00",
)
def use_light():
    C.update(LIGHT)

# ---------------------------------------------------------------- xml utils
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
def _q(t): return "{%s}%s" % (A, t)
def _sub(parent, tag, **kw):
    e = etree.SubElement(parent, _q(tag))
    for k, v in kw.items(): e.set(k, str(v))
    return e

def no_autofit(shape):
    bp = shape.text_frame._txBody.bodyPr
    for t in ("normAutofit", "spAutoFit"):
        for e in bp.findall(_q(t)): bp.remove(e)

def set_spacing(run, spc_pts):
    """letter spacing in points (can be negative)"""
    run.font._rPr.set("spc", str(int(round(spc_pts * 100))))

def line_spacing(para, mult=None, exact_pt=None, before=0, after=0):
    pPr = para._pPr if para._pPr is not None else para._p.get_or_add_pPr()
    for tag in ("lnSpc", "spcBef", "spcAft"):
        for e in pPr.findall(_q(tag)): pPr.remove(e)
    order = []
    if mult or exact_pt:
        ln = etree.SubElement(pPr, _q("lnSpc"))
        if mult: _sub(ln, "spcPct", val=int(mult * 100000))
        else: _sub(ln, "spcPts", val=int(exact_pt * 100))
        order.append(ln)
    b = etree.SubElement(pPr, _q("spcBef")); _sub(b, "spcPts", val=int(before * 100))
    a = etree.SubElement(pPr, _q("spcAft")); _sub(a, "spcPts", val=int(after * 100))
    # lnSpc must precede spcBef/spcAft
    for e in list(pPr):
        if e.tag == _q("lnSpc"): pPr.remove(e); pPr.insert(0, e)

def set_radius(shape, adj):
    """rounded-rect corner radius as fraction of the short side (0..0.5)"""
    av = shape._element.spPr.find(_q("prstGeom")).find(_q("avLst"))
    for e in list(av): av.remove(e)
    _sub(av, "gd", name="adj", fmla="val %d" % int(adj * 100000))

def set_grad(shape, stops, angle=0):
    """stops: [(pos 0..1, hex, alpha 0..1)]"""
    sp = shape._element.spPr
    for t in ("solidFill", "noFill", "gradFill", "blipFill", "pattFill"):
        for e in sp.findall(_q(t)): sp.remove(e)
    gf = etree.Element(_q("gradFill")); gf.set("rotWithShape", "1")
    gsl = _sub(gf, "gsLst")
    for pos, col, al in stops:
        gs = _sub(gsl, "gs", pos=int(pos * 100000))
        c = _sub(gs, "srgbClr", val=C.get(col, col))
        _sub(c, "alpha", val=int(al * 100000))
    _sub(gf, "lin", ang=int(angle * 60000), scaled="0")
    geom = sp.find(_q("prstGeom"))
    geom.addnext(gf)

def set_alpha_fill(shape, col, alpha):
    sp = shape._element.spPr
    for t in ("solidFill", "noFill", "gradFill"):
        for e in sp.findall(_q(t)): sp.remove(e)
    sf = etree.Element(_q("solidFill"))
    c = _sub(sf, "srgbClr", val=C.get(col, col)); _sub(c, "alpha", val=int(alpha * 100000))
    sp.find(_q("prstGeom")).addnext(sf)

def set_line_alpha(shape, col, alpha, w_pt):
    ln = shape._element.spPr.get_or_add_ln()
    for e in list(ln): ln.remove(e)
    ln.set("w", str(int(w_pt * 12700)))
    sf = _sub(ln, "solidFill")
    c = _sub(sf, "srgbClr", val=C.get(col, col)); _sub(c, "alpha", val=int(alpha * 100000))

def shadow_off(shape):
    sp = shape._element.spPr
    if sp.find(_q("effectLst")) is None:
        el = etree.SubElement(sp, _q("effectLst"))

def add_shadow(shape, blur=14, dist=5, alpha=0.45, col="000000"):
    sp = shape._element.spPr
    for e in sp.findall(_q("effectLst")): sp.remove(e)
    el = etree.SubElement(sp, _q("effectLst"))
    sh = _sub(el, "outerShdw", blurRad=int(blur * 12700), dist=int(dist * 12700),
              dir="5400000", rotWithShape="0")
    c = _sub(sh, "srgbClr", val=col); _sub(c, "alpha", val=int(alpha * 100000))

def set_arrow(shape, head=True, tail=False, w="med", l="med"):
    ln = shape._element.spPr.get_or_add_ln()
    if tail:
        e = _sub(ln, "headEnd", type="triangle", w=w, len=l)
    if head:
        e = _sub(ln, "tailEnd", type="triangle", w=w, len=l)

# ---------------------------------------------------------------- primitives
def rect(slide, x, y, w, h, fill=None, alpha=None, line=None, lw=0.75,
         line_alpha=1.0, radius=None, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, I(x), I(y), I(w), I(h))
    s.shadow.inherit = False
    shadow_off(s)
    if radius is not None: set_radius(s, radius)
    if fill is None:
        s.fill.background()
    elif alpha is not None:
        set_alpha_fill(s, fill, alpha)
    else:
        s.fill.solid(); s.fill.fore_color.rgb = rgb(fill)
    if line is None:
        s.line.fill.background()
    else:
        set_line_alpha(s, line, line_alpha, lw)
    s.text_frame.word_wrap = True
    return s

def rrect(slide, x, y, w, h, radius_in=0.06, **kw):
    r = min(radius_in / min(w, h), 0.49) if min(w, h) > 0 else 0.1
    return rect(slide, x, y, w, h, radius=r, shape=MSO_SHAPE.ROUNDED_RECTANGLE, **kw)

def line(slide, x1, y1, x2, y2, col="line", lw=0.9, alpha=1.0, arrow=False,
         dash=None, aw="med", al="med"):
    from pptx.util import Emu
    c = slide.shapes.add_connector(1, I(x1), I(y1), I(x2), I(y2))
    c.shadow.inherit = False
    ln = c._element.spPr.get_or_add_ln()
    for e in list(ln): ln.remove(e)
    ln.set("w", str(int(lw * 12700)))
    sf = _sub(ln, "solidFill")
    cc = _sub(sf, "srgbClr", val=C.get(col, col)); _sub(cc, "alpha", val=int(alpha * 100000))
    if dash: _sub(ln, "prstDash", val=dash)
    if arrow: _sub(ln, "tailEnd", type="triangle", w=aw, len=al)
    return c

def tri(slide, x, y, w, h, fill="amber", rot=0):
    s = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE, I(x), I(y), I(w), I(h))
    s.shadow.inherit = False; shadow_off(s)
    s.fill.solid(); s.fill.fore_color.rgb = rgb(fill); s.line.fill.background()
    s.rotation = rot
    return s

def text(slide, x, y, w, h, runs, size=11, font=F_BODY, color="ink", bold=False,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spc=0, lh=1.18, caps=False,
         italic=False, wrap=True, margin=0.0):
    tb = slide.shapes.add_textbox(I(x), I(y), I(w), I(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.margin_left = tf.margin_right = I(margin)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    no_autofit(tb)
    if isinstance(runs, str): runs = [(runs, {})]
    paras = []
    cur = []
    for r in runs:
        if r == "BR": paras.append(cur); cur = []
        else: cur.append(r)
    paras.append(cur)
    for pi, pruns in enumerate(paras):
        p = tf.paragraphs[0] if pi == 0 else tf.add_paragraph()
        p.alignment = align
        st = pruns[0][1] if pruns else {}
        line_spacing(p, mult=st.get("lh", lh), before=st.get("before", 0),
                     after=st.get("after", 0))
        for txt, st in pruns:
            run = p.add_run()
            run.text = txt.upper() if st.get("caps", caps) else txt
            f = run.font
            f.size = Pt(st.get("size", size))
            f.name = st.get("font", font)
            f.bold = st.get("bold", bold)
            f.italic = st.get("italic", italic)
            f.color.rgb = rgb(st.get("color", color))
            sp = st.get("spc", spc)
            if sp: set_spacing(run, sp)
    return tb

def label(slide, x, y, w, txt, color="ink3", size=7.5, spc=1.1, align=PP_ALIGN.LEFT,
          bold=True):
    """small mono all-caps kicker"""
    return text(slide, x, y, w, 0.18, [(txt, {})], size=size, font=F_MONO,
                color=color, bold=bold, caps=True, spc=spc, align=align, lh=1.0)

def chip(slide, x, y, w, h, txt, fill="panel2", fill_alpha=None, border="line",
         color="ink2", size=8, font=F_MONO, bold=True, caps=True, spc=0.7,
         radius=0.5, lw=0.75, border_alpha=1.0):
    s = rrect(slide, x, y, w, h, radius_in=h * radius, fill=fill, alpha=fill_alpha,
              line=border, lw=lw, line_alpha=border_alpha)
    text(slide, x, y + h / 2 - 0.10, w, 0.20, [(txt, {})], size=size, font=font,
         color=color, bold=bold, caps=caps, spc=spc, align=PP_ALIGN.CENTER, lh=1.0)
    return s

# ---------------------------------------------------------------- icons
_ICONS = {
 # 24x24 viewBox, stroke icons
 "bridge":  'M2 15h20 M2 15c0-5 4.5-8 10-8s10 3 10 8 M6 15v-3.4 M12 15V8.6 M18 15v-3.4 M4 18.5h16',
 "road":    'M4 21 7 3 M20 21 17 3 M12 4v2.5 M12 10.5v3 M12 17.5v3',
 "hospital":'M4 20V9l8-5 8 5v11 M9.5 13h5 M12 10.5v5 M4 20h16',
 "fire":    'M12 22c3.3 0 6-2.5 6-5.6 0-3.6-3-5.2-3.6-8.9-2 1.3-2.7 3.2-2.7 4.8 0 1.2-.8 1.8-1.6 1.2-.9-.7-1-2.1-1-2.7C7.2 12.4 6 14.2 6 16.4 6 19.5 8.7 22 12 22z',
 "tower":   'M12 10.6a2 2 0 100-4 2 2 0 000 4z M12 10.6V21 M8.3 14.3 12 21l3.7-6.7 M7.4 4.5a8 8 0 000 9.5 M16.6 4.5a8 8 0 010 9.5 M4.6 2a12 12 0 000 14.5 M19.4 2a12 12 0 010 14.5',
 "people":  'M9 11a3.2 3.2 0 100-6.4A3.2 3.2 0 009 11z M2.5 20.5c0-3.6 2.9-5.8 6.5-5.8s6.5 2.2 6.5 5.8 M16.2 5.2a3.2 3.2 0 010 6.2 M17.5 15.2c2.6.5 4 2.4 4 5.3',
 "warn":    'M12 3 1.8 20.5h20.4L12 3z M12 9.6v5 M12 17.6v.1',
 "shield":  'M12 2.5 4 5.6v6c0 5 3.4 8.7 8 9.9 4.6-1.2 8-4.9 8-9.9v-6L12 2.5z M8.7 11.9l2.4 2.5 4.3-4.6',
 "target":  'M12 21a9 9 0 100-18 9 9 0 000 18z M12 16.5a4.5 4.5 0 100-9 4.5 4.5 0 000 9z M12 13.2a1.2 1.2 0 100-2.4 1.2 1.2 0 000 2.4z',
 "graph":   'M6 7.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M18.5 10a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M8 21.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M19 21.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M7.6 6.6l8.6 1.3 M6.6 7.4l.9 9 M9.9 17.6l7.3-8.2 M10.5 19h6',
 "db":      'M12 7.6c4.4 0 8-1.2 8-2.6s-3.6-2.5-8-2.5-8 1.1-8 2.5 3.6 2.6 8 2.6z M4 5v14c0 1.4 3.6 2.6 8 2.6s8-1.2 8-2.6V5 M4 12c0 1.4 3.6 2.6 8 2.6s8-1.2 8-2.6',
 "server":  'M3 4.5h18v5H3v-5z M3 14.5h18v5H3v-5z M6.5 7h.1 M6.5 17h.1 M10 7h5 M10 17h5',
 "map":     'M2.5 6.2 9 3.2v14.6l-6.5 3V6.2z M9 3.2l6 3v14.6l-6-3 M15 6.2l6.5-3v14.6l-6.5 3',
 "bolt":    'M13.5 2 4 13.8h7L10.5 22 20 10.2h-7L13.5 2z',
 "clock":   'M12 21.5a9.5 9.5 0 100-19 9.5 9.5 0 000 19z M12 6.8V12l3.5 2.2',
 "city":    'M3 21h18 M5 21V8l6-4 6 4v13 M9.5 12h1 M13.5 12h1 M9.5 16h1 M13.5 16h1',
 "ambu":    'M2.5 7.5h11v9h-11v-9z M13.5 10.5h3.6l2.9 3v3h-6.5v-6z M6.5 20a2 2 0 100-4 2 2 0 000 4z M17 20a2 2 0 100-4 2 2 0 000 4z M6.3 12h3.4 M8 10.3v3.4',
 "moon":    'M20.5 14.3A8.7 8.7 0 019.7 3.5a8.8 8.8 0 1010.8 10.8z',
 "wave":    'M12 14.5a1.6 1.6 0 100-3.2 1.6 1.6 0 000 3.2z M8.6 16.4a4.8 4.8 0 010-6.8 M15.4 9.6a4.8 4.8 0 010 6.8 M5.8 19.2a8.8 8.8 0 010-12.4 M18.2 6.8a8.8 8.8 0 010 12.4',
 "search":  'M11 19a8 8 0 100-16 8 8 0 000 16z M21 21l-4.4-4.4',
 "layers":  'M12 2.5 2.5 7.4 12 12.3l9.5-4.9L12 2.5z M2.5 16.6 12 21.5l9.5-4.9 M2.5 12 12 16.9l9.5-4.9',
 "lock":    'M6 10.5h12v10H6v-10z M8.6 10.5V7.3a3.4 3.4 0 016.8 0v3.2',
 "stop":    'M12 21.5a9.5 9.5 0 100-19 9.5 9.5 0 000 19z M8 12h8',
 "play":    'M7 4.5 19 12 7 19.5v-15z',
 "route":   'M6 20.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M18 8.5a2.5 2.5 0 100-5 2.5 2.5 0 000 5z M18 8.5c0 4.5-12 4-12 9',
 "phone":   'M7 2.5h10v19H7v-19z M10.5 19h3',
 "build":   'M14.5 6.5a3.5 3.5 0 004.7 3.3l-8 8A3.5 3.5 0 006 13.2l8-8a3.5 3.5 0 00.5 1.3z',
 "chart":   'M4 20V10 M10 20V4 M16 20v-7 M22 20H2',
 "grid":    'M3 3h7v7H3V3z M14 3h7v7h-7V3z M3 14h7v7H3v-7z M14 14h7v7h-7v-7z',
 "flag":    'M5 21V3.5h13l-2.6 4.4L18 12.3H5',
 "cross":   'M12 4v16 M4 12h16',
 "check":   'M4.5 12.8 9.6 18 19.5 6.5',
 "arrowr":  'M4 12h15 M13.5 6.5 20 12l-6.5 5.5',
 "arrowd":  'M12 4v15 M6.5 13.5 12 20l5.5-6.5',
 "sat":     'M12 21a9 9 0 01-9-9 M12 17.5A5.5 5.5 0 006.5 12 M12 3a9 9 0 019 9 M17.5 12A5.5 5.5 0 0012 6.5 M12 13.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z',
}

def icon(name, color, px=96, sw=1.8, fill=None):
    key = hashlib.md5(f"{name}{color}{px}{sw}{fill}".encode()).hexdigest()[:12]
    path = f"{ICON_DIR}/{name}_{key}.png"
    if not os.path.exists(path):
        d = _ICONS[name]
        col = "#" + C.get(color, color)
        fl = "none" if not fill else "#" + C.get(fill, fill)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
               f'width="24" height="24"><path d="{d}" fill="{fl}" stroke="{col}" '
               f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
        cairosvg.svg2png(bytestring=svg.encode(), write_to=path,
                         output_width=px, output_height=px)
    return path

def put_icon(slide, name, x, y, size, color, sw=1.8, fill=None):
    p = icon(name, color, px=int(size * 400), sw=sw, fill=fill)
    return slide.shapes.add_picture(p, I(x), I(y), I(size), I(size))

def svg_png(svg, path, w_px, h_px):
    if not os.path.exists(path):
        cairosvg.svg2png(bytestring=svg.encode(), write_to=path,
                         output_width=w_px, output_height=h_px)
    return path

def panel(slide, x, y, w, h, fill="panel", alpha=0.55, border="line", lw=0.75,
          rule=None, rule_w=0.055, border_alpha=1.0):
    """flat, square-cornered panel with an optional heavy left rule"""
    p = rect(slide, x, y, w, h, fill=fill, alpha=alpha, line=border, lw=lw,
             line_alpha=border_alpha)
    if rule:
        rect(slide, x, y, rule_w, h, fill=rule)
    return p

def kicker(slide, x, y, w, txt, color="ink3", size=10):
    return text(slide, x, y, w, 0.22, [(txt, {})], size=size, font=F_BODY,
                color=color, bold=True, caps=True, spc=0.9, lh=1.0)

# ---------------------------------------------------------------- chrome
LOGO = "logo_m26.png"
LOGO_X, LOGO_Y, LOGO_W = 8195825 / EMU_IN, 86900 / EMU_IN, 832675 / EMU_IN
LOGO_H = LOGO_W * (774 / 1042)

M = 0.42                     # side margin
HEADER_H = 0.80
CTOP = 1.02
CBOT = 5.22
CW = SW - 2 * M

def canvas(slide, col="bg"):
    rect(slide, 0, 0, SW, SH, fill=col)

def logo(slide, x=None, y=None, w=None):
    w = w or LOGO_W
    h = w * (774 / 1042)
    return slide.shapes.add_picture(LOGO, I(x if x is not None else LOGO_X),
                                    I(y if y is not None else LOGO_Y), I(w), I(h))

def header(slide, _unused, title, accent="amber"):
    """top band: brand at left, slide title, official logo at right"""
    rect(slide, 0, 0, SW, HEADER_H, fill="bg2")
    rect(slide, 0, HEADER_H, SW, 0.014, fill="line")
    rect(slide, 0, HEADER_H, 1.62, 0.014, fill=accent)
    rect(slide, M, 0.245, 0.06, 0.315, fill=accent)
    text(slide, M + 0.18, 0.225, 2.3, 0.28, [("DOMINO", {})], size=17, font=F_DISP,
         color="ink", bold=True, spc=1.2, lh=1.0)
    rect(slide, 2.35, 0.20, 0.008, 0.40, fill="line2")
    text(slide, 2.60, 0.235, 6.25, 0.34, [(title, {})], size=19, font=F_DISP,
         color="ink", bold=True, spc=-0.2, lh=1.0)
    logo(slide, x=LOGO_X + 0.06, y=0.10, w=0.70)

def footer(slide, n, note=""):
    y = 5.31
    rect(slide, 0, y, SW, 0.012, fill="line")
    text(slide, M, y + 0.065, 3.6, 0.20, [("M#26  ·  P05  ·  TEAM MOSSAD.EXE", {})],
         size=9, font=F_BODY, color="ink4", bold=True, spc=0.5, lh=1.0)
    if note:
        text(slide, SW - M - 5.55, y + 0.065, 5.22, 0.20, [(note, {})], size=9,
             font=F_BODY, color="ink4", spc=0.2, lh=1.0, align=PP_ALIGN.RIGHT)
    text(slide, SW - M - 0.32, y + 0.055, 0.32, 0.22, [("%02d" % n, {})], size=11,
         font=F_DISP, color="ink3", bold=True, align=PP_ALIGN.RIGHT, lh=1.0)
