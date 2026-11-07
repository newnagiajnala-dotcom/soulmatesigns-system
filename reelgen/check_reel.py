"""SOULMATE CHECK reel: red marker handwriting writes itself on a photo of a notebook page (a maths ritual viewers repeat
with their own number and comment). Original format inspired by the 'soulmate check' trend, own formula + own visuals.

spec: {"bg": "page.png", "label": "SOULMATE CHECK",
       "steps": [{"text": "1998", "x": 330, "y": 640, "size": 190, "t": 1.0, "d": 1.4}, ...   # write a line
                 {"line": [300, 1010, 760, 1010], "t": 4.6, "d": 0.5},                      # draw a rule
                 {"circle": [400, 1050, 760, 1260], "t": 7.0, "d": 1.0}],                   # circle (bbox)
       "cta": "COMMENT YOUR NUMBER", "cta_t": 13.0, "dur": 16.0, "rot": -6, "music": "x.mp3"}
usage (Higgsfield sandbox): python3 check_reel.py spec.json outdir   (needs Caveat.ttf next to the script)
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
INK = (206, 22, 52, 255)
HERE = os.path.dirname(os.path.abspath(__file__))

def hand(size):
    f = ImageFont.truetype(os.path.join(HERE, "Caveat.ttf"), size)
    try: f.set_variation_by_axes([700])
    except Exception: pass
    return f

def sans(size):
    for p in ["/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf", "/usr/share/fonts/truetype/higgsfield/Montserrat-Bold.ttf"]:
        if os.path.exists(p): return ImageFont.truetype(p, size)
    import glob
    g = glob.glob("/usr/share/fonts/**/Montserrat*Bold*.ttf", recursive=True)
    return ImageFont.truetype(g[0], size)

def ease(p): return 1 - (1 - max(0, min(1, p))) ** 2

def text_img(s, size):
    f = hand(size); w = int(f.getlength(s)) + 30; a, d = f.getmetrics()
    im = Image.new("RGBA", (w, a + d + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 6), s, font=f, fill=INK)
    return im

def spec_from_check(base, c, bg, music):
    L = base["layout"]
    def tx(key, text):
        x, y, s, t0, d = L[key]; return {"text": text, "x": x, "y": y, "size": s, "t": t0, "d": d}
    x0, y0, x1, y1, t0, d = L["rule"]; cx0, cy0, cx1, cy1, ct, cd = L["circle"]; hx, hy, hs, ht, hd = L["heart"]
    return {"bg": bg, "music": music, "label": c["label"], "rot": base["rot"], "dur": base["dur"], "cta_t": base["cta_t"], "cta": c.get("cta", "COMMENT YOUR NUMBER"),
            "steps": [tx("line1", c["line1"]), tx("line2", c["line2"]), {"line": [x0, y0, x1, y1], "t": t0, "d": d},
                      tx("result", c["result"]), {"circle": [cx0, cy0, cx1, cy1], "t": ct, "d": cd}, {"heart": [hx, hy, hs], "t": ht, "d": hd},
                      tx("t1", c["t1"]), tx("t2", c["t2"])]}

def love_rows(a, b):
    """Viral 'name compatibility' method: count each letter (in order of first appearance) across both names,
    then repeatedly add the outer digits moving inward until 2 digits are left = the love %."""
    s = [ch for ch in (a + b).lower() if ch.isalpha()]; seen = []
    for ch in s:
        if ch not in seen: seen.append(ch)
    ds = [s.count(ch) for ch in seen]; rows = [ds]
    for _ in range(8):
        if len(ds) <= 2: break
        new, i, j = [], 0, len(ds) - 1
        while i < j:
            new += [int(c) for c in str(ds[i] + ds[j])]; i += 1; j -= 1
        if i == j: new.append(ds[i])
        ds = new; rows.append(ds)
    pct = int("".join(map(str, ds[:2])))
    return rows, pct

def spec_from_names(a, b, bg, music, reply=None):
    rows, pct = love_rows(a, b)
    lines = [(a.capitalize(), 1.3), ("+", 0.4), (b.capitalize(), 1.3)] + [("".join(map(str, r)), 0.32 * len(r) + 0.4) for r in rows] + [(f"{pct}%", 1.0)]
    n = len(lines); top, bottom = 430, 1560; h = min(165, (bottom - top) / n)
    steps, t0, y = [], 1.0, top
    for k, (txt, d) in enumerate(lines):
        size = int(h * (1.25 if k == n - 1 else 1.05))
        f = hand(size)
        while f.getlength(txt) > 700 and size > 50: size -= 6; f = hand(size)
        x = int(540 - f.getlength(txt) / 2) - 10
        steps.append({"text": txt, "x": x, "y": int(y), "size": size, "t": round(t0, 2), "d": round(d, 2)})
        t0 += d + (0.5 if k >= 3 else 0.25); y += h
    fy = steps[-1]["y"]; fs = steps[-1]["size"]
    steps.append({"heart": [540, int(fy + fs * 0.55), fs / 26], "t": round(t0, 2), "d": 1.1})
    end = t0 + 1.1
    sp = {"bg": bg, "music": music, "label": "LOVE % CHECK", "rot": -2, "dur": round(end + 3.5, 1), "cta_t": round(end + 0.3, 1),
          "cta": "COMMENT YOUR NAMES", "steps": steps, "pct": pct}
    if reply: sp["reply"] = reply
    return sp

def main():
    if sys.argv[1] == "--names":  # python3 check_reel.py --names Ashley Daniel page.png music.mp3 outdir ["@user|their comment text" only if REAL]
        reply = None
        if len(sys.argv) > 7 and "|" in sys.argv[7]:
            u, tx = sys.argv[7].split("|", 1); reply = {"user": u, "text": tx}
        sp = spec_from_names(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], reply); json.dump(sp, open("spec_built.json", "w"))
        print(json.dumps({"pct": sp["pct"], "dur": sp["dur"]}))
        sys.argv = [sys.argv[0], "spec_built.json", sys.argv[6]]
    if sys.argv[1] == "--check":  # python3 check_reel.py --check checks.json <id> page.png music.mp3 outdir
        d = json.load(open(sys.argv[2])); c = [x for x in d["checks"] if x["id"] == sys.argv[3]][0]
        sp = spec_from_check(d["base"], c, sys.argv[4], sys.argv[5]); json.dump(sp, open("spec_built.json", "w"))
        sys.argv = [sys.argv[0], "spec_built.json", sys.argv[6]]
    spec = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(f"{out}/f", exist_ok=True)
    bg = Image.open(spec["bg"]).convert("RGBA")
    s = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1))
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    dur = spec.get("dur", 16.0); rot = spec.get("rot", -6)
    imgs = {i: text_img(st["text"], st.get("size", 170)) for i, st in enumerate(spec["steps"]) if "text" in st}
    lab = sans(58); ctaf = sans(66)
    n = int(dur * FPS)
    for k in range(n):
        t = k / FPS
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
        tip = None
        for i, st in enumerate(spec["steps"]):
            p = (t - st["t"]) / st["d"]
            if p <= 0: continue
            p = min(p, 1.0)
            if "text" in st:
                im = imgs[i]; cw = max(1, int(im.width * p))
                layer.alpha_composite(im.crop((0, 0, cw, im.height)), (st["x"], st["y"]))
                if p < 1: tip = (st["x"] + cw, st["y"] + int(im.height * 0.62))
            elif "line" in st:
                x0, y0, x1, y1 = st["line"]; xe = x0 + (x1 - x0) * ease(p); ye = y0 + (y1 - y0) * ease(p)
                d.line([(x0, y0), (xe, ye)], fill=INK, width=12)
                if p < 1: tip = (int(xe), int(ye))
            elif "circle" in st:
                x0, y0, x1, y1 = st["circle"]; cx, cy, rx, ry = (x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2, (y1 - y0) / 2
                end = 400 * ease(p); pts = [(cx + rx * math.cos(math.radians(a - 200)), cy + ry * math.sin(math.radians(a - 200))) for a in range(0, int(end) + 1, 4)]
                if len(pts) > 1: d.line(pts, fill=INK, width=11, joint="curve")
                if p < 1 and pts: tip = (int(pts[-1][0]), int(pts[-1][1]))
            elif "heart" in st:
                cx, cy, sc = st["heart"]; end = 2 * math.pi * ease(p)
                pts = [(cx + sc * 16 * math.sin(a) ** 3, cy - sc * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))
                       for a in [end * j / 80 for j in range(81)]]
                d.line(pts, fill=INK, width=10, joint="curve")
                if p < 1: tip = (int(pts[-1][0]), int(pts[-1][1]))
        if tip:  # marker nib
            d.ellipse([tip[0] - 9, tip[1] - 9, tip[0] + 9, tip[1] + 9], fill=(150, 10, 35, 255))
        layer = layer.rotate(rot, resample=Image.BICUBIC, center=(W // 2, H // 2))
        ink = layer.filter(ImageFilter.GaussianBlur(0.8))
        fr = bg.copy(); fr.alpha_composite(ink)
        fd = ImageDraw.Draw(fr)
        if spec.get("reply"):
            rf = sans(34); rb = sans(44); u = f"Reply to {spec['reply']['user']}'s comment"; tx = spec["reply"]["text"][:40]
            bw = max(fd.textlength(u, font=rf), fd.textlength(tx, font=rb)) + 60
            fd.rounded_rectangle([60, 250, 60 + bw, 380], radius=22, fill=(255, 255, 255, 245))
            fd.text((90, 268), u, font=rf, fill=(120, 120, 120, 255)); fd.text((90, 312), tx, font=rb, fill=(20, 20, 20, 255))
        lt = spec.get("label", "SOULMATE CHECK")
        for i, line in enumerate(lt.split("\n")):
            fd.text((70, 150 + i * 70), line, font=lab, fill=(255, 255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0, 200))
        if t >= spec.get("cta_t", dur - 3):
            c = spec.get("cta", "COMMENT YOUR NUMBER"); w = fd.textlength(c, font=ctaf)
            bx = (W - w) / 2 - 36; by = H - 250
            fd.rounded_rectangle([bx, by, bx + w + 72, by + 120], radius=28, fill=(255, 128, 0, 255))
            fd.text((W / 2, by + 60), c, font=ctaf, fill=(255, 255, 255, 255), anchor="mm")
        fr.convert("RGB").save(f"{out}/f/{k:04d}.jpg", quality=90)
    a = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{out}/f/%04d.jpg"]
    if spec.get("music"):
        a += ["-stream_loop", "-1", "-i", spec["music"], "-filter_complex",
              f"[1:a]volume=0.9,afade=t=out:st={dur - 1.2:.2f}:d=1.1,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "160k"]
    a += ["-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", f"{out}/reel.mp4"]
    subprocess.run(a, check=True)
    print(json.dumps({"ok": True, "seconds": dur}))

if __name__ == "__main__":
    main()
