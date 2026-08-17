#!/usr/bin/env python3
"""Inline the brand assets into src-template.html and write index.html.

Usage:  cd src && python3 build.py
Requires: pillow  (pip install pillow)
"""
import base64
import io
import json
import os
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TEMPLATE = os.path.join(ROOT, "src-template.html")
OUTPUT = os.path.join(ROOT, "index.html")

assets = json.load(open(os.path.join(HERE, "assets.json")))

# Re-encode the mascot small + quantised. It appears in 5 places, so it is
# injected once via JS rather than repeated as 5 data URLs (saves ~800KB).
raw = base64.b64decode(assets["profit"].split(",")[1])
mascot = Image.open(io.BytesIO(raw)).convert("RGBA")
mascot.thumbnail((360, 360), Image.LANCZOS)
alpha = mascot.getchannel("A")
mascot = mascot.convert("RGB").quantize(colors=200).convert("RGBA")
mascot.putalpha(alpha)
buf = io.BytesIO()
mascot.save(buf, "PNG", optimize=True)
profit = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def inline(filename, height, fmt="PNG"):
    """Load an asset, scale it to `height` px and return it as a data URL."""
    im = Image.open(os.path.join(HERE, "assets", filename))
    im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
    buf = io.BytesIO()
    if fmt == "JPEG":
        if im.mode == "RGBA":
            # Both association marks render on a white chip, so flattening the
            # alpha onto white is lossless in context and far smaller than PNG.
            flat = Image.new("RGB", im.size, "white")
            flat.paste(im, mask=im.getchannel("A"))
            im = flat
        im.convert("RGB").save(buf, "JPEG", quality=86, optimize=True)
    else:
        im.save(buf, "PNG", optimize=True)
    return "data:image/%s;base64,%s" % (
        fmt.lower(),
        base64.b64encode(buf.getvalue()).decode(),
    )


# Lift a light plate to pure white, leaving the artwork itself alone, so each
# platform logo sits invisibly on its chip. CollaborateMD ships on #DFDFDF; the
# rest are already white. Ramping rather than thresholding avoids edge halos.
WHITE_POINT = [
    v if v <= 190 else 255 if v >= 223 else round(190 + (v - 190) * 65 / 33)
    for v in range(256)
] * 3


def platform(filename, display_height):
    """Normalise a platform logo's plate to white, trim it, and inline it."""
    im = Image.open(os.path.join(HERE, "assets", filename)).convert("RGBA")
    art = Image.new("RGB", im.size, "white")
    art.paste(im, mask=im.getchannel("A"))
    art = art.point(WHITE_POINT)

    # Crop the uniform border so logos are sized by their artwork, not padding.
    ref = Image.new("RGB", art.size, art.getpixel((0, 0)))
    box = (
        ImageChops.difference(art, ref)
        .convert("L")
        .point(lambda p: 255 if p > 18 else 0)
        .getbbox()
    )
    if box:
        art = art.crop(box)

    h = display_height * 2  # encode at 2x for retina
    art = art.resize((round(art.width * h / art.height), h), Image.LANCZOS)
    buf = io.BytesIO()
    art.quantize(colors=256).save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


# Images used more than once are injected via JS instead of being repeated as
# data URLs. The mascot appears 5 times; each association mark twice; each
# platform logo twice, because the marquee duplicates its track to loop.
# Platform heights are normalised by area, not by height — a blocky mark and a
# long wordmark need different heights to carry the same visual weight.
REPEATED = {
    "profit": profit,
    "mmba": inline("MMBA_logo.png", 96, "JPEG"),
    "amba": inline("AMBA_logo.jpg", 96, "JPEG"),
    "therapynotes": platform("TherapyNotes.png", 28),
    "collaboratemd": platform("CollaborateMD.png", 30),
    "nextgen": platform("Nextgen.jpg", 38),
    "greenway": platform("Greenway.jpg", 32),
    "tebra": platform("tebra.png", 30),
}

html = open(TEMPLATE).read()
html = html.replace("{{LOGO_WHITE}}", assets["logo_white"])
html = html.replace("{{LOGO}}", assets["logo"])
for key in REPEATED:
    html = html.replace('src="{{%s}}"' % key.upper(), 'data-img="%s"' % key)

ANCHOR = """    document.getElementById('navMenu').classList.toggle('open');
  });"""
inject = "".join(
    '\n  document.querySelectorAll(\'[data-img="%s"]\')'
    '.forEach(function(el){el.src="%s"});' % (key, url)
    for key, url in REPEATED.items()
)
html = html.replace(ANCHOR, ANCHOR + inject)

assert "{{" not in html, "unreplaced placeholder remains"
for key in REPEATED:
    assert 'data-img="%s"' % key in html, "%s injection failed" % key

open(OUTPUT, "w").write(html)
print("wrote %s (%d KB)" % (OUTPUT, len(html) // 1024))
