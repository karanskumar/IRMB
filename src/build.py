#!/usr/bin/env python3
"""Inline the brand assets into src-template.html and write index.html.

Usage:  cd src && python3 build.py
Requires: pillow  (pip install pillow)
"""
import base64
import io
import json
import os
from PIL import Image

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

html = open(TEMPLATE).read()
html = html.replace("{{LOGO_WHITE}}", assets["logo_white"])
html = html.replace("{{LOGO}}", assets["logo"])
html = html.replace('src="{{PROFIT}}"', 'data-img="profit"')

ANCHOR = """    document.getElementById('navMenu').classList.toggle('open');
  });"""
html = html.replace(
    ANCHOR,
    ANCHOR
    + '\n  var P="'
    + profit
    + '";\n  document.querySelectorAll(\'[data-img="profit"]\').forEach(function(el){el.src=P});',
)

assert "{{" not in html, "unreplaced placeholder remains"
assert "var P=" in html, "mascot injection failed"

open(OUTPUT, "w").write(html)
print("wrote %s (%d KB)" % (OUTPUT, len(html) // 1024))
