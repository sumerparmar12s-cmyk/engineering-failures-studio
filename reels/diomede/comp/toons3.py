"""Flat cartoon stickers in the Point Roberts style (cairo): Dutch merchant, Stuyvesant (peg leg), King Charles II, English officer + props."""
import math, cairo
from toons import _surf, _pil, sticker, fillstroke, ell, eyes, mouth, SKIN, SKIN_D, INK, bubble
def _bust(c, coat):
    c.move_to(55, 525); c.curve_to(65, 420, 140, 392, 210, 392); c.curve_to(280, 392, 355, 420, 365, 525); c.close_path(); fillstroke(c, coat)
def dutch(expr='happy', S=400):
    s, c = _surf(S, int(S * 1.3)); k = S / 420; c.scale(k, k); c.translate(0, 20); cx = 210
    _bust(c, (0.12, 0.12, 0.14))
    c.new_path(); c.move_to(120, 400); c.curve_to(150, 450, 270, 450, 300, 400); c.curve_to(260, 425, 160, 425, 120, 400); fillstroke(c, (1, 1, 1), 5)   # flat white collar
    ell(c, cx, 270, 102, 120); fillstroke(c, SKIN)
    for sx in (-1, 1): ell(c, cx + sx * 102, 280, 17, 26); fillstroke(c, SKIN_D, 5)
    eyes(c, cx, 255, 40, expr); ell(c, cx, 292, 16, 14); fillstroke(c, SKIN_D, 4)
    c.new_path(); c.move_to(cx - 44, 318); c.curve_to(cx - 15, 300, cx + 15, 300, cx + 44, 318); c.curve_to(cx + 15, 312, cx - 15, 312, cx - 44, 318); fillstroke(c, (0.42, 0.26, 0.14), 4)   # moustache
    mouth(c, cx, 340, expr, 24)
    c.new_path(); c.move_to(cx - 12, 372); c.line_to(cx + 12, 372); c.line_to(cx, 400); c.close_path(); fillstroke(c, (0.42, 0.26, 0.14), 4)   # goatee
    c.new_path(); c.save(); c.translate(cx, 168); c.scale(1.6, 0.28); c.arc(0, 0, 105, 0, 6.3); c.restore(); fillstroke(c, (0.1, 0.1, 0.12))   # brim
    c.new_path(); c.move_to(cx - 72, 165); c.line_to(cx - 60, 52); c.curve_to(cx - 30, 38, cx + 30, 38, cx + 60, 52); c.line_to(cx + 72, 165); c.close_path(); fillstroke(c, (0.1, 0.1, 0.12))
    c.rectangle(cx - 70, 130, 140, 22); fillstroke(c, (0.3, 0.22, 0.12), 4); c.rectangle(cx - 16, 126, 32, 30); fillstroke(c, (0.95, 0.78, 0.25), 4)   # band + buckle
    return sticker(_pil(s))
def stuyvesant(expr='worried', S=380):
    """full body: black coat, sash, one boot + one wooden peg leg (he really had one)."""
    s, c = _surf(S, int(S * 1.9)); k = S / 420; c.scale(k, k); cx = 210
    c.rectangle(150, 600, 34, 150); fillstroke(c, (0.62, 0.43, 0.22), 5); ell(c, 167, 752, 20, 8); fillstroke(c, (0.45, 0.3, 0.15), 4)   # peg
    c.new_path(); c.move_to(236, 600); c.line_to(270, 600); c.line_to(272, 735); c.curve_to(272, 760, 330, 760, 330, 742); c.line_to(300, 720); c.line_to(300, 600); c.close_path(); fillstroke(c, (0.1, 0.1, 0.12), 5)   # boot
    c.new_path(); c.move_to(90, 620); c.curve_to(80, 470, 140, 392, 210, 392); c.curve_to(280, 392, 340, 470, 330, 620); c.close_path(); fillstroke(c, (0.15, 0.15, 0.2))   # long coat
    c.move_to(130, 420); c.line_to(300, 560); c.set_source_rgb(0.95, 0.55, 0.15); c.set_line_width(22); c.stroke()   # orange sash (Dutch)
    c.new_path(); c.move_to(140, 402); c.curve_to(170, 440, 250, 440, 280, 402); c.curve_to(250, 418, 170, 418, 140, 402); fillstroke(c, (1, 1, 1), 5)
    ell(c, cx, 280, 100, 118); fillstroke(c, SKIN)
    c.new_path(); c.arc(cx, 232, 98, math.pi * 1.02, math.pi * 1.98); c.close_path(); fillstroke(c, (0.12, 0.12, 0.14))   # skullcap
    for sx in (-1, 1): ell(c, cx + sx * 92, 300, 24, 50); fillstroke(c, (0.4, 0.28, 0.18), 4)   # hair
    eyes(c, cx, 268, 38, expr); ell(c, cx, 304, 15, 13); fillstroke(c, SKIN_D, 4)
    c.new_path(); c.move_to(cx - 40, 326); c.curve_to(cx - 12, 312, cx + 12, 312, cx + 40, 326); fillstroke(c, (0.4, 0.28, 0.18), 4); mouth(c, cx, 350, expr, 22)
    return sticker(_pil(s))
def charles(expr='happy', S=400):
    s, c = _surf(S, int(S * 1.3)); k = S / 420; c.scale(k, k); c.translate(0, 20); cx = 210
    _bust(c, (0.75, 0.1, 0.15))
    c.new_path(); c.move_to(70, 450); c.curve_to(110, 400, 310, 400, 350, 450); c.line_to(350, 480); c.curve_to(300, 430, 120, 430, 70, 480); c.close_path(); fillstroke(c, (0.97, 0.96, 0.92), 4)
    for i in range(6): ell(c, 100 + i * 44, 455 - abs(i - 2.5) * 8, 4, 7); c.set_source_rgb(0.1, 0.1, 0.1); c.fill()
    c.new_path()   # big dark curly wig
    for i in range(12):
        a = math.pi * (-0.05 + i * 0.1); ell(c, cx + math.cos(a + math.pi) * 112, 290 + math.sin(a + math.pi) * -130 + (40 if i in (0, 11) else 0), 42, 46)
    c.set_source_rgb(0.16, 0.11, 0.08); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    for sx in (-1, 1):
        for j in range(3): ell(c, cx + sx * 138, 320 + j * 55, 38, 34); fillstroke(c, (0.16, 0.11, 0.08), 5)
    ell(c, cx, 275, 96, 116); fillstroke(c, SKIN)
    eyes(c, cx, 262, 38, expr); ell(c, cx, 298, 16, 14); fillstroke(c, SKIN_D, 4)
    c.new_path(); c.move_to(cx - 30, 322); c.curve_to(cx - 10, 314, cx + 10, 314, cx + 30, 322); c.set_source_rgb(0.16, 0.11, 0.08); c.set_line_width(6); c.stroke(); mouth(c, cx, 346, expr, 24)
    c.new_path(); c.move_to(cx - 70, 168); c.line_to(cx - 78, 95); c.line_to(cx - 38, 130); c.line_to(cx, 70); c.line_to(cx + 38, 130); c.line_to(cx + 78, 95); c.line_to(cx + 70, 168); c.close_path(); fillstroke(c, (0.98, 0.8, 0.25))
    for dx in (-38, 0, 38): ell(c, cx + dx, 150, 9, 9); c.set_source_rgb(0.85, 0.12, 0.2); c.fill()
    return sticker(_pil(s))
def officer(expr='smug', S=380):
    s, c = _surf(S, int(S * 1.3)); k = S / 420; c.scale(k, k); c.translate(0, 20); cx = 210
    _bust(c, (0.8, 0.12, 0.12))
    for i in range(4): ell(c, cx, 430 + i * 24, 7, 7); fillstroke(c, (0.98, 0.8, 0.25), 3)
    c.move_to(90, 470); c.line_to(330, 470); c.set_source_rgb(1, 1, 1); c.set_line_width(14); c.stroke()
    ell(c, cx, 275, 98, 116); fillstroke(c, SKIN); eyes(c, cx, 262, 38, expr); ell(c, cx, 298, 15, 13); fillstroke(c, SKIN_D, 4); mouth(c, cx, 340, expr, 24)
    c.new_path(); c.move_to(cx - 130, 175); c.curve_to(cx - 80, 70, cx + 80, 70, cx + 130, 175); c.curve_to(cx + 50, 140, cx - 50, 140, cx - 130, 175); c.close_path(); fillstroke(c, (0.1, 0.1, 0.12))
    c.move_to(cx - 125, 172); c.curve_to(cx - 50, 136, cx + 50, 136, cx + 125, 172); c.set_source_rgb(0.98, 0.8, 0.25); c.set_line_width(6); c.stroke()
    return sticker(_pil(s))
def ship(S=300, flag=(0.95, 0.5, 0.1)):
    s, c = _surf(S, int(S * 0.95)); k = S / 300; c.scale(k, k)
    c.new_path(); c.move_to(20, 190); c.line_to(280, 190); c.curve_to(262, 255, 50, 255, 20, 190); c.close_path(); fillstroke(c, (0.58, 0.36, 0.18))
    c.move_to(30, 205); c.line_to(270, 205); c.set_source_rgb(0.85, 0.7, 0.3); c.set_line_width(6); c.stroke()
    for mx, top in ((110, 30), (195, 50)):
        c.move_to(mx, top); c.line_to(mx, 192); c.set_source_rgb(*INK); c.set_line_width(7); c.stroke()
        for w_, y_ in ((70, top + 18), (90, top + 72)):
            c.new_path(); c.move_to(mx - w_ / 2, y_); c.curve_to(mx - w_ / 2 + 8, y_ + 34, mx + w_ / 2 - 8, y_ + 34, mx + w_ / 2, y_); c.line_to(mx + w_ / 2 - 4, y_ + 44); c.curve_to(mx, y_ + 54, mx, y_ + 54, mx - w_ / 2 + 4, y_ + 44); c.close_path(); fillstroke(c, (1, 0.98, 0.93), 4)
        c.rectangle(mx + 3, top - 2, 34, 20); fillstroke(c, flag, 3)
    return sticker(_pil(s), ow=6)
def nutmeg(S=150):
    s, c = _surf(S, S); k = S / 150; c.scale(k, k)
    ell(c, 75, 78, 55, 50); fillstroke(c, (0.55, 0.34, 0.2), 5)
    for a in (-30, -10, 10, 30): c.new_path(); c.move_to(75 + a, 32); c.curve_to(75 + a * 1.6, 70, 75 + a * 0.9, 100, 75 + a * 0.3, 126); c.set_source_rgb(0.85, 0.15, 0.12); c.set_line_width(6); c.stroke()
    ell(c, 55, 58, 12, 7); c.set_source_rgba(1, 1, 1, 0.35); c.fill()
    return sticker(_pil(s), ow=5)
def scroll(S=300, title='Treaty of Breda', year='1667'):
    s, c = _surf(S, int(S * 1.2)); k = S / 300; c.scale(k, k)
    c.rectangle(45, 40, 210, 280); fillstroke(c, (0.98, 0.93, 0.78), 5)
    for y in (40, 320): ell(c, 150, y, 120, 16); fillstroke(c, (0.9, 0.8, 0.6), 5)
    c.select_font_face('Serif', 0, 1); c.set_source_rgb(*INK); c.set_font_size(30)
    for i, line in enumerate(title.split(' ')): e = c.text_extents(line); c.move_to(150 - e.width / 2, 105 + i * 36); c.show_text(line)
    c.set_font_size(40); e = c.text_extents(year); c.move_to(150 - e.width / 2, 230); c.show_text(year)
    ell(c, 215, 285, 22, 22); fillstroke(c, (0.8, 0.12, 0.12), 4)
    return sticker(_pil(s))
def latte(S=260):
    s, c = _surf(S, int(S * 1.05)); k = S / 260; c.scale(k, k)
    c.new_path(); c.move_to(50, 80); c.line_to(210, 80); c.line_to(188, 250); c.line_to(72, 250); c.close_path(); fillstroke(c, (1, 1, 1))
    ell(c, 130, 80, 80, 16); fillstroke(c, (0.88, 0.72, 0.5), 5)
    for i in range(16): a = i * 2.4; ell(c, 130 + math.cos(a) * (8 + i * 4), 79 + math.sin(a) * (2 + i * 0.6), 3.5, 3.5); c.set_source_rgb(0.42, 0.24, 0.1); c.fill()
    c.new_path(); c.arc(214, 160, 30, -1.3, 1.3); c.set_source_rgb(*INK); c.set_line_width(14); c.stroke(); c.new_path(); c.arc(214, 160, 30, -1.3, 1.3); c.set_source_rgb(1, 1, 1); c.set_line_width(7); c.stroke()
    return sticker(_pil(s))
def whiteflag(S=220):
    s, c = _surf(S, int(S * 1.3)); k = S / 220; c.scale(k, k)
    c.move_to(40, 280); c.line_to(40, 20); c.set_source_rgb(0.5, 0.33, 0.18); c.set_line_width(10); c.stroke()
    c.new_path(); c.move_to(45, 25); c.curve_to(100, 5, 140, 45, 195, 25); c.line_to(195, 120); c.curve_to(140, 140, 100, 100, 45, 120); c.close_path(); fillstroke(c, (1, 1, 1), 5)
    return sticker(_pil(s))
if __name__ == '__main__':
    from PIL import Image
    items = [dutch('happy'), dutch('laugh'), stuyvesant('worried'), charles('happy'), officer('smug'), ship(), ship(flag=(0.85, 0.1, 0.15)), nutmeg(), scroll(), latte(), whiteflag()]
    out = Image.new('RGBA', (2600, 1400), (60, 110, 140, 255)); x = 20; y = 20; mh = 0
    for im in items:
        if x + im.width > 2600: x = 20; y += mh + 20; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 20; mh = max(mh, im.height)
    out.convert('RGB').resize((1300, 700)).save('/tmp/claude-0/fr/t3.png')
def local(kind='ru', expr='happy', S=380):
    """Bering Strait locals: 'ru' (fur ushanka, red parka), 'us' (cap, blue parka)."""
    s, c = _surf(S, int(S * 1.3)); k = S / 420; c.scale(k, k); c.translate(0, 20); cx = 210
    coat = (0.82, 0.18, 0.2) if kind == 'ru' else (0.2, 0.42, 0.85)
    _bust(c, coat)
    c.new_path(); c.move_to(120, 405); c.curve_to(150, 440, 270, 440, 300, 405); c.set_source_rgb(0.92, 0.9, 0.86); c.set_line_width(26); c.stroke()   # fur collar
    ell(c, cx, 275, 100, 116); fillstroke(c, SKIN)
    for sx in (-1, 1): ell(c, cx + sx * 48, 312, 18, 12); c.set_source_rgba(1, 0.4, 0.4, 0.45); c.fill()   # cold red cheeks
    eyes(c, cx, 262, 38, expr); ell(c, cx, 298, 16, 14); fillstroke(c, (0.98, 0.62, 0.55), 4); mouth(c, cx, 340, expr, 26)
    if kind == 'ru':
        c.new_path(); c.arc(cx, 220, 110, math.pi, 2 * math.pi); c.line_to(cx + 110, 205); c.line_to(cx - 110, 205); c.close_path(); fillstroke(c, (0.42, 0.28, 0.17))
        c.rectangle(cx - 118, 182, 236, 36); fillstroke(c, (0.55, 0.38, 0.24))
        for sx in (-1, 1): c.new_path(); c.move_to(cx + sx * 104, 215); c.curve_to(cx + sx * 132, 250, cx + sx * 128, 320, cx + sx * 98, 330); c.line_to(cx + sx * 92, 250); c.close_path(); fillstroke(c, (0.55, 0.38, 0.24))
        ell(c, cx, 198, 13, 13); fillstroke(c, (0.95, 0.78, 0.2), 3)
    else:
        c.new_path(); c.arc(cx, 215, 104, math.pi, 2 * math.pi); c.close_path(); fillstroke(c, (0.2, 0.42, 0.85))
        c.new_path(); c.move_to(cx - 20, 210); c.curve_to(cx + 60, 190, cx + 160, 200, cx + 170, 222); c.line_to(cx - 10, 224); c.close_path(); fillstroke(c, (0.15, 0.32, 0.7))
        ell(c, cx, 112, 10, 10); fillstroke(c, (0.15, 0.32, 0.7), 3)
    return sticker(_pil(s))
def calendar(word='TUESDAY', col=(0.85, 0.15, 0.2), S=260):
    s, c = _surf(S, int(S * 1.05)); k = S / 260; c.scale(k, k)
    c.rectangle(20, 40, 220, 220); fillstroke(c, (1, 1, 1)); c.rectangle(20, 40, 220, 64); fillstroke(c, col)
    for x in (70, 190): c.rectangle(x - 7, 22, 14, 36); fillstroke(c, (0.75, 0.75, 0.78), 3)
    c.select_font_face('Sans', 0, 1); c.set_font_size(30 if len(word) > 7 else 36); e = c.text_extents(word); c.set_source_rgb(1, 1, 1); c.move_to(130 - e.width / 2, 84); c.show_text(word)
    c.set_font_size(110); c.set_source_rgb(*INK); w2 = '?' ; e = c.text_extents(w2)
    return sticker(_pil(s))
