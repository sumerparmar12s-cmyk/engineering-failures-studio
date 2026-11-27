import sys; sys.path.insert(0, '.')
from engine import *
import fx3
ov = lambda **k: k
S = [Shot(0, ('img', 'media/uscg_rig_burning.png'), mode='upscale', kb=((0.5, 0.5, 1.0), (0.5, 0.5, 1.1)), src_tag='U.S. Coast Guard photo',
          ov=[dict(k='callout', pt=(1100, 420), lab=(1400, 300), text='THE DERRICK', sub='20+ stories tall', at=0.3)]),
     Shot(1.5, ('black',), ov=[dict(k='well', at=1.5, disp=(1.6, 2.6), gas=(2.2, 3.0), cement_fail=1.8, labels=[('CEMENT FAILED', 700, 900, 1.9, (255, 80, 60)), ('SEAWATER REPLACES MUD', 1500, 380, 1.7, (90, 170, 255))])]),
     Shot(3.0, ('black',), ov=[dict(k='chart', at=3.0, dur=1.2, box=(500, 300, 1000, 500), vmax=1600, title='DRILL PIPE PRESSURE (PSI)', note='illustrative, based on NTSB/Commission accounts',
            series=[dict(pts=[(0, 0), (0.15, 900), (0.2, 0), (0.4, 1100), (0.45, 0), (0.7, 1300), (1.0, 1400)], color=(255, 140, 40), label='DRILL PIPE 1,400'),
                    dict(pts=[(0.7, 0), (1.0, 0)], color=(64, 214, 214), label='KILL LINE 0')])]),
     Shot(4.4, ('black',), ov=[dict(k='cheese', at=4.4, names=['CEMENT\nFAILED', 'CEMENT CHECK\nSKIPPED', 'PRESSURE TEST\nMISREAD', 'KICK\nMISSED', 'BLOWOUT PREVENTER\nFAILED'], align=4.6, arrow=5.0)]),
     Shot(6.2, ('black',), ov=[dict(k='bigtime', at=6.2, time='9:49 PM', sub='the gas finds a spark')]),
     Shot(7.0, ('black',), ov=[dict(k='names', at=7.0, step=0.05, names=['Jason Anderson', 'Dale Burkeen', 'Donald Clark', 'Stephen Curtis', 'Gordon Jones', 'Roy Wyatt Kemp', 'Karl Kleppinger', 'Blair Manuel', 'Dewey Revette', 'Shane Roshto', 'Adam Weise'])])]
post = fx3.clock_post([(0, '05:45 AM', 5 * 60 + 45), (3.0, '05:00 PM', 17 * 60)], (0, 8))
render(S, 8.0, '/tmp/claude-0/-home-user-engineering-failures-studio/8f0372dc-b71e-5e2c-bad3-2a780bf4125c/scratchpad/t3.mp4', post=post)
