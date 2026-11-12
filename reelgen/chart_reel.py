"""Pause-and-find chart reel (research: 14.1M-view 'find your initials' format, 5–9 s, replays + screenshots).
usage: python3 chart_reel.py <spec.json> <out.mp4>
spec: {"hook": "...", "sub": "...", "rows": [["A","J"],...], "footer": "...", "theme": "cream|blush|night", "dur": 8}"""
import json, sys, subprocess, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D = os.path.dirname(os.path.abspath(__file__)); W, H = 1080, 1920
CAV = os.path.join(D, "fonts/Caveat.ttf")
THEMES = {"cream": ((246, 238, 226), (40, 34, 30), (200, 30, 50)), "blush": ((250, 228, 230), (60, 30, 40), (190, 20, 60)),
          "night": ((22, 20, 40), (245, 240, 255), (255, 120, 160))}
def f(s): return ImageFont.truetype(CAV, s)
def heart(d, x, y, s, c):
    d.ellipse([x - s, y - s * .6, x, y + s * .4], fill=c); d.ellipse([x, y - s * .6, x + s, y + s * .4], fill=c)
    d.polygon([(x - s * .97, y + .05 * s), (x + s * .97, y + .05 * s), (x, y + s * 1.25)], fill=c)
def frame(spec):
    bg, ink, red = THEMES[spec.get("theme", "cream")]
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im); rnd = random.Random(7)
    for _ in range(9000):  # paper grain
        x, y = rnd.randrange(W), rnd.randrange(H); v = rnd.randint(-10, 10)
        im.putpixel((x, y), tuple(max(0, min(255, c + v)) for c in bg))
    # hook (auto-fit)
    hs = 118
    for line_i, line in enumerate(spec["hook"].split("\n")):
        s = hs
        while f(s).getlength(line) > 960: s -= 4
        d.text((W / 2, 150 + line_i * (s + 6)), line, font=f(s), fill=ink, anchor="mm")
    d.text((W / 2, 150 + len(spec["hook"].split("\n")) * (hs + 6) + 10), spec["sub"], font=f(64), fill=red, anchor="mm")
    if spec.get("layout") == "list":  # one column for longer answers ("at a wedding")
        rows = spec["rows"]; top = 470; bottom = 1700; rh = (bottom - top) / len(rows)
        for i, (a, b) in enumerate(rows):
            y = top + i * rh + rh / 2; sz = int(min(rh * .72, 96))
            while (f(sz).getlength(a) > 330 or f(sz).getlength(b) > 470) and sz > 36: sz -= 4
            d.text((430, y), a, font=f(sz), fill=ink, anchor="rm"); heart(d, 480, y - 6, min(rh * .18, 24), red)
            d.text((530, y), b, font=f(sz), fill=red, anchor="lm")
        d.text((W / 2, 1790), spec["footer"], font=f(66), fill=ink, anchor="mm")
        return im
    rows = spec["rows"]; n = (len(rows) + 1) // 2; top = 470; bottom = 1700; rh = (bottom - top) / n
    for i, (a, b) in enumerate(rows):
        col, r = divmod(i, n); cx = 290 if col == 0 else 790; y = top + r * rh + rh / 2
        sz = int(rh * .78)
        while max(f(sz).getlength(a), f(sz).getlength(b)) > 165 and sz > 40: sz -= 4
        hr = min(rh * .2, 26)
        d.text((cx - 105 - (len(a) > 1) * 30, y), a, font=f(sz), fill=ink, anchor="mm")
        heart(d, cx - 10, y - 6, hr, red)
        d.text((cx + 90 + (len(b) > 1) * 30, y), b, font=f(sz), fill=red, anchor="mm")
    d.line([(W / 2, top + 10), (W / 2, bottom - 10)], fill=ink, width=3)
    d.text((W / 2, 1790), spec["footer"], font=f(66), fill=ink, anchor="mm")
    return im
def main(sp, out):
    spec = json.load(open(sp)); im = frame(spec); png = out + ".png"; im.save(png)
    dur = spec.get("dur", 8)
    vf = (f"scale=1188:-1,zoompan=z='min(1.0+0.0009*on,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(dur*30)}:s=1080x1920:fps=30,format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-vf", vf, "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-shortest", out], check=True)
    print(out)
if __name__ == "__main__": main(*sys.argv[1:3])
