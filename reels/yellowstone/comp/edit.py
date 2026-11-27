"""Yellowstone explosions reel (1080x1920, 'alert window' template). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
OR, RED, TEAL, WHITE, INK, GRN = (255, 128, 20), (230, 35, 45), (0, 200, 190), (255, 255, 255), (0, 0, 0), (60, 220, 100)
END = 24.0
USGS = 'Video: USGS webcam'; NPS = 'Video: National Park Service'; NASA = 'Photo: NASA (Space Shuttle, 1994)'
def V(t0, f, cr, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=1.5, credit=cr, ss=k.pop('ss', 0.0), zoom=k.pop('zoom', (1.0, 1.05)), **k)
T = [V(0.0, 'blast', USGS, zoom=(1.0, 1.12)),
     V(7.64, 'newpool', USGS, trans='whip', zoom=(1.0, 1.08)),
     Shot(13.32, ('img', 'media/sts068_yellowstone.jpg'), grade='none', grain=1.5, credit=NASA, kb=((0.5, 0.5, 1.0), (0.5, 0.48, 1.35)), trans='flash'),
     V(15.72, 'fumaroles', NPS, trans='zoom', zoom=(1.0, 1.1)),
     V(18.34, 'grand', NPS, trans='whip', zoom=(1.0, 1.08))]
CHIP = [(0.0, 7.64, 'USGS WEBCAM · MAY 31, 2025'), (7.64, 13.32, 'USGS WEBCAM · JUNE 18, 2026'), (15.72, 18.34, 'NORRIS GEYSER BASIN'), (18.34, END, 'GRAND GEYSER')]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def emoji(img, ch, x, y, s):
    em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), ch, font=EMO, embedded_color=True)
    em = em.resize((s, s)); img.paste(em, (int(x - s / 2), int(y - s / 2)), em)
def pop(d, txt, x, y, size, fill, t, t0, anchor='mm', stroke=INK):
    p = eout((t - t0) / 0.16); f = font('oswald', int(size * lerp(1.35, 1.0, p)))
    d.text((x, y), txt, font=f, fill=fill, anchor=anchor, stroke_width=9, stroke_fill=stroke)
def chip(d, txt, x, y, bg, fg=INK, size=40):
    f = font('oswald', size); tw = f.getlength(txt); d.rounded_rectangle([x, y - size * 0.75, x + tw + 40, y + size * 0.75], int(size * 0.75), fill=bg)
    d.text((x + 20, y + 2), txt, font=f, fill=fg, anchor='lm'); return tw + 40
TICK = 'YELLOWSTONE CALDERA ≈ 30 × 45 MILES   •   HYDROTHERMAL EXPLOSIONS CAN HAPPEN WITH LITTLE OR NO WARNING   •   SOURCE: USGS   •   '
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    # top bar
    w = chip(d, 'YELLOWSTONE, WYOMING', 40, 84, OR, size=46)
    if int(t * 2.5) % 2 == 0 or t > 13.3: chip(d, 'REAL FOOTAGE', 40 + w + 20, 84, RED, WHITE, 46)
    else: chip(d, 'REAL FOOTAGE', 40 + w + 20, 84, (120, 15, 20), WHITE, 46)
    # hook / beats (above window, y 150-320)
    if t < 3.44: pop(d, 'IT EXPLODED', W // 2 - 50, 240, 130, WHITE, t, 1.5 if t >= 1.5 else 0.0); emoji(img, '💥', 930, 236, 110)
    elif t < 7.64: pop(d, 'TOURISTS RAN', W // 2, 240, 120, OR, t, 5.0 if t >= 5.0 else 3.44)
    elif t < 13.32: pop(d, 'A NEW POOL APPEARED', W // 2, 240, 104, TEAL, t, 11.44 if t >= 11.44 else 7.64)
    elif t < 18.34:
        pop(d, 'A VOLCANO UNDERNEATH', W // 2, 240, 100, WHITE, t, 13.84)
        if t >= 14.80: pop(d, '30 × 45 MILES', W // 2, 1000, 170, OR, t, 14.80)
    else:
        pop(d, 'SUPER-ERUPTION?', W // 2, 220, 96, WHITE, t, 18.34)
        if t >= 19.84: chip(d, 'NOT SOON', 300, 330, GRN, INK, 52)
        if t >= 21.18: pop(d, 'STEAM: ANY TIME', W // 2, 1000, 130, RED, t, 21.18, stroke=WHITE)
    for a, b, txt in CHIP:
        if a <= t < b: chip(d, txt, 70, 390, (0, 0, 0), WHITE, 34)
    cr = sh.k.get('credit')
    if cr: d.text((80, 1540), cr, font=font('SemiBold', 26), fill=WHITE, anchor='lm', stroke_width=3, stroke_fill=INK)
    # karaoke captions under window: line of current sentence, spoken words orange
    sent, cur = [], []
    for x in WORDS:
        cur.append(x)
        if x['w'][-1] in '.?' and not x['w'].endswith('...'): sent.append(cur); cur = []
    if cur: sent.append(cur)
    for s in sent:
        if s[0]['s'] - 0.05 <= t < s[-1]['e'] + 0.3:
            words = [x['w'].upper() for x in s]; f = font('oswald', 64); lines, line = [], []
            for i, wd in enumerate(words):
                if f.getlength(' '.join([words[j] for j in line] + [wd])) > 980 and line: lines.append(line); line = [i]
                else: line.append(i)
            lines.append(line)
            for li, ln in enumerate(lines[:2]):
                txt = ' '.join(words[j] for j in ln); x = W / 2 - f.getlength(txt) / 2; y = 1660 + li * 84
                for j in ln:
                    on = s[j]['s'] - 0.02 <= t
                    d.text((x, y), words[j], font=f, fill=OR if on else WHITE, anchor='lm', stroke_width=6, stroke_fill=INK); x += f.getlength(words[j] + ' ')
            break
    # ticker
    d.rectangle([0, 1838, W, 1900], fill=(15, 15, 18)); d.rectangle([0, 1838, 170, 1900], fill=RED)
    d.text((85, 1869), 'ALERT', font=font('oswald', 38), fill=WHITE, anchor='mm')
    f = font('oswald', 34); L = f.getlength(TICK); off = (t * 220) % L
    lay = Image.new('RGB', (W - 170, 62), (15, 15, 18)); ld = ImageDraw.Draw(lay)
    for k in range(3): ld.text((-off + k * L, 31), TICK, font=f, fill=(240, 240, 240), anchor='lm')
    img.paste(lay, (170, 1838))
    d.rectangle([0, 1900, int(W * t / END), 1920], fill=OR)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
