"""Deepwater Horizon edit: countdown thriller. usage: edit3.py render FROM TO OUT"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *
import fx3
from fx3 import TEAL, ORANGE, WHITE

WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')

RED = (255, 70, 50)
CG, NASA, CSB, NC = 'U.S. Coast Guard photo', 'NASA photo', 'U.S. Chemical Safety Board report', 'National Commission report (2011)'
def AI(t0, name, **k): return Shot(t0, ('ai', name), **k)                       # AI clips: no on-screen label (Studio disclosure is ticked)
def ST(t0, name, **k): return Shot(t0, ('img', f'ai/still/{name}.png'), mode='upscale', **k)
def IMG(t0, path, tag, **k): return Shot(t0, ('img', path), src_tag=tag, **k)
def DOC(t0, path, tag, kb, **k): return Shot(t0, ('img', path), mode='cover', kb=kb, grade='paper', grain=3.0, src_tag=tag, **k)
def V3(t0, **k): return Shot(t0, ('black',), grain=2.0, grade='none', **k)      # diagram / card on a dark plate
def X(**k): return k
def BIG(at, time, sub=None): return X(k='bigtime', at=at, time=time, sub=sub)
def Q(text, at, who='', hl=None, size=70): return O.quote(text, at, who=who, hl=hl or [], size=size)
def PUNCH(text, at, col=None, size=150, y=None): return O.punch(text, at, color=col or [WHITE, ORANGE], size=size, y=y, f='bebas')
def STAT(at, v0, v1, unit, dur=1.0, fmt='{:,.0f}', y=None, size=230): return X(k='stat', at=at, v0=v0, v1=v1, unit=unit, dur=dur, fmt=fmt, y=y or H // 2 - 40, size=size)
def CALL(pt, lab, text, at, sub=None, col=TEAL): return X(k='callout', pt=pt, lab=lab, text=text, at=at, sub=sub, color=col)

CLOCK = [(42.86, '05:45 AM', 345), (103.18, '11:00 AM', 660), (141.96, '04:00 PM', 960), (155.9, '05:00 PM', 1020), (190.72, '06:00 PM', 1080),
         (266.72, '08:02 PM', 1202), (283.46, '09:00 PM', 1260), (S('9:01', 293.5), '09:01 PM', 1261), (S('9:30', 306.5), '09:30 PM', 1290),
         (S('9:40', 320.5), '09:40 PM', 1300), (S('9:45', 346.5), '09:45 PM', 1305), (S('9:49', 354.5), '09:49 PM', 1309), (S('11:45', 443.5), '11:45 PM', 1425)]
WELL_LABELS = lambda at: [('MACONDO WELL', 760, 640, at + 0.4, ORANGE), ('~5,000 FT OF WATER', 1600, 420, at + 1.2, (120, 190, 255)),
                          ('13,000+ FT BELOW THE SEABED', 1600, 760, at + 2.6, (230, 200, 160))]
T = []
# ============================ HOOK (no black screen: open on the fire) ============================
T += [AI(0.0, 'd01_rig_fireball', grade='fire', zoom=(1.12, 1.0)),
      IMG(3.84, 'media/uscg_rig_burning.png', CG + ' · April 21, 2010', mode='upscale', grade='fire', kb=((0.45, 0.5, 1.25), (0.5, 0.45, 1.05)), trans='zoom',
          ov=[O.dark(4.0, amount=0.35), STAT(4.2, 0, 11, 'men never came home', dur=0.8)]),
      ST(6.52, 't02_celebration', trans='leak', grade='film', kb=((0.5, 0.5, 1.0), (0.52, 0.5, 1.15))),
      AI(10.16, 'd02_rig_dusk', grade='film', zoom=(1.0, 1.12), ov=[STAT(10.3, 0, 7, 'years without a lost-time incident', dur=0.7),
            O.label('"ONE OF THE TOP PERFORMING RIGS" — BP, that day', W // 2, 840, 13.6, anchor='mm', color=WHITE, size=40, bg=False)]),
      AI(17.86, 'd01_rig_fireball', ss=3.0, trans='glitch', grade='fire', zoom=(1.0, 1.15), ov=[O.dark(17.9, amount=0.35),
            PUNCH('THE SAFEST RIG IN THE GULF\nEXPLODED THE SAME NIGHT?', 18.0, size=120)]),
      AI(24.58, 'd05_control_gauges', trans='push', grade='night', zoom=(1.0, 1.25)),
      ST(28.26, 't05_gauge_1400', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.35))),
      AI(30.74, 'd04_drill_floor', grade='night', zoom=(1.0, 1.1)),
      ST(32.56, 't04_control_room', trans='glitch', grade='night', kb=((0.5, 0.5, 1.2), (0.5, 0.5, 1.0)), ov=[O.label('…AND EXPLAINED IT AWAY', W // 2, 840, 33.0, anchor='mm', color=ORANGE, bg=False, size=54)]),
      AI(35.12, 'd02_rig_dusk', ss=3.0, trans='leak', grade='film', zoom=(1.15, 1.0), nohud=True, ov=[O.dark(35.2, amount=0.35),
            O.punch('DEEPWATER HORIZON', 35.4, size=170, f='play', shake=False, color=WHITE, sub='the last 16 hours')]),
      V3(41.07, nohud=True, ov=[BIG(41.15, '5:45 AM', 'tuesday, april 20, 2010')]),
]
# ============================ 05:45 — THE RIG ============================
T += [IMG(48.18, 'media/csb_map.png', CSB, mode='contain', grade='paper', kb=((0.5, 0.5, 1.0), (0.62, 0.55, 1.6)), trans='push',
          ov=[O.label('≈ 50 MILES OFF LOUISIANA', W // 2, 860, 49.0, anchor='mm', color=ORANGE)]),
      AI(53.66, 'd02_rig_dusk', ss=1.0, grade='night', zoom=(1.0, 1.08), ov=[O.lower('Deepwater Horizon', 'drilling rig · owned by Transocean · working for BP', 53.8, until=58.6)]),
      ST(55.46, 't03_derrick_low', grade='night', kb=((0.5, 0.6, 1.0), (0.5, 0.4, 1.2)), ov=[CALL((960, 300), (1250, 260), 'THE DERRICK', 56.5, '20+ stories tall')]),
      ST(61.76, 't01_crew_mess', trans='zoom', grade='film', kb=((0.5, 0.5, 1.15), (0.5, 0.5, 1.0)), ov=[O.dark(61.8, amount=0.3), STAT(61.9, 0, 126, 'people on board · 13 companies', dur=1.0)]),
      AI(64.96, 'd06_pipe_ocean_depth', grade='cold', zoom=(1.0, 1.2), ov=[O.label('4,992 FT OF WATER', W // 2, 840, 65.3, anchor='mm', color=(120, 190, 255), size=56)]),
      V3(67.58, ov=[X(k='well', at=67.58, labels=WELL_LABELS(67.58))], src_tag='Diagram · not to scale'),
      AI(77.34, 'd26_drill_pipe_spin', trans='push', grade='night', zoom=(1.0, 1.15)),
      IMG(86.04, 'media/csb_cement.png', CSB, mode='contain', grade='paper', kb=((0.5, 0.75, 1.3), (0.5, 0.85, 1.9)),
          ov=[O.label('CEMENT = THE CORK IN THE BOTTLE', W // 2, 860, 87.5, anchor='mm', color=ORANGE)]),
      DOC(92.36, 'media/doc_email.png', NC, ((0.45, 0.6, 1.0), (0.4, 0.75, 1.4)), trans='push'),
      Shot(99.46, ('img', 'media/doc_email.png'), mode='cover', grade='paper', src_tag=NC, kb=((0.4, 0.75, 1.4), (0.4, 0.75, 1.5)),
           ov=[O.dark(99.5, amount=0.5), PUNCH('REMEMBER THIS SENTENCE.', 99.6, col=[ORANGE], size=130)]),
]
# ============================ 11:00 — THE SKIPPED CHECK ============================
T += [AI(103.18, 'd03_helicopter', trans='leak', grade='film', zoom=(1.0, 1.1), nohud=False, ov=[O.dark(103.2, amount=0.25, until=104.8), BIG(103.25, '11:00 AM')]),
      AI(104.82, 'd26_drill_pipe_spin', ss=3.0, grade='night', zoom=(1.15, 1.0), ov=[O.type('A TEAM THAT COULD TEST THE CEMENT\n→ SENT HOME ON THE 11:00 HELICOPTER', 105.2, x=110, y=760, size=40, cps=28)]),
      DOC(113.94, 'media/doc_128k.png', NC, ((0.4, 0.4, 1.0), (0.35, 0.45, 1.4))),
      AI(119.26, 'd03_helicopter', ss=2.0, grade='film', zoom=(1.0, 1.25), ov=[O.dark(119.3, amount=0.3), STAT(119.4, 0, 128000, 'saved by skipping the check', fmt='${:,.0f}', dur=1.2)]),
      AI(124.74, 'd22_waves_dawn', grade='film', zoom=(1.0, 1.1), ov=[O.label('THE ONE TEST THAT COULD LOOK INSIDE THE WELL — GONE', W // 2, 840, 125.2, anchor='mm', size=44, color=ORANGE, bg=False)]),
]
# ============================ AFTERNOON — THE VIPs ============================
T += [AI(129.16, 'd03_helicopter', ss=5.0, trans='push', grade='film', zoom=(1.1, 1.2)),
      ST(132.16, 't02_celebration', grade='film', kb=((0.4, 0.5, 1.0), (0.55, 0.5, 1.2)), ov=[CALL((700, 520), (1100, 330), '4 EXECUTIVES', 133.0, 'BP + Transocean · "management visibility tour"', col=ORANGE)]),
      AI(141.96, 'd02_rig_dusk', ss=4.0, grade='film', zoom=(1.2, 1.05)),
      AI(143.26, 'd21_office_meeting', grade='film', zoom=(1.0, 1.12), ov=[O.type('TOPIC: SLIPS · FALLS · DROPPED TOOLS', S('slips', 147.5) - 0.2, x=110, y=780, size=44)]),
      AI(150.7, 'd08_mud_eruption', trans='glitch', grade='night', zoom=(1.0, 1.1), ov=[O.label('THE REAL DANGER WAS SOMEWHERE ELSE', W // 2, 840, 152.6, anchor='mm', color=RED, size=50, bg=False)]),
]
# ============================ 17:00 — THE TEST ============================
T += [AI(155.9, 'd04_drill_floor', trans='leak', grade='night', zoom=(1.0, 1.12), ov=[O.dark(155.9, amount=0.3, until=157.6), BIG(155.95, '5:00 PM', 'the most important test of the day'),
            O.lower('Negative pressure test', 'does the well stay sealed?', 158.5, until=162.2)]),
      V3(162.38, src_tag='Analogy', ov=[X(k='bottle', at=162.4, vals=[(162.4, 0), (S('pull', 167), 0), (S('zero', 171), 0), (S('creeping', 174), 0), (175.6, 55)], vmax=100, warn=20,
            notes=[('SEAL THE BOTTLE · DROP THE PRESSURE', 162.6, WHITE), ('GOOD SEAL → STAYS AT ZERO', S('seal', 170) - 0.2, TEAL), ('CREEPS UP → SOMETHING IS LEAKING IN', S('creeping', 174) - 0.2, RED)])]),
      AI(176.82, 'd05_control_gauges', trans='push', grade='night', zoom=(1.0, 1.15)),
      V3(179.3, src_tag='Illustrative · based on the National Commission report', ov=[X(k='chart', at=179.4, dur=10.5, box=(420, 300, 1080, 520), vmax=1600, title='DRILL PIPE PRESSURE (PSI) · 5–6 PM',
            series=[dict(pts=[(0, 0), (0.06, 0), (0.25, 900), (0.3, 0), (0.5, 1000), (0.55, 0), (0.78, 1150), (0.82, 0), (1.0, 900)], color=ORANGE, label='BLEED · CLIMB · BLEED · CLIMB')],
            marks=[(0.06, 'BLEED', 180.0), (0.3, 'AGAIN', S('again', 185.5)), (0.55, 'A THIRD TIME', S('third', 188.5))])]),
      AI(190.72, 'd04_drill_floor', ss=3.0, grade='night', zoom=(1.1, 1.25), ov=[O.label('SHIFT CHANGE · CROWDED DRILL SHACK', W // 2, 840, 191.0, anchor='mm', bg=False, size=46)]),
      ST(195.06, 't02_celebration', grade='night', kb=((0.6, 0.5, 1.2), (0.5, 0.5, 1.35)), ov=[O.dark(195.1, amount=0.4),
            Q('Looks like they’re having a discussion here.', 198.7, who='Transocean manager, on the tour (National Commission)', hl=['a discussion'], size=66)]),
      ST(203.46, 't04_control_room', trans='glitch', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[O.dark(203.5, amount=0.4), PUNCH("NOW HERE'S WHERE\nIT GETS DANGEROUS", 203.55, size=140)]),
      V3(206.26, src_tag='Illustrative · values from the National Commission report', ov=[X(k='chart', at=206.4, dur=8.5, box=(420, 300, 1080, 520), vmax=1600, title='SECOND TEST · ~6–7 PM',
            series=[dict(pts=[(0, 1400), (1.0, 1400)], color=ORANGE, label='DRILL PIPE: 1,400 PSI', labat=0.5), dict(pts=[(0, 0), (1.0, 0)], color=TEAL, label='KILL LINE: 0 PSI', labat=0.3)]),
            O.label('TWO READINGS THAT SHOULD MATCH', W // 2, 900, S('match', 219.5) - 0.4, anchor='mm', color=RED, size=48, bg=False)]),
      ST(221.38, 't04_control_room', grade='night', kb=((0.5, 0.5, 1.25), (0.45, 0.5, 1.45)), ov=[O.dark(221.4, amount=0.55),
            PUNCH('"THE BLADDER EFFECT"', S('bladder', 227) - 0.2, col=[ORANGE], size=170), O.label('A respected toolpusher\'s explanation, per BP witnesses', W // 2, 760, 222.0, anchor='mm', bg=False, size=36, color=WHITE)]),
      DOC(231.04, 'media/doc_bladder.png', NC + ', ch. 4 note 141', ((0.45, 0.35, 1.0), (0.38, 0.3, 1.45)), trans='push'),
      AI(240.82, 'd05_control_gauges', ss=2.0, grade='night', zoom=(1.3, 1.1), ov=[O.dark(240.9, amount=0.45),
            O.type('NEGATIVE PRESSURE TEST . . . RESULT: PASS', S('declared', 245.5) - 0.8, x=330, y=480, size=56, cps=26, color=(120, 255, 140))]),
]
# ============================ MYTH vs FACT · SWISS CHEESE ============================
T += [V3(247.04, nohud=True, ov=[PUNCH('MYTH', 247.1, col=[RED], size=160, y=330), O.type('ONE PERSON MADE ONE TERRIBLE MISTAKE', S('Myth', 249.5), x=330, y=470, size=52, box=False),
            O.label('FACT: A CHAIN OF FAILURES', W // 2, 700, S('Fact', 252.5), anchor='mm', color=TEAL, size=64, bg=False)]),
      V3(255.32, nohud=True, src_tag='The "Swiss cheese" model of accidents', ov=[X(k='cheese', at=255.32, names=['CEMENT\nFAILED', 'CEMENT CHECK\nSKIPPED', 'PRESSURE TEST\nMISREAD', 'KICK\nMISSED', 'BLOWOUT PREVENTER\nFAILED'],
            align=S('lined', 263), arrow=S('Swiss', 265) - 0.2)]),
]
# ============================ 20:02 → 21:49 ============================
T += [V3(266.72, ov=[BIG(266.75, '8:02 PM', 'heavy mud out · seawater in'), ]),
      V3(268.7, src_tag='Diagram · not to scale', ov=[X(k='well', at=268.7, disp=(269.5, 279.0), cement_fail=S('failing', 282), labels=[('HEAVY MUD = THE WEIGHT', 760, 760, 270.5, (230, 170, 120)),
            ('SEAWATER (LIGHTER)', 1600, 330, 271.5, (120, 190, 255)), ('CEMENT FAILING', 760, 960, S('failing', 282) - 0.3, RED)])]),
      ST(283.46, 't08_bridge_panel', trans='push', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[O.label('9:00 PM · THE VIPs TOUR THE BRIDGE', W // 2, 840, 285.0, anchor='mm', bg=False, size=46)]),
      V3(290.12, src_tag='Diagram · not to scale', ov=[X(k='well', at=290.12, disp=(289.0, 289.5), gas=(S('9:01', 293.5), 304.0), cement_fail=290.1,
            labels=[('9:01 PM · PRESSURE RISING', 760, 520, S('9:01', 293.5) + 0.3, RED), ('A "KICK": OIL & GAS COMING UP', 1600, 640, S('kick', 300.5) - 0.2, ORANGE)])]),
      ST(304.2, 't04_control_room', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), ov=[O.dark(304.25, amount=0.5), PUNCH('NOBODY CATCHES IT.', 304.3, col=[WHITE], size=150)]),
      AI(306.28, 'd05_control_gauges', ss=1.0, grade='night', zoom=(1.0, 1.3), ov=[O.type('9:30 PM · DRILL PIPE ≠ KILL LINE', 306.6, x=110, y=780, size=46)]),
      AI(316.62, 'd25_storm_sea', grade='night', zoom=(1.0, 1.15), ov=[PUNCH('ABOUT 10 MINUTES LEFT', 316.7, col=[RED], size=130)]),
      AI(320.2, 'd08_mud_eruption', trans='flash', grade='night', zoom=(1.0, 1.2)),
      AI(328.89, 'd08_mud_eruption', ss=4.0, grade='night', zoom=(1.2, 1.35)),
      AI(331.06, 'd26_drill_pipe_spin', ss=1.0, trans='push', grade='night', speed=1.4, zoom=(1.2, 1.0)),
      V3(337.28, src_tag='Diagram · not to scale', ov=[X(k='well', at=337.28, disp=(336.0, 336.5), gas=(337.3, 341.5), cement_fail=337.3, labels=[('GAS ABOVE THE PREVENTER', 1600, 430, 337.8, RED)])]),
      AI(342.34, 'd09_alarm_lights', trans='glitch', grade='night', zoom=(1.0, 1.15)),
      ST(346.34, 't03_derrick_low', grade='night', kb=((0.5, 0.7, 1.1), (0.5, 0.2, 1.4)), ov=[O.dark(346.4, amount=0.35),
            O.type('9:45 PM · "WE HAVE MUD GOING TO THE CROWN."', 346.8, x=110, y=780, size=44, cps=26)]),
      V3(354.1, nohud=True, ov=[BIG(354.15, '9:49 PM', 'the gas finds a spark')]),
      AI(358.47, 'd10_explosion_night', trans='flash', grade='fire', zoom=(1.0, 1.25), nohud=True),
      Shot(362.26, ('black',), grain=10.0, nohud=True),
      AI(363.78, 'd01_rig_fireball', ss=2.0, trans='flash', grade='fire', zoom=(1.2, 1.0)),
      AI(366.86, 'd09_alarm_lights', ss=3.0, grade='night', zoom=(1.2, 1.3), ov=[O.dark(366.9, amount=0.4), O.type('"THIS IS NOT A DRILL."', 368.2, x=500, y=480, size=70, cps=14, box=False, color=RED)]),
]
# ============================ THE LAST LINE OF DEFENSE ============================
T += [AI(373.2, 'd07_seabed_bop', trans='leak', grade='cold', zoom=(1.0, 1.15)),
      IMG(379.56, 'media/csb_bop.png', CSB, mode='contain', grade='paper', kb=((0.5, 0.4, 1.0), (0.5, 0.55, 1.35)),
          ov=[O.label('57 FT TALL', 1500, 380, 380.0, color=ORANGE, size=56), O.label('≈ 400 TONS', 1500, 480, S('four', 382.5), color=ORANGE, size=56),
              O.label('JOB: CUT THE PIPE · SEAL THE WELL', W // 2, 880, 385.2, anchor='mm', color=WHITE, size=46)]),
      ST(390.76, 't08_bridge_panel', trans='push', grade='night', kb=((0.5, 0.5, 1.2), (0.5, 0.5, 1.45)), ov=[O.label('EMERGENCY DISCONNECT', W // 2, 840, 391.5, anchor='mm', color=RED, size=50, bg=False)]),
      ST(395.26, 't08_bridge_panel', trans='glitch', grade='cold', kb=((0.5, 0.5, 1.45), (0.5, 0.5, 1.45)), ov=[O.dark(395.3, amount=0.55), PUNCH('NOTHING HAPPENS.', 395.35, col=[WHITE], size=150)]),
      AI(399.96, 'd07_seabed_bop', ss=3.0, grade='cold', zoom=(1.2, 1.35), ov=[O.label('AUTOMATIC BACKUP: LIKELY FIRED', W // 2, 840, 404.0, anchor='mm', color=TEAL, size=46, bg=False)]),
      IMG(405.86, 'media/csb_bop.png', CSB + ', vol. 2', mode='contain', grade='paper', kb=((0.5, 0.55, 1.35), (0.5, 0.6, 1.9)),
          ov=[O.label('THE DRILL PIPE HAD BUCKLED · BLADES COULDN\'T SEAL', W // 2, 880, 406.5, anchor='mm', color=RED, size=44)]),
      AI(414.04, 'd17_underwater_leak', grade='cold', zoom=(1.0, 1.15)),
]
# ============================ ESCAPE ============================
T += [AI(416.72, 'd11_lifeboat', trans='push', grade='fire', zoom=(1.0, 1.12)),
      AI(428.2, 'd12_jump_sea', trans='flash', grade='fire', zoom=(1.15, 1.0)),
      AI(433.0, 'd13_supply_boat', grade='night', zoom=(1.0, 1.12), ov=[O.lower('Damon B. Bankston', 'offshore supply vessel', 433.4, until=442.8)]),
      ST(443.16, 't07_lifeboat_sea', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[O.label('11:45 PM · THE LIFEBOATS ARE EMPTY', W // 2, 840, 443.4, anchor='mm', size=46, bg=False)]),
      V3(446.98, nohud=True, ov=[STAT(447.1, 0, 11, 'men missing', dur=0.8)]),
      AI(451.42, 'd25_storm_sea', ss=4.0, trans='dip', grade='night', zoom=(1.0, 1.1), nohud=True, ov=[O.label('THEY WERE NEVER FOUND.', W // 2, 840, 451.6, anchor='mm', size=54, bg=False)]),
      ST(454.98, 't11_family_dock', grade='night', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), nohud=True, ov=[STAT(455.1, 0, 115, 'survived', dur=1.0, y=420)]),
      IMG(462.72, 'media/uscg_fireboats.png', CG + ' · April 21, 2010', mode='upscale', grade='fire', kb=((0.5, 0.45, 1.0), (0.5, 0.45, 1.3)), trans='push', nohud=True,
          ov=[O.label('BURNED FOR ABOUT 36 HOURS', W // 2, 860, 463.0, anchor='mm', color=ORANGE, size=50)]),
      AI(466.72, 'd15_rig_sinking', grade='cold', zoom=(1.0, 1.12), nohud=True, ov=[O.label('APRIL 22 · EARTH DAY', W // 2, 840, 467.5, anchor='mm', size=50, bg=False)]),
]
# ============================ 87 DAYS ============================
T += [AI(470.92, 'd17_underwater_leak', ss=2.0, trans='glitch', grade='cold', zoom=(1.0, 1.2), nohud=True, ov=[STAT(S('eighty-seven', 476.6) - 0.2, 0, 87, 'days of oil and gas', dur=1.2)]),
      AI(481.36, 'd20_containment_boom', grade='film', zoom=(1.0, 1.12), nohud=True, ov=[O.type('DOMES · JUNK SHOT · TOP KILL', 481.5, x=110, y=780, size=46),
            O.label('CAPPED: JULY 15, 2010', W // 2, 300, S('July', 487), anchor='mm', color=TEAL, size=56)]),
      AI(489.9, 'd16_oil_slick_aerial', grade='film', zoom=(1.0, 1.15), nohud=True, ov=[O.label('3.2 – 5 MILLION BARRELS', W // 2, 840, 490.4, anchor='mm', color=ORANGE, size=64, bg=False)]),
      AI(494.3, 'd19_pelican', grade='film', zoom=(1.0, 1.1), nohud=True),
      IMG(499.46, 'media/nasa_iss023e032397.jpg', NASA + ' from the ISS · May 4, 2010', mode='upscale', grade='film', kb=((0.5, 0.45, 1.0), (0.45, 0.4, 1.35)), trans='zoom', nohud=True),
]
# ============================ WHY ============================
T += [AI(502.06, 'd21_office_meeting', ss=2.0, trans='leak', grade='film', zoom=(1.1, 1.0), nohud=True, ov=[PUNCH('SO, WHY DID IT HAPPEN?', 502.1, col=[WHITE], size=140)]),
      DOC(507.2, 'media/doc_csb_personal.png', CSB + ' · executive summary', ((0.5, 0.3, 1.0), (0.55, 0.3, 1.4)), nohud=True),
      ST(516.8, 't01_crew_mess', grade='film', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), nohud=True, ov=[O.type('MEASURED: SLIPS · TRIPS · FALLS', 516.9, x=110, y=780, size=46)]),
      V3(523.1, nohud=True, src_tag='Diagram · not to scale', ov=[X(k='well', at=523.1, disp=(522.0, 522.5), gas=(523.3, 534.0), cement_fail=523.1,
            labels=[('THE REAL RISK: A WELL UNDER PRESSURE', 1600, 430, 526.6, ORANGE), ('PROCESS SAFETY', 760, 640, S('process', 532) - 0.2, RED)])]),
      ST(535.7, 't02_celebration', trans='leak', grade='film', kb=((0.5, 0.5, 1.2), (0.5, 0.5, 1.0)), nohud=True, ov=[STAT(535.8, 0, 7, 'years without a lost-time incident', dur=0.6)]),
      V3(541.18, nohud=True, ov=[STAT(541.3, 0, 11, 'lives lost that night', dur=0.8)]),
      DOC(545.12, 'media/doc_email.png', NC, ((0.4, 0.75, 1.4), (0.4, 0.75, 1.6)), trans='glitch', nohud=True),
      V3(551.28, nohud=True, src_tag='The "Swiss cheese" model of accidents', ov=[X(k='cheese', at=551.3, names=['CEMENT\nFAILED', 'CEMENT CHECK\nSKIPPED', 'PRESSURE TEST\nMISREAD', 'KICK\nMISSED', 'BLOWOUT PREVENTER\nFAILED'],
            align=553.0, arrow=S('missed', 559) - 0.4)]),
      AI(560.44, 'd24_courtroom', trans='push', grade='film', zoom=(1.0, 1.12), nohud=True, ov=[O.type('NEW RULES:\n• NEGATIVE PRESSURE TESTS REQUIRED\n• NEW BLOWOUT PREVENTER STANDARDS', 566.2, x=110, y=640, size=42, cps=30)]),
      AI(573.79, 'd24_courtroom', ss=3.0, grade='film', zoom=(1.12, 1.2), nohud=True, ov=[O.label('BILLIONS IN FINES AND SETTLEMENTS', W // 2, 840, 574.0, anchor='mm', size=50, bg=False)]),
]
# ============================ TRIBUTE + OUTRO ============================
T += [AI(577.82, 'd23_memorial_candles', trans='dip', grade='film', zoom=(1.0, 1.1), nohud=True),
      AI(581.5, 'd22_waves_dawn', grade='film', zoom=(1.0, 1.08), nohud=True, ov=[O.dark(581.5, amount=0.55),
            X(k='names', at=581.76, step=1.0, names=['Jason Anderson', 'Dale Burkeen', 'Donald Clark', 'Stephen Curtis', 'Gordon Jones', 'Roy Wyatt Kemp', 'Karl Kleppinger', 'Blair Manuel', 'Dewey Revette', 'Shane Roshto', 'Adam Weise'])]),
      AI(595.96, 'd22_waves_dawn', ss=4.0, trans='dip', grade='film', zoom=(1.08, 1.15), nohud=True, ov=[O.dark(596.0, amount=0.35),
            Q("The most dangerous warning is the one we've already decided to explain away.", 596.2, hl=['explain away.'], size=70)]),
      AI(601.02, 'd02_rig_dusk', ss=2.0, trans='leak', grade='film', zoom=(1.0, 1.15), nohud=True, ov=[O.label('LIKE  ·  COMMENT  ·  SUBSCRIBE', W // 2, 840, 601.5, anchor='mm', until=613.0, bg=False, size=50),
            O.type('SHOULD A RIG EVER STOP WORK\nBECAUSE ONE READING DOESN\'T MAKE SENSE?', S('Tell', 607.8) - 0.1, x=200, y=260, size=50, until=613.0)]),
      ST(613.16, 't12_ocean_horizon', grade='film', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.12)), nohud=True, ov=[O.punch('WRECKLORE', 613.3, size=220, f='play', shake=False, color=WHITE, sub='every disaster leaves a lesson')]),
      AI(622.5, 'd22_waves_dawn', ss=1.0, trans='dip', grade='film', zoom=(1.0, 1.06), outfade=True, nohud=True, ov=[O.dark(622.5, amount=0.55),
            O.label('WATCH NEXT', 520, 300, 623.0, color=WHITE, size=56), O.label('SUBSCRIBE', 1400, 300, 623.0, color=ORANGE, size=56)]),
]
END = 637.5
POST = fx3.clock_post(CLOCK, (42.8, 451.0))
INTRO_NOTE = [O.label('Some scenes are dramatized with AI visualizations.', W // 2, H - 150, 0.3, until=3.6, anchor='mm', color=(220, 220, 220), size=26, bg=False)]
T[0].ov += INTRO_NOTE

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render(T, END, sys.argv[4], float(sys.argv[2]), float(sys.argv[3]), log=True, post=POST)
