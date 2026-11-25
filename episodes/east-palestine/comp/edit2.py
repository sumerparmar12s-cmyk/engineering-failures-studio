"""East Palestine v2 edit: footage-first timeline (absolute VO seconds). usage: edit2.py [render FROM TO OUT] | [sfx]"""
import sys, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import *

WORDS = json.load(open(f'{ROOT}/vo/vo.mp3.words.json'))
def S(word, near, tol=1.5):
    n = lambda x: re.sub(r'[^a-z0-9]', '', x.lower())
    for x in WORDS:
        if x['s'] >= near - tol and n(x['w']) == n(word): return x['s']
    raise SystemExit(f'word not found {word} {near}')

R = 'NTSB report RIR-24-05'; NP = 'NTSB photo'; D3 = '3D reconstruction'
RED, YEL, WHT = (235, 45, 35), (255, 214, 64), (255, 255, 255)
def AI(t0, name, **k): return Shot(t0, ('ai', name), ai=True, **k)
def IMG(t0, path, **k): return Shot(t0, ('img', path), **k)
def V3(t0, name, ss=0.0, **k): return Shot(t0, ('vid', f'real3d/{name}.mp4'), ss=ss, src_tag=D3, zoom=(1.0, 1.0), **k)
def STILL(t0, name, **k): return Shot(t0, ('img', f'ai/still/{name}.png'), mode='upscale', ai=True, **k)
def DOC(t0, path, kb, **k): return Shot(t0, ('img', path), mode='cover', kb=kb, grade='paper', grain=3.0, src_tag=R, **k)

# map canvas coordinates (contain canvas 2400x1350)
HBD = dict(seb=(397, 494), sal=(1003, 647), ep=(2059, 878))
ROUTE_MARKS = [(255, 1059, 'MADISON, ILLINOIS', 0, YEL), (2053, 444, 'EAST PALESTINE, OHIO', 0, RED)]

T = []
# ======================= COLD OPEN =======================
T += [AI(0.0, 'v02_town_smoke', trans='fade', grade='cold', zoom=(1.0, 1.08), ov=[O.type('FEBRUARY 6, 2023', 0.4, x=90, y=90, size=44)]),
      AI(3.72, 'v22_clock', grade='cold', zoom=(1.05, 1.18), ov=[O.type('4:37 P.M.', 3.9, x=90, y=90, size=56)]),
      AI(6.08, 'v28_town_aerial', grade='cold', zoom=(1.0, 1.1), ov=[O.lower('East Palestine, Ohio', 'population 4,761 · U.S. Census 2020', 6.6, until=10.6)]),
      AI(10.0, 'v25_old_tankcars', grade='cold', zoom=(1.0, 1.12)),
      V3(11.2, 'T5', ss=6.85, trans='flash', grade='film'),
      AI(14.46, 'v01_fireball', grade='fire', zoom=(1.0, 1.1), ov=[O.counter(S('nine', 17) - 0.2, 0, 887400, 1.6, 'pounds of vinyl chloride', y=430)]),
      AI(21.5, 'v04_tank_flames', grade='fire', zoom=(1.12, 1.22), ov=[O.label('A CHEMICAL THAT CAUSES CANCER', 960, 900, S('causes', 22.2) - 0.2, anchor='mm', color=WHT, size=48)]),
      AI(26.2, 'v03_column', trans='flash', grade='cold', zoom=(1.0, 1.15), ov=[O.bars(26.2), O.punch('ON PURPOSE.', 26.4, color=RED, size=210)]),
      STILL(28.9, 's13_wreck_day', grade='cold', kb=((0.5, 0.5, 1.0), (0.45, 0.55, 1.2)), ov=[O.dark(29.0, amount=0.3),
            O.quote('The only way to stop a massive explosion.', 29.2, who='what officials were told', hl=['massive explosion'], size=74)]),
      AI(34.18, 'v24_report_desk', grade='film', zoom=(1.0, 1.1), ov=[O.lower('NTSB final report', 'Railroad Investigation Report RIR-24-05 · June 2024', 34.6, until=39.1)]),
      DOC(39.3, 'media/doc_notnecessary.png', ((0.5, 0.5, 1.0), (0.42, 0.46, 1.9)), trans='glitch', ov=[O.stamp('NEVER GOING TO HAPPEN', 40.2, x=1180, y=760, size=96)]),
      DOC(41.84, 'media/doc_oxyquote.png', ((0.5, 0.42, 1.25), (0.42, 0.33, 2.0)), ov=[O.label('THE CHEMICAL\'S MAKER, BEFORE THE BURN', 960, 120, 42.4, anchor='mm')]),
      AI(47.24, 'v23_crowd_watch', grade='cold', zoom=(1.0, 1.12), ov=[O.punch('SO WHY DID\nNO ONE LISTEN?', 47.4, color=[WHT, RED], size=170)]),
      AI(49.32, 'v05_wheel_sparks', trans='glitch', grade='fire', speed=0.8, ov=[O.type('3 DAYS EARLIER', 49.5, x=90, y=90, size=54), O.label('ONE TINY PART', 960, 920, S('tiny', 52.5) - 0.2, anchor='mm')]),
      V3(53.8, 'T2', ss=3.0, grade='night'),
      AI(56.36, 'v07_town_night', trans='flash', grade='night', zoom=(1.08, 1.0), ov=[O.dark(56.4, amount=0.35),
            O.punch('EAST PALESTINE', 56.5, size=200, f='play', shake=False, sub="the burn that didn't have to happen")]),
]
# ======================= CHAPTER 1 · THE TRAIN =======================
T += [AI(59.54, 'v06_train_town_night', trans='whip', grade='night', zoom=(1.0, 1.1), ov=[O.chapter(1, 'The Train', 59.7, until=64.5)]),
      IMG(64.0, 'media/ntsb_town.png', mode='upscale', src_tag=NP + ' · ' + R, kb=((0.5, 0.5, 1.0), (0.42, 0.42, 1.45)),
          ov=[O.label('THE TRACKS RUN RIGHT THROUGH TOWN', 960, 930, 64.6, anchor='mm')]),
      AI(67.44, 'v06_train_town_night', ss=4.0, grade='night', zoom=(1.12, 1.0)),
      AI(72.44, 'v08_loco_headlight', grade='night', zoom=(1.0, 1.12), ov=[O.lower('Norfolk Southern train 32N', 'Friday, February 3, 2023 · night', 72.8, until=76.0)]),
      V3(76.08, 'T1', ss=0.5, grade='night', ov=[O.counter(76.2, 0, 3, 0.4, 'locomotives', until=77.6, y=420), O.counter(77.7, 0, 149, 1.0, 'freight cars', until=80.8, y=420),
                                                  O.counter(80.9, 0, 17977, 1.2, 'tons · about 1¾ miles long', y=420)]),
      Shot(85.54, ('route', 'media/ntsb_route.png'), trans='whip', grade='paper', src_tag=R + ', fig. 2', rev=(86.2, 90.6), follow=False,
           kb=((0.12, 0.75, 1.5), (0.8, 0.35, 1.25)), marks=[ROUTE_MARKS[0][:3] + (85.7, YEL), ROUTE_MARKS[1][:3] + (89.6, RED)]),
      AI(91.04, 'v10_cab_night', grade='night', zoom=(1.0, 1.08), ov=[O.dark(91.1, amount=0.25),
            O.type('ENGINEER · 24 YEARS\nCONDUCTOR\nCONDUCTOR TRAINEE', S('engineer', 93) - 0.2, x=110, y=720, size=46, cps=20)]),
      AI(98.38, 'v11_bearing_glow', trans='glitch', grade='fire', zoom=(1.0, 1.15), ov=[O.punch('CAR #23\nIS ON FIRE', S('fire', 101) - 0.3, color=[WHT, RED], size=180)]),
      STILL(102.22, 's01_hopper', grade='night', kb=((0.5, 0.5, 1.0), (0.55, 0.55, 1.15)), ov=[O.label('HOPPER CAR · PLASTIC PELLETS', 960, 930, 102.8, anchor='mm')]),
      IMG(106.74, 'media/ntsb_wheelset_diag.png', mode='contain', grade='paper', src_tag=R + ', fig. 4', kb=((0.5, 0.5, 1.0), (0.78, 0.6, 1.9)),
          ov=[O.label('L1 BEARING', 1500, 250, S('failing', 108.5) - 0.1, color=RED, size=60)]),
      V3(109.82, 'T3', ss=0.0, grade='film'),
      IMG(121.8, 'media/ntsb_cup.png', mode='upscale', src_tag=NP + ' · ' + R + ', fig. 18', kb=((0.5, 0.5, 1.05), (0.45, 0.5, 1.35)),
          ov=[O.circle((640, 260, 1320, 860), 122.2), O.punch('VERY HOT.', S('Very', 124) - 0.05, y=960, size=120, color=RED)]),
      STILL(126.0, 's02_detector', grade='night', kb=((0.5, 0.55, 1.0), (0.5, 0.6, 1.2)), ov=[O.lower('Hot bearing detector', 'reads the temperature of every wheel', 128.2, until=132.6)]),
      IMG(132.7, 'media/ntsb_hbd_photo.png', mode='upscale', src_tag=NP + ' · ' + R + ', fig. 13', kb=((0.5, 0.6, 1.0), (0.5, 0.62, 1.3))),
]
# ======================= CHAPTER 2 · THE WARNINGS =======================
T += [AI(137.38, 'v09_rails_rolling', trans='whip', grade='night', speed=0.8, ov=[O.chapter(2, 'The Warnings', 137.5, until=140.2)]),
      Shot(140.32, ('route', 'media/ntsb_hbd_map.png'), trans='flash', grade='paper', src_tag=R + ', fig. 3', rev=(140.4, 146.0), xr=(126, 397), follow=True,
           kb=((0, 0, 1.9), (0, 0, 2.1)), marks=[HBD['seb'] + ('SEBRING · 7:37 P.M.\n+38°F · NO ALERT', 145.9, YEL)]),
      Shot(151.34, ('route', 'media/ntsb_hbd_map.png'), grade='paper', src_tag=R + ', fig. 3', rev=(151.4, 156.0), xr=(397, 1003), follow=True,
           kb=((0, 0, 1.9), (0, 0, 2.0)), marks=[HBD['seb'] + ('SEBRING\n+38°F', 151.3, YEL), HBD['sal'] + ('SALEM · 8:13 P.M.\n+103°F', S('hundred', 156.5) - 0.2, RED)]),
      AI(159.9, 'v12_desk_monitor', grade='cold', zoom=(1.0, 1.1), ov=[O.type('NON-CRITICAL ALERT\n→ HELP DESK ANALYST', 160.0, x=110, y=760, size=46),
            O.stamp('NOT TO THE CREW', S('crew', 168.5) - 0.2, x=1300, y=360, size=100)]),
      STILL(169.4, 's03_camera_pole', trans='glitch', grade='night', kb=((0.5, 0.5, 1.15), (0.5, 0.45, 1.3)), ov=[O.punch('BUT WAIT.', 169.45, color=RED, size=200)]),
      AI(174.04, 'v13_train_sparks', grade='night', zoom=(1.0, 1.1)),
      V3(178.1, 'T2', ss=2.0, grade='night', ov=[O.type('NTSB: SALEM CAMERAS SHOWED FIRE ON THIS WHEELSET', 178.3, x=90, y=90, size=36)]),
      Shot(180.8, ('route', 'media/ntsb_hbd_map.png'), trans='whip', grade='paper', src_tag=R + ', fig. 3', rev=(180.9, 185.5), xr=(1003, 2059), follow=True,
           kb=((0, 0, 1.7), (0, 0, 1.9)), marks=[HBD['sal'] + ('SALEM\n+103°F', 180.8, RED), HBD['ep'] + ('EAST PALESTINE · 8:52 P.M.', 185.4, RED)],
           ov=[O.label('≈ 19 MILES', 960, 930, 181.3, anchor='mm', color=YEL, size=60)]),
      AI(186.06, 'v09_rails_rolling', ss=3.0, grade='night', speed=1.3, ov=[O.counter(S('forty-three', 189.5) - 0.2, 0, 43, 0.8, 'miles per hour', y=460)]),
      STILL(192.2, 's02_detector', trans='glitch', grade='fire', kb=((0.5, 0.6, 1.3), (0.5, 0.6, 1.5)), ov=[O.dark(192.3, amount=0.3),
            O.punch('+253°F', S('two', 193.5), color=RED, size=280)]),
      AI(197.48, 'v10_cab_night', grade='night', zoom=(1.1, 1.2), ov=[O.dark(197.5, amount=0.4)]),
      AI(200.3, 'v10_cab_night', ss=3.0, grade='night', zoom=(1.2, 1.25), ov=[O.dark(200.3, amount=0.62),
            O.type('"CRITICAL ALARM, CRITICAL ALARM,\nCRITICAL ALARM. NORFOLK SOUTHERN\nMILEPOST 49.8, TRACK 1 HOTBOX,\nAXLE 101, SOUTH RAIL."', 200.5, x=200, y=330, size=58, cps=17, color=(255, 90, 70)),
            O.tag('in-cab alarm text · quoted in the NTSB report')]),
]
# ======================= CHAPTER 3 · THE CRASH =======================
T += [AI(209.56, 'v09_rails_rolling', ss=1.0, grade='night', speed=0.6, ov=[O.chapter(3, 'The Crash', 209.7, until=212.2)]),
      AI(212.28, 'v05_wheel_sparks', ss=2.0, grade='fire', speed=1.4, zoom=(1.1, 1.3)),
      V3(217.45, 'T4', ss=0.0, grade='night'),
      AI(222.86, 'v14_derail_fire', trans='flash', grade='fire', zoom=(1.0, 1.12), ov=[O.counter(222.95, 0, 38, 1.0, 'cars derailed', y=430)]),
      AI(226.48, 'v15b_night_fire', trans='flash', grade='fire', zoom=(1.0, 1.15)),
      IMG(230.24, 'media/ntsb_aerial_pile.png', mode='upscale', src_tag=NP + ' · ' + R + ', fig. 7', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)),
          ov=[O.dark(230.3, amount=0.55), O.punch('MYTH', 230.4, y=330, size=150, color=YEL), O.type('THE CREW IGNORED THE WARNING', S('crew', 233) - 0.1, x=420, y=470, size=56, box=False),
              O.stamp('FALSE', S('Fact', 234.5) - 0.1, x=1460, y=520, size=150, rot=-12)]),
      DOC(238.1, 'media/doc_crew.png', ((0.5, 0.3, 1.0), (0.4, 0.22, 1.8))),
      IMG(243.46, 'media/ntsb_hbd_photo.png', mode='upscale', src_tag=NP, kb=((0.5, 0.5, 1.3), (0.5, 0.6, 1.0)), ov=[O.type('PROBLEM #2: DETECTORS READ LOW', 243.6, x=90, y=90, size=46)]),
      IMG(251.18, 'media/ntsb_hbd_summary.png', mode='contain', grade='paper', src_tag=R + ', fig. 29', kb=((0.85, 0.75, 1.6), (0.88, 0.8, 2.0)),
          ov=[O.label('253°F = THE MAXIMUM IT COULD SHOW', 960, 950, 253.8, anchor='mm', color=RED, size=54)]),
      AI(256.84, 'v16_firetrucks', trans='whip', grade='night', zoom=(1.0, 1.12), ov=[O.type('8:56 P.M. · FIRST 911 CALL', 257.0, x=90, y=90, size=50)]),
      AI(261.02, 'v17_firefighters', grade='fire', zoom=(1.0, 1.1), ov=[O.label('MANY WERE VOLUNTEERS', 960, 930, S('volunteers', 264.5) - 0.2, anchor='mm', color=YEL)]),
      AI(265.98, 'v16_firetrucks', ss=4.0, grade='night', zoom=(1.15, 1.25)),
      IMG(268.2, 'media/ntsb_dot111.png', mode='upscale', src_tag=NP + ' · ' + R + ', fig. 20', kb=((0.4, 0.4, 1.0), (0.4, 0.36, 1.4)),
          ov=[O.circle((520, 160, 900, 520), 268.8), O.label('3 TANK CARS PUNCTURED', 960, 930, 269.0, anchor='mm', color=RED)]),
      AI(272.42, 'v15b_night_fire', ss=3.0, grade='fire', zoom=(1.1, 1.0)),
      AI(276.92, 'v18_evacuation', grade='night', zoom=(1.0, 1.12), ov=[O.counter(S('two', 280.5) - 0.2, 0, 2000, 1.0, 'people evacuated · 1-mile zone', y=440)]),
      IMG(282.26, 'media/ntsb_aerial_pile.png', mode='upscale', src_tag=NP + ' · ' + R + ', fig. 7', kb=((0.3, 0.5, 1.1), (0.75, 0.55, 1.5))),
      Shot(286.0, ('img', 'media/ntsb_aerial_pile.png'), mode='upscale', src_tag=NP, kb=((0.75, 0.55, 1.5), (0.8, 0.5, 1.7)),
           ov=[O.punch('VINYL CHLORIDE', 286.1, color=RED, size=170, y=900)]),
      STILL(287.7, 's05_pvc', grade='film', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[O.label('VINYL CHLORIDE → PVC PLASTIC', 960, 930, 288.2, anchor='mm')]),
      AI(293.86, 'v19b_valve_jet', grade='fire', zoom=(1.0, 1.12), ov=[O.stamp('KNOWN HUMAN CARCINOGEN', S('carcinogen', 298.5) - 0.5, x=960, y=500, size=90),
            O.tag('AI visualization · carcinogen: U.S. EPA / NTP')]),
      IMG(300.32, 'media/ntsb_prd_fire.png', mode='upscale', src_tag=NP + ' · ' + R + ', fig. 8', kb=((0.25, 0.5, 1.6), (0.7, 0.45, 1.6)), smooth=True,
          ov=[O.label('NOT PUNCTURED — BUT HEATED BY FIRE', 960, 930, 300.6, anchor='mm', until=309.0),
              O.label('SAFETY VALVES VENTING · UNTIL FEB 4', 960, 930, 309.2, anchor='mm', color=YEL)]),
]
# ======================= CHAPTER 4 · THE FEAR =======================
T += [AI(315.22, 'v29_hazmat', trans='whip', grade='cold', zoom=(1.0, 1.1), ov=[O.chapter(4, 'The Fear', 315.3, until=319.1),
            O.punch('NOT ACCORDING TO\nNORFOLK SOUTHERN', 317.1, size=120, color=[WHT, RED], y=380)]),
      STILL(319.26, 's06_gauge', grade='fire', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.3)), ov=[O.punch('"POLYMERIZATION"', S('polymerization', 322) - 0.2, size=150, color=RED, y=900)]),
      AI(324.5, 'v20_popcorn', trans='whip', grade='film', zoom=(1.0, 1.2), ov=[O.label('THINK: POPCORN IN A SEALED POT', 960, 120, 326.8, anchor='mm', size=50),
            O.label('MORE HEAT → MORE POPPING', 960, 930, S('More', 332.5) - 0.1, anchor='mm', color=RED, size=56)]),
      V3(334.2, 'T5', ss=0.0, grade='cold', ov=[O.type('INSIDE A CLOSED TANK:\nREACTION → HEAT → FASTER REACTION', 335.0, x=90, y=760, size=42),
                                               O.punch('TANK BURSTS?', S('bursts', 340.5) - 0.2, color=RED, size=150, y=300)]),
      STILL(342.06, 's06_gauge', grade='fire', kb=((0.55, 0.5, 1.4), (0.5, 0.45, 1.7)), ov=[O.dark(342.1, amount=0.35),
            O.counter(342.3, 120, 138, 6.0, 'one tank car · Feb 5 · "+3°F in one hour"', suffix='°F', y=440)]),
      IMG(354.74, 'media/ntsb_temp_graph.png', mode='contain', grade='paper', src_tag=R + ', fig. 32', kb=((0.5, 0.5, 1.0), (0.3, 0.35, 1.7)),
          ov=[O.label('TO THE RAILROAD: "POLYMERIZING"', 960, 120, 355.0, anchor='mm', color=RED)]),
      AI(358.46, 'v01_fireball', ss=2.0, grade='fire', zoom=(1.15, 1.0), ov=[O.punch('STEEL FLYING\n½ MILE', S('half', 362.5) - 0.3, color=[WHT, RED], size=170),
            O.tag("AI visualization · the railroad's assessment")]),
      IMG(364.24, 'media/ntsb_vb_illus.png', mode='contain', grade='paper', src_tag=R + ', fig. 9', kb=((0.5, 0.5, 1.0), (0.5, 0.55, 1.25)),
          ov=[O.punch('VENT AND BURN', 364.4, size=110, color=RED, y=140), O.label('1 · EXPLOSIVE CHARGES', 1500, 380, S('Explosive', 368) - 0.2),
              O.label('2 · TRENCH + PIT', 1500, 480, S('trench', 371.5) - 0.3), O.label('3 · SET ON FIRE', 1500, 580, S('fire', 373) - 0.3, color=RED)]),
      STILL(374.68, 's07_dallas', trans='glitch', grade='cold', kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.2)), ov=[O.punch('THE TWIST', 374.75, color=RED, size=220),
            O.lower('Oxy Vinyls', 'made the vinyl chloride · shipped it on this train', S('Oxy', 381.5) - 0.1, until=390.0)]),
      AI(390.28, 'v12_desk_monitor', ss=3.0, grade='cold', zoom=(1.2, 1.1), ov=[O.stamp('NOT POLYMERIZING', S('opposite', 391.2), x=960, y=480, size=110, color=(40, 200, 90))]),
      AI(392.94, 'v21_meeting', grade='cold', zoom=(1.0, 1.12), ov=[O.type('FEB 5 · EVENING', 393.1, x=90, y=90, size=46)]),
      AI(397.96, 'v21_meeting', ss=3.0, grade='cold', zoom=(1.15, 1.25), ov=[O.dark(398.0, amount=0.62),
            O.quote("Don't do it because of polymerization, because polymerization is not occurring.", 399.4, who='Oxy Vinyls, as recalled to the NTSB', hl=['polymerization is not occurring.'], size=66)]),
      DOC(405.6, 'media/doc_oxyquote.png', ((0.45, 0.4, 1.4), (0.42, 0.34, 2.1))),
      Shot(409.49, ('black',), trans='cut', grain=8.0, ov=[O.quote("…polymerization is not occurring.", 409.6, hl=['not occurring.'], size=80)]),
      Shot(411.44, ('black',), trans='glitch', grain=8.0, ov=[O.punch('THE NEXT DAY,\nIT VANISHED.', 411.5, color=[WHT, RED], size=170)]),
]
# ======================= CHAPTER 5 · THE ROOM =======================
T += [AI(414.92, 'v21_meeting', trans='whip', grade='cold', zoom=(1.05, 1.0), ov=[O.chapter(5, 'The Room', 415.0, until=420.4)]),
      AI(420.62, 'v21_meeting', ss=5.0, grade='cold', zoom=(1.2, 1.3), ov=[O.counter(S('sixty', 422) - 0.2, 0, 100, 1.4, 'people · including two governors', prefix='60–', y=430)]),
      STILL(427.74, 's08_empty_chair', trans='flash', grade='cold', kb=((0.5, 0.5, 1.0), (0.5, 0.55, 1.25)), ov=[O.stamp('NOT INVITED', S('invited', 430.5) - 0.2, x=960, y=420, size=140)]),
      DOC(431.62, 'media/doc_notinvited.png', ((0.5, 0.6, 1.2), (0.6, 0.72, 1.8)), ov=[O.label('NOBODY ELSE KNEW THE MAKER DISAGREED', 960, 120, 433.0, anchor='mm', color=RED)]),
      IMG(441.78, 'media/ntsb_temp_graph.png', mode='contain', grade='paper', src_tag=R + ', fig. 32', kb=((0.3, 0.4, 1.5), (0.72, 0.45, 1.5)),
          ov=[O.label('PEAK 138°F', 520, 300, 442.0, color=RED), O.label('COOLING → 126°F', 1250, 420, S('cooled', 446) - 0.2, color=(60, 200, 100)),
              O.punch('NOT A RUNAWAY REACTION', S('opposite', 452.5) - 0.2, size=110, color=RED, y=930)]),
      STILL(455.28, 's09_helmet', trans='dip', grade='cold', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.2)), ov=[O.bars(455.3, until=466.0),
            O.lower('The incident commander', "East Palestine's fire chief", 457.9, until=465.8)]),
      AI(466.08, 'v22_clock', grade='cold', zoom=(1.2, 1.5), ov=[O.dark(466.1, amount=0.35), O.punch('13 MINUTES', S('thirteen', 467) - 0.2, color=RED, size=230)]),
      DOC(469.52, 'media/doc_13min.png', ((0.5, 0.3, 1.2), (0.72, 0.24, 1.9)), ov=[O.label('START BEFORE 3 P.M.', 960, 950, 470.0, anchor='mm', color=RED)]),
      STILL(473.66, 's09_helmet', grade='cold', kb=((0.5, 0.5, 1.25), (0.48, 0.5, 1.4)), ov=[O.dark(473.7, amount=0.6),
            O.quote('He felt overwhelmed and blindsided.', 474.0, who='NTSB, from the incident commander\'s interview', hl=['overwhelmed and blindsided.'], size=76)]),
      STILL(478.58, 's08_empty_chair', grade='cold', kb=((0.5, 0.55, 1.35), (0.5, 0.55, 1.6)), ov=[O.dark(478.6, amount=0.45),
            O.type('"IT\'S GOING TO EXPLODE."\nNOBODY OBJECTS.\nTHE CLOCK IS RUNNING.', 480.3, x=200, y=380, size=60, cps=16, box=False)]),
      Shot(486.42, ('black',), grain=8.0, ov=[O.punch('WHAT WOULD\nYOU SAY?', 486.45, color=[WHT, YEL], size=170, shake=False)]),
      Shot(487.66, ('black',), trans='flash', grain=8.0, ov=[O.punch('HE SAID YES.', 487.7, color=RED, size=210)]),
      V3(490.06, 'T5', ss=0.0, trans='fade', grade='cold', ov=[O.type('4:37 P.M. · FEBRUARY 6', 490.3, x=90, y=90, size=48)]),
      V3(501.38, 'T6', ss=0.0, grade='cold'),
      AI(508.16, 'v03_column', grade='cold', zoom=(1.0, 1.15), ov=[O.label('HYDROGEN CHLORIDE · A TRACE OF PHOSGENE', 960, 930, 509.5, anchor='mm', color=YEL),
            O.tag("AI visualization · smoke contents per the railroad, NTSB report")]),
      AI(517.04, 'v23_crowd_watch', grade='cold', zoom=(1.0, 1.1)),
]
# ======================= CHAPTER 6 · THE VERDICT =======================
T += [AI(522.12, 'v24_report_desk', trans='whip', grade='film', zoom=(1.0, 1.1), ov=[O.chapter(6, 'The Verdict', 522.2, until=525.8)]),
      IMG(526.0, 'media/doc_cover.png', mode='contain', grade='paper', src_tag=R, kb=((0.5, 0.4, 1.0), (0.5, 0.3, 1.3)), ov=[O.label('JUNE 25, 2024', 960, 950, 526.3, anchor='mm', color=RED, size=60)]),
      DOC(531.72, 'media/doc_notnecessary.png', ((0.5, 0.5, 1.0), (0.4, 0.46, 1.6))),
      DOC(544.02, 'media/doc_notnecessary.png', ((0.4, 0.46, 1.6), (0.4, 0.46, 2.2)), ov=[O.stamp('NOT NECESSARY', S('necessary', 547.5) - 0.2, x=1250, y=760, size=130)]),
      DOC(551.88, 'media/doc_compromised.png', ((0.5, 0.6, 1.1), (0.5, 0.72, 1.8))),
      Shot(563.86, ('img', 'media/doc_compromised.png'), mode='cover', grade='paper', src_tag=R, kb=((0.5, 0.72, 1.8), (0.5, 0.72, 2.0)),
           ov=[O.dark(563.9, amount=0.55), O.punch('"UNJUSTIFIED."', S('unjustified', 565) - 0.2, color=RED, size=210)]),
      AI(568.08, 'v25_old_tankcars', trans='whip', grade='cold', zoom=(1.0, 1.15)),
      IMG(570.9, 'media/ntsb_dot111.png', mode='upscale', src_tag=NP + ' · ' + R, kb=((0.5, 0.5, 1.0), (0.45, 0.45, 1.3)), ov=[O.label('DOT-111 · AN OLDER DESIGN', 960, 930, S('DOT-111', 576.5) - 0.3, anchor='mm', color=RED)]),
      STILL(582.78, 's13_wreck_day', grade='cold', kb=((0.4, 0.5, 1.2), (0.6, 0.5, 1.2)), ov=[O.type('IF THOSE CARS HAD SURVIVED:\nLIKELY NO VINYL CHLORIDE RELEASE', 583.2, x=90, y=780, size=44)]),
      AI(591.36, 'v16_firetrucks', ss=2.0, grade='night', zoom=(1.0, 1.1), ov=[O.label('SLOW TO TELL RESPONDERS WHAT WAS ON THE TRAIN', 960, 930, 591.6, anchor='mm')]),
      AI(596.9, 'v17_firefighters', ss=3.0, grade='fire', zoom=(1.1, 1.0), ov=[O.label('OHIO VOLUNTEER FIREFIGHTER TRAINING: NOT ENOUGH', 960, 930, 597.1, anchor='mm', color=YEL)]),
      STILL(602.9, 's12_town_sign', grade='cold', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.15)), ov=[O.counter(S('six-hundred-million-dollar', 604.5) - 0.2, 0, 600, 1.2, 'class action settlement · no admission of wrongdoing', prefix='$', suffix='M', y=430)]),
      IMG(610.5, 'media/doc_cover.png', mode='contain', grade='paper', src_tag=R, kb=((0.5, 0.3, 1.3), (0.5, 0.5, 1.0)), ov=[O.dark(610.6, amount=0.4),
            O.counter(S('thirty-four', 613) - 0.2, 0, 34, 1.0, 'new safety recommendations', y=470)]),
]
# ======================= OUTRO =======================
T += [AI(616.72, 'v05_wheel_sparks', trans='dip', grade='fire', speed=0.7, ov=[O.label('THE CRASH: AN ACCIDENT', 960, 930, 619.2, anchor='mm')]),
      AI(623.72, 'v03_column', ss=2.0, grade='cold', zoom=(1.0, 1.12), ov=[O.label('THE BLACK CLOUD: A DECISION', 960, 930, S('decision', 626) - 0.2, anchor='mm', color=RED)]),
      STILL(627.48, 's08_empty_chair', grade='cold', kb=((0.5, 0.5, 1.0), (0.5, 0.55, 1.2))),
      AI(633.62, 'v26_dawn_street', trans='dip', grade='film', zoom=(1.0, 1.1)),
      STILL(638.8, 's10_home_window', grade='film', kb=((0.5, 0.5, 1.0), (0.5, 0.45, 1.15))),
      STILL(646.76, 's11_creek', grade='film', kb=((0.5, 0.5, 1.15), (0.5, 0.5, 1.0)), ov=[O.punch("IT'S IN THE\nCONVERSATION.", S('conversation', 651) - 0.2, color=[WHT, YEL], size=150, shake=False)]),
      AI(654.4, 'v27_sunset_tracks', trans='dip', grade='film', zoom=(1.0, 1.15), ov=[O.label('LIKE  ·  COMMENT  ·  SUBSCRIBE', 960, 930, 655.0, anchor='mm', until=666.0),
            O.type('SHOULD A RAILROAD EVER MAKE THE CALL\nON A VENT AND BURN?', S('Tell', 661) - 0.1, x=200, y=200, size=52, until=668.0)]),
      AI(666.52, 'v27_sunset_tracks', ss=4.0, grade='film', zoom=(1.15, 1.25), ov=[O.punch('WRECKLORE', 666.6, size=230, f='play', shake=False, sub='every disaster leaves a lesson')]),
      AI(677.0, 'v07_town_night', trans='dip', grade='night', zoom=(1.0, 1.06), outfade=True, ov=[O.dark(677.0, amount=0.55),
            O.label('WATCH NEXT', 520, 250, 677.6, color=WHT, size=56), O.label('SUBSCRIBE', 1400, 250, 677.6, color=RED, size=56)]),
]
END = 692.0

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'render':
        render(T, END, sys.argv[4], float(sys.argv[2]), float(sys.argv[3]), log=True)
