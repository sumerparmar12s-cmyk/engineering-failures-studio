"""Pseudo-3D 'figurine' characters and props (cairo gradients: key light top-left, rim light, contact shadow)."""
import math, cairo
import numpy as np
from PIL import Image, ImageFilter
def _surf(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); return s, c
def _pil(s):
    w, h = s.get_width(), s.get_height(); a = np.frombuffer(s.get_data(), np.uint8).reshape(h, s.get_stride() // 4, 4)[:, :w]
    b, g, r, al = [a[..., i].astype(np.float32) for i in range(4)]; m = np.maximum(al, 1) / 255
    return Image.fromarray(np.dstack([r / m, g / m, b / m, al]).clip(0, 255).astype(np.uint8), 'RGBA')
def shade(col, k): return tuple(min(1, max(0, v * k)) for v in col)
def ball(c, x, y, r, col, gloss=0.35):
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r * 1.05)
    g.add_color_stop_rgb(0, *shade(col, 1.25)); g.add_color_stop_rgb(0.55, *col); g.add_color_stop_rgb(1, *shade(col, 0.55))
    c.new_path(); c.arc(x, y, r, 0, 2 * math.pi); c.set_source(g); c.fill()
    if gloss:
        g2 = cairo.RadialGradient(x - r * 0.38, y - r * 0.45, 0, x - r * 0.38, y - r * 0.45, r * 0.45); g2.add_color_stop_rgba(0, 1, 1, 1, gloss); g2.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.arc(x, y, r, 0, 2 * math.pi); c.set_source(g2); c.fill()
def body(c, x, top, w, h, col):
    """rounded capsule torso with cylindrical shading"""
    c.new_path(); r = w / 2
    c.move_to(x - r, top + r); c.arc(x, top + r, r, math.pi, 0); c.line_to(x + r, top + h - 12); c.curve_to(x + r, top + h + 6, x - r, top + h + 6, x - r, top + h - 12); c.close_path()
    g = cairo.LinearGradient(x - r, 0, x + r, 0)
    g.add_color_stop_rgb(0, *shade(col, 0.6)); g.add_color_stop_rgb(0.3, *shade(col, 1.18)); g.add_color_stop_rgb(0.7, *col); g.add_color_stop_rgb(1, *shade(col, 0.5))
    c.set_source(g); c.fill_preserve(); c.set_source_rgba(0, 0, 0, 0.25); c.set_line_width(2); c.stroke()
def face(c, x, y, r, expr='happy'):
    for sx in (-1, 1):
        ex = x + sx * r * 0.33; ey = y - r * 0.05
        if expr in ('happy', 'laugh'):
            c.new_path(); c.arc(ex, ey + 4, r * 0.11, math.pi * 1.1, math.pi * 1.9); c.set_source_rgb(0.12, 0.08, 0.06); c.set_line_width(r * 0.06); c.stroke()
        else:
            c.new_path(); c.arc(ex, ey, r * 0.085, 0, 6.3); c.set_source_rgb(0.1, 0.07, 0.05); c.fill()
            c.arc(ex - r * 0.03, ey - r * 0.03, r * 0.03, 0, 6.3); c.set_source_rgb(1, 1, 1); c.fill()
        c.new_path(); c.arc(x + sx * r * 0.45, y + r * 0.22, r * 0.12, 0, 6.3); c.set_source_rgba(1, 0.45, 0.45, 0.35); c.fill()
    c.new_path()
    if expr == 'laugh':
        c.move_to(x - r * 0.25, y + r * 0.25); c.curve_to(x - r * 0.2, y + r * 0.6, x + r * 0.2, y + r * 0.6, x + r * 0.25, y + r * 0.25); c.close_path(); c.set_source_rgb(0.5, 0.1, 0.12); c.fill()
    elif expr == 'worried':
        c.move_to(x - r * 0.18, y + r * 0.42); c.curve_to(x - r * 0.08, y + r * 0.32, x + r * 0.08, y + r * 0.32, x + r * 0.18, y + r * 0.42); c.set_source_rgb(0.15, 0.08, 0.06); c.set_line_width(r * 0.05); c.stroke()
    elif expr == 'shock':
        c.arc(x, y + r * 0.38, r * 0.1, 0, 6.3); c.set_source_rgb(0.4, 0.08, 0.1); c.fill()
    else:
        c.move_to(x - r * 0.2, y + r * 0.3); c.curve_to(x - r * 0.08, y + r * 0.42, x + r * 0.08, y + r * 0.42, x + r * 0.2, y + r * 0.3); c.set_source_rgb(0.15, 0.08, 0.06); c.set_line_width(r * 0.05); c.stroke()
SKIN = (0.98, 0.80, 0.66)
def _finish(s, shadow=True):
    im = _pil(s)
    if not shadow: return im
    w, h = im.size; out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    sh = Image.new('L', (w, h), 0); from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse([w * 0.22, h * 0.9, w * 0.78, h * 0.985], fill=120); sh = sh.filter(ImageFilter.GaussianBlur(8))
    blk = Image.new('RGBA', (w, h), (20, 15, 10, 0)); blk.putalpha(sh); out.alpha_composite(blk); out.alpha_composite(im); return out
def figure(kind, expr='happy', S=300):
    """kind: 'dutch' (VOC merchant), 'stuyvesant' (peg leg governor), 'king' (Charles II), 'redcoat' (English officer)"""
    s, c = _surf(S, int(S * 1.52)); k = S / 300; c.scale(k, k); c.translate(0, 22); x = 150
    if kind == 'stuyvesant':   # peg leg + boot
        c.rectangle(118, 360, 18, 60); g = cairo.LinearGradient(118, 0, 136, 0); g.add_color_stop_rgb(0, 0.45, 0.3, 0.15); g.add_color_stop_rgb(0.5, 0.7, 0.5, 0.28); g.add_color_stop_rgb(1, 0.4, 0.26, 0.13); c.set_source(g); c.fill()
        c.new_path(); c.move_to(160, 360); c.line_to(160, 405); c.curve_to(160, 422, 196, 422, 196, 410); c.line_to(180, 360); c.close_path(); c.set_source_rgb(0.12, 0.1, 0.1); c.fill()
    coat = {'dutch': (0.13, 0.13, 0.16), 'stuyvesant': (0.16, 0.16, 0.2), 'king': (0.72, 0.1, 0.14), 'redcoat': (0.78, 0.12, 0.12)}[kind]
    body(c, x, 200, 170, 175, coat)
    if kind in ('dutch', 'stuyvesant'):   # white falling-band collar
        c.new_path(); c.move_to(95, 215); c.curve_to(110, 260, 190, 260, 205, 215); c.curve_to(180, 230, 120, 230, 95, 215); c.set_source_rgb(0.97, 0.97, 0.97); c.fill()
    if kind == 'king':   # ermine stole + gold buttons
        c.new_path(); c.move_to(80, 225); c.curve_to(110, 265, 190, 265, 220, 225); c.line_to(220, 245); c.curve_to(190, 285, 110, 285, 80, 245); c.close_path(); c.set_source_rgb(0.97, 0.96, 0.92); c.fill()
        for i in range(5): c.arc(100 + i * 25, 250 + (abs(i - 2) * -4), 3, 0, 6.3); c.set_source_rgb(0.1, 0.1, 0.1); c.fill()
    if kind == 'redcoat':
        for i in range(4): ball(c, x, 260 + i * 28, 6, (0.95, 0.78, 0.25), 0.4)
        c.rectangle(80, 300, 140, 14); c.set_source_rgb(0.95, 0.95, 0.9); c.fill()
    if kind == 'king':   # long dark curly wig behind head
        for i in range(10):
            a = math.pi * (0.05 + i * 0.1); ball(c, x + math.cos(a) * 82, 140 + math.sin(a) * 70 - 10, 26, (0.18, 0.12, 0.09), 0.15)
    ball(c, x, 130, 78, SKIN, 0.25); face(c, x, 140, 78, expr)
    if kind in ('dutch', 'stuyvesant'):   # moustache + goatee
        c.new_path(); c.move_to(x - 26, 172); c.curve_to(x - 10, 160, x + 10, 160, x + 26, 172); c.set_source_rgb(0.35, 0.22, 0.12); c.set_line_width(7); c.stroke()
        c.new_path(); c.move_to(x - 7, 196); c.line_to(x + 7, 196); c.line_to(x, 214); c.close_path(); c.fill()
    # hats
    if kind == 'dutch':
        c.new_path(); c.save(); c.translate(x, 72); c.scale(1.45, 0.32); c.arc(0, 0, 80, 0, 6.3); c.restore(); c.set_source_rgb(0.08, 0.08, 0.1); c.fill()
        c.new_path(); c.move_to(x - 55, 70); c.line_to(x - 45, 0); c.curve_to(x - 20, -12, x + 20, -12, x + 45, 0); c.line_to(x + 55, 70); c.close_path()
        g = cairo.LinearGradient(x - 55, 0, x + 55, 0); g.add_color_stop_rgb(0, 0.05, 0.05, 0.07); g.add_color_stop_rgb(0.35, 0.22, 0.22, 0.26); g.add_color_stop_rgb(1, 0.04, 0.04, 0.05); c.set_source(g); c.fill()
        c.rectangle(x - 52, 50, 104, 12); c.set_source_rgb(0.75, 0.6, 0.25); c.fill()
    if kind == 'stuyvesant':   # skullcap + long hair
        c.new_path(); c.arc(x, 112, 74, math.pi * 1.05, math.pi * 1.95); c.close_path(); c.set_source_rgb(0.1, 0.1, 0.12); c.fill()
    if kind == 'king':   # crown
        c.new_path(); c.move_to(x - 48, 70); c.line_to(x - 52, 20); c.line_to(x - 25, 45); c.line_to(x, 8); c.line_to(x + 25, 45); c.line_to(x + 52, 20); c.line_to(x + 48, 70); c.close_path()
        g = cairo.LinearGradient(x - 50, 0, x + 50, 0); g.add_color_stop_rgb(0, 0.75, 0.55, 0.1); g.add_color_stop_rgb(0.35, 1, 0.9, 0.45); g.add_color_stop_rgb(1, 0.65, 0.45, 0.08); c.set_source(g); c.fill()
        for dx in (-25, 0, 25): ball(c, x + dx, 58, 7, (0.85, 0.1, 0.2), 0.5)
    if kind == 'redcoat':   # tricorne
        c.new_path(); c.move_to(x - 90, 78); c.curve_to(x - 60, 20, x + 60, 20, x + 90, 78); c.curve_to(x + 30, 55, x - 30, 55, x - 90, 78); c.close_path(); c.set_source_rgb(0.08, 0.08, 0.1); c.fill()
        c.move_to(x - 88, 76); c.curve_to(x - 30, 52, x + 30, 52, x + 88, 76); c.set_source_rgb(0.95, 0.8, 0.3); c.set_line_width(4); c.stroke()
    return _finish(s)
def nutmeg(S=200):
    s, c = _surf(S, S); k = S / 200; c.scale(k, k)
    ball(c, 100, 105, 70, (0.55, 0.33, 0.18), 0.3)
    c.set_source_rgba(0.85, 0.15, 0.1, 0.9); c.set_line_width(7)   # red mace web
    for a in range(-60, 70, 25):
        c.new_path(); c.move_to(100 + a, 40); c.curve_to(100 + a * 1.4, 90, 100 + a * 0.8, 140, 100 + a * 0.3, 175); c.stroke()
    return _finish(s)
def ship(S=360, flag=(0.95, 0.5, 0.1)):
    s, c = _surf(S, int(S * 0.95)); k = S / 360; c.scale(k, k)
    c.new_path(); c.move_to(30, 230); c.line_to(330, 230); c.curve_to(310, 300, 60, 300, 30, 230); c.close_path()
    g = cairo.LinearGradient(0, 230, 0, 300); g.add_color_stop_rgb(0, 0.62, 0.38, 0.18); g.add_color_stop_rgb(1, 0.32, 0.18, 0.08); c.set_source(g); c.fill()
    c.rectangle(30, 222, 300, 10); c.set_source_rgb(0.85, 0.7, 0.3); c.fill()
    for mx, top in ((120, 40), (220, 60)):
        c.rectangle(mx - 4, top, 8, 190); c.set_source_rgb(0.35, 0.22, 0.1); c.fill()
        for i, (w_, y_) in enumerate(((90, top + 20), (110, top + 80))):
            c.new_path(); c.move_to(mx - w_ / 2, y_); c.curve_to(mx - w_ / 2 + 10, y_ + 40, mx + w_ / 2 - 10, y_ + 40, mx + w_ / 2, y_); c.line_to(mx + w_ / 2 - 4, y_ + 50); c.curve_to(mx, y_ + 62, mx, y_ + 62, mx - w_ / 2 + 4, y_ + 50); c.close_path()
            g = cairo.LinearGradient(mx - w_ / 2, 0, mx + w_ / 2, 0); g.add_color_stop_rgb(0, 0.85, 0.82, 0.72); g.add_color_stop_rgb(0.5, 1, 0.99, 0.94); g.add_color_stop_rgb(1, 0.78, 0.75, 0.66); c.set_source(g); c.fill()
        c.rectangle(mx + 4, top, 34, 18); c.set_source_rgb(*flag); c.fill()
    return _finish(s)
def scroll(S=320, title='Treaty of Breda', year='1667'):
    s, c = _surf(S, int(S * 1.2)); k = S / 320; c.scale(k, k)
    c.rectangle(50, 40, 220, 300); g = cairo.LinearGradient(50, 0, 270, 0); g.add_color_stop_rgb(0, 0.86, 0.78, 0.58); g.add_color_stop_rgb(0.5, 0.97, 0.92, 0.78); g.add_color_stop_rgb(1, 0.84, 0.75, 0.55); c.set_source(g); c.fill()
    for y in (40, 340):
        c.new_path(); c.save(); c.translate(160, y); c.scale(125, 16); c.arc(0, 0, 1, 0, 6.3); c.restore(); g = cairo.LinearGradient(0, y - 16, 0, y + 16); g.add_color_stop_rgb(0, 0.95, 0.88, 0.7); g.add_color_stop_rgb(1, 0.7, 0.6, 0.4); c.set_source(g); c.fill()
    c.select_font_face('Serif', 0, 1); c.set_source_rgb(0.25, 0.15, 0.08); c.set_font_size(28)
    for i, line in enumerate(title.split(' ')): e = c.text_extents(line); c.move_to(160 - e.width / 2, 110 + i * 34); c.show_text(line)
    c.set_font_size(36); e = c.text_extents(year); c.move_to(160 - e.width / 2, 220); c.show_text(year)
    for i in range(4): c.rectangle(80, 245 + i * 18, 160 - (i % 2) * 40, 5); c.set_source_rgba(0.3, 0.2, 0.1, 0.5); c.fill()
    ball(c, 230, 310, 22, (0.75, 0.1, 0.1), 0.4)
    return _finish(s)
def latte(S=220):
    s, c = _surf(S, int(S * 1.1)); k = S / 220; c.scale(k, k)
    c.new_path(); c.move_to(40, 70); c.line_to(180, 70); c.line_to(160, 220); c.line_to(60, 220); c.close_path()
    g = cairo.LinearGradient(40, 0, 180, 0); g.add_color_stop_rgb(0, 0.8, 0.8, 0.82); g.add_color_stop_rgb(0.4, 1, 1, 1); g.add_color_stop_rgb(1, 0.75, 0.75, 0.78); c.set_source(g); c.fill()
    c.new_path(); c.save(); c.translate(110, 70); c.scale(70, 14); c.arc(0, 0, 1, 0, 6.3); c.restore(); c.set_source_rgb(0.85, 0.7, 0.5); c.fill()
    for i in range(14):
        a = i * 2.4; ball(c, 110 + math.cos(a) * (8 + i * 3.5), 68 + math.sin(a) * (2 + i * 0.6), 3, (0.45, 0.25, 0.1), 0)
    c.new_path(); c.arc(185, 140, 26, -1.2, 1.2); c.set_source_rgb(0.85, 0.85, 0.88); c.set_line_width(9); c.stroke()
    return _finish(s)
if __name__ == '__main__':
    items = [figure('dutch', 'happy'), figure('stuyvesant', 'worried'), figure('king', 'happy'), figure('redcoat', 'neutral'), figure('dutch', 'laugh'), nutmeg(), ship(), ship(flag=(0.85, 0.1, 0.15)), scroll(), latte()]
    out = Image.new('RGBA', (2400, 1000), (200, 185, 150, 255)); x = 20; y = 20; mh = 0
    for im in items:
        if x + im.width > 2400: x = 20; y += mh + 10; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 10; mh = max(mh, im.height)
    out.convert('RGB').resize((1200, 500)).save('/tmp/claude-0/fr/p3d.png')
