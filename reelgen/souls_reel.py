"""Twin-souls reel: two glowing constellation silhouettes (warm + cool) facing each other on a starfield,
connected by drifting network lines, with big word-by-word captions and a CTA. Original art, drawn in code.

spec: {"title": str, "lines": ["SOULS", "*recognize* each other", ...], "cta": str, "music": "dreamy", "seed": int}
usage: python3 reelgen/souls_reel.py spec.json out_base [--frames t1,t2]
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
sys.path.insert(0, os.path.dirname(__file__))
from split_reel import W, H, FPS, FONT_B, FONT_M, text_block, boxed, paste_pop
from reveal_reel import caption, nebula

GOLD = (255, 214, 102, 255)
# Head-and-shoulders profile facing RIGHT (x,y in a 0..1 box), traced clockwise from top of head.
PROFILE = [(0.30, 0.02), (0.52, 0.00), (0.68, 0.06), (0.76, 0.17), (0.79, 0.27), (0.80, 0.32), (0.88, 0.40),
           (0.83, 0.43), (0.84, 0.47), (0.81, 0.50), (0.83, 0.54), (0.79, 0.58), (0.77, 0.65), (0.66, 0.70),
           (0.62, 0.78), (0.66, 0.86), (0.98, 0.95), (1.00, 1.00), (0.00, 1.00), (0.04, 0.88), (0.16, 0.80),
           (0.14, 0.62), (0.06, 0.44), (0.07, 0.24), (0.15, 0.08)]

def silhouette_mask(box_w, box_h, flip):
    pts = [((1 - x if flip else x) * box_w, y * box_h) for x, y in PROFILE]
    m = Image.new("L", (box_w, box_h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return m, pts

def soul_layer(box_w, box_h, flip, color, rng):
    mask, outline = silhouette_mask(box_w, box_h, flip)
    a = np.asarray(mask) > 0
    ys, xs = np.nonzero(a)
    idx = rng.choice(len(xs), 260, replace=False)
    pts = np.stack([xs[idx], ys[idx]], 1).astype(float)
    # add outline points for a crisp edge
    ol = []
    for (x1, y1), (x2, y2) in zip(outline, outline[1:] + outline[:1]):
        for k in np.linspace(0, 1, 7, endpoint=False):
            ol.append((x1 + (x2 - x1) * k, y1 + (y2 - y1) * k))
    pts = np.concatenate([pts, np.array(ol)])
    lay = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    # fill glow
    fill = Image.new("RGBA", (box_w, box_h), color + (0,))
    fill.putalpha(mask.point(lambda v: 38 if v else 0))
    lay.alpha_composite(fill)
    # network lines
    for i in range(len(pts)):
        dd = np.hypot(*(pts - pts[i]).T)
        for j in np.argsort(dd)[1:4]:
            if dd[j] < box_w * 0.11:
                d.line([tuple(pts[i]), tuple(pts[j])], fill=color + (int(150 - dd[j] / (box_w * 0.11) * 110),), width=2)
    for x, y in ol:
        pass
    d.line([tuple(p) for p in outline] + [outline[0]], fill=color + (235,), width=4)
    for x, y in pts:
        r = rng.choice([2, 2.5, 3.5])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 250, 240, 230))
    glow = lay.filter(ImageFilter.GaussianBlur(16))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(glow); out.alpha_composite(lay)
    fade = Image.linear_gradient("L").rotate(180).resize((box_w, box_h))  # 255 at top -> 0 at bottom
    fade = fade.point(lambda v: min(255, int(v * 2.2)))
    out.putalpha(ImageChops.multiply(out.getchannel("A"), fade))
    return out

def build(spec):
    rng = np.random.default_rng(spec.get("seed", 9))
    bw, bh = 560, 900
    L = {"neb": nebula(spec.get("seed", 9) + 100),
         "left": soul_layer(bw, bh, False, (255, 150, 60), rng),
         "right": soul_layer(bw, bh, True, (70, 210, 255), rng),
         "title": text_block(spec["title"], 76, GOLD, 900),
         "caps": [caption(l, 78) for l in spec["lines"]],
         "cta": boxed(text_block(spec["cta"], 52, (20, 16, 40, 255), 820, gap=0.08), 40, 24, GOLD, 26),
         "sparks": [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, 6.28)) for _ in range(60)]}
    L["t_lines"] = 1.2; L["step"] = 2.2
    L["t_cta"] = L["t_lines"] + L["step"] * len(L["caps"]) + 0.4
    L["end"] = L["t_cta"] + 3.0
    return L

def frame_at(t, L):
    z = 1.0 + 0.08 * (t / L["end"]); neb = L["neb"]
    cw, ch = int(W * 1.25 / z), int(H * 1.25 / z)
    x0, y0 = (neb.width - cw) // 2, (neb.height - ch) // 2
    f = neb.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    f = Image.blend(f, Image.new("RGBA", (W, H), (6, 4, 18, 255)), 0.45)
    approach = min(1.0, t / 3.0)
    gap = int(150 * (1 - approach))
    breathe = math.sin(t * 1.6) * 6
    lw = L["left"]; rw = L["right"]
    f.alpha_composite(lw, (int(W / 2 - lw.width + 60 - gap), int(480 + breathe)))
    f.alpha_composite(rw, (int(W / 2 - 60 + gap), int(480 - breathe)))
    d = ImageDraw.Draw(f)
    for x, y, ph in L["sparks"]:
        a = int(120 + 120 * math.sin(t * 2.5 + ph))
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 240, 255, max(20, a)))
    paste_pop(f, L["title"], W / 2, 300, 0.2, t)
    n = len(L["caps"])
    if t < L["t_cta"]:
        i = int((t - L["t_lines"]) / L["step"]) if t >= L["t_lines"] else -1
        if 0 <= i < n:
            paste_pop(f, L["caps"][i], W / 2, 1520, L["t_lines"] + i * L["step"], t, .35)
    else:
        paste_pop(f, L["cta"], W / 2, 1560, L["t_cta"], t, .45)
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
    add_to_video(base + ".mp4", spec.get("music", "dreamy"), spec.get("seed", 1))
    print("ok", base + ".mp4", f"{L['end']:.1f}s")

if __name__ == "__main__":
    main()
