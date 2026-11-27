import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 59.98
ev = [('whoosh2', 0.0, 0.3), ('pop', 0.3, 0.4), ('pop', 1.7, 0.4), ('riser', 2.73, 0.3), ('whoosh', 3.17, 0.45), ('ding', 3.87, 0.3), ('pop', 5.12, 0.4), ('pop', 5.38, 0.35), ('pop', 6.92, 0.3), ('ding', 7.25, 0.3), ('ding', 9.17, 0.3), ('whoosh2', 9.8, 0.3), ('swell', 11.11, 0.2), ('pop', 12.25, 0.35), ('whoosh', 13.35, 0.45), ('thud', 13.82, 0.4), ('pop', 15.82, 0.4), ('pop', 16.58, 0.4), ('whoosh2', 20.5, 0.35), ('ding', 21.68, 0.3), ('pop', 22.14, 0.35), ('pop', 23.5, 0.35), ('pop', 24.14, 0.35), ('pop', 25.14, 0.35), ('rewind', 25.71, 0.35), ('whoosh', 27.54, 0.4), ('snap', 29.31, 0.5), ('metal_tear', 29.37, 0.15), ('ding', 30.95, 0.4), ('whoosh2', 33.64, 0.3), ('pop', 34.84, 0.4), ('pop', 36.43, 0.4), ('hit', 36.62, 0.35), ('pop', 38.04, 0.35), ('whoosh', 39.25, 0.35), ('pop', 40.55, 0.35), ('pop', 42.3, 0.3), ('horn', 44.6, 0.25), ('ding', 44.99, 0.3), ('ding', 46.66, 0.3), ('ding', 47.32, 0.3), ('ding', 48.94, 0.3), ('horn', 50.03, 0.2), ('ding', 51.64, 0.3), ('pop', 52.9, 0.3), ('pop', 53.08, 0.3), ('pop', 53.3, 0.3), ('whoosh2', 54.52, 0.3), ('stamp', 56.88, 0.55), ('whoosh', 57.12, 0.3), ('pop', 57.44, 0.4)]
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
