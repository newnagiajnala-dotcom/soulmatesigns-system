"""Birth-date CODE grid reel: "Who will be your soulmate? Find your birth date → comment your code".
Days 1-31 are grouped into 8 codes; rows pop in one by one; ends on the full grid (= cover, so people pause).

spec: {"title": "Who will be your", "title2": "Soulmate?", "sub": "find your birth date 👇", "cta": "comment your CODE 👇",
       "codes": 8, "music": "dreamy", "seed": int}
usage: python3 reelgen/code_reel.py spec.json out_base [--frames t1,t2]
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FPS, FONT_B, FONT_M, text_block, boxed, paste_pop
from reveal_reel import nebula

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
GOLD = (255, 214, 102, 255); WHITE = (255, 255, 255, 255)

def serif(size, wt=700):
    f = ImageFont.truetype(os.path.join(FONTS, "Cinzel.ttf"), size); f.set_variation_by_axes([wt]); return f

def title_card(t1, t2):
    f1, f2 = serif(64, 600), serif(124, 800)
    w = int(max(f1.getlength(t1), f2.getlength(t2))) + 140
    im = Image.new("RGBA", (min(w, 980), 330), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], 30, fill=(30, 14, 50, 200), outline=GOLD, width=4)
    d.rounded_rectangle([14, 14, im.width - 15, im.height - 15], 22, outline=(255, 214, 102, 120), width=2)
    d.text(((im.width - f1.getlength(t1)) / 2, 40), t1, font=f1, fill=WHITE)
    d.text(((im.width - f2.getlength(t2)) / 2, 125), t2, font=f2, fill=GOLD)
    return im

def groups(n):
    g = [[] for _ in range(n)]
    for d in range(1, 32):
        g[(d - 1) % n].append(d)
    return g

def row(days, code):
    f = ImageFont.truetype(FONT_M, 46); fb = ImageFont.truetype(FONT_B, 46)
    left = "Born on " + ", ".join(map(str, days))
    right = f"Code {code}"
    im = Image.new("RGBA", (900, 92), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 899, 91], 20, fill=(20, 10, 40, 170), outline=(255, 214, 102, 90), width=2)
    d.text((28, 18), "✦", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40), fill=GOLD)
    d.text((80, 16), left, font=f, fill=WHITE)
    d.text((900 - 28 - fb.getlength(right), 16), right, font=fb, fill=GOLD)
    return im

def build(spec):
    n = spec.get("codes", 8)
    L = {"neb": nebula(spec.get("seed", 6) + 7),
         "title": title_card(spec.get("title", "Who will be your"), spec.get("title2", "Soulmate?")),
         "sub": text_block(spec.get("sub", "find your birth date 👇"), 50, GOLD, 900, FONT_M),
         "rows": [row(g, i + 1) for i, g in enumerate(groups(n))],
         "cta": boxed(text_block(spec.get("cta", "comment your CODE 👇"), 56, (20, 16, 40, 255), 820, gap=0.08), 42, 24, GOLD, 26)}
    L["t_rows"] = 1.3; L["step"] = 0.55
    L["t_cta"] = L["t_rows"] + L["step"] * n + 0.4
    L["end"] = L["t_cta"] + 4.0
    return L

def frame_at(t, L):
    z = 1.0 + 0.06 * (t / L["end"]); neb = L["neb"]
    cw, ch = int(W * 1.25 / z), int(H * 1.25 / z)
    x0, y0 = (neb.width - cw) // 2, (neb.height - ch) // 2
    f = neb.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    paste_pop(f, L["title"], W / 2, 330, 0.1, t)
    paste_pop(f, L["sub"], W / 2, 560, 0.7, t)
    for i, r in enumerate(L["rows"]):
        paste_pop(f, r, W / 2, 680 + i * 106, L["t_rows"] + i * L["step"], t, .3)
    paste_pop(f, L["cta"], W / 2, 680 + len(L["rows"]) * 106 + 70, L["t_cta"], t, .45)
    return f

def main():
    spec = json.load(open(sys.argv[1])); base = sys.argv[2]
    L = build(spec)
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            frame_at(float(ts), L).convert("RGB").save(f"{base}_f{ts}.jpg", quality=90)
        return
    frame_at(L["end"] - 0.4, L).convert("RGB").save(base + "_cover.jpg", quality=92)
    tmp = base + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    for i in range(int(L["end"] * FPS)):
        p.stdin.write(frame_at(i / FPS, L).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        print("ffmpeg failed"); sys.exit(1)
    os.replace(tmp, base + ".mp4")
    from music import add_to_video
    add_to_video(base + ".mp4", spec.get("music", "dreamy"), spec.get("seed", 1))
    print("ok", base + ".mp4", f"{L['end']:.1f}s")

if __name__ == "__main__":
    main()
