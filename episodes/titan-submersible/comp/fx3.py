"""Deepwater Horizon look: cinematic letterbox, running story clock + countdown, live pressure chart, animated well
cross-section, Swiss-cheese model, big time-stamp chapter cards, leader-line callouts, tribute names."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import EXTRA, font, eout, ease, clamp, lerp, W, H

TEAL, ORANGE, WHITE, GREY = (64, 214, 214), (255, 140, 40), (255, 255, 255), (170, 178, 186)
BAR = 0                                        # no letterbox: always full-frame 16:9 (creator rule)

# ---------------- story clock (post hook) ----------------
def clock_post(CLOCK, show):
    """CLOCK: list of (vo_t, 'HH:MM', minutes_of_day). show: (t0,t1) range where the HUD is visible."""
    def post(img, t, fi, sh):
        d = ImageDraw.Draw(img)
        if BAR:
            d.rectangle([0, 0, W, BAR], fill=(0, 0, 0)); d.rectangle([0, H - BAR, W, H], fill=(0, 0, 0))
        if not (show[0] <= t <= show[1]) or sh.k.get('nohud'): return img
        cur = None
        for c in CLOCK:
            if t >= c[0]: cur = c
        if not cur: return img
        p = eout((t - cur[0]) / 0.35)
        boom = 21 * 60 + 49; left = boom - cur[2]
        f1, f2 = font('monob', 40), font('mono', 30)
        x, y = 70, BAR + 26 if BAR else 70
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rectangle([x - 18, y - 12, x + 560, y + 92], fill=(0, 0, 0, 150))
        ld.rectangle([x - 18, y - 12, x - 12, y + 92], fill=ORANGE + (255,))
        ld.text((x, y + (1 - p) * -20), f'APR 20, 2010  ·  {cur[1]}', font=f1, fill=WHITE + (int(255 * p),))
        if left > 0:
            txt = f'T-MINUS {left // 60:02d}:{left % 60:02d} TO EXPLOSION'
            col = ORANGE if left > 60 else (255, 70, 50)
        else:
            txt = 'EXPLOSION · 9:49 P.M.' if left == 0 else f'+{-left // 60:02d}:{-left % 60:02d} AFTER EXPLOSION'
            col = (255, 70, 50)
        blink = 1 if left > 15 or (fi // 10) % 2 == 0 else 0.35
        ld.text((x, y + 50), txt, font=f2, fill=col + (int(255 * p * blink),))
        img = img.convert('RGBA'); img.alpha_composite(lay); return img.convert('RGB')
    return post

# ---------------- live chart ----------------
def _chart(d, lay, o, t, a, A, fi):
    x0, y0, w, h = o['box']; prog = clamp((t - o['at']) / o['dur'])
    d.rectangle([x0 - 30, y0 - 70, x0 + w + 30, y0 + h + 60], fill=(6, 10, 14, int(200 * a)))
    d.text((x0, y0 - 56), o['title'], font=font('oswald', 34), fill=WHITE + (A,))
    for i in range(5):
        yy = y0 + h * i / 4; d.line([(x0, yy), (x0 + w, yy)], fill=(255, 255, 255, int(40 * a)), width=1)
        d.text((x0 - 12, yy), f"{int(o['vmax'] * (1 - i / 4)):,}", font=font('mono', 20), fill=GREY + (A,), anchor='rm')
    for s in o['series']:
        pts = s['pts']; n = max(2, int(len(pts) * prog))
        xy = [(x0 + w * px, y0 + h * (1 - py / o['vmax'])) for px, py in pts[:n]]
        if len(xy) > 1: d.line(xy, fill=s['color'] + (A,), width=6, joint='curve')
        if xy:
            ex, ey = xy[-1]; d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=s['color'] + (A,))
            if prog > s.get('labat', 0.95): d.text((ex + 16, ey - 16), s['label'], font=font('monob', 30), fill=s['color'] + (A,))
    for (fx, txt, tt) in o.get('marks', []):
        if t >= tt:
            xx = x0 + w * fx; d.line([(xx, y0), (xx, y0 + h)], fill=(255, 255, 255, int(120 * a)), width=2)
            d.text((xx + 8, y0 + h + 14), txt, font=font('mono', 22), fill=WHITE + (A,))
    if o.get('note'): d.text((x0 + w, y0 + h + 14), o['note'], font=font('mono', 18), fill=GREY + (int(A * 0.8),), anchor='ra')
EXTRA['chart'] = _chart

# ---------------- well cross-section ----------------
def _well(d, lay, o, t, a, A, fi):
    """Full-frame diagram. keys: disp=(t0,t1) seawater replacing mud from the top; gas=(t0,t1) gas rising from the bottom;
    labels=[(text, x, y, at, color)]; cement_fail=at."""
    cx = W // 2 + (180 if W > H else 0); top = int(H * 0.16); sea = int(H * 0.36); bed = int(H * 0.52); bot = int(H * 0.93)
    for yy in range(top, bed):                                   # sea gradient
        k = (yy - top) / (bed - top); c = (int(lerp(20, 4, k)), int(lerp(70, 18, k)), int(lerp(110, 40, k)))
        d.line([(0, yy), (W, yy)], fill=c + (A,))
    d.rectangle([0, bed, W, H], fill=(58, 44, 32, A))              # rock
    for i in range(14):
        yy = bed + (bot - bed) * i / 14; d.line([(0, yy), (W, yy + 6)], fill=(70, 54, 40, A), width=2)
    d.polygon([(cx - 150, top - 30), (cx + 150, top - 30), (cx + 120, top + 10), (cx - 120, top + 10)], fill=(200, 205, 210, A))  # rig hull
    d.rectangle([cx - 8, top - 140, cx + 8, top - 30], fill=(200, 205, 210, A))   # derrick
    d.line([(cx - 60, top - 30), (cx, top - 140), (cx + 60, top - 30)], fill=(200, 205, 210, A), width=4)
    d.rectangle([cx - 10, top + 10, cx + 10, bed - 40], fill=(150, 156, 162, A))  # riser
    d.rectangle([cx - 34, bed - 60, cx + 34, bed], fill=(255, 200, 0, A))         # BOP
    pw = 26; d.rectangle([cx - pw, bed, cx + pw, bot], fill=(40, 40, 44, A))      # casing
    d.rectangle([cx - pw - 18, bot - 70, cx + pw + 18, bot], fill=(150, 150, 150, A))   # cement plug zone
    # fluid column: mud (brown) replaced by seawater (blue) from the top
    dp = ease(clamp((t - o['disp'][0]) / (o['disp'][1] - o['disp'][0]))) if o.get('disp') else 0
    col_top, col_bot = top + 10, bot - 70; split = col_top + (col_bot - col_top) * dp * 0.75
    d.rectangle([cx - 8, col_top, cx + 8, split], fill=(60, 140, 230, A)); d.rectangle([cx - 8, split, cx + 8, col_bot], fill=(120, 80, 45, A))
    if o.get('cement_fail') and t >= o['cement_fail']:
        for i in range(6):
            yy = bot - 70 + 10 * i; d.line([(cx - pw - 18, yy), (cx + pw + 18, yy + 8)], fill=(255, 60, 40, A), width=3)
    if o.get('gas'):
        g = clamp((t - o['gas'][0]) / (o['gas'][1] - o['gas'][0]))
        if g > 0:
            rng = np.random.default_rng(3); n = 40
            for i in range(n):
                ph = (rng.random() + t * (0.25 + 0.35 * rng.random())) % 1
                yy = bot - (bot - top) * g * ph; xx = cx + (rng.random() - 0.5) * 14 + math.sin(t * 3 + i) * 3
                r = 4 + 3 * rng.random(); d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 210, 80, A))
    for (txt, x, y, at, col) in o.get('labels', []):
        if t >= at:
            p = eout((t - at) / 0.3); ff = font('oswald', 38)
            d.line([(x, y + 20), (cx + (30 if x > cx else -30), y + 20)], fill=col + (int(A * p),), width=2)
            if x > cx: x = min(x, W - 40 - ff.getlength(txt))
            else: x = max(x, 40 + ff.getlength(txt))
            d.text((x, y), txt, font=ff, fill=col + (int(A * p),), anchor='ra' if x < cx else 'la')
EXTRA['well'] = _well

# ---------------- Swiss cheese ----------------
def _cheese(d, lay, o, t, a, A, fi):
    names = o['names']; n = len(names); gap = (W - 400) / (n - 1) if n > 1 else 0
    al = clamp((t - o['align']) / 1.2) if o.get('align') else 0
    for i, nm in enumerate(names):
        p = eout((t - o['at'] - i * 0.35) / 0.4)
        if p <= 0: continue
        x = 200 + i * gap; y0, y1 = H * 0.3, H * 0.72
        d.polygon([(x - 60, y0 + 20), (x + 60, y0 - 20), (x + 60, y1 - 20), (x - 60, y1 + 20)], fill=(250, 200, 70, int(235 * p * a)), outline=(160, 110, 20, A))
        hy = lerp(H * (0.38 + 0.28 * ((i * 37) % 10) / 10), H * 0.5, ease(al))
        d.ellipse([x - 26, hy - 34, x + 26, hy + 34], fill=(20, 16, 10, int(255 * p * a)))
        ff = font('oswald', 30)
        for j, line in enumerate(nm.split('\n')):
            d.text((x, y1 + 40 + 36 * j), line, font=ff, fill=WHITE + (int(A * p),), anchor='ma')
    if o.get('arrow') and t >= o['arrow']:
        p = eout((t - o['arrow']) / 1.0); xe = lerp(80, W - 80, p)
        d.line([(80, H * 0.5), (xe, H * 0.5)], fill=(255, 70, 50, A), width=10)
        d.polygon([(xe + 30, H * 0.5), (xe - 10, H * 0.5 - 24), (xe - 10, H * 0.5 + 24)], fill=(255, 70, 50, A))
        if p > 0.95: d.text((W - 90, H * 0.5 - 70), 'BLOWOUT', font=font('bebas', 80), fill=(255, 70, 50, A), anchor='rs')
EXTRA['cheese'] = _cheese

# ---------------- big time stamp chapter card ----------------
def _bigtime(d, lay, o, t, a, A, fi):
    p = eout((t - o['at']) / 0.45); fs = 300 if W > H else 220; f = font('Thin', fs)
    while f.getlength(o['time']) > W * 0.84 and fs > 90: fs -= 12; f = font('Thin', fs)
    x = int(W * 0.08) if W > H else W // 2; anc = 'ls' if W > H else 'ms'; y = int(H * 0.62)
    d.text((x + int((1 - p) * 120), y), o['time'], font=f, fill=WHITE + (A,), anchor=anc)
    if o.get('sub'):
        sp = eout((t - o['at'] - 0.35) / 0.5)
        d.text((x + (8 if W > H else 0), y + 30), o['sub'].upper(), font=font('oswald', 46), fill=ORANGE + (int(A * sp),), anchor='la' if W > H else 'ma')
EXTRA['bigtime'] = _bigtime

# ---------------- leader-line callout ----------------
def _callout(d, lay, o, t, a, A, fi):
    p = eout((t - o['at']) / 0.45); (px, py), (lx, ly) = o['pt'], o['lab']
    d.ellipse([px - 10, py - 10, px + 10, py + 10], outline=o.get('color', TEAL) + (A,), width=4)
    r = 10 + 30 * ((t - o['at']) % 1.2) / 1.2; d.ellipse([px - r, py - r, px + r, py + r], outline=o.get('color', TEAL) + (int(A * (1 - (r - 10) / 30)),), width=2)
    mx, my = lerp(px, lx, p), lerp(py, ly, p); d.line([(px, py), (mx, my)], fill=WHITE + (A,), width=3)
    if p > 0.9:
        ff = font('oswald', o.get('size', 44)); anc = 'ls' if lx >= px else 'rs'
        d.line([(lx, ly), (lx + (1 if lx >= px else -1) * (ff.getlength(o['text']) + 10), ly)], fill=WHITE + (A,), width=3)
        d.text((lx + (6 if lx >= px else -6), ly - 8), o['text'], font=ff, fill=o.get('color', TEAL) + (A,), anchor=anc)
        if o.get('sub'): d.text((lx + (6 if lx >= px else -6), ly + 8), o['sub'], font=font('Medium', 28), fill=WHITE + (A,), anchor='la' if lx >= px else 'ra')
EXTRA['callout'] = _callout

# ---------------- tribute names ----------------
def _names(d, lay, o, t, a, A, fi):
    names = o['names']; cols = 2 if W > H else 1; per = math.ceil(len(names) / cols)
    f = font('play', 54 if W > H else 46)
    for i, nm in enumerate(names):
        tt = o['at'] + i * o['step']; p = eout((t - tt) / 0.6)
        if p <= 0: continue
        c, r = divmod(i, per); x = (W * (0.3 + 0.4 * c)) if cols == 2 else W / 2; y = H * 0.2 + r * (H * 0.62 / per)
        d.text((x, y + (1 - p) * 14), nm, font=f, fill=WHITE + (int(A * p),), anchor='ma')
EXTRA['names'] = _names

# ---------------- data line (big number + unit, minimal) ----------------
def _stat(d, lay, o, t, a, A, fi):
    p = eout((t - o['at']) / 0.5); v = o['v0'] + (o['v1'] - o['v0']) * eout((t - o['at']) / o.get('dur', 1.0))
    f = font('Light', o.get('size', 220)); txt = o.get('fmt', '{:,.0f}').format(v)
    x, y = o.get('x', W // 2), o.get('y', H // 2)
    d.text((x, y), txt, font=f, fill=WHITE + (A,), anchor='mm')
    if o.get('unit'): d.text((x, y + o.get('size', 220) * 0.55), o['unit'].upper(), font=font('oswald', 44), fill=ORANGE + (int(A * p),), anchor='mt')
EXTRA['stat'] = _stat

# ---------------- sealed bottle + gauge analogy ----------------
def _bottle(d, lay, o, t, a, A, fi):
    kf = o['vals']; v = kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t0 <= t <= t1: v = lerp(v0, v1, ease((t - t0) / max(0.01, t1 - t0)))
        elif t > t1: v = v1
    bx, by = int(W * 0.3), int(H * 0.52)
    d.rounded_rectangle([bx - 110, by - 160, bx + 110, by + 230], 40, outline=WHITE + (A,), width=6)
    d.rectangle([bx - 40, by - 230, bx + 40, by - 160], outline=WHITE + (A,), width=6)
    d.rectangle([bx - 52, by - 250, bx + 52, by - 226], fill=ORANGE + (A,))           # the cap = the seal
    d.text((bx, by + 270), o.get('blabel', 'SEALED'), font=font('oswald', 40), fill=WHITE + (A,), anchor='ma')
    gx, gy, r = int(W * 0.68), int(H * 0.5), 200
    d.ellipse([gx - r, gy - r, gx + r, gy + r], outline=WHITE + (A,), width=6)
    for i in range(11):
        an = math.radians(225 - 270 * i / 10); d.line([(gx + (r - 26) * math.cos(an), gy - (r - 26) * math.sin(an)), (gx + r * math.cos(an), gy - r * math.sin(an))], fill=WHITE + (A,), width=4)
    an = math.radians(225 - 270 * clamp(v / o.get('vmax', 100)))
    col = (255, 70, 50) if v > o.get('warn', 20) else TEAL
    d.line([(gx, gy), (gx + (r - 40) * math.cos(an), gy - (r - 40) * math.sin(an))], fill=col + (A,), width=10)
    d.ellipse([gx - 16, gy - 16, gx + 16, gy + 16], fill=WHITE + (A,))
    d.text((gx, gy + r + 30), o.get('glabel', 'PRESSURE'), font=font('oswald', 40), fill=WHITE + (A,), anchor='ma')
    cur = [n for n in o.get('notes', []) if t >= n[1]]
    if cur: d.text((W // 2, int(H * 0.16) + 40), cur[-1][0], font=font('oswald', 56), fill=cur[-1][2] + (A,), anchor='ma')
EXTRA['bottle'] = _bottle
