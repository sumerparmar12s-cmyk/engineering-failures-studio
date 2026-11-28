"""Paul Revere / three riders. Point Roberts look on the self-drawn globe + ref-4 techniques (voiced lines, chat gag, counters).
usage: python3 edit.py OUT.mp4 [t0 t1] | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import Point, shape
from shapely.ops import unary_union
import globe3d as G, toons as TO, toons3 as T3, toons4 as T4
from globe3d import Camera as Cm
R = G.R; W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json')); END = round(WORDS[-1]['e'] + 1.1, 2)
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
def F(name, size):
    p = {'play': 'PlayfairDisplay.ttf', 'oswald': 'Oswald.ttf'}.get(name)
    f = ImageFont.truetype(f'{FONTS}/{p}', size) if p else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
    try:
        if name == 'play': f.set_variation_by_axes([800])
        if name == 'oswald': f.set_variation_by_axes([600])
    except Exception: pass
    return f
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
def T(word, n=1):
    k = 0
    for w in WORDS:
        if norm(w['w']) == norm(word):
            k += 1
            if k == n: return w['s']
    raise SystemExit(f'word not found: {word} #{n}')
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
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=50, sc=1.0):
    if sc <= 0.02: return
    xy = (min(max(xy[0], 40 + len(txt) * size * 0.3), W - 40 - len(txt) * size * 0.3), xy[1])
    f = F('SemiBold', int(size)); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 50), int(size * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width - 1, im.height - 1], fill=bg + (255,)); d.rectangle([0, im.height - 6, im.width - 1, im.height - 1], fill=tuple(int(v * 0.7) for v in bg) + (255,))
    d.text((im.width / 2, im.height / 2 - 1), txt, font=f, fill=fg, anchor='mm'); paste(img, im, xy[0], xy[1], sc)
def stext(img, xy, txt, f, fill=(255, 255, 255), a=1.0):
    if a <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, int(200 * a)), anchor='mm'); lay = lay.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(lay).text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor='mm'); img.alpha_composite(lay)
# ---------- places & routes ----------
LANDP = G.land_polys()
BOSTON_RED = unary_union([p.intersection(Point(-71.062, 42.357).buffer(0.012)) for p in LANDP if p.intersects(Point(-71.062, 42.357).buffer(0.02))])
CHARLES = [(-71.072, 42.362), (-71.09, 42.355), (-71.115, 42.362), (-71.14, 42.37), (-71.18, 42.364), (-71.215, 42.368), (-71.245, 42.372)]
MYSTIC = [(-71.06, 42.383), (-71.08, 42.394), (-71.105, 42.41), (-71.125, 42.425)]
ST = {f['properties']['name']: shape(f['geometry']) for f in json.load(open(f'{R}/work/states.geojson'))['features'] if f['properties'].get('admin') == 'United States of America'}
COLONIES = unary_union([ST[n] for n in ['New Hampshire', 'Massachusetts', 'Maine', 'Rhode Island', 'Connecticut', 'New York', 'New Jersey', 'Pennsylvania', 'Delaware', 'Maryland', 'Virginia', 'North Carolina', 'South Carolina', 'Georgia']])
MASS = unary_union([ST['Massachusetts']])
def town(lo, la, r):
    b = Point(lo, la).buffer(r); return unary_union([p.intersection(b) for p in LANDP if p.intersects(b)])
TOWNS = {'Boston': town(-71.062, 42.357, 0.012), 'Charlestown': town(-71.062, 42.377, 0.008), 'Lexington': town(-71.2265, 42.4473, 0.022), 'Concord': town(-71.349, 42.4604, 0.022)}
PL = {'Boston': (-71.058, 42.358), 'Old North Church': (-71.0545, 42.3663), 'Charlestown': (-71.063, 42.377), 'Lexington': (-71.2265, 42.4473), 'Concord': (-71.349, 42.4604)}
REVERE = [(-71.0545, 42.3663), (-71.063, 42.377), (-71.09, 42.397), (-71.11, 42.418), (-71.156, 42.415), (-71.20, 42.44), (-71.2265, 42.4473)]
DAWES = [(-71.058, 42.356), (-71.075, 42.345), (-71.083, 42.333), (-71.12, 42.336), (-71.135, 42.36), (-71.118, 42.376), (-71.15, 42.405), (-71.2265, 42.4473)]
TOCON = [(-71.2265, 42.4473), (-71.26, 42.445), (-71.30, 42.437)]
PRESC = [(-71.30, 42.437), (-71.32, 42.445), (-71.349, 42.4604)]
BRIT = [(-71.2265, 42.4473), (-71.30, 42.437), (-71.349, 42.4604)]
def proj(cam, pts):
    lo = np.array([p[0] for p in pts]); la = np.array([p[1] for p in pts]); x, y, ok = cam.project(lo, la, W, H); return list(zip(x, y)), ok
def geo(cam, lo, la): P, ok = proj(cam, [(lo, la)]); return P[0]
def cpoly(c, cam, g, fill, alpha, lw=4):
    gs = list(g.geoms) if hasattr(g, 'geoms') else [g]; c.new_path()
    for p in gs:
        if p.geom_type != 'Polygon': continue
        pts, ok = proj(cam, list(p.exterior.coords))
        if not ok.all(): continue
        [(c.move_to if i == 0 else c.line_to)(x, y) for i, (x, y) in enumerate(pts)]; c.close_path()
    c.set_source_rgba(*fill, alpha); c.fill_preserve(); c.set_source_rgba(1, 1, 1, min(1, alpha * 1.6)); c.set_line_width(lw); c.stroke()
def cline(c, cam, pts, col, lw, frac=1.0, dash=None):
    P, ok = proj(cam, pts)
    if not ok.all(): return
    if frac < 1:
        L = [0]
        for (x0, y0), (x1, y1) in zip(P, P[1:]): L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
        tg = L[-1] * clamp(frac); Q = [P[0]]
        for i in range(1, len(P)):
            if L[i] <= tg: Q.append(P[i])
            else: k = (tg - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); Q.append((P[i - 1][0] + (P[i][0] - P[i - 1][0]) * k, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * k)); break
        P = Q
    if len(P) < 2: return
    c.new_path(); c.move_to(*P[0]); [c.line_to(*p) for p in P[1:]]
    if dash: c.set_dash(dash)
    c.set_source_rgba(*col, 0.95); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke(); c.set_dash([])
def along(cam, pts, k):
    P, _ = proj(cam, pts); L = [0]
    for (x0, y0), (x1, y1) in zip(P, P[1:]): L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
    tg = L[-1] * clamp(k)
    for i in range(1, len(P)):
        if L[i] >= tg: kk = (tg - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); return P[i - 1][0] + (P[i][0] - P[i - 1][0]) * kk, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * kk
    return P[-1]
REVC, DAWC, PREC = ((0.45, 0.28, 0.16), (0.5, 0.32, 0.18)), ((0.42, 0.44, 0.5), (0.85, 0.82, 0.78)), ((0.2, 0.35, 0.3), (0.25, 0.18, 0.12))
def horse(img, key, cols, x, y, t, sc=1.0, red=False, rot=0, flip=False):
    ph = int(t * 10) % 4; im = art(f'{key}{ph}', lambda: T4.rider(cols[0], cols[1], 260, red=red, phase=ph * 1.57))
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    paste(img, im, x, y - 70 + 6 * math.sin(t * 20), sc, rot)
# ---------- camera (Point Roberts pacing) ----------
def keys():
    return [(0.0, Cm(-74.5, 39.5, 2600, 22, -4)), (T('Only') - 0.2, Cm(-72.5, 41.5, 1500, 28, -6)), (T('never') + 0.4, Cm(-71.6, 42.3, 420, 34, -8)),
            (T('April') + 0.1, Cm(-71.07, 42.36, 34, 42, -12)), (T('secret') - 0.2, Cm(-71.07, 42.36, 30, 44, -14)),
            (T('Concord') + 0.6, Cm(-71.2, 42.40, 95, 38, -8)), (T('Gentlemen') + 0.0, Cm(-71.2, 42.40, 92, 38, -8)),
            (T('signal') + 0.0, Cm(-71.058, 42.366, 12, 48, -6)), (T('boat') + 0.4, Cm(-71.065, 42.367, 15, 46, -8)),
            (T('gallops') + 0.2, Cm(-71.10, 42.39, 34, 44, -18)), (T('British', 5) + 0.3, Cm(-71.13, 42.405, 38, 44, -22)),
            (T('Regulars') + 0.6, Cm(-71.15, 42.41, 42, 44, -24)), (T('Dawes') + 0.2, Cm(-71.12, 42.37, 46, 42, -10)),
            (T('night', 3) + 0.4, Cm(-71.16, 42.39, 55, 40, -14)), (T('Lexington') + 0.2, Cm(-71.23, 42.44, 30, 46, -20)),
            (T('Concord', 2) + 0.4, Cm(-71.27, 42.443, 30, 46, -18)), (T('Halt') - 0.1, Cm(-71.29, 42.44, 24, 48, -18)),
            (T('horse', 2) + 0.4, Cm(-71.30, 42.437, 25, 48, -22)), (T('Prescott') + 0.3, Cm(-71.32, 42.447, 28, 46, -22)),
            (T('dawn') - 0.1, Cm(-71.2265, 42.445, 26, 48, -14)), (T('Revolution') + 0.5, Cm(-71.2, 42.41, 80, 38, -10)),
            (T('Eighty-five') + 0.1, Cm(-71.2, 42.41, 90, 36, -6)), (END, Cm(-71.2, 42.41, 120, 34, -4))]
KEYS = keys()
def cam_at(t):
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t < t1: return a.lerp(b, ease((t - t0) / (t1 - t0)))
    return KEYS[-1][1]
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15: stext(img, (W // 2, 1790), ' '.join(x['w'] for x in g), F('SemiBold', 44)); break
def frame(t):
    cam = cam_at(t)
    shake = 0
    if T('Halt') - 0.05 <= t < T('Halt') + 0.5: shake = 14 * math.sin(t * 90) * (1 - (t - T('Halt')) / 0.55)
    if T('shots') - 0.05 <= t < T('shots') + 0.6: shake = 18 * math.sin(t * 80) * (1 - (t - T('shots')) / 0.65)
    img = G.render(cam, W, H).filter(ImageFilter.UnsharpMask(radius=1.4, percent=50, threshold=2)).convert('RGBA')
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    wide = cam.dist > 300
    if wide:
        cpoly(c, cam, COLONIES, (0.2, 0.42, 0.95), 0.42, lw=3)
        if t >= T('Only') - 0.3: cpoly(c, cam, MASS, (0.2, 0.42, 0.95), 0.35 + 0.25 * eout((t - T('Only') + 0.3) / 0.5), lw=4)
    def tw(name, col, a):
        if a > 0.01: cpoly(c, cam, TOWNS[name], col, a, lw=5)
    if not wide:
        tw('Boston', (0.86, 0.15, 0.2), 0.62)
        if t >= T('Concord') - 0.2: tw('Concord', (0.2, 0.42, 0.95), 0.6 * eout((t - T('Concord') + 0.2) / 0.4))
        if t >= T('Lexington') - 0.3: tw('Lexington', (0.2, 0.42, 0.95), 0.6 * eout((t - T('Lexington') + 0.3) / 0.4))
        if T('boat') - 0.5 <= t < T('Dawes'): tw('Charlestown', (0.95, 0.75, 0.2), 0.55)
    for rv in (CHARLES, MYSTIC):
        cline(c, cam, rv, (0.95, 0.97, 1.0), 16); cline(c, cam, rv, (0.2, 0.5, 0.65), 10)
    if T('march') <= t < T('Gentlemen') + 1.5: cline(c, cam, [PL['Boston'], (-71.15, 42.41), PL['Concord']], (0.9, 0.15, 0.2), 9, frac=eout((t - T('march')) / 1.2), dash=[24, 14])
    if T('gallops') - 0.5 <= t < T('Lexington') + 2: cline(c, cam, REVERE, (1, 0.85, 0.2), 7, eout((t - T('gallops') + 0.5) / (T('Regulars') + 1.2 - T('gallops'))), [3, 14])
    if T('Dawes') - 0.2 <= t < T('Lexington') + 2: cline(c, cam, DAWES, (0.85, 0.88, 0.98), 7, eout((t - T('Dawes') + 0.2) / (T('night', 3) + 1.0 - T('Dawes'))), [3, 14])
    if T('Lexington') + 0.5 <= t < T('dawn'): cline(c, cam, TOCON, (1, 0.85, 0.2), 7, eout((t - T('Lexington') - 0.5) / (T('Halt') - T('Lexington') - 0.5)), [3, 14])
    if T('Prescott') - 0.1 <= t < T('dawn'):
        cline(c, cam, PRESC, (0.4, 0.9, 0.6), 7, eout((t - T('Prescott')) / 2.4), [3, 14])
        cline(c, cam, [(-71.311, 42.433), (-71.309, 42.446)], (0.55, 0.55, 0.58), 10)   # stone wall
    img.alpha_composite(TO._pil(s))
    # ---------- stickers ----------
    if t < T('April') - 0.1:
        stext(img, (W // 2, 270), 'Just imagine...', F('play', 92), a=eout(t / 0.3) * clamp((T('Only') - t) / 0.3))
        if t < T('Only') + 0.2:
            x, y = geo(cam, -73.5, 40.6); pill(img, (x, y), '13 Colonies', (40, 90, 220), size=52, sc=pop(t, 0.6))
        else:
            x, y = geo(cam, -71.9, 42.35); pill(img, (x, y - 40), 'Massachusetts', (40, 90, 220), size=48, sc=pop(t, T('Only') + 0.1))
        for i, (cols, nm, t0) in enumerate(((REVC, 'r', 0.5), (DAWC, 'd', 0.9), (PREC, 'p', 1.3))):
            x = 190 + i * 350; y = 1330
            horse(img, nm, cols, x, y, t, 1.0)
            if t >= T('legend') - 0.2 and i == 0: pill(img, (x, y - 250), 'LEGEND', (240, 175, 20), (20, 20, 20), 50, pop(t, T('legend') - 0.2))
            if t >= T('two') - 0.2 and i > 0: pill(img, (x, y - 250), '???', (30, 30, 34), size=50, sc=pop(t, T('two') - 0.2 + 0.2 * i))
        if t >= T('never'): stext(img, (W // 2, 270), 'Never heard of them?', F('play', 80), a=eout((t - T('never')) / 0.25))
    if T('April') - 0.1 <= t < T('signal'):
        if t < T('Boston'): stext(img, (W // 2, 270), 'April 18, 1775', F('play', 100), a=eout((t - T('April') + 0.1) / 0.3))
        x, y = geo(cam, *PL['Boston'])
        if T('Boston') <= t < T('march'): pill(img, (x, y - 140), 'Boston', (200, 35, 45), size=58, sc=pop(t, T('Boston')))
        if T('soldiers') <= t < T('march'):
            for i in range(4): paste(img, art('rc', lambda: T3.officer('smug', 170)), 130 + i * 170, 1330 + (i % 2) * 40, pop(t, T('soldiers') + i * 0.1))
        if T('locals') <= t < T('march'): paste(img, art('loc', lambda: T4.colonial('dawes', 'worried', 260)), 900, 1350, pop(t, T('locals'))); pill(img, (880, 1110), 'not thrilled', (30, 30, 34), size=40, sc=pop(t, T('thrilled')))
        if T('march') <= t:
            x2, y2 = geo(cam, *PL['Concord']); pill(img, (x2, y2 - 80), 'Concord', (40, 90, 220), size=52, sc=pop(t, T('Concord')))
            if t >= T('weapons') - 0.1: pill(img, (x2, y2 + 60), 'rebel weapons', (30, 30, 34), size=38, sc=pop(t, T('weapons')))
            if t < T('Gentlemen'): stext(img, (W // 2, 270), 'SECRET MISSION', F('oswald', 96), fill=(255, 90, 90), a=eout((t - T('secret')) / 0.25))
        if T('Gentlemen') - 0.1 <= t:
            paste(img, art('gen', lambda: T3.officer('smug', 380)), 300, 1300, pop(t, T('Gentlemen') - 0.1))
            paste(img, art('bg', lambda: TO.bubble('This is\ntop secret.', 54)), 360, 900, pop(t, T('Gentlemen')))
            if t >= T('Everyone') - 0.1:
                n = 1 + int((t - T('Everyone') + 0.1) / 0.45)
                ch = art(f'chat{min(n,4)}', lambda: T4.chat([('Redcoat_77', (0.95, 0.3, 0.3), 'shh its a secret'), ('Boston_Baker', (0.4, 0.7, 1), 'we know lol'), ('Tavern_Guy', (0.4, 0.7, 1), 'its Concord right?'), ('Redcoat_77', (0.95, 0.3, 0.3), '...who told u')], 760, min(n, 4)))
                paste(img, ch, W // 2, 560, 1.0)
    if T('signal') <= t < T('gallops'):
        x, y = geo(cam, *PL['Old North Church']); lit = 0 if t < T('One', 2) else (1 if t < T('two', 2) else 2)
        paste(img, art(f'church{lit}', lambda: T4.church(300, lit)), x, y - 200, pop(t, T('signal')))
        pill(img, (x, y + 80), 'Old North Church', (30, 30, 34), size=44, sc=pop(t, T('Old')))
        if T('One', 2) <= t < T('Two', 3): pill(img, (W // 2, 300), '1 = by land   2 = by sea', (240, 175, 20), (20, 20, 20), 48, pop(t, T('One', 2)))
        if t >= T('Two', 3): stext(img, (W // 2, 300), 'Two lanterns!', F('play', 96), fill=(255, 220, 90), a=eout((t - T('Two', 3)) / 0.25))
        if t >= T('boat') - 0.4:
            for i in range(3):
                k = eout((t - T('boat') + 0.4 - i * 0.2) / 2.0); xa, ya = geo(cam, -71.066 - 0.004 * i, 42.357 + 0.013 * k); paste(img, art('boat', lambda: T3.ship(150, flag=(0.85, 0.1, 0.15))), xa, ya, 1.0)
    if T('gallops') - 0.5 <= t < T('Dawes') + 0.5:
        k = eout((t - T('gallops') + 0.5) / (T('Regulars') + 1.2 - T('gallops'))); x, y = along(cam, REVERE, k); horse(img, 'r', REVC, x, y, t, 1.0)
        if t < T('silversmith') + 1.2: pill(img, (x, y - 220), 'Paul Revere', (240, 175, 20), (20, 20, 20), 48, pop(t, T('Paul')))
        if T('never', 2) - 0.1 <= t < T('Regulars') - 0.3:
            stext(img, (W // 2, 300), '"The British are coming!"', F('play', 70), a=eout((t - T('never', 2)) / 0.25))
            if t >= T('Everyone', 2):
                d = ImageDraw.Draw(img); d.line([(120, 300), (960, 300)], fill=(230, 40, 50, 255), width=12); pill(img, (W // 2, 420), 'Everyone was British', (200, 35, 45), size=46, sc=pop(t, T('Everyone', 2)))
        if t >= T('Regulars') - 0.3:
            paste(img, art('rev', lambda: T4.colonial('revere', 'laugh', 360)), 280, 1330, pop(t, T('Regulars') - 0.3))
            paste(img, art('breg', lambda: TO.bubble('The Regulars are\ncoming out!', 50)), 400, 920, pop(t, T('Regulars') - 0.2))
    if T('Dawes') - 0.2 <= t < T('Lexington') + 1.0:
        k = eout((t - T('Dawes') + 0.2) / (T('night', 3) + 1.0 - T('Dawes'))); x, y = along(cam, DAWES, k); horse(img, 'd', DAWC, x, y, t, 1.0)
        pill(img, (x, y - 220), 'William Dawes', (120, 130, 150), size=44, sc=pop(t, T('William')))
        if T('long') <= t < T('Same'): pill(img, (W // 2, 300), 'the long way around', (30, 30, 34), size=46, sc=pop(t, T('long')))
        if t >= T('Same'): stext(img, (W // 2, 300), 'Same night.', F('play', 90), a=eout((t - T('Same')) / 0.25))
    if T('Lexington') <= t < T('dawn'):
        x, y = geo(cam, *PL['Lexington']); pill(img, (x, y + 90), 'Lexington', (40, 90, 220), size=50, sc=pop(t, T('Lexington')))
        if T('Adams') <= t < T('Halt'):
            paste(img, art('adams', lambda: T4.colonial('prescott', 'shock', 260)), 260, 1380, pop(t, T('Adams'))); pill(img, (260, 1170), 'Samuel Adams', (30, 30, 34), size=34, sc=pop(t, T('Adams')))
            paste(img, art('hanc', lambda: T4.colonial('revere', 'shock', 260)), 820, 1380, pop(t, T('Hancock'))); pill(img, (820, 1170), 'John Hancock', (30, 30, 34), size=34, sc=pop(t, T('Hancock')))
        k = eout((t - T('Lexington') - 0.5) / (T('Halt') - T('Lexington') - 0.5))
        caught = t >= T('caught') - 0.1
        if t >= T('patrol') - 0.3:
            xpp, _ = geo(cam, -71.305, 42.437); k = min(k, 1.0)
        x1, y1 = along(cam, TOCON, k); x2, y2 = along(cam, TOCON, max(0, k - 0.45)); x2 -= 120; y2 += 150
        if t >= T('patrol') - 0.3: x1 = min(x1, xpp + 220 - 230)
        if t < T('Prescott'):
            horse(img, 'r', REVC, x1, y1, t if not caught else 0, 1.0)
            fall = t >= T('falls') - 0.1
            if not fall: horse(img, 'd', DAWC, x2, y2, t, 0.9)
            else:
                ang = -min(110, (t - T('falls') + 0.1) * 360); horse(img, 'd', DAWC, x2 - (t - T('falls')) * 120, y2, 0, 0.9, rot=ang)
                pill(img, (x2, y2 - 190), 'OOF.', (30, 30, 34), size=50, sc=pop(t, T('falls')))
        if t >= T('patrol') - 0.3:
            xp, yp = geo(cam, -71.305, 42.437); xp += 220; horse(img, 'b', ((0.82, 0.12, 0.12), (0.2, 0.15, 0.12)), xp, yp - 60, t, 1.0, red=True, flip=True)
        if T('Halt') - 0.05 <= t < T('Revere', 2) + 0.4: stext(img, (W // 2, 520), 'HALT!', F('oswald', 190), fill=(255, 70, 70), a=1)
        if caught and t < T('Prescott'): pill(img, (x1, y1 - 210), 'CAUGHT', (200, 35, 45), size=50, sc=pop(t, T('caught') - 0.1))
        if t >= T('Prescott') - 0.1:
            k3 = eout((t - T('Prescott')) / 2.4); x3, y3 = along(cam, PRESC, k3); jump = 120 * math.sin(math.pi * clamp((k3 - 0.25) / 0.3)) if 0.25 < k3 < 0.55 else 0
            horse(img, 'p', PREC, x3, y3 - jump, t, 1.0); pill(img, (x3, y3 - 230 - jump), 'Samuel Prescott', (40, 140, 80), size=42, sc=pop(t, T('Prescott')))
            x4, y4 = geo(cam, *PL['Concord']); pill(img, (x4, y4 + 90), 'Concord', (40, 90, 220), size=50, sc=pop(t, T('makes') - 0.2))
    if T('dawn') <= t < T('Eighty-five'):
        if T('shots') - 0.05 <= t < T('shots') + 0.25: img.alpha_composite(Image.new('RGBA', (W, H), (255, 240, 200, int(200 * (1 - (t - T('shots')) / 0.3)))))
        x, y = geo(cam, *PL['Lexington']); pill(img, (x, y + 90), 'Lexington', (40, 90, 220), size=50)
        stext(img, (W // 2, 280), 'April 19, 1775', F('play', 90), a=eout((t - T('dawn')) / 0.3))
        if t >= T('American') - 0.1: stext(img, (W // 2, 420), 'The Revolution begins', F('play', 72), fill=(255, 220, 90), a=eout((t - T('American') + 0.1) / 0.3))
    if t >= T('Eighty-five'):
        img.alpha_composite(Image.new('RGBA', (W, H), (10, 20, 35, int(110 * eout((t - T('Eighty-five')) / 0.5)))))
        if t < T('legend', 2) - 0.2:
            stext(img, (W // 2, 300), '1860', F('play', 120), a=eout((t - T('Eighty-five')) / 0.3))
            paste(img, art('book', lambda: T4.book(560)), W // 2, 900, pop(t, T('poet') - 0.1))
            if t >= T('left'): pill(img, (W // 2, 1250), 'left the other two out', (200, 35, 45), size=46, sc=pop(t, T('left')))
        else:
            paste(img, art('revL', lambda: T4.colonial('revere', 'laugh', 380)), 290, 1150, pop(t, T('legend', 2) - 0.2)); pill(img, (290, 1450), 'LEGEND', (240, 175, 20), (20, 20, 20), 54, pop(t, T('legend', 2)))
            if t >= T('Dawes', 3) - 0.1: paste(img, art('dawW', lambda: T4.colonial('dawes', 'worried', 380)), 790, 1150, pop(t, T('Dawes', 3) - 0.1))
            if t >= T('trivia') - 0.1: pill(img, (790, 1450), 'TRIVIA QUESTION', (120, 130, 150), size=46, sc=pop(t, T('trivia') - 0.1))
    subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 10, int(W * t / END), H], fill=(240, 175, 20, 255))
    img = img.convert('RGB')
    if shake: img = img.transform(img.size, Image.AFFINE, (1, 0, shake, 0, 1, shake * 0.5), resample=Image.BILINEAR)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): frame(tt).resize((360, 640)).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(round(a * FPS)), int(round(min(b, END) * FPS))):
            enc.stdin.write(np.asarray(frame(fi / FPS)).tobytes())
            if fi % 300 == 0: print(f'{fi / FPS:.1f}s', flush=True)
        enc.stdin.close(); enc.wait()
