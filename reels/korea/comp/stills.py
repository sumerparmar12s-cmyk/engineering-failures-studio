import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cairo
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from shapely.geometry import shape, Polygon, box
from shapely.ops import unary_union
import globe3d as G, raise3d as R3, flags as FL, toons as TO
W, H = 1080, 1920; R = G.R
C50 = {f['properties']['ADMIN']: shape(f['geometry']) for f in json.load(open(f'{R}/dl/c50.geojson'))['features']}
USSR = unary_union([C50[n].intersection(box(19, 34, 179.9, 82)) for n in ['Russia', 'Ukraine', 'Belarus', 'Kazakhstan', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan', 'Tajikistan', 'Georgia', 'Armenia', 'Azerbaijan', 'Moldova', 'Lithuania', 'Latvia', 'Estonia']])
USA48 = [p for p in R3.polys(C50['United States of America']) if p.bounds[0] > -130 and p.bounds[1] > 24][0] if False else max(R3.polys(C50['United States of America']), key=lambda p: p.area)
FONTS = '/home/user/engineering-failures-studio/.toolchain/fonts'
def F(name, size):
    p = {'play': 'PlayfairDisplay.ttf', 'oswald': 'Oswald.ttf'}.get(name)
    f = ImageFont.truetype(f'{FONTS}/{p}', size) if p else ImageFont.truetype(f'/usr/share/fonts/opentype/inter/Inter-{name}.otf', size)
    if name == 'play':
        try: f.set_variation_by_axes([800])
        except Exception: pass
    return f
def flag(n): return FL.flag_surface(n, 900, 600)
def pill(img, xy, txt, bg, fg=(255, 255, 255), size=46, icon=None):
    f = F('SemiBold', size); tw = ImageDraw.Draw(Image.new('RGBA', (4, 4))).textlength(txt, font=f); pad = 70 if icon else 26
    im = Image.new('RGBA', (int(tw + pad + 26), int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], 12, fill=bg + (255,)); d.text((pad + tw / 2, im.height / 2), txt, font=f, fill=fg, anchor='mm')
    if icon:
        s = FL.flag_surface(icon, 54, 36); a = np.frombuffer(s.get_data(), np.uint8).reshape(36, 54, 4)[..., [2, 1, 0, 3]]; im.alpha_composite(Image.fromarray(a.copy()), (14, (im.height - 36) // 2))
    im = TO.sticker(im, ow=4); x = min(max(xy[0], im.width / 2 + 24), W - im.width / 2 - 24); img.alpha_composite(im, (int(x - im.width / 2), int(xy[1] - im.height / 2)))
def stext(img, xy, txt, f, fill=(255, 255, 255)):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.text((xy[0] + 3, xy[1] + 5), txt, font=f, fill=(0, 0, 0, 200), anchor='mm'); lay = lay.filter(ImageFilter.GaussianBlur(6))
    ImageDraw.Draw(lay).text(xy, txt, font=f, fill=fill + (255,), anchor='mm'); img.alpha_composite(lay)
def base(cam):
    return G.render(cam, W, H).filter(ImageFilter.UnsharpMask(radius=1.3, percent=45, threshold=2)).convert('RGBA')
def layer(): s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s); c.set_line_join(cairo.LINE_JOIN_ROUND); return s, c
KOR = (127.5, 37.5)
# ---------- still 1: hook - America, Canada (and Britain) rise up ----------
cam = G.Camera(-97, 43, 9500, 22, -4)
img = base(cam); s, c = layer()
R3.raised(c, cam, C50['Canada'].intersection(box(-141, 41, -52, 62)), 70, flag('Canada'), tol=0.06, min_area=0.3)
R3.raised(c, cam, USA48, 90, flag('United States of America'), tol=0.05, min_area=0.3)
for a0 in ((-120, 40), (-100, 52)): R3.arc3d(c, cam, a0, (-150, 40), 500, 0.55, (1, 0.85, 0.2), 10)
img.alpha_composite(TO._pil(s))
x, y = R3.raised_label_pos(cam, USA48, 95); pill(img, (x, y), 'USA', (25, 30, 45), size=52, icon='United States of America')
pill(img, (W // 2 + 120, 520), 'Canada', (25, 30, 45), size=52, icon='Canada')
pill(img, (W // 2, 1450), 'heading to Korea', (240, 175, 20), (20, 20, 20), 46)
stext(img, (W // 2, 230), 'Just imagine...', F('play', 92)); img.convert('RGB').save(f'{R}/stills/1_hook.png')
# ---------- still 2: Korea split, USSR vs USA ----------
cam = G.Camera(128.5, 36.5, 2500, 36, 8)
img = base(cam); s, c = layer()
R3.raised(c, cam, USSR, 30, flag('USSR'), tol=0.05, min_area=0.5)
R3.raised(c, cam, C50['North Korea'], 18, flag('North Korea'), tol=0.01)
R3.raised(c, cam, C50['South Korea'], 18, flag('South Korea'), tol=0.01, min_area=0.05)
x0, y0, z0, ok = R3.project_alt(cam, np.array([124.3, 129.5]), np.array([38.0, 38.0]), 19, W, H)
c.move_to(x0[0], y0[0]); c.line_to(x0[1], y0[1]); c.set_source_rgb(1, 0.85, 0.2); c.set_dash([20, 12]); c.set_line_width(7); c.stroke(); c.set_dash([])
img.alpha_composite(TO._pil(s))
x, y = R3.raised_label_pos(cam, C50['North Korea'], 20); pill(img, (x, y + 20), 'North Korea', (25, 30, 45), icon='North Korea')
x, y = R3.raised_label_pos(cam, C50['South Korea'], 20); pill(img, (x, y + 160), 'South Korea', (25, 30, 45), icon='South Korea')
pill(img, (820, 400), 'Soviet Union', (150, 20, 20), icon='USSR'); pill(img, (x0[1] + 60, y0[1] + 40), '38th parallel', (240, 175, 20), (20, 20, 20), 40)
stext(img, (W // 2, 230), 'Korea, 1945', F('play', 96)); img.convert('RGB').save(f'{R}/stills/2_split.png')
# ---------- still 3: invasion, Seoul falls, Pusan perimeter ----------
cam = G.Camera(127.7, 34.6, 900, 44, 6)
img = base(cam); s, c = layer()
NK, SK = C50['North Korea'], C50['South Korea']
occ = SK.intersection(Polygon([(124, 39), (131, 39), (131, 36.0), (129.3, 35.9), (128.6, 35.1), (127.8, 35.0), (126.0, 34.2), (124, 34.2)]))
pusan = SK.difference(occ)
R3.raised(c, cam, unary_union([NK, occ]), 10, flag('North Korea'), tol=0.008)
R3.raised(c, cam, pusan, 10, flag('South Korea'), tol=0.008, min_area=0.01)
for a, b in (((126.7, 38.4), (127.0, 36.0)), ((127.6, 38.3), (128.4, 36.2)), ((126.9, 37.6), (126.9, 35.4))): R3.arc3d(c, cam, a, b, 25, 1.0, (0.95, 0.85, 0.2), 12)
img.alpha_composite(TO._pil(s))
X, Y, Z, ok = R3.project_alt(cam, np.array([126.98, 129.04]), np.array([37.57, 35.18]), 12, W, H)
pill(img, (X[0] - 60, Y[0] - 60), 'Seoul: captured', (180, 25, 30), size=40); pill(img, (X[1] + 40, Y[1] + 120), 'Pusan Perimeter', (40, 80, 180), size=40, icon='South Korea')
stext(img, (W // 2, 230), 'June 25, 1950', F('play', 96)); img.convert('RGB').save(f'{R}/stills/3_invasion.png')
# ---------- still 4: China enters ----------
cam = G.Camera(123.5, 33.0, 2600, 36, -14)
img = base(cam); s, c = layer()
R3.raised(c, cam, C50['China'].intersection(box(73, 18, 135, 54)), 28, flag('China'), tol=0.05, min_area=0.5)
R3.raised(c, cam, NK, 22, flag('North Korea'), tol=0.01)
R3.raised(c, cam, SK, 22, flag('UN'), tol=0.01, min_area=0.05)
for a, b in (((124.5, 40.5), (126.5, 38.0)), ((125.6, 40.9), (127.6, 38.2)), ((126.6, 41.3), (128.7, 38.6))): R3.arc3d(c, cam, a, b, 60, 1.0, (0.95, 0.85, 0.2), 12)
img.alpha_composite(TO._pil(s))
pill(img, (300, 620), 'China', (180, 25, 30), icon='China'); x, y = R3.raised_label_pos(cam, SK, 22); pill(img, (x + 40, y + 170), 'UN forces', (40, 120, 200), icon='UN')
stext(img, (W // 2, 230), 'October 1950', F('play', 96)); img.convert('RGB').save(f'{R}/stills/4_china.png')
print('stills ok')
