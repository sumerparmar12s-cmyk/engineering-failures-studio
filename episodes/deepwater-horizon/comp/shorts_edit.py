"""Vertical Shorts (1080x1920). usage: VW=1080 VH=1920 python3 shorts_edit.py N OUT.mp4"""
import sys, os, json, re
assert os.environ.get('VW') == '1080', 'run with VW=1080 VH=1920'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import fx3
from fx3 import TEAL, ORANGE, WHITE
N = int(sys.argv[1]); SD = f'{ROOT}/shorts/s{N}'
WORDS = json.load(open(f'{SD}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')
RED = (255, 70, 50)
CG, CSB, NC, NASA = 'U.S. Coast Guard photo', 'CSB report', 'National Commission report', 'NASA photo'
def AI(t0, name, **k): return Shot(t0, ('ai', name), **k)
def ST(t0, name, **k): return Shot(t0, ('img', f'ai/still/{name}.png'), mode='upscale', **k)
def IMG(t0, path, tag, **k): return Shot(t0, ('img', path), src_tag=tag, **k)
def DOC(t0, path, tag, kb, **k): return Shot(t0, ('img', path), mode='contain', kb=kb, grade='paper', grain=3.0, src_tag=tag, **k)
def V3(t0, **k): return Shot(t0, ('black',), grain=2.0, grade='none', **k)
def X(**k): return k
def STAT(at, v0, v1, unit, fmt='{:,.0f}', dur=1.0): return X(k='stat', at=at, v0=v0, v1=v1, unit=unit, fmt=fmt, dur=dur, y=560, size=200)
def LAB(text, at, col=WHITE, y=420, size=56): return O.label(text, W // 2, y, at, anchor='mm', color=col, size=size)

if N == 1:
    END = 51.3
    T = [AI(0.0, 'd01_rig_fireball', grade='fire', zoom=(1.25, 1.0)),
         DOC(4.94, 'media/doc_128k.png', NC, ((0.5, 0.5, 1.0), (0.42, 0.5, 1.6)), trans='zoom', ov=[STAT(S('hundred', 7.2) - 0.2, 0, 128000, 'saved', fmt='${:,.0f}', dur=1.3)]),
         AI(9.88, 'd02_rig_dusk', trans='push', grade='film', zoom=(1.0, 1.15), ov=[LAB('APRIL 20, 2010', 10.0, ORANGE)]),
         AI(12.54, 'd06_pipe_ocean_depth', grade='cold', zoom=(1.0, 1.2), ov=[LAB('A MILE UNDER THE GULF', 13.5, (120, 190, 255))]),
         IMG(18.36, 'media/csb_cement.png', CSB, mode='contain', grade='paper', kb=((0.5, 0.6, 1.0), (0.5, 0.85, 1.6)), ov=[LAB('THE CEMENT PLUG = THE CORK', 19.5, ORANGE)]),
         DOC(26.2, 'media/doc_email.png', NC, ((0.5, 0.5, 1.0), (0.4, 0.7, 1.5)), trans='push'),
         AI(28.95, 'd03_helicopter', grade='film', zoom=(1.0, 1.2), ov=[LAB('11:00 A.M. · TEAM SENT HOME', 29.2, ORANGE)]),
         V3(33.2, src_tag='Diagram · not to scale', ov=[X(k='well', at=33.2, disp=(33.0, 33.3), gas=(33.6, 36.0), cement_fail=33.3, labels=[('CEMENT FAILED', 1020, 1700, 33.6, RED)])]),
         AI(35.16, 'd10_explosion_night', trans='flash', grade='fire', zoom=(1.0, 1.3)),
         IMG(38.56, 'media/uscg_rig_burning.png', CG, mode='upscale', grade='fire', kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.2)), ov=[O.dark(38.6, amount=0.35), STAT(38.7, 0, 11, 'men killed', dur=0.6)]),
         AI(40.14, 'd16_oil_slick_aerial', grade='film', zoom=(1.0, 1.25), ov=[LAB('87 DAYS OF OIL', 40.6, ORANGE)]),
         IMG(43.68, 'media/nasa_iss023e032397.jpg', NASA + ' from the ISS', mode='upscale', grade='film', kb=((0.5, 0.45, 1.0), (0.45, 0.4, 1.4)), ov=[LAB('FULL STORY ON THE CHANNEL', 44.0, TEAL)]),
         AI(47.38, 'd01_rig_fireball', ss=1.0, trans='glitch', grade='fire', zoom=(1.0, 1.25), ov=[O.label('WOULD YOU HAVE SENT THEM HOME?', W // 2, 420, 47.5, anchor='mm', color=WHITE, size=60)])]
elif N == 2:
    END = 52.5
    T = [ST(0.0, 't05_gauge_1400', grade='night', kb=((0.5, 0.5, 1.4), (0.5, 0.5, 1.0)), ov=[LAB('1,400 PSI', 0.2, RED, size=90)]),
         ST(3.36, 't04_control_room', trans='glitch', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[O.dark(3.4, amount=0.45), O.punch('"BLADDER\nEFFECT"', 3.5, color=[ORANGE, ORANGE], size=170, y=520)]),
         IMG(5.78, 'media/uscg_rig_burning.png', CG, mode='upscale', grade='fire', kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.2)), trans='flash', ov=[STAT(5.9, 0, 11, 'men died', dur=0.6)]),
         AI(7.7, 'd02_rig_dusk', trans='push', grade='film', zoom=(1.0, 1.15), ov=[LAB('APRIL 20, 2010', 7.9, ORANGE)]),
         AI(11.7, 'd04_drill_floor', grade='night', zoom=(1.0, 1.2), ov=[LAB('THE NEGATIVE PRESSURE TEST', 12.0, ORANGE)]),
         V3(15.0, src_tag='Analogy', ov=[X(k='bottle', at=15.0, vals=[(15.0, 0), (19.5, 0), (21.0, 55), (22.8, 60)], vmax=100, warn=20,
               notes=[('STAYS AT ZERO = SEALED', 17.2, TEAL), ('CLIMBING = LEAKING', 20.3, RED)])]),
         V3(22.84, src_tag='Illustrative · National Commission report', ov=[X(k='chart', at=22.9, dur=4.0, box=(150, 520, 800, 520), vmax=1600, title='SAME WELL · TWO READINGS',
               series=[dict(pts=[(0, 1400), (1.0, 1400)], color=ORANGE, label='DRILL PIPE 1,400', labat=0.4), dict(pts=[(0, 0), (1.0, 0)], color=TEAL, label='KILL LINE 0', labat=0.2)])]),
         ST(28.26, 't04_control_room', grade='night', kb=((0.5, 0.5, 1.2), (0.45, 0.5, 1.4)), ov=[O.dark(28.3, amount=0.5), O.punch('"I\'VE SEEN\nTHIS BEFORE"', 28.4, color=[WHITE, WHITE], size=140, y=520)]),
         AI(32.56, 'd05_control_gauges', grade='night', zoom=(1.2, 1.0), ov=[O.dark(32.6, amount=0.4), O.type('RESULT:\nPASS', 32.8, x=330, y=480, size=90, cps=10, color=(120, 255, 140), box=False)]),
         DOC(35.48, 'media/doc_bladder.png', NC, ((0.5, 0.5, 1.0), (0.35, 0.3, 1.8)), trans='push'),
         V3(40.26, src_tag='Diagram · not to scale', ov=[X(k='well', at=40.26, disp=(40.0, 40.3), gas=(40.3, 42.0), cement_fail=40.3, labels=[('THE WELL WAS FLOWING', 1020, 300, 40.6, RED)])]),
         AI(42.08, 'd10_explosion_night', trans='flash', grade='fire', zoom=(1.0, 1.3)),
         AI(46.72, 'd01_rig_fireball', grade='fire', zoom=(1.0, 1.2), ov=[LAB('FULL STORY ON THE CHANNEL', 46.9, TEAL)]),
         ST(48.4, 't05_gauge_1400', trans='glitch', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.4)), ov=[O.label('WOULD YOU HAVE\nSTOPPED THE JOB?', W // 2, 420, 48.5, anchor='mm', color=WHITE, size=62)])]
else:
    END = 53.3
    T = [AI(0.0, 'd07_seabed_bop', grade='cold', zoom=(1.3, 1.0), ov=[LAB('400 TONS · ONE JOB', 0.3, ORANGE, size=70)]),
         AI(6.1, 'd17_underwater_leak', trans='glitch', grade='cold', zoom=(1.0, 1.2), ov=[O.punch('IT FAILED.', 6.15, color=[RED], size=170, y=560)]),
         IMG(7.24, 'media/csb_bop.png', CSB, mode='contain', grade='paper', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[LAB("HERE'S WHY", 7.3, TEAL)]),
         AI(8.54, 'd02_rig_dusk', trans='push', grade='film', zoom=(1.0, 1.15), ov=[LAB('DEEPWATER HORIZON · 2010', 8.7, ORANGE)]),
         IMG(14.92, 'media/csb_bop.png', CSB, mode='contain', grade='paper', kb=((0.5, 0.4, 1.3), (0.5, 0.6, 1.8)), ov=[LAB('57 FT TALL', 15.3, ORANGE, size=70), LAB('A MILE UNDERWATER', 18.0, (120, 190, 255), y=520)]),
         AI(20.02, 'd07_seabed_bop', ss=3.0, grade='cold', zoom=(1.2, 1.35), ov=[LAB('JOB: CUT THE PIPE · SEAL THE WELL', 20.3, WHITE, size=48)]),
         ST(24.76, 't08_bridge_panel', trans='push', grade='night', kb=((0.5, 0.5, 1.2), (0.5, 0.5, 1.5)), ov=[LAB('EMERGENCY DISCONNECT', 25.5, RED)]),
         ST(29.04, 't08_bridge_panel', trans='glitch', grade='cold', kb=((0.5, 0.5, 1.5), (0.5, 0.5, 1.5)), ov=[O.dark(29.1, amount=0.55), O.punch('NOTHING\nHAPPENED.', 29.1, color=[WHITE, WHITE], size=160, y=520)]),
         AI(30.42, 'd09_alarm_lights', grade='night', zoom=(1.0, 1.2)),
         AI(33.38, 'd07_seabed_bop', ss=2.0, grade='cold', zoom=(1.1, 1.3), ov=[LAB('BACKUP: LIKELY FIRED', 33.6, TEAL)]),
         IMG(36.14, 'media/csb_bop.png', CSB + ', vol. 2', mode='contain', grade='paper', kb=((0.5, 0.55, 1.4), (0.5, 0.6, 2.1)), ov=[LAB('THE PIPE HAD BUCKLED', 36.5, RED, size=64)]),
         AI(41.14, 'd17_underwater_leak', ss=2.0, grade='cold', zoom=(1.0, 1.25)),
         AI(43.42, 'd16_oil_slick_aerial', grade='film', zoom=(1.0, 1.25), ov=[LAB('87 DAYS OF OIL', 43.6, ORANGE)]),
         AI(46.56, 'd07_seabed_bop', grade='cold', zoom=(1.0, 1.3), ov=[LAB('FULL STORY ON THE CHANNEL', 46.7, TEAL), O.label('SHOULD THESE BE\nTESTED MORE OFTEN?', W // 2, 560, 48.5, anchor='mm', color=WHITE, size=62)])]

def captions(img, t, fi, sh):
    """Shorts captions: 3-word groups, current word highlighted, big and centred in the lower third."""
    grp = []; cur = None
    for i in range(0, len(WORDS), 3):
        g = WORDS[i:i + 3]
        if g[0]['s'] - 0.05 <= t <= g[-1]['e'] + 0.25: cur = g
    if not cur: return img
    d = ImageDraw.Draw(img); f = font('bebas', 112); words = [x['w'].upper() for x in cur]
    sp = 26; widths = [f.getlength(w) for w in words]; tot = sum(widths) + sp * (len(words) - 1); x = (W - tot) / 2; y = int(H * 0.70)
    for w, wd, x0 in zip(words, widths, [x + sum(widths[:j]) + sp * j for j in range(len(words))]):
        on = any(c['w'].upper() == w and c['s'] <= t for c in cur) and t <= max(c['e'] for c in cur if c['w'].upper() == w) + 0.15
        d.text((x0, y), w, font=f, fill=(255, 214, 64) if on else (255, 255, 255), stroke_width=8, stroke_fill=(0, 0, 0))
    # top progress bar (retention cue)
    d.rectangle([0, 0, int(W * t / END), 10], fill=ORANGE)
    return img

if __name__ == '__main__':
    render(T, END, sys.argv[2], 0.0, END, log=True, post=captions)
