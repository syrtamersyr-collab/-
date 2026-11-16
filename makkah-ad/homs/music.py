# Original Levantine score for «من قلب حمص», played with sampled instruments (FluidR3 GM).
# 120 BPM maqsum groove, D Nahawand. Cuts at beats 8 (4s), 20 (10s), 27 (13.5s), 32 (16s), 44 (22s), 56 (28s).
import mido, subprocess
TPB = 480; BPM = 120; ev = []
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v): ev.append((0, mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, pitch, beat, dur, vel):
    ev.append((int(beat * TPB), mido.Message('note_on', channel=ch, note=int(pitch), velocity=max(1, min(127, int(vel))))))
    ev.append((int((beat + dur) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(pitch), velocity=0)))
OUD, QANUN, ACC, STR, BASS, PIZZ, DR, CLAR = 0, 1, 2, 3, 4, 5, 9, 6
for ch, p in ((OUD, 24), (QANUN, 15), (ACC, 21), (STR, 48), (BASS, 32), (PIZZ, 45), (CLAR, 71)): prog(ch, p)
for ch, v in ((OUD, 118), (QANUN, 104), (ACC, 96), (STR, 92), (BASS, 108), (PIZZ, 100), (DR, 116), (CLAR, 92)): cc(ch, 7, v)
for ch, pan in ((OUD, 50), (QANUN, 82), (ACC, 46), (PIZZ, 76)): cc(ch, 10, pan)
for ch in range(10): cc(ch, 91, 58 if ch != DR else 26)
DUM, TEK, KA, RIQ, CLAP, WOOD, CRASH = 64, 60, 62, 54, 39, 76, 49      # low conga / hi bongo / open hi conga / tambourine
def maqsum(b, g=1.0, full=True):
    for o, n, v in ((0, DUM, 118), (.5, TEK, 100), (1.5, TEK, 104), (2, DUM, 114), (3, TEK, 108)): note(DR, n, b + o, .2, v * g)
    if full:
        for o in (1, 2.5, 3.5): note(DR, KA, b + o, .15, 70 * g)
        for k in range(8): note(DR, RIQ, b + k * .5, .1, (78 if k % 2 == 0 else 54) * g)
def trem(ch, p, b, d, v, step=.125):
    k = 0
    while k * step < d - 1e-6: note(ch, p, b + k * step, step * .9, v - (6 if k % 2 else 0)); k += 1
D3, D4 = 50, 62
# --- 0–4s: oud taqsim over a drone ---
note(STR, 38, 0, 8, 46); note(STR, 50, 0, 8, 40)
for o, p, d in ((.2, 62, .8), (1.0, 65, .4), (1.4, 64, .4), (1.8, 62, .7), (2.6, 69, 1.0), (3.6, 70, .3), (3.9, 69, .3), (4.2, 67, .3), (4.5, 65, .5), (5.0, 64, .4), (5.4, 65, .4), (5.8, 62, 1.6)): trem(OUD, p, o, d, 100) if d >= .7 else note(OUD, p, o, d, 104)
note(OUD, 50, .2, 3, 86); note(OUD, 50, 5.8, 2, 86)
for k in range(4): note(DR, RIQ, 6 + k * .5, .1, 50 + k * 10)
# --- 4–10s: waiting — sparse, cheeky: woodblock ticks, pizzicato, bass ---
for bar in range(3):
    b = 8 + bar * 4
    for k in range(4): note(DR, WOOD, b + k, .1, 86 if k % 2 == 0 else 60)
    for o, p in ((0, 50), (1.5, 50), (2, 57), (3, 53)): note(BASS, p - 12, b + o, .4, 88)
    for o, p in ((.5, 62), (1, 65), (2.5, 64), (3, 62), (3.5, 61)): note(PIZZ, p, b + o, .3, 84)
    maqsum(b, .55, full=False)
note(CLAR, 69, 16.5, .5, 70); note(CLAR, 68, 17, .5, 70); note(CLAR, 67, 17.5, .5, 70); note(CLAR, 65, 18, 1.6, 76)     # a little sigh
# --- 10–13.5s: the arcs light up — rising qanun runs on each arc ---
for b0, base in ((21.6, 62), (22.9, 65), (24.2, 69)):
    for i, st in enumerate((0, 2, 3, 5, 7, 8, 12)): note(QANUN, base + st, b0 + i * .09, .5, 92 + i * 3)
note(STR, 50, 20, 7, 60); note(STR, 57, 20, 7, 56); note(STR, 62, 23.5, 3.5, 70); note(STR, 69, 24.8, 2.2, 80)
for k in range(12): note(DR, RIQ, 25.5 + k * .125, .1, 50 + k * 6)
# --- 13.5s onward: full dabke-flavoured groove, beats 27 → 56 ---
note(DR, CRASH, 27, 2, 112); note(DR, DUM, 27, .3, 127)
MEL = [(0, 69, .5), (.5, 70, .5), (1, 69, .5), (1.5, 67, .5), (2, 65, 1), (3, 64, .5), (3.5, 62, .5),
       (4, 65, .5), (4.5, 67, .5), (5, 69, 1), (6, 67, .5), (6.5, 65, .5), (7, 64, 1),
       (8, 69, .5), (8.5, 70, .5), (9, 72, .5), (9.5, 70, .5), (10, 69, 1), (11, 67, .5), (11.5, 65, .5),
       (12, 64, .5), (12.5, 65, .5), (13, 64, .5), (13.5, 61, .5), (14, 62, 2)]
BASSL = [38, 38, 43, 45, 38, 38, 41, 45]
b = 28; bar = 0
note(DR, DUM, 27, .2, 120); note(DR, TEK, 27.5, .2, 100)
while b < 56:
    maqsum(b)
    for k in (1, 3): note(DR, CLAP, b + k, .15, 84)
    r = BASSL[bar % 8]
    for o in (0, 1.5, 2, 3): note(BASS, r, b + o, .45, 100)
    for o in (.5, 1.5, 2.5, 3.5): note(OUD, [50, 57, 62][int(o * 2) % 3], b + o, .3, 80)
    bar += 1; b += 4
for rep_, b0 in enumerate((28, 44)):
    for o, p, d in MEL:
        if b0 + o < 56: note(ACC, p, b0 + o, d * .92, 96); note(STR, p + 12, b0 + o, d * .92, 78); note(QANUN, p + 12, b0 + o, d * .5, 70)
for o, p, d in ((0, 62, 1), (1, 65, 1), (2, 69, 1), (3, 70, 1), (4, 69, 2), (6, 67, 1), (7, 65, 1), (8, 64, 1), (9, 65, 1), (10, 67, 2), (12, 69, 1), (13, 67, 1), (14, 65, 2)):
    if 32 + o < 44: trem(OUD, p + 12, 32 + o + 4 if False else 40 + o - 8, d, 96)        # oud answer phrase, bars 3–5 of the groove
for bb in (32, 44): note(DR, CRASH, bb, 2, 92)
for k in range(8): note(DR, TEK, 55 + k * .125, .1, 70 + k * 6)
# --- 28s: full signal + sign-off (beats 56 → 70) ---
note(DR, CRASH, 56, 3, 116); note(DR, DUM, 56, .3, 127)
for i in range(5): note(QANUN, [62, 65, 69, 74, 77][i], 57.2 + i * .68, .6, 100)           # one note per bar that fills
b = 56
while b < 68:
    maqsum(b, .9); [note(DR, CLAP, b + k, .15, 80) for k in (1, 3)]
    for o in (0, 1.5, 2, 3): note(BASS, 38 if b < 64 else 45, b + o, .45, 98)
    b += 4
for o, p, d in ((0, 69, 1), (1, 70, .5), (1.5, 69, .5), (2, 67, 1), (3, 65, 1), (4, 64, 1), (5, 65, .5), (5.5, 64, .5), (6, 62, 2), (8, 65, 1), (9, 64, 1), (10, 61, 1), (11, 62, 1)): note(ACC, p, 56 + o, d * .92, 96); note(STR, p + 12, 56 + o, d * .92, 80)
for p in (38, 50, 57, 62, 66, 69): note(STR, p, 68, 3, 90)
trem(OUD, 62, 68, 2, 104); note(OUD, 50, 68, 3, 100); note(DR, CRASH, 68, 3, 104); note(DR, DUM, 68, .3, 127); note(DR, RIQ, 68, .5, 100)

ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for t, m in ev: tr.append(m.copy(time=t - last)); last = t
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.6', '-r', '44100', '-o', 'synth.reverb.room-size=0.6', '-o', 'synth.reverb.level=0.45', '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('music ok')
