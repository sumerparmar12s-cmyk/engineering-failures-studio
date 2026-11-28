"""The Great Emu War (1080x1920). Self-drawn: globe map + cairo scenes (office, farm, battlefield, water hole, truck chase).
usage: python3 edit.py OUT.mp4 [t0 t1] | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import shape
import globe3d as G, toons as TO, emuart as EA
from globe3d import Camera as Cm
R = G.R; W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json')); SEGS = json.load(open(f'{R}/work/segments.json'))
END = round(WORDS[-1]['e'] + 1.4, 2)
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
    i = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC) if sc != 1 else im
    if rot: i = i.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: i = i.copy(); i.putalpha(i.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(i, (int(cx - i.width / 2), int(cy - i.height / 2)))
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=50, sc=1.0):
    if sc <= 0.02: return
    f = F('SemiBold', int(size)); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 50), int(size * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], 12, fill=bg + (255,))
    d.text((im.width / 2, im.height / 2 - 1), txt, font=f, fill=fg, anchor='mm')
    x = min(max(xy[0], im.width / 2 + 30), W - im.width / 2 - 30); paste(img, TO.sticker(im, ow=4), x, xy[1], sc)
def stext(img, xy, txt, f, fill=(255, 255, 255), a=1.0):
    if a <= 0.01: return
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, int(200 * a)), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0, int(150 * a))); lay = lay.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(lay).text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor='mm'); img.alpha_composite(lay)
def headline(img, txt, t, t0, col=(255, 255, 255), size=92, y=250):
    stext(img, (W // 2, y), txt, F('play', size), fill=col, a=eout((t - t0) / 0.25))
def stamp(img, txt, t, t0, col=(220, 30, 40), y=900, size=130, rot=-8):
    if t < t0: return
    p = eout((t - t0) / 0.14); sc = 1.8 - 0.8 * p; f = F('oswald', int(size * sc)); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
    st = Image.new('RGBA', (int(tw + 80), int(size * sc * 1.45)), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle([6, 6, st.width - 6, st.height - 6], 14, outline=col + (255,), width=12); d.text((st.width / 2, st.height / 2 + 2), txt, font=f, fill=col + (255,), anchor='mm')
    paste(img, st.rotate(rot, expand=True, resample=Image.BICUBIC), W // 2, y, 1.0)
# ---------------- talking (acted lines) ----------------
ACTED = []
for sg in SEGS:
    if sg['kind'] == 'acted':
        ws = [w for w in WORDS if sg['start'] - 0.3 <= w['s'] <= sg['start'] + 4]
        n = len(sg['text'].split()); ACTED.append((sg['start'], ws[min(n, len(ws)) - 1]['e'] if ws else sg['start'] + 2, sg['voice']))
def talk(t, voice):
    for a, b, v in ACTED:
        if v == voice and a <= t <= b: return 0.35 + 0.65 * abs(math.sin(t * 17))
    return 0
# ---------------- backgrounds ----------------
def bg(name):
    return art('bg_' + name, lambda: {'field': lambda: EA.outback(), 'water': lambda: EA.outback(water=True, seed=3), 'office': EA.office, 'field2': lambda: EA.outback(seed=7)}[name]())
def push(im, t, t0, t1, z0=1.0, z1=1.07, cx=0.5, cy=0.5, shake=0.0):
    k = ease((t - t0) / max(0.01, t1 - t0)); z = z0 + (z1 - z0) * k; w, h = W / z, H / z
    x0 = cx * W - w / 2 + shake * math.sin(t * 71); y0 = cy * H - h / 2 + shake * math.cos(t * 59)
    x0 = clamp(x0, 0, W - w); y0 = clamp(y0, 0, H - h)
    return im.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h)).convert('RGBA')
# ---------------- globe (Australia) ----------------
ST = {f['properties']['name']: shape(f['geometry']) for f in json.load(open(f'{R}/work/states.geojson'))['features'] if f['properties'].get('admin') == 'Australia'}
WA = ST['Western Australia']
from shapely.geometry import Polygon
WHEAT = Polygon([(115.6, -29.0), (117.5, -28.6), (119.6, -30.2), (120.2, -32.5), (119.8, -33.8), (117.5, -34.5), (115.9, -33.6), (115.8, -31.0)]).intersection(WA)
CAMPION = (118.45, -31.05)
def proj(cam, pts):
    lo = np.array([p[0] for p in pts]); la = np.array([p[1] for p in pts]); x, y, ok = cam.project(lo, la, W, H); return list(zip(x, y)), ok
def cpoly(c, cam, g, fill, alpha, lw=4):
    gs = list(g.geoms) if hasattr(g, 'geoms') else [g]; c.new_path()
    for p in gs:
        if p.geom_type != 'Polygon': continue
        pts, ok = proj(cam, list(p.exterior.coords)[::2])
        if not ok.all(): continue
        [(c.move_to if i == 0 else c.line_to)(x, y) for i, (x, y) in enumerate(pts)]; c.close_path()
    c.set_source_rgba(*fill, alpha); c.fill_preserve(); c.set_source_rgba(1, 1, 1, min(1, alpha * 1.8)); c.set_line_width(lw); c.stroke()
MAPKEYS1 = [(T('Western') - 0.3, Cm(125, -25, 9000, 10, 0)), (T('1932') + 0.3, Cm(122, -27, 3800, 28, -4)), (T('emus') + 0.2, Cm(118.6, -31.2, 1500, 36, -6)), (T('Hello') + 0.1, Cm(118.5, -31.1, 1300, 40, -8))]
MAPKEYS2 = [(T('After') - 0.2, Cm(118.6, -31.2, 1700, 34, -4)), (T('army', 3) + 0.2, Cm(119, -31, 1500, 38, -8))]
def camk(keys, t):
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t < t1: return a.lerp(b, ease((t - t0) / (t1 - t0)))
    return keys[-1][1]
EMU_DOTS = [(115.9 + (i * 37 % 41) / 41 * 4.0, -29.3 - (i * 53 % 47) / 47 * 4.6) for i in range(60)]
EMU_DOTS = [p for p in EMU_DOTS if WHEAT.contains(shape({'type': 'Point', 'coordinates': list(p)}))]
def map_scene(t, keys, show_dots=True, counter=None):
    cam = camk(keys, t)
    img = G.render(cam, W, H).filter(ImageFilter.UnsharpMask(radius=1.3, percent=45, threshold=2)).convert('RGBA')
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    cpoly(c, cam, WA, (0.95, 0.55, 0.15), 0.45)
    if t >= T('wheat') - 0.3 or keys is MAPKEYS2: cpoly(c, cam, WHEAT, (1.0, 0.85, 0.3), 0.55 * (eout((t - T('wheat') + 0.3) / 0.5) if keys is MAPKEYS1 else 1))
    img.alpha_composite(TO._pil(s))
    if show_dots and t >= T('twenty') - 0.1:
        n = int(len(EMU_DOTS) * clamp((t - T('twenty') + 0.1) / 1.4))
        for i, (lo, la) in enumerate(EMU_DOTS[:n]):
            P, ok = proj(cam, [(lo, la)]); x, y = P[0]; paste(img, art(f'emudot{i % 4}', lambda: EA.emu(i % 4 * 1.5, 'run', 'normal', 80)), x, y - 30, pop(t, T('twenty') - 0.1 + i * 0.03, 0.2))
    return img, cam
# ---------------- subtitles ----------------
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15: stext(img, (W // 2, 1800), ' '.join(x['w'] for x in g), F('SemiBold', 44)); break
# ---------------- helpers for animated actors ----------------
def emu_at(img, x, y, t, sc=1.0, pose='run', expr='normal', speed=14.0, flip=False, seed=0):
    ph = int((t * speed + seed * 1.7) % 8); key = f'emu_{pose}_{expr}_{ph}_{flip}'
    paste(img, art(key, lambda: EA.emu(ph * math.pi / 4, pose, expr, 300, flip)), x, y, sc)
def marcher_at(img, x, y, t, sc=1.0, seed=0):
    ph = int((t * 7 + seed) % 6); paste(img, art(f'march{ph}', lambda: EA.marcher(ph * math.pi / 3, 200)), x, y, sc)
def gunner_at(img, x, y, t, fire=False, jam=False, expr='neutral', sc=1.0):
    fl = fire and int(t * 20) % 2 == 0; key = f'gun_{fl}_{jam}_{expr}'
    paste(img, art(key, lambda: EA.gunner(0, fl, jam, expr, 560)), x, y, sc)
def bullets(img, t, x0, y0, t0, t1, dirs=(0,)):
    if not (t0 <= t < t1): return
    d = ImageDraw.Draw(img)
    for i in range(10):
        u = ((t * 9 + i * 0.37) % 1.0); ang = dirs[i % len(dirs)] + 0.08 * math.sin(i * 7.3)
        x = x0 + u * 900 * math.cos(ang); y = y0 + u * 900 * math.sin(ang)
        d.line([(x, y), (x + 40 * math.cos(ang), y + 40 * math.sin(ang))], fill=(255, 230, 120, 255), width=6)
def desk_cover(img):
    img.alpha_composite(bg('office').crop((0, 1180, W, H)).convert('RGBA'), (0, 1180))
# ---------------- frame ----------------
def frame(t):
    # ===== 1. HOOK: an army marches out... to fight a bird =====
    if t < T('Western') - 0.3:
        if t < T('to') - 0.05:
            img = push(bg('field'), t, 0, 5.3, 1.0, 1.08, 0.5, 0.6)
            for row in range(2):
                for i in range(5):
                    x = -150 + (t * 120) + i * 190 + row * 90; y = 1240 + row * 170
                    marcher_at(img, x, y, t, 0.9 + row * 0.25, seed=i + row)
            if t >= T('machine') - 0.1:
                paste(img, art('crate', lambda: EA.ammo_crate(220)), 860, 1600, pop(t, T('machine') - 0.1))
            if t >= T('ten') - 0.1:
                n = int(10000 * eout((t - T('ten') + 0.1) / 0.9)); pill(img, (W // 2, 420), f'{n:,} BULLETS', (60, 70, 50), size=60, sc=pop(t, T('ten') - 0.1))
            headline(img, 'Just imagine...', t, 0.0)
        else:
            img = push(bg('field2'), t, T('to'), T('Western'), 1.15, 1.0, 0.5, 0.65)
            pose, expr = ('stand', 'smug') if t < T('And', 2) else ('cheer', 'happy')
            emu_at(img, W // 2, 1280, t, 1.9, pose, expr, speed=6)
            headline(img, 'vs. a BIRD', t, T('to'), (255, 220, 90), 110)
            if t >= T('wins') - 0.1: pill(img, (W // 2, 430), 'AND THE BIRD WINS', (230, 160, 20), (20, 20, 20), 58, pop(t, T('wins') - 0.1))
    # ===== 2. MAP: Western Australia, 1932, 20,000 emus =====
    elif t < T('Hello') - 0.1:
        img, cam = map_scene(t, MAPKEYS1)
        if t < T('About'): headline(img, 'Western Australia, 1932', t, T('Western') - 0.2, size=78)
        P, ok = proj(cam, [(121, -26)]); pill(img, (P[0][0], P[0][1]), 'Western Australia', (230, 120, 25), size=46, sc=pop(t, T('Western')) * (1 if t < T('emus') else 0))
        if t >= T('twenty') - 0.1:
            n = int(20000 * eout((t - T('twenty') + 0.1) / 1.2)); pill(img, (W // 2, 300), f'~{n:,} EMUS', (120, 80, 40), size=64, sc=pop(t, T('twenty') - 0.1))
        if t >= T('wheat') - 0.2: P, ok = proj(cam, [(117.2, -33.9)]); pill(img, (P[0][0], P[0][1] + 40), 'wheat farms', (200, 160, 30), (20, 20, 20), 42, pop(t, T('wheat') - 0.2))
    # ===== 3. FARMER calls the government =====
    elif t < T('And', 3) - 0.1:
        img = push(bg('field'), t, T('Hello') - 0.1, T('And', 3), 1.0, 1.06, 0.5, 0.55)
        paste(img, art('house', lambda: EA.farmhouse(380)), 260, 870)
        for i in range(6): emu_at(img, 160 + i * 150, 1080 + (i % 2) * 70, t, 0.75, 'peck', 'happy', speed=7, seed=i, flip=i % 2 == 1)
        paste(img, art(f'farm{int(talk(t, "am_adam") * 3)}', lambda: EA.farmer(int(talk(t, 'am_adam') * 3) / 3, 'shock', 480)), 690, 1450, pop(t, T('Hello') - 0.1))
        paste(img, art('bub_farm', lambda: TO.bubble('The birds are\neating everything!', 50)), 380, 1100, pop(t, T('birds') - 0.1))
    # ===== 4. MINISTER in his office =====
    elif t < T('Major') - 0.1:
        img = push(bg('office'), t, T('And', 3) - 0.1, T('Major'), 1.0, 1.05, 0.5, 0.6)
        tk = talk(t, 'bm_george'); paste(img, art(f'min{int(tk * 3)}', lambda: EA.minister(int(tk * 3) / 3, 'smug', 620)), 520, 900); desk_cover(img)
        ring = t < T('send') - 0.2
        paste(img, art(f'phone{int(t * 30) % 2 if ring else 0}', lambda: EA.phone(200, 0.4 if ring and int(t * 30) % 2 else 0)), 860, 1100)
        if ring: pill(img, (860, 920), 'RING RING', (200, 40, 40), size=40, sc=pop(t, T('And', 3)))
        if t >= T('send'): stamp(img, 'SEND THE ARMY', t, T('send'), (200, 30, 40), y=1500, size=110, rot=-6)
        if t >= T('How') - 0.1: paste(img, art('bub_min', lambda: TO.bubble('How hard\ncan it be?', 60, tail='left')), 330, 660, pop(t, T('How') - 0.1))
        if t >= T('be') + 0.4: pill(img, (W // 2, 230), '(spoiler: very hard)', (30, 30, 34), size=40, sc=pop(t, T('be') + 0.4))
    # ===== 5. MAJOR MEREDITH arrives =====
    elif t < T('soldiers') - 0.1:
        img = push(bg('field2'), t, T('Major') - 0.1, T('soldiers'), 1.0, 1.06, 0.5, 0.6)
        for i in range(4): marcher_at(img, 120 + i * 120, 1160, 0, 0.75, seed=i)
        if t >= T('two') - 0.1:
            for i in range(2): gunner_at(img, 220 + i * 360, 1420, t, sc=0.6) if False else paste(img, art('lg', lambda: _lg()), 230 + i * 330, 1520, pop(t, T('two') + i * 0.15))
        if t >= T('ten', 2) - 0.1:
            for i in range(5): paste(img, art('crate2', lambda: EA.ammo_crate(170)), 720 + (i % 3) * 110, 1700 - (i // 3) * 90, pop(t, T('ten', 2) + i * 0.08))
            pill(img, (W // 2, 330), '10,000 ROUNDS', (60, 70, 50), size=58, sc=pop(t, T('ten', 2)))
        tk = talk(t, 'bm_lewis'); paste(img, art(f'maj{int(tk * 3)}', lambda: EA.major(int(tk * 3) / 3, 'smug', 560)), 740, 1100, pop(t, T('Major') - 0.1))
        if t < T('Gentlemen') - 0.1: headline(img, 'Major Meredith', t, T('Major'), size=86)
        if t >= T('Gentlemen') - 0.1: paste(img, art('bub_maj', lambda: TO.bubble('This will be\nover by lunch.', 54, tail='right')), 640, 720, pop(t, T('Gentlemen') - 0.1))
    # ===== 6. OPEN FIRE: emus scatter =====
    elif t < T('Plan') - 0.1:
        fire = T('fire') - 0.1 <= t < T('split') + 0.6
        img = push(bg('field'), t, T('soldiers') - 0.1, T('Plan'), 1.02, 1.08, 0.5, 0.6, shake=6 if fire else 0)
        sc_t = t - T('split') + 0.2
        for i in range(10):
            ang = (i / 10) * 2 * math.pi + 0.3; r = 0 if sc_t < 0 else 900 * eout(sc_t / 1.6)
            x = 640 + math.cos(ang) * r * 0.9 + (i % 3 - 1) * 90; y = 1060 + math.sin(ang) * r * 0.45 + (i // 3) * 40
            flip = math.cos(ang) < 0
            emu_at(img, x, y, t, 0.8 + 0.08 * (i % 3), 'run' if sc_t > 0 else 'stand', 'shock' if 0 < sc_t < 1.0 else 'normal', speed=18, seed=i, flip=flip)
        if t >= T('rehearsed') - 0.3:
            for i in range(3): paste(img, art('emuhappy', lambda: EA.emu(0, 'cheer', 'smug', 300)), 640 + (i - 1) * 260, 1200, pop(t, T('rehearsed') - 0.3 + i * 0.1) * 0.9)
            pill(img, (W // 2, 420), 'DRILL PRACTICE: 10/10', (40, 140, 80), size=48, sc=pop(t, T('rehearsed')))
        gunner_at(img, 300, 1560, t, fire, False, 'neutral')
        bullets(img, t, 520, 1430, T('fire') - 0.1, T('split') + 0.6, dirs=(-0.25, -0.15, -0.3))
        if T('split') <= t < T('rehearsed') - 0.3: paste(img, art('bub_sc', lambda: TO.bubble('SCATTER!', 64, tail='right')), 700, 640, pop(t, T('split')))
        headline(img, 'OPEN FIRE!', t, T('soldiers') - 0.1, (255, 200, 80), 110) if t < T('emus', 2) else None
    # ===== 7. PLAN B: the water hole... and the gun jams =====
    elif t < T('Plan', 2) - 0.1:
        fire = T('fires') - 0.1 <= t < T('jams') - 0.2; jam = t >= T('jams') - 0.2
        img = push(bg('water'), t, T('Plan') - 0.1, T('Plan', 2), 1.0, 1.06, 0.5, 0.6, shake=5 if fire else 0)
        n = int(14 * clamp((t - T('Hundreds') + 0.3) / 1.4))
        for i in range(n):
            leave = jam and t > T('jams') + 0.3; kx = (t - T('jams') - 0.3) * 260 if leave else 0
            x = 960 - (i % 7) * 120 + kx + (0 if leave else -60 * clamp((t - T('Hundreds')) / 1.5)); y = 1150 + (i // 7) * 120 + (i % 2) * 30
            emu_at(img, x, y, t, 0.7, 'run' if leave else ('peck' if i % 3 == 0 else 'stand'), 'smug' if leave else 'normal', speed=10 if leave else 5, seed=i, flip=False)
        gunner_at(img, 300, 1600, t, fire, jam, 'shock' if jam else 'neutral')
        bullets(img, t, 520, 1470, T('fires') - 0.1, T('jams') - 0.2, dirs=(-0.2, -0.28))
        pill(img, (W // 2, 300), 'PLAN B: AMBUSH', (40, 90, 160), size=58, sc=pop(t, T('Plan') - 0.1))
        if t >= T('jams') - 0.2:
            pill(img, (W // 2, 440), 'click... click...', (30, 30, 34), size=54, sc=pop(t, T('jams') - 0.2))
            stamp(img, 'JAMMED', t, T('jams'), (220, 30, 40), y=850, size=150, rot=-8)
    # ===== 8. PLAN C: gun on a truck, emus are faster =====
    elif t < T('After') - 0.2:
        t0 = T('Plan', 2) - 0.1; u = t - t0
        base = bg('field2'); off = int((u * 520) % W)
        strip = Image.new('RGB', (W, H)); strip.paste(base.crop((off, 0, W, H)), (0, 0)); strip.paste(base.crop((0, 0, off, H)), (W - off, 0))
        img = strip.convert('RGBA')
        ph = int(u * 16) % 6; fire = u > 1.2 and int(u * 10) % 3 != 0
        paste(img, art(f'truck{ph}_{fire}', lambda: EA.truck(ph, 640, fire)), 380, 1330)
        for i in range(5):
            x = 300 + u * 150 * (1.2 + 0.25 * i) + i * 60; y = 1200 + (i % 2) * 120
            emu_at(img, x, y, t, 0.75, 'run', 'smug' if t > T('faster') else 'normal', speed=20, seed=i)
        pill(img, (W // 2, 300), 'PLAN C: TRUCK', (40, 90, 160), size=58, sc=pop(t, t0))
        if t >= T('faster') - 0.1: pill(img, (W // 2, 440), 'TOP SPEED: EMU 50 km/h', (230, 160, 20), (20, 20, 20), 44, pop(t, T('faster') - 0.1))
        if t >= T('truck', 2) - 0.3: paste(img, art('bub_slow', lambda: TO.bubble('Too slow!', 60, tail='left')), 760, 820, pop(t, T('truck', 2) - 0.3))
    # ===== 9. AFTER A WEEK: the numbers =====
    elif t < T('army', 3) - 0.1:
        img, cam = map_scene(t, MAPKEYS2, show_dots=False)
        img.alpha_composite(Image.new('RGBA', (W, H), (10, 15, 25, 120)))
        headline(img, 'After 1 week', t, T('After') - 0.2, size=96)
        n = int(2500 * eout((t - T('twenty-five') + 0.1) / 0.9))
        if t >= T('twenty-five') - 0.1:
            for i in range(min(8, 1 + n // 320)): paste(img, art('crate3', lambda: EA.ammo_crate(170)), 200 + (i % 4) * 150, 900 - (i // 4) * 90)
            pill(img, (W // 2, 1080), f'{n:,} BULLETS', (60, 70, 50), size=64, sc=pop(t, T('twenty-five') - 0.1))
        if t >= T('few') - 0.2:
            pill(img, (W // 2, 1250), 'EMUS DOWN: a few dozen', (120, 80, 40), size=52, sc=pop(t, T('few') - 0.2))
            for i in range(6): emu_at(img, 180 + i * 145, 1500, t, 0.55, 'cheer', 'happy', speed=8, seed=i)
    # ===== 10. DECEMBER: mission called off, bounty =====
    elif t < T('history') - 0.4:
        img = push(bg('office'), t, T('army', 3) - 0.1, T('history'), 1.0, 1.05, 0.5, 0.6)
        tk = 0; paste(img, art('min_w', lambda: EA.minister(0, 'worried', 620)), 520, 900); desk_cover(img)
        paste(img, art('cal', lambda: EA.calendar('DEC', 260)), 860, 1080, pop(t, T('December') - 0.1))
        if t >= T('called') - 0.1: stamp(img, 'MISSION CANCELLED', t, T('called') - 0.1, (200, 30, 40), y=780, size=96, rot=-7)
        if t >= T('farmers', 1) - 0.2:
            paste(img, art('farmH', lambda: EA.farmer(0, 'happy', 380)), 220, 1520, pop(t, T('farmers', 1) - 0.2))
            paste(img, art('coins', lambda: EA.coins(220)), 420, 1600, pop(t, T('bounty') - 0.1))
            pill(img, (W // 2, 230), 'BOUNTY: paid per emu', (200, 160, 30), (20, 20, 20), 50, pop(t, T('bounty') - 0.1))
    # ===== 11. THE GREAT EMU WAR: final score =====
    else:
        img = push(bg('field'), t, T('history') - 0.4, END, 1.0, 1.06, 0.5, 0.6)
        for i in range(7): emu_at(img, 110 + i * 145, 1150 + (i % 2) * 60, t, 0.8, 'cheer', 'happy', speed=9, seed=i)
        for i in range(3): marcher_at(img, 200 + i * 300, 1600, 0, 0.9, seed=i)
        if t < T('Final') - 0.1: stamp(img, 'THE GREAT EMU WAR', t, T('Great') - 0.1, (240, 190, 60), y=520, size=100, rot=-4)
        if t >= T('Final') - 0.1: paste(img, art('score0', lambda: EA.scoreboard(1, 0, 760)), W // 2, 560, pop(t, T('Final') - 0.1))
    subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 10, int(W * t / END), H], fill=(240, 175, 20, 255))
    return img.convert('RGB')
def _lg():
    s, c = EA._surf(360, 160); EA.lewis_gun(c, 140, 140, 0.8); return EA.sticker(EA._pil(s), ow=4)
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): frame(tt).resize((360, 640)).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(round(a * FPS)), int(round(min(b, END) * FPS))):
            enc.stdin.write(np.asarray(frame(fi / FPS)).tobytes())
        enc.stdin.close(); enc.wait()
