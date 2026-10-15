"""Writes the Horyeong Cobblemon model assets into <repo>/assets/cobblemon/..."""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cg, model_def, paint, poses, anims

NAME = model_def.NAME
REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
A = os.path.join(REPO, "assets", "cobblemon")
P_MODEL = os.path.join(A, "bedrock", "pokemon", "models", NAME)
P_ANIM = os.path.join(A, "bedrock", "pokemon", "animations", NAME)
P_POSER = os.path.join(A, "bedrock", "pokemon", "posers", NAME)
P_RES = os.path.join(A, "bedrock", "pokemon", "resolvers", NAME)
P_TEX = os.path.join(A, "textures", "pokemon", NAME)


def poser():
    g = NAME
    look = "q.look('head', 1, 1, 50, -35, 40, -40)"
    blink = "q.bedrock_quirk('%s', 'blink')" % g
    return {
        "portraitScale": 1.06,
        "portraitTranslation": [-0.51, 1.07, 0],
        "profileScale": 0.55,
        "profileTranslation": [0, 0.9, 0],
        "rootBone": g,
        "animations": {
            "cry": "q.bedrock_stateful('%s', 'cry')" % g,
            "recoil": "q.bedrock_stateful('%s', 'recoil')" % g,
            "physical": "q.bedrock_primary('%s', 'physical', q.curve('symmetrical_wide'))" % g,
            "special": "q.bedrock_primary('%s', 'special', q.curve('symmetrical_wide'))" % g,
            "status": "q.bedrock_primary('%s', 'status', q.curve('symmetrical_wide'))" % g,
            "faint": "q.bedrock_primary('%s', 'faint', q.curve('one'))" % g,
        },
        "poses": {
            "battle-standing": {
                "poseTypes": ["STAND"],
                "isBattle": True,
                "animations": [look, "q.bedrock('%s', 'battle_idle')" % g],
                "quirks": [blink],
            },
            "standing": {
                "poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE"],
                "isBattle": False,
                "animations": [look, "q.bedrock('%s', 'ground_idle')" % g],
                "quirks": [blink,
                           "q.bedrock_quirk('%s', 'yawn', 25, 70)" % g,
                           "q.bedrock_quirk('%s', 'doze', 30, 90)" % g],
            },
            "floating": {
                "poseTypes": ["FLOAT"],
                "animations": [look, "q.bedrock('%s', 'battle_idle')" % g],
                "quirks": [blink],
            },
            "walking": {
                "poseTypes": ["WALK", "SWIM"],
                "condition": "!q.is_sprinting",
                "animations": [look, "q.bedrock('%s', 'ground_walk')" % g],
                "quirks": [blink],
            },
            "running": {
                "poseTypes": ["WALK", "SWIM"],
                "condition": "q.is_sprinting",
                "animations": [look, "q.bedrock('%s', 'ground_run')" % g],
                "quirks": [blink],
            },
            "battle-sleep": {
                "poseTypes": ["SLEEP"],
                "isBattle": True,
                "namedAnimations": {"cry": "q.bedrock_stateful('dummy', 'cry')"},
                "animations": ["q.bedrock('%s', 'sleep')" % g],
            },
            "sleep": {
                "poseTypes": ["SLEEP"],
                "isBattle": False,
                "namedAnimations": {"cry": "q.bedrock_stateful('dummy', 'cry')"},
                "animations": ["q.bedrock('%s', 'sleep')" % g],
            },
        },
    }


def resolver():
    tex = "cobblemon:textures/pokemon/%s/%s" % (NAME, NAME)
    return {
        "species": "cobblemon:%s" % NAME,
        "order": 0,
        "variations": [
            {"aspects": [], "poser": "cobblemon:%s" % NAME, "model": "cobblemon:%s.geo" % NAME,
             "texture": tex + ".png", "layers": []},
            {"aspects": ["shiny"], "texture": tex + "_shiny.png"},
            {"aspects": ["alpha_eyes"],
             "layers": [{"name": "alpha_eyes", "texture": tex + "_alpha.png", "emissive": True}]},
        ],
    }


def validate(geo, anim_doc, pose):
    g = geo["minecraft:geometry"][0]
    seen = set()
    for b in g["bones"]:
        assert b["name"] not in seen, "duplicate bone " + b["name"]
        if "parent" in b:
            assert b["parent"] in seen, "parent must come first: " + b["name"]
        seen.add(b["name"])
        for c in b.get("cubes", []):
            assert all(isinstance(v, int) for v in c["uv"]), b["name"]
            u, v = c["uv"]; dx, dy, dz = c["size"]
            assert u + 2 * (dx + dz) <= g["description"]["texture_width"] + 1e-6, b["name"]
            assert v + dz + dy <= g["description"]["texture_height"] + 1e-6, b["name"]
    locs = [k for b in g["bones"] for k in b.get("locators", {})]
    assert any("eye" in k for k in locs), "alpha eye locators missing"
    for an_name, an in anim_doc["animations"].items():
        for bn in an["bones"]:
            assert bn in seen, "%s animates unknown bone %s" % (an_name, bn)
        if an.get("loop") is True:
            assert an.get("animation_length", 0) > 0, an_name + " loops need animation_length"
    assert not anims.check_loops(anim_doc), anims.check_loops(anim_doc)
    assert pose["rootBone"] in seen
    names = set(k.split(".")[-1] for k in anim_doc["animations"])
    import re
    for expr in json.dumps(pose).split('"'):
        for grp, an in re.findall(r"q\.bedrock(?:_stateful|_primary|_quirk)?\('([a-z_]+)', '([a-z_]+)'", expr):
            if grp == NAME:
                assert an in names, "poser references missing animation " + an
    return len(seen)


def main():
    m = model_def.build()
    used = m.pack_uvs(256, 128)
    tex = paint.paint(m, {"normal": paint.PAL_NORMAL, "shiny": paint.PAL_SHINY, "alpha": paint.PAL_ALPHA})
    geo = m.to_geo_json(visible_bounds=(6, 4.5, (0, 1.5, 0)))
    anim_doc = anims.build_all(poses.sit_pose2(m), poses.sleep_pose(m))
    pose = poser()
    nb = validate(geo, anim_doc, pose)
    for p in (P_MODEL, P_ANIM, P_POSER, P_RES, P_TEX):
        os.makedirs(p, exist_ok=True)

    def dump(obj, path):
        with open(path, "w") as f:
            json.dump(obj, f, indent=2)
            f.write("\n")
    dump(geo, os.path.join(P_MODEL, NAME + ".geo.json"))
    dump(anim_doc, os.path.join(P_ANIM, NAME + ".animation.json"))
    dump(pose, os.path.join(P_POSER, NAME + ".json"))
    dump(resolver(), os.path.join(P_RES, "0_%s_base.json" % NAME))
    Image.fromarray(tex["normal"]).save(os.path.join(P_TEX, NAME + ".png"))
    Image.fromarray(tex["shiny"]).save(os.path.join(P_TEX, NAME + "_shiny.png"))
    Image.fromarray(tex["alpha"]).save(os.path.join(P_TEX, NAME + "_alpha.png"))
    cubes = sum(len(b.cubes) for b in m.bones)
    print("bones", nb, "cubes", cubes, "atlas rows used", used, "animations", len(anim_doc["animations"]))


if __name__ == "__main__":
    main()
