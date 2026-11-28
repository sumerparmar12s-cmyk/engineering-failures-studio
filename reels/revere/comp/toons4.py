"""Revolutionary-war cartoons (cairo, Point Roberts sticker style): colonial busts, rider on horse, church with lanterns, poem book, game chat box."""
import math, cairo
from toons import _surf, _pil, sticker, fillstroke, ell, eyes, mouth, SKIN, SKIN_D, INK
from toons3 import _bust
def colonial(kind='revere', expr='happy', S=380):
    coat = {'revere': (0.45, 0.28, 0.16), 'dawes': (0.42, 0.44, 0.5), 'prescott': (0.2, 0.35, 0.3)}[kind]
    s, c = _surf(S, int(S * 1.3)); k = S / 420; c.scale(k, k); c.translate(0, 20); cx = 210
    _bust(c, coat)
    c.new_path(); c.move_to(170, 396); c.line_to(cx, 452); c.line_to(250, 396); c.close_path(); fillstroke(c, (1, 1, 1), 4)   # cravat
    for i in range(3): ell(c, 165, 450 + i * 26, 6, 6); fillstroke(c, (0.85, 0.8, 0.7), 2)
    ell(c, cx, 275, 98, 116); fillstroke(c, SKIN)
    hair = {'revere': (0.38, 0.24, 0.14), 'dawes': (0.85, 0.85, 0.85), 'prescott': (0.25, 0.16, 0.1)}[kind]
    for sx in (-1, 1): ell(c, cx + sx * 92, 300, 22, 40); fillstroke(c, hair, 4)
    eyes(c, cx, 262, 38, expr); ell(c, cx, 298, 15, 13); fillstroke(c, SKIN_D, 4); mouth(c, cx, 340, expr, 26)
    c.new_path(); c.move_to(cx - 135, 180); c.curve_to(cx - 80, 70, cx + 80, 70, cx + 135, 180); c.curve_to(cx + 50, 145, cx - 50, 145, cx - 135, 180); c.close_path(); fillstroke(c, (0.12, 0.1, 0.1))   # tricorne
    return sticker(_pil(s))
def rider(coat=(0.45, 0.28, 0.16), horse=(0.5, 0.32, 0.18), S=330, lantern=False, red=False, phase=0.0):
    """side view, facing right; phase animates the legs (gallop)"""
    s, c = _surf(S, int(S * 0.95)); k = S / 330; c.scale(k, k)
    a = math.sin(phase) * 0.5
    for i, (x0, sgn) in enumerate(((95, 1), (115, -1), (215, -1), (235, 1))):   # legs
        ang = a * sgn; c.save(); c.translate(x0, 190); c.rotate(ang); c.rectangle(-8, 0, 16, 85); c.restore(); c.set_source_rgb(*[v * 0.8 for v in horse]); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    ell(c, 165, 175, 95, 48); fillstroke(c, horse)                                 # body
    c.new_path(); c.move_to(235, 160); c.line_to(275, 90); c.line_to(305, 100); c.line_to(270, 175); c.close_path(); fillstroke(c, horse)   # neck
    ell(c, 296, 92, 30, 18); fillstroke(c, horse)                                  # head
    c.new_path(); c.move_to(250, 95); c.curve_to(240, 120, 245, 150, 252, 165); c.set_source_rgb(0.15, 0.1, 0.08); c.set_line_width(10); c.stroke()   # mane
    c.new_path(); c.move_to(72, 165); c.curve_to(40, 175, 30, 215, 38, 240); c.set_source_rgb(0.15, 0.1, 0.08); c.set_line_width(12); c.stroke()   # tail
    ell(c, 305, 86, 4, 4); c.set_source_rgb(*INK); c.fill()
    # rider
    c.new_path(); c.move_to(140, 140); c.curve_to(135, 90, 150, 70, 175, 70); c.curve_to(200, 70, 210, 95, 205, 140); c.close_path(); fillstroke(c, coat if not red else (0.82, 0.12, 0.12))
    ell(c, 178, 52, 26, 28); fillstroke(c, SKIN, 4)
    c.new_path(); c.move_to(140, 40); c.curve_to(160, 12, 200, 12, 218, 40); c.curve_to(190, 30, 168, 30, 140, 40); c.close_path(); fillstroke(c, (0.12, 0.1, 0.1), 4)
    c.move_to(200, 100); c.line_to(250, 105); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()   # reins arm
    if lantern:
        c.move_to(150, 95); c.line_to(120, 70); c.stroke(); c.rectangle(105, 55, 22, 28); fillstroke(c, (1, 0.85, 0.3), 3)
    return sticker(_pil(s), ow=5)
def church(S=360, lit=2):
    s, c = _surf(S, int(S * 1.6)); k = S / 360; c.scale(k, k)
    c.new_path(); c.move_to(180, 10); c.line_to(220, 170); c.line_to(140, 170); c.close_path(); fillstroke(c, (0.95, 0.95, 0.93))   # spire
    c.rectangle(120, 170, 120, 130); fillstroke(c, (0.9, 0.9, 0.88)); c.rectangle(100, 300, 160, 260); fillstroke(c, (0.7, 0.33, 0.25))   # tower (brick)
    for i in range(lit):
        x = 150 + i * 40; ell(c, x, 230, 14, 20); c.set_source_rgba(1, 0.85, 0.3, 0.35); c.fill(); c.rectangle(x - 10, 215, 20, 30); fillstroke(c, (1, 0.82, 0.25), 3)
    c.rectangle(155, 470, 50, 90); fillstroke(c, (0.35, 0.2, 0.12), 4)
    return sticker(_pil(s))
def book(S=340):
    s, c = _surf(S, int(S * 0.85)); k = S / 340; c.scale(k, k)
    c.new_path(); c.move_to(20, 40); c.curve_to(90, 20, 150, 30, 170, 50); c.line_to(170, 270); c.curve_to(150, 250, 90, 240, 20, 260); c.close_path(); fillstroke(c, (0.99, 0.96, 0.88))
    c.new_path(); c.move_to(320, 40); c.curve_to(250, 20, 190, 30, 170, 50); c.line_to(170, 270); c.curve_to(190, 250, 250, 240, 320, 260); c.close_path(); fillstroke(c, (0.99, 0.96, 0.88))
    c.select_font_face('Serif', 1, 1); c.set_source_rgb(*INK); c.set_font_size(19)
    for i, l in enumerate(["Listen, my", "children, and", "you shall hear", "of the midnight", "ride of..."]): c.move_to(34, 78 + i * 30); c.show_text(l)
    c.set_font_size(19); c.select_font_face('Serif', 0, 1)
    for i, (n, x) in enumerate((('Paul Revere', False), ('W. Dawes', True), ('S. Prescott', True))):
        y = 95 + i * 55; c.move_to(182, y); c.set_source_rgb(*INK); c.show_text(n)
        if x: c.move_to(178, y - 7); c.line_to(300, y - 7); c.set_source_rgb(0.85, 0.12, 0.15); c.set_line_width(5); c.stroke()
    return sticker(_pil(s))
def chat(lines, S=760, upto=99):
    """strategy-game style chat panel: list of (name, color, text)"""
    h = 90 + 62 * len(lines); s, c = _surf(S, h)
    c.rectangle(0, 0, S, h); c.set_source_rgba(0.08, 0.08, 0.1, 0.88); c.fill(); c.rectangle(0, 0, S, 52); c.set_source_rgba(0.25, 0.2, 0.12, 0.95); c.fill()
    c.select_font_face('Sans', 0, 1); c.set_font_size(26); c.set_source_rgb(0.95, 0.85, 0.55); c.move_to(20, 36); c.show_text('ALL CHAT')
    c.set_font_size(30)
    for i, (n, col, tx) in enumerate(lines[:upto]):
        y = 100 + i * 62; c.set_source_rgb(*col); c.move_to(22, y); c.show_text(n + ':'); w = c.text_extents(n + ': ').x_advance
        c.set_source_rgb(0.95, 0.95, 0.95); c.select_font_face('Sans', 0, 0); c.move_to(22 + w, y); c.show_text(tx); c.select_font_face('Sans', 0, 1)
    c.rectangle(1, 1, S - 2, h - 2); c.set_source_rgb(0.6, 0.5, 0.3); c.set_line_width(3); c.stroke()
    return _pil(s)
if __name__ == '__main__':
    from PIL import Image
    from toons3 import officer
    items = [colonial('revere'), colonial('dawes', 'worried'), colonial('prescott', 'smug'), officer('smug', 380), rider(), rider((0.42, 0.44, 0.5), (0.85, 0.82, 0.78), phase=1.5), rider(red=True, horse=(0.2, 0.15, 0.12)), church(), book(),
             chat([('Redcoat_77', (0.95, 0.3, 0.3), 'shh its a secret'), ('Boston', (0.4, 0.7, 1), 'we know lol')])]
    out = Image.new('RGBA', (2600, 1500), (60, 110, 140, 255)); x = 20; y = 20; mh = 0
    for im in items:
        if x + im.width > 2600: x = 20; y += mh + 20; mh = 0
        out.alpha_composite(im, (x, y)); x += im.width + 20; mh = max(mh, im.height)
    out.convert('RGB').resize((1300, 750)).save('/tmp/claude-0/fr/t4.png')
