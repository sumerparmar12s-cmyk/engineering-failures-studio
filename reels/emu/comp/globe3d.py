"""Self-drawn 3D globe map engine (Point Roberts look, but on a real sphere): procedural terrain textures painted from
Natural Earth 10m outlines at several detail levels, ray-cast through a tilted pinhole camera at full resolution."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates
from shapely.geometry import shape, Polygon, box
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE = 6371.0
def noise(h, w, seed, octaves=6, base=4):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o; a = rng.random((max(2, int(n * h / w)) + 1, n + 1)).astype(np.float32)
        acc += np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) * np.float32(amp / 255); tot += amp; amp *= 0.55
    return acc / np.float32(tot)
def paint(mask, lat, seed, detail=1.0):
    h, w = mask.shape; d = lambda b: max(2, int(b * detail))
    n1 = noise(h, w, seed, 7, d(6)); n2 = noise(h, w, seed + 1, 6, d(14)); ridge = 1 - np.abs(noise(h, w, seed + 2, 6, d(10)) * 2 - 1)
    lat = lat.astype(np.float32)
    t = np.clip((np.abs(lat) - 48) / 24, 0, 1)
    lush = np.array([60, 104, 50], np.float32); green = np.array([92, 118, 62], np.float32); olive = np.array([150, 142, 98], np.float32)
    brown = np.array([138, 110, 76], np.float32); snow = np.array([236, 240, 244], np.float32); desert = np.array([206, 178, 128], np.float32)
    trop = np.clip(1 - np.abs(lat) / 18, 0, 1)                      # equatorial rainforest band
    des = np.clip(1 - np.abs(lat - 24) / 9, 0, 1) * 0.85             # northern desert band (Sahara/Arabia)
    land = green * (1 - t[..., None]) + olive * t[..., None]
    land = land * (1 - trop[..., None]) + lush * trop[..., None]
    land = land * (1 - des[..., None]) + desert * des[..., None]
    mtn = np.clip((ridge - 0.72) * 2.2, 0, 1)[..., None] * (0.5 + 0.5 * n2[..., None]); land = land * (1 - mtn) + brown * mtn
    sn = np.clip((np.abs(lat) - 64) / 9 + (ridge - 0.82) * 1.2, 0, 1)[..., None] * (0.6 + 0.4 * n1[..., None]); land = land * (1 - sn) + snow * sn
    land *= (0.92 + 0.14 * n1[..., None])
    hs = noise(h, w, seed + 3, 7, d(8)) * 0.6 + ridge * 0.4; gy, gx = np.gradient(hs); land *= np.clip(1 + (gx - gy) * 60 / detail ** 0.3, 0.84, 1.14)[..., None]
    mi = Image.fromarray((mask * 255).astype(np.uint8)); blur = np.asarray(mi.filter(ImageFilter.GaussianBlur(max(3, w / 220))), np.float32) / 255
    deep = np.array([16, 52, 82], np.float32); shallow = np.array([48, 132, 150], np.float32)
    sea = deep * (1 - blur[..., None] ** 0.7) + shallow * (blur[..., None] ** 0.7); sea *= (0.94 + 0.08 * n1[..., None])
    img = land * mask[..., None] + sea * (1 - mask[..., None])
    edge = np.asarray(mi.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.0)), np.float32) / 255
    return img * (1 - edge[..., None] * 0.5) + 240 * edge[..., None] * 0.5
_LANDG = None
def land_polys():
    global _LANDG
    if _LANDG is None:
        d = json.load(open(f'{R}/dl/land10.geojson')); ps = []
        for f in d['features']:
            g = shape(f['geometry']); ps += list(g.geoms) if g.geom_type == 'MultiPolygon' else [g]
        _LANDG = ps
    return _LANDG
def _ellipse(cx, cy, a, b, ang, n=48, seed=3):
    rng = np.random.default_rng(seed); pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; r = 1 + 0.08 * math.sin(3 * t + 1.3) + 0.05 * math.sin(5 * t + rng.random())
        x, y = a * r * math.cos(t), b * r * math.sin(t); ca, sa = math.cos(ang), math.sin(ang); pts.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    return Polygon(pts)
RUN_ISLAND = _ellipse(129.693, -4.552, 0.014, 0.0055, math.radians(25))
class Tex:
    def __init__(self, name, lon0, lon1, lat0, lat1, K, seed, detail, near, far):
        self.lon0, self.lon1, self.lat0, self.lat1, self.K, self.near, self.far = lon0, lon1, lat0, lat1, K, near, far
        path = f'{R}/work/tex_{name}.npy'
        if os.path.exists(path): self.a = np.load(path, mmap_mode='r'); return
        w, h = int((lon1 - lon0) * K), int((lat0 - lat1) * K)
        m = Image.new('L', (w, h), 0); dr = ImageDraw.Draw(m); bb = box(lon0 - 1, lat1 - 1, lon1 + 1, lat0 + 1)
        for p in land_polys():
            if not p.intersects(bb): continue
            q = p.simplify(0.5 / K) if K < 200 else p
            for ring in [q.exterior]:
                dr.polygon([((x - lon0) * K, (lat0 - y) * K) for x, y in ring.coords], fill=255)
            for ring in q.interiors: dr.polygon([((x - lon0) * K, (lat0 - y) * K) for x, y in ring.coords], fill=0)
        lat = lat0 - (np.arange(h, dtype=np.float32) + 0.5)[:, None] / K
        a = np.clip(paint(np.asarray(m, np.float32) / 255, lat, seed, detail), 0, 255).astype(np.uint8); np.save(path, a); self.a = np.load(path, mmap_mode='r')
    def sample(self, lon, lat):
        px = (lon - self.lon0) * self.K; py = (self.lat0 - lat) * self.K
        if self.lon1 - self.lon0 >= 359: px = np.clip(px, 0, self.a.shape[1] - 1.01)
        ins = (px >= 0) & (py >= 0) & (px < self.a.shape[1] - 1) & (py < self.a.shape[0] - 1)
        ef = np.clip(np.minimum.reduce([lon - self.lon0, self.lon1 - lon, lat - self.lat1, self.lat0 - lat]) / ((self.lon1 - self.lon0) * 0.06), 0, 1) * ins
        if not ins.any(): return None, ef
        ys, xs = np.where(ins); y0, y1 = int(py[ins].min()), int(py[ins].max()) + 2; x0, x1 = int(px[ins].min()), int(px[ins].max()) + 2
        sub = np.asarray(self.a[max(0, y0):y1, max(0, x0):x1])
        out = np.zeros(lon.shape + (3,), np.float32)
        for c in range(3): out[..., c][ins] = map_coordinates(sub[..., c], [py[ins] - max(0, y0), px[ins] - max(0, x0)], order=1, mode='nearest')
        return out, ef
LEVELS = [('world', -180, 180, 80, -60, 40, 51, 1.6, 0, 1e9),
          ('aus', 110, 156, -9, -45, 110, 81, 2.4, 0, 6000)]
_T = {}
def tex():
    if not _T:
        for L in LEVELS: _T[L[0]] = Tex(*L)
    return _T
def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat); return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
class Camera:
    def __init__(self, lon, lat, dist, pitch=35, heading=0, fov=42):
        self.lon, self.lat, self.dist, self.pitch, self.heading, self.fov = lon, lat, dist, pitch, heading, fov
    def lerp(self, o, k):
        L = lambda a, b: a + (b - a) * k
        return Camera(L(self.lon, o.lon), L(self.lat, o.lat), math.exp(L(math.log(self.dist), math.log(o.dist))), L(self.pitch, o.pitch), L(self.heading, o.heading), L(self.fov, o.fov))
    def basis(self):
        n = unit(self.lon, self.lat); lo = math.radians(self.lon); la = math.radians(self.lat)
        e = np.array([-math.sin(lo), math.cos(lo), 0.0]); nn = np.cross(n, e)
        p, h = math.radians(self.pitch), math.radians(self.heading)
        hd = nn * math.cos(h) + e * math.sin(h); f = -n * math.cos(p) + hd * math.sin(p); f /= np.linalg.norm(f)
        r = np.cross(f, n); r /= np.linalg.norm(r); u = np.cross(r, f)
        C = n * RE - f * self.dist; return C, f, r, u
    def project(self, lon, lat, W, H):
        C, f, r, u = self.basis(); P = unit(np.asarray(lon, float), np.asarray(lat, float)) * RE
        v = P - C; z = v @ f; th = math.tan(math.radians(self.fov / 2))
        sx = (v @ r) / (z * th * W / H); sy = (v @ u) / (z * th)
        front = ((P * (C - P)).sum(-1) > 0) & (z > 0)
        return (sx + 1) * W / 2, (1 - sy) * H / 2, front
def render(cam, W=1080, H=1920):
    T = tex(); C, f, r, u = cam.basis(); th = math.tan(math.radians(cam.fov / 2))
    sx = ((np.arange(W, dtype=np.float32) + 0.5) / W * 2 - 1) * th * W / H; sy = (1 - (np.arange(H, dtype=np.float32) + 0.5) / H * 2) * th
    d = f[None, None, :] + sx[None, :, None] * r[None, None, :] + sy[:, None, None] * u[None, None, :]
    d /= np.linalg.norm(d, axis=-1, keepdims=True)
    b = (d * C).sum(-1); c = (C @ C) - RE * RE; disc = b * b - c; hit = disc > 0
    t = np.where(hit, -b - np.sqrt(np.maximum(disc, 0)), 1e9)
    P = C + d * t[..., None]; lon = np.degrees(np.arctan2(P[..., 1], P[..., 0])); lat = np.degrees(np.arcsin(np.clip(P[..., 2] / RE, -1, 1)))
    col, _ = T['world'].sample(lon, lat)
    for L in LEVELS[1:]:
        tx = T[L[0]]
        if not (tx.near <= cam.dist <= tx.far * 1.0): continue
        wd = np.clip((tx.far - cam.dist) / (tx.far * 0.5), 0, 1)
        cl, ef = tx.sample(lon, lat)
        if cl is None: continue
        k = (ef * wd * hit)[..., None]; col = col * (1 - k) + cl * k
    # light atmosphere toward the limb + space
    mu = np.clip(-(d * (P / RE)).sum(-1), 0, 1)
    rim = (1 - mu) ** 3 * 0.55; col = col * (1 - rim[..., None]) + np.array([170, 205, 240], np.float32) * rim[..., None]
    sky = np.array([8, 14, 32], np.float32) + np.array([70, 120, 190], np.float32) * np.clip(1 - (np.sqrt(np.maximum(-disc, 0)) / RE) * 6, 0, 1)[..., None] ** 2
    col = np.where(hit[..., None], col, sky)
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
if __name__ == '__main__':
    import time
    t0 = time.time(); tex(); print('tex', round(time.time() - t0, 1))
    for i, cam in enumerate([Camera(-40, 30, 14000, 10), Camera(5, 50, 2200, 35, -5), Camera(-74.0, 40.75, 40, 45, -20), Camera(129.72, -4.55, 30, 45, 0), Camera(120, -3, 2200, 30, 0)]):
        t0 = time.time(); im = render(cam); print(i, round(time.time() - t0, 2)); im.resize((270, 480)).save(f'/tmp/claude-0/fr/g3_{i}.png')
