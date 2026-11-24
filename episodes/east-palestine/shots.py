#!/usr/bin/env python3
"""Shot list: The Burn That Didn't Have to Happen — East Palestine, Ohio (≈10:50). Times are absolute VO seconds."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.claude/skills/engineering-failures-video/scripts'))
from vidlib import A169, NX, N, I, finish, init, sh, w

init(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent))
S = lambda word, near: w(word, near)

D3 = {k: {'file': f'real3d/{k}.mp4', 'crop': 'eq=saturation=1.18:brightness=0.035,'} for k in ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']}
SRC3 = 'Animated reconstruction (illustrative) · Wrecklore'
def F(t0, key, ss=0.0): sh(t0, 'full', clip=dict(src=key, ss=ss), src=SRC3)
R = 'NTSB Railroad Investigation Report RIR-24-05 (2024)'
NTSB = 'NTSB photo · public domain'
WIDE = dict(x=210, y=140, w=1500, h=640)       # wide figure (maps, graphs)
DOC = dict(x=200, y=150, w=1300, h=731)         # report page crop, 16:9

# ================= HOOK =================
sh(0.0, 'box', src=NTSB + ' · ' + R, boxes=[I('ntsb_aerial_pile.png', A169, cap='East Palestine, Ohio · the derailment site', push=0.1, origin='30% 50%')],
   notes=[N('FEBRUARY 6, 2023', NX, 300, 0.2, 'yellow', size=60), N('East Palestine, Ohio', NX, 390, S('East', 3.5), 'white', size=50)])
sh(5.66, 'head', lines=["They're about to do something", 'UNBELIEVABLE.'], accent=1, acol='red', fs=110, at=[5.7, S('unbelievable', 7.5) - 0.3])
sh(8.94, 'counter', steps=[dict(value=5, label='tank cars', at=9.0, dur=0.5),
                           dict(value=887400, label='pounds of vinyl chloride · a known carcinogen', at=S('nine', 11) - 0.3, dur=1.6, accent=True)], fs=250, src=R)
F(12.94, 'T5', 0.0)                                                     # tank cars → charges at 19.94 → fireball
sh(22.7, 'head', lines=['"The only way to stop', 'a massive EXPLOSION."'], accent=1, acol='red', fs=110, at=[22.75, S('massive', 25) - 0.2])
sh(26.64, 'box', src=R + ', executive summary', boxes=[I('doc_notnecessary.png', DOC, cap='NTSB final report · June 2024', push=0.12, origin='40% 45%')],
   notes=[N('a year and a half later…', 1560, 260, 26.8, 'white', size=46, w=330), N('NEVER going to happen', 1560, 420, S('never', 32.5) - 0.2, 'red', size=58, w=330)])
sh(34.4, 'head', lines=["The chemical's own maker", 'SAID SO. Before.'], accent=1, acol='yellow', fs=110, at=[34.45, S('before', 37.5) - 0.2])
sh(39.72, 'head', lines=['So why did', 'no one LISTEN?'], accent=1, acol='red', fs=150, at=[39.75, S('listen', 40.5) - 0.2])
F(41.7, 'T2', 0.0)                                                      # the burning wheelset
sh(49.28, 'list', items=[dict(text='→ minute by minute', at=49.4), dict(text='→ the official NTSB report', at=S('official', 52.5) - 0.2),
                         dict(text='→ who knew what, and when', at=S('who', 55) - 0.2, accent=True)], fs=104)
sh(58.46, 'title', lines=["The Burn That Didn't", 'Have to Happen'], kicker='East Palestine, Ohio · February 2023', sub='one bearing · one decision · thirteen minutes')
# ================= THE TRAIN =================
F(61.38, 'T1', 0.0)                                                     # night, the train rolls through town
sh(72.24, 'box', src=NTSB + ' · ' + R, boxes=[I('ntsb_town.png', WIDE, cap='NTSB: the derailment site sits inside the town', fit='cover', push=0.1, origin='45% 40%')])
sh(74.46, 'head', lines=['Norfolk Southern', 'train 32N'], accent=1, acol='yellow', fs=150, at=[74.5, S('thirty-two', 76) - 0.2], sub='Friday, February 3, 2023 · night', subAt=75.5)
sh(78.18, 'counter', steps=[dict(value=3, label='locomotives', at=78.2, dur=0.4), dict(value=149, label='freight cars', at=S('hundred', 79.7) - 0.1, dur=0.9),
                            dict(value=17977, label='tons · about 1¾ miles long', at=S('eighteen', 83.5) - 0.3, dur=1.2, accent=True)], fs=280, src=R)
sh(87.62, 'box', src=R + ', fig. 2', boxes=[I('ntsb_route.png', WIDE, fit='contain', bg='#f3efe6', cap="Train 32N's route", push=0.05)],
   notes=[N('Madison, Illinois', 230, 850, S('Madison', 88.5), 'red', size=46), N('→ Conway, Pennsylvania', 1000, 850, S('Pennsylvania', 91) - 0.2, 'red', size=46)])
sh(93.06, 'list', items=[dict(text='Engineer · 24 years', at=93.15), dict(text='Conductor', at=S('conductor', 97.5) - 0.2),
                         dict(text='Conductor trainee', at=S('trainee', 99) - 0.2)], fs=110, src=R)
sh(100.42, 'head', lines=['The 23rd car', 'is ON FIRE.'], accent=1, acol='red', fs=170, at=[100.5, S('fire', 103.5) - 0.3])
sh(104.92, 'box', src=R + ', fig. 4', boxes=[I('ntsb_wheelset_diag.png', WIDE, fit='contain', bg='#ffffff', cap='The hopper car: 4 wheelsets, 8 bearings', push=0.05, origin='85% 70%')],
   notes=[N('loaded with plastic pellets', 230, 850, S('plastic', 107) - 0.2, 'white', size=46, w=900),
          N('L1 bearing: failing', 1180, 850, S('failing', 110) - 0.2, 'red', size=52, arrow=[[1420, 840], [1560, 640]])])
F(111.88, 'T3', 0.0)                                                    # bearing cutaway: rollers, heat
sh(123.88, 'box', src=NTSB + ' · ' + R + ', fig. 18', boxes=[I('ntsb_cup.png', A169, cap='What was left of the L1 bearing', push=0.08)],
   notes=[N('melted · deformed', NX, 320, 124.2, 'red', size=56), N('VERY hot.', NX, 420, S('Very', 126) - 0.1, 'yellow', size=64)])
sh(127.9, 'box', src=NTSB + ' · ' + R + ', fig. 13', boxes=[I('ntsb_hbd_photo.png', dict(x=150, y=170, w=620, h=740), cap='A hot bearing detector', push=0.07)],
   notes=[N('Hot bearing detectors', 900, 260, S('detectors', 132) - 0.4, 'yellow', size=62, w=900),
          N('read the temperature of', 900, 370, S('sensors', 134) - 0.2, 'white', size=50, w=900), N('EVERY wheel that rolls by', 900, 440, S('wheel', 136.5) - 0.2, 'white', size=50, w=900)])
sh(139.4, 'head', lines=["Now here's where it", 'gets interesting.'], accent=1, acol='yellow', fs=120, at=[139.45, S('interesting', 140.5) - 0.2])
sh(142.2, 'box', src=R + ', fig. 3', boxes=[I('ntsb_hbd_map.png', WIDE, fit='contain', bg='#f3efe6', cap='The last three detectors before East Palestine', push=0.1, origin='10% 40%')],
   notes=[N('#1 SEBRING · 7:37 p.m.', 230, 850, 142.4, 'red', size=48, w=900)])
sh(148.02, 'bars', lines=['Bearing temperature, above the outside air'], bars=[dict(value='+38°F', label='Sebring · no alert', h=0.15, at=148.1),
   dict(value='+103°F', label='Salem · 8:13 p.m.', h=0.41, at=S('hundred', 158.5) - 0.2, color='red')], src=R)
sh(161.52, 'saiddid', lk='WHO GOT THE ALERT', said=['An analyst at', 'a help desk'], saidAt=[S('analyst', 166.5) - 0.2, S('help', 168) - 0.2],
   rk="WHO DIDN'T", did=['The crew.'], didAt=S('crew', 170.5) - 0.2, sfs=104, dfs=130, src=R)
sh(171.52, 'head', lines=['BUT WAIT.'], accent=0, acol='red', fs=220, at=[171.55])
F(172.92, 'T2', 2.0)                                                    # fire on the wheelset (NTSB found it in Salem camera images)
sh(182.86, 'box', src=R + ', fig. 3', boxes=[I('ntsb_hbd_map.png', WIDE, fit='contain', bg='#f3efe6', cap='Next detector: East Palestine', push=0.12, origin='92% 40%')],
   notes=[N('≈ 19 miles to go', 700, 850, 183.0, 'red', size=60), N('→ EAST PALESTINE', 1150, 850, S('East', 185.5), 'red', size=56)])
sh(187.98, 'counter', steps=[dict(value=43, label='mph · 8:52 p.m.', at=S('8:52', 188.5) + 0.6, dur=0.9, accent=True)], fs=300, suffix=' mph', src=R)
sh(194.26, 'bars', lines=['Above outside air'], bars=[dict(value='+38°F', label='Sebring', h=0.15, at=194.3),
   dict(value='+103°F', label='Salem', h=0.41, at=194.4), dict(value='+253°F', label='East Palestine', h=0.85, at=S('two', 196) - 0.1, color='red')], src=R)
sh(199.46, 'head', lines=['And in the cab…'], accent=0, fs=150, at=[199.5])
sh(202.49, 'doc', header='IN-CAB SPEAKERS · TRAIN 32N · ABOUT 8:53 P.M. (QUOTED IN THE NTSB REPORT)', src=R + ', p. 8',
   body='"[[Critical alarm, critical alarm, critical alarm.]] Norfolk Southern milepost 49.8, track 1 hotbox, axle 101, south rail."', hlAt=202.6, fs=46)
F(211.6, 'T2', 8.0)                                                     # slowing…
F(215.6, 'T4', 0.0)                                                     # axle separates at 217.6 → pileup → fire
sh(227.6, 'box', src=NTSB + ' · ' + R + ', fig. 7', boxes=[I('ntsb_aerial_pile.png', A169, cap='The pileup, seen by NTSB drone', push=0.1)],
   notes=[N('38 cars', NX, 300, 227.7, 'red', size=80), N('derailed', NX, 400, 227.9, 'white', size=56), N('FIRE', NX, 500, S('Fire', 228.3), 'red', size=80)])
sh(232.1, 'saiddid', lk='MYTH', said=['The crew ignored', 'the warning'], saidAt=[S('crew', 235) - 0.1, S('ignored', 235.5) - 0.1],
   rk='FACT', did=['They reacted', 'immediately'], didAt=S('Fact', 236.5) - 0.1, sfs=96, dfs=96)
sh(240.36, 'doc', header='NTSB FINAL REPORT RIR-24-05 · WHAT WE FOUND', src=R, fs=44,
   body="Train 32N's crew [[did not have adequate warning]] to stop the train before the derailment.", hlAt=S('enough', 243) - 0.3)
sh(245.44, 'head', lines=['Problem #2:', 'detectors read LOW'], accent=1, acol='red', fs=140, at=[245.5, S('misleadingly', 250.5) - 0.3],
   sub='"likely to indicate misleadingly low bearing temperatures" — NTSB', subAt=S('misleadingly', 250.5))
sh(253.2, 'counter', steps=[dict(value=253, label="the HIGHEST number this detector could show", at=253.3, dur=0.9, accent=True)], fs=300, suffix='°F', src=R + ', p. 8')
sh(258.72, 'head', lines=['8:56 p.m.', 'the first 911 call'], accent=0, acol='red', fs=150, at=[258.8, S('nine-one-one', 259.5)])
sh(263.06, 'box', src=NTSB + ' · ' + R + ', fig. 8', boxes=[I('ntsb_prd_fire.png', A169, cap='Fires at the derailment site', push=0.1)],
   notes=[N('Many of the firefighters', NX, 300, S('Many', 266) - 0.2, 'white', size=48, w=600), N('were VOLUNTEERS', NX, 380, S('volunteers', 267) - 0.2, 'yellow', size=58, w=600)])
sh(270.72, 'box', src=NTSB + ' · ' + R + ', fig. 20', boxes=[I('ntsb_dot111.png', A169, cap='A punctured tank car', push=0.1, origin='35% 40%')],
   notes=[N('3 tank cars', NX, 300, 270.8, 'red', size=70), N('PUNCTURED', NX, 390, 271.2, 'red', size=60), N('burning liquid in a ditch', NX, 500, S('ditch', 276.5) - 0.2, 'white', size=44, w=620)])
sh(278.96, 'counter', steps=[dict(value=2000, label='people evacuated · 1-mile zone', at=279.1, dur=1.0, accent=True)], more='about', fs=300, src=R)
sh(284.42, 'head', lines=['Something else', 'in the pileup…'], accent=1, acol='yellow', fs=140, at=[284.45, 285.4])
sh(286.52, 'box', src=NTSB + ' · ' + R + ', fig. 7', boxes=[I('ntsb_aerial_pile.png', A169, cap='Labels: NTSB', push=0.16, origin='25% 40%')],
   notes=[N('5 tank cars', NX, 300, 286.6, 'yellow', size=70), N('VINYL CHLORIDE', NX, 390, S('vinyl', 288) - 0.2, 'red', size=60)])
sh(289.74, 'list', items=[dict(text='Vinyl chloride → PVC plastic', at=289.8), dict(text='flammable gas, under pressure', at=S('flammable', 296.5) - 0.2),
                          dict(text='a known human carcinogen', at=S('carcinogen', 300.5) - 0.6, accent=True)], fs=96, src='U.S. EPA; National Toxicology Program')
sh(302.3, 'box', src=NTSB + ' · ' + R + ', fig. 8', boxes=[I('ntsb_prd_fire.png', A169, cap='Safety valves venting, and burning', push=0.1, origin='25% 50%')],
   notes=[N('NOT punctured', NX, 290, 302.4, 'yellow', size=56), N('but heated by fire', NX, 370, S('heated', 305) - 0.2, 'white', size=50),
          N('releases stopped:', NX, 480, S('stopped', 314.5) - 0.2, 'white', size=46), N('Feb 4, afternoon', NX, 545, S('February', 315.5) - 0.2, 'yellow', size=52)])
sh(317.32, 'head', lines=['So the danger', 'was over?'], accent=1, acol='yellow', fs=150, at=[317.35, 318.2])
sh(319.04, 'head', lines=['Not according to', 'NORFOLK SOUTHERN.'], accent=1, acol='red', fs=130, at=[319.1, 319.8])
sh(321.34, 'head', lines=['"POLYMERIZATION"'], accent=0, acol='red', fs=150, at=[321.45], sub='the word that changed everything', subAt=324.6)
sh(326.5, 'blueprint', kind='structure', title='Think of popcorn in a sealed pot',
   paths=[dict(d='M 620 420 V 760 Q 620 800 660 800 H 1260 Q 1300 800 1300 760 V 420', at=328.7, dur=0.8),
          dict(d='M 590 410 H 1330 M 900 410 V 380 H 1020 V 410', at=329.4, dur=0.5),
          dict(d='M 760 860 Q 780 830 770 800 M 900 870 Q 930 830 910 800 M 1040 870 Q 1070 830 1050 800 M 1170 860 Q 1190 830 1180 800', at=330.9, color='red', dur=0.6),
          dict(d='M 760 700 a 22 22 0 1 0 1 0 M 880 640 a 22 22 0 1 0 1 0 M 1010 690 a 22 22 0 1 0 1 0 M 1130 620 a 22 22 0 1 0 1 0 M 960 560 a 22 22 0 1 0 1 0', at=S('popping', 331.5), color='yellow', dur=0.8)],
   labels=[dict(text='kernels pop → make heat', x=960, y=220, at=S('make', 332.5) - 0.2, color='yellow', size=54, align='center'),
           dict(text='more heat → more popping', x=960, y=290, at=S('More', 334.5) - 0.1, color='red', size=54, align='center')])
sh(336.45, 'blueprint', kind='structure', title='Polymerization inside a closed tank (simplified)',
   paths=[dict(d='M 560 420 H 1360 Q 1480 420 1480 560 Q 1480 700 1360 700 H 560 Q 440 700 440 560 Q 440 420 560 420 Z', at=336.6, dur=0.9),
          dict(d='M 760 560 m -80 0 a 80 80 0 1 1 160 0 a 80 80 0 1 1 -160 0 M 840 470 l 18 -14 M 840 470 l 20 10', at=S('reaction', 340.5) - 0.2, color='red', dur=0.9),
          dict(d='M 1150 560 m -70 0 a 70 70 0 1 0 140 0 a 70 70 0 1 0 -140 0', at=S('feed', 341.2), color='yellow', dur=0.7),
          dict(d='M 1480 560 L 1600 500 M 1480 560 L 1610 580 M 1470 610 L 1580 660', at=S('bursts', 342.9) - 0.2, color='red', width=7, dur=0.4)],
   labels=[dict(text='reaction → heat', x=760, y=760, at=S('reaction', 340.5), color='red', size=50, align='center'),
           dict(text='heat → faster reaction', x=1150, y=760, at=S('feed', 341.2), color='yellow', size=50, align='center'),
           dict(text='until the tank BURSTS', x=960, y=250, at=S('bursts', 342.9) - 0.2, color='red', size=60, align='center')])
sh(344.14, 'counter', steps=[dict(value=135, label='Feb 5 · the railroad told the NTSB…', at=344.3, dur=1.0), dict(value=138, label='+3°F in one hour', at=S('three', 350.5) - 0.2, dur=1.4, accent=True)], suffix='°F', fs=300,
   more='one tank car', src=R + ', p. 26')
sh(356.78, 'head', lines=['To the railroad:', 'it was POLYMERIZING.'], accent=1, acol='red', fs=120, at=[356.8, S('happening', 358.5) - 0.3])
sh(360.4, 'head', lines=['Feared explosion:', 'steel flying ½ MILE'], accent=1, acol='red', fs=130, at=[360.45, S('half', 364.5) - 0.3], sub="the railroad's assessment", subAt=361.5, src=R + ', p. 26')
sh(366.42, 'box', src=R + ', fig. 9', boxes=[I('ntsb_vb_illus.png', A169, fit='contain', bg='#ffffff', cap='How a vent and burn works', push=0.06)],
   notes=[N('VENT AND BURN', NX, 260, 366.5, 'red', size=60), N('1 · explosive charges', NX, 360, S('Explosive', 370) - 0.2, 'white', size=46),
          N('2 · drains to a trench + pit', NX, 430, S('trench', 373.5) - 0.3, 'white', size=46), N('3 · set on fire', NX, 500, S('fire', 375) - 0.3, 'yellow', size=50)])
sh(376.76, 'head', lines=['But here is', 'THE TWIST.'], accent=1, acol='red', fs=170, at=[376.8, 377.5])
sh(378.54, 'head', lines=['Oxy Vinyls', 'made this chemical'], accent=0, acol='yellow', fs=140, at=[378.6, S('made', 384) - 0.2],
   sub='and shipped it on this train', subAt=S('shipped', 385) - 0.2, src=R)
sh(386.8, 'saiddid', lk='THE RAILROAD SAID', said=["It's", 'polymerizing.'], saidAt=[386.9, 387.2], rk="OXY VINYLS' EXPERTS", did=['It is NOT.'],
   didAt=S('opposite', 393.5) - 0.2, sfs=110, dfs=130, src=R + ', pp. 26–27')
sh(395.0, 'box', src=R + ', p. 27 (interview with Oxy Vinyls)', boxes=[I('doc_oxyquote.png', DOC, cap="Oxy Vinyls to the railroad's contractor, Feb 5", push=0.16, origin='30% 32%')],
   notes=[N('Feb 5, evening', 1560, 260, 395.1, 'white', size=46, w=330), N('"NOT occurring"', 1560, 420, S('not', 409) - 0.3, 'red', size=56, w=330)])
sh(411.62, 'head', lines=['Hold on to', 'that sentence.'], accent=1, acol='yellow', fs=150, at=[411.65, 412.2])
sh(413.0, 'head', lines=['The next day,', 'it VANISHED.'], accent=1, acol='red', fs=170, at=[413.05, S('vanished', 414.8) - 0.2])
sh(416.96, 'head', lines=['February 6 · noon', 'the final meeting'], accent=1, acol='yellow', fs=130, at=[417.0, S('final', 421) - 0.2], src=R + ', p. 27')
sh(422.9, 'counter', steps=[dict(value=60, label='people in the room', at=S('sixty', 424) - 0.2, dur=0.6), dict(value=100, label='incl. the governors of Ohio and Pennsylvania', at=S('hundred', 425.5) - 0.2, dur=0.8, accent=True)],
   fs=300, more='up to', src=R + ', p. 27')
sh(429.76, 'box', src=R + ', p. 27', boxes=[I('doc_notinvited.png', DOC, cap='NTSB final report', push=0.16, origin='60% 72%')],
   notes=[N('NOT', 1560, 260, 429.9, 'red', size=90, w=330), N('INVITED', 1560, 360, S('invited', 432.5) - 0.2, 'red', size=70, w=330),
          N('nobody else knew', 1560, 520, S('evidence', 436.5) - 0.2, 'white', size=44, w=330), N('the maker disagreed', 1560, 580, S('disagreed', 442) - 0.3, 'yellow', size=44, w=330)])
sh(443.8, 'box', src=R + ', fig. 32', boxes=[I('ntsb_temp_graph.png', WIDE, fit='contain', bg='#ffffff', cap='Hottest tank car: measured temperatures', push=0.06)],
   notes=[N('peak 138°F', 230, 850, S('heating', 445.5) - 0.2, 'red', size=56), N('…cooling to ~126°F', 640, 850, S('cooled', 448.5) - 0.2, 'yellow', size=56),
          N('NOT a runaway', 1220, 850, S('opposite', 454.5) - 0.2, 'red', size=56, w=600)])
sh(457.28, 'head', lines=['Then came the moment', 'that sealed it.'], accent=1, acol='red', fs=120, at=[457.3, S('sealed', 458.5) - 0.2])
sh(459.52, 'box', src=R + ', p. 28', boxes=[I('doc_13min.png', DOC, cap='NTSB final report', push=0.16, origin='70% 25%')],
   notes=[N('a separate room', 1560, 260, S('separate', 462) - 0.2, 'white', size=46, w=330), N('13 MINUTES', 1560, 380, S('thirteen', 469) - 0.3, 'red', size=64, w=330)])
sh(468.28, 'counter', steps=[dict(value=13, label='minutes to decide', at=468.35, dur=0.8, accent=True)], fs=320, src=R + ', p. 28')
sh(471.52, 'head', lines=['Start before 3 p.m.', 'finish in daylight'], accent=1, acol='yellow', fs=130, at=[471.55, S('finish', 474.5) - 0.2])
sh(475.68, 'doc', header='THE INCIDENT COMMANDER, IN HIS INTERVIEW WITH THE NTSB', src=R + ', p. 28', fs=52,
   body='He felt [[overwhelmed and blindsided]] by the size of the decision.', hlAt=S('overwhelmed', 478) - 0.2)
sh(480.48, 'head', lines=['Put yourself', 'in his chair.'], accent=1, acol='yellow', fs=160, at=[480.5, 481.2])
sh(482.3, 'list', items=[dict(text='"It\'s going to explode."', at=482.35), dict(text='Nobody objects.', at=S('Nobody', 485.5) - 0.1),
                         dict(text='The clock is running.', at=S('clock', 487.3) - 0.2, accent=True)], fs=110)
sh(488.46, 'head', lines=['What would', 'YOU say?'], accent=1, acol='yellow', fs=170, at=[488.48, 488.9])
sh(489.66, 'head', lines=['He said', 'YES.'], accent=1, acol='red', fs=200, at=[489.68, S('yes', 490.3) - 0.1])
F(490.36, 'T5', 0.0)                                                    # 4:37 p.m.: charges at 497.36
F(506.36, 'T6', 0.0)                                                    # the column over the town
sh(522.36, 'head', lines=['So, was it', 'NECESSARY?'], accent=1, acol='red', fs=180, at=[522.4, S('necessary', 523.5) - 0.2])
sh(524.62, 'doc', header='NATIONAL TRANSPORTATION SAFETY BOARD · RAILROAD INVESTIGATION REPORT RIR-24-05', src=R, fs=46,
   body='Norfolk Southern Railway Train Derailment with Subsequent Hazardous Materials Release and Fires · East Palestine, Ohio · [[adopted June 25, 2024]]', hlAt=S('June', 525.5))
sh(529.94, 'box', src=R + ', executive summary', boxes=[I('doc_notnecessary.png', DOC, cap='NTSB final report', push=0.18, origin='35% 30%')],
   notes=[N('STABLE', 1560, 260, S('stable', 533.5) - 0.2, 'yellow', size=70, w=330), N('the whole time', 1560, 350, S('whole', 534) - 0.2, 'white', size=46, w=330),
          N('no polymerization', 1560, 470, S('temperature', 538.5) - 0.2, 'red', size=46, w=330), N('confirmed', 1560, 540, S('confirmed', 543) - 0.3, 'red', size=52, w=330)])
sh(544.28, 'doc', header='NTSB FINAL REPORT RIR-24-05 · EXECUTIVE SUMMARY', src=R, fs=50,
   body='"The vent and burn procedure was [[not necessary]] to prevent a polymerization-induced explosion."', hlAt=S('not', 549) - 0.2)
sh(552.3, 'box', src=R + ', executive summary', boxes=[I('doc_compromised.png', DOC, cap='NTSB final report', push=0.16, origin='55% 80%')],
   notes=[N('COMPROMISED', 1560, 260, S('compromised', 557) - 0.2, 'red', size=56, w=330), N('dissent never', 1560, 380, S('dissenting', 561) - 0.2, 'white', size=46, w=330),
          N('reached him', 1560, 440, S('dissenting', 561) + 0.3, 'white', size=46, w=330)])
sh(564.02, 'head', lines=['"UNJUSTIFIED."'], accent=0, acol='red', fs=200, at=[564.1], sub='— the NTSB', subAt=S('unjustified', 566) + 0.3, src=R)
sh(568.34, 'head', lines=['The report found', 'more problems.'], accent=1, acol='yellow', fs=130, at=[568.4, 569.6])
sh(571.16, 'box', src=NTSB + ' · ' + R + ', fig. 20', boxes=[I('ntsb_dot111.png', A169, cap='Punctured DOT-111 tank car', push=0.12)],
   notes=[N('DOT-111', NX, 280, S('DOT-111', 578) - 0.2, 'red', size=80), N('older design', NX, 380, S('older', 576) - 0.2, 'white', size=50),
          N('started the fire', NX, 450, S('started', 573.5) - 0.2, 'yellow', size=50)])
sh(582.9, 'head', lines=['If those cars had survived:', 'likely NO vinyl chloride release'], accent=1, acol='red', fs=100, at=[583.0, S('never', 588) - 0.3], src=R)
sh(591.56, 'list', items=[dict(text='→ DOT-111 tank cars', at=591.6), dict(text='→ slow train info to responders', at=S('slow', 594) - 0.2),
                          dict(text='→ volunteer firefighter training', at=S('volunteer', 600) - 0.3, accent=True)], fs=96, src=R)
sh(603.06, 'counter', steps=[dict(value=600, label='class action settlement · no admission of wrongdoing', at=S('six-hundred-million-dollar', 605) - 0.2, dur=1.2, accent=True)],
   prefix='$', suffix='M', fs=300, src='In re: East Palestine Train Derailment, U.S. District Court, N.D. Ohio')
sh(610.6, 'counter', steps=[dict(value=34, label='new safety recommendations', at=610.7, dur=0.9, accent=True)], fs=300, src=R)
F(616.74, 'T1', 1.0)                                                    # back to the beginning
sh(619.12, 'saiddid', lk='THE CRASH', said=['An', 'accident.'], saidAt=[619.2, S('accident', 622.5) - 0.2], rk='THE BLACK CLOUD', did=['A', 'decision.'],
   didAt=S('decision', 626) - 0.2, sfs=120, dfs=130)
F(627.62, 'T6', 6.0)                                                    # a decision made in 13 minutes…
sh(633.98, 'head', lines=['The most dangerous failure', "isn't in the steel."], accent=1, acol='yellow', fs=110, at=[634.0, S('steel', 636.5) - 0.3])
sh(637.5, 'head', lines=["It's in the", 'CONVERSATION.'], accent=1, acol='red', fs=170, at=[637.55, S('conversation', 638.3) - 0.2])
sh(639.38, 'title', lines=['Subscribe to', 'Wrecklore'], kicker='The full story behind engineering disasters', sub='Should a railroad make the call on a vent and burn?')
END = 651.4

# ---------- music (FreePD.com, CC0 / public domain) ----------
music = [dict(file='audio/m_Hidden_Danger_A.wav', start=0.0, dur=12.9, vol=0.30),
         dict(file='audio/m_Tension.wav', start=22.6, dur=36.0, vol=0.30),
         dict(file='audio/m_Mysterious_Lights.wav', start=58.4, dur=80.8, vol=0.28),
         dict(file='audio/m_The_Abyss.wav', start=139.3, dur=63.0, vol=0.32),
         dict(file='audio/m_Hidden_Truth.wav', start=232.0, dur=89.0, vol=0.30),
         dict(file='audio/m_Asking_Questions.wav', start=321.2, dur=55.4, vol=0.28),
         dict(file='audio/m_Driving_Concern.wav', start=376.6, dur=113.5, vol=0.32),
         dict(file='audio/m_Final_Step.wav', start=522.2, dur=94.4, vol=0.28),
         dict(file='audio/m_Emotional_Piano.wav', start=616.6, dur=END - 616.6, vol=0.38)]
# ---------- sound effects (original, synthesized) ----------
X = lambda f, t, v, **k: dict(file=f'audio/sfx/{f}.wav', t=round(t, 2), vol=v, **k)
TD1, TD2 = 19.94, 497.36           # vent-and-burn charges in the two T5 uses
TE = 217.6                          # derailment in T4
sfx = [X('fire_bed', 0.0, 0.25, dur=5.5), X('shutter', 0.05, 0.4), X('hit', 5.66, 0.45), X('tick', 9.0, 0.4), X('stamp', S('nine', 11) - 0.3, 0.45),
       X('drone', 12.9, 0.35, dur=7.0), X('whoosh', 12.7, 0.3), X('explosion_big', TD1 - 0.03, 0.9), X('fire_bed', TD1 + 0.5, 0.35, dur=7.0),
       X('hit', 22.7, 0.5), X('typewriter', 26.8, 0.3), X('stamp', S('never', 32.5) - 0.2, 0.5), X('whoosh', 34.3, 0.3), X('heartbeat', 39.7, 0.45), X('heartbeat', 40.7, 0.45),
       X('train_rumble', 41.6, 0.3, dur=7.6), X('pop', S('minute', 50.5) - 0.2, 0.35), X('pop', S('official', 52.5) - 0.2, 0.35), X('pop', S('who', 55) - 0.2, 0.35),
       X('whoosh', 58.2, 0.4), X('hit', 58.46, 0.55),
       X('train_rumble', 61.3, 0.45, dur=11.2), X('horn', 61.6, 0.35), X('shutter', 72.3, 0.4), X('hit', 74.5, 0.4), X('tick', 78.2, 0.4), X('tick', S('hundred', 79.7) - 0.1, 0.4),
       X('stamp', S('eighteen', 83.5) - 0.3, 0.45), X('whoosh', 87.5, 0.3), X('pop', S('engineer', 95) - 0.2, 0.35), X('pop', S('conductor', 97.5) - 0.2, 0.35), X('pop', S('trainee', 99) - 0.2, 0.35),
       X('hit', 100.45, 0.55), X('flame_burst', S('fire', 103.5) - 0.3, 0.4), X('shutter', 105.0, 0.4), X('whoosh', 111.7, 0.3), X('creak', 119.0, 0.35), X('shutter', 123.95, 0.4),
       X('shutter', 128.0, 0.4), X('riser', 137.2, 0.35), X('hit', 139.45, 0.5), X('shutter', 142.3, 0.4), X('alarm_beep', 148.2, 0.2), X('alarm_beep', S('hundred', 158.5) - 0.2, 0.3),
       X('whoosh', 161.5, 0.3), X('stamp', S('crew', 170.5) - 0.2, 0.5), X('hit', 171.55, 0.7), X('train_rumble', 172.9, 0.3, dur=9.9), X('flame_burst', 180.1, 0.3),
       X('whoosh', 182.8, 0.3), X('tick', 188.6, 0.4), X('alarm_beep', S('two', 196) - 0.1, 0.4), X('riser', 197.5, 0.35), X('drone', 199.4, 0.3, dur=3.2),
       X('radio_click', 202.35, 0.5), X('radio_click', 210.9, 0.45),
       X('train_rumble', 211.5, 0.3, dur=6.2), X('brake_squeal', 213.0, 0.35), X('snap', TE - 0.05, 0.5), X('derail_crash', TE + 0.1, 0.8), X('brake_squeal', TE + 0.4, 0.3),
       X('flame_burst', TE + 1.5, 0.5), X('fire_bed', TE + 2.0, 0.4, dur=12.0), X('boom', S('Fire', 228.3) + 0.1, 0.45),
       X('whoosh', 232.0, 0.3), X('stamp', S('Fact', 236.5) - 0.1, 0.45), X('typewriter', 240.5, 0.3), X('hit', 245.5, 0.45), X('tick', 253.3, 0.45),
       X('alarm_beep', 258.8, 0.3), X('sirens', 267.8, 0.55, dur=4.0), X('shutter', 270.8, 0.4), X('fire_bed', 271.0, 0.25, dur=8.0), X('tick', 279.0, 0.4),
       X('riser', 282.6, 0.3), X('hit', 284.45, 0.45), X('shutter', 286.6, 0.4), X('pop', 289.8, 0.3), X('pop', S('flammable', 296.5) - 0.2, 0.3), X('stamp', S('carcinogen', 300.5) - 0.6, 0.5),
       X('shutter', 302.4, 0.4), X('fire_bed', 302.5, 0.2, dur=12.0), X('hit', 317.35, 0.4), X('stamp', 319.1, 0.45), X('riser', 320.0, 0.3), X('hit', S('polymerization', 324) - 0.3, 0.5),
       X('pop', S('popping', 331.5), 0.3), X('pop', S('popping', 331.5) + 0.25, 0.25), X('pop', S('More', 334.5), 0.3), X('pop', S('popping', 335.5), 0.3),
       X('boom', S('bursts', 342.9) - 0.1, 0.35), X('tick', 344.2, 0.35), X('stamp', S('three', 350.5) - 0.2, 0.4), X('hit', 360.45, 0.4),
       X('shutter', 366.5, 0.4), X('whoosh', 376.6, 0.35), X('hit', 376.8, 0.6), X('whoosh', 386.7, 0.3), X('stamp', S('opposite', 393.5) - 0.2, 0.55),
       X('typewriter', 395.2, 0.3), X('heartbeat', 411.7, 0.45), X('heartbeat', 412.7, 0.45), X('hit', 413.05, 0.55), X('heartbeat', 415.5, 0.5), X('heartbeat', 416.4, 0.5),
       X('tick', 417.0, 0.35), X('tick', 423.0, 0.4), X('stamp', 429.9, 0.55), X('shutter', 443.9, 0.4), X('hit', 457.3, 0.45),
       X('typewriter', 459.6, 0.3), X('stamp', S('thirteen', 469) - 0.3, 0.55)] + \
      [X('tick', 468.35 + i * 1.0, 0.45) for i in range(7)] + \
      [X('typewriter', 475.8, 0.3), X('drone', 480.4, 0.35, dur=8.0), X('heartbeat', 482.3, 0.4), X('heartbeat', 483.3, 0.4), X('heartbeat', 484.3, 0.4),
       X('heartbeat', 485.3, 0.45), X('heartbeat', 486.3, 0.45), X('heartbeat', 487.3, 0.5), X('stamp', S('yes', 490.3) - 0.1, 0.5),
       X('drone', 490.4, 0.3, dur=6.9), X('explosion_big', TD2 - 0.03, 0.95), X('fire_bed', TD2 + 0.5, 0.35, dur=24.0),
       X('hit', 522.4, 0.5), X('typewriter', 524.8, 0.3), X('shutter', 530.0, 0.4), X('stamp', S('not', 549) - 0.2, 0.6), X('shutter', 552.4, 0.4),
       X('stamp', S('unjustified', 566) - 0.2, 0.6), X('whoosh', 568.3, 0.3), X('shutter', 571.2, 0.4), X('hit', 583.0, 0.4), X('pop', 591.6, 0.3), X('pop', S('slow', 594) - 0.2, 0.3),
       X('pop', S('volunteer', 600) - 0.3, 0.3), X('tick', 603.2, 0.4), X('tick', 610.7, 0.4), X('rewind', 616.4, 0.4), X('train_rumble', 616.7, 0.25, dur=2.4),
       X('stamp', S('decision', 626) - 0.2, 0.45), X('whoosh', 627.5, 0.3), X('hit', 637.55, 0.5), X('whoosh', 639.2, 0.4), X('ding', 640.3, 0.45)]

# ---- mix balance: voice first. Loud SFX lowered under the narration; only the solo moments (pauses) play loud ----
SCALE = {'train_rumble': 0.35, 'fire_bed': 0.3, 'flame_burst': 0.35, 'boom': 0.3, 'hit': 0.45, 'derail_crash': 0.75, 'explosion_big': 0.8, 'sirens': 0.7,
         'radio_click': 0.6, 'horn': 0.35, 'brake_squeal': 0.3, 'drone': 0.35, 'heartbeat': 0.4}
SOLO = [(19.87, 22.87), (221.49, 224.89), (229.98, 232.38), (268.02, 270.62), (497.31, 501.51)]      # narration pauses: sound plays alone
LOUD = ('explosion_big', 'derail_crash', 'sirens', 'fire_bed', 'boom', 'flame_burst')
extra = []
for x in sfx:
    name = x['file'].split('/')[-1][:-4]
    win = [(a, b) for a, b in SOLO if a - 0.3 <= x['t'] <= b]
    base = x['vol']
    x['vol'] = round(base * (1.0 if win and name in LOUD else SCALE.get(name, 0.5)), 3)
    if win and name in LOUD and x.get('dur') and x['t'] + x['dur'] > win[0][1] + 0.6:     # long bed: loud only while the voice is silent
        end = x['t'] + x['dur']; cut = win[0][1] + 0.4
        x['dur'] = round(cut - x['t'], 2)
        extra.append(dict(file=x['file'], t=round(cut, 2), vol=round(base * SCALE.get(name, 0.5), 3), dur=round(end - cut, 2), ss=round(cut - x['t'], 2)))
sfx += extra
for m in music:
    m['vol'] = round(m['vol'] * 0.6, 3)

finish(cuts=[0, 61.38, 139.4, 232.1, 321.34, 416.96, 522.36, END], names=['hook', 'train', 'detectors', 'fire', 'poly', 'room', 'verdict'],
       tags=[], music=music, sfx=sfx, archive=D3, end=END, caption_fixes={})
