"""NASA 'looks fake' reel (1080x1920, ~20 s). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
RED, GREEN, CYAN, WHITE = (255, 60, 60), (60, 230, 110), (90, 225, 255), (255, 255, 255)
END = 25.0
M = lambda n: f'media/{n}.jpg'
def S(word, near, tol=1.2):
    import re
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')
def P(t0, n, tag, kb, **k): return Shot(t0, ('img', M(n)), mode='portrait', grade='none', grain=2.0, src_tag=tag, kb=kb, **k)
def V(t0, f, tag, ss=0.0, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=2.0, src_tag=tag, ss=ss, zoom=k.pop('zoom', (1.0, 1.08)), **k)
def FAKE(at, until=None): return O.stamp('FAKE?', at, until=until, x=W // 2, y=430, rot=-6, color=RED, size=170)
def REAL(at): return O.stamp('REAL', at, x=W // 2, y=430, rot=4, color=GREEN, size=200)
NASA = 'Image: NASA/JPL'; NV = 'Video: NASA/JPL-Caltech · Perseverance rover'
T = [V(0.0, 'v_parachute', NV, ss=0.6, zoom=(1.15, 1.0)),
     V(1.48, 'v_skycrane', NV, ss=4.5, trans='flash', zoom=(1.0, 1.12)),
     P(4.38, 'PIA01141', 'Image: NASA (Viking 1, 1976)', ((0.51, 0.40, 1.0), (0.51, 0.36, 1.2)), trans='flash'),
     P(4.95, 'PIA02325c', NASA, ((0.5, 0.5, 1.05), (0.5, 0.5, 1.15)), trans='flash'),
     P(5.5, 'PIA19400', NASA + ' · Curiosity rover', ((0.5, 0.4, 1.05), (0.5, 0.4, 1.15)), trans='flash'),
     P(6.05, 'PIA11682', NASA + ' · Cassini', ((0.5, 0.45, 1.05), (0.5, 0.45, 1.15)), trans='flash'),
     V(6.68, 'v_descent', NV, ss=0.5, trans='zoom', zoom=(1.0, 1.25)),
     P(7.76, 'PIA01141', 'Image: NASA (Viking 1, 1976)', ((0.51, 0.40, 1.0), (0.51, 0.35, 2.1)), trans='zoom', ov=[FAKE(7.82, S('Real', 8.8)), REAL(S('Real', 8.8))]),
     P(13.12, 'PIA02325c', NASA, ((0.48, 0.5, 1.0), (0.48, 0.5, 1.35)), trans='whip', ov=[FAKE(13.16, S('real', 14.1)), REAL(S('real', 14.1))]),
     P(15.86, 'PIA19400', NASA + ' · Curiosity rover', ((0.5, 0.38, 1.0), (0.52, 0.38, 1.35)), trans='whip', ov=[FAKE(15.9, 16.6), REAL(16.6)]),
     P(18.96, 'PIA11682', NASA + ' · Cassini', ((0.5, 0.45, 1.0), (0.5, 0.45, 1.4)), trans='whip', ov=[FAKE(19.0, S('real', 20.9)), REAL(S('real', 20.9))]),
     V(22.44, 'v_descent', NV, ss=3.0, trans='flash', zoom=(1.0, 1.2))]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    if t < 1.48:
        d.text((W // 2, 330), "THIS ISN'T CGI", font=font('bebas', 150), fill=WHITE, anchor='mm', stroke_width=12, stroke_fill=(0, 0, 0))
        em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), '🤯', font=EMO, embedded_color=True)
        em = em.resize((150, 150)); img.paste(em, (W // 2 - 75, 440), em)
    elif t < 4.38:
        d.text((W // 2, 330), 'REAL VIDEO FROM MARS', font=font('bebas', 120), fill=(255, 200, 120), anchor='mm', stroke_width=10, stroke_fill=(0, 0, 0))
    elif t < 7.76:   # hook title
        f = font('bebas', 128); lines = ['THESE NASA PHOTOS', 'LOOK EVEN MORE FAKE']
        for i, l in enumerate(lines): d.text((W // 2, 300 + i * 130), l, font=f, fill=WHITE, anchor='mm', stroke_width=10, stroke_fill=(0, 0, 0))
        em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), '🤯', font=EMO, embedded_color=True)
        em = em.resize((150, 150)); img.paste(em, (W // 2 - 75, 540), em)
        if t > 6.68: d.text((W // 2, 760), "THEY'RE NOT.", font=font('bebas', 110), fill=GREEN, anchor='mm', stroke_width=8, stroke_fill=(0, 0, 0))
    # one-word captions (current word), lower third
    cur = None
    for w in WORDS:
        if w['s'] - 0.02 <= t <= w['e'] + 0.12: cur = w
    if cur and 7.76 <= t < END:
        txt = cur['w'].upper().strip('.,?')
        f = font('bebas', 150)
        d.text((W // 2, int(H * 0.80)), txt, font=f, fill=WHITE if txt not in ('REAL', 'FAKE') else (GREEN if txt == 'REAL' else RED), anchor='mm', stroke_width=12, stroke_fill=(0, 0, 0))
    d.rectangle([0, 0, int(W * t / END), 10], fill=CYAN)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
