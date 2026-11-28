"""Overlay effects for the AMOC reel: glowing flowing currents, text along paths, conveyor belt, thermometers, weather icons, exploding cartoon Earth."""
import math, cairo, numpy as np
from PIL import Image, ImageFilter, ImageDraw
from toons import _pil, sticker, INK
import earth as E
W, H = 1080, 1920
def slerp_path(pts, n=24):
    out = []
    for (a, b) in zip(pts, pts[1:]):
        A, B = E.unit(*a), E.unit(*b); om = math.acos(max(-1, min(1, float(A @ B)))) or 1e-6
        for k in range(n):
            t = k / n; v = (math.sin((1 - t) * om) * A + math.sin(t * om) * B) / math.sin(om)
            out.append((math.degrees(math.atan2(v[1], v[0])), math.degrees(math.asin(max(-1, min(1, v[2]))))))
    out.append(pts[-1]); return out
def proj_path(cam, pts):
    lo = np.array([p[0] for p in pts]); la = np.array([p[1] for p in pts]); x, y, ok = cam.project(lo, la, W, H); return x, y, ok
def cut(x, y, frac):
    seg = np.hypot(np.diff(x), np.diff(y)); L = np.concatenate([[0], np.cumsum(seg)]); tg = L[-1] * max(0, min(1, frac))
    i = int(np.searchsorted(L, tg)); i = max(1, min(i, len(x) - 1))
    k = (tg - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); xe, ye = x[i - 1] + (x[i] - x[i - 1]) * k, y[i - 1] + (y[i] - y[i - 1]) * k
    return np.append(x[:i], xe), np.append(y[:i], ye), L
def stream(glow, crisp, cam, pts, t, frac=1.0, col=(1.0, 0.35, 0.3), width=34, speed=1.0, alpha=1.0, dash=True):
    """glowing ribbon (into `glow` ctx, blurred later) + flowing streak lines (into `crisp` ctx)."""
    x, y, ok = proj_path(cam, pts)
    if not ok.any() or frac <= 0 or alpha <= 0.01: return
    x, y, L = cut(x, y, frac)
    def path(c):
        c.new_path(); c.move_to(x[0], y[0]); [c.line_to(a, b) for a, b in zip(x[1:], y[1:])]
    glow.set_line_cap(cairo.LINE_CAP_ROUND); glow.set_line_join(cairo.LINE_JOIN_ROUND)
    path(glow); glow.set_source_rgba(*col, 0.45 * alpha); glow.set_line_width(width * 2.6); glow.stroke()
    path(glow); glow.set_source_rgba(*col, 0.8 * alpha); glow.set_line_width(width * 1.2); glow.stroke()
    crisp.set_line_cap(cairo.LINE_CAP_ROUND)
    if dash:
        for off, w_, a_ in ((0, 4, 0.95), (17, 3, 0.7)):
            for dy in (-width * 0.22, width * 0.22):
                c = crisp; c.save(); c.translate(0, dy * 0.0); path(c); c.restore()
                c.set_dash([26, 30], -(t * 160 * speed + off)); c.set_source_rgba(1, 1, 1, a_ * alpha); c.set_line_width(w_); c.stroke(); c.set_dash([])
def text_along(c, cam, pts, txt, start_frac=0.35, size=40, col=(1, 1, 1), alpha=1.0):
    x, y, ok = proj_path(cam, pts)
    if not ok.all() or alpha <= 0.01: return
    seg = np.hypot(np.diff(x), np.diff(y)); L = np.concatenate([[0], np.cumsum(seg)])
    c.select_font_face('Sans', cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD); c.set_font_size(size)
    s = L[-1] * start_frac
    for ch in txt:
        adv = c.text_extents(ch).x_advance; m = s + adv / 2
        if m > L[-1]: break
        i = max(1, min(int(np.searchsorted(L, m)), len(x) - 1)); k = (m - L[i - 1]) / max(1e-6, L[i] - L[i - 1])
        px, py = x[i - 1] + (x[i] - x[i - 1]) * k, y[i - 1] + (y[i] - y[i - 1]) * k; ang = math.atan2(y[i] - y[i - 1], x[i] - x[i - 1])
        if abs(ang) > math.pi / 2: ang += math.pi
        c.save(); c.translate(px, py); c.rotate(ang); c.move_to(-adv / 2, size * 0.35); c.text_path(ch)
        c.set_source_rgba(0, 0, 0, 0.45 * alpha); c.set_line_width(5); c.stroke_preserve(); c.set_source_rgba(*col, alpha); c.fill(); c.restore()
        s += adv
def vortex(c, x, y, t, r=70, col=(0.55, 0.85, 1.0), strength=1.0):
    for k in range(3):
        a0 = t * 4 * strength + k * 2.1
        c.new_path()
        for i in range(60):
            u = i / 59; ang = a0 + u * 4.5; rr = r * (1 - u * 0.85)
            (c.move_to if i == 0 else c.line_to)(x + rr * math.cos(ang), y + rr * 0.45 * math.sin(ang))
        c.set_source_rgba(*col, 0.85 * strength); c.set_line_width(5 - k); c.stroke()
    c.new_path(); c.arc(x, y, 6, 0, 2 * math.pi); c.set_source_rgba(*col, strength); c.fill()
def blob(glow, cam, lon, lat, rad_deg, col, alpha):
    pts = [(lon + rad_deg * 1.4 * math.cos(a) / max(0.2, math.cos(math.radians(lat))) * 0.7, lat + rad_deg * 0.7 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    x, y, ok = proj_path(cam, pts)
    if not ok.any(): return
    glow.new_path(); [(glow.move_to if i == 0 else glow.line_to)(a, b) for i, (a, b) in enumerate(zip(x, y))]; glow.close_path(); glow.set_source_rgba(*col, alpha); glow.fill()
def apply_glow(img, glow_surf, blur=14):
    g = _pil(glow_surf).filter(ImageFilter.GaussianBlur(blur)); img.alpha_composite(g); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur * 2)))
# ---------------- icons ----------------
def _surf(w, h): s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND); return s, c
def lin(c, x0, y0, x1, y1, col, ks=(1.25, 1.0, 0.6)):
    g = cairo.LinearGradient(x0, y0, x1, y1)
    for i, k in enumerate(ks): g.add_color_stop_rgb(i / (len(ks) - 1), *(min(1, v * k) for v in col))
    return g
def conveyor(angle=0.0, S=460, warn=False):
    s, c = _surf(S, int(S * 0.62)); k = S / 460; c.scale(k, k)
    # frame legs
    for x in (90, 370): c.move_to(x, 170); c.line_to(x - 25, 270); c.move_to(x, 170); c.line_to(x + 25, 270); c.set_source_rgb(0.3, 0.32, 0.36); c.set_line_width(12); c.stroke()
    # belt
    c.new_path(); c.arc(80, 130, 52, math.pi / 2, 3 * math.pi / 2); c.arc(380, 130, 52, -math.pi / 2, math.pi / 2); c.close_path()
    c.set_source(lin(c, 0, 78, 0, 182, (0.2, 0.22, 0.26), (1.4, 0.9, 0.6))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(5); c.stroke()
    for i in range(14):   # belt cleats moving
        u = ((i / 14) + angle / (2 * math.pi) * 0.25) % 1.0; x = 80 + u * 300
        c.move_to(x, 80); c.line_to(x, 92); c.set_source_rgb(0.75, 0.78, 0.82); c.set_line_width(5); c.stroke()
    for cx in (80, 380, 230):
        c.save(); c.translate(cx, 130); c.rotate(angle)
        c.arc(0, 0, 40 if cx != 230 else 26, 0, 2 * math.pi); c.set_source(cairo.RadialGradient(-10, -12, 4, 0, 0, 42)); c.get_source().add_color_stop_rgb(0, 0.85, 0.87, 0.9); c.get_source().add_color_stop_rgb(1, 0.35, 0.38, 0.42); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
        for a in range(4): c.move_to(0, 0); c.line_to(math.cos(a * math.pi / 2) * 30, math.sin(a * math.pi / 2) * 30); c.set_source_rgb(0.25, 0.27, 0.3); c.set_line_width(5); c.stroke()
        c.restore()
    # warm water "boxes" riding on top (red/orange droplets)
    for i in range(4):
        u = ((i / 4) + angle / (2 * math.pi) * 0.25) % 1.0; x = 100 + u * 260
        c.new_path(); c.move_to(x, 30); c.curve_to(x + 20, 55, x + 22, 75, x, 78); c.curve_to(x - 22, 75, x - 20, 55, x, 30); c.set_source(lin(c, x - 20, 0, x + 20, 0, (1, 0.45, 0.3))); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(3); c.stroke()
    if warn:
        c.new_path(); c.move_to(420, 10); c.line_to(455, 70); c.line_to(385, 70); c.close_path(); c.set_source_rgb(1, 0.8, 0.1); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
        c.move_to(420, 30); c.line_to(420, 52); c.set_line_width(6); c.stroke(); c.arc(420, 61, 3.5, 0, 6.3); c.fill()
    return sticker(_pil(s), ow=5)
def thermo(value, hot=True, S=120, fill=1.0):
    s, c = _surf(S * 3, int(S * 1.9)); k = S / 120; c.scale(k, k)
    c.new_path(); c.arc(40, 175, 26, 0, 2 * math.pi); c.rectangle(28, 25, 24, 150); c.set_source_rgb(1, 1, 1); c.fill()
    col = (0.95, 0.25, 0.2) if hot else (0.2, 0.55, 0.95)
    c.arc(40, 175, 19, 0, 2 * math.pi); c.set_source_rgb(*col); c.fill(); h = 130 * fill; c.rectangle(34, 170 - h, 12, h); c.fill()
    c.new_path(); c.arc(40, 175, 26, 0.5, 2 * math.pi - 0.5 + 0.0); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    c.select_font_face('Sans', 0, 1); c.set_font_size(52); c.set_source_rgb(1, 1, 1); c.move_to(80, 120); c.text_path(value); c.set_source_rgba(0, 0, 0, 0.6); c.set_line_width(7); c.stroke_preserve(); c.set_source_rgb(1, 1, 1); c.fill()
    return _pil(s)
def cloud(kind='rain', S=220, t=0.0):
    s, c = _surf(S, int(S * 1.2)); k = S / 220; c.scale(k, k)
    for x, y, r in ((70, 90, 45), (115, 70, 55), (160, 95, 42), (110, 105, 50)):
        c.arc(x, y, r, 0, 2 * math.pi); c.set_source(lin(c, 0, 20, 0, 150, (0.85, 0.88, 0.94) if kind != 'storm' else (0.55, 0.58, 0.65), (1.15, 1.0, 0.75))); c.fill()
    if kind in ('rain', 'storm'):
        for i in range(7):
            x = 50 + i * 20; y0 = 150 + ((t * 300 + i * 23) % 70); c.move_to(x, y0); c.line_to(x - 6, y0 + 22); c.set_source_rgb(0.35, 0.65, 1); c.set_line_width(5); c.stroke()
    if kind == 'snow':
        for i in range(7):
            x = 50 + i * 20 + 6 * math.sin(t * 3 + i); y0 = 150 + ((t * 90 + i * 31) % 80)
            for a in range(3): c.move_to(x - 8 * math.cos(a * 1.05), y0 - 8 * math.sin(a * 1.05)); c.line_to(x + 8 * math.cos(a * 1.05), y0 + 8 * math.sin(a * 1.05)); c.set_source_rgb(1, 1, 1); c.set_line_width(3); c.stroke()
    return sticker(_pil(s), ow=4)
def wave(S=220, t=0.0):
    s, c = _surf(S, int(S * 0.8)); k = S / 220; c.scale(k, k)
    for j, col in enumerate(((0.15, 0.45, 0.85), (0.35, 0.7, 1.0))):
        c.new_path(); c.move_to(0, 170)
        for x in range(0, 221, 10): c.line_to(x, 110 + j * 25 + 18 * math.sin(x / 26 + t * 5 + j))
        c.line_to(220, 170); c.close_path(); c.set_source_rgb(*col); c.fill()
    c.new_path(); c.move_to(110, 10); c.line_to(140, 50); c.line_to(122, 50); c.line_to(122, 90); c.line_to(98, 90); c.line_to(98, 50); c.line_to(80, 50); c.close_path(); c.set_source_rgb(1, 1, 1); c.fill_preserve(); c.set_source_rgb(*INK); c.set_line_width(4); c.stroke()
    return sticker(_pil(s), ow=4)
_EARTH = None
def earth_emoji(u, S=640):
    """u 0..1: calm face -> worried -> top blows off with a fiery mushroom (mind blown)."""
    global _EARTH
    if _EARTH is None:
        cam = E.Camera(-30, 25, 22000, 0.1, 0, fov=36); im = E.render(cam, 900, 900)
        r = int(math.tan(math.asin(E.RE / (E.RE + 22000))) / math.tan(math.radians(18)) * 450) - 2
        _EARTH = (im, r)
    im, r = _EARTH
    s, c = _surf(S, int(S * 1.25)); cx, cy, R_ = S / 2, S * 0.72, S * 0.36
    shake = 6 * math.sin(u * 90) if 0.35 < u < 0.55 else 0; cx += shake
    disc = im.crop((450 - r, 450 - r, 450 + r, 450 + r)).resize((int(2 * R_), int(2 * R_)))
    mask = Image.new('L', disc.size, 0); ImageDraw.Draw(mask).ellipse([0, 0, disc.width - 1, disc.height - 1], fill=255)
    top_off = 0 if u < 0.5 else (u - 0.5) * 2
    body = Image.new('RGBA', (S, int(S * 1.25)), (0, 0, 0, 0)); d2 = disc.copy(); d2.putalpha(mask)
    # split the globe: top cap flies up when it blows
    cap_h = int(R_ * 0.55)
    lower = d2.crop((0, cap_h, d2.width, d2.height)); upper = d2.crop((0, 0, d2.width, cap_h))
    body.alpha_composite(lower, (int(cx - R_), int(cy - R_ + cap_h)))
    # explosion between cap and body
    s2, c2 = _surf(S, int(S * 1.25))
    if top_off > 0:
        for i in range(10):
            a = math.pi + i / 9 * math.pi; rr = R_ * (0.3 + 0.9 * top_off) * (0.8 + 0.2 * math.sin(i * 3.1))
            c2.arc(cx + math.cos(a) * rr * 0.8, cy - R_ + cap_h + math.sin(a) * rr * 0.9, R_ * 0.32 * (0.6 + top_off), 0, 2 * math.pi)
            g = cairo.RadialGradient(cx, cy - R_ + cap_h, 5, cx, cy - R_ + cap_h, R_ * 1.4); g.add_color_stop_rgb(0, 1, 0.95, 0.6); g.add_color_stop_rgb(0.5, 1, 0.55, 0.15); g.add_color_stop_rgb(1, 0.6, 0.25, 0.15)
            c2.set_source(g); c2.fill()
    body.alpha_composite(_pil(s2))
    body.alpha_composite(upper.rotate(-25 * top_off, expand=False), (int(cx - R_ + 40 * top_off), int(cy - R_ - R_ * 1.3 * top_off)))
    # face
    s3, c3 = _surf(S, int(S * 1.25)); ey = cy + R_ * 0.05
    worried = u > 0.25
    for sx in (-1, 1):
        ex = cx + sx * R_ * 0.33; c3.save(); c3.translate(ex, ey); c3.scale(1, 1.25 if worried else 1.0)
        c3.arc(0, 0, R_ * 0.16, 0, 2 * math.pi); c3.set_source_rgb(1, 1, 1); c3.fill_preserve(); c3.set_source_rgb(*INK); c3.set_line_width(5); c3.stroke()
        c3.arc(0, R_ * 0.02, R_ * (0.07 if worried else 0.09), 0, 2 * math.pi); c3.fill(); c3.restore()
    if u < 0.25: c3.new_path(); c3.move_to(cx - R_ * 0.25, cy + R_ * 0.4); c3.line_to(cx + R_ * 0.25, cy + R_ * 0.4)
    else: c3.new_path(); c3.save(); c3.translate(cx, cy + R_ * 0.45); c3.scale(1, 1.4); c3.arc(0, 0, R_ * 0.12, 0, 2 * math.pi); c3.restore()
    c3.set_source_rgb(*INK); c3.set_line_width(7); c3.stroke() if u < 0.25 else c3.fill()
    body.alpha_composite(_pil(s3))
    return body
def film(img, t, strength=1.0):
    a = np.asarray(img.convert('RGB')).astype(np.float32); g = a.mean(-1, keepdims=True)
    sep = np.concatenate([g * 1.07 + 18, g * 0.93 + 8, g * 0.72], -1); a = a * (1 - strength) + sep * strength
    a *= 0.92 + 0.08 * math.sin(t * 47)
    out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(out)
    rng = np.random.default_rng(int(t * 24))
    for i in range(int(18 * strength)): x = rng.integers(0, W); d.line([(x, 0), (x + rng.integers(-3, 3), H)], fill=(255, 255, 240, 40), width=1)
    for side in (0, W - 70):
        d.rectangle([side, 0, side + 70, H], fill=(10, 8, 6, int(230 * strength)))
        for k in range(14): y = (k * 140 + int(t * 600)) % (H + 140) - 70; d.rounded_rectangle([side + 18, y, side + 52, y + 60], 8, fill=(220, 210, 190, int(200 * strength)))
    return out
