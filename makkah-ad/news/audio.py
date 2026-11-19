# Upbeat TV-news score (sampled instruments) + cartoon effects, mixed to assets/mix.wav
import mido, subprocess, numpy as np, wave
SR = 44100; DUR = 35.0; N = int(SR * DUR); TPB = 480; BPM = 128; ev = []
bt = lambda s: s * BPM / 60
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v): ev.append((0, mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, p, t, d, v):
    ev.append((int(bt(t) * TPB), mido.Message('note_on', channel=ch, note=int(p), velocity=max(1, min(127, int(v))))))
    ev.append((int(bt(t + d) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(p), velocity=0)))
BR, STR, BASS, PIZZ, MAR, TUBA, DR, WB = 0, 1, 2, 3, 4, 5, 9, 6
for ch, p in ((BR, 61), (STR, 48), (BASS, 33), (PIZZ, 45), (MAR, 12), (TUBA, 58), (WB, 115)): prog(ch, p)
for ch, v in ((BR, 100), (STR, 84), (BASS, 104), (PIZZ, 96), (MAR, 98), (TUBA, 96), (DR, 108), (WB, 110)): cc(ch, 7, v)
for ch in range(10): cc(ch, 91, 50 if ch != DR else 25)
B = 60 / BPM
# 0-3 news ident: brass fanfare
for i, (ch, d) in enumerate([([60, 64, 67], .4), ([62, 65, 69], .4), ([64, 67, 72], 1.4)]):
    for p in ch: note(BR, p, .25 + i * .45, d, 110)
note(DR, 49, 1.15, 2, 110); note(DR, 36, 1.15, .3, 120)
# 3-16: bad forecast — sneaky pizzicato + tuba (comic "uh-oh")
t = 3.0
while t < 16:
    for k, p in enumerate([57, 60, 64, 60, 56, 59, 62, 59]): note(PIZZ, p, t + k * B, B * .6, 84)
    for k in (0, 2, 4, 6): note(TUBA, [45, 40, 44, 40][k // 2], t + k * B, B * .9, 92)
    for k in range(8): note(WB, 76, t + k * B, .08, 50 + (20 if k % 2 == 0 else 0))
    t += 8 * B
for k in range(8): note(TUBA, 45 - k, 13.6 + k * .18, .2, 90)        # sad slide at the power cut
# 16-17.6 alarm stabs
for k in range(6): note(BR, 84, 16 + k * .27, .13, 120); note(BR, 79, 16 + k * .27, .13, 110)
# 17.6-35 good news: bright major groove
t, bar = 17.6, 0; prog_ = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]
while t < 34:
    ch = prog_[bar % 4]
    for k in range(4): note(DR, 36, t + k * B, .2, 108); note(DR, 42, t + k * B + B / 2, .1, 70)
    for k in (1, 3): note(DR, 38, t + k * B, .2, 96)
    for k in range(8): note(BASS, ch[0] - 24 + (12 if k % 2 else 0), t + k * B / 2, B / 2 * .9, 98)
    for k in range(8): note(MAR, [ch[0], ch[1], ch[2], ch[1] + 12][k % 4] + 12, t + k * B / 2, B / 2, 86)
    for p in ch: note(STR, p, t, 4 * B, 70)
    if bar % 2 == 1:
        for p in ch: note(BR, p + 12, t + 2 * B, B * 1.5, 100)
    t += 4 * B; bar += 1
for p in (48, 60, 64, 67, 72): note(BR, p, 34.0, 1.0, 118)
note(DR, 49, 34.0, 1, 120); note(DR, 36, 34.0, .3, 127)
ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for tt, m in ev: tr.append(m.copy(time=tt - last)); last = tt
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.55', '-r', str(SR), '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
# cartoon effects: pops for icons, whoosh-flash on cuts, siren at the alert
T = lambda n: np.arange(n) / SR; fx = np.zeros(N)
def put(t, s, g=1): i = int(t * SR); j = min(N, i + len(s)); fx[i:j] += s[:j - i] * g
def popsnd(f=600): n = int(.12 * SR); tt = T(n); fr = f + 900 * np.exp(-tt * 40); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 30) * .5
def whoosh(): rng = np.random.default_rng(1); n = int(.4 * SR); x = rng.standard_normal(n); x = np.convolve(x, np.ones(30) / 30, 'same'); return x * np.sin(np.linspace(0, np.pi, n)) ** 2 * .9
for c in (3, 10, 16, 24, 30): put(c - .12, whoosh(), .5)
for i in range(6): put(4 + i * .35, popsnd(500 + i * 60))
for i in range(6): put(17.6 + i * .43, popsnd(800 + i * 80))
for i in range(6): put(24.3 + i * .3, popsnd(700 + i * 50))
for x in (6.5, 8, 12.6, 13.6, 21, 22.2, 27.6, 30.4, 31, 31.8): put(x, popsnd(420), .8)
n = int(1.6 * SR); tt = T(n); put(16, np.sin(2 * np.pi * np.cumsum(700 + 250 * np.sign(np.sin(2 * np.pi * 3 * tt))) / SR) * .22)
with wave.open('assets/fx.wav', 'wb') as f: f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(fx, -1, 1) * 32767).astype(np.int16).tobytes())
print('ok')
