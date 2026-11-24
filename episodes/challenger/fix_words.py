#!/usr/bin/env python3
"""Make caption words exact: align Whisper timings to the script text, and insert the NASA audio lines
(which Whisper misses) from their measured clip timings. Rewrites vo/vo.mp3.words.json and vo/sentences.txt."""
import difflib, json, os, re, sys
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
W = json.load(open(f'{P}/vo/vo.mp3.words.json'))
segs = json.load(open(f'{P}/work/segments.json'))
# NASA words: (text, start, end) in source-clip seconds, and where each piece was cut from the clip
NASA = {
 'a': (5.70, [('T-minus', 5.86, 6.56), ('10,', 6.56, 7.10), ('9,', 7.60, 8.10), ('8,', 8.30, 8.88), ('7,', 9.40, 9.82), ('6.', 10.18, 10.62),
              ('We', 11.30, 11.36), ('have', 11.36, 11.68), ('main', 11.68, 11.94), ('engine', 11.94, 12.28), ('start,', 12.28, 12.72),
              ('4,', 13.44, 13.74), ('3,', 13.94, 14.40), ('2,', 14.68, 15.20), ('1,', 15.52, 16.18), ('and', 16.86, 17.34), ('liftoff!', 17.34, 18.02)]),
 'b': (80.85, [('Engines', 81.00, 81.22), ('throttling', 81.22, 81.64), ('up,', 81.64, 81.82), ('three', 82.06, 82.08), ('engines', 82.08, 82.28),
               ('now', 82.28, 82.52), ('at', 82.52, 82.62), ('104', 82.62, 82.94), ('percent.', 82.94, 83.40), ('"Challenger,', 83.40, 83.92),
               ('go', 84.42, 84.56), ('at', 84.56, 84.72), ('throttle', 84.72, 84.94), ('up."', 84.94, 85.40)]),
 'c': (127.70, [('Flight', 127.94, 128.62), ('controllers', 128.62, 128.98), ('here', 128.98, 129.20), ('looking', 129.20, 129.38), ('very', 129.38, 129.72),
                ('carefully', 129.72, 130.08), ('at', 130.08, 130.22), ('the', 130.22, 130.34), ('situation.', 130.34, 130.92),
                ('"Obviously', 132.74, 132.98), ('a', 132.98, 133.24), ('major', 133.24, 133.50), ('malfunction."', 133.50, 133.94)]),
}
nasa_segs = [s for s in segs if s['kind'] == 'nasa']
spans, inserted = [], []
for key, s in zip('abc', nasa_segs):
    cut, words = NASA[key]
    a = s['start']; b = a + (words[-1][2] - cut) + 0.3
    spans.append((a - 0.05, b))
    inserted += [dict(w=t, s=round(a + st - cut, 2), e=round(a + en - cut, 2), nasa=True) for t, st, en in words]
W = [x for x in W if not any(a <= x['s'] <= b for a, b in spans)]

# script narration tokens, in order
txt = open(f'{P}/script.md', encoding='utf-8').read().split('## Narration (final)')[1].split('## Claim')[0]
script = [t for p in txt.strip().split('\n\n') if not p.startswith('[NASA]') for t in p.split()]
norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
# whisper splits "Seventy -three", "11 ,000", "O -rings": merge such fragments first
merged = []
for x in W:
    if merged and re.match(r'^[-,.][0-9A-Za-z]', x['w']):
        merged[-1]['w'] += x['w']; merged[-1]['e'] = x['e']
    else:
        merged.append(dict(x))
sm = difflib.SequenceMatcher(a=[norm(x['w']) for x in merged], b=[norm(t) for t in script], autojunk=False)
out = []
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == 'equal' or (op == 'replace' and i2 - i1 == j2 - j1):
        for k in range(i2 - i1):
            out.append(dict(w=script[j1 + k], s=merged[i1 + k]['s'], e=merged[i1 + k]['e']))
    elif op == 'replace' and i2 > i1:   # different counts: spread script words over whisper's span
        a, b = merged[i1]['s'], merged[i2 - 1]['e']; n = j2 - j1; step = (b - a) / n
        out += [dict(w=script[j1 + k], s=round(a + k * step, 2), e=round(a + (k + 1) * step, 2)) for k in range(n)]
    elif op == 'insert':   # script words whisper dropped: squeeze them in after the previous word
        a = out[-1]['e'] if out else 0
        out += [dict(w=script[j1 + k], s=round(a + 0.05 * k, 2), e=round(a + 0.05 * (k + 1), 2)) for k in range(j2 - j1)]
    # 'delete' (whisper words not in the script) are dropped
out = sorted(out + inserted, key=lambda x: x['s'])
json.dump(out, open(f'{P}/vo/vo.mp3.words.json', 'w', encoding='utf-8'))
lines, line, st = [], [], None
for x in out:
    st = x['s'] if st is None else st; line.append(x['w'])
    if re.search(r'[.?!]"?$', x['w']): lines.append(f"{st:7.2f} {' '.join(line)}"); line, st = [], None
if line: lines.append(f"{st:7.2f} {' '.join(line)}")
open(f'{P}/vo/sentences.txt', 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print(len(out), 'words; ops', sum(1 for o in sm.get_opcodes() if o[0] != 'equal'))
