"""
Cross-checks the built packs against a Cobblemon 1.8.1 source checkout.

    python3 tools/validate.py <cobblemon-repo> <unzipped-showdown-dir>

Checks that every move, ability, item, biome tag, species, particle, sound and animation
the packs reference really exists (in Cobblemon 1.8.1, vanilla 1.21.1 or in the packs).
"""

import glob
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
COB = os.path.abspath(sys.argv[1])
SD = os.path.abspath(sys.argv[2])
RES = os.path.join(COB, "common/src/main/resources")
RP = os.path.join(ROOT, "resourcepack/assets/cobblemon")
DP = os.path.join(ROOT, "datapack/data/cobblemon")

errors = []


def err(msg):
    errors.append(msg)
    print("  ERROR:", msg)


def node_keys(module, export):
    out = subprocess.check_output(["node", "-e", f"console.log(JSON.stringify(Object.keys(require('{module}').{export})))"])
    return set(json.loads(out))


# ---------------------------------------------------------------- reference data
moves = node_keys(os.path.join(SD, "data/moves.js"), "Moves") | {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(DP, "moves/*.js"))}
abilities = node_keys(os.path.join(SD, "data/abilities.js"), "Abilities") | {os.path.basename(f)[:-3] for f in glob.glob(os.path.join(DP, "abilities/*.js"))}
species = {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(RES, "data/cobblemon/species/*/*.json"))}
species |= {os.path.basename(f)[:-5] for f in glob.glob(os.path.join(DP, "species/*/*.json"))}
biome_tags = {"#cobblemon:" + os.path.relpath(f, os.path.join(RES, "data/cobblemon/tags/worldgen/biome"))[:-5]
              for f in glob.glob(os.path.join(RES, "data/cobblemon/tags/worldgen/biome/**/*.json"), recursive=True)}
cob_lang = json.load(open(os.path.join(RES, "assets/cobblemon/lang/en_us.json"), encoding="utf-8"))
cob_items = {k.split(".", 2)[2] for k in cob_lang if k.startswith("item.cobblemon.") and k.count(".") == 2}
cob_items |= {k.split(".", 2)[2] for k in cob_lang if k.startswith("block.cobblemon.") and k.count(".") == 2}
vanilla_items = {"white_wool", "blue_ice", "feather", "cod", "cobblestone", "soul_sand", "iron_nugget", "packed_ice", "kelp",
                 "seagrass", "kelp_plant", "tall_seagrass"}
particles = set()
for f in glob.glob(os.path.join(RES, "assets/cobblemon/bedrock/particles/**/*.particle.json"), recursive=True) + \
        glob.glob(os.path.join(RP, "bedrock/particles/**/*.particle.json"), recursive=True):
    particles.add(json.load(open(f))["particle_effect"]["description"]["identifier"])
cob_sounds = json.load(open(os.path.join(RES, "assets/cobblemon/sounds.json"), encoding="utf-8"))
pack_sounds = json.load(open(os.path.join(RP, "sounds.json"), encoding="utf-8"))
sound_files = {os.path.relpath(p, os.path.join(RES, "assets/cobblemon/sounds"))[:-4]
               for p in subprocess.check_output(["git", "-C", COB, "ls-tree", "-r", "--name-only", "HEAD",
                                                 "common/src/main/resources/assets/cobblemon/sounds"]).decode().split()}
sound_files = {s.replace("common/src/main/resources/assets/cobblemon/sounds/", "") for s in sound_files}
sound_files = {os.path.basename(os.path.dirname(s)) + "/" + os.path.basename(s) if "/" in s else s for s in sound_files}


def check_item(item, where):
    ns, _, path = item.partition(":")
    if ns == "cobblemon" and path not in cob_items:
        err(f"{where}: unknown Cobblemon item {item}")
    if ns == "minecraft" and path not in vanilla_items:
        err(f"{where}: unchecked vanilla item {item}")


def check_biome(b, where):
    if b.startswith("#cobblemon:") and b not in biome_tags:
        err(f"{where}: unknown biome tag {b}")


def walk_requirements(reqs, where):
    for r in reqs:
        v = r["variant"]
        if v == "any":
            walk_requirements(r["possibilities"], where)
        elif v == "held_item":
            check_item(r["itemCondition"], where)
        elif v in ("has_move", "use_move"):
            if r["move"] not in moves:
                err(f"{where}: unknown move {r['move']}")
        elif v == "biome":
            check_biome(r.get("biomeCondition", ""), where)
        elif v == "party_member":
            if r["target"].split()[0] not in species and "=" not in r["target"]:
                err(f"{where}: unknown party member {r['target']}")


# ---------------------------------------------------------------- species
print("species")
for f in sorted(glob.glob(os.path.join(DP, "species/*/*.json"))):
    d = json.load(open(f))
    n = os.path.basename(f)
    for m in d["moves"]:
        mv = m.split(":", 1)[1]
        if mv not in moves:
            err(f"{n}: unknown move {mv}")
    for a in d["abilities"]:
        if a.replace("h:", "") not in abilities:
            err(f"{n}: unknown ability {a}")
    for e in d["drops"]["entries"]:
        check_item(e["item"], n)
    if d["preEvolution"] not in species:
        err(f"{n}: unknown preEvolution")
    for seat in d.get("riding", {}).get("seats", []):
        geo = glob.glob(os.path.join(RP, f"bedrock/pokemon/models/*/{n[:-5]}.geo.json"))[0]
        if f'"{seat["locator"]}"' not in open(geo).read():
            err(f"{n}: seat locator {seat['locator']} not in model")
    for ride in d.get("riding", {}).get("behaviours", {}).values():
        for s in ride.get("rideSounds", []):
            if s["soundLocation"].split(":")[1] not in cob_sounds:
                err(f"{n}: ride sound {s['soundLocation']} missing")

print("evolutions")
for f in sorted(glob.glob(os.path.join(DP, "species_additions/*/*.json"))):
    d = json.load(open(f))
    n = os.path.basename(f)
    if d["target"].split(":")[1] not in species:
        err(f"{n}: unknown target")
    for ev in d["evolutions"]:
        if ev["result"] not in species:
            err(f"{n}: unknown result {ev['result']}")
        for m in ev["learnableMoves"]:
            if m not in moves:
                err(f"{n}: unknown learnable move {m}")
        if ev["variant"] == "item_interact":
            check_item(ev["requiredContext"], n)
        if ev["variant"] == "trade" and "requiredContext" in ev and ev["requiredContext"] not in species:
            err(f"{n}: unknown trade partner {ev['requiredContext']}")
        walk_requirements(ev["requirements"], n)
        for e in ev.get("drops", {}).get("entries", []):
            check_item(e["item"], n)

print("spawns")
for f in sorted(glob.glob(os.path.join(DP, "spawn_pool_world/**/*.json"), recursive=True)):
    d = json.load(open(f))
    n = os.path.basename(f)
    ids = set()
    for s in d["spawns"]:
        if s["id"] in ids:
            err(f"{n}: duplicate id {s['id']}")
        ids.add(s["id"])
        for b in s.get("condition", {}).get("biomes", []) + s.get("anticondition", {}).get("biomes", []):
            check_biome(b, n)
        for p in s.get("presets", []):
            if not os.path.exists(os.path.join(RES, f"data/cobblemon/spawn_detail_presets/{p}.json")):
                err(f"{n}: unknown preset {p}")
        mons = [s["pokemon"]] if "pokemon" in s else [h["pokemon"] for h in s["herdablePokemon"]]
        for mon in mons:
            parts = mon.split()
            if parts[0] not in species:
                err(f"{n}: unknown species {parts[0]}")
            for p in parts[1:]:
                if p.startswith("held_item="):
                    check_item(p.split("=", 1)[1], n)

print("habitat pools")
for f in sorted(glob.glob(os.path.join(DP, "habitat_pools/*.json"))):
    d = json.load(open(f))
    if d["name"] not in json.load(open(os.path.join(RP, "lang/en_us.json"), encoding="utf-8")):
        err(f"{f}: missing lang for {d['name']}")
    for s in d["spawns"]:
        if s["species"].lower() not in species:
            err(f"{f}: unknown species {s['species']}")
        for p in s.get("modifiers", "").split():
            if p.startswith("held_item="):
                check_item(p.split("=", 1)[1], os.path.basename(f))

print("action effects")
for f in sorted(glob.glob(os.path.join(DP, "action_effects/moves/*.json"))):
    d = json.load(open(f))
    n = os.path.basename(f)
    if n[:-5] not in moves:
        err(f"{n}: action effect for unknown move")
    for kf in d["timeline"]:
        if kf["type"] == "entity_particles" and kf["effect"] not in particles:
            err(f"{n}: unknown particle {kf['effect']}")
        if kf["type"] == "entity_sound" and kf["sound"].split(":")[1] not in cob_sounds:
            err(f"{n}: unknown sound {kf['sound']}")

print("tms")
for f in sorted(glob.glob(os.path.join(DP, "tms/*.json"))):
    d = json.load(open(f))
    if d["moveName"] not in moves:
        err(f"{f}: unknown move")
    for r in d["recipe"]:
        check_item(r["item"], os.path.basename(f))

print("resource pack")
for key, val in pack_sounds.items():
    for s in val["sounds"]:
        path = s["name"].split(":")[1].replace("pokemon/", "", 1)
        if path not in sound_files:
            err(f"sounds.json {key}: missing file {s['name']}")
lang = json.load(open(os.path.join(RP, "lang/en_us.json"), encoding="utf-8"))
ko = json.load(open(os.path.join(RP, "lang/ko_kr.json"), encoding="utf-8"))
if set(lang) != set(ko):
    err("en_us and ko_kr keys differ")
for f in sorted(glob.glob(os.path.join(DP, "species/*/*.json"))):
    i = os.path.basename(f)[:-5]
    for k in (f"cobblemon.species.{i}.name", f"cobblemon.species.{i}.desc"):
        if k not in lang:
            err(f"missing lang {k}")
for m in glob.glob(os.path.join(DP, "moves/*.js")):
    if f"cobblemon.move.{os.path.basename(m)[:-3]}" not in lang:
        err(f"missing move lang {m}")
for resolver in glob.glob(os.path.join(RP, "bedrock/pokemon/resolvers/*/*.json")):
    d = json.load(open(resolver))
    for v in d["variations"]:
        texs = [v.get("texture")] + [layer["texture"] for layer in v.get("layers", [])]
        for t in filter(None, texs):
            if not os.path.exists(os.path.join(RP, t.split(":")[1])):
                err(f"{resolver}: missing texture {t}")
        if "model" in v and not glob.glob(os.path.join(RP, "bedrock/pokemon/models/*", v["model"].split(":")[1] + ".json")):
            err(f"{resolver}: missing model {v['model']}")
        if "poser" in v and not glob.glob(os.path.join(RP, "bedrock/pokemon/posers/*", v["poser"].split(":")[1] + ".json")):
            err(f"{resolver}: missing poser {v['poser']}")
for anim_file in glob.glob(os.path.join(RP, "bedrock/pokemon/animations/*/*.animation.json")):
    i = os.path.basename(anim_file).split(".")[0]
    anims = json.load(open(anim_file))["animations"]
    bones = {b["name"] for b in json.load(open(glob.glob(os.path.join(RP, f"bedrock/pokemon/models/*/{i}.geo.json"))[0]))["minecraft:geometry"][0]["bones"]}
    for name, a in anims.items():
        for b in a.get("bones", {}):
            if b not in bones:
                err(f"{i}: animation {name} references missing bone {b}")
        for t, eff in a.get("sound_effects", {}).items():
            effs = eff if isinstance(eff, list) else [eff]
            for e in effs:
                if e["effect"] not in cob_sounds and e["effect"] not in pack_sounds:
                    err(f"{i}: animation {name} plays unknown sound {e['effect']}")
    poser = json.load(open(glob.glob(os.path.join(RP, f"bedrock/pokemon/posers/*/{i}.json"))[0]))
    for bone in re.findall(r"q\.look\('(\w+)'", json.dumps(poser)) + [poser["rootBone"]]:
        if bone not in bones:
            err(f"{i}: poser uses missing bone {bone}")
    model_text = open(glob.glob(os.path.join(RP, f"bedrock/pokemon/models/*/{i}.geo.json"))[0]).read()
    for loc in ("beam1", "beam2", "beam3") if i == "threiscue" else ():
        if f'"{loc}"' not in model_text:
            err(f"{i}: missing locator {loc}")
    if not re.search(r'"eye\w*"\s*:', model_text):
        err(f"{i}: no eye locator for alpha glow")

print()
if errors:
    print(f"{len(errors)} problem(s) found")
    sys.exit(1)
print("ALL CHECKS PASSED")
