"""Zuaja PK music v5: upbeat e-commerce COMMERCIAL ad music (Daraz / Amazon / TikTok-Shop style).

Happy, bright, catchy: G major, I-V-vi-IV (G-D-Em-C), 96 BPM with a double-time groove
(four-on-the-floor kick, claps on 2 & 4, 16th hats, tambourine, shaker), whistle + marimba hook,
nylon-guitar offbeat strums, bright piano stabs, pizzicato, bouncy synth bass, glockenspiel sparkle,
short whooshes into the drop and the logo. Same grid as before (24 beats = 15 s, logo motif from beat 20),
so every reel cut lands on a beat. Sonic logo = degrees 5-6-8-6-8 -> D E G E G on glockenspiel + whistle + "ding".
Outputs music/commercial/zuaja-commercial-15s.*, -logo-4s.*, -30s.* (wav, mp3, mid), mastered to ~-13 LUFS.
"""
import subprocess
import wave
from pathlib import Path

import mido
import numpy as np
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
OUT = HERE / "music/commercial"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM, TPB, SR = 96, 480, 44100
BEAT = 60 / BPM
NOTE = {"C": 0, "C#": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
rng = np.random.default_rng(3)


def n(s):
    return NOTE[s[:-1]] + 12 * (int(s[-1]) + 1)


CH = {  # name: (channel, program, volume, pan, reverb, chorus)
    "whistle": (0, 78, 96, 70, 50, 20), "marimba": (1, 12, 100, 54, 40, 10), "guitar": (2, 24, 84, 80, 40, 30),
    "piano": (3, 1, 82, 60, 45, 20), "pizz": (4, 45, 78, 44, 40, 10), "bass": (5, 38, 104, 64, 10, 0),
    "glock": (6, 9, 92, 70, 70, 20), "strings": (7, 49, 56, 64, 80, 40), "drums": (9, 0, 118, 64, 25, 0),
}
KICK, CLAP, SNARE, HH, OH, TAMB, SHAK, CRASH, SNAP = 36, 39, 38, 42, 46, 54, 70, 49, 37
PROG = ["G", "D", "Em", "C"]
CHORD = {"G": ["G3", "B3", "D4"], "D": ["D3", "F#3", "A3"], "Em": ["E3", "G3", "B3"], "C": ["C3", "E3", "G3"]}
ROOT = {"G": "G1", "D": "D2", "Em": "E2", "C": "C2"}
HOOK = {  # whistle / marimba hook, one bar each
    "G": [("D5", 0, .5), ("G5", .5, .5), ("B5", 1, .75), ("A5", 1.75, .25), ("G5", 2, 1), ("D5", 3, .5), ("E5", 3.5, .5)],
    "D": [("F#5", 0, .5), ("A5", .5, .5), ("D6", 1, .75), ("C#6", 1.75, .25), ("A5", 2, 1.5), ("F#5", 3.5, .5)],
    "Em": [("G5", 0, .5), ("B5", .5, .5), ("E6", 1, .75), ("D6", 1.75, .25), ("B5", 2, 1), ("G5", 3, .5), ("A5", 3.5, .5)],
    "C": [("E5", 0, .5), ("G5", .5, .5), ("C6", 1, .5), ("B5", 1.5, .5), ("A5", 2, .5), ("G5", 2.5, .5), ("D5", 3, 1)],
}
MOTIF = [("D5", 0, .5), ("E5", .5, .5), ("G5", 1, 1), ("E5", 2, .5), ("G5", 2.5, 1.5)]


class Song:
    def __init__(self): self.ev = []; self.whoosh = []

    def note(self, part, p, beat, dur, vel):
        ch = CH[part][0]; p = p if isinstance(p, int) else n(p)
        self.ev += [(beat, 1, ch, p, vel), (beat + dur * .95, 0, ch, p, 0)]

    def drum(self, d, beat, vel):
        self.ev += [(beat, 1, 9, d, vel), (beat + .1, 0, 9, d, 0)]

    def bar(self, b, ch, drums="full", hook="whistle", arp=True):
        s = b * 4
        for o in (0.5, 1.5, 2.5, 3.5):  # offbeat guitar strums
            for k, p in enumerate(CHORD[ch]):
                self.note("guitar", n(p) + 12, s + o + k * 0.02, .35, 76)
        for o in (0, 1.75, 2.5):
            for p in CHORD[ch]:
                self.note("piano", n(p) + 12, s + o, .4, 70)
        for p in CHORD[ch]:
            self.note("strings", n(p) + 12, s, 4, 48)
        r = n(ROOT[ch]) + 12
        for o, oct_ in ((0, 0), (0.75, 12), (1.5, 0), (2, 0), (2.75, 12), (3.5, 0)):  # bouncy octave bass
            self.note("bass", r + oct_, s + o, .35, 104)
        if arp:
            notes = [n(p) + 12 for p in CHORD[ch]]
            for i in range(8):
                self.note("pizz", notes[i % 3] + (12 if i % 4 == 3 else 0), s + i * .5, .3, 70)
        if hook and ch in HOOK:
            for p, o, d in HOOK[ch]:
                self.note(hook, p, s + o, d, 100)
                if hook == "whistle": self.note("marimba", n(p) - 12, s + o, d, 74)
        if drums == "full":
            for i in range(4): self.drum(KICK, s + i, 118)
            self.drum(KICK, s + 3.75, 90)
            for o in (1, 3): self.drum(CLAP, s + o, 112); self.drum(SNARE, s + o, 70)
            for i in range(16): self.drum(HH, s + i * .25, (70, 46, 60, 46)[i % 4])
            for o in (.5, 1.5, 2.5, 3.5): self.drum(OH, s + o, 52)
            for i in range(8): self.drum(TAMB, s + i * .5, 58 if i % 2 else 40)
        elif drums == "light":
            for o in (1, 3): self.drum(SNAP, s + o, 90)
            for i in range(8): self.drum(SHAK, s + i * .5, 54)

    def motif(self, beat):
        self.whoosh.append(beat)
        for p, o, d in MOTIF:
            self.note("glock", n(p) + 12, beat + o, d, 118); self.note("whistle", p, beat + o, d, 96)
            self.note("marimba", n(p) - 12, beat + o, d, 90)
        for p in CHORD["G"]:
            self.note("piano", n(p) + 12, beat + 2.5, 3, 96); self.note("strings", n(p) + 12, beat + 2.5, 3.5, 80)
        self.note("bass", "G2", beat + 2.5, 2, 110)
        self.drum(KICK, beat + 2.5, 124); self.drum(CRASH, beat + 2.5, 96); self.drum(CLAP, beat + 2.5, 110)
        for o in (0, .5, 1, 2): self.drum(CLAP, beat + o, 96)

    def save(self, path, beats):
        mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
        for name, (ch, prog, vol, pan, rev, cho) in CH.items():
            if ch != 9: tr.append(mido.Message("program_change", channel=ch, program=prog, time=0))
            for cc, val in ((7, vol), (10, pan), (91, rev), (93, cho)):
                tr.append(mido.Message("control_change", channel=ch, control=cc, value=val, time=0))
        last = 0
        for beat, kind, ch, p, v in sorted(self.ev, key=lambda e: (e[0], e[1])):
            t = int(round(beat * TPB)); dt = max(0, t - last); last = t
            tr.append(mido.Message("note_on" if kind else "note_off", channel=ch, note=p, velocity=v, time=dt))
        tr.append(mido.MetaMessage("end_of_track", time=max(0, int(beats * TPB) - last)))
        mid.save(path)


def fx_whoosh(length):
    t = np.arange(int(length * SR)) / SR
    noise = sosfilt(butter(2, [1200, 10000], "bp", fs=SR, output="sos"), rng.uniform(-1, 1, len(t)))
    return noise * (t / length) ** 2.5 * 0.5


def fx_ding():
    t = np.arange(int(1.6 * SR)) / SR; f = 1567.98  # G6
    return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * (2.5 + m)) for m, a in ((1, .6), (2.0, .25), (3.0, .12)))


def render(song, name, secs, dings=()):
    OUT.mkdir(parents=True, exist_ok=True)
    midp, raw, wav = OUT / f"{name}.mid", OUT / f"{name}.raw.wav", OUT / f"{name}.wav"
    song.save(midp, secs * BPM / 60)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.55", "-r", str(SR), "-o", "synth.reverb.room-size=0.4",
                    "-o", "synth.reverb.level=0.4", "-F", str(raw), "-T", "wav", "-O", "s16", SF2, str(midp)], check=True)
    with wave.open(str(raw)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768
    L = int(secs * SR); x = x[:L]
    if len(x) < L: x = np.pad(x, ((0, L - len(x)), (0, 0)))
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    fx = np.zeros(L)
    for b in song.whoosh:
        w_ = fx_whoosh(2 * BEAT); i = int(b * BEAT * SR) - len(w_)
        if i >= 0: fx[i:i + len(w_)] += w_
    for b in dings:
        d = fx_ding(); i = int(b * BEAT * SR); j = min(L, i + len(d)); fx[i:j] += d[: j - i] * 0.5
    mix = x + fx[:, None]
    pre = OUT / f"{name}.mix.wav"
    with wave.open(str(pre), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix / (np.abs(mix).max() + 1e-9) * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())
    af = (f"highpass=f=30,bass=g=-1:f=90:w=0.8,treble=g=4:f=8000,"
          f"acompressor=threshold=-18dB:ratio=3:attack=6:release=100:makeup=2,extrastereo=m=1.2,"
          f"loudnorm=I=-13:TP=-1.0:LRA=7,afade=t=out:st={secs - 0.5}:d=0.5")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pre), "-af", af, "-ar", str(SR), str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(wav.with_suffix(".mp3"))], check=True)
    raw.unlink(); pre.unlink(); print(name, "ok")


def intro(s):
    # bar 0: claps + snaps build, marimba pickup, whoosh into the drop on beat 4
    for o in (0, 1, 2, 3): s.drum(SNAP, o, 80)
    for o in (2, 2.5, 3, 3.25, 3.5, 3.75): s.drum(CLAP, o, 70 + int(o * 10))
    for p, o in (("D5", 2.5), ("E5", 3), ("F#5", 3.5)): s.note("marimba", p, o, .5, 96)
    s.whoosh.append(4); s.drum(CRASH, 4, 96)


def commercial15():
    s = Song(); intro(s)
    for b, c in enumerate(PROG, start=1):
        s.bar(b, c, hook="whistle" if b % 2 else "marimba")
    s.motif(20)
    render(s, "zuaja-commercial-15s", 15.0, dings=(22.5,))


def logo4():
    s = Song()
    for o in (0, .5): s.drum(SNAP, o, 80)
    s.motif(0.5)
    render(s, "zuaja-commercial-logo-4s", 4.6, dings=(3.0,))


def commercial30():
    s = Song(); intro(s)
    s.bar(1, "G", drums="light", hook=None)
    for b, c in enumerate(PROG, start=2):
        s.bar(b, c, hook="whistle")
    s.drum(CRASH, 24, 90)
    for b, c in enumerate(PROG, start=6):
        s.bar(b, c, hook="marimba" if b % 2 else "whistle")
    s.bar(10, "C", drums="light", hook=None)
    s.motif(44)
    render(s, "zuaja-commercial-30s", 30.0, dings=(46.5,))


if __name__ == "__main__":
    commercial15(); logo4(); commercial30()
