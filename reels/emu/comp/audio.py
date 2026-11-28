import subprocess, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); A = R + '/../tmi/audio/sfx'
END = 62.35
ev = [('whoosh2', 0.0, 0.3), ('stamp', 2.36, 0.3), ('ding', 3.56, 0.3), ('whoosh', 5.23, 0.45), ('hit', 5.28, 0.4), ('ding', 6.68, 0.45), ('whoosh2', 7.44, 0.45), ('pop', 7.74, 0.35), ('pop', 10.64, 0.3), ('pop', 11.04, 0.3), ('pop', 11.44, 0.3), ('ding', 12.52, 0.3), ('whoosh', 13.78, 0.4), ('pop', 14.98, 0.35), ('whoosh2', 16.7, 0.35), ('stamp', 18.04, 0.6), ('pop', 19.24, 0.4), ('ding', 20.56, 0.3), ('whoosh', 21.12, 0.4), ('clank', 22.36, 0.4), ('clank', 22.51, 0.4), ('thud', 23.76, 0.35), ('pop', 25.16, 0.4), ('whoosh2', 27.8, 0.35), ('pop', 30.32, 0.45), ('ding', 32.7, 0.35), ('whoosh', 33.56, 0.4), ('pop', 33.56, 0.3), ('stamp', 39.8, 0.55), ('whoosh2', 40.52, 0.4), ('pop', 43.48, 0.3), ('pop', 43.98, 0.4), ('whoosh', 44.7, 0.4), ('tick', 45.84, 0.3), ('pop', 47.6, 0.35), ('whoosh2', 49.2, 0.35), ('pop', 50.4, 0.4), ('stamp', 51.92, 0.6), ('ding', 54.42, 0.4), ('whoosh', 56.04, 0.4), ('stamp', 58.02, 0.55), ('braam', 58.02, 0.3), ('hit', 59.3, 0.45), ('ding', 29.94, 0.45)]
trim = {}
BEDS = []
CUSTOM = [('march.wav', 0.0, 5.18, 0.5), ('ring.wav', 16.8, 17.84, 0.35), ('mg_long.wav', 28.56, 30.36, 0.55), ('mg_short.wav', 30.22, 30.92, 0.45), ('mg_short.wav', 38.38, 39.08, 0.5), ('click.wav', 39.6, 40.6, 0.7), ('engine.wav', 40.52, 44.7, 0.35), ('mg_short.wav', 41.82, 42.42, 0.35), ('mg_short.wav', 43.02, 43.62, 0.35)]
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
