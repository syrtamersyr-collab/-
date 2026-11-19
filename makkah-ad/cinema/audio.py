# Cinematic score (sampled instruments) + rain and thunder synced to the lightning, mixed to assets/mix.wav
import mido, subprocess, numpy as np, wave
SR = 44100; DUR = 40.0; N = int(SR * DUR); TPB = 480; BPM = 90; ev = []
bt = lambda s: s * BPM / 60
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v): ev.append((0, mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, p, t, d, v):
    ev.append((int(bt(t) * TPB), mido.Message('note_on', channel=ch, note=int(p), velocity=max(1, min(127, int(v))))))
    ev.append((int(bt(t + d) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))
PIANO, STR, CELLO, CHOIR, BRASS, TIMP, DR, HARP = 0, 1, 2, 3, 4, 5, 9, 6
for ch, p in ((PIANO, 0), (STR, 49), (CELLO, 42), (CHOIR, 52), (BRASS, 61), (TIMP, 47), (HARP, 46)): prog(ch, p)
for ch, v in ((PIANO, 108), (STR, 92), (CELLO, 100), (CHOIR, 70), (BRASS, 90), (TIMP, 118), (DR, 110), (HARP, 92)): cc(ch, 7, v)
for ch in range(10): cc(ch, 91, 80 if ch != DR else 40)
Am, F, C, G, Em, Dm = [57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62], [52, 55, 59], [50, 53, 57]
B = 60 / BPM  # seconds per beat
prog_ = [Am, F, C, G]
# 0-5: lone piano motif over strings (Homs)
for i, p in enumerate([76, 72, 69, 71, 72, 69, 64]): note(PIANO, p, .6 + i * B * .75, B * 1.4, 70 + (8 if i == 0 else 0))
for p in Am: note(STR, p, 0, 5.2, 58)
note(CELLO, 45, 0, 5.2, 70); note(TIMP, 45, 1.1, 2, 90)
# 5-32: pulse — cello ostinato, strings, piano arps, deep drums every bar
t, bar = 5.0, 0
while t < 32:
    ch = prog_[bar % 4]; r = ch[0] - 12
    for k in range(8): note(CELLO, r if k % 2 == 0 else r + 7, t + k * B / 2, B / 2 * .9, 84 + (10 if k == 0 else 0))
    for p in ch: note(STR, p + 12, t, 4 * B, 60 + min(bar, 8) * 3)
    for k, p in enumerate([ch[0] + 24, ch[1] + 24, ch[2] + 24, ch[1] + 24]): note(PIANO, p, t + k * B, B * 1.2, 62)
    note(DR, 36, t, .3, 100); note(DR, 36, t + 2 * B, .3, 82); note(TIMP, r + 12, t, 1.2, 80)
    if bar >= 4:
        note(DR, 38, t + B, .2, 64); note(DR, 38, t + 3 * B, .2, 70)
        for p in ch: note(CHOIR, p + 12, t, 4 * B, 55)
    if bar >= 8: note(BRASS, ch[0], t, 4 * B * .95, 72); note(BRASS, ch[2], t, 4 * B * .95, 66)
    t += 4 * B; bar += 1
for cut in (5, 9, 14, 19, 24, 28, 32, 36): note(TIMP, 45, cut, 1.5, 112); note(DR, 49, cut, 2, 90); note(HARP, 81, cut, 1, 70); note(HARP, 76, cut + .08, 1, 64)
# 32-40: lift and resolve
for p in (45, 57, 64, 69, 72, 76): note(STR, p, 32, 4, 90)
for p in (57, 64, 69): note(BRASS, p, 32, 3.8, 92); note(CHOIR, p + 12, 32, 4, 72)
for p in (41, 53, 60, 65, 69): note(STR, p, 36, 4, 86)
for p in (53, 60, 65): note(BRASS, p, 36, 3.5, 84)
for i, p in enumerate([69, 72, 76, 81, 84]): note(PIANO, p, 36.4 + i * .35, 2.5, 80)
note(CELLO, 41, 36, 4, 90); note(TIMP, 41, 36, 3, 110)
ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=tt - last)); last = tt
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.5', '-r', str(SR), '-o', 'synth.reverb.room-size=0.9', '-o', 'synth.reverb.level=0.7', '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
rng = np.random.default_rng(7); T = lambda n: np.arange(n) / SR
def lp(x, c): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / c) ** 4); return np.fft.irfft(X, len(x))
def hp(x, c): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 - 1 / np.sqrt(1 + (f / c) ** 4); return np.fft.irfft(X, len(x))
fx = np.zeros((N, 2))
for ch in (0, 1): fx[:, ch] += hp(lp(rng.standard_normal(N), 8000), 700) * .045
for b in (1.1, 4.95, 13.9, 23.9, 31.9, 35.9):
    n = int(3.5 * SR); th = lp(rng.standard_normal(n), 300) * np.exp(-T(n) * 1.1) * (1 - np.exp(-T(n) * 25))
    cr = hp(rng.standard_normal(int(.3 * SR)), 1800) * np.exp(-T(int(.3 * SR)) * 14)
    i = int(b * SR); j = min(N, i + n); fx[i:j] += (th[:j - i] * 1.7)[:, None]; k = min(N, i + len(cr)); fx[i:k] += (cr[:k - i] * .4)[:, None]
fade = np.ones(N); fade[:int(.4 * SR)] = np.linspace(0, 1, int(.4 * SR)); fade[-int(1 * SR):] = np.linspace(1, 0, int(1 * SR)); fx *= fade[:, None]
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok')
