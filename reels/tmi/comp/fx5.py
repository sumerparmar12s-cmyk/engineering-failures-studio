"""Three Mile Island reel look (new): 1979 control room. Annunciator alarm wall, the lying indicator lamp,
relief-valve diagram with live steam, tank level gauge, core temperature bar, phosphor-green labels, radiation badge."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine
from engine import EXTRA, font, eout, ease, clamp, lerp, W, H

AMBER, GREEN, RED, WHITE, GREY, CREAM = (255, 176, 40), (80, 255, 120), (255, 60, 50), (255, 255, 255), (170, 170, 160), (240, 232, 210)
engine.GRADES['seventies'] = engine._lut((1.05, 0.02), (1.0, 0.01), (0.88, 0.0), lift=0.04, gamma=1.02, gain=0.97, sat=0.8)
engine.GRADES['crt'] = engine._lut((0.9, 0.0), (1.05, 0.02), (0.92, 0.0), lift=0.03, gamma=1.0, gain=0.98, sat=0.7)

def _annun(d, lay, o, t, a, A, fi):
    """Alarm wall: tiles (text, on_at, color). Lit tiles blink for 1.5 s then stay lit."""
    cols = o.get('cols', 3); tiles = o['tiles']; x0, y0 = o.get('xy', (60, 330)); tw = (W - 2 * x0 - (cols - 1) * 14) // cols; th = o.get('th', 120)
    d.rectangle([x0 - 24, y0 - 24, W - x0 + 24, y0 + (th + 14) * ((len(tiles) + cols - 1) // cols) + 10], fill=(18, 18, 16, int(230 * a)))
    for i, (txt, on, col) in enumerate(tiles):
        cx, cy = x0 + (i % cols) * (tw + 14), y0 + (i // cols) * (th + 14)
        lit = on is not None and t >= on
        blink = lit and (t - on < 1.5) and (fi // 5) % 2 == 0
        fill = (col if lit and not blink else (52, 50, 44)) + (int(235 * a),)
        d.rectangle([cx, cy, cx + tw, cy + th], fill=fill, outline=(90, 88, 80, A), width=3)
        f = font('oswald', 30); lines = txt.split('\n')
        for j, l in enumerate(lines):
            d.text((cx + tw / 2, cy + th / 2 + (j - (len(lines) - 1) / 2) * 34), l, font=f, fill=((20, 16, 10) if lit and not blink else (150, 146, 130)) + (A,), anchor='mm')
EXTRA['annun'] = _annun

def _lamp(d, lay, o, t, a, A, fi):
    """Indicator lamp with label: glows its colour; optional 'truth' tag fades in later."""
    cx, cy, r = o.get('x', W // 2), o.get('y', 700), o.get('r', 120); col = o.get('color', GREEN)
    for k in range(6, 0, -1): d.ellipse([cx - r - k * 14, cy - r - k * 14, cx + r + k * 14, cy + r + k * 14], fill=col + (int(14 * a),))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (A,), outline=(30, 30, 30, A), width=10)
    d.ellipse([cx - r * 0.45, cy - r * 0.55, cx - r * 0.05, cy - r * 0.2], fill=(255, 255, 255, int(110 * a)))
    d.text((cx, cy - r - 70), o['label'], font=font('oswald', 46), fill=CREAM + (A,), anchor='mm')
    d.text((cx, cy + r + 60), o['state'], font=font('bebas', 110), fill=col + (A,), anchor='mm')
    if o.get('truth') and t >= o['truth'][0]:
        p = eout((t - o['truth'][0]) / 0.4)
        d.text((cx, cy + r + 170), o['truth'][1], font=font('bebas', 96), fill=RED + (int(A * p),), anchor='mm')
EXTRA['lamp'] = _lamp

def _valve(d, lay, o, t, a, A, fi):
    """Pipe with a relief valve on top; disc lifts at open_at; steam particles stream out while open."""
    cx, cy = o.get('x', W // 2), o.get('y', 900); s = o.get('s', 1.0)
    pw = int(90 * s)
    d.rectangle([cx - pw // 2, cy, cx + pw // 2, cy + int(520 * s)], fill=(120, 130, 140, A))      # pipe up from vessel
    d.rectangle([cx - int(170 * s), cy + int(520 * s), cx + int(170 * s), cy + int(700 * s)], fill=(90, 100, 110, A))  # vessel top
    op = clamp((t - o['open_at']) / 0.4) if t >= o['open_at'] else 0.0
    lift = int(70 * s * op)
    d.rectangle([cx - int(110 * s), cy - int(40 * s) - lift, cx + int(110 * s), cy - lift], fill=(200, 60, 40, A) if op > 0 else (150, 150, 150, A))
    d.text((cx + int(140 * s), cy - int(20 * s)), 'RELIEF VALVE', font=font('oswald', 34), fill=CREAM + (A,), anchor='lm')
    if op > 0:
        rnd = random.Random(7)
        for i in range(90):
            ph = (t * 1.8 + rnd.random()) % 1.0; ang = rnd.uniform(-0.9, 0.9)
            px = cx + math.sin(ang) * ph * 420 * s; py = cy - lift - ph * 560 * s; rr = 10 + ph * 46
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=(235, 240, 245, int(A * 0.32 * (1 - ph) * op)))
    if o.get('stuck') and t >= o['stuck']:
        p = eout((t - o['stuck']) / 0.35)
        d.text((cx, cy - int(330 * s)), 'STUCK OPEN', font=font('bebas', 120), fill=RED + (int(A * p),), anchor='mm')
EXTRA['valve'] = _valve

def _level(d, lay, o, t, a, A, fi):
    """Tank level gauge: keyframes [(t, level 0..1)]."""
    x, y, w, h = o.get('box', (W // 2 - 140, 520, 280, 760))
    ks = o['keys']; lv = ks[0][1]
    for (ta, va), (tb, vb) in zip(ks, ks[1:]):
        if ta <= t < tb: lv = lerp(va, vb, ease((t - ta) / (tb - ta)))
        elif t >= tb: lv = vb
    d.rectangle([x - 10, y - 10, x + w + 10, y + h + 10], fill=(20, 20, 18, int(220 * a)), outline=CREAM + (A,), width=4)
    col = (60, 150, 255) if lv > 0.4 else ((255, 170, 40) if lv > 0.2 else RED)
    d.rectangle([x, y + h * (1 - lv), x + w, y + h], fill=col + (A,))
    for k in range(1, 10): d.line([(x + w - 30, y + h * k / 10), (x + w, y + h * k / 10)], fill=(255, 255, 255, int(120 * a)), width=2)
    d.text((x + w / 2, y - 60), o.get('label', 'REACTOR WATER LEVEL'), font=font('oswald', 40), fill=CREAM + (A,), anchor='mm')
    if o.get('note') and t >= o['note'][0]:
        d.text((x + w / 2, y + h + 70), o['note'][1], font=font('bebas', 80), fill=o['note'][2] + (A,), anchor='mm')
EXTRA['level'] = _level

def _thermo(d, lay, o, t, a, A, fi):
    """Core temperature bar climbing to red with shake at the top."""
    p = ease(clamp((t - o['at']) / o.get('dur', 4.0))); x, y, w, h = W // 2 - 60, 430, 120, 640
    d.rounded_rectangle([x - 14, y - 14, x + w + 14, y + h + 14], radius=70, fill=(20, 20, 18, int(220 * a)), outline=CREAM + (A,), width=4)
    hh = h * (0.25 + 0.72 * p); col = (int(lerp(255, 255, p)), int(lerp(190, 50, p)), int(lerp(60, 40, p)))
    jit = int(6 * math.sin(fi * 1.7)) if p > 0.85 else 0
    d.rounded_rectangle([x + jit, y + h - hh, x + w + jit, y + h], radius=60, fill=col + (A,))
    d.text((W // 2, y - 70), 'CORE TEMPERATURE', font=font('oswald', 44), fill=CREAM + (A,), anchor='mm')
    if p > 0.85: d.text((W // 2, y + h + 80), 'OVERHEATING', font=font('bebas', 110), fill=RED + (A,), anchor='mm')
EXTRA['thermo'] = _thermo

def trefoil(d, cx, cy, r, col):
    for k in range(3):
        a0 = -90 + k * 120 - 30
        d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a0 + 60, fill=col)
    d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18], fill=col)
