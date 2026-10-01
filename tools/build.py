"""Builds the Wind Wave Cobblemon pack (models, textures, animations, posers,
resolvers) and preview renders.

    python3 tools/build.py            # build pack files
    python3 tools/build.py --previews # also render previews/ (slower)
"""
import argparse
import importlib
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "pokemon"))

from cobblegen import anim as animlib, geom, preview  # noqa: E402

PACK = os.path.join(ROOT, "pack")
ASSETS = os.path.join(PACK, "assets", "cobblemon")
PREVIEWS = os.path.join(ROOT, "previews")

SPECIES = ["gulpin", "swalot"]


def _write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def build_species(name, previews=False):
    mod = importlib.import_module(name)
    amod = importlib.import_module(name + "_anim")
    dex = mod.DEX
    model = mod.build_model()
    bad = geom.check_integer_sizes(model)
    if bad:
        raise SystemExit("non-integer cube sizes: %r" % bad)

    bed = os.path.join(ASSETS, "bedrock", "pokemon")
    for sub in ("models", "animations", "posers", "resolvers"):
        os.makedirs(os.path.join(bed, sub, dex), exist_ok=True)
    tex_dir = os.path.join(ASSETS, "textures", "pokemon", dex)
    os.makedirs(tex_dir, exist_ok=True)

    model.write_geo(os.path.join(bed, "models", dex, name + ".geo.json"))

    textures = {}
    for pal in ("normal", "shiny"):
        arr = mod.paint_textures(model, pal)
        textures[pal] = arr
        fn = name + (".png" if pal == "normal" else "_shiny.png")
        Image.fromarray(arr, "RGBA").save(os.path.join(tex_dir, fn), optimize=True)
    alpha = mod.paint_alpha(model)
    Image.fromarray(alpha, "RGBA").save(os.path.join(tex_dir, name + "_alpha.png"), optimize=True)

    anims = amod.all_animations()
    animlib.write_animation_file(os.path.join(bed, "animations", dex, name + ".animation.json"), name, anims)
    _write_json(os.path.join(bed, "posers", dex, name + ".json"), amod.poser(False))
    _write_json(os.path.join(bed, "posers", dex, name + "_female.json"), amod.poser(True))
    _write_json(os.path.join(bed, "resolvers", dex, "0_%s_base.json" % name), amod.resolver())
    print("built", name, "-", sum(1 for _ in model.cubes()), "cubes,", len(anims), "animations")

    if previews:
        render_previews(name, mod, amod, model, textures, alpha, anims)


def render_previews(name, mod, amod, model, textures, alpha, anims):
    out = os.path.join(PREVIEWS, name)
    os.makedirs(out, exist_ok=True)
    size = getattr(mod, "PREVIEW_SIZE", (420, 420))
    # turntable sheet
    imgs = []
    for yaw in (-35, 35, -100, 150):
        sc = preview.Scene(model, textures["normal"], yaw=yaw, pitch=16, size=size)
        imgs.append(sc.frame())
    preview.sheet(imgs, 4).save(os.path.join(out, "turntable.png"))
    # variants
    v = []
    v.append(preview.Scene(model, textures["normal"], yaw=-32, pitch=14, size=size).frame(label="normal"))
    v.append(preview.Scene(model, textures["shiny"], yaw=-32, pitch=14, size=size).frame(label="shiny"))
    sc = preview.Scene(model, textures["normal"], emissive=alpha, yaw=-20, pitch=10, size=size)
    v.append(sc.frame(glow=True, label="alpha"))
    sc = preview.Scene(model, textures["shiny"], emissive=alpha, yaw=-20, pitch=10, size=size)
    v.append(sc.frame(glow=True, label="shiny alpha"))
    preview.sheet(v, 4).save(os.path.join(out, "variants.png"))
    # textures (x4 nearest)
    for key, arr in (("normal", textures["normal"]), ("shiny", textures["shiny"]), ("alpha", alpha)):
        im = Image.fromarray(arr, "RGBA")
        bg = Image.new("RGBA", im.size, (40, 40, 40, 255))
        bg.alpha_composite(im)
        bg.resize((im.size[0] * 4, im.size[1] * 4), Image.NEAREST).save(os.path.join(out, "texture_%s.png" % key))
    # animations
    ad = {a.name: a.to_dict() for a in anims}
    idle = ad.get("ground_idle")
    small = (240, 240)
    sc = preview.Scene(model, textures["normal"], yaw=-35, pitch=14, size=small)
    order = getattr(amod, "PREVIEW_ORDER", list(ad))
    sheets = []
    for an in order:
        d = ad[an]
        length = d.get("animation_length", 3.0)
        base = [idle] if an in getattr(amod, "OVER_IDLE", ()) and idle else []
        fr = preview.animate(sc, base + [d], length, fps=15, label=an, flat=True)
        preview.gif(os.path.join(out, "anim_%s.gif" % an), fr, fps=15)
        idx = np.linspace(0, len(fr) - 1, 6).astype(int)
        sheets.append(preview.sheet([fr[i] for i in idx], 6, pad=2))
    w = max(s.size[0] for s in sheets)
    h = sum(s.size[1] for s in sheets)
    big = Image.new("RGBA", (w, h), (30, 30, 30, 255))
    y = 0
    for s in sheets:
        big.alpha_composite(s, (0, y))
        y += s.size[1]
    big.convert("RGB").save(os.path.join(out, "animations.png"), optimize=True)
    print("previews", name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--previews", action="store_true")
    ap.add_argument("species", nargs="*")
    args = ap.parse_args()
    for n in (args.species or SPECIES):
        build_species(n, args.previews)


if __name__ == "__main__":
    main()
