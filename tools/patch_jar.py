"""Builds the Wind Wave Pokémon directly into a Cobblemon 1.8.1 jar.

Instead of shipping a resource pack + data pack, this writes everything into the
mod jar the same way Cobblemon ships its own Pokémon:
  * models / animations / posers / resolvers / textures -> assets/cobblemon/...
  * the species files themselves get "implemented": true, baseScale and hitbox
    (data/cobblemon/species/generationN/<name>.json)
  * spawn pools and alpha herds -> data/cobblemon/spawn_pool_world/...
No existing file other than those species files is changed.

    python3 tools/patch_jar.py Cobblemon-fabric-1.8.1+1.21.1.jar [out.jar]
"""
import json
import os
import sys
import zipfile
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(ROOT, "pack")


def pack_files(top):
    out = {}
    base = os.path.join(PACK, top)
    for b, _, names in os.walk(base):
        for n in names:
            full = os.path.join(b, n)
            out[os.path.relpath(full, PACK).replace(os.sep, "/")] = full
    return out


def species_patches():
    """species name -> fields from our species_additions files."""
    d = os.path.join(PACK, "data", "cobblemon", "species_additions")
    out = {}
    for fn in sorted(os.listdir(d)):
        with open(os.path.join(d, fn), encoding="utf-8") as f:
            add = json.load(f, object_pairs_hook=OrderedDict)
        name = add.pop("target").split(":")[1]
        out[name] = add
    return out


def patch_species(raw, fields):
    data = json.loads(raw, object_pairs_hook=OrderedDict)
    out = OrderedDict()
    out["implemented"] = True
    for k, v in data.items():
        if k == "implemented":
            continue
        out[k] = fields.get(k, v) if k in fields else v
    for k, v in fields.items():
        if k not in out:
            out[k] = v
    return (json.dumps(out, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def patch(src, dst):
    adds = {}
    adds.update(pack_files("assets"))
    data = pack_files("data")
    # species_additions are folded into the species files instead
    adds.update({k: v for k, v in data.items() if "/species_additions/" not in k})
    patches = species_patches()

    zin = zipfile.ZipFile(src)
    names = set(zin.namelist())
    clash = sorted(k for k in adds if k in names)
    if clash:
        raise SystemExit("refusing to overwrite existing jar entries: %s" % clash[:5])
    species_paths = {}
    for n in names:
        if n.startswith("data/cobblemon/species/") and n.endswith(".json"):
            base = os.path.basename(n)[:-5]
            if base in patches:
                species_paths[base] = n
    missing = sorted(set(patches) - set(species_paths))
    if missing:
        raise SystemExit("species not found in jar: %s" % missing)

    changed = []
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            raw = zin.read(info.filename)
            base = os.path.basename(info.filename)[:-5] if info.filename.endswith(".json") else None
            if base in species_paths and species_paths[base] == info.filename:
                raw = patch_species(raw, patches[base])
                changed.append(info.filename)
            ni = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            ni.compress_type = zipfile.ZIP_STORED if info.filename.endswith("/") else zipfile.ZIP_DEFLATED
            ni.external_attr = info.external_attr
            ni.create_system = info.create_system
            zout.writestr(ni, raw)
        # directory entries for the new folders, then the files
        new_dirs = set()
        for arc in adds:
            parts = arc.split("/")[:-1]
            for i in range(1, len(parts) + 1):
                d = "/".join(parts[:i]) + "/"
                if d not in names:
                    new_dirs.add(d)
        for d in sorted(new_dirs):
            zi = zipfile.ZipInfo(d, date_time=(2026, 10, 3, 0, 0, 0))
            zi.external_attr = 0o40755 << 16
            zout.writestr(zi, b"")
        for arc in sorted(adds):
            zi = zipfile.ZipInfo(arc, date_time=(2026, 10, 3, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            with open(adds[arc], "rb") as f:
                zout.writestr(zi, f.read())
    return changed, sorted(adds)


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else src.replace(".jar", "-windwave.jar")
    changed, added = patch(src, dst)
    print("patched species:", ", ".join(changed))
    print("added %d files" % len(added))
    print("->", dst)


if __name__ == "__main__":
    main()
