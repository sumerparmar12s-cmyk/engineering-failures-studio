import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 24.2
SND = [('s_bloop', 3.44), ('s_upsweep', 15.25), ('s_mars', 21.84)]
SOLO = [(3.34, 5.3), (15.15, 17.2), (21.74, 24.2)]          # music fully ducked while the real recordings play
ev = [('braam', 0.0, .4), ('sonar_ping', 0.05, .35), ('riser', 2.2, .3), ('whoosh', 5.0, .3), ('sub_drop', 7.9, .45), ('whoosh2', 8.85, .4),
      ('crunch', 10.8, .4), ('hit', 12.16, .35), ('riser', 14.0, .25), ('stamp', 17.6, .55), ('whoosh', 19.6, .35), ('wind_bed', 19.7, .25)]
trim = {('wind_bed', 19.7): 2.0}
inp = ['-i', R + '/vo/vo.mp3', '-ss', '0', '-t', str(END), '-i', R + '/audio/music.mp3']
vol = '*'.join(f"(1-0.97*between(t,{a},{b}))" for a, b in SOLO)
fc = [f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]", f"[1:a]aresample=44100,volume=0.22,volume='{vol}':eval=frame,afade=t=in:d=0.2,afade=t=out:st={END-1.4}:d=1.4[m]",
      "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
sl = []; n = 2
for nm, t in SND:
    inp += ['-i', f'{R}/audio/{nm}.wav']; fc.append(f"[{n}:a]aresample=44100,aformat=channel_layouts=stereo,adelay={int(t*1000)}|{int(t*1000)}[r{n}]"); sl.append(f'[r{n}]'); n += 1
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[rec]")
el = []
for i, (nm, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{nm}.wav']; tr = trim.get((nm, t)); cut = f"atrim=0:{tr},afade=t=out:st={tr-0.5}:d=0.5," if tr else ''
    fc.append(f"[{n}:a]aresample=44100,{cut}volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); el.append(f'[s{i}]'); n += 1
fc.append(''.join(el) + f"amix=inputs={len(el)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]")
fc.append("[vo][rec][md][sfxd]amix=inputs=4:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
# envelope for the on-screen waveform (30 fps)
import numpy as np, soundfile as sf, json
a, sr = sf.read(R + '/work/audio.wav'); a = a.mean(1); hop = sr // 30
env = [float(np.sqrt((a[i:i + hop] ** 2).mean())) for i in range(0, len(a), hop)]
seg = [list(map(float, np.abs(a[i:i + hop:max(1, hop // 64)])[:64])) for i in range(0, len(a), hop)]
json.dump({'env': env, 'seg': seg}, open(R + '/work/env.json', 'w'))
print('audio ok')
