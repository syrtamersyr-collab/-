# Original score for «من حمص… بمستوى عالمي», played with sampled instruments (FluidR3 GM).
# 120 BPM, 2-beat pickup so bars land on the cuts: 11s (beat 22), 17s (34), 23s (46), 29s (58).
import mido, subprocess
TPB = 480; BPM = 120; ev = []
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v): ev.append((0, mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, pitch, beat, dur, vel):
    ev.append((int(beat * TPB), mido.Message('note_on', channel=ch, note=int(pitch), velocity=max(1, min(127, int(vel))))))
    ev.append((int((beat + dur) * TPB) - 1, mido.Message('note_off', channel=ch, note=int(pitch), velocity=0)))
PIANO, PAD, PIZZ, BASS, VIBE, STR, HARP, TIMP, CEL, DR, REV, MAR, HORN = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
for ch, p in ((PIANO, 0), (PAD, 89), (PIZZ, 45), (BASS, 33), (VIBE, 11), (STR, 48), (HARP, 46), (TIMP, 47), (CEL, 8), (REV, 119), (MAR, 12), (HORN, 60)): prog(ch, p)
for ch, v in ((PIANO, 104), (PAD, 84), (PIZZ, 96), (BASS, 104), (VIBE, 100), (STR, 86), (HARP, 96), (TIMP, 112), (CEL, 92), (DR, 108), (REV, 100), (MAR, 100), (HORN, 92)): cc(ch, 7, v)
for ch, pan in ((PIANO, 56), (MAR, 78), (VIBE, 46), (CEL, 84), (HARP, 40), (PIZZ, 76)): cc(ch, 10, pan)
for ch in range(13): cc(ch, 91, 74 if ch != DR else 28)
KICK, SNARE, CLAP, HAT, OHAT, CRASH, RIDE, SHAK = 36, 38, 39, 42, 46, 49, 51, 70
Bm, G, D, A = [59, 62, 66], [55, 59, 62], [62, 66, 69], [57, 61, 64]
# ---- Act 1 (beats 0–22): space, mystery → Homs ----
A1 = [(Bm, 35), (G, 31), (D, 38), (A, 33), (Bm, 35)]
note(PAD, 59, 0, 2, 50); note(CEL, 90, .5, 1, 60); note(CEL, 86, 1.25, 1, 54)
for i, (ch, root) in enumerate(A1):
    b = 2 + i * 4
    for p in ch: note(PAD, p, b, 4, 62 + i * 4); note(STR, p + 12, b, 4, 34 + i * 7)
    note(BASS, root, b, 3.8, 70)
    note(PIANO, ch[2] + 12, b, 2, 66); note(PIANO, ch[1] + 12, b + 2, 1, 56); note(PIANO, ch[0] + 24, b + 3, 1, 60)
    for k in range(8): note(CEL, [ch[0], ch[2], ch[1], ch[2]][k % 4] + 24, b + k * .5, .4, 44 + (k % 2) * 8)
    if i >= 2:                                   # 5s: «وحمص؟» — pulse enters
        for k in range(8): note(PIZZ, ch[k % 3] + (12 if k % 2 else 0), b + k * .5, .3, 60 + i * 6)
        for k in range(4): note(DR, KICK, b + k, .2, 58 + i * 6)
note(REV, 60, 18, 4, 118)
for k in range(24): note(TIMP, 38, 19 + k * .125, .12, 40 + k * 3); note(DR, SNARE, 19 + k * .125, .1, 28 + k * 3)
# ---- Act 2 (beats 22–58): bright, confident product groove — D A Bm G ----
PR = [(D, 38), (A, 33), (Bm, 35), (G, 31)]
MEL = [[78, 81, 86, 81], [76, 81, 85, 81], [74, 78, 83, 78], [74, 79, 83, 81]]
note(DR, CRASH, 22, 3, 116); note(DR, KICK, 22, .3, 124); note(TIMP, 38, 22, 2, 110)
[note(HARP, p, 22 + i * .08, 3, 84) for i, p in enumerate([50, 54, 57, 62, 66, 69, 74, 78, 81, 86])]
for bar in range(9):
    b = 22 + bar * 4; ch, root = PR[bar % 4]; lift = bar >= 6
    for k in range(8): note(MAR, [ch[0], ch[2], ch[1], ch[2], ch[0] + 12, ch[2], ch[1], ch[2]][k] + 12, b + k * .5, .35, 82 if k % 2 == 0 else 66)
    for k in (0, 1.5, 2.5): note(PIANO, ch[0], b + k, .9, 80); note(PIANO, ch[1], b + k, .9, 76); note(PIANO, ch[2], b + k, .9, 76)
    for k in range(8): note(BASS, root, b + k * .5, .42, 96 if k % 2 == 0 else 78)
    for p in ch: note(PAD, p, b, 4, 56)
    for k in range(4): note(DR, KICK, b + k, .2, 98)
    for k in (1, 3): note(DR, CLAP, b + k, .2, 90)
    for k in range(8): note(DR, HAT, b + k * .5, .1, 62 if k % 2 else 44)
    note(DR, OHAT, b + 3.5, .3, 58)
    if bar >= 1:
        for k, p in enumerate(MEL[bar % 4]): note(VIBE, p + (12 if lift else 0), b + k, .9, 90); note(CEL, p + 12, b + k, .9, 54)
    if lift:
        for p in ch: note(STR, p + 12, b, 4, 80)
        for k in range(16): note(DR, SHAK, b + k * .25, .1, 46)
    if bar in (3, 6): note(DR, CRASH, b, 2, 96)      # product changes at 17s and 23s
for k in range(8): note(DR, SNARE, 33 + k * .125, .1, 50 + k * 8); note(DR, SNARE, 45 + k * .125, .1, 50 + k * 8)
note(REV, 60, 55, 3, 110)
# ---- Act 3 (beats 58–76): resolve — G A Bm D ----
H = 58
note(DR, CRASH, H, 3, 112); note(TIMP, 31 + 12, H, 3, 112); note(DR, KICK, H, .3, 120)
OUT = [(G, 31, H, 4), (A, 33, H + 4, 4), (Bm, 35, H + 8, 4), ([62, 66, 69, 76], 38, H + 12, 6)]
for ch, root, b, d in OUT:
    for p in ch: note(PAD, p, b, d, 78); note(STR, p + 12, b, d, 84)
    note(BASS, root, b, d * .95, 88)
    for k in range(int(d * 2)): note(PIANO, [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24][k % 4], b + k * .5, .8, max(40, 78 - k * 2))
tm = H
for p, d in [(74, 2), (71, 2), (73, 2), (76, 2), (78, 2), (74, 2), (81, 6)]: note(HORN, p - 12, tm, d * .95, 90); note(VIBE, p + 12, tm, d * .95, 70); tm += d
for k in range(6): note(DR, KICK, H + 2 + k * 2, .2, 66)
[note(HARP, p, H + 12 + i * .09, 4, 86) for i, p in enumerate([50, 57, 62, 66, 69, 74, 78, 81, 86, 90])]
note(DR, CRASH, H + 12, 4, 92); note(TIMP, 38, H + 12, 4, 100)

ev.sort(key=lambda e: e[0]); mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for t, m in ev: tr.append(m.copy(time=t - last)); last = t
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.5', '-r', '44100', '-o', 'synth.reverb.room-size=0.8', '-o', 'synth.reverb.level=0.65', '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('music ok')
