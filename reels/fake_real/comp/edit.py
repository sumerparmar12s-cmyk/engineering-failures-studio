"""NASA 'looks fake' reel (1080x1920, ~20 s). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
RED, GREEN, CYAN, WHITE = (255, 60, 60), (60, 230, 110), (90, 225, 255), (255, 255, 255)
END = 20.6
M = lambda n: f'media/{n}.jpg'
def P(t0, n, tag, kb, **k): return Shot(t0, ('img', M(n)), mode='portrait', grade='none', grain=2.0, src_tag=tag, kb=kb, **k)
def FAKE(at, until=None): return O.stamp('FAKE?', at, until=until, x=W // 2, y=430, rot=-6, color=RED, size=170)
def REAL(at): return O.stamp('REAL', at, x=W // 2, y=430, rot=4, color=GREEN, size=200)
NASA = 'Image: NASA/JPL'
T = [P(0.0, 'PIA01141', 'Image: NASA (Viking 1, 1976)', ((0.51, 0.40, 1.0), (0.51, 0.36, 1.25))),
     P(0.7, 'PIA02325c', NASA, ((0.5, 0.5, 1.1), (0.5, 0.5, 1.2)), trans='flash'),
     P(1.4, 'PIA19400', NASA + ' · Curiosity rover', ((0.5, 0.4, 1.1), (0.5, 0.4, 1.2)), trans='flash'),
     P(2.1, 'PIA11682', NASA + ' · Cassini', ((0.5, 0.45, 1.1), (0.5, 0.45, 1.2)), trans='flash'),
     P(2.78, 'PIA01141', 'Image: NASA (Viking 1, 1976)', ((0.51, 0.40, 1.0), (0.51, 0.35, 2.1)), trans='zoom', ov=[FAKE(2.85, 3.82), REAL(3.82)]),
     P(8.30, 'PIA02325c', NASA, ((0.48, 0.5, 1.0), (0.48, 0.5, 1.35)), trans='whip', ov=[FAKE(8.36, 9.30), REAL(9.30)]),
     P(11.12, 'PIA19400', NASA + ' · Curiosity rover', ((0.5, 0.38, 1.0), (0.52, 0.38, 1.35)), trans='whip', ov=[FAKE(11.18, 11.86), REAL(11.86)]),
     P(14.32, 'PIA11682', NASA + ' · Cassini', ((0.5, 0.45, 1.0), (0.5, 0.45, 1.4)), trans='whip', ov=[FAKE(14.40, 16.12), REAL(16.12)]),
     P(18.90, 'PIA11682', NASA + ' · Cassini', ((0.5, 0.45, 1.4), (0.5, 0.45, 1.55)), ov=[O.dark(18.9, amount=0.45)])]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    if t < 2.78:   # hook title
        f = font('bebas', 128); lines = ['THESE NASA PHOTOS', 'LOOK FAKE...']
        for i, l in enumerate(lines): d.text((W // 2, 300 + i * 130), l, font=f, fill=WHITE, anchor='mm', stroke_width=10, stroke_fill=(0, 0, 0))
        em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), '🤯', font=EMO, embedded_color=True)
        em = em.resize((150, 150)); img.paste(em, (W // 2 - 75, 540), em)
        if t > 1.6: d.text((W // 2, 760), "THEY'RE NOT.", font=font('bebas', 110), fill=GREEN, anchor='mm', stroke_width=8, stroke_fill=(0, 0, 0))
    if t >= 18.9:
        d.text((W // 2, 760), 'FOLLOW FOR MORE', font=font('bebas', 130), fill=CYAN, anchor='mm', stroke_width=10, stroke_fill=(0, 0, 0))
    # one-word captions (current word), lower third
    cur = None
    for w in WORDS:
        if w['s'] - 0.02 <= t <= w['e'] + 0.12: cur = w
    if cur and 2.78 <= t < 18.9:
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
