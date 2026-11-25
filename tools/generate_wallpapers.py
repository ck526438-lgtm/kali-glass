#!/usr/bin/env python3
"""Génère les fonds d'écran « Kali Glass » (effet verre dépoli façon macOS).

Usage : python3 tools/generate_wallpapers.py [dossier_sortie] [largeur] [hauteur]
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "wallpapers"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 3840
H = int(sys.argv[3]) if len(sys.argv) > 3 else 2160

# nom : (fond haut, fond bas, couleurs des halos, clair ?)
PALETTES = {
    "aurora":   ((10, 12, 38), (24, 10, 52), [(66, 99, 255), (170, 70, 255), (0, 210, 255), (255, 80, 190)], False),
    "ocean":    ((4, 22, 40), (2, 40, 58), [(0, 200, 210), (40, 120, 255), (0, 255, 170), (90, 70, 255)], False),
    "sunset":   ((40, 10, 30), (70, 20, 30), [(255, 120, 60), (255, 60, 130), (255, 190, 80), (160, 60, 255)], False),
    "midnight": ((5, 6, 14), (12, 10, 26), [(90, 60, 220), (30, 80, 200), (180, 40, 160), (40, 160, 220)], False),
    "dragon":   ((6, 14, 30), (8, 24, 44), [(36, 125, 255), (0, 230, 255), (80, 60, 255), (0, 140, 200)], False),
    "light":    ((228, 234, 250), (246, 232, 246), [(120, 160, 255), (255, 150, 210), (130, 230, 255), (200, 160, 255)], True),
}


def vertical_gradient(w, h, top, bottom):
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        grad.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return grad.resize((w, h))


def aurora_layer(w, h, colors, rng, light):
    """Halos colorés doux (somme de gaussiennes + tone-mapping, sans saturation)."""
    import numpy as np
    s = 8
    sw, sh = w // s, h // s
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    acc = np.zeros((sh, sw, 3), np.float32)
    for i in range(7):
        c = np.array(colors[i % len(colors)], np.float32) / 255.0
        cx, cy = rng.uniform(-0.1, 1.1) * sw, rng.uniform(-0.1, 1.1) * sh
        rx, ry = rng.uniform(0.16, 0.34) * sw, rng.uniform(0.18, 0.40) * sh
        k = rng.uniform(0.55, 0.95)
        g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)) * k
        acc += g[..., None] * c
    acc = 1.0 - np.exp(-acc * 1.15)          # tone-mapping doux
    acc *= 0.82 if not light else 1.0
    img = Image.fromarray((np.clip(acc, 0, 1) * 255).astype("uint8"), "RGB")
    return img.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(4))


def rounded_mask(size, box, radius):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, radius=radius, fill=255)
    return m


def glass_panel(base, box, radius, light, strength=1.0):
    """Applique un panneau de verre dépoli : flou + voile + reflet + liseré."""
    w, h = base.size
    x0, y0, x1, y1 = [int(v) for v in box]
    pad = 120
    cx0, cy0, cx1, cy1 = max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)
    crop = base.crop((cx0, cy0, cx1, cy1))
    small = crop.resize((max(1, crop.width // 4), max(1, crop.height // 4)))
    blurred = small.filter(ImageFilter.GaussianBlur(28)).resize(crop.size, Image.BICUBIC)
    # voile laiteux
    veil = Image.new("RGB", crop.size, (255, 255, 255))
    blurred = Image.blend(blurred, veil, 0.07 * strength if not light else 0.30 * strength)
    lb = (x0 - cx0, y0 - cy0, x1 - cx0, y1 - cy0)
    mask = rounded_mask(crop.size, lb, radius)

    # ombre portée douce
    shadow = Image.new("L", base.size, 0)
    ImageDraw.Draw(shadow).rounded_rectangle((x0, y0 + 30, x1, y1 + 40), radius=radius, fill=110 if not light else 60)
    shadow = shadow.filter(ImageFilter.GaussianBlur(50))
    base.paste(Image.new("RGB", base.size, (0, 0, 0) if not light else (90, 90, 130)), (0, 0), shadow)

    crop = base.crop((cx0, cy0, cx1, cy1))
    crop.paste(blurred, (0, 0), mask)

    # reflet diagonal en haut à gauche
    shine = Image.new("L", crop.size, 0)
    sd = ImageDraw.Draw(shine)
    bw, bh = lb[2] - lb[0], lb[3] - lb[1]
    for i in range(0, int(bh * 0.55), 2):
        a = int((1 - i / (bh * 0.55)) * (38 if not light else 55) * strength)
        sd.line((lb[0], lb[1] + i, lb[0] + bw, lb[1] + i - bw * 0.25), fill=a, width=2)
    shine = ImageChops.multiply(shine, mask)
    crop.paste(Image.new("RGB", crop.size, (255, 255, 255)), (0, 0), shine)

    # liseré lumineux (bord du verre)
    edge = Image.new("L", crop.size, 0)
    ImageDraw.Draw(edge).rounded_rectangle(lb, radius=radius, outline=120 if not light else 200, width=3)
    edge = edge.filter(ImageFilter.GaussianBlur(0.8))
    crop.paste(Image.new("RGB", crop.size, (255, 255, 255)), (0, 0), edge)
    base.paste(crop, (cx0, cy0))


def noise(w, h, amount, rng):
    n = Image.effect_noise((w // 2, h // 2), 40).resize((w, h)).convert("RGB")
    return n, amount


def make(name, top, bottom, colors, light, seed):
    rng = random.Random(seed)
    img = vertical_gradient(W, H, top, bottom)
    aur = aurora_layer(W, H, colors, rng, light)
    if light:
        img = ImageChops.multiply(img, ImageChops.screen(aur, Image.new("RGB", (W, H), (175, 175, 190))))
        img = ImageChops.screen(img, Image.new("RGB", (W, H), (30, 30, 36)))
    else:
        img = ImageChops.screen(img, aur)

    u = W / 3840
    # composition : grande carte, carte moyenne, petite carte, pastille ronde
    panels = [
        ((0.10 * W, 0.20 * H, 0.52 * W, 0.70 * H), 90 * u, 1.0),
        ((0.46 * W, 0.40 * H, 0.86 * W, 0.84 * H), 90 * u, 0.9),
        ((0.62 * W, 0.12 * H, 0.84 * W, 0.34 * H), 70 * u, 0.8),
    ]
    for box, r, s in panels:
        glass_panel(img, box, r, light, s)
    # bulle ronde
    cx, cy, r = 0.30 * W, 0.80 * H, 0.085 * W
    glass_panel(img, (cx - r, cy - r, cx + r, cy + r), int(r), light, 0.9)

    # léger grain pour éviter le banding
    n = Image.effect_noise((W, H), 18).convert("RGB")
    img = Image.blend(img, ImageChops.overlay(img, n), 0.06)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"kali-glass-{name}.jpg"
    img.save(path, quality=93, subsampling=0, optimize=True)
    print("écrit", path)


if __name__ == "__main__":
    for i, (n, (top, bottom, colors, light)) in enumerate(PALETTES.items()):
        make(n, top, bottom, colors, light, seed=42 + i * 7)
