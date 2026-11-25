#!/usr/bin/env python3
"""Génère docs/preview.jpg : aperçu (simulé) du bureau Kali Glass."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

R = Path(__file__).resolve().parent.parent
W, H = 1920, 1080
bg = Image.open(R / "wallpapers" / "kali-glass-aurora.jpg").convert("RGB").resize((W, H), Image.LANCZOS)

def font(size, bold=False):
    for f in (["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] if bold else []) + [
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(f, size)
        except Exception: pass
    return ImageFont.load_default()

def glass(img, box, radius, tint=(255, 255, 255), alpha=0.16, blur=26, border=90):
    x0, y0, x1, y1 = box
    region = img.crop(box).filter(ImageFilter.GaussianBlur(blur))
    region = Image.blend(region, Image.new("RGB", region.size, tint), alpha)
    m = Image.new("L", region.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radius=radius, fill=255)
    img.paste(region, (x0, y0), m)
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, radius=radius, outline=(255, 255, 255, border), width=1)
    img.paste(ov, (0, 0), ov)

def shadow(img, box, radius, strength=140, off=18, blur=34):
    s = Image.new("L", img.size, 0)
    x0, y0, x1, y1 = box
    ImageDraw.Draw(s).rounded_rectangle((x0, y0 + off, x1, y1 + off), radius=radius, fill=strength)
    img.paste(Image.new("RGB", img.size, (0, 0, 0)), (0, 0), s.filter(ImageFilter.GaussianBlur(blur)))

# barre du haut
glass(bg, (0, 0, W, 32), 0, tint=(20, 20, 30), alpha=0.35, blur=20, border=0)
d = ImageDraw.Draw(bg)
f = font(15); fb = font(15, True)
d.text((22, 7), "", font=fb, fill="white")
x = 22
for i, t in enumerate(["Kali", "Fichier", "Édition", "Affichage", "Fenêtre", "Aide"]):
    d.text((x, 7), t, font=fb if i == 0 else f, fill="white"); x += d.textlength(t, font=f) + 26
d.text((W - 290, 7), "FR    100 %    mer. 25 nov.  19:05", font=f, fill="white")

# fenêtre Glass Center
win = Image.open(R / "docs" / "glass-center.png").convert("RGB")
win = win.crop((1, 1, win.width - 1, win.height - 1))
wx, wy = 470, 150
box = (wx, wy, wx + win.width, wy + win.height)
shadow(bg, box, 14)
# verre : on mélange la capture avec le fond flouté pour simuler la transparence
behind = bg.crop(box).filter(ImageFilter.GaussianBlur(30))
win = Image.blend(win, Image.blend(behind, win, 0.55), 0.55)
m = Image.new("L", win.size, 0)
ImageDraw.Draw(m).rounded_rectangle((0, 0, win.width - 1, win.height - 1), radius=14, fill=255)
bg.paste(win, (wx, wy), m)
d = ImageDraw.Draw(bg)
d.rectangle((wx + 6, wy + 8, wx + 130, wy + 44), fill=tuple(int(v) for v in win.getpixel((150, 25))))
for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):  # boutons façon macOS
    cx, cy = wx + 22 + i * 22, wy + 26
    d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=c)
ov = Image.new("RGBA", bg.size, (0, 0, 0, 0))
ImageDraw.Draw(ov).rounded_rectangle(box, radius=14, outline=(255, 255, 255, 70), width=1)
bg.paste(ov, (0, 0), ov)

# terminal translucide
tb = (90, 560, 640, 900)
shadow(bg, tb, 14)
glass(bg, tb, 14, tint=(10, 12, 22), alpha=0.62, blur=30, border=70)
d = ImageDraw.Draw(bg)
for i, c in enumerate([(255, 95, 87), (254, 188, 46), (40, 200, 64)]):
    d.ellipse((tb[0] + 15 + i * 22, tb[1] + 14, tb[0] + 29 + i * 22, tb[1] + 28), fill=c)
d.text((tb[0] + 230, tb[1] + 12), "kali@kali: ~", font=f, fill=(220, 220, 235))
mono = font(15)
lines = [("┌──(kali@kali)-[~]", (90, 160, 255)), ("└─$ kali-glass apply", (235, 235, 245)),
         ("✓ Mode sombre (WhiteSur-Dark)", (110, 230, 140)), ("✓ Fond d'écran : kali-glass-aurora.jpg", (110, 230, 140)),
         ("✓ Flou verre : 7", (110, 230, 140)), ("✓ Dock Plank « KaliGlass » activé", (110, 230, 140)),
         ("", None), ("  Terminé.", (235, 235, 245))]
for i, (t, c) in enumerate(lines):
    if c: d.text((tb[0] + 20, tb[1] + 48 + i * 26), t, font=mono, fill=c)

# dock
icons = [(66, 133, 244), (52, 52, 64), (255, 120, 40), (232, 92, 60), (40, 120, 200), (120, 200, 120), (138, 61, 255), (110, 110, 130)]
n, s, gap = len(icons), 60, 14
dw = n * s + (n + 1) * gap
dx0, dy0 = (W - dw) // 2, H - s - 2 * gap - 10
glass(bg, (dx0, dy0, dx0 + dw, dy0 + s + 2 * gap), 22, alpha=0.18, blur=24, border=110)
d = ImageDraw.Draw(bg)
logo = Image.open("/tmp/icon.png").convert("RGBA").resize((s, s)) if Path("/tmp/icon.png").exists() else None
for i, c in enumerate(icons):
    x = dx0 + gap + i * (s + gap); y = dy0 + gap
    if i == 6 and logo:
        bg.paste(logo, (x, y), logo)
    else:
        top = tuple(min(255, v + 50) for v in c)
        g = Image.new("RGB", (s, s))
        gd = ImageDraw.Draw(g)
        for yy in range(s):
            t = yy / s
            gd.line((0, yy, s, yy), fill=tuple(int(top[k] + (c[k] - top[k]) * t) for k in range(3)))
        mm = Image.new("L", (s, s), 0); ImageDraw.Draw(mm).rounded_rectangle((0, 0, s - 1, s - 1), radius=14, fill=255)
        bg.paste(g, (x, y), mm)
    if i in (0, 1, 6):
        d.ellipse((x + s // 2 - 3, dy0 + s + 2 * gap - 9, x + s // 2 + 3, dy0 + s + 2 * gap - 3), fill=(230, 235, 255))

out = R / "docs" / "preview.jpg"
bg.save(out, quality=90)
print("écrit", out)
