"""Zuaja PK music v4: "aura" cinematic trailer (Hollywood/Bollywood action feel) for video ads and reels.

96 BPM, D minor, 24 beats = 15 s (same grid as before, so all reel cuts land on beats).
Layers:
  - FluidSynth (FluidR3 GM): staccato string ostinato, brass "braam" stabs, choir aahs, taiko/toms, timpani,
    808-style synth bass, trap hats, tubular bell.
  - Synthesised FX mixed in numpy: big BOOM impacts ("taun") on every bar downbeat, whoosh risers into
    each hit, a sub-drop, a clock tick in the intro.
  - Sonic logo on beat 20: the Zuaja motif (degrees 5-6-8-6-8 -> A Bb D Bb D) on brass + strings + bell,
    with the biggest impact on its last note (beat 22.5).
Outputs music/aura/zuaja-aura-15s.*, zuaja-aura-logo-4s.*, zuaja-aura-30s.* (wav + mp3, ~-12 LUFS punchy master).
"""
import subprocess
import wave
from pathlib import Path

import mido
import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

HERE = Path(__file__).resolve().parent
OUT = HERE / "music/aura"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
BPM, TPB, SR = 96, 480, 44100
BEAT = 60 / BPM
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
rng = np.random.default_rng(7)


def n(s):
    return NOTE[s[:-1]] + 12 * (int(s[-1]) + 1)


CH = {  # name: (channel, program, volume, pan, reverb)
    "strings": (0, 48, 104, 64, 70), "brass": (1, 61, 110, 64, 80), "choir": (2, 52, 84, 64, 100),
    "bass": (3, 38, 112, 64, 20), "timp": (4, 47, 110, 64, 70), "bell": (5, 14, 90, 64, 110),
    "trombone": (6, 57, 100, 64, 70), "drums": (9, 0, 112, 64, 50),
}
KICK, TOM_L, TOM_F, HH, OH, SNARE, CLAP, CRASH = 36, 41, 43, 42, 46, 38, 39, 49
PROG = ["Dm", "Bb", "Gm", "A"]
CHORD = {"Dm": ["D3", "F3", "A3"], "Bb": ["Bb2", "D3", "F3"], "Gm": ["G2", "Bb2", "D3"], "A": ["A2", "C#3", "E3"]}
ROOT = {"Dm": "D1", "Bb": "Bb0", "Gm": "G1", "A": "A1"}
MOTIF = [("A4", 0, .5), ("Bb4", .5, .5), ("D5", 1, 1), ("Bb4", 2, .5), ("D5", 2.5, 1.5)]


class Song:
    def __init__(self): self.ev = []; self.hits = []; self.risers = []

    def note(self, part, p, beat, dur, vel):
        ch = CH[part][0]; p = p if isinstance(p, int) else n(p)
        self.ev += [(beat, 1, ch, p, vel), (beat + dur * .97, 0, ch, p, 0)]

    def drum(self, d, beat, vel):
        self.ev += [(beat, 1, 9, d, vel), (beat + .1, 0, 9, d, 0)]

    def boom(self, beat, size=1.0):
        self.hits.append((beat, size)); self.risers.append((beat, min(2.0, 2 * size)))
        self.drum(KICK, beat, 127); self.drum(TOM_F, beat, 120); self.drum(CRASH, beat, 100)
        self.note("timp", "D2", beat, 2, 127)

    def bar(self, b, ch, full=True, braam=False):
        s = b * 4
        notes = [n(p) for p in CHORD[ch]]
        for i in range(16 if full else 8):  # staccato ostinato (16ths when full)
            st = s + i * (.25 if full else .5)
            p = notes[[0, 0, 2, 0, 1, 0, 2, 1][i % 8]] + 12
            self.note("strings", p, st, .2, 96 if i % 4 == 0 else 76)
        for p in notes:
            self.note("choir", p + 12, s, 4, 70)
        r = n(ROOT[ch]) + 12
        for o, d, v in ((0, 1.4, 120), (1.5, .4, 100), (2.5, 1.2, 116)):
            self.note("bass", r, s + o, d, v)
        if braam:
            for p in notes:
                self.note("brass", p, s, 1.6, 118); self.note("trombone", p - 12, s, 1.6, 116)
        if full:
            for o in (0, 0.75, 1.5, 2.5, 3.25):
                self.drum(TOM_L if o % 1 else KICK, s + o, 110)
            for o in (1, 3):
                self.drum(SNARE, s + o, 104); self.drum(CLAP, s + o, 96)
            for i in range(16):
                self.drum(HH, s + i * .25, (84, 50, 66, 50)[i % 4])
            for i in range(6):  # trap roll at the end of the bar
                self.drum(HH, s + 3.5 + i / 12, 60 + i * 6)

    def motif(self, beat):
        for p, o, d in MOTIF:
            self.note("brass", p, beat + o, d, 120); self.note("strings", n(p) + 12, beat + o, d, 110)
            self.drum(TOM_F, beat + o, 100)
        self.note("bell", "D5", beat + 2.5, 3.5, 120)
        for p in CHORD["Dm"]:
            self.note("choir", n(p) + 12, beat, 6, 90); self.note("trombone", p, beat + 2.5, 3, 118)
        self.note("bass", "D2", beat + 2.5, 3.5, 124)
        self.boom(beat + 2.5, 1.4)

    def save(self, path, beats):
        mid = mido.MidiFile(ticks_per_beat=TPB); tr = mido.MidiTrack(); mid.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM), time=0))
        for name, (ch, prog, vol, pan, rev) in CH.items():
            if ch != 9: tr.append(mido.Message("program_change", channel=ch, program=prog, time=0))
            for cc, val in ((7, vol), (10, pan), (91, rev)):
                tr.append(mido.Message("control_change", channel=ch, control=cc, value=val, time=0))
        last = 0
        for beat, kind, ch, p, v in sorted(self.ev, key=lambda e: (e[0], e[1])):
            t = int(round(beat * TPB)); dt = max(0, t - last); last = t
            tr.append(mido.Message("note_on" if kind else "note_off", channel=ch, note=p, velocity=v, time=dt))
        tr.append(mido.MetaMessage("end_of_track", time=max(0, int(beats * TPB) - last)))
        mid.save(path)


# ---------- synthesised FX ----------
def fx_boom(size):
    d = 2.6; t = np.arange(int(d * SR)) / SR
    f = 32 + 90 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    click = rng.uniform(-1, 1, len(t)) * np.exp(-t * 60)
    noise = sosfilt(butter(2, 900, "lp", fs=SR, output="sos"), rng.uniform(-1, 1, len(t))) * np.exp(-t * 5) * 0.8
    y = np.tanh((body * 1.4 + click * 0.5 + noise) * 1.6) * size
    ir = rng.uniform(-1, 1, int(2.2 * SR)) * np.exp(-np.arange(int(2.2 * SR)) / SR * 2.4)
    tail = fftconvolve(y, ir)[: len(y)]; tail /= np.abs(tail).max() + 1e-9
    return y * 0.8 + tail * 0.35 * size


def fx_whoosh(length):
    """Riser: band-passed noise swelling up + a rising tone, ends exactly on the hit."""
    t = np.arange(int(length * SR)) / SR
    noise = sosfilt(butter(2, [900, 9000], "bp", fs=SR, output="sos"), rng.uniform(-1, 1, len(t)))
    f = 180 + 900 * (t / length) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    env = (t / length) ** 2.4
    return (noise * 0.9 + tone) * env


def fx_tick():
    t = np.arange(int(0.05 * SR)) / SR
    return np.sin(2 * np.pi * 3000 * t) * np.exp(-t * 120) * 0.35


def add(track, sig, at):
    i = int(at * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(len(track), i + len(sig)); track[i:j] += sig[: j - i]


def render(song, name, secs, ticks=0):
    OUT.mkdir(parents=True, exist_ok=True)
    midp, raw, wav = OUT / f"{name}.mid", OUT / f"{name}.raw.wav", OUT / f"{name}.wav"
    song.save(midp, secs * BPM / 60)
    subprocess.run(["fluidsynth", "-ni", "-q", "-g", "0.5", "-r", str(SR), "-o", "synth.reverb.room-size=0.8",
                    "-o", "synth.reverb.level=0.55", "-F", str(raw), "-T", "wav", "-O", "s16", SF2, str(midp)], check=True)
    with wave.open(str(raw)) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).astype(np.float32) / 32768
    x = x[: int(secs * SR)]
    if len(x) < int(secs * SR): x = np.pad(x, ((0, int(secs * SR) - len(x)), (0, 0)))
    music = x / (np.abs(x).max() + 1e-9) * 0.6
    fx = np.zeros(len(music))
    for beat, size in song.hits: add(fx, fx_boom(size) * 0.85, beat * BEAT)
    for beat, length in song.risers: w_ = fx_whoosh(length * BEAT) * 0.35; add(fx, w_, beat * BEAT - len(w_) / SR)
    for i in range(ticks): add(fx, fx_tick(), i * BEAT / 2)
    mix = music + fx[:, None]
    pre = OUT / f"{name}.mix.wav"
    with wave.open(str(pre), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(mix / (np.abs(mix).max() + 1e-9) * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())
    af = (f"highpass=f=25,bass=g=2:f=60:w=0.7,treble=g=3:f=7000,"
          f"acompressor=threshold=-16dB:ratio=3:attack=5:release=120:makeup=2,"
          f"loudnorm=I=-12:TP=-1.0:LRA=9,afade=t=out:st={secs - 0.5}:d=0.5")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(pre), "-af", af, "-ar", str(SR), str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(wav.with_suffix(".mp3"))], check=True)
    raw.unlink(); pre.unlink(); print(name, "ok")


def intro(s):
    for p in ("D2", "A2"):
        s.note("choir", p, 0, 4, 60)
    s.note("bass", "D1", 0, 4, 90)
    s.drum(TOM_F, 2, 70); s.drum(TOM_F, 3, 84); s.drum(TOM_F, 3.5, 96)


def aura15():
    s = Song(); intro(s)
    for b, c in enumerate(PROG, start=1):
        s.boom(b * 4, 1.0 if b in (1, 3) else 0.7)
        s.bar(b, c, full=True, braam=(b in (1, 3)))
    s.motif(20)
    render(s, "zuaja-aura-15s", 15.0, ticks=8)


def logo4():
    s = Song()
    s.note("choir", "D3", 0, 3, 60)
    s.motif(0.5)
    render(s, "zuaja-aura-logo-4s", 4.6)


def aura30():
    s = Song(); intro(s)
    s.bar(1, "Dm", full=False); s.boom(4, 0.8)
    for b, c in enumerate(PROG, start=2):
        s.boom(b * 4, 0.9); s.bar(b, c, braam=(b % 2 == 0))
    for b, c in enumerate(PROG, start=6):
        s.boom(b * 4, 1.0); s.bar(b, c, braam=True)
    s.bar(10, "A", full=False)
    s.motif(44)
    render(s, "zuaja-aura-30s", 30.0, ticks=8)


if __name__ == "__main__":
    aura15(); logo4(); aura30()
