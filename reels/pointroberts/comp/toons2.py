"""Extra self-drawn characters/props for the Point Roberts reel (cairo)."""
import math, cairo
from toons import _surf, _pil, sticker, fillstroke, ell, eyes, mouth, SKIN, SKIN_D, INK
def victoria(expr='neutral', S=420):
    """Queen Victoria caricature: small crown, white lace veil, black dress, very unamused."""
    s, c = _surf(S, int(S * 1.25)); k = S / 420; c.scale(k, k); cx = 210
    c.move_to(55, 525); c.curve_to(65, 420, 140, 392, 210, 392); c.curve_to(280, 392, 355, 420, 365, 525); c.close_path(); fillstroke(c, (0.12, 0.12, 0.14))
    c.move_to(150, 400); c.line_to(cx, 455); c.line_to(270, 400); c.set_source_rgb(0.2, 0.35, 0.8); c.set_line_width(12); c.stroke()   # blue sash
    ell(c, 300, 440, 16, 16); fillstroke(c, (0.98, 0.8, 0.25), 4)
    # veil behind head
    c.new_path(); c.move_to(80, 200); c.curve_to(60, 330, 80, 400, 120, 420); c.line_to(300, 420); c.curve_to(340, 400, 360, 330, 340, 200); c.close_path(); fillstroke(c, (0.97, 0.97, 0.97), 5)
    ell(c, cx, 270, 104, 120); fillstroke(c, SKIN)
    # dark hair parted in the middle
    c.new_path(); c.move_to(108, 250); c.curve_to(110, 160, 200, 150, cx, 175); c.curve_to(220, 150, 310, 160, 312, 250); c.curve_to(290, 200, 240, 190, cx, 200); c.curve_to(180, 190, 130, 200, 108, 250); c.close_path(); fillstroke(c, (0.3, 0.2, 0.14), 5)
    for sx in (-1, 1): ell(c, cx + sx * 50, 300, 16, 11); c.set_source_rgba(1, 0.55, 0.55, 0.5); c.fill()
    eyes(c, cx, 262, 40, expr); mouth(c, cx, 330, expr, 26)
    ell(c, cx, 292, 13, 11); fillstroke(c, SKIN_D, 4)
    # small crown
    c.new_path(); c.move_to(165, 150); c.line_to(175, 105); c.line_to(193, 135); c.line_to(cx, 95); c.line_to(227, 135); c.line_to(245, 105); c.line_to(255, 150); c.close_path(); fillstroke(c, (0.98, 0.8, 0.25), 5)
    for x in (180, cx, 240): ell(c, x, 140, 6, 6); c.set_source_rgb(0.9, 0.2, 0.3); c.fill()
    return sticker(_pil(s))
def polk(expr='smug', S=420):
    """President James K. Polk caricature: long grey hair swept back behind the ears, stern brows, black coat, white cravat."""
    s, c = _surf(S, int(S * 1.25)); k = S / 420; c.scale(k, k); cx = 210
    c.move_to(55, 525); c.curve_to(65, 420, 140, 392, 210, 392); c.curve_to(280, 392, 355, 420, 365, 525); c.close_path(); fillstroke(c, (0.1, 0.1, 0.13))
    c.move_to(170, 396); c.line_to(cx, 450); c.line_to(250, 396); c.close_path(); fillstroke(c, (1, 1, 1), 5)
    c.new_path(); c.move_to(90, 250); c.curve_to(70, 330, 95, 380, 140, 370); c.line_to(280, 370); c.curve_to(325, 380, 350, 330, 330, 250); c.close_path(); fillstroke(c, (0.62, 0.62, 0.66), 5)   # long hair behind
    ell(c, cx, 268, 100, 122); fillstroke(c, SKIN)
    c.new_path(); c.move_to(112, 230); c.curve_to(120, 140, 300, 140, 308, 230); c.curve_to(270, 175, 150, 175, 112, 230); c.close_path(); fillstroke(c, (0.62, 0.62, 0.66), 5)
    eyes(c, cx, 255, 38, expr)
    c.new_path(); c.move_to(cx - 4, 262); c.curve_to(cx + 26, 300, cx + 14, 318, cx - 8, 314); fillstroke(c, SKIN_D, 5)
    mouth(c, cx, 345, expr, 28)
    c.move_to(cx - 40, 375); c.curve_to(cx - 20, 368, cx + 20, 368, cx + 40, 375); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()   # jaw line
    return sticker(_pil(s))
def _rr(c, x, y, w, h, r):
    c.new_path(); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.arc(x + w - r, y + r, r, 1.5 * math.pi, 0); c.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi); c.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi); c.close_path()
def bus(S=240):
    s, c = _surf(S, int(S * 0.62)); k = S / 240; c.scale(k, k)
    _rr(c, 10, 20, 220, 95, 16); fillstroke(c, (1.0, 0.78, 0.1), 5)
    for i in range(4): _rr(c, 24 + i * 46, 34, 36, 32, 5); fillstroke(c, (0.75, 0.9, 1.0), 3)
    c.move_to(14, 82); c.line_to(226, 82); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    for x in (55, 185): ell(c, x, 118, 18, 18); fillstroke(c, (0.15, 0.15, 0.17), 4); ell(c, x, 118, 7, 7); c.set_source_rgb(0.7, 0.7, 0.7); c.fill()
    c.select_font_face('Sans', 0, 1); c.set_font_size(15); c.set_source_rgb(*INK); c.move_to(70, 104); c.show_text('SCHOOL BUS')
    return sticker(_pil(s), ow=4)
def car(col=(0.85, 0.15, 0.2), S=170, leaf=True):
    s, c = _surf(S, int(S * 0.75)); k = S / 170; c.scale(k, k)
    c.new_path(); c.move_to(15, 85); c.line_to(20, 60); c.line_to(50, 55); c.line_to(70, 28); c.line_to(120, 28); c.line_to(140, 55); c.line_to(158, 62); c.line_to(158, 85); c.close_path(); fillstroke(c, col, 5)
    c.new_path(); c.move_to(76, 34); c.line_to(95, 34); c.line_to(95, 55); c.line_to(60, 55); c.close_path(); fillstroke(c, (0.75, 0.9, 1.0), 3)
    c.new_path(); c.move_to(102, 34); c.line_to(116, 34); c.line_to(132, 55); c.line_to(102, 55); c.close_path(); fillstroke(c, (0.75, 0.9, 1.0), 3)
    for x in (48, 128): ell(c, x, 88, 15, 15); fillstroke(c, (0.15, 0.15, 0.17), 4)
    if leaf:   # tiny maple-leaf flag on the roof
        c.move_to(95, 28); c.line_to(95, 6); c.set_source_rgb(*INK); c.set_line_width(3); c.stroke()
        c.rectangle(95, 4, 34, 20); fillstroke(c, (1, 1, 1), 2); c.rectangle(95, 4, 8, 20); c.set_source_rgb(0.85, 0.1, 0.15); c.fill(); c.rectangle(121, 4, 8, 20); c.fill()
        c.move_to(112, 8); c.line_to(116, 15); c.line_to(112, 20); c.line_to(108, 15); c.close_path(); c.fill()
    return sticker(_pil(s), ow=4)
def gaspump(S=180):
    s, c = _surf(S, int(S * 1.3)); k = S / 180; c.scale(k, k)
    _rr(c, 30, 30, 100, 190, 14); fillstroke(c, (0.2, 0.65, 0.35), 5); _rr(c, 45, 48, 70, 50, 6); fillstroke(c, (0.9, 1, 0.9), 3)
    c.select_font_face('Sans', 0, 1); c.set_font_size(30); c.set_source_rgb(*INK); c.move_to(56, 84); c.show_text('$$')
    c.move_to(130, 80); c.curve_to(165, 80, 160, 160, 150, 170); c.set_source_rgb(*INK); c.set_line_width(8); c.stroke(); c.rectangle(140, 165, 20, 34); fillstroke(c, (0.25, 0.25, 0.28), 4)
    return sticker(_pil(s), ow=5)
def package(S=140):
    s, c = _surf(S, S); k = S / 140; c.scale(k, k)
    c.rectangle(15, 30, 110, 90); fillstroke(c, (0.78, 0.6, 0.38), 5); c.move_to(70, 30); c.line_to(70, 120); c.set_source_rgb(0.95, 0.85, 0.6); c.set_line_width(12); c.stroke()
    return sticker(_pil(s), ow=4)
def passport(S=220, cross=False):
    s, c = _surf(S, int(S * 1.3)); k = S / 220; c.scale(k, k)
    _rr(c, 30, 20, 160, 230, 14); fillstroke(c, (0.12, 0.2, 0.45), 6)
    ell(c, 110, 120, 38, 38); c.set_source_rgb(0.95, 0.8, 0.3); c.set_line_width(5); c.stroke()
    c.select_font_face('Sans', 0, 1); c.set_font_size(24); c.set_source_rgb(0.95, 0.8, 0.3); c.move_to(54, 205); c.show_text('PASSPORT')
    if cross:
        c.move_to(20, 30); c.line_to(200, 250); c.move_to(200, 30); c.line_to(20, 250); c.set_source_rgb(0.9, 0.12, 0.15); c.set_line_width(20); c.stroke()
    return sticker(_pil(s))
def pin(col=(0.2, 0.45, 0.9), S=60):
    s, c = _surf(S, int(S * 1.4)); k = S / 60; c.scale(k, k)
    ell(c, 30, 22, 14, 14); fillstroke(c, (1, 0.84, 0.69), 3); c.move_to(10, 78); c.curve_to(10, 40, 50, 40, 50, 78); c.close_path(); fillstroke(c, col, 3)
    return _pil(s)
def palm(S=300):
    s, c = _surf(S, int(S * 1.1)); k = S / 300; c.scale(k, k); c.translate(22, 0)
    c.move_to(130, 300); c.curve_to(120, 220, 140, 150, 128, 90); c.set_source_rgb(0.55, 0.38, 0.2); c.set_line_width(18); c.stroke()
    for a in (-150, -110, -70, -30, 10):
        r = math.radians(a); c.new_path(); c.move_to(128, 90); c.curve_to(128 + 60 * math.cos(r), 90 + 40 * math.sin(r) - 30, 128 + 110 * math.cos(r), 90 + 80 * math.sin(r), 128 + 120 * math.cos(r), 90 + 100 * math.sin(r) + 20)
        c.set_source_rgb(0.2, 0.62, 0.25); c.set_line_width(22); c.stroke()
    ell(c, 130, 300, 90, 16); c.set_source_rgb(0.93, 0.85, 0.6); c.fill()
    return sticker(_pil(s), ow=6)
if __name__ == '__main__':
    from PIL import Image
    items = [victoria('neutral'), victoria('worried'), polk('smug'), polk('laugh'), bus(), car(), car((0.2, 0.45, 0.9), leaf=False), gaspump(), package(), passport(cross=True), palm()]
    out = Image.new('RGBA', (2600, 1200), (60, 110, 140, 255)); x = 20; y = 20; mh = 0
    for im in items:
        if x + im.width > 2600: x = 20; y += mh + 20; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 20; mh = max(mh, im.height)
    out.convert('RGB').resize((1300, 600)).save('/tmp/claude-0/fr/toons2.png')
