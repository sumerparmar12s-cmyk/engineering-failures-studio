"""Titan look (new for this episode): two intercut timelines.
DIVE timeline  -> cold 'abyss' grade + live depth gauge (right edge), dive clock, pressure readout.
FLASHBACK      -> warm desaturated 'flashback' grade, flicker + scratches, a 'FLASHBACK · <date>' slate.
Overlays: acoustic text-message console (chat), depth cards, sonar scope with sweep, plus fx3 helpers (stat, names, callout)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import engine
from engine import EXTRA, font, eout, ease, clamp, lerp, W, H
import fx3  # registers stat / names / callout / bigtime overlays

CYAN, AMBER, WHITE, GREY, RED = (90, 220, 255), (255, 176, 60), (255, 255, 255), (160, 175, 190), (255, 70, 60)
PSI_PER_M = 4930 / 3346.0          # report: ~4,930 psi at the implosion depth

engine.GRADES['abyss'] = engine._lut((0.86, 0.0), (1.0, 0.01), (1.12, 0.04), lift=0.02, gamma=1.08, gain=0.97, sat=0.78)
engine.GRADES['flashback'] = engine._lut((1.06, 0.02), (1.0, 0.01), (0.86, 0.0), lift=0.05, gamma=1.0, gain=0.95, sat=0.45)
engine.GRADES['report'] = engine._lut((1.0, 0.0), (1.0, 0.0), (0.97, 0.0), lift=0.0, gamma=1.0, gain=1.0, sat=0.9)

def _depth_at(KEYS, t):
    """KEYS: [(t, depth_m, 'HH:MM:SS')]; linear between keys (descent is continuous)."""
    if t <= KEYS[0][0]: return KEYS[0][1], KEYS[0][2]
    for (a, da, ca), (b, db, cb) in zip(KEYS, KEYS[1:]):
        if a <= t < b: return lerp(da, db, (t - a) / (b - a)), ca
    return KEYS[-1][1], KEYS[-1][2]

def depth_post(KEYS, dive_ranges, flash_ranges, end_depth=None):
    rnd = random.Random(7)
    scratches = [(rnd.randint(0, W), rnd.randint(3, 9)) for _ in range(40)]
    def post(img, t, fi, sh):
        inside = lambda rr: any(a <= t < b for a, b in rr)
        if sh.k.get('nohud'): return img
        if inside(flash_ranges) and sh.k.get('fb'):
            a = np.asarray(img).astype(np.float32)
            a *= 0.93 + 0.07 * math.sin(fi * 2.1) * math.sin(fi * 0.7)          # projector flicker
            r = random.Random(fi // 2)
            for _ in range(2):
                x, wdt = scratches[r.randint(0, len(scratches) - 1)]; a[:, x:x + 2] = a[:, x:x + 2] * 0.6 + 70
            img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
            d = ImageDraw.Draw(img, 'RGBA'); p = eout((t - sh.t0) / 0.4)
            txt = 'FLASHBACK  ·  ' + sh.k['fb']; f = font('monob', 34 if W > H else 40)
            x, y = (70, 70) if W > H else (60, 250)
            tw = f.getlength(txt)
            d.rectangle([x - 16, y - 12, x + tw + 20, y + 50], fill=(0, 0, 0, 160))
            d.rectangle([x - 16, y - 12, x - 10, y + 50], fill=AMBER + (255,))
            d.text((x + (1 - p) * -30, y), txt, font=f, fill=AMBER + (int(255 * p),))
            return img
        if not inside(dive_ranges): return img
        dep, clk = _depth_at(KEYS, t)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if W > H:
            gx, gy0, gy1 = W - 120, 150, H - 150
        else:
            gx, gy0, gy1 = W - 90, 420, H - 620
        MAXD = 4000.0
        d.rectangle([gx - 70, gy0 - 70, gx + 60, gy1 + 80], fill=(0, 8, 14, 120))
        d.line([(gx, gy0), (gx, gy1)], fill=(255, 255, 255, 90), width=3)
        for m in range(0, 4001, 500):
            yy = gy0 + (gy1 - gy0) * m / MAXD; L = 18 if m % 1000 == 0 else 9
            d.line([(gx - L, yy), (gx, yy)], fill=(255, 255, 255, 150), width=2)
            if m % 1000 == 0: d.text((gx - 26, yy), f'{m}', font=font('mono', 20), fill=GREY + (220,), anchor='rm')
        ty = gy0 + (gy1 - gy0) * 3800 / MAXD                         # Titanic depth line
        for xx in range(gx - 60, gx + 40, 12): d.line([(xx, ty), (xx + 6, ty)], fill=AMBER + (200,), width=2)
        d.text((gx - 62, ty + 8), 'TITANIC', font=font('mono', 18), fill=AMBER + (230,))
        yy = gy0 + (gy1 - gy0) * min(dep, MAXD) / MAXD
        d.line([(gx, gy0), (gx, yy)], fill=CYAN + (255,), width=7)
        d.polygon([(gx + 8, yy), (gx + 30, yy - 12), (gx + 30, yy + 12)], fill=CYAN + (255,))
        # readout block (top-left)
        x, y = (70, 70) if W > H else (60, 250)
        f1, f2 = font('monob', 38 if W > H else 44), font('mono', 28 if W > H else 32)
        d.rectangle([x - 16, y - 12, x + 600, y + 128], fill=(0, 0, 0, 150))
        d.rectangle([x - 16, y - 12, x - 10, y + 128], fill=CYAN + (255,))
        d.text((x, y), f'DIVE 88  ·  JUNE 18, 2023  ·  {clk}', font=f1 if W > H else font('monob', 30), fill=WHITE + (255,))
        d.text((x, y + 50), f'DEPTH     {int(dep):>5,} m', font=f2, fill=CYAN + (255,))
        psi = int(dep * PSI_PER_M)
        col = RED if dep > 3000 else (AMBER if dep > 1500 else GREY)
        d.text((x, y + 86), f'PRESSURE  {psi:>5,} psi', font=f2, fill=col + (255,))
        img = img.convert('RGBA'); img.alpha_composite(lay); return img.convert('RGB')
    return post

# ---------------- acoustic text-message console ----------------
def _chat(d, lay, o, t, a, A, fi):
    x0, y0, w = o.get('box', (W // 2 - 520, 230, 1040)) if W > H else o.get('box', (60, 520, W - 120))
    msgs = [m for m in o['msgs'] if t >= m[0]]
    shown = msgs[-o.get('keep', 5):]
    rowh = 96 if W > H else 110; hgt = 90 + rowh * max(1, o.get('keep', 5))
    d.rectangle([x0, y0, x0 + w, y0 + hgt], fill=(2, 10, 16, int(215 * a)), outline=CYAN + (int(160 * a),), width=2)
    d.text((x0 + 24, y0 + 22), o.get('title', 'ACOUSTIC TEXT LINK  ·  POLAR PRINCE <-> TITAN'), font=font('mono', 24), fill=CYAN + (A,))
    d.line([(x0, y0 + 64), (x0 + w, y0 + 64)], fill=CYAN + (int(90 * a),), width=1)
    fm = font('monob', 34 if W > H else 36); fs = font('mono', 22)
    for i, (at, who, text, stamp) in enumerate(shown):
        yy = y0 + 84 + i * rowh; k = clamp((t - at) / max(0.3, len(text) / 26))
        vis = text[:int(len(text) * k + 0.999)]
        mine = who == 'PP'; col = (150, 235, 255) if mine else AMBER
        tw = fm.getlength(vis) + 40; bx = x0 + w - 24 - tw if mine else x0 + 24
        d.rounded_rectangle([bx, yy, bx + tw, yy + 58], radius=14, fill=col + (int(40 * a),), outline=col + (A,), width=2)
        d.text((bx + 20, yy + 12), vis + ('_' if k < 1 and (fi // 6) % 2 == 0 else ''), font=fm, fill=WHITE + (A,))
        lab = ('POLAR PRINCE' if mine else 'TITAN') + '  ' + stamp
        d.text((bx + (tw if mine else 0), yy + 62), lab, font=fs, fill=col + (int(200 * a),), anchor='ra' if mine else 'la')
EXTRA['chat'] = _chat

# ---------------- depth card ----------------
def _depthcard(d, lay, o, t, a, A, fi):
    p = eout((t - o['at']) / 1.2); dep = lerp(o.get('from', 0), o['depth'], p)
    cx, cy = W // 2, H // 2 - (40 if W > H else 120)
    d.rectangle([0, 0, W, H], fill=(0, 6, 12, int(120 * a)))
    d.text((cx, cy - 150), 'DEPTH', font=font('mono', 40), fill=CYAN + (A,), anchor='mm')
    d.text((cx, cy), f'{int(dep):,} m', font=font('bebas', 230 if W > H else 200), fill=WHITE + (A,), anchor='mm')
    d.text((cx, cy + 150), f'{int(dep * 3.281):,} ft   ·   {int(dep * PSI_PER_M):,} psi', font=font('mono', 34), fill=GREY + (A,), anchor='mm')
    if o.get('sub'): d.text((cx, cy + 215), o['sub'], font=font('oswald', 40), fill=AMBER + (A,), anchor='mm')
EXTRA['depthcard'] = _depthcard

# ---------------- sonar scope ----------------
def _sonar(d, lay, o, t, a, A, fi):
    cx, cy = o.get('c', (W // 2, H // 2)); R = o.get('r', 360)
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(0, 20, 18, int(170 * a)), outline=(80, 255, 170, A), width=3)
    for k in (0.33, 0.66): d.ellipse([cx - R * k, cy - R * k, cx + R * k, cy + R * k], outline=(80, 255, 170, int(90 * a)), width=2)
    d.line([(cx - R, cy), (cx + R, cy)], fill=(80, 255, 170, int(70 * a))); d.line([(cx, cy - R), (cx, cy + R)], fill=(80, 255, 170, int(70 * a)))
    ang = (t - o['at']) * 2.2
    for j in range(14):
        aa = ang - j * 0.05; d.line([(cx, cy), (cx + R * math.cos(aa), cy + R * math.sin(aa))], fill=(80, 255, 170, int(A * (1 - j / 14) * 0.8)), width=4)
    for (bt, bang, br, lab) in o.get('blips', []):
        if t >= bt:
            bx, by = cx + R * br * math.cos(bang), cy + R * br * math.sin(bang); pp = 10 + 6 * math.sin((t - bt) * 7)
            d.ellipse([bx - pp, by - pp, bx + pp, by + pp], fill=(255, 220, 90, A))
            if lab: d.text((bx + 22, by - 14), lab, font=font('monob', 30), fill=(255, 220, 90, A))
    if o.get('title'): d.text((cx, cy + R + 40), o['title'], font=font('mono', 30), fill=(80, 255, 170, A), anchor='mm')
EXTRA['sonar'] = _sonar

# ---------------- ping transition (registered into engine.transition) ----------------
_orig_trans = engine.transition
def _trans(img, prev, sh, t, fi):
    dt = t - sh.t0
    if sh.trans == 'ping' and dt < 0.5:
        p = eout(dt / 0.5); R = int(p * math.hypot(W, H) / 2) + 2
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse([W // 2 - R, H // 2 - R, W // 2 + R, H // 2 + R], fill=255)
        base = Image.new('RGB', (W, H), (0, 10, 16)); base.paste(img, (0, 0), m)
        d = ImageDraw.Draw(base); d.ellipse([W // 2 - R, H // 2 - R, W // 2 + R, H // 2 + R], outline=CYAN, width=max(2, int(10 * (1 - p))))
        return engine.transition.__wrapped__(base, prev, _NoTrans(sh), t, fi)
    if sh.trans == 'sink' and dt < 0.45:       # image slides up into frame from below (going deeper)
        p = eout(dt / 0.45); off = int((1 - p) * H)
        base = Image.new('RGB', img.size, (0, 8, 14)); base.paste(img, (0, off)); return base
    return _orig_trans(img, prev, sh, t, fi)
class _NoTrans:
    def __init__(self, sh): self.__dict__.update(sh.__dict__); self.trans = 'cut'
_trans.__wrapped__ = _orig_trans
engine.transition = _trans
