"""AMOC reel: crisp Blue Marble globe + glowing animated currents (El Nino reference style). usage: python3 edit.py OUT.mp4 [t0 t1] | frames PREFIX t..."""
import sys, os, json, math, subprocess, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import earth as E, fx as X, toons as TO
from earth import Camera as Cm
R = E.R; W, H, FPS = 1080, 1920, 30
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json')); END = round(WORDS[-1]['e'] + 1.6, 2)
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
def win(t, a, b, f=0.3): return clamp((t - a) / f) * clamp((b - t) / f)
ART = {}
def art(k, fn):
    if k not in ART: ART[k] = fn()
    return ART[k]
def paste(img, im, cx, cy, sc=1.0, alpha=1.0):
    if sc <= 0.01 or alpha <= 0.01: return
    i = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC) if abs(sc - 1) > 0.01 else im
    if alpha < 1: i = i.copy(); i.putalpha(i.split()[3].point(lambda v: int(v * alpha)))
    img.alpha_composite(i, (int(cx - i.width / 2), int(cy - i.height / 2)))
SLOTS = []
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=44, sc=1.0):
    if sc <= 0.02: return
    def mk():
        f = F('SemiBold', size); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
        im = Image.new('RGBA', (int(tw + 52), int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], int(size * 0.8), fill=bg + (235,)); d.text((im.width / 2, im.height / 2), txt, font=f, fill=fg, anchor='mm'); return im
    im = art(('pill', txt, bg, fg, size), mk); x = min(max(xy[0], im.width * sc / 2 + 24), W - im.width * sc / 2 - 24); y = min(max(xy[1], 150), 1690)
    for (ax, ay, aw, ah) in SLOTS:
        if abs(x - ax) < (aw + im.width * sc) / 2 and abs(y - ay) < (ah + im.height * sc) / 2 + 6: y = ay + (ah + im.height * sc) / 2 + 10
    SLOTS.append((x, y, im.width * sc, im.height * sc)); paste(img, im, x, y, sc)
def glowtext(img, xy, txt, size, col=(255, 255, 255), glow=(90, 140, 255), a=1.0, f='Bold'):
    if a <= 0.01: return
    fo = F(f, size); lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text(xy, txt, font=fo, fill=glow + (int(255 * a),), anchor='mm', stroke_width=10, stroke_fill=glow + (int(255 * a),)); lay = lay.filter(ImageFilter.GaussianBlur(18))
    img.alpha_composite(lay); img.alpha_composite(lay)
    lay2 = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay2).text(xy, txt, font=fo, fill=col + (int(255 * a),), anchor='mm', stroke_width=3, stroke_fill=(30, 30, 60, int(200 * a))); img.alpha_composite(lay2)
# ---------------- geography ----------------
WARM = X.slerp_path([(-90, 25), (-84, 24.5), (-80.2, 26.5), (-77, 32), (-72, 37), (-62, 40), (-48, 43), (-35, 48), (-22, 52), (-12, 56), (-6, 60), (3, 64)])
TOLAB = X.slerp_path([(-30, 51), (-38, 56), (-47, 59)])
DEEP = X.slerp_path([(-50, 57), (-53, 50), (-61, 41), (-67, 31), (-60, 16), (-46, 1), (-36, -12)])
SINKS = [(-50, 58.5), (-3, 68)]
LONDON, CALGARY = (-0.13, 51.5), (-114.07, 51.05)
KEYS = [(0, Cm(-40, 38, 14500, 8, 0)), (T('And') - 0.2, Cm(-40, 40, 13800, 10, 0)), (T('You') - 0.2, Cm(-78, 30, 5600, 30, -5)), (T('north') + 0.2, Cm(-68, 36, 6400, 30, -5)),
        (T('Europe', 2) + 0.2, Cm(-32, 47, 7600, 26, 0)), (T('London') - 0.2, Cm(-57, 51, 10800, 14, 0)), (T('Near') - 0.2, Cm(-38, 57, 6300, 30, 0)),
        (T('But') - 0.2, Cm(-38, 61, 4600, 36, 0)), ((T('weakens') - 0.2) - 0.4, Cm(-30, 32, 14500, 8, 0)), ((T('happened') - 0.15) - 0.2, Cm(-35, 48, 14000, 8, 0)),
        (T('Today') - 0.2, Cm(-40, 45, 12500, 10, 0)), (END, Cm(-40, 45, 11500, 12, 0))]
def cam_at(t):
    for (t0, a), (t1, b) in zip(KEYS, KEYS[1:]):
        if t < t1: return a.lerp(b, ease((t - t0) / (t1 - t0)))
    return KEYS[-1][1]
def P(cam, lon, lat): x, y, ok = cam.project(np.array([lon]), np.array([lat]), W, H); return float(x[0]), float(y[0])
def belt_speed(t):
    if t < T('slowing') - 0.2: return 1.0
    if t < T('And'): return max(0.15, 1 - (t - T('slowing') + 0.2) / 1.0)
    if t < T('slows'): return 0.8
    if t < T('Today'): return max(0.25, 0.8 - (t - T('slows')) / 1.2)
    return max(0.05, 0.25 - (t - T('Today')) / 8)
_ANG = {}
def belt_angle(t):
    k = round(t * FPS); a = 0.0
    if k in _ANG: return _ANG[k]
    for i in range(k + 1): a += belt_speed(i / FPS) * 0.35
    _ANG[k] = a; return a
GROUPS, cur = [], []
for w in WORDS:
    cur.append(w)
    if len(cur) == 4 or w['w'][-1] in '.?:!,': GROUPS.append(cur); cur = []
if cur: GROUPS.append(cur)
def subtitle(img, t):
    for g in GROUPS:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.15:
            txt = ' '.join(x['w'] for x in g); f = F('SemiBold', 44); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle([W / 2 - tw / 2 - 26, 1765, W / 2 + tw / 2 + 26, 1838], 18, fill=(0, 0, 0, 110))
            d.text((W / 2, 1801), txt, font=f, fill=(255, 255, 255, 255), anchor='mm'); img.alpha_composite(lay); break
EMO = ((T('weakens') - 0.2) - 0.35, T('Northern') + 0.25)
def frame(t):
    SLOTS.clear()
    if EMO[0] <= t < EMO[1]:   # cutaway: the Earth blows its top
        u = (t - EMO[0]) / (EMO[1] - EMO[0]); img = Image.new('RGBA', (W, H), (10, 30, 40, 255))
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([140, 520, 940, 1320], fill=(40, 140, 160, 255)); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
        e = X.earth_emoji(min(1, u * 1.15), 700); paste(img, e, W // 2, 900)
        subtitle(img, t); return img.convert('RGB')
    cam = cam_at(t); img = E.render(cam, W, H).convert('RGBA')
    gs = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); gl = cairo.Context(gs)
    cs = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); cr = cairo.Context(cs); cr.set_line_join(cairo.LINE_JOIN_ROUND)
    hist = (T('happened') - 0.15) - 0.2 <= t < T('Today') - 0.2
    sp = 1.0 if t < T('slows') else max(0.25, 1 - (t - T('slows')) / 1.5)
    # ---------- hook glow: faint warm band behind the belt ----------
    if t < T('You') - 0.2:
        X.stream(gl, cr, cam, WARM, t, 1.0, (1, 0.35, 0.3), 30, 1.0 * belt_speed(t), 0.55 * win(t, 0.4, T('You') - 0.2), dash=True)
    # ---------- warm current ----------
    if t >= T('Warm') - 0.1 and not hist:
        fr = ease((t - T('Warm') + 0.1) / (T('Europe', 2) - T('Warm') + 0.4)); a = 1.0 if t < T('Today') else 0.55 + 0.25 * math.sin(t * 4)
        X.stream(gl, cr, cam, WARM, t, fr, (1, 0.33, 0.28), 40, sp, a)
        if fr > 0.4 and t < (T('weakens') - 0.2): X.text_along(cr, cam, WARM, 'Gulf Stream', 0.2, 46, alpha=clamp((fr - 0.4) / 0.2))
    if t >= T('cools') - 0.3 and not hist:
        X.stream(gl, cr, cam, TOLAB, t, ease((t - T('cools') + 0.3) / 1.0), (1, 0.45, 0.35), 26, sp, 0.9)
    if t >= T('flows', 2) - 0.2 and not hist:
        fr = ease((t - T('flows', 2) + 0.2) / 1.6); X.stream(gl, cr, cam, DEEP, t, fr, (0.2, 0.55, 1.0), 28, sp, 0.95)
        if fr > 0.5 and t < (T('weakens') - 0.2): X.text_along(cr, cam, DEEP, 'cold, deep return', 0.25, 40, alpha=clamp((fr - 0.5) / 0.2))
    # sinking vortices
    if t >= T('sinks') - 0.2 and not hist:
        st = 1.0 if t < T('sink', 1) else max(0.3, 1 - (t - T('sink', 1)) / 1.2)
        for lo, la in SINKS: x, y = P(cam, lo, la); X.vortex(cr, x, y, t, 70 * clamp((t - T('sinks') + 0.2) / 0.4), (0.6, 0.9, 1.0), st)
    # freshwater from Greenland
    if t >= T('melting') - 0.2 and not hist:
        k = ease((t - T('fresh') + 0.2) / 1.6)
        X.blob(gl, cam, -42, 70, 7, (1, 1, 1), 0.35 + 0.25 * math.sin(t * 6))
        if k > 0:
            for lo, la, r in ((-45, 61, 4), (-38, 63, 5), (-30, 62, 5), (-50, 58, 4)): X.blob(gl, cam, lo, la, r * k, (0.7, 0.95, 1.0), 0.6 * k)
    # impacts
    if T('Northern') <= t < (T('happened') - 0.15) - 0.2:
        if t >= T('colder') - 0.2: X.blob(gl, cam, 12, 55, 9, (0.4, 0.75, 1.0), 0.55 * eout((t - T('colder') + 0.2) / 0.5))
        if t >= T('rise') - 0.2: X.blob(gl, cam, -75, 37, 5, (0.2, 0.5, 1.0), 0.6 * eout((t - T('rise') + 0.2) / 0.5))
        if t >= T('shift') - 0.2:
            X.blob(gl, cam, 2, 12, 8, (0.3, 0.6, 1.0), 0.5 * eout((t - T('shift') + 0.2) / 0.5)); X.blob(gl, cam, -60, -4, 9, (0.3, 0.6, 1.0), 0.5 * eout((t - T('shift') + 0.2) / 0.5))
    # history: ice sheets
    if hist and t >= T('plunged') - 0.3:
        k = ease((t - T('plunged') + 0.3) / 2.2)
        for lo, la, r in ((-95, 58, 18), (-75, 52, 12), (-110, 55, 12), (15, 62, 11), (0, 56, 6), (30, 64, 10)): X.blob(gl, cam, lo, la, r * k, (0.92, 0.97, 1.0), 0.7 * k)
    # London vs Calgary latitude line
    if T('London') - 0.2 <= t < T('Near') - 0.2 and t >= T('Calgary') - 0.2:
        x1, y1 = P(cam, *CALGARY); x2, y2 = P(cam, *LONDON); pts = X.slerp_path([CALGARY, (-60, 51.3), LONDON]); xs, ys, ok = X.proj_path(cam, pts)
        xc, yc, _ = X.cut(xs, ys, ease((t - T('Calgary') + 0.2) / 0.9)); cr.new_path(); cr.move_to(xc[0], yc[0]); [cr.line_to(a, b) for a, b in zip(xc[1:], yc[1:])]
        cr.set_source_rgba(1, 1, 1, 0.9); cr.set_dash([14, 12]); cr.set_line_width(4); cr.stroke(); cr.set_dash([])
    X.apply_glow(img, gs, 14); img.alpha_composite(TO._pil(cs))
    # ---------- icons & labels ----------
    if T('giant') - 0.1 <= t < T('You') - 0.2 or T('Today') - 0.2 <= t:
        x, y = P(cam, -42, 33); t0 = T('giant') - 0.1 if t < T('You') else T('Today') - 0.2
        paste(img, X.conveyor(belt_angle(t), 420, warn=t >= T('Today')), x, y, pop(t, t0, 0.45))
        if T('slowing') - 0.1 <= t < T('And') + 0.6: pill(img, (x, y - 190), 'SLOWING DOWN', (200, 40, 40), size=42, sc=pop(t, T('slowing') - 0.1))
    if T('called') - 0.1 <= t < T('You') - 0.1:
        glowtext(img, (W // 2, 520), 'AMOC', 170, a=eout((t - T('called') + 0.1) / 0.3) * clamp((T('You') - 0.1 - t) / 0.25))
        pill(img, (W // 2, 660), 'Atlantic Meridional Overturning Circulation', (20, 40, 80), size=30, sc=pop(t, T('AMOC')))
    if T('Gulf') - 0.1 <= t < T('London') - 0.2: x, y = P(cam, -90, 23.5); pill(img, (x, y + 70), 'Gulf of Mexico', (20, 40, 80), size=38, sc=pop(t, T('Gulf') - 0.1))
    if T('U.S.') - 0.1 <= t < T('London') - 0.2: x, y = P(cam, -82, 38); pill(img, (x - 40, y), 'U.S. East Coast', (20, 40, 80), size=38, sc=pop(t, T('U.S.') - 0.1))
    if T('Europe', 2) - 0.2 <= t < T('Near') - 0.2: x, y = P(cam, 2, 50); pill(img, (x, y - 40), 'Europe', (20, 40, 80), size=40, sc=pop(t, T('Europe', 2) - 0.2))
    if T('London') - 0.1 <= t < T('Near') - 0.2:
        x, y = P(cam, *LONDON); paste(img, art('thL', lambda: X.thermo('+5°C', True, 110, 0.6)), min(x, W - 200), y - 200, pop(t, T('London') - 0.1)); pill(img, (min(x, W - 120), y + 60), 'London', (20, 40, 80), size=40)
        if t >= T('Calgary') - 0.2: x, y = P(cam, *CALGARY); paste(img, art('thC', lambda: X.thermo('-7°C', False, 110, 0.15)), max(x, 200), y - 200, pop(t, T('Calgary') - 0.2)); pill(img, (max(x, 120), y + 60), 'Calgary', (20, 40, 80), size=40)
        if t >= T('farther') - 0.2: pill(img, (W // 2, 330), 'average January temperature', (20, 40, 80), size=34, sc=pop(t, T('farther') - 0.2))
    if T('Greenland') - 0.1 <= t < (T('weakens') - 0.2) - 0.4: x, y = P(cam, -41, 72); pill(img, (x, y), 'Greenland', (20, 40, 80), size=40, sc=pop(t, T('Greenland') - 0.1))
    if T('sinks') <= t < T('But') - 0.2: x, y = P(cam, -50, 58.5); pill(img, (x, y + 110), 'sinks deep', (20, 60, 120), size=36, sc=pop(t, T('sinks')))
    if T('Around') - 0.1 <= t < T('But') - 0.1: pill(img, (W // 2, 330), 'around and around', (20, 40, 80), size=46, sc=pop(t, T('Around') - 0.1))
    if T('melting') <= t < (T('weakens') - 0.2) - 0.4:
        if t >= T('fresh') - 0.1: pill(img, (W // 2, 330), 'fresh meltwater', (30, 110, 160), size=44, sc=pop(t, T('fresh') - 0.1))
        if t >= T('lighter') - 0.1: pill(img, (W // 2, 440), 'lighter: does not sink', (30, 110, 160), size=40, sc=pop(t, T('lighter') - 0.1))
        if t >= T('slows') - 0.2: x, y = P(cam, -36, 50); paste(img, X.conveyor(belt_angle(t), 330, warn=True), x, y, pop(t, T('slows') - 0.2, 0.4))
    if T('Northern') <= t < (T('happened') - 0.15) - 0.2:
        if t >= T('colder') - 0.2: x, y = P(cam, 12, 56); paste(img, art(f'snow{int(t * 10) % 6}', lambda: X.cloud('snow', 200, t)), x, y - 80, pop(t, T('colder') - 0.2)); pill(img, (x, y + 50), 'colder winters', (30, 80, 160), size=34, sc=pop(t, T('colder')))
        if t >= T('rise') - 0.2: x, y = P(cam, -76, 37); paste(img, art(f'wave{int(t * 10) % 6}', lambda: X.wave(190, t)), x - 30, y - 60, pop(t, T('rise') - 0.2)); pill(img, (x - 20, y + 70), 'faster sea level rise', (30, 80, 160), size=32, sc=pop(t, T('rise')))
        if t >= T('shift') - 0.2:
            for lo, la, lab in ((2, 13, 'Africa'), (-60, -4, 'South America')):
                x, y = P(cam, lo, la); paste(img, art(f'rain{int(t * 10) % 6}', lambda: X.cloud('rain', 170, t)), x, y - 70, pop(t, T('shift') - 0.2)); pill(img, (x, y + 60), lab, (30, 80, 160), size=32, sc=pop(t, T('shift')))
    if T('Today') - 0.2 <= t:
        if t >= T('weakest') - 0.2: glowtext(img, (W // 2, 330), 'WEAKEST IN 1,000 YEARS', 72, glow=(255, 80, 60), a=eout((t - T('weakest') + 0.2) / 0.3))
        if t >= T('tipping') - 0.2: glowtext(img, (W // 2, 620), 'TIPPING POINT?', 112, col=(255, 230, 230), glow=(255, 40, 40), a=eout((t - T('tipping') + 0.2) / 0.25))
        if t < T('weakest') - 0.2: pill(img, (W // 2, 330), 'some studies suggest...', (20, 40, 80), size=40, sc=pop(t, T('some')))
    if hist:
        img = X.film(img, t, eout((t - (T('happened') - 0.15) + 0.2) / 0.4) * clamp((T('Today') - 0.2 - t) / 0.3))
        if t >= T('12,900') - 0.2: glowtext(img, (W // 2, 420), '12,900 YEARS AGO', 82, col=(255, 245, 225), glow=(200, 150, 90), a=eout((t - T('12,900') + 0.2) / 0.3))
        if t >= T('ice') - 0.2: pill(img, (W // 2, 560), 'near ice age cold', (60, 90, 120), size=44, sc=pop(t, T('ice') - 0.2))
        if t >= T('thousand') - 0.2: pill(img, (W // 2, 680), 'for 1,000+ years', (60, 90, 120), size=44, sc=pop(t, T('thousand') - 0.2))
    subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 9, int(W * t / END), H], fill=(255, 110, 90, 255))
    return img.convert('RGB')
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): frame(tt).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        a, b = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (0, END)
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(round(a * FPS)), int(round(min(b, END) * FPS))):
            enc.stdin.write(np.asarray(frame(fi / FPS)).tobytes())
        enc.stdin.close(); enc.wait()
