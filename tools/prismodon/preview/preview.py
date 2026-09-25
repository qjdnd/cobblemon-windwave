"""Render preview sheets of the generated model with the headless three.js viewer.

    python3 preview.py views  OUT.png [--tex normal|shiny|alpha]
    python3 preview.py anim   NAME OUT.gif [--seconds 2 --fps 12 --yaw -60]

Environment: PREVIEW_NODE_MODULES (folder with three + playwright),
             CHROMIUM_PATH (optional Chromium binary).
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NAME = "prismodon"
A = os.path.join(REPO, "assets", "cobblemon")
GEO = os.path.join(A, "bedrock", "pokemon", "models", NAME, f"{NAME}.geo.json")
ANIM = os.path.join(A, "bedrock", "pokemon", "animations", NAME, f"{NAME}.animation.json")
TEX = {
    "normal": os.path.join(A, "textures", "pokemon", NAME, f"{NAME}.png"),
    "shiny": os.path.join(A, "textures", "pokemon", NAME, f"{NAME}_shiny.png"),
}
ALPHA = os.path.join(A, "textures", "pokemon", NAME, f"{NAME}_alpha.png")

VIEWS = [
    ("reference", -58, 10, 150, [0, 26, -2]),
    ("left", -90, 4, 150, [0, 26, 2]),
    ("front", 0, 8, 150, [0, 26, 0]),
    ("rear", 145, 18, 150, [0, 26, 0]),
    ("top", -60, 55, 150, [0, 22, 2]),
    ("head", -65, 6, 58, [0, 40, -16]),
]


def run(job, prefix):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(job, f)
        path = f.name
    subprocess.run(["node", os.path.join(HERE, "render.mjs"), path, prefix], check=True,
                   stdout=subprocess.DEVNULL)
    os.unlink(path)


def sheet(images, cols):
    w, h = images[0].size
    rows = (len(images) + cols - 1) // cols
    out = Image.new("RGBA", (w * cols, h * rows), (32, 36, 42, 255))
    for i, im in enumerate(images):
        out.paste(im, ((i % cols) * w, (i // cols) * h))
    return out


def views(out, tex="normal", size=520, names=None, background="#2a2f36"):
    layers = [ALPHA] if tex == "alpha" else []
    job = {"geo": GEO, "texture": TEX["normal" if tex == "alpha" else tex], "layers": layers,
           "animation": ANIM if os.path.exists(ANIM) else None,
           "width": size, "height": size, "background": background, "shots": []}
    for name, yaw, pitch, dist, tgt in VIEWS:
        if names and name not in names:
            continue
        job["shots"].append({"name": name, "yaw": yaw, "pitch": pitch, "dist": dist, "target": tgt})
    tmp = tempfile.mkdtemp()
    run(job, os.path.join(tmp, "v_"))
    ims = [Image.open(os.path.join(tmp, f"v_{s['name']}.png")).convert("RGBA") for s in job["shots"]]
    sheet(ims, min(3, len(ims))).save(out)


def anim(name, out, seconds=2.0, fps=12, yaw=-58, pitch=10, dist=150, target=(0, 26, -2), size=420,
         tex="normal", extra=()):
    frames = int(round(seconds * fps))
    layers = [ALPHA] if tex == "alpha" else []
    job = {"geo": GEO, "texture": TEX["normal" if tex == "alpha" else tex], "layers": layers,
           "animation": ANIM, "width": size, "height": size, "background": "#2a2f36", "shots": []}
    for i in range(frames):
        t = i / fps
        a = [{"name": f"animation.{NAME}.{name}", "time": t}]
        a += [{"name": f"animation.{NAME}.{e}", "time": t} for e in extra]
        job["shots"].append({"name": f"{i:04d}", "yaw": yaw, "pitch": pitch, "dist": dist,
                             "target": list(target), "anims": a})
    tmp = tempfile.mkdtemp()
    run(job, os.path.join(tmp, "f_"))
    ims = [Image.open(os.path.join(tmp, f"f_{i:04d}.png")).convert("RGB") for i in range(frames)]
    # one shared 64-colour palette keeps the GIF small and flicker free
    strip = Image.new("RGB", (size, size * min(len(ims), 6)))
    for k, im in enumerate(ims[:: max(1, len(ims) // 6)][:6]):
        strip.paste(im, (0, k * size))
    pal = strip.quantize(colors=64, method=Image.Quantize.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in ims]
    q[0].save(out, save_all=True, append_images=q[1:], duration=int(1000 / fps), loop=0, optimize=True)
    return ims


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["views", "anim"])
    ap.add_argument("args", nargs="+")
    ap.add_argument("--tex", default="normal")
    ap.add_argument("--seconds", type=float, default=2.0)
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--yaw", type=float, default=-58)
    ap.add_argument("--only", default="")
    ns = ap.parse_args()
    if ns.mode == "views":
        views(ns.args[0], ns.tex, names=[s for s in ns.only.split(",") if s] or None)
    else:
        anim(ns.args[0], ns.args[1], ns.seconds, ns.fps, ns.yaw, tex=ns.tex)
    sys.exit(0)
