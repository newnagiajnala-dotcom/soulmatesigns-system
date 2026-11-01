"""'If you are seeing this on <3 dates>, it's a sign' reel. Mystic nebula, drifting glowing angel numbers,
big serif text, short message, comment CTA ("type 222 to claim it").

spec: {"start_date": "2026-11-03" (first of the 3 dates; default = today US Eastern), "message": [str, str],
       "cta": "type 222 to claim it 🙏", "music": "emotional", "seed": int}
usage: python3 reelgen/sign_reel.py spec.json out_base [--frames t1,t2]
"""
import datetime as dt, json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FPS, FONT_B, FONT_M, text_block, boxed, paste_pop, ease_out
from reveal_reel import nebula

FONTS = os.path.join(os.path.dirname(__file__), "fonts")
GOLD = (255, 214, 102, 255); WHITE = (255, 255, 255, 255)
ANGEL = ["11:11", "222", "333", "444", "555", "777", "888", "1111", "1212"]

def serif_block(text, size, color, maxw):
    f = ImageFont.truetype(os.path.join(FONTS, "Cinzel.ttf"), size); f.set_variation_by_axes([700])
    words, lines, cur = text.split(), [], ""
    for w in words:
        tt = (cur + " " + w).strip()
        if f.getlength(tt) <= maxw or not cur: cur = tt
        else: lines.append(cur); cur = w
    lines.append(cur)
    lh = int(size * 1.25)
    im = Image.new("RGBA", (maxw + 40, lh * len(lines) + 30), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); d, ds = ImageDraw.Draw(im), ImageDraw.Draw(sh)
    for i, l in enumerate(lines):
        x = (im.width - f.getlength(l)) / 2
        ds.text((x + 3, 15 + i * lh + 3), l, font=f, fill=(0, 0, 0, 220))
        d.text((x, 15 + i * lh), l, font=f, fill=color)
    sh = sh.filter(ImageFilter.GaussianBlur(7)); sh.alpha_composite(im)
    return sh

def glow_num(s, size):
    f = ImageFont.truetype(FONT_B, size)
    im = Image.new("RGBA", (int(f.getlength(s)) + 60, size + 60), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30, 20), s, font=f, fill=(255, 236, 190, 255))
    g = im.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im)
    return out

def dates_text(start):
    ds = [start + dt.timedelta(days=i) for i in range(3)]
    m = ds[0].strftime("%b")
    if all(d.month == ds[0].month for d in ds):
        return f"{m} {ds[0].day}, {ds[1].day} or {ds[2].day}"
    return f"{ds[0].strftime('%b')} {ds[0].day}, {ds[1].strftime('%b')} {ds[1].day} or {ds[2].strftime('%b')} {ds[2].day}"

def build(spec):
    rnd = random.Random(spec.get("seed", 2))
    if spec.get("start_date"):
        start = dt.date.fromisoformat(spec["start_date"])
    else:
        start = (dt.datetime.utcnow() - dt.timedelta(hours=5)).date()
    L = {"neb": nebula(spec.get("seed", 2) + 31),
         "l1": serif_block(f"If you are seeing this on {dates_text(start)},", 74, WHITE, 900),
         "l2": serif_block("it's a sign.", 110, GOLD, 900),
         "msg": [text_block(m, 52, WHITE, 880, FONT_M, gap=0.1) for m in spec["message"]],
         "cta": boxed(text_block(spec.get("cta", "type 222 to claim it 🙏"), 56, (20, 16, 40, 255), 820, gap=0.08), 42, 24, GOLD, 26),
         "floats": [(glow_num(rnd.choice(ANGEL), rnd.choice([44, 52, 64])), rnd.uniform(60, W - 220), rnd.choice([rnd.uniform(110, 330), rnd.uniform(1600, 1800)]),
                     rnd.uniform(0, 6.28), rnd.uniform(18, 40)) for _ in range(7)]}
    L["t_msg"] = 4.2; L["t_cta"] = L["t_msg"] + 2.4 * len(L["msg"]) + 0.3; L["end"] = L["t_cta"] + 3.0
    return L

def frame_at(t, L):
    z = 1.0 + 0.1 * (t / L["end"]); neb = L["neb"]
    cw, ch = int(W * 1.25 / z), int(H * 1.25 / z)
    x0, y0 = (neb.width - cw) // 2, (neb.height - ch) // 2
    f = neb.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    for img, x, y, ph, amp in L["floats"]:
        a = 0.35 + 0.35 * (1 + math.sin(t * 1.3 + ph)) / 2
        im = img.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
        f.alpha_composite(im, (int(x + math.sin(t * 0.7 + ph) * amp), int(y + math.cos(t * 0.9 + ph) * amp)))
    if t < L["t_msg"]:
        paste_pop(f, L["l1"], W / 2, 760, 0.3, t, .5)
        paste_pop(f, L["l2"], W / 2, 1010, 1.9, t, .5)
    else:
        paste_pop(f, L["l2"], W / 2, 520, L["t_msg"], t, .01)
        for i, m in enumerate(L["msg"]):
            paste_pop(f, m, W / 2, 820 + i * 220, L["t_msg"] + 0.2 + i * 2.4, t, .4)
        paste_pop(f, L["cta"], W / 2, 1460, L["t_cta"], t, .45)
    return f

def main():
    spec = json.load(open(sys.argv[1])); base = sys.argv[2]
    L = build(spec)
    if "--frames" in sys.argv:
        for ts in sys.argv[sys.argv.index("--frames") + 1].split(","):
            frame_at(float(ts), L).convert("RGB").save(f"{base}_f{ts}.jpg", quality=90)
        return
    frame_at(2.6, L).convert("RGB").save(base + "_cover.jpg", quality=92)
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
