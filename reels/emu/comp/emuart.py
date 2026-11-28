"""Hand-drawn (cairo) art for the Great Emu War: emus, soldiers, Lewis gun, 1930s truck, minister's office, farm, battlefield."""
import math, cairo, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from toons import _surf, _pil, sticker, fillstroke, ell, eyes, mouth, SKIN, SKIN_D, INK
W, H = 1080, 1920
KHAKI, KHAKI_D, SLOUCH = (0.62, 0.55, 0.36), (0.46, 0.40, 0.25), (0.48, 0.38, 0.24)
def rr(c, x, y, w, h, r):
    c.new_path(); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.arc(x + w - r, y + r, r, 1.5 * math.pi, 0); c.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi); c.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi); c.close_path()
# ---------------------------------------------------------------- EMU
def emu(phase=0.0, pose='run', expr='normal', S=300, flip=False):
    """side view facing right. pose: run | stand | peck | cheer. phase in radians animates legs/neck."""
    s, c = _surf(int(S * 1.12), int(S * 1.42)); k = S / 300; c.scale(k, k); c.translate(10, 52)
    if flip: c.translate(300, 0); c.scale(-1, 1)
    body = (0.43, 0.36, 0.30); dark = (0.27, 0.22, 0.18); leg = (0.55, 0.47, 0.40)
    hip = (150, 205)
    # legs (2-segment, opposite phases)
    for i, ph in enumerate((phase, phase + math.pi)):
        if pose == 'run': th = math.sin(ph) * 0.75; kn = 0.9 + 0.6 * max(0, math.cos(ph))
        elif pose == 'cheer': th = math.sin(ph) * 0.25; kn = 0.5
        else: th = (0.12 if i == 0 else -0.12); kn = 0.45
        kx = hip[0] + math.sin(th) * 70; ky = hip[1] + math.cos(th) * 70
        fx = kx + math.sin(th - kn) * 75; fy = ky + math.cos(th - kn) * 75
        col = leg if i == 0 else tuple(v * 0.8 for v in leg)
        c.new_path(); c.move_to(*hip); c.line_to(kx, ky); c.line_to(fx, fy); c.set_source_rgb(*INK); c.set_line_width(17); c.stroke()
        c.new_path(); c.move_to(*hip); c.line_to(kx, ky); c.line_to(fx, fy); c.set_source_rgb(*col); c.set_line_width(10); c.stroke()
        for dx in (-14, 0, 16): c.new_path(); c.move_to(fx, fy); c.line_to(fx + dx + 10, fy + 6); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    # shaggy body
    bob = 6 * math.sin(phase * 2) if pose == 'run' else 0
    c.save(); c.translate(0, bob)
    c.new_path(); c.save(); c.translate(140, 160); c.scale(95, 62); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); fillstroke(c, body, 6)
    rng = np.random.default_rng(4)
    for i in range(26):   # feather strokes
        a = rng.uniform(0.2, 3.0); r = rng.uniform(0.3, 0.95); x = 140 + math.cos(a) * 90 * r; y = 160 + math.sin(a) * 58 * r - 10
        c.new_path(); c.move_to(x, y); c.curve_to(x - 10, y + 10, x - 18, y + 22, x - 24, y + 30); c.set_source_rgb(*dark); c.set_line_width(4); c.stroke()
    c.new_path(); c.move_to(55, 175); c.curve_to(40, 185, 35, 200, 45, 210); c.set_source_rgb(*dark); c.set_line_width(9); c.stroke()   # tail fluff
    # neck + head
    nk = {'run': -0.35, 'stand': 0.0, 'peck': 1.25, 'cheer': -0.15}[pose] + (0.08 * math.sin(phase * 2) if pose == 'run' else 0)
    if pose == 'peck': nk += 0.25 * max(0, math.sin(phase))
    base = (205, 125); L = 120
    hx = base[0] + math.sin(nk) * L * 0.55 + 18; hy = base[1] - math.cos(nk) * L
    c.new_path(); c.move_to(base[0] - 12, base[1] + 18); c.curve_to(base[0] + 5, base[1] - 30, hx - 25, hy + 40, hx - 6, hy + 8)
    c.line_to(hx + 10, hy + 16); c.curve_to(hx - 8, hy + 50, base[0] + 30, base[1] - 10, base[0] + 26, base[1] + 26); c.close_path(); fillstroke(c, (0.36, 0.42, 0.55), 5)   # bluish neck skin
    ell(c, hx, hy, 30, 25); fillstroke(c, (0.36, 0.40, 0.50), 5)
    c.new_path(); c.move_to(hx + 22, hy - 6); c.line_to(hx + 58, hy + 4); c.line_to(hx + 22, hy + 12); c.close_path(); fillstroke(c, (0.22, 0.2, 0.2), 4)   # beak
    # eye (big cartoon eye, expressions)
    ell(c, hx + 6, hy - 5, 12, 13); fillstroke(c, (1, 1, 1), 3)
    px = {'normal': 3, 'smug': 4, 'angry': 4, 'shock': 0, 'happy': 3}[expr]
    if expr == 'happy':
        c.new_path(); c.arc(hx + 6, hy - 2, 8, math.pi * 1.1, math.pi * 1.9); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    else:
        ell(c, hx + 6 + px, hy - 4, 5.5, 6.5); c.set_source_rgb(*INK); c.fill()
    if expr in ('smug', 'angry'):
        c.new_path(); c.move_to(hx - 8, hy - 14 - (4 if expr == 'smug' else 0)); c.line_to(hx + 20, hy - 12 + (6 if expr == 'angry' else -2)); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    c.restore()
    return sticker(_pil(s), ow=5)
# ---------------------------------------------------------------- SOLDIERS
def digger_head(c, x, y, r, expr='neutral', hat=True):
    ell(c, x, y, r, r * 1.08); fillstroke(c, SKIN, 5)
    eyes(c, x, y - r * 0.05, r * 0.38, expr, r=r * 0.17); ell(c, x, y + r * 0.28, r * 0.14, r * 0.12); fillstroke(c, SKIN_D, 3); mouth(c, x, y + r * 0.55, expr, r * 0.25)
    if hat:   # slouch hat, left brim pinned up
        c.new_path(); c.move_to(x - r * 1.5, y - r * 0.55); c.curve_to(x - r * 0.6, y - r * 0.82, x + r * 0.6, y - r * 0.82, x + r * 1.5, y - r * 0.55)
        c.line_to(x + r * 1.45, y - r * 0.4); c.curve_to(x + r * 0.5, y - r * 0.6, x - r * 0.4, y - r * 0.6, x - r * 1.0, y - r * 0.45); c.close_path(); fillstroke(c, SLOUCH, 4)
        c.new_path(); c.move_to(x - r * 0.75, y - r * 0.6); c.curve_to(x - r * 0.75, y - r * 1.5, x + r * 0.75, y - r * 1.5, x + r * 0.75, y - r * 0.6); c.close_path(); fillstroke(c, SLOUCH, 4)
        c.rectangle(x - r * 0.75, y - r * 0.82, r * 1.5, r * 0.18); fillstroke(c, (0.25, 0.2, 0.12), 3)
        c.new_path(); c.move_to(x - r * 1.0, y - r * 0.5); c.line_to(x - r * 1.05, y - r * 1.25); c.line_to(x - r * 0.65, y - r * 0.7); c.close_path(); fillstroke(c, SLOUCH, 4)   # pinned-up brim
def lewis_gun(c, x, y, sc=1.0, fire=False, jam=False):
    """Lewis gun on bipod, pointing right, origin at bipod foot."""
    c.save(); c.translate(x, y); c.scale(sc, sc)
    c.new_path(); c.move_to(70, 0); c.line_to(95, -55); c.move_to(120, 0); c.line_to(95, -55); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()   # bipod
    rr(c, -40, -75, 230, 30, 10); fillstroke(c, (0.25, 0.27, 0.25), 4)       # cooling shroud
    for i in range(8): c.move_to(-20 + i * 26, -75); c.line_to(-20 + i * 26, -45); c.set_source_rgb(0.15, 0.16, 0.15); c.set_line_width(3); c.stroke()
    c.rectangle(190, -66, 40, 12); fillstroke(c, (0.2, 0.2, 0.2), 3)       # muzzle
    ell(c, 10, -90, 48, 14); fillstroke(c, (0.3, 0.32, 0.3), 4); ell(c, 10, -92, 14, 5); c.set_source_rgb(0.15, 0.15, 0.15); c.fill()   # pan magazine
    c.new_path(); c.move_to(-40, -62); c.line_to(-120, -50); c.line_to(-125, -25); c.line_to(-40, -45); c.close_path(); fillstroke(c, (0.48, 0.32, 0.18), 4)   # stock
    if fire:
        for i in range(9):
            a = (i / 9) * 2 * math.pi; r1 = 26 + (i % 2) * 22; c.line_to(250 + math.cos(a) * r1, -60 + math.sin(a) * r1 * 0.7)
        c.close_path(); c.set_source_rgb(1, 0.82, 0.25); c.fill_preserve(); c.set_source_rgb(1, 0.5, 0.1); c.set_line_width(4); c.stroke()
        ell(c, 250, -60, 12, 9); c.set_source_rgb(1, 1, 0.85); c.fill()
    if jam:
        for i, (dx, dy, r) in enumerate(((240, -95, 26), (270, -120, 32), (225, -130, 22), (300, -150, 36))):
            ell(c, dx, dy, r, r * 0.85); c.set_source_rgba(0.55, 0.55, 0.58, 0.85); c.fill()
    c.restore()
def gunner(phase=0.0, fire=False, jam=False, expr='neutral', S=520):
    """kneeling Digger operating a Lewis gun (side view, facing right) + loader."""
    s, c = _surf(S, int(S * 0.62)); k = S / 520; c.scale(k, k)
    shake = 3 * math.sin(phase * 40) if fire else 0
    c.translate(shake, 0)
    # loader (behind)
    c.new_path(); c.move_to(70, 300); c.curve_to(60, 230, 90, 200, 120, 200); c.curve_to(150, 200, 175, 230, 170, 300); c.close_path(); fillstroke(c, KHAKI_D, 5)
    digger_head(c, 120, 165, 36, 'shock' if jam else 'neutral')
    # gunner kneeling
    c.new_path(); c.move_to(170, 300); c.line_to(210, 255); c.line_to(260, 300); c.set_source_rgb(*KHAKI_D); c.set_line_width(26); c.stroke()   # legs
    c.new_path(); c.move_to(180, 270); c.curve_to(175, 205, 210, 180, 245, 185); c.curve_to(275, 190, 290, 215, 285, 270); c.close_path(); fillstroke(c, KHAKI, 5)
    c.new_path(); c.move_to(260, 210); c.line_to(320, 228); c.set_source_rgb(*KHAKI); c.set_line_width(22); c.stroke()   # arm
    digger_head(c, 255, 150, 40, expr)
    lewis_gun(c, 300, 300, 0.95, fire, jam)
    return _pil(s)
def marcher(phase=0.0, S=200):
    s, c = _surf(S, int(S * 1.6)); k = S / 200; c.scale(k, k)
    for i, ph in enumerate((phase, phase + math.pi)):
        th = math.sin(ph) * 0.45; c.new_path(); c.move_to(100, 200); c.line_to(100 + math.sin(th) * 110, 200 + math.cos(th) * 110)
        c.set_source_rgb(*INK); c.set_line_width(30); c.stroke(); c.new_path(); c.move_to(100, 200); c.line_to(100 + math.sin(th) * 110, 200 + math.cos(th) * 110); c.set_source_rgb(*(KHAKI_D if i else KHAKI)); c.set_line_width(22); c.stroke()
    c.new_path(); c.move_to(60, 210); c.curve_to(55, 140, 75, 110, 100, 110); c.curve_to(125, 110, 145, 140, 140, 210); c.close_path(); fillstroke(c, KHAKI, 5)
    c.move_to(125, 120); c.line_to(150, 30); c.set_source_rgb(0.4, 0.27, 0.15); c.set_line_width(10); c.stroke()   # rifle on shoulder
    digger_head(c, 100, 80, 34, 'neutral')
    return sticker(_pil(s), ow=4)
def truck(phase=0.0, S=560, fire=False):
    """1930s flatbed truck with Lewis gun and two Diggers, facing right; wheels spin with phase."""
    s, c = _surf(S, int(S * 0.62)); k = S / 560; c.scale(k, k)
    bounce = 6 * abs(math.sin(phase * 1.5)); c.translate(0, -bounce)
    rr(c, 30, 170, 330, 60, 8); fillstroke(c, (0.42, 0.33, 0.2), 5)                         # flatbed
    for i in range(6): c.move_to(40 + i * 55, 170); c.line_to(40 + i * 55, 230); c.set_source_rgb(0.3, 0.22, 0.12); c.set_line_width(3); c.stroke()
    c.new_path(); c.move_to(360, 230); c.line_to(360, 110); c.line_to(450, 110); c.line_to(470, 150); c.line_to(520, 160); c.line_to(530, 230); c.close_path(); fillstroke(c, (0.25, 0.36, 0.25), 5)   # cab + bonnet
    rr(c, 372, 122, 62, 48, 6); fillstroke(c, (0.75, 0.88, 0.95), 4)
    c.rectangle(515, 175, 18, 30); fillstroke(c, (0.75, 0.75, 0.7), 3)
    for x in (110, 445):
        c.save(); c.translate(x, 240 + bounce); c.rotate(phase * 3)
        ell(c, 0, 0, 44, 44); fillstroke(c, (0.12, 0.12, 0.12), 5); ell(c, 0, 0, 20, 20); fillstroke(c, (0.6, 0.6, 0.6), 3)
        for a in range(4): c.move_to(0, 0); c.line_to(math.cos(a * 1.57) * 20, math.sin(a * 1.57) * 20); c.set_source_rgb(0.3, 0.3, 0.3); c.set_line_width(4); c.stroke()
        c.restore()
    c.new_path(); c.move_to(150, 170); c.curve_to(145, 120, 170, 100, 195, 100); c.curve_to(220, 100, 240, 120, 235, 170); c.close_path(); fillstroke(c, KHAKI, 5)
    digger_head(c, 192, 68, 34, 'worried')
    c.new_path(); c.move_to(60, 170); c.curve_to(55, 125, 75, 110, 95, 110); c.curve_to(115, 110, 132, 125, 128, 170); c.close_path(); fillstroke(c, KHAKI_D, 5)
    digger_head(c, 93, 80, 30, 'shock')
    lewis_gun(c, 230, 165, 0.7, fire)
    return _pil(s)
# ---------------------------------------------------------------- PEOPLE (busts)
def bust_base(c, coat):
    c.move_to(55, 525); c.curve_to(65, 420, 140, 392, 210, 392); c.curve_to(280, 392, 355, 420, 365, 525); c.close_path(); fillstroke(c, coat)
def minister(talk=0, expr='smug', S=420):
    s, c = _surf(S, int(S * 1.3)); k = S / 420; c.scale(k, k); c.translate(0, 20); cx = 210
    bust_base(c, (0.18, 0.2, 0.26))
    c.new_path(); c.move_to(170, 396); c.line_to(cx, 470); c.line_to(250, 396); c.close_path(); fillstroke(c, (1, 1, 1), 4)
    c.new_path(); c.move_to(cx - 14, 410); c.line_to(cx + 14, 410); c.line_to(cx + 8, 470); c.line_to(cx - 8, 470); c.close_path(); fillstroke(c, (0.65, 0.12, 0.15), 3)   # tie
    ell(c, cx, 270, 102, 120); fillstroke(c, SKIN)
    c.new_path(); c.arc(cx, 230, 102, math.pi * 1.08, math.pi * 1.92); c.set_source_rgb(0.55, 0.55, 0.58); c.set_line_width(26); c.stroke()   # receding grey hair
    for sx in (-1, 1): ell(c, cx + sx * 102, 280, 17, 26); fillstroke(c, SKIN_D, 5)
    eyes(c, cx, 258, 40, expr)
    for sx in (-1, 1): ell(c, cx + sx * 40, 258, 30, 26); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()   # round glasses
    c.move_to(cx - 10, 258); c.line_to(cx + 10, 258); c.stroke()
    ell(c, cx, 296, 16, 14); fillstroke(c, SKIN_D, 4)
    c.new_path(); c.move_to(cx - 46, 322); c.curve_to(cx - 15, 306, cx + 15, 306, cx + 46, 322); c.curve_to(cx + 15, 316, cx - 15, 316, cx - 46, 322); fillstroke(c, (0.5, 0.5, 0.52), 4)   # moustache
    if talk: ell(c, cx, 348, 20, 16 * talk); fillstroke(c, (0.5, 0.1, 0.12), 4)
    else: mouth(c, cx, 345, expr, 24)
    return sticker(_pil(s))
def major(talk=0, expr='smug', S=420):
    s, c = _surf(S, int(S * 1.4)); k = S / 420; c.scale(k, k); c.translate(0, 50); cx = 210
    bust_base(c, KHAKI)
    for sx in (-1, 1): c.rectangle(cx + sx * 70 - 22, 420, 44, 50); fillstroke(c, KHAKI_D, 4)   # pockets
    c.move_to(150, 400); c.line_to(cx, 440); c.line_to(270, 400); c.set_source_rgb(*KHAKI_D); c.set_line_width(6); c.stroke()
    for i in range(3): ell(c, 132 + i * 14, 470, 6, 9); c.set_source_rgb(*(0.8, 0.15, 0.15) if i != 1 else (0.2, 0.4, 0.8)); c.fill()   # ribbons
    c.save(); c.translate(cx, 270); c.scale(1, 1); c.restore()
    digger_head(c, cx, 270, 105, expr)
    c.new_path(); c.move_to(cx - 60, 318); c.curve_to(cx - 30, 300, cx + 30, 300, cx + 60, 318); c.curve_to(cx + 72, 330, cx + 80, 322, cx + 84, 312)
    c.curve_to(cx + 60, 330, cx - 60, 330, cx - 84, 312); c.curve_to(cx - 80, 322, cx - 72, 330, cx - 60, 318); fillstroke(c, (0.35, 0.24, 0.14), 4)   # walrus moustache
    if talk: ell(c, cx, 350, 18, 14 * talk); fillstroke(c, (0.5, 0.1, 0.12), 4)
    return sticker(_pil(s))
def farmer(talk=0, expr='shock', S=420):
    s, c = _surf(S, int(S * 1.35)); k = S / 420; c.scale(k, k); c.translate(0, 40); cx = 210
    bust_base(c, (0.74, 0.32, 0.22))
    for x in (150, 270): c.rectangle(x - 12, 400, 24, 125); fillstroke(c, (0.25, 0.35, 0.6), 4)   # overall straps
    ell(c, cx, 270, 100, 116); fillstroke(c, SKIN)
    for sx in (-1, 1): ell(c, cx + sx * 50, 310, 16, 11); c.set_source_rgba(1, 0.45, 0.4, 0.45); c.fill()
    eyes(c, cx, 262, 38, expr); ell(c, cx, 298, 15, 13); fillstroke(c, SKIN_D, 4)
    if talk: ell(c, cx, 348, 22, 18 * talk); fillstroke(c, (0.5, 0.1, 0.12), 4)
    else: mouth(c, cx, 345, expr, 24)
    c.new_path(); c.save(); c.translate(cx, 175); c.scale(1.7, 0.3); c.arc(0, 0, 100, 0, 6.3); c.restore(); fillstroke(c, (0.92, 0.82, 0.5))   # straw hat
    c.new_path(); c.move_to(cx - 80, 172); c.curve_to(cx - 75, 80, cx + 75, 80, cx + 80, 172); c.close_path(); fillstroke(c, (0.92, 0.82, 0.5))
    c.rectangle(cx - 80, 150, 160, 18); fillstroke(c, (0.65, 0.2, 0.15), 3)
    # phone handset at ear
    c.new_path(); c.move_to(cx + 95, 240); c.curve_to(cx + 150, 250, cx + 150, 330, cx + 100, 350); c.set_source_rgb(0.1, 0.1, 0.1); c.set_line_width(22); c.stroke()
    return sticker(_pil(s))
# ---------------------------------------------------------------- BACKGROUNDS (PIL RGB, cached by caller)
def _noise(h, w, seed, base=6, oct=5):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        n = base * 2 ** o; a = rng.random((int(n * h / w) + 2, n + 2)).astype(np.float32)
        acc += np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 * amp; tot += amp; amp *= 0.55
    return acc / tot
def outback(horizon=860, water=False, seed=1):
    """wide outback wheat country: sky gradient, sun, far hills, golden wheat with depth, a fence."""
    s, c = _surf(W, H)
    g = cairo.LinearGradient(0, 0, 0, horizon); g.add_color_stop_rgb(0, 0.33, 0.62, 0.92); g.add_color_stop_rgb(1, 0.82, 0.9, 0.96); c.rectangle(0, 0, W, horizon); c.set_source(g); c.fill()
    ell(c, 940, 640, 55, 55); c.set_source_rgb(1, 0.95, 0.75); c.fill()
    for i, (y0, col) in enumerate(((horizon - 70, (0.62, 0.52, 0.42)), (horizon - 30, (0.72, 0.58, 0.40)))):
        c.new_path(); c.move_to(0, horizon)
        for x in range(0, W + 60, 60): c.line_to(x, y0 + 30 * math.sin(x / (170 + i * 60) + i * 2) + 15 * math.sin(x / 47))
        c.line_to(W, horizon); c.close_path(); c.set_source_rgb(*col); c.fill()
    g = cairo.LinearGradient(0, horizon, 0, H); g.add_color_stop_rgb(0, 0.86, 0.72, 0.38); g.add_color_stop_rgb(1, 0.72, 0.54, 0.22); c.rectangle(0, horizon, W, H - horizon); c.set_source(g); c.fill()
    if water:
        c.new_path(); c.save(); c.translate(540, horizon + 330); c.scale(430, 120); c.arc(0, 0, 1, 0, 6.3); c.restore()
        g2 = cairo.RadialGradient(540, horizon + 330, 20, 540, horizon + 330, 430); g2.add_color_stop_rgb(0, 0.45, 0.7, 0.85); g2.add_color_stop_rgb(1, 0.25, 0.5, 0.68)
        c.set_source(g2); c.fill_preserve(); c.set_source_rgb(0.55, 0.42, 0.25); c.set_line_width(14); c.stroke()
    rng = np.random.default_rng(seed)
    for i in range(1400):   # wheat stalks, bigger toward the front
        y = horizon + (rng.random() ** 1.6) * (H - horizon); sz = 0.25 + 1.8 * (y - horizon) / (H - horizon); x = rng.random() * W
        if water and ((x - 540) / 470) ** 2 + ((y - horizon - 330) / 150) ** 2 < 1: continue
        c.move_to(x, y); c.line_to(x + 3 * sz, y - 26 * sz); c.set_source_rgba(0.95, 0.82, 0.45, 0.8); c.set_line_width(2.2 * sz); c.stroke()
        ell(c, x + 3 * sz, y - 30 * sz, 3 * sz, 7 * sz); c.set_source_rgba(0.98, 0.86, 0.5, 0.9); c.fill()
    for i in range(9):   # fence posts
        x = 40 + i * 130; c.rectangle(x, horizon + 40, 8, 60); c.set_source_rgb(0.42, 0.3, 0.18); c.fill()
    c.move_to(0, horizon + 55); c.line_to(W, horizon + 55); c.move_to(0, horizon + 80); c.line_to(W, horizon + 80); c.set_source_rgb(0.35, 0.3, 0.25); c.set_line_width(2); c.stroke()
    return _pil(s).convert('RGB')
def office():
    """1930s minister's office: wallpaper, window with sky, framed map of Australia, flag, wooden desk, candlestick phone, papers."""
    s, c = _surf(W, H)
    c.rectangle(0, 0, W, H); c.set_source_rgb(0.62, 0.66, 0.55); c.fill()
    for x in range(0, W, 54): c.rectangle(x, 0, 22, 1300); c.set_source_rgba(0.55, 0.6, 0.48, 0.6); c.fill()   # stripes
    c.rectangle(0, 1240, W, 30); c.set_source_rgb(0.42, 0.28, 0.16); c.fill()                                # dado rail
    c.rectangle(0, 1270, W, H - 1270); c.set_source_rgb(0.36, 0.22, 0.12); c.fill()
    rr(c, 620, 230, 360, 470, 10); fillstroke(c, (0.98, 0.98, 0.95), 14)                                      # window
    g = cairo.LinearGradient(0, 240, 0, 690); g.add_color_stop_rgb(0, 0.45, 0.7, 0.95); g.add_color_stop_rgb(1, 0.85, 0.92, 0.98); rr(c, 634, 244, 332, 442, 6); c.set_source(g); c.fill()
    c.move_to(800, 244); c.line_to(800, 686); c.move_to(634, 465); c.line_to(966, 465); c.set_source_rgb(0.98, 0.98, 0.95); c.set_line_width(12); c.stroke()
    c.rectangle(110, 300, 380, 300); fillstroke(c, (0.6, 0.42, 0.22), 14); c.rectangle(126, 316, 348, 268); c.set_source_rgb(0.92, 0.88, 0.76); c.fill()   # framed map
    c.new_path()
    AUS = [(0.05, 0.45), (0.2, 0.28), (0.38, 0.3), (0.48, 0.1), (0.58, 0.3), (0.7, 0.05), (0.8, 0.35), (0.95, 0.55), (0.85, 0.85), (0.6, 0.95), (0.45, 0.75), (0.3, 0.8), (0.1, 0.75)]
    for i, (u, v) in enumerate(AUS): (c.move_to if i == 0 else c.line_to)(150 + u * 300, 340 + v * 210)
    c.close_path(); fillstroke(c, (0.85, 0.6, 0.3), 4)
    c.select_font_face('Serif', 0, 1); c.set_font_size(30); c.set_source_rgb(0.3, 0.2, 0.1); c.move_to(200, 360); c.show_text('AUSTRALIA')
    rr(c, 40, 1180, W - 80, 120, 12); fillstroke(c, (0.5, 0.3, 0.15), 6)                                       # desk top
    c.rectangle(70, 1300, W - 140, 620); c.set_source_rgb(0.42, 0.25, 0.12); c.fill(); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    for y in (1380, 1560, 1740): rr(c, 120, y, 300, 130, 8); fillstroke(c, (0.48, 0.3, 0.15), 4); ell(c, 270, y + 65, 12, 12); fillstroke(c, (0.85, 0.7, 0.3), 3)
    for i in range(3): c.save(); c.translate(560 + i * 18, 1215 - i * 6); c.rotate(-0.08 + i * 0.07); c.rectangle(0, 0, 200, 40); fillstroke(c, (0.98, 0.97, 0.92), 3); c.restore()
    return _pil(s).convert('RGB')
def phone(S=200, ring=0.0):
    s, c = _surf(S, int(S * 1.4)); k = S / 200; c.scale(k, k); c.translate(0, 0); c.rotate(0.06 * math.sin(ring * 40) if ring else 0)
    ell(c, 100, 255, 70, 18); fillstroke(c, (0.12, 0.12, 0.12), 4); c.rectangle(88, 90, 24, 165); fillstroke(c, (0.15, 0.15, 0.15), 4)
    ell(c, 100, 80, 34, 22); fillstroke(c, (0.15, 0.15, 0.15), 4); c.new_path(); c.move_to(130, 140); c.curve_to(180, 130, 185, 60, 160, 40); c.set_source_rgb(0.1, 0.1, 0.1); c.set_line_width(14); c.stroke()
    ell(c, 165, 35, 18, 24); fillstroke(c, (0.12, 0.12, 0.12), 4)
    return sticker(_pil(s), ow=4)
def farmhouse(S=420):
    s, c = _surf(S, int(S * 0.8)); k = S / 420; c.scale(k, k)
    c.rectangle(40, 140, 340, 180); fillstroke(c, (0.92, 0.88, 0.78), 6)
    c.new_path(); c.move_to(20, 150); c.line_to(210, 40); c.line_to(400, 150); c.close_path(); fillstroke(c, (0.55, 0.6, 0.62), 6)   # tin roof
    for i in range(10): c.move_to(40 + i * 36, 140 - (abs(i - 4.5) * -0)); c.line_to(210, 45); c.set_source_rgba(0.4, 0.45, 0.48, 0.5); c.set_line_width(2); c.stroke()
    c.rectangle(80, 200, 70, 60); fillstroke(c, (0.7, 0.85, 0.95), 4); c.rectangle(270, 200, 70, 60); fillstroke(c, (0.7, 0.85, 0.95), 4)
    c.rectangle(180, 210, 60, 110); fillstroke(c, (0.5, 0.3, 0.18), 4)
    c.rectangle(10, 315, 400, 10); c.set_source_rgb(0.45, 0.32, 0.2); c.fill()
    return sticker(_pil(s), ow=5)
def ammo_crate(S=180, text='10,000'):
    s, c = _surf(S, int(S * 0.75)); k = S / 180; c.scale(k, k)
    c.rectangle(10, 20, 160, 100); fillstroke(c, (0.42, 0.45, 0.28), 5); c.move_to(10, 55); c.line_to(170, 55); c.set_source_rgb(*INK); c.set_line_width(3); c.stroke()
    c.select_font_face('Sans', 0, 1); c.set_font_size(24); c.set_source_rgb(0.95, 0.9, 0.7); e = c.text_extents('.303 AMMO'); c.move_to(90 - e.width / 2, 45); c.show_text('.303 AMMO')
    return sticker(_pil(s), ow=4)
def scoreboard(a=1, b=0, S=700):
    s, c = _surf(S, int(S * 0.55)); k = S / 700; c.scale(k, k)
    rr(c, 10, 10, 680, 360, 30); fillstroke(c, (0.1, 0.12, 0.14), 8)
    c.select_font_face('Sans', 0, 1); c.set_font_size(54)
    for i, (n, col) in enumerate((('EMUS', (0.95, 0.75, 0.25)), ('ARMY', (0.75, 0.82, 0.6)))):
        x = 180 + i * 340; e = c.text_extents(n); c.set_source_rgb(*col); c.move_to(x - e.width / 2, 100); c.show_text(n)
    c.set_font_size(170); c.set_source_rgb(1, 1, 1)
    for i, v in enumerate((a, b)): e = c.text_extents(str(v)); c.move_to(180 + i * 340 - e.width / 2, 300); c.show_text(str(v))
    c.set_font_size(110); e = c.text_extents('-'); c.move_to(350 - e.width / 2, 270); c.show_text('-')
    return sticker(_pil(s), ow=6)
def calendar(text='DEC', S=240):
    s, c = _surf(S, int(S * 1.05)); k = S / 240; c.scale(k, k)
    c.rectangle(20, 40, 200, 200); fillstroke(c, (1, 1, 1)); c.rectangle(20, 40, 200, 60); fillstroke(c, (0.85, 0.15, 0.2))
    c.select_font_face('Sans', 0, 1); c.set_font_size(38); e = c.text_extents(text); c.set_source_rgb(1, 1, 1); c.move_to(120 - e.width / 2, 84); c.show_text(text)
    c.set_font_size(66); c.set_source_rgb(*INK); e = c.text_extents('1932'); c.move_to(120 - e.width / 2, 190); c.show_text('1932')
    return sticker(_pil(s))
def coins(S=200):
    s, c = _surf(S, S); k = S / 200; c.scale(k, k)
    for i, (x, y) in enumerate(((70, 140), (120, 140), (95, 110), (60, 95), (130, 95))):
        ell(c, x, y, 34, 34); fillstroke(c, (0.95, 0.78, 0.2), 4); ell(c, x, y, 22, 22); c.set_source_rgb(0.85, 0.62, 0.1); c.set_line_width(3); c.stroke()
    return sticker(_pil(s), ow=4)
if __name__ == '__main__':
    out = Image.new('RGBA', (2600, 1700), (60, 110, 140, 255)); x = 20; y = 20; mh = 0
    items = [emu(0, 'run'), emu(1.5, 'run', 'smug'), emu(0, 'stand', 'happy'), emu(1, 'peck'), emu(0, 'cheer', 'happy'), gunner(0, True), gunner(0, False, True, 'shock'), marcher(0.5), truck(0.4, fire=True),
             minister(0, 'smug'), major(0.6), farmer(0.8), phone(), farmhouse(), ammo_crate(), scoreboard(), calendar(), coins()]
    for im in items:
        if x + im.width > 2600: x = 20; y += mh + 20; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 20; mh = max(mh, im.height)
    out.convert('RGB').resize((1300, 850)).save('/tmp/claude-0/fr/emuart.png')
    o = Image.new('RGB', (1080, 960)); o.paste(outback().resize((540, 960)), (0, 0)); o.paste(office().resize((540, 960)), (540, 0)); o.save('/tmp/claude-0/fr/emubg.png')
