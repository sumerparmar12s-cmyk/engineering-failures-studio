"""Original synthesized train / emergency sound effects for the East Palestine episode. usage: python sfx_train.py OUT_DIR"""
import sys, numpy as np, soundfile as sf
OUT = sys.argv[1]; SR = 44100; R = np.random.default_rng(41)
T = lambda d: np.arange(int(d * SR)) / SR
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    m = np.clip(np.minimum((f - lo) / (lo * 0.5 + 1), (hi - f) / (hi * 0.5 + 1)) + 1, 0, 1)
    return np.fft.irfft(X * m, len(x))
def env(n, a, r):
    e = np.ones(n); A, B = int(a * SR), int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A) ** 1.5
    if B: e[-B:] *= np.linspace(1, 0, B) ** 2
    return e
def save(name, x, peak=0.95):
    x = x / (np.abs(x).max() + 1e-9) * peak
    d = int(SR * 0.01); y = np.concatenate([np.zeros(d), x[:-d]])
    sf.write(f'{OUT}/{name}.wav', np.stack([x, 0.85 * x + 0.15 * y], 1).astype(np.float32), SR)
# train rumble with wheel clacks (43 mph: car length 18 m -> pairs of clicks every ~0.95 s), 14 s
d = 14; t = T(d); n = len(t)
rum = band(R.standard_normal(n), 25, 180) * 1.4 + band(R.standard_normal(n), 180, 1200) * 0.35
cl = np.zeros(n)
for k in range(int(d / 0.95) + 1):
    for off in (0.0, 0.09, 0.62, 0.71):
        i = int((k * 0.95 + off) * SR)
        if i < n: m = min(n - i, int(0.12 * SR)); tt = np.arange(m) / SR; cl[i:i + m] += (np.sin(2 * np.pi * 180 * tt) * 0.6 + band(R.standard_normal(m), 400, 3000)) * np.exp(-tt * 45)
save('train_rumble', (rum + cl * 0.9) * env(n, 1.5, 2.0), 0.85)
# freight horn: 5-chime chord, long-long-short-long feel shortened to two blasts, 3.2 s
def horn(d):
    t = T(d); x = sum(a * (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)) for f, a in [(311, 1), (370, 0.9), (415, 0.8), (494, 0.7), (622, 0.5)])
    return np.tanh(x * 0.5) * env(len(t), 0.06, 0.25)
save('horn', np.concatenate([horn(1.4), np.zeros(int(0.25 * SR)), horn(1.6)]), 0.8)
# brake squeal + emergency air dump, 3.5 s
d = 3.5; t = T(d); n = len(t)
sq = sum(np.sin(2 * np.pi * f * (1 + 0.01 * np.sin(2 * np.pi * 5 * t)) * t) * a for f, a in [(2830, 1), (4120, 0.5), (1960, 0.4)]) * (0.6 + 0.4 * np.sin(2 * np.pi * 1.7 * t) ** 2)
air = band(R.standard_normal(n), 1500, 9000) * np.exp(-t * 0.9)
save('brake_squeal', (sq * 0.35 + air * 0.8) * env(n, 0.08, 0.8), 0.8)
# derailment: cascade of heavy metal impacts, grinding, tearing, 4.5 s
d = 4.5; t = T(d); n = len(t); x = np.zeros(n)
for k in range(26):
    t0 = 0.05 + (k / 26) ** 1.3 * 3.0 + R.uniform(-0.05, 0.05); i = int(t0 * SR); m = n - i; tt = np.arange(m) / SR
    hit = np.sin(2 * np.pi * R.uniform(40, 90) * tt) * np.exp(-tt * 6) * 1.2 + band(R.standard_normal(m), 150, 5000) * np.exp(-tt * R.uniform(6, 14))
    x[i:] += hit * R.uniform(0.5, 1.0) * (1 - k / 40)
grind = band(R.standard_normal(n), 300, 4000) * (0.5 + 0.5 * (np.sin(2 * np.pi * 23 * t) > 0)) * np.exp(-t * 0.7) * 0.5
scr = sum(np.sin(2 * np.pi * f * (1 + 0.2 * np.sin(2 * np.pi * 3 * t + f)) * t) for f in (900, 1310, 1770)) * np.exp(-t * 0.9) * 0.12
save('derail_crash', (x + grind + scr) * env(n, 0.005, 1.0))
# emergency sirens: two wailing sirens with doppler-ish drift, 6 s
d = 6; t = T(d); n = len(t)
def wail(rate, lo, hi, ph):
    f = lo + (hi - lo) * (0.5 - 0.5 * np.cos(2 * np.pi * rate * t + ph)); p = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(p) + 0.3 * np.sin(2 * p) + 0.15 * np.sin(3 * p)
s = wail(0.22, 650, 1450, 0) + 0.7 * wail(0.31, 700, 1550, 1.7)
s = band(s, 300, 4000) * env(n, 1.2, 1.5) * (0.6 + 0.4 * t / d)
save('sirens', s + band(R.standard_normal(n), 60, 300) * 0.08, 0.7)
# radio squelch click + static (for the alarm voice)
d = 0.35; t = T(d); n = len(t)
save('radio_click', band(R.standard_normal(n), 800, 6000) * np.exp(-t * 18) + band(R.standard_normal(n), 2000, 5000) * 0.15 * env(n, 0.0, 0.1), 0.6)
# alarm beeps (three short tones)
x = np.concatenate([np.concatenate([np.sin(2 * np.pi * 1480 * T(0.16)) * env(int(0.16 * SR), 0.005, 0.02), np.zeros(int(0.09 * SR))]) for _ in range(3)])
save('alarm_beep', x, 0.7)
# big explosion for the vent and burn charges: sharp crack + long rolling boom, 5 s
d = 5; t = T(d); n = len(t)
crack = band(R.standard_normal(n), 400, 8000) * np.exp(-t * 30)
boom = band(R.standard_normal(n), 20, 160) * np.exp(-t * 0.9) * 2.2 + np.sin(2 * np.pi * (38 + 30 * np.exp(-t * 4)) * t) * np.exp(-t * 1.2)
roll = band(R.standard_normal(n), 60, 600) * (np.exp(-t * 0.6) * (1 - np.exp(-t * 3))) * 0.7
save('explosion_big', crack + boom + roll)
# low drone (tension bed under silence), 8 s
d = 8; t = T(d); n = len(t)
save('drone', (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.5 * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) + band(R.standard_normal(n), 40, 200) * 0.6) * env(n, 2.0, 2.0), 0.6)
print('ok')
