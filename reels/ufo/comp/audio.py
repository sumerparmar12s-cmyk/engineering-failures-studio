import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 23.6
ev = [('radio_click', 0.0, .5), ('braam', 0.0, .45), ('jet_pass', 0.1, .35), ('glitch', 0.02, .35), ('hit', 2.80, .3), ('sonar_ping', 2.9, .3),
      ('glitch', 5.34, .45), ('typewriter', 5.4, .25), ('glitch', 7.08, .45), ('stamp', 7.32, .6), ('shutter', 10.24, .5), ('shutter', 11.86, .5),
      ('riser', 12.4, .3), ('glitch', 13.90, .5), ('hit', 13.92, .45), ('modem_blip', 15.54, .35), ('modem_blip', 16.98, .35), ('stamp', 19.30, .6),
      ('glitch', 20.30, .45), ('radio_click', 20.32, .4), ('hit', 21.78, .4), ('drone', 0.0, .35)]
# trim beds: wind 0-8.4, fire 20.4-26.3
trim = {('drone', 0.0): 23.6}
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
