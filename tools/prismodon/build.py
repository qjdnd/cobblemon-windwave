"""Build every Prismodon asset: geometry, textures (normal / shiny / alpha eyes),
animations, poser, resolver and a Blockbench project.

    python3 build.py            # writes into the repository's assets/ + blockbench/

Requires: numpy, pillow.
"""

import json
import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import model_def  # noqa: E402
import paint  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
NAME = model_def.NAME
ASSETS = os.path.join(REPO, "assets", "cobblemon")
PATHS = {
    "geo": os.path.join(ASSETS, "bedrock", "pokemon", "models", NAME, f"{NAME}.geo.json"),
    "anim": os.path.join(ASSETS, "bedrock", "pokemon", "animations", NAME, f"{NAME}.animation.json"),
    "poser": os.path.join(ASSETS, "bedrock", "pokemon", "posers", NAME, f"{NAME}.json"),
    "resolver": os.path.join(ASSETS, "bedrock", "pokemon", "resolvers", NAME, f"0_{NAME}_base.json"),
    "tex": os.path.join(ASSETS, "textures", "pokemon", NAME, f"{NAME}.png"),
    "tex_shiny": os.path.join(ASSETS, "textures", "pokemon", NAME, f"{NAME}_shiny.png"),
    "tex_alpha": os.path.join(ASSETS, "textures", "pokemon", NAME, f"{NAME}_alpha.png"),
    "bbmodel": os.path.join(REPO, "blockbench", f"{NAME}.bbmodel"),
}


def write_json(path, data, indent=2):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def save_png(path, arr):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA").save(path, optimize=True)


def main():
    m = model_def.build()
    used = m.pack_uv()
    print(f"{len(m.bones)} bones, {sum(1 for _ in m.cubes())} cubes, atlas rows used {used}/{m.tex_h}")

    geo = m.to_geo(bounds_w=6, bounds_h=5, bounds_off=[0, 2.25, 0])
    write_json(PATHS["geo"], geo)

    textures = paint.paint_all(m)
    save_png(PATHS["tex"], textures["normal"])
    save_png(PATHS["tex_shiny"], textures["shiny"])
    save_png(PATHS["tex_alpha"], textures["alpha"])

    import anims
    import cobblemon_json
    write_json(PATHS["anim"], anims.build(m))
    write_json(PATHS["poser"], cobblemon_json.poser())
    write_json(PATHS["resolver"], cobblemon_json.resolver())

    # Optional: let a locally built Blockbench (web) compile the .bbmodel project
    # BLOCKBENCH_DIR=<blockbench checkout after `npm run build-web`>
    # PREVIEW_NODE_MODULES=<node_modules containing playwright>
    if os.environ.get("BLOCKBENCH_DIR") and os.environ.get("PREVIEW_NODE_MODULES"):
        os.makedirs(os.path.dirname(PATHS["bbmodel"]), exist_ok=True)
        subprocess.run(["node", os.path.join(HERE, "preview", "blockbench_export.mjs"),
                        PATHS["geo"], PATHS["anim"], PATHS["bbmodel"], "",
                        PATHS["tex"], PATHS["tex_shiny"], PATHS["tex_alpha"]], check=True)
    else:
        print("  (skipping .bbmodel: set BLOCKBENCH_DIR and PREVIEW_NODE_MODULES to export it)")
    for k, p in PATHS.items():
        if os.path.exists(p):
            print(f"  {k:10s} {os.path.relpath(p, REPO)}")


if __name__ == "__main__":
    main()
