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

# --- before/after sound design (music is added separately) ---
def sweep(f0, f1, d, g=.3):
    n = int(d * SR); f = np.linspace(f0, f1, n); s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return s * np.sin(np.linspace(0, np.pi, n)) ** .5 * g
def buzz(d=.35, g=.22):
    n = int(d * SR); t = T(n); s = np.sign(np.sin(2 * np.pi * 110 * t)) * .5 + np.sign(np.sin(2 * np.pi * 116 * t)) * .5
    return lp_fast(s, 1800) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03) * g
def glitch(d=.12): n = int(d * SR); x = np.round(rng.standard_normal(n) * 3) / 3; return bp_fast(x, 700, 6000) * .3
def crowd(d=2.2, g=.35):
    n = int(d * SR); s = bp_fast(rng.standard_normal(n), 300, 2500); e = np.sin(np.linspace(0, np.pi, n)) ** .7
    return s * e * g
def notif(): return ping(1318.5)[:int(.18 * SR)] + np.concatenate([np.zeros(int(.09 * SR)), ping(1760)[:int(.2 * SR)]])[:int(.18 * SR)]
st(0.3, buzz(.5, .15), 1, pan=-.2); [st(tt, glitch(), 1, pan=-.3) for tt in (.8, 1.1, 2.0)]
st(1.4, ping(1568), .6, fx=.4)
SC = [3.0, 8.5, 14.0, 19.5, 25.0]
for k, t0 in enumerate(SC):
    st(t0 - .25, whoosh(.5, .38), 1, pan=.3 if k % 2 else -.3); st(t0 + .05, ping(1046.5), .4, fx=.3)
    for j in range(4): st(t0 + .9 + j * 1.1 + rng.random() * .2, glitch(), .8, pan=-.4)
    if k != 4: st(t0 + .7, buzz(.3), 1, pan=-.35)
st(3.3, sweep(500, 1200, .25, .2), 1, pan=.3, fx=.3); st(3.6, ping(2093), .4, fx=.4)          # call connects
st(9.0, crowd(), 1, pan=.3, fx=.3); st(10.5, crowd(1.4, .45), 1, pan=.3, fx=.3)                 # goal!
st(15.8, ping(1568), .6, fx=.4); st(16.0, bell(2093, 1.0), .5, fx=.5)                           # download done
for i in range(3): st(20.0 + i * .6, notif(), .7, pan=.3, fx=.3)                                # orders
st(25.2, sweep(400, 60, .7, .3), 1, pan=-.3)                                                    # power down (top)
st(25.9, sweep(80, 700, .6, .25), 1, pan=.3, fx=.2); st(26.3, ping(1318.5), .5, fx=.4)          # power up (bottom)
st(30.4, whoosh(.9, .5), 1); st(31.0, impact()[:int(1.6 * SR)], .55); st(31.0, bell(880, 2.0), .5, fx=.6)
for i in range(5): st(33.8 + i * .12, ping(1046.5 * (1.12 ** i)), .3, fx=.3)
st(34.8, ping(1760), .6, fx=.4); st(37.2, ping(2093), .5, fx=.4)
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
