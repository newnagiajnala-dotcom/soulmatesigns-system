"""Tarot pick-a-card reel (F1). 3 face-down cards -> "pick one" -> each card flips and reveals a message -> CTA.

spec: {"hook": str, "cards": [{"title": str, "emoji": str, "message": str} x3], "cta": str, "music": "dreamy", "seed": int}
usage: python3 reelgen/tarot_reel.py spec.json out_base [--frames t1,t2]
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FPS, FONT_B, FONT_M, text_block, boxed, background, paste_pop, ease_out, emoji_img

CW, CH = 316, 540
GOLD = (255, 214, 102, 255)

def card_back(n):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CW - 1, CH - 1], 26, fill=(58, 34, 110, 255), outline=GOLD, width=6)
    d.rounded_rectangle([18, 18, CW - 19, CH - 19], 18, outline=(255, 214, 102, 140), width=2)
    rnd = random.Random(n * 7)
    for _ in range(26):
        x, y, r = rnd.randint(30, CW - 30), rnd.randint(30, CH - 30), rnd.choice([2, 3, 4])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 220, 200))
    cx, cy = CW // 2, CH // 2
    d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=GOLD, width=4)
    f = ImageFont.truetype(FONT_B, 96)
    t = str(n); w = f.getlength(t)
    d.text((cx - w / 2, cy - 66), t, font=f, fill=GOLD)
    return im

def card_face(c):
    im = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CW - 1, CH - 1], 26, fill=(255, 246, 232, 255), outline=GOLD, width=6)
    d.rounded_rectangle([18, 18, CW - 19, CH - 19], 18, outline=(176, 125, 18, 160), width=2)
    e = emoji_img(c["emoji"], 130)
    im.alpha_composite(e, ((CW - e.width) // 2, 130))
    t = text_block(c["title"], 38, (40, 26, 70, 255), CW - 50, gap=0.04)
    im.alpha_composite(t, ((CW - t.width) // 2, 340))
    return im

def flip(back, face, k):
    """k in [0,1]: 0=back, 1=face, with horizontal squash."""
    img = back if k < 0.5 else face
    s = abs(math.cos(k * math.pi))
    w = max(2, int(CW * s))
    return img.resize((w, CH), Image.BILINEAR)

def glow(img, color=(255, 214, 102), radius=28):
    g = Image.new("RGBA", (img.width + radius * 4, img.height + radius * 4), (0, 0, 0, 0))
    m = Image.new("RGBA", g.size, color + (0,))
    a = img.getchannel("A").point(lambda v: 170 if v > 0 else 0)
    m.putalpha(Image.new("L", g.size, 0)); m.getchannel("A").paste(a, (radius * 2, radius * 2))
    al = Image.new("L", g.size, 0); al.paste(a, (radius * 2, radius * 2))
    al = al.filter(ImageFilter.GaussianBlur(radius))
    g = Image.new("RGBA", g.size, color + (0,)); g.putalpha(al)
    return g

T0, PICK, FLIP0, STEP, MSG = 0.15, 1.6, 4.4, 3.6, 0.55

def timeline(n):
    end_cards = FLIP0 + STEP * n
    return end_cards, end_cards + 3.2

def build(spec):
    random.seed(spec.get("seed", 5))
    L = {"hook": boxed(text_block(spec["hook"], 66, (20, 16, 40, 255), 860, gap=0.08), 44, 28, (255, 255, 255, 255), 28),
         "pick": text_block("pause & pick one 👇", 50, (255, 214, 102, 255), 900, FONT_M),
         "backs": [card_back(i + 1) for i in range(3)],
         "faces": [card_face(c) for c in spec["cards"]],
         "msgs": [boxed(text_block(f"card {i + 1}: " + c["message"], 46, (255, 255, 255, 255), 860, FONT_M, gap=0.08), 36, 24, (124, 92, 255, 230), 26)
                  for i, c in enumerate(spec["cards"])],
         "cta": boxed(text_block(spec["cta"], 54, (20, 16, 40, 255), 820, gap=0.08), 42, 26, GOLD, 28),
         "stars": [(random.randint(0, W), random.randint(0, H), random.choice([1.5, 2, 3]), random.random() * 6.28) for _ in range(140)]}
    L["glow"] = glow(L["backs"][0])
    return L

def frame_at(t, BG, L):
    f = BG.copy(); d = ImageDraw.Draw(f)
    for (x, y, r, ph) in L["stars"]:
        a = int(110 + 110 * math.sin(t * 2.0 + ph))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 245, 255, max(25, a)))
    paste_pop(f, L["hook"], W / 2, 250, T0, t)
    end_cards, _ = timeline(3)
    if PICK <= t < FLIP0:
        paste_pop(f, L["pick"], W / 2, 1400, PICK, t)
    xs = [W / 2 - CW - 22, W / 2, W / 2 + CW + 22]
    cy = 830
    for i in range(3):
        t_in = 0.5 + i * 0.18
        if t < t_in: continue
        a = ease_out((t - t_in) / 0.5)
        bob = math.sin(t * 2.2 + i) * 8 if t < FLIP0 + STEP * i else 0
        fs = FLIP0 + STEP * i
        k = min(1.0, max(0.0, (t - fs) / 0.6))
        active = fs <= t < fs + STEP
        if active:
            g = L["glow"]; f.alpha_composite(g, (int(xs[i] - g.width / 2), int(cy - g.height / 2)))
        img = flip(L["backs"][i], L["faces"][i], k) if t >= fs else L["backs"][i]
        if a < 1:
            img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * a)))
        sc = 1.06 if active and k >= 1 else 1.0
        if sc != 1.0: img = img.resize((int(img.width * sc), int(img.height * sc)), Image.BILINEAR)
        f.alpha_composite(img, (int(xs[i] - img.width / 2), int(cy - img.height / 2 + bob + (1 - a) * 60)))
    for i in range(3):
        fs = FLIP0 + STEP * i
        if fs + MSG <= t < fs + STEP or (i == 2 and fs + MSG <= t < end_cards):
            paste_pop(f, L["msgs"][i], W / 2, 1420, fs + MSG, t, .35)
    paste_pop(f, L["cta"], W / 2, 1420, end_cards, t, .45)
    return f

def main():
    spec = json.load(open(sys.argv[1])); base = sys.argv[2]
    BG, L = background(), build(spec)
    end = timeline(3)[1]
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            frame_at(float(ts), BG, L).convert("RGB").save(f"{base}_f{ts}.jpg", quality=90)
        return
    cover = frame_at(1.2, BG, L).convert("RGB"); cover.save(base + "_cover.jpg", quality=92)
    tmp = base + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for i in range(int(end * FPS)):
        p.stdin.write(frame_at(i / FPS, BG, L).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        print("ffmpeg failed"); sys.exit(1)
    os.replace(tmp, base + ".mp4")
    from music import add_to_video
    add_to_video(base + ".mp4", spec.get("music", "dreamy"), spec.get("seed", 1))
    print("ok", base + ".mp4", f"{end:.1f}s")

if __name__ == "__main__":
    main()
