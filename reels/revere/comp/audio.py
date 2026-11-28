import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 82.26
ev = [('whoosh2', 0.0, 0.35), ('pop', 5.64, 0.3), ('pop', 5.94, 0.3), ('ding', 6.4, 0.4), ('hit', 8.84, 0.3), ('whoosh', 10.5, 0.4), ('pop', 13.82, 0.35), ('pop', 14.96, 0.3), ('pop', 16.12, 0.35), ('whoosh2', 18.86, 0.35), ('stamp', 19.06, 0.4), ('pop', 22.86, 0.4), ('modem_blip', 25.32, 0.35), ('modem_blip', 25.77, 0.35), ('modem_blip', 26.22, 0.35), ('modem_blip', 26.67, 0.35), ('whoosh', 28.38, 0.4), ('bell', 29.08, 0.35), ('ding', 30.36, 0.35), ('ding', 32.76, 0.4), ('splash', 34.62, 0.3), ('whoosh2', 38.12, 0.4), ('hit', 41.94, 0.35), ('pop', 43.42, 0.4), ('whoosh', 46.94, 0.35), ('pop', 49.44, 0.3), ('ding', 51.54, 0.3), ('pop', 53.32, 0.35), ('pop', 54.16, 0.35), ('braam', 58.63, 0.45), ('hit', 58.68, 0.5), ('stamp', 60.0, 0.5), ('thud', 62.36, 0.6), ('crunch', 62.41, 0.4), ('whoosh2', 66.44, 0.4), ('boom', 69.42, 0.6), ('explosion_big', 69.47, 0.25), ('swell', 71.08, 0.3), ('paper', 74.74, 0.5), ('stamp', 76.5, 0.45), ('ding', 78.88, 0.45), ('pop', 79.68, 0.35), ('hit', 80.5, 0.35)]
trim = {}
BEDS = [(0.0, 10.4), (37.92, 51.84), (52.14, 58.68), (65.36, 68.74)]
inp = ['-i', R + '/vo/vo.mp3', '-ss', '0', '-t', str(END), '-i', R + '/audio/music.mp3']
fc = [f"[0:a]apad=whole_dur={END},asplit=3[vo][sc][sc2]", f"[1:a]aresample=44100,volume=0.30,afade=t=in:d=0.3,afade=t=out:st={END-1.6}:d=1.6[m]",
      "[m][sc]sidechaincompress=threshold=0.04:ratio=6:attack=10:release=300[md]"]
el = []
for i, (nm, t, v) in enumerate(ev):
    inp += ['-i', f'{A}/{nm}.wav']; tr = trim.get((nm, t)); cut = f"atrim=0:{tr},afade=t=out:st={tr-0.4}:d=0.4," if tr else ''
    fc.append(f"[{i+2}:a]aresample=44100,{cut}volume={v*0.45:.3f},adelay={int(t*1000)}|{int(t*1000)}[s{i}]"); el.append(f'[s{i}]')
for j, (a0, b0) in enumerate(BEDS):
    inp += ['-stream_loop', '-1', '-i', R + '/audio/hooves.wav']; n = len(inp) // 2 - 1
    fc.append(f"[{2 + len(ev) + j}:a]aresample=44100,atrim=0:{b0 - a0},afade=t=in:d=0.3,afade=t=out:st={b0 - a0 - 0.4}:d=0.4,volume=0.16,adelay={int(a0 * 1000)}|{int(a0 * 1000)}[h{j}]"); el.append(f'[h{j}]')
fc.append(''.join(el) + f"amix=inputs={len(el)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]")
fc.append("[vo][md][sfxd]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
