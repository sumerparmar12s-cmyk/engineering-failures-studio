"""Original synthesized SFX for the Deepwater Horizon episode: helicopter, ship alarm, gas hiss, geyser roar, ocean bed,
machinery hum, underwater bed, metal groan, splash, ticking clock bed, soft bell. usage: sfx_dw.py OUT_DIR"""
import sys, numpy as np, soundfile as sf
OUT = sys.argv[1]; SR = 44100; R = np.random.default_rng(91)
T = lambda d: np.arange(int(d * SR)) / SR
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip(np.minimum((f - lo) / (lo * 0.5 + 1), (hi - f) / (hi * 0.5 + 1)) + 1, 0, 1); return np.fft.irfft(X * m, len(x))
def env(n, a, r):
    e = np.ones(n); A, B = int(a * SR), int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A) ** 1.5
    if B: e[-B:] *= np.linspace(1, 0, B) ** 2
    return e
def save(name, x, peak=0.9):
    x = x / (np.abs(x).max() + 1e-9) * peak; d = int(SR * 0.009); y = np.concatenate([np.zeros(d), x[:-d]])
    sf.write(f'{OUT}/{name}.wav', np.stack([x, 0.86 * x + 0.14 * y], 1).astype(np.float32), SR)
t = T(8); n = len(t)   # helicopter: blade slap ~ 11 Hz + turbine whine, passing (fade in/out)
slap = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 11 * t))) ** 4 * band(R.standard_normal(n), 60, 900)
whine = np.sin(2 * np.pi * 1850 * t) * 0.05
save('helicopter', (slap + whine + band(R.standard_normal(n), 100, 3000) * 0.15) * np.sin(np.pi * t / 8) ** 1.2)
t = T(4); n = len(t)   # ship general alarm: two-tone klaxon bursts
k = np.sign(np.sin(2 * np.pi * 420 * t)) * 0.6 + np.sign(np.sin(2 * np.pi * 560 * t)) * 0.4
gate = (np.sin(2 * np.pi * 1.0 * t) > 0).astype(float)
save('klaxon', band(k, 200, 3000) * gate * env(n, 0.02, 0.2), 0.7)
t = T(6); n = len(t); save('gas_hiss', band(R.standard_normal(n), 2000, 12000) * (0.4 + 0.6 * (1 - np.exp(-t * 0.8))) * env(n, 0.3, 1.0), 0.6)
t = T(7); n = len(t)   # geyser/mud roar
save('geyser', (band(R.standard_normal(n), 40, 400) * 1.4 + band(R.standard_normal(n), 400, 4000) * 0.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.9 * t) ** 2) * env(n, 0.15, 1.5))
t = T(24); n = len(t)  # ocean bed: slow swells
sw = 0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t + np.sin(2 * np.pi * 0.03 * t) * 2)
save('ocean_bed', band(R.standard_normal(n), 100, 2500) * (0.25 + 0.75 * sw ** 2) * env(n, 2, 2), 0.6)
t = T(20); n = len(t)  # machinery hum (rig)
save('rig_hum', (np.sin(2 * np.pi * 50 * t) * 0.3 + np.sin(2 * np.pi * 100 * t) * 0.15 + band(R.standard_normal(n), 60, 600) * 0.6 + band(R.standard_normal(n), 3000, 6000) * 0.05) * env(n, 1.5, 1.5), 0.5)
t = T(20); n = len(t)  # underwater: muffled low rumble with bubbles
bub = np.zeros(n)
for i in range(60):
    p = R.integers(0, n - 4000); m = 3000; tt = np.arange(m) / SR; f0 = R.uniform(300, 900)
    bub[p:p + m] += np.sin(2 * np.pi * f0 * (1 + 2 * tt) * tt) * np.exp(-tt * 40) * 0.3
save('underwater_bed', (band(R.standard_normal(n), 20, 250) + bub) * env(n, 2, 2), 0.55)
t = T(5); n = len(t)   # metal groan (sinking / buckling)
f = 70 + 40 * np.sin(2 * np.pi * 0.3 * t) + 20 * R.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)) * 0
g = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.5 * np.sin(2 * np.pi * np.cumsum(f * 2.7) / SR)
save('groan', np.tanh(g * 1.5) * band(R.standard_normal(n), 60, 1200) * 0.6 * env(n, 0.8, 1.2) + g * 0.2 * env(n, 0.8, 1.2))
t = T(1.5); n = len(t); save('splash', band(R.standard_normal(n), 300, 8000) * np.exp(-t * 4) * (1 - np.exp(-t * 60)) + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 8) * 0.5)
# ticking clock bed (1 tick per second, 20 s) and a soft low bell
t = T(20); n = len(t); x = np.zeros(n)
for s in range(20):
    i = int(s * SR); m = int(0.06 * SR); tt = np.arange(m) / SR
    x[i:i + m] += band(R.standard_normal(m), 2500, 9000) * np.exp(-tt * 180) * (1.0 if s % 2 == 0 else 0.7)
save('tick_bed', x, 0.6)
t = T(6); n = len(t); save('bell', sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t * d) for f, a, d in [(196, 1, 0.6), (392.5, 0.5, 0.8), (523, 0.3, 1.1), (784, 0.2, 1.4)]), 0.6)
print('ok')
