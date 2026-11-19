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
ACC, CLA, PIZ, BAS, STR, CEL, BRS, DR = 0, 1, 2, 3, 4, 5, 6, 9
for ch, p in ((ACC, 21), (CLA, 71), (PIZ, 45), (BAS, 58), (STR, 48), (CEL, 8), (BRS, 61)): prog(ch, p)
for ch, v in ((ACC, 92), (CLA, 96), (PIZ, 100), (BAS, 96), (STR, 78), (CEL, 100), (BRS, 96), (DR, 112)): cc(ch, 7, v)
for ch in range(10): cc(ch, 91, 45 if ch != DR else 20)
HJ = [62, 63, 66, 67, 69, 70, 72, 74, 75, 78, 79]           # D hijaz
def darbuka(t0, t1, vel=1.0, fast=False):            # doum-tek pattern (maqsum)
    t = t0
    pat = [(0, 'D'), (.5, 't'), (1, 't'), (1.5, 'D'), (2, 't'), (3, 'D'), (3.5, 't')]
    while t < t1 - .01:
        for o, k in pat:
            tt = t + o * B * (.5 if fast else 1)
            if tt >= t1: break
            if k == 'D': note(DR, 61, tt, .15, 112 * vel); note(DR, 35, tt, .15, 70 * vel)
            else: note(DR, 60, tt, .1, 86 * vel)
        note(DR, 54, t + B * (.5 if fast else 1) * 2.5, .1, 60 * vel)
        t += 4 * B * (.5 if fast else 1)
# 0-1.4 opening sting
for k in range(10): note(DR, 54, .05 + k * .07, .06, 60 + k * 5)
for p in (50, 62, 66, 69): note(ACC, p, .75, .6, 110)
note(DR, 61, .75, .2, 120)
# 1.4-3.55 sneaky build to the sneeze: pizzicato hijaz walk, rising
t = 1.4; i = 0
while t < 3.5:
    note(PIZ, HJ[[0, 2, 4, 2, 3, 5, 6, 5][i % 8]] - 12 + (i // 8) * 2, t, B * .3, 80 + i * 3); 
    if i % 2 == 0: note(BAS, 38, t, B * .4, 80)
    t += B / 2; i += 1
note(CLA, 74, 3.0, .5, 90); note(CLA, 79, 3.3, .25, 100)
# 3.55-4.55 dead silence (comic freeze) then crash-zoom stabs "dun dun DUN"
for k, (p, d) in enumerate([(50, .16), (51, .16), (54, .7)]):
    for q in (p, p + 12, p + 15): note(BRS, q, 4.55 + k * .2, d, 120)
    note(DR, 41, 4.55 + k * .2, .2, 120)
# 4.8-10.5 light hijaz groove under the dialogue
darbuka(4.95, 10.5, .7)
mel = [(0, 1), (2, .5), (3, .5), (4, 1), (3, .5), (2, .5), (1, 1), (0, 2)]
t = 5.0
while t < 10.2:
    for d, l in mel:
        if t >= 10.3: break
        note(ACC, HJ[d] + 12, t, l * B * .9, 70); t += l * B
for k in range(int(5.5 / B)): note(BAS, [38, 45][k % 2], 4.95 + k * B, B * .7, 84)
note(CLA, 74, 10.0, .2, 100); note(CLA, 81, 10.25, .35, 110)   # cue the run
# 10.6-16.3 chase: double-time darbuka, clarinet runs
darbuka(10.6, 16.3, 1.0, fast=True)
t = 10.6; k = 0
while t < 16.2:
    run = [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3]
    for j, d in enumerate(run):
        tt = t + j * B / 4
        if tt >= 16.2: break
        note(CLA, HJ[d] + (0 if k % 2 == 0 else 5), tt, B / 4 * .9, 92)
    for j in range(6): note(BAS, [38, 50][j % 2], t + j * B / 2, B / 2 * .8, 98)
    for p in (62, 66, 69): note(ACC, p, t, B * 2.7, 72)
    t += 3 * B; k += 1
# 16.4-20.5 rooftop: bright major lift + celesta pings
for j, chord in enumerate([[62, 66, 69], [67, 71, 74], [69, 73, 76], [74, 78, 81]]):
    for p in chord: note(STR, p, 16.5 + j * 1.0, 1.0, 80 + j * 8)
for j in range(5): note(CEL, 84 + j * 2, 17.9 + j * .22, .3, 100)
for p in (62, 66, 69, 74): note(BRS, p, 18.75, .9, 118)
note(DR, 49, 18.75, 1.2, 110)
# 20.6-22.8 dreamy: strings + celesta sparkle
for p in (62, 66, 69, 74): note(STR, p, 20.7, 2.1, 72)
for j in range(8): note(CEL, [86, 90, 93, 98][j % 4], 20.9 + j * .15, .3, 96)
# 22.85 record scratch (fx) -> silence, then 25.2 joyful dabke to the end
darbuka(25.2, 33.3, 1.0)
for k in range(int(8.1 / (B / 2))):
    tt = 25.2 + k * B / 2
    if tt > 33.2: break
    note(DR, 39, tt, .1, 76 if k % 2 else 0) if k % 4 == 2 else None
dab = [(4, .5), (4, .5), (5, .5), (4, .5), (3, .5), (2, .5), (3, 1), (2, .5), (1, .5), (2, .5), (3, .5), (2, 1), (0, 1)]
t = 25.25
while t < 33.0:
    for d, l in dab:
        if t >= 33.0: break
        note(ACC, HJ[d] + 12, t, l * B * .85, 96); note(CLA, HJ[d] + 12, t, l * B * .85, 64); t += l * B
for k in range(int(8 / B)): note(BAS, [38, 45, 43, 45][k % 4], 25.2 + k * B, B * .6, 98)
for q in (38, 50, 62, 66, 69, 74): note(BRS if q > 50 else BAS, q, 33.2, .7, 122)
note(DR, 49, 33.2, 1, 120); note(DR, 61, 33.2, .3, 127)
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
