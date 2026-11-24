#!/usr/bin/env python3
"""Pre-render each footage overlay with its camera move into real/moves/, then point shots.json at those clips.
Run after shots.py and before assemble.py (keeps assemble's memory use low)."""
import json, os, subprocess, sys
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
D = json.load(open(f'{P}/shots.json', encoding='utf-8'))
os.makedirs(f'{P}/real/moves', exist_ok=True)
arch = D['archive']; new_arch = {}
for i, o in enumerate(D['overlays']):
    a = arch[o['src']]; key = f'mv{i:02d}'; out = f'real/moves/{key}.mp4'
    dur = o['tout'] - o['tin'] + 0.6
    vf = a.get('crop', '') + 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30,format=yuv420p'
    if not os.path.isfile(f'{P}/{out}'):
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f"{o['ss']:.3f}", '-t', f'{dur:.3f}', '-i', f"{P}/{a['file']}",
                        '-vf', vf, '-an', '-t', f'{dur:.3f}', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', f'{P}/{out}'], check=True)
    new_arch[key] = {'file': out, 'crop': ''}
    o['src'] = key; o['ss'] = 0.0
    print(key, 'ok', flush=True)
D['archive'] = new_arch
json.dump(D, open(f'{P}/shots.json', 'w', encoding='utf-8'), indent=1)
