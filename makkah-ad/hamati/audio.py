# «حماتي والنت» — original comedic Levantine score (accordion, clarinet, darbuka, pizzicato) + cartoon FX -> assets/mix.wav
import mido, subprocess, numpy as np, wave
SR = 44100; DUR = 34.0; N = int(SR * DUR); TPB = 480; BPM = 100; ev = []
bt = lambda s: s * BPM / 60; B = 60 / BPM
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v): ev.append((0, mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, p, t, d, v):
    if t >= DUR: return
    ev.append((int(bt(t) * TPB), mido.Message('note_on', channel=ch, note=int(p), velocity=max(1, min(127, int(v))))))
    ev.append((int(bt(t + d) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))

# --- v2: playful cartoon swing (honky-tonk piano, whistle, bassoon, upright bass, brushes, glockenspiel), C major, 120 BPM
BPM = 120; B = 60 / BPM
PNO, WHI, BSN, UB, GLK, BRS, VIB, DR = 0, 1, 2, 3, 4, 5, 6, 9
for ch, p in ((PNO, 3), (WHI, 78), (BSN, 70), (UB, 32), (GLK, 9), (BRS, 56), (VIB, 11)): prog(ch, p)
for ch, v in ((PNO, 92), (WHI, 96), (BSN, 100), (UB, 108), (GLK, 92), (BRS, 100), (VIB, 90), (DR, 100)): cc(ch, 7, v)
for ch in range(10): cc(ch, 91, 40 if ch != DR else 18)
sw = lambda k: (k // 2) * B + (B * .66 if k % 2 else 0)          # swung eighth k
def brushes(t0, t1, v=1.0):
    t = t0
    while t < t1 - .01:
        for k in range(4):
            note(DR, 42, t + k * B, .1, 70 * v); note(DR, 42, t + k * B + B * .66, .1, 50 * v)
            if k % 2: note(DR, 38, t + k * B, .1, 64 * v)
            else: note(DR, 36, t + k * B, .15, 84 * v)
        t += 4 * B
def walk(t0, t1, roots):
    t = t0; i = 0
    while t < t1 - .01:
        r = roots[(i // 4) % len(roots)]; note(UB, [r, r + 4, r + 7, r + 9][i % 4], t, B * .85, 100); t += B; i += 1
def comp(t0, t1, chords, v=70):
    t = t0; i = 0
    while t < t1 - .01:
        for p in chords[(i // 2) % len(chords)]: note(PNO, p, t + B * .66, B * .3, v)
        t += B * 2 if False else B; i += 1
C, F, G, A = [60, 64, 67, 70], [65, 69, 72, 75], [67, 71, 74, 77], [57, 61, 64, 67]
# 0-1.4 sting: glissando + button
for k in range(9): note(PNO, 60 + k * 2, .05 + k * .05, .1, 80 + k * 4)
for p in (48, 60, 64, 67, 72): note(BRS if p > 50 else UB, p, .7, .45, 112)
note(DR, 49, .7, .6, 100)
# 1.4-3.55 tiptoe: staccato bassoon + pizz-like piano, tension creeping up a semitone each bar
for k in range(8):
    t = 1.4 + k * B / 2
    note(BSN, [48, 55, 48, 55, 49, 56, 49, 56][k], t, B * .25, 96)
for k in range(8): note(GLK, [79, 80, 81, 82, 83, 84, 85, 86][k], 1.4 + k * .26, .1, 50 + k * 6)
note(WHI, 84, 3.1, .2, 90); note(WHI, 91, 3.32, .2, 100)
# 3.55-4.55 silence (freeze); 4.55 bassoon "uh-oh" slide + brass stabs
for k, p in enumerate([55, 54, 53, 52, 51, 50]): note(BSN, p, 4.55 + k * .07, .1, 110)
for k, (ch, d) in enumerate([([48, 51, 54], .15), ([49, 52, 55], .15), ([47, 50, 53, 56], .6)]):
    for p in ch: note(BRS, p + 12, 4.55 + k * .18, d, 118)
# 4.95-10.5 gossip swing: brushes + walking bass + whistled tune
brushes(4.95, 10.5, .8); walk(4.95, 10.5, [36, 41, 43, 36]); comp(4.95, 10.5, [C, C, F, F, G, G, C, C], 60)
tune = [(76, 1), (74, .66), (72, .34), (74, 1), (67, 1), (69, .66), (72, .34), (76, .66), (74, .34), (72, 2)]
t = 5.0
for rep in range(3):
    for p, l in tune:
        if t >= 10.3: break
        note(WHI, p + 12, t, l * B * .9, 84); t += l * B
# 10.6-16.3 chase: fast piano runs, double-time brushes, bassoon ostinato
for k in range(int(5.7 / (B / 2))):
    t = 10.6 + k * B / 2
    note(DR, 38 if k % 2 else 36, t, .08, 90); note(DR, 42, t + B / 4, .05, 60)
    note(BSN, [48, 48, 55, 48, 51, 48, 55, 53][k % 8], t, B * .4, 100)
for k in range(int(5.6 / (B / 4))):
    t = 10.6 + k * B / 4
    note(PNO, [72, 74, 76, 79, 81, 79, 76, 74][k % 8] + (5 if (k // 16) % 2 else 0), t, B / 4 * .8, 74)
for k in range(5): note(BRS, 79, 11.6 + k * 1.0, .15, 104); note(BRS, 76, 11.6 + k * 1.0, .15, 98)
# 16.4-20.5 rooftop: big major lift with vibraphone
for j, ch in enumerate([[60, 64, 67, 72], [65, 69, 72, 77], [67, 71, 74, 79], [72, 76, 79, 84]]):
    for p in ch: note(VIB, p, 16.5 + j * 1.0, .95, 84 + j * 6)
    note(UB, ch[0] - 24, 16.5 + j * 1.0, .9, 104)
for j in range(5): note(GLK, 84 + [0, 2, 4, 7, 12][j], 17.9 + j * .22, .3, 100)
for p in (60, 64, 67, 72, 76): note(BRS, p, 18.75, .8, 120)
note(DR, 49, 18.75, 1.2, 108)
# 20.6-22.8 dreamy: vibraphone arps + glock sparkle
for j in range(16): note(VIB, [72, 76, 79, 84, 79, 76][j % 6], 20.7 + j * .135, .4, 70)
for j in range(8): note(GLK, [88, 91, 96, 100][j % 4], 20.95 + j * .15, .3, 90)
# 25.2-33.2 victory: up-tempo swing with whistle + brass shout chorus
brushes(25.2, 33.2, 1.0); walk(25.2, 33.2, [36, 45, 38, 43]); comp(25.2, 33.2, [C, A, [62, 65, 69, 72], G], 74)
chorus = [(79, .5), (81, .5), (79, .5), (76, .5), (72, 1), (74, .66), (76, .34), (79, 1), (77, .5), (76, .5), (74, 2)]
t = 25.25
for rep in range(3):
    for p, l in chorus:
        if t >= 33.0: break
        note(WHI, p + 12, t, l * B * .85, 92); note(BSN, p - 12, t, l * B * .85, 70); t += l * B
for k in range(8): note(BRS, 72, 26.2 + k * 1.0, .18, 104); note(BRS, 76, 26.2 + k * 1.0, .18, 100)
for p in (36, 48, 60, 64, 67, 72, 76): note(BRS if p > 50 else UB, p, 33.2, .7, 124)
note(DR, 49, 33.2, 1, 120); note(DR, 36, 33.2, .3, 127)
ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=max(0, tt - last))); last = max(last, tt)
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.6', '-r', str(SR), '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# ---------------- FX ----------------
rng = np.random.default_rng(7); T = lambda n: np.arange(n) / SR; fx = np.zeros(N)
def put(t, s, g=1): i = int(t * SR); j = min(N, i + len(s)); fx[i:j] += s[:j - i] * g
def env(n, a=.005, r=.1): e = np.ones(n); ai = int(a * SR); ri = int(r * SR); e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri); return e
def pop(f=600): n = int(.12 * SR); tt = T(n); fr = f + 900 * np.exp(-tt * 40); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 30) * .5
def whoosh(l=.4): n = int(l * SR); x = rng.standard_normal(n); x = np.convolve(x, np.ones(30) / 30, 'same'); return x * np.sin(np.linspace(0, np.pi, n)) ** 2 * .9
def thump(): n = int(.5 * SR); tt = T(n); return (np.sin(2 * np.pi * np.cumsum(120 * np.exp(-tt * 6) + 40) / SR) * np.exp(-tt * 9) + rng.standard_normal(n) * np.exp(-tt * 40) * .3) * .8
def glitch(l=.9):
    n = int(l * SR); tt = T(n); sq = np.sign(np.sin(2 * np.pi * 110 * tt)) * .3 + np.sign(np.sin(2 * np.pi * 1730 * tt)) * .08
    gate = np.repeat(rng.random(int(l * 40) + 1) > .35, int(SR / 40) + 1)[:n]; return sq * gate * env(n, .002, .2) + rng.standard_normal(n) * .05 * gate
def scratch(): n = int(.45 * SR); tt = T(n); x = rng.standard_normal(n); f = 600 + 2500 * np.abs(np.sin(2 * np.pi * 3.3 * tt)); ph = np.cumsum(f) / SR; return (np.sin(2 * np.pi * ph) * .5 + x * .25) * env(n, .005, .08) * .6
def bell(f): n = int(.6 * SR); tt = T(n); return (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.76 * tt)) * np.exp(-tt * 7) * .25
def ulul(l=1.5):  # stylised zaghrouta trill (synth, not a voice)
    n = int(l * SR); tt = T(n); f = 1180 + 140 * np.sin(2 * np.pi * 8.5 * tt) + 60 * tt
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) + .35 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return s * (.55 + .45 * np.sin(2 * np.pi * 8.5 * tt + 1)) * env(n, .05, .3) * .22
def fall(): n = int(.55 * SR); tt = T(n); return np.sin(2 * np.pi * np.cumsum(1800 * np.exp(-tt * 3) + 200) / SR) * .18 * env(n, .01, .05)
def clank(): n = int(.4 * SR); tt = T(n); return sum(np.sin(2 * np.pi * f * tt) for f in (520, 1370, 2210)) * np.exp(-tt * 14) * .2
for c in (1.4, 10.6, 16.4, 20.6, 28.2): put(c - .15, whoosh(), .55)
for b in (2.25, 4.95, 7.3, 9.0, 11.3, 13.1, 14.9, 22.9, 25.2): put(b, pop(560), .9)
put(3.55, glitch(), .7); put(3.72, thump(), .9); put(18.75, thump(), .8)
put(16.65, fall()); put(17.15, clank())
for j in range(5): put(17.9 + j * .22, bell(1300 + j * 160), .8)
for j in range(6): put(20.95 + j * .12, bell(2000 + j * 220), .6)
put(22.8, scratch(), 1.0)
put(25.8, ulul(1.6), 1.0)
for j in range(int(5.6 / .16)): put(10.7 + j * .16, rng.standard_normal(int(.03 * SR)) * np.exp(-np.arange(int(.03 * SR)) / SR * 120) * .12)  # running feet
for j in range(8): put(28.45 + j * .3, pop(800 + j * 70), .5)
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
# duck music: true silence during the freeze (3.55-4.5) and after the scratch (22.85-25.15)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'assets/music.wav', '-i', 'assets/fx.wav', '-filter_complex',
  "[0:a]volume='if(between(t,3.55,4.5)+between(t,22.9,25.15),0.0,1)':eval=frame,atrim=0:34[m];[1:a]volume=1.2[f];[m][f]amix=inputs=2:normalize=0,afade=t=out:st=33.4:d=0.6,loudnorm=I=-14:TP=-1:LRA=9", '-ar', '44100', 'assets/mix.wav'], check=True)
print('ok')
