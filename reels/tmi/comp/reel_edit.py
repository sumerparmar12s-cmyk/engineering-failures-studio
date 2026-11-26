"""Three Mile Island reels (1080x1920), no channel branding. usage: VW=1080 VH=1920 python3 reel_edit.py PART OUT.mp4 | frames PREFIX t..."""
import sys, os, json, re
assert os.environ.get('VW') == '1080', 'run with VW=1080 VH=1920'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import fx3, fx5
from fx5 import AMBER, GREEN, RED, WHITE, GREY, CREAM
N = int(sys.argv[1]); PD = f'{ROOT}/p{N}'
WORDS = json.load(open(f'{PD}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')
M = lambda n: f'media/{n}'
NRC = 'U.S. Nuclear Regulatory Commission'
TOWERS, UNIT2 = M('Three_Mile_Island_Nuclear_Generating_Station.jpg'), M('Three_Mile_Island_Nuclear_Generating_Station_Unit_2.jpg')
PLANT79, HBG79, CORE, CLEAN = M('Three_Mile_Island_(color)-2.jpg'), M('Harrisburg_Int_Airport_with_Pennsylvania_ANG_aircraft_1979.jpg'), M('Graphic_TMI-2_Core_End-State_Configuration.png'), M('TMI_cleanup-2.jpg')
def V(t0, path, tag, ss=0.0, g='seventies', **k): return Shot(t0, ('vid', path), grade=g, src_tag=None, ss=ss, **k)   # no on-screen source text (credits go in the post caption)
def IMG(t0, path, tag, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), g='seventies', **k): return Shot(t0, ('img', path), grade=g, src_tag=None, kb=kb, **k)
def X(**k): return k
def DARK(at, a=0.6): return O.dark(at, amount=a)
def LAB(text, at, col=CREAM, y=330, size=58): return O.label(text, W // 2, y, at, anchor='mm', color=col, size=size)
def BIGT(text, at, sub=None, col=AMBER): return O.punch(text, at, color=[col], size=150, y=760, f='bebas', sub=sub, shake=False)

if N == 1:
    END = 67.9; TITLE = 'THREE MILE ISLAND  ·  PART 1'
    TILES = [('FEEDWATER\nPUMPS TRIP', S('stop', 23.0), AMBER), ('TURBINE\nTRIP', S('turbine', 23.6) + 0.4, AMBER), ('REACTOR\nTRIP', S('reactor', 25.5) + 0.4, RED),
             ('PRESSURIZER\nLEVEL', None, AMBER), ('RELIEF\nVALVE', None, GREEN), ('STEAM GEN\nLEVEL LOW', S('turbine', 23.6) + 1.0, AMBER),
             ('COOLANT\nTEMP', None, AMBER), ('RADIATION\nMONITOR', None, RED), ('DRAIN TANK\nPRESSURE', None, AMBER)]
    T = [IMG(0.0, UNIT2, 'Photo: Wikimedia Commons (CC BY-SA 3.0)', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.15)), ov=[DARK(0.0, 0.72),
             X(k='lamp', at=0.2, label='RELIEF VALVE', state='CLOSED', color=GREEN, y=820, truth=(S('lying', 6.4) + 0.1, 'IT WAS OPEN'))]),
         IMG(7.66, TOWERS, 'Photo: Wikimedia Commons (CC BY-SA 3.0)', trans='glitch', kb=((0.55, 0.5, 1.0), (0.5, 0.5, 1.2)),
             ov=[DARK(7.7, 0.3), LAB('THE MOST SERIOUS ACCIDENT IN\nU.S. NUCLEAR POWER HISTORY', 8.4, AMBER, size=52)]),
         IMG(13.60, HBG79, 'U.S. Air National Guard photo, 1979', trans='zoom', ov=[DARK(13.6, 0.45), BIGT('MARCH 28, 1979', 13.7, sub='4:00 A.M.')]),
         IMG(16.46, PLANT79, 'Three Mile Island, 1979 · public domain', kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.25)), ov=[LAB('THREE MILE ISLAND · PENNSYLVANIA', 16.7, CREAM, size=50)]),
         IMG(19.26, PLANT79, 'Three Mile Island, 1979 · public domain', trans='push', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.4)), ov=[DARK(19.3, 0.75), LAB('IT STARTS SMALL', 19.4, AMBER, y=230, size=56),
             X(k='annun', at=19.3, tiles=TILES, xy=(60, 420), th=130)]),
         V(27.20, 'real/nrc_reactor_v.mp4', 'Animation: ' + NRC, ss=11.0, g='none', trans='zoom', ov=[LAB('PRESSURE RISES · VALVE OPENS', 27.6, AMBER, y=300, size=52),
             LAB('WHEN PRESSURE DROPS, IT SHOULD CLOSE', S('drops', 33.2) - 0.2, CREAM, y=1560, size=46)]),
         IMG(35.42, PLANT79, 'Three Mile Island, 1979 · public domain', trans='glitch', kb=((0.5, 0.5, 1.4), (0.5, 0.5, 1.5)), ov=[DARK(35.4, 0.8), X(k='valve', at=35.4, x=W // 2, y=900, open_at=35.0, stuck=S('stuck', 36.3) - 0.1, s=1.1)]),
         IMG(37.48, PLANT79, 'Three Mile Island, 1979 · public domain', trans='flash', kb=((0.5, 0.5, 1.5), (0.5, 0.5, 1.6)), ov=[DARK(37.5, 0.82), LAB('WHAT THE CONTROL ROOM SHOWED', 37.6, CREAM, y=300, size=50),
             X(k='lamp', at=37.5, label='RELIEF VALVE', state='CLOSED', color=GREEN, y=860)]),
         IMG(40.98, PLANT79, 'Three Mile Island, 1979 · public domain', trans='push', kb=((0.5, 0.5, 1.6), (0.5, 0.5, 1.7)), ov=[DARK(41.0, 0.8), X(k='valve', at=41.0, x=W // 2, y=1000, open_at=40.0, s=1.0), LAB('WHAT WAS REALLY HAPPENING', 41.1, RED, y=240, size=52), O.punch('NOBODY KNOWS.', S('nobody', 44.6), color=[WHITE], size=130, y=1550, f='bebas', shake=False)]),
         IMG(46.02, TOWERS, 'Photo: Wikimedia Commons (CC BY-SA 3.0)', trans='glitch', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.4)), ov=[DARK(46.0, 0.82), LAB('THE WORST MOVE OF ALL', 46.2, RED, y=300, size=56),
             X(k='level', at=46.1, label='PRESSURIZER LEVEL', box=(W // 2 - 140, 520, 280, 560), keys=[(46.1, 0.55), (49.5, 0.92)], note=(S('too', 49.8), 'LOOKS TOO FULL', AMBER)),
             O.stamp('EMERGENCY WATER CUT BACK', S('cut', 51.3), x=W // 2, y=900, size=74)]),
         V(53.38, 'real/nrc_reactor_v.mp4', 'Animation: ' + NRC, ss=19.0, g='none', trans='push', ov=[LAB('THE WATER LEVEL FALLS', 53.6, AMBER, y=300, size=56)]),
         IMG(56.94, PLANT79, 'Three Mile Island, 1979 · public domain', trans='flash', kb=((0.5, 0.5, 1.6), (0.5, 0.5, 1.7)), ov=[DARK(57.0, 0.82), X(k='thermo', at=57.0, dur=1.7)]),
         IMG(58.92, CORE, 'Graphic: ' + NRC, mode='portrait', g='none', trans='zoom', kb=((0.5, 0.45, 1.0), (0.5, 0.5, 1.35)), ov=[LAB('PART OF THE CORE MELTED', 59.6, RED, y=300, size=60)]),
         IMG(62.30, CLEAN, 'TMI cleanup, 1979 · public domain', trans='glitch', kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.25)), ov=[DARK(62.3, 0.55), BIGT('PART 2', 62.4, sub='why the outside world panicked', col=AMBER),
             O.label('FOLLOW', W // 2, 1040, S('Follow', 65.7), anchor='mm', color=WHITE, size=80)])]

def captions(img, t, fi, sh):
    """New caption style: big cream Oswald words, current word boxed in amber; radiation badge + part title; amber progress bar."""
    cur = None
    for i in range(0, len(WORDS), 3):
        g = WORDS[i:i + 3]
        if g[0]['s'] - 0.05 <= t <= g[-1]['e'] + 0.25: cur = g
    d = ImageDraw.Draw(img)
    if cur:
        f = font('oswald', 88); sp = 24; words = [x['w'].upper() for x in cur]; widths = [f.getlength(w) for w in words]
        tot = sum(widths) + sp * (len(words) - 1)
        while tot > W - 100: f = font('oswald', f.size - 6); widths = [f.getlength(w) for w in words]; tot = sum(widths) + sp * (len(words) - 1)
        x = (W - tot) / 2; y = int(H * 0.66)
        for w, wd, x0 in zip(words, widths, [x + sum(widths[:j]) + sp * j for j in range(len(words))]):
            on = any(c['w'].upper() == w and c['s'] <= t for c in cur) and t <= max(c['e'] for c in cur if c['w'].upper() == w) + 0.15
            if on: d.rectangle([x0 - 10, y + 6, x0 + wd + 10, y + f.size * 1.18], fill=AMBER)
            d.text((x0, y), w, font=f, fill=(20, 16, 10) if on else CREAM, stroke_width=0 if on else 6, stroke_fill=(0, 0, 0))
    # badge: radiation trefoil + part title
    fb = font('oswald', 36); tw = fb.getlength(TITLE); bx = (W - tw) / 2 + 30
    d.rectangle([bx - 90, 110, bx + tw + 24, 178], fill=(16, 14, 10))
    d.ellipse([bx - 78, 116, bx - 22, 172], fill=AMBER); fx5.trefoil(d, bx - 50, 144, 24, (16, 14, 10)); d.ellipse([bx - 57, 137, bx - 43, 151], fill=AMBER); d.ellipse([bx - 54, 140, bx - 46, 148], fill=(16, 14, 10))
    d.text((bx, 144), TITLE, font=fb, fill=AMBER, anchor='lm')
    d.rectangle([0, H - 14, int(W * t / END), H], fill=AMBER)
    return img

if __name__ == '__main__':
    if sys.argv[2] == 'frames':
        for tt in map(float, sys.argv[4:]): render(T, END, f'{sys.argv[3]}_{tt:05.1f}.mp4', tt, tt + 1 / 30, post=captions)
    else:
        render(T, END, sys.argv[2], float(os.environ.get('T0', 0)), float(os.environ.get('T1', END)), log=True, post=captions)
