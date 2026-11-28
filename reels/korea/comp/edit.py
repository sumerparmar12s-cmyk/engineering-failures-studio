"""The Korean War, 1080x1920. Self-drawn globe + raised flag-textured countries + shaded units. usage: python3 edit.py OUT.mp4 [t0 t1] | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import shape, Polygon, box, Point
from shapely.ops import unary_union
import globe3d as G, raise3d as R3, flags as FL, toons as TO, units3d as U
from globe3d import Camera as Cm
R = G.R; W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json')); END = round(WORDS[-1]['e'] + 1.5, 2)
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
def back(x): x = clamp(x); c1 = 1.7; return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pop(t, t0, d=0.35): return back((t - t0) / d) if t >= t0 else 0
def rise(t, t0, d=0.6): return back((t - t0) / d) if t >= t0 else 0
ART = {}
def art(k, fn):
    if k not in ART: ART[k] = fn()
    return ART[k]
FS = {}
def flag(n):
    if n not in FS: FS[n] = FL.flag_surface(n, 900, 600)
    return FS[n]
def paste(img, im, cx, cy, sc=1.0, anchor='c'):
    if sc <= 0.01: return
    i = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC) if abs(sc - 1) > 0.01 else im
    y = cy - i.height / 2 if anchor == 'c' else cy - i.height
    img.alpha_composite(i, (int(cx - i.width / 2), int(y)))
SLOTS = []
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=46, sc=1.0, icon=None):
    if sc <= 0.02: return
    key = ('pill', txt, bg, fg, size, icon)
    def mk():
        f = F('SemiBold', size); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f); pad = 76 if icon else 26
        im = Image.new('RGBA', (int(tw + pad + 26), int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], 12, fill=bg + (255,)); d.text((pad + tw / 2, im.height / 2), txt, font=f, fill=fg, anchor='mm')
        if icon:
            s = FL.flag_surface(icon, 57, 38); a = np.frombuffer(s.get_data(), np.uint8).reshape(38, 57, 4)[..., [2, 1, 0, 3]]; im.alpha_composite(Image.fromarray(a.copy()), (14, (im.height - 38) // 2))
        return TO.sticker(im, ow=4)
    im = art(key, mk); x = min(max(xy[0], im.width * sc / 2 + 24), W - im.width * sc / 2 - 24); y = min(max(xy[1], 140), 1700)
    # avoid overlapping previously placed pills this frame
    for (ax, ay, aw, ah) in SLOTS:
        if abs(x - ax) < (aw + im.width * sc) / 2 and abs(y - ay) < (ah + im.height * sc) / 2 + 6: y = ay + (ah + im.height * sc) / 2 + 10
    SLOTS.append((x, y, im.width * sc, im.height * sc)); paste(img, im, x, y, sc)
def stext(img, xy, txt, f, fill=(255, 255, 255), a=1.0):
    if a <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, int(210 * a)), anchor='mm', stroke_width=4, stroke_fill=(0, 0, 0, int(160 * a))); lay = lay.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(lay).text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor='mm'); img.alpha_composite(lay)
def headline(img, txt, t, t0, t1=None, col=(255, 255, 255), size=88):
    a = eout((t - t0) / 0.25) * (1 if t1 is None else clamp((t1 - t) / 0.25)); stext(img, (W // 2, 230), txt, F('play', size), col, a)
def stamp(img, txt, t, t0, col=(220, 30, 40), y=900, size=110, rot=-7):
    if t < t0: return
    p = eout((t - t0) / 0.14); sc = 1.8 - 0.8 * p; f = F('oswald', int(size * sc)); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    st = Image.new('RGBA', (int(tw + 80), int(size * sc * 1.45)), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle([6, 6, st.width - 6, st.height - 6], 14, fill=(255, 255, 255, 215), outline=col + (255,), width=12); d.text((st.width / 2, st.height / 2 + 2), txt, font=f, fill=col + (255,), anchor='mm')
    paste(img, st.rotate(rot, expand=True, resample=Image.BICUBIC), W // 2, y)
# ---------------- geography ----------------
C50 = {f['properties']['ADMIN']: shape(f['geometry']) for f in json.load(open(f'{R}/dl/c50.geojson'))['features']}
NK, SK = C50['North Korea'], C50['South Korea']; KOREA = unary_union([NK, SK]).buffer(0)
USSR = unary_union([C50[n].intersection(box(19, 34, 179.9, 82)) for n in ['Russia', 'Ukraine', 'Belarus', 'Kazakhstan', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan', 'Tajikistan', 'Georgia', 'Armenia', 'Azerbaijan', 'Moldova', 'Lithuania', 'Latvia', 'Estonia']])
CHINA = C50['China'].intersection(box(73, 18, 135, 54)); USA48 = max(R3.polys(C50['United States of America']), key=lambda p: p.area)
UK, CAN = C50['United Kingdom'], C50['Canada'].intersection(box(-141, 41, -52, 62))
FRONTS = {   # UN/ROK-held polygon (same vertex count, interpolated)
    'pre':    [(123, 38.0), (127, 38.0), (131, 38.0), (131, 33), (123, 33), (123, 35.5)],
    'pusan':  [(128.3, 36.1), (129.0, 36.1), (131, 36.15), (131, 33), (128.3, 33), (128.3, 35.0)],
    'north':  [(123, 40.0), (127, 40.9), (131, 41.6), (131, 33), (123, 33), (123, 35.5)],
    'pushed': [(123, 37.0), (127, 37.1), (131, 37.35), (131, 33), (123, 33), (123, 35.5)],
    'dmz':    [(123, 37.75), (127, 38.3), (131, 38.65), (131, 33), (123, 33), (123, 35.5)]}
def front(a, b, k):
    k = ease(k); return Polygon([(xa + (xb - xa) * k, ya + (yb - ya) * k) for (xa, ya), (xb, yb) in zip(FRONTS[a], FRONTS[b])])
def front_at(t):
    seq = [(0, 'pre'), (T('border') - 0.6, 'pre'), (T('southeast') + 0.4, 'pusan'), (T('Inchon') - 0.2, 'pusan'), (T('Victory') + 0.4, 'north'), (T('pushes') - 0.4, 'north'), (T('south', 3) + 0.6, 'pushed'), (T('armistice') - 0.8, 'pushed'), (T('fighting') + 0.4, 'dmz')]
    for (t0, a), (t1, b) in zip(seq, seq[1:]):
        if t < t1: return front(a, b, (t - t0) / max(0.01, t1 - t0)) if a != b else Polygon(FRONTS[a])
    return Polygon(FRONTS['dmz'])
PLACES = {'Seoul': (126.98, 37.57), 'Pusan': (129.04, 35.18), 'Inchon': (126.63, 37.46), 'Pyongyang': (125.75, 39.03)}
YEL, ORA, CYAN = (1, 0.82, 0.15), (1, 0.55, 0.1), (0.25, 0.75, 1.0)
# ---------------- shots ----------------
def shots():
    return [(0.0, 'hook', Cm(127.8, 36.4, 1500, 38, 6), Cm(127.8, 36.6, 1350, 40, 8)),
            (T('America') - 0.7, 'west', Cm(-50, 47, 20000, 6, 0), Cm(-52, 47, 19000, 8, 0)),
            (T('more') - 0.2, 'ships', Cm(128.5, 35.5, 1700, 40, 10), Cm(128.5, 35.8, 1550, 42, 12)),
            (T('then') - 0.1, 'bigger', Cm(106, 36, 7600, 18, 0), Cm(106, 36, 7000, 20, 0)),
            (T('After') - 0.1, 'split', Cm(128.5, 36.4, 2500, 36, 8), Cm(128.8, 37.4, 2700, 32, 6)),
            (T('June') - 0.1, 'invasion', Cm(127.6, 35.6, 1150, 44, 6), Cm(127.8, 35.3, 1050, 46, 8)),
            (T('America', 2) - 0.1, 'un', Cm(128.4, 35.3, 900, 46, 10), Cm(128.6, 35.4, 820, 48, 12)),
            (T('Then', 2) - 0.1, 'inchon', Cm(126.9, 37.0, 950, 44, -10), Cm(127.0, 37.6, 1100, 42, -8)),
            (T('until') - 0.3, 'china', Cm(108, 36, 7400, 20, 0), Cm(110, 37, 7000, 22, 0)),
            (T('pushes') - 0.5, 'chinafront', Cm(126.6, 38.6, 1500, 40, -6), Cm(126.9, 38.2, 1400, 42, -4)),
            (T('Now') - 0.1, 'powers', Cm(127, 40, 7000, 18, 0), Cm(127, 40, 7600, 16, 0)),
            (T('Finally') - 0.05, 'end', Cm(127.7, 37.2, 1400, 40, 4), Cm(127.7, 37.4, 1250, 42, 6))]
SHOTS = shots(); FLY = 0.75
def _fly(a, b, k):
    c = a.lerp(b, k); d = math.hypot(a.lon - b.lon, a.lat - b.lat)
    if d > 8 or max(a.dist, b.dist) / min(a.dist, b.dist) > 2.5:
        top = max(a.dist, b.dist, 4000 + d * 90); c.dist = math.exp(math.log(c.dist) + (math.log(top) - math.log(c.dist)) * math.sin(math.pi * k))
        c.pitch = c.pitch * (1 - 0.7 * math.sin(math.pi * k))
    return c
def cam_at(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t + 1e-6); t0, nm, a, b = SHOTS[i]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else END
    if i > 0 and t < t0 + FLY: return _fly(SHOTS[i - 1][3], a, ease((t - t0) / FLY)), nm, t0
    return a.lerp(b, ease((t - t0 - (FLY if i else 0)) / max(0.1, t1 - t0 - FLY))), nm, t0
# ---------------- subtitles ----------------
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15:
            txt = ' '.join(x['w'] for x in g); f = F('SemiBold', 44); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle([W / 2 - tw / 2 - 26, 1765, W / 2 + tw / 2 + 26, 1838], 18, fill=(0, 0, 0, 120)); img.alpha_composite(lay)
            stext(img, (W // 2, 1800), txt, f); break
# ---------------- helpers ----------------
def P(cam, lon, lat, alt=0):
    x, y, z, ok = R3.project_alt(cam, np.array([lon]), np.array([lat]), alt, W, H); return float(x[0]), float(y[0])
def along(path, k):
    k = clamp(k) * (len(path) - 1); i = min(int(k), len(path) - 2); f = k - i
    return path[i][0] + (path[i + 1][0] - path[i][0]) * f, path[i][1] + (path[i + 1][1] - path[i][1]) * f
def unit(img, cam, kind, lon, lat, t, sc=1.0, side='nk', fire=False):
    x, y = P(cam, lon, lat, alt_k(cam) * 1.05)
    if kind == 'tank':
        ph = int(t * 8) % 4; im = art(f'tank_{side}_{ph}_{fire}', lambda: U.tank(side, 300, ph, fire))
    else:
        ph = int(t * 8) % 4; im = art(f'sol_{side}_{ph}', lambda: U.soldier(side, ph * math.pi / 2, 130))
    paste(img, im, x, y, sc, anchor='b')
def alt_k(cam): return cam.dist * 0.009
BOOMS = []
def booms(img, cam, t, items):
    for t0, lo, la in items:
        u = (t - t0) / 0.7
        if 0 <= u < 1: x, y = P(cam, lo, la, alt_k(cam)); paste(img, art(f'boom{int(u * 9)}', lambda: U.explosion(int(u * 9), 260)), x, y - 60, 1.0)
def shake_amt(t, items):
    a = 0
    for t0, *_ in items:
        u = (t - t0) / 0.35
        if 0 <= u < 1: a = max(a, 9 * (1 - u))
    return a
INV_BOOMS = [(T('tanks') + 0.4, 127.2, 37.9), (T('border') + 0.1, 126.9, 37.7), (T('Seoul') - 0.05, 126.98, 37.57), (T('Seoul') + 0.3, 127.1, 37.4), (T('pushed') + 0.1, 127.6, 36.4), (T('corner') - 0.1, 128.2, 35.9)]
CHI_BOOMS = [(T('jumps') + 0.1, 126.5, 39.6), (T('pushes') + 0.1, 127.0, 38.8), (T('back', 3) + 0.0, 127.4, 37.9), (T('south', 3) + 0.1, 126.9, 37.4)]
INC_BOOMS = [(T('land') + 0.2, 126.63, 37.46), (T('take') + 0.1, 126.98, 37.57)]
# ---------------- frame ----------------
def frame(t):
    SLOTS.clear()
    cam, si, st0 = cam_at(t); ak = alt_k(cam)
    img = G.render(cam, W, H).filter(ImageFilter.UnsharpMask(radius=1.3, percent=45, threshold=2)).convert('RGBA')
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    korea_view = si in ('hook', 'ships', 'split', 'invasion', 'un', 'inchon', 'chinafront', 'end')
    # ----- big countries -----
    if si == 'west':
        R3.raised(c, cam, CAN, ak * 0.9 * rise(t, T('Canada')), flag('Canada'), tol=0.08, min_area=0.4)
        R3.raised(c, cam, USA48, ak * 1.0 * rise(t, T('America')), flag('United States of America'), tol=0.08, min_area=0.4)
        R3.raised(c, cam, UK, ak * 1.0 * rise(t, T('Britain')), flag('United Kingdom'), tol=0.03, min_area=0.05)
        for a0, tt in (((-98, 39), T('America')), ((-2, 53), T('Britain')), ((-100, 56), T('Canada'))):
            if t >= tt + 0.2: R3.arc3d(c, cam, a0, (127.5, 37.0), ak * 3, eout((t - tt - 0.2) / 1.6) * 0.42, CYAN, 10)
    if si == 'bigger': R3.raised(c, cam, CHINA, ak * 1.0 * rise(t, T('bigger') - 0.2), None, tol=0.05, min_area=0.5, wall=(0.32, 0.32, 0.36))
    if si == 'split' and t >= T('Soviet') - 0.2: R3.raised(c, cam, USSR, ak * 1.2 * rise(t, T('Soviet') - 0.2), flag('USSR'), tol=0.05, min_area=0.5)
    if si == 'china': R3.raised(c, cam, CHINA, ak * 1.0 * rise(t, T('China') - 0.1), flag('China'), tol=0.05, min_area=0.5)
    if si == 'chinafront': R3.raised(c, cam, CHINA, ak * 1.0, flag('China'), tol=0.05, min_area=0.5)
    if si == 'powers':
        R3.raised(c, cam, USSR, ak * 1.2, flag('USSR'), tol=0.05, min_area=0.5); R3.raised(c, cam, CHINA, ak * 1.2, flag('China'), tol=0.05, min_area=0.5)
    # ----- Korea -----
    if korea_view or si in ('bigger', 'powers', 'china'):
        if si == 'hook':
            R3.raised(c, cam, SK, ak * rise(t, T('small')), flag('South Korea'), tol=0.008, min_area=0.02)
            if t >= T('invaded') - 0.2: R3.raised(c, cam, NK, ak * rise(t, T('invaded') - 0.2), flag('North Korea'), tol=0.008)
        elif si in ('ships', 'bigger', 'split', 'powers', 'china'):
            R3.raised(c, cam, NK, ak, flag('North Korea'), tol=0.008); R3.raised(c, cam, SK, ak, flag('South Korea'), tol=0.008, min_area=0.02)
        else:
            un = KOREA.intersection(front_at(t)); red = KOREA.difference(front_at(t))
            R3.raised(c, cam, red, ak, flag('North Korea'), tol=0.008, min_area=0.02)
            R3.raised(c, cam, un, ak, flag('South Korea'), tol=0.008, min_area=0.02)
    if si == 'split' and t >= T('split') - 0.2:   # 38th parallel
        fr = eout((t - T('split') + 0.2) / 0.8); xs, ys, z, ok = R3.project_alt(cam, np.array([124.2, 124.2 + 5.5 * fr]), np.array([38.0, 38.0]), ak * 1.05, W, H)
        c.move_to(xs[0], ys[0]); c.line_to(xs[1], ys[1]); c.set_source_rgb(1, 1, 1); c.set_line_width(12); c.stroke(); c.move_to(xs[0], ys[0]); c.line_to(xs[1], ys[1]); c.set_source_rgb(*YEL); c.set_dash([22, 12]); c.set_line_width(7); c.stroke(); c.set_dash([])
    # ----- arrows -----
    if si == 'hook' and t >= T('invaded'):
        for a, b in (((126.8, 38.3), (127.0, 36.6)), ((128.0, 38.3), (128.5, 36.8))): R3.arc3d(c, cam, a, b, ak * 1.5, eout((t - T('invaded')) / 0.8), YEL, 11)
    if si == 'split' and t >= T('each') - 0.1:
        k = eout((t - T('each') + 0.1) / 0.8); R3.arc3d(c, cam, (126.5, 39.5), (127.3, 36.4), ak * 2, k, YEL, 11); R3.arc3d(c, cam, (128.6, 36.0), (128.0, 39.6), ak * 2, k, CYAN, 11)
    if si == 'invasion' and t >= T('tanks') - 0.2:
        k = eout((t - T('tanks') + 0.2) / (T('southeast') - T('tanks') + 0.4))
        for a, b in (((126.7, 38.4), (127.2, 36.2)), ((127.6, 38.3), (128.3, 36.3)), ((126.9, 37.5), (127.6, 35.4))): R3.arc3d(c, cam, a, b, ak * 1.6, k, YEL, 11)
    if si == 'inchon' and t >= T('land') - 0.3:
        R3.arc3d(c, cam, (124.8, 36.6), (126.55, 37.42), ak * 1.5, eout((t - T('land') + 0.3) / 0.8), CYAN, 12)
        if t >= T('take') - 0.2: R3.arc3d(c, cam, (126.65, 37.47), (126.95, 37.57), ak * 1.0, eout((t - T('take') + 0.2) / 0.5), CYAN, 10)
        if t >= T('Victory') - 0.2: R3.arc3d(c, cam, (127.0, 37.6), (126.8, 40.3), ak * 1.8, eout((t - T('Victory') + 0.2) / 0.9), CYAN, 12)
    if si == 'chinafront':
        k = eout((t - st0) / 2.2)
        for a, b in (((124.6, 40.6), (126.4, 37.7)), ((125.6, 41.0), (127.3, 37.8)), ((126.8, 41.5), (128.6, 38.2))): R3.arc3d(c, cam, a, b, ak * 1.6, k, YEL, 12)
    if si == 'powers':
        for a, col in (((100, 50), YEL), ((108, 33), YEL), ((150, 38), CYAN)): R3.arc3d(c, cam, a, (127.5, 38.0), ak * 3, eout((t - T('Now') - 0.3) / 1.0), col, 10)
    img.alpha_composite(TO._pil(s))
    # ----- units, explosions, labels -----
    if si == 'hook':
        if t >= T('small') + 0.2: x, y = P(cam, 127.9, 36.0, ak); pill(img, (x, y + 150), 'South Korea', (25, 30, 45), icon='South Korea', sc=pop(t, T('small') + 0.2))
        if t >= T('invaded'):
            x, y = P(cam, 127.0, 39.6, ak); pill(img, (x, y - 70), 'North Korea', (25, 30, 45), icon='North Korea', sc=pop(t, T('invaded')))
            for i, path in enumerate((((126.8, 38.3), (127.0, 36.6)), ((128.0, 38.3), (128.5, 36.8)))):
                lo, la = along(path, eout((t - T('invaded')) / 1.6) * 0.55); unit(img, cam, 'tank', lo, la, t, 0.55, 'nk')
        headline(img, 'Just imagine...', t, 0.0, T('America') - 0.1)
    if si == 'west':
        for lo, la, lab, n, tt, dy in ((-98, 39, 'USA', 'United States of America', T('America'), 0), (-2, 53, 'Britain', 'United Kingdom', T('Britain'), -90), (-100, 57, 'Canada', 'Canada', T('Canada'), -40)):
            if t >= tt: x, y = P(cam, lo, la, ak); pill(img, (x, y + dy), lab, (25, 30, 45), size=48, icon=n, sc=pop(t, tt))
        n = int(16 * eout((t - T('dozen')) / 1.0)) if t >= T('dozen') else 0
        if n: pill(img, (W // 2, 360), f'{n} NATIONS', (40, 90, 170), size=50)
    if si == 'ships':
        names = ['United States of America', 'United Kingdom', 'Canada', 'New Zealand', 'Norway']
        for i, n in enumerate(names):
            t0 = T('more') + i * 0.25; k = eout((t - t0) / 1.4)
            lo = 133.5 - 4.2 * k - (i % 2) * 0.6; la = 33.2 + 1.6 * k + i * 0.35; x, y = P(cam, lo, la, 0)
            if t >= t0: paste(img, art(f'ship_{n}', lambda: U.ship(n, 230)), x, y, 1.0)
        n = int(16 * eout((t - T('dozen')) / 1.0)) if t >= T('dozen') else 0
        if n: pill(img, (W // 2, 360), f'{n} NATIONS SEND TROOPS', (40, 90, 170), size=50)
    if si == 'bigger':
        x, y = P(cam, 104, 35, ak); stext(img, (x, y), '?', F('oswald', 260), (255, 255, 255), a=eout((t - T('bigger')) / 0.3))
        headline(img, 'an even bigger country...', t, T('even'), size=72)
    if si == 'split':
        headline(img, 'Korea, 1945', t, T('After'), T('Soviet') - 0.3)
        x, y = P(cam, 127.0, 39.7, ak); pill(img, (x - 60, y), 'North Korea', (25, 30, 45), icon='North Korea')
        x, y = P(cam, 128.0, 36.2, ak); pill(img, (x, y + 120), 'South Korea', (25, 30, 45), icon='South Korea')
        if t >= T('split'): x, y = P(cam, 129.6, 38.0, ak); pill(img, (x + 40, y - 10), '38th parallel', (240, 175, 20), (20, 20, 20), 40, pop(t, T('split')))
        if t >= T('Soviet') - 0.2: pill(img, (W // 2, 330), 'backed by the Soviet Union', (150, 20, 20), size=44, icon='USSR', sc=pop(t, T('Soviet') - 0.2))
        if t >= T('United') - 0.2: pill(img, (W // 2, 1560), 'backed by the United States', (30, 50, 120), size=44, icon='United States of America', sc=pop(t, T('United') - 0.2))
    if si == 'invasion':
        headline(img, 'June 25, 1950', t, T('June'), T('tanks') + 0.6)
        k = eout((t - T('tanks') + 0.2) / (T('southeast') - T('tanks') + 0.4))
        if t >= T('tanks') - 0.2:
            for i, path in enumerate((((126.7, 38.4), (127.2, 36.2)), ((127.6, 38.3), (128.3, 36.3)), ((126.9, 37.5), (127.6, 35.4)))):
                for q in range(2): lo, la = along(path, max(0, k * 0.92 - q * 0.1)); unit(img, cam, 'tank', lo + q * 0.06, la, t, 0.68, 'nk', fire=int(t * 6 + q) % 5 == 0)
                for q in range(3): lo, la = along(path, max(0, k * 0.92 - 0.2 - q * 0.05)); unit(img, cam, 'sol', lo + 0.18 + q * 0.06, la + 0.04, t + q * 0.11, 0.9, 'nk')
        booms(img, cam, t, INV_BOOMS)
        x, y = P(cam, *PLACES['Seoul'], ak)
        if t >= T('Seoul') - 0.1: pill(img, (x - 40, y - 70), 'Seoul falls', (180, 25, 30), size=42, icon='North Korea', sc=pop(t, T('Seoul') - 0.1))
        if t >= T('corner') - 0.2: x, y = P(cam, 128.9, 35.4, ak); pill(img, (x, y + 130), 'Pusan Perimeter', (40, 80, 180), size=42, icon='South Korea', sc=pop(t, T('corner') - 0.2))
    if si == 'un':
        x, y = P(cam, 128.8, 35.6, ak)
        for i, (n, t0) in enumerate((('United States of America', T('America', 2)), ('United Kingdom', T('Britain', 2)), ('Canada', T('Canada', 2)), ('New Zealand', T('New')))):
            k = eout((t - t0) / 1.0); lo = 130.6 - 1.2 * k; la = 34.4 + 0.25 * i; xs, ys = P(cam, lo, la, 0)
            if t >= t0: paste(img, art(f'ship2_{n}', lambda: U.ship(n, 220)), xs, ys)
        for i in range(5):
            if t >= T('troops') + i * 0.12: unit(img, cam, 'sol', 128.55 + (i % 3) * 0.18, 35.55 + (i // 3) * 0.2, t + i * 0.1, 0.95, 'us' if i % 2 == 0 else 'uk')
        if t >= T('United', 2) - 0.2: pill(img, (W // 2, 330), 'United Nations', (40, 120, 200), size=50, icon='UN', sc=pop(t, T('United', 2) - 0.2))
        row = [('Britain', 'United Kingdom', T('Britain', 2)), ('Canada', 'Canada', T('Canada', 2)), ('New Zealand', 'New Zealand', T('New'))]
        for i, (lab, n, t0) in enumerate(row):
            if t >= t0 - 0.1: pill(img, (200 + i * 340, 470), lab, (25, 30, 45), size=36, icon=n, sc=pop(t, t0 - 0.1))
        if t >= T('Norway') - 0.1:
            x, y = P(cam, 128.75, 35.25, ak); paste(img, art('tent', lambda: U.medtent(240)), x, y, pop(t, T('Norway') - 0.1), anchor='b')
            pill(img, (x, y + 40), 'Norway: medical team', (25, 30, 45), size=38, icon='Norway', sc=pop(t, T('Norway')))
    if si == 'inchon':
        headline(img, 'Inchon, Sept 1950', t, T('Then', 2), T('land') + 0.2, size=78)
        k = eout((t - T('UN', 1) + 0.2) / 1.2) if t >= T('UN', 1) - 0.2 else 0
        for i in range(3):
            lo, la = 124.8 + 1.6 * k + i * 0.1, 36.6 + 0.8 * k - i * 0.12; x, y = P(cam, lo, la, 0)
            if k > 0: paste(img, art(f'ship3_{i}', lambda: U.ship('United States of America', 210)), x, y)
        booms(img, cam, t, INC_BOOMS)
        x, y = P(cam, *PLACES['Seoul'], ak)
        if t >= T('take') - 0.1: pill(img, (x + 60, y - 70), 'Seoul retaken', (40, 120, 200), size=42, icon='South Korea', sc=pop(t, T('take') - 0.1))
        if t >= T('Victory') - 0.1:
            for i in range(3): lo, la = along(((127.0, 37.6), (126.8, 40.0)), eout((t - T('Victory') + 0.1) / 1.2) - i * 0.12); unit(img, cam, 'tank', lo + i * 0.25, la, t, 0.62, 'us')
            stext(img, (W // 2, 370), 'Victory looks close...', F('play', 70), a=eout((t - T('close')) / 0.3))
    if si == 'china':
        x, y = P(cam, 104, 35, ak); pill(img, (x, y), 'China', (180, 25, 30), size=56, icon='China', sc=pop(t, T('China')))
        stamp(img, 'CHINA JOINS', t, T('China') + 0.25, (200, 30, 40), y=420, size=90, rot=-5)
    if si == 'chinafront':
        x, y = P(cam, 123.8, 40.8, ak); pill(img, (x, y - 40), 'China', (180, 25, 30), size=46, icon='China')
        k = eout((t - st0) / 2.2)
        paths = (((124.6, 40.6), (126.4, 37.7)), ((125.6, 41.0), (127.3, 37.8)), ((126.8, 41.5), (128.6, 38.2)))
        for j in range(3):
            for i in range(4):
                lo, la = along(paths[j], k * 0.9 - i * 0.07); unit(img, cam, 'sol', lo + (i % 2) * 0.12, la, t + i * 0.13, 0.95, 'pva')
        for i in range(3):
            lo, la = along(((127.0, 38.4), (127.1, 37.3)), k * 0.9 - i * 0.12); unit(img, cam, 'tank', lo + 0.35 + i * 0.1, la - 0.1, t, 0.55, 'us')
        booms(img, cam, t, CHI_BOOMS)
    if si == 'powers':
        pill(img, (W // 2, 330), 'Not just two Koreas', (25, 30, 45), size=50, sc=pop(t, T('Now')))
        x, y = P(cam, 100, 55, ak * 1.2); pill(img, (x, y), 'Soviet Union', (150, 20, 20), size=44, icon='USSR', sc=pop(t, T('world') - 0.1))
        x, y = P(cam, 108, 33, ak * 1.2); pill(img, (x, y), 'China', (180, 25, 30), size=44, icon='China', sc=pop(t, T('biggest') - 0.1))
        pill(img, (W - 220, 1250), 'USA', (30, 50, 120), size=44, icon='United States of America', sc=pop(t, T('powers') - 0.1))
    if si == 'end':
        if t < T('armistice') - 0.3: headline(img, 'July 27, 1953', t, T('July'))
        x, y = P(cam, 127.0, 38.3, ak)
        if t >= T('armistice') - 0.3:
            paste(img, art('doc', lambda: U.document(300)), W // 2, 520, pop(t, T('armistice') - 0.3))
        if t >= T('divided') - 0.2: x, y = P(cam, 129.1, 38.45, ak); pill(img, (x, y - 10), 'still divided', (240, 175, 20), (20, 20, 20), 40, pop(t, T('divided') - 0.2))
        if t >= T('never') - 0.1: stamp(img, 'NO PEACE TREATY', t, T('never') - 0.1, (200, 30, 40), y=980, size=100, rot=-6)
        if t >= T('peace') + 0.5: pill(img, (W // 2, 1150), '...still, to this day', (25, 30, 45), size=46, sc=pop(t, T('peace') + 0.5))
    # cut flash between far-apart shots
    if False:
        img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (1 - (t - st0) / 0.18)))))
    subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 10, int(W * t / END), H], fill=(240, 175, 20, 255))
    out = img.convert('RGB')
    sk = shake_amt(t, INV_BOOMS + CHI_BOOMS + INC_BOOMS)
    if sk: out = out.transform(out.size, Image.AFFINE, (1, 0, sk * math.sin(t * 90), 0, 1, sk * 0.6 * math.cos(t * 70)), resample=Image.BILINEAR)
    return out
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): frame(tt).resize((360, 640)).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(round(a * FPS)), int(round(min(b, END) * FPS))):
            enc.stdin.write(np.asarray(frame(fi / FPS)).tobytes())
        enc.stdin.close(); enc.wait()
