"""Hand-drawn (code-drawn) cartoon characters and props with cairo. All return PIL RGBA 'stickers' (white outline + soft shadow)."""
import math, cairo
import numpy as np
from PIL import Image, ImageFilter
SKIN, SKIN_D, INK = (1.0, 0.84, 0.69), (0.93, 0.70, 0.55), (0.16, 0.10, 0.08)
def _surf(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); return s, c
def _pil(s):
    w, h = s.get_width(), s.get_height(); a = np.frombuffer(s.get_data(), np.uint8).reshape(h, s.get_stride() // 4, 4)[:, :w]
    b, g, r, al = [a[..., i].astype(np.float32) for i in range(4)]; m = np.maximum(al, 1) / 255
    return Image.fromarray(np.dstack([r / m, g / m, b / m, al]).clip(0, 255).astype(np.uint8), 'RGBA')
def sticker(im, ow=9, shadow=True):
    a = im.split()[3]; o = a.filter(ImageFilter.MaxFilter(ow * 2 + 1)).filter(ImageFilter.GaussianBlur(1))
    W, H = im.size; out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    if shadow:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sh.putalpha(o.point(lambda v: int(v * 0.45)).filter(ImageFilter.GaussianBlur(10)))
        out.alpha_composite(sh, (6, 12))
    wl = Image.new('RGBA', (W, H), (255, 255, 255, 0)); wl.putalpha(o); out.alpha_composite(wl); out.alpha_composite(im); return out
def fillstroke(c, col, lw=6, ink=INK):
    c.set_source_rgb(*col); c.fill_preserve(); c.set_source_rgb(*ink); c.set_line_width(lw); c.stroke()
def ell(c, x, y, rx, ry):
    c.save(); c.translate(x, y); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
def eyes(c, cx, cy, sp, expr, r=17):
    for sx in (-1, 1):
        x = cx + sx * sp
        if expr in ('laugh', 'happy'):
            c.new_path(); c.arc(x, cy + 6, r * 0.9, math.pi * 1.15, math.pi * 1.85); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
        else:
            ell(c, x, cy, r * 0.85, r * 1.05); fillstroke(c, (1, 1, 1), 4)
            dx = {'smug': 5, 'worried': 0, 'neutral': 2, 'shock': 0}.get(expr, 0)
            ell(c, x + dx * sx * (0 if expr == 'smug' else 1) + (5 if expr == 'smug' else 0), cy + 3, r * 0.42, r * 0.5); c.set_source_rgb(*INK); c.fill()
            if expr == 'smug':   # half-closed lids
                c.new_path(); c.rectangle(x - r, cy - r * 1.2, 2 * r, r * 1.0); c.set_source_rgb(*SKIN_D); c.fill()
                c.move_to(x - r, cy - 2); c.line_to(x + r, cy - 2); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    # brows
    for sx in (-1, 1):
        x = cx + sx * sp; t = {'worried': -14, 'smug': 8, 'shock': -4, 'angry': 14}.get(expr, 0) * sx
        c.move_to(x - 22, cy - 34 - (t if sx > 0 else 0) * 0.5); c.line_to(x + 22, cy - 34 + t * 0.5 * (1 if sx > 0 else -1) * -1)
        c.set_source_rgb(*INK); c.set_line_width(9); c.stroke()
def mouth(c, x, y, expr, w=40):
    c.new_path()
    if expr == 'laugh':
        c.move_to(x - w, y - 6); c.curve_to(x - w, y + 50, x + w, y + 50, x + w, y - 6); c.close_path(); fillstroke(c, (0.55, 0.1, 0.12), 5)
        ell(c, x, y + 24, w * 0.5, 10); c.set_source_rgb(0.95, 0.45, 0.45); c.fill()
    elif expr in ('happy', 'smug'):
        c.move_to(x - w * 0.8, y); c.curve_to(x - w * 0.3, y + 22, x + w * 0.3, y + 22, x + w * 0.8, y - (8 if expr == 'smug' else 0)); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
    elif expr == 'worried':
        c.move_to(x - w * 0.7, y + 12); c.curve_to(x - w * 0.3, y - 6, x + w * 0.3, y - 6, x + w * 0.7, y + 12); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
    elif expr == 'shock':
        ell(c, x, y + 8, 16, 22); fillstroke(c, (0.45, 0.08, 0.1), 5)
    else:
        c.move_to(x - w * 0.5, y + 4); c.line_to(x + w * 0.5, y + 4); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
def tsar(expr='neutral', S=420):
    """Russian emperor caricature: imperial crown, big mutton-chop whiskers joined to a moustache, green uniform with gold epaulettes."""
    s, c = _surf(S, int(S * 1.25)); k = S / 420; c.scale(k, k); cx = 210
    # body / uniform
    c.move_to(60, 525); c.curve_to(70, 420, 140, 395, 210, 395); c.curve_to(280, 395, 350, 420, 360, 525); c.close_path(); fillstroke(c, (0.13, 0.32, 0.22))
    for sx in (-1, 1):   # epaulettes
        ell(c, cx + sx * 115, 428, 42, 16); fillstroke(c, (0.95, 0.75, 0.2), 5)
    c.move_to(cx, 400); c.line_to(cx, 525); c.set_source_rgb(0.95, 0.75, 0.2); c.set_line_width(6); c.stroke()
    c.move_to(150, 400); c.line_to(cx, 470); c.line_to(270, 400); c.set_source_rgb(0.85, 0.15, 0.2); c.set_line_width(10); c.stroke()   # sash
    # head
    ell(c, cx, 270, 112, 128); fillstroke(c, SKIN)
    for sx in (-1, 1): ell(c, cx + sx * 112, 280, 18, 28); fillstroke(c, SKIN_D, 5)   # ears
    # whiskers (mutton chops + moustache)
    c.new_path(); c.move_to(102, 230); c.curve_to(85, 330, 120, 380, 170, 355); c.curve_to(190, 345, 200, 335, 210, 338)
    c.curve_to(220, 335, 230, 345, 250, 355); c.curve_to(300, 380, 335, 330, 318, 230); c.curve_to(300, 300, 270, 320, 210, 318)
    c.curve_to(150, 320, 120, 300, 102, 230); c.close_path(); fillstroke(c, (0.47, 0.32, 0.2), 5)
    eyes(c, cx, 250, 42, expr); mouth(c, cx, 340, expr, 30)
    ell(c, cx, 288, 22, 18); fillstroke(c, SKIN_D, 5)   # nose
    # crown
    c.new_path(); c.move_to(130, 165); c.curve_to(130, 60, 290, 60, 290, 165); c.close_path(); fillstroke(c, (0.82, 0.12, 0.18))
    c.move_to(cx, 70); c.line_to(cx, 165); c.set_source_rgb(0.98, 0.8, 0.25); c.set_line_width(14); c.stroke()
    c.rectangle(118, 150, 184, 34); fillstroke(c, (0.98, 0.8, 0.25), 5)
    for i in range(5): ell(c, 140 + i * 35, 167, 9, 9); c.set_source_rgb(*((0.2, 0.5, 0.95) if i % 2 else (0.95, 0.2, 0.3))); c.fill()
    c.move_to(cx, 30); c.line_to(cx, 70); c.move_to(cx - 16, 46); c.line_to(cx + 16, 46); c.set_source_rgb(0.98, 0.8, 0.25); c.set_line_width(10); c.stroke()
    return sticker(_pil(s))
def seward(expr='neutral', S=420):
    """US Secretary of State caricature: wild grey hair, big nose, high white collar, bow tie, dark frock coat, stars-and-stripes pin."""
    s, c = _surf(S, int(S * 1.25)); k = S / 420; c.scale(k, k); cx = 210
    c.move_to(60, 525); c.curve_to(70, 420, 140, 395, 210, 395); c.curve_to(280, 395, 350, 420, 360, 525); c.close_path(); fillstroke(c, (0.14, 0.14, 0.2))
    c.move_to(160, 398); c.line_to(210, 470); c.line_to(260, 398); c.close_path(); fillstroke(c, (1, 1, 1), 5)
    c.move_to(185, 412); c.line_to(235, 432); c.line_to(235, 402); c.line_to(185, 432); c.close_path(); fillstroke(c, (0.1, 0.1, 0.12), 4)
    ell(c, 290, 450, 14, 14); fillstroke(c, (0.15, 0.3, 0.75), 4)
    ell(c, cx, 270, 106, 126); fillstroke(c, SKIN)
    for sx in (-1, 1): ell(c, cx + sx * 106, 280, 18, 28); fillstroke(c, SKIN_D, 5)
    # grey hair tufts
    c.new_path()
    for i in range(9):
        a = math.pi * (1.05 + i * 0.1); x = cx + math.cos(a) * 112; y = 225 + math.sin(a) * 118
        ell(c, x, y, 38, 30)
    c.set_source_rgb(0.86, 0.86, 0.88); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    for sx in (-1, 1): ell(c, cx + sx * 96, 300, 22, 46); fillstroke(c, (0.86, 0.86, 0.88), 5)   # side whiskers
    eyes(c, cx, 250, 40, expr)
    c.new_path(); c.move_to(cx - 6, 262); c.curve_to(cx + 60, 290, cx + 40, 330, cx - 10, 318); fillstroke(c, SKIN_D, 5)   # big nose
    mouth(c, cx, 352, expr, 30)
    return sticker(_pil(s))
def person(expr='laugh', S=160, col=(0.25, 0.45, 0.8)):
    s, c = _surf(S, int(S * 1.4)); k = S / 160; c.scale(k, k)
    c.move_to(20, 224); c.curve_to(25, 160, 55, 150, 80, 150); c.curve_to(105, 150, 135, 160, 140, 224); c.close_path(); fillstroke(c, col, 4)
    ell(c, 80, 95, 52, 56); fillstroke(c, SKIN, 4)
    c.new_path(); c.arc(80, 70, 52, math.pi, 2 * math.pi); c.close_path(); fillstroke(c, (0.35, 0.22, 0.14), 4)
    for sx in (-1, 1):
        c.new_path(); c.arc(80 + sx * 18, 98, 8, math.pi * 1.15, math.pi * 1.85); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.new_path(); c.move_to(62, 112); c.curve_to(62, 140, 98, 140, 98, 112); c.close_path(); fillstroke(c, (0.55, 0.1, 0.12), 3)
    return sticker(_pil(s), ow=5)
# ---------- props ----------
def bubble(text, font_px=58, pad=34, tail='left', col=(1, 1, 1)):
    s, c = _surf(10, 10); c.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(font_px)
    lines = text.split('\n'); ws = [c.text_extents(l).x_advance for l in lines]; w = int(max(ws) + pad * 2); h = int(len(lines) * font_px * 1.2 + pad * 1.6)
    s, c = _surf(w + 20, h + 70); c.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(font_px)
    r = 34; x0, y0, x1, y1 = 10, 10, 10 + w, 10 + h
    c.new_path(); c.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi); c.arc(x1 - r, y0 + r, r, 1.5 * math.pi, 0); c.arc(x1 - r, y1 - r, r, 0, 0.5 * math.pi)
    tx = x0 + 70 if tail == 'left' else x1 - 70
    c.line_to(tx + 26, y1); c.line_to(tx + (-20 if tail == 'left' else 40), y1 + 52); c.line_to(tx - 26, y1)
    c.arc(x0 + r, y1 - r, r, 0.5 * math.pi, math.pi); c.close_path(); fillstroke(c, col, 6)
    c.set_source_rgb(*INK)
    for i, l in enumerate(lines):
        c.move_to(10 + pad, 10 + pad * 0.8 + font_px * (i + 0.95) * 1.2 - font_px * 0.2); c.show_text(l)
    return _pil(s)
def moneybag(S=260):
    s, c = _surf(S, S); k = S / 260; c.scale(k, k)
    c.move_to(95, 70); c.curve_to(20, 120, 20, 240, 130, 240); c.curve_to(240, 240, 240, 120, 165, 70); c.close_path(); fillstroke(c, (0.82, 0.68, 0.38))
    c.move_to(95, 70); c.line_to(80, 30); c.line_to(130, 52); c.line_to(180, 30); c.line_to(165, 70); c.close_path(); fillstroke(c, (0.82, 0.68, 0.38))
    c.rectangle(90, 62, 80, 14); fillstroke(c, (0.55, 0.35, 0.2), 4)
    c.select_font_face('Sans', 0, 1); c.set_font_size(96); c.set_source_rgb(0.18, 0.5, 0.25); c.move_to(100, 200); c.show_text('$')
    return sticker(_pil(s))
def coin(text='2¢', S=230):
    s, c = _surf(S, S); k = S / 230; c.scale(k, k)
    ell(c, 115, 115, 100, 100); fillstroke(c, (0.82, 0.5, 0.28), 7); ell(c, 115, 115, 78, 78); c.set_source_rgb(0.9, 0.6, 0.35); c.set_line_width(5); c.stroke()
    c.select_font_face('Sans', 0, 1); c.set_font_size(84); e = c.text_extents(text); c.set_source_rgb(0.45, 0.22, 0.1); c.move_to(115 - e.width / 2 - e.x_bearing, 145); c.show_text(text)
    return sticker(_pil(s))
def fridge(S=300):
    s, c = _surf(S, int(S * 1.6)); k = S / 300; c.scale(k, k)
    c.new_path(); c.rectangle(30, 20, 240, 440); fillstroke(c, (0.93, 0.96, 0.99), 8)
    c.move_to(30, 170); c.line_to(270, 170); c.set_source_rgb(*INK); c.set_line_width(6); c.stroke()
    for y0, y1 in ((60, 130), (210, 330)): c.rectangle(230, y0, 16, y1 - y0); fillstroke(c, (0.7, 0.75, 0.8), 4)
    for i in range(7):   # frost
        ell(c, 60 + i * 30, 26, 18, 10); c.set_source_rgb(0.75, 0.9, 1.0); c.fill()
    return sticker(_pil(s))
def nugget(S=150):
    s, c = _surf(S, S); k = S / 150; c.scale(k, k)
    c.move_to(25, 95); c.curve_to(20, 40, 70, 25, 100, 40); c.curve_to(140, 50, 135, 110, 95, 122); c.curve_to(60, 132, 30, 125, 25, 95); c.close_path(); fillstroke(c, (0.98, 0.78, 0.15), 5)
    ell(c, 65, 60, 14, 8); c.set_source_rgb(1, 0.95, 0.7); c.fill()
    return sticker(_pil(s), ow=5)
def derrick(S=260):
    s, c = _surf(S, int(S * 1.3)); k = S / 260; c.scale(k, k)
    c.set_source_rgb(*INK); c.set_line_width(9)
    c.move_to(60, 320); c.line_to(130, 40); c.line_to(200, 320); c.stroke()
    for y in (120, 200, 270):
        t = (y - 40) / 280; c.move_to(130 - 70 * t, y); c.line_to(130 + 70 * t, y); c.stroke()
    c.move_to(80, 240); c.line_to(170, 140); c.move_to(180, 240); c.line_to(95, 150); c.set_line_width(6); c.stroke()
    for i, (dx, dy) in enumerate(((0, 0), (-30, 26), (30, 22), (0, 40))):   # oil gush
        ell(c, 130 + dx, 22 + dy - 30, 22, 26); c.set_source_rgb(0.08, 0.08, 0.1); c.fill()
    return sticker(_pil(s), ow=6)
def receipt(S=260, text='REFUND?'):
    s, c = _surf(S, int(S * 1.35)); k = S / 260; c.scale(k, k)
    c.new_path(); c.move_to(30, 20); c.line_to(230, 20); c.line_to(230, 320)
    for i in range(8): c.line_to(230 - i * 25 - 12, 335 if i % 2 == 0 else 320)
    c.line_to(30, 320); c.close_path(); fillstroke(c, (1, 1, 0.97), 6)
    c.select_font_face('Sans', 0, 1); c.set_source_rgb(*INK); c.set_font_size(24); c.move_to(48, 70); c.show_text('ALASKA, 1867')
    c.set_font_size(17); c.move_to(44, 120); c.show_text('Land ..... $7,200,000')
    c.move_to(48, 155); c.show_text('Gold ................ $0')
    c.move_to(48, 190); c.show_text('Oil ................... $0')
    c.set_font_size(36); c.set_source_rgb(0.85, 0.15, 0.2); c.move_to(48, 270); c.show_text(text)
    return sticker(_pil(s))
if __name__ == '__main__':
    items = [tsar('neutral'), tsar('worried'), tsar('laugh'), seward('smug'), seward('happy'), seward('shock'), person(), moneybag(), coin(), fridge(), nugget(), derrick(), receipt(), bubble('Wanna buy\nAlaska?')]
    W = sum(i.width for i in items[:7]) + 80; out = Image.new('RGBA', (2600, 1300), (60, 110, 140, 255)); x = 20; y = 20; mh = 0
    for im in items:
        if x + im.width > 2600: x = 20; y += mh + 20; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 20; mh = max(mh, im.height)
    out.convert('RGB').resize((1300, 650)).save('/tmp/claude-0/fr/toons.png')
