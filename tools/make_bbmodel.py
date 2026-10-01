"""Writes Blockbench projects (bbmodel/<name>.bbmodel) for every Pokémon, with the
geometry, all textures (normal, shiny, alpha, extra layers) and every animation."""
import glob
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

from cobblegen import bbmodel  # noqa: E402
import build  # noqa: E402

OUT = os.path.join(ROOT, "bbmodel")


def assets_root(name):
    if name in build.STANDALONE:
        return os.path.join(build.STANDALONE[name], "assets", "cobblemon")
    return build.ASSETS


def make(name):
    mod = importlib.import_module(name)
    model = mod.build_model()
    a = assets_root(name)
    tex_dir = os.path.join(a, "textures", "pokemon", mod.DEX)
    files = [name + ".png", name + "_shiny.png", name + "_alpha.png"] + \
        sorted(os.path.basename(p) for p in glob.glob(os.path.join(tex_dir, name + "_flame_*.png")))
    textures = [(f, np.array(Image.open(os.path.join(tex_dir, f)).convert("RGBA"))) for f in files]
    flame_idx = next((i for i, (f, _) in enumerate(textures) if "_flame_" in f), None)
    anim = json.load(open(os.path.join(a, "bedrock", "pokemon", "animations", mod.DEX, name + ".animation.json")))

    def face_tex(c):
        return flame_idx if (flame_idx is not None and c.tag == "flame") else 0

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".bbmodel")
    proj = bbmodel.export(model, textures, anim, path, face_texture=face_tex)

    # round-trip check against the shipped .geo.json
    geo = json.load(open(os.path.join(a, "bedrock", "pokemon", "models", mod.DEX, name + ".geo.json")))
    bones = {b["name"]: b for b in geo["minecraft:geometry"][0]["bones"]}
    back = bbmodel.to_geo_bones(proj)
    assert set(back) == set(bones), "bone mismatch"
    for bn, b in bones.items():
        r = back[bn]
        assert r["parent"] == b.get("parent"), bn
        assert np.allclose(r["pivot"], b["pivot"]), bn
        assert np.allclose(r["rotation"] or [0, 0, 0], b.get("rotation", [0, 0, 0])), bn
        assert len(r["cubes"]) == len(b.get("cubes", [])), bn
        for (o, s, uv, mir, inf), c in zip(r["cubes"], b.get("cubes", [])):
            assert np.allclose(o, c["origin"]) and np.allclose(s, c["size"]), bn
            assert list(uv) == c["uv"] and mir == c.get("mirror", False), bn
        for k, v in b.get("locators", {}).items():
            assert np.allclose(r["locators"][k], v), bn
    n_kf = sum(len(an["keyframes"]) for x in proj["animations"] for an in x["animators"].values())
    print("%s.bbmodel: %d elements, %d textures, %d animations (%d keyframes), %.0f KB"
          % (name, len(proj["elements"]), len(textures), len(proj["animations"]), n_kf, os.path.getsize(path) / 1024))


if __name__ == "__main__":
    for n in (sys.argv[1:] or build.SPECIES):
        make(n)
