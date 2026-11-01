"""Daily carousel post: 1080x1350 slides — cover, 3-5 item slides, closing CTA slide.
spec: {"title": "5 signs you've already met your soulmate", "kicker": "save this 💫",
       "items": [{"head": "time disappears", "body": "hours feel like minutes when you're together"}, ...],
       "cta": "which one is you? 👇 save this + send it to your person", "seed": int}
usage: python3 reelgen/carousel.py spec.json outdir   → outdir/slide1.jpg ... slideN.jpg
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import FONT_B, FONT_M, text_block, boxed
from reveal_reel import nebula

W, H = 1080, 1350
FONTS = os.path.join(os.path.dirname(__file__), "fonts")
GOLD = (255, 214, 102, 255); WHITE = (255, 255, 255, 255); SOFT = (230, 220, 255, 230)

def serif(size, wt=700):
    f = ImageFont.truetype(os.path.join(FONTS, "Cinzel.ttf"), size); f.set_variation_by_axes([wt]); return f

def serif_block(text, size, color, maxw):
    f = serif(size); words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); lh = int(size * 1.22)
    im = Image.new("RGBA", (maxw + 40, lh * len(lines) + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(lines): d.text(((im.width - f.getlength(l)) / 2, 10 + i * lh), l, font=f, fill=color)
    g = im.filter(ImageFilter.GaussianBlur(10)); out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(im)
    return out

def bg(seed):
    n = nebula(seed); return n.crop(((n.width - W) // 2, (n.height - H) // 2, (n.width - W) // 2 + W, (n.height - H) // 2 + H)).convert("RGBA")

def center(f, img, y): f.alpha_composite(img, (int(W / 2 - img.width / 2), int(y)))

def footer(f, i, n):
    center(f, text_block(f"@soulmatesigns.daily   ·   {i}/{n}" + ("   swipe >>" if i < n else ""), 30, SOFT, 900, FONT_M), H - 90)

def render(spec, outdir):
    os.makedirs(outdir, exist_ok=True); seed = spec.get("seed", 3); items = spec["items"]; n = len(items) + 2
    f = bg(seed); t = serif_block(spec["title"].upper(), 92, GOLD, 920)
    center(f, t, H / 2 - t.height / 2 - 60)
    center(f, boxed(text_block(spec.get("kicker", "save this 💫"), 44, (20, 16, 40, 255), 700, gap=0.08), 36, 20, GOLD, 24), H / 2 + t.height / 2)
    footer(f, 1, n); f.convert("RGB").save(f"{outdir}/slide1.jpg", quality=92)
    for k, it in enumerate(items, start=2):
        f = bg(seed + k)
        num = serif_block(f"{k - 1}", 260, (255, 236, 190, 255), 400); center(f, num, 250)
        head = serif_block(it["head"].upper(), 76, GOLD, 920); center(f, head, 640)
        body = boxed(text_block(it["body"], 56, WHITE, 860, FONT_M, gap=0.12), 48, 38, (20, 10, 40, 170), 30)
        center(f, body, 660 + head.height + 30); footer(f, k, n); f.convert("RGB").save(f"{outdir}/slide{k}.jpg", quality=92)
    f = bg(seed + 99)
    c = serif_block("WHICH ONE IS YOU?", 92, GOLD, 920); y = 360; center(f, c, y); y += c.height + 40
    b = boxed(text_block(spec.get("cta", "save this + send it to your person 💌"), 50, (20, 16, 40, 255), 820, gap=0.08), 40, 26, GOLD, 26); center(f, b, y); y += b.height + 60
    center(f, text_block("curious what your soulmate looks like?\nlink in bio ✨", 50, WHITE, 900, FONT_M, gap=0.15), y)
    footer(f, n, n); f.convert("RGB").save(f"{outdir}/slide{n}.jpg", quality=92)
    print("ok", n, "slides")

if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
