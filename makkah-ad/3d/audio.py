# Original score for «خيط الضوء»: 120 BPM cinematic electronic + Hijaz oud phrase. No vocals.
import numpy as np, wave
SR = 44100; DUR = 36.0; N = int(SR * DUR)
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

# --- 3D diorama sound design: cinematic ambience + effects (music is added separately) ---
def sweep(f0, f1, d, g=.3):
    n = int(d * SR); f = np.linspace(f0, f1, n); s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * np.sin(np.linspace(0, np.pi, n)) ** .5 * g
def drone(d, f=55, g=.1):
    n = int(d * SR); t = T(n); s = np.sin(2 * np.pi * f * t) + .6 * np.sin(2 * np.pi * f * 1.5 * t + np.sin(t * .7)) + .3 * np.sin(2 * np.pi * f * 2.01 * t)
    return s * np.minimum(1, t / 1.5) * np.minimum(1, (d - t) / 1.5) * g
def air(d, g=.05): n = int(d * SR); return bp_fast(rng.standard_normal(n), 200, 1200) * np.minimum(1, T(n) / 2) * np.minimum(1, (d - T(n)) / 1) * g
def zip_(g=.22): return sweep(500, 2600, .22, g)
for k in range(8): st(.5 + k * .35, ping(2637)[:int(.08 * SR)], .25, pan=.2)          # antenna LED
st(3.6, whoosh(1.6, .45), 1, pan=-.3)                                                   # pull back
for k in range(12): st(4.6 + k * 1.8, sweep(180, 90, 1.2, .12), 1, fx=.4)               # tower pulses
for i in range(19): st(5.2 + i * .27, zip_(), 1, pan=.5 * ((-1) ** i), fx=.3); st(5.75 + i * .27, ping(880 * (1.06 ** (i % 12))), .35, fx=.4)
st(10.6, whoosh(1.4, .45), 1, pan=.3)                                                   # descend
for k in range(6): st(12.0 + k * .6, ping(1976)[:int(.07 * SR)], .35, pan=.25)          # camera scan beeps
st(11.4, sweep(300, 420, 1.0, .08), 1)
st(16.2, whoosh(1.4, .45), 1, pan=-.3)
st(17.6, bell(1568, 2.0), .5, fx=.6); st(18.0, bell(2093, 2.0), .35, fx=.6)             # solar glint
st(21.2, whoosh(2.0, .5), 1)                                                            # rise
st(22.3, impact()[:int(1.5 * SR)], .45); st(22.3, bell(659.25, 3), .5, fx=.6)
st(26.6, noise_swell(2.2, 200, 12000, g=.4), 1, fx=.2); st(26.8, sweep(120, 900, 2.0, .16), 1)
st(28.8, impact(), 1.0); st(28.8, bell(587.33, 3.5), .7, fx=.7); st(28.8, bell(880, 3.5), .45, fx=.7)
for k in range(5): st(29.0 + k * .32 * (1 + k * .25), whoosh(.35, .3 - k * .04), 1, pan=.4 * ((-1) ** k))   # medallion spin
st(31.6, ping(1760), .7, fx=.5); st(32.4, ping(1318.5), .4, fx=.4); st(33.2, ping(2093), .5, fx=.5)
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
