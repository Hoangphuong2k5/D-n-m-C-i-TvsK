#!/usr/bin/env python3
"""Animate the wedding star-screen into a 12s MP4 (24fps, 1920x1080):
- starfield with twinkling bright stars
- two constellations draw themselves in over the first 5s, then glow-pulse
- shooting stars at t=6.5s and t=9.5s
- centre text (infinity, initials, THE WEDDING OF, names, date) fades in
  from t=5s, fully visible by t=7s
Text is PIL-rendered, so Vietnamese diacritics stay exact.
"""
import math
import os
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
FPS, DUR = 24, 12
NFRAMES = FPS * DUR
FRAMES_DIR = "/tmp/wedding-video/frames"
OUT = "/home/hatch/workspace/your_files/man-sao-cuoi-Thinh-Khanh.mp4"

GOLD = (245, 200, 100)
WHITE = (255, 255, 255)
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

NAMES = "Ngọc Thịnh \u2661 Châu Khanh"
INITIALS = "T \u2661 K"
DATE = "28.11.2026"

random.seed(11)
os.makedirs(FRAMES_DIR, exist_ok=True)

# ---------- static base: gradient + dim stars ----------
base = Image.new("RGB", (W, H), (2, 2, 10))
bd = ImageDraw.Draw(base, "RGBA")
for y in range(H):
    t = y / H
    bd.line([(0, y), (W, y)], fill=(int(2 + 6 * t), int(2 + 6 * t), int(10 + 18 * t)))
for _ in range(420):
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    r = random.choice([0.6, 0.9, 1.2, 1.6])
    bd.ellipse([x - r, y - r, x + r, y + r],
               fill=(255, 255, 255, random.randint(50, 150)))

# twinkling bright stars: (x, y, base_r, phase, freq in cycles per 12s)
twinkles = []
for _ in range(46):
    twinkles.append((random.uniform(40, W - 40), random.uniform(40, H - 40),
                     random.uniform(1.8, 2.8), random.uniform(0, 2 * math.pi),
                     random.choice([6, 8, 10, 12])))


def dashed_line(d, p1, p2, dash=16, gap=12, color=GOLD + (230,), width=2):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    n = int(dist // (dash + gap))
    for i in range(n + 1):
        t1 = (i * (dash + gap)) / dist
        t2 = min(((i * (dash + gap)) + dash) / dist, 1.0)
        if t1 >= 1:
            break
        d.line([(x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1),
                (x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2)],
               fill=color, width=width)


def glow_star(d, x, y, r):
    for rr, a in [(r * 4, 28), (r * 2.6, 55), (r * 1.6, 110)]:
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 215, 130, a))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 240, 200, 255))
    L = r * 3.2
    d.line([(x - L, y), (x + L, y)], fill=(255, 230, 160, 160), width=1)
    d.line([(x, y - L), (x, y + L)], fill=(255, 230, 160, 160), width=1)


def draw_partial(d, points, edges, bright, reveal, t, pulse):
    """Reveal edges in order over reveal=1; stars pop when their edge starts."""
    n = len(edges)
    for i, (a, b) in enumerate(edges):
        start = i / n
        if reveal <= start:
            continue
        frac = min((reveal - start) * n, 1.0)
        p1, p2 = points[a], points[b]
        px = (p1[0] + (p2[0] - p1[0]) * frac, p1[1] + (p2[1] - p1[1]) * frac)
        dashed_line(d, p1, px)
        # start-point star pops in when its edge starts
        if a in bright:
            glow_star(d, p1[0], p1[1], 6 * pulse)
        else:
            glow_star(d, p1[0], p1[1], 3.5 * pulse)
        if frac >= 1.0:
            if b in bright:
                glow_star(d, p2[0], p2[1], 6 * pulse)
            else:
                glow_star(d, p2[0], p2[1], 3.5 * pulse)


# ---------- constellations (same layout as the still frame) ----------
taurus_pts = [(120, 260), (210, 360), (300, 440), (470, 230), (390, 360),
              (400, 520), (490, 560), (230, 520)]
taurus_edges = [(0, 1), (1, 2), (3, 4), (4, 2), (2, 5), (5, 6), (2, 7)]
taurus_bright = {2, 0, 3, 6}
for (x, y) in [(150, 180), (180, 165), (165, 200), (195, 190)]:
    pass  # Pleiades drawn per-frame with twinkle instead
pleiades = [(150, 180), (180, 165), (165, 200), (195, 190)]

cap_pts = [(1400, 300), (1520, 240), (1680, 230), (1800, 300),
           (1760, 450), (1640, 540), (1500, 520), (1420, 420)]
cap_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0)]
cap_bright = {1, 2, 3}


def spaced_text(draw, cx, y, text, font, fill, spacing):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing


# ---------- pre-rendered centre text layer (with glow) ----------
text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(text_layer)
f_inf = ImageFont.truetype(SERIF, 150)
f_init = ImageFont.truetype(SANS, 40)
f_small = ImageFont.truetype(SANS, 38)
f_names = ImageFont.truetype(SERIF, 96)
f_label = ImageFont.truetype(SANS_BD, 34)
gd.text(((W - gd.textlength("\u221e", font=f_inf)) / 2, 250), "\u221e",
        font=f_inf, fill=GOLD + (255,))
spaced_text(gd, W // 2, 430, INITIALS, f_init, GOLD + (255,), 10)
spaced_text(gd, W // 2, 520, "THE WEDDING OF", f_small, (255, 240, 200, 255), 12)
gd.text(((W - gd.textlength(NAMES, font=f_names)) / 2, 590), NAMES,
        font=f_names, fill=WHITE + (255,))
spaced_text(gd, W // 2, 730, DATE, f_small, (255, 240, 200, 255), 6)
gd.line([(W // 2 - 200, 800), (W // 2 + 200, 800)], fill=GOLD + (200,), width=2)
spaced_text(gd, 300, 950, "KIM NGƯU", f_label, GOLD + (255,), 8)
spaced_text(gd, 1620, 950, "MA KẾT", f_label, GOLD + (255,), 8)
text_layer = text_layer.filter(ImageFilter.GaussianBlur(2))


def fade(t, t0, t1):
    if t <= t0:
        return 0.0
    if t >= t1:
        return 1.0
    return (t - t0) / (t1 - t0)


def shooting_streak(d, x0, y0, angle_deg, length, t, t0, dur):
    """A streak head travelling along a diagonal, tail fading behind it."""
    if t < t0 or t > t0 + dur:
        return
    p = (t - t0) / dur
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    hx = x0 + dx * length * p
    hy = y0 + dy * length * p
    for i in range(20):
        tt = i / 20
        px = hx - dx * length * 0.35 * tt
        py = hy - dy * length * 0.35 * tt
        alpha = int(230 * (1 - tt))
        d.line([(px, py), (px + dx * 8, py + dy * 8)],
               fill=(255, 255, 255, alpha), width=2)


for fi in range(NFRAMES):
    t = fi / FPS
    frame = base.copy()
    d = ImageDraw.Draw(frame, "RGBA")

    # fade-in from black over the first 0.8s
    fin = fade(t, 0, 0.8)

    # twinkling bright stars (integer cycles over 12s -> loop-friendly)
    for (x, y, r, ph, cyc) in twinkles:
        a = 0.55 + 0.45 * math.sin(2 * math.pi * cyc * t / DUR + ph)
        rr = r * (0.8 + 0.4 * a)
        d.ellipse([x - rr, y - rr, x + rr, y + rr],
                  fill=(255, 255, 255, int(120 + 130 * a)))
        L = rr * 3
        d.line([(x - L, y), (x + L, y)], fill=(255, 255, 255, int(90 * a)), width=1)
        d.line([(x, y - L), (x, y + L)], fill=(255, 255, 255, int(90 * a)), width=1)
    for (x, y) in pleiades:
        glow_star(d, x, y, 2.5)

    # constellations draw in over the first 5s, then glow-pulse
    reveal = fade(t, 0.8, 5.8)
    pulse = 1.0 + (0.15 * math.sin(2 * math.pi * 0.8 * t) if t > 5.8 else 0)
    draw_partial(d, taurus_pts, taurus_edges, taurus_bright, reveal, t, pulse)
    draw_partial(d, cap_pts, cap_edges, cap_bright, reveal, t, pulse)

    # shooting stars
    shooting_streak(d, 420, 150, 32, 260, t, 6.5, 1.4)
    shooting_streak(d, 1520, 130, 148, 220, t, 9.5, 1.4)

    # centre text fades in 5s -> 7s
    ta = fade(t, 5.0, 7.0) * fin
    if ta > 0:
        layer = text_layer.copy()
        alpha = layer.split()[3].point(lambda v: int(v * ta))
        layer.putalpha(alpha)
        frame = Image.alpha_composite(frame.convert("RGBA"), layer).convert("RGB")
    elif fin < 1:
        # before text appears, still apply the opening fade
        frame = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), frame, fin)

    frame.save(os.path.join(FRAMES_DIR, "frame_%04d.png" % fi))
    if fi % 48 == 0:
        print("frame", fi, "/", NFRAMES)

print("frames done")
cmd = ["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
       "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("libx264 failed, trying mpeg4:", r.stderr[-500:])
    cmd[cmd.index("libx264")] = "mpeg4"
    r = subprocess.run(cmd, capture_output=True, text=True)
print("ffmpeg rc:", r.returncode)
if os.path.exists(OUT):
    print("saved", OUT, os.path.getsize(OUT), "bytes")
