"""Zuaja PK original music (fully synthesised here, so it is 100% ours and copyright-free).

Sound: desi-modern. Tanpura drone (Sa-Pa), sitar-like Karplus-Strong plucks, synthesised tabla
(keherwa groove: dha-ge-na-ti / na-ka-dhi-na), soft shaker, warm bass and pad, bell on the logo.
Signature motif "Zu-a-ja P-K": A B D' B | D (5 notes) closes every track.
Key D (Khamaj flavour: D E F# G A B C D), 96 BPM.

Outputs (marketing/social-pack/music/):
  zuaja-jingle-15s.wav/.mp3   reel track, 6 bars + logo ending
  zuaja-sonic-logo-4s.wav/.mp3  the 5-note motif + bell, for intros/outros
  zuaja-bed-30s.wav/.mp3      longer background bed (12 bars) for posts/stories
"""
import subprocess
from pathlib import Path

import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

SR = 44100
BPM = 96
BEAT = 60 / BPM
OUT = Path(__file__).resolve().parent / "music"
rng = np.random.default_rng(11)


def hz(note):
    names = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    n, o = note[:-1], int(note[-1])
    return 440.0 * 2 ** ((names[n] + 12 * (o - 4)) / 12)


def env(n, a=0.005, d=0.3, s=0.0, r=0.05):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    e = e * (s + (1 - s) * np.exp(-np.maximum(0, t - a) / max(d, 1e-4)))
    tail = np.clip((n / SR - t) / r, 0, 1)
    return e * tail


def pluck(f, dur, bright=0.5, amp=1.0):
    """Karplus-Strong string with a little 'jawari' buzz and onset pitch slide (sitar-ish)."""
    n = int(dur * SR)
    period = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, period) * amp
    out = np.zeros(n)
    k = 0.5 + 0.49 * bright
    for i in range(n):
        out[i] = buf[i % period]
        nxt = buf[(i + 1) % period]
        buf[i % period] = 0.996 * (k * buf[i % period] + (1 - k) * nxt)
    out = np.tanh(out * 1.6) * 0.8  # buzz
    return out * env(n, 0.002, dur * 0.6, 0, 0.08)


def tanpura(dur, root="D3"):
    t = np.arange(int(dur * SR)) / SR
    y = np.zeros_like(t)
    for base, w in ((hz(root), 1.0), (hz(root) * 1.5, 0.7), (hz(root) * 2, 0.6)):
        for h in range(1, 9):
            det = 1 + rng.uniform(-0.0015, 0.0015)
            y += w * (0.6 / h) * np.sin(2 * np.pi * base * h * det * t + rng.uniform(0, 6))
    shimmer = 0.75 + 0.25 * np.sin(2 * np.pi * 0.35 * t) * np.sin(2 * np.pi * 0.11 * t + 1)
    y = sosfilt(butter(2, 110, "hp", fs=SR, output="sos"), y)
    return y * shimmer / 8


def bayan(dur=0.45):  # low tabla, pitch glide
    n = int(dur * SR); t = np.arange(n) / SR
    f = 75 + 70 * np.exp(-t * 18)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7)


def dayan(f=620, dur=0.22, ring=1.0):  # high tabla 'na'
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum((1 / k) * np.sin(2 * np.pi * f * m * t) for k, m in enumerate((1, 1.52, 2.0, 2.98), start=1))
    click = rng.uniform(-1, 1, n) * np.exp(-t * 400) * 0.4
    return (y * np.exp(-t * (14 / ring)) + click) * 0.6


def shaker(dur=0.06):
    n = int(dur * SR)
    sos = butter(2, 6000, "hp", fs=SR, output="sos")
    return sosfilt(sos, rng.uniform(-1, 1, n)) * np.exp(-np.arange(n) / SR * 60)


def bell(f, dur=2.4):
    n = int(dur * SR); t = np.arange(n) / SR
    parts = ((1, 1.0), (2.0, 0.5), (2.76, 0.35), (5.4, 0.18), (8.93, 0.08))
    return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * (1.2 + m * 0.6)) for m, a in parts) * 0.5


def pad(freqs, dur):
    t = np.arange(int(dur * SR)) / SR
    y = sum(np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2 * t) for f in freqs)
    return y * env(len(t), 0.6, 99, 1, 0.6) / len(freqs)


def add(track, sig, at, gain=1.0):
    i = int(at * SR)
    if i >= len(track): return
    j = min(len(track), i + len(sig))
    track[i:j] += sig[: j - i] * gain


def reverb(x, secs=1.6, mix=0.22):
    n = int(secs * SR)
    ir = rng.uniform(-1, 1, n) * np.exp(-np.arange(n) / SR * 4.2)
    ir[0] = 0
    wet = fftconvolve(x, ir)[: len(x)]
    wet = wet / (np.abs(wet).max() + 1e-9) * np.abs(x).max()
    return x * (1 - mix) + wet * mix


CHORDS = {  # I - IV - V - I  (D, G, A, D)
    "D": (["D3", "F#3", "A3"], "D2"), "G": (["G3", "B3", "D4"], "G1"), "A": (["A3", "C#4", "E4"], "A1"),
    "Bm": (["B3", "D4", "F#4"], "B1"),
}
MOTIF = [("A4", 0.5), ("B4", 0.5), ("D5", 1.0), ("B4", 0.5), ("D5", 1.5)]  # "Zu-a-ja P-K"
MELODY_A = [("D5", .5), ("E5", .5), ("F#5", 1), ("E5", .5), ("D5", .5), ("B4", 1),
            ("A4", .5), ("B4", .5), ("D5", 1), ("E5", 1), ("D5", 1),
            ("F#5", .5), ("G5", .5), ("A5", 1), ("G5", .5), ("F#5", .5), ("E5", 1),
            ("D5", .5), ("E5", .5), ("F#5", .5), ("E5", .5), ("D5", 2)]


def groove(track, start, bars, intensity=1.0):
    # keherwa feel on eighths: dha ge na ti | na ka dhi na
    pat = [("dha", 1.0), ("ge", .6), ("na", .8), ("ti", .5), ("na", .8), ("ka", .5), ("dhi", .9), ("na", .7)]
    for b in range(bars):
        for i, (bol, g) in enumerate(pat):
            t = start + b * 4 * BEAT + i * BEAT / 2
            if bol in ("dha", "dhi", "ge"):
                add(track, bayan(), t, 0.36 * g * intensity)
            if bol in ("dha", "na", "dhi"):
                add(track, dayan(620 if bol != "dhi" else 560), t, 0.32 * g * intensity)
            if bol in ("ti", "ka"):
                add(track, dayan(900, 0.08, 0.5), t, 0.18 * intensity)
        for s in range(16):
            add(track, shaker(), start + b * 4 * BEAT + s * BEAT / 4, (0.05 if s % 2 else 0.08) * intensity)


def harmony(track, start, prog):
    for i, ch in enumerate(prog):
        notes, bass = CHORDS[ch]
        t = start + i * 4 * BEAT
        add(track, pad([hz(n) for n in notes], 4 * BEAT + 0.4), t, 0.05)
        for k in (0, 2.5, 3):  # bass rhythm
            n = int((1.2 if k == 0 else 0.6) * SR); tt = np.arange(n) / SR
            add(track, np.sin(2 * np.pi * hz(bass) * 2 * tt) * np.exp(-tt * 3), t + k * BEAT, 0.14)


def melody(track, start, notes, gain=0.46):
    t = start
    for n, beats in notes:
        add(track, pluck(hz(n), max(0.4, beats * BEAT + 0.3), 0.55), t, gain)
        t += beats * BEAT
    return t


def motif_end(track, t):
    end = melody(track, t, MOTIF, 0.55)
    add(track, bell(hz("D5")), t + 2.5 * BEAT, 0.28)
    add(track, bell(hz("A5")), t + 2.5 * BEAT + 0.02, 0.12)
    return end


def master(track, name):
    track = reverb(track)
    sos = butter(1, 30, "hp", fs=SR, output="sos"); track = sosfilt(sos, track)
    track = np.tanh(track / (np.abs(track).max() + 1e-9) * 1.2) / np.tanh(1.2) * 0.89  # gentle glue, peak ~ -1 dB
    n = len(track); fade = int(0.04 * SR); track[:fade] *= np.linspace(0, 1, fade)
    OUT.mkdir(parents=True, exist_ok=True)
    wav = OUT / f"{name}.wav"
    import wave
    st = np.stack([track, np.roll(track, 220) * 0.98], 1)  # slight stereo width
    with wave.open(str(wav), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "192k", str(wav.with_suffix(".mp3"))], check=True)
    print(name, f"{n / SR:.1f}s peak {np.abs(track).max():.2f}")


def jingle15():
    dur = 15.0; tr = np.zeros(int(dur * SR))
    add(tr, tanpura(dur), 0, 0.35)
    harmony(tr, 0, ["D", "G", "A", "D", "Bm"])
    groove(tr, 1 * BEAT * 4, 4)          # drums enter in bar 2
    melody(tr, 0, MELODY_A[:6])
    melody(tr, 4 * BEAT * 2, MELODY_A[11:22])
    motif_end(tr, 20 * BEAT)             # bars 6-7: the Zuaja motif + bell
    master(tr, "zuaja-jingle-15s")


def logo4():
    dur = 4.2; tr = np.zeros(int(dur * SR))
    add(tr, tanpura(dur), 0, 0.3)
    add(tr, pad([hz(n) for n in CHORDS["D"][0]], dur), 0, 0.06)
    add(tr, bayan(), 0, 0.4)
    motif_end(tr, 0.15)
    master(tr, "zuaja-sonic-logo-4s")


def bed30():
    bars = 12; dur = bars * 4 * BEAT + 2.5; tr = np.zeros(int(dur * SR))
    add(tr, tanpura(dur), 0, 0.32)
    harmony(tr, 0, ["D", "G", "A", "D", "Bm", "G", "A", "D", "D", "G", "A", "D"])
    groove(tr, 2 * 4 * BEAT, 9, 0.85)
    melody(tr, 4 * 4 * BEAT, MELODY_A, 0.42)
    motif_end(tr, 11 * 4 * BEAT)
    master(tr, "zuaja-bed-30s")


if __name__ == "__main__":
    jingle15(); logo4(); bed30()
