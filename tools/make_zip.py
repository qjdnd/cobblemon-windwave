"""Zips pack/ into dist/.

Produces four files:
  * ..._resourcepack.zip  (assets only, for .minecraft/resourcepacks/)
  * ..._datapack.zip      (data only, for saves/<world>/datapacks/)
  * ...gulpin-swalot.zip  (combined, works in both places)
  * cobblemon-windwave-models.zip (model assets of every Pokémon, incl. standalone ones)
"""
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "pack")
DIST = os.path.join(ROOT, "dist")
BASE = "cobblemon-windwave-gulpin-swalot"
DESC = "Cobblemon Wind Wave - Gulpin & Swalot (1.8.1)"

# Minecraft 1.21.1: resource pack format 34, data pack format 48
RESOURCE_META = {"pack": {"pack_format": 34, "description": DESC + " [Resource Pack]"}}
DATA_META = {"pack": {"pack_format": 48, "description": DESC + " [Data Pack]"}}


def _collect(top):
    files = []
    root = os.path.join(PACK, top)
    for base, _, names in os.walk(root):
        for n in names:
            full = os.path.join(base, n)
            files.append((os.path.relpath(full, PACK).replace(os.sep, "/"), full))
    return sorted(files)


def _write(path, entries):
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, data in entries:
            info = zipfile.ZipInfo(arc, date_time=(2026, 10, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    print(path, len(entries), "files")


def _read(p):
    with open(p, "rb") as f:
        return f.read()


def main():
    os.makedirs(DIST, exist_ok=True)
    icon = ("pack.png", _read(os.path.join(PACK, "pack.png")))
    assets = [(a, _read(f)) for a, f in _collect("assets")]
    data = [(a, _read(f)) for a, f in _collect("data")]

    def meta(d):
        return ("pack.mcmeta", (json.dumps(d, indent=2) + "\n").encode("utf-8"))

    _write(os.path.join(DIST, BASE + "_resourcepack.zip"), [meta(RESOURCE_META), icon] + assets)
    _write(os.path.join(DIST, BASE + "_datapack.zip"), [meta(DATA_META), icon] + data)
    _write(os.path.join(DIST, BASE + ".zip"),
           [("pack.mcmeta", _read(os.path.join(PACK, "pack.mcmeta"))), icon] + assets + data)


def models_zip():
    """All model assets (geo, animations, posers, resolvers, normal/shiny/alpha textures)
    for every Pokémon, including standalone ones that are not in the pack yet."""
    roots = [PACK] + sorted(os.path.join(ROOT, "standalone", d) for d in os.listdir(os.path.join(ROOT, "standalone")))
    entries = []
    for r in roots:
        base = os.path.join(r, "assets")
        for b, _, names in os.walk(base):
            for n in names:
                full = os.path.join(b, n)
                entries.append((os.path.relpath(full, r).replace(os.sep, "/"), _read(full)))
    entries.sort()
    _write(os.path.join(DIST, "cobblemon-windwave-models.zip"), entries)



if __name__ == "__main__":
    main()
    models_zip()
