import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 68.76
ev = [('braam', 0.0, 0.35), ('pop', 1.36, 0.35), ('thud', 2.04, 0.4), ('whoosh', 4.4, 0.45), ('thud', 4.5, 0.35), ('whoosh2', 5.2, 0.45), ('thud', 5.3, 0.35), ('whoosh', 5.66, 0.45), ('thud', 5.76, 0.35), ('whoosh2', 6.32, 0.4), ('horn', 6.72, 0.25), ('tick', 6.88, 0.3), ('whoosh', 8.95, 0.45), ('braam', 10.18, 0.45), ('whoosh2', 12.2, 0.4), ('stamp', 13.8, 0.35), ('pop', 15.9, 0.35), ('pop', 17.64, 0.35), ('hit', 19.92, 0.3), ('whoosh', 21.9, 0.4), ('ding', 22.0, 0.3), ('hit', 27.18, 0.4), ('stamp', 30.9, 0.35), ('whoosh2', 32.62, 0.4), ('horn', 32.92, 0.3), ('pop', 34.36, 0.4), ('pop', 36.76, 0.35), ('pop', 37.18, 0.35), ('pop', 37.76, 0.35), ('ding', 39.34, 0.4), ('whoosh', 42.24, 0.4), ('swell', 42.68, 0.3), ('horn', 44.12, 0.3), ('ding', 45.68, 0.4), ('swell', 46.84, 0.25), ('whoosh2', 48.14, 0.45), ('braam', 48.44, 0.5), ('stamp', 48.74, 0.55), ('whoosh', 51.36, 0.4), ('pop', 12.34, 0.3), ('pop', 54.36, 0.3), ('pop', 54.56, 0.3), ('whoosh2', 56.09, 0.4), ('paper', 59.86, 0.5), ('ding', 62.18, 0.35), ('stamp', 65.94, 0.6), ('hit', 65.94, 0.35), ('explosion_big', 25.16, 0.2), ('boom', 25.16, 0.22), ('explosion_big', 26.28, 0.2), ('boom', 26.28, 0.22), ('explosion_big', 27.23, 0.2), ('boom', 27.23, 0.22), ('explosion_big', 27.58, 0.2), ('boom', 27.58, 0.22), ('explosion_big', 29.66, 0.2), ('boom', 29.66, 0.22), ('explosion_big', 31.0, 0.2), ('boom', 31.0, 0.22), ('explosion_big', 49.04, 0.2), ('boom', 49.04, 0.22), ('explosion_big', 50.04, 0.2), ('boom', 50.04, 0.22), ('explosion_big', 50.44, 0.2), ('boom', 50.44, 0.22), ('explosion_big', 50.74, 0.2), ('boom', 50.74, 0.22), ('explosion_big', 44.32, 0.2), ('boom', 44.32, 0.22), ('explosion_big', 45.88, 0.2), ('boom', 45.88, 0.22)]
trim = {}
BEDS = []
CUSTOM = [('engine.wav', 24.56, 32.04, 0.4), ('mg_short.wav', 26.18, 26.78, 0.35), ('mg_short.wav', 29.56, 30.16, 0.35), ('march.wav', 35.82, 41.42, 0.35), ('mg_short.wav', 48.94, 49.54, 0.4), ('mg_short.wav', 50.44, 51.04, 0.4), ('engine.wav', 46.74, 48.34, 0.3)]
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
for j, (fn, a0, b0, v0) in enumerate(CUSTOM):
    inp += ['-stream_loop', '-1', '-i', R + '/audio/' + fn]
    fc.append(f"[{2 + len(ev) + len(BEDS) + j}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=0:{b0 - a0},afade=t=out:st={max(0, b0 - a0 - 0.15)}:d=0.15,volume={v0},adelay={int(a0 * 1000)}|{int(a0 * 1000)}[cu{j}]"); el.append(f'[cu{j}]')
fc.append(''.join(el) + f"amix=inputs={len(el)}:duration=longest:normalize=0[sfx]")
fc.append("[sfx][sc2]sidechaincompress=threshold=0.05:ratio=4:attack=5:release=250[sfxd]")
fc.append("[vo][md][sfxd]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5,alimiter=limit=0.84:level=false[a]")
subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', ';'.join(fc), '-map', '[a]', '-t', str(END), '-ar', '48000', '-ac', '2', R + '/work/audio.wav'], check=True)
print('audio ok')
