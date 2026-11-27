import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 40.0
ev = [('whoosh2', 0.0, .35), ('ding', 1.5, .35), ('pop', 3.6, .45), ('pop', 5.3, .45), ('whoosh', 6.3, .4), ('stamp', 9.35, .6), ('ding', 9.5, .3),
      ('whoosh2', 10.45, .3), ('pop', 11.95, .35), ('pop', 13.9, .35), ('pop', 14.6, .35), ('pop', 15.5, .35), ('pop', 17.7, .35),
      ('whoosh', 18.9, .35), ('pop', 19.2, .4), ('pop', 19.8, .4), ('tick_bed', 20.3, .25), ('ding', 21.85, .4), ('pop', 22.3, .4),
      ('whoosh2', 24.2, .3), ('pop', 24.3, .25), ('pop', 24.6, .25), ('pop', 24.9, .25), ('pop', 25.5, .4), ('whoosh', 27.0, .35), ('thud', 27.1, .5),
      ('whoosh2', 28.45, .35), ('swell', 29.4, .3), ('hit', 30.4, .35), ('pop', 32.2, .35), ('whoosh', 33.6, .35), ('ding', 33.8, .35), ('ding', 34.1, .3),
      ('clank', 35.4, .4), ('whoosh2', 36.65, .35), ('paper', 37.0, .5), ('pop', 37.7, .4), ('pop', 39.0, .45)]
trim = {('tick_bed', 20.3): 1.5}
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
