"""Sketch-reveal reel (Day 5 script in the owner's content doc, 19 Nov 2026).
0-7 s   chart (first initial) + hook "Pause when you see your initial"
7-9 s   chart blurs, "You found their initial..."
9-13 s  our own pencil-line face drawing appears stroke by stroke (labelled "illustration"):
        "...but what if you could see their face?" then "A psychic artist draws them by hand"
13-14.5 s end card "Comment SKETCH" (same card as chart reels)
No real person, no AI people, no guarantees.
usage: python3 reelgen/sketch_reveal.py promo/chart/chart1.json docs/v/sketch1.mp4
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_reel import frame, card, f, THEMES, W, H

FPS = 30

def strokes():
    """Generic pencil face as polylines (oval, hair, brows, eyes, nose, lips, neck)."""
    cx, cy = W / 2, 960
    S = []
    def arc(x, y, rx, ry, a0, a1, n=40):
        return [(x + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), y + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
    S.append(arc(cx, cy + 20, 205, 290, 0, 180, 60))      # cheeks + jaw + chin
    S.append(arc(cx, cy + 20, 205, 330, 180, 360, 60))   # temples + top of head
    for k in range(7):                                    # hair strands
        o = -200 + k * 60
        S.append([(cx + o + 10 * math.sin(t / 3), cy - 300 + t * 9) for t in range(0, 40)] if k % 2 else
                 arc(cx + o * 0.4, cy - 230, 240 - k * 12, 120 + k * 8, 190, 350, 30))
    for s in (-1, 1):                                     # brows, eyes, iris
        ex = cx + s * 90
        S.append(arc(ex, cy - 70, 70, 22, 200, 340, 20))
        S.append(arc(ex, cy - 10, 58, 22, 180, 360, 24))
        S.append(arc(ex, cy - 10, 58, 18, 0, 180, 24))
        S.append(arc(ex, cy - 10, 18, 18, 0, 360, 20))
    S.append([(cx - 6, cy + 10), (cx - 18, cy + 95), (cx, cy + 108), (cx + 20, cy + 98)])  # nose
    S.append(arc(cx, cy + 165, 70, 18, 200, 340, 20))     # upper lip
    S.append(arc(cx, cy + 168, 66, 26, 10, 170, 20))      # lower lip
    S.append([(cx - 120, cy + 250), (cx - 110, cy + 420)])
    S.append([(cx + 120, cy + 250), (cx + 110, cy + 420)])
    return S

def draw_partial(img, S, frac, ink):
    d = ImageDraw.Draw(img)
    total = sum(len(s) - 1 for s in S); left = int(total * frac)
    for s in S:
        for i in range(len(s) - 1):
            if left <= 0: return
            d.line([s[i], s[i + 1]], fill=ink, width=6); left -= 1

def label(img, lines, ink, y=300, size=92):
    d = ImageDraw.Draw(img)
    for t in lines:
        s = size
        while f(s).getlength(t) > W - 120: s -= 4
        d.text((W / 2, y), t, font=f(s), fill=ink, anchor="mm"); y += s + 20

def main(spec_path, out):
    spec = json.load(open(spec_path)); bg, ink, red = THEMES[spec.get("theme", "cream")]
    chart = frame(spec).convert("RGB")
    tmp = out + "_frames"; os.makedirs(tmp, exist_ok=True)
    S = strokes(); n = 0
    def save(im):
        nonlocal n; im.save(f"{tmp}/{n:05d}.png"); n += 1
    hook = chart.copy(); d = ImageDraw.Draw(hook)
    d.rounded_rectangle([60, H - 190, W - 60, H - 50], 36, fill=red)
    s = 84
    while f(s).getlength("Pause when you see your initial") > W - 180: s -= 4
    d.text((W / 2, H - 120), "Pause when you see your initial", font=f(s), fill=(255, 255, 255), anchor="mm")
    for i in range(7 * FPS): save(hook)
    blur = chart.filter(ImageFilter.GaussianBlur(10))
    ov = Image.new("RGBA", (W, H), bg + (150,)); blur = Image.alpha_composite(blur.convert("RGBA"), ov).convert("RGB")
    b2 = blur.copy(); label(b2, ["You found their initial..."], red, y=H / 2, size=120)
    for i in range(2 * FPS): save(b2)
    for i in range(4 * FPS):
        im = Image.new("RGB", (W, H), bg)
        draw_partial(im, S, min(1, i / (3.2 * FPS)), ink)
        label(im, ["...but what if you could", "see their face?"] if i < 2 * FPS else ["A psychic artist", "draws them by hand"], red if i >= 2 * FPS else ink, y=230)
        ImageDraw.Draw(im).text((W - 60, H - 70), "illustration", font=f(44), fill=ink, anchor="rm")
        save(im)
    end = card(chart, spec, ["Want to see your", "soulmate's face?", "Comment", "and we'll message you the link"], big=(3, "SKETCH"))
    for i in range(int(1.5 * FPS)): save(end)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{tmp}/%05d.png",
                    "-f", "lavfi", "-t", str(n / FPS), "-i", "anullsrc=r=44100:cl=stereo",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-shortest", out], check=True)
    for k in (0, 7 * FPS + 10, 9 * FPS + 50, 9 * FPS + 110, n - 1):
        Image.open(f"{tmp}/{k:05d}.png").resize((270, 480)).save(f"{out}_k{k}.png")
    subprocess.run(["rm", "-rf", tmp])
    print(out, n / FPS, "s")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
