import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 23.4
ev = [('braam', 0.0, .4), ('whoosh2', 0.0, .4), ('wind_bed', 0.0, .5), ('creak', 0.6, .5), ('hit', 1.92, .35), ('groan', 2.2, .4), ('whoosh', 3.7, .4),
      ('metal_tear', 5.06, .6), ('crunch', 5.10, .4), ('splash', 5.6, .55), ('whoosh2', 9.4, .4), ('jet_pass', 9.5, .3),
      ('explosion_big', 11.28, .6), ('sub_drop', 11.30, .5), ('hit', 14.16, .45), ('whoosh', 15.0, .4), ('fire_bed', 15.12, .5),
      ('flame_burst', 16.74, .45), ('whoosh', 18.76, .35), ('boom', 21.06, .45), ('metal_tear', 21.5, .3), ('stamp', 21.62, .6), ('ding', 21.67, .45)]
# trim beds: wind 0-8.4, fire 20.4-26.3
trim = {('wind_bed', 0.0): 5.1, ('fire_bed', 15.12): 5.9}
inp = ['-i', R + '/vo/vo.mp3', '-ss', '4', '-t', str(END), '-i', R + '/../tmi/audio/m/Creepy_Hallow.mp3']
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
