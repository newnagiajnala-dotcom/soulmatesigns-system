"""Replace a rendered template reel's code-generated music with a real instrumental from music/library.json.
Runs in the Higgsfield sandbox (it can download the Higgsfield CDN tracks; the repo container cannot).
usage: python3 remix_music.py <video url or path> <mood> <seed> <out.mp4>
       (mood = playful | dreamy | emotional, seed = spec "seed"; the library is fetched from the repo's raw URL)
Audio: track from 0 s, 0.3 s fade-in, 1.2 s fade-out, two-pass loudnorm to -14 LUFS / -1.5 dBTP, AAC 192k 48 kHz.
"""
import json, subprocess, sys, urllib.request
RAW = "https://raw.githubusercontent.com/newnagiajnala-dotcom/soulmatesigns-system/main/"

def get(url, path):
    if url.startswith("http"): urllib.request.urlretrieve(url, path); return path
    return url

def main():
    src, mood, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
    lib = json.load(urllib.request.urlopen(RAW + "music/library.json"))
    tracks = lib.get(mood) or lib["dreamy"]
    video = get(src, "in_video.mp4"); track = get(tracks[seed % len(tracks)], "in_track.mp3")
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video]))
    pre = f"aresample=48000,aformat=channel_layouts=stereo,atrim=0:{d:.2f},afade=t=in:d=0.3,afade=t=out:st={max(0, d-1.2):.2f}:d=1.2"
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-stream_loop", "-1", "-i", track, "-af",
                           pre + ",loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json", "-f", "null", "-"],
                          capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-stream_loop", "-1", "-i", track, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-af", pre + "," + ln + ",aformat=sample_fmts=fltp:channel_layouts=stereo",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-t", f"{d:.2f}", "-movflags", "+faststart", out], check=True)
    print(json.dumps({"ok": True, "out": out, "seconds": round(d, 2), "track": tracks[seed % len(tracks)]}))

if __name__ == "__main__":
    main()
