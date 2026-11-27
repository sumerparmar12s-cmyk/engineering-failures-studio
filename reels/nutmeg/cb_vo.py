"""Natural VO with Chatterbox (CPU). Generates each paragraph of script.md, joins with short gaps -> work/vo_raw.wav + work/segments.json"""
import sys, json, re, numpy as np, soundfile as sf, os
from chatterbox.tts import ChatterboxTTS
P = sys.argv[1] if len(sys.argv) > 1 else '.'
txt = open(f'{P}/script.md').read().split('## Narration (final)')[1].split('## Claim')[0].strip()
paras = [p.strip() for p in txt.split('\n\n') if p.strip()]
m = ChatterboxTTS.from_pretrained(device='cpu'); SR = m.sr
EXAG = float(os.environ.get('EXAG', 0.6)); CFG = float(os.environ.get('CFG', 0.45))
out = [np.zeros(int(SR * 0.05), np.float32)]; segs = []
def t(): return sum(len(x) for x in out) / SR
for i, p in enumerate(paras):
    w = m.generate(p, exaggeration=EXAG, cfg_weight=CFG).squeeze(0).numpy().astype(np.float32)
    # trim leading/trailing silence
    a = np.abs(w); thr = 0.01; idx = np.where(a > thr)[0]
    if len(idx): w = w[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]
    segs.append(dict(kind='vo', start=t(), text=p)); out.append(w); out.append(np.zeros(int(SR * 0.28), np.float32))
    print(i, round(len(w) / SR, 2), flush=True)
out.append(np.zeros(int(SR * 0.8), np.float32))
os.makedirs(f'{P}/work', exist_ok=True); sf.write(f'{P}/work/vo_raw.wav', np.concatenate(out), SR); json.dump(segs, open(f'{P}/work/segments.json', 'w'), indent=1)
print('total', round(t(), 1))
