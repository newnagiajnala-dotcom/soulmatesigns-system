"""Chart CAROUSEL + chart PHOTO POST (1080x1350, same hand-drawn look as chart_reel.py).
Owner 15 Nov 2026: daily = 1 reel + 1 carousel + 1 photo post, copied from proven viral chart formats.
usage:
  python3 reelgen/chart_carousel.py <chart spec.json> <outdir>
spec = a chart spec (hook, sub, rows, theme, footer, trigger) — same file as promo/chart/chartN.json.
writes:
  outdir/slide1.jpg            cover: hook + sub + "swipe to find yours"
  outdir/slide2..k.jpg         3 rows per slide, big
  outdir/slideN_fb.jpg         last slide for Facebook: "Comment <WORD>" (Comment-to-message / bot sends the link)
  outdir/slideN_ig.jpg         last slide for Instagram: "link in bio"
  outdir/post_fb.jpg / post_ig.jpg   single photo post: whole chart + CTA line
"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chart_reel import THEMES, f, heart
import random

W, H = 1080, 1350

def base(spec):
    bg, ink, red = THEMES[spec.get("theme", "night")]
    im = Image.new("RGB", (W, H), bg); rnd = random.Random(7)
    for _ in range(6000):
        x, y = rnd.randrange(W), rnd.randrange(H); v = rnd.randint(-10, 10)
        im.putpixel((x, y), tuple(max(0, min(255, c + v)) for c in bg))
    return im, ImageDraw.Draw(im), ink, red

def fit(d, text, size, maxw):
    while f(size).getlength(text) > maxw and size > 30: size -= 4
    return size

def handle(d, ink, i=None, n=None):
    t = "@soulmatesigns.daily" + (f"   ·   {i}/{n}" if i else "")
    d.text((W / 2, H - 60), t, font=f(40), fill=ink, anchor="mm")

def hook_block(d, spec, ink, red, y0, big=120):
    y = y0
    for line in spec["hook"].split("\n"):
        s = fit(d, line, big, 960); d.text((W / 2, y), line, font=f(s), fill=ink, anchor="mm"); y += s + 8
    d.text((W / 2, y + 20), spec["sub"], font=f(66), fill=red, anchor="mm")
    return y + 60

def rows_block(d, rows, ink, red, top, bottom, maxsz=110):
    rh = (bottom - top) / len(rows)
    for i, (a, b) in enumerate(rows):
        y = top + i * rh + rh / 2; sz = int(min(rh * .7, maxsz))
        while (f(sz).getlength(a) > 380 or f(sz).getlength(b) > 470) and sz > 30: sz -= 4
        d.text((450, y), a, font=f(sz), fill=ink, anchor="rm"); heart(d, 508, y - 6, min(rh * .17, 28), red)
        d.text((560, y), b, font=f(sz), fill=red, anchor="lm")

def cta(spec, platform):
    w = spec.get("post_trigger", "YES")  # feed posts: YES = owner's Comment-to-message keyword
    if platform == "fb":
        return ["Want to see your", "soulmate's face?", f"Comment {w}", "and we'll message you the link"]
    return ["Want to see your", "soulmate's face?", "tap the link", "in our bio"]

def render(spec, out):
    os.makedirs(out, exist_ok=True); rows = spec["rows"]
    per = max(3, -(-len(rows) // 8))  # IG carousel max 10 items: cover + <=8 row slides + CTA
    chunks = [rows[i:i + per] for i in range(0, len(rows), per)]
    n = len(chunks) + 2
    im, d, ink, red = base(spec); y = hook_block(d, spec, ink, red, 430, 150)
    d.text((W / 2, y + 150), "swipe to find yours  >>", font=f(64), fill=ink, anchor="mm"); handle(d, ink, 1, n)
    im.save(f"{out}/slide1.jpg", quality=92)
    for k, ch in enumerate(chunks, 2):
        im, d, ink, red = base(spec)
        d.text((W / 2, 130), spec["hook"].replace("\n", " ").lower(), font=f(fit(d, spec["hook"].replace("\n", " ").lower(), 60, 960)), fill=ink, anchor="mm")
        rows_block(d, ch, ink, red, 260, 1150, 130); handle(d, ink, k, n)
        im.save(f"{out}/slide{k}.jpg", quality=92)
    for p in ("fb", "ig"):
        im, d, ink, red = base(spec); lines = cta(spec, p); y = 420
        for j, t in enumerate(lines):
            big = j == 2; s = fit(d, t, 170 if big else 92, 960)
            d.text((W / 2, y), t, font=f(s), fill=red if big else ink, anchor="mm"); y += s + (40 if big else 24)
        handle(d, ink, n, n); im.save(f"{out}/slide{n}_{p}.jpg", quality=92)
        # single photo post
        im, d, ink, red = base(spec); y = hook_block(d, spec, ink, red, 110, 96)
        rows_block(d, rows, ink, red, y + 10, H - 190, 80)
        line = f"comment {spec.get('post_trigger', 'YES')} to see their face" if p == "fb" else (spec.get("footer") or "send this to your person")
        d.text((W / 2, H - 130), line, font=f(fit(d, line, 62, 960)), fill=ink, anchor="mm"); handle(d, ink)
        im.save(f"{out}/post_{p}.jpg", quality=92)
    return n

if __name__ == "__main__":
    print(render(json.load(open(sys.argv[1])), sys.argv[2]))
