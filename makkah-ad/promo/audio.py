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

# --- arrangement v3: driving tech / electro, E minor, 120 BPM ---
BEAT = .5
MUS = np.zeros((N, 2))        # melodic bus, gets side-chained to the kick
def mus(t, sig, g=1.0, pan=0.0, fx=0.0):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N: return
    MUS[i:j, 0] += sig[:j - i] * g * (1 - pan); MUS[i:j, 1] += sig[:j - i] * g * (1 + pan)
    if fx: put(FX, t, sig, g * fx)
def sawn(f, n, det=(0,)):
    t = T(n); return sum(((t * f * (1 + d) + .37 * k) % 1) * 2 - 1 for k, d in enumerate(det)) / len(det) ** .5
def kick2(g=1.0):
    n = int(.4 * SR); t = T(n); f = 48 + 140 * np.exp(-t * 35)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    click = hp_fast(rng.standard_normal(n), 3000) * np.exp(-t * 300) * .5
    return np.tanh((body + click) * 2.2) * .8 * g
def clap2(g=1.0):
    n = int(.35 * SR); t = T(n); s = bp_fast(rng.standard_normal(n), 1000, 5000)
    e = np.exp(-t * 14); bursts = np.ones(n); bursts[:int(.03 * SR)] = (np.sin(np.linspace(0, 3 * np.pi, int(.03 * SR))) > 0) * 1.0
    sn = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 35) * .6
    return (s * e * bursts + sn) * .55 * g
def ohat():
    n = int(.22 * SR); return hp_fast(rng.standard_normal(n), 8000) * np.exp(-T(n) * 16) * .22
def rollbass(f, dur, cutoff=900):
    n = int(dur * SR); t = T(n); s = sawn(f, n, (-.004, .004)) + .6 * np.sin(2 * np.pi * f / 2 * t)
    s = lp_fast(s, cutoff) * np.exp(-t * 4)
    return np.tanh(s * 1.8) * np.minimum(1, t / .004) * np.minimum(1, (dur - t) / .01) * .32
def arpnote(f, dur, cutoff):
    n = int(dur * SR); t = T(n); s = sawn(f, n, (-.006, 0, .006))
    s = lp_fast(s, cutoff) * np.exp(-t * 14)
    return s * np.minimum(1, t / .002) * .16
def lead2(f, dur, g=.14):
    n = int(dur * SR); t = T(n); s = sawn(f, n, (-.01, -.004, .004, .01)) + .5 * sawn(f * 2, n, (0,))
    s = lp_fast(s, 3800) * np.minimum(1, t / .01) * np.minimum(1, (dur - t) / .05) * (0.75 + .25 * np.exp(-t * 6))
    return s * g
def padw(freqs, dur, g=.05, cutoff=1800):
    n = int(dur * SR); s = sum(sawn(f, n, (-.01, -.005, 0, .005, .01)) for f in freqs)
    s = lp_fast(s, cutoff); t = T(n); return s * np.minimum(1, t / .3) * np.minimum(1, (dur - t) / .3) * g
def riser(dur, g=.3):
    n = int(dur * SR); t = T(n); sweep = np.sin(2 * np.pi * np.cumsum(np.linspace(150, 1600, n)) / SR) * .25
    return (noise_swell(dur, 300, 12000, g=1) * .9 + sweep * np.linspace(0, 1, n) ** 2) * g
CH = {'Em': [164.81, 196.0, 246.94], 'C': [130.81, 164.81, 196.0], 'G': [196.0, 246.94, 293.66], 'D': [146.83, 185.0, 220.0]}
ROOT = {'Em': 41.20, 'C': 32.70, 'G': 49.0, 'D': 36.71}
PROG = ['Em', 'C', 'G', 'D']
RIFF = [659.25, 0, 783.99, 659.25, 987.77, 0, 880.0, 783.99, 739.99, 0, 659.25, 587.33, 659.25, 0, 0, 0]  # 16ths per 2 bars? (per bar of 4 beats = 8 eighths)
def drums2(t0, t1, level=2):
    b = 0; t = t0
    while t < t1 - 1e-6:
        st(t, kick2(), 1)
        if level >= 1 and b % 2 == 1: st(t, clap2(), 1, fx=.2)
        if level >= 1: st(t + .25, ohat(), 1, pan=.25)
        if level >= 2:
            for k in range(4): st(t + k * .125, hat(), .7 if k % 2 else .35, pan=-.3)
        t += BEAT; b += 1
def bassline(t0, t1, cutoff=900):
    t = t0; b = 0
    while t < t1 - 1e-6:
        root = ROOT[PROG[int((t - t0) // 2) % 4]] * 2
        for k in (1, 2, 3): mus(t + k * .125, rollbass(root, .12, cutoff), 1)   # rolling off-beat 16ths
        t += BEAT; b += 1
def arp(t0, t1, c0, c1):
    k = 0; t = t0
    while t < t1 - 1e-6:
        ch = CH[PROG[int((t - 6) // 2) % 4]]; notes = [ch[0] * 2, ch[1] * 2, ch[2] * 2, ch[1] * 4]
        cut = c0 * (c1 / c0) ** ((t - t0) / max(.01, t1 - t0))
        mus(t, arpnote(notes[k % 4], .14, cut), 1, pan=.45 * (1 if k % 2 else -1), fx=.25)
        t += .125; k += 1
def pads(t0, nbars, g=.045):
    for bar in range(nbars): mus(t0 + bar * 2, padw(CH[PROG[bar % 4]], 2.0, g), 1, fx=.3)
def riff(t0, nbars=2, g=.14):
    for bar in range(nbars):
        for i, f in enumerate(RIFF[:8] if bar % 2 == 0 else RIFF[8:]):
            if f: mus(t0 + bar * 2 + i * .25, lead2(f, .23, g), 1, pan=.1, fx=.3)
def glitch(t, d=.15):
    n = int(d * SR); x = np.round(rng.standard_normal(n) * 3) / 3; st(t, bp_fast(x, 800, 6000) * .35, 1, pan=(rng.random() - .5))

# 0–3 intro: filtered arp builds under the glitches, riser into the drop
arp(0.0, 3.0, 300, 2500)
mus(0.0, padw(CH['Em'], 3.0, .03, 700), 1)
for tt in (.9, 1.0, 1.75, 1.85, 2.5, 2.6, 2.7, 2.8): glitch(tt)
eb = np.sin(2 * np.pi * 660 * T(int(.12 * SR))) * .2; st(1.2, eb); st(1.38, eb)
st(1.5, riser(1.5), 1, fx=.2)
for k in range(8): st(2.0 + k * .125, clap2(.25 + k * .08), 1)          # snare roll
# 3 DROP
st(3.0, impact(), 1.0)
drums2(3.0, 6.0, 1); bassline(3.0, 6.0, 1400); arp(3.0, 6.0, 3000, 3000); pads(3.0, 2, .05)
mus(3.0, lead2(987.77, 1.0, .12), 1, fx=.5)
# 6–9 values
drums2(6.0, 9.0, 2); bassline(6.0, 9.0, 1100); pads(6.0, 2)
for tt in (6.2, 6.65, 7.1): st(tt, ping(1318.5), .55, fx=.4)
# 9–30 services: full drive, riff from 15s, extra energy from 21s
drums2(9.0, 30.0, 2); bassline(9.0, 30.0, 1300)
arp(9.0, 21.0, 1200, 4500); arp(21.0, 30.0, 4500, 6000)
pads(9.0, 11)
for k in range(3): riff(15.0 + k * 4, 2)
riff(27.0, 1)
for k in range(7):
    t0 = 9 + 3 * k
    st(t0 - .5, riser(.5, .18), 1); st(t0, impact()[:int(.6 * SR)], .35)
for tt in (16.0, 16.25, 16.6): st(tt, tick(), .8)
for tt in (18.45, 18.8, 19.15): st(tt, ping(1046.5), .4, fx=.3)
st(22.2, ping(1568), .4, fx=.3)
for j in range(5): st(28.6 + j * .1, ping(1760 + j * 220), .28, fx=.4)
# 30–34 breakdown: no kick, filtered arp + wide pad, riser
pads(30.0, 2, .06); arp(30.0, 34.0, 600, 3500)
st(32.0, riser(2.0, .35), 1, fx=.2)
for k in range(16): st(33.0 + k * .0625, clap2(.15 + k * .04), 1)
# 34–41 final drop
st(34.0, impact(), 1.0)
drums2(34.0, 41.0, 2); bassline(34.0, 41.0, 1500); arp(34.0, 41.0, 5000, 5000); pads(34.0, 4, .05)
riff(34.0, 2); riff(38.0, 1)
st(35.3, ping(1760), .6, fx=.4)
st(39.1, tick(), 1.2); st(39.6, ping(2093), .5, fx=.5)
# 41 ending hit
st(41.0, impact(), .8); mus(41.0, padw(CH['Em'] + [329.63], 1.0, .07, 4000) * np.exp(-T(int(SR)) * 2.5), 1, fx=.6)

# side-chain the melodic bus to the kick grid wherever drums play
sc = np.ones(N); t_ = T(N)
for a, b in ((3, 30), (34, 41)):
    i0, i1 = int(a * SR), int(b * SR); ph = (t_[i0:i1] - a) % BEAT
    sc[i0:i1] = .25 + .75 * np.minimum(1, ph / .18) ** 1.4
MUS *= sc[:, None]
MUS[int(30 * SR):int(34 * SR)] *= 2.4   # keep the breakdown present
MUS[0:int(3 * SR)] *= 1.8
L += MUS[:, 0]; R += MUS[:, 1]
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
