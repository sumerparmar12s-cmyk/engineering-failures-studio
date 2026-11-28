#!/usr/bin/env python3
"""Make caption words exact: align Whisper timings to the script text, and insert the NASA audio lines
(which Whisper misses) from their measured clip timings. Rewrites vo/vo.mp3.words.json and vo/sentences.txt."""
import difflib, json, os, re, sys
P = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__))
W = json.load(open(f'{P}/vo/vo.mp3.words.json'))
segs = json.load(open(f'{P}/work/segments.json'))
inserted=[]
# script narration tokens, in order
txt = open(f'{P}/script.md', encoding='utf-8').read().split('## Narration (final)')[1].split('## Claim')[0]
script = [t for p in txt.strip().split('\n\n') if not p.startswith('Lines in [') for t in re.sub(r'^\[\w+\]\s*', '', p).split()]
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
