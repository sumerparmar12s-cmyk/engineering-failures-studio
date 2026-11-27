#!/usr/bin/env python3
"""Shot list: The Engine That Fell Off — UPS Flight 2976 (≈6:00). Times are absolute VO seconds."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.claude/skills/engineering-failures-video/scripts'))
from vidlib import A169, NX, N, I, finish, init, sh, w

init(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent))
S = lambda word, near: w(word, near)

# 3D clips (original animation) are pre-rendered in real3d/; NTSB photos are in media/
D3 = {k: {'file': f'real3d/{k}.mp4', 'crop': 'eq=saturation=1.18:brightness=0.035,'} for k in ['A1', 'A2', 'A3', 'C', 'C2', 'D', 'B1', 'B2', 'B3']}
SRC3 = 'Animated reconstruction (illustrative) · Wrecklore'
def F(t0, key, ss=0.0): sh(t0, 'full', clip=dict(src=key, ss=ss), src=SRC3)
NTSB = 'NTSB (public domain)'

# ================= HOOK =================
DV = 'U.S. Air National Guard photo by Phil Speck · DVIDS (public domain)'
sh(0.0, 'box', src=DV, boxes=[I('dvids_fire_foam.jpg', A169, cap='Louisville, Kentucky · the night of the crash', push=0.08, at=0.0)],
   notes=[N('NOVEMBER 4, 2025', NX, 300, 0.25, 'yellow', size=64), N('5:12 p.m.', NX, 400, 1.3, 'white', size=54)])
F(3.52, 'A1')                                                          # takeoff roll, rotation, engine tears off
F(13.74, 'A3')                                                         # staggering on, toward the fence
sh(18.3, 'head', lines=['The part that broke', 'had FAILED BEFORE.'], accent=1, acol='red', fs=130, at=[18.4, S('failed', 21) - 0.3])
sh(23.22, 'timeline', events=[dict(date='2002', label='first reports', at=23.3), dict(date='2025', label='Louisville', at=S('twenty', 25) - 0.1, accent=True)],
   gap=dict(**{'from': 0, 'to': 1}, label='20+ years of warnings', at=S('again', 24.5)))
sh(26.98, 'head', lines=['So why was this plane', 'still flying?'], accent=1, acol='yellow', fs=130, at=[27.0, S('still', 28.5) - 0.2])
sh(30.0, 'title', lines=['The Engine', 'That Fell Off'], kicker='UPS Flight 2976 · November 4, 2025', sub='and the warning written 14 years earlier')
# ================= THE FLIGHT =================
sh(35.62, 'blueprint', kind='structure', title='Flight 2976 · Louisville to Honolulu (not to scale)',
   paths=[dict(d='M 1500 520 Q 960 180 420 600', at=35.9, dur=1.6, color='yellow', width=6),
          dict(d='M 1500 520 m -14 0 a 14 14 0 1 0 28 0 a 14 14 0 1 0 -28 0', at=35.8, color='red', width=8, dur=0.4),
          dict(d='M 420 600 m -14 0 a 14 14 0 1 0 28 0 a 14 14 0 1 0 -28 0', at=37.2, color='red', width=8, dur=0.4)],
   labels=[dict(text='SDF · Louisville', x=1500, y=560, at=36.0, color='white', size=46, align='center'),
           dict(text='HNL · Honolulu', x=420, y=640, at=37.3, color='white', size=46, align='center'),
           dict(text='8+ hours across the Pacific', x=960, y=300, at=S('eight', 38), color='yellow', size=48, align='center')])
F(40.32, 'C')                                                          # the MD-11: three engines
sh(49.58, 'counter', steps=[dict(value=34, label='years in service · Thai Airways, then UPS', at=49.7, dur=1.2),
                            dict(value=92992, label='hours in the air', at=S('ninety-three', 58) - 0.3, dur=1.4, accent=True)], fs=260)
sh(61.92, 'list', items=[dict(text='3 pilots', at=62.0), dict(text='30,000+ flight hours', at=S('thirty', 65) - 0.2, accent=True)], fs=130)
sh(68.54, 'head', lines=['5:12 P.M.'], accent=0, fs=200, at=[68.6], sub='takeoff roll · runway 17R', subAt=S('throttles', 72) - 0.4)
F(73.86, 'A2')                                                         # slow motion: the separation
# ================= THE NINETEEN SECONDS =================
sh(96.42, 'head', lines=['ENGINE 1', 'FIRE'], accent=1, acol='red', fs=200, at=[96.45, 97.0])
sh(99.52, 'box', src='NTSB investigative update, Jan 2026: flight data recorder',
   boxes=[I('ntsb_fdr_fire.jpg', dict(x=110, y=330, w=1700, h=458), fit='contain', bg='#ffffff', push=0.02, cap='Flight data: engine 1 fire parameter switches to FIRE')],
   notes=[N('NO FIRE → FIRE', 1180, 200, 100.0, 'red', size=60, arrow=[[1150, 260], [560, 560]])])
sh(102.64, 'counter', steps=[dict(value=212, label='mph · and it would not climb', at=S('more', 103) - 0.1, dur=1.2, accent=True)], suffix=' mph', more='more than', fs=260)
sh(108.08, 'blueprint', kind='structure', title='How high it got (not to scale)',
   paths=[dict(d='M 160 800 H 1760', at=108.2, dur=0.8),
          dict(d='M 1500 800 V 330 M 1460 330 H 1540 V 390 H 1460 Z', at=108.5, color='yellow'),
          dict(d='M 160 800 Q 500 800 700 760 L 1300 742 Q 1500 744 1700 800', at=S('thirty', 110) - 0.6, color='red', width=7, dur=1.3)],
   labels=[dict(text='control tower ≈ 200 ft', x=1500, y=280, at=108.8, color='yellow', size=44, align='center'),
           dict(text='Flight 2976: about 30 ft', x=900, y=680, at=S('thirty', 110), color='red', size=56, align='center')])
F(112.52, 'D')                                                         # aerial: fence, warehouse roof, storage yard
sh(S('storage', 121) - 0.15, 'box', src=DV, boxes=[I('dvids_tanks.jpg', A169, cap='The petroleum recycling facility after the crash', push=0.07)],
   notes=[N('storage yard &', NX, 280, S('storage', 121) + 0.2, 'white', size=48), N('recycling facility', NX, 350, S('recycling', 122) - 0.2, 'red', size=56)])
sh(126.6, 'counter', steps=[dict(value=19, label='seconds after the engine separated', at=126.7, dur=1.0, accent=True)], fs=300)
sh(130.82, 'list', items=[dict(text='3 pilots', at=S('pilots', 131.5) - 0.2), dict(text='11 people on the ground', at=S('eleven', 133) - 0.2),
                          dict(text='1 more, weeks later', at=S('fifteenth', 136) - 0.2, accent=True)], fs=110)
# ================= THE PART =================
sh(139.48, 'box', src=DV, boxes=[I('dvids_wreck_engine.jpg', A169, cap='Kentucky National Guard team at the crash site, Nov 5, 2025', push=0.07, origin='60% 40%')],
   notes=[N('What could tear', NX, 260, 139.6, 'white', size=58), N('an engine off a jet?', NX, 340, S('off', 140.5) - 0.2, 'yellow', size=58)])
sh(142.0, 'box', src='NTSB preliminary report, fig. 10',
   boxes=[I('ntsb_bearing_parts.jpg', A169, cap='Recovered by the NTSB: the aft mount bearing and hardware', push=0.07)],
   notes=[N('one small part', NX, 330, S('small', 143.5) - 0.3, 'yellow', size=60)])
F(146.26, 'B1')                                                        # 3D: pylon, aft mount, lugs, ball, race
sh(160.02, 'box', src='NTSB investigative update, fig. 2 (Materials Laboratory)',
   boxes=[I('ntsb_race_split.jpg', A169, cap='The bearing race, fractured into two pieces', push=0.06)],
   notes=[N('SPLIT IN TWO', NX, 300, S('split', 161.5) - 0.3, 'red', size=64, arrow=[[1240, 360], [1000, 520]])])
F(164.82, 'B2')                                                        # 3D: fatigue crack from the groove, race splits
sh(175.48, 'box', src='NTSB preliminary report, fig. 7',
   boxes=[I('ntsb_pylon_lugs.jpg', A169, cap='The fractured forward and aft lugs', push=0.07, origin='75% 50%')],
   notes=[N('fatigue cracks here too', NX, 330, 175.7, 'red', size=52)])
F(178.58, 'B3')                                                        # 3D: nothing left holding the engine
# ================= THE WARNINGS =================
sh(183.24, 'section', no='02', name=['The', 'Warnings'], sub='2002 – 2017', img='ntsb_clevis_bearing.jpg', cap='NTSB: the failed bearing (left) and an intact one (right)')
sh(189.82, 'timeline', events=[dict(date='2002', label='fracture reports begin', at=S('2002', 190.5) - 0.2),
                                dict(date='2017', label='still being reported', at=S('2017', 192) - 0.2, accent=True)],
   gap=dict(**{'from': 0, 'to': 1}, label='same bearing, other MD-11s', at=S('fractures', 194) - 0.2))
sh(198.16, 'doc', header='BOEING SERVICE LETTER MD-11-SL-54-104-A · FEBRUARY 7, 2011',
   body='Informs operators of [[four previously reported bearing race failures]] on three different airplanes.', hlAt=S('four', 203) - 0.2, fs=44)
sh(207.08, 'blueprint', kind='structure', title='Bearing race cross-section (simplified)',
   paths=[dict(d='M 360 360 H 760 V 640 H 360 Z', at=207.2), dict(d='M 540 640 V 600 H 580 V 640', at=207.5, color='red', width=8),
          dict(d='M 1160 360 H 1560 V 640 H 1160 Z', at=S('new', 208.5) - 0.2)],
   labels=[dict(text='OLD · with groove', x=560, y=700, at=207.4, color='red', size=48, align='center'),
           dict(text='NEW · no groove', x=1360, y=700, at=S('new', 208.5), color='yellow', size=48, align='center')])
sh(210.86, 'doc', header='BOEING SERVICE LETTER · 2011 · CONCLUSION',
   body='"A review of the spherical bearing failure by Boeing determined [[it would not result in a safety of flight condition.]]"', hlAt=S('safety-of-flight', 215.5) - 0.6, fs=44)
sh(219.98, 'head', lines=['The old design:', 'still allowed.'], accent=1, acol='red', fs=140, at=[220.0, S('old', 221.5)])
sh(223.22, 'head', lines=['2014: Boeing asks the FAA', 'to inspect LESS often'], accent=1, acol='yellow', fs=110, at=[223.3, S('stretch', 228) - 0.2])
sh(S('nineteen', 231) - 1.2, 'bars', lines=['Lug inspection interval'], bars=[dict(value='19,900', label='flights · before', h=0.55, at=S('nineteen', 231) - 0.2),
                                                         dict(value='29,200', label='flights · after 2014', h=0.8, at=S('twenty-nine', 234) - 0.2, color='red')])
sh(238.32, 'counter', steps=[dict(value=5, label='fractures already reported', at=238.4, dur=0.8, accent=True)], fs=300)
sh(241.84, 'head', lines=['THE FAA', 'AGREED.'], accent=1, acol='red', fs=200, at=[241.86, 242.3])
sh(243.7, 'bars', lines=['Flights flown by the accident jet'], bars=[dict(value='19,900', label='old limit', h=0.5, at=244.0),
                                                                       dict(value='21,043', label='this jet', h=0.53, at=S('twenty-one', 246) - 0.2, color='red'),
                                                                       dict(value='29,200', label='new limit', h=0.8, at=S('new', 253.5) - 0.2)])
sh(255.88, 'doc', header='NTSB INVESTIGATIVE HEARING · MAY 2026 · WITNESS TESTIMONY',
   body='"There was a [[misunderstanding initially 20 years ago]] about the severity of the event that might result from failure of this bearing."', hlAt=S('misunderstanding', 260) - 0.2, fs=42)
# ================= IT HAPPENED BEFORE =================
sh(266.78, 'section', no='03', name=['It Happened', 'Before'], sub='Chicago · May 25, 1979', img='sep_still.jpg', cap='Illustration')
sh(269.62, 'timeline', events=[dict(date='1979', label='AA 191 · DC-10', at=S('1979', 270) - 0.1, accent=True),
                                dict(date='2025', label='UPS 2976 · MD-11', at=S('ancestor', 275) - 0.2, accent=True)],
   gap=dict(**{'from': 0, 'to': 1}, label='left engine + pylon, on takeoff', at=S('left', 277) - 0.2))
sh(281.3, 'counter', steps=[dict(value=273, label='people died · Chicago, 1979', at=281.4, dur=1.0, accent=True)], fs=280)
sh(283.72, 'saiddid', lk='THE CAUSE IN 1979', said=['A maintenance', 'shortcut'], saidAt=[S('maintenance', 286), S('shortcut', 286.5)],
   rk='THE RESULT', did=['Engine leaves', 'the wing'], didAt=S('result', 289) - 0.2, sfs=100, dfs=100)
# ================= AFTERMATH =================
F(293.9, 'C2', 0.0)                                                     # the fleet grounded
sh(301.74, 'box', src=DV, boxes=[I('dvids_wreckage_field.jpg', A169, cap='Louisville, November 5, 2025', push=0.06)],
   notes=[N('Nov 2025: MD-11 & DC-10 grounded', NX, 250, 301.85, 'white', size=40, w=620),
          N('Jan 2026: UPS retires its MD-11s', NX, 360, S('retired', 304) - 0.3, 'yellow', size=40, w=620),
          N('May 2026: MD-11 cleared to fly', NX, 470, S('allowed', 312) - 0.3, 'red', size=40, w=620)])
sh(316.06, 'doc', header='NTSB · AVIATION INVESTIGATION DCA26MA024', body='Final report and probable cause: [[STILL TO COME]]', hlAt=S('still', 319) - 0.2, fs=56)
sh(323.04, 'counter', steps=[dict(value=19, label='seconds', at=323.1, dur=0.6), dict(value=15, label='lives', at=S('Fifteen', 324) - 0.1, dur=0.5, accent=True)], fs=300)
sh(S('warning', 325.5) - 0.2, 'head', lines=['A warning, 14 years early:', '"nothing to worry about."'], accent=1, acol='red', fs=96,
   at=[S('warning', 325.5), S('nothing', 330) - 0.2])
sh(332.84, 'box', src=DV, boxes=[I('dvids_wreck_survey.jpg', A169, cap='The crash site, November 5, 2025', push=0.06)],
   notes=[N('the most dangerous failures', NX, 280, S('dangerous', 334) - 0.3, 'white', size=46, w=600), N('= the ones we decided', NX, 360, S('decided', 337) - 0.3, 'yellow', size=46, w=600),
          N('are harmless', NX, 440, S('harmless', 338) - 0.3, 'red', size=56)])
sh(339.12, 'title', lines=['Subscribe to', 'Wrecklore'], kicker='When the final report drops, we break it down', sub='Should jets this old still be flying?')
END = 357.0

# ---------- music (FreePD.com, CC0 / public domain) ----------
music = [dict(file='audio/m_Action_Investigation.wav', start=0.0, dur=31.0, vol=0.30),
         dict(file='audio/m_Ambiant_Inconvenient_Truth.wav', start=30.0, dur=44.6, vol=0.30),
         dict(file='audio/m_Tension.wav', start=73.6, dur=round(S('flames', 124) + 1.6 - 73.6, 2), vol=0.32),
         dict(file='audio/m_Mysterious_Lights.wav', start=139.2, dur=44.6, vol=0.28),
         dict(file='audio/m_The_Abyss.wav', start=183.0, dur=84.4, vol=0.32),
         dict(file='audio/m_Hidden_Danger_A.wav', start=266.5, dur=28.0, vol=0.36),
         dict(file='audio/m_Emotional_Piano.wav', start=293.6, dur=END - 293.6, vol=0.38)]
# ---------- sound effects (original, synthesized) ----------
X = lambda f, t, v, **k: dict(file=f'audio/sfx/{f}.wav', t=round(t, 2), vol=v, **k)
sep1, sep2 = S('tears', 10.5), S('entire', 81)
sfx = [X('hit', 0.0, 0.5), X('shutter', 0.05, 0.4), X('fire_bed', 0.0, 0.18, dur=3.6), X('whoosh', 3.2, 0.35), X('jet_roll', 3.5, 0.55),
       X('metal_tear', sep1 - 0.15, 0.75), X('hit', sep1 - 0.1, 0.6), X('flame_burst', sep1 + 0.3, 0.55), X('fire_bed', sep1 + 0.5, 0.25, dur=7.0),
       X('boom', S('down', 16.5), 0.55), X('heartbeat', 19.0, 0.5), X('heartbeat', 20.0, 0.5), X('heartbeat', 21.0, 0.5), X('stamp', S('failed', 21) - 0.25, 0.5),
       X('heartbeat', 22.0, 0.45), X('heartbeat', 23.0, 0.45), X('whoosh', 23.0, 0.3), X('riser', 25.0, 0.45), X('hit', 30.0, 0.6), X('whoosh', 29.7, 0.4),
       X('whoosh', 35.4, 0.3), X('jet_pass', 39.5, 0.22), X('whoosh', 49.4, 0.3), X('tick', 49.8, 0.4), X('pop', 62.0, 0.4), X('pop', S('thirty', 65) - 0.2, 0.4),
       X('tick', 68.6, 0.4), X('jet_roll', S('throttles', 72) - 0.6, 0.5),
       X('metal_tear', sep2 - 0.2, 0.8), X('hit', sep2 - 0.1, 0.6), X('flame_burst', sep2 + 0.4, 0.5), X('fire_bed', sep2 + 0.6, 0.3, dur=13.5),
       X('thud', S('crashed', 90.5), 0.6), X('flame_burst', S('Fire', 93) - 0.1, 0.4),
       X('fire_bell', 96.45, 0.45), X('jet_roll', 99.4, 0.3, ss=3.0), X('tick', 102.8, 0.4), X('whoosh', 107.9, 0.3),
       X('whoosh', S('cleared', 113) - 0.4, 0.4), X('crunch', S('roof', 118) - 0.3, 0.55), X('boom', S('storage', 121) - 0.2, 0.7), X('fire_bed', S('flames', 124), 0.35, dur=3.5),
       X('tick', 126.7, 0.55), X('tick', 127.7, 0.55), X('tick', 128.7, 0.55), X('tick', 129.7, 0.55),
       X('whoosh', 139.3, 0.35), X('shutter', 142.05, 0.5), X('clank', S('joint', 151.5) - 0.1, 0.4), X('clank', S('lugs', 153) - 0.1, 0.4),
       X('clank', S('spherical', 154.5) - 0.1, 0.4), X('clank', S('ball', 156.5) - 0.1, 0.35), X('clank', S('race', 158.5) - 0.1, 0.4),
       X('shutter', 160.1, 0.5), X('creak', S('fatigue', 167) - 0.2, 0.45), X('snap', 164.82 + 8.6, 0.55), X('shutter', 175.55, 0.5),
       X('snap', S('let', 179) - 0.1, 0.5), X('thud', S('let', 179) + 1.0, 0.5),
       X('hit', 183.25, 0.6), X('riser', 184.5, 0.3), X('typewriter', 190.0, 0.3), X('typewriter', 198.3, 0.35), X('pop', 207.3, 0.35),
       X('typewriter', 211.0, 0.3), X('hit', S('safety-of-flight', 215.5) - 0.6, 0.55), X('stamp', 220.0, 0.4),
       X('typewriter', 223.4, 0.25), X('stamp', S('nineteen', 231) - 0.2, 0.4), X('stamp', S('twenty-nine', 234) - 0.2, 0.5),
       X('hit', 238.35, 0.5), X('stamp', 241.86, 0.65), X('tick', 244.0, 0.4), X('stamp', S('twenty-one', 246) - 0.2, 0.5), X('typewriter', 256.1, 0.3),
       X('rewind', 266.4, 0.45), X('whoosh', 266.6, 0.35), X('boom', 281.35, 0.4), X('whoosh', 293.7, 0.3),
       X('stamp', S('grounded', 297) - 0.3, 0.45), X('pop', S('retired', 304) - 0.3, 0.35), X('pop', S('allowed', 312) - 0.3, 0.35),
       X('typewriter', 316.2, 0.3), X('stamp', S('still', 319) - 0.2, 0.5), X('hit', 323.05, 0.45), X('hit', S('Fifteen', 324) - 0.1, 0.45),
       X('whoosh', 332.6, 0.3), X('whoosh', 338.9, 0.4), X('hit', 339.15, 0.45), X('ding', S('notifications', 344.5) - 0.1, 0.5)]

# ---- mix balance: voice first. Jet engine almost silent, all other SFX and music lowered under the narration ----
SCALE = {'jet_roll': 0.06, 'jet_pass': 0.2, 'fire_bed': 0.22, 'metal_tear': 0.35, 'flame_burst': 0.3, 'boom': 0.3, 'crunch': 0.3, 'thud': 0.4, 'hit': 0.45}
for x in sfx:
    name = x['file'].split('/')[-1][:-4]
    x['vol'] = round(x['vol'] * SCALE.get(name, 0.5), 3)
for m in music:
    m['vol'] = round(m['vol'] * 0.6, 3)

finish(cuts=[0, 73.86, 139.48, 266.78, END], names=['hook', 'crash', 'part', 'echo'], tags=[], music=music, sfx=sfx, archive=D3, end=END,
       caption_fixes={})
