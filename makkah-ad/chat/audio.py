# Original score for «خيط الضوء»: 120 BPM cinematic electronic + Hijaz oud phrase. No vocals.
import numpy as np, wave
SR = 44100; DUR = 40.0; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N); FX = np.zeros(N)   # FX bus gets reverb
rng = np.random.default_rng(1)
def T(n): return np.arange(n) / SR
def put(buf, t, sig, g=1.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i < N: buf[i:j] += sig[:j - i] * g
def st(t, sig, g=1.0, pan=0.0, fx=0.0):
    put(L, t, sig, g * (1 - pan) * .9); put(R, t, sig, g * (1 + pan) * .9)
    if fx: put(FX, t, sig, g * fx)
def onepole(x, a):  # simple low-pass, a in (0,1)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def lp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / np.sqrt(1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x))
def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / np.sqrt(1 + (f / cutoff) ** 4); return np.fft.irfft(X, len(x))
def bp_fast(x, lo, hi): return hp_fast(lp_fast(x, hi), lo)
def env(n, a=.005, d=None, k=6.0):
    t = T(n); e = np.minimum(1, t / max(a, 1e-4))
    return e * np.exp(-k * t)

# --- instruments ---
def kick(g=1.0):
    n = int(.45 * SR); t = T(n); f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR; s = np.sin(ph) * np.exp(-t * 7.5)
    s[:220] += rng.standard_normal(220) * .25 * np.linspace(1, 0, 220)
    return np.tanh(s * 1.6) * g
def clap():
    n = int(.25 * SR); s = rng.standard_normal(n); s = bp_fast(s, 900, 3500)
    e = np.exp(-T(n) * 22); e[:int(.01 * SR)] *= np.abs(np.sin(np.linspace(0, 9, int(.01 * SR))))
    return s * e * .5
def hat(open_=False):
    n = int((.18 if open_ else .05) * SR); s = hp_fast(rng.standard_normal(n), 7000)
    return s * np.exp(-T(n) * (14 if open_ else 70)) * .25
def oud(freq, dur=1.6, bright=.996):
    # Karplus–Strong pluck, vectorised by period
    n = int(dur * SR); p = int(SR / freq); y = np.zeros(n + p + 1)
    y[:p] = rng.uniform(-1, 1, p) * np.hanning(p) * 1.4
    for s0 in range(p, n + p, p):
        e = min(s0 + p, n + p); k = e - s0
        y[s0:e] = bright * .5 * (y[s0 - p:s0 - p + k] + y[s0 - p + 1:s0 - p + k + 1])
    out = y[:n]; out = out + .35 * np.sin(2 * np.pi * freq * 2 * T(n)) * np.exp(-T(n) * 9) * .3
    return out * np.minimum(1, T(n) / .002) * .55
def pluck(freq, dur=.6):
    t = T(int(dur * SR)); s = np.sign(np.sin(2 * np.pi * freq * t)) * .3 + np.sin(2 * np.pi * freq * t)
    s = lp_fast(s, 3500) * np.exp(-t * 7); return s * .35
def bell(freq, dur=2.0):
    t = T(int(dur * SR)); s = sum(np.sin(2 * np.pi * freq * m * t) * a for m, a in [(1, 1), (2.76, .4), (5.4, .2)])
    return s * np.exp(-t * 3) * .18
def ping(freq=1760):
    t = T(int(.9 * SR)); s = np.sin(2 * np.pi * freq * t) + .4 * np.sin(2 * np.pi * freq * 1.5 * t)
    return s * np.exp(-t * 9) * np.minimum(1, t / .002) * .28
def saw(freq, n):
    t = T(n); return sum(np.sin(2 * np.pi * freq * k * t) / k for k in range(1, 9))
def pad(freqs, dur, g=.08):
    n = int(dur * SR); s = sum(saw(f * d, n) for f in freqs for d in (0.997, 1.003))
    s = lp_fast(s, 1400); a = np.minimum(1, T(n) / .4) * np.minimum(1, (dur - T(n)) / .4)
    return s * a * g
def bass(freq, dur):
    n = int(dur * SR); t = T(n); s = np.sin(2 * np.pi * freq * t) + .3 * np.tanh(3 * np.sin(2 * np.pi * freq * t))
    return s * np.minimum(1, t / .01) * np.minimum(1, (dur - t) / .05) * .32
def noise_swell(dur, lo, hi, rise=True, g=.25):
    n = int(dur * SR); s = rng.standard_normal(n); out = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        q = i / n; q = q if rise else 1 - q
        cut = lo * (hi / lo) ** q; seg_ = s[i:i + blk]
        out[i:i + blk] = bp_fast(np.concatenate([seg_, np.zeros(blk - len(seg_))]), cut * .5, cut * 1.5)[:len(seg_)]
    e = np.linspace(0, 1, n) ** 2 if rise else np.linspace(1, 0, n) ** 1.5
    return out * e * g
def whoosh(dur=.7, g=.35):
    n = int(dur * SR); s = rng.standard_normal(n); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return bp_fast(s, 300, 3000) * e * g
def impact():
    n = int(2.5 * SR); t = T(n); f = 35 + 80 * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8)
    s += lp_fast(rng.standard_normal(n), 2500) * np.exp(-t * 4) * .5
    return np.tanh(s * 1.4) * .9
def tick():
    n = int(.04 * SR); return bp_fast(rng.standard_normal(n), 2000, 6000) * np.exp(-T(n) * 120) * .5

# Hijaz on D
D3, Eb3, Fs3, G3, A3, Bb3, C4, D4 = 146.83, 155.56, 185.0, 196.0, 220.0, 233.08, 261.63, 293.66
HIJ = [D4, 311.13, 369.99, 392.0, 440.0, 466.16, 523.25, 587.33, 622.25, 739.99, 783.99, 880.0]

# --- chat-story sound design (music is added separately) ---
ME = [(0.4,1),(1.8,1),(4.1,0),(5.0,0),(7.0,1),(9.0,0),(10.8,1),(11.9,0),(14.6,0),(17.0,0),(19.8,1),(21.0,1),(23.2,0),(24.6,0),(27.6,1),(29.2,0)]
TYPING = [(3.0,4.1),(8.0,9.0),(22.2,23.2)]
def sweep(f0, f1, d, g=.3):
    n = int(d * SR); f = np.linspace(f0, f1, n); s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * np.sin(np.linspace(0, np.pi, n)) ** .5 * g
def sent(): return sweep(380, 980, .13, .28) + np.concatenate([np.zeros(int(.09 * SR)), ping(1568)[:int(.1 * SR)] * .5])[:int(.13 * SR)]
def recv():
    n = int(.16 * SR); t = T(n); f = 1050 - 450 * np.minimum(1, t / .05); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 28)
    return s * .38
def key(): n = int(.025 * SR); return bp_fast(rng.standard_normal(n), 2500, 7000) * np.exp(-T(n) * 220) * .22
def shutter(): a = bp_fast(rng.standard_normal(int(.05 * SR)), 1500, 8000) * np.exp(-T(int(.05 * SR)) * 80) * .5; return np.concatenate([a, np.zeros(int(.06 * SR)), a * .8])
for tt, me in ME: st(tt, sent() if me else recv(), 1, pan=-.25 if me else .25, fx=.15)
for a, b in TYPING:
    t = a
    while t < b - .1: st(t, key(), .5 + rng.random() * .4, pan=.3); t += .07 + rng.random() * .1
for tt, me in ME:
    if me:
        t = tt - 1.0
        while t < tt - .12: st(t, key(), .6 + rng.random() * .4, pan=-.3); t += .06 + rng.random() * .07
st(13.1, whoosh(.8, .4), 1); st(13.4, ping(1318.5), .5, fx=.4)
st(14.6, shutter(), 1, fx=.2); st(15.1, ping(1760), .45, fx=.4)
st(17.3, sweep(300, 1400, 1.5, .14), 1, fx=.2); st(18.8, ping(2093), .6, fx=.5)
for i in range(5): st(24.95 + i * .22, ping(1046.5 * (1.12 ** i)), .35, fx=.3)
st(28.6, bell(1568, 1.2), .7, fx=.5)
st(30.9, whoosh(.9, .45), 1)
st(31.8, impact()[:int(1.4 * SR)], .45); st(31.8, bell(880, 2.0), .6, fx=.6)
st(33.5, ping(1760), .6, fx=.4); st(35.3, recv(), 1); st(36.3, sent(), 1)
# reverb on FX bus
ir_n = int(2.2 * SR); ir = rng.standard_normal(ir_n) * np.exp(-T(ir_n) * 2.6); ir = lp_fast(ir, 6000); ir /= np.abs(ir).sum() ** .5 * 6
def conv(x, h):
    n = len(x) + len(h); F = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(h, F), F)[:len(x)]
wetL = conv(FX, ir); wetR = conv(np.roll(FX, 300), ir)
L += wetL * .5; R += wetR * .5
# gentle bus glue + fades
mix = np.stack([L, R], 1)
mix = np.tanh(mix / (np.abs(mix).max() * .7)) * .9
fade = np.ones(N); fade[-int(.25 * SR):] = np.linspace(1, 0.4, int(.25 * SR)); mix *= fade[:, None]
pcm = (mix / np.abs(mix).max() * .89 * 32767).astype(np.int16)
with wave.open('assets/score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
