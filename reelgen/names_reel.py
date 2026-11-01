"""Name-writing reel: a pen writes two first names on notebook paper, then a "love number" and its meaning.
Faceless. If the names came from a real comment, set "reply_to" to that @handle to show a reply bubble;
never invent a reply bubble.

spec: {"name1": "Ashley", "name2": "Daniel", "reply_to": "" (only for real comments), "cta": str,
       "music": "playful", "seed": int}
usage: python3 reelgen/names_reel.py spec.json out_base [--frames t1,t2]
"""
import json, math, os, subprocess, sys, hashlib
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FPS, FONT_B, FONT_M, text_block, boxed, paste_pop, ease_out

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
INK = (28, 40, 110, 255)

NUMBERS = {  # love number -> short meaning (entertainment)
    "111": "a brand-new beginning together ✨", "222": "balance: you bring out the best in each other 💞",
    "333": "you'll grow a lot together 🌱", "444": "a steady, protected bond 🛡️", "555": "big changes are coming for you two 🔥",
    "717": "a soul connection that feels familiar 🌙", "777": "lucky in love together 🍀", "888": "abundance and a long future 💫",
    "211": "written in the stars 💫", "1111": "twin-flame energy 🔥",
}

def love_number(a, b):
    key = "".join(sorted([a.lower(), b.lower()]))
    h = int(hashlib.md5(key.encode()).hexdigest(), 16)
    return list(NUMBERS)[h % len(NUMBERS)]

def hand_font(size):
    f = ImageFont.truetype(os.path.join(FONTS, "Caveat.ttf"), size)
    f.set_variation_by_axes([600])
    return f

def paper():
    im = Image.new("RGBA", (W, H), (250, 248, 240, 255)); d = ImageDraw.Draw(im)
    for y in range(260, H, 92):
        d.line([(0, y), (W, y)], fill=(150, 190, 230, 255), width=3)
    d.line([(150, 0), (150, H)], fill=(235, 140, 150, 255), width=3)
    shade = Image.new("L", (W, H), 0); sd = ImageDraw.Draw(shade)
    for i in range(60):
        sd.rectangle([i * 4, i * 4, W - i * 4, H - i * 4], outline=int(70 - i * 1.1) if i < 60 else 0)
    shade = shade.filter(ImageFilter.GaussianBlur(40))
    dark = Image.new("RGBA", (W, H), (60, 50, 40, 0)); dark.putalpha(shade)
    im.alpha_composite(dark)
    return im

def ink_text(text, size):
    f = hand_font(size)
    w = int(f.getlength(text)) + 40
    asc, desc = f.getmetrics()
    im = Image.new("RGBA", (w, asc + desc + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 6), text, font=f, fill=INK)
    return im

def pen():
    im = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # pen pointing down-left; tip at (20, 400)
    d.polygon([(20, 400), (60, 330), (78, 348)], fill=(70, 70, 80, 255))
    d.polygon([(60, 330), (360, 30), (392, 60), (78, 348)], fill=(235, 236, 240, 255), outline=(170, 172, 180, 255))
    d.polygon([(250, 140), (300, 90), (330, 120), (280, 170)], fill=(210, 90, 140, 255))
    return im.filter(ImageFilter.SMOOTH)

def build(spec):
    n1, n2 = spec["name1"], spec["name2"]
    num = spec.get("number") or love_number(n1, n2)
    L = {"paper": paper(), "pen": pen(),
         "lines": [ink_text(n1, 150), ink_text("+", 120), ink_text(n2, 150), ink_text(num, 190)],
         "meaning": boxed(text_block(f"{num} = {NUMBERS.get(num, spec.get('meaning', ''))}", 50, (255, 255, 255, 255), 860, FONT_M, gap=0.08), 34, 22, (124, 92, 255, 235), 26),
         "cta": boxed(text_block(spec["cta"], 52, (20, 16, 40, 255), 840, gap=0.08), 40, 24, (255, 214, 102, 255), 26),
         "reply": None}
    if spec.get("reply_to"):
        t = text_block(f"Reply to {spec['reply_to']}'s comment\n", 30, (90, 90, 100, 255), 700, FONT_M)
        nm = text_block(f"{n1} & {n2} 🥰", 44, (20, 20, 30, 255), 700)
        card = Image.new("RGBA", (max(t.width, nm.width) + 60, t.height + nm.height + 40), (0, 0, 0, 0))
        ImageDraw.Draw(card).rounded_rectangle([0, 0, card.width - 1, card.height - 1], 22, fill=(255, 255, 255, 245))
        card.alpha_composite(t, (30, 16)); card.alpha_composite(nm, (30, 16 + t.height))
        L["reply"] = card
    L["ys"] = [560, 760, 930, 1190]
    L["dur"] = [1.4, 0.5, 1.4, 1.2]
    t = 0.9; L["starts"] = []
    for d in L["dur"]:
        L["starts"].append(t); t += d + 0.25
    L["t_meaning"] = t + 0.2; L["t_cta"] = L["t_meaning"] + 2.6; L["end"] = L["t_cta"] + 2.8
    return L

def frame_at(t, L):
    f = L["paper"].copy()
    tip = None
    for img, y, st, du in zip(L["lines"], L["ys"], L["starts"], L["dur"]):
        if t < st: continue
        k = min(1.0, (t - st) / du)
        x0 = int(W / 2 - img.width / 2)
        w = max(1, int(img.width * k))
        f.alpha_composite(img.crop((0, 0, w, img.height)), (x0, int(y - img.height / 2)))
        if k < 1:
            wob = math.sin(t * 40) * 10
            tip = (x0 + w, int(y + img.height * 0.15 + wob))
    if tip is None and t < L["t_meaning"]:
        tip = (int(W / 2 + 260), 1260)
    if tip and t < L["t_meaning"] + 0.3:
        p = L["pen"]; f.alpha_composite(p, (tip[0] - 20, tip[1] - 400))
    if L["reply"] is not None:
        paste_pop(f, L["reply"], W / 2, 270, 0.15, t)
    paste_pop(f, L["meaning"], W / 2, 1400, L["t_meaning"], t, .4)
    paste_pop(f, L["cta"], W / 2, 1610, L["t_cta"], t, .45)
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
    add_to_video(base + ".mp4", spec.get("music", "playful"), spec.get("seed", 1))
    print("ok", base + ".mp4", f"{L['end']:.1f}s")

if __name__ == "__main__":
    main()
