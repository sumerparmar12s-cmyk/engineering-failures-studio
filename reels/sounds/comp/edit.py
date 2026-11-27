"""Strangest sounds reel (1080x1920, 'audio lab' split template). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
from PIL import ImageFont
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json')); ENV = json.load(open(f'{ROOT}/work/env.json'))
CY, MG, YEL, WHITE, INK, ORG = (0, 240, 255), (255, 50, 200), (255, 225, 40), (255, 255, 255), (0, 0, 0), (255, 140, 30)
END = 24.2; TOP = 1150
NOAA = 'Video: NOAA Ocean Exploration · Audio: NOAA'; NASA_I = 'Video: NASA Operation IceBridge'; NOAA_S = 'Spectrogram & audio: NOAA'; JPL = 'Video & audio: NASA/JPL-Caltech'
def V(t0, f, cr, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=1.5, credit=cr, ss=k.pop('ss', 0.0), zoom=k.pop('zoom', (1.0, 1.0)), **k)
T = [V(0.0, 'ocean_a', NOAA), V(5.02, 'ocean_b', NOAA, trans='push'), V(8.90, 'ice_a', NASA_I, trans='flash'), V(10.80, 'ice_b', NASA_I, trans='whip'),
     Shot(12.16, ('img', 'media/upsweep_canvas.jpg'), grade='none', grain=1.5, credit=NOAA_S, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.0)), trans='glitch'),
     V(19.64, 'mars', JPL, trans='flash')]
PLAY = [(3.44, 5.24, 'THE BLOOP', '1997 · PACIFIC OCEAN', CY), (15.25, 17.15, 'THE UPSWEEP', 'SINCE 1991 · STILL UNSOLVED', MG), (21.84, END, 'WIND ON MARS', 'PERSEVERANCE ROVER · 2021', ORG)]
EMO = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
def emoji(img, ch, x, y, s):
    em = Image.new('RGBA', (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(em).text((10, 10), ch, font=EMO, embedded_color=True)
    em = em.resize((s, s)); img.paste(em, (int(x - s / 2), int(y - s / 2)), em)
def pop(d, txt, y, size, fill, t, t0, stroke=INK, f='bebas'):
    p = eout((t - t0) / 0.16); fo = font(f, int(size * lerp(1.35, 1.0, p)))
    d.text((W // 2, y), txt, font=fo, fill=fill, anchor='mm', stroke_width=10, stroke_fill=stroke)
def stamp(img, txt, t, t0, col, y, size=150, rot=-7):
    p = eout((t - t0) / 0.12); sc = lerp(1.8, 1.0, p); f = font('bebas', int(size * sc)); tw = f.getlength(txt)
    st = Image.new('RGBA', (int(tw + 80), int(size * sc * 1.25)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rectangle([6, 6, st.width - 6, st.height - 6], outline=col + (255,), width=12); sd.text((st.width / 2, st.height / 2 + 4), txt, font=f, fill=col + (255,), anchor='mm')
    st = st.rotate(rot, expand=True, resample=Image.BICUBIC); img.paste(st, (int(W / 2 - st.width / 2), int(y - st.height / 2)), st)
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    # lab panel
    for y in range(TOP, H, 8):
        k = (y - TOP) / (H - TOP); d.rectangle([0, y, W, y + 8], fill=(int(lerp(10, 4, k)), int(lerp(14, 6, k)), int(lerp(40, 18, k))))
    d.rectangle([0, TOP, W, TOP + 6], fill=CY)
    playing = next((p for p in PLAY if p[0] <= t < p[1]), None)
    col = playing[4] if playing else CY
    # waveform from the real mix
    i = min(len(ENV['seg']) - 1, fi); seg = (ENV['seg'][i] + [0.0] * 64)[:64]; e = ENV['env'][i]
    cy = TOP + 190; gain = 900 if playing else 520
    pts = []
    for j in range(64):
        x = 60 + j * (W - 120) / 63; amp = min(105, seg[j] * gain * (1 + 0.25 * math.sin(j * 0.7 + t * 9)))
        pts.append((x, cy - amp * (1 if j % 2 else -1)))
    d.line(pts, fill=col, width=6, joint='curve')
    for j in range(0, 64, 2):
        x = 60 + j * (W - 120) / 63; h = min(105, seg[j] * gain); d.line([(x, cy - h), (x, cy + h)], fill=col + (90,), width=3)
    lab = f'▶ NOW PLAYING' if playing else '● LISTENING'
    d.text((60, TOP + 40), lab.replace('▶', '>').replace('●', '•'), font=font('monob', 36), fill=col)
    d.text((W - 60, TOP + 40), f'{t:05.2f}s', font=font('monob', 36), fill=(150, 160, 200), anchor='ra')
    if playing:
        d.text((W // 2, TOP + 395), playing[2], font=font('bebas', 110), fill=col, anchor='mm')
        d.text((W // 2, TOP + 478), playing[3], font=font('oswald', 40), fill=WHITE, anchor='mm')
    # captions in panel when nothing plays
    if not playing:
        sent, cur = [], []
        for x in WORDS:
            cur.append(x)
            if x['w'][-1] in '.?' and not x['w'].endswith('...'): sent.append(cur); cur = []
        if cur: sent.append(cur)
        for s in sent:
            if s[0]['s'] - 0.05 <= t < s[-1]['e'] + 0.3:
                words = [x['w'].upper() for x in s]; f = font('bebas', 96); lines, line = [], []
                for k2, wd in enumerate(words):
                    if f.getlength(' '.join([words[j] for j in line] + [wd])) > 960 and line: lines.append(line); line = [k2]
                    else: line.append(k2)
                lines.append(line)
                for li, ln in enumerate(lines[:2]):
                    txt = ' '.join(words[j] for j in ln); x = W / 2 - f.getlength(txt) / 2; y = TOP + 360 + li * 100
                    for j in ln:
                        on = s[j]['s'] - 0.02 <= t
                        d.text((x, y), words[j], font=f, fill=YEL if on and t < s[j]['e'] + 0.12 else (WHITE if on else (110, 120, 150)), anchor='lm'); x += f.getlength(words[j] + ' ')
                break
    # beats over footage
    if t < 3.44:
        pop(d, 'TURN YOUR SOUND ON', 150, 96, WHITE, t, 0.0); emoji(img, '🔊', W // 2, 270, 110)
    if playing and playing[0] == 3.44:   # expanding rings = heard far away
        for r0 in range(3):
            r = ((t - 3.44) * 420 + r0 * 160) % 520; a = d.ellipse([W / 2 - r, 560 - r, W / 2 + r, 560 + r], outline=CY, width=6)
    if 5.24 <= t < 8.90:
        pop(d, '3,000+ MILES', 200, 150, CY, t, 5.32)
        if t >= 7.32: pop(d, 'A MONSTER?', 1000, 140, MG, t, 7.32, stroke=WHITE)
    if 8.90 <= t < 12.16:
        if t >= 9.08: stamp(img, 'IT WAS ICE', t, 9.08, WHITE, 230, size=150)
    if 12.16 <= t < 19.64:
        x = int(W * clamp((t - 12.16) / 7.48)); d.line([(x, 0), (x, TOP)], fill=WHITE, width=6)
        pop(d, 'SINCE 1991', 150, 120, YEL, t, 13.34)
        if t >= 17.15: stamp(img, 'UNSOLVED', t, 17.15, MG, 620, size=180, rot=6)
    if t >= 19.64:
        pop(d, 'THIS IS MARS', 160, 140, ORG, t, 20.86)
    cr = sh.k.get('credit')
    if cr: d.text((W // 2, TOP - 30), cr, font=font('SemiBold', 26), fill=WHITE, anchor='mm', stroke_width=3, stroke_fill=INK)
    d.rectangle([0, H - 14, int(W * t / END), H], fill=col)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
