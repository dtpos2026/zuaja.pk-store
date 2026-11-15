"""Zuaja PK brand music v3: international beauty-brand identity (luxury cosmetics ad feel).

Modern, elegant R&B-pop at 96 BPM in F major: grand piano maj7 voicings, celesta/music-box hook,
airy 'ooh' vocal pad, warm synth pad, slow strings, smooth synth bass, finger snaps + claps,
glossy 16th hats, soft kick, reverse-cymbal swells into the drop and into the logo.
Sonic logo "Zu-a-ja P-K" = C5 D5 F5 D5 F5 (same rhythm and beats as before: motif from beat 20),
on piano + celesta + crystal bell over Fmaj9, so the reels stay in sync.
Real sampled instruments via FluidSynth + FluidR3 GM soundfont. Mastered to -14 LUFS.
"""
import subprocess
from pathlib import Path

import mido

HERE = Path(__file__).resolve().parent
OUT = HERE / "music"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM, TPB = 96, 480
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}


def n(s):
    return NOTE[s[:-1]] + 12 * (int(s[-1]) + 1)


# name: (channel, program, volume, pan, reverb, chorus)
CH = {
    "piano": (0, 0, 100, 60, 70, 20),
    "celesta": (1, 8, 92, 74, 90, 30),
    "box": (2, 10, 70, 50, 95, 20),
    "ooh": (3, 53, 66, 64, 110, 60),
    "pad": (4, 89, 60, 64, 100, 70),
    "strings": (5, 49, 58, 70, 100, 40),
    "bass": (6, 38, 84, 64, 10, 0),
    "bell": (7, 14, 78, 66, 115, 30),
    "swell": (8, 119, 70, 64, 80, 0),
    "drums": (9, 0, 104, 64, 35, 0),
}
CH9 = {"kick": 36, "snap": 39, "clap": 39, "rim": 37, "hh": 42, "oh": 46, "shaker": 70, "crash": 49, "chime": 84}
CHORD = {  # piano voicings (rich, open)
    "Fmaj7": ["F3", "C4", "E4", "A4"], "Am7": ["A2", "E3", "G3", "C4"], "Dm7": ["D3", "A3", "C4", "F4"],
    "Bbmaj7": ["Bb2", "F3", "A3", "D4"], "Fmaj9": ["F3", "C4", "E4", "G4", "A4"], "C6": ["C3", "G3", "A3", "E4"],
}
ROOT = {"Fmaj7": "F1", "Am7": "A1", "Dm7": "D2", "Bbmaj7": "Bb1", "Fmaj9": "F1", "C6": "C2"}
HOOK = {
    "Fmaj7": [("A5", 0, 1), ("G5", 1, .5), ("F5", 1.5, .5), ("E5", 2, 1), ("C5", 3, 1)],
    "Am7": [("E5", 0, .5), ("G5", .5, .5), ("A5", 1, 1), ("G5", 2, 1), ("E5", 3, 1)],
    "Dm7": [("F5", 0, .5), ("E5", .5, .5), ("D5", 1, 1), ("A4", 2, 1), ("C5", 3, 1)],
    "Bbmaj7": [("D5", 0, 1), ("C5", 1, .5), ("Bb4", 1.5, .5), ("A4", 2, 2)],
}
MOTIF = [("C5", 0, .5), ("D5", .5, .5), ("F5", 1, 1), ("D5", 2, .5), ("F5", 2.5, 1.5)]


class Song:
    def __init__(self): self.ev = []

    def note(self, part, p, beat, dur, vel):
        ch = CH[part][0]; p = p if isinstance(p, int) else n(p)
        self.ev += [(beat, 1, ch, p, vel), (beat + dur * 0.97, 0, ch, p, 0)]

    def hit(self, name, beat, vel):
        d = CH9[name]; self.ev += [(beat, 1, 9, d, vel), (beat + .1, 0, 9, d, 0)]

    def chord(self, part, name, beat, dur, vel, up=0):
        for p in CHORD[name]:
            self.note(part, n(p) + up, beat, dur, vel)

    def bar(self, b, ch, drums=True, hook=True, ooh=False, arp=False):
        s = b * 4
        self.chord("piano", ch, s, 1.9, 70); self.chord("piano", ch, s + 2.5, 1.4, 58)
        self.chord("pad", ch, s, 4, 54, 12)
        self.chord("strings", ch, s, 4, 44, 12)
        r = n(ROOT[ch])
        for o, d, v in ((0, 1.4, 96), (1.75, .5, 80), (2.5, 1.2, 90)):
            self.note("bass", r + 12, s + o, d, v)
        if arp:  # music-box shimmer
            notes = [n(p) + 24 for p in CHORD[ch]]
            for i in range(8):
                self.note("box", notes[i % len(notes)], s + i * .5, .5, 58)
        if hook and ch in HOOK:
            for p, o, d in HOOK[ch]:
                self.note("celesta", p, s + o, d, 96); self.note("piano", n(p) + 12, s + o, d, 52)
        if ooh and ch in HOOK:
            for p, o, d in HOOK[ch][::2]:
                self.note("ooh", n(p), s + o, d * 2, 70)
        if drums:
            for o, v in ((0, 104), (1.75, 74), (2.5, 92)):
                self.hit("kick", s + o, v)
            for o in (1, 3):
                self.hit("snap", s + o, 92); self.hit("clap", s + o + .01, 70)
            for i in range(16):
                self.hit("hh", s + i * .25, (76, 44, 60, 44)[i % 4])
            self.hit("oh", s + 3.5, 46); self.hit("rim", s + 2.75, 40)
            for i in range(8):
                self.hit("shaker", s + i * .5, 36 if i % 2 else 44)

    def swell(self, end_beat, length=2):
        self.note("swell", "C4", end_beat - length, length, 82)

    def motif(self, beat):
        self.swell(beat, 2)
        for p, o, d in MOTIF:
            self.note("piano", p, beat + o, d, 96); self.note("celesta", n(p) + 12, beat + o, d, 92)
        self.note("bell", "F5", beat + 2.5, 3.5, 100); self.note("bell", "C6", beat + 2.53, 3.5, 70)
        self.chord("ooh", "Fmaj9", beat, 6, 72, 12); self.chord("pad", "Fmaj9", beat, 6, 60, 12)
        self.chord("piano", "Fmaj9", beat + 2.5, 3.5, 74)
        self.note("bass", "F2", beat + 2.5, 3.5, 92)
        self.hit("chime", beat + 2.5, 70); self.hit("kick", beat + 2.5, 96)
        for o in (0, 1): self.hit("snap", beat + o + .5, 60)

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
    midp, raw, wav = OUT / f"{name}.mid", OUT / f"{name}.raw.wav", OUT / f"{name}.wav"
    song.save(midp, secs * BPM / 60)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.55", "-r", "44100", "-o", "synth.reverb.room-size=0.7",
                    "-o", "synth.reverb.width=1.0", "-o", "synth.reverb.level=0.6", "-o", "synth.chorus.level=1.2",
                    "-F", str(raw), SF2, str(midp)], check=True)
    af = (f"atrim=0:{secs},highpass=f=32,bass=g=-2:f=100:w=0.8,treble=g=5:f=7000,"
          f"acompressor=threshold=-20dB:ratio=2.2:attack=10:release=150:makeup=2,"
          f"extrastereo=m=1.25,loudnorm=I=-14:TP=-1.2:LRA=8,afade=t=out:st={secs - 0.7}:d=0.7")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ar", "44100", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(wav.with_suffix(".mp3"))], check=True)
    raw.unlink(); print(name, "ok")


def intro(s):
    s.chord("pad", "Fmaj7", 0, 4, 50, 12); s.chord("ooh", "Fmaj7", 0, 4, 46, 12)
    for i, p in enumerate(["F4", "A4", "C5", "E5", "A5", "C6"]):  # rising piano sparkle
        s.note("piano", p, i * .5, 1.5, 54 + i * 6)
    s.note("celesta", "E6", 3, 1, 70)
    s.swell(4, 2); s.hit("crash", 4, 64)


def jingle15():
    s = Song(); intro(s)
    for b, c in enumerate(["Fmaj7", "Am7", "Dm7", "Bbmaj7"], start=1):
        s.bar(b, c, arp=(b >= 3))
    s.motif(20)
    render(s, "zuaja-jingle-15s", 15.0)


def logo4():
    s = Song()
    s.chord("pad", "Fmaj9", 0, 3, 46, 12)
    s.motif(0.5)
    render(s, "zuaja-sonic-logo-4s", 4.6)


def bed30():
    s = Song(); intro(s)
    s.bar(1, "Fmaj7", drums=False, hook=False, arp=True)
    for b, c in enumerate(["Fmaj7", "Am7", "Dm7", "Bbmaj7"], start=2):
        s.bar(b, c)
    s.hit("crash", 24, 60)
    for b, c in enumerate(["Fmaj7", "Am7", "Dm7", "Bbmaj7"], start=6):
        s.bar(b, c, hook=(b % 2 == 0), ooh=True, arp=True)
    s.bar(10, "C6", drums=False, hook=False, arp=True)
    s.motif(44)
    render(s, "zuaja-bed-30s", 30.0)


if __name__ == "__main__":
    jingle15(); logo4(); bed30()
