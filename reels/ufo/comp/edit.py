"""Pentagon UFO files reel (1080x1920, 'declassified thermal' template). usage: VW=1080 VH=1920 python3 edit.py OUT.mp4 | frames PREFIX t..."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
RED, YEL, CY, WHITE, INK, LIME = (235, 40, 50), (255, 214, 0), (0, 230, 255), (255, 255, 255), (0, 0, 0), (120, 255, 90)
END = 23.6
NAVY = 'Video: U.S. Navy / Dept. of Defense'; DOD = 'Video: Dept. of Defense (UAP release, 2026)'; NASA = 'Photo: NASA (Pentagon UAP release, 2026)'
def V(t0, f, cr, **k): return Shot(t0, ('vid', f'real/{f}.mp4'), grade='none', grain=2.5, credit=cr, ss=k.pop('ss', 0.0), zoom=k.pop('zoom', (1.0, 1.08)), **k)
def P(t0, f, cr, kb, **k): return Shot(t0, ('img', f'media/{f}.jpg'), grade='none', grain=2.0, credit=cr, kb=kb, **k)
T = [V(0.0, 'gf_a', NAVY, zoom=(1.25, 1.0)),
     V(5.34, 'rel_jet', DOD, trans='glitch', zoom=(1.0, 1.15)),
     V(7.08, 'rel_orb', DOD, trans='glitch', zoom=(1.0, 1.12)),
     P(10.24, 'apollo12_vm1', NASA, ((0.5, 0.55, 1.0), (0.43, 0.24, 2.4)), trans='flash'),
     P(11.86, 'apollo17_vm6', NASA, ((0.55, 0.5, 1.0), (0.68, 0.22, 2.4)), trans='flash'),
     V(13.90, 'gf_b', NAVY, trans='glitch', zoom=(1.0, 1.18)),
     V(20.30, 'rel_sea', DOD, trans='glitch', zoom=(1.0, 1.1)),
     V(21.78, 'rel_end', DOD, trans='flash', zoom=(1.0, 1.12))]
LABEL = [(10.24, 11.86, 'APOLLO 12  ·  1969'), (11.86, 13.90, 'APOLLO 17  ·  1972')]
def box(d, x0, y0, x1, y1, fill): d.rectangle([x0, y0, x1, y1], fill=fill)
def pop(d, txt, y, size, fill, t, t0, f='oswald', stroke=INK):
    p = eout((t - t0) / 0.15); fo = font(f, int(size * lerp(1.35, 1.0, p)))
    d.text((W // 2, y), txt, font=fo, fill=fill, anchor='mm', stroke_width=10, stroke_fill=stroke)
def card(d, txt, val, y, t, t0, col):
    p = eout((t - t0) / 0.25); x = int(lerp(W + 40, 90, p))
    box(d, x, y, x + 900, y + 150, (0, 0, 0)); box(d, x, y, x + 14, y + 150, col)
    d.text((x + 44, y + 22), txt, font=font('monob', 40), fill=col)
    d.text((x + 44, y + 66), val, font=font('oswald', 70), fill=WHITE)
def stamp(img, txt, t, t0, col, y, size=150, rot=-8):
    p = eout((t - t0) / 0.12); sc = lerp(1.8, 1.0, p); f = font('oswald', int(size * sc)); tw = f.getlength(txt)
    st = Image.new('RGBA', (int(tw + 80), int(size * sc * 1.45)), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rectangle([6, 6, st.width - 6, st.height - 6], outline=col + (255,), width=12); sd.text((st.width / 2, st.height / 2), txt, font=f, fill=col + (255,), anchor='mm')
    st = st.rotate(rot, expand=True, resample=Image.BICUBIC); img.paste(st, (int(W / 2 - st.width / 2), int(y - st.height / 2)), st)
def post(img, t, fi, sh):
    d = ImageDraw.Draw(img)
    # top tape: declassified header with blinking REC
    box(d, 0, 0, W, 120, (12, 12, 14)); box(d, 0, 120, W, 128, RED)
    d.text((40, 60), 'DECLASSIFIED  //  UAP FILES', font=font('monob', 44), fill=WHITE, anchor='lm')
    if int(t * 2) % 2 == 0: d.ellipse([W - 190, 44, W - 158, 76], fill=RED)
    d.text((W - 145, 60), 'REC', font=font('monob', 40), fill=WHITE, anchor='lm')
    # hook + beats
    if t < 2.80: pop(d, 'A NAVY JET', 300, 150, WHITE, t, 0.0); pop(d, 'FILMED THIS', 455, 150, YEL, t, 0.25)
    elif t < 5.34:
        pop(d, 'WATCH THE OBJECT', 300, 120, YEL, t, 2.80)
        r = 120 + 12 * math.sin(t * 9); d.ellipse([W / 2 - r, 960 - r, W / 2 + r, 960 + r], outline=RED, width=10)
    if 5.34 <= t < 10.24:
        pop(d, 'PENTAGON', 300, 120, WHITE, t, 5.34); pop(d, 'UFO FILES · 2026', 430, 96, CY, t, 5.5)
        if t >= 7.32: stamp(img, 'RELEASED', t, 7.32, RED, 1180)
    for a, b, lab in LABEL:
        if a <= t < b:
            p = eout((t - a) / 0.3); f = font('oswald', 78); tw = f.getlength(lab); x = int(lerp(-tw - 60, 60, p))
            box(d, x - 20, 230, x + tw + 30, 340, YEL); d.text((x + 5, 285), lab, font=f, fill=INK, anchor='lm')
    if 13.90 <= t < 20.30:
        if t < 15.54: pop(d, 'PLOT TWIST', 300, 150, RED, t, 13.90, stroke=WHITE)
        else:
            card(d, 'NASA: ALTITUDE', '~13,000 FT UP', 260, t, 15.54, CY)
            if t >= 16.98: card(d, 'NASA: SPEED', '~40 MPH  (THE WIND)', 440, t, 16.98, LIME)
        if t >= 19.30: stamp(img, 'ILLUSION', t, 19.30, YEL, 1120, size=170, rot=6)
    if t >= 20.30:
        pop(d, 'THE REST?', 300, 150, WHITE, t, 20.30)
        if t >= 21.78: pop(d, 'YOU DECIDE.', 460, 150, YEL, t, 21.78)
    # typewriter captions: current sentence typed word by word in mono, black boxes
    sent, cur = [], []
    for w in WORDS:
        cur.append(w)
        if w['w'][-1] in '.?:' and w['w'] != 'U.S.': sent.append(cur); cur = []
    if cur: sent.append(cur)
    for s in sent:
        if s[0]['s'] - 0.05 <= t < s[-1]['e'] + 0.3:
            shown = [w['w'].upper() for w in s if w['s'] - 0.02 <= t]
            f = font('monob', 62); lines, line = [], ''
            for w in shown:
                if f.getlength(line + ' ' + w) > 920 and line: lines.append(line); line = w
                else: line = (line + ' ' + w).strip()
            lines.append(line); y = 1560
            for i, l in enumerate(lines[-3:]):
                tw = f.getlength(l); box(d, W / 2 - tw / 2 - 18, y + i * 86 - 40, W / 2 + tw / 2 + 18, y + i * 86 + 40, (0, 0, 0))
                d.text((W / 2, y + i * 86), l, font=f, fill=WHITE if i < len(lines[-3:]) - 1 else YEL, anchor='mm')
            break
    cr = sh.k.get('credit')
    if cr: d.text((W // 2, 1872), cr, font=font('SemiBold', 26), fill=WHITE, anchor='mm', stroke_width=3, stroke_fill=INK)
    box(d, 0, 1904, int(W * t / END), 1920, RED)
    return img
if __name__ == '__main__':
    if sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]): render(T, END, f'{sys.argv[2]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=post)
    else:
        render(T, END, sys.argv[1], 0, END, log=True, post=post)
