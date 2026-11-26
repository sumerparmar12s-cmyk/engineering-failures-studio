"""Titan edit: two intercut timelines (live DIVE with depth gauge  <->  FLASHBACK warnings). usage: edit4.py render FROM TO OUT"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import fx3, fx4
from fx4 import CYAN, AMBER, WHITE, GREY, RED

WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')

def ex(p): return os.path.exists(p if p.startswith('/') else f'{ROOT}/{p}')
R = 'real/'
ANIF, TAIL, AFT, SALV, LIFT = R + 'CG_001_1_TITAN_Animation_20240915_v2.2.mp4', R + '04_ROV_Titan_Submersible_Tail_Cone.mp4', \
    R + '07_ROV_Titan_Submersible_Aft_Dome_Aft_Ring_Hull_Remnants.mp4', R + 'DOD_110579329.mp4', R + 'DOD_110579650.mp4'
CHART, PRESS, HEAR, TIT, NOAA = R + 'DOD_111016570.mp4', R + 'DOD_109728593.mp4', R + 'hearing_chair_open.mp4', R + 'titanic_1912_footage.mp4', R + 'DOD_110804017.mp4'
MBI = 'USCG Marine Board of Investigation report'
CGA, ROV = 'U.S. Coast Guard animation (Google Earth base)', 'ROV footage · U.S. Coast Guard / Pelagic Research Services'
OGM = 'OceanGate photo · via USCG MBI report'
RUSH = 'media/Stockton_Rush.png' if ex('media/Stockton_Rush.png') else 'docs/img/p16-001.png'
RUSH_TAG = 'Photo: OceanGate (CC BY 3.0)' if ex('media/Stockton_Rush.png') else OGM
M = lambda n: 'media/' + n
D = lambda n: f'media/doc/{n}.png'

def V(t0, path, tag, ss=0.0, g='abyss', **k): return Shot(t0, ('vid', path), grade=g, src_tag=tag, ss=ss, **k)
def ANI(t0, ss, **k): return Shot(t0, ('vid', ANIF), grade='none', src_tag=CGA, ss=ss, nohud=True, zoom=k.pop('zoom', (1.0, 1.06)), **k)
def IMG(t0, path, tag, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), g='abyss', **k): return Shot(t0, ('img', path), grade=g, src_tag=tag, kb=kb, **k)
def DOC(t0, key, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.22)), **k): return Shot(t0, ('img', D(key)), mode='cover', kb=kb, grade='paper', grain=3.0, src_tag=k.pop('tag', MBI), **k)
def X(**k): return k
def BIG(at, time, sub=None): return X(k='bigtime', at=at, time=time, sub=sub)
def Q(text, at, who='', hl=None, size=64): return O.quote(text, at, who=who, hl=hl or [], size=size)
def PUNCH(text, at, col=None, size=150, y=None): return O.punch(text, at, color=col or [WHITE, CYAN], size=size, y=y, f='bebas')
def STAT(at, v0, v1, unit, dur=1.0, fmt='{:,.0f}', y=None, size=230): return X(k='stat', at=at, v0=v0, v1=v1, unit=unit, dur=dur, fmt=fmt, y=y or H // 2 - 40, size=size)
def DEPTH(at, d, frm=0, sub=None): return X(k='depthcard', at=at, depth=d, **({'from': frm}), sub=sub)
def CHAT(msgs, keep=4): return X(k='chat', at=msgs[0][0], msgs=msgs, keep=keep)
def LAB(text, at, col=WHITE, size=50, y=860, until=None): return O.label(text, W // 2, y, at, anchor='mm', color=col, size=size, bg=False, until=until)
def DARK(at, a=0.45, until=None): return O.dark(at, amount=a, until=until)
def LOWER(t, s, at, until=None): return O.lower(t, s, at, until=until)
def CALL(pt, lab, text, at, sub=None, col=CYAN): return X(k='callout', pt=pt, lab=lab, text=text, at=at, sub=sub, color=col)

T = []
# ============================ HOOK: the last message (no black, real Coast Guard animation first frame) ============================
T += [ANI(0.0, 590.0, zoom=(1.0, 1.1), ov=[LAB('10:47 A.M.  ·  JUNE 18, 2023  ·  NORTH ATLANTIC', 0.4, col=CYAN, size=40, y=1010)]),
      V(6.94, TAIL, ROV, ss=2.0, zoom=(1.12, 1.0), trans='sink', ov=[DARK(6.94, 0.3), LAB('MORE THAN TWO MILES DOWN', 7.3, col=CYAN)]),
      DOC(10.10, 'wts', trans='glitch', kb=((0.45, 0.5, 1.25), (0.45, 0.5, 1.5))),
      ANI(12.72, 600.0, trans='flash', zoom=(1.1, 1.25)),
      V(16.92, TAIL, ROV, ss=52.0, trans='ping', zoom=(1.0, 1.08), ov=[DARK(16.92, 0.55), X(k='sonar', at=17.2, r=260, title='NO SIGNAL')]),
      IMG(20.38, 'docs/img/p10-000.png', OGM, trans='push', g='film', ov=[LAB('FIVE PEOPLE INSIDE', 20.7, size=56)]),
      IMG(22.64, RUSH, RUSH_TAG, g='film', kb=((0.5, 0.4, 1.0), (0.5, 0.4, 1.15)), ov=[O.type('THE DESIGNER.\nTHE SELLER.\nTHE PILOT.', 23.0, x=110, y=640, size=44, cps=26)]),
      IMG(27.94, RUSH, RUSH_TAG, g='film', kb=((0.5, 0.4, 1.15), (0.5, 0.38, 1.3)), ov=[LOWER('Stockton Rush', 'CEO, OceanGate', 28.0)]),
      V(29.66, HEAR, 'U.S. Coast Guard hearing, Sept. 2024', ss=6.0, g='film', trans='whip'),
      DOC(32.58, '26', trans='glitch', ov=[O.stamp('WARNED', 33.9, x=1500, y=300)]),
      DOC(36.30, 'fired', kb=((0.5, 0.5, 1.1), (0.5, 0.5, 1.3))),
      V(38.10, AFT, ROV, ss=22.0, trans='zoom', ov=[DARK(38.1, 0.5), PUNCH('SO WHY DID HE\nGO DOWN ANYWAY?', 38.3, size=130)]),
      V(40.32, PRESS, 'U.S. Coast Guard press briefing', ss=42.0, g='film', trans='whip', ov=[LAB('U.S. COAST GUARD  ·  MARINE BOARD OF INVESTIGATION', 40.8, size=42)]),
      ANI(46.10, 150.0, trans='ping', zoom=(1.0, 1.15), ov=[DARK(46.1, 0.35), O.punch('TITAN', 46.3, size=230, f='bebas', color=WHITE, sub='the warnings under the water', shake=False)]),
]
# ============================ DIVE (depth 0): the morning ============================
T += [IMG(50.32, 'docs/img/p18-000.png', 'Photo: OceanGate · via ' + MBI, trans='sink', kb=((0.5, 0.5, 1.0), (0.55, 0.5, 1.2)), ov=[DEPTH(S('Depth', 54.4), 0, sub='JUNE 18, 2023 · SUNDAY MORNING')]),
      ANI(55.94, 98.0, zoom=(1.0, 1.25), ov=[LAB('370 NAUTICAL MILES OFF NEWFOUNDLAND', 56.6, col=CYAN, size=44, y=1000)]),
      IMG(62.3, 'docs/img/p14-000.png', 'Photo: ' + MBI, kb=((0.45, 0.55, 1.0), (0.55, 0.5, 1.15)), g='film', ov=[LOWER('POLAR PRINCE', 'support ship · towed Titan\'s launch platform', 62.6)]),
      IMG(66.20, 'docs/img/p142-000.png', 'Photo: ' + MBI, g='film', trans='push', ov=[CALL((560, 470), (300, 250), 'TITAN', 67.0, sub='22 feet long', col=CYAN)]),
      IMG(70.86, 'docs/img/p16-003.png', OGM, kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.15)), ov=[LAB('"MISSION SPECIALISTS"', 71.3, col=AMBER)]),
      IMG(73.66, 'docs/img/p16-001.png', OGM, g='film', kb=((0.5, 0.5, 1.1), (0.5, 0.5, 1.25)), ov=[DARK(73.7, 0.5), STAT(73.9, 0, 250000, 'paid by two of them, each', fmt='${:,.0f}', dur=1.2)]),
      V(77.36, TIT, 'RMS Titanic, 1912 · public-domain film', ss=3.0, g='none', trans='dip', ov=[LOWER('Hamish Harding', 'British businessman & explorer', 77.6)]),
      V(80.62, TIT, 'RMS Titanic, 1912 · public-domain film', ss=36.0, g='none', ov=[LOWER('Shahzada & Suleman Dawood', 'a father, and his son, 19', 80.8)]),
      V(84.26, TIT, 'RMS Titanic, 1912 · public-domain film', ss=52.0, g='none', ov=[LOWER('Paul-Henri Nargeolet', 'veteran Titanic diver · the expert', 84.5)]),
      IMG(89.70, 'docs/img/p103-000.png', 'Game controller used to pilot OceanGate\'s Cyclops I · photo: ' + MBI, g='film', trans='flash', ov=[LOWER('Stockton Rush', 'CEO, OceanGate · the pilot', 90.0)]),
      IMG(94.42, 'docs/img/p10-000.png', OGM, g='film', trans='push', kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.2)), ov=[LAB('UNUSUAL BY DESIGN', 94.7, col=AMBER, y=140)]),
      IMG(96.76, 'docs/img/p101-000.png', 'Cyclops I · photo: ' + MBI, g='film', ov=[LAB('MOST DEEP SUBS: THICK STEEL OR TITANIUM SPHERES', 97.0, size=40)]),
      IMG(101.24, M('Titan_carbon_fiber_hull_sits_in_storage_(9057367).jpg'), 'Titan carbon fiber hull · U.S. Coast Guard photo', g='film', kb=((0.5, 0.35, 1.0), (0.5, 0.45, 1.15)),
          ov=[O.type('CARBON FIBER TUBE\n5 INCHES THICK\nGLUED TO TITANIUM RINGS', 101.8, x=110, y=620, size=44, cps=26)]),
      IMG(109.20, 'docs/img/p262-000.png', OGM, kb=((0.45, 0.5, 1.0), (0.45, 0.5, 1.2)), trans='sink', ov=[LAB('8:30 A.M.  ·  FIVE SEALED INSIDE', 109.5, col=CYAN)]),
      IMG(111.92, 'docs/img/p16-000.png', 'Photo: ' + MBI, g='film', kb=((0.3, 0.5, 1.3), (0.3, 0.5, 1.6)), ov=[LAB('THE FRONT DOME IS BOLTED SHUT', 112.1, size=46)]),
      V(114.14, AFT, ROV, ss=2.0, ov=[DARK(114.14, 0.35), CHAT([(115.0, 'PP', 'k', '9:18:16'), (116.4, 'TITAN', 'k', '9:19:00'), (117.6, 'PP', 'a', '9:19:11'), (118.6, 'TITAN', 'a', '9:19:19')])]),
      ANI(121.20, 147.0, zoom=(1.0, 1.15), ov=[LAB('9:14 A.M.  ·  TITAN BEGINS TO FALL', 121.5, col=CYAN, size=44, y=1000)]),
]
# ============================ FLASHBACK 1: 2018–2019 the warnings ============================
FB1 = dict(fb='JANUARY 2018')
T += [IMG(126.00, M('hearing_slide_1800.png'), 'U.S. Coast Guard hearing exhibit', g='flashback', trans='glitch', kb=((0.35, 0.5, 1.0), (0.35, 0.5, 1.15)), fb='2018–2019'),
      IMG(130.98, 'docs/img/p101-000.png', 'Photo: ' + MBI, g='flashback', ov=[BIG(131.0, 'JANUARY 2018', 'five years before the final dive')], **FB1),
      IMG(133.38, 'docs/img/p142-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.6, 0.5, 1.0), (0.6, 0.5, 1.2)),
          ov=[LOWER('Director of Marine Operations', 'OceanGate · in charge of crew & passenger safety', 133.8)], **FB1),
      DOC(143.42, '26', ov=[O.label('26 ITEMS NEEDING CORRECTIVE ACTION', W // 2, 980, 143.8, anchor='mm', color=RED, size=48)], **FB1),
      IMG(147.60, 'docs/img/p16-000.png', 'Photo: ' + MBI, g='flashback', ov=[DARK(147.6, 0.45), O.type('"...THE SUBMERSIBLE SHOULD NOT BE USED\nIN ANY UPCOMING TRIALS."', 148.0, x=110, y=640, size=42, cps=30)], **FB1),
      IMG(154.10, RUSH, RUSH_TAG, g='flashback', kb=((0.5, 0.4, 1.0), (0.5, 0.4, 1.15)), ov=[BIG(S('two', 156.4), '2 HOURS', 'a recorded meeting with Rush')], **FB1),
      DOC(161.36, 'fired', trans='glitch', ov=[O.stamp('FIRED', 161.6, x=1450, y=320)], fb='JANUARY 23, 2018'),
      DOC(164.02, 'lawsuit', fb='JUNE 2018'),
      DOC(168.18, 'osha', fb='FEBRUARY 2018', ov=[O.label('NEVER REACHED THE RIGHT PERSON', W // 2, 860, 172.5, anchor='mm', color=RED, size=46)]),
      DOC(176.14, 'withdrew', fb='DECEMBER 2018'),
      DOC(180.26, 'letter', trans='push', fb='2018'),
      IMG(188.62, RUSH, RUSH_TAG, g='flashback', kb=((0.5, 0.4, 1.2), (0.5, 0.4, 1.35)), ov=[LAB('NOTHING FUNDAMENTAL CHANGES', 190.0, col=AMBER, size=54)], fb='2018'),
      IMG(192.24, M('hearing_slide_1800.png'), 'U.S. Coast Guard hearing exhibit', g='flashback', kb=((0.84, 0.66, 1.6), (0.84, 0.66, 2.2)), fb='2019'),
      IMG(193.46, 'docs/img/p163-000.png', 'First Titan hull, crack ground out · photo: ' + MBI, g='flashback', trans='flash', kb=((0.5, 0.5, 1.0), (0.62, 0.55, 1.35)),
          ov=[LAB('THE CRACK', 196.0, col=RED, y=140)], fb='2019 · BAHAMAS'),
      DOC(203.66, 'crack', fb='2019'),
      IMG(211.00, 'docs/img/p163-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.6, 0.5, 1.3), (0.5, 0.5, 1.05)), ov=[DARK(211.0, 0.45), LAB('PUBLICLY: "THE SUPPORT SHIP WASN\'T AVAILABLE"', 211.8, size=42)], fb='2019'),
      IMG(217.94, M('Titan_carbon_fiber_hull_sits_in_storage_(9057367).jpg'), 'First Titan hull · U.S. Coast Guard photo', g='flashback', kb=((0.5, 0.5, 1.0), (0.5, 0.55, 1.2)),
          ov=[LAB('HULL 1: RETIRED', 218.2, col=AMBER)], fb='2019'),
      IMG(220.66, 'docs/img/p16-001.png', OGM, g='flashback', trans='push', ov=[LAB('HULL 2: THE ONE THAT WENT TO THE TITANIC', 221.0, col=CYAN, size=44)], fb='2021'),
      DOC(224.70, 'anathema', trans='glitch', fb='OCEANGATE BLOG'),
      DOC(231.84, 'notcert', ov=[O.stamp('NOT CERTIFIED', 233.2, x=1400, y=300, size=100)], fb='TITAN'),
]
# ============================ DIVE (1,000 m): silence ============================
T += [V(239.08, AFT, ROV, ss=40.0, trans='sink', ov=[DEPTH(239.2, 1038, frm=0, sub='9:40 A.M.')]),
      V(241.20, TAIL, ROV, ss=3.0, ov=[DARK(241.2, 0.35), CHAT([(241.6, 'PP', 'we see you at 33 m/sec', '9:28:35'), (243.4, 'PP', 'm/min', '9:28:41')])]),
      ANI(247.32, 330.0, trans='ping', zoom=(1.0, 1.08)),
      V(255.54, AFT, ROV, ss=58.0, ov=[DARK(255.6, 0.5), BIG(255.6, '13 MINUTES', 'of silence')]),
      V(258.22, TAIL, ROV, ss=8.0, trans='ping', ov=[DARK(258.2, 0.35), CHAT([(259.3, 'PP', 'do you see Polar Prince on your display?', '9:53:51'), (260.6, 'TITAN', 'k', '10:08')], keep=2)]),
      IMG(262.88, 'docs/img/p10-000.png', OGM, g='film', trans='whip', ov=[DARK(262.9, 0.5), PUNCH('MYTH', 263.0, col=[RED], size=150, y=300),
            O.type('A BRAND-NEW SUB FAILED\nON ITS FIRST DEEP DIVE', 263.6, x=420, y=440, size=50, box=False)], nohud=True),
      IMG(267.94, 'docs/img/p10-000.png', OGM, g='film', kb=((0.5, 0.5, 1.15), (0.5, 0.5, 1.3)), ov=[DARK(267.9, 0.5), STAT(268.0, 0, 88, 'this was dive number', dur=0.8)], nohud=True),
]
# ============================ FLASHBACK 2: July 2022 the bang + the winter ============================
T += [IMG(273.56, 'docs/img/p263-000.png', OGM, g='flashback', trans='glitch', ov=[BIG(273.6, 'JULY 2022', 'one year earlier')], fb='JULY 2022'),
      IMG(277.40, 'docs/img/p16-003.png', OGM, g='flashback', kb=((0.5, 0.5, 1.15), (0.45, 0.4, 1.35)), ov=[LAB('DIVE 80  ·  RISING FROM THE TITANIC', 277.8, col=AMBER, size=44)], fb='JULY 15, 2022'),
      DOC(283.60, 'loud', fb='DIVE 80', ov=[DARK(283.6, 0.7), Q('"A large bang or cracking sound."', 283.9, who='mission specialist, to the Coast Guard', size=60)]),
      DOC(289.08, 'loud', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.5)), fb='DIVE 80'),
      IMG(292.36, 'docs/img/p263-000.png', OGM, g='flashback', kb=((0.5, 0.6, 1.2), (0.5, 0.7, 1.4)), ov=[LAB('HEARD FROM A BOAT ON THE SURFACE', 292.6, size=46)], fb='DIVE 80'),
      V(295.66, AFT, ROV, ss=62.0, g='abyss', trans='glitch', ov=[DARK(295.7, 0.55),
          X(k='chart', at=295.9, dur=3.6, box=(420, 300, 1080, 470), vmax=30000, title='TITAN HULL ACOUSTIC SENSOR · DIVE 80 (mV)',
            series=[dict(pts=[(0, 300), (0.3, 500), (0.55, 900), (0.7, 1400), (0.82, 4000), (0.9, 25687), (0.95, 9000), (1.0, 2000)], color=RED, label='25,687 mV', labat=0.9)],
            marks=[]),
          O.label('Values from the USCG MBI report', W - 60, H - 60, 296.0, anchor='rm', color=GREY, size=24, bg=False)], fb='DIVE 80 · SENSOR DATA'),
      DOC(303.04, 'inop', fb='SENSORS', ov=[O.stamp('3 OF 8 DEAD', 303.4, x=1450, y=300, size=96)]),
      IMG(306.10, 'docs/img/p142-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.3, 0.5, 1.2), (0.3, 0.5, 1.4)), ov=[LAB('THE HULL WAS NEVER OPENED UP AND CHECKED', 306.4, size=44)], fb='JULY 2022'),
      IMG(309.54, RUSH, RUSH_TAG, g='flashback', kb=((0.5, 0.4, 1.0), (0.5, 0.4, 1.12)), fb='JULY 2022'),
      DOC(311.58, 'sled', fb='DIVE 80 DEBRIEF'),
      DOC(318.06, 'strain', trans='push', fb='USCG ANALYSIS'),
      DOC(325.60, 'strain', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.45)), ov=[O.stamp('NEVER ANALYZED', 326.0, x=1400, y=320, size=100)], fb='USCG ANALYSIS'),
      V(329.34, AFT, ROV, ss=70.0, trans='dip', ov=[DARK(329.3, 0.4)], nohud=True),
      IMG(330.66, M('hearing_slide_2400.png'), 'U.S. Coast Guard hearing exhibit', g='flashback', kb=((0.5, 0.5, 1.0), (0.78, 0.42, 1.9)), fb='WINTER 2022–23'),
      IMG(332.62, 'docs/img/p237-000.png', 'Image: A. Harvey · via ' + MBI, g='flashback', kb=((0.45, 0.5, 1.0), (0.48, 0.45, 1.3)),
          ov=[LAB('ST. JOHN\'S, NEWFOUNDLAND  ·  OPEN LOT', 333.0, col=AMBER, size=44)], fb='WINTER 2022–23'),
      IMG(339.46, 'docs/img/p240-000.png', 'Photo · via ' + MBI, g='flashback', kb=((0.5, 0.55, 1.0), (0.6, 0.6, 1.2)),
          ov=[LAB('~7 MONTHS  ·  UNCOVERED', 339.7, size=50), STAT(S('one', 344.5), 0, 1, 'degree Fahrenheit, at the coldest', dur=0.5, fmt='{:.0f}°F', y=380, size=190)], fb='FEBRUARY 2023'),
      DOC(346.80, 'cover', ov=[DARK(347.0, 0.65), STAT(347.2, 0, 1750, 'Canadian dollars · cover quote', fmt='CA${:,.0f}', dur=1.0, y=300, size=150)], fb='JULY 2022'),
      DOC(351.54, 'cover', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.4)), ov=[O.stamp('NEVER APPROVED', 351.8, x=1400, y=320, size=100)], fb='2022'),
]
# ============================ DIVE (2,800 m) ============================
T += [V(353.82, AFT, ROV, ss=80.0, trans='sink', ov=[DEPTH(353.9, 2833, frm=1038, sub='10:23 A.M.')]),
      ANI(356.58, 474.0, zoom=(1.0, 1.1)),
      V(362.72, TIT, 'RMS Titanic, 1912 · public-domain film', ss=12.0, g='none', ov=[LAB('THE TITANIC LIES AT ~3,800 m', 363.0, size=48)], nohud=True),
      V(368.18, TAIL, ROV, ss=56.0, ov=[DARK(368.2, 0.5), STAT(368.4, 0, 4930, 'pounds per square inch', dur=2.5, y=H // 2 - 60)]),
]
# ============================ FLASHBACK 3: June 12, 2023 Dive 87 ============================
FB3 = dict(fb='JUNE 12, 2023')
T += [IMG(373.32, 'docs/img/p263-000.png', OGM, g='flashback', trans='glitch', ov=[BIG(373.4, 'JUNE 12, 2023', 'six days earlier')], **FB3),
      IMG(379.44, 'docs/img/p16-000.png', 'Photo: ' + MBI, g='flashback', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), ov=[LAB('DIVE 87', 379.7, col=AMBER, size=60, y=140)], **FB3),
      DOC(383.96, 'kills', ov=[DARK(387.4, 0.7), Q('"I\'m going to get a dive in,\neven if it kills me."', 387.6, who='Stockton Rush, as recalled by a passenger', hl=['even if it kills me."'], size=62)], **FB3),
      IMG(393.04, 'docs/img/p262-000.png', OGM + ' (Dive 87)', g='flashback', kb=((0.5, 0.5, 1.0), (0.55, 0.5, 1.25)), ov=[LAB('THE PLATFORM\'S BALLAST SYSTEM FAILS', 393.3, size=46)], **FB3),
      IMG(396.22, 'docs/img/p263-000.png', OGM + ' (Dive 87)', g='flashback', kb=((0.5, 0.4, 1.0), (0.55, 0.42, 1.5)),
          ov=[O.type('THROWN UP AT 45°\nSLAMMED BACK DOWN\nAGAIN AND AGAIN', 396.8, x=110, y=640, size=46, cps=26)], **FB3),
      DOC(405.20, 'laundry', **FB3),
      DOC(408.82, 'indestructible', **FB3),
      IMG(415.28, RUSH, RUSH_TAG, g='flashback', kb=((0.5, 0.4, 1.1), (0.5, 0.4, 1.25)), ov=[O.stamp('"COMPLETELY SAFE"', 415.4, x=W // 2, y=300, size=110)], **FB3),
      IMG(417.02, 'docs/img/p16-003.png', OGM, g='flashback', trans='dip', ov=[LAB('SIX DAYS LATER, HE TOOK IT DOWN AGAIN', 417.3, size=50), O.label('COMMENT: WOULD YOU HAVE CLIMBED IN?', W // 2, 1000, 417.8, anchor='mm', color=CYAN, size=34, until=420.5)], **FB3),
]
# ============================ DIVE (3,341 m): the last ten seconds ============================
T += [V(420.56, AFT, ROV, ss=90.0, trans='sink', ov=[DEPTH(420.7, 3341, frm=2833, sub='10:47 A.M.')]),
      ANI(424.22, 592.0, zoom=(1.0, 1.12)),
      V(430.34, TAIL, ROV, ss=45.0, ov=[DARK(430.3, 0.35), CHAT([(430.7, 'TITAN', 'dropped two wts', '10:47:02')], keep=1)]),
      ANI(435.44, 600.0, zoom=(1.1, 1.3)),
      V(439.30, TAIL, ROV, ss=58.0, ov=[DEPTH(439.4, 3346, frm=3341, sub='10:47:08 · LAST PING')]),
      V(443.04, NOAA, 'NOAA acoustic recording of the implosion · USCG MBI Exhibit 140', ss=6.9, g='none', nohud=True, zoom=(1.0, 1.12),
          ov=[LAB('10:47:09', 443.2, col=RED, size=70, y=140)]),
      V(448.70, AFT, ROV, ss=12.0, trans='flash', nohud=True, ov=[DARK(448.7, 0.25)]),
      IMG(452.04, M('Titan_submersible_debris_(9057368).jpg'), 'Titan debris · U.S. Coast Guard photo', g='film', nohud=True),
      IMG(453.60, M('Titan_submersible_debris_recovery_(9057342).jpg'), 'Titan debris recovery · U.S. Coast Guard photo', g='film', nohud=True, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15))),
      IMG(457.90, 'docs/img/p32-000.png', 'Polar Prince bridge office · photo: ' + MBI, g='film', trans='push', nohud=True, kb=((0.5, 0.5, 1.0), (0.45, 0.5, 1.15))),
      IMG(461.6, 'docs/img/p35-000.png', 'Comms team after the sound · OceanGate video still (faces blurred by USCG) · via ' + MBI, g='film', nohud=True,
          kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), ov=[LAB('"WHAT WAS THAT BANG?"', S('What', 462.9), col=AMBER, size=60)]),
      IMG(466.36, 'docs/img/p35-000.png', 'OceanGate video still (faces blurred by USCG) · via ' + MBI, g='film', nohud=True, kb=((0.5, 0.5, 1.12), (0.5, 0.5, 1.2)), ov=[DARK(466.4, 0.35), LAB('NOBODY ANSWERS.', 466.5, size=56)]),
      IMG(468.42, 'docs/img/p38-000.png', 'Tracking display · OceanGate · via ' + MBI, g='film', nohud=True, kb=((0.3, 0.5, 1.2), (0.3, 0.5, 1.45)),
          ov=[LAB('"WE HAVE LOST TRACKING."', S('lost', 471.9) - 0.3, col=RED, size=56)]),
      IMG(473.36, 'docs/img/p14-000.png', 'Photo: ' + MBI, g='film', nohud=True, kb=((0.5, 0.5, 1.15), (0.6, 0.45, 1.3))),
      DOC(476.0, 'shudder', nohud=True),
      IMG(481.30, M('Coast_Guard_air_crew_conducts_overflight_search_for_missing_submersible,_Titan_-_230621-G-MJ422-1001.jpg'), 'U.S. Coast Guard photo', g='film', trans='whip', nohud=True,
          ov=[BIG(481.5, '7:10 P.M.', 'the Canadian Coast Guard is notified')]),
      IMG(487.94, M("Coast_Guard_HC-130_and_L'Atalante_searching_for_Titan.jpg"), 'U.S. Coast Guard photo', g='film', nohud=True, ov=[LAB('A HUGE INTERNATIONAL SEARCH', 488.2, size=50)]),
      IMG(491.20, 'docs/img/p41-002.png', 'U.S. Coast Guard briefing slide · via ' + MBI, g='film', nohud=True, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.1)),
          ov=[DARK(491.2, 0.45), STAT(S('twelve', 493.5) - 0.2, 0, 12145, 'square nautical miles searched', dur=1.2)]),
      IMG(496.88, M('Coast_Guard_air_crew_conducts_overflight_search_for_missing_submersible,_Titan_-_230621-G-MJ422-1003.jpg'), 'U.S. Coast Guard photo', g='film', nohud=True),
      V(502.28, TAIL, ROV, ss=50.0, trans='dip', nohud=True, ov=[DARK(502.3, 0.5), X(k='sonar', at=503.0, r=260, title='SEARCHING')]),
      V(505.42, TAIL, ROV, ss=6.0, trans='ping', nohud=True, ov=[BIG(505.5, 'JUNE 22', 'four days later'), LOWER('Odysseus 6000 ROV', 'Pelagic Research Services', 507.5, until=511.8)]),
      V(511.98, TAIL, ROV, ss=14.0, nohud=True),
      V(515.90, TAIL, ROV, ss=22.0, nohud=True, ov=[LAB('TITAN\'S TAIL CONE', 516.1, col=CYAN, size=56)]),
      V(517.52, AFT, ROV, ss=26.0, nohud=True),
      V(519.14, SALV, ROV, ss=30.0, nohud=True),
      V(521.44, LIFT, ROV, ss=70.0, nohud=True),
]
# ============================ THE VERDICT ============================
T += [V(523.74, PRESS, 'U.S. Coast Guard press briefing', ss=200.0, g='film', trans='whip', nohud=True, ov=[LAB('SO, WHAT WENT WRONG?', 524.0, size=56), O.label('LIKE IF YOU THINK THIS WAS PREVENTABLE', W // 2, 1000, 524.2, anchor='mm', color=CYAN, size=34, until=525.9)]),
      V(525.92, HEAR, 'U.S. Coast Guard hearing, Sept. 2024', ss=20.0, g='film', nohud=True, ov=[LOWER('Marine Board of Investigation', 'final report · August 2025', 526.4)]),
      DOC(533.30, 'report335', nohud=True, ov=[DARK(533.3, 0.6), STAT(533.4, 0, 335, 'pages', dur=0.8, y=320, size=170)]),
      DOC(535.94, 'preventable', nohud=True, kb=((0.5, 0.5, 1.1), (0.5, 0.5, 1.3))),
      DOC(539.48, 'primary', nohud=True),
      IMG(548.50, M('Titan_submersible_carbon_fiber_debris_(9057369).jpg'), 'Titan carbon fiber debris · U.S. Coast Guard photo', g='film', nohud=True, trans='push', ov=[LAB('FLAWS IN DESIGN & MANUFACTURING', 548.8, size=48)]),
      IMG(551.90, M('Titan_carbon_fiber_hull_sits_in_storage_(9057367).jpg'), 'U.S. Coast Guard photo', g='film', nohud=True, ov=[LAB('NO ANALYSIS OF HOW MANY DIVES THE HULL COULD SURVIVE', 552.2, size=40)]),
      DOC(556.14, 'strain', nohud=True, kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[LAB('SENSORS INSTEAD OF REAL INSPECTIONS', 556.4, col=RED, size=46)]),
      IMG(562.98, 'docs/img/p263-000.png', OGM, g='film', nohud=True, ov=[LAB('KEPT DIVING AFTER DAMAGING INCIDENTS', 563.2, size=46)]),
      DOC(566.50, 'firings', nohud=True, trans='glitch'),
      DOC(573.82, 'misrep', nohud=True),
      DOC(583.64, 'ceased', nohud=True, ov=[O.stamp('CEASED ALL OPERATIONS', 584.2, x=1350, y=320, size=90)]),
]
# ============================ PAYOFF + TRIBUTE + OUTRO ============================
T += [ANI(586.72, 596.0, trans='dip', zoom=(1.0, 1.15)),
      V(589.50, TAIL, ROV, ss=40.0, nohud=True, ov=[DARK(589.5, 0.4), CHAT([(589.6, 'TITAN', 'dropped two wts', '10:47:02')], keep=1), LAB('IT MEANT: EVERYTHING IS NORMAL', 590.8, col=CYAN, size=46)]),
      DOC(596.90, '26', nohud=True, trans='whip', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.35))),
      DOC(599.06, 'letter', nohud=True, trans='whip', kb=((0.5, 0.5, 1.3), (0.5, 0.5, 1.35))),
      IMG(600.90, 'docs/img/p263-000.png', OGM, g='film', nohud=True, trans='whip'),
      IMG(603.20, 'docs/img/p240-000.png', 'Photo · via ' + MBI, g='film', nohud=True, trans='whip'),
      IMG(605.52, 'docs/img/p16-000.png', 'Photo: ' + MBI, g='film', nohud=True, trans='whip'),
      V(609.14, AFT, ROV, ss=84.0, nohud=True, trans='dip', ov=[DARK(609.2, 0.45), Q('Every one of those warnings was heard.\nAnd every one of them was explained away.', 609.3, hl=['explained away.'], size=60)]),
      V(614.18, TAIL, ROV, ss=32.0, nohud=True, trans='dip', ov=[DARK(614.2, 0.6), X(k='names', at=S('Stockton', 616.1) - 0.1, step=1.2, names=['Stockton Rush', 'Paul-Henri Nargeolet', 'Hamish Harding', 'Shahzada Dawood', 'Suleman Dawood'])]),
      V(622.60, TAIL, ROV, ss=30.0, nohud=True, trans='dip', ov=[DARK(622.6, 0.5), O.label('LIKE  ·  COMMENT  ·  SUBSCRIBE', W // 2, 840, 623.0, anchor='mm', bg=False, size=50, until=641.0),
          O.type('SHOULD ANYONE TAKE PAYING PASSENGERS\nINTO THE DEEP WITHOUT CERTIFICATION?', S('Tell', 627.4) - 0.1, x=170, y=260, size=48, until=641.0)]),
      V(641.10, AFT, ROV, ss=10.0, nohud=True, trans='dip', ov=[DARK(641.1, 0.45), O.punch('WRECKLORE', 641.3, size=220, f='play', shake=False, color=WHITE, sub='every disaster leaves a lesson', until=645.5),
          O.label('WATCH NEXT', 520, 300, 646.0, color=WHITE, size=56), O.label('SUBSCRIBE', 1400, 300, 646.0, color=CYAN, size=56)], outfade=True),
]
END = 656.1
KEYS = [(50.3, 0, '08:30'), (109.2, 0, '08:30'), (121.2, 0, '09:14'), (126.0, 130, '09:18'),
        (239.08, 1038, '09:40'), (247.32, 1700, '09:53'), (258.22, 2050, '10:08'), (273.56, 2080, '10:09'),
        (353.82, 2833, '10:23'), (373.32, 2950, '10:25'),
        (420.56, 3341, '10:47:02'), (435.44, 3346, '10:47:08'), (443.04, 3346, '10:47:09')]
DIVE = [(50.3, 126.0), (239.08, 273.56), (353.82, 373.32), (420.56, 445.7)]
FLASH = [(126.0, 239.08), (273.56, 353.82), (373.32, 420.56)]
POST = fx4.depth_post(KEYS, DIVE, FLASH)

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render(T, END, sys.argv[4], float(sys.argv[2]), float(sys.argv[3]), log=True, post=POST)
    elif len(sys.argv) > 1 and sys.argv[1] == 'frames':
        for tt in map(float, sys.argv[3:]):
            render(T, END, f'{sys.argv[2]}_{tt:07.2f}.mp4', tt, tt + 1 / 30, post=POST)
