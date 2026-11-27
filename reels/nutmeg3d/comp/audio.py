import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 72.46
ev = [('pop', 2.5, 0.4), ('whoosh2', 5.12, 0.4), ('pop', 5.52, 0.4), ('hit', 7.08, 0.35), ('pop', 9.12, 0.4), ('ding', 9.56, 0.3), ('rewind', 10.7, 0.5), ('whoosh', 11.76, 0.4), ('pop', 15.68, 0.35), ('whoosh2', 17.78, 0.4), ('pop', 19.36, 0.3), ('whoosh', 21.44, 0.35), ('ding', 23.48, 0.35), ('pop', 26.5, 0.35), ('ding', 28.96, 0.35), ('pop', 29.68, 0.4), ('whoosh2', 32.14, 0.4), ('ding', 35.58, 0.3), ('thud', 36.66, 0.35), ('horn', 39.16, 0.3), ('pop', 41.52, 0.4), ('pop', 42.38, 0.3), ('thud', 43.64, 0.35), ('ding', 43.9, 0.3), ('whoosh', 45.46, 0.3), ('ding', 46.22, 0.4), ('pop', 47.38, 0.35), ('pop', 48.3, 0.35), ('whoosh2', 49.4, 0.4), ('paper', 50.44, 0.5), ('pop', 51.54, 0.3), ('pop', 53.76, 0.4), ('pop', 55.14, 0.4), ('pop', 56.54, 0.4), ('pop', 58.46, 0.4), ('rewind', 60.76, 0.3), ('pop', 62.2, 0.3), ('whoosh', 64.16, 0.35), ('ding', 65.9, 0.4), ('pop', 67.58, 0.4), ('hit', 70.24, 0.35)]
trim = {}
inp = ['-i', R + '/vo/vo.mp3', '-ss', '0', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]", f"[1:a]aresample=44100,volume=0.30,afade=t=in:d=0.3,afade=t=out:st={END-1.6}:d=1.6[m]",
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
