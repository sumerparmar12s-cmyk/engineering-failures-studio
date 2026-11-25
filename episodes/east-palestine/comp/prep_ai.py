"""AI clip frames (512x288, 16 @ 8fps) -> 1920x1080 30fps slow-motion clip with motion interpolation. usage: prep_ai.py [names...]"""
import os, sys, subprocess, glob
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
names = sys.argv[1:] or sorted(os.path.basename(d) for d in glob.glob(f'{R}/ai/video/*') if os.path.exists(f'{d}/015.png'))
for n in names:
    out = f'{R}/comp/cache/{n}.mp4'
    if os.path.exists(out): continue
    # ping-pong (forward + reverse) doubles usable length without a jump; slow x2.5 with motion-compensated interpolation
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '8', '-i', f'{R}/ai/video/{n}/%03d.png', '-filter_complex',
                    '[0]split[a][b];[b]reverse,trim=start_frame=1[r];[a][r]concat=n=2:v=1,setpts=2.5*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,'
                    'scale=1920:1080:flags=lanczos,unsharp=5:5:0.8,eq=contrast=1.04', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', out], check=True)
    print('prepped', n, flush=True)
