"""Alaska explainer reel, fully self-drawn (procedural map + cairo cartoons). usage: python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import mapart as MA, toons as TO
R = MA.R; W, H, FPS = 1080, 1920, 30; END = 40.0
WORDS = json.load(open(f'{R}/vo/vo.mp3.words.json'))
SH = MA.load_shapes(); CANVAS = MA.build_canvas(SH)
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
def F(name, size):
    p = {'play': 'PlayfairDisplay.ttf', 'oswald': 'Oswald.ttf', 'bebas': 'BebasNeue-Regular.ttf'}.get(name)
    f = ImageFont.truetype(f'{FONTS}/{p}', size) if p else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
    try:
        if name == 'play': f.set_variation_by_axes([800])
        if name == 'oswald': f.set_variation_by_axes([600])
    except Exception: pass
    return f
clamp = lambda x, a=0, b=1: max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eout(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x):   # ease-out-back (pop)
    x = clamp(x); c1 = 1.9; return 1 + (c1 + 1) * (x - 1) ** 3 + c1 * (x - 1) ** 2
# ---------- cached art ----------
ART = {}
def art(key, fn):
    if key not in ART: ART[key] = fn()
    return ART[key]
def paste(img, im, cx, cy, sc=1.0, rot=0, alpha=1.0):
    if sc <= 0.01 or alpha <= 0.01: return
    w, h = max(1, int(im.width * sc)), max(1, int(im.height * sc)); i = im.resize((w, h), Image.BICUBIC)
    if rot: i = i.rotate(rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1: a = i.split()[3].point(lambda v: int(v * alpha)); i.putalpha(a)
    img.alpha_composite(i, (int(cx - i.width / 2), int(cy - i.height / 2)))
def popin(t, t0, d=0.35): return back((t - t0) / d) if t >= t0 else 0
# ---------- island close-up (drawn once) ----------
def islands_img():
    rng = np.random.default_rng(7); img = np.zeros((H, W, 3), np.float32)
    n = MA.noise(H, W, 11, 6, 3); img[:] = np.array([20, 58, 92]) * (0.85 + 0.3 * n[..., None])
    yy, xx = np.mgrid[0:H, 0:W]
    def blob(cx, cy, rx, ry, seed):
        a = np.arctan2((yy - cy) / ry, (xx - cx) / rx); r = np.hypot((xx - cx) / rx, (yy - cy) / ry)
        k = np.zeros_like(a)
        g = np.random.default_rng(seed)
        for f in range(2, 9): k += g.normal(0, 0.06 / f ** 0.6) * np.cos(f * a + g.random() * 6.28)
        return r < 1 + k
    m = blob(330, 960, 210, 420, 3) | blob(820, 900, 150, 170, 5)
    mi = Image.fromarray((m * 255).astype(np.uint8)); bl = np.asarray(mi.filter(ImageFilter.GaussianBlur(40)), np.float32) / 255
    img = img * (1 - bl[..., None] * 0.6) + np.array([60, 140, 150]) * bl[..., None] * 0.6
    t = MA.noise(H, W, 12, 6, 6); ridge = 1 - np.abs(MA.noise(H, W, 13, 6, 8) * 2 - 1)
    land = np.array([96, 120, 66]) * (1 - ridge[..., None] * 0.5) + np.array([150, 132, 96]) * ridge[..., None] * 0.5
    land *= (0.85 + 0.3 * t[..., None])
    sn = np.clip((ridge - 0.9) * 3, 0, 1)[..., None] * 0.5; land = land * (1 - sn) + 220 * sn
    img = np.where(m[..., None], land, img)
    e = np.asarray(mi.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(2)), np.float32)[..., None] / 255
    img = img * (1 - e * 0.7) + 250 * e * 0.7
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
ISL = None
# ---------- map overlays with cairo (antialiased polygons) ----------
def cairo_layer():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); return s, c
def cpil(s): return TO._pil(s)
def poly(c, cam, rings, fill, alpha, stroke=(1, 1, 1), lw=4, salpha=0.95, pts_override=None):
    c.new_path()
    for r in (pts_override or rings):
        for i, (x, y) in enumerate(r):
            X, Y = cam.xy(x, y)
            (c.move_to if i == 0 else c.line_to)(X, Y)
        c.close_path()
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    c.set_source_rgba(*fill, alpha); c.fill_preserve(); c.set_source_rgba(*stroke, salpha); c.set_line_width(lw); c.stroke()
def truesize(rings, src_c, dst_c, k):
    """move a shape at true size from src centre to dst centre (k: 0 = original place, 1 = moved)"""
    out = []
    for r in rings:
        rr = []
        for lon, lat in r:
            xkm = (lon - src_c[0]) * 111.32 * math.cos(math.radians(lat)); ykm = (lat - src_c[1]) * 110.57
            lat2 = dst_c[1] + ykm / 110.57; lon2 = dst_c[0] + xkm / (111.32 * math.cos(math.radians(lat2)))
            rr.append((lon + (lon2 - lon) * k, lat + (lat2 - lat) * k))
        out.append(rr)
    return out
AK = SH['S:Alaska']; TX = SH['S:Texas']; RU = SH['C:Russia']; AK_C = (MA.wl(-152.5), 63.5); TX_C = (MA.wl(-99.3), 31.3)
L48 = [r for k, v in SH.items() if k.startswith('S:') and k not in ('S:Alaska', 'S:Hawaii') for r in v]
# ---------- text helpers ----------
def shadow_text(img, xy, txt, f, fill=(255, 255, 255), anchor='mm', blur=6, a=1.0, stroke=0):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, int(190 * a)), anchor=anchor, stroke_width=stroke)
    lay = lay.filter(ImageFilter.GaussianBlur(blur)); d = ImageDraw.Draw(lay)
    d.text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0, int(255 * a)))
    img.alpha_composite(lay)
def tag(img, xy, txt, bg, fg=(255, 255, 255), size=52, sc=1.0):
    if sc <= 0.02: return
    f = F('oswald', int(size)); d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10))); tw = d0.textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 64), int(size * 1.7)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], int(size * 0.5), fill=bg + (255,)); d.text((im.width / 2, im.height / 2 + 2), txt, font=f, fill=fg, anchor='mm')
    paste(img, TO.sticker(im, ow=5), xy[0], xy[1], sc)
def subtitle(img, t):
    if t >= 39.2: return
    chunk = []
    for i, w in enumerate(WORDS):
        if w['s'] - 0.05 <= t:
            idx = i
    # 4-word windows that reset on sentence ends
    groups, cur = [], []
    for w in WORDS:
        cur.append(w)
        if len(cur) == 4 or w['w'][-1] in '.?:': groups.append(cur); cur = []
    if cur: groups.append(cur)
    for g in groups:
        if g[0]['s'] - 0.05 <= t < g[-1]['e'] + 0.2:
            shadow_text(img, (W // 2, 1800), ' '.join(x['w'] for x in g), F('SemiBold', 46)); break
# ---------- scenes ----------
CAM = {'bering': MA.Cam(-171, 65.5, 16), 'ak': MA.Cam(-158, 62.5, 34), 'akwide': MA.Cam(-163, 62, 42), 'us': MA.Cam(-110, 46, 58), 'us2': MA.Cam(-106, 44, 64), 'east': MA.Cam(-80, 40, 30), 'akgold': MA.Cam(-153, 65, 24)}
def campath(t, keys):
    """keys: [(t, camname), ...] eased between consecutive keys"""
    for (t0, a), (t1, b) in zip(keys, keys[1:]):
        if t < t1: return CAM[a].lerp(CAM[b], ease((t - t0) / max(0.01, t1 - t0)))
    return CAM[keys[-1][1]]
def frame(t):
    global ISL
    if t < 6.52:   # ---------- 1. islands close-up ----------
        if ISL is None: ISL = islands_img()
        z = 1.0 + 0.06 * t / 6.5; img = ISL.resize((int(W * z), int(H * z)), Image.BICUBIC).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H)).convert('RGBA')
        s, c = cairo_layer(); p = eout((t - 0.9) / 1.0)
        if p > 0:   # distance ruler
            x0, x1, y = 545, 545 + (680 - 545) * p, 900
            c.set_source_rgba(1, 1, 1, 0.95); c.set_line_width(7); c.set_dash([18, 12]); c.move_to(x0, y); c.line_to(x1, y); c.stroke(); c.set_dash([])
            for x in (x0, x1): c.arc(x, y, 11, 0, 6.3); c.fill()
        img.alpha_composite(cpil(s))
        if t > 1.5: tag(img, (612, 820), '2.5 MILES', (240, 180, 40), (20, 20, 20), 56, popin(t, 1.5))
        if t > 3.6: paste(img, art('tsar_smug', lambda: TO.tsar('smug', 330)), 300, 1460, popin(t, 3.6)); tag(img, (330, 520), 'RUSSIA', (200, 40, 50), size=60, sc=popin(t, 3.6))
        if t > 5.3: paste(img, art('sew_happy', lambda: TO.seward('happy', 330)), 800, 1350, popin(t, 5.3)); tag(img, (820, 640), 'USA', (40, 80, 190), size=60, sc=popin(t, 5.3))
        if t < 2.9: shadow_text(img, (W // 2, 230), 'Two islands.', F('play', 92), a=eout(t / 0.3))
        if 6.2 <= t: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (t - 6.2) / 0.32))))
        return img
    if t < 18.96:  # ---------- 2. map: Russia owns Alaska, sells it ----------
        cam = campath(t, [(6.52, 'bering'), (9.0, 'ak'), (10.5, 'ak'), (12.0, 'akwide')])
        img = MA.render_bg(CANVAS, cam).convert('RGBA'); s, c = cairo_layer()
        sold = t >= 9.3
        poly(c, cam, RU, (0.85, 0.2, 0.25), 0.38)
        akcol = (0.85, 0.2, 0.25) if not sold else ((0.85, 0.2, 0.25) if (t < 9.9 and int(t * 8) % 2) else (0.2, 0.4, 0.85))
        poly(c, cam, AK, akcol, 0.42)
        img.alpha_composite(cpil(s))
        if t < 6.84: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (1 - (t - 6.52) / 0.32)))))
        X, Y = cam.xy(MA.wl(-176), 66.5); shadow_text(img, (X - 60, Y - 120), 'RUSSIA', F('play', 66))
        X, Y = cam.xy(MA.wl(-152), 64.5)
        if t < 13.6: shadow_text(img, (X, Y), 'ALASKA', F('play', 66))
        if t < 9.3: shadow_text(img, (W // 2, 260), 'Next door?', F('play', 84), a=eout((t - 6.9) / 0.3))
        if 9.3 <= t < 10.5:
            sc = popin(t, 9.35, 0.25); X, Y = cam.xy(MA.wl(-152), 63)
            st = art('sold', lambda: TO.sticker(stamp_img('SOLD!'), ow=0, shadow=False)); paste(img, st, X, Y + 140, sc * 1.0, rot=-10)
        if t >= 10.5:
            shadow_text(img, (W // 2, 250), '1867', F('play', 150), a=eout((t - 10.5) / 0.3))
            ex = 'worried' if t >= 17.6 else 'neutral'
            paste(img, art('tsar_' + ex, lambda: TO.tsar(ex, 380)), 270, 1470, popin(t, 11.95))
            for t0, txt, col, y in ((13.9, 'COLD', (70, 150, 230), 560), (14.6, 'FAR AWAY', (230, 140, 40), 680), (15.5, 'HARD TO DEFEND', (200, 60, 60), 800), (17.7, 'NEEDS CASH', (40, 150, 80), 920)):
                if t >= t0: tag(img, (W - 300 + 0 * (1 - eout((t - t0) / 0.3)), y), txt, col, size=54, sc=popin(t, t0, 0.3))
        return img
    if t < 24.28:  # ---------- 3. the phone call (deal) ----------
        cam = CAM['akwide']; img = MA.render_bg(CANVAS, cam).filter(ImageFilter.GaussianBlur(14)).convert('RGBA')
        img.alpha_composite(Image.new('RGBA', (W, H), (10, 25, 45, 110)))
        paste(img, art('tsar_happy', lambda: TO.tsar('happy', 420)), 290, 1430, popin(t, 18.96))
        paste(img, art('sew_smug', lambda: TO.seward('smug', 420)), 800, 980, popin(t, 19.1))
        if t >= 19.2: paste(img, art('b1', lambda: TO.bubble('Wanna buy\nAlaska?', 60)), 330, 960, popin(t, 19.2, 0.3))
        if t >= 19.8: paste(img, art('b2', lambda: TO.bubble('How much?', 60, tail='right')), 760, 560, popin(t, 19.8, 0.3))
        if t >= 20.3:
            v = int(7_200_000 * ease((t - 20.3) / 1.5)); shadow_text(img, (W // 2, 250), f'${v:,}', F('oswald', 118), fill=(120, 240, 140))
        if t >= 22.3:
            paste(img, art('coin', lambda: TO.coin('2¢', 230)), 820, 1500, popin(t, 22.3)); tag(img, (820, 1660), 'PER ACRE', (240, 180, 40), (20, 20, 20), 48, popin(t, 22.6))
        return img
    if t < 28.52:  # ---------- 4. people laughed -> giant fridge ----------
        if t < 27.0:
            cam = CAM['east']; img = MA.render_bg(CANVAS, cam).convert('RGBA'); s, c = cairo_layer(); poly(c, cam, L48, (0.2, 0.4, 0.85), 0.18, lw=2, salpha=0.6); img.alpha_composite(cpil(s))
            spots = [(250, 900), (520, 820), (780, 950), (380, 1120), (660, 1180), (900, 1250), (200, 1320), (500, 1400)]
            for i, (x, y) in enumerate(spots):
                t0 = 24.3 + i * 0.12
                if t >= t0:
                    bob = 10 * math.sin((t - t0) * 14 + i); paste(img, art(f'p{i % 4}', lambda: TO.person('laugh', 150, [(0.25, 0.45, 0.8), (0.8, 0.3, 0.3), (0.3, 0.65, 0.4), (0.85, 0.6, 0.2)][i % 4])), x, y + bob, popin(t, t0, 0.25))
            if t >= 24.6: shadow_text(img, (W // 2, 330), 'HA HA HA', F('oswald', 110), fill=(255, 220, 80), a=eout((t - 24.6) / 0.2))
            if t >= 25.5: tag(img, (W // 2, 560), "SEWARD'S ICEBOX", (60, 160, 220), size=66, sc=popin(t, 25.5))
        else:
            cam = CAM['ak']; img = MA.render_bg(CANVAS, cam).convert('RGBA'); s, c = cairo_layer(); poly(c, cam, AK, (0.75, 0.9, 1.0), 0.45); img.alpha_composite(cpil(s))
            X, Y = cam.xy(MA.wl(-152), 64); paste(img, art('fridge', lambda: TO.fridge(330)), X, Y - 40, popin(t, 27.1, 0.4))
            shadow_text(img, (W // 2, 260), 'A giant fridge.', F('play', 90), a=eout((t - 27.1) / 0.3))
        return img
    if t < 33.64:  # ---------- 5. bigger than Texas ----------
        cam = campath(t, [(28.52, 'us'), (30.3, 'us2')]); img = MA.render_bg(CANVAS, cam).convert('RGBA'); s, c = cairo_layer()
        poly(c, cam, L48, (1, 1, 1), 0.0, lw=2, salpha=0.35)
        poly(c, cam, TX, (0.95, 0.55, 0.15), 0.75, lw=4)
        k = ease((t - 29.4) / 1.4)
        poly(c, cam, AK, (0.2, 0.45, 0.9), 0.55, pts_override=truesize(AK, AK_C, (TX_C[0] - 2, TX_C[1] + 6), k))
        img.alpha_composite(cpil(s))
        X, Y = cam.xy(*TX_C)
        if t >= 32.2:   # Texas is sad
            s, c = cairo_layer()
            X, Y = cam.xy(MA.wl(-99.0), 30.2)
            for sx in (-1, 1): TO.ell(c, X + sx * 22, Y, 9, 12); c.set_source_rgb(0.1, 0.08, 0.08); c.fill()
            c.move_to(X - 22, Y + 38); c.curve_to(X - 10, Y + 24, X + 10, Y + 24, X + 22, Y + 38); c.set_line_width(5); c.stroke()
            ty = Y + 14 + ((t - 32.2) * 90) % 40; TO.ell(c, X - 24, ty, 6, 9); c.set_source_rgb(0.4, 0.7, 1); c.fill()
            img.alpha_composite(cpil(s)); tag(img, (W // 2, 1520), 'Sorry, Texas.', (230, 120, 30), size=58, sc=popin(t, 32.2))
        shadow_text(img, (W // 2, 250), 'Alaska vs Texas', F('play', 84), a=eout((t - 28.6) / 0.3))
        if t >= 30.4: tag(img, (W // 2, 400), 'MORE THAN 2×', (40, 90, 200), size=64, sc=popin(t, 30.4))
        return img
    if t < 36.72:  # ---------- 6. gold + oil ----------
        cam = CAM['akgold']; img = MA.render_bg(CANVAS, cam).convert('RGBA'); s, c = cairo_layer(); poly(c, cam, AK, (0.2, 0.45, 0.9), 0.25); img.alpha_composite(cpil(s))
        g = [(-165.4, 64.5), (-147.7, 64.8), (-162, 63.8), (-150, 66)]
        for i, (lo, la) in enumerate(g):
            t0 = 33.8 + i * 0.15
            if t >= t0: X, Y = cam.xy(MA.wl(lo), la); paste(img, art('nug', lambda: TO.nugget(140)), X, Y - 30 * (1 - eout((t - t0) / 0.3)), popin(t, t0, 0.3))
        if t >= 33.8: tag(img, (300, 380), 'GOLD!  1890s', (230, 170, 20), (20, 20, 20), 60, popin(t, 33.8))
        if t >= 35.4:
            X, Y = cam.xy(MA.wl(-148.4), 70.25); paste(img, art('der', lambda: TO.derrick(230)), X, Y + 60, popin(t, 35.4))
            tag(img, (760, 500), 'OIL!  1968', (30, 30, 34), size=60, sc=popin(t, 35.6))
        return img
    # ---------- 7. refund ----------
    cam = CAM['akwide']; img = MA.render_bg(CANVAS, cam).filter(ImageFilter.GaussianBlur(14)).convert('RGBA'); img.alpha_composite(Image.new('RGBA', (W, H), (40, 10, 20, 90)))
    paste(img, art('tsar_worried', lambda: TO.tsar('worried', 420)), 300, 1450, popin(t, 36.72))
    if t >= 37.0: paste(img, art('rcpt', lambda: TO.receipt(300)), 760, 1180, popin(t, 37.0), rot=8)
    if t >= 37.7: paste(img, art('b3', lambda: TO.bubble('Can we get\na refund?', 58)), 360, 900, popin(t, 37.7, 0.3))
    if t >= 38.9:
        paste(img, art('sew_laugh', lambda: TO.seward('laugh', 300)), 840, 520, popin(t, 38.9)); paste(img, art('b4', lambda: TO.bubble('Nope.', 64, tail='right')), 760, 250, popin(t, 39.0, 0.3))
    return img
def stamp_img(txt):
    f = F('oswald', 150); d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10))); tw = d0.textlength(txt, font=f)
    im = Image.new('RGBA', (int(tw + 90), 240), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle([8, 8, im.width - 8, im.height - 8], outline=(220, 30, 40, 255), width=14); d.text((im.width / 2, im.height / 2 + 4), txt, font=f, fill=(220, 30, 40, 255), anchor='mm'); return im
def full(t):
    img = frame(t); subtitle(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 12, int(W * t / END), H], fill=(240, 180, 40, 255))
    return img.convert('RGB')
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): full(tt).resize((360, 640)).save(f'{sys.argv[2]}_{tt:05.1f}.png')
    else:
        enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p', sys.argv[1]], stdin=subprocess.PIPE)
        for fi in range(int(END * FPS)):
            enc.stdin.write(np.asarray(full(fi / FPS)).tobytes())
            if fi % 150 == 0: print(f'{fi / FPS:.1f}s', flush=True)
        enc.stdin.close(); enc.wait()
