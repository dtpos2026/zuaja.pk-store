"""Zuaja PK brand music v2: real sampled instruments (FluidR3 GM soundfont via FluidSynth).

Desi-pop: sitar hook over I-vi-IV-V (D - Bm - G - A), electric piano, warm strings,
fingered bass, pop drums with congas (tabla feel), shaker and tambourine.
The 5-note "Zu-a-ja P-K" motif (A B D B D) closes every track on sitar + glockenspiel + bell,
on the same beats as v1 (96 BPM, motif from beat 20), so the reels stay in sync.

Needs: apt fluidsynth fluid-soundfont-gm; pip mido.
Outputs music/zuaja-jingle-15s.*, zuaja-sonic-logo-4s.*, zuaja-bed-30s.* (wav + mp3, -14 LUFS).
"""
import subprocess
from pathlib import Path

import mido

HERE = Path(__file__).resolve().parent
OUT = HERE / "music"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM = 96
TPB = 480

NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def n(s):
    return NOTE[s[:-1]] + 12 * (int(s[-1]) + 1)


# channel: (program, volume, pan, reverb, chorus)
CH = {
    "sitar": (0, 104, 122, 68, 70, 20),
    "ep": (1, 4, 74, 50, 60, 40),
    "strings": (2, 48, 62, 76, 90, 50),
    "bass": (3, 33, 82, 64, 20, 0),
    "glock": (4, 9, 82, 72, 90, 10),
    "flute": (5, 75, 70, 54, 80, 30),
    "bell": (6, 14, 70, 64, 110, 20),
    "drums": (9, 0, 110, 64, 40, 0),
}
CHORDS = {"D": ["D3", "F#3", "A3", "D4"], "Bm": ["B2", "D3", "F#3", "B3"], "G": ["G2", "B2", "D3", "G3"],
          "A": ["A2", "C#3", "E3", "A3"], "Dsus": ["D3", "G3", "A3", "D4"]}
ROOT = {"D": "D2", "Bm": "B1", "G": "G1", "A": "A1", "Dsus": "D2"}
HOOK = {  # one bar each (beats), sitar
    "D": [("F#5", 0, .75, 100), ("E5", .75, .25, 84), ("D5", 1, .5, 92), ("E5", 1.5, .5, 88), ("F#5", 2, 1, 100), ("A5", 3, 1, 104)],
    "Bm": [("F#5", 0, .5, 96), ("E5", .5, .5, 88), ("D5", 1, 1, 94), ("B4", 2, 2, 98)],
    "G": [("D5", 0, .5, 92), ("E5", .5, .5, 88), ("G5", 1, 1, 102), ("F#5", 2, .5, 92), ("E5", 2.5, .5, 88), ("D5", 3, 1, 94)],
    "A": [("E5", 0, .5, 96), ("D5", .5, .5, 88), ("C#5", 1, .5, 90), ("B4", 1.5, .5, 86), ("A4", 2, 2, 100)],
}
FLUTE = {  # answer line for the B section
    "D": [("A5", 0, 2, 70), ("F#5", 2, 2, 66)], "Bm": [("D6", 0, 2, 72), ("B5", 2, 2, 66)],
    "G": [("B5", 0, 1.5, 70), ("A5", 1.5, .5, 64), ("G5", 2, 2, 66)], "A": [("E5", 0, 1, 66), ("F#5", 1, 1, 66), ("A5", 2, 2, 72)],
}
MOTIF = [("A4", 0, .5, 104), ("B4", .5, .5, 100), ("D5", 1, 1, 110), ("B4", 2, .5, 98), ("D5", 2.5, 1.5, 114)]
K, SN, CLAP, HH, OH, SHAK, TAMB, HCON, LCON, OCON, CRASH = 36, 38, 39, 42, 46, 70, 54, 63, 64, 62, 49


class Song:
    def __init__(self):
        self.ev = []  # (beat, kind, ch, note, vel)

    def note(self, part, pitch, beat, dur, vel):
        ch = CH[part][0]
        p = pitch if isinstance(pitch, int) else n(pitch)
        self.ev.append((beat, 1, ch, p, vel)); self.ev.append((beat + dur * 0.96, 0, ch, p, 0))

    def hit(self, d, beat, vel):
        self.ev.append((beat, 1, 9, d, vel)); self.ev.append((beat + 0.1, 0, 9, d, 0))

    def bar(self, b, chord, drums="full", hook=True, flute=False, ep=True, strings=True):
        s = b * 4
        if strings:
            for p in CHORDS[chord][1:]:
                self.note("strings", n(p) + 12, s, 4, 52)
        if ep:
            for off, v in ((0.5, 70), (1.5, 58), (2.5, 66), (3.25, 54)):  # offbeat stabs
                for p in CHORDS[chord]:
                    self.note("ep", p, s + off, .4, v)
        r = n(ROOT[chord])
        for off, d, v in ((0, .9, 100), (1.5, .4, 84), (2, .9, 96), (3.5, .4, 80)):
            self.note("bass", r + (7 if off == 3.5 else 0), s + off, d, v)
        if hook and chord in HOOK:
            for p, o, d, v in HOOK[chord]:
                self.note("sitar", p, s + o, d, v)
        if flute and chord in FLUTE:
            for p, o, d, v in FLUTE[chord]:
                self.note("flute", p, s + o, d, v)
        if drums in ("full", "light", "intro"):
            for i in range(8):
                self.hit(SHAK, s + i * .5, 50 if i % 2 else 66)
        if drums in ("full", "light"):
            for i in range(8):
                self.hit(HH, s + i * .5, 76 if i % 2 == 0 else 54)
            self.hit(OH, s + 3.5, 60)
            for o, d, v in ((0, HCON, 82), (.75, LCON, 70), (1.5, OCON, 64), (2, HCON, 80), (2.5, LCON, 72), (3.25, HCON, 66), (3.5, OCON, 60)):
                self.hit(d, s + o, v - (10 if drums == "light" else 0))
        if drums == "full":
            for o in (0, 1.75, 2.5):
                self.hit(K, s + o, 110 if o == 0 else 92)
            for o in (1, 3):
                self.hit(CLAP, s + o, 100); self.hit(SN, s + o, 70)
            self.hit(TAMB, s + 1.5, 52); self.hit(TAMB, s + 3.5, 52)
        if drums == "intro":
            self.hit(LCON, s + 2, 70); self.hit(HCON, s + 2.75, 64); self.hit(HCON, s + 3.5, 70)

    def motif(self, beat, big=True):
        for p, o, d, v in MOTIF:
            self.note("sitar", p, beat + o, d, v)
            self.note("glock", n(p) + 12, beat + o, d, v - 28)
        self.note("bell", "D5", beat + 2.5, 3, 96); self.note("bell", "A5", beat + 2.52, 3, 64)
        for p in CHORDS["D"]:
            self.note("strings", n(p) + 12, beat, 6, 66)
            self.note("ep", p, beat + 2.5, 3, 62)
        self.note("bass", "D2", beat + 2.5, 3, 96)
        if big:
            self.hit(K, beat + 2.5, 112); self.hit(CRASH, beat + 2.5, 80)
            for o, d in ((0, HCON), (.5, HCON), (1, LCON), (2, OCON)):
                self.hit(d, beat + o, 78)

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


def render(song, name, secs):
    OUT.mkdir(parents=True, exist_ok=True)
    midp = OUT / f"{name}.mid"; raw = OUT / f"{name}.raw.wav"; wav = OUT / f"{name}.wav"
    song.save(midp, secs * BPM / 60)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.6", "-r", "44100", "-o", "synth.reverb.room-size=0.55",
                    "-o", "synth.reverb.level=0.5", "-F", str(raw), SF2, str(midp)], check=True)
    af = (f"atrim=0:{secs},highpass=f=35,bass=g=-4:f=110:w=0.8,treble=g=2:f=6000,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120:makeup=2,"
          f"loudnorm=I=-14:TP=-1.2:LRA=9,afade=t=out:st={secs - 0.6}:d=0.6")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ar", "44100", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(wav.with_suffix(".mp3"))], check=True)
    raw.unlink()
    print(name, "ok")


def jingle15():
    s = Song()
    s.bar(0, "Dsus", drums="intro", hook=False, ep=False)
    for p, o, d, v in (("A4", 2.5, .5, 84), ("B4", 3, .5, 90), ("D5", 3.5, .5, 96)):  # pickup slide into the hook
        s.note("sitar", p, o, d, v)
    s.hit(CRASH, 4, 76)
    for b, c in enumerate(["D", "Bm", "G", "A"], start=1):
        s.bar(b, c)
    s.motif(20)
    render(s, "zuaja-jingle-15s", 15.0)


def logo4():
    s = Song()
    for p in CHORDS["Dsus"]:
        s.note("strings", n(p) + 12, 0, 2, 50)
    s.motif(0.25)
    render(s, "zuaja-sonic-logo-4s", 4.4)


def bed30():
    s = Song()
    s.bar(0, "Dsus", drums="intro", hook=False, ep=False)
    s.bar(1, "D", drums="intro", hook=False)
    for b, c in enumerate(["D", "Bm", "G", "A"], start=2):
        s.bar(b, c)
    for b, c in enumerate(["D", "Bm", "G", "A"], start=6):
        s.bar(b, c, hook=(b % 2 == 0), flute=True)
    s.hit(CRASH, 24, 70)
    s.bar(10, "G", drums="light", hook=False, flute=False)
    s.motif(44)
    render(s, "zuaja-bed-30s", 30.0)


if __name__ == "__main__":
    jingle15(); logo4(); bed30()
