import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 21.1
ev = [('whoosh2', 0.0, 0.3), ('pop', 1.1, 0.35), ('pop', 3.7, 0.4), ('pop', 3.92, 0.4), ('pop', 5.34, 0.4), ('ding', 6.64, 0.35), ('pop', 8.04, 0.4), ('ding', 9.42, 0.35), ('whoosh', 11.08, 0.4), ('swell', 10.72, 0.25), ('pop', 12.8, 0.35), ('whoosh2', 13.76, 0.35), ('pop', 14.3, 0.4), ('pop', 15.6, 0.4), ('pop', 17.1, 0.4), ('pop', 17.68, 0.4), ('ding', 19.62, 0.45)]
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
