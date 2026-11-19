# Warm winter score (sampled instruments via FluidSynth) + rain/thunder/transition effects, mixed to assets/mix.wav
import mido, subprocess, numpy as np, wave
SR = 44100; DUR = 35.0; N = int(SR * DUR)
TPB = 480; BPM = 120; ev = []
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v): ev.append((0, mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, pitch, t, dur, vel):            # t, dur in seconds (120 BPM: 1 beat = .5 s)
    ev.append((int(t * 2 * TPB), mido.Message('note_on', channel=ch, note=int(pitch), velocity=max(1, min(127, int(vel))))))
    ev.append((int((t + dur) * 2 * TPB) - 1, mido.Message('note_off', channel=ch, note=int(pitch), velocity=0)))
PIANO, GUIT, PIZZ, BASS, GLOCK, STR, DR = 0, 1, 2, 3, 4, 5, 9
for ch, p in ((PIANO, 0), (GUIT, 24), (PIZZ, 45), (BASS, 32), (GLOCK, 9), (STR, 48)): prog(ch, p)
for ch, v in ((PIANO, 104), (GUIT, 100), (PIZZ, 96), (BASS, 100), (GLOCK, 84), (STR, 80), (DR, 96)): cc(ch, 7, v)
for ch, pan in ((GUIT, 40), (PIZZ, 86), (GLOCK, 70)): cc(ch, 10, pan)
for ch in range(10): cc(ch, 91, 70 if ch != DR else 30)
G, Em, C, D = [55, 59, 62], [52, 55, 59], [48, 52, 55], [50, 54, 57]
PR = [(G, 43), (Em, 40), (C, 36), (D, 38)]
# 0–6.8 s: rain intro — soft piano and strings
for k, (ch, r) in enumerate([(Em, 40), (C, 36), (G, 43)]):
    t0 = .4 + k * 2.2
    for p in ch: note(STR, p, t0, 2.2, 52)
    for i, p in enumerate([ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24]): note(PIANO, p, t0 + i * .5, 1.2, 62 + (8 if i == 0 else 0))
# 6.8 s onward: cosy groove
t, bar = 6.8, 0
while t < 34.0:
    ch, r = PR[bar % 4]
    for i in range(8): note(GUIT, [ch[0], ch[1], ch[2], ch[1] + 12][i % 4] + 12, t + i * .25, .45, 72 if i % 2 == 0 else 58)
    for i in (0, .75, 1.0, 1.5): note(BASS, r, t + i, .35, 92)
    for p in ch: note(STR, p + 12, t, 2, 46)
    note(DR, 36, t, .2, 84); note(DR, 36, t + 1, .2, 76); note(DR, 38, t + .5, .2, 58); note(DR, 38, t + 1.5, .2, 62)
    for i in range(8): note(DR, 70, t + i * .25, .1, 44 + (10 if i % 2 else 0))
    if bar >= 2:
        for i, p in enumerate([ch[2] + 12, ch[1] + 24, ch[0] + 24, ch[2] + 12]): note(GLOCK, p + 12, t + i * .5, .5, 64)
    t += 2; bar += 1
for cut in (3.2, 6.8, 10.8, 14.8, 18.8, 22.8, 26.8): note(GLOCK, 79, cut, 1.2, 96); note(PIANO, 67, cut, 1.5, 80)
for p in (43, 55, 59, 62, 67): note(STR, p, 34.0, 1.0, 84)
note(PIANO, 79, 34.0, 1.0, 84)
ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=tt - last)); last = tt
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.55', '-r', str(SR), '-o', 'synth.reverb.room-size=0.7', '-o', 'synth.reverb.level=0.55', '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# --- effects ---
rng = np.random.default_rng(3); T = lambda n: np.arange(n) / SR
def lp(x, c): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / c) ** 4); return np.fft.irfft(X, len(x))
def hp(x, c): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 - 1 / np.sqrt(1 + (f / c) ** 4); return np.fft.irfft(X, len(x))
fx = np.zeros((N, 2))
def put(t, s, g=1, pan=0):
    i = int(t * SR); j = min(N, i + len(s)); fx[i:j, 0] += s[:j - i] * g * (1 - pan); fx[i:j, 1] += s[:j - i] * g * (1 + pan)
rainL = hp(lp(rng.standard_normal(N), 9000), 900) * .05; rainR = hp(lp(rng.standard_normal(N), 9000), 900) * .05
drops = np.zeros(N); idx = rng.integers(0, N, 2600); drops[idx] = rng.uniform(.2, 1, 2600); drops = hp(drops, 2500) * .25
env = np.ones(N); env[int(7 * SR):] = .45
fx[:, 0] += (rainL + drops) * env; fx[:, 1] += (rainR + drops) * env
n = int(3.2 * SR); th = lp(rng.standard_normal(n), 380) * np.exp(-T(n) * 1.3) * (1 - np.exp(-T(n) * 30)); put(.55, th, 1.6)
cr = hp(rng.standard_normal(int(.25 * SR)), 2000) * np.exp(-T(int(.25 * SR)) * 18); put(.55, cr, .35)
for cut in (3.2, 6.8, 10.8, 14.8, 18.8, 22.8, 26.8):
    n = int(.5 * SR); w = lp(hp(rng.standard_normal(n), 300), 3000) * np.sin(np.linspace(0, np.pi, n)) ** 2; put(cut - .2, w, .28)
fade = np.ones(N); fade[:int(.3 * SR)] = np.linspace(0, 1, int(.3 * SR)); fade[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR)); fx *= fade[:, None]
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
print('audio ok')
