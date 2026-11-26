#!/usr/bin/env python3
"""Génère les fonds d'écran ANIMÉS « Kali Glass Live » : boucles vidéo parfaites (sans saut)
de halos lumineux qui dérivent derrière des panneaux de verre dépoli.

Usage :
  python3 tools/generate_live.py [--out DOSSIER] [--size 3840x2160] [--fps 30]
                                 [--seconds 20] [--only aurora,ocean] [--crf 20]

Sortie : kali-glass-live-<nom>-<hauteur>p.mp4 (H.264, yuv420p, +faststart)
Nécessite numpy, Pillow et ffmpeg.
"""
import argparse
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# nom : (fond haut, fond bas, couleurs des halos)
PALETTES = {
    "aurora": ((10, 12, 38), (24, 10, 52), [(66, 99, 255), (170, 70, 255), (0, 210, 255), (255, 80, 190)]),
    "ocean": ((4, 22, 40), (2, 40, 58), [(0, 200, 210), (40, 120, 255), (0, 255, 170), (90, 70, 255)]),
    "sunset": ((40, 10, 30), (70, 20, 30), [(255, 120, 60), (255, 60, 130), (255, 190, 80), (160, 60, 255)]),
    "midnight": ((5, 6, 14), (12, 10, 26), [(90, 60, 220), (30, 80, 200), (180, 40, 160), (40, 160, 220)]),
}


class Scene:
    def __init__(self, name, W, H, seed):
        self.W, self.H = W, H
        top, bottom, colors = PALETTES[name]
        rng = np.random.default_rng(seed)
        # fond en dégradé vertical
        t = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        self.base = ((np.array(top) + (np.array(bottom) - np.array(top)) * t) / 255.0).astype(np.float32)
        self.base = np.broadcast_to(self.base, (H, W, 3))

        # halos : chaque centre parcourt une ellipse avec une fréquence ENTIÈRE → boucle parfaite
        self.s = 8
        self.sw, self.sh = W // self.s, H // self.s
        self.blobs = []
        for i in range(7):
            self.blobs.append(dict(
                c=np.array(colors[i % len(colors)], np.float32) / 255.0,
                cx=rng.uniform(0.0, 1.0), cy=rng.uniform(0.0, 1.0),
                ax=rng.uniform(0.10, 0.28), ay=rng.uniform(0.08, 0.22),
                fx=int(rng.integers(1, 3)), fy=int(rng.integers(1, 3)),
                ph=rng.uniform(0, 2 * math.pi), ph2=rng.uniform(0, 2 * math.pi),
                rx=rng.uniform(0.16, 0.32), ry=rng.uniform(0.18, 0.38),
                k=rng.uniform(0.55, 0.95), pulse=rng.uniform(0.0, 0.25),
            ))
        yy, xx = np.mgrid[0:self.sh, 0:self.sw].astype(np.float32)
        self.xx, self.yy = xx / self.sw, yy / self.sh

        # panneaux de verre (statiques), en coordonnées 0..1
        u = W / 3840
        panels = [((0.10, 0.20, 0.52, 0.70), 90 * u), ((0.46, 0.40, 0.86, 0.84), 90 * u),
                  ((0.62, 0.12, 0.84, 0.34), 70 * u)]
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        shadow = Image.new("L", (W, H), 0)
        sd = ImageDraw.Draw(shadow)
        edge = Image.new("L", (W, H), 0)
        ed = ImageDraw.Draw(edge)
        boxes = [(tuple(v * (W if i % 2 == 0 else H) for i, v in enumerate(b)), r) for b, r in panels]
        cx, cy, rr = 0.30 * W, 0.80 * H, 0.085 * W
        boxes.append(((cx - rr, cy - rr, cx + rr, cy + rr), rr))
        for (x0, y0, x1, y1), r in boxes:
            md.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255)
            sd.rounded_rectangle((x0, y0 + 30 * u, x1, y1 + 40 * u), radius=r, fill=110)
            ed.rounded_rectangle((x0, y0, x1, y1), radius=r, outline=120, width=max(2, int(3 * u)))
        self.mask = (np.asarray(mask.filter(ImageFilter.GaussianBlur(1)), np.float32) / 255.0)[..., None]
        self.shadow = (np.asarray(shadow.filter(ImageFilter.GaussianBlur(50 * u)), np.float32) / 255.0)[..., None]
        self.edge = (np.asarray(edge.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255.0)[..., None]

        # reflet statique en haut des panneaux
        gy = np.linspace(1, 0, H, dtype=np.float32)[:, None, None]
        self.static_shine = self.mask * (gy ** 3) * 0.10

        # coordonnée diagonale pour le balayage lumineux
        X = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        Y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        self.diag = (X * 0.75 + Y * 0.25)[..., None]
        self.noise = np.random.default_rng(seed + 1).normal(0, 1.2 / 255, (H, W, 1)).astype(np.float32)

    def aurora(self, phase):
        acc = np.zeros((self.sh, self.sw, 3), np.float32)
        for b in self.blobs:
            px = b["cx"] + b["ax"] * math.cos(b["fx"] * phase + b["ph"])
            py = b["cy"] + b["ay"] * math.sin(b["fy"] * phase + b["ph2"])
            k = b["k"] * (1 + b["pulse"] * math.sin(phase + b["ph"]))
            g = np.exp(-(((self.xx - px) / b["rx"]) ** 2 + ((self.yy - py) / b["ry"]) ** 2)) * k
            acc += g[..., None] * b["c"]
        acc = (1.0 - np.exp(-acc * 1.15)) * 0.82
        return np.clip(acc, 0, 1)

    def frame(self, phase):
        W, H = self.W, self.H
        small = Image.fromarray((self.aurora(phase) * 255).astype(np.uint8), "RGB")
        aur = np.asarray(small.resize((W, H), Image.BICUBIC), np.float32) / 255.0
        frosted_small = small.filter(ImageFilter.GaussianBlur(max(2, self.sw / 60)))
        frosted = np.asarray(frosted_small.resize((W, H), Image.BICUBIC), np.float32) / 255.0

        bg = 1 - (1 - self.base) * (1 - aur)                      # screen
        bg = bg * (1 - self.shadow * 0.45)                        # ombre portée
        glass = 1 - (1 - self.base) * (1 - frosted)
        glass = glass * 0.93 + 0.07                               # voile laiteux
        out = bg * (1 - self.mask) + glass * self.mask

        # balayage de lumière qui traverse le verre (une fois par boucle)
        pos = (phase / (2 * math.pi)) * 1.6 - 0.3
        sweep = np.exp(-((self.diag - pos) / 0.06) ** 2) * self.mask * 0.10
        out = out + self.static_shine + sweep + self.edge * 0.45 + self.noise
        return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def render(name, out_dir, W, H, fps, seconds, crf, preset, seed):
    out = out_dir / f"kali-glass-live-{name}-{H}p.mp4"
    n = fps * seconds
    scene = Scene(name, W, H, seed)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-tune", "film", "-g", str(fps * 2), "-movflags", "+faststart",
           "-metadata", f"title=Kali Glass Live — {name}", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        proc.stdin.write(scene.frame(2 * math.pi * i / n).tobytes())
        if i % max(1, n // 10) == 0:
            print(f"  {name} {H}p : {i}/{n} images ({time.time() - t0:.0f} s)", flush=True)
    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit(f"ffmpeg a échoué pour {name}")
    print(f"✓ {out} ({out.stat().st_size / 1e6:.1f} Mo, {time.time() - t0:.0f} s)")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="dist/live")
    ap.add_argument("--size", default="3840x2160")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--seconds", type=int, default=20)
    ap.add_argument("--crf", type=int, default=20)
    ap.add_argument("--preset", default="veryfast")
    ap.add_argument("--only", default=",".join(PALETTES))
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg est requis : sudo apt install ffmpeg")
    W, H = (int(v) for v in a.size.lower().split("x"))
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, name in enumerate(a.only.split(",")):
        render(name.strip(), out_dir, W, H, a.fps, a.seconds, a.crf, a.preset, seed=100 + i * 13)


if __name__ == "__main__":
    main()
