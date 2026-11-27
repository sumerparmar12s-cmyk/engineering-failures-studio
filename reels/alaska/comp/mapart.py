"""Self-drawn 'illustrated satellite' map: land/ocean/terrain generated procedurally from Natural Earth outlines (coordinates only).
Wrapped longitude: lonw = lon+360 if lon < 60 (so the Bering Strait is continuous)."""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LON0, LON1, LAT0, LAT1, K = 120.0, 300.0, 84.0, 4.0, 36   # canvas covers lonw 120..300, lat 80..12, K px/deg
CW, CH = int((LON1 - LON0) * K), int((LAT0 - LAT1) * K)
def wl(lon): return lon + 360 if lon < 0 else lon
def rings(geom):
    if geom['type'] == 'Polygon': return [geom['coordinates'][0]]
    return [p[0] for p in geom['coordinates']]
def load_shapes():
    C = json.load(open(f'{R}/dl/countries.geojson')); S = json.load(open(f'{R}/dl/states.geojson'))
    sh = {}
    for f in C['features']:
        sh['C:' + f['properties']['ADMIN']] = rings(f['geometry'])
    for f in S['features']:
        if f['properties'].get('admin') == 'United States of America': sh['S:' + f['properties']['name']] = rings(f['geometry'])
    # unwrap each ring so it is continuous across 180
    out = {}
    for k, rs in sh.items():
        rr = []
        for r in rs:
            pts = [(wl(x), y) for x, y in r]
            if max(p[0] for p in pts) - min(p[0] for p in pts) > 180: continue   # rings crossing lon 0 (Europe/Africa): not on this canvas
            rr.append(pts)
        out[k] = rr
    return out
def noise(h, w, seed, octaves=6, base=4):
    rng = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); amp = 1.0; tot = 0
    for o in range(octaves):
        n = base * 2 ** o; a = rng.random((max(2, int(n * h / w)) + 1, n + 1)).astype(np.float32)
        im = Image.fromarray((a * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += np.asarray(im, np.float32) / 255 * amp; tot += amp; amp *= 0.55
    return acc / tot
def build_canvas(sh):
    path = f'{R}/work/canvas.png'
    if os.path.exists(path): return Image.open(path)
    mask = Image.new('L', (CW, CH), 0); d = ImageDraw.Draw(mask)
    for k, rs in sh.items():
        if not k.startswith('C:'): continue
        for r in rs:
            pts = [((x - LON0) * K, (LAT0 - y) * K) for x, y in r]
            if len(pts) > 2: d.polygon(pts, fill=255)
    m = np.asarray(mask, np.float32) / 255
    lat = LAT0 - (np.arange(CH) + 0.5)[:, None] / K
    n1 = noise(CH, CW, 1, 7, 6); n2 = noise(CH, CW, 2, 6, 14); ridge = 1 - np.abs(noise(CH, CW, 3, 6, 10) * 2 - 1)
    # land colour by latitude: boreal green -> tundra olive -> snow; mountains from ridged noise
    t = np.clip((lat - 50) / 22, 0, 1)
    green = np.array([86, 112, 58], np.float32); olive = np.array([150, 140, 96], np.float32); brown = np.array([132, 104, 72], np.float32)
    snow = np.array([236, 240, 244], np.float32); desert = np.array([196, 168, 120], np.float32)
    tdes = np.clip((32 - lat) / 8, 0, 1)
    land = green * (1 - t[..., None]) + olive * t[..., None]
    land = land * (1 - tdes[..., None]) + desert * tdes[..., None]
    mtn = np.clip((ridge - 0.7) * 2.4, 0, 1)[..., None] * (0.55 + 0.45 * n2[..., None])
    land = land * (1 - mtn) + brown * mtn
    snowk = np.clip((lat - 67) / 9 + (ridge - 0.78) * 1.2, 0, 1)[..., None] * (0.6 + 0.4 * n1[..., None])
    land = land * (1 - snowk) + snow * snowk
    land *= (0.9 + 0.18 * n1[..., None])
    # hillshade
    hs = noise(CH, CW, 4, 7, 8) * 0.6 + ridge * 0.4; gy, gx = np.gradient(hs); shade = np.clip(1 + (gx - gy) * 70, 0.82, 1.15)[..., None]
    land *= shade
    # ocean: deep teal with lighter shallow band along coasts
    blur = np.asarray(mask.filter(ImageFilter.GaussianBlur(K * 0.9)), np.float32) / 255
    deep = np.array([18, 52, 78], np.float32); shallow = np.array([46, 118, 138], np.float32)
    sea = deep * (1 - blur[..., None] ** 0.7) + shallow * (blur[..., None] ** 0.7); sea *= (0.92 + 0.12 * n1[..., None])
    img = land * m[..., None] + sea * (1 - m[..., None])
    # thin bright coastline
    edge = np.asarray(mask.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
    img = img * (1 - edge[..., None] * 0.6) + 245 * edge[..., None] * 0.6
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)); out.save(path); return out
class Cam:
    def __init__(self, lon, lat, span, W=1080, H=1920): self.lon, self.lat, self.span, self.W, self.H = wl(lon), lat, span, W, H
    @property
    def s(self): return self.H / self.span
    @property
    def sx(self): return self.s * math.cos(math.radians(self.lat))
    def xy(self, lon, lat): return ((lon - self.lon) * self.sx + self.W / 2, (self.lat - lat) * self.s + self.H / 2)
    def lerp(self, o, k):
        c = Cam(0, 0, 1, self.W, self.H); c.lon = self.lon + (o.lon - self.lon) * k; c.lat = self.lat + (o.lat - self.lat) * k
        c.span = math.exp(math.log(self.span) + (math.log(o.span) - math.log(self.span)) * k); return c
def render_bg(canvas, cam):
    lonspan = cam.W / cam.sx; latspan = cam.span
    x0 = (cam.lon - lonspan / 2 - LON0) * K; y0 = (LAT0 - (cam.lat + latspan / 2)) * K
    bx = (x0, y0, x0 + lonspan * K, y0 + latspan * K)
    if bx[0] >= 0 and bx[1] >= 0 and bx[2] <= CW and bx[3] <= CH:
        return canvas.resize((cam.W, cam.H), Image.BICUBIC, box=bx)
    ib = tuple(int(math.floor(v)) for v in bx[:2]) + tuple(int(math.ceil(v)) for v in bx[2:])
    c = canvas.crop(ib); fx, fy = bx[0] - ib[0], bx[1] - ib[1]
    return c.resize((cam.W, cam.H), Image.BICUBIC, box=(fx, fy, fx + bx[2] - bx[0], fy + bx[3] - bx[1]))
if __name__ == '__main__':
    sh = load_shapes(); cv = build_canvas(sh); print(cv.size)
    for name, cam in [('ak', Cam(-152, 63, 28)), ('bering', Cam(-172, 64, 30)), ('us', Cam(-108, 44, 74))]:
        render_bg(cv, cam).resize((360, 640)).save(f'/tmp/claude-0/fr/map_{name}.png')
