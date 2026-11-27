"""Thorn removal, v2: clean 'real moment' edit, original sound kept. usage: VW=1080 VH=1920 python3 edit2.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont, ImageFilter
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json')); LINES = json.load(open(f'{ROOT}/vo/lines2.json'))
WHITE, INK, YEL = (255, 255, 255), (0, 0, 0), (255, 214, 60)
END = 32.2
TH0 = (0.35, 0.488); TH1 = (0.45, 0.50)
def V(t0, f, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=0.0, ss=k.pop('ss', 0.0), **k)
T = [V(0.0, 's1', zoom=(1.5, 1.25), c=TH0),                        # hook: tight on the thorn, slowly easing out
     V(3.9, 's1', ss=3.9, trans='zoom', zoom=(1.05, 1.15), c=(0.38, 0.5)),
     V(8.4, 's2', trans='zoom', zoom=(1.0, 1.1), c=(0.45, 0.5)),
     V(11.8, 's3', trans='zoom', zoom=(1.1, 1.12), c=(0.4, 0.5)),
     V(18.9, 's3', ss=7.1, trans='zoom', zoom=(1.3, 1.45), c=(0.42, 0.5)),   # punch-in when the tweezers take the tip
     V(23.4, 's4', trans='zoom', zoom=(1.15, 1.3), c=(0.42, 0.5)),
     V(28.2, 's5', trans='zoom', zoom=(1.25, 1.6), c=TH1),            # slow motion, pushing in
     Shot(31.2, ('img', 'real/last.png'), grade='none', grain=0.0, kb=((TH1[0], TH1[1], 1.6), (TH1[0], TH1[1], 1.75)))]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def emoji(img, ch, x, y, s):
    em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), ch, font=EMO, embedded_color=True)
    em = em.resize((s, s)); img.paste(em, (int(x - s / 2), int(y - s / 2)), em)
def soft_text(img, xy, txt, f, fill=WHITE, a=1.0, anchor='mm'):
    """text with a soft blurred shadow (no hard outline) - looks like native phone captions"""
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.text((xy[0] + 3, xy[1] + 4), txt, font=f, fill=(0, 0, 0, int(200 * a)), anchor=anchor)
    lay = lay.filter(ImageFilter.GaussianBlur(7)); ld = ImageDraw.Draw(lay)
    ld.text(xy, txt, font=f, fill=fill + (int(255 * a),), anchor=anchor)
    base = img.convert('RGBA'); base.alpha_composite(lay); return base.convert('RGB')
def post(img, t, fi, sh):
    # hook title, first 3.9 s
    if t < 3.9:
        a = min(eout(t / 0.25), eout((3.9 - t) / 0.3))
        img = soft_text(img, (W // 2, 300), "There's a thorn stuck deep", font('Bold', 70), a=a)
        if a > 0.5: emoji(img, '😬', W // 2, 410, 96)
        d = ImageDraw.Draw(img)   # thin ring on the thorn
        z = lerp(1.5, 1.25, ease(t / 3.9)); s = z
        vw, vh = W / z, H / z; x0 = clamp(TH0[0] * W - vw / 2, 0, W - vw); y0 = clamp(TH0[1] * H - vh / 2, 0, H - vh)
        x, y = (TH0[0] * W - x0) * z, (TH0[1] * H - y0) * z; r = 62 + 5 * math.sin(t * 7)
        if t > 0.4: d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=5)
    if 28.2 <= t < 31.2:
        img = soft_text(img, (W - 70, 120), 'slow-mo', font('SemiBold', 40), a=0.9, anchor='rm')
    if t >= 31.2:
        a = eout((t - 31.2) / 0.3)
        img = soft_text(img, (W // 2, 330), 'Almost out', font('Bold', 84), a=a); emoji(img, '🙌', W // 2, 450, 100)
        img = soft_text(img, (W // 2, 1650), 'Deep or painful? See a doctor.', font('Medium', 38), a=a)
    # subtitles: whole line, sentence case, soft shadow, active word slightly yellow
    for L in LINES:
        if L['t'] - 0.05 <= t < L['t'] + L['d'] + 0.25:
            ws = [w for w in WORDS if L['t'] - 0.6 <= w['s'] <= L['t'] + L['d'] + 0.2]
            f = font('Bold', 52); words = [w['w'] for w in ws]; lines, line = [], []
            for i, wd in enumerate(words):
                if f.getlength(' '.join([words[j] for j in line] + [wd])) > 880 and line: lines.append(line); line = [i]
                else: line.append(i)
            lines.append(line)
            lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); top = Image.new('RGBA', img.size, (0, 0, 0, 0)); td = ImageDraw.Draw(top)
            for li, ln in enumerate(lines):
                txt = ' '.join(words[j] for j in ln); x = W / 2 - f.getlength(txt) / 2; y = 1500 + li * 72
                for j in ln:
                    on = ws[j]['s'] - 0.02 <= t < ws[j]['e'] + 0.08
                    ld.text((x + 3, y + 4), words[j], font=f, fill=(0, 0, 0, 210), anchor='lm')
                    td.text((x, y), words[j], font=f, fill=YEL + (255,) if on else WHITE + (255,), anchor='lm'); x += f.getlength(words[j] + ' ')
            lay = lay.filter(ImageFilter.GaussianBlur(6)); lay.alpha_composite(top)
            b = img.convert('RGBA'); b.alpha_composite(lay); img = b.convert('RGB')
            break
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
