"""Original, copyright-free background music for reels (generated in code, so no licensing issues).

Moods:
  dreamy    - soft pads + bell melody, slow (reassurance, soulmate, birth month)
  playful   - plucky chords + light beat, upbeat (memes, 6-vs-6 splits)
  emotional - piano-like arpeggio + warm pad (deep/love reels)

usage: python3 reelgen/music.py <mood> <seconds> <out.wav> [seed]
"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}

def hz(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)

PROGS = {  # chord roots (minor/major marked) per mood
    "dreamy":    [("F", "maj7"), ("A", "m7"), ("D", "m7"), ("C", "add9")],
    "playful":   [("C", "maj"), ("G", "maj"), ("A", "m"), ("F", "maj")],
    "emotional": [("A", "m"), ("F", "maj7"), ("C", "maj"), ("G", "sus2")],
}
SHAPES = {"maj": [0, 4, 7], "m": [0, 3, 7], "maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10],
          "add9": [0, 4, 7, 14], "sus2": [0, 2, 7]}
BPM = {"dreamy": 72, "playful": 112, "emotional": 80}

def env(n, a, r):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    if ai: e[:ai] = np.linspace(0, 1, ai)
    if ri: e[-ri:] *= np.linspace(1, 0, ri)
    return e

def tone(f, dur, kind="pad", rng=None):
    t = np.arange(int(dur * SR)) / SR
    if kind == "pad":
        det = [0.997, 1.0, 1.003]
        s = sum(np.sin(2 * np.pi * f * d * t) for d in det) / 3
        s += 0.25 * np.sin(2 * np.pi * f * 2 * t)
        return s * env(len(t), dur * 0.35, dur * 0.4)
    if kind == "bell":
        s = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) + 0.2 * np.sin(2 * np.pi * f * 5.4 * t)
        return s * np.exp(-t * 3.2)
    if kind == "pluck":
        s = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)
        return s * np.exp(-t * 7)
    if kind == "keys":
        s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2 * t) + 0.15 * np.sin(2 * np.pi * f * 3 * t)
        return s * np.exp(-t * 2.2)
    raise ValueError(kind)

def lowpass(x, cut):
    b, a = butter(2, cut / (SR / 2), "low")
    return lfilter(b, a, x)

def drums(total, bpm, rng):
    out = np.zeros(total)
    beat = 60 / bpm
    n = int(total / SR / (beat / 2)) + 1
    for i in range(n):
        p = int(i * beat / 2 * SR)
        if p >= total: break
        if i % 4 == 0:  # kick
            t = np.arange(int(0.25 * SR)) / SR
            k = np.sin(2 * np.pi * (55 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
            out[p:p + len(k)] += k[: total - p] * 0.9
        if i % 4 == 2:  # soft snare/clap
            t = np.arange(int(0.18 * SR)) / SR
            s = rng.standard_normal(len(t)) * np.exp(-t * 20) * 0.35
            out[p:p + len(s)] += s[: total - p]
        t = np.arange(int(0.05 * SR)) / SR  # hat
        h = rng.standard_normal(len(t)) * np.exp(-t * 80) * 0.12
        out[p:p + len(h)] += h[: total - p]
    b, a = butter(1, 120 / (SR / 2), "high")
    return out

def compose(mood, seconds, seed=1):
    rng = np.random.default_rng(seed)
    bpm = BPM[mood]; bar = 4 * 60 / bpm
    total = int(seconds * SR)
    mix = np.zeros(total + SR * 3)
    prog = PROGS[mood][:]
    rot = seed % len(prog); prog = prog[rot:] + prog[:rot]
    bars = int(np.ceil(seconds / bar)) + 1
    for b in range(bars):
        root, shape = prog[b % len(prog)]
        start = int(b * bar * SR)
        if start >= total: break
        notes = [hz(root, 3) * 2 ** (s / 12) for s in SHAPES[shape]]
        if mood in ("dreamy", "emotional"):
            for f in notes:
                x = tone(f, bar * 1.15, "pad") * 0.18
                mix[start:start + len(x)] += x[: len(mix) - start]
        if mood == "playful":
            step = 60 / bpm / 2
            for k in range(8):
                f = notes[k % len(notes)] * (2 if k % 4 == 3 else 1)
                p = start + int(k * step * SR)
                x = tone(f, 0.4, "pluck") * 0.22
                mix[p:p + len(x)] += x[: len(mix) - p]
        if mood == "emotional":
            step = 60 / bpm / 2
            for k in range(8):
                f = notes[[0, 1, 2, 1, 3 % len(notes), 2, 1, 2][k] % len(notes)] * 2
                p = start + int(k * step * SR)
                x = tone(f, 1.2, "keys") * 0.16
                mix[p:p + len(x)] += x[: len(mix) - p]
        if mood == "dreamy":
            for k in range(4):
                if rng.random() < 0.7:
                    f = notes[rng.integers(len(notes))] * 4
                    p = start + int(k * (bar / 4) * SR)
                    x = tone(f, 1.6, "bell") * 0.08
                    mix[p:p + len(x)] += x[: len(mix) - p]
        bass = tone(hz(root, 2), bar, "pad") * 0.22
        mix[start:start + len(bass)] += bass[: len(mix) - start]
    mix = mix[:total]
    if mood == "playful":
        mix += drums(total, bpm, rng) * 0.45
    if mood != "playful":
        mix = lowpass(mix, 5200)
    # simple stereo + reverb-ish delay
    d = int(0.23 * SR)
    wet = np.zeros_like(mix); wet[d:] = mix[:-d] * 0.35
    L = mix + wet; R = mix + np.roll(wet, int(0.03 * SR))
    st = np.stack([L, R], 1)
    fade = int(0.8 * SR)
    st[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    st[-fade:] *= np.linspace(1, 0, fade)[:, None]
    st /= max(1e-9, np.abs(st).max()) / 0.8
    return st

def add_to_video(video, mood="dreamy", seed=1):
    """Replace the video's silent track with generated music, normalized for Instagram (~-16 LUFS)."""
    import os, subprocess, tempfile, json
    dur = float(json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video]))["format"]["duration"])
    wav = tempfile.mktemp(suffix=".wav")
    wavfile.write(wav, SR, (compose(mood, dur + 0.2, seed) * 32767).astype(np.int16))
    tmp = video[:-4] + ".mus.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart", tmp], check=True)
    os.replace(tmp, video); os.remove(wav)
    return video

def main():
    mood, secs, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    wavfile.write(out, SR, (compose(mood, secs, seed) * 32767).astype(np.int16))
    print("ok", out)

if __name__ == "__main__":
    main()
