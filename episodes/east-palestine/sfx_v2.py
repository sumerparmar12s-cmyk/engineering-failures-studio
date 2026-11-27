"""Second original SFX set (synthesized): key clicks, braam, glitch, marker squeak, paper, wind/room beds, sub drop, short whoosh, reverse swell."""
import sys, numpy as np, soundfile as sf
OUT = sys.argv[1]; SR = 44100; R = np.random.default_rng(77)
T = lambda d: np.arange(int(d * SR)) / SR
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip(np.minimum((f - lo) / (lo * 0.5 + 1), (hi - f) / (hi * 0.5 + 1)) + 1, 0, 1); return np.fft.irfft(X * m, len(x))
def env(n, a, r):
    e = np.ones(n); A, B = int(a * SR), int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A) ** 1.5
    if B: e[-B:] *= np.linspace(1, 0, B) ** 2
    return e
def save(name, x, peak=0.95):
    x = x / (np.abs(x).max() + 1e-9) * peak; d = int(SR * 0.008); y = np.concatenate([np.zeros(d), x[:-d]])
    sf.write(f'{OUT}/{name}.wav', np.stack([x, 0.88 * x + 0.12 * y], 1).astype(np.float32), SR)
for k in range(3):   # typewriter / keyboard key clicks
    t = T(0.09); n = len(t)
    x = band(R.standard_normal(n), 1800 + k * 500, 7000) * np.exp(-t * 160) + np.sin(2 * np.pi * (900 + 180 * k) * t) * np.exp(-t * 90) * 0.5 + band(R.standard_normal(n), 200, 900) * np.exp(-t * 60) * 0.4
    save(f'key{k}', x, 0.8)
t = T(0.5); x = band(R.standard_normal(len(t)), 300, 3000) * np.exp(-t * 30) + np.sin(2 * np.pi * 220 * t) * np.exp(-t * 18) * 0.6
save('key_return', x, 0.8)
# braam: low brass-like swell with sub hit, 3.5 s
t = T(3.5); n = len(t)
f0 = 55; br = sum(np.sin(2 * np.pi * f0 * h * t + h) / h ** 0.8 for h in range(1, 18)) * (1 + 0.3 * np.sin(2 * np.pi * 5.5 * t))
br = np.tanh(br * 1.4) * (1 - np.exp(-t * 18)) * np.exp(-t * 0.9)
sub = np.sin(2 * np.pi * (48 * np.exp(-t * 0.8) + 30) * t) * np.exp(-t * 1.6) * 1.2
save('braam', br * 0.7 + sub)
# glitch burst 0.4 s
t = T(0.4); n = len(t); x = R.standard_normal(n); step = (R.integers(20, 120, n // 400 + 1)).repeat(400)[:n]
x = np.round(x * 3) / 3 * (np.sin(2 * np.pi * 60 * t) > -0.3) + np.sign(np.sin(2 * np.pi * 1300 * t)) * 0.3 * (np.sin(2 * np.pi * 9 * t) > 0)
save('glitch', band(x, 200, 9000) * env(n, 0.005, 0.08), 0.7)
# marker squeak (drawing a circle) 0.6 s
t = T(0.6); n = len(t); fq = 2400 + 600 * np.sin(2 * np.pi * 2.2 * t); ph = 2 * np.pi * np.cumsum(fq) / SR
x = (np.sin(ph) * 0.3 + band(R.standard_normal(n), 2000, 7000)) * (0.5 + 0.5 * np.abs(np.sin(2 * np.pi * 3 * t))) * env(n, 0.03, 0.1)
save('marker', x, 0.5)
# paper slide / rustle 0.8 s
t = T(0.8); n = len(t); save('paper', band(R.standard_normal(n), 1500, 9000) * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * 4 * t))) * env(n, 0.05, 0.3), 0.6)
# winter wind bed 20 s
t = T(20); n = len(t); w = band(R.standard_normal(n), 120, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t) * np.sin(2 * np.pi * 0.17 * t + 1))
save('wind_bed', w * env(n, 2, 2), 0.6)
# room tone / tense room bed 20 s (low hum + air)
t = T(20); n = len(t); save('room_bed', (np.sin(2 * np.pi * 60 * t) * 0.15 + band(R.standard_normal(n), 80, 400) * 0.6 + band(R.standard_normal(n), 2000, 6000) * 0.05) * env(n, 1.5, 1.5), 0.5)
# sub drop 2.2 s
t = T(2.2); save('sub_drop', np.sin(2 * np.pi * (90 * np.exp(-t * 1.8) + 28) * t) * np.exp(-t * 1.3) + band(R.standard_normal(len(t)), 40, 200) * np.exp(-t * 4) * 0.4)
# short whoosh 0.6 s and reverse swell 2 s
t = T(0.6); n = len(t); fc = np.linspace(300, 4000, n); x = band(R.standard_normal(n), 200, 6000) * np.sin(np.pi * t / 0.6) ** 2
save('whoosh2', x, 0.7)
t = T(2.0); n = len(t); x = (band(R.standard_normal(n), 100, 5000) + np.sin(2 * np.pi * 110 * t) * 0.3) * (t / 2.0) ** 3
save('swell', x, 0.85)
# clock tick (crisp)
t = T(0.08); save('clock', band(R.standard_normal(len(t)), 2500, 9000) * np.exp(-t * 200) + np.sin(2 * np.pi * 3200 * t) * np.exp(-t * 120) * 0.4, 0.7)
print('ok')
