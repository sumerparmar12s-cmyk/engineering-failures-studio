"""Render an NTSB report page with a highlighted phrase, cropped 16:9 around it. usage: docpage.py page "phrase" out.png"""
import sys, subprocess, re, html
from PIL import Image, ImageDraw
pg, phrase, out = int(sys.argv[1]), sys.argv[2], sys.argv[3]
DPI = 220; sc = DPI / 72
subprocess.run(['pdftoppm', '-f', str(pg), '-l', str(pg), '-r', str(DPI), '-png', '-singlefile', 'docs/final.pdf', '/tmp/_pg'], check=True)
bb = subprocess.run(['pdftotext', '-f', str(pg), '-l', str(pg), '-bbox', 'docs/final.pdf', '-'], capture_output=True, text=True).stdout
words = [(float(a), float(b), float(c), float(d), html.unescape(w)) for a, b, c, d, w in re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', bb)]
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
target = [norm(x) for x in phrase.split()]
toks = [norm(w[4]) for w in words]
for i in range(len(toks)):
    if toks[i:i + len(target)] == target: hit = words[i:i + len(target)]; break
else: raise SystemExit('phrase not found')
im = Image.open('/tmp/_pg.png').convert('RGB'); ov = Image.new('RGB', im.size, (255, 255, 255)); d = ImageDraw.Draw(ov)
lines = {}
for x0, y0, x1, y1, _ in hit: lines.setdefault(round(y0), []).append((x0, y0, x1, y1))
for ws in lines.values():
    d.rectangle([min(w[0] for w in ws) * sc - 6, min(w[1] for w in ws) * sc - 4, max(w[2] for w in ws) * sc + 6, max(w[3] for w in ws) * sc + 5], fill=(255, 226, 60))
from PIL import ImageChops
im = ImageChops.multiply(im, ov)
cy = (min(h[1] for h in hit) + max(h[3] for h in hit)) / 2 * sc
W = im.width - int(0.9 * 72 * sc * 2) ; x0 = int(0.9 * 72 * sc); H = int(W * 9 / 16)
y0 = int(max(0, min(im.height - H, cy - H / 2)))
im.crop((x0, y0, x0 + W, y0 + H)).save(out); print(out, im.size, (x0, y0, W, H))
