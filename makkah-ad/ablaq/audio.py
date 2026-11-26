# «الأبلق» — emotional orchestral score in maqam Nahawand (D), 72 BPM, 11 bars = 36.67s, locked to the film's acts.
import mido, subprocess, numpy as np, wave
SR = 44100; DUR = 36.67; N = int(SR * DUR); TPB = 480; BPM = 72; B = 60 / BPM; BAR = 4 * B; ev = []
bt = lambda s: s * BPM / 60
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v, t=0): ev.append((int(bt(t) * TPB), mido.Message('control_change', channel=ch, control=c, value=int(max(0, min(127, v))))))
def note(ch, p, t, d, v):
    if t >= DUR or v <= 0: return
    ev.append((int(bt(t) * TPB), mido.Message('note_on', channel=ch, note=int(p), velocity=max(1, min(127, int(v))))))
    ev.append((int(bt(min(t + d, DUR)) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))
STR, CEL, CHO, HRP, PNO, HRN, TIM, CB, BRS, VLN, DR = 0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 9
for ch, p in ((STR, 49), (CEL, 42), (CHO, 52), (HRP, 46), (PNO, 0), (HRN, 60), (TIM, 47), (CB, 43), (BRS, 61), (VLN, 40)): prog(ch, p)
for ch, v in ((STR, 92), (CEL, 104), (CHO, 70), (HRP, 92), (PNO, 84), (HRN, 92), (TIM, 112), (CB, 100), (BRS, 84), (VLN, 96), (DR, 90)): cc(ch, 7, v)
for ch in range(11): cc(ch, 91, 75 if ch not in (DR, TIM) else 40); cc(ch, 93, 30)
for ch, pan in ((STR, 50), (CEL, 70), (CHO, 64), (HRP, 30), (PNO, 84), (HRN, 44), (CB, 70), (VLN, 40)): cc(ch, 10, pan)
# swells via expression (CC11)
def swell(ch, t0, t1, a, b, steps=24):
    for k in range(steps + 1): cc(ch, 11, a + (b - a) * k / steps, t0 + (t1 - t0) * k / steps)
# harmony per bar (D nahawand): i  VI  iv  V | i  VI  III  V ...
Dm, Bb, Gm, A7, F, C, Eb = [38, 50, 53, 57], [34, 46, 50, 53], [43, 50, 55, 58], [45, 49, 52, 55], [41, 48, 53, 57], [36, 48, 52, 55], [39, 46, 51, 55]
PLAN = [Dm, Dm, Bb, Gm, Dm, A7, Bb, F, Gm, A7, Dm]
DMAJ = [38, 50, 54, 57]
def pad(ch, notes, t, d, v, up=12):
    for p in notes[1:]: note(ch, p + up, t, d, v)
# ---- bar 0-1 (0-6.67): darkness. low D drone, sparse piano, harp ripples when the vein ignites
note(CB, 26, 0, 2 * BAR, 90); note(CB, 38, 0, 2 * BAR, 60); swell(STR, 0, 2 * BAR, 30, 80)
pad(STR, Dm, 0, 2 * BAR, 60, 0)
for t, p in ((0.4, 74), (1.25, 69), (2.1, 70), (3.33, 74), (4.2, 77), (5.0, 76), (5.85, 74)): note(PNO, p, t, 1.6, 62)
for k in range(10): note(HRP, [62, 65, 69, 74, 77, 81, 86, 89, 93, 98][k], 1.0 + k * .09, 1.5, 54 + k * 3)   # ignition
# ---- bar 2-3 (6.67-13.33): cello theme (the "Homs" melody); strings answer; build toward the wall
CELLO = [(62, 1.5), (64, .5), (65, 1), (67, 1), (69, 2), (70, 1), (69, 1), (67, 1.5), (65, .5), (64, 1), (65, 1), (62, 4)]
t = 2 * BAR
for p, l in CELLO:
    note(CEL, p - 12, t, l * B * .98, 92); t += l * B
for j, c in enumerate([Bb, Gm]): pad(STR, c, (2 + j) * BAR, BAR, 70, 0); note(CB, c[0], (2 + j) * BAR, BAR, 92)
for k in range(16): note(HRP, [50, 57, 62, 65][k % 4] + (12 if k % 8 >= 4 else 0), 2 * BAR + k * B / 2, B, 58)
swell(STR, 2 * BAR, 4 * BAR, 70, 112)
for k in range(8): note(TIM, 38, 4 * BAR - .55 + k * .07, .06, 40 + k * 9)                 # roll into act 3
# ---- bar 4-5 (13.33-20): the clock rises. choir + horns; theme on violins an octave up
for j, c in enumerate([Dm, A7]): pad(STR, c, (4 + j) * BAR, BAR, 84, 0); pad(CHO, c, (4 + j) * BAR, BAR, 78, 12); note(CB, c[0], (4 + j) * BAR, BAR, 100)
t = 4 * BAR
for p, l in CELLO:
    if t >= 6 * BAR: break
    note(VLN, p + 12, t, l * B * .98, 96); note(HRN, p, t, l * B * .98, 70); t += l * B
note(TIM, 38, 4 * BAR, .5, 110); note(DR, 49, 4 * BAR, 2.5, 70)
note(TIM, 45, 5 * BAR + 2 * B, .4, 104)                                          # the light rings leave the clock
for k in range(12): note(HRP, 74 + [0, 3, 7, 12][k % 4] + (k // 4) * 2, 5 * BAR + 2 * B + k * .08, 1.2, 60)
# ---- bar 6-8 (20-30): services. pulsing string ostinato (8ths), impacts on each emblem
for b, c in zip(range(6, 9), [Bb, F, Gm]):
    t0 = b * BAR
    for k in range(8): note(STR, [c[1], c[2], c[3], c[2]][k % 4] + 12, t0 + k * B / 2, B / 2 * .8, 74 + (10 if k % 2 == 0 else 0))
    pad(CHO, c, t0, BAR, 62, 12); note(CB, c[0], t0, BAR, 104); note(CB, c[0] - 12, t0, BAR, 80)
    note(TIM, c[0] + 12 if c[0] < 40 else c[0], t0, .5, 116); note(DR, 49, t0, 2, 64)
    melody = {6: [(74, 1), (72, 1), (70, 2)], 7: [(72, 1), (74, 1), (77, 2)], 8: [(79, 1), (77, 1), (74, 2)]}[b]
    t = t0
    for p, l in melody: note(VLN, p, t, l * B * .96, 92); note(CEL, p - 24, t, l * B * .96, 70); t += l * B
# bar 9 (30-33.33): gathering (A7 dominant, rising tension)
pad(STR, A7, 9 * BAR, BAR, 96, 0); pad(STR, A7, 9 * BAR, BAR, 84, 12); pad(CHO, A7, 9 * BAR, BAR, 86, 12); note(CB, 33, 9 * BAR, BAR, 108)
swell(STR, 9 * BAR, 10 * BAR - .1, 70, 120)
for k in range(16): note(TIM, 45, 9 * BAR + 2 * B + k * B / 8, .05, 50 + k * 4)
for k in range(8): note(VLN, [69, 70, 72, 73, 74, 76, 77, 79][k], 9 * BAR + 2 * B + k * B / 4, B / 4, 90 + k * 3)
# bar 10 (33.33-36.67): resolution in D MAJOR (Picardy) on the engraved logo — hope
note(TIM, 38, 10 * BAR, .8, 127); note(DR, 49, 10 * BAR, 3, 100); note(DR, 52, 10 * BAR, 3, 50)
for p in (26, 38, 50): note(CB, p, 10 * BAR, BAR, 110)
for p in DMAJ[1:]: note(STR, p, 10 * BAR, BAR, 100); note(STR, p + 12, 10 * BAR, BAR, 92); note(CHO, p + 12, 10 * BAR, BAR, 92); note(BRS, p, 10 * BAR, 1.6, 84); note(HRN, p, 10 * BAR, BAR, 84)
note(VLN, 78, 10 * BAR, 1.2, 100); note(VLN, 81, 10 * BAR + 1.2, 2.0, 96)
for k in range(14): note(HRP, [62, 66, 69, 74, 78, 81, 86][k % 7] + (12 if k >= 7 else 0), 10 * BAR + .4 + k * .1, 2, 64)
note(PNO, 86, 10 * BAR + 2.2, 1.2, 60); note(PNO, 90, 10 * BAR + 2.5, 1.0, 54)
swell(STR, 10 * BAR + 1.4, DUR, 120, 40)

ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=max(0, tt - last))); last = max(last, tt)
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.55', '-r', str(SR), '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------------- sound design ----------------
rng = np.random.default_rng(11); T = lambda n: np.arange(n) / SR; fx = np.zeros(N)
def put(t, s, g=1): i = int(t * SR); j = min(N, i + len(s)); fx[i:j] += s[:j - i] * g
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
def boom(l=3.0, f0=48): n = int(l * SR); tt = T(n); return np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-tt * .7) + 22) / SR) * np.exp(-tt * 1.6) * .9
def shimmer(l=2.2, f=2400):
    n = int(l * SR); tt = T(n); s = sum(np.sin(2 * np.pi * (f * m) * tt + m) * np.exp(-tt * (2 + m)) for m in (1, 1.5, 2.01, 2.76)); return s * np.r_[np.linspace(0, 1, int(.02 * SR)), np.ones(n - int(.02 * SR))] * .08
def stone(l=.18): n = int(l * SR); x = rng.standard_normal(n); x = lp(x, 6) - lp(x, 60); return x * np.exp(-T(n) * 30) * .55
def grind(l=1.6): n = int(l * SR); x = lp(rng.standard_normal(n), 12) * (0.6 + .4 * np.sin(2 * np.pi * 7 * T(n)) ** 2); return x * np.sin(np.linspace(0, np.pi, n)) * .22
def riser(l=2.0): n = int(l * SR); x = rng.standard_normal(n); k = np.linspace(80, 4, n).astype(int); y = np.array([0.0] * n); c = np.cumsum(x); y = (c - np.r_[np.zeros(80), c[:-80]]) / 80; return (x * .3 + y) * np.linspace(0, 1, n) ** 3 * .35
def whoosh(l=1.2): n = int(l * SR); x = lp(rng.standard_normal(n), 25); return x * np.sin(np.linspace(0, np.pi, n)) ** 2 * .6
put(0.0, boom(4.0, 40), .9)
put(1.0, shimmer(3.5, 1800), 1.0)                                  # the vein ignites
put(7.6, grind(4.0), .9)
for k in range(46): put(8.6 + rng.random() * 3.0, stone(), .25 + rng.random() * .35)     # stones landing in the wall
put(11.2, shimmer(2.5, 2200), .9)
put(13.33, boom(3.0, 46), .7); put(14.6, grind(3.2), .7)
for k in range(5): put(17.4 + k * .45, shimmer(1.6, 1400 + k * 200), .6)                 # rings of light
for t0 in (20.0, 23.33, 26.67): put(t0 - 1.0, whoosh(1.2), .8); put(t0, boom(1.6, 60), .55); put(t0 + .3, shimmer(1.8, 2600), .5)
for k in range(30): put(20.2 + rng.random() * 9, stone(.12), .15 + rng.random() * .2)
put(28.33, riser(1.6), 1.0)
put(30.0, whoosh(1.6), .8)
for k in range(40): put(30.4 + rng.random() * 1.8, stone(), .2 + rng.random() * .3)
put(31.6, shimmer(3.0, 1600), 1.0)                                 # logo engraving
put(33.33, boom(3.3, 38), 1.0)
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'assets/music.wav', '-i', 'assets/fx.wav', '-filter_complex',
  "[0:a]atrim=0:36.67,aecho=0.8:0.6:60|110:0.18|0.12[m];[1:a]pan=stereo|c0=c0|c1=c0,aecho=0.8:0.7:90:0.25[f];"
  "[m][f]amix=inputs=2:normalize=0,acompressor=threshold=-20dB:ratio=2:attack=25:release=250:makeup=2,afade=t=in:d=0.3,afade=t=out:st=35.4:d=1.25,loudnorm=I=-14:TP=-1:LRA=10", '-ar', '48000', 'assets/mix.wav'], check=True)
print('ok')
