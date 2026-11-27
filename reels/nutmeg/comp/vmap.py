"""Crisp vector 'parchment' map engine (cairo, full resolution, Web-Mercator camera, optional perspective tilt).
Land = Natural Earth 10m (outlines only), drawn with paper fill + coastal ripple lines; territories = flat bold fills with dark outlines."""
import json, math, os
import numpy as np, cairo
from PIL import Image, ImageFilter
from shapely.geometry import shape, box, Polygon, MultiPolygon
from shapely.strtree import STRtree
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
def merc(lon, lat):
    lat = max(-85, min(85, lat)); return math.radians(lon), math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
def unmerc(x, y): return math.degrees(x), math.degrees(2 * math.atan(math.exp(y)) - math.pi / 2)
# ---------- data ----------
def _load(fn):
    d = json.load(open(f'{R}/dl/{fn}')); return [shape(f['geometry']) for f in d['features']], d['features']
_LAND = None
def land():
    global _LAND
    if _LAND is None:
        gs, _ = _load('land10.geojson'); polys = []
        for g in gs: polys += list(g.geoms) if g.geom_type == 'MultiPolygon' else [g]
        polys.append(RUN_ISLAND)
        lods = {}
        for tol in (0.5, 0.15, 0.04):
            ps = [q for q in (p.simplify(tol) for p in polys if p.area > tol * tol * 0.5) if not q.is_empty]
            lods[tol] = (ps, STRtree(ps))
        _LAND = (polys, lods, STRtree(polys))
    return _LAND
_C = None
def countries():
    global _C
    if _C is None: gs, fs = _load('c50.geojson'); _C = {f['properties']['ADMIN']: g for g, f in zip(gs, fs)}
    return _C
# hand-drawn Run island (Pulau Run, Banda Islands): ~3 km long, NE-SW
def _ellipse(cx, cy, a, b, ang, n=40, wob=0.12, seed=3):
    rng = np.random.default_rng(seed); pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; r = 1 + wob * math.sin(3 * t + rng.random()) * 0.5 + wob * 0.5 * math.sin(5 * t)
        x, y = a * r * math.cos(t), b * r * math.sin(t); ca, sa = math.cos(ang), math.sin(ang)
        pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return Polygon(pts)
RUN_ISLAND = _ellipse(129.693, -4.552, 0.014, 0.0055, math.radians(25))
# ---------- camera ----------
class Cam:
    def __init__(self, lon, lat, z, rot=0.0, tilt=0.0):   # z: screen px per degree of longitude at the equator
        self.lon, self.lat, self.z, self.rot, self.tilt = lon, lat, z, rot, tilt
    def lerp(self, o, k):
        L = lambda a, b: a + (b - a) * k
        return Cam(L(self.lon, o.lon), L(self.lat, o.lat), math.exp(L(math.log(self.z), math.log(o.z))), L(self.rot, o.rot), L(self.tilt, o.tilt))
    @property
    def k(self): return self.z * 180 / math.pi   # px per mercator unit
    def xy(self, lon, lat):
        mx, my = merc(lon, lat); cx, cy = merc(self.lon, self.lat); x, y = (mx - cx) * self.k, -(my - cy) * self.k
        r = math.radians(self.rot); return W / 2 + x * math.cos(r) - y * math.sin(r), H / 2 + x * math.sin(r) + y * math.cos(r)
    def bounds(self, pad=0.25):
        pts = [unmerc(merc(self.lon, self.lat)[0] + sx * (W * (1 + pad)) / 2 / self.k * 1.5, merc(self.lon, self.lat)[1] + sy * (H * (1 + pad)) / 2 / self.k * 1.2) for sx in (-1, 1) for sy in (-1, 1)]
        return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)
def path_geom(c, cam, g, tol_px=0.7):
    gs = list(g.geoms) if hasattr(g, 'geoms') else [g]
    tol = tol_px / cam.z if cam.z > 250 else 0   # degrees per px (LOD lists are pre-simplified)
    for p in gs:
        if p.is_empty or p.geom_type != 'Polygon': continue
        q0 = p.simplify(tol, preserve_topology=False) if tol > 1e-5 else p
        qs = list(q0.geoms) if hasattr(q0, 'geoms') else [q0]
        for ring in [r for q in qs if q.geom_type == 'Polygon' and not q.is_empty for r in [q.exterior] + list(q.interiors)]:
            cs = list(ring.coords)
            if len(cs) < 3: continue
            x, y = cam.xy(*cs[0]); c.move_to(x, y)
            for lo, la in cs[1:]: x, y = cam.xy(lo, la); c.line_to(x, y)
            c.close_path()
# ---------- paper textures (screen space, generated once) ----------
def _noise(h, w, seed, oct=5, base=6):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        n = base * 2 ** o; a = rng.random((int(n * h / w) + 2, n + 2)).astype(np.float32)
        acc += np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 * amp; tot += amp; amp *= 0.55
    return acc / tot
_PAPER = None
def paper():
    global _PAPER
    if _PAPER is None:
        n = _noise(H, W, 5, 6, 5); f = _noise(H, W, 6, 3, 60)
        sea = np.dstack([0.42 + 0.06 * n, 0.56 + 0.06 * n, 0.58 + 0.05 * n]) * 255
        land = np.dstack([0.86 + 0.06 * n - 0.03 * f, 0.79 + 0.06 * n - 0.03 * f, 0.62 + 0.05 * n - 0.03 * f]) * 255
        vig = 1 - 0.18 * (np.hypot((np.arange(W)[None] - W / 2) / W, (np.arange(H)[:, None] - H / 2) / H) * 1.6) ** 2
        _PAPER = (np.clip(sea * vig[..., None], 0, 255).astype(np.uint8), np.clip(land * vig[..., None], 0, 255).astype(np.uint8))
    return _PAPER
def to_surface(rgb):
    h, w, _ = rgb.shape; a = np.zeros((h, w, 4), np.uint8); a[..., 0] = rgb[..., 2]; a[..., 1] = rgb[..., 1]; a[..., 2] = rgb[..., 0]; a[..., 3] = 255
    return cairo.ImageSurface.create_for_data(memoryview(a), cairo.FORMAT_ARGB32, w, h), a
def render(cam, territories=(), extra=None):
    """territories: list of (shapely geom, (r,g,b), alpha). returns PIL RGB."""
    sea_rgb, land_rgb = paper()
    s, keep = to_surface(sea_rgb.copy()); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND)
    polys, lods, tree = land(); x0, y0, x1, y1 = cam.bounds(); bb = box(x0, y0, x1, y1)
    if cam.z > 250: use = [polys[i] for i in tree.query(bb)]
    else:
        tol = 0.5 if cam.z < 12 else (0.15 if cam.z < 60 else 0.04); ps, tr = lods[tol]; use = [ps[i] for i in tr.query(bb)]
    # coastal ripples (vintage map water lines)
    c.new_path()
    for p in use: path_geom(c, cam, p)
    for wdt, a in ((34, 0.10), (20, 0.14), (9, 0.22)):
        c.set_source_rgba(0.25, 0.38, 0.42, a); c.set_line_width(wdt); c.stroke_preserve()
    c.new_path()
    for p in use: path_geom(c, cam, p)
    lsurf, lkeep = to_surface(land_rgb); c.save(); c.clip_preserve(); c.set_source_surface(lsurf, 0, 0); c.paint(); c.restore()
    c.new_path()
    for g, col, a in territories:
        c.new_path(); path_geom(c, cam, g); c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.set_source_rgba(*col, a); c.fill_preserve()
        c.set_source_rgba(0.08, 0.08, 0.1, 0.95 * min(1, a / 0.6)); c.set_line_width(4.2); c.stroke()
    c.new_path()
    for p in use: path_geom(c, cam, p)
    c.set_source_rgba(0.12, 0.12, 0.14, 0.9); c.set_line_width(2.6); c.stroke()
    if extra: extra(c, cam)
    s.flush(); a = np.frombuffer(s.get_data(), np.uint8).reshape(H, W, 4)
    img = Image.fromarray(a[..., [2, 1, 0]].copy())
    if cam.tilt > 0.01: img = tilt(img, cam.tilt)
    return img
def tilt(img, k):
    """fake 3D: perspective-tilt the flat map (top recedes)."""
    dx = W * 0.22 * k; dy = H * 0.06 * k
    # map output corners to input quad (PIL expects coefficients mapping output->input)
    src = [(dx, dy), (W - dx, dy), (W, H), (0, H)]; dst = [(0, 0), (W, 0), (W, H), (0, H)]
    A = []; B = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u); A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    coef = np.linalg.solve(np.array(A, float), np.array(B, float))
    out = img.transform((W, H), Image.PERSPECTIVE, tuple(coef), Image.BICUBIC, fillcolor=(108, 140, 146))
    # atmospheric haze toward the top
    g = np.linspace(1, 0, H)[:, None, None] ** 3 * 0.35 * k
    arr = np.asarray(out, np.float32); arr = arr * (1 - g) + np.array([196, 214, 214]) * g
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))
if __name__ == '__main__':
    import time
    from shapely.geometry import Point
    tests = [('world', Cam(20, 25, 5.5)), ('europe', Cam(10, 50, 28, 0, 0.6)), ('nyc', Cam(-74.0, 40.75, 3500)), ('banda', Cam(129.8, -4.55, 2500, -8, 0.5)), ('indo', Cam(122, -3, 70))]
    for n, cam in tests:
        t0 = time.time(); im = render(cam, [(countries()['Netherlands'], (0.95, 0.5, 0.1), 0.85)] if n == 'europe' else []); print(n, round(time.time() - t0, 2))
        im.resize((270, 480)).save(f'/tmp/claude-0/fr/vm_{n}.png')
