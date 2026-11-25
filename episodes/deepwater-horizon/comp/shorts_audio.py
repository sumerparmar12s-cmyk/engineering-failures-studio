"""Audio for a Short: VO + one CC0 track (ducked) + auto SFX from the Short's timeline + a few story sounds. usage: VW=1080 VH=1920 python3 shorts_audio.py N OUT.wav"""
import sys, os, subprocess, random
sys.argv = [sys.argv[0], sys.argv[1], '/dev/null', sys.argv[2]]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shorts_edit as E
N = int(sys.argv[1]); OUT = sys.argv[3]; A = f'{E.ROOT}/audio'; SD = E.SD
X = lambda f, t, v, **k: dict(file=f'{A}/sfx/{f}.wav', t=round(max(0, t), 3), vol=v, **k)
sfx = [X('boom', 0.0, 0.6), X('braam', 0.02, 0.45)]; r = random.Random(N)
for sh in E.T:
    if sh.trans in ('push', 'zoom'): sfx.append(X('whoosh2', sh.t0 - 0.08, 0.35))
    elif sh.trans == 'glitch': sfx.append(X('glitch', sh.t0, 0.4))
    elif sh.trans == 'flash': sfx.append(X('explosion_big', sh.t0, 0.5))
    for o in sh.ov:
        k = o['k']
        if k == 'punch': sfx.append(X('hit', o['at'], 0.4))
        elif k == 'stat': sfx.append(X('hit', o['at'], 0.4)); sfx.append(X('tick', o['at'] + 0.1, 0.3))
        elif k == 'label': sfx.append(X('pop', o['at'], 0.18))
        elif k == 'type':
            for i, ch in enumerate(o['text']):
                if ch.strip(): sfx.append(X(f'key{r.randint(0, 2)}', o['at'] + i / o['cps'], 0.15))
        elif k == 'well' and o.get('gas'): sfx.append(X('geyser', o['gas'][0], 0.2, dur=2.5))
music = {1: 'Behind_Enemy_Lines', 2: 'Chill_Dark', 3: 'Behind_Enemy_Lines'}[N]
inputs = ['-i', f'{SD}/vo/vo.mp3', '-ss', '8', '-t', str(E.END), '-i', f'{A}/m3/{music}.mp3']
fc = [f"[0:a]apad=whole_dur={E.END},asplit=2[vo][sc]", f"[1:a]aresample=44100,volume=0.07,afade=t=out:st={E.END - 2}:d=2[m]", "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=400[md]"]
sl = []
for i, s in enumerate(sfx):
    inputs += ['-i', s['file']] if not s.get('dur') else ['-t', str(s['dur']), '-i', s['file']]
    fc.append(f"[{i + 2}:a]aresample=44100,volume={s['vol'] * 0.3:.3f},adelay={int(s['t'] * 1000)}|{int(s['t'] * 1000)}[s{i}]"); sl.append(f'[s{i}]')
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
fc.append("[vo][md][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false[a]")
open(f'{SD}/work/fc.txt', 'w').write(';\n'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex_script', f'{SD}/work/fc.txt', '-map', '[a]', '-t', str(E.END), '-ar', '48000', '-ac', '2', OUT], check=True)
print('wrote', OUT, len(sfx), 'sfx')
