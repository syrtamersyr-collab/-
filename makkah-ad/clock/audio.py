# «ساعة حمص بتحكي» — original cartoon-orchestral score, 96 BPM (bar = 2.5s), muted-trumpet "voice" for the clock. -> assets/mix.wav
import mido, subprocess, numpy as np, wave, math
SR = 44100; DUR = 40.0; N = int(SR * DUR); TPB = 480; BPM = 96; B = 60 / BPM; BAR = 4 * B; ev = []
bt = lambda s: s * BPM / 60
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v, t=0): ev.append((int(bt(t) * TPB), mido.Message('control_change', channel=ch, control=c, value=int(max(0, min(127, v))))))
def bend(ch, v, t): ev.append((int(bt(t) * TPB), mido.Message('pitchwheel', channel=ch, pitch=int(max(-8192, min(8191, v))))))
def note(ch, p, t, d, v):
    if t >= DUR or v <= 0: return
    ev.append((int(bt(t) * TPB), mido.Message('note_on', channel=ch, note=int(p), velocity=max(1, min(127, int(v))))))
    ev.append((int(bt(min(t + d, DUR)) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))
CEL, PIZ, STR, BSN, VOX, CLA, TUB, BEL, GLK, HRN, FL, DR = 0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 9
for ch, p in ((CEL, 8), (PIZ, 45), (STR, 48), (BSN, 70), (VOX, 59), (CLA, 71), (TUB, 58), (BEL, 14), (GLK, 9), (HRN, 60), (FL, 73)): prog(ch, p)
for ch, v in ((CEL, 96), (PIZ, 100), (STR, 84), (BSN, 104), (VOX, 112), (CLA, 88), (TUB, 100), (BEL, 104), (GLK, 92), (HRN, 92), (FL, 90), (DR, 92)): cc(ch, 7, v)
for ch in range(12): cc(ch, 91, 55 if ch not in (DR, VOX) else 25)
cc(VOX, 101, 0); cc(VOX, 100, 0); cc(VOX, 6, 12)      # pitch-bend range 12 semitones for the "voice"
F, Bb, C7, Dm, Gm = [41, 53, 57, 60], [46, 53, 58, 62], [48, 52, 55, 58], [38, 50, 53, 57], [43, 50, 55, 58]
def chord(ch, c, t, d, v, up=0):
    for p in c[1:]: note(ch, p + up, t, d, v)
# ---- bars 0-1 (0-5): night lullaby: celesta + soft pizz + strings; bassoon snores
LUL = [(72, 1), (77, 1), (76, .5), (74, .5), (72, 1), (69, 1), (70, 1), (72, 2)]
t = 0.3
for p, l in LUL: note(CEL, p, t, l * B * .95, 70); t += l * B
for k in range(8): note(PIZ, [41, 48][k % 2], 0.3 + k * B, B * .5, 60)
chord(STR, F, 0, BAR, 46); chord(STR, Bb, BAR, BAR, 46)
for k in range(4):                                     # snore: low in (rising bend) / out
    t0 = .7 + k * 1.1
    note(BSN, 34, t0, .45, 70); bend(BSN, 0, t0); bend(BSN, 1500, t0 + .4); bend(BSN, 0, t0 + .5)
    note(BSN, 31, t0 + .55, .4, 54)
# ---- bar 2 (5.0): startle! bell + orchestra hit, then light "talk" bed bars 2-4
note(BEL, 65, 5.0, 2.0, 120); note(BEL, 53, 5.0, 2.0, 100); chord(HRN, [0, 53, 57, 60, 65], 5.0, .25, 115); note(DR, 49, 5.0, 1.5, 100); note(TUB, 29, 5.0, .3, 110)
for b in range(2, 5):
    c = [F, C7, F][b - 2]; t0 = b * BAR
    for k in range(4): note(PIZ, c[0] if k % 2 == 0 else c[0] + 7, t0 + k * B, B * .45, 82); chord(CLA, c, t0 + k * B + B / 2, B * .3, 44, 12)
    note(DR, 42, t0, .05, 40)
# ---- bar 5 (12.5-15): sad — D minor, flute lament over sustained strings
chord(STR, Dm, 12.5, BAR, 66); note(STR, 38, 12.5, BAR, 60)
for i, (p, l) in enumerate([(74, 1), (72, .5), (70, .5), (69, 1.5), (65, .5)]): note(FL, p, 12.5 + sum(x[1] for x in [(74, 1), (72, .5), (70, .5), (69, 1.5), (65, .5)][:i]) * B, l * B * .95, 80)
# ---- bars 6-7 (15-20): the Makkah van — bouncy march (tuba, snare, brass), F major
for b in (6, 7):
    t0 = b * BAR
    for k in range(4):
        note(TUB, [41, 48, 45, 48][k], t0 + k * B, B * .5, 104); note(DR, 38, t0 + k * B + B / 2, .08, 72); note(DR, 36, t0 + k * B, .1, 90 if k % 2 == 0 else 0)
        note(DR, 42, t0 + k * B + B * .75, .05, 50)
    mel = [(72, .5), (72, .5), (77, 1), (76, .5), (74, .5), (72, 1)] if b == 6 else [(74, .5), (74, .5), (79, 1), (77, .5), (76, .5), (77, 1)]
    t = t0
    for p, l in mel: note(HRN, p - 12, t, l * B * .8, 96); note(GLK, p + 12, t, .2, 60); t += l * B
# ---- bars 8-10 (20-27.5): happy theme (strings + flute + glock), clock's lines over it
HAP = [(77, 1), (76, .5), (77, .5), (79, 1), (81, 1), (79, .5), (77, .5), (76, .5), (74, .5), (72, 2)]
for rep in range(2):
    t = 20 + rep * 2 * BAR
    if t >= 25.6: break
    for p, l in HAP:
        if t >= 25.6: break
        note(FL, p, t, l * B * .9, 70); t += l * B
for b, c in zip(range(8, 11), [F, Bb, C7]):
    t0 = b * BAR; chord(STR, c, t0, BAR, 60)
    for k in range(4): note(PIZ, c[0] + (12 if k % 2 else 0), t0 + k * B, B * .4, 80); note(DR, 42, t0 + k * B, .05, 44)
# 25.0 slide whistle up (look up) / 25.7 falling (the LiteBeam drops) -> fx ; 26.25 impact
note(TUB, 29, 26.25, .4, 120); note(DR, 49, 26.25, 1.2, 110); note(DR, 36, 26.25, .2, 120)
# ---- bar 11 (27.5-30): celebration — bells peal + full orchestra
PEAL = [77, 81, 79, 72, 77, 79, 81, 77, 81, 77, 79, 72]
for k, p in enumerate(PEAL): note(BEL, p, 27.5 + k * B / 2, 1.2, 110 - k * 2)
chord(STR, F, 27.5, BAR, 96); chord(STR, F, 27.5, BAR, 86, 12); chord(HRN, F, 27.5, BAR, 90)
for k in range(8): note(DR, 38, 27.5 + k * B / 2, .08, 80); note(TUB, [41, 48][k % 2], 27.5 + k * B / 2, B * .4, 100)
note(DR, 49, 27.5, 2, 110)
# ---- bars 12-15 (30-40): dawn anthem: strings + horns + flute, warm resolution
ANT = [(72, 1.5), (74, .5), (77, 1), (76, 1), (74, 1), (72, 1), (70, 1), (69, 1), (70, 1.5), (72, .5), (74, 1), (77, 1), (76, 2), (77, 2)]
t = 30.0
for p, l in ANT:
    if t >= 37.5: break
    note(HRN, p - 12, t, l * B * .97, 80); note(FL, p + 12, t, l * B * .97, 56); t += l * B
for b, c in zip(range(12, 16), [Bb, F, Gm, C7]):
    t0 = b * BAR; chord(STR, c, t0, BAR, 74); chord(STR, c, t0, BAR, 64, 12); note(STR, c[0] - 12, t0, BAR, 70)
    for k in range(8): note(CEL, [c[1], c[2], c[3], c[2]][k % 4] + 24, t0 + k * B / 2, .25, 46)
note(GLK, 96, 34.4, .5, 90); note(GLK, 101, 34.55, .6, 90)     # the wink
for p in (29, 41, 53, 57, 60, 65, 69, 72): note(STR, p, 37.5, 2.5, 96)
chord(HRN, F, 37.5, 2.3, 92); note(BEL, 77, 37.5, 2.5, 100); note(DR, 49, 37.5, 2.5, 100); note(TUB, 29, 37.5, .5, 110)

# ---- the clock's "voice": muted trumpet syllables, synced to the mouth (one syllable every 0.16s)
LINES = [(5.1, 7.3, 1, 1), (7.6, 9.9, 0, 0), (10.0, 12.4, 0, 1), (13.0, 15.0, 0, -1), (21.0, 23.6, 1, 1), (23.8, 25.9, 1, 1), (30.3, 32.4, 1, 0)]
def h(n): s = math.sin(n * 127.1) * 43758.5453; return s - math.floor(s)
for li, (t0, t1, shout, contour) in enumerate(LINES):
    n = int((t1 - .35 - t0 - .08) / .16)
    for k in range(n):
        ts = t0 + .08 + k * .16; frac = k / max(1, n - 1)
        p = 67 + int((h(li * 31 + k) - .5) * 6) + (int(frac * 5) if contour > 0 and frac > .7 else 0) - (int(frac * 4) if contour < 0 else 0)
        if (k + 1) % 5 == 0: continue                       # breath between words
        note(VOX, p, ts, .13, 100 + 20 * shout)
        bend(VOX, 0, ts); bend(VOX, int((h(k + li) - .5) * 1400), ts + .07)

ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=max(0, tt - last))); last = max(last, tt)
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.6', '-r', str(SR), '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ---------------- FX ----------------
rng = np.random.default_rng(5); T = lambda n: np.arange(n) / SR; fx = np.zeros(N)
def put(t, s, g=1): i = int(t * SR); j = min(N, i + len(s)); fx[i:j] += s[:j - i] * g
def env(n, a=.005, r=.05): e = np.ones(n); ai = max(1, int(a * SR)); ri = max(1, int(r * SR)); e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri); return e
def err(): n = int(.22 * SR); tt = T(n); f = np.where(tt < .11, 880, 660); return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .12 * env(n)
def pop(f=700): n = int(.14 * SR); tt = T(n); fr = f + 1100 * np.exp(-tt * 40); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 28) * .45
def honk(): n = int(.55 * SR); tt = T(n); g = ((tt < .2) | (tt > .3)).astype(float); s = sum(np.sign(np.sin(2 * np.pi * f * tt)) for f in (392, 494)) * .1; return s * g * env(n)
def engine(l): n = int(l * SR); tt = T(n); x = np.sin(2 * np.pi * np.cumsum(38 + 14 * tt / l) / SR) + .4 * rng.standard_normal(n) * .3; return np.convolve(x, np.ones(40) / 40, 'same') * np.sin(np.linspace(0, np.pi, n)) * .35
def slide(up, l=.55): n = int(l * SR); tt = T(n); f = (700 + 1300 * tt / l) if up else (2000 - 1500 * tt / l); return np.sin(2 * np.pi * np.cumsum(f) / SR) * .16 * env(n, .02, .05)
def clank(): n = int(.7 * SR); tt = T(n); return (sum(np.sin(2 * np.pi * f * tt) for f in (410, 1130, 1870)) * np.exp(-tt * 9) * .2 + rng.standard_normal(n) * np.exp(-tt * 60) * .3)
def whoosh(l=.5): n = int(l * SR); x = np.convolve(rng.standard_normal(n), np.ones(25) / 25, 'same'); return x * np.sin(np.linspace(0, np.pi, n)) ** 2 * .7
for k in range(4): put(2.0 + k * .25, err()); put(12.6 + k * .25, err(), .8)
put(14.9, engine(2.6), 1.0); put(17.5, honk(), 1.0)
for bi, tc in [(6, 17.5), (8, 18.1), (4, 18.7), (10, 19.3), (2, 19.6), (12, 19.9), (7, 20.2), (5, 20.5), (9, 20.8), (3, 21.1), (11, 21.4), (1, 21.7), (13, 22.0), (0, 22.3), (14, 22.6)]:
    put(tc - .3, pop(600 + bi * 40), .55)
put(25.0, slide(True), 1); put(25.7, slide(False), 1); put(26.25, clank(), 1.0)
for k in range(5): put(28.0 + k * .2, pop(900 + k * 90), .5)
for c in (4.4, 14.4, 20.7, 29.6): put(c - .25, whoosh(), .45)
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', 'assets/music.wav', '-i', 'assets/fx.wav', '-filter_complex',
  "[0:a]atrim=0:40[m];[1:a]pan=stereo|c0=c0|c1=c0[f];[m][f]amix=inputs=2:normalize=0,acompressor=threshold=-18dB:ratio=2.5:attack=15:release=200:makeup=2,afade=t=in:d=0.4,afade=t=out:st=39.2:d=0.8,loudnorm=I=-14:TP=-1:LRA=10", '-ar', '48000', 'assets/mix.wav'], check=True)
print('ok')
