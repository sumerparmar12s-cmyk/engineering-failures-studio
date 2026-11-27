"""Point Roberts reel: self-drawn 3D-tilted map + cairo cartoons. usage: python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math, subprocess, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import world3d as WD, toons as TO, toons2 as T2
from world3d import Camera as Cm
R = WD.R; W, H, FPS = 1080, 1920, 30; END = 61.6
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json'))
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
def F(name, size):
    p = {'play': 'PlayfairDisplay.ttf', 'oswald': 'Oswald.ttf'}.get(name)
    f = ImageFont.truetype(f'{FONTS}/{p}', size) if p else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
    try:
        if name == 'play': f.set_variation_by_axes([800])
        if name == 'oswald': f.set_variation_by_axes([600])
    except Exception: pass
    return f
clamp = lambda x, a=0, b=1: max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x): x = clamp(x); c1 = 1.9; return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pop(t, t0, d=0.35): return back((t - t0) / d) if t >= t0 else 0
ART = {}
def art(k, fn):
    if k not in ART: ART[k] = fn()
    return ART[k]
def paste(img, im, cx, cy, sc=1.0, rot=0, alpha=1.0):
    if sc <= 0.01: return
    i = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if rot: i = i.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: i.putalpha(i.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(i, (int(cx - i.width / 2), int(cy - i.height / 2)))
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=50, sc=1.0, font='SemiBold'):
    if sc <= 0.02: return
    f = F(font, int(size)); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 50), int(size * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width - 1, im.height - 1], fill=bg + (255,)); d.rectangle([0, im.height - 6, im.width - 1, im.height - 1], fill=tuple(int(v * 0.7) for v in bg) + (255,))
    d.text((im.width / 2, im.height / 2 - 1), txt, font=f, fill=fg, anchor='mm'); paste(img, im, xy[0], xy[1], sc)
def stext(img, xy, txt, f, fill=(255, 255, 255), a=1.0, anchor='mm'):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, int(200 * a)), anchor=anchor); lay = lay.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(lay).text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor=anchor); img.alpha_composite(lay)
# ---------- camera path ----------
KEYS = [(0.0, Cm(-99, 43, 11500, 24, 0)), (3.0, Cm(-101, 44, 10600, 27, -3)),
        (5.7, Cm(-123.03, 49.01, 75, 46, -14)), (10.5, Cm(-123.045, 49.0, 58, 50, -24)), (13.4, Cm(-123.05, 48.99, 42, 56, -32)),
        (16.2, Cm(-111, 47.5, 5200, 38, -6)), (26.9, Cm(-110, 47.8, 4900, 40, -2)),
        (30.3, Cm(-123.04, 49.0, 85, 48, -10)), (35.1, Cm(-123.045, 48.995, 62, 50, -16)),
        (40.0, Cm(-123.05, 48.985, 30, 50, -20)), (45.4, Cm(-123.052, 48.985, 26, 52, -24)), (46.6, Cm(-122.89, 49.015, 80, 42, -6)),
        (50.9, Cm(-122.90, 49.015, 76, 43, -5)), (52.0, Cm(-123.02, 48.99, 40, 50, -14)), (56.0, Cm(-123.05, 48.985, 32, 52, -22)), (61.6, Cm(-123.05, 48.985, 95, 38, -38))]
def cam_at(t):
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t < t1: return a.lerp(b, ease((t - t0) / (t1 - t0)))
    return KEYS[-1][1]
# ---------- geometry ----------
US = WD.country('United States of America'); CA = WD.country('Canada')
PR = WD.poly_rings(WD.PR_POLY); CAL = WD.poly_rings(WD.CA_LOCAL); USL = WD.poly_rings(WD.US_LOCAL)
ROUTE = [(-122.70, 48.96), (-122.735, 48.985), (-122.757, 49.0), (-122.78, 49.03), (-122.86, 49.055), (-122.95, 49.06), (-123.02, 49.05), (-123.045, 49.03), (-123.062, 49.0), (-123.062, 48.985)]
CROSS = [(-122.757, 49.0), (-123.062, 49.0)]
rng = random.Random(4)
PEOPLE = []
while len(PEOPLE) < 26:
    lo, la = rng.uniform(-123.088, -123.026), rng.uniform(48.974, 48.998)
    if WD.PR_POLY.buffer(-0.002).contains(WD.Polygon([(lo, la), (lo + 1e-5, la), (lo, la + 1e-5)])): PEOPLE.append((lo, la))
def proj(cam, pts):
    lo = np.array([p[0] for p in pts]); la = np.array([p[1] for p in pts]); x, y, ok = cam.project(lo, la, W, H); return list(zip(x, y)), ok
def cpoly(c, cam, rings, fill, alpha, stroke=(1, 1, 1), lw=3, sa=0.9, dash=None):
    c.new_path()
    for r in rings:
        pts, ok = proj(cam, r)
        if not ok.all(): continue
        for i, (x, y) in enumerate(pts): (c.move_to if i == 0 else c.line_to)(x, y)
        c.close_path()
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source_rgba(*fill, alpha); c.fill_preserve()
    if dash: c.set_dash(dash)
    c.set_source_rgba(*stroke, sa); c.set_line_width(lw); c.stroke(); c.set_dash([])
def cline(c, cam, pts, col, lw, a=1.0, dash=None, frac=1.0):
    P, ok = proj(cam, pts)
    if frac < 1:   # partial polyline by length
        L = [0]; 
        for (x0, y0), (x1, y1) in zip(P, P[1:]): L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
        tgt = L[-1] * frac; Q = [P[0]]
        for i in range(1, len(P)):
            if L[i] <= tgt: Q.append(P[i])
            else:
                k = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); Q.append((P[i - 1][0] + (P[i][0] - P[i - 1][0]) * k, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * k)); break
        P = Q
    if len(P) < 2: return P[-1] if P else None
    c.new_path(); c.move_to(*P[0])
    for p in P[1:]: c.line_to(*p)
    if dash: c.set_dash(dash)
    c.set_source_rgba(*col, a); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke(); c.set_dash([]); return P[-1]
def route_point(cam, frac, pts=ROUTE):
    P, _ = proj(cam, pts); L = [0]
    for (x0, y0), (x1, y1) in zip(P, P[1:]): L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
    tgt = L[-1] * clamp(frac)
    for i in range(1, len(P)):
        if L[i] >= tgt:
            k = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); return (P[i - 1][0] + (P[i][0] - P[i - 1][0]) * k, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * k), math.degrees(math.atan2(P[i][1] - P[i - 1][1], P[i][0] - P[i - 1][0]))
    return P[-1], 0
def at(cam, lon, lat): (x, y), ok = proj(cam, [(lon, lat)]); return x[0] if isinstance(x, tuple) else x, y
def geo(cam, lon, lat): P, ok = proj(cam, [(lon, lat)]); return P[0]
# ---------- subtitles (small, like native captions) ----------
GROUPS = []; cur = []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15:
            stext(img, (W // 2, 1600), ' '.join(x['w'] for x in g), F('SemiBold', 44)); break
# ---------- frame ----------
LOW = None
def frame(t):
    cam = cam_at(t)
    base = WD.render(cam, 540, 960).resize((W, H), Image.BICUBIC).convert('RGBA')
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    far = cam.dist > 1500
    if t < 5.0:   # US / Canada highlight
        a = clamp(1 - (t - 4.2) / 0.8)
        cpoly(c, cam, US, (0.2, 0.4, 0.95), 0.45 * eout(t / 0.4) * a, lw=3)
        if t >= 1.68: cpoly(c, cam, CA, (0.92, 0.2, 0.25), 0.45 * eout((t - 1.68) / 0.4) * a, lw=3)
    if 3.0 <= t < 5.7:   # target ring on the corner
        x, y = geo(cam, -123.05, 49.0); r = 60 + 10 * math.sin(t * 8)
        c.arc(x, y, r, 0, 6.3); c.set_source_rgba(1, 0.85, 0.2, 0.95); c.set_line_width(7); c.stroke()
    if 5.68 <= t < 14.5 or 30.3 <= t < 35.1 or t >= 40.0:   # local polygons
        k = eout((t - 5.68) / 0.4) if t < 14.5 else 1
        cpoly(c, cam, CAL, (0.92, 0.2, 0.25), 0.30 * k, lw=0.1, sa=0)
        cpoly(c, cam, [r for r in USL], (0.2, 0.42, 0.95), 0.22 * k, lw=0.1, sa=0)
        tip_on = not (30.3 <= t < 32.46) or (t >= 32.46)
        flash = 0.25 * (math.sin(t * 12) > 0) if 32.46 <= t < 34.0 else 0
        cpoly(c, cam, PR, (0.2, 0.42, 0.95), (0.5 + flash) * k if tip_on else 0.0, lw=4)
        cline(c, cam, [(-123.2, 49.0), (-122.6, 49.0)], (1, 1, 1), 4, 0.95, dash=[16, 12])
    if 7.36 <= t < 10.6:   # drive route (US -> Canada -> US)
        fr = ease((t - 7.4) / 2.9); cline(c, cam, ROUTE, (1, 0.85, 0.2), 9, 1, dash=[2, 18], frac=fr)
    if 16.2 <= t < 30.3:   # 1846 wide map, 49th parallel drawn
        fr = ease((t - 21.9) / 1.6)
        if fr > 0: cline(c, cam, [(-95.15 - 1.0 * i, 49.0) for i in range(0, 30)], (1, 0.86, 0.2), 9, 1, frac=fr)
    if 27.0 <= t < 30.3:
        cline(c, cam, [(-95.15 - 1.0 * i, 49.0) for i in range(0, 30)], (1, 0.86, 0.2), 9, 1)
    if 30.3 <= t < 35.1:   # the line slices the peninsula
        fr = ease((t - 30.4) / 1.2); cline(c, cam, [(-123.25, 49.0), (-122.85, 49.0)], (1, 0.86, 0.2), 11, 1, frac=fr)
    if 45.48 <= t < 50.9:   # school bus: there and back, 4 crossings
        pass
    img = base; img.alpha_composite(TO._pil(s))
    # ---------- stickers & labels ----------
    if t < 5.0:
        a = clamp(1 - (t - 4.2) / 0.8)
        if a > 0:
            x, y = geo(cam, -99, 40); pill(img, (x, y), 'United States', (40, 90, 220), size=52, sc=pop(t, 0.3) * a)
            if t >= 1.68: x, y = geo(cam, -103, 57); pill(img, (x, y), 'Canada', (215, 40, 55), size=52, sc=pop(t, 1.7) * a)
    if 3.06 <= t < 5.7: stext(img, (W // 2, 300), 'Look closely...', F('play', 80), a=eout((t - 3.1) / 0.3))
    if 5.68 <= t < 10.6:
        x, y = geo(cam, -123.057, 48.985); pill(img, (x, y + 110), 'USA', (40, 90, 220), size=56, sc=pop(t, 5.75))
        x, y = geo(cam, -123.0, 49.04); pill(img, (x, y - 30), 'Canada', (215, 40, 55), size=52, sc=pop(t, 6.0))
        if t >= 7.36:
            (px, py), ang = route_point(cam, ease((t - 7.4) / 2.9)); paste(img, art('carus', lambda: T2.car((0.2, 0.45, 0.9), 150, leaf=False)), px, py - 30, pop(t, 7.36, 0.3))
            for i, (lo, la) in enumerate(CROSS):
                tc = 7.4 + 2.9 * (0.18 if i == 0 else 0.86)
                if t >= tc: x, y = geo(cam, lo, la); pill(img, (x, y - 70), 'BORDER', (30, 30, 34), size=36, sc=pop(t, tc))
    if 10.62 <= t < 14.5:
        stext(img, (W // 2, 280), 'Point Roberts', F('play', 104), a=eout((t - 10.62) / 0.3)); stext(img, (W // 2, 390), 'Washington, USA', F('SemiBold', 50), a=eout((t - 11.6) / 0.3))
        if t >= 13.26: stext(img, (W // 2, 1250), 'But... how?', F('play', 86), fill=(255, 220, 90), a=eout((t - 13.26) / 0.2))
    if 14.5 <= t < 30.3:
        if t >= 14.86: stext(img, (W // 2, 270), '1846', F('play', 150), a=eout((t - 14.86) / 0.3))
        if t >= 16.24: paste(img, art('pol', lambda: T2.polk('smug', 340)), 260, 1330, pop(t, 16.24)); pill(img, (260, 1580), 'USA', (40, 90, 220), size=40, sc=pop(t, 16.4))
        if t >= 17.56: paste(img, art('vic', lambda: T2.victoria('neutral', 340)), 820, 1330, pop(t, 17.56)); pill(img, (820, 1580), 'BRITAIN', (215, 40, 55), size=40, sc=pop(t, 17.7))
        if 19.8 <= t < 24.0: stext(img, (W // 2, 470), 'The easy option:', F('SemiBold', 54), a=eout((t - 20.2) / 0.3))
        if t >= 24.04: x, y = geo(cam, -108, 49.0); pill(img, (x, y - 60), '49th PARALLEL', (240, 175, 20), (20, 20, 20), 46, pop(t, 24.1))
        for i, (t0, w) in enumerate(((25.32, 'CLEAN'), (25.82, 'SIMPLE'), (26.1, 'DONE'))):
            if t >= t0: pill(img, (W // 2, 760 + i * 95), w + ' ✓', (40, 170, 90), size=50, sc=pop(t, t0, 0.25))
        if t >= 27.08: stext(img, (W // 2, 1080), 'Except...', F('play', 96), fill=(255, 220, 90), a=eout((t - 27.08) / 0.2))
    if 30.3 <= t < 35.1:
        if t >= 32.46: x, y = geo(cam, -123.057, 48.985); pill(img, (x, y + 110), 'USA!', (40, 90, 220), size=58, sc=pop(t, 32.5))
        if t >= 30.4: stext(img, (W // 2, 300), 'Snip.', F('play', 110), a=eout((t - 30.42) / 0.2))
    if 35.1 <= t < 40.0:   # the comedy exchange over a blurred map
        bl = img.filter(ImageFilter.GaussianBlur(16)); img.alpha_composite(bl); img.alpha_composite(Image.new('RGBA', (W, H), (10, 20, 40, 100)))
        paste(img, art('vic_w', lambda: T2.victoria('worried', 420)), 290, 1300, pop(t, 35.14))
        if t >= 35.9: paste(img, art('bv', lambda: TO.bubble('Can we just\nkeep that bit?', 56)), 340, 850, pop(t, 35.95, 0.3))
        if t >= 37.28: paste(img, art('pol_s', lambda: T2.polk('smug', 380)), 800, 760, pop(t, 37.28))
        if t >= 37.8: paste(img, art('bp1', lambda: TO.bubble('Nope.', 64, tail='right')), 760, 380, pop(t, 37.84, 0.3))
        if t >= 38.5: paste(img, art('bp2', lambda: TO.bubble('A line is a line.', 46, tail='right')), 700, 230, pop(t, 38.5, 0.3))
    if 40.0 <= t < 45.48:
        for i, (lo, la) in enumerate(PEOPLE):
            t0 = 40.8 + i * 0.05
            if t >= t0: x, y = geo(cam, lo, la); paste(img, art(f'pin{i % 3}', lambda: T2.pin([(0.2, 0.45, 0.9), (0.9, 0.3, 0.3), (0.95, 0.7, 0.2)][i % 3], 46)), x, y - 26, pop(t, t0, 0.25))
        if t >= 41.3: pill(img, (W // 2, 300), '~1,000 AMERICANS', (40, 90, 220), size=56, sc=pop(t, 41.3))
        if t >= 43.08: pill(img, (W // 2, 420), 'Canada on one side. Sea on the rest.', (30, 30, 34), size=38, sc=pop(t, 43.1))
    if 45.48 <= t < 50.94:   # bus: PR -> Canada -> Blaine and back = 4 crossings
        u = clamp((t - 45.8) / 4.4); there = u < 0.5; fr = (1 - u * 2) if there else (u - 0.5) * 2   # route is US(Blaine)->PR ; trip starts at PR
        (px, py), ang = route_point(cam, fr); paste(img, art('bus', lambda: T2.bus(200)), px, py - 30, pop(t, 45.6))
        n = 0
        for k_, f0 in enumerate((0.92, 0.18, 0.18, 0.92)):   # crossing order along the round trip
            pass
        n = (1 if u > 0.04 else 0) + (1 if u > 0.42 else 0) + (1 if u > 0.58 else 0) + (1 if u > 0.96 else 0)
        pill(img, (W // 2, 300), f'BORDER CROSSINGS: {n}', (240, 175, 20), (20, 20, 20), 54, pop(t, 45.6))
        x, y = geo(cam, -122.745, 48.975); pill(img, (x + 40, y + 60), 'Blaine (school)', (40, 90, 220), size=34, sc=pop(t, 46.0))
    if 50.94 <= t < 56.0:
        for i in range(3):
            t0 = 51.2 + i * 0.6; u = clamp((t - t0) / 2.6)
            if t >= t0: (px, py), _ = route_point(cam, 0.55 + 0.45 * u, list(reversed(list(reversed(ROUTE))))); paste(img, art('carca', lambda: T2.car((0.85, 0.15, 0.2), 140)), px, py - 26, pop(t, t0, 0.3))
        x, y = geo(cam, -123.06, 48.982)
        if t >= 52.88: paste(img, art('gas', lambda: T2.gaspump(170)), x - 170, y - 120, pop(t, 52.9)); pill(img, (x - 170, y + 20), 'CHEAPER GAS', (40, 170, 90), size=34, sc=pop(t, 53.0))
        if t >= 54.2:
            for j in range(5): paste(img, art('pkg', lambda: T2.package(110)), x + 150 + (j % 3) * 70, y - 40 - (j // 3) * 70, pop(t, 54.2 + j * 0.08, 0.25))
            pill(img, (x + 220, y + 60), 'ONLINE ORDERS', (215, 120, 30), size=34, sc=pop(t, 54.4))
    if t >= 56.0:
        if t >= 58.2: paste(img, art('pp', lambda: T2.passport(220, cross=True)), W // 2, 560, pop(t, 58.22))
        if t >= 59.3:
            x, y = geo(cam, -123.057, 48.983); paste(img, art('palm', lambda: T2.palm(260)), x + 20, y - 90, pop(t, 59.3))
            stext(img, (W // 2, 300), 'Basically... an island.', F('play', 78), a=eout((t - 59.3) / 0.3))
    subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 10, int(W * t / END), H], fill=(240, 175, 20, 255))
    return img.convert('RGB')
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): frame(tt).resize((360, 640)).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(round(a * FPS)), int(round(b * FPS))):
            enc.stdin.write(np.asarray(frame(fi / FPS)).tobytes())
            if fi % 150 == 0: print(f'{fi / FPS:.1f}s', flush=True)
        enc.stdin.close(); enc.wait()
