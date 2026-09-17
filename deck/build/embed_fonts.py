"""Embed the deck's typefaces into the .pptx (same mechanism the M#26 template uses)."""
import zipfile, shutil, re, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "DOMINO_M26_Round1.pptx"
TMP = SRC + ".tmp"

FAMILIES = [
    ("Source Serif 4", {"regular": "fonts/ttf/SourceSerif4-Regular.ttf",
                        "bold":    "fonts/ttf/SourceSerif4-Bold.ttf"}),
    ("Libre Franklin", {"regular": "fonts/ttf/LibreFranklin-Regular.ttf",
                        "bold":    "fonts/ttf/LibreFranklin-Bold.ttf"}),
]

zin = zipfile.ZipFile(SRC)
items = {n: zin.read(n) for n in zin.namelist()}
zin.close()

rels = items["ppt/_rels/presentation.xml.rels"].decode()
pres = items["ppt/presentation.xml"].decode()
ct = items["[Content_Types].xml"].decode()

used = set(int(m) for m in re.findall(r'Id="rId(\d+)"', rels))
nxt = max(used) + 1 if used else 1

font_xml = []
new_rels = []
for fam, faces in FAMILIES:
    parts = []
    for face, src in faces.items():
        name = "fonts/%s-%s.fntdata" % (fam.replace(" ", ""), face)
        items["ppt/" + name] = open(src, "rb").read()
        rid = "rId%d" % nxt; nxt += 1
        new_rels.append('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/'
                        'officeDocument/2006/relationships/font" Target="%s"/>' % (rid, name))
        parts.append('<p:%s r:id="%s"/>' % (face, rid))
    font_xml.append('<p:embeddedFont><p:font typeface="%s"/>%s</p:embeddedFont>'
                    % (fam, "".join(parts)))

rels = rels.replace("</Relationships>", "".join(new_rels) + "</Relationships>")

# embeddedFontLst goes after sldSz/notesSz, before defaultTextStyle / extLst
block = "<p:embeddedFontLst>%s</p:embeddedFontLst>" % "".join(font_xml)
assert "<p:embeddedFontLst>" not in pres
if "<p:defaultTextStyle>" in pres:
    pres = pres.replace("<p:defaultTextStyle>", block + "<p:defaultTextStyle>", 1)
else:
    pres = pres.replace("</p:presentation>", block + "</p:presentation>", 1)
if "embedTrueTypeFonts" not in pres:
    pres = re.sub(r"(<p:presentation\b[^>]*?)(\s*>)", r'\1 embedTrueTypeFonts="1"\2', pres, count=1)

if 'Extension="fntdata"' not in ct:
    ct = ct.replace("<Types ", '<Types ', 1)
    ct = re.sub(r"(<Types[^>]*>)",
                r'\1<Default ContentType="application/x-fontdata" Extension="fntdata"/>',
                ct, count=1)

items["ppt/_rels/presentation.xml.rels"] = rels.encode()
items["ppt/presentation.xml"] = pres.encode()
items["[Content_Types].xml"] = ct.encode()

with zipfile.ZipFile(TMP, "w", zipfile.ZIP_DEFLATED) as z:
    for n, d in items.items():
        z.writestr(n, d)
shutil.move(TMP, SRC)
print("embedded %d families into %s (%.1f MB)"
      % (len(FAMILIES), SRC, os.path.getsize(SRC) / 1e6))
