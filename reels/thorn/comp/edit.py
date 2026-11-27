"""Thorn removal edit (1080x1920). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
LINES = json.load(open(f'{ROOT}/vo/lines.json'))
MINT, YEL, WHITE, INK, RED = (60, 230, 160), (255, 215, 50), (255, 255, 255), (0, 0, 0), (255, 70, 70)
END = 29.7
THORN0 = (0.35, 0.488); THORN1 = (0.45, 0.50)
def V(t0, f, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=0.0, ss=k.pop('ss', 0.0), **k)
T = [V(0.0, 'a', zoom=(1.45, 1.3), c=THORN0),
     V(2.4, 'a', ss=2.4, trans='zoom', zoom=(1.0, 1.08), c=(0.4, 0.5)),
     V(7.0, 'b', trans='whip', zoom=(1.05, 1.12), c=(0.45, 0.5)),
     V(13.33, 'c', trans='push', zoom=(1.08, 1.2), c=(0.4, 0.5)),
     V(25.5, 'd', trans='flash', zoom=(1.1, 1.35), c=THORN1),
     Shot(28.5, ('img', 'real/last.png'), grade='none', grain=0.0, kb=((THORN1[0], THORN1[1], 1.35), (THORN1[0], THORN1[1], 1.7)))]
STEPS = [(7.0, 13.33, 'STEP 1', 'PRESS GENTLY AROUND IT'), (13.33, 19.8, 'STEP 2', 'GRIP IT AT THE BASE'), (19.8, 25.5, 'STEP 3', 'PULL OUT SLOWLY')]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def emoji(img, ch, x, y, s):
    em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), ch, font=EMO, embedded_color=True)
    em = em.resize((s, s)); img.paste(em, (int(x - s / 2), int(y - s / 2)), em)
def screen_pt(cx, cy, z, px, py, w=1080, h=1920):   # where a source point lands after view()
    vw, vh = w / z, h / z; x0 = clamp(cx * w - vw / 2, 0, w - vw); y0 = clamp(cy * h - vh / 2, 0, h - vh)
    return (px * w - x0) * z, (py * h - y0) * z
def pill(d, txt, x, y, f, bg, fg, anchor='l'):
    tw = f.getlength(txt); x0 = x if anchor == 'l' else x - tw / 2 - 30
    d.rounded_rectangle([x0, y - f.size * 0.72, x0 + tw + 60, y + f.size * 0.72], int(f.size * 0.72), fill=bg)
    d.text((x0 + 30, y + 2), txt, font=f, fill=fg, anchor='lm'); return x0 + tw + 60
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    if t < 2.4:   # hook: circle the thorn
        z = lerp(1.45, 1.3, ease(t / 2.4)); x, y = screen_pt(*THORN0, z, *THORN0)
        r = 70 + 8 * math.sin(t * 10); d.ellipse([x - r, y - r, x + r, y + r], outline=YEL, width=9)
        d.line([(x + r * 0.7, y - r * 0.7), (x + 230, y - 260)], fill=YEL, width=9)
        p = eout(t / 0.2); f = font('oswald', int(108 * lerp(1.3, 1, p)))
        d.text((W // 2, 250), 'A THORN, STUCK DEEP', font=f, fill=WHITE, anchor='mm', stroke_width=10, stroke_fill=INK)
        emoji(img, '😬', W // 2, 400, 120)
    for a, b, s1, s2 in STEPS:
        if a <= t < b:
            p = eout((t - a) / 0.3); x = int(lerp(-500, 50, p))
            x2 = pill(d, s1, x, 230, font('oswald', 54), MINT, INK)
            pill(d, s2, x2 + 14, 230, font('oswald', 54), (15, 15, 18), WHITE)
    if 7.0 <= t < 13.33: pill(d, '1.8× SPEED', W - 300, 330, font('SemiBold', 34), (0, 0, 0), (220, 220, 220))
    if 25.5 <= t < 28.5:
        pill(d, 'SLOW MOTION', 50, 230, font('oswald', 54), YEL, INK)
        if t >= 25.8:
            p = eout((t - 25.8) / 0.18); f = font('oswald', int(120 * lerp(1.4, 1, p)))
            d.text((W // 2, 420), 'THERE IT IS', font=f, fill=YEL, anchor='mm', stroke_width=10, stroke_fill=INK); emoji(img, '✅', W // 2, 570, 110)
    if t >= 28.5:
        u = ease((t - 28.5) / 1.2); z = lerp(1.35, 1.7, u); x, y = screen_pt(*THORN1, z, *THORN1)
        r = 85; d.ellipse([x - r, y - r, x + r, y + r], outline=MINT, width=9)
        f = font('oswald', 110); d.text((W // 2, 300), 'ALMOST OUT!', font=f, fill=WHITE, anchor='mm', stroke_width=10, stroke_fill=INK); emoji(img, '🙌', W // 2, 450, 110)
        d.text((W // 2, 1700), 'Deep or painful? Please see a doctor.', font=font('SemiBold', 40), fill=WHITE, anchor='mm', stroke_width=4, stroke_fill=INK)
    # captions: current VO line in a white box, active word highlighted
    for L in LINES:
        if L['t'] - 0.05 <= t < L['t'] + L['d'] + 0.2 and t < 28.5:
            ws = [w for w in WORDS if L['t'] - 0.6 <= w['s'] <= L['t'] + L['d'] + 0.2]
            f = font('Bold', 54); words = [w['w'] for w in ws]; lines, line = [], []
            for i, wd in enumerate(words):
                if f.getlength(' '.join([words[j] for j in line] + [wd])) > 900 and line: lines.append(line); line = [i]
                else: line.append(i)
            lines.append(line); y0 = 1560
            for li, ln in enumerate(lines):
                txt = ' '.join(words[j] for j in ln); tw = f.getlength(txt); x = W / 2 - tw / 2; y = y0 + li * 82
                d.rounded_rectangle([x - 24, y - 40, x + tw + 24, y + 40], 18, fill=(255, 255, 255))
                for j in ln:
                    on = ws[j]['s'] - 0.02 <= t < ws[j]['e'] + 0.1
                    d.text((x, y + 2), words[j], font=f, fill=(20, 150, 100) if on else INK, anchor='lm'); x += f.getlength(words[j] + ' ')
            break
    d.rectangle([0, H - 12, int(W * t / END), H], fill=MINT)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
