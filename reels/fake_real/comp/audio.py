import subprocess, sys, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 20.6
ev = [('whoosh2', 0.0, .5), ('hit', 0.7, .35), ('hit', 1.4, .35), ('hit', 2.1, .35), ('pop', 1.6, .4), ('whoosh2', 2.7, .45),
      ('stamp', 2.85, .55), ('ding', 3.82, .5), ('stamp', 3.85, .4), ('whoosh', 8.2, .45), ('stamp', 8.36, .55), ('ding', 9.30, .5),
      ('whoosh', 11.0, .45), ('stamp', 11.18, .55), ('ding', 11.86, .5), ('whoosh', 14.2, .45), ('stamp', 14.40, .55), ('ding', 16.12, .5), ('braam', 18.9, .4)]
inp = ['-i', R + '/vo/vo.mp3', '-ss', '10', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=2[vo][sc]", f"[1:a]aresample=44100,volume=0.16,afade=t=in:d=0.3,afade=t=out:st={END-1.5}:d=1.5[m]", "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
sl = []
for i, (n, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{n}.wav']; fc.append(f"[{i+2}:a]aresample=44100,volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); sl.append(f'[s{i}]')
fc.append(''.join(sl) + f"amix=inputs={len(sl)}:duration=longest:normalize=0[sfx]")
fc.append("[vo][md][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
