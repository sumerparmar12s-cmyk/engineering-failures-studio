#!/usr/bin/env python3
"""Turn NASA stills into 1920x1080 Ken Burns clips (slow push / pull / pan) in real/kb_<id>_<move>.mp4."""
import os, subprocess, sys
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
D, FPS = 12, 30; N = D * FPS
Z = {'in': ("'1+0.12*on/%d'" % N, "'iw/2-iw/zoom/2'", "'ih/2-ih/zoom/2'"),
     'out': ("'1.12-0.12*on/%d'" % N, "'iw/2-iw/zoom/2'", "'ih/2-ih/zoom/2'"),
     'panr': ("1.12", "'(iw-iw/zoom)*on/%d'" % N, "'ih/2-ih/zoom/2'"),
     'up': ("1.12", "'iw/2-iw/zoom/2'", "'(ih-ih/zoom)*(1-on/%d)'" % N)}
JOBS = [('51L-S-002', 'in'), ('51l-s-029', 'out'), ('S85-40074', 'in'), ('S85-44253', 'in'), ('NHQ202501230017', 'in'),
        ('s26-s-030', 'up'), ('51l-s-156', 'in'), ('51l-s-155', 'panr'), ('S85-41239', 'up')]
for img, mv in JOBS:
    out = f'{P}/real/kb_{img}_{mv}.mp4'
    if os.path.isfile(out): continue
    z, x, y = Z[mv]
    vf = (f"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
          f"zoompan=z={z}:x={x}:y={y}:d=1:s=1920x1080:fps={FPS},eq=saturation=1.35:contrast=1.05,format=yuv420p")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', str(FPS), '-t', str(D), '-i', f'{P}/media/{img}.jpg',
                    '-vf', vf, '-frames:v', str(N), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '17', out], check=True)
    print('kb', img, mv, flush=True)
