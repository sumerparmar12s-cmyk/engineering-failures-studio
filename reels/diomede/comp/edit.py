"""Tomorrow Island / Yesterday Island (Diomedes), Point Roberts look on the self-drawn globe. usage: python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import shape, box
import globe3d as G, toons as TO, toons3 as T3
from globe3d import Camera as Cm
R = G.R; W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json')); END = round(WORDS[-1]['e'] + 1.1, 2)
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
def F(name, size):
    p = {'play': 'PlayfairDisplay.ttf'}.get(name)
    f = ImageFont.truetype(f'{FONTS}/{p}', size) if p else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
    if name == 'play':
        try: f.set_variation_by_axes([800])
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
LANDP = G.land_polys()
def pick(lo, la): return [p for p in LANDP if p.contains(shape({'type': 'Point', 'coordinates': [lo, la]}))][0]
BIG = pick(-169.05, 65.79); LITTLE = pick(-168.925, 65.755)
RED, BLUE = (0.86, 0.15, 0.2), (0.2, 0.42, 0.95)
def proj(cam, pts):
    lo = np.array([p[0] for p in pts]); la = np.array([p[1] for p in pts]); x, y, ok = cam.project(lo, la, W, H); return list(zip(x, y)), ok
def geo(cam, lo, la): P, ok = proj(cam, [(lo, la)]); return P[0]
def cpoly(c, cam, g, fill, alpha, lw=5):
    if alpha <= 0.01: return
    pts, ok = proj(cam, list(g.exterior.coords))
    c.new_path(); [(c.move_to if i == 0 else c.line_to)(x, y) for i, (x, y) in enumerate(pts)]; c.close_path()
    c.set_source_rgba(*fill, alpha); c.fill_preserve(); c.set_source_rgba(1, 1, 1, min(1, alpha * 1.6)); c.set_line_width(lw); c.stroke()
def cline(c, cam, pts, col, lw, frac=1.0, dash=None):
    P, ok = proj(cam, pts)
    if frac < 1: n = max(2, int(len(P) * frac)); P = P[:n]
    c.new_path(); c.move_to(*P[0]); [c.line_to(*p) for p in P[1:]]
    if dash: c.set_dash(dash)
    c.set_source_rgba(*col, 0.95); c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); c.stroke(); c.set_dash([])
CLOSE_A = Cm(-168.99, 65.776, 34, 40, 0); CLOSE_B = Cm(-168.99, 65.776, 28, 46, 5)
KEYS = [(0.0, CLOSE_A), (T('Line') - 0.4, CLOSE_B), (T('between') + 0.2, Cm(-169.0, 65.6, 330, 32, 0)), (T('Locals') + 0.1, Cm(-169.0, 65.62, 360, 30, 0)),
        (T('Tomorrow', 2) + 0.2, Cm(-168.99, 65.776, 30, 44, 6)), (END, Cm(-168.99, 65.776, 34, 40, 10))]
def cam_at(t):
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t < t1:
            u = (t - t0) / (t1 - t0); c = a.lerp(b, ease(u))
            return c
    return KEYS[-1][1]
DATELINE = [(-168.977, 72.0 - i * 0.25) for i in range(49)]
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15: stext(img, (W // 2, 1660), ' '.join(x['w'] for x in g), F('SemiBold', 44)); break
def frame(t):
    cam = cam_at(t)
    img = G.render(cam, W, H).filter(ImageFilter.UnsharpMask(radius=1.4, percent=50, threshold=2)).convert('RGBA')
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    close = cam.dist < 80
    if t >= T('Russia') - 0.2: cpoly(c, cam, BIG, RED, 0.5 * eout((t - T('Russia') + 0.2) / 0.4))
    if t >= T('America') - 0.2: cpoly(c, cam, LITTLE, BLUE, 0.55 * eout((t - T('America') + 0.2) / 0.4))
    if close and 0.8 <= t < T('Russia'):
        cline(c, cam, [(-168.995 + 0.0043 * i, 65.772 - 0.0012 * i) for i in range(11)], (1, 1, 1), 6, frac=eout((t - 0.8) / 0.8), dash=[14, 10])
    if t >= T('International') - 0.2:
        cline(c, cam, DATELINE, (1, 0.85, 0.2), 8, frac=eout((t - T('International') + 0.2) / 1.0), dash=[22, 14])
    img.alpha_composite(TO._pil(s))
    # labels & stickers
    if close and 1.0 <= t < T('Russia'):
        x, y = geo(cam, -168.973, 65.766); pill(img, (x, y - 90), '2.5 miles', (240, 175, 20), (20, 20, 20), 50, pop(t, 1.1))
    if T('almost') <= t < T('Russia') + 0.2:
        paste(img, art('calR', lambda: T3.calendar('TUESDAY', (0.85, 0.15, 0.2), 240)), 300, 1250, pop(t, T('whole')))
        paste(img, art('calU', lambda: T3.calendar('MONDAY', (0.2, 0.42, 0.95), 240)), 780, 1250, pop(t, T('day')))
        if t >= T('day'): stext(img, (W // 2, 300), 'Almost a day apart', F('play', 76), a=eout((t - T('day')) / 0.3))
    if T('Russia') - 0.2 <= t < T('International') - 0.3:
        x, y = geo(cam, -169.05, 65.79); pill(img, (x, y - 260), 'RUSSIA', (215, 40, 55), size=56, sc=pop(t, T('Russia') - 0.2))
        paste(img, art('ru', lambda: T3.local('ru', 'happy', 330)), 260, 1270, pop(t, T('Russia')))
        if t >= T('tomorrow') - 0.1: pill(img, (260, 1500), 'TOMORROW', (215, 40, 55), size=46, sc=pop(t, T('tomorrow') - 0.1))
    if T('America') - 0.2 <= t < T('International') - 0.3:
        x, y = geo(cam, -168.925, 65.755); pill(img, (x, y - 140), 'USA', (40, 90, 220), size=56, sc=pop(t, T('America') - 0.2))
        paste(img, art('us', lambda: T3.local('us', 'happy', 330)), 820, 1270, pop(t, T('America')))
        if t >= T('yesterday') - 0.1: pill(img, (820, 1500), 'YESTERDAY', (40, 90, 220), size=46, sc=pop(t, T('yesterday') - 0.1))
    if T('International') - 0.2 <= t < T('Tomorrow', 2) - 0.3:
        x, y = geo(cam, -168.977, 66.6); pill(img, (x, y), 'International Date Line', (240, 175, 20), (20, 20, 20), 46, pop(t, T('International')))
        if t >= T('between'): x, y = geo(cam, -169.0, 65.75); pill(img, (x - 240, y + 120), 'TUESDAY', (215, 40, 55), size=40, sc=pop(t, T('between'))); pill(img, (x + 240, y + 120), 'MONDAY', (40, 90, 220), size=40, sc=pop(t, T('between') + 0.15))
    if T('Tomorrow', 2) - 0.3 <= t < T('So'):
        x, y = geo(cam, -169.05, 65.79); pill(img, (x, y - 260), 'Tomorrow Island', (215, 40, 55), size=50, sc=pop(t, T('Tomorrow', 2) - 0.1))
        x, y = geo(cam, -168.925, 65.755); pill(img, (x - 40, y - 150), 'Yesterday Island', (40, 90, 220), size=50, sc=pop(t, T('Yesterday', 2) - 0.1))
    if t >= T('So') - 0.1:
        bob = 10 * math.sin(t * 9)
        paste(img, art('usL', lambda: T3.local('us', 'laugh', 340)), 800, 1360 + bob, pop(t, T('So') - 0.1))
        paste(img, art('ruH', lambda: T3.local('ru', 'happy', 340)), 280, 1360 - bob, pop(t, T('So')))
        if t >= T('wave'): paste(img, art('bu', lambda: TO.bubble('Hi, future!', 52, tail='right')), 760, 1020, pop(t, T('wave') + 0.1))
        if t >= T('future') - 0.1: paste(img, art('br', lambda: TO.bubble('Hi, past!', 52)), 330, 1020, pop(t, T('future') - 0.1))
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
        enc.stdin.close(); enc.wait()
