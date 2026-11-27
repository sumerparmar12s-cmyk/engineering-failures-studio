import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 61.6
ev = [('whoosh2', 0.0, .3), ('pop', 0.3, .4), ('pop', 1.7, .4), ('riser', 2.9, .3), ('whoosh', 3.4, .45), ('ding', 4.2, .3), ('pop', 5.75, .4), ('pop', 6.0, .35),
      ('pop', 7.36, .3), ('ding', 7.9, .3), ('ding', 9.9, .3), ('whoosh2', 10.6, .3), ('swell', 12.0, .2), ('pop', 13.3, .35), ('whoosh', 14.4, .45), ('thud', 14.9, .4),
      ('pop', 16.24, .4), ('pop', 17.56, .4), ('whoosh2', 21.9, .35), ('ding', 23.5, .3), ('pop', 24.1, .35), ('pop', 25.32, .35), ('pop', 25.82, .35), ('pop', 26.1, .35),
      ('rewind', 27.0, .35), ('whoosh', 28.4, .4), ('snap', 30.45, .5), ('metal_tear', 30.5, .15), ('ding', 32.5, .4), ('whoosh2', 35.0, .3), ('pop', 35.95, .4),
      ('pop', 37.3, .4), ('hit', 37.84, .35), ('pop', 38.5, .35), ('whoosh', 39.9, .35), ('pop', 41.3, .35), ('pop', 43.1, .3), ('horn', 45.6, .25), ('ding', 46.0, .3),
      ('ding', 47.7, .3), ('ding', 48.4, .3), ('ding', 50.0, .3), ('horn', 51.2, .2), ('ding', 52.9, .3), ('pop', 54.2, .3), ('pop', 54.4, .3), ('pop', 54.6, .3),
      ('whoosh2', 55.9, .3), ('stamp', 58.22, .55), ('whoosh', 59.2, .3), ('pop', 59.3, .4)]
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
