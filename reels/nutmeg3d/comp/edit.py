"""Manhattan-for-nutmeg, remade in the Point Roberts look on a self-drawn 3D globe. usage: python3 edit.py OUT.mp4 [t0 t1] | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import shape, box, Polygon
from shapely.ops import unary_union
import globe3d as G, toons as TO, toons3 as T3
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
def paste(img, im, cx, cy, sc=1.0, rot=0):
    if sc <= 0.01: return
    i = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if rot: i = i.rotate(rot, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(i, (int(cx - i.width / 2), int(cy - i.height / 2)))
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=50, sc=1.0):
    if sc <= 0.02: return
    f = F('SemiBold', int(size)); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 50), int(size * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, im.width - 1, im.height - 1], fill=bg + (255,)); d.rectangle([0, im.height - 6, im.width - 1, im.height - 1], fill=tuple(int(v * 0.7) for v in bg) + (255,))
    d.text((im.width / 2, im.height / 2 - 1), txt, font=f, fill=fg, anchor='mm'); paste(img, im, xy[0], xy[1], sc)
def stext(img, xy, txt, f, fill=(255, 255, 255), a=1.0):
    if a <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, int(200 * a)), anchor='mm'); lay = lay.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(lay).text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor='mm'); img.alpha_composite(lay)
# ---------- geography ----------
LANDP = G.land_polys()
MANH = [p for p in LANDP if abs(p.bounds[0] + 74.017) < 0.01 and abs(p.bounds[3] - 40.878) < 0.01][0]
C50 = {f['properties']['ADMIN']: shape(f['geometry']) for f in json.load(open(f'{R}/dl/c50.geojson'))['features']}
NL, UK = C50['Netherlands'], C50['United Kingdom']
def clip_land(poly): return unary_union([p.intersection(poly) for p in LANDP if p.intersects(poly)])
NEWNL = clip_land(Polygon([(-75.6, 39.0), (-74.9, 39.0), (-74.05, 40.5), (-73.65, 41.0), (-73.5, 42.2), (-73.3, 43.1), (-74.6, 43.1), (-75.6, 42.0)]))
BANDA = clip_land(box(129.84, -4.60, 130.0, -4.45)); AI = clip_land(box(129.74, -4.55, 129.80, -4.50)); RUN = G.RUN_ISLAND
ORANGE, RED, BLUE = (0.96, 0.52, 0.1), (0.86, 0.15, 0.2), (0.2, 0.42, 0.95)
def proj(cam, pts):
    lo = np.array([p[0] for p in pts]); la = np.array([p[1] for p in pts]); x, y, ok = cam.project(lo, la, W, H); return list(zip(x, y)), ok
def geo(cam, lo, la): P, ok = proj(cam, [(lo, la)]); return P[0]
def cpoly(c, cam, g, fill, alpha, stroke=(1, 1, 1), lw=4):
    if alpha <= 0.01: return
    gs = list(g.geoms) if hasattr(g, 'geoms') else [g]; c.new_path()
    for p in gs:
        if p.geom_type != 'Polygon': continue
        pts, ok = proj(cam, list(p.exterior.coords))
        if not ok.all(): continue
        for i, (x, y) in enumerate(pts): (c.move_to if i == 0 else c.line_to)(x, y)
        c.close_path()
    c.set_source_rgba(*fill, alpha); c.fill_preserve(); c.set_source_rgba(*stroke, min(1, alpha * 1.6)); c.set_line_width(lw); c.stroke()
def cline(c, cam, pts, col, lw, frac=1.0, dash=None):
    P, ok = proj(cam, pts)
    if frac < 1:
        L = [0]
        for (x0, y0), (x1, y1) in zip(P, P[1:]): L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
        tg = L[-1] * frac; Q = [P[0]]
        for i in range(1, len(P)):
            if L[i] <= tg: Q.append(P[i])
            else: k = (tg - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); Q.append((P[i - 1][0] + (P[i][0] - P[i - 1][0]) * k, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * k)); break
        P = Q
    if len(P) < 2: return
    c.new_path(); c.move_to(*P[0])
    for p in P[1:]: c.line_to(*p)
    if dash: c.set_dash(dash)
    c.set_source_rgba(*col, 0.95); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke(); c.set_dash([])
def along(cam, pts, k):
    P, _ = proj(cam, pts); L = [0]
    for (x0, y0), (x1, y1) in zip(P, P[1:]): L.append(L[-1] + math.hypot(x1 - x0, y1 - y0))
    tg = L[-1] * clamp(k)
    for i in range(1, len(P)):
        if L[i] >= tg: kk = (tg - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); return P[i - 1][0] + (P[i][0] - P[i - 1][0]) * kk, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * kk
    return P[-1]
SEA_ROUTE = [(4.3, 52.0), (-6, 47), (-15, 30), (-20, 10), (-5, -5), (8, -25), (18.5, -35.5), (35, -36), (55, -25), (75, -15), (95, -9), (112, -9.5), (122, -7), (129.85, -4.6)]
# ---------- camera keys (Point Roberts pacing: smooth moves across each sentence) ----------
def keys():
    return [(0.0, Cm(-73.98, 40.76, 60, 42, -28)), (T('kept') - 0.3, Cm(-73.98, 40.77, 46, 46, -30)),
            (T('tiny') + 0.6, Cm(129.693, -4.555, 16, 48, 0)), (T('joke') + 0.4, Cm(129.693, -4.555, 13, 50, 4)),
            (T('looked') + 0.2, Cm(129.70, -4.555, 24, 46, 6)), (T('rewind') - 0.2, Cm(129.70, -4.555, 28, 44, 8)),
            (T('1600s') + 0.2, Cm(5, 50, 2300, 30, -4)), (T('nutmeg') + 0.6, Cm(7, 49, 2000, 34, -2)),
            (T('sailors') + 0.3, Cm(10, 15, 9500, 18, 0)), (T('planet') + 0.6, Cm(70, -12, 9500, 18, 0)),
            (T('only') + 0.1, Cm(124, -4, 2600, 30, 0)), (T('Banda') + 0.4, Cm(129.85, -4.53, 90, 40, -6)), (T('Indonesia') + 0.6, Cm(129.84, -4.53, 70, 44, -10)),
            (T('except') + 0.2, Cm(129.75, -4.55, 40, 46, -4)), (T('first') + 0.4, Cm(129.71, -4.552, 22, 50, 6)),
            (T('other') + 0.5, Cm(-74.0, 40.72, 420, 36, -10)), (T('Amsterdam') + 0.3, Cm(-74.0, 40.71, 120, 42, -18)),
            (T('1664') + 0.2, Cm(-74.02, 40.63, 70, 46, -14)), (T('warships') + 1.0, Cm(-74.01, 40.66, 60, 48, -16)),
            (T('Stuyvesant') + 0.2, Cm(-73.99, 40.72, 40, 50, -24)), (T('renamed') + 0.2, Cm(-73.98, 40.76, 48, 46, -28)), (T('Duke') + 0.4, Cm(-73.98, 40.77, 56, 44, -30)),
            (T('three') + 0.5, Cm(40, 20, 15000, 6, 0)), (T('Dutch', 6) + 0.3, Cm(50, 15, 15500, 6, 4)),
            (T('Fast') + 0.4, Cm(78, 2, 14000, 8, 0)), (T('Manhattan', 3) + 0.3, Cm(-73.98, 40.76, 55, 44, -28)),
            (T('sprinkle') + 0.2, Cm(-73.98, 40.76, 50, 46, -30)), (END, Cm(-73.98, 40.76, 120, 36, -36))]
KEYS = keys()
def cam_at(t):
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t < t1:
            u = (t - t0) / (t1 - t0); k = ease(u); c = a.lerp(b, k)
            far = math.hypot(a.lon - b.lon, a.lat - b.lat) > 20
            if far:   # long flight: rise to see the globe, travel, come down
                top = max(9000, a.dist, b.dist); c.dist = math.exp(math.log(c.dist) + (math.log(top) - math.log(c.dist)) * math.sin(math.pi * k) ** 0.7)
                c.pitch = c.pitch * (1 - 0.8 * math.sin(math.pi * k))
            elif max(a.dist, b.dist) / min(a.dist, b.dist) > 8:   # big zoom: centre first, then descend
                kp = 1 - (1 - clamp(u * 1.15)) ** 4; c.lon = a.lon + (b.lon - a.lon) * kp; c.lat = a.lat + (b.lat - a.lat) * kp
            return c
    return KEYS[-1][1]
# ---------- subtitles ----------
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15: stext(img, (W // 2, 1600), ' '.join(x['w'] for x in g), F('SemiBold', 44)); break
def _inset(cm_, g_, col, S=440):
    im = G.render(cm_, 540, 960).convert('RGBA'); s = cairo.ImageSurface(cairo.FORMAT_ARGB32, 540, 960); c = cairo.Context(s)
    gs = list(g_.geoms) if hasattr(g_, 'geoms') else [g_]
    for p in gs:
        lo = np.array([q[0] for q in p.exterior.coords]); la = np.array([q[1] for q in p.exterior.coords]); x, y, ok = cm_.project(lo, la, 540, 960)
        c.new_path(); [(c.move_to if i == 0 else c.line_to)(a, b) for i, (a, b) in enumerate(zip(x, y))]; c.close_path()
        c.set_source_rgba(*col, 0.6); c.fill_preserve(); c.set_source_rgb(1, 1, 1); c.set_line_width(4); c.stroke()
    im.alpha_composite(TO._pil(s)); im = im.crop((50, 260, 490, 700)).resize((S, S))
    m = Image.new('L', (S, S), 0); ImageDraw.Draw(m).ellipse([0, 0, S - 1, S - 1], fill=255); im.putalpha(m)
    out = Image.new('RGBA', (S + 24, S + 24), (0, 0, 0, 0)); ImageDraw.Draw(out).ellipse([0, 0, S + 23, S + 23], fill=(255, 255, 255, 255)); out.alpha_composite(im, (12, 12)); return out
# ---------- frame ----------
def frame(t):
    cam = cam_at(t)
    img = G.render(cam, W, H).filter(ImageFilter.UnsharpMask(radius=1.4, percent=50, threshold=2)).convert('RGBA')
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    near_ny = cam.dist < 800 and abs(cam.lon + 74) < 3; near_banda = cam.dist < 400 and abs(cam.lon - 129.8) < 2
    if near_ny:
        dutch_era = t < T('renamed') + 0.6
        if T('Amsterdam') - 0.4 <= t < T('renamed') + 0.6: cpoly(c, cam, NEWNL, ORANGE, 0.28, lw=3)
        cpoly(c, cam, MANH, ORANGE if dutch_era else RED, 0.55 if t < T('Manhattan', 3) else 0.6, lw=5)
    if near_banda:
        if t >= T('grabbed'): cpoly(c, cam, BANDA, ORANGE, 0.55 * eout((t - T('grabbed')) / 0.5)); cpoly(c, cam, AI, ORANGE, 0.55 * eout((t - T('grabbed') - 0.3) / 0.5))
        run_col = ORANGE if t < T('Run') - 0.3 or t > T('other') else RED
        cpoly(c, cam, RUN, run_col, 0.6, lw=5)
    if T('1600s') - 0.2 <= t < T('sailors') + 0.6:
        cpoly(c, cam, NL, ORANGE, 0.6); cpoly(c, cam, UK, RED, 0.55)
    if T('sailors') <= t < T('only') + 0.3:
        cline(c, cam, SEA_ROUTE, (1, 0.85, 0.25), 7, frac=ease((t - T('sailors')) / (T('planet') + 0.6 - T('sailors'))), dash=[2, 16])
    img.alpha_composite(TO._pil(s))
    # ---------- stickers / labels ----------
    if t < T('kept') - 0.1:
        stext(img, (W // 2, 280), '1667', F('play', 140), a=eout(t / 0.3))
        x, y = geo(cam, -73.97, 40.775); pill(img, (x, y), 'Manhattan', (225, 120, 25), size=56, sc=pop(t, 0.3))
        paste(img, art('dutchH', lambda: T3.dutch('happy', 360)), 820, 1360, pop(t, T('Dutch')))
    if T('kept') - 0.1 <= t < T('1600s'):
        if t >= T('tiny') + 0.3:
            x, y = geo(cam, 129.693, -4.552); pill(img, (x, y - 150), 'Run Island', (225, 120, 25), size=56, sc=pop(t, T('tiny') + 0.3))
            pill(img, (x, y + 140), '~ 3 km long', (30, 30, 34), size=40, sc=pop(t, T('tiny') + 0.6))
        if t >= T('joke') - 0.1: stext(img, (W // 2, 280), "That's not a joke.", F('play', 80), a=eout((t - T('joke') + 0.1) / 0.3))
        if t >= T('looked'): paste(img, art('dutchL', lambda: T3.dutch('laugh', 360)), 280, 1380, pop(t, T('looked'))); pill(img, (280, 1640), 'Great deal!', (225, 120, 25), size=42, sc=pop(t, T('great')))
        if t >= T('rewind') - 0.05:
            a = clamp(1 - abs(t - (T('rewind') + 0.35)) / 0.5); d = ImageDraw.Draw(img)
            for i in range(10): yy = (i * 197 + int(t * 1900)) % H; d.rectangle([0, yy, W, yy + 5], fill=(255, 255, 255, int(110 * a)))
            stext(img, (W // 2 + 40, 960), 'REWIND', F('oswald', 96), a=a); d.polygon([(250, 960), (310, 920), (310, 1000)], fill=(255, 255, 255, int(255 * a))); d.polygon([(300, 960), (360, 920), (360, 1000)], fill=(255, 255, 255, int(255 * a)))
    if T('1600s') <= t < T('sailors'):
        stext(img, (W // 2, 280), 'The 1600s', F('play', 110), a=eout((t - T('1600s')) / 0.3))
        x, y = geo(cam, 5.5, 52.3); pill(img, (x + 60, y - 40), 'Dutch', (225, 120, 25), size=44, sc=pop(t, T('1600s') + 0.3))
        x, y = geo(cam, -1.5, 52.8); pill(img, (x - 60, y), 'English', (200, 35, 45), size=44, sc=pop(t, T('1600s') + 0.45))
        if t >= T('nutmeg') - 0.1:
            for i in range(9):
                t0 = T('nutmeg') - 0.1 + i * 0.07; fy = 420 + 900 * eout((t - t0) / 0.8)
                paste(img, art('nut', lambda: T3.nutmeg(130)), 120 + i * 105, min(fy, 1260 + (i % 3) * 60), pop(t, t0, 0.25), rot=(i * 47) % 360)
            pill(img, (W // 2, 420), 'NUTMEG', (120, 70, 35), size=60, sc=pop(t, T('nutmeg')))
        if t >= T('valuable'): pill(img, (W // 2, 540), 'worth a fortune', (30, 30, 34), size=40, sc=pop(t, T('valuable')))
    if T('sailors') <= t < T('only') + 0.3:
        k = ease((t - T('sailors')) / (T('planet') + 0.6 - T('sailors'))); x, y = along(cam, SEA_ROUTE, k)
        paste(img, art('shipNL', lambda: T3.ship(220)), x, y - 50, pop(t, T('sailors')))
        if t >= T('half'): pill(img, (W // 2, 330), 'Half the planet', (120, 70, 35), size=52, sc=pop(t, T('half')))
    if T('only') - 0.1 <= t < T('other'):
        if t < T('Banda') + 0.2: pill(img, (W // 2, 330), 'Only one place on Earth', (180, 40, 40), size=48, sc=pop(t, T('only')))
        if t >= T('Banda') - 0.1: x, y = geo(cam, 129.9, -4.53); pill(img, (x, y - 170), 'Banda Islands', (225, 120, 25), size=54, sc=pop(t, T('Banda') - 0.1))
        if t >= T('Indonesia'): pill(img, (W // 2, 330), "today's Indonesia", (30, 30, 34), size=46, sc=pop(t, T('Indonesia')))
        if t >= T('grabbed'): paste(img, art('dutchG', lambda: T3.dutch('happy', 320)), 250, 1380, pop(t, T('grabbed'))); pill(img, (250, 1620), 'Dutch', (225, 120, 25), size=42, sc=pop(t, T('grabbed') + 0.1))
        if t >= T('Run') - 0.3: x, y = geo(cam, 129.693, -4.552); pill(img, (x, y - 140), 'Run', (200, 35, 45), size=60, sc=pop(t, T('Run') - 0.3))
        if t >= T('English'): paste(img, art('off', lambda: T3.officer('smug', 320)), 830, 1380, pop(t, T('English'))); pill(img, (830, 1620), 'English', (200, 35, 45), size=42, sc=pop(t, T('English') + 0.1))
    if T('other') <= t < T('three') + 0.4:
        if T('Amsterdam') - 0.3 <= t < T('renamed'): x, y = geo(cam, -74.0, 40.715); pill(img, (x, y + 120), 'New Amsterdam', (225, 120, 25), size=54, sc=pop(t, T('Amsterdam') - 0.3))
        if T('Amsterdam') <= t < T('1664'): paste(img, art('dutchA', lambda: T3.dutch('happy', 320)), 820, 1380, pop(t, T('Amsterdam')))
        if T('1664') <= t < T('Stuyvesant'): stext(img, (W // 2, 280), '1664', F('play', 130), a=eout((t - T('1664')) / 0.3))
        if T('warships') - 0.2 <= t < T('Stuyvesant') + 0.2:
            for i in range(3):
                k = eout((t - T('warships') + 0.2 - i * 0.2) / 1.6); x, y = geo(cam, -73.95 + 0.06 * i, 40.52 + 0.04 * i); paste(img, art('shipEN', lambda: T3.ship(210, flag=(0.85, 0.1, 0.15))), x - 300 * (1 - k), y, 1.0)
        if T('Stuyvesant') - 0.1 <= t < T('renamed'):
            paste(img, art('stuy', lambda: T3.stuyvesant('worried', 380)), 300, 1230, pop(t, T('Stuyvesant') - 0.1))
            pill(img, (300, 1660), 'Peter Stuyvesant', (30, 30, 34), size=40, sc=pop(t, T('Stuyvesant')))
            if t >= T('peg'): pill(img, (430, 1520), 'peg leg!', (120, 70, 35), size=36, sc=pop(t, T('peg')))
            if t >= T('surrendered'): paste(img, art('flag', lambda: T3.whiteflag(200)), 560, 1050, pop(t, T('surrendered'))); pill(img, (W // 2, 330), 'No fight', (40, 140, 80), size=54, sc=pop(t, T('without')))
        if t >= T('renamed'):
            x, y = geo(cam, -73.97, 40.775)
            if t < T('York'): pill(img, (x, y), 'New Amsterdam', (225, 120, 25), size=56)
            else: pill(img, (x, y), 'New York', (200, 35, 45), size=64, sc=pop(t, T('York')))
            if t >= T("king's"): paste(img, art('king', lambda: T3.charles('happy', 330)), 250, 1380, pop(t, T("king's"))); pill(img, (250, 1640), 'King Charles II', (200, 35, 45), size=36, sc=pop(t, T("king's") + 0.1))
            if t >= T('Duke'): paste(img, art('duke', lambda: T3.officer('happy', 300)), 830, 1400, pop(t, T('Duke'))); pill(img, (830, 1640), 'Duke of York', (200, 35, 45), size=36, sc=pop(t, T('Duke') + 0.1))
    if T('three') <= t < T('Fast'):
        if t < T('keep', 1) - 0.2:
            paste(img, art('scroll', lambda: T3.scroll(330)), W // 2, 900, pop(t, T('peace') - 0.1))
            if t >= T('everybody'): pill(img, (W // 2, 330), 'Everybody keeps what they have', (30, 30, 34), size=42, sc=pop(t, T('everybody')))
        else:
            for side, (cm_, g_, col, lab, t0) in enumerate(((Cm(129.693, -4.555, 18, 40, 0), RUN, ORANGE, 'Run', T('keep', 1)), (Cm(-73.98, 40.775, 50, 40, -28), MANH, RED, 'Manhattan', T('keep', 2)))):
                if t < t0 - 0.25: continue
                inset = art(f'inset{side}', lambda: _inset(cm_, g_, col))
                sc = pop(t, t0 - 0.25, 0.4); cx_ = 280 + side * 520; paste(img, inset, cx_, 760, sc)
                pill(img, (cx_, 1010), lab, (225, 120, 25) if side == 0 else (200, 35, 45), size=52, sc=sc)
            if t >= T('keep', 1) - 0.2: paste(img, art('dutchL2', lambda: T3.dutch('laugh', 330)), 270, 1420, pop(t, T('keep', 1)))
            if t >= T('keep', 2) - 0.2: paste(img, art('kingH', lambda: T3.charles('happy', 330)), 820, 1420, pop(t, T('keep', 2)))
            if t >= T('Dutch', 6): paste(img, art('b1', lambda: TO.bubble('Nutmeg\nforever!', 52)), 330, 1130, pop(t, T('Dutch', 6) + 0.15))
            if t >= T('English', 5): paste(img, art('b2', lambda: TO.bubble('Enjoy your\nisland.', 52, tail='right')), 760, 1130, pop(t, T('English', 5) + 0.15))
    if T('Fast') <= t < T('Manhattan', 3):
        stext(img, (W // 2 - 40, 280), 'FAST FORWARD', F('oswald', 90), a=eout((t - T('Fast')) / 0.3))
        d0 = ImageDraw.Draw(img); al = int(255 * eout((t - T('Fast')) / 0.3)); d0.polygon([(820, 250), (870, 280), (820, 310)], fill=(255, 255, 255, al)); d0.polygon([(865, 250), (915, 280), (865, 310)], fill=(255, 255, 255, al))
        for i, (lo, la) in enumerate([(39.2, -6.1), (80.7, 7.8), (76.3, 10.0), (101.5, 3.0), (129.8, -4.5), (55.5, -21.0), (120.9, 14.6), (97, 4.5)]):
            t0 = T('grows') + i * 0.12
            if t >= t0: x, y = geo(cam, lo, la); paste(img, art('nut2', lambda: T3.nutmeg(100)), x, y, pop(t, t0, 0.3))
    if T('Manhattan', 3) <= t < T('sprinkle'):
        x, y = geo(cam, -73.97, 40.775); pill(img, (x, y), 'New York', (200, 35, 45), size=64)
        k = eout((t - T('Manhattan', 3)) / 1.5)
        for i in range(int(3 + 15 * k)): paste(img, art('bag', lambda: TO.moneybag(150)), 140 + (i % 6) * 160, 1500 - (i // 6) * 130, 1.0)
        if t >= T('more'): pill(img, (W // 2, 330), '...a little more', (40, 140, 80), size=56, sc=pop(t, T('more')))
    if t >= T('sprinkle'):
        paste(img, art('latte', lambda: T3.latte(360)), W // 2, 1150, pop(t, T('sprinkle')))
        if t >= T('cost'): paste(img, art('dutchS', lambda: T3.dutch('worried', 300)), 240, 1420, pop(t, T('cost')))
    subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 10, int(W * t / END), H], fill=(240, 175, 20, 255))
    return img.convert('RGB')
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): frame(tt).resize((360, 640)).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(round(a * FPS)), int(round(min(b, END) * FPS))):
            enc.stdin.write(np.asarray(frame(fi / FPS)).tobytes())
            if fi % 150 == 0: print(f'{fi / FPS:.1f}s', flush=True)
        enc.stdin.close(); enc.wait()
