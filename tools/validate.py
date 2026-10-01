"""Sanity checks for the generated pack: JSON syntax, bone/animation/poser
cross references, texture sizes and resolver paths."""
import glob
import json
import os
import re
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "pack")
A = os.path.join(PACK, "assets", "cobblemon")
ROOTS = [PACK] + sorted(glob.glob(os.path.join(ROOT, "standalone", "*")))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    total = 0
    for r in ROOTS:
        total += check(r)
    print("all OK (%d roots)" % len(ROOTS))


def check(pack):
    global PACK, A
    PACK = pack
    A = os.path.join(PACK, "assets", "cobblemon")
    errors = []
    files = glob.glob(os.path.join(PACK, "**", "*.json"), recursive=True)
    if os.path.exists(os.path.join(PACK, "pack.mcmeta")):
        files.append(os.path.join(PACK, "pack.mcmeta"))
    for p in files:
        try:
            load(p)
        except Exception as e:  # noqa: BLE001
            errors.append("bad json %s: %s" % (p, e))

    models = {}
    for p in glob.glob(os.path.join(A, "bedrock/pokemon/models/*/*.geo.json")):
        g = load(p)["minecraft:geometry"][0]
        bones = {b["name"] for b in g["bones"]}
        models[os.path.basename(p)[:-5]] = (g, bones)
        for b in g["bones"]:
            for c in b.get("cubes", []):
                if any(abs(s - round(s)) > 1e-6 for s in c["size"]):
                    errors.append("%s: fractional cube size in %s" % (p, b["name"]))
                u, v = c["uv"]
                w, h, d = (int(round(s)) for s in c["size"])
                if u + 2 * (w + d) > g["description"]["texture_width"] or v + h + d > g["description"]["texture_height"]:
                    errors.append("%s: uv out of bounds in %s" % (p, b["name"]))

    anims = {}
    for p in glob.glob(os.path.join(A, "bedrock/pokemon/animations/*/*.animation.json")):
        group = os.path.basename(p).split(".")[0]
        anims[group] = load(p)["animations"]

    for p in glob.glob(os.path.join(A, "bedrock/pokemon/resolvers/*/*.json")):
        r = load(p)
        species = r["species"].split(":")[1]
        base = r["variations"][0]
        model_key = base["model"].split(":")[1]
        if model_key not in models:
            errors.append("%s: missing model %s" % (p, model_key))
            continue
        g, bones = models[model_key]
        group = species
        for name, an in anims.get(group, {}).items():
            for bone in an.get("bones", {}):
                if bone not in bones:
                    errors.append("%s: animation %s targets unknown bone %s" % (group, name, bone))
        for var in r["variations"]:
            texs = [var.get("texture")]
            for l in var.get("layers", []):
                t = l["texture"]
                texs += t["frames"] if isinstance(t, dict) else [t]
            for t in texs:
                if not t:
                    continue
                tp = os.path.join(A, t.split(":")[1])
                if not os.path.exists(tp):
                    errors.append("%s: missing texture %s" % (p, tp))
                    continue
                im = Image.open(tp)
                if im.size != (g["description"]["texture_width"], g["description"]["texture_height"]):
                    errors.append("%s: texture size mismatch %s" % (p, tp))
            if "poser" in var:
                pp = glob.glob(os.path.join(A, "bedrock/pokemon/posers/*/%s.json" % var["poser"].split(":")[1]))
                if not pp:
                    errors.append("%s: missing poser %s" % (p, var["poser"]))
                    continue
                poser = load(pp[0])
                text = json.dumps(poser)
                for grp, an in re.findall(r"q\.bedrock(?:_primary|_stateful|_quirk)?\('([a-z_]+)', '([a-z_]+)'", text):
                    if grp == "dummy":
                        continue
                    if "animation.%s.%s" % (grp, an) not in anims.get(grp, {}):
                        errors.append("%s: references missing animation %s.%s" % (pp[0], grp, an))
                for bone in re.findall(r"q\.look\('([a-z_0-9]+)'", text):
                    if bone not in bones:
                        errors.append("%s: look bone %s missing" % (pp[0], bone))
                for pose in poser["poses"].values():
                    for tp in pose.get("transformedParts", []):
                        if tp["part"] not in bones:
                            errors.append("%s: transformed part %s missing" % (pp[0], tp["part"]))
                if poser["rootBone"] not in bones:
                    errors.append("%s: root bone missing" % pp[0])
        locs = [k for b in g["bones"] for k in b.get("locators", {})]
        if not any("eye" in k for k in locs):
            errors.append("%s: no eye locators for alpha bloom" % model_key)

    for p in glob.glob(os.path.join(PACK, "data/cobblemon/species_additions/*.json")):
        d = load(p)
        if not d.get("implemented"):
            errors.append("%s: not implemented" % p)

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("OK %s - %d json files, %d models, %d animation groups" % (os.path.relpath(PACK, ROOT), len(files), len(models), len(anims)))
    return len(files)


if __name__ == "__main__":
    main()
