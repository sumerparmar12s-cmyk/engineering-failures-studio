import subprocess, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 25.0
ev = [('whoosh2', 0.0, .5), ('braam', 0.05, .35), ('hit', 1.48, .4), ('pop', 1.6, .3), ('hit', 4.38, .35), ('hit', 4.95, .35), ('hit', 5.5, .35), ('hit', 6.05, .35),
      ('whoosh2', 6.6, .45), ('pop', 6.75, .4), ('stamp', 7.82, .55), ('ding', 8.78, .5), ('whoosh', 13.0, .45), ('stamp', 13.16, .55), ('ding', 14.1, .5),
      ('whoosh', 15.74, .45), ('stamp', 15.9, .55), ('ding', 16.6, .5), ('whoosh', 18.84, .45), ('stamp', 19.0, .55), ('ding', 20.9, .5), ('hit', 22.44, .4)]
inp = ['-i', R + '/vo/vo.mp3', '-ss', '10', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=2[vo][sc]", f"[1:a]aresample=44100,volume=0.16,afade=t=in:d=0.3,afade=t=out:st={END-1.5}:d=1.5[m]", "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
sl = []
for i, (n, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{n}.wav']; fc.append(f"[{i+2}:a]aresample=44100,volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); sl.append(f'[s{i}]')
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
fc.append("[vo][md][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
