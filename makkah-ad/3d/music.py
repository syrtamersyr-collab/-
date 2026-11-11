# Original cinematic score for the 3D reel, played with sampled instruments (FluidR3 GM soundfont).
# 120 BPM, D minor: Dm – Bb – F – C. Cuts: 4s pull-back, 12s groove, 21s lift, 27s riser, 28.8s hit, outro.
import mido, subprocess, sys
TPB = 480; BPM = 120
mid = mido.MidiFile(ticks_per_beat=TPB); ev = []
def prog(ch, p): ev.append((0, mido.Message('program_change', channel=ch, program=p)))
def cc(ch, c, v, beat=0): ev.append((int(beat * TPB), mido.Message('control_change', channel=ch, control=c, value=v)))
def note(ch, pitch, beat, dur, vel):
    ev.append((int(beat * TPB), mido.Message('note_on', channel=ch, note=pitch, velocity=max(1, min(127, int(vel))))))
    ev.append((int((beat + dur) * TPB) - 1, mido.Message('note_off', channel=ch, note=pitch, velocity=0)))
PIANO, PAD, PIZZ, BASS, HORN, CHOIR, HARP, TIMP, HIT, DR, REV, HI, CELLO = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
for ch, p in ((PIANO, 0), (PAD, 48), (PIZZ, 45), (BASS, 38), (HORN, 60), (CHOIR, 52), (HARP, 46), (TIMP, 47), (HIT, 55), (REV, 119), (HI, 48), (CELLO, 42)): prog(ch, p)
for ch, v in ((PIANO, 105), (PAD, 80), (PIZZ, 100), (BASS, 96), (HORN, 100), (CHOIR, 78), (HARP, 95), (TIMP, 115), (HIT, 110), (DR, 110), (REV, 100), (HI, 92), (CELLO, 96)): cc(ch, 7, v)
for ch, pan in ((PIANO, 54), (PIZZ, 78), (HARP, 40), (HORN, 72), (HI, 50), (CELLO, 74)): cc(ch, 10, pan)
for ch in range(13): cc(ch, 91, 70 if ch != DR else 30)
D, Bb, F, C = [62, 65, 69], [58, 62, 65], [53, 57, 60], [60, 64, 67]     # Dm, Bb, F, C (around middle C)
PROG = [D, Bb, F, C]; ROOT = [38, 34, 41, 36]
chord = lambda bar: PROG[bar % 4]
KICK, SNARE, CLAP, HAT, OHAT, CRASH, TOM, RIDE = 36, 38, 39, 42, 46, 49, 41, 51
MEL = [[(69, 0, 1.5), (74, 1.5, .5), (77, 2, 2)], [(77, 0, 1.5), (74, 1.5, .5), (70, 2, 2)], [(69, 0, 1.5), (72, 1.5, .5), (77, 2, 2)], [(76, 0, 2), (79, 2, 1), (76, 3, 1)]]

for bar in range(14):                      # bars 0–13 = 0–28s
    b0 = bar * 4; ch = chord(bar); t = b0 / 2
    # piano arpeggio (always), brighter as we go
    arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12, ch[1] + 12, ch[0] + 24, ch[2] + 12]
    for i, p in enumerate(arp): note(PIANO, p, b0 + i * .5, .6, (52 if bar < 2 else 66) + (10 if i % 4 == 0 else 0))
    # warm pad
    for p in ch: note(PAD, p, b0, 4, 46 + min(bar, 10) * 3)
    note(PAD, ROOT[bar % 4] + 12, b0, 4, 50)
    if bar < 2 and bar == 0: [note(HARP, p, i * .12, 2, 70) for i, p in enumerate([50, 57, 62, 65, 69, 74, 77, 81])]
    if bar >= 2:                               # 4s: pulse enters
        for i in range(8): note(PIZZ, ch[i % 3] + (12 if i % 2 else 0), b0 + i * .5, .3, 70 + (12 if i % 2 == 0 else 0))
        note(CELLO, ROOT[bar % 4] + 12, b0, 4, 74)
        for i in range(4): note(DR, KICK, b0 + i, .2, 92 if bar >= 6 else 70)
    if bar >= 4:
        for i in range(8): note(DR, HAT, b0 + i * .5, .1, 58 if i % 2 else 44)
    if bar >= 6:                               # 12s: full groove + horn theme
        for i in (1, 3): note(DR, CLAP, b0 + i, .2, 88); note(DR, SNARE, b0 + i, .2, 70)
        for i in range(8): note(BASS, ROOT[bar % 4], b0 + i * .5, .42, 92 if i % 2 == 0 else 74)
        note(DR, OHAT, b0 + 3.5, .3, 60)
        for p, o, d in MEL[bar % 4]: note(HORN, p - 12, b0 + o, d * .95, 88)
    if bar >= 11:                              # 22s: the lift
        for p, o, d in MEL[bar % 4]: note(HI, p + 12, b0 + o, d * .95, 96); note(HI, p, b0 + o, d * .95, 84)
        for p in ch: note(CHOIR, p + 12, b0, 4, 78)
        for i in (0, 2.5): note(DR, TOM, b0 + i, .4, 104)
        for i in range(16): note(DR, RIDE, b0 + i * .25, .1, 40) if i % 2 else None
# fills / accents
for i in range(8): note(DR, SNARE, 22 + i * .25, .1, 50 + i * 8)          # 11–12s fill into the groove
note(DR, CRASH, 24, 2, 104); note(DR, CRASH, 8, 2, 78)
note(DR, CRASH, 42, 2, 112); note(TIMP, 38, 42, 2, 110); note(DR, CRASH, 44, 2, 100)   # 21s lift
# 27–28.8s riser
note(REV, 60, 53.4, 4.2, 120)
for i in range(29): note(TIMP, 38, 54 + i * .125, .12, 40 + i * 3); note(DR, SNARE, 54 + i * .125, .1, 30 + i * 3)
for i, p in enumerate([62, 65, 69, 74, 77, 81, 86]): note(HI, p, 54 + i * .5, .5, 70 + i * 7)
# 28.8s HIT + outro (beats 57.6 → 72)
H = 57.6
for p in (38, 50, 62, 65, 69, 74): note(HIT, p, H, 1.5, 118)
note(DR, CRASH, H, 3, 124); note(DR, KICK, H, .3, 127); note(TIMP, 38, H, 3, 124); note(TIMP, 26 + 12, H + .02, 3, 110)
OUT = [(Bb, 34, H, 4), (C, 36, H + 4, 4), (D, 38, H + 8, 2.4), ([53, 57, 60, 67], 41, H + 10.4, 4.0)]   # Bb – C – Dm – Fadd9
for ch, root, b, d in OUT:
    for p in ch: note(PAD, p, b, d, 78); note(CHOIR, p + 12, b, d, 62)
    note(CELLO, root + 12, b, d, 84); note(BASS, root, b, d * .9, 84)
    n = int(d * 2)
    for i in range(n): note(PIANO, [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[1] + 24][i % 4], b + i * .5, .7, 74 - i)
for i, (p, d) in enumerate([(74, 2), (77, 2), (79, 2), (76, 2), (77, 2.4), (81, 4)]): note(HORN, p - 12, H + sum(x[1] for x in [(74, 2), (77, 2), (79, 2), (76, 2), (77, 2.4), (81, 4)][:i]), d * .95, 86)
for i in range(4): note(DR, KICK, H + 2 + i * 2, .2, 70)
[note(HARP, p, H + 10.4 + i * .1, 3, 82) for i, p in enumerate([53, 57, 60, 65, 69, 72, 77, 81, 84])]
note(DR, CRASH, H + 10.4, 3, 84); note(TIMP, 41, H + 10.4, 3, 96)

ev.sort(key=lambda e: e[0]); tr = mido.MidiTrack(); mid.tracks.append(tr)
tr.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(BPM), time=0)); last = 0
for t, m in ev: tr.append(m.copy(time=t - last)); last = t
mid.save('assets/music.mid')
subprocess.run(['fluidsynth', '-ni', '-g', '0.55', '-r', '44100', '-o', 'synth.reverb.room-size=0.75', '-o', 'synth.reverb.level=0.6', '-F', 'assets/music.wav', '/usr/share/sounds/sf2/FluidR3_GM.sf2', 'assets/music.mid'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print('music ok')
