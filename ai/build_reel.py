"""Assemble a "Luna" AI reel inside the Higgsfield sandbox (it has ffmpeg, faster-whisper, fonts, internet).
usage: python3 build_reel.py spec.json outdir
spec: {"hook_text": "YOU'RE NOT IN LOVE.", "cta_text": "comment 'limerence' 💜",
       "scenes": ["https://...png", x4], "voice_url": "https://...wav", "music_url": "https://...wav",
       "highlight": ["limerence", "love"]}
Output: outdir/reel.mp4 (1080x1920, 30fps, captions word-by-word, voice + soft music, -16 LUFS), outdir/cover.jpg
"""
import json, os, subprocess, sys, urllib.request

W, H, FPS, XF, TAIL = 1080, 1920, 30, 0.45, 1.6
FONTDIR = "/usr/share/fonts/truetype/higgsfield"

def sh(*a): subprocess.run(a, check=True)

def dl(url, path):
    if not os.path.exists(path):
        urllib.request.urlretrieve(url, path)
    return path

def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).strip())

def words(voice):
    from faster_whisper import WhisperModel
    m = WhisperModel("base.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(voice, word_timestamps=True)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words if w.word.strip()]

def ts(t):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"

def ass(spec, ws, total, path):
    hl = {h.lower() for h in spec.get("highlight", [])}
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,82,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,2,2,70,70,560,1
Style: Hook,Montserrat ExtraBold,88,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,3,18,0,8,60,60,250,1
Style: Cta,Montserrat ExtraBold,70,&H00202020,&H00202020,&H0066D6FF,&H0066D6FF,1,0,0,0,100,100,0,0,3,22,0,8,80,80,300,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 1,{ts(0)},{ts(2.6)},Hook,,0,0,0,,{{\\fad(80,200)}}{spec['hook_text']}"]
    if spec.get("cta_text"):
        ev.append(f"Dialogue: 1,{ts(total - TAIL - 0.6)},{ts(total)},Cta,,0,0,0,,{{\\fad(200,0)}}{spec['cta_text']}")
    chunks = [ws[i:i + 3] for i in range(0, len(ws), 3)]
    for ch in chunks:
        for j, (st, en, _) in enumerate(ch):
            end = ch[j + 1][0] if j + 1 < len(ch) else en + 0.15
            parts = []
            for k, (_, _, w) in enumerate(ch):
                clean = w.strip(".,!?…\"'").lower()
                if k == j:
                    parts.append("{\\c&H66D6FF&\\fscx108\\fscy108}" + w.upper() + "{\\r}")
                elif clean in hl:
                    parts.append("{\\c&HB4A0FF&}" + w.upper() + "{\\r}")
                else:
                    parts.append(w.upper())
            ev.append(f"Dialogue: 0,{ts(st)},{ts(end)},Cap,,0,0,0,,{' '.join(parts)}")
    open(path, "w").write(head + "\n".join(ev) + "\n")

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    imgs = [dl(u, f"{out}/s{i}.png") for i, u in enumerate(spec["scenes"])]
    voice = dl(spec["voice_url"], f"{out}/voice.wav"); music = dl(spec["music_url"], f"{out}/music.wav")
    vd = dur(voice); total = vd + TAIL; n = len(imgs)
    seg = (total + XF * (n - 1)) / n
    clips = []
    for i, im in enumerate(imgs):
        frames = int(seg * FPS) + 2
        z = f"min(1+on*0.0009,1.12)" if i % 2 == 0 else f"max(1.12-on*0.0009,1.0)"
        c = f"{out}/c{i}.mp4"
        sh("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", im, "-vf",
           f"scale={W*3//2}:{H*3//2}:force_original_aspect_ratio=increase,crop={W*3//2}:{H*3//2},"
           f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={W}x{H}:fps={FPS},setsar=1",
           "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", c)
        clips.append(c)
    # crossfade chain
    inputs, fc, last, off = [], [], "0:v", 0.0
    for c in clips: inputs += ["-i", c]
    for i in range(1, n):
        off += seg - XF
        fc.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); last = f"v{i}"
    sh("ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc), "-map", f"[{last}]",
       "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f"{out}/base.mp4")
    ws = words(voice); ass(spec, ws, total, f"{out}/subs.ass")
    # Audio (v2, 5 Nov 2026): cleaned + gently compressed voice, music ducked under speech (sidechain),
    # music fades out at the end, then TWO-PASS loudness normalization (no pumping) to -14 LUFS / -1.5 dBTP.
    mvol = spec.get("music_volume", 0.35)
    mix = f"{out}/mix.wav"
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-stream_loop", "-1", "-i", music, "-filter_complex",
       f"[0:a]aresample=48000,aformat=channel_layouts=stereo,highpass=f=80,"
       f"acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,deesser=i=0.4,apad,asplit[vo][sc];"
       f"[1:a]aresample=48000,aformat=channel_layouts=stereo,volume={mvol},"
       f"afade=t=in:d=0.6,afade=t=out:st={max(0.0, total - 1.6):.2f}:d=1.5[mus];"
       f"[mus][sc]sidechaincompress=threshold=0.04:ratio=6:attack=30:release=450:makeup=1[duck];"
       f"[vo][duck]amix=inputs=2:duration=first:normalize=0,aformat=channel_layouts=stereo[a]",
       "-map", "[a]", "-t", f"{total:.2f}", "-c:a", "pcm_s16le", mix)
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix, "-af", "loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/base.mp4", "-i", mix, "-filter_complex",
       f"[0:v]ass={out}/subs.ass:fontsdir={FONTDIR}[v];[1:a]{ln},alimiter=limit=0.84:level=false,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", f"{out}/reel.mp4")
    sh("ffmpeg", "-y", "-loglevel", "error", "-ss", "1.2", "-i", f"{out}/reel.mp4", "-frames:v", "1", f"{out}/cover.jpg")
    print(json.dumps({"ok": True, "seconds": round(total, 1), "words": len(ws)}))

if __name__ == "__main__":
    main()
