"""Cinematic sign reveal (F3/F5). Slow-zoom nebula, big word-by-word captions, glowing zodiac symbol reveal, CTA.

spec: {"lines": ["There is *ONE* sign", "who loves the hardest", ...] (2-4 lines, *word* = gold highlight),
       "sign": "scorpio", "tagline": str, "cta": str, "music": "emotional", "seed": int}
usage: python3 reelgen/reveal_reel.py spec.json out_base [--frames t1,t2]
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FPS, FONT_B, FONT_M, text_block, boxed, paste_pop, ease_out, ease_back

SYM = {"aries": "♈", "taurus": "♉", "gemini": "♊", "cancer": "♋", "leo": "♌", "virgo": "♍", "libra": "♎",
       "scorpio": "♏", "sagittarius": "♐", "capricorn": "♑", "aquarius": "♒", "pisces": "♓"}
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
GOLD = (255, 214, 102, 255); WHITE = (255, 255, 255, 255)

def nebula(seed):
    rng = np.random.default_rng(seed)
    Wb, Hb = int(W * 1.25), int(H * 1.25)
    acc = np.zeros((Hb, Wb, 3))
    palette = [np.array(c) for c in [(120, 40, 160), (40, 60, 170), (200, 70, 140), (60, 20, 90)]]
    for s, w in [(8, 1.0), (16, 0.6), (32, 0.35)]:
        n = rng.random((s * 2, s)) if False else rng.random((max(2, Hb // (Wb // s)), s))
        img = Image.fromarray((n * 255).astype(np.uint8)).resize((Wb, Hb), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
        a = np.asarray(img) / 255.0
        col = palette[rng.integers(len(palette))]
        acc += (a[..., None] ** 2.2) * col * w
    base = np.zeros((Hb, Wb, 3)); base[...] = (10, 6, 28)
    out = np.clip(base + acc * 0.9, 0, 255).astype(np.uint8)
    im = Image.fromarray(out).convert("RGBA"); d = ImageDraw.Draw(im)
    for _ in range(420):
        x, y = rng.integers(Wb), rng.integers(Hb); r = rng.choice([1, 1, 1.5, 2, 2.5])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 255, int(rng.integers(120, 255))))
    return im

def caption(line, size=84):
    """Render a line with *highlighted* words in gold, with soft shadow."""
    f = ImageFont.truetype(FONT_B, size)
    words = line.split()
    parts = [(w.strip("*").upper(), w.startswith("*")) for w in words]
    space = f.getlength(" ")
    width = int(sum(f.getlength(p) for p, _ in parts) + space * (len(parts) - 1))
    asc, desc = f.getmetrics()
    im = Image.new("RGBA", (width + 20, asc + desc + 20), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ds, d = ImageDraw.Draw(sh), ImageDraw.Draw(im)
    x = 10
    for p, hl in parts:
        ds.text((x + 3, 13), p, font=f, fill=(0, 0, 0, 200))
        d.text((x, 10), p, font=f, fill=GOLD if hl else WHITE)
        x += f.getlength(p) + space
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    sh.alpha_composite(im)
    if sh.width > W - 80:
        s = (W - 80) / sh.width
        sh = sh.resize((int(sh.width * s), int(sh.height * s)), Image.LANCZOS)
    return sh

def symbol(sign):
    f = ImageFont.truetype(DEJAVU, 300)
    ch = SYM[sign.lower()]
    im = Image.new("RGBA", (460, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    w = f.getlength(ch)
    d.text(((460 - w) / 2, 40), ch, font=f, fill=GOLD)
    g = im.filter(ImageFilter.GaussianBlur(26))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for _ in range(3): out.alpha_composite(g)
    out.alpha_composite(im)
    return out

LINE_T = 2.3

def build(spec):
    L = {"neb": nebula(spec.get("seed", 3)), "caps": [caption(l) for l in spec["lines"]],
         "sym": symbol(spec["sign"]),
         "name": text_block(spec["sign"].upper(), 92, GOLD, 900),
         "tag": text_block(spec["tagline"], 50, WHITE, 880, FONT_M, gap=0.1),
         "cta": boxed(text_block(spec["cta"], 52, (20, 16, 40, 255), 820, gap=0.08), 40, 24, GOLD, 26)}
    n = len(L["caps"])
    L["t_reveal"] = 0.4 + n * LINE_T
    L["t_cta"] = L["t_reveal"] + 3.0
    L["end"] = L["t_cta"] + 3.0
    return L

def frame_at(t, L):
    z = 1.0 + 0.12 * (t / L["end"])
    neb = L["neb"]
    cw, ch = int(W * 1.25 / z), int(H * 1.25 / z)
    x0, y0 = (neb.width - cw) // 2, (neb.height - ch) // 2
    f = neb.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    n = len(L["caps"])
    if t < L["t_reveal"]:
        i = min(n - 1, int((t - 0.4) / LINE_T)) if t >= 0.4 else -1
        # show all lines so far, newest pops
        for j in range(max(0, i + 1)):
            y = 760 + (j - i) * 150 if j < i else 760
            if j < i:
                im = L["caps"][j].copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * 0.45)))
                f.alpha_composite(im, (int(W / 2 - im.width / 2), int(760 - (i - j) * 140 - im.height / 2)))
            else:
                paste_pop(f, L["caps"][j], W / 2, 860, 0.4 + j * LINE_T, t, .4)
    else:
        k = ease_back((t - L["t_reveal"]) / 0.7)
        s = L["sym"]; sz = max(1, int(s.width * (0.4 + 0.6 * k)))
        im = s.resize((sz, sz), Image.BILINEAR)
        pulse = 1 + 0.03 * math.sin((t - L["t_reveal"]) * 3)
        if pulse != 1: im = im.resize((int(im.width * pulse), int(im.height * pulse)), Image.BILINEAR)
        f.alpha_composite(im, (int(W / 2 - im.width / 2), int(640 - im.height / 2)))
        paste_pop(f, L["name"], W / 2, 930, L["t_reveal"] + 0.5, t)
        paste_pop(f, L["tag"], W / 2, 1080, L["t_reveal"] + 1.1, t)
        paste_pop(f, L["cta"], W / 2, 1420, L["t_cta"], t, .45)
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
    add_to_video(base + ".mp4", spec.get("music", "emotional"), spec.get("seed", 1))
    print("ok", base + ".mp4", f"{L['end']:.1f}s")

if __name__ == "__main__":
    main()
