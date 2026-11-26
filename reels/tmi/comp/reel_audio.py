"""Reel audio: VO + one CC0 track (ducked) + SFX from the timeline + story sounds. usage: VW=1080 VH=1920 python3 reel_audio.py PART OUT.wav"""
import sys, os, subprocess, random
sys.argv = [sys.argv[0], sys.argv[1], '/dev/null', sys.argv[2]]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel_edit as E
N = int(sys.argv[1]); OUT = sys.argv[3]; A = f'{E.ROOT}/audio'
X = lambda f, t, v, **k: dict(file=f'{A}/sfx/{f}.wav', t=round(max(0, t), 3), vol=v, **k)
sfx = []; r = random.Random(N)
for sh in E.T:
    if sh.trans in ('push', 'zoom'): sfx.append(X('whoosh2', sh.t0 - 0.08, 0.35))
    elif sh.trans == 'glitch': sfx.append(X('glitch', sh.t0, 0.45))
    elif sh.trans == 'flash': sfx.append(X('hit', sh.t0, 0.5))
    for o in sh.ov:
        k = o['k']
        if k == 'stamp': sfx.append(X('stamp', o['at'], 0.6))
        elif k == 'punch': sfx.append(X('hit', o['at'], 0.5)); sfx.append(X('braam', o['at'], 0.35))
        elif k == 'label': sfx.append(X('pop', o['at'], 0.18))
        elif k == 'annun':
            for (txt, on, col) in o['tiles']:
                if on: sfx.append(X('alarm_beep', on, 0.45))
        elif k == 'lamp': sfx.append(X('marker', o['at'] + 0.1, 0.35))
        elif k == 'valve': sfx.append(X('gas_hiss', max(o['at'], o['open_at']), 0.5, dur=min(6.0, sh.t1n - sh.t0 if hasattr(sh, 't1n') else 5.0)))
        elif k == 'level': sfx.append(X('riser', o['at'], 0.3))
        elif k == 'thermo': sfx.append(X('riser', o['at'], 0.45)); sfx.append(X('heartbeat', o['at'] + 0.6, 0.5))
if N == 1:
    sfx += [X('room_bed', 0.0, 0.5, dur=7.6), X('geiger', 0.0, 0.25, dur=6.3), X('klaxon', E.S('lying', 6.4), 0.55, dur=1.8), X('braam', 6.4, 0.4),
            X('wind_bed', 7.7, 0.3, dur=11.0), X('rig_hum', 19.3, 0.35, dur=8.0), X('heartbeat', 44.0, 0.45), X('heartbeat', 45.0, 0.5),
            X('geiger', 53.4, 0.35, dur=5.5), X('sub_drop', 58.9, 0.6), X('pressure_rumble', 58.9, 0.5, dur=3.4), X('geiger', 62.3, 0.4, dur=5.5)]
if N == 2:
    sfx += [X('clock', 0.2, 0.5, dur=6.0), X('room_bed', 0.0, 0.4, dur=9.7), X('klaxon', 6.3, 0.35, dur=1.5), X('geiger', 12.6, 0.25, dur=8.0),
            X('stamp', 31.0, 0.5), X('alarm_beep', 23.4, 0.4), X('heartbeat', 46.8, 0.5), X('rig_hum', 48.0, 0.4, dur=2.6), X('thud', 48.6, 0.4), X('thud', 49.4, 0.4),
            X('geiger', 52.4, 0.35, dur=7.5), X('sub_drop', 60.0, 0.6), X('pressure_rumble', 60.0, 0.5, dur=3.2), X('geiger', 63.3, 0.4, dur=7.0)]
if N == 3:
    sfx += [X('geiger', 0.0, 0.35, dur=9.3), X('room_bed', 0.0, 0.35, dur=11.0), X('braam', 6.3, 0.4), X('wind_bed', 13.9, 0.3, dur=15.0), X('geiger', 19.2, 0.4, dur=10.0),
            X('rig_hum', 29.3, 0.35, dur=11.5), X('sub_drop', 40.8, 0.55), X('pressure_rumble', 42.3, 0.5, dur=8.5), X('boom', 51.0, 0.45), X('clank', 55.0, 0.35), X('geiger', 58.4, 0.35, dur=3.5), X('geiger', 61.9, 0.35, dur=6.3)]
if N == 4:
    sfx += [X('klaxon', 0.5, 0.4, dur=2.0), X('room_bed', 0.0, 0.35, dur=8.2), X('wind_bed', 10.9, 0.3, dur=12.0), X('geiger', 23.0, 0.45, dur=5.2), X('alarm_beep', 31.3, 0.45),
            X('alarm_beep', 35.0, 0.45), X('heartbeat', 40.5, 0.45), X('rig_hum', 41.8, 0.25, dur=7.7), X('braam', 49.6, 0.5), X('tick', 57.2, 0.4), X('tick', 60.3, 0.4),
            X('sub_drop', 65.1, 0.5), X('pressure_rumble', 65.1, 0.45, dur=3.5), X('geiger', 68.7, 0.35, dur=6.0)]
music = {1: 'ElectroShuffle_Dark', 2: 'ElectroShuffle_Dark', 3: 'ElectroShuffle_Dark', 4: 'ElectroShuffle_Dark'}[N]
inputs = ['-i', f'{E.PD}/vo/vo.mp3', '-t', str(E.END), '-ss', str({1: 0, 2: 70, 3: 130, 4: 20}[N]), '-i', f'{A}/m/{music}.mp3']
fc = [f"[0:a]apad=whole_dur={E.END},asplit=2[vo][sc]", f"[1:a]aresample=44100,volume=0.10,afade=t=out:st={E.END - 2}:d=2[m]", "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=400[md]"]
sl = []; n = 2
for s in sfx:
    inputs += ['-i', s['file']] if not s.get('dur') else ['-t', str(s['dur']), '-i', s['file']]
    fc.append(f"[{n}:a]aresample=44100,volume={s['vol'] * 0.32:.3f},adelay={int(s['t'] * 1000)}|{int(s['t'] * 1000)}[s{n}]"); sl.append(f'[s{n}]'); n += 1
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
fc.append("[vo][md][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:level=false[a]")
open(f'{E.PD}/work/fc.txt', 'w').write(';\n'.join(fc))
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex_script', f'{E.PD}/work/fc.txt', '-map', '[a]', '-t', str(E.END), '-ar', '48000', '-ac', '2', OUT], check=True)
print('wrote', OUT, len(sfx), 'sfx')
