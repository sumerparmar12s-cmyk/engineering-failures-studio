"""'Real footage that looks fake' Earth reel (1080x1920). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
YEL, RED, GREEN, WHITE, INK = (255, 208, 40), (255, 60, 50), (70, 230, 110), (255, 255, 255), (0, 0, 0)
END = 28.8
TAC = 'Film: Barney Elliott, 1940 · public domain'; NAV = 'Film: U.S. Army / National Archives'; USGS = 'Video: USGS'
def V(t0, f, tag, ss=0.0, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=3.0, credit=tag, ss=ss, zoom=k.pop('zoom', (1.0, 1.08)), **k)
T = [V(0.0, 't_center', TAC, ss=0.0, zoom=(1.18, 1.0)),
     V(1.90, 't_road', TAC, ss=1.0, trans='flash', zoom=(1.0, 1.1)),
     V(3.72, 't_side', TAC, ss=0.5, trans='whip'),
     V(6.32, 't_tilt', TAC, ss=0.0, trans='push', zoom=(1.05, 1.15)),
     V(8.42, 't_fall', TAC, ss=1.8, trans='flash', zoom=(1.0, 1.12)),
     V(12.92, 'n_b29', NAV, ss=0.0, trans='whip'),
     V(14.48, 'n_cloud', NAV, ss=1.0, trans='flash', zoom=(1.0, 1.28)),
     V(20.38, 'l_all', USGS, ss=6.0, trans='whip'),
     V(21.96, 'l_all', USGS, ss=18.0, trans='flash', zoom=(1.0, 1.12)),
     V(24.70, 'l_all', USGS, ss=27.0, trans='zoom', zoom=(1.0, 1.15)),
     V(26.36, 'n_cloud', NAV, ss=12.0, trans='flash'),
     V(26.92, 't_fall', TAC, ss=2.0, trans='flash', zoom=(1.0, 1.1), ov=[O.stamp('REAL', 27.0, x=W // 2, y=1180, rot=-5, color=GREEN, size=210)])]
FILES = [(3.72, 12.92, '01', '1940', 'WASHINGTON STATE, USA'), (12.92, 20.38, '02', '1946', 'BIKINI ATOLL, PACIFIC'), (20.38, 26.36, '03', '2018', 'HAWAII, USA')]
def chunks():
    out, cur = [], []
    for w in WORDS:
        cur.append(w)
        if len(cur) == 3 or w['w'][-1] in '.,?': out.append(cur); cur = []
    if cur: out.append(cur)
    return out
CH = chunks()
def big(d, txt, y, size, fill, t, t0):
    p = eout((t - t0) / 0.18); f = font('bebas', int(size * lerp(1.35, 1.0, p)))
    d.text((W // 2, y), txt, font=f, fill=fill, anchor='mm', stroke_width=12, stroke_fill=INK)
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    # hook
    if t < 1.90: big(d, 'THIS IS STEEL.', 190, 175, WHITE, t, 0.0)
    elif t < 3.72: big(d, 'WATCH THE WIND', 190, 165, YEL, t, 1.90)
    # case-file header
    for a, b, no, yr, loc in FILES:
        if a <= t < b:
            p = eout((t - a) / 0.3)
            d.text((60, 70), f'REAL FOOTAGE  ·  FILE {no}/03', font=font('monob', 34), fill=WHITE, stroke_width=3, stroke_fill=INK)
            f = font('bebas', 170); x = int(lerp(-300, 60, p))
            d.text((x, 105), yr, font=f, fill=YEL, stroke_width=8, stroke_fill=INK)
            d.text((x + int(f.getlength(yr)) + 26, 165), loc, font=font('oswald', 46), fill=WHITE, stroke_width=4, stroke_fill=INK)
    if 17.70 <= t < 18.55: big(d, 'ON PURPOSE.', 960, 200, RED, t, 17.70)
    if t >= 26.36: big(d, 'NONE OF THIS IS FAKE', 200, 140, WHITE, t, 26.36)
    # captions: 3-word chunks, active word on yellow box
    for c in CH:
        if c[0]['s'] - 0.05 <= t < (c[-1]['e'] + 0.25) and t < 26.36:
            f = font('bebas', 118); words = [x['w'].upper() for x in c]; gap = 26
            ws = [f.getlength(x) for x in words]; x = W // 2 - (sum(ws) + gap * (len(ws) - 1)) / 2; y = 1660
            for w, wd, x_ in zip(c, ws, words):
                on = w['s'] - 0.03 <= t
                if on and t < w['e'] + 0.15:
                    d.rounded_rectangle([x - 12, y - 66, x + wd + 12, y + 58], 14, fill=YEL); d.text((x, y), x_, font=f, fill=INK, anchor='lm')
                else:
                    d.text((x, y), x_, font=f, fill=WHITE if on else (200, 200, 200), anchor='lm', stroke_width=8, stroke_fill=INK)
                x += wd + gap
            break
    # 3-segment progress
    for i, (a, b, *_ ) in enumerate([(0, 12.92), (12.92, 20.38), (20.38, END)]):
        x0 = 40 + i * 340; d.rectangle([x0, 1872, x0 + 320, 1882], fill=(255, 255, 255))
        d.rectangle([x0, 1872, x0 + int(320 * clamp((t - a) / (b - a))), 1882], fill=YEL)
    cr = sh.k.get('credit')
    if cr: d.text((W // 2, 1838), cr, font=font('SemiBold', 26), fill=(235, 235, 235), anchor='mm', stroke_width=3, stroke_fill=INK)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
