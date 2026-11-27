"""v2 sound design + mix: SFX generated from the timeline (typing, transitions, reveals) + story SFX + new music, voice-first.
usage: audio2.py MUSIC_K SFX_K [--mix]   -> work/mix2.wav ; prints voice-over-background stats"""
import sys, os, json, random, subprocess
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import edit3
from edit3 import T, END, S
ROOT = edit3.ROOT; A = f'{ROOT}/audio'
MK, SK = float(sys.argv[1]), float(sys.argv[2])
X = lambda f, t, v, **k: dict(file=f'{A}/sfx/{f}.wav', t=round(t, 3), vol=v, **k)
sfx = []; rnd = random.Random(3)
BIG = {358.47, 320.2}
for sh in T:
    if sh.trans == 'whip': sfx.append(X('whoosh', sh.t0 - 0.12, 0.45))
    elif sh.trans == 'glitch': sfx.append(X('glitch', sh.t0, 0.5))
    elif sh.trans in ('push', 'zoom'): sfx.append(X('whoosh2', sh.t0 - 0.08, 0.4))
    elif sh.trans == 'leak': sfx.append(X('swell', sh.t0 - 1.2, 0.25))
    elif sh.trans == 'flash': sfx.append(X('braam' if round(sh.t0, 2) in BIG else 'hit', sh.t0, 0.55))
    if sh.grade == 'paper' and sh.src[0] == 'img': sfx.append(X('paper', sh.t0, 0.35))
    if (sh.k.get('src_tag') or '') and 'NTSB photo' in str([o.get('text') for o in sh.ov if o['k'] == 'tag']): sfx.append(X('shutter', sh.t0 + 0.05, 0.25))
    if sh.src[0] == 'route':
        sfx.append(X('whoosh2', sh.t0, 0.35))
        for m in sh.k.get('marks', []):
            if m[3] > sh.t0 + 0.2: sfx.append(X('pop', m[3], 0.4))
    for o in sh.ov:
        k = o['k']
        if k == 'type':
            n = len(o['text']); t = o['at']
            for i, ch in enumerate(o['text']):
                tt = o['at'] + i / o['cps']
                if ch == '\n': sfx.append(X('key_return', tt, 0.22))
                elif ch != ' ': sfx.append(X(f'key{rnd.randint(0, 2)}', tt + rnd.uniform(-0.01, 0.01), 0.16 + rnd.uniform(0, 0.05)))
        elif k == 'quote':
            for i in range(0, len(o['text']), 2): sfx.append(X(f'key{rnd.randint(0, 2)}', o['at'] + i / 34, 0.08))
        elif k == 'punch': sfx.append(X('hit', o['at'], 0.45))
        elif k == 'stamp': sfx.append(X('stamp', o['at'], 0.6))
        elif k == 'counter': sfx.append(X('tick', o['at'], 0.35)); sfx.append(X('pop', o['at'] + o['dur'], 0.3))
        elif k == 'circle': sfx.append(X('marker', o['at'], 0.45))
        elif k == 'chapter': sfx.append(X('swell', o['at'] - 1.9, 0.35)); sfx.append(X('braam', o['at'], 0.4))
        elif k == 'bigtime': sfx.append(X('whoosh2', o['at'] - 0.1, 0.4)); sfx.append(X('hit', o['at'] + 0.05, 0.4))
        elif k == 'stat': sfx.append(X('hit', o['at'], 0.45)); sfx.append(X('tick', o['at'] + 0.1, 0.3))
        elif k == 'cheese':
            for i in range(len(o['names'])): sfx.append(X('whoosh2', o['at'] + i * 0.35, 0.3))
            if o.get('arrow'): sfx.append(X('braam', o['arrow'], 0.45))
        elif k == 'callout': sfx.append(X('pop', o['at'], 0.3))
        elif k == 'names':
            for i in range(len(o['names'])): sfx.append(X('key0', o['at'] + i * o['step'], 0.12))
        elif k == 'lower': sfx.append(X('whoosh2', o['at'], 0.35))
        elif k == 'label': sfx.append(X('pop', o['at'], 0.2))
# ---- story sounds ----
sfx += [X('boom', 0.02, 0.9), X('braam', 0.05, 0.7), X('fire_bed', 0.2, 0.35, dur=3.6), X('hit', 3.84, 0.5), X('swell', 4.6, 0.3), X('fire_bed', 17.9, 0.25, dur=6.6),
        X('heartbeat', 28.3, 0.35), X('heartbeat', 29.3, 0.35), X('rig_hum', 24.5, 0.25, dur=10.5), X('braam', 35.2, 0.55), X('tick_bed', 41.07, 0.9, dur=7.0),
        X('rig_hum', 48.2, 0.22, dur=16.5), X('ocean_bed', 48.2, 0.25, dur=16.5), X('underwater_bed', 64.9, 0.35, dur=12.5), X('rig_hum', 77.3, 0.25, dur=15.0),
        X('tick_bed', 99.5, 0.35, dur=3.6), X('tick_bed', 103.18, 0.45, dur=1.8), X('helicopter', 103.2, 0.3, dur=8.0), X('helicopter', 119.3, 0.45, dur=4.3), X('helicopter', 123.5, 0.95, dur=3.0),
        X('helicopter', 129.1, 0.35, dur=4.0), X('rig_hum', 141.9, 0.2, dur=13.0), X('tick_bed', 155.9, 0.45, dur=2.2), X('rig_hum', 157.0, 0.2, dur=5.4),
        X('creak', S('creeping', 174) - 0.1, 0.35), X('alarm_beep', S('climbs', 183.5), 0.25), X('alarm_beep', S('again', 186.5), 0.25), X('alarm_beep', S('keeps', 189.5), 0.3),
        X('rig_hum', 190.7, 0.25, dur=12.7), X('sub_drop', S('bladder', 227) - 0.2, 0.45), X('pop', S('declared', 245.5) + 0.9, 0.4),
        X('tick_bed', 266.72, 0.45, dur=2.0), X('underwater_bed', 268.7, 0.3, dur=14.7), X('rig_hum', 283.4, 0.22, dur=6.7), X('underwater_bed', 290.1, 0.3, dur=14.1), X('geyser', 293.5, 0.12, dur=7.0),
        X('heartbeat', 316.7, 0.4), X('heartbeat', 317.7, 0.45), X('heartbeat', 318.7, 0.5), X('heartbeat', 319.6, 0.6),
        X('geyser', 320.2, 0.45, dur=8.6), X('geyser', 328.89, 1.0, dur=2.8), X('gas_hiss', 337.3, 0.4, dur=5.0), X('klaxon', 342.3, 0.25, dur=4.0), X('gas_hiss', 342.3, 0.25, dur=12.0),
        X('tick_bed', 354.1, 0.6, dur=4.3), X('heartbeat', 355.0, 0.5), X('heartbeat', 356.0, 0.55), X('heartbeat', 357.0, 0.6),
        X('explosion_big', 358.47, 1.0), X('fire_bed', 359.0, 0.9, dur=3.4), X('sub_drop', 362.26, 0.6), X('explosion_big', 363.78, 0.45), X('fire_bed', 364.2, 0.3, dur=9.0),
        X('klaxon', 366.86, 0.2, dur=5.0), X('klaxon', 371.91, 0.9, dur=1.5),
        X('underwater_bed', 373.2, 0.35, dur=17.5), X('glitch', 395.26, 0.5), X('underwater_bed', 399.9, 0.3, dur=6.0), X('groan', 405.9, 0.4), X('underwater_bed', 414.0, 0.3, dur=2.8),
        X('fire_bed', 416.7, 0.3, dur=11.5), X('ocean_bed', 416.7, 0.25, dur=26.5), X('splash', S('jump', 430.5), 0.5), X('ocean_bed', 443.1, 0.3, dur=11.0), X('bell', 447.1, 0.3),
        X('fire_bed', 462.7, 0.25, dur=4.0), X('groan', 466.8, 0.45), X('splash', 469.0, 0.35), X('underwater_bed', 470.9, 0.35, dur=10.4), X('ocean_bed', 481.3, 0.25, dur=20.0),
        X('bell', 577.9, 0.35), X('ocean_bed', 581.5, 0.25, dur=20.0), X('ocean_bed', 622.5, 0.25, dur=15.0)]
SOLO = [(41.07, 42.67), (123.59, 124.99), (319.02, 320.22), (328.89, 331.49), (358.47, 362.47), (371.91, 373.31), (450.32, 451.82), (593.86, 595.86)]
music = [('Evil_Incoming', 0.0, 41.2, 0.32, 0), ('Island_Mystery', 41.0, 115.0, 0.3, 0), ('Think_About_It', 155.8, 111.0, 0.3, 0),
         ('Night_Attack', 266.6, 87.6, 0.32, 0), ('Horror_Ambiance', 373.0, 98.0, 0.3, 0), ('Lonely_Mountain', 470.8, 89.4, 0.3, 0),
         ('Piano_Etude', 560.2, END - 560.2, 0.38, 0)]

def graph(stem):
    inputs, fc = [], []; idx = [0]
    def ain(path, extra=None): inputs.extend((extra or []) + ['-i', path]); idx[0] += 1; return idx[0] - 1
    vo = ain(f'{ROOT}/vo/vo.mp3'); fc.append(f"[{vo}:a]apad=whole_dur={END},asplit=2[vo][sc]")
    ml = []
    for i, (n, st, du, v, ss) in enumerate(music):
        j = ain(f'{A}/m3/{n}.mp3', ['-ss', str(ss), '-t', str(du)])
        fc.append(f"[{j}:a]aresample=44100,volume={v * MK:.4f},afade=t=in:st=0:d=1.5,afade=t=out:st={max(0, du - 2.5):.2f}:d=2.5,adelay={int(st * 1000)}|{int(st * 1000)}[m{i}]"); ml.append(f'[m{i}]')
    fc.append(''.join(ml) + f"amix=inputs={len(ml)}:duration=longest:normalize=0[mus]")
    fc.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=8:attack=15:release=450[musd]")
    sl = []
    for i, s in enumerate(sfx):
        solo = any(a - 0.2 <= s['t'] <= b for a, b in SOLO)
        j = ain(s['file'], ['-ss', str(s.get('ss', 0))] + (['-t', str(s['dur'])] if s.get('dur') else []))
        fade = f",afade=t=out:st={max(0, s['dur'] - 0.6):.2f}:d=0.6" if s.get('dur') else ''
        fc.append(f"[{j}:a]aresample=44100,volume={s['vol'] * (1.0 if solo else SK):.4f}{fade},adelay={int(s['t'] * 1000)}|{int(s['t'] * 1000)}[s{i}]"); sl.append(f'[s{i}]')
    # mix SFX in groups to keep the graph manageable
    G = 60; grp = []
    for g in range(0, len(sl), G):
        fc.append(''.join(sl[g:g + G]) + f"amix=inputs={len(sl[g:g + G])}:duration=longest:normalize=0[sg{g}]"); grp.append(f'[sg{g}]')
    fc.append(''.join(grp) + f"amix=inputs={len(grp)}:duration=longest:normalize=0[sfx]")
    if stem == 'vo': fc.append("[musd]anullsink;[sfx]anullsink;[vo]anull[aout]")
    elif stem == 'bg': fc.append("[vo]anullsink;[musd][sfx]amix=inputs=2:duration=longest:normalize=0[aout]")
    else: fc.append("[vo][musd][sfx]amix=inputs=3:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.84:attack=2:release=60:level=false[aout]")
    return inputs, fc
def render(stem, out):
    inputs, fc = graph(stem); script = f'{ROOT}/work/fc_{stem}.txt'; open(script, 'w').write(';\n'.join(fc))
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex_script', script, '-map', '[aout]', '-t', str(END), '-ar', '48000', '-ac', '2', out], check=True)
W = f'{ROOT}/work'
print('sfx events', len(sfx))
render('vo', f'{W}/st3_vo.wav'); render('bg', f'{W}/st3_bg.wav')
v, sr = sf.read(f'{W}/st3_vo.wav'); b, _ = sf.read(f'{W}/st3_bg.wav'); v = v.mean(1); b = b.mean(1); n = min(len(v), len(b)); rows = []
for i in range(0, n - sr * 5, sr * 5):
    vv, bb = v[i:i + sr * 5], b[i:i + sr * 5]; vr = np.sqrt((vv ** 2).mean())
    if vr < 0.01: continue
    rows.append((i / sr, 20 * np.log10(vr / max(1e-6, np.sqrt((bb ** 2).mean())))))
d = np.array([r[1] for r in rows])
print(f'MK={MK} SK={SK}: voice over background median {np.median(d):.1f} dB, 10th pct {np.percentile(d, 10):.1f}')
print('worst:', [(round(t), round(x, 1)) for t, x in sorted(rows, key=lambda r: r[1])[:8]])
if '--mix' in sys.argv: render('mix', f'{W}/mix3.wav'); print('wrote work/mix3.wav')
