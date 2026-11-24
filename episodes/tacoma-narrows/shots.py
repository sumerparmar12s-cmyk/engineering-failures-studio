#!/usr/bin/env python3
"""Shot list: Galloping Gertie (Tacoma Narrows Bridge, 1940). ~2:10. Times are absolute VO seconds."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / '.claude/skills/engineering-failures-video/scripts'))
from vidlib import finish, init, sh, w

init(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent))

# --- camera moves on the archive film (applied before the full-frame cover crop) ---
BASE = "scale=1920:1440,setsar=1,"
LOOK = "vignette=angle=PI/4.2,noise=alls=7:allf=t,"
MOVES = {
    'in':   "zoompan=z='min(1.22,1.02+0.0011*on)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1440x1080:fps=30000/1001,",
    'out':  "zoompan=z='max(1.02,1.20-0.0010*on)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1440x1080:fps=30000/1001,",
    'panr': "zoompan=z=1.16:x='(iw-iw/zoom)*min(1,on/220)':y='ih/2-ih/zoom/2':d=1:s=1440x1080:fps=30000/1001,",
    'panl': "zoompan=z=1.16:x='(iw-iw/zoom)*(1-min(1,on/220))':y='ih/2-ih/zoom/2':d=1:s=1440x1080:fps=30000/1001,",
    'up':   "zoompan=z=1.16:x='iw/2-iw/zoom/2':y='(ih-ih/zoom)*(1-min(1,on/220))':d=1:s=1440x1080:fps=30000/1001,",
}
FILES = {'P': 'real/prelinger.mp4', 'C': 'real/cep176.mpg'}
archive = {f'{s}_{m}': {'file': f, 'crop': BASE + mv + LOOK} for s, f in FILES.items() for m, mv in MOVES.items()}
SRC_P = 'Prelinger Archives, 1940 (public domain)'
SRC_C = 'Tacoma Fire Dept. / Stillman Fires Collection, 1940 (public domain)'

def F(t0, key, ss):
    sh(t0, 'full', clip=dict(src=key, ss=ss), src=SRC_P if key[0] == 'P' else SRC_C)

# ---------------- COLD OPEN ----------------
sh(0, 'title', lines=['Galloping', 'Gertie'], kicker='Tacoma Narrows Bridge · November 7, 1940',
   sub='the bridge that tore itself apart')
F(w('a', 6), 'C_in', 54.2)                       # deck twisting, side view
F(w('Within', 11), 'P_out', 205.6)               # the fall (glimpse)
# ---------------- THE BRIDGE ----------------
F(w('The', 13.5), 'P_panr', 12.2)               # cable spinning, construction
F(w('opened', 15), 'P_in', 63.0)                 # opening-day crowds
sh(w('Its', 17), 'blueprint', kind='structure', title='Tacoma Narrows Bridge · elevation (simplified)',
   paths=[
       dict(d='M 160 640 H 1760', at=17.6, dur=1.0),                                         # deck
       dict(d='M 520 790 V 300 M 1400 790 V 300', at=17.9, color='yellow'),                  # towers
       dict(d='M 160 600 Q 340 560 520 300 Q 960 700 1400 300 Q 1580 560 1760 600', at=18.3, dur=1.2),  # cables
       dict(d='M 300 760 H 1620', at=17.6, width=2),                                         # water
       dict(d='M 520 870 H 1400 M 520 850 V 890 M 1400 850 V 890', at=w('2', 18), color='red'),
   ],
   labels=[dict(text='2,800 ft main span', x=960, y=880, at=w('2', 18) + 0.2, color='red', align='center', size=50),
           dict(text='3rd longest in the world', x=960, y=420, at=w('third', 22) - 0.2, color='yellow', align='center', size=48)])
F(w('And', 25), 'P_in', 79.4)                    # on the deck, towers ahead
sh(w('a', 28), 'blueprint', kind='structure', title='Deck cross-section (simplified, not to scale)',
   paths=[
       dict(d='M 560 470 H 1360', at=28.4, dur=0.8, width=7),                                 # roadway
       dict(d='M 560 470 V 560 M 1360 470 V 560', at=w('stiffened', 30) - 0.2, color='yellow', width=9),  # girders
       dict(d='M 560 390 H 1360 M 560 370 V 410 M 1360 370 V 410', at=w('39', 28) - 0.2, color='red'),
       dict(d='M 1440 470 V 560 M 1420 470 H 1460 M 1420 560 H 1460', at=w('eight', 32) - 0.2, color='red'),
   ],
   labels=[dict(text='39 ft wide', x=960, y=300, at=w('39', 28), color='red', align='center', size=54),
           dict(text='8 ft girders', x=1480, y=490, at=w('eight', 32), color='red', size=50),
           dict(text='span ÷ width ≈ 72 : 1', x=960, y=660, at=w('deep', 33) + 0.2, color='yellow', align='center', size=46)])
F(w('That', 34), 'P_panl', 83.8)                 # side view of the span
F(w('Even', 36.5), 'P_in', 96.5)                 # deck rolling
F(w('Drivers', 42), 'C_up', 13.0)                # approaching along the deck
sh(w('Locals', 45.5), 'head', lines=['“Galloping', 'Gertie”'], accent=1, acol='yellow', fs=170,
   at=[w('Galloping', 47) - 0.3, w('Galloping', 47) + 0.15], sub='what locals called the bridge', subAt=w('Locals', 45.5) + 0.3)
# ---------------- THE STORM ----------------
F(w('Then', 49), 'P_out', 135.4)                 # Nov 7: side view, onlookers
sh(w('That', 51), 'counter', steps=[dict(value=42, label='sustained wind, November 7, 1940', at=w('42', 53) - 0.4, accent=True)],
   suffix=' mph', more='about', fs=280)
F(w('Shortly', 57.5), 'C_in', 0.6)              # first twisting, side view
F(w('stopped', 61) - 0.55, 'P_in', 159.2)                   # from the tower: deck twisting hard
sh(w('One', 64), 'blueprint', kind='structure', title='Torsion: the deck twists about its centre line',
   paths=[
       dict(d='M 560 520 H 1360', at=64.7, width=3),
       dict(d='M 580 370 L 1340 670', at=w('climbed', 65) - 0.1, color='red', width=9, dur=0.5),
       dict(d='M 580 670 L 1340 370', at=w('plunged', 66) - 0.1, color='yellow', width=9, dur=0.5),
       dict(d='M 1180 520 A 220 220 0 0 1 1160 450', at=w('tilting', 67) - 0.1, color='red'),
   ],
   labels=[dict(text='sidewalk up', x=440, y=320, at=w('climbed', 65), color='red', size=46),
           dict(text='sidewalk down', x=440, y=690, at=w('plunged', 66), color='yellow', size=46),
           dict(text='≈ 28° each way', x=1250, y=410, at=w('30', 68) - 0.2, color='red', size=56)])
F(w('Newspaper', 71), 'C_in', 72.4)              # stranded car on the deck
F(w('He', 75), 'P_panr', 151.0)                  # people walking off the approach
F(w('forced', 78.5), 'C_in', 87.6)               # man on the deck near the abandoned car
F(w('Each', 84), 'C_out', 63.2)                  # tower view: violent twist
sh(w("bridge's", 89) - 0.2, 'blueprint', kind='chain', title='Aeroelastic flutter: a feedback loop',
   nodes=[dict(label='Deck twists', detail='angle changes', at=w('motion', 90) - 0.3),
          dict(label='Airflow shifts', detail='vortices on the deck', at=w('shaping', 90.5) - 0.1),
          dict(label='More energy in', detail='every cycle grows', at=w('pumping', 92) - 0.2, accent=True)])
sh(w('Engineers', 95), 'head', lines=['Aeroelastic', 'flutter'], accent=1, acol='red', fs=160,
   at=[w('aero', 96.5) - 0.3, w('flutter', 97) - 0.2], sub='self-excited torsional oscillation', subAt=w('flutter', 97) + 0.4)
# ---------------- THE FALL ----------------
F(w('Just', 98.5), 'P_in', 196.0)                # the tower, deck sagging
F(w('center', 101) - 0.5, 'P_out', 204.9)                 # the centre span falls into the Narrows
F(w('No', 105), 'C_in', 112.2)                   # second angle of the fall
F(w('Tubby', 107.5), 'P_panr', 220.8)            # empty water, broken span
# ---------------- AFTERMATH ----------------
F(w('The', 109.8), 'P_in', 229.1)                # hanging wreckage
sh(w('Today', 113.5), 'timeline', events=[dict(date='1940', label='Gertie falls', at=w('Today', 113.5) + 0.2, accent=True),
                                          dict(date='1950', label='stiffer bridge opens', at=w('every', 114) + 0.1)],
   gap=dict(**{'from': 0, 'to': 1}, label='wind-tunnel testing', at=w('wind', 116)))
F(w('and', 118.5), 'P_out', 233.2)               # the broken span from afar
F(w('Puget', 121.5), 'P_in', 225.1)
sh(125.6, 'title', lines=['A lesson', 'written in steel'], kicker='Tacoma Narrows Bridge · 1940',
   sub='the wreck still lies beneath Puget Sound')
END = 131.0

music = [dict(file='audio/score.wav', start=0, dur=END, vol=0.42)]
sfx = [dict(file='audio/whoosh.wav', t=0.0, vol=0.25),
       dict(file='audio/wind_soft.wav', t=0.0, vol=0.18),
       dict(file='audio/hit.wav', t=w('Within', 11) - 0.05, vol=0.5),
       dict(file='audio/wind.wav', t=48.6, vol=0.22),
       dict(file='audio/groan1.wav', t=w('twist', 62) - 0.4, vol=0.3),
       dict(file='audio/groan2.wav', t=w('plunged', 66) - 0.5, vol=0.3),
       dict(file='audio/groan1.wav', t=w('Each', 84) - 0.2, vol=0.28),
       dict(file='audio/groan2.wav', t=w('gave', 99.5) - 0.6, vol=0.38),
       dict(file='audio/impact.wav', t=w('tore', 102) - 0.25, vol=0.75),
       dict(file='audio/whoosh.wav', t=125.2, vol=0.2),
       dict(file='audio/hit.wav', t=125.6, vol=0.35)]

finish(cuts=[0, w('Then', 49), w('Just', 98.5), END], names=['bridge', 'storm', 'fall'], tags=[], music=music, sfx=sfx,
       archive=archive, end=END,
       caption_fixes={'Girdy.': 'Gertie.', 'Girdy': 'Gertie', 'narrows': 'Narrows', 'narrows.': 'Narrows.', 'aero-elastic': 'aeroelastic'})
