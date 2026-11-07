"""Realistic hand-writing LOVE % reel: a real-looking hand with a marker writes two names letter by letter, crosses out each
letter as it counts it, writes the counts, crosses out digit pairs while adding them, writes the final % and draws a heart.
Phone-camera feel: handheld shake, slow zoom, grain, vignette, hand shadow. Original visuals (own hand/paper assets).

usage (Higgsfield sandbox):
  python3 hand_reel.py --names Daniel Julia paper.png hand.png music.mp3 outdir ["@user|real comment text"]
needs Caveat.ttf + love_rows() logic (same method as check_reel.py). Hand PNG must have alpha; HAND_TIP = pen tip pixel in hand.png.
"""
import json, math, os, random, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
HAND_TIP = (110, 283)      # in the 752x1344 hand cutout (job 900b18b5)
HAND_SCALE = 1.22
INK = (196, 18, 40)

def font(size):
    f = ImageFont.truetype(os.path.join(HERE, "Caveat.ttf"), size)
    try: f.set_variation_by_axes([700])
    except Exception: pass
    return f

def sans(size):
    import glob
    g = sorted(glob.glob("/usr/share/fonts/**/Montserrat*Bold*.ttf", recursive=True))
    return ImageFont.truetype(g[0], size)

def love_rows(a, b):
    s = [c for c in (a + b).lower() if c.isalpha()]; seen = []
    for c in s:
        if c not in seen: seen.append(c)
    ds = [s.count(c) for c in seen]; rows = [ds]
    for _ in range(8):
        if len(ds) <= 2: break
        new, i, j = [], 0, len(ds) - 1
        while i < j:
            new += [int(c) for c in str(ds[i] + ds[j])]; i += 1; j -= 1
        if i == j: new.append(ds[i])
        ds = new; rows.append(ds)
    return seen, rows, int("".join(map(str, ds[:2])))

class Row:
    """A line of hand-written characters with natural jitter; knows where each char sits."""
    def __init__(self, text, y, size, rng, cx=540):
        self.f = font(size); self.text = text; self.size = size
        widths = [self.f.getlength(c) for c in text]; total = sum(widths) * 1.04
        x = cx - total / 2; self.chars = []
        for c, w in zip(text, widths):
            g = Image.new("RGBA", (int(w) + 60, size + 60), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((30, 15), c, font=self.f, fill=INK + (int(rng.uniform(225, 255)),))
            g = g.rotate(rng.uniform(-5, 5), resample=Image.BICUBIC)
            sc = rng.uniform(0.95, 1.06); g = g.resize((int(g.width * sc), int(g.height * sc)), Image.BICUBIC)
            yy = y + rng.uniform(-5, 5)
            self.chars.append({"c": c, "img": g, "x": int(x - 30), "y": int(yy - 15), "x0": x, "x1": x + w * 1.04,
                               "ymid": yy + size * 0.55, "ytop": yy + size * 0.30, "ybot": yy + size * 0.80})
            x += w * 1.04

def build_events(a, b, rng):
    seen, rows, pct = love_rows(a, b)
    ev = []; y = 300; R = []
    n1 = Row(a.capitalize(), y, 170, rng); y += 175
    plus = Row("+", y, 120, rng); y += 135
    n2 = Row(b.capitalize(), y, 170, rng); y += 200
    rowsz = 150 if max(len(r) for r in rows) <= 9 else 130
    drows = []
    for r in rows[:-1] if len(rows) > 1 and len(rows[-1]) <= 2 else rows:
        drows.append(Row("".join(map(str, r)), y, rowsz, rng)); y += rowsz * 0.95
    final = Row(f"{pct}%", y + 10, 200, rng)
    def write(row):
        for ch in row.chars:
            if ch["c"] == " ": continue
            ev.append({"k": "glyph", "ch": ch, "d": rng.uniform(0.11, 0.2) * (ch["x1"] - ch["x0"]) / 45 + 0.05})
    def strike(ch):
        ev.append({"k": "line", "p0": (ch["x0"] - 4, ch["ybot"] + 4), "p1": (ch["x1"] + 6, ch["ytop"] - 6), "d": 0.12})
    write(n1); write(plus); write(n2)
    letters = [ch for ch in n1.chars + n2.chars if ch["c"].isalpha()]
    first = drows[0]; di = 0
    for c in seen:  # count: cross out every copy of this letter, then write its count
        for ch in letters:
            if ch["c"].lower() == c: strike(ch)
        ev.append({"k": "glyph", "ch": first.chars[di], "d": 0.18}); di += 1
    for ri in range(1, len(drows) + 1):  # add outer digits inward: cross both, write the sum
        prev = drows[ri - 1].chars; tgt = drows[ri].chars if ri < len(drows) else final.chars
        i, j, wi = 0, len(prev) - 1, 0
        while i <= j and wi < len(tgt):
            strike(prev[i])
            if i != j: strike(prev[j])
            s = str(int(prev[i]["c"]) + int(prev[j]["c"])) if i != j else prev[i]["c"]
            for _ in s:
                if wi < len(tgt) and tgt[wi]["c"].isdigit():
                    ev.append({"k": "glyph", "ch": tgt[wi], "d": 0.2}); wi += 1
            i += 1; j -= 1
    for ch in final.chars:
        if not ch["c"].isdigit(): ev.append({"k": "glyph", "ch": ch, "d": 0.25})
    fx0, fx1 = final.chars[0]["x0"], final.chars[-1]["x1"]; fy = final.chars[0]["ymid"]
    ev.append({"k": "heart", "c": ((fx0 + fx1) / 2, fy - 10), "s": (fx1 - fx0) / 22, "d": 1.3})
    return ev, pct

def tip_at(e, p):
    if e["k"] == "glyph":
        ch = e["ch"]; return (ch["x0"] + (ch["x1"] - ch["x0"]) * p, ch["ymid"] + 14 * math.sin(p * math.pi * 3))
    if e["k"] == "line":
        (x0, y0), (x1, y1) = e["p0"], e["p1"]; return (x0 + (x1 - x0) * p, y0 + (y1 - y0) * p)
    a = math.pi + 2 * math.pi * p * 0.999  # heart starting at the bottom tip
    cx, cy = e["c"]; s = e["s"]
    return (cx + s * 16 * math.sin(a) ** 3, cy - s * (13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)))

def main():
    a, b, paper_p, hand_p, music, out = sys.argv[2:8]
    reply = None
    if len(sys.argv) > 8 and "|" in sys.argv[8]:
        u, tx = sys.argv[8].split("|", 1); reply = (u, tx)
    rng = random.Random(hash((a, b)) & 0xffff)
    ev, pct = build_events(a, b, rng)
    # timeline with pen-up travel between events
    t = 1.2; tl = []; last = (1350, 2300)
    for e in ev:
        st = tip_at(e, 0); dist = math.dist(last, st)
        travel = 0.06 + dist / 2600 + (0.05 if e["k"] == "line" else 0)
        tl.append({"k": "travel", "from": last, "to": st, "t0": t, "t1": t + travel}); t += travel
        e["t0"], e["t1"] = t, t + e["d"]; tl.append(e); t += e["d"]; last = tip_at(e, 1)
    t_end_write = t
    tl.append({"k": "travel", "from": last, "to": (1350, 2300), "t0": t + 0.3, "t1": t + 1.3})
    dur = t + 3.8
    os.makedirs(f"{out}/f", exist_ok=True)
    paper = Image.open(paper_p).convert("RGB")
    s = max(W * 1.08 / paper.width, H * 1.08 / paper.height); paper = paper.resize((int(paper.width * s), int(paper.height * s)), Image.LANCZOS)
    paper = paper.crop(((paper.width - int(W * 1.08)) // 2, (paper.height - int(H * 1.08)) // 2, (paper.width - int(W * 1.08)) // 2 + int(W * 1.08), (paper.height - int(H * 1.08)) // 2 + int(H * 1.08)))
    paper = Image.eval(paper, lambda v: min(255, int(v * 1.1 + 8))).convert("RGBA")
    PW, PH = paper.size; off = ((PW - W) // 2, (PH - H) // 2)
    hand = Image.open(hand_p).convert("RGBA"); hand = hand.resize((int(hand.width * HAND_SCALE), int(hand.height * HAND_SCALE)), Image.LANCZOS)
    tip = (HAND_TIP[0] * HAND_SCALE, HAND_TIP[1] * HAND_SCALE)
    sh_a = hand.split()[3].filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.33))
    shadow = Image.new("RGBA", hand.size, (40, 30, 25, 0)); shadow.putalpha(sh_a)
    ink = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))   # committed ink (paper coords)
    noise = [Image.effect_noise((W // 2, H // 2), 22).resize((W, H)).convert("L") for _ in range(6)]
    vg = Image.radial_gradient("L").resize((W, H)).point(lambda v: 255 - int(max(0, v - 90) * 0.5))
    vmul = Image.merge("RGB", (vg, vg, vg))
    done = set(); bubble_f = sans(34); bubble_b = sans(44); end_f = sans(64)
    events = [e for e in tl if e["k"] != "travel"]
    for k in range(int(dur * FPS)):
        tt = k / FPS
        partial = None; tipxy = None; pen_up = 0
        for e in tl:
            if e["t0"] <= tt < e["t1"]:
                p = (tt - e["t0"]) / (e["t1"] - e["t0"])
                if e["k"] == "travel":
                    pe = p * p * (3 - 2 * p); tipxy = (e["from"][0] + (e["to"][0] - e["from"][0]) * pe, e["from"][1] + (e["to"][1] - e["from"][1]) * pe)
                    pen_up = math.sin(p * math.pi) * 22
                else:
                    tipxy = tip_at(e, p); partial = (e, p)
                break
        for e in events:  # commit finished strokes
            if id(e) in done or tt < e["t1"]: continue
            done.add(id(e)); d = ImageDraw.Draw(ink)
            if e["k"] == "glyph":
                ch = e["ch"]; ink.alpha_composite(ch["img"], (ch["x"] + off[0], ch["y"] + off[1]))
            elif e["k"] == "line":
                d.line([(e["p0"][0] + off[0], e["p0"][1] + off[1]), (e["p1"][0] + off[0], e["p1"][1] + off[1])], fill=INK + (235,), width=7)
            else:
                pts = [tip_at(e, q / 120) for q in range(121)]; d.line([(x + off[0], y + off[1]) for x, y in pts], fill=INK + (240,), width=9, joint="curve")
        fr = paper.copy(); fr.alpha_composite(ink)
        if partial:
            e, p = partial; d = ImageDraw.Draw(fr)
            if e["k"] == "glyph":
                ch = e["ch"]; g = ch["img"]; cw = max(1, int(g.width * min(1, 0.15 + p * 0.85)))
                fr.alpha_composite(g.crop((0, 0, cw, g.height)), (ch["x"] + off[0], ch["y"] + off[1]))
            elif e["k"] == "line":
                x1, y1 = tip_at(e, p); d.line([(e["p0"][0] + off[0], e["p0"][1] + off[1]), (x1 + off[0], y1 + off[1])], fill=INK + (235,), width=7)
            else:
                pts = [tip_at(e, q / 120 * p) for q in range(121)]; d.line([(x + off[0], y + off[1]) for x, y in pts], fill=INK + (240,), width=9, joint="curve")
        if tipxy is None: tipxy = (1350, 2300)
        jx = 2 * math.sin(tt * 37) + 1.5 * math.sin(tt * 23); jy = 2 * math.cos(tt * 31)
        hx = int(tipxy[0] + off[0] - tip[0] + jx + pen_up * 0.6); hy = int(tipxy[1] + off[1] - tip[1] + jy - pen_up)
        fr.alpha_composite(shadow, (hx + 28, hy + 34)); fr.alpha_composite(hand, (hx, hy))
        # handheld camera: smooth drift + tiny rotation + slow zoom
        z = 1.0 + 0.025 * tt / dur; ang = 0.35 * math.sin(tt * 0.9) + 0.15 * math.sin(tt * 2.3)
        cx = PW / 2 + 6 * math.sin(tt * 0.7) + 3 * math.sin(tt * 1.9); cy = PH / 2 + 6 * math.cos(tt * 0.6) + 3 * math.sin(tt * 2.1)
        fr = fr.rotate(ang, resample=Image.BILINEAR, center=(cx, cy))
        cw, chh = W / z, H / z
        fr = fr.crop((int(cx - cw / 2), int(cy - chh / 2), int(cx + cw / 2), int(cy + chh / 2))).resize((W, H), Image.BILINEAR).convert("RGB")
        fr = ImageChops.multiply(fr, vmul)
        nz = noise[k % 6]; fr = ImageChops.add(fr, Image.merge("RGB", (nz, nz, nz)).point(lambda v: v // 12), 1.0, -8)
        dd = ImageDraw.Draw(fr)
        if reply:
            u = f"Reply to {reply[0]}'s comment"; tx = reply[1][:40]
            bw = max(dd.textlength(u, font=bubble_f), dd.textlength(tx, font=bubble_b)) + 60
            dd.rounded_rectangle([60, 140, 60 + bw, 270], radius=22, fill=(255, 255, 255))
            dd.text((90, 158), u, font=bubble_f, fill=(120, 120, 120)); dd.text((90, 202), tx, font=bubble_b, fill=(20, 20, 20))
        if tt > t_end_write + 1.0:
            m = "comment your names"; dd.text((W / 2, H - 260), m, font=end_f, fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
        fr.save(f"{out}/f/{k:04d}.jpg", quality=88)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{out}/f/%04d.jpg"]
    if music and music != "-":
        cmd += ["-stream_loop", "-1", "-i", music, "-filter_complex", f"[1:a]volume=0.9,afade=t=out:st={dur - 1.2:.2f}:d=1.1,loudnorm=I=-14:TP=-1.5[a]",
                "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "160k"]
    cmd += ["-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", f"{out}/reel.mp4"]
    subprocess.run(cmd, check=True)
    print(json.dumps({"ok": True, "pct": pct, "seconds": round(dur, 1)}))

if __name__ == "__main__":
    main()
