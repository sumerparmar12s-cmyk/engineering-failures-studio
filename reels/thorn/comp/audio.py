import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 29.7
ev = [('pop', 0.05, .4), ('ding', 0.3, .25), ('whoosh', 2.35, .3), ('whoosh2', 6.95, .35), ('pop', 7.1, .35), ('whoosh', 13.28, .3), ('pop', 13.4, .35),
      ('pop', 19.85, .35), ('rewind', 25.4, .25), ('pop', 25.55, .3), ('ding', 25.85, .45), ('swell', 27.6, .25), ('ding', 28.55, .5)]
inp = ['-i', R + '/vo/vo.mp3', '-ss', '6', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]", f"[1:a]aresample=44100,volume=0.20,afade=t=in:d=0.4,afade=t=out:st={END-1.5}:d=1.5[m]",
      "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
el = []
for i, (nm, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{nm}.wav']; fc.append(f"[{i+2}:a]aresample=44100,volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); el.append(f'[s{i}]')
fc.append(''.join(el) + f"amix=inputs={len(el)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]")
fc.append("[vo][md][sfxd]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
