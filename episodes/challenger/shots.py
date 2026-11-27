#!/usr/bin/env python3
"""Shot list: 73 Seconds — the Challenger disaster (≈5:30). Times are absolute VO seconds."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.claude/skills/engineering-failures-video/scripts'))
from vidlib import A169, NX, N, I, finish, init, sh, w

init(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent))

# ---------- footage: NASA colour film, vivid grade + camera moves ----------
BASE = "fps=30,scale=1920:1440,setsar=1,"
LOOK = "eq=saturation=1.45:contrast=1.08,vignette=angle=PI/5,"   # assemble later applies saturation 0.85 to full shots
ZP = ":d=1:s=1440x1080:fps=30,"
MOVES = {
    'in':   "zoompan=z='min(1.25,1.02+0.0012*on)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'" + ZP,
    'out':  "zoompan=z='max(1.02,1.22-0.0011*on)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'" + ZP,
    'panr': "zoompan=z=1.18:x='(iw-iw/zoom)*min(1,on/200)':y='ih/2-ih/zoom/2'" + ZP,
    'panl': "zoompan=z=1.18:x='(iw-iw/zoom)*(1-min(1,on/200))':y='ih/2-ih/zoom/2'" + ZP,
    'up':   "zoompan=z=1.18:x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*(1-min(1,on/200))'" + ZP,
}
archive = {f'C_{m}': {'file': 'real/challenger_pd.mpg', 'crop': BASE + mv + LOOK} for m, mv in MOVES.items()}
KB = ['51L-S-002_in', '51l-s-029_out', 'S85-40074_in', 'S85-44253_in', 'NHQ202501230017_in', 's26-s-030_up', '51l-s-156_in', '51l-s-155_panr', 'S85-41239_up']
archive.update({f'K_{k}': {'file': f'real/kb_{k}.mp4', 'crop': ''} for k in KB})
SRC_F = 'NASA launch footage, Jan 28, 1986 (public domain)'
def F(t0, key, ss=0.0, src=None):
    sh(t0, 'full', clip=dict(src=key, ss=ss), src=src or (SRC_F if key.startswith('C_') else 'NASA photo (public domain)'))

S = lambda word, near: w(word, near)        # cue on a spoken word

# ================= HOOK =================
F(0.0, 'C_in', 89.0)                                  # flash-forward: the breakup
sh(4.58, 'doc', header='MORTON THIOKOL ENGINEERS · NIGHT OF JANUARY 27, 1986',
   body='Engineering recommendation: [[DO NOT LAUNCH]] below 53°F.', hlAt=S('begged', 5.78) - 0.2, fs=46)
sh(9.62, 'head', lines=['OVERRULED.'], accent=0, acol='red', fs=230, at=[9.64])
F(11.22, 'C_panr', 33.6)                               # climbing through a blue sky
sh(S('Challenger', 16.32) + 0.4, 'title', lines=['73 Seconds', 'to Disaster'], kicker='Space Shuttle Challenger · January 28, 1986',
   sub='the warning that was ignored')
# ================= THE MISSION =================
F(21.3, 'K_51L-S-002_in', 0.0)                       # Mission Control
sh(26.72, 'box', src='NASA official portrait, 1985',
   boxes=[I('S85-41239.jpg', dict(x=300, y=140, w=500, h=628), cap='Christa McAuliffe', pos='50% 25%', push=0.05)],
   notes=[N('Social studies teacher', 900, 220, S('social', 29.6) - 0.3, 'white', size=58),
          N('Concord, New Hampshire', 900, 310, S('Concord', 31.6) - 0.3, 'yellow', size=52),
          N('1 of 11,000+ applicants', 900, 430, S('eleven', 34.6) - 0.3, 'red', size=62),
          N('First teacher in space', 900, 560, S('first', 36.6) - 0.3, 'yellow', size=62)])
F(39.52, 'K_51l-s-155_panr', 0.0, 'NASA photo: Challenger liftoff, Jan 28, 1986')
sh(44.48, 'box', src='NASA official STS-51L crew portrait',
   boxes=[I('S85-44253.jpg', A169, cap='The crew of STS-51L', push=0.05)],
   notes=[N('Dick Scobee · commander', NX, 205, S('Scobee', 45.64) - 0.3, 'white', size=40),
          N('Michael Smith · pilot', NX, 285, S('Smith', 47.64) - 0.3, 'white', size=40),
          N('Judith Resnik', NX, 365, S('Resnik', 48.64) - 0.3, 'white', size=40),
          N('Ellison Onizuka', NX, 445, S('Onizuka', 49.64) - 0.3, 'white', size=40),
          N('Ronald McNair', NX, 525, S('McNair', 50.64) - 0.3, 'white', size=40),
          N('Gregory Jarvis', NX, 605, S('Jarvis', 52.64) - 0.3, 'white', size=40),
          N('Christa McAuliffe', NX, 685, S('Jarvis', 52.64) + 0.4, 'yellow', size=40)])
F(54.59, 'K_S85-40074_in', 0.0, 'NASA: McAuliffe and backup Barbara Morgan, Teacher in Space training, 1985')
# ================= THE COLD =================
sh(60.62, 'section', no='01', name=['A Freezing', 'Morning'], sub='Kennedy Space Center · Jan 28, 1986',
   img='51L-10147.jpg', cap='Ice on the launch tower', pos='50% 60%')
sh(63.12, 'box', src='NASA photo 51L-10147: ice on the launch complex, Jan 28, 1986',
   boxes=[I('51L-10147.jpg', dict(x=420, y=140, w=560, h=688), fit='cover', push=0.08, origin='60% 60%')],
   notes=[N('ICICLES', 1190, 360, S('icicles', 64.76) - 0.4, 'yellow', size=80, arrow=[[1180, 440], [930, 545]]),
          N('on the launch tower', 1190, 470, S('icicles', 64.76) + 0.3, 'white', size=50)])
sh(68.74, 'counter', steps=[dict(value=36, label='at launch', at=S('thirty-six', 69.26) - 0.4, accent=True),
                            dict(value=36, label='15° colder than any launch before', at=S('fifteen', 72.26) - 0.2, accent=True)],
   suffix='°F', more='just', fs=300)
F(76.02, 'C_up', 17.6)                                # boosters & tank on the pad
sh(79.62, 'blueprint', kind='structure', title='Solid rocket booster · field joint (simplified)',
   paths=[dict(d='M 330 300 L 380 230 L 430 300 Z', at=79.72, dur=0.5),
          dict(d='M 330 300 V 860 H 430 V 300', at=79.92, dur=1.0),
          dict(d='M 330 440 H 430 M 330 580 H 430 M 330 720 H 430', at=S('segments', 80.72) - 0.2, color='yellow'),
          dict(d='M 440 720 L 760 530', at=S('joints', 83.52) - 0.3, color='red', width=3),
          dict(d='M 800 300 H 980 V 760 H 800 Z M 1300 300 H 1120 V 760 H 1300 Z', at=S('joints', 83.52), dur=0.8),
          dict(d='M 980 300 V 760 M 1120 300 V 760', at=S('joints', 83.52) + 0.3, width=3),
          dict(d='M 1050 300 V 760', at=S('joints', 83.52) + 0.5, color='yellow', width=8),
          dict(d='M 1050 470 m -16 0 a 16 16 0 1 0 32 0 a 16 16 0 1 0 -32 0', at=S('two', 84.52) - 0.2, color='red', width=8, dur=0.4),
          dict(d='M 1050 590 m -16 0 a 16 16 0 1 0 32 0 a 16 16 0 1 0 -32 0', at=S('two', 84.52) + 0.2, color='red', width=8, dur=0.4)],
   labels=[dict(text='4 segments', x=200, y=880, at=S('segments', 80.72), color='yellow', size=40),
           dict(text='Primary O-ring', x=1340, y=440, at=S('rubber', 84.52), color='red', size=46),
           dict(text='Secondary O-ring', x=1340, y=560, at=S('rubber', 84.52) + 0.4, color='red', size=46),
           dict(text='≈ ¼ inch thick', x=1340, y=680, at=S('quarter', 85.52) - 0.2, color='yellow', size=46)])
sh(88.68, 'blueprint', kind='structure', title='At ignition: the O-ring must seal in milliseconds',
   paths=[dict(d='M 800 300 H 980 V 760 H 800 Z M 1300 300 H 1120 V 760 H 1300 Z', at=88.78, dur=0.6),
          dict(d='M 1050 300 V 760', at=88.78, color='yellow', width=8),
          dict(d='M 1050 470 m -16 0 a 16 16 0 1 0 32 0 a 16 16 0 1 0 -32 0', at=88.88, color='red', width=8, dur=0.3),
          dict(d='M 1050 590 m -16 0 a 16 16 0 1 0 32 0 a 16 16 0 1 0 -32 0', at=88.88, color='red', width=8, dur=0.3),
          dict(d='M 300 380 H 1020 M 990 350 L 1025 380 L 990 410', at=S('gases', 90.78) - 0.2, color='red', width=10, dur=0.7)],
   labels=[dict(text='Hot gas > 5,000°F', x=320, y=300, at=S('five', 91.78) - 0.2, color='red', size=56),
           dict(text='COLD = STIFF', x=330, y=520, at=S('stiff', 95.82) - 0.2, color='yellow', size=72),
           dict(text='STIFF = NO SEAL', x=330, y=640, at=S('cannot', 97.64) - 0.2, color='red', size=72)])
# ================= THE WARNING =================
sh(99.76, 'section', no='02', name=['The', 'Warning'], sub='Morton Thiokol · the booster maker',
   img='51l-s-154.jpg', cap='The boosters Thiokol built', pos='50% 40%')
sh(105.36, 'doc', header='POST-FLIGHT INSPECTIONS · 1985', body='On earlier flights, hot gas had [[scorched and eroded]] the O-ring seals.',
   hlAt=S('scorched', 106.68) - 0.2, fs=46)
sh(110.24, 'doc', header='MEMO · ROGER BOISJOLY, MORTON THIOKOL · JULY 31, 1985',
   body='"The result would be a [[catastrophe of the highest order]] — loss of human life."', hlAt=S('catastrophe', 114.52) - 0.2, fs=46)
sh(119.18, 'saiddid', lk='THIOKOL ENGINEERS', said=['No launch', 'below 53°F'], saidAt=[S('recommended', 123.82), S('fifty-three', 125.82)],
   rk='NASA MANAGERS', did=['Pushed', 'back.'], didAt=S('pushed', 128.2) - 0.2, sfs=110, dfs=110)
sh(130.14, 'head', lines=['"When do you want me', 'to launch — next April?"'], accent=1, acol='red', fs=110,
   at=[144.4, S('next', 132.76) - 0.2], sub='— a NASA manager, as reported to the commission', subAt=S('April', 133.26))
sh(134.46, 'head', lines=['Thiokol managers', 'went offline.'], accent=1, acol='yellow', fs=130, at=[134.5, 135.1])
sh(136.98, 'head', lines=['"Take off your', 'engineering hat."'], accent=1, acol='yellow', fs=130,
   at=[S('take', 138.52) - 0.2, S('engineering', 141.02) - 0.2], sub='…and put on your management hat.', subAt=S('management', 140.52) - 0.3)
sh(143.6, 'head', lines=['LAUNCH', 'APPROVED.'], accent=1, acol='red', fs=200, at=[157.9, S('approved', 144.74) - 0.2])
sh(147.48, 'head', lines=['One engineer', 'refused to sign.'], accent=1, acol='yellow', fs=130, at=[147.53, 148.18],
   sub='Allan McDonald, Morton Thiokol', subAt=148.38)
# ================= 73 SECONDS =================
F(150.3, 'K_51l-s-029_out', 0.0, 'NASA: STS-51L crew at pre-launch breakfast, Jan 28, 1986')
F(154.8, 'C_in', 0.3)                                   # Challenger on the pad, countdown audio
F(160.2, 'C_in', 9.85)                                  # ignition close-up (synced to the countdown audio)
F(167.7, 'C_out', 21.0)                                # liftoff
sh(169.38, 'box', src='NASA photo 51L-10096: first evidence of black smoke, right booster',
   boxes=[I('51l-10096.jpg', A169, cap='Launch pad camera · fractions of a second after ignition', push=0.09, origin='58% 78%')],
   notes=[N('BLACK SMOKE', NX, 330, S('black', 173.16) - 0.4, 'red', size=72, arrow=[[1240, 400], [800, 690]]),
          N('from the right booster joint', NX, 440, S('right', 175.16) - 0.2, 'white', size=46),
          N('< 1 second after ignition', NX, 540, S('second', 172.16) - 0.2, 'yellow', size=46)])
sh(177.96, 'blueprint', kind='structure', title='The joint fails to seal',
   paths=[dict(d='M 800 300 H 980 V 760 H 800 Z M 1300 300 H 1120 V 760 H 1300 Z', at=178.0, dur=0.6),
          dict(d='M 1050 300 V 760', at=178.0, color='yellow', width=8),
          dict(d='M 300 380 H 1040 V 820 H 1500', at=178.3, color='red', width=10, dur=1.2),
          dict(d='M 1030 520 h 40 v 60 h -40 Z', at=S('aluminum', 181.24) - 0.2, color='yellow', width=10, dur=0.6)],
   labels=[dict(text='BLOW-BY', x=320, y=300, at=178.4, color='red', size=72),
           dict(text='burned aluminum plugs the gap', x=1110, y=600, at=S('aluminum', 181.24), color='yellow', size=44),
           dict(text='…for now', x=1110, y=680, at=S('temporary', 184.24) - 0.2, color='white', size=44)])
F(185.98, 'C_in', 40.0)                               # climbing on
F(194.66, 'C_in', 55.0)
sh(197.76, 'blueprint', kind='structure', title='At 58 seconds: a flame from the right booster',
   paths=[dict(d='M 860 160 Q 960 90 1060 160 V 860 H 860 Z', at=197.84, dur=0.9, color='yellow'),
          dict(d='M 700 260 L 740 200 L 780 260 V 860 H 700 Z M 1140 260 L 1180 200 L 1220 260 V 860 H 1140 Z', at=198.04, dur=0.9),
          dict(d='M 1140 640 Q 1060 660 1030 700 M 1140 660 Q 1080 700 1050 760', at=S('blowtorch', 200.34) - 0.3, color='red', width=12, dur=0.6)],
   labels=[dict(text='External tank', x=960, y=460, at=198.24, color='yellow', size=46, align='center'),
           dict(text='liquid hydrogen + oxygen', x=960, y=520, at=198.54, color='white', size=34, align='center'),
           dict(text='Right booster', x=1240, y=300, at=198.74, color='white', size=40),
           dict(text='FLAME', x=1240, y=640, at=S('blowtorch', 200.34), color='red', size=70)])
F(204.71, 'C_in', 60.6)                               # "go at throttle up"
F(210.34, 'C_out', 66.0)
F(S('Seventy-three', 212.34), 'C_out', 88.8)             # breakup
F(219.97, 'C_in', 111.5)
F(224.31, 'C_in', 132.0)                              # debris trails
F(231.72, 'K_S85-44253_in', 0.0, 'NASA official STS-51L crew portrait')
# ================= THE INVESTIGATION =================
sh(235.78, 'section', no='03', name=['The', 'Investigation'], sub='Presidential Commission · 1986',
   img='S86-28889.jpg', cap='Commission members at Kennedy, Feb 1986')
sh(238.66, 'head', lines=['Richard Feynman'], accent=0, acol='yellow', fs=150, at=[238.74], sub='Nobel Prize-winning physicist', subAt=239.44)
sh(243.14, 'blueprint', kind='structure', title="Feynman's ice-water test (illustration)",
   paths=[dict(d='M 760 360 V 820 H 1160 V 360', at=243.24, dur=0.8),
          dict(d='M 760 470 Q 860 450 960 470 T 1160 470', at=S('ice', 247.44) - 0.4, width=4),
          dict(d='M 820 560 h 60 v 60 h -60 Z M 1060 520 h 60 v 60 h -60 Z M 900 700 h 60 v 60 h -60 Z', at=S('ice', 247.44) - 0.2, width=4, dur=0.5),
          dict(d='M 940 300 V 640 H 1000 V 300 M 900 300 H 1040', at=S('clamp', 245.44) - 0.3, color='yellow', width=8),
          dict(d='M 955 640 h 30 v 30 h -30 Z', at=S('rubber', 244.44) - 0.2, color='red', width=10, dur=0.4)],
   labels=[dict(text='O-ring rubber', x=1200, y=640, at=S('rubber', 244.44), color='red', size=46),
           dict(text='C-clamp', x=1200, y=330, at=S('clamp', 245.44), color='yellow', size=46),
           dict(text='ice water · 32°F', x=1200, y=480, at=S('ice', 247.44), color='white', size=46),
           dict(text='It did not spring back.', x=960, y=880, at=S('spring', 250.94) - 0.3, color='red', size=56, align='center')])
sh(253.3, 'head', lines=['Cold rubber', 'cannot seal.'], accent=1, acol='red', fs=170, at=[253.35, 254.2])
sh(256.16, 'doc', header='REPORT OF THE PRESIDENTIAL COMMISSION · JUNE 6, 1986',
   body='Cause: failure of the O-ring pressure seal in the right solid rocket booster. [[The decision to launch the Challenger was flawed.]]',
   hlAt=S('decision', 262.8) - 0.2, fs=42)
sh(264.84, 'box', src='NASA photo S86-28889: commission members inspect hardware at Kennedy',
   boxes=[I('S86-28889.jpg', A169, cap='Rogers Commission at Kennedy Space Center', push=0.06)],
   notes=[N('Warnings existed for months', NX, 300, 263.6, 'yellow', size=50),
          N('…but never reached the people who made the call', NX, 420, S('never', 266.86) - 0.2, 'red', size=44, w=560)])
sh(270.58, 'timeline', events=[dict(date='1986', label='Challenger lost', at=270.72, accent=True),
                                dict(date='1988', label='Return to flight', at=S('grounded', 271.62) + 0.4)],
   gap=dict(**{'from': 0, 'to': 1}, label='32 months grounded', at=S('three', 272.62) - 0.2))
sh(273.8, 'list', items=[dict(text='+ Third O-ring', at=S('third', 275.4) - 0.2),
                         dict(text='+ Joint heaters', at=S('heaters', 277.4) - 0.2),
                         dict(text='+ Independent safety office', at=S('safety', 280.4) - 0.2, accent=True)], fs=110)
F(282.7, 'K_s26-s-030_up', 0.0, 'NASA photo: Discovery returns to flight, STS-26, Sep 29, 1988')
sh(287.9, 'doc', header="R. P. FEYNMAN · APPENDIX F, ROGERS COMMISSION REPORT · 1986",
   body='"For a successful technology, reality must take precedence over public relations, for [[nature cannot be fooled.]]"',
   hlAt=S('nature', 296.4) - 0.2, fs=46)
# ================= CLOSING =================
sh(300.18, 'counter', steps=[dict(value=73, label='seconds', at=300.26, dur=0.8),
                             dict(value=7, label='lives', at=S('Seven', 300.86) - 0.1, dur=0.6, accent=True),
                             dict(value=1, label='warning that should have been heard', at=S('warning', 302.4) - 0.3, dur=0.6, accent=True)],
   fs=300)
F(305.38, 'K_NHQ202501230017_in', 0.0, 'NASA photo: Challenger memorial, Arlington National Cemetery')
sh(313.0, 'title', lines=['Subscribe to', 'Wrecklore'], kicker='True stories of engineering disasters',
   sub='Where were you when Challenger launched?')
END = 332.5

# ---------- music (FreePD.com, CC0 public domain) ----------
music = [dict(file='audio/m_Hidden_Truth.wav', start=0.0, dur=20.4, vol=0.38),
         dict(file='audio/m_Infinite_Wonder.wav', start=19.32, dur=41.6, vol=0.36, ss=20),
         dict(file='audio/m_Driving_Concern.wav', start=59.83, dur=90.8, vol=0.30),
         dict(file='audio/m_Final_Step.wav', start=149.58, dur=round(S('Seventy-three', 200) + 0.9 - 149.58, 2), vol=0.36),
         dict(file='audio/m_Asking_Questions.wav', start=235.16, dur=53.2, vol=0.30),
         dict(file='audio/m_Emotional_Blockbuster_2.wav', start=287.32, dur=END - 287.32, vol=0.40)]
# ---------- sound effects (original, synthesized) ----------
X = lambda f, t, v, **k: dict(file=f'audio/sfx/{f}.wav', t=round(t, 2), vol=v, **k)
sfx = [X('quindar', 154.85, 0.45), X('static', 155.0, 0.10), X('roar', 166.4, 0.85), X('boom', 0.0, 0.55)]
sfx += [X('tick', 0.38 + i, 0.5) for i in range(4)]
sfx += [X('whoosh', 4.08, 0.5), X('hit', 9.63, 0.65), X('whoosh', 10.24, 0.4), X('riser', S('Challenger', 16.32) - 5.6, 0.35),
        X('hit', S('Challenger', 16.32) + 0.4, 0.6), X('whoosh', 20.64, 0.35), X('shutter', 26.8, 0.5), X('shutter', 44.54, 0.5),
        X('whoosh', 59.93, 0.45), X('wind_ice', 60.78, 0.32), X('hit', 68.76, 0.45), X('whoosh', 79.24, 0.4),
        X('hit', S('stiff', 95.82) - 0.2, 0.5), X('whoosh', 99.44, 0.45), X('typewriter', 105.58, 0.35), X('typewriter', 110.52, 0.4)]
beat, tb = 1.05, 119.22
while tb < 149.28:
    sfx.append(X('heartbeat', tb, 0.55)); beat = max(0.62, beat - 0.012); tb += beat
sfx += [X('hit', 143.64, 0.7), X('hit', 147.53, 0.35), X('shutter', 169.48, 0.45), X('whoosh', 177.76, 0.35),
        X('whoosh', 185.64, 0.3), X('flame', 197.6, 0.45), X('riser', S('Seventy-three', 212.34) - 6.0, 0.45),
        X('boom', S('broke', 214.27) - 0.2, 0.9), X('static', 223.57, 0.08), X('quindar', 223.62, 0.35), X('quindar', 231.25, 0.35),
        X('whoosh', 235.96, 0.45), X('typewriter', 256.28, 0.35), X('hit', S('decision', 262.8) - 0.2, 0.5), X('whoosh', 269.66, 0.35),
        X('hit', 275.4, 0.25), X('hit', 277.4, 0.25), X('hit', 280.4, 0.3), X('typewriter', 288.1, 0.3),
        X('hit', 300.21, 0.5), X('hit', S('Seven', 300.86) - 0.1, 0.5), X('hit', S('warning', 302.4) - 0.3, 0.5),
        X('whoosh', 312.7, 0.4), X('hit', 313.03, 0.45)]

finish(cuts=[0, 60.62, 150.3, 235.78, END], names=['hook', 'cold', 'launch', 'aftermath'], tags=[], music=music, sfx=sfx,
       archive=archive, end=END)
