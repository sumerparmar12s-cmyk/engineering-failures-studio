"""Deep-sea 'looks fake' reel (1080x1920, colourful depth template). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
CY, PK, LIME, WHITE, INK, NAVY = (40, 230, 255), (255, 70, 160), (170, 255, 60), (255, 255, 255), (0, 0, 0), (8, 20, 60)
END = 23.0
CR = 'Video: NOAA Ocean Exploration'
def V(t0, f, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=1.5, ss=k.pop('ss', 0.0), zoom=k.pop('zoom', (1.0, 1.08)), **k)
T = [V(0.0, 'glass_front', zoom=(1.2, 1.0)),
     V(5.18, 'glass_side', trans='zoom', zoom=(1.0, 1.12)),
     V(8.60, 'dumbo_red', trans='whip', zoom=(1.05, 1.15)),
     V(12.52, 'casper_wide', trans='flash', zoom=(1.0, 1.12)),
     V(16.92, 'casper_close', trans='zoom', zoom=(1.0, 1.1)),
     V(19.86, 'dumbo_blob', trans='flash', zoom=(1.0, 1.15))]
# (start, end, depth_ft, name, place, colour)
SEG = [(1.80, 8.60, 2300, 'GLASS SQUID', 'ALASKA', CY), (8.60, 12.52, 2950, 'DUMBO OCTOPUS', 'NORTH CAROLINA', PK),
       (12.52, 19.86, 14000, 'GHOST OCTOPUS', 'HAWAII', LIME), (19.86, END, 3940, 'DUMBO OCTOPUS', 'FLORIDA KEYS', (255, 170, 40))]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def emoji(img, ch, x, y, s):
    em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), ch, font=EMO, embedded_color=True)
    em = em.resize((s, s)); img.paste(em, (int(x - s / 2), int(y - s / 2)), em)
def chunks():
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        if len(cur) == 3 or w['w'][-1] in '.,?': out.append(cur); cur = []
    if cur: out.append(cur)
    return out
CH = chunks()
def pop(d, txt, y, size, fill, t, t0, stroke=INK):
    p = eout((t - t0) / 0.16); f = font('bebas', int(size * lerp(1.4, 1.0, p)))
    d.text((W // 2, y), txt, font=f, fill=fill, anchor='mm', stroke_width=12, stroke_fill=stroke)
def gauge(img, d, t, depth, col, t0):
    # vertical depth bar on the right: gradient cyan -> navy -> violet, marker eases to depth (log scale)
    x0, y0, y1 = W - 70, 330, 1500
    for i in range(y0, y1, 6):
        k = (i - y0) / (y1 - y0); c = tuple(int(lerp(a, b, k)) for a, b in zip((60, 220, 255), (90, 20, 160)))
        d.rectangle([x0, i, x0 + 16, i + 5], fill=c)
    import math
    tgt = math.log10(depth) / math.log10(16000); prev = getattr(gauge, 'prev', tgt)
    k = eout((t - t0) / 0.8); v = lerp(prev if t - t0 < 0.8 else tgt, tgt, k) if t - t0 < 0.8 else tgt
    y = int(y0 + (y1 - y0) * clamp((v - 0.6) / 0.4))
    shown = int(depth * clamp(k * 1.05))
    d.polygon([(x0 - 6, y), (x0 - 30, y - 16), (x0 - 30, y + 16)], fill=col)
    txt = f'{shown:,} FT'; f = font('bebas', 64)
    tw = f.getlength(txt); d.rounded_rectangle([x0 - 52 - tw - 24, y - 40, x0 - 40, y + 40], 18, fill=col)
    d.text((x0 - 52 - tw / 2 - 12, y + 2), txt, font=f, fill=INK, anchor='mm')
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    if t < 1.80:
        pop(d, 'THIS IS REAL', 200, 170, WHITE, t, 0.0); emoji(img, '👀', W // 2, 330, 120)
    elif t < 5.18:
        pop(d, 'YOU CAN SEE', 150, 140, CY, t, 1.80); pop(d, 'THROUGH IT', 280, 140, CY, t, 1.80)
    if t >= 19.86:
        pop(d, "EARTH'S REAL ALIENS", 190, 140, (255, 170, 40), t, 19.86); emoji(img, '👽', W // 2, 330, 120)
    for a, b, dep, name, place, col in SEG:
        if a <= t < b:
            gauge(img, d, t, dep, col, a)
            if t >= 5.18 or a > 2:
                p = eout((t - a) / 0.3); f = font('bebas', 84); tw = f.getlength(name); x = int(lerp(-tw - 80, 50, p)); y = 1450
                d.rounded_rectangle([x - 10, y - 50, x + tw + 30, y + 48], 22, fill=col); d.text((x + 10, y + 2), name, font=f, fill=INK, anchor='lm')
                d.text((x + 6, y + 72), '📍 ' + place if False else place, font=font('oswald', 40), fill=WHITE, stroke_width=4, stroke_fill=INK, anchor='lm')
    for c in CH:
        if c[0]['s'] - 0.05 <= t < (c[-1]['e'] + 0.25) and t < 19.86:
            f = font('bebas', 112); words = [x['w'].upper() for x in c]; gap = 24
            ws = [f.getlength(x) for x in words]; x = W // 2 - (sum(ws) + gap * (len(ws) - 1)) / 2; y = 1700
            for w, wd, x_ in zip(c, ws, words):
                on = w['s'] - 0.03 <= t
                if on and t < w['e'] + 0.15:
                    d.rounded_rectangle([x - 12, y - 64, x + wd + 12, y + 56], 16, fill=CY); d.text((x, y), x_, font=f, fill=INK, anchor='lm')
                else:
                    d.text((x, y), x_, font=f, fill=WHITE if on else (190, 200, 210), anchor='lm', stroke_width=8, stroke_fill=INK)
                x += wd + gap
            break
    if t >= 19.86:   # end caption
        f = font('bebas', 112); d.text((W // 2, 1700), 'LIVE DOWN HERE.', font=f, fill=WHITE, anchor='mm', stroke_width=8, stroke_fill=INK)
    d.text((W // 2, 1845), CR, font=font('SemiBold', 26), fill=(235, 240, 245), anchor='mm', stroke_width=3, stroke_fill=INK)
    # gradient progress bar
    n = int(W * t / END)
    for x in range(0, n, 8):
        k = x / W; c = tuple(int(lerp(a, b, k)) for a, b in zip(CY, PK)); d.rectangle([x, 1886, x + 7, 1898], fill=c)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
