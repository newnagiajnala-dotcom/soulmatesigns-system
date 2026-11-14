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
def card(base, spec, lines, big=None):
    """Dim the chart and put a centred card on top (intro question / end CTA)."""
    bg, ink, red = THEMES[spec.get("theme", "cream")]
    im = base.copy().filter(ImageFilter.GaussianBlur(6))
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 120)); im = Image.alpha_composite(im.convert("RGBA"), ov)
    d = ImageDraw.Draw(im); x0, x1 = 70, W - 70
    hts = [(t, 96) for t in lines]
    if big: hts.insert(big[0], (big[1], 230))
    total = sum(sz + 24 for _, sz in hts) + 120; y0 = (H - total) // 2
    d.rounded_rectangle([x0, y0, x1, y0 + total], 48, fill=bg + (255,))
    y = y0 + 70
    for t, sz in hts:
        s2 = sz
        while f(s2).getlength(t) > x1 - x0 - 90: s2 -= 4
        d.text((W / 2, y + s2 / 2), t, font=f(s2), fill=red if sz > 150 else ink, anchor="mm"); y += s2 + 24
    return im.convert("RGB")
def seg(png, dur, out, zoom):
    vf = (f"scale=1188:-1,zoompan=z='min(1.0+{zoom}*on,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(dur*30)}:s=1080x1920:fps=30,format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", png, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                    "-vf", vf, "-t", str(dur), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-shortest", out], check=True)
def main(sp, out):
    spec = json.load(open(sp)); im = frame(spec); png = out + ".png"; im.save(png)
    dur = spec.get("dur", 8)
    intro = spec.get("intro", ["Who's the first person", "that came to your mind?"])
    end = spec.get("end", ["if you want to see", "your soulmate's face"])
    if spec.get("cards", True):
        tmp = out + "_parts"; os.makedirs(tmp, exist_ok=True)
        card(im, spec, intro).save(f"{tmp}/a.png"); card(im, spec, end, big=(0, "Type YES")).save(f"{tmp}/c.png")
        seg(f"{tmp}/a.png", 2.0, f"{tmp}/a.mp4", 0.0004); seg(png, dur, f"{tmp}/b.mp4", 0.0009); seg(f"{tmp}/c.png", 3.0, f"{tmp}/c.mp4", 0.0004)
        open(f"{tmp}/l.txt", "w").write("".join(f"file '{os.path.abspath(tmp)}/{x}.mp4'\n" for x in "abc"))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{tmp}/l.txt", "-c", "copy", out], check=True)
        import shutil; shutil.rmtree(tmp)
    else:
        seg(png, dur, out, 0.0009)
    print(out)
if __name__ == "__main__": main(*sys.argv[1:3])
