"""Text-card reel (formats F1 pick-a-pile, F2 birth month, F3 zodiac list, F5 reassurance, F6 debate).
Hook box -> items revealed one by one -> CTA. 1080x1920, 30fps.

spec: {"hook": str, "sub": str (optional), "items": [str, ...] (max 6), "cta": str, "caption": str, "seed": int}
usage: python3 reelgen/cards_reel.py spec.json out_base [--frames t1,t2]
"""
import json, os, subprocess, sys
from PIL import ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import (W, H, FPS, FONT_B, FONT_M, text_block, boxed, background, paste_pop, ease_out)
import math, random

def build(spec):
    random.seed(spec.get("seed", 7))
    L = {"hook": boxed(text_block(spec["hook"], 70, (20, 16, 40, 255), 860, gap=0.08), 46, 30, (255, 255, 255, 255), 28)}
    L["sub"] = text_block(spec["sub"], 44, (255, 214, 102, 255), 880, FONT_M) if spec.get("sub") else None
    L["cta"] = boxed(text_block(spec["cta"], 56, (20, 16, 40, 255), 800, gap=0.08), 42, 26, (255, 214, 102, 255), 28)
    for size in (50, 46, 42, 39, 36, 33):
        texts = [text_block(it, size, (255, 255, 255, 255), 880, FONT_M, gap=0.06) for it in spec["items"][:6]]
        wmax = max(t.width for t in texts)
        L["items"] = [boxed(t, 28 + (wmax - t.width) // 2, 18, (124, 92, 255, 225), 24) for t in texts]
        _, ys, cta_y = layout_y(L)
        if ys[-1] + L["items"][-1].height // 2 + 30 + L["cta"].height <= 1640:
            break
    L["stars"] = [(random.randint(0, W), random.randint(0, int(H * .95)), random.choice([1.5, 2, 3]), random.random() * 6.28) for _ in range(120)]
    return L

def timeline(L):
    t_items = 1.6
    step = 1.15 if len(L["items"]) <= 4 else 0.95
    t_cta = t_items + step * len(L["items"]) + 0.5
    return t_items, step, t_cta, t_cta + 2.8

def layout_y(L):
    top = 330 + (L["hook"].height // 2) + (70 if L["sub"] else 40)
    ys, y = [], top + 40
    for it in L["items"]:
        ys.append(y + it.height // 2); y += it.height + 22
    return top, ys, y + 18 + L["cta"].height // 2

def frame_at(t, BG, L):
    f = BG.copy(); d = ImageDraw.Draw(f)
    for (x, y, r, ph) in L["stars"]:
        if 40 < x < 1040 and 150 < y < 1720:
            continue
        a = int(120 + 120 * math.sin(t * 2.2 + ph))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 245, 255, max(30, a)))
    t_items, step, t_cta, _ = timeline(L)
    sub_y, ys, cta_y = layout_y(L)
    paste_pop(f, L["hook"], W / 2, 330, 0.12, t)
    if L["sub"]:
        paste_pop(f, L["sub"], W / 2, sub_y, 0.7, t)
    for i, (it, y) in enumerate(zip(L["items"], ys)):
        paste_pop(f, it, W / 2, y, t_items + i * step, t, .35)
    paste_pop(f, L["cta"], W / 2, cta_y, t_cta, t, .45)
    return f

def main():
    spec = json.load(open(sys.argv[1])); base = sys.argv[2]
    BG, L = background(), build(spec)
    end = timeline(L)[3]
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            frame_at(float(ts), BG, L).convert("RGB").save(f"{base}_f{ts}.jpg", quality=90)
        return
    frame_at(end - .4, BG, L).convert("RGB").save(base + "_cover.jpg", quality=92)
    tmp = base + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for i in range(int(end * FPS)):
        p.stdin.write(frame_at(i / FPS, BG, L).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, base + ".mp4")
        from music import add_to_video
        add_to_video(base + ".mp4", spec.get("music", "dreamy"), spec.get("seed", 1))
        print("ok", base + ".mp4", f"{end:.1f}s")
    else:
        print("ffmpeg failed"); sys.exit(1)

if __name__ == "__main__":
    main()
