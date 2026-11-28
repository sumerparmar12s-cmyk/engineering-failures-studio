"""National flags drawn with cairo (W x H surface, 3:2 unless noted). Simplified but faithful designs."""
import math, cairo
def _star(c, cx, cy, r, rot=-math.pi / 2, inner=0.382):
    c.new_path()
    for i in range(10):
        rr = r if i % 2 == 0 else r * inner; a = rot + i * math.pi / 5; c.line_to(cx + rr * math.cos(a), cy + rr * math.sin(a))
    c.close_path()
def usa(c, w, h):
    for i in range(13): c.rectangle(0, i * h / 13, w, h / 13 + 0.5); c.set_source_rgb(*((0.70, 0.13, 0.20) if i % 2 == 0 else (1, 1, 1))); c.fill()
    cw, ch = w * 0.4, h * 7 / 13; c.rectangle(0, 0, cw, ch); c.set_source_rgb(0.24, 0.23, 0.43); c.fill()
    c.set_source_rgb(1, 1, 1)
    for r in range(9):
        n = 6 if r % 2 == 0 else 5
        for k in range(n): _star(c, cw * ((k * 2 + (1 if r % 2 == 0 else 2)) / 12), ch * ((r + 1) / 10), ch * 0.035); c.fill()
def uk(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(0.0, 0.14, 0.49); c.fill()
    for lw, col in ((h * 0.2, (1, 1, 1)), (h * 0.07, (0.78, 0.06, 0.18))):
        c.move_to(0, 0); c.line_to(w, h); c.move_to(w, 0); c.line_to(0, h); c.set_source_rgb(*col); c.set_line_width(lw); c.stroke()
    for lw, col in ((h * 0.34, (1, 1, 1)), (h * 0.2, (0.78, 0.06, 0.18))):
        c.move_to(w / 2, 0); c.line_to(w / 2, h); c.move_to(0, h / 2); c.line_to(w, h / 2); c.set_source_rgb(*col); c.set_line_width(lw); c.stroke()
def canada(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(1, 1, 1); c.fill()
    c.rectangle(0, 0, w / 4, h); c.rectangle(w * 3 / 4, 0, w / 4, h); c.set_source_rgb(0.85, 0.12, 0.13); c.fill()
    s = h * 0.42; cx, cy = w / 2, h / 2
    P = [(0, -1), (0.15, -0.65), (0.35, -0.75), (0.28, -0.25), (0.6, -0.5), (0.55, -0.32), (0.9, -0.38), (0.75, -0.08), (0.95, 0.05), (0.45, 0.4), (0.5, 0.6), (0.05, 0.5), (0.05, 0.95), (-0.05, 0.95), (-0.05, 0.5), (-0.5, 0.6), (-0.45, 0.4), (-0.95, 0.05), (-0.75, -0.08), (-0.9, -0.38), (-0.55, -0.32), (-0.6, -0.5), (-0.28, -0.25), (-0.35, -0.75), (-0.15, -0.65)]
    c.new_path(); [c.line_to(cx + x * s, cy + y * s) for x, y in P]; c.close_path(); c.fill()
def new_zealand(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(0.0, 0.14, 0.49); c.fill()
    c.save(); c.rectangle(0, 0, w / 2, h / 2); c.clip(); c.scale(0.5, 0.5); uk(c, w, h); c.restore()
    for (x, y, r) in ((0.75, 0.25, 0.06), (0.67, 0.5, 0.06), (0.83, 0.45, 0.05), (0.75, 0.78, 0.07)):
        _star(c, w * x, h * y, h * r * 1.25); c.set_source_rgb(1, 1, 1); c.fill(); _star(c, w * x, h * y, h * r); c.set_source_rgb(0.8, 0.08, 0.18); c.fill()
def norway(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(0.73, 0.05, 0.18); c.fill()
    for lw, col in ((h * 0.25, (1, 1, 1)), (h * 0.125, (0.0, 0.13, 0.36))):
        c.move_to(w * 0.375, 0); c.line_to(w * 0.375, h); c.move_to(0, h / 2); c.line_to(w, h / 2); c.set_source_rgb(*col); c.set_line_width(lw); c.stroke()
def south_korea(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(1, 1, 1); c.fill()
    cx, cy, r = w / 2, h / 2, h * 0.25
    c.new_path(); c.arc(cx, cy, r, math.pi, 2 * math.pi); c.arc(cx + r / 2, cy, r / 2, math.pi, 0, ) if False else None
    c.new_path(); c.arc(cx, cy, r, 0, 2 * math.pi); c.set_source_rgb(0.0, 0.2, 0.55); c.fill()     # blue (bottom)
    c.save(); c.translate(cx, cy); c.rotate(math.radians(33.7))
    c.new_path(); c.arc(0, 0, r, math.pi, 2 * math.pi); c.arc_negative(r / 2, 0, r / 2, 0, math.pi); c.arc(-r / 2, 0, r / 2, 0, math.pi); c.close_path(); c.set_source_rgb(0.8, 0.0, 0.18); c.fill()
    c.restore()
    for ang, pat in ((-33.7 - 90, (1, 1, 1)), (33.7 - 90, (1, 0, 1)), (33.7 + 90, (0, 1, 0)), (-33.7 + 90, (0, 0, 0))):
        c.save(); c.translate(cx, cy); c.rotate(math.radians(ang + 90)); c.translate(0, -r * 1.75)
        for i, solid in enumerate(pat):
            y = (i - 1) * r * 0.2
            if solid: c.rectangle(-r * 0.5, y - r * 0.06, r, r * 0.12)
            else: c.rectangle(-r * 0.5, y - r * 0.06, r * 0.45, r * 0.12); c.rectangle(r * 0.05, y - r * 0.06, r * 0.45, r * 0.12)
        c.set_source_rgb(0, 0, 0); c.fill(); c.restore()
def north_korea(c, w, h):
    for y0, hh, col in ((0, h / 6, (0.01, 0.31, 0.64)), (h / 6, h / 24, (1, 1, 1)), (h * 5 / 24, h * 14 / 24, (0.93, 0.11, 0.14)), (h * 19 / 24, h / 24, (1, 1, 1)), (h * 20 / 24, h / 6, (0.01, 0.31, 0.64))):
        c.rectangle(0, y0, w, hh + 0.5); c.set_source_rgb(*col); c.fill()
    c.arc(w * 0.36, h / 2, h * 0.22, 0, 2 * math.pi); c.set_source_rgb(1, 1, 1); c.fill(); _star(c, w * 0.36, h / 2, h * 0.21); c.set_source_rgb(0.93, 0.11, 0.14); c.fill()
def ussr(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(0.8, 0.0, 0.0); c.fill()
    c.set_source_rgb(1, 0.85, 0.0); _star(c, w * 0.16, h * 0.14, h * 0.07); c.set_line_width(h * 0.015); c.stroke()
    c.new_path(); c.arc(w * 0.15, h * 0.33, h * 0.11, math.radians(200), math.radians(60)); c.set_line_width(h * 0.035); c.stroke()   # sickle
    c.move_to(w * 0.08, h * 0.44); c.line_to(w * 0.22, h * 0.24); c.stroke(); c.move_to(w * 0.19, h * 0.22); c.line_to(w * 0.25, h * 0.27); c.set_line_width(h * 0.05); c.stroke()   # hammer
def china(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(0.93, 0.11, 0.14); c.fill(); c.set_source_rgb(1, 1, 0)
    _star(c, w * 5 / 30, h * 5 / 20, h * 3 / 20); c.fill()
    for x, y in ((10, 2), (12, 4), (12, 7), (10, 9)):
        a = math.atan2(5 - y, 5 - x); _star(c, w * x / 30, h * y / 20, h / 20, rot=a + math.pi); c.fill()
def un(c, w, h):
    c.rectangle(0, 0, w, h); c.set_source_rgb(0.27, 0.6, 0.86); c.fill()
    c.set_source_rgb(1, 1, 1); cx, cy, r = w / 2, h * 0.47, h * 0.28; c.set_line_width(h * 0.018)
    for k in range(1, 5): c.new_path(); c.arc(cx, cy, r * k / 4, 0, 2 * math.pi); c.stroke()
    for a in range(8): c.move_to(cx, cy); c.line_to(cx + r * math.cos(a * math.pi / 4), cy + r * math.sin(a * math.pi / 4)); c.stroke()
    c.set_line_width(h * 0.045)
    c.new_path(); c.arc(cx, cy, r * 1.3, math.pi * 0.55, math.pi * 1.25); c.stroke(); c.new_path(); c.arc_negative(cx, cy, r * 1.3, math.pi * 0.45, -math.pi * 0.25); c.stroke()
FLAGS = {'United States of America': usa, 'United Kingdom': uk, 'Canada': canada, 'New Zealand': new_zealand, 'Norway': norway, 'South Korea': south_korea, 'North Korea': north_korea,
         'USSR': ussr, 'China': china, 'UN': un}
def flag_surface(name, w=900, h=600):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); FLAGS[name](c, w, h); return s
if __name__ == '__main__':
    from PIL import Image
    import numpy as np
    out = Image.new('RGB', (1500, 900), (40, 40, 40))
    for i, n in enumerate(FLAGS):
        s = flag_surface(n, 270, 180); a = np.frombuffer(s.get_data(), np.uint8).reshape(180, 270, 4)[..., [2, 1, 0]]
        out.paste(Image.fromarray(a.copy()), (20 + (i % 5) * 295, 20 + (i // 5) * 220))
    out.save('/tmp/claude-0/fr/flags.png')
