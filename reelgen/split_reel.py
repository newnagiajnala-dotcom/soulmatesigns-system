"""6-vs-6 zodiac split reel (format F0). Renders a 1080x1920 30fps MP4 + cover PNG from a JSON spec.

usage: python3 reelgen/split_reel.py spec.json out_basename [--frames t1,t2,...]
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
FONT_B = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
SYMBOL = {"aries":"♈","taurus":"♉","gemini":"♊","cancer":"♋","leo":"♌","virgo":"♍","libra":"♎",
          "scorpio":"♏","sagittarius":"♐","capricorn":"♑","aquarius":"♒","pisces":"♓"}
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F300 or 0x2600 <= o <= 0x27BF and ch not in SYMBOL.values()

_emoji_font = None
def emoji_img(ch, size):
    global _emoji_font
    if _emoji_font is None:
        _emoji_font = ImageFont.truetype(EMOJI, 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=_emoji_font, embedded_color=True)
    im = im.crop(im.getbbox())
    s = size / im.height
    return im.resize((max(1, int(im.width * s)), int(size)), Image.LANCZOS)

def rich_line(text, font, color, size):
    """Render one line mixing text and emoji into an RGBA image."""
    parts, buf = [], ""
    for ch in text:
        if is_emoji(ch) or ch == "️":
            if ch == "️":
                continue
            if buf: parts.append(("t", buf)); buf = ""
            parts.append(("e", ch))
        else:
            buf += ch
    if buf: parts.append(("t", buf))
    asc, desc = font.getmetrics()
    lh = asc + desc
    imgs = []
    for kind, val in parts:
        if kind == "t":
            w = int(font.getlength(val))
            im = Image.new("RGBA", (max(1, w), lh), (0, 0, 0, 0))
            ImageDraw.Draw(im).text((0, 0), val, font=font, fill=color)
            imgs.append(im)
        else:
            e = emoji_img(val, size * 0.95)
            im = Image.new("RGBA", (e.width + int(size * .12), lh), (0, 0, 0, 0))
            im.alpha_composite(e, (int(size * .06), int((lh - e.height) / 2)))
            imgs.append(im)
    out = Image.new("RGBA", (sum(i.width for i in imgs), lh), (0, 0, 0, 0))
    x = 0
    for i in imgs:
        out.alpha_composite(i, (x, 0)); x += i.width
    return out

def wrap(text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def text_block(text, size, color, maxw, font_path=FONT_B, align="center", gap=0.12):
    f = ImageFont.truetype(font_path, size)
    lines = [rich_line(l, f, color, size) for l in wrap(text, f, maxw)]
    lh = lines[0].height
    out = Image.new("RGBA", (max(l.width for l in lines), int(lh * (1 + gap) * len(lines))), (0, 0, 0, 0))
    for i, l in enumerate(lines):
        x = (out.width - l.width) // 2 if align == "center" else 0
        out.alpha_composite(l, (x, int(i * lh * (1 + gap))))
    return out

def boxed(img, pad_x, pad_y, fill, radius):
    out = Image.new("RGBA", (img.width + 2 * pad_x, img.height + 2 * pad_y), (0, 0, 0, 0))
    ImageDraw.Draw(out).rounded_rectangle([0, 0, out.width - 1, out.height - 1], radius, fill=fill)
    out.alpha_composite(img, (pad_x, pad_y))
    return out

def bubble(text, incoming, size=50, maxw=430):
    fill = (58, 52, 92, 255) if incoming else (124, 92, 255, 255)
    t = text_block(text, size, (255, 255, 255, 255), maxw, FONT_M, gap=0.05)
    return boxed(t, 34, 20, fill, 40)

def sign_stack(signs, color):
    rows = []
    f = ImageFont.truetype(FONT_B, 58)
    sf = ImageFont.truetype(DEJAVU, 52)
    for s in signs:
        sym = SYMBOL.get(s.lower(), "")
        w = int(sf.getlength(sym)) + 16 + int(f.getlength(s))
        im = Image.new("RGBA", (w, 84), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        d.text((0, 12), sym, font=sf, fill=color)
        d.text((int(sf.getlength(sym)) + 16, 0), s, font=f, fill=(255, 255, 255, 255))
        rows.append(im)
    return rows

def ease_back(x):
    x = max(0.0, min(1.0, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2

def ease_out(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3

def background():
    bg = Image.new("RGB", (W, H))
    top, mid, bot = (14, 10, 38), (46, 24, 84), (112, 46, 106)
    px = bg.load()
    for y in range(H):
        t = y / H
        c = [int(top[i] + (mid[i] - top[i]) * (t / .6)) if t < .6 else int(mid[i] + (bot[i] - mid[i]) * ((t - .6) / .4)) for i in range(3)]
        for x in range(W):
            px[x, y] = tuple(c)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W - 420, 40, W + 120, 580], fill=(255, 196, 228, 70))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    bg = Image.alpha_composite(bg.convert("RGBA"), glow)
    return bg

def build(spec):
    random.seed(spec.get("seed", 11))
    L = {}
    L["title"] = boxed(text_block(spec["title"], 66, (20, 16, 40, 255), 860, gap=0.08), 46, 30, (255, 255, 255, 255), 28)
    L["incoming"] = bubble(spec["incoming"], True, 54)
    L["lhead"] = text_block(spec["left"]["head"], 42, (255, 214, 102, 255), 440)
    L["rhead"] = text_block(spec["right"]["head"], 42, (255, 214, 102, 255), 400)
    L["lbub"] = bubble(spec["left"]["reply"], False, 46, 400)
    L["rbub"] = bubble(spec["right"]["reply"], False, 46, 360)
    L["rseen"] = text_block(spec["right"].get("seen", ""), 30, (190, 180, 230, 255), 400, FONT_M) if spec["right"].get("seen") else None
    L["lsigns"] = sign_stack(spec["left"]["signs"], (255, 214, 102, 255))
    L["rsigns"] = sign_stack(spec["right"]["signs"], (255, 214, 102, 255))
    L["cta"] = boxed(text_block(spec["cta"], 58, (20, 16, 40, 255), 780, gap=0.08), 42, 26, (255, 214, 102, 255), 28)
    L["stars"] = [(random.randint(0, W), random.randint(0, int(H * .9)), random.choice([1.5, 2, 2.5, 3.5]), random.random() * 6.28) for _ in range(130)]
    return L

T = {"title": 0.15, "incoming": 0.9, "left": 2.1, "right": 4.6, "cta": 7.6, "end": 10.4}

def paste_pop(frame, img, cx, cy, t0, t, dur=0.38, anchor="center"):
    if t < t0: return
    k = ease_back((t - t0) / dur)
    a = ease_out((t - t0) / (dur * 0.7))
    s = 0.6 + 0.4 * k
    im = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))), Image.BILINEAR) if s != 1 else img
    if a < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    x = int(cx - im.width / 2) if anchor == "center" else int(cx)
    y = int(cy - im.height / 2)
    frame.alpha_composite(im, (x, y))

def frame_at(t, BG, L):
    f = BG.copy()
    d = ImageDraw.Draw(f)
    for (x, y, r, ph) in L["stars"]:
        if 40 < x < 1040 and 150 < y < 1720:
            continue  # keep the text area clean
        a = int(120 + 120 * math.sin(t * 2.2 + ph))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 245, 255, max(30, a)))
    paste_pop(f, L["title"], W / 2, 320, T["title"], t)
    paste_pop(f, L["incoming"], W / 2, 545, T["incoming"], t)
    # divider
    if t >= T["left"]:
        a = int(140 * ease_out((t - T["left"]) / .4))
        d.line([(W / 2, 650), (W / 2, 1410)], fill=(255, 255, 255, a), width=3)
    lx, rx = 290, 770
    paste_pop(f, L["lhead"], lx, 690, T["left"], t)
    paste_pop(f, L["lbub"], lx, 815, T["left"] + .35, t)
    for i, row in enumerate(L["lsigns"]):
        paste_pop(f, row, lx, 960 + i * 82, T["left"] + .7 + i * .13, t, .3)
    paste_pop(f, L["rhead"], rx, 690, T["right"], t)
    if L["rseen"] is not None:
        paste_pop(f, L["rseen"], rx, 745, T["right"] + .2, t)
    paste_pop(f, L["rbub"], rx, 835, T["right"] + .55, t)
    for i, row in enumerate(L["rsigns"]):
        paste_pop(f, row, rx, 960 + i * 82, T["right"] + .9 + i * .13, t, .3)
    paste_pop(f, L["cta"], W / 2, 1555, T["cta"], t, .45)
    return f

def main():
    spec = json.load(open(sys.argv[1])); base = sys.argv[2]
    BG, L = background(), build(spec)
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            frame_at(float(ts), BG, L).convert("RGB").save(f"{base}_f{ts}.jpg", quality=90)
        return
    frame_at(T["end"] - .5, BG, L).convert("RGB").save(base + "_cover.jpg", quality=92)
    tmp = base + ".part.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k",
                          "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
    n = int(T["end"] * FPS)
    for i in range(n):
        p.stdin.write(frame_at(i / FPS, BG, L).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, base + ".mp4")
        sys.path.insert(0, os.path.dirname(__file__)); from music import add_to_video
        add_to_video(base + ".mp4", spec.get("music", "playful"), spec.get("seed", 1))
        print("ok", base + ".mp4")
    else:
        print("ffmpeg failed"); sys.exit(1)

if __name__ == "__main__":
    main()
