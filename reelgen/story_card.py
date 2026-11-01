"""Daily story card (1080x1920 JPG): date, "today's love message", short message, angel number, soft CTA.
Story replies arrive as DMs (good engagement signal); the autopilot never replies to DMs itself.

spec: {"date": "2026-11-02", "title": "today's love message", "message": str, "number": "222",
       "cta": "reply 💜 if this is for you", "seed": int}
usage: python3 reelgen/story_card.py spec.json out.jpg
"""
import datetime as dt, json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FONT_B, FONT_M, text_block, boxed
from reveal_reel import nebula

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
GOLD = (255, 214, 102, 255); WHITE = (255, 255, 255, 255)

def serif(size, wt=700):
    f = ImageFont.truetype(os.path.join(FONTS, "Cinzel.ttf"), size); f.set_variation_by_axes([wt]); return f

def glow_text(s, font, color):
    w = int(font.getlength(s)) + 80; h = font.size + 80
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).text((40, 25), s, font=font, fill=color)
    g = im.filter(ImageFilter.GaussianBlur(14)); out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im); return out

def render(spec, out):
    neb = nebula(spec.get("seed", 5))
    f = neb.crop(((neb.width - W) // 2, (neb.height - H) // 2, (neb.width - W) // 2 + W, (neb.height - H) // 2 + H)).convert("RGBA")
    d = dt.date.fromisoformat(spec["date"])
    date_s = d.strftime("%A, %b ") + str(d.day)
    def center(img, y): f.alpha_composite(img, (int(W / 2 - img.width / 2), int(y)))
    center(text_block(date_s.upper(), 40, (230, 220, 255, 255), 900, FONT_M), 330)
    t = glow_text(spec.get("title", "today's love message").upper(), serif(64), GOLD); center(t, 400)
    num = glow_text(spec.get("number", "222"), serif(230, 800), (255, 236, 190, 255)); center(num, 560)
    msg = text_block(spec["message"], 62, WHITE, 900, FONT_B, gap=0.12)
    card = boxed(msg, 50, 40, (20, 10, 40, 170), 34); center(card, 960)
    cta = boxed(text_block(spec.get("cta", "reply 💜 if this is for you"), 50, (20, 16, 40, 255), 820, gap=0.08), 40, 24, GOLD, 26)
    center(cta, 960 + card.height + 70)
    center(text_block("@soulmatesigns.daily", 36, (230, 220, 255, 200), 900, FONT_M), 1700)
    f.convert("RGB").save(out, quality=92)
    print("ok", out)

if __name__ == "__main__":
    render(json.load(open(sys.argv[1])), sys.argv[2])
