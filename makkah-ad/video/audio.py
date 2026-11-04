# Original score for «خيط الضوء»: 120 BPM cinematic electronic + Hijaz oud phrase. No vocals.
import numpy as np, wave
SR = 44100; DUR = 35.0; N = int(SR * DUR)
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

# --- arrangement ---
BEAT = .5
# 0–5: frozen room
st(0, pad([73.42, 110.0], 5.2, .06)); st(0, np.sin(2 * np.pi * 55 * T(int(5 * SR))) * np.minimum(1, T(int(5 * SR)) / .5) * .12)
for f in (2093, 2637, 3136): st(0.0, bell(f, 3), .7, pan=.3, fx=.6)
for i, f in enumerate([440.0, 392.0, 369.99, 311.13, 293.66]):
    st(2.0 + i * .25, oud(f, 1.8), 1.0, pan=-.15, fx=.35)
st(3.25, ping(1760), 1, fx=.5)
st(4.0, noise_swell(1.0, 300, 9000), 1, fx=.2)
st(4.0, np.sin(2 * np.pi * np.cumsum(np.linspace(200, 900, int(SR))) / SR) * np.linspace(0, .12, int(SR)))
st(5.0, impact(), .55); st(5.0, whoosh(.9), 1, pan=.4)

# 5–25 groove (bars of 2s), chords in Hijaz: D – Eb – C m – D
prog = [([D3, Fs3, A3], 73.42), ([Eb3, G3, Bb3], 77.78), ([130.81, Eb3, G3], 65.41), ([D3, Fs3, A3], 73.42)]
def groove(t0, t1, full=True):
    b = 0; t = t0
    while t < t1 - 1e-6:
        st(t, kick(), .9)
        if full:
            if b % 2 == 1: st(t, clap(), .8, fx=.2)
            st(t + .25, hat(), 1, pan=.35); st(t, hat(), .6, pan=-.35)
            if b % 4 == 3: st(t + .25, hat(True), .8, pan=.2)
        t += BEAT; b += 1
groove(5.0, 15.0)
for bar in range(5):
    chord, root = prog[bar % 4]; t = 5.0 + bar * 2
    st(t, pad(chord, 2.0, .05), 1, fx=.25)
    for k in range(8): st(t + k * .25, bass(root, .22), 1)
# 8–15 arp of plucks over the flyover
for k in range(int(7 / .125)):
    t = 8.0 + k * .125; chord, _ = prog[int((t - 5) // 2) % 4]
    f = (chord + [c * 2 for c in chord])[k % 6] * 2
    st(t, pluck(f, .3), .55, pan=.4 * np.sin(k), fx=.3)
for t in (7.55, 14.55): st(t, whoosh(.8, .45), 1, pan=-.3)
for k in range(5): st(10.0 + k * .5, tick(), .9, pan=-.2)   # clock ticks… then stop
st(12.2, bell(1318.5, 1.5), .5, fx=.5)
# 15–25 coverage: lighter beat, a rising note for every node
st(15.0, impact(), .35)
groove(16.0, 24.0)
for bar in range(5):
    chord, root = prog[bar % 4]; t = 15.0 + bar * 2
    st(t, pad(chord, 2.0, .055), 1, fx=.3)
    if t >= 16: [st(t + k * .5, bass(root, .45), 1) for k in range(4)]
for i in range(8): st(17.0 + i * .6, pluck(HIJ[i], .9), .9, pan=.3 * ((-1) ** i), fx=.45)
for i in range(14): st(21.6 + i * .2, bell(HIJ[(i + 4) % 12] * 2, .8), .55, pan=.5 * ((-1) ** i), fx=.5)
st(24.0, noise_swell(1.0, 400, 10000), 1.2, fx=.2)
# 25–30 build → crescent hit at 27.0 → hook
st(25.0, whoosh(1.0, .4), 1)
st(25.0, pad([D3, A3, D4], 2.0, .07), 1, fx=.35)
for k in range(8): st(25.0 + k * .25, kick(.35 + k * .05), 1)          # snare-roll style build
st(26.0, noise_swell(1.0, 500, 12000, g=.32), 1, fx=.2)
st(27.0, impact(), 1.0); st(27.0, bell(587.33, 3), .8, fx=.6); st(27.0, bell(880, 3), .5, fx=.6)
groove(27.0, 30.0)
for bar, (chord, root) in enumerate([prog[0], prog[1]]):
    t = 27.0 + bar * 1.5
    st(t, pad(chord, 1.6, .06), 1, fx=.3); [st(t + k * .25, bass(root, .22), 1) for k in range(6)]
# 30–35 calm outro: oud reprise, numbers on screen
st(29.8, whoosh(.6, .35), 1, pan=.3)
st(30.0, pad([D3, Fs3, A3, D4], 5.0, .06), 1, fx=.4)
for i, f in enumerate([293.66, 311.13, 369.99, 392.0, 440.0]): st(30.4 + i * .25, oud(f, 1.8), 1.0, pan=.15, fx=.35)
for k in range(8): st(31.0 + k * .5, kick(.35), 1)
st(31.45, ping(1318.5), .8, fx=.4); st(31.65, ping(1760), .8, fx=.4)
st(34.35, noise_swell(.65, 400, 6000, g=.2), 1)

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
