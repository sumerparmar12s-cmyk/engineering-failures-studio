"""Casual in-scene dialogue (US English), placed on the new 32.2 s timeline -> vo/dialog.wav + vo/lines2.json"""
import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
M = '/home/user/engineering-failures-studio/.toolchain/kokoro/'
k = Kokoro(M + 'kokoro-v1.0.onnx', M + 'voices-v1.0.bin'); SR = 24000
LINES = [(0.35, "Okay... there's a thorn stuck in here. Pretty deep, too."),
         (4.70, "Hold still for me... hold still."),
         (8.70, "Let me push it up a little."),
         (12.10, "See it? Right there."),
         (19.20, "Alright, got the tip. Nice and easy."),
         (24.20, "Come on... almost..."),
         (28.50, "Ohh, there it is. Look at that.")]
END = 32.2; out = np.zeros(int(SR * END), np.float32); meta = []
for t, s in LINES:
    a, _ = k.create(s, voice='am_michael', speed=0.98, lang='en-us'); a = a.astype(np.float32)
    i = int(t * SR); out[i:i + len(a)] += a[:len(out) - i]; meta.append(dict(t=t, d=len(a) / SR, text=s))
sf.write('vo/dialog_raw.wav', out, SR); json.dump(meta, open('vo/lines2.json', 'w'), indent=1)
for m in meta: print(f"{m['t']:.2f} +{m['d']:.2f}  {m['text']}")
