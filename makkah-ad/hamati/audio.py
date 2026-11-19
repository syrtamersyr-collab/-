# «حماتي والنت» — v3 score: one orchestral comedy theme («لحن الحماية») in variations, locked to a 120 BPM grid.
# Every cut / gag lands on a beat (the film is time-warped to the same grid in index.html). Output: assets/mix.wav
import mido, subprocess, numpy as np, wave
SR = 44100; DUR = 34.0; N = int(SR * DUR); TPB = 480; BPM = 120; B = 60 / BPM; ev = []
bt = lambda s: s * BPM / 60
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v, t=0): ev.append((int(bt(t) * TPB), mido.Message('control_change', channel=ch, control=c, value=int(v))))
def note(ch, p, t, d, v):
    if t >= DUR or v <= 0: return
    ev.append((int(bt(t) * TPB), mido.Message('note_on', channel=ch, note=int(p), velocity=max(1, min(127, int(v))))))
    ev.append((int(bt(t + d) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))
STR, PIZ, FL, CL, BSN, HRN, BRS, GLK, TIM, HRP, CB, DR = 0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 9
for ch, p in ((STR, 48), (PIZ, 45), (FL, 73), (CL, 71), (BSN, 70), (HRN, 60), (BRS, 61), (GLK, 9), (TIM, 47), (HRP, 46), (CB, 43)): prog(ch, p)
for ch, v in ((STR, 88), (PIZ, 104), (FL, 96), (CL, 92), (BSN, 104), (HRN, 96), (BRS, 98), (GLK, 88), (TIM, 112), (HRP, 92), (CB, 100), (DR, 96)): cc(ch, 7, v)
for ch in range(12):
    cc(ch, 91, 55 if ch not in (DR, TIM) else 30)
    cc(ch, 10, {STR: 44, PIZ: 76, FL: 84, CL: 50, BSN: 58, HRN: 40, BRS: 64, GLK: 88, HRP: 30, CB: 64}.get(ch, 64))
# the theme (C major), 8 beats: (pitch, beats)
THEME = [(67, .5), (72, .5), (76, .5), (74, .5), (72, 1), (69, .5), (67, .5), (76, .5), (77, .5), (76, .5), (74, .5), (72, 2)]
def play(ch, t0, v, transp=0, stretch=1.0, stac=.85, until=99, vel_acc=True):
    t = t0
    for i, (p, l) in enumerate(THEME):
        if t >= until: break
        note(ch, p + transp, t, l * B * stretch * stac, v + (8 if vel_acc and i % 2 == 0 else 0)); t += l * B * stretch
    return t
def chord(ch, ps, t, d, v):
    for p in ps: note(ch, p, t, d, v)
I, IV, V, vi, ii = [48, 60, 64, 67], [53, 60, 65, 69], [55, 59, 62, 67], [57, 60, 64, 69], [50, 57, 62, 65]
# ---- 0.0-1.5 opening: harp gliss, theme head on flute, button on the title cut
for k in range(12): note(HRP, [60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 88][k], .05 + k * .03, .6, 70 + k * 3)
for i, (p, l) in enumerate(THEME[:4]): note(FL, p + 12, .5 + i * .25, .22, 100)
chord(BRS, [60, 64, 67, 72], 1.5, .35, 112); chord(STR, I, 1.5, .4, 90); note(TIM, 48, 1.5, .3, 110); note(DR, 49, 1.5, .8, 80)
# ---- 1.5-3.5 the call: sneaky pizzicato theme + bassoon, crescendo to the sneeze
play(PIZ, 1.5, 70, stac=.3, until=3.5)
for k in range(4): note(BSN, [36, 43, 36, 43][k], 1.5 + k * B, B * .4, 96)
for k in range(4): note(BSN, [41, 43, 44, 46][k], 2.5 + k * .25, .2, 90 + k * 8)     # "aaa... aaa..." rising
for k in range(8): note(STR, 67 + k, 2.5 + k * .125, .12, 50 + k * 8)            # strings creeping up to the sneeze
note(CL, 84, 3.25, .2, 110)
# ---- 3.5 FREEZE: total silence (fx only) until 4.5
# ---- 4.5 shock: dissonant tutti + timpani "dun-dun" into the mother's line at 5.0
chord(BRS, [49, 55, 61, 64], 4.5, .25, 122); chord(STR, [37, 49, 55, 61], 4.5, .3, 110); note(TIM, 41, 4.5, .2, 127)
note(TIM, 41, 4.75, .2, 115); note(DR, 49, 4.5, .8, 100)
# ---- 5.0-10.5 gossip: pizzicato + bassoon theme, light percussion, accents on each line (7.5 bride, 9.0 mother)
for k in range(11):
    t = 5.0 + k * B
    note(CB, [36, 43, 41, 43, 36, 43, 45, 43, 41, 43, 43][k], t, B * .5, 92)
    note(DR, 42, t, .05, 46); note(DR, 37, t + B / 2, .05, 40 if k % 2 else 0)
for k in range(11, 22): t = 5.0 + k * B; note(CB, [41, 43, 36, 43, 45, 43, 41, 43, 43, 47, 48][k - 11], t, B * .5, 92); note(DR, 42, t, .05, 46)
play(BSN, 5.0, 84, transp=-24, stac=.45)                      # theme in the bassoon (the mother)
for k in range(8): chord(PIZ, [64, 67, 72] if k < 4 else [65, 69, 72], 5.0 + k * B + B / 2, .12, 60)
play(CL, 9.0, 82, transp=-12, stac=.55, until=10.5)               # clarinet answers (the son's call to action)
note(GLK, 88, 7.5, .3, 90); note(GLK, 84, 9.0, .3, 90)
for k in range(8): note(STR, 60 + [0, 2, 4, 5, 7, 9, 11, 12][k], 10.0 + k * .0625, .07, 70 + k * 6)   # run into the cut
# ---- 10.5-16.5 chase: driving strings, horns on the theme, snare on 2&4; hits at 11.5, 13.0, 15.0
for k in range(int(6.0 / (B / 4))):
    t = 10.5 + k * B / 4
    note(STR, [48, 55, 60, 55][k % 4] + (5 if 13.0 <= t < 15.0 else 0) + (7 if t >= 15.0 else 0), t, B / 4 * .8, 78)
for k in range(12):
    t = 10.5 + k * B; note(DR, 36, t, .1, 100 if k % 2 == 0 else 0); note(DR, 38, t, .1, 92 if k % 2 else 0); note(DR, 42, t + B / 2, .05, 62)
    note(CB, [36, 36, 43, 43, 41, 41, 43, 43, 36, 36, 43, 43][k], t, B * .8, 100)
play(HRN, 10.5, 96, transp=-12, stretch=.75, stac=.8, until=16.5)
play(FL, 13.0, 90, transp=12, stretch=.5, stac=.6, until=16.5)
play(FL, 15.0, 92, transp=17, stretch=.5, stac=.6, until=16.5)
for t in (11.5, 13.0, 15.0): chord(BRS, [60, 64, 67], t, .15, 110); note(TIM, 43, t, .15, 110)
for k in range(8): note(TIM, 43, 16.0 + k * .0625, .06, 70 + k * 7)       # timpani roll into the rooftop
# ---- 16.5-20.5 rooftop: majestic theme (half-time) in horns + strings, stamp at 18.5
play(HRN, 16.5, 104, transp=-12, stretch=1.0, stac=.95, until=20.5)
for j, c in enumerate([I, IV, V, I]): chord(STR, c, 16.5 + j * 1.0, .98, 82 + j * 6); note(CB, c[0] - 12, 16.5 + j * 1.0, .9, 104)
for j in range(5): note(GLK, [84, 86, 88, 91, 96][j], 17.5 + j * .2, .3, 96)
chord(BRS, [60, 64, 67, 72, 76], 18.5, .9, 124); note(TIM, 48, 18.5, .3, 127); note(DR, 49, 18.5, 1.5, 110); note(DR, 36, 18.5, .2, 110)
# ---- 20.5-23.0 the crisp call: tender theme on flute, harp arpeggios, string pad
chord(STR, [60, 64, 67, 72], 20.5, 2.4, 68)
for k in range(20): note(HRP, [60, 64, 67, 72, 76, 72, 67, 64][k % 8], 20.5 + k * .125, .5, 72)
play(FL, 20.5, 80, transp=12, stretch=1.0, stac=.95, until=23.0)
note(GLK, 96, 21.0, .5, 90); note(GLK, 100, 21.25, .5, 90)
# ---- 23.0-25.0 "مين هاد؟!": scratch stop, then suspense tremolo + timpani roll crescendo
for k in range(32): note(STR, [55, 56][k % 2], 23.6 + k * .0437, .05, 40 + k * 2)
for k in range(24): note(TIM, 43, 24.0 + k * .0417, .05, 50 + k * 3)
# ---- 25.0-33.0 celebration ("قبلنا فيه!"): full festive theme, handclaps + darbuka flavour, end card rides it
for k in range(16):
    t = 25.0 + k * B
    note(DR, 61, t, .1, 104 if k % 2 == 0 else 0); note(DR, 60, t + B / 2, .08, 84); note(DR, 39, t, .08, 96 if k % 2 else 0)
    note(CB, [36, 43][k % 2] + (5 if (k // 4) % 4 == 1 else 0) + (7 if (k // 4) % 4 == 2 else 0), t, B * .7, 104)
for k in range(16, 32):
    t = 25.0 + k * B
    if t >= 33.0: break
    note(DR, 61, t, .1, 100 if k % 2 == 0 else 0); note(DR, 60, t + B / 2, .08, 80); note(DR, 39, t, .08, 92 if k % 2 else 0)
    note(CB, [36, 43][k % 2] + (5 if (k // 4) % 4 == 1 else 0) + (7 if (k // 4) % 4 == 2 else 0), t, B * .7, 100)
for j, c in enumerate([I, IV, V, I, vi, ii, V, I]): chord(STR, c, 25.0 + j * 1.0, .95, 74)
t = play(BRS, 25.0, 100, transp=0, stac=.75); play(FL, 25.0, 92, transp=12, stac=.75)
play(CL, t, 92, transp=0, stac=.75); play(HRN, t, 90, transp=-12, stac=.85)
for k in range(8): note(GLK, [84, 88, 91, 96][k % 4], 28.0 + k * .125, .3, 80)     # sparkle on the end card
# button on the beat at 33.0
for k in range(10): note(HRP, 60 + k * 3, 32.6 + k * .03, .5, 80)
chord(BRS, [48, 60, 64, 67, 72, 76], 33.0, .8, 126); chord(STR, [36, 48, 60, 64, 67, 72], 33.0, .9, 110)
note(TIM, 36, 33.0, .4, 127); note(DR, 49, 33.0, 1, 120); note(DR, 36, 33.0, .3, 127)

ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=max(0, tt - last))); last = max(last, tt)
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.6', '-r', str(SR), '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------------- FX (all on the same grid) ----------------
rng = np.random.default_rng(7); T = lambda n: np.arange(n) / SR; fx = np.zeros(N)
def put(t, s, g=1): i = int(t * SR); j = min(N, i + len(s)); fx[i:j] += s[:j - i] * g
def env(n, a=.005, r=.1): e = np.ones(n); ai = max(1, int(a * SR)); ri = max(1, int(r * SR)); e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri); return e
def pop(f=600): n = int(.12 * SR); tt = T(n); fr = f + 900 * np.exp(-tt * 40); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 30) * .5
def whoosh(l=.45): n = int(l * SR); x = rng.standard_normal(n); x = np.convolve(x, np.ones(30) / 30, 'same'); return x * np.linspace(0, 1, n) ** 2 * np.r_[np.ones(n - 800), np.linspace(1, 0, 800)] * .9
def thump(): n = int(.5 * SR); tt = T(n); return (np.sin(2 * np.pi * np.cumsum(120 * np.exp(-tt * 6) + 40) / SR) * np.exp(-tt * 9) + rng.standard_normal(n) * np.exp(-tt * 40) * .3) * .8
def glitch(l=.95):
    n = int(l * SR); tt = T(n); sq = np.sign(np.sin(2 * np.pi * 110 * tt)) * .3 + np.sign(np.sin(2 * np.pi * 1730 * tt)) * .08
    gate = np.repeat(rng.random(int(l * 40) + 1) > .35, int(SR / 40) + 1)[:n]; return sq * gate * env(n, .002, .2) + rng.standard_normal(n) * .05 * gate
def scratch(): n = int(.45 * SR); tt = T(n); x = rng.standard_normal(n); f = 600 + 2500 * np.abs(np.sin(2 * np.pi * 3.3 * tt)); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * .5 + x * .25) * env(n, .005, .08) * .6
def bell(f): n = int(.6 * SR); tt = T(n); return (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * 7) * .22
def ulul(l=1.5):
    n = int(l * SR); tt = T(n); f = 1180 + 140 * np.sin(2 * np.pi * 8 * tt) + 60 * tt
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + .35 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return s * (.55 + .45 * np.sin(2 * np.pi * 8 * tt + 1)) * env(n, .05, .3) * .2
def fall(): n = int(.5 * SR); tt = T(n); return np.sin(2 * np.pi * np.cumsum(1800 * np.exp(-tt * 3) + 200) / SR) * .16 * env(n, .01, .05)
def clank(): n = int(.4 * SR); tt = T(n); return sum(np.sin(2 * np.pi * f * tt) for f in (520, 1370, 2210)) * np.exp(-tt * 14) * .18
for c in (1.5, 10.5, 16.5, 20.5, 28.0): put(c - .45, whoosh(), .45)          # whooshes peak exactly on the cut
for b in (2.5, 5.0, 7.5, 9.0, 11.5, 13.0, 15.0, 23.0, 25.0): put(b, pop(560), .8)
put(3.5, glitch(), .7); put(3.68, thump(), .85); put(18.5, thump(), .7)
put(16.7, fall()); put(17.1, clank())
for j in range(5): put(17.5 + j * .2, bell(1300 + j * 160), .7)
put(22.95, scratch(), 1.0)
put(26.0, ulul(1.5), .9)
for j in range(int(6 / .125)): put(10.5 + j * .125, rng.standard_normal(int(.03 * SR)) * np.exp(-np.arange(int(.03 * SR)) / SR * 120) * .1)  # feet on 16ths
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
# master: hard silence for the freeze and the scratch stop, gentle glue compression, loudness for Instagram
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'assets/music.wav', '-i', 'assets/fx.wav', '-filter_complex',
  "[0:a]volume='if(between(t,3.5,4.48)+between(t,23.0,23.55),0.0,1)':eval=frame,atrim=0:34[m];[1:a]volume=1.1,pan=stereo|c0=c0|c1=c0[f];"
  "[m][f]amix=inputs=2:normalize=0,acompressor=threshold=-18dB:ratio=2.5:attack=15:release=180:makeup=2,afade=t=out:st=33.5:d=0.5,loudnorm=I=-14:TP=-1:LRA=9", '-ar', '44100', 'assets/mix.wav'], check=True)
print('ok')
