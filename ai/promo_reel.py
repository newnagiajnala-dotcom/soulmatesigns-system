"""ClickBank-style promo reel for the Soulmate Sketch offer (runs in the Higgsfield sandbox).
Weird hook clip (video, can be reversed) + simple b-roll (images with motion or video clips) + voiceover +
bold centered captions (2-3 words, current word orange) + hook text + end CTA. Soft music under the voice.

usage: python3 promo_reel.py spec.json outdir
spec: {"hook_text": "STOP CUTTING TIES.", "cta_text": "LINK IN BIO",
       "scenes": [{"url": "...mp4", "video": true, "reverse": true, "dur": 4.0}, {"url": "...png"}, ...],
       "voice_url": "...wav", "music_url": "...wav", "highlight": ["soulmate"]}
"""
import json, os, subprocess, sys, urllib.request

W, H, FPS, XF, TAIL = 1080, 1920, 30, 0.35, 2.2
GAP = 0.85  # max pause between sentences (owner: 28 s felt slow, 17 s too fast, 21-22 s right)
FONTDIR = "/usr/share/fonts/truetype/higgsfield"

def sh(*a): subprocess.run(a, check=True)
def dl(url, path):
    if not os.path.exists(path): urllib.request.urlretrieve(url, path)
    return path
def dur(p): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).strip())
def ts(t):
    h, r = divmod(max(t, 0), 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"

def words(voice):
    from faster_whisper import WhisperModel
    m = WhisperModel("base.en", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(voice, word_timestamps=True)
    return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words if w.word.strip()]

def tighten(voice, out):
    """Cut every pause longer than GAP down to GAP, trim leading silence. Returns the new voice path."""
    ws = words(voice)
    if not ws: return voice
    segs, st = [], max(ws[0][0] - 0.08, 0)
    for a, b in zip(ws, ws[1:]):
        if b[0] - a[1] > GAP:
            segs.append((st, a[1] + 0.12)); st = b[0] - 0.08
    segs.append((st, ws[-1][1] + 0.25))
    parts, labels = [], []
    for i, (a, b) in enumerate(segs):
        parts.append(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=N/SR/TB,aresample=44100,aformat=channel_layouts=mono[s{i}]"); labels.append(f"[s{i}]")
        if i < len(segs) - 1:
            parts.append(f"aevalsrc=0:d={GAP - 0.2:.2f}:s=44100[g{i}]"); labels.append(f"[g{i}]")
    fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=0:a=1[o]"
    dst = f"{out}/voice_tight.wav"
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-filter_complex", fc, "-map", "[o]", dst)
    return dst

def make_lines_ass(spec, total, path):
    """Style B: no voice. Big text lines that change every ~2 s. *word* = orange."""
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Montserrat ExtraBold,128,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,9,4,5,70,70,0,1
Style: Txt,Montserrat ExtraBold,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,7,3,5,80,80,0,1
Style: Cta,Montserrat ExtraBold,104,&H00FFFFFF,&H00FFFFFF,&H000080FF,&H000080FF,1,0,0,0,100,100,0,0,3,26,0,2,80,80,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    import re
    col = lambda s: re.sub(r"\*(.+?)\*", lambda m: "{\\c&H0080FF&}" + m.group(1) + "{\\r}", s)
    hd = spec.get("hook_dur", 2.4)
    ev = [f"Dialogue: 2,{ts(0)},{ts(hd)},Hook,,0,0,0,,{{\\fad(0,150)\\c&H0080FF&}}{spec['hook_text']}"]
    t0 = hd
    for ln in spec["lines"]:
        d = ln.get("dur", 2.4)
        ev.append(f"Dialogue: 1,{ts(t0)},{ts(t0 + d)},Txt,,0,0,0,,{{\\fad(120,80)\\fscx90\\fscy90\\t(0,160,\\fscx100\\fscy100)}}{col(ln['text'].upper())}")
        t0 += d
    if spec.get("cta_text"):
        ev.append(f"Dialogue: 2,{ts(t0)},{ts(total)},Cta,,0,0,0,,{{\\fad(150,0)}}{spec['cta_text']}")
    open(path, "w").write(head + "\n".join(ev) + "\n")

def make_ass(spec, ws, total, path):
    hl = {h.lower() for h in spec.get("highlight", [])}
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Hook,Montserrat ExtraBold,138,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,9,4,8,50,50,330,1
Style: Cta,Montserrat ExtraBold,104,&H00FFFFFF,&H00FFFFFF,&H000080FF,&H000080FF,1,0,0,0,100,100,0,0,3,26,0,2,80,80,420,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = [f"Dialogue: 2,{ts(0)},{ts(2.4)},Hook,,0,0,0,,{{\\fad(0,200)\\c&H0080FF&}}{spec['hook_text']}"]
    if spec.get("cta_text"):
        ev.append(f"Dialogue: 2,{ts(total - TAIL - 0.8)},{ts(total)},Cta,,0,0,0,,{{\\fad(150,0)}}{spec['cta_text']}")
    chunks, cur = [], []
    for w in ws:  # 2-3 words per chunk, break after punctuation
        cur.append(w)
        if len(cur) == 3 or w[2][-1:] in ".?!,…" or (len(cur) == 2 and len(w[2]) > 7):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for ch in chunks:
        for j, (st, en, _) in enumerate(ch):
            if st < 2.4: st = max(st, 2.4)  # hook text owns the first 2.4 s
            end = ch[j + 1][0] if j + 1 < len(ch) else en + 0.12
            if end <= st: continue
            parts = []
            for k, (_, _, w) in enumerate(ch):
                c = w.strip(".,!?…\"'").lower()
                if k == j: parts.append("{\\c&H0080FF&\\fscx112\\fscy112}" + w.upper() + "{\\r}")
                elif c in hl: parts.append("{\\c&H66D6FF&}" + w.upper() + "{\\r}")
                else: parts.append(w.upper())
            ev.append(f"Dialogue: 0,{ts(st)},{ts(end)},Cap,,0,0,0,,{' '.join(parts)}")
    open(path, "w").write(head + "\n".join(ev) + "\n")

def main():
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    music = dl(spec["music_url"], f"{out}/music.wav")
    text_mode = bool(spec.get("lines"))
    if text_mode:
        voice = None; total = spec.get("hook_dur", 2.4) + sum(l.get("dur", 2.4) for l in spec["lines"]) + TAIL
    else:
        voice = dl(spec["voice_url"], f"{out}/voice.wav")
        if not spec.get("no_tighten"): voice = tighten(voice, out)
        total = dur(voice) + TAIL
    sc = spec["scenes"]; n = len(sc)
    fixed = sum(s.get("dur", 0) for s in sc); free = [s for s in sc if not s.get("dur")]
    rest = (total + XF * (n - 1) - fixed) / max(len(free), 1)
    clips = []
    for i, s in enumerate(sc):
        d = s.get("dur") or rest; c = f"{out}/c{i}.mp4"
        if s.get("video"):
            src = dl(s["url"], f"{out}/s{i}.mp4")
            vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},setsar=1"
            if s.get("reverse"): vf = "reverse," + vf
            sh("ffmpeg", "-y", "-loglevel", "error", "-i", src, "-an", "-vf", vf, "-t", f"{d:.2f}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", c)
        else:
            src = dl(s["url"], f"{out}/s{i}.png"); fr = int(d * FPS) + 2
            z = "min(1+on*0.0011,1.14)" if i % 2 else "max(1.14-on*0.0011,1.0)"
            sh("ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", src, "-vf",
               f"scale={W*3//2}:{H*3//2}:force_original_aspect_ratio=increase,crop={W*3//2}:{H*3//2},"
               f"zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={fr}:s={W}x{H}:fps={FPS},setsar=1",
               "-frames:v", str(fr), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", c)
        clips.append((c, dur(c)))
    inputs, fc, last, off = [], [], "0:v", 0.0
    for c, _ in clips: inputs += ["-i", c]
    for i in range(1, n):
        off += clips[i - 1][1] - XF
        fc.append(f"[{last}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); last = f"v{i}"
    sh("ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(fc) or "null", "-map", f"[{last}]",
       "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", f"{out}/base.mp4")
    if text_mode:
        ws = []; make_lines_ass(spec, total, f"{out}/subs.ass")
        sh("ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/base.mp4", "-stream_loop", "-1", "-i", music, "-filter_complex",
           f"[0:v]ass={out}/subs.ass:fontsdir={FONTDIR}[v];[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.9,"
           f"afade=t=out:st={max(total - 1.2, 0):.2f}:d=1.1,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
           "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", f"{out}/reel.mp4")
        sh("ffmpeg", "-y", "-loglevel", "error", "-ss", "0.8", "-i", f"{out}/reel.mp4", "-frames:v", "1", f"{out}/cover.jpg")
        print(json.dumps({"ok": True, "seconds": round(total, 1), "mode": "text"})); return
    ws = words(voice); make_ass(spec, ws, total, f"{out}/subs.ass")
    sh("ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/base.mp4", "-i", voice, "-i", music, "-filter_complex",
       f"[0:v]ass={out}/subs.ass:fontsdir={FONTDIR}[v];"
       f"[1:a]aresample=44100,aformat=channel_layouts=stereo,volume=1.6,apad[a1];"
       f"[2:a]aresample=44100,aformat=channel_layouts=stereo,volume=0.14[a2];"
       f"[a1][a2]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11[a]",
       "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
       "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", f"{out}/reel.mp4")
    sh("ffmpeg", "-y", "-loglevel", "error", "-ss", "0.8", "-i", f"{out}/reel.mp4", "-frames:v", "1", f"{out}/cover.jpg")
    print(json.dumps({"ok": True, "seconds": round(total, 1), "words": len(ws)}))

if __name__ == "__main__":
    main()
