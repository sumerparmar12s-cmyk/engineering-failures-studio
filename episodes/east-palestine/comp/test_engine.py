import sys, time; sys.path.insert(0, '.')
from engine import *
S = [Shot(0, ('img', 'media/ntsb_aerial_pile.png'), mode='upscale', kb=((0.3, 0.5, 1.0), (0.32, 0.5, 1.25)), src_tag='NTSB photo',
          ov=[O.type('EAST PALESTINE, OHIO\nFEB. 3, 2023 · 8:54 P.M.', 0.2), O.circle((500, 300, 900, 650), 0.8)]),
     Shot(2.0, ('route', 'media/ntsb_hbd_map.png'), trans='whip', rev=(2.2, 4.8), follow=True, kb=((0.5, 0.5, 1.6), (0.5, 0.5, 1.8)),
          ov=[O.punch('+253°F', 3.2, color=(255, 60, 40))]),
     Shot(5.0, ('vid', 'real3d/T4.mp4'), ss=2.0, trans='glitch', grade='night', src_tag='3D reconstruction', ov=[O.counter(5.2, 0, 38, 1.0, 'cars derailed')])]
t = time.time(); render(S, 7.0, '/tmp/claude-0/-home-user-engineering-failures-studio/8f0372dc-b71e-5e2c-bad3-2a780bf4125c/scratchpad/etest.mp4'); print('secs', round(time.time() - t, 1), 'for 210 frames')
