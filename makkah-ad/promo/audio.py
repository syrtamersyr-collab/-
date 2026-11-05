# Original score for «خيط الضوء»: 120 BPM cinematic electronic + Hijaz oud phrase. No vocals.
import numpy as np, wave
SR = 44100; DUR = 42.0; N = int(SR * DUR)
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

# --- arrangement v2: uplifting future-pop in A major (no oud, no Hijaz) ---
BEAT = .5
def supersaw(freqs, dur, g=.05, cutoff=3200, pump=True):
    n = int(dur * SR); t = T(n); s = np.zeros(n)
    for f in freqs:
        for d in (-.012, -.006, -.002, 0, .002, .006, .012):
            ph = rng.random(); s += ((t * f * (1 + d) + ph) % 1) * 2 - 1
    s = lp_fast(s, cutoff) / (len(freqs) * 7) ** .5
    a = np.minimum(1, t / .02) * np.minimum(1, (dur - t) / .08)
    if pump: a *= .25 + .75 * np.minimum(1, ((t % BEAT) / .22)) ** 1.5
    return s * a * g
def piano(f, dur=1.6, g=.22):
    n = int(dur * SR); t = T(n)
    s = sum(np.sin(2 * np.pi * f * k * (1 + .0004 * k * k) * t) * k ** -1.3 * np.exp(-t * (1.8 + k * 1.1)) for k in range(1, 9))
    return s * np.minimum(1, t / .003) * g
def snare(g=.55):
    n = int(.3 * SR); t = T(n)
    s = bp_fast(rng.standard_normal(n), 1500, 7000) * np.exp(-t * 16) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * .8
    return s * g
def sub(f, dur, g=.36):
    n = int(dur * SR); t = T(n); s = np.sin(2 * np.pi * f * t) + .15 * np.sin(4 * np.pi * f * t)
    return s * np.minimum(1, t / .008) * np.minimum(1, (dur - t) / .04) * g
def lead(f, dur=.45, g=.16):
    n = int(dur * SR); t = T(n); vib = 1 + .004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / .2)
    s = ((t * f * vib) % 1) * 2 - 1 + .6 * np.sign(np.sin(2 * np.pi * f * .5 * t))
    return lp_fast(s, 2600) * np.minimum(1, t / .01) * np.exp(-t * 2.5) * g
CH = {'Fm': ([185.0, 220.0, 277.18], 92.50), 'D': ([146.83, 185.0, 220.0], 73.42), 'A': ([220.0, 277.18, 329.63], 110.0), 'E': ([164.81, 207.65, 246.94], 82.41)}
PROG = ['Fm', 'D', 'A', 'E']
MEL = [659.25, 554.37, 493.88, 440.0, 493.88, 554.37, 659.25, 739.99]   # hook motif
def drums(t0, t1, hats16=True, snr=True):
    b = 0; t = t0
    while t < t1 - 1e-6:
        st(t, kick(), .95)
        if snr and b % 2 == 1: st(t, snare(), 1, fx=.25)
        if hats16:
            for k in range(4): st(t + k * .125, hat(), .9 if k % 2 else .5, pan=.3 * ((-1) ** k))
            if b % 8 == 7: [st(t + .25 + k * .0625, hat(), .7, pan=.3) for k in range(4)]   # hat roll
        t += BEAT; b += 1
def section(t0, nbars, g=.05, bassline=True, piano_g=0):
    for bar in range(nbars):
        chord, root = CH[PROG[bar % 4]]; t = t0 + bar * 2
        st(t, supersaw(chord + [c * 2 for c in chord[:1]], 2.0, g), 1, fx=.25)
        if bassline:
            for k in range(4): st(t + k * .5, sub(root, .45), 1)
        if piano_g: [st(t + k * .5, piano(c * 2, 1.2, piano_g), 1, pan=.2, fx=.3) for k, c in enumerate(chord + chord[:1])]
def glitch(t, d=.15):
    n = int(d * SR); x = rng.standard_normal(n); x = np.round(x * 3) / 3; x = bp_fast(x, 800, 6000) * .35
    st(t, x, 1, pan=(rng.random() - .5))
# 0–3 hook: tense filtered pad, glitches, error beeps, reverse riser
st(0, lp_fast(supersaw([92.5, 98.0], 3.0, .06, 600, pump=False), 500), 1)
for tt in (.9, 1.0, 1.75, 1.85, 2.5, 2.6, 2.7, 2.8): glitch(tt)
eb = np.sin(2 * np.pi * 660 * T(int(.12 * SR))) * .22; st(1.2, eb); st(1.38, eb)
st(1.8, noise_swell(1.2, 200, 12000, g=.32), 1, fx=.2)
# 3–6 drop: big chord stab + impact, piano motif
st(3.0, impact(), 1.0)
st(3.0, supersaw([220.0, 277.18, 329.63, 440.0], 3.0, .07, 5000, pump=False) * np.exp(-T(int(3 * SR)) * .6), 1, fx=.4)
for i, f in enumerate([659.25, 554.37, 440.0, 554.37, 659.25, 880.0]): st(3.5 + i * .33, piano(f, 1.5, .2), 1, pan=.15, fx=.4)
# 6–30 main groove
drums(6.0, 30.0)
section(6.0, 12)
for tt in (6.2, 6.65, 7.1): st(tt, ping(1318.5), .6, fx=.4)
for rep in range(3):                     # hook melody every 8 s
    t0 = 9.0 + rep * 8
    for i, f in enumerate(MEL): st(t0 + i * .5, lead(f), 1, pan=-.1, fx=.35)
for k in range(7):                       # accent on each service change
    t0 = 9 + 3 * k
    st(t0 - .3, whoosh(.6, .35), 1, pan=.4 if k % 2 else -.4)
    st(t0, piano([880.0, 739.99, 659.25, 554.37, 659.25, 739.99, 880.0][k], 1.2, .18), 1, fx=.4)
for tt in (16.0, 16.25, 16.6): st(tt, tick(), .8)
for tt in (18.45, 18.8, 19.15): st(tt, ping(1046.5), .45, fx=.3)
st(22.2, ping(1568), .45, fx=.3)
for j in range(5): st(28.6 + j * .1, ping(1760 + j * 220), .3, fx=.4)
# 30–34 breakdown: piano + soft pad
st(29.7, noise_swell(.5, 6000, 300, rise=False, g=.22), 1)
for bar in range(2):
    chord, root = CH[PROG[bar % 4]]; t = 30.0 + bar * 2
    st(t, supersaw(chord, 2.0, .035, 1500, pump=False), 1, fx=.4)
    for k, c in enumerate(chord + [chord[1] * 2]): st(t + k * .5, piano(c * 2, 1.6, .2), 1, pan=.2, fx=.45)
st(33.0, noise_swell(1.0, 400, 12000, g=.3), 1, fx=.2)
# 34–42 final chorus + ending
st(34.0, impact(), .7)
drums(34.0, 41.0)
section(34.0, 4, g=.055)
for i, f in enumerate(MEL): st(34.0 + i * .5, lead(f), 1, pan=-.1, fx=.35)
st(35.3, ping(1760), .7, fx=.4)
st(39.1, tick(), 1.2); st(39.5, whoosh(.4, .3), 1); st(39.6, ping(2093), .6, fx=.5)
st(41.0, supersaw([220.0, 277.18, 329.63, 440.0], 1.0, .06, 4000, pump=False) * np.exp(-T(int(SR)) * 2), 1, fx=.5)
st(41.0, kick(), .8); st(41.0, piano(880.0, 1.0, .2), 1, fx=.5)
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
