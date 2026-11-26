"""Titan Shorts series (1080x1920), Part 1/2/3. usage: VW=1080 VH=1920 python3 shorts_edit.py N OUT.mp4"""
import sys, os, json, re
assert os.environ.get('VW') == '1080', 'run with VW=1080 VH=1920'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import fx3, fx4
from fx4 import CYAN, AMBER, WHITE, GREY, RED
N = int(sys.argv[1]); SD = f'{ROOT}/shorts/s{N}'
WORDS = json.load(open(f'{SD}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')
def ex(p): return os.path.exists(f'{ROOT}/{p}')
R = 'real/'
ANIF, TAIL, AFT, SALV, LIFT = R + 'CG_001_1_TITAN_Animation_20240915_v2.2.mp4', R + '04_ROV_Titan_Submersible_Tail_Cone.mp4', \
    R + '07_ROV_Titan_Submersible_Aft_Dome_Aft_Ring_Hull_Remnants.mp4', R + 'DOD_110579329.mp4', R + 'DOD_110579650.mp4'
NOAA, PRESS, TIT = R + 'DOD_110804017.mp4', R + 'DOD_109728593.mp4', R + 'titanic_1912_footage.mp4'
MBI = 'USCG MBI report'; OGM = 'OceanGate photo · via USCG MBI report'; ROV = 'ROV footage · USCG / Pelagic Research Services'; CGA = 'U.S. Coast Guard animation'
RUSH = 'media/Stockton_Rush.png' if ex('media/Stockton_Rush.png') else 'docs/img/p16-001.png'
RUSH_TAG = 'Photo: OceanGate (CC BY 3.0)' if ex('media/Stockton_Rush.png') else OGM
def V(t0, path, tag, ss=0.0, g='abyss', **k): return Shot(t0, ('vid', path), grade=g, src_tag=tag, ss=ss, **k)
def ANI(t0, ss, **k): return Shot(t0, ('vid', ANIF), grade='none', src_tag=CGA, ss=ss, nohud=True, zoom=k.pop('zoom', (1.0, 1.06)), **k)
def IMG(t0, path, tag, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), g='abyss', **k): return Shot(t0, ('img', path), grade=g, src_tag=tag, kb=kb, **k)
def DOC(t0, key, kb=((0.5, 0.45, 1.0), (0.5, 0.45, 1.08)), **k): return Shot(t0, ('img', f'media/doc/{key}.png'), mode='portrait', kb=kb, grade='paper', grain=3.0, src_tag=MBI, **k)
def X(**k): return k
def STAT(at, v0, v1, unit, fmt='{:,.0f}', dur=1.0, y=600): return X(k='stat', at=at, v0=v0, v1=v1, unit=unit, fmt=fmt, dur=dur, y=y, size=190)
def LAB(text, at, col=WHITE, y=470, size=56): return O.label(text, W // 2, y, at, anchor='mm', color=col, size=size)
def STAMP(text, at, size=96): return O.stamp(text, at, x=W // 2, y=560, size=size)
def DARK(at, a=0.45): return O.dark(at, amount=a)
def CHAT(msgs, keep=2): return X(k='chat', at=msgs[0][0], msgs=msgs, keep=keep, box=(50, 820, W - 100))

if N == 1:   # PART 1 · THE WARNING (2018-2019)
    END = 77.4; TITLE = 'PART 1 / 3  ·  THE WARNING'
    T = [V(0.0, AFT, ROV, ss=24.0, zoom=(1.3, 1.1), ov=[LAB('FIVE YEARS BEFORE IT IMPLODED...', 0.2, AMBER, size=52)]),
         DOC(5.22, 'fired', trans='glitch', ov=[STAMP('FIRED', 5.4)]),
         ANI(7.1, 147.0, zoom=(1.3, 1.5), ov=[LAB('THE TITAN STORY', 7.3, CYAN, size=64)]),
         IMG(9.86, 'docs/img/p101-000.png', 'Photo: ' + MBI, g='flashback', ov=[LAB('JANUARY 2018', 10.0, AMBER, size=80)]),
         IMG(11.86, 'docs/img/p142-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.6, 0.5, 1.0), (0.6, 0.5, 1.2)), ov=[LAB('DIRECTOR OF MARINE OPERATIONS', 12.2, WHITE, size=46)]),
         IMG(16.5, 'docs/img/p16-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.35, 0.5, 1.0), (0.45, 0.5, 1.15))),
         DOC(21.12, '26', trans='push', ov=[STAT(21.4, 0, 26, 'problems listed', dur=0.8, y=420)]),
         DOC(23.92, '26', kb=((0.5, 0.45, 1.05), (0.5, 0.45, 1.15)), ov=[LAB('"SHOULD NOT BE USED"', 24.2, RED, y=420, size=60)]),
         IMG(27.48, RUSH, RUSH_TAG, g='flashback', ov=[LAB('STOCKTON RUSH · CEO', 27.7, CYAN, size=52)]),
         IMG(31.18, RUSH, RUSH_TAG, g='flashback', kb=((0.5, 0.4, 1.2), (0.5, 0.4, 1.35)), ov=[LAB('2 HOURS', 31.2, AMBER, size=90)]),
         DOC(34.92, 'fired', trans='glitch', kb=((0.5, 0.45, 1.05), (0.5, 0.45, 1.15)), ov=[STAMP('FIRED', 35.1)]),
         DOC(37.56, 'lawsuit', trans='push'),
         DOC(41.70, 'osha', ov=[LAB('NEVER REACHED THE RIGHT PERSON', 44.5, RED, y=420, size=46)]),
         DOC(46.74, 'withdrew'),
         DOC(49.48, 'letter', trans='push', ov=[STAT(50.4, 0, 20, 'experts signed · and more', dur=0.8, y=420)]),
         IMG(55.54, RUSH, RUSH_TAG, g='flashback', ov=[LAB('NOTHING FUNDAMENTAL CHANGES', 57.2, AMBER, size=48)]),
         IMG(59.40, 'docs/img/p163-000.png', 'First Titan hull · photo: ' + MBI, g='flashback', trans='flash', kb=((0.5, 0.5, 1.0), (0.62, 0.55, 1.5)), ov=[LAB('2019: A CRACK', 59.6, RED, size=70)]),
         IMG(66.82, M := 'media/Titan_carbon_fiber_hull_sits_in_storage_(9057367).jpg', 'First Titan hull · U.S. Coast Guard photo', g='flashback', ov=[LAB('RETIRED', 67.0, AMBER, size=70)]),
         IMG(68.60, 'docs/img/p16-001.png', OGM, g='film', trans='push', ov=[LAB('A NEW HULL', 68.7, CYAN, size=70)]),
         V(72.40, TAIL, ROV, ss=10.0, trans='glitch', ov=[DARK(72.4, 0.5), LAB('PART 2: THE BANG', 72.5, AMBER, size=84), LAB('FOLLOW', 74.8, CYAN, y=620, size=70)])]
elif N == 2:   # PART 2 · THE BANG (2022-2023)
    END = 79.5; TITLE = 'PART 2 / 3  ·  THE BANG'
    T = [IMG(0.0, 'docs/img/p263-000.png', OGM, g='flashback', kb=((0.5, 0.5, 1.4), (0.5, 0.5, 1.0)), ov=[LAB('"AS LOUD AS AN EXPLOSION"', 0.3, AMBER, size=58)]),
         DOC(5.96, 'loud', trans='glitch'),
         ANI(7.94, 147.0, zoom=(1.3, 1.5), ov=[LAB('THE TITAN STORY', 8.1, CYAN, size=64)]),
         IMG(10.70, 'docs/img/p16-003.png', OGM, g='flashback', ov=[LAB('JULY 2022', 10.8, AMBER, size=80)]),
         V(11.94, TIT, 'RMS Titanic, 1912 · public-domain film', ss=40.0, g='none', ov=[LAB('RISING FROM THE TITANIC', 12.2, WHITE, size=52)]),
         DOC(16.06, 'loud', trans='flash', kb=((0.5, 0.45, 1.05), (0.5, 0.45, 1.15))),
         IMG(19.48, 'docs/img/p263-000.png', OGM, g='flashback', kb=((0.5, 0.65, 1.2), (0.5, 0.7, 1.5)), ov=[LAB('HEARD ON THE SURFACE', 19.7, WHITE, size=54)]),
         V(22.28, AFT, ROV, ss=62.0, trans='glitch', ov=[DARK(22.3, 0.55), STAT(24.2, 0, 25687, 'millivolts · sensor spike', dur=1.0)]),
         DOC(25.66, 'inop', ov=[STAMP('3 OF 8 DEAD', 26.0, size=84)]),
         IMG(27.82, 'docs/img/p142-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.3, 0.5, 1.2), (0.3, 0.5, 1.4)), ov=[LAB('NEVER OPENED UP', 28.0, RED, size=64)]),
         DOC(31.46, 'sled'),
         DOC(35.68, 'strain', trans='push'),
         DOC(40.42, 'strain', kb=((0.5, 0.45, 1.05), (0.5, 0.45, 1.15)), ov=[STAMP('NEVER ANALYZED', 40.8, size=80)]),
         IMG(44.08, 'docs/img/p240-000.png', 'Photo · via ' + MBI, g='flashback', kb=((0.5, 0.55, 1.0), (0.6, 0.6, 1.25)), ov=[LAB('7 MONTHS OUTSIDE', 44.3, AMBER, size=64)]),
         IMG(47.98, 'docs/img/p240-000.png', 'Photo · via ' + MBI, g='flashback', kb=((0.6, 0.6, 1.25), (0.5, 0.6, 1.4)), ov=[LAB('UNCOVERED · SNOW · 1°F', 48.1, WHITE, size=56)]),
         DOC(50.58, 'cover', trans='push', ov=[STAT(51.6, 0, 1750, 'Canadian dollars', fmt='CA${:,.0f}', y=420)]),
         DOC(55.24, 'cover', kb=((0.5, 0.45, 1.05), (0.5, 0.45, 1.15)), ov=[STAMP('NEVER APPROVED', 55.3, size=80)]),
         IMG(56.86, 'docs/img/p263-000.png', OGM + ' (Dive 87)', g='flashback', trans='glitch', ov=[LAB('JUNE 2023', 57.0, AMBER, size=80)]),
         IMG(58.92, 'docs/img/p262-000.png', OGM + ' (Dive 87)', g='flashback', kb=((0.5, 0.5, 1.0), (0.55, 0.5, 1.3)), ov=[LAB('THROWN · SLAMMED · AGAIN', 60.5, RED, size=58)]),
         DOC(66.34, 'indestructible'),
         DOC(69.66, 'kills', trans='flash'),
         V(74.52, TAIL, ROV, ss=10.0, trans='glitch', ov=[DARK(74.5, 0.5), LAB('PART 3: THE LAST MESSAGE', 74.6, AMBER, size=70), LAB('FOLLOW', 76.9, CYAN, y=620, size=70)])]
else:   # PART 3 · THE LAST MESSAGE (June 18, 2023)
    END = 79.7; TITLE = 'PART 3 / 3  ·  THE LAST MESSAGE'
    T = [V(0.0, TAIL, ROV, ss=45.0, zoom=(1.2, 1.0), ov=[DARK(0.0, 0.3), CHAT([(0.3, 'TITAN', 'dropped two wts', '10:47:02')], keep=1)]),
         ANI(5.50, 150.0, zoom=(1.3, 1.5), ov=[LAB('THE TITAN STORY', 5.7, CYAN, size=64)]),
         IMG(8.82, 'docs/img/p18-000.png', 'Photo: OceanGate · via ' + MBI, g='film', ov=[LAB('JUNE 18, 2023', 9.0, CYAN, size=80)]),
         IMG(11.78, 'docs/img/p262-000.png', OGM, kb=((0.45, 0.5, 1.0), (0.45, 0.5, 1.25)), trans='sink'),
         ANI(15.0, 168.0, zoom=(1.6, 1.8)),
         V(18.52, AFT, ROV, ss=2.0, ov=[DARK(18.5, 0.35), CHAT([(19.0, 'PP', 'k', '9:18:16'), (20.0, 'TITAN', 'k', '9:19:00')])]),
         ANI(22.18, 330.0, trans='ping', zoom=(1.6, 1.8)),
         V(24.52, AFT, ROV, ss=58.0, ov=[DARK(24.5, 0.5), LAB('13 MINUTES OF SILENCE', 24.6, WHITE, size=62)]),
         V(26.32, TAIL, ROV, ss=8.0, ov=[DARK(26.3, 0.35), CHAT([(26.6, 'TITAN', 'k', '10:08')], keep=1)]),
         ANI(28.30, 592.0, zoom=(1.6, 1.8)),
         V(32.22, TAIL, ROV, ss=45.0, ov=[DARK(32.2, 0.35), CHAT([(32.4, 'TITAN', 'dropped two wts', '10:47:02')], keep=1)]),
         ANI(34.66, 600.0, zoom=(1.6, 1.9)),
         V(38.20, NOAA, 'NOAA acoustic recording · USCG MBI Exhibit 140', ss=7.9, g='none', zoom=(1.0, 1.1), ov=[LAB('10:47:09', 38.3, RED, size=90)]),
         V(41.70, AFT, ROV, ss=12.0, trans='flash'),
         IMG(44.96, 'docs/img/p32-000.png', 'Polar Prince bridge office · photo: ' + MBI, g='film'),
         IMG(48.06, 'docs/img/p35-000.png', 'OceanGate video still (faces blurred by USCG) · via ' + MBI, g='film', ov=[LAB('"WHAT WAS THAT BANG?"', 48.1, AMBER, size=60)]),
         IMG(50.76, 'media/Coast_Guard_air_crew_conducts_overflight_search_for_missing_submersible,_Titan_-_230621-G-MJ422-1001.jpg', 'U.S. Coast Guard photo', g='film', ov=[LAB('7:10 P.M. · COAST GUARD NOTIFIED', 50.9, WHITE, size=46)]),
         IMG(53.16, "media/Coast_Guard_HC-130_and_L'Atalante_searching_for_Titan.jpg", 'U.S. Coast Guard photo', g='film', ov=[LAB('11 SHIPS · 4 AIRCRAFT', 54.6, CYAN, size=64)]),
         V(58.84, TAIL, ROV, ss=14.0, trans='ping', ov=[LAB('JUNE 22', 59.0, CYAN, size=80)]),
         V(62.0, TAIL, ROV, ss=22.0, ov=[LAB("TITAN'S TAIL CONE", 62.2, WHITE, size=60)]),
         DOC(65.16, 'preventable', trans='glitch', kb=((0.5, 0.45, 1.05), (0.5, 0.45, 1.15))),
         V(70.22, SALV, ROV, ss=30.0),
         V(72.06, AFT, ROV, ss=84.0, ov=[DARK(72.1, 0.4), LAB('EXPLAINED AWAY', 72.8, RED, size=80)]),
         V(74.00, LIFT, ROV, ss=70.0, trans='dip', ov=[DARK(74.0, 0.5), LAB('FULL STORY ON THE CHANNEL', 74.1, CYAN, size=56), LAB('WOULD YOU HAVE\nCLIMBED INSIDE?', 76.9, WHITE, y=620, size=70)])]

DEPTHPOST = fx4.depth_post([(8.8, 0, '08:30'), (15.0, 300, '09:20'), (22.18, 1700, '09:53'), (26.32, 2050, '10:08'), (28.3, 3300, '10:47'), (34.66, 3346, '10:47:08')],
                           [(11.78, 22.18), (24.52, 28.3), (32.22, 34.66)], []) if N == 3 else None

def captions(img, t, fi, sh):
    """Captions (3-word groups, active word yellow, on a soft band) + series badge + progress bar."""
    if DEPTHPOST: img = DEPTHPOST(img, t, fi, sh)
    cur = None
    for i in range(0, len(WORDS), 3):
        g = WORDS[i:i + 3]
        if g[0]['s'] - 0.05 <= t <= g[-1]['e'] + 0.25: cur = g
    d = ImageDraw.Draw(img)
    if cur:
        words = [x['w'].upper() for x in cur]; fs = 112
        while True:
            f = font('bebas', fs); sp = 26; widths = [f.getlength(w) for w in words]; tot = sum(widths) + sp * (len(words) - 1)
            if tot <= W - 120 or fs <= 70: break
            fs -= 6
        x = (W - tot) / 2; y = int(H * 0.70)
        band = Image.new('L', img.size, 0); ImageDraw.Draw(band).rounded_rectangle([int(x) - 34, y - 14, int(x + tot) + 34, y + fs + 18], radius=26, fill=150)
        img.paste((0, 0, 0), (0, 0), band); d = ImageDraw.Draw(img)
        for w, wd, x0 in zip(words, widths, [x + sum(widths[:j]) + sp * j for j in range(len(words))]):
            on = any(c['w'].upper() == w and c['s'] <= t for c in cur) and t <= max(c['e'] for c in cur if c['w'].upper() == w) + 0.15
            d.text((x0, y), w, font=f, fill=(255, 214, 64) if on else (255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
    # series badge (top) + progress bar
    fb = font('monob', 34); tw = fb.getlength(TITLE)
    d.rectangle([(W - tw) / 2 - 24, 120, (W + tw) / 2 + 24, 176], fill=(0, 0, 0))
    d.rectangle([(W - tw) / 2 - 24, 172, (W + tw) / 2 + 24, 176], fill=CYAN)
    d.text((W / 2, 148), TITLE, font=fb, fill=WHITE, anchor='mm')
    d.rectangle([0, 0, int(W * t / END), 10], fill=CYAN)
    return img

if __name__ == '__main__':
    if sys.argv[2] == 'frames':
        for tt in map(float, sys.argv[4:]): render(T, END, f'{sys.argv[3]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=captions)
    else:
        render(T, END, sys.argv[2], float(os.environ.get('T0', 0)), float(os.environ.get('T1', END)), log=True, post=captions)
