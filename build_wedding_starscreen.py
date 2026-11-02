#!/usr/bin/env python3
"""Render a wedding star-screen frame (màn sao cưới):
dark starfield + two zodiac constellations in dashed gold lines
+ couple names in the centre. Text is drawn with PIL so Vietnamese
diacritics render exactly (no AI text mangling).
Usage: edit NAMES / DATE below, run, check the PNG visually.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
GOLD = (245, 200, 100)
GOLD_DIM = (200, 160, 80)
WHITE = (255, 255, 255)

SERIF_IT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_BD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# --- couple info (date left empty until supplied) ---
NAMES = "Ngọc Thịnh \u2661 Châu Khanh"   # ♡
INITIALS = "T \u2661 K"
DATE = "28.11.2026"  # supplied 02/11/2026

random.seed(11)

img = Image.new("RGB", (W, H), (2, 2, 10))
d = ImageDraw.Draw(img, "RGBA")

# vertical gradient: near-black top -> deep navy bottom
for y in range(H):
    t = y / H
    r = int(2 + 6 * t)
    g = int(2 + 6 * t)
    b = int(10 + 18 * t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# ---- background stars ----
for _ in range(520):
    x = random.uniform(0, W)
    y = random.uniform(0, H)
    r = random.choice([0.6, 0.9, 1.2, 1.6, 2.0])
    a = random.randint(60, 200)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
# a few bright stars with 4-point sparkle
for _ in range(28):
    x = random.uniform(40, W - 40)
    y = random.uniform(40, H - 40)
    r = random.uniform(1.8, 2.8)
    L = random.uniform(7, 13)
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 235))
    d.line([(x - L, y), (x + L, y)], fill=(255, 255, 255, 120), width=1)
    d.line([(x, y - L), (x, y + L)], fill=(255, 255, 255, 120), width=1)


def dashed_line(p1, p2, dash=16, gap=12, color=GOLD + (230,), width=2):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    n = int(dist // (dash + gap))
    if n == 0:
        d.line([p1, p2], fill=color, width=width)
        return
    for i in range(n + 1):
        t1 = (i * (dash + gap)) / dist
        t2 = min(((i * (dash + gap)) + dash) / dist, 1.0)
        if t1 >= 1:
            break
        d.line([(x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1),
                (x1 + (x2 - x1) * t2, y1 + (y2 - y1) * t2)],
               fill=color, width=width)


def glow_star(x, y, r, core=(255, 240, 200)):
    for rr, a in [(r * 4, 28), (r * 2.6, 55), (r * 1.6, 110)]:
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 215, 130, a))
    d.ellipse([x - r, y - r, x + r, y + r], fill=core + (255,))
    L = r * 3.2
    d.line([(x - L, y), (x + L, y)], fill=(255, 230, 160, 160), width=1)
    d.line([(x, y - L), (x, y + L)], fill=(255, 230, 160, 160), width=1)


def constellation(points, edges, bright_idx):
    for a, b in edges:
        dashed_line(points[a], points[b])
    for i, (x, y) in enumerate(points):
        if i in bright_idx:
            glow_star(x, y, 6)
        else:
            glow_star(x, y, 3.5)


def spaced_text(draw, cx, y, text, font, fill, spacing):
    """Draw letterspaced centred text; returns bottom y."""
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + spacing * (len(text) - 1)
    x = cx - total / 2
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + spacing
    return y + font.size


# ---- Taurus (Kim Ngưu) — upper left: Pleiades + Hyades V + 2 horns ----
# Real stick figure: the V face (Aldebaran at the vertex), one horn each
# side (tips: Elnath / Zeta Tau), Pleiades cluster apart, no dangling legs.
taurus = [
    (200, 155), (225, 145), (215, 180), (240, 170), (195, 190),  # Pleiades
    (170, 300), (235, 370), (300, 440),   # left arm -> Aldebaran
    (360, 380), (420, 320),               # right arm
    (130, 215), (480, 230),               # horn tips
]
taurus_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (4, 6)]
# Pleiades: small cluster, no lines
for (x, y) in taurus[:5]:
    glow_star(x, y, 2.5)
constellation(taurus[5:], taurus_edges, bright_idx={2, 5, 6})

# ---- Capricorn (Ma Kết) — upper right: the classic triangle ----
# Real stick figure: a broad triangle (west alpha/beta pair, east delta,
# south vertex), with one intermediate star on each side.
cap = [
    (1400, 310), (1550, 275), (1700, 250),   # west -> east side
    (1720, 380), (1620, 510),               # east -> south side
    (1480, 420),                            # south -> west side
    (1435, 285),                            # alpha/beta close pair
]
cap_edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
constellation(cap, cap_edges, bright_idx={0, 2})

# ---- shooting stars (fading streaks) ----
def shooting_star(x, y, length, angle_deg):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    a = math.radians(angle_deg)
    dx, dy = math.cos(a), math.sin(a)
    steps = 24
    for i in range(steps):
        t = i / steps
        px = x + dx * length * t
        py = y + dy * length * t
        alpha = int(220 * (1 - t))
        ld.line([(px, py), (px + dx * 8, py + dy * 8)],
                fill=(255, 255, 255, alpha), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"),
              (0, 0))
    return ImageDraw.Draw(img, "RGBA")

d = shooting_star(420, 150, 260, 32)
d = shooting_star(1520, 130, 220, 148)

# ---- centre text with glow ----
glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_layer)

f_inf = ImageFont.truetype(SERIF_IT, 150)
f_init = ImageFont.truetype(SANS, 40)
f_small = ImageFont.truetype(SANS, 38)
f_names = ImageFont.truetype(SERIF_IT, 96)

# infinity symbol
w_inf = gd.textlength("\u221e", font=f_inf)  # ∞
gd.text(((W - w_inf) / 2, 250), "\u221e", font=f_inf, fill=GOLD + (255,))
spaced_text(gd, W // 2, 430, INITIALS, f_init, GOLD + (255,), 10)
spaced_text(gd, W // 2, 520, "THE WEDDING OF", f_small, (255, 240, 200, 255), 12)
w_names = gd.textlength(NAMES, font=f_names)
gd.text(((W - w_names) / 2, 590), NAMES, font=f_names, fill=WHITE + (255,))
if DATE:
    spaced_text(gd, W // 2, 730, DATE, f_small, (255, 240, 200, 255), 6)

glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(6))
img = Image.alpha_composite(img.convert("RGBA"), glow_layer).convert("RGB")
d = ImageDraw.Draw(img, "RGBA")

# sharp text on top
d.text(((W - d.textlength("\u221e", font=f_inf)) / 2, 250), "\u221e",
       font=f_inf, fill=GOLD)
spaced_text(d, W // 2, 430, INITIALS, f_init, GOLD, 10)
spaced_text(d, W // 2, 520, "THE WEDDING OF", f_small, (255, 240, 200), 12)
d.text(((W - d.textlength(NAMES, font=f_names)) / 2, 590), NAMES,
       font=f_names, fill=WHITE)
if DATE:
    spaced_text(d, W // 2, 730, DATE, f_small, (255, 240, 200), 6)

# divider under names
d.line([(W // 2 - 200, 800), (W // 2 + 200, 800)], fill=GOLD + (200,), width=2)

# constellation labels (bottom corners, clear of the names band)
f_label = ImageFont.truetype(SANS_BD, 34)
spaced_text(d, 300, 950, "KIM NGƯU", f_label, GOLD, 8)
spaced_text(d, 1620, 950, "MA KẾT", f_label, GOLD, 8)

out = "/home/hatch/workspace/your_files/man-sao-cuoi-Thinh-Khanh.png"
img.save(out)
print("saved", out, img.size)
