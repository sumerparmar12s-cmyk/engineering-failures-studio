"""Shaded (pseudo-3D) military units for the Korean War map, drawn with cairo gradients. 3/4 view facing right."""
import math, cairo, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from toons import _pil, sticker, INK
import flags as FL
def _surf(w, h):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); return s, c
def sh(col, k): return tuple(min(1, max(0, v * k)) for v in col)
def lin(c, x0, y0, x1, y1, col, ks=(1.25, 1.0, 0.6)):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for i, k in enumerate(ks): g.add_color_stop_rgb(i / (len(ks) - 1), *sh(col, k))
    return g
def rr(c, x, y, w, h, r):
    c.new_path(); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.arc(x + w - r, y + r, r, 1.5 * math.pi, 0); c.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi); c.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi); c.close_path()
def star(c, cx, cy, r):
    c.new_path()
    for i in range(10): rr_ = r if i % 2 == 0 else r * 0.4; a = -math.pi / 2 + i * math.pi / 5; c.line_to(cx + rr_ * math.cos(a), cy + rr_ * math.sin(a))
    c.close_path()
def contact_shadow(im, k=0.42):
    w, h = im.size; out = Image.new('RGBA', (w, h + 30), (0, 0, 0, 0)); m = Image.new('L', (w, h + 30), 0)
    ImageDraw.Draw(m).ellipse([w * 0.08, h - 30, w * 0.92, h + 18], fill=int(255 * k)); m = m.filter(ImageFilter.GaussianBlur(10))
    sh_ = Image.new('RGBA', m.size, (10, 10, 10, 0)); sh_.putalpha(m); out.alpha_composite(sh_); out.alpha_composite(im, (0, 0)); return out
# ---------------- tanks ----------------
def tank(side='nk', S=320, phase=0.0, fire=False):
    """side: 'nk' (T-34/85, green, red star) | 'us' (M26/M4, olive drab, white star)."""
    body = (0.30, 0.38, 0.22) if side == 'nk' else (0.36, 0.38, 0.24)
    s, c = _surf(S, int(S * 0.72)); k = S / 320; c.scale(k, k)
    # tracks (side + top)
    rr(c, 20, 140, 270, 62, 30); c.set_source(lin(c, 0, 140, 0, 202, (0.22, 0.22, 0.2), (1.2, 0.8, 0.45))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    for i in range(6):
        x = 48 + i * 43 + (phase * 12) % 43 * 0
        c.arc(x, 172, 17, 0, 2 * math.pi); c.set_source(cairo.RadialGradient(x - 5, 166, 2, x, 172, 18)); c.get_source().add_color_stop_rgb(0, 0.6, 0.6, 0.55); c.get_source().add_color_stop_rgb(1, 0.18, 0.18, 0.16); c.fill()
    for i in range(18):   # moving track links
        x = 30 + ((i * 15 + phase * 40) % 255); c.rectangle(x, 140, 5, 8); c.set_source_rgba(0.12, 0.12, 0.1, 0.8); c.fill()
    # hull (top face lighter, side darker)
    c.new_path(); c.move_to(35, 145); c.line_to(70, 108); c.line_to(250, 108); c.line_to(292, 145); c.close_path(); c.set_source(lin(c, 0, 108, 0, 145, body, (1.35, 1.1, 0.85))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.rectangle(35, 140, 257, 18); c.set_source(lin(c, 0, 140, 0, 158, body, (0.85, 0.6))); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    # turret
    c.new_path(); c.move_to(110, 108); c.curve_to(110, 62, 205, 55, 222, 82); c.line_to(228, 108); c.close_path()
    g = cairo.RadialGradient(150, 70, 8, 165, 90, 80); g.add_color_stop_rgb(0, *sh(body, 1.45)); g.add_color_stop_rgb(1, *sh(body, 0.7)); c.set_source(g); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    # barrel
    rr(c, 215, 76, 105 if side == 'nk' else 95, 13, 6); c.set_source(lin(c, 0, 76, 0, 89, body, (1.4, 0.9, 0.55))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(3); c.stroke()
    if side == 'us': rr(c, 300, 73, 18, 19, 4); c.set_source_rgb(*sh(body, 0.7)); c.fill()
    # hatch + commander
    c.arc(150, 62, 16, math.pi, 2 * math.pi); c.set_source_rgb(*sh(body, 0.75)); c.fill()
    # markings
    if side == 'nk': star(c, 160, 90, 13); c.set_source_rgb(0.9, 0.12, 0.12); c.fill()
    else: c.arc(165, 88, 15, 0, 2 * math.pi); c.set_source_rgb(1, 1, 1); c.set_line_width(3); c.stroke(); star(c, 165, 88, 12); c.set_source_rgb(1, 1, 1); c.fill()
    if fire:
        bx = 325 if side == 'nk' else 315
        for i in range(10):
            a = i / 10 * 2 * math.pi; r = 18 + (i % 2) * 16; c.line_to(bx + 6 + math.cos(a) * r, 83 + math.sin(a) * r * 0.8)
        c.close_path(); c.set_source_rgb(1, 0.85, 0.3); c.fill()
    return contact_shadow(sticker(_pil(s), ow=4))
# ---------------- soldiers ----------------
UNI = {'us': dict(coat=(0.40, 0.42, 0.28), helmet=(0.33, 0.36, 0.22), kind='m1'),
       'uk': dict(coat=(0.48, 0.44, 0.30), helmet=(0.38, 0.38, 0.26), kind='brodie'),
       'nk': dict(coat=(0.55, 0.52, 0.36), helmet=(0.45, 0.42, 0.28), kind='cap'),
       'pva': dict(coat=(0.45, 0.46, 0.35), helmet=(0.40, 0.38, 0.28), kind='furcap'),
       'kr': dict(coat=(0.38, 0.40, 0.27), helmet=(0.30, 0.33, 0.21), kind='m1')}
def soldier(side='us', phase=0.0, S=150, rifle=True):
    u = UNI[side]; s, c = _surf(S, int(S * 1.7)); k = S / 150; c.scale(k, k)
    skin = (0.96, 0.78, 0.62)
    for i, ph in enumerate((phase, phase + math.pi)):   # legs
        th = math.sin(ph) * 0.45; x2 = 75 + math.sin(th) * 85; y2 = 160 + math.cos(th) * 85
        c.move_to(75, 160); c.line_to(x2, y2); c.set_source_rgb(*INK); c.set_line_width(27); c.stroke()
        c.move_to(75, 160); c.line_to(x2, y2); c.set_source_rgb(*sh(u['coat'], 0.85 if i else 1.0)); c.set_line_width(19); c.stroke()
        c.arc(x2 + 6, y2 + 2, 10, 0, 2 * math.pi); c.set_source_rgb(0.18, 0.14, 0.1); c.fill()
    rr(c, 40, 85, 70, 92, 26); c.set_source(lin(c, 40, 0, 110, 0, u['coat'], (1.3, 1.05, 0.65))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    if side == 'pva':   # quilted lines
        for y in (105, 125, 145, 165): c.move_to(44, y); c.line_to(106, y); c.set_source_rgba(0, 0, 0, 0.25); c.set_line_width(2); c.stroke()
    c.move_to(50, 120); c.line_to(100, 120); c.set_source_rgb(*sh(u['coat'], 0.55)); c.set_line_width(5); c.stroke()   # belt
    if rifle:
        c.move_to(55, 145); c.line_to(140, 88); c.set_source_rgb(0.35, 0.22, 0.12); c.set_line_width(9); c.stroke(); c.move_to(118, 102); c.line_to(150, 81); c.set_source_rgb(0.15, 0.15, 0.15); c.set_line_width(5); c.stroke()
        c.arc(108, 112, 10, 0, 2 * math.pi); c.set_source_rgb(*skin); c.fill()
    # head with radial shading
    g = cairo.RadialGradient(68, 52, 4, 75, 62, 34); g.add_color_stop_rgb(0, 1, 0.88, 0.75); g.add_color_stop_rgb(1, *sh(skin, 0.75))
    c.arc(75, 62, 30, 0, 2 * math.pi); c.set_source(g); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.arc(86, 60, 4.5, 0, 2 * math.pi); c.set_source_rgb(*INK); c.fill()
    hk = u['kind']; hc = u['helmet']
    if hk == 'm1':
        c.new_path(); c.arc(75, 55, 35, math.pi * 1.02, math.pi * 1.98); c.line_to(112, 60); c.line_to(38, 60); c.close_path()
    elif hk == 'brodie':
        c.new_path(); c.save(); c.translate(75, 50); c.scale(1.55, 0.35); c.arc(0, 0, 32, 0, 2 * math.pi); c.restore(); c.set_source(lin(c, 0, 40, 0, 60, hc)); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(3.5); c.stroke()
        c.new_path(); c.arc(75, 50, 24, math.pi, 2 * math.pi); c.close_path()
    elif hk == 'cap':
        c.new_path(); c.move_to(45, 48); c.curve_to(55, 22, 100, 22, 106, 46); c.line_to(45, 48); c.close_path()
    else:   # PVA fur-lined cap with ear flaps
        c.new_path(); c.arc(75, 52, 33, math.pi, 2 * math.pi); c.line_to(108, 80); c.line_to(96, 82); c.line_to(96, 55); c.line_to(54, 55); c.line_to(54, 82); c.line_to(42, 80); c.close_path()
    if hk != 'brodie' or True:
        c.set_source(lin(c, 0, 20, 0, 70, hc, (1.4, 1.0, 0.6))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(3.5); c.stroke()
    if hk in ('cap', 'furcap'): star(c, 75, 38, 8); c.set_source_rgb(0.9, 0.15, 0.15); c.fill()
    return contact_shadow(sticker(_pil(s), ow=3), 0.35)
# ---------------- ships, plane, tent ----------------
def ship(flag='United States of America', S=360, wake=0.0):
    s, c = _surf(S, int(S * 0.62)); k = S / 360; c.scale(k, k)
    c.new_path(); c.move_to(10, 140); c.line_to(345, 140); c.line_to(320, 185); c.line_to(40, 185); c.close_path(); c.set_source(lin(c, 0, 140, 0, 185, (0.48, 0.52, 0.56), (1.25, 0.9, 0.55))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.new_path(); c.move_to(18, 140); c.line_to(345, 140); c.line_to(330, 126); c.line_to(30, 126); c.close_path(); c.set_source_rgb(0.62, 0.66, 0.7); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    rr(c, 190, 80, 90, 48, 6); c.set_source(lin(c, 190, 0, 280, 0, (0.55, 0.58, 0.62))); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    rr(c, 215, 52, 40, 30, 4); c.set_source(lin(c, 215, 0, 255, 0, (0.5, 0.53, 0.57))); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    for i in range(4): c.rectangle(200 + i * 20, 92, 11, 10); c.set_source_rgb(0.85, 0.9, 0.95); c.fill()
    c.move_to(235, 52); c.line_to(235, 12); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    fs = FL.flag_surface(flag, 54, 36); c.set_source_surface(fs, 238, 12); c.paint(); c.rectangle(238, 12, 54, 36); c.set_source_rgb(*INK); c.set_line_width(2); c.stroke()
    c.move_to(80, 126); c.line_to(80, 106); c.line_to(130, 106); c.line_to(130, 126); c.set_source_rgb(0.35, 0.38, 0.4); c.set_line_width(5); c.stroke()   # landing ramp frame
    return sticker(_pil(s), ow=4)
def plane(S=260):
    s, c = _surf(S, int(S * 0.55)); k = S / 260; c.scale(k, k)
    c.new_path(); c.move_to(20, 72); c.curve_to(60, 58, 200, 58, 248, 70); c.curve_to(200, 84, 60, 86, 20, 72); c.set_source(lin(c, 0, 58, 0, 86, (0.75, 0.77, 0.8), (1.25, 1.0, 0.6))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(3.5); c.stroke()
    c.new_path(); c.move_to(110, 70); c.line_to(160, 18); c.line_to(178, 18); c.line_to(150, 72); c.close_path(); c.set_source_rgb(0.68, 0.7, 0.73); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    c.new_path(); c.move_to(110, 74); c.line_to(145, 128); c.line_to(162, 128); c.line_to(150, 74); c.close_path(); c.set_source_rgb(0.58, 0.6, 0.63); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    c.new_path(); c.move_to(22, 70); c.line_to(10, 38); c.line_to(30, 38); c.line_to(45, 66); c.close_path(); c.set_source_rgb(0.68, 0.7, 0.73); c.fill_preserve(); c.set_source_rgb(*INK); c.stroke()
    c.arc(150, 95, 10, 0, 2 * math.pi); c.set_source_rgb(1, 1, 1); c.fill(); star(c, 150, 95, 8); c.set_source_rgb(0.15, 0.25, 0.55); c.fill()
    return sticker(_pil(s), ow=3)
def medtent(S=300):
    s, c = _surf(S, int(S * 0.85)); k = S / 300; c.scale(k, k)
    c.new_path(); c.move_to(30, 220); c.line_to(150, 70); c.line_to(270, 220); c.close_path(); c.set_source(lin(c, 30, 0, 270, 0, (0.92, 0.92, 0.88), (1.08, 1.0, 0.72))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.new_path(); c.move_to(150, 70); c.line_to(150, 220); c.set_source_rgba(0, 0, 0, 0.25); c.set_line_width(3); c.stroke()
    c.rectangle(135, 135, 30, 72); c.rectangle(115, 157, 70, 28); c.set_source_rgb(0.85, 0.1, 0.12); c.fill()
    c.move_to(150, 70); c.line_to(150, 20); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    fs = FL.flag_surface('Norway', 60, 40); c.set_source_surface(fs, 152, 20); c.paint(); c.rectangle(152, 20, 60, 40); c.set_source_rgb(*INK); c.set_line_width(2); c.stroke()
    return contact_shadow(sticker(_pil(s), ow=4))
def document(S=320):
    s, c = _surf(S, int(S * 1.25)); k = S / 320; c.scale(k, k)
    c.rectangle(30, 20, 260, 340); c.set_source(lin(c, 30, 0, 290, 0, (0.98, 0.95, 0.85), (1.0, 1.02, 0.92))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.select_font_face('Serif', 0, 1); c.set_source_rgb(*INK); c.set_font_size(30); e = c.text_extents('ARMISTICE'); c.move_to(160 - e.width / 2, 75); c.show_text('ARMISTICE')
    c.set_font_size(22); e = c.text_extents('July 27, 1953'); c.move_to(160 - e.width / 2, 110); c.show_text('July 27, 1953')
    for i in range(7): c.rectangle(60, 140 + i * 22, 200 - (i % 3) * 30, 6); c.set_source_rgba(0, 0, 0, 0.35); c.fill()
    for x, y in ((70, 320), (200, 315)): c.move_to(x, y); c.curve_to(x + 20, y - 25, x + 40, y + 15, x + 70, y - 10); c.set_source_rgb(0.1, 0.15, 0.45); c.set_line_width(3); c.stroke()
    return sticker(_pil(s))
def explosion(frame, S=220):
    """frame 0..9: flash -> fireball -> smoke"""
    s, c = _surf(S, S); u = frame / 9.0; cx, cy = S / 2, S * 0.6
    if u < 0.6:
        r = S * (0.22 + 0.55 * u); g = cairo.RadialGradient(cx, cy, 2, cx, cy, r); g.add_color_stop_rgba(0, 1, 1, 0.85, 1); g.add_color_stop_rgba(0.45, 1, 0.75, 0.2, 0.95); g.add_color_stop_rgba(0.85, 0.95, 0.35, 0.05, 0.6); g.add_color_stop_rgba(1, 0.9, 0.25, 0.05, 0.0)
        c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source(g); c.fill()
    rng = np.random.default_rng(2)
    for i in range(8):
        a = rng.uniform(0, 2 * math.pi); d = S * 0.08 + S * 0.3 * u; r = S * (0.08 + 0.12 * u)
        x = cx + math.cos(a) * d; y = cy + math.sin(a) * d * 0.6 - S * 0.25 * u
        c.arc(x, y, r, 0, 2 * math.pi); c.set_source_rgba(0.25, 0.23, 0.22, max(0, 0.75 - 0.6 * u) if u > 0.25 else 0); c.fill()
    return _pil(s)
if __name__ == '__main__':
    out = Image.new('RGBA', (2600, 1100), (90, 120, 90, 255)); x = 20; y = 20; mh = 0
    items = [tank('nk', 320, 0, True), tank('us', 320), soldier('us', 0.4), soldier('uk', 1.2), soldier('nk', 0.0), soldier('pva', 0.8), soldier('kr', 2.0), ship(), ship('United Kingdom'), plane(), medtent(), document()] + [explosion(f, 160) for f in (1, 3, 6, 8)]
    for im in items:
        if x + im.width > 2600: x = 20; y += mh + 20; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 20; mh = max(mh, im.height)
    out.convert('RGB').resize((1300, 550)).save('/tmp/claude-0/fr/units.png')
