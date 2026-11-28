"""Crisp satellite globe: NASA Blue Marble topo-bathy 21600x10800 (public domain) ray-cast through a tilted pinhole camera."""
import math, os
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RE = 6371.0
Image.MAX_IMAGE_PIXELS = None
_BM = None
def bm():
    """graded Blue Marble cached as a memory-mapped .npy (built in row chunks to keep RAM low)"""
    global _BM
    if _BM is None:
        path = f'{R}/work/bm_graded.npy'
        if not os.path.exists(path):
            im = Image.open(f'{R}/dl/bm21.jpg').convert('RGB'); a = np.asarray(im)
            out = np.lib.format.open_memmap(path + '.tmp.npy', mode='w+', dtype=np.uint8, shape=a.shape)
            for y0 in range(0, a.shape[0], 600):
                f = a[y0:y0 + 600].astype(np.float32)
                water = np.clip((f[..., 2] - np.maximum(f[..., 0], f[..., 1]) - 15) / 40, 0, 1)[..., None]
                lum = f.mean(-1, keepdims=True) / 255.0
                teal = np.concatenate([30 + 120 * lum, 105 + 170 * lum, 125 + 150 * lum], -1)
                f = f * (1 - water * 0.75) + teal * water * 0.75
                g = f.mean(-1, keepdims=True); f = g + (f - g) * 1.15; f = (f - 128) * 1.05 + 132
                out[y0:y0 + 600] = np.clip(f, 0, 255).astype(np.uint8)
            out.flush(); del out, a, im; os.replace(path + '.tmp.npy', path)
        _BM = np.load(path, mmap_mode='r')
    return _BM
def unit(lon, lat):
    lo, la = np.radians(lon), np.radians(lat); return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)
class Camera:
    def __init__(self, lon, lat, dist, pitch=30, heading=0, fov=40):
        self.lon, self.lat, self.dist, self.pitch, self.heading, self.fov = lon, lat, dist, pitch, heading, fov
    def lerp(self, o, k):
        L = lambda a, b: a + (b - a) * k
        dlon = ((o.lon - self.lon + 180) % 360) - 180
        return Camera(self.lon + dlon * k, L(self.lat, o.lat), math.exp(L(math.log(self.dist), math.log(o.dist))), L(self.pitch, o.pitch), L(self.heading, o.heading), L(self.fov, o.fov))
    def basis(self):
        n = unit(self.lon, self.lat); lo = math.radians(self.lon)
        e = np.array([-math.sin(lo), math.cos(lo), 0.0]); nn = np.cross(n, e)
        p, h = math.radians(max(self.pitch, 0.05)), math.radians(self.heading)
        hd = nn * math.cos(h) + e * math.sin(h); f = -n * math.cos(p) + hd * math.sin(p); f /= np.linalg.norm(f)
        r = np.cross(f, n); r /= np.linalg.norm(r); u = np.cross(r, f)
        return n * RE - f * self.dist, f, r, u
    def project(self, lon, lat, W, H, alt=0.0):
        C, f, r, u = self.basis(); P = unit(np.asarray(lon, float), np.asarray(lat, float)) * (RE + np.asarray(alt, float))[..., None] if np.ndim(alt) else unit(np.asarray(lon, float), np.asarray(lat, float)) * (RE + alt)
        v = P - C; z = v @ f; th = math.tan(math.radians(self.fov / 2))
        x = (v @ r) / (z * th * W / H) * W / 2 + W / 2; y = H / 2 - (v @ u) / (z * th) * H / 2
        front = ((P * (C - P)).sum(-1) > 0) & (z > 0); return x, y, front
STARS = None
def render(cam, W=1080, H=1920):
    global STARS
    a = bm(); C, f, r, u = cam.basis(); th = math.tan(math.radians(cam.fov / 2))
    sx = ((np.arange(W, dtype=np.float32) + 0.5) / W * 2 - 1) * th * W / H; sy = (1 - (np.arange(H, dtype=np.float32) + 0.5) / H * 2) * th
    d = f[None, None, :] + sx[None, :, None] * r[None, None, :] + sy[:, None, None] * u[None, None, :]; d /= np.linalg.norm(d, axis=-1, keepdims=True)
    b = (d * C).sum(-1); cc = C @ C - RE * RE; disc = b * b - cc; hit = disc > 0
    t = np.where(hit, -b - np.sqrt(np.maximum(disc, 0)), 0)
    P = C + d * t[..., None]; lon = np.degrees(np.arctan2(P[..., 1], P[..., 0])); lat = np.degrees(np.arcsin(np.clip(P[..., 2] / RE, -1, 1)))
    hh, ww = a.shape[:2]; px = (lon + 180) / 360 * ww - 0.5; py = (90 - lat) / 180 * hh - 0.5
    m = hit; out = np.zeros((H, W, 3), np.float32)
    yy, xx = py[m], px[m] % ww
    if m.any():
        y0, y1 = max(0, int(yy.min()) - 2), min(hh, int(yy.max()) + 3); x0, x1 = max(0, int(xx.min()) - 2), min(ww, int(xx.max()) + 3)
        if x1 - x0 > ww * 0.8: x0, x1 = 0, ww
        sub = np.asarray(a[y0:y1, x0:x1])
        for ch in range(3): out[..., ch][m] = map_coordinates(sub[..., ch], [yy - y0, xx - x0], order=1, mode='nearest')
    mu = np.clip(-(d * (P / RE)).sum(-1), 0, 1); rim = (1 - mu) ** 4 * 0.6
    out = out * (1 - rim[..., None]) + np.array([150, 200, 255], np.float32) * rim[..., None]
    if STARS is None or STARS.shape != (H, W):
        rng = np.random.default_rng(1); STARS = np.zeros((H, W), np.float32); ys = rng.integers(0, H, 900); xs = rng.integers(0, W, 900); STARS[ys, xs] = rng.uniform(0.3, 1, 900)
    halo = np.clip(1 - (np.sqrt(np.maximum(-disc, 0)) / RE) * 5, 0, 1) ** 2
    space = np.array([4, 8, 20], np.float32) + np.array([60, 120, 220], np.float32) * halo[..., None] + 255 * STARS[..., None] * (1 - halo[..., None])
    out = np.where(m[..., None], out, space)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
if __name__ == '__main__':
    import time
    t0 = time.time(); bm(); print('load', round(time.time() - t0, 1))
    for i, cam in enumerate([Camera(-40, 35, 14000, 8, 0), Camera(-30, 50, 6000, 30, 0), Camera(-45, 62, 3000, 38, 0)]):
        t0 = time.time(); im = render(cam); print(i, round(time.time() - t0, 2)); im.save(f'/tmp/claude-0/fr/e{i}.png')
