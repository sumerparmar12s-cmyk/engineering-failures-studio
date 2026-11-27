"""Manhattan-for-nutmeg reel: crisp vector parchment map (vmap), fast camera, pseudo-3D figurines (props3d). usage: python3 edit.py OUT.mp4 [t0 t1] | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import box, Polygon
import vmap as V, props3d as P3
from vmap import Cam
R = V.R; W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json')); END = round(WORDS[-1]['e'] + 1.2, 2)
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
def F(name, size):
    p = {'play': 'PlayfairDisplay.ttf', 'oswald': 'Oswald.ttf'}.get(name)
    f = ImageFont.truetype(f'{FONTS}/{p}', size) if p else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
    try:
        if name == 'play': f.set_variation_by_axes([700])
        if name == 'oswald': f.set_variation_by_axes([600])
    except Exception: pass
    return f
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
def T(word, n=1):
    """time of the n-th occurrence of word in the narration"""
    k = 0
    for w in WORDS:
        if norm(w['w']) == norm(word):
            k += 1
            if k == n: return w['s']
    raise SystemExit(f'word not found: {word} #{n}')
clamp = lambda x, a=0, b=1: max(a, min(b, x))
def ease(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2   # snappy in-out cubic
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x): x = clamp(x); c1 = 1.9; return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2
def pop(t, t0, d=0.3): return back((t - t0) / d) if t >= t0 else 0
ART = {}
def art(k, fn):
    if k not in ART: ART[k] = fn()
    return ART[k]
def paste(img, im, cx, cy, sc=1.0, rot=0, alpha=1.0, anchor='c'):
    if sc <= 0.01: return
    i = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if rot: i = i.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: i.putalpha(i.split()[3].point(lambda v: int(v * alpha)))
    y = cy - i.height / 2 if anchor == 'c' else cy - i.height
    img.alpha_composite(i, (int(cx - i.width / 2), int(y)))
def label(img, xy, txt, size=64, col=(40, 30, 25), a=1.0, italic=False):
    """serif place name printed on the map (no box) with a soft paper halo"""
    if a <= 0.01: return
    f = F('play', size); lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text(xy, txt, font=f, fill=(245, 236, 210, int(220 * a)), anchor='mm', stroke_width=8, stroke_fill=(245, 236, 210, int(160 * a)))
    lay = lay.filter(ImageFilter.GaussianBlur(3)); ImageDraw.Draw(lay).text(xy, txt, font=f, fill=col + (int(255 * a),), anchor='mm'); img.alpha_composite(lay)
def tag(img, xy, txt, bg, fg=(255, 255, 255), size=46, sc=1.0):
    if sc <= 0.02: return
    f = F('SemiBold', size); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 44), int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], 10, fill=bg + (255,)); d.text((im.width / 2, im.height / 2), txt, font=f, fill=fg, anchor='mm'); paste(img, im, xy[0], xy[1], sc)
def big(img, xy, txt, size, fill=(255, 255, 255), a=1.0, f='play'):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); fo = F(f, size)
    d.text((xy[0] + 3, xy[1] + 6), txt, font=fo, fill=(0, 0, 0, int(170 * a)), anchor='mm'); lay = lay.filter(ImageFilter.GaussianBlur(7))
    ImageDraw.Draw(lay).text(xy, txt, font=fo, fill=fill + (int(255 * a),), anchor='mm', stroke_width=2, stroke_fill=(0, 0, 0, int(120 * a))); img.alpha_composite(lay)
def bubble(text, size=50):
    from toons_bubble import bubble as B
    return B(text, size)
# ---------- geography ----------
C = V.countries()
NL = C['Netherlands']; UK = C['United Kingdom']; FR = C['France']; INDO = C['Indonesia']
LAND = V.land()[0]
def clip_land(b):
    from shapely.ops import unary_union
    return unary_union([p.intersection(b) for p in LAND if p.intersects(b)])
MANH = [p for p in LAND if abs(p.bounds[0] + 74.017) < 0.01 and abs(p.bounds[3] - 40.878) < 0.01][0]
NEWNL = clip_land(Polygon([(-75.6, 39.0), (-74.9, 39.0), (-73.9, 40.55), (-73.65, 41.0), (-73.5, 42.2), (-73.3, 43.1), (-74.6, 43.1), (-75.6, 42.0)]))
NEWENG = clip_land(Polygon([(-73.5, 41.0), (-69.8, 41.2), (-69.8, 45.2), (-73.3, 45.0), (-73.3, 43.1)]))
BANDA = clip_land(box(129.70, -4.62, 130.0, -4.45)); RUN = V.RUN_ISLAND
ORANGE, RED, BLUE = (0.95, 0.52, 0.12), (0.82, 0.12, 0.16), (0.16, 0.3, 0.75)
# ---------- timeline (all anchored to the narration) ----------
def shots():
    C_ = Cam
    return [(0.0, C_(-73.975, 40.775, 5200, -29, 0.5), C_(-73.975, 40.775, 5900, -29, 0.55)),
            (T('kept') - 0.1, C_(129.693, -4.552, 26000, 0, 0.5), C_(129.693, -4.552, 30000, 6, 0.55)),
            (T('looked') - 0.2, C_(129.70, -4.553, 12000, 6, 0.5), C_(129.70, -4.553, 13000, 8, 0.5)),
            (T('1600s') - 0.1, C_(6, 49, 30, 0, 0.55), C_(7, 49.5, 37, 0, 0.6)),
            (T('sailors') - 0.05, C_(40, 8, 8.5, 0, 0.3), C_(75, 0, 9, 0, 0.3)),
            (T('only') - 0.2, C_(124, -3, 45, 0, 0.45), C_(126, -3.5, 62, 0, 0.5)),
            (T('Banda') - 0.3, C_(129.82, -4.53, 2600, -6, 0.55), C_(129.82, -4.53, 2950, -8, 0.55)),
            (T('except') - 0.1, C_(129.70, -4.552, 15000, -8, 0.55), C_(129.70, -4.552, 16500, -10, 0.55)),
            (T('other') - 0.05, C_(-74.0, 40.75, 700, -10, 0.5), C_(-74.0, 40.72, 1100, -12, 0.55)),
            (T('1664') - 0.1, C_(-74.03, 40.64, 1500, -8, 0.55), C_(-74.02, 40.66, 1750, -10, 0.55)),
            (T('Stuyvesant') - 0.1, C_(-73.99, 40.73, 3800, -20, 0.55), C_(-73.99, 40.73, 4300, -22, 0.55)),
            (T('renamed') - 0.1, C_(-73.975, 40.775, 5200, -29, 0.55), C_(-73.975, 40.775, 5800, -29, 0.55)),
            (T('three') - 0.05, C_(15, 25, 5.2, 0, 0.25), C_(15, 25, 5.5, 0, 0.25)),
            (T('Fast') - 0.05, C_(20, 5, 5.0, 0, 0.3), C_(20, 5, 5.3, 0, 0.3)),
            (T('Manhattan', 3) - 0.1, C_(-73.975, 40.775, 5600, -29, 0.55), C_(-73.975, 40.775, 6100, -29, 0.55)),
            (T('sprinkle') - 0.1, C_(-73.975, 40.775, 6100, -29, 0.55), C_(-73.975, 40.775, 6800, -26, 0.6))]
SHOTS = shots(); MOVE = 0.6
def _fly(a, b, k):
    """fast move; long jumps dip the zoom out and back in (like a camera flight)"""
    c = a.lerp(b, k); d = math.hypot(a.lon - b.lon, a.lat - b.lat)
    if d > 15:
        dip = max(0.0, min(math.log(a.z), math.log(b.z)) - math.log(4.5)) + 0.4
        c.z = math.exp(math.log(c.z) - dip * math.sin(math.pi * k))
    return c
def cam_at(t):
    i = max(j for j, s in enumerate(SHOTS) if s[0] <= t + 1e-6)
    t0, a, b = SHOTS[i]; t1 = SHOTS[i + 1][0] if i + 1 < len(SHOTS) else END
    if i > 0 and t < t0 + MOVE:
        pt0, pa, pb = SHOTS[i - 1]; return _fly(pb, a, ease((t - t0) / MOVE)), 0
    return a.lerp(b, clamp((t - t0 - (MOVE if i > 0 else 0)) / max(0.1, t1 - t0 - MOVE))), 1
def speed(t):
    a, _ = cam_at(t); b, _ = cam_at(t + 1 / FPS); mx, my = V.merc(a.lon, a.lat); nx, ny = V.merc(b.lon, b.lat)
    return abs(math.log(b.z / a.z)) * 40 + math.hypot(nx - mx, ny - my) * a.k / 40
# ---------- territory state by time ----------
def territories(t):
    tr = []
    tA = T('Amsterdam'); tSw = T('keep', 1)
    if t < T('kept') + 0.15 or (T('other') < t):
        man_col = ORANGE if t < T('renamed') else RED
        if t >= tA - 0.3 and t < T('renamed'): tr.append((NEWNL, ORANGE, 0.35)); tr.append((NEWENG, RED, 0.3))
        
        tr.append((MANH, man_col, 0.8))
    if T('kept') < t < T('other'):
        if t >= T('grabbed'): tr.append((BANDA, ORANGE, min(0.8, (t - T('grabbed')) / 0.6)))
        run_col = ORANGE if t < T('Run') - 0.5 else RED
        if t >= T('tiny') - 0.3: tr.append((RUN, run_col if t >= T('Run') - 0.5 else ORANGE, 0.85))
    if T('1600s') - 0.2 < t < T('sailors'): tr.append((NL, ORANGE, 0.8)); tr.append((UK, RED, 0.7))
    return tr
def extra_lines(t):
    def draw(c, cam):
        if T('sailors') <= t < T('only') - 0.2:   # sea route Europe -> Cape -> Indonesia
            pts = [(4, 51), (-10, 40), (-18, 15), (-10, -10), (10, -33), (19.5, -36), (40, -30), (65, -15), (95, -8), (115, -6), (129.8, -4.5)]
            k = ease((t - T('sailors')) / (T('planet') + 0.5 - T('sailors'))); n = max(2, int(len(pts) * k) + 1)
            c.set_source_rgba(0.55, 0.12, 0.1, 0.9); c.set_line_width(7); c.set_dash([4, 16]); c.new_path()
            for i, (lo, la) in enumerate(pts[:n]): x, y = cam.xy(lo, la); (c.move_to if i == 0 else c.line_to)(x, y)
            c.stroke(); c.set_dash([])
        if T('tiny') - 0.3 <= t < T('looked') and cam.z > 8000:   # scale bar under Run
            x, y = cam.xy(129.678, -4.566); x2, _ = cam.xy(129.705, -4.566)
            c.set_source_rgb(0.1, 0.1, 0.1); c.set_line_width(5); c.move_to(x, y); c.line_to(x2, y); c.stroke()
    return draw
# ---------- captions (small, like the reference) ----------
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def caption(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.12:
            big(img, (W // 2, 1640), ' '.join(x['w'] for x in g), 46, f='SemiBold'); break
# ---------- one frame ----------
def frame(t):
    cam, _ = cam_at(t)
    img = V.render(cam, territories(t), extra_lines(t))
    sp = speed(t)
    if sp > 2.5: img = img.filter(ImageFilter.GaussianBlur(min(14, (sp - 2.5) * 1.2)))
    img = img.convert('RGBA')
    def ll(lo, la):
        x, y = cam.xy(lo, la)
        if cam.tilt > 0.01:   # follow the perspective tilt (approx)
            k = cam.tilt; dx = W * 0.22 * k; dy = H * 0.06 * k; v = y / H
            top_w = W - 2 * dx; sc = top_w / W + (1 - top_w / W) * v
            x = W / 2 + (x - W / 2) * (1 / sc) * 1.0; y = dy + (y - dy) * 1.0
        return x, y
    # ---- hook ----
    if t < T('kept') + 0.15:
        x, y = ll(-73.975, 40.78); label(img, (x, y), 'Manhattan', 76, a=eout(t / 0.3))
        big(img, (W // 2, 300), '1667', 120, a=eout(t / 0.25))
        paste(img, art('dutch', lambda: P3.figure('dutch', 'happy', 260)), 820, 1420, pop(t, 0.6))
    if T('kept') + 0.15 <= t < T("Let's") + 0.1:
        x, y = ll(129.693, -4.552)
        if t >= T('tiny'): label(img, (x, y - 150), 'Run Island', 70, a=eout((t - T('tiny')) / 0.25)); tag(img, (x, y + 170), '≈ 3 km long', (40, 30, 25), size=40, sc=pop(t, T('tiny') + 0.2))
        if t >= T('joke') - 0.3: big(img, (W // 2, 320), 'Not a joke.', 92, a=eout((t - T('joke') + 0.3) / 0.25))
        if t >= T('looked'): paste(img, art('dutch_l', lambda: P3.figure('dutch', 'laugh', 300)), 300, 1450, pop(t, T('looked'))); tag(img, (300, 1630), 'Great deal!', (225, 120, 25), size=40, sc=pop(t, T('great')))
    if T('rewind') - 0.1 <= t < T('1600s') + 0.2:   # VHS rewind flash
        a = clamp(1 - abs(t - (T('rewind') + 0.3)) / 0.45)
        d = ImageDraw.Draw(img)
        for i in range(14): y = (i * 151 + int(t * 2400)) % H; d.rectangle([0, y, W, y + 6], fill=(255, 255, 255, int(120 * a)))
        big(img, (W // 2 + 40, H // 2), 'REWIND', 92, a=a, f='oswald'); d.polygon([(250, 960), (310, 920), (310, 1000)], fill=(255, 255, 255, int(255 * a))); d.polygon([(300, 960), (360, 920), (360, 1000)], fill=(255, 255, 255, int(255 * a)))
    # ---- nutmeg in Europe ----
    if T('1600s') - 0.1 <= t < T('sailors'):
        big(img, (W // 2, 290), '1600s', 120, a=eout((t - T('1600s')) / 0.25))
        x, y = ll(5.3, 52.2); label(img, (x + 40, y - 60), 'Dutch', 54, a=1)
        x, y = ll(-2, 53.5); label(img, (x - 30, y), 'English', 54, a=1)
        if t >= T('nutmeg'):
            for i in range(7):
                t0 = T('nutmeg') + i * 0.08; fy = 520 + i * 40 + 600 * eout((t - t0) / 0.6)
                paste(img, art('nut', lambda: P3.nutmeg(150)), 160 + i * 130, min(fy, 1180 + (i % 3) * 60), pop(t, t0, 0.25), rot=(i * 37) % 360)
            tag(img, (W // 2, 420), 'NUTMEG', (110, 60, 30), size=58, sc=pop(t, T('nutmeg')))
    if T('sailors') <= t < T('only') - 0.2:
        k = ease((t - T('sailors')) / (T('planet') + 0.5 - T('sailors')))
        pts = [(4, 51), (-10, 40), (-18, 15), (-10, -10), (10, -33), (19.5, -36), (40, -30), (65, -15), (95, -8), (115, -6), (129.8, -4.5)]
        i = min(len(pts) - 2, int(k * (len(pts) - 1))); f = k * (len(pts) - 1) - i; lo = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f; la = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
        x, y = ll(lo, la); paste(img, art('shipNL', lambda: P3.ship(230)), x, y - 40, pop(t, T('sailors')))
        tag(img, (W // 2, 320), 'Half the planet', (110, 60, 30), size=50, sc=pop(t, T('half')))
    # ---- Banda ----
    if T('only') - 0.2 <= t < T('other') + 0.05:
        if t >= T('Banda') - 0.2: x, y = ll(129.88, -4.47); label(img, (x, y - 110), 'Banda Islands', 66, a=eout((t - T('Banda') + 0.2) / 0.25))
        if t >= T('Indonesia'): tag(img, (W // 2, 300), "today's Indonesia", (40, 30, 25), size=46, sc=pop(t, T('Indonesia')))
        if t >= T('only') - 0.1 and t < T('grabbed'): tag(img, (W // 2, 420), 'ONLY PLACE ON EARTH', (180, 40, 40), size=50, sc=pop(t, T('only') - 0.1))
        if t >= T('grabbed'): paste(img, art('dutch2', lambda: P3.figure('dutch', 'happy', 260)), 230, 1430, pop(t, T('grabbed'))); tag(img, (230, 1610), 'Dutch', (225, 120, 25), size=40, sc=pop(t, T('grabbed') + 0.1))
        if t >= T('Run') - 0.5:
            x, y = ll(129.693, -4.552); label(img, (x, y - 120), 'Run', 76, col=(150, 20, 25), a=eout((t - T('Run') + 0.5) / 0.25))
        if t >= T('English'): paste(img, art('red', lambda: P3.figure('redcoat', 'happy', 260)), 850, 1430, pop(t, T('English'))); tag(img, (850, 1610), 'English', (200, 30, 40), size=40, sc=pop(t, T('English') + 0.1))
    # ---- New Amsterdam ----
    if T('other') + 0.05 <= t < T('three') + 0.1:
        if t >= T('Amsterdam') - 0.25 and t < T('renamed'): x, y = ll(-74.01, 40.705); label(img, (x, y + 120), 'New Amsterdam', 70, a=eout((t - T('Amsterdam') + 0.25) / 0.25))
        if T('Amsterdam') <= t < T('1664'): paste(img, art('dutch3', lambda: P3.figure('dutch', 'happy', 250)), 800, 1430, pop(t, T('Amsterdam')))
        if T('1664') <= t < T('Stuyvesant'): big(img, (W // 2, 300), '1664', 120, a=eout((t - T('1664')) / 0.25))
        if T('warships') - 0.2 <= t < T('Stuyvesant'):
            for i in range(3):
                k = eout((t - T('warships') + 0.2 - i * 0.15) / 1.0); paste(img, art('shipEN', lambda: P3.ship(220, flag=(0.85, 0.1, 0.15))), -200 + k * (380 + i * 230), 1150 + i * 110, 1.0)
        if T('Stuyvesant') <= t < T('renamed'):
            paste(img, art('stuy', lambda: P3.figure('stuyvesant', 'worried', 420)), W // 2, 1250, pop(t, T('Stuyvesant')))
            tag(img, (W // 2, 1600), 'Peter Stuyvesant', (40, 30, 25), size=46, sc=pop(t, T('Stuyvesant') + 0.1))
            if t >= T('peg'): tag(img, (W // 2 + 230, 1430), 'peg leg', (110, 60, 30), size=38, sc=pop(t, T('peg')))
            if t >= T('surrendered'):
                d = ImageDraw.Draw(img); x0 = W // 2 + 150; d.line([(x0, 1300), (x0, 1020)], fill=(90, 60, 30, 255), width=10); d.polygon([(x0, 1020), (x0 + 150, 1045), (x0, 1090)], fill=(255, 255, 255, 255), outline=(40, 40, 40, 255))
                tag(img, (W // 2, 420), 'Without a fight', (40, 120, 70), size=52, sc=pop(t, T('without')))
        if t >= T('renamed'):
            x, y = ll(-73.975, 40.78)
            if t < T('York') : label(img, (x, y), 'New Amsterdam', 70, a=1)
            else:
                label(img, (x, y), 'New York', 86, col=(150, 20, 25), a=eout((t - T('York')) / 0.25))
            if t >= T("king's"): paste(img, art('king', lambda: P3.figure('king', 'happy', 300)), 270, 1430, pop(t, T("king's"))); tag(img, (270, 1620), 'The King', (200, 30, 40), size=40, sc=pop(t, T("king's") + 0.1))
            if t >= T('Duke'): paste(img, art('duke', lambda: P3.figure('redcoat', 'happy', 260)), 820, 1440, pop(t, T('Duke'))); tag(img, (820, 1620), 'Duke of York', (200, 30, 40), size=40, sc=pop(t, T('Duke') + 0.1))
    # ---- treaty + swap ----
    if T('three') + 0.1 <= t < T('Fast'):
        img.alpha_composite(Image.new('RGBA', (W, H), (30, 22, 12, 70)))
        if t < T('Dutch', 6): paste(img, art('scroll', lambda: P3.scroll(330)), W // 2, 760, pop(t, T('peace') - 0.1))
        if T('everybody') <= t < T('Dutch', 6): tag(img, (W // 2, 330), 'Everybody keeps what they have', (40, 30, 25), size=44, sc=pop(t, T('everybody')))
        if t >= T('keep', 1) - 0.2:
            for side, (lo, la, z, nm, col, fig) in enumerate(((129.693, -4.552, 30000, 'Run', ORANGE, 'dutch'), (-73.975, 40.775, 9000, 'Manhattan', RED, 'king'))):
                tt = T('keep', 1) if side == 0 else T('keep', 2)
                if t < tt - 0.2: continue
                sc = pop(t, tt - 0.2, 0.35)
                mini = V.render(Cam(lo, la, z, 0, 0), [(RUN if side == 0 else MANH, col, 0.85)]).crop((240, 560, 840, 1360)).resize((420, 560))
                m = Image.new('RGBA', (440, 580), (245, 236, 210, 255)); m.paste(mini, (10, 10)); paste(img, m, 290 + side * 500, 1050, sc)
                label(img, (290 + side * 500, 720), nm, 60, a=sc if sc < 1 else 1)
                paste(img, art(fig + 'mini', lambda: P3.figure(fig, 'laugh', 190)), 290 + side * 500, 1420, sc)
        if t >= T('Dutch', 6):
            paste(img, art('bub1', lambda: bubble('Nutmeg forever!', 48)), 300, 520, pop(t, T('Dutch', 6) + 0.2))
            if t >= T('English', 5): paste(img, art('bub2', lambda: bubble('Enjoy your island.', 44)), 780, 420, pop(t, T('English', 5) + 0.2))
    # ---- fast forward ----
    if T('Fast') <= t < T('sprinkle') - 0.1:
        if t < T('Manhattan', 3):
            big(img, (W // 2 - 40, 300), 'FAST FORWARD', 84, a=eout((t - T('Fast')) / 0.25), f='oswald'); d0 = ImageDraw.Draw(img); al = int(255 * eout((t - T('Fast')) / 0.25)); d0.polygon([(800, 270), (850, 300), (800, 330)], fill=(255, 255, 255, al)); d0.polygon([(845, 270), (895, 300), (845, 330)], fill=(255, 255, 255, al))
            spots = [(-61.7, 12.1), (39.2, -6.1), (80.7, 7.8), (76.3, 10.0), (101.5, 3.0), (129.8, -4.5), (-77, 18.1), (12, 0)]
            for i, (lo, la) in enumerate(spots):
                t0 = T('grows') + i * 0.1
                if t >= t0: x, y = ll(lo, la); paste(img, art('nut2', lambda: P3.nutmeg(90)), x, y, pop(t, t0, 0.25))
        else:
            x, y = ll(-73.975, 40.78); label(img, (x, y), 'New York', 86, col=(150, 20, 25))
            k = eout((t - T('Manhattan', 3)) / 1.6)
            for i in range(int(4 + 20 * k)):
                paste(img, art('bag', lambda: money_bag()), 150 + (i % 6) * 155, 1500 - (i // 6) * 120, 0.8)
            if t >= T('more'): tag(img, (W // 2, 360), '...a little more', (40, 120, 70), size=54, sc=pop(t, T('more')))
    if t >= T('sprinkle') - 0.1:
        paste(img, art('latte', lambda: P3.latte(380)), W // 2, 1180, pop(t, T('sprinkle') - 0.1))
        if t >= T('cost'): paste(img, art('dutchsad', lambda: P3.figure('dutch', 'worried', 260)), 230, 1450, pop(t, T('cost'))); big(img, (W // 2, 330), 'Worth it?', 96, a=eout((t - T('cost')) / 0.25))
    caption(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 9, int(W * t / END), H], fill=(225, 120, 25, 255))
    return img.convert('RGB')
def money_bag():
    from toons_bubble import moneybag
    return moneybag(170)
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
