"""Self-drawn 3D-tilted map engine: procedural textures (from Natural Earth outlines + hand-drawn local coast) ray-cast through a pinhole camera."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import map_coordinates
from shapely.geometry import Polygon, box, mapping
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COS0 = math.cos(math.radians(45)); KX, KY = 111.32 * COS0, 110.57
def to_xy(lon, lat): return np.asarray(lon) * KX, np.asarray(lat) * KY
def to_ll(x, y): return x / KX, y / KY
def noise(h, w, seed, octaves=6, base=4):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = np.float32(1.0); tot = 0
    for o in range(octaves):
        n = base * 2 ** o; a = rng.random((max(2, int(n * h / w)) + 1, n + 1)).astype(np.float32)
        acc += np.asarray(Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 * amp; tot += amp; amp *= 0.55
    return acc / tot
def paint(mask, lat, seed, detail=1.0):
    """mask (HxW float 0..1 land), lat (Hx1) -> RGB float terrain/ocean"""
    h, w = mask.shape; n1 = noise(h, w, seed, 7, int(6 * detail)); n2 = noise(h, w, seed + 1, 6, int(14 * detail)); ridge = 1 - np.abs(noise(h, w, seed + 2, 6, int(10 * detail)) * 2 - 1)
    t = np.clip((lat - 48) / 24, 0, 1)
    green = np.array([92, 118, 62], np.float32); olive = np.array([150, 142, 98], np.float32); brown = np.array([138, 110, 76], np.float32); snow = np.array([236, 240, 244], np.float32); desert = np.array([200, 172, 124], np.float32)
    tdes = np.clip((34 - lat) / 8, 0, 1)
    land = green * (1 - t[..., None]) + olive * t[..., None]; land = land * (1 - tdes[..., None]) + desert * tdes[..., None]
    mtn = np.clip((ridge - 0.7) * 2.4, 0, 1)[..., None] * (0.55 + 0.45 * n2[..., None]); land = land * (1 - mtn) + brown * mtn
    sn = np.clip((lat - 66) / 9 + (ridge - 0.8) * 1.2, 0, 1)[..., None] * (0.6 + 0.4 * n1[..., None]); land = land * (1 - sn) + snow * sn
    land *= (0.9 + 0.18 * n1[..., None])
    hs = noise(h, w, seed + 3, 7, int(8 * detail)) * 0.6 + ridge * 0.4; gy, gx = np.gradient(hs); land *= np.clip(1 + (gx - gy) * 70, 0.82, 1.15)[..., None]
    mi = Image.fromarray((mask * 255).astype(np.uint8)); blur = np.asarray(mi.filter(ImageFilter.GaussianBlur(max(4, w / 160))), np.float32) / 255
    deep = np.array([16, 50, 78], np.float32); shallow = np.array([52, 128, 146], np.float32)
    sea = deep * (1 - blur[..., None] ** 0.7) + shallow * (blur[..., None] ** 0.7); sea *= (0.93 + 0.1 * n1[..., None])
    img = land * mask[..., None] + sea * (1 - mask[..., None])
    edge = np.asarray(mi.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    return img * (1 - edge[..., None] * 0.55) + 240 * edge[..., None] * 0.55
class Tex:
    def __init__(self, name, lon0, lon1, lat0, lat1, K, rings, seed, detail=1.0):
        self.lon0, self.lon1, self.lat0, self.lat1, self.K = lon0, lon1, lat0, lat1, K
        path = f'{R}/work/tex_{name}.npy'
        if os.path.exists(path): self.a = np.load(path); return
        w, h = int((lon1 - lon0) * K), int((lat0 - lat1) * K)
        m = Image.new('L', (w, h), 0); d = ImageDraw.Draw(m)
        for r in rings: d.polygon([((x - lon0) * K, (lat0 - y) * K) for x, y in r], fill=255)
        lat = lat0 - (np.arange(h) + 0.5)[:, None] / K
        self.a = np.clip(paint(np.asarray(m, np.float32) / 255, lat, seed, detail), 0, 255).astype(np.uint8); np.save(path, self.a)
    def sample(self, lon, lat):
        px = (lon - self.lon0) * self.K; py = (self.lat0 - lat) * self.K
        inside = (px >= 0) & (py >= 0) & (px < self.a.shape[1] - 1) & (py < self.a.shape[0] - 1)
        out = np.stack([map_coordinates(self.a[..., c], [py, px], order=1, mode='nearest') for c in range(3)], -1).astype(np.float32)
        return out, inside
def rings_of(geom):
    if geom['type'] == 'Polygon': return [geom['coordinates'][0]]
    return [p[0] for p in geom['coordinates']]
C50 = json.load(open(f'{R}/dl/countries.geojson'))
def country(name): return [r for f in C50['features'] if f['properties']['ADMIN'] == name for r in rings_of(f['geometry'])]
NA_RINGS = [r for f in C50['features'] for r in rings_of(f['geometry']) if all(-180 <= x <= -40 for x, _ in r[:1])]
# ---- hand-drawn local coastline around Point Roberts / Tsawwassen / Boundary Bay (stylised from public geography) ----
LOCAL_LAND = [(-123.70, 49.60), (-123.70, 49.42), (-123.28, 49.33), (-123.21, 49.27), (-123.24, 49.25), (-123.20, 49.15), (-123.17, 49.10), (-123.13, 49.065), (-123.105, 49.045), (-123.098, 49.025),
              (-123.094, 49.005), (-123.090, 48.986), (-123.083, 48.974), (-123.066, 48.971), (-123.046, 48.972), (-123.033, 48.977), (-123.024, 48.988),
              (-123.022, 49.000), (-123.027, 49.018), (-123.030, 49.040), (-123.012, 49.058), (-122.975, 49.072), (-122.93, 49.080), (-122.885, 49.078),
              (-122.845, 49.064), (-122.815, 49.040), (-122.795, 49.017), (-122.778, 49.000), (-122.762, 48.990), (-122.752, 48.975), (-122.742, 48.950),
              (-122.70, 48.92), (-122.66, 48.88), (-122.60, 48.75), (-122.50, 48.55), (-121.90, 48.55), (-121.90, 49.60)]
LAND_POLY = Polygon(LOCAL_LAND)
PR_POLY = LAND_POLY.intersection(box(-123.2, 48.9, -122.95, 49.0))     # Point Roberts: peninsula tip south of 49N
US_LOCAL = LAND_POLY.intersection(box(-122.95, 48.7, -122.3, 49.0)).union(PR_POLY)
CA_LOCAL = LAND_POLY.intersection(box(-123.5, 49.0, -122.3, 49.3))
def poly_rings(g):
    gs = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [list(p.exterior.coords) for p in gs]
_TEX = {}
def textures():
    if not _TEX:
        _TEX['na'] = Tex('na', -172, -48, 76, 12, 85, NA_RINGS, 21, detail=2.0)
        C10 = json.load(open(f'{R}/dl/c10.geojson'))
        mid = [r for f in C10['features'] if f['properties']['ADMIN'] in ('United States of America', 'Canada') for r in rings_of(f['geometry'])
               if any(-128 < x < -117 and 45.5 < y < 52 for x, y in r[::max(1, len(r) // 50)])]
        _TEX['mid'] = Tex('mid', -128.0, -117.0, 52.0, 45.5, 650, mid, 41, detail=6.0)
        _TEX['loc'] = Tex('loc', -123.70, -122.10, 49.55, 48.60, 2800, [LOCAL_LAND], 31, detail=4.0)
    return _TEX
class Camera:
    def __init__(self, lon, lat, dist, pitch=35, heading=0, fov=42):
        self.lon, self.lat, self.dist, self.pitch, self.heading, self.fov = lon, lat, dist, pitch, heading, fov
    def lerp(self, o, k):
        L = lambda a, b: a + (b - a) * k
        return Camera(L(self.lon, o.lon), L(self.lat, o.lat), math.exp(L(math.log(self.dist), math.log(o.dist))), L(self.pitch, o.pitch), L(self.heading, o.heading), L(self.fov, o.fov))
    def basis(self):
        p, h = math.radians(self.pitch), math.radians(self.heading)
        f = np.array([math.sin(p) * math.sin(h), math.sin(p) * math.cos(h), -math.cos(p)])
        r = np.array([math.cos(h), -math.sin(h), 0.0]); u = np.cross(r, f)
        tx, ty = to_xy(self.lon, self.lat); C = np.array([tx, ty, 0.0]) - f * self.dist
        return C, f, r, u
    def project(self, lon, lat, W, H):
        C, f, r, u = self.basis(); x, y = to_xy(np.asarray(lon, float), np.asarray(lat, float))
        v = np.stack([x - C[0], y - C[1], -C[2] * np.ones_like(x)], -1); z = v @ f; th = math.tan(math.radians(self.fov / 2))
        sx = (v @ r) / (z * th * W / H); sy = (v @ u) / (z * th)
        return (sx + 1) * W / 2, (1 - sy) * H / 2, z > 0
def render(cam, W=540, H=960):
    T = textures(); C, f, r, u = cam.basis(); th = math.tan(math.radians(cam.fov / 2))
    sx = (np.arange(W) + 0.5) / W * 2 - 1; sy = 1 - (np.arange(H) + 0.5) / H * 2
    SX, SY = np.meshgrid(sx * th * W / H, sy * th)
    d = f[None, None, :] + SX[..., None] * r[None, None, :] + SY[..., None] * u[None, None, :]
    dz = d[..., 2]; ground = dz < -1e-4; t = np.where(ground, -C[2] / np.where(ground, dz, -1), 1e9)
    gx = C[0] + d[..., 0] * t; gy = C[1] + d[..., 1] * t; lon, lat = to_ll(gx, gy)
    col, ins0 = T['na'].sample(lon, lat); col = np.where(ins0[..., None], col, np.array([16, 50, 78], np.float32))
    wm = np.clip((2600 - cam.dist) / 1300, 0, 1)
    if wm > 0:
        cm_, insm = T['mid'].sample(lon, lat); M_ = T['mid']
        efm = np.clip(np.minimum.reduce([(lon - M_.lon0), (M_.lon1 - lon), (lat - M_.lat1), (M_.lat0 - lat)]) / 0.8, 0, 1)
        km = (insm * efm * wm)[..., None]; col = col * (1 - km) + cm_ * km
    w2 = np.clip((260 - cam.dist) / 160, 0, 1)
    if w2 > 0:
        cl, ins = T['loc'].sample(lon, lat); L = T['loc']
        ef = np.clip(np.minimum.reduce([(lon - L.lon0), (L.lon1 - lon), (lat - L.lat1), (L.lat0 - lat)]) / 0.12, 0, 1)
        k = (ins * ef * w2)[..., None]; col = col * (1 - k) + cl * k
    # atmosphere: distance haze + sky above the horizon
    haze = 1 - np.exp(-t / (cam.dist * 4.0)); hz = np.array([190, 214, 232], np.float32)
    col = col * (1 - haze[..., None] * 0.35) + hz * haze[..., None] * 0.35
    sky = np.array([150, 196, 235], np.float32) * (1 - np.clip(SY / th, 0, 1)[..., None] * 0.5) + np.array([40, 90, 160], np.float32) * np.clip(SY / th, 0, 1)[..., None] * 0.5
    col = np.where(ground[..., None], col, sky)
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
if __name__ == '__main__':
    import time
    for i, cam in enumerate([Camera(-100, 44, 11000, 22), Camera(-112, 47, 4500, 35, -8), Camera(-123.0, 49.02, 70, 45, -12), Camera(-123.05, 48.99, 20, 50, -18)]):
        t0 = time.time(); im = render(cam); print(i, round(time.time() - t0, 2)); im.resize((270, 480)).save(f'/tmp/claude-0/fr/w3d_{i}.png')
