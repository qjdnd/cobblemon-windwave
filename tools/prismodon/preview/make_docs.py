"""Regenerate the preview images / GIFs under docs/prismodon/."""

import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import preview  # noqa: E402

OUT = os.path.join(preview.REPO, "docs", "prismodon")


def label(im, text):
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 8 + 7 * len(text), 18], fill=(20, 22, 26))
    d.text((5, 3), text, fill=(235, 235, 235))
    return im


def main():
    os.makedirs(OUT, exist_ok=True)
    preview.VIEWS = [
        ("reference", -58, 10, 150, [0, 27, -2]),
        ("left", -90, 4, 150, [0, 27, 2]),
        ("front", -12, 10, 145, [0, 27, 0]),
        ("rear", 140, 18, 150, [0, 27, 0]),
        ("top", -60, 55, 150, [0, 22, 2]),
        ("head", -62, 6, 60, [0, 43, -17]),
    ]
    preview.views(os.path.join(OUT, "views.png"), size=440)

    preview.VIEWS = [("reference", -58, 10, 150, [0, 27, -2])]
    tiles = []
    for tex, name in (("normal", "normal"), ("shiny", "shiny"), ("alpha", "alpha (glowing eyes layer)")):
        path = os.path.join(OUT, f"_{tex}.png")
        preview.views(path, tex=tex, size=440)
        tiles.append(label(Image.open(path).convert("RGB"), name))
        os.unlink(path)
    preview.VIEWS = [("head", -70, 4, 52, [0, 43, -17])]
    path = os.path.join(OUT, "_alpha_head.png")
    preview.views(path, tex="alpha", size=440, background="#0e1014")
    tiles.append(label(Image.open(path).convert("RGB"), "alpha eyes (night)"))
    os.unlink(path)
    sheet = Image.new("RGB", (440 * len(tiles), 440))
    for i, t in enumerate(tiles):
        sheet.paste(t, (i * 440, 0))
    sheet.save(os.path.join(OUT, "variants.png"))

    anims = [
        ("ground_idle", 4.0, dict()),
        ("ground_walk", 1.6, dict(yaw=-90, pitch=4)),
        ("battle_idle", 2.0, dict()),
        ("cry", 2.4, dict(yaw=-70)),
        ("faint", 3.2, dict(yaw=-40, pitch=14)),
        ("sleep", 5.0, dict(yaw=-70, pitch=12, target=(0, 18, -6))),
        ("physical", 1.0, dict(yaw=-75)),
        ("special", 1.3, dict(yaw=-75)),
    ]
    for name, seconds, kw in anims:
        fps = 10 if seconds <= 2.5 else 8
        preview.anim(name, os.path.join(OUT, f"anim_{name}.gif"), seconds=seconds, fps=fps, size=300, **kw)
        print("gif", name)


if __name__ == "__main__":
    main()
