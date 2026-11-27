"""Audio for a Titan Short: VO + one CC0 track (ducked) + auto SFX + story sounds. usage: VW=1080 VH=1920 python3 shorts_audio.py N OUT.wav"""
import sys, os, subprocess, random
sys.argv = [sys.argv[0], sys.argv[1], '/dev/null', sys.argv[2]]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shorts_edit as E
N = int(sys.argv[1]); OUT = sys.argv[3]; A = f'{E.ROOT}/audio'; SD = E.SD
X = lambda f, t, v, **k: dict(file=f'{A}/sfx/{f}.wav', t=round(max(0, t), 3), vol=v, **k)
sfx = [X('sonar_ping', 0.0, 0.7), X('underwater_bed', 0.0, 0.35, dur=E.END)]; r = random.Random(N)
for sh in E.T:
    if sh.trans in ('push', 'zoom'): sfx.append(X('whoosh2', sh.t0 - 0.08, 0.35))
    elif sh.trans == 'glitch': sfx.append(X('glitch', sh.t0, 0.4))
    elif sh.trans == 'flash': sfx.append(X('hit', sh.t0, 0.5))
    elif sh.trans == 'ping': sfx.append(X('sonar_ping', sh.t0, 0.5))
    elif sh.trans == 'sink': sfx.append(X('pressure_rumble', sh.t0, 0.4, dur=3.0))
    if sh.grade == 'paper': sfx.append(X('paper', sh.t0, 0.3))
    for o in sh.ov:
        k = o['k']
        if k == 'stamp': sfx.append(X('stamp', o['at'], 0.55))
        elif k == 'stat': sfx.append(X('hit', o['at'], 0.4)); sfx.append(X('tick', o['at'] + 0.1, 0.3))
        elif k == 'label': sfx.append(X('pop', o['at'], 0.18))
        elif k == 'chat':
            for (at, who, text, st) in o['msgs']:
                sfx.append(X('modem_blip', at - 0.05, 0.5))
                for i, ch in enumerate(text):
                    if ch != ' ': sfx.append(X(f'key{r.randint(0, 2)}', at + i * max(0.3, len(text) / 26) / len(text), 0.12))
REAL = []
if N == 2: sfx += [X('boom', 0.1, 0.6), X('boom', 16.1, 0.5), X('creak', 17.0, 0.4), X('wind_bed', 44.0, 0.5, dur=12.0), X('thud', 59.5, 0.5), X('clank', 60.5, 0.5), X('thud', 61.5, 0.5)]
if N == 3: sfx += [X('sub_drop', 38.2, 0.9), X('heartbeat', 35.0, 0.4), X('heartbeat', 36.0, 0.45), X('heartbeat', 37.0, 0.5)]; REAL = [(f'{E.ROOT}/real/DOD_110804017.mp4', 38.2, 9.6, 4.0, 2.2)]
if N == 1: sfx += [X('typewriter', 21.2, 0.3), X('thud', 35.0, 0.5), X('thud', 5.3, 0.4)]
music = {1: 'Hidden_Danger_B', 2: 'Tension', 3: 'Ambient_K_Slow_Go'}[N]
inputs = ['-i', f'{SD}/vo/vo.mp3', '-t', str(E.END), '-i', f'{A}/m4/{music}.mp3']
fc = [f"[0:a]apad=whole_dur={E.END},asplit=2[vo][sc]", f"[1:a]aresample=44100,volume=0.09,afade=t=out:st={E.END - 2}:d=2[m]", "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=400[md]"]
sl = []; n = 2
for s in sfx:
    inputs += ['-i', s['file']] if not s.get('dur') else ['-t', str(s['dur']), '-i', s['file']]
    fc.append(f"[{n}:a]aresample=44100,volume={s['vol'] * 0.3:.3f},adelay={int(s['t'] * 1000)}|{int(s['t'] * 1000)}[s{n}]"); sl.append(f'[s{n}]'); n += 1
for (f, t, ss, du, v) in REAL:
    inputs += ['-ss', str(ss), '-t', str(du), '-i', f]
    fc.append(f"[{n}:a]aresample=44100,volume={v:.3f},adelay={int(t * 1000)}|{int(t * 1000)}[s{n}]"); sl.append(f'[s{n}]'); n += 1
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
fc.append("[vo][md][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false[a]")
os.makedirs(f'{SD}/work', exist_ok=True); open(f'{SD}/work/fc.txt', 'w').write(';\n'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex_script', f'{SD}/work/fc.txt', '-map', '[a]', '-t', str(E.END), '-ar', '48000', '-ac', '2', OUT], check=True)
print('wrote', OUT, len(sfx), 'sfx')
