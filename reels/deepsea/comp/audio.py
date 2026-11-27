import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 23.0
ev = [('sonar_ping', 0.0, .5), ('underwater_bed', 0.0, .55), ('pop', 0.05, .4), ('whoosh2', 1.75, .35), ('pop', 1.85, .3), ('ding', 3.6, .25),
      ('whoosh', 5.1, .35), ('sonar_ping', 5.2, .35), ('whoosh2', 8.5, .4), ('pop', 8.65, .35), ('sonar_ping', 12.5, .45), ('hit', 12.52, .3),
      ('swell', 15.0, .3), ('whoosh', 16.85, .35), ('sonar_ping', 16.95, .3), ('braam', 19.8, .35), ('hit', 19.86, .35), ('ding', 21.5, .3)]
# trim beds: wind 0-8.4, fire 20.4-26.3
trim = {('underwater_bed', 0.0): 23.0}
inp = ['-i', R + '/vo/vo.mp3', '-ss', '0', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=2[vo][sc]", f"[1:a]aresample=44100,volume=0.20,afade=t=in:d=0.2,afade=t=out:st={END-1.6}:d=1.6[m]", "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
sl = []
for i, (n, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{n}.wav']; tr = trim.get((n, t))
    cut = f"atrim=0:{tr},afade=t=out:st={tr-0.6}:d=0.6," if tr else ''
    fc.append(f"[{i+2}:a]aresample=44100,{cut}volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); sl.append(f'[s{i}]')
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]".replace('[sc2]', '[sc2]'))
fc[0] = f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]"
fc.append("[vo][md][sfxd]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
