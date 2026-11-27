import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 61.74
ev = [('whoosh', 3.47, 0.4), ('whoosh2', 7.19, 0.4), ('whoosh', 9.91, 0.4), ('whoosh2', 14.38, 0.4), ('whoosh', 17.81, 0.4), ('whoosh2', 19.55, 0.4), ('whoosh', 23.71, 0.4), ('whoosh2', 27.54, 0.4), ('whoosh', 31.33, 0.4), ('whoosh2', 34.85, 0.4), ('whoosh', 38.03, 0.4), ('whoosh2', 41.28, 0.4), ('whoosh', 51.78, 0.4), ('whoosh2', 54.75, 0.4), ('whoosh', 57.45, 0.4), ('pop', 3.92, 0.4), ('hit', 5.22, 0.35), ('pop', 7.44, 0.35), ('rewind', 8.98, 0.5), ('pop', 12.7, 0.35), ('ding', 19.9, 0.3), ('pop', 22.64, 0.35), ('ding', 24.76, 0.35), ('pop', 25.44, 0.35), ('ding', 30.34, 0.3), ('horn', 32.78, 0.3), ('pop', 35.0, 0.4), ('thud', 36.48, 0.4), ('ding', 38.84, 0.4), ('pop', 39.68, 0.35), ('pop', 40.48, 0.35), ('paper', 42.72, 0.5), ('pop', 45.7, 0.4), ('pop', 46.92, 0.4), ('pop', 48.22, 0.4), ('pop', 49.96, 0.4), ('pop', 53.42, 0.3), ('ding', 56.22, 0.4), ('pop', 57.6, 0.4), ('hit', 59.62, 0.35)]
trim = {}
inp = ['-i', R + '/vo/vo.mp3', '-ss', '0', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]", f"[1:a]aresample=44100,volume=0.24,afade=t=in:d=0.3,afade=t=out:st={END-1.6}:d=1.6[m]",
      "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
el = []
for i, (nm, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{nm}.wav']; tr = trim.get((nm, t)); cut = f"atrim=0:{tr},afade=t=out:st={tr-0.4}:d=0.4," if tr else ''
    fc.append(f"[{i+2}:a]aresample=44100,{cut}volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); el.append(f'[s{i}]')
fc.append(''.join(el) + f"amix=inputs={len(el)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]")
fc.append("[vo][md][sfxd]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
