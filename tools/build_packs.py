"""
Builds the Windwave resource pack + data pack for Cobblemon 1.8.1 (Minecraft 1.21.1).

    python3 tools/build_packs.py

Inputs : source/bbmodel/*.bbmodel, tools/windwave_species.py,
         datapack/data/cobblemon/{moves,abilities}/*.js (hand written Showdown scripts)
Outputs: resourcepack/, datapack/ (generated parts), dist/*.zip
"""

import copy
import json
import os
import shutil
import sys
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from convert_bbmodel import Converter  # noqa: E402
from render_preview import load, chain, Pose, transform_point, render  # noqa: E402
import windwave_species as W  # noqa: E402

RP = os.path.join(ROOT, "resourcepack")
DP = os.path.join(ROOT, "datapack")
DIST = os.path.join(ROOT, "dist")
NS = "cobblemon"
MC_VERSION = "1.21.1"
PACK_VERSION = "1.0.0"
RP_FORMAT = 34
DP_FORMAT = 48


def write_json(path, data, indent=2):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=indent, ensure_ascii=False)
        fh.write("\n")


def folder(sp):
    return f"{sp['dex']:04d}_{sp['id']}"


# =============================================================================================== model tweaks
# Extra / corrected locators (positions in Blockbench space, same as the .bbmodel).
LOCATOR_FIXES = {
    # The eye locators were left at the pre-evolution's eye position when the model was scaled up.
    "avalott": {"eye1": [3.25, 37.75, -17.4], "eye2": [-3.25, 37.75, -17.4]},
    "cleaweed": {"eye1": [4.1, 38.0, -3.5], "eye2": [-4.1, 38.0, -3.5]},
}
EXTRA_LOCATORS = {
    # Alpha eye glow needs locators containing "eye".
    "eeveeon": [("iris_left", "eye2", [-5.5, 38.5, -35.4]), ("iris_right", "eye1", [5.5, 38.5, -35.4]),
                ("torso2", "seat_1", [0, 36.5, -1])],
    "cryptonix": [("head", "seat_1", [0, 33.5, -37]), ("segment1", "seat_2", [0, 24, -18])],
    "cleaweed": [("torso", "seat_1", [0, 26.5, 5])],
}

# Poser configuration ---------------------------------------------------------------------------
POSER = {
    "eeveeon": {
        "look": "q.look('head_ai', 1, 1, 50, -35, 45, -45)",
        "quirks": ["quirk_earflick", "quirk_tailfan", "quirk_stretch"],
        "portrait_anim": "pose",
        "run": True, "water": "simple",
    },
    "threiscue": {
        "look": "q.look('head_ai', 1, 1, 30, -30, 45, -45)",
        "quirks": ["quirk_swing", "quirk_shiver", "quirk_bob"],
        "portrait_anim": "ground_idle",
        "run": True, "water": "surface",
    },
    "cryptonix": {
        "look": "q.look('head', 0.6, 0.6, 25, -25, 30, -30)",
        "quirks": ["quirk_crosses", "quirk_look", "quirk_wail"],
        "portrait_anim": "ground_idle",
        "run": False, "water": None,
    },
    "avalott": {
        "look": None,
        "quirks": ["quirk_spin", "quirk_shake"],
        "portrait_anim": "ground_idle",
        "run": False, "water": "simple",
    },
    "cleaweed": {
        "look": "q.look('head', 0.8, 0.8, 30, -30, 40, -40)",
        "quirks": ["quirk_preen", "quirk_bubble"],
        "portrait_anim": "ground_idle",
        "run": False, "water": "simple",
    },
}

CRY_PITCH = {  # new cry sound events, built from the pre-evolution cries
    "eeveeon": ("cobblemon:pokemon/eevee/eevee_cry", 0.82),
    "threiscue": ("cobblemon:pokemon/eiscueice/eiscueice_cry", 0.78),
    "cryptonix": ("cobblemon:pokemon/onix/onix_cry", 0.72),
    "avalott": ("cobblemon:pokemon/bergmite/bergmite_cry", 0.74),
    "cleaweed": ("cobblemon:pokemon/skrelp/skrelp_cry", 0.8),
}


# =============================================================================================== resource pack

def posed_points(sp_id, points, anim="ground_idle"):
    data, groups, elements, parent, owner = load(os.path.join(ROOT, "source/bbmodel", sp_id + ".bbmodel"))
    pose = Pose(data, anim, 0.0)
    out = []
    for bone, pt in points:
        g = next(g for g in groups.values() if g["name"] == bone)
        out.append(transform_point(pt, {}, chain(g["uuid"], groups, parent), pose))
    return np.array(out)


def eye_points(sp_id):
    data, groups, elements, parent, owner = load(os.path.join(ROOT, "source/bbmodel", sp_id + ".bbmodel"))
    pts = []
    fixes = LOCATOR_FIXES.get(sp_id, {})
    for e in data["elements"]:
        if e.get("type") == "locator" and "eye" in e["name"]:
            pts.append((groups[owner[e["uuid"]]]["name"], fixes.get(e["name"], e["position"])))
    for bone, name, pos in EXTRA_LOCATORS.get(sp_id, []):
        if "eye" in name:
            pts.append((bone, pos))
    return pts


def framing(sp_id):
    """Portrait/profile numbers derived from the posed model (regression over Cobblemon's own posers)."""
    from render_preview import bounds
    mn, mx = bounds(os.path.join(ROOT, "source/bbmodel", sp_id + ".bbmodel"), "ground_idle", 0.0)
    size = (mx - mn) / 16.0
    eyes = posed_points(sp_id, eye_points(sp_id)).mean(axis=0) / 16.0
    ey, ez = eyes[1], eyes[2]
    head_scale = {"eeveeon": 1.25, "threiscue": 1.0, "cryptonix": 0.6, "avalott": 0.85, "cleaweed": 1.9}[sp_id]
    if sp_id == "threiscue":
        ey += 0.35  # frame the face together with the first ice cube
    s = head_scale
    ty = 0.7526 * s * ey - 0.2897 * s * ez - 1.401 * s + 1.0547
    tx = -0.1069 * s * ey + 0.2687 * s * ez + 0.0777 * s - 0.0556
    h, w, l = size[1], size[0], size[2]
    profile = round(2.0 / max(h, 0.8 * l, 0.8 * w), 2)
    profile_ty = {"eeveeon": 0.7, "threiscue": 1.0, "cryptonix": 1.1, "avalott": 1.0, "cleaweed": 0.95}[sp_id]
    return {
        "portraitScale": round(s, 2),
        "portraitTranslation": [round(float(tx), 2), round(float(ty), 2), 0],
        "profileScale": profile,
        "profileTranslation": [0, profile_ty, 0],
    }


def build_poser(sp, anim_names):
    i = sp["id"]
    cfg = POSER[i]
    sig = sp["signature"]
    look = [cfg["look"]] if cfg["look"] else []
    blink = f"q.bedrock_quirk('{i}', 'blink')"
    quirk = f"q.bedrock_quirk('{i}', q.array({', '.join(repr(q) for q in cfg['quirks'])}), 15, 45, 1)"
    poser = framing(i)
    poser["rootBone"] = i
    poser["animations"] = {
        "cry": f"q.bedrock_stateful('{i}', 'cry')",
        "recoil": f"q.bedrock_stateful('{i}', 'recoil')",
        "faint": f"q.bedrock_primary('{i}', 'faint', q.curve('one'))",
        "physical": f"q.bedrock_primary('{i}', 'physical', q.curve('symmetrical'))",
        "special": f"q.bedrock_primary('{i}', 'special', q.curve('symmetrical'))",
        "status": f"q.bedrock_primary('{i}', 'status', q.curve('symmetrical'))",
        sig: f"q.bedrock_primary('{i}', '{sig}', q.curve('symmetrical'))",
    }

    def bed(a):
        return f"q.bedrock('{i}', '{a}')"

    ridden = []  # riding reuses the regular walk/run/swim poses

    poses = {}
    poses["portrait"] = {"poseTypes": ["PORTRAIT", "PROFILE"], "isBattle": False,
                         "animations": [bed(cfg["portrait_anim"])], "quirks": [blink]}
    land_cond = {"isTouchingWater": False} if cfg["water"] else {}
    poses["battle-standing"] = dict({"poseTypes": ["STAND", "FLOAT"], "isBattle": True,
                                     "animations": look + [bed("battle_idle")], "quirks": [blink]})
    poses["standing"] = dict({"poseTypes": ["STAND", "NONE", "FLOAT"] if not cfg["water"] else ["STAND", "NONE"],
                              "isBattle": False}, **land_cond)
    poses["standing"]["animations"] = look + [bed("ground_idle")] + ridden
    poses["standing"]["quirks"] = [blink, quirk]
    walk_types = ["WALK", "SWIM"] if not cfg["water"] else ["WALK"]
    if cfg["run"]:
        poses["walking"] = dict({"poseTypes": walk_types, "condition": "!q.is_sprinting"}, **land_cond)
        poses["walking"]["animations"] = look + [bed("ground_walk")] + ridden
        poses["walking"]["quirks"] = [blink]
        poses["running"] = dict({"poseTypes": walk_types, "condition": "q.is_sprinting"}, **land_cond)
        poses["running"]["animations"] = look + [bed("ground_run")]
        poses["running"]["quirks"] = [blink]
    else:
        poses["walking"] = dict({"poseTypes": walk_types}, **land_cond)
        poses["walking"]["animations"] = look + [bed("ground_walk")] + ridden
        poses["walking"]["quirks"] = [blink]
    if cfg["water"] == "surface":
        poses["surface"] = {"poseTypes": ["FLOAT", "STAND", "NONE"], "isTouchingWater": True, "isUnderWater": False,
                            "animations": look + [bed("water_surface")], "quirks": [blink]}
        poses["underwater"] = {"poseTypes": ["FLOAT", "STAND", "NONE"], "isUnderWater": True,
                               "animations": look + [bed("water_idle")], "quirks": [blink]}
        poses["swim"] = {"poseTypes": ["SWIM", "WALK"], "isTouchingWater": True,
                         "animations": look + [bed("water_swim")], "quirks": [blink]}
    elif cfg["water"] == "simple":
        poses["float"] = {"poseTypes": ["FLOAT", "STAND", "NONE"], "isTouchingWater": True,
                          "animations": look + [bed("water_idle")] + ridden, "quirks": [blink]}
        poses["swim"] = {"poseTypes": ["SWIM", "WALK"], "isTouchingWater": True,
                         "animations": look + [bed("water_swim")] + ridden, "quirks": [blink]}
    poses["sleep"] = {"poseTypes": ["SLEEP"], "animations": [bed("sleep")],
                      "namedAnimations": {"cry": "q.bedrock_stateful('dummy', 'cry')"}}
    poser["poses"] = poses
    # sanity: every referenced animation exists
    import re
    text = json.dumps(poser)
    names = set(re.findall(r"q\.bedrock(?:_primary|_stateful|_quirk)?\('" + i + r"', '(\w+)'", text))
    for arr in re.findall(r"q\.array\(([^)]*)\)", text):
        names.update(re.findall(r"'(\w+)'", arr))
    missing = [n for n in names if f"animation.{i}.{n}" not in anim_names]
    if missing:
        raise ValueError(f"{i}: poser references missing animations {missing}")
    return poser


def build_resolver(sp):
    i, f = sp["id"], folder(sp)
    tex = f"{NS}:textures/pokemon/{f}/{i}"
    return {
        "species": f"{NS}:{i}",
        "order": 0,
        "variations": [
            {"aspects": [], "poser": f"{NS}:{i}", "model": f"{NS}:{i}.geo", "texture": tex + ".png", "layers": []},
            {"aspects": ["shiny"], "texture": tex + "_shiny.png"},
            {"aspects": ["alpha_eyes"], "layers": [{"name": "alpha_eyes", "texture": tex + "_alpha.png", "emissive": True}]},
        ],
    }


def build_models():
    sounds = {}
    for sp in W.SPECIES:
        i, f = sp["id"], folder(sp)
        conv = Converter(os.path.join(ROOT, "source/bbmodel", i + ".bbmodel"))
        # locator fixes
        for el in conv.data["elements"]:
            if el.get("type") == "locator" and el["name"] in LOCATOR_FIXES.get(i, {}):
                el["position"] = LOCATOR_FIXES[i][el["name"]]
        for bone, name, pos in EXTRA_LOCATORS.get(i, []):
            conv.group_by_name(bone)  # raises if missing
            conv.add_locator(bone, name, pos)
        geo = conv.geometry(i)
        anims = conv.animations()
        # cries: own sound event, and make sure every cry actually plays a sound
        cry = anims["animations"][f"animation.{i}.cry"]
        cry["sound_effects"] = {"0.05": {"effect": f"pokemon.{i}.cry"}}
        sounds[f"pokemon.{i}.cry"] = {"sounds": [{"name": CRY_PITCH[i][0], "volume": 0.8, "pitch": CRY_PITCH[i][1]}]}
        base = os.path.join(RP, "assets", NS)
        write_json(os.path.join(base, f"bedrock/pokemon/models/{f}/{i}.geo.json"), geo, indent=None)
        write_json(os.path.join(base, f"bedrock/pokemon/animations/{f}/{i}.animation.json"), anims, indent=None)
        write_json(os.path.join(base, f"bedrock/pokemon/posers/{f}/{i}.json"), build_poser(sp, set(anims["animations"])))
        write_json(os.path.join(base, f"bedrock/pokemon/resolvers/{f}/0_{i}_base.json"), build_resolver(sp))
        tex_dir = os.path.join(base, f"textures/pokemon/{f}")
        os.makedirs(tex_dir, exist_ok=True)
        for name, blob in conv.textures().items():
            with open(os.path.join(tex_dir, name), "wb") as fh:
                fh.write(blob)
        print(f"  model {i}: {len(geo['minecraft:geometry'][0]['bones'])} bones, {len(anims['animations'])} animations")
    write_json(os.path.join(RP, "assets", NS, "sounds.json"), sounds)


def build_lang():
    for code, key in (("en_us", "en"), ("ko_kr", "ko")):
        lang = {}
        for sp in W.SPECIES:
            i = sp["id"]
            lang[f"cobblemon.species.{i}.name"] = sp["names"][key]
            lang[f"cobblemon.species.{i}.desc"] = sp["dex_text"][key]
            lang[f"cobblemon.ui.pokedex.info.form.{i}"] = ""
        for move, text in W.MOVE_TEXT.items():
            lang[f"cobblemon.move.{move}"] = text[key][0]
            lang[f"cobblemon.move.{move}.desc"] = text[key][1]
        for ability, text in W.ABILITY_TEXT.items():
            lang[f"cobblemon.ability.{ability}"] = text[key][0]
            lang[f"cobblemon.ability.{ability}.desc"] = text[key][1]
        lang.update(W.EXTRA_LANG[key])
        write_json(os.path.join(RP, "assets", NS, "lang", code + ".json"), lang)


# --------------------------------------------------------------------------------------------- particles

def billboard(size, uv, facing="rotate_xyz"):
    return {"size": size, "facing_camera_mode": facing, "uv": uv}


UV_SPARKLE = {"texture_width": 8, "texture_height": 16,
              "flipbook": {"base_UV": [0, 0], "size_UV": [8, 8], "step_UV": [0, 8], "frames_per_second": 6, "max_frame": 2, "loop": True}}
UV_RING = {"texture_width": 448, "texture_height": 64,
           "flipbook": {"base_UV": [0, 0], "size_UV": [64, 64], "step_UV": [64, 0], "frames_per_second": 14, "max_frame": 7, "stretch_to_lifetime": True}}
UV_WISP = {"texture_width": 99, "texture_height": 13,
           "flipbook": {"base_UV": [0, 0], "size_UV": [9, 13], "step_UV": [9, 0], "frames_per_second": 12, "max_frame": 11, "loop": True}}
UV_ROCK = {"texture_width": 32, "texture_height": 192, "uv": [0, "math.round(v.particle_random_2*5)*32"], "uv_size": [32, 32]}
UV_LEAF = {"texture_width": 16, "texture_height": 64,
           "flipbook": {"base_UV": [0, 0], "size_UV": [16, 16], "step_UV": [0, 16], "frames_per_second": 12, "max_frame": 4, "loop": True}}
UV_ORB = {"texture_width": 45, "texture_height": 5,
          "flipbook": {"base_UV": [0, 0], "size_UV": [5, 5], "step_UV": [5, 0], "frames_per_second": 10, "max_frame": 9, "stretch_to_lifetime": True}}


def particle(identifier, texture, material, components, curves=None):
    eff = {"description": {"identifier": identifier,
                           "basic_render_parameters": {"material": material, "texture": texture}}}
    if curves:
        eff["curves"] = curves
    eff["components"] = components
    return {"format_version": "1.10.0", "particle_effect": eff}


SCALE_CURVE = {"variable.fade": {"type": "linear", "input": "v.particle_age", "horizontal_range": "v.particle_lifetime", "nodes": [1, 1, 0.6, 0]}}


def build_particles():
    out = os.path.join(RP, "assets", NS, "bedrock/particles/windwave")
    p = {}
    # Last Evolution: rainbow sparkles in every Eeveelution colour
    p["windwave_lastevolution_burst"] = particle(
        "cobblemon:windwave_lastevolution_burst", "textures/particles/generic/sparkle/sparkle", "particles_blend", {
            "minecraft:emitter_rate_instant": {"num_particles": "45*math.clamp(v.entity_size,1,2)"},
            "minecraft:emitter_lifetime_once": {"active_time": 0.2},
            "minecraft:emitter_shape_sphere": {"radius": 0.3, "surface_only": True, "direction": "outwards"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(0.8, 1.4)"},
            "minecraft:particle_initial_speed": "math.random(4, 8)*math.clamp(v.entity_size,1,3)",
            "minecraft:particle_motion_dynamic": {"linear_acceleration": [0, 1.5, 0], "linear_drag_coefficient": 3.2},
            "minecraft:particle_appearance_billboard": billboard(["0.28*v.fade", "0.28*v.fade"], UV_SPARKLE),
            "minecraft:particle_appearance_tinting": {"color": [
                "0.75+0.25*math.sin(v.particle_random_1*360)",
                "0.75+0.25*math.sin(v.particle_random_1*360+120)",
                "0.75+0.25*math.sin(v.particle_random_1*360+240)", 1]},
        }, SCALE_CURVE)
    p["windwave_lastevolution_charge"] = particle(
        "cobblemon:windwave_lastevolution_charge", "textures/particles/generic/sparkle/sparkle", "particles_blend", {
            "minecraft:emitter_rate_steady": {"spawn_rate": "8 + v.emitter_age * 30", "max_particles": 80},
            "minecraft:emitter_lifetime_once": {"active_time": 1.7},
            "minecraft:emitter_shape_sphere": {"radius": "1.4*math.clamp(v.entity_size,1,2)", "surface_only": True, "direction": "inwards"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": 0.5},
            "minecraft:particle_initial_speed": "2.8*math.clamp(v.entity_size,1,2)",
            "minecraft:particle_motion_dynamic": {},
            "minecraft:particle_appearance_billboard": billboard(["0.2*v.fade", "0.2*v.fade"], UV_SPARKLE),
            "minecraft:particle_appearance_tinting": {"color": [
                "0.75+0.25*math.sin(v.particle_random_1*360)",
                "0.75+0.25*math.sin(v.particle_random_1*360+120)",
                "0.75+0.25*math.sin(v.particle_random_1*360+240)", 1]},
        }, SCALE_CURVE)
    p["windwave_lastevolution_ring"] = particle(
        "cobblemon:windwave_lastevolution_ring", "textures/particles/generic/ring/giantring_white", "particles_alpha", {
            "minecraft:emitter_rate_instant": {"num_particles": 1},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_point": {},
            "minecraft:particle_lifetime_expression": {"max_lifetime": 0.6},
            "minecraft:particle_initial_speed": 0,
            "minecraft:particle_motion_dynamic": {},
            "minecraft:particle_appearance_billboard": billboard(
                ["(0.5+v.particle_age*6)*math.clamp(v.entity_size,1,3)", "(0.5+v.particle_age*6)*math.clamp(v.entity_size,1,3)"], UV_RING),
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "v.particle_age / v.particle_lifetime",
                                                                "gradient": {"0.0": "#FFFFF6D8", "0.5": "#FFFFD27A", "1.0": "#00C98B4B"}}},
        })
    # Grave Uprising: rubble bursting out of the ground + teal crypt spirits
    p["windwave_grave_rubble"] = particle(
        "cobblemon:windwave_grave_rubble", "textures/particles/generic/large_rock", "particles_alpha", {
            "minecraft:emitter_rate_instant": {"num_particles": "14*math.clamp(v.entity_size,1,2)"},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_disc": {"radius": "0.9*math.clamp(v.entity_size,1,3)", "plane_normal": "y",
                                             "direction": ["(v.particle_random_1-0.5)*0.6", 1, "(v.particle_random_3-0.5)*0.6"]},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(0.9, 1.3)"},
            "minecraft:particle_initial_spin": {"rotation": "math.random(0, 360)", "rotation_rate": "math.random(-180, 180)"},
            "minecraft:particle_initial_speed": "math.random(6, 10)",
            "minecraft:particle_motion_dynamic": {"linear_acceleration": [0, -22, 0]},
            "minecraft:particle_motion_collision": {"coefficient_of_restitution": 0.2, "collision_drag": 4, "collision_radius": 0.1},
            "minecraft:particle_appearance_billboard": billboard(["0.35*v.fade", "0.35*v.fade"], UV_ROCK),
            "minecraft:particle_appearance_lighting": {},
        }, SCALE_CURVE)
    p["windwave_grave_spirits"] = particle(
        "cobblemon:windwave_grave_spirits", "textures/particles/generic/fire/wisp", "particles_add", {
            "minecraft:emitter_rate_steady": {"spawn_rate": 30, "max_particles": 60},
            "minecraft:emitter_lifetime_once": {"active_time": 0.9},
            "minecraft:emitter_shape_disc": {"radius": "0.8*math.clamp(v.entity_size,1,3)", "plane_normal": "y", "direction": [0, 1, 0]},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(0.7, 1.2)"},
            "minecraft:particle_initial_speed": "math.random(1.5, 3)",
            "minecraft:particle_motion_dynamic": {"linear_acceleration": ["math.sin(v.particle_age*540)*2", 2, "math.cos(v.particle_age*540)*2"], "linear_drag_coefficient": 1.5},
            "minecraft:particle_appearance_billboard": billboard(["0.3*v.fade", "0.43*v.fade"], UV_WISP),
            "minecraft:particle_appearance_tinting": {"color": [0.45, 1, 0.9, 0.9]},
        }, SCALE_CURVE)
    # Frostsaw: icy slash arcs spinning around the target
    p["windwave_frostsaw_slash"] = particle(
        "cobblemon:windwave_frostsaw_slash", "textures/particles/generic/ring/giantring_white", "particles_add", {
            "minecraft:emitter_rate_steady": {"spawn_rate": 10, "max_particles": 12},
            "minecraft:emitter_lifetime_once": {"active_time": 0.9},
            "minecraft:emitter_shape_point": {},
            "minecraft:particle_lifetime_expression": {"max_lifetime": 0.35},
            "minecraft:particle_initial_spin": {"rotation": "math.random(0, 360)", "rotation_rate": 900},
            "minecraft:particle_initial_speed": 0,
            "minecraft:particle_motion_dynamic": {},
            "minecraft:particle_appearance_billboard": billboard(
                ["(1.2+v.particle_age*3)*math.clamp(v.entity_size,1,3)", "(0.35+v.particle_age)*math.clamp(v.entity_size,1,3)"], UV_RING),
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "v.particle_age / v.particle_lifetime",
                                                                "gradient": {"0.0": "#FFFFFFFF", "0.4": "#FFB8F2FF", "1.0": "#0066CCFF"}}},
        })
    p["windwave_frostsaw_frost"] = particle(
        "cobblemon:windwave_frostsaw_frost", "textures/particles/generic/orb/xsfadeorb", "particles_blend", {
            "minecraft:emitter_rate_instant": {"num_particles": "40*math.clamp(v.entity_size,1,2)"},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_disc": {"radius": 0.2, "plane_normal": "y", "direction": "outwards"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(0.6, 1.0)"},
            "minecraft:particle_initial_speed": "math.random(6, 11)*math.clamp(v.entity_size,1,3)",
            "minecraft:particle_motion_dynamic": {"linear_acceleration": [0, 0.5, 0], "linear_drag_coefficient": 4},
            "minecraft:particle_appearance_billboard": billboard(["0.22", "0.22"], UV_ORB),
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "v.particle_age / v.particle_lifetime",
                                                                "gradient": {"0.0": "#FFFFFFFF", "0.3": "#FFC4F0FF", "1.0": "#0092BCFF"}}},
        })
    # Cleansing Net: leaves swirl in from all sides and close around the target like a net
    p["windwave_cleansing_net"] = particle(
        "cobblemon:windwave_cleansing_net", "textures/particles/generic/grass/leaf", "particles_alpha", {
            "minecraft:emitter_rate_steady": {"spawn_rate": 40, "max_particles": 60},
            "minecraft:emitter_lifetime_once": {"active_time": 1.2},
            "minecraft:emitter_shape_sphere": {"radius": "1.6*math.clamp(v.entity_size,1,3)", "surface_only": True, "direction": "inwards"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": 0.75},
            "minecraft:particle_initial_spin": {"rotation": "math.random(0, 360)", "rotation_rate": 360},
            "minecraft:particle_initial_speed": "2*math.clamp(v.entity_size,1,3)",
            "minecraft:particle_motion_dynamic": {"linear_drag_coefficient": 0.5},
            "minecraft:particle_appearance_billboard": billboard(["0.26*v.fade", "0.26*v.fade"], UV_LEAF),
            "minecraft:particle_appearance_tinting": {"color": [0.55, 1, 0.45, 1]},
        }, SCALE_CURVE)
    for name, data in p.items():
        write_json(os.path.join(out, name + ".particle.json"), data)


def pack_meta(desc):
    return {"pack": {"pack_format": RP_FORMAT, "description": desc}}


def build_resourcepack():
    if os.path.isdir(RP):
        shutil.rmtree(RP)
    os.makedirs(RP)
    build_models()
    build_lang()
    build_particles()
    write_json(os.path.join(RP, "pack.mcmeta"), {"pack": {
        "pack_format": RP_FORMAT,
        "supported_formats": [34, 34],
        "description": f"§bWindwave§r Pokémon v{PACK_VERSION} §7(Cobblemon 1.8.1)§r\n이브이온·트리큐보·크립토닉스·아발롯·클리위드"}})
    render(os.path.join(ROOT, "source/bbmodel/eeveeon.bbmodel"), os.path.join(RP, "pack.png"), yaw=35, size=128, anim="ground_idle")


# =============================================================================================== data pack

def species_json(sp):
    s = copy.deepcopy(sp["species"])
    out = {
        "implemented": True,
        "nationalPokedexNumber": sp["dex"],
        "name": sp["names"]["en"],
    }
    keys_first = ["primaryType", "secondaryType", "maleRatio", "height", "weight"]
    for k in keys_first:
        if k in s:
            out[k] = s.pop(k)
    out["pokedex"] = [f"cobblemon.species.{sp['id']}.desc"]
    out["labels"] = ["custom", "windwave", "gen9"]
    out["aspects"] = []
    for k in ["abilities", "eggGroups", "baseStats", "evYield", "baseExperienceYield", "experienceGroup", "catchRate",
              "eggCycles", "baseFriendship", "baseScale", "hitbox", "drops"]:
        out[k] = s.pop(k)
    out["moves"] = sp["moves"]
    out["preEvolution"] = sp["pre_evolution"]
    out["evolutions"] = []
    out.update(s)  # riding, behaviour, lightingData, ai ...
    return out


def species_addition(sp):
    return {"target": f"cobblemon:{sp['pre_evolution']}", "evolutions": sp["evolutions"]}


def spawn(id_, pokemon, bucket, level, weight, condition, position="grounded", presets=("natural",), **extra):
    d = {"id": id_, "pokemon": pokemon}
    if presets:
        d["presets"] = list(presets)
    d.update({"type": "pokemon", "spawnablePositionType": position, "bucket": bucket, "level": level, "weight": weight,
              "condition": condition})
    d.update(extra)
    return d


LURE = {"weightMultipliers": [{"multiplier": 3.0, "condition": {"minLureLevel": 2, "maxLureLevel": 2}},
                              {"multiplier": 5.0, "condition": {"minLureLevel": 3}}]}
SNACK = {"weightMultiplier": {"multiplier": 1.5, "condition": {"isPokeSnack": True}}}
DAYLIGHT = {"minSkyLight": 8, "maxSkyLight": 15}


def herd(id_, presets, position, level, weight, condition, leader, followers, max_size=6):
    hp = [{"pokemon": leader, "weight": 30.0, "levelRange": "1-100", "maxTimes": 1, "isLeader": True, "isFollower": False}]
    for pokemon, w, lvl, times in followers:
        hp.append({"pokemon": pokemon, "weight": w, "levelRange": lvl, "levelRangeOffset": "-3-3", "maxTimes": times,
                   "isLeader": False, "isFollower": True})
    return {"id": id_, "presets": list(presets), "type": "pokemon-herd", "bucket": "boss", "spawnablePositionType": position,
            "maxHerdSize": max_size, "levelRange": level, "weight": weight, "condition": condition, "herdablePokemon": hp}


def spawn_files():
    pools = {
        "eeveeon": [
            spawn("eeveeon-1", "eeveeon", "ultra-rare", "30-60", 4.0,
                  dict(DAYLIGHT, biomes=["#cobblemon:is_temperate", "#cobblemon:is_floral", "#cobblemon:is_plains", "#cobblemon:is_magical"]),
                  anticondition={"biomes": ["#cobblemon:is_ocean"]}, **SNACK),
        ],
        "threiscue": [
            spawn("threiscue-1", "threiscue", "rare", "40-60", 6.0,
                  dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean", "#cobblemon:is_glacial"]), **SNACK),
            spawn("threiscue-2", "threiscue", "rare", "40-60", 4.0,
                  dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean"]), position="surface", presets=("water",)),
            spawn("threiscue-3", "threiscue", "rare", "40-60", 3.0,
                  dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean", "#cobblemon:is_glacial", "#cobblemon:is_tundra"]),
                  position="fishing", presets=(), **LURE),
        ],
        "cryptonix": [
            spawn("cryptonix-1", "cryptonix", "ultra-rare", "40-65", 3.0,
                  {"maxSkyLight": 7, "biomes": ["#cobblemon:is_deep_dark"]}),
            spawn("cryptonix-2", "cryptonix", "rare", "40-65", 8.0, {"canSeeSky": False}, presets=("ancient_city",)),
            spawn("cryptonix-3", "cryptonix", "ultra-rare", "40-65", 2.0,
                  {"timeRange": "night", "biomes": ["#cobblemon:is_spooky"]}),
        ],
        "avalott": [
            spawn("avalott-1", "avalott", "rare", "37-55", 5.0,
                  dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean", "#cobblemon:is_glacial"]), **SNACK),
            spawn("avalott-2", "avalott", "rare", "37-55", 4.0,
                  dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean"]), position="surface", presets=("water",)),
        ],
        "cleaweed": [
            spawn("cleaweed-1", "cleaweed", "rare", "40-60", 5.0,
                  {"biomes": ["#cobblemon:is_ocean"], "neededNearbyBlocks": ["minecraft:kelp_plant", "minecraft:seagrass", "minecraft:tall_seagrass"]},
                  position="submerged", presets=("water",)),
            spawn("cleaweed-2", "cleaweed", "rare", "40-60", 3.0,
                  {"biomes": ["#cobblemon:is_freshwater", "#cobblemon:is_swamp"]}, position="submerged", presets=("water",)),
            spawn("cleaweed-3", "cleaweed", "rare", "40-60", 6.0,
                  {"biomes": ["#cobblemon:is_ocean", "#cobblemon:is_coast", "#cobblemon:is_freshwater", "#cobblemon:is_swamp"]},
                  position="fishing", presets=(), **LURE),
        ],
    }
    herds = {
        "eeveeon": [herd("eeveeon-alpha-1", ["natural"], "grounded", "30-100", 10.0,
                         dict(DAYLIGHT, biomes=["#cobblemon:is_temperate", "#cobblemon:is_floral", "#cobblemon:is_plains"]),
                         "eeveeon held_item=cobblemon:normal_gem alpha=true",
                         [("eevee", 90.0, "8-30", 5), ("eeveeon", 10.0, "30-49", 1)])],
        "threiscue": [herd("threiscue-alpha-1", ["natural"], "grounded", "40-100", 20.0,
                           dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean", "#cobblemon:is_glacial"]),
                           "threiscue held_item=cobblemon:ice_gem alpha=true",
                           [("eiscue", 80.0, "22-47", 6)], max_size=7)],
        "cryptonix": [herd("cryptonix-alpha-1", ["ancient_city"], "grounded", "45-100", 25.0, {"canSeeSky": False},
                           "cryptonix held_item=cobblemon:ghost_gem alpha=true",
                           [("onix", 80.0, "14-39", 3)], max_size=4)],
        "avalott": [herd("avalott-alpha-1", ["natural"], "grounded", "37-100", 20.0,
                         dict(DAYLIGHT, biomes=["#cobblemon:is_frozen_ocean", "#cobblemon:is_glacial"]),
                         "avalott held_item=cobblemon:steel_gem alpha=true",
                         [("bergmite", 80.0, "8-27", 6), ("avalugg", 20.0, "39-47", 1)], max_size=8)],
        "cleaweed": [herd("cleaweed-alpha-1", ["water"], "submerged", "40-100", 20.0,
                          {"biomes": ["#cobblemon:is_ocean"]},
                          "cleaweed held_item=cobblemon:water_gem alpha=true",
                          [("skrelp", 80.0, "7-32", 6)], max_size=7)],
    }
    return pools, herds


ACTION_EFFECTS = {
    "lastevolution": [
        {"type": "add_holds", "holds": ["effects"]},
        {"type": "entity_particles", "effect": "cobblemon:windwave_lastevolution_charge", "locators": ["middle", "root"]},
        {"type": "entity_sound", "sound": "cobblemon:move.swordsdance.actor"},
        {"type": "animation", "animation": ["lastevolution", "special"], "delay": 1.85},
        {"type": "entity_particles", "effect": "cobblemon:evo_sparkleburst", "locators": ["middle", "root"]},
        {"type": "entity_sound", "sound": "cobblemon:move.dracometeor.actor_2"},
        {"type": "pause", "pause": 0.25},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:windwave_lastevolution_ring", "locators": ["middle", "target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:windwave_lastevolution_burst", "locators": ["target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:impact_normal", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:impact.normal"},
        {"type": "remove_holds", "holds": ["effects"]},
        {"type": "pause", "pause": 1.5},
    ],
    "triplefreezebeam": [
        {"type": "add_holds", "holds": ["effects"]},
        {"type": "animation", "animation": ["triplefreezebeam", "special"], "delay": 1.55},
        {"type": "entity_particles", "effect": "cobblemon:icebeam_actorpilot", "locators": ["beam3", "special", "target"], "targetLocators": ["target"]},
        {"type": "entity_sound", "sound": "cobblemon:move.icebeam.actor"},
        {"type": "pause", "pause": 0.4},
        {"type": "entity_particles", "effect": "cobblemon:icebeam_actorpilot", "locators": ["beam2", "special", "target"], "targetLocators": ["target"]},
        {"type": "pause", "pause": 0.4},
        {"type": "entity_particles", "effect": "cobblemon:icebeam_actorpilot", "locators": ["beam1", "special", "target"], "targetLocators": ["target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:icebeam_target", "locators": ["target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:icebeam_targetbuild", "locators": ["middle"]},
        {"type": "pause", "pause": 0.3},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:move.icebeam.target_1"},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:icebeam_targetburst", "locators": ["target"]},
        {"type": "remove_holds", "holds": ["effects"]},
        {"type": "pause", "pause": 0.25},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:icebeam_targetfrost", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:move.icebeam.target_2"},
        {"type": "pause", "pause": 1.5},
    ],
    "graveuprising": [
        {"type": "add_holds", "holds": ["effects"]},
        {"type": "animation", "animation": ["graveuprising", "physical"], "delay": 0.8},
        {"type": "entity_sound", "sound": "cobblemon:move.shadowball.actor"},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:windwave_grave_rubble", "locators": ["root"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:windwave_grave_spirits", "locators": ["root"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:impact.rock"},
        {"type": "pause", "pause": 0.35},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:shadowball_targetimpact", "locators": ["target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:impact_ghost", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:move.shadowball.target"},
        {"type": "remove_holds", "holds": ["effects"]},
        {"type": "pause", "pause": 1.8},
    ],
    "frostsaw": [
        {"type": "add_holds", "holds": ["effects"]},
        {"type": "animation", "animation": ["frostsaw", "physical"], "delay": 1.2},
        {"type": "entity_sound", "sound": "cobblemon:move.iceshard.actor_1"},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:windwave_frostsaw_slash", "locators": ["middle", "target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:impact_ice", "locators": ["target"]},
        {"type": "pause", "pause": 0.3},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:icebeam_targetburst", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:move.iceshard.target"},
        {"type": "pause", "pause": 0.25},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:impact_steel", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:impact.steel"},
        {"type": "remove_holds", "holds": ["effects"]},
        {"type": "pause", "pause": 1.2},
        {"type": "entity_particles", "effect": "cobblemon:windwave_frostsaw_frost", "locators": ["root"]},
        {"type": "pause", "pause": 0.8},
    ],
    "cleansingnet": [
        {"type": "add_holds", "holds": ["effects"]},
        {"type": "animation", "animation": ["cleansingnet", "special"], "delay": 0.5},
        {"type": "entity_sound", "sound": "cobblemon:move.leafstorm.actor"},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:windwave_cleansing_net", "locators": ["middle", "target"]},
        {"type": "pause", "pause": 1.0},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:bubble_targetpop", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:move.bubble.target"},
        {"type": "pause", "pause": 0.8},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:waterpulse_target", "locators": ["target"]},
        {"type": "entity_particles", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "effect": "cobblemon:impact_water", "locators": ["target"]},
        {"type": "entity_sound", "entityCondition": "q.entity.is_user == false && q.missed(q.entity.uuid) == false",
         "sound": "cobblemon:move.waterpulse.target"},
        {"type": "remove_holds", "holds": ["effects"]},
        {"type": "pause", "pause": 1.2},
    ],
}

def habitat_spawn(species, bucket, level, weight, phases, position="grounded", **extra):
    d = {"species": species, "bucket": bucket, "spawnablePositionType": position, "weight": weight, "levelRange": level,
         "phases": phases}
    d.update(extra)
    return d


# Habitat Block pool (Cobblemon 1.8): one family per phase, the evolution shows up as the rare spawn.
HABITAT_POOL = {
    "name": "cobblemon.habitat.windwave_sanctuary.name",
    "type": "cobblemon:natural",
    "spawns": [
        habitat_spawn("Eevee", "common", "5-30", 8.0, "1"),
        habitat_spawn("Eeveeon", "rare", "30-50", 1.5, "1"),
        habitat_spawn("Eiscue", "common", "22-45", 8.0, "2"),
        habitat_spawn("Threiscue", "rare", "40-55", 1.5, "2"),
        habitat_spawn("Onix", "common", "14-39", 8.0, "3"),
        habitat_spawn("Cryptonix", "rare", "40-60", 1.5, "3", timeRange="night"),
        habitat_spawn("Bergmite", "common", "8-30", 8.0, "4"),
        habitat_spawn("Frigibax", "uncommon", "8-30", 3.0, "4"),
        habitat_spawn("Avalott", "rare", "37-55", 1.5, "4"),
        habitat_spawn("Skrelp", "common", "7-32", 6.0, "5"),
        habitat_spawn("Trubbish", "uncommon", "10-30", 3.0, "5"),
        habitat_spawn("Cleaweed", "rare", "40-55", 1.5, "5"),
        habitat_spawn("Eeveeon", "ultra-rare", "50-70", 1.0, "6", modifiers="alpha=true held_item=cobblemon:normal_gem"),
        habitat_spawn("Eevee", "common", "20-40", 6.0, "6"),
    ],
}

TM_RECIPES = {
    "lastevolution": ("normal", [("cobblemon:normal_gem", 3), ("cobblemon:eviolite", 1)]),
    "triplefreezebeam": ("ice", [("cobblemon:ice_gem", 3), ("cobblemon:never_melt_ice", 1)]),
    "graveuprising": ("ghost", [("cobblemon:ghost_gem", 3), ("cobblemon:spell_tag", 1)]),
    "frostsaw": ("ice", [("cobblemon:ice_gem", 2), ("cobblemon:steel_gem", 2)]),
    "cleansingnet": ("water", [("cobblemon:water_gem", 3), ("cobblemon:miracle_seed", 1)]),
}


def build_datapack():
    data = os.path.join(DP, "data", NS)
    for sub in ["species", "species_additions", "spawn_pool_world", "dex_entries", "dexes", "dex_additions", "tms", "action_effects",
                "habitat_pools"]:
        p = os.path.join(data, sub)
        if os.path.isdir(p):
            shutil.rmtree(p)
    for sp in W.SPECIES:
        i = sp["id"]
        write_json(os.path.join(data, "species/windwave", i + ".json"), species_json(sp))
        write_json(os.path.join(data, "species_additions/windwave", f"{sp['pre_evolution']}_to_{i}.json"), species_addition(sp))
        write_json(os.path.join(data, "dex_entries/pokemon/windwave", i + ".json"), {
            "id": f"cobblemon:{i}", "speciesId": f"cobblemon:{i}", "displayAspects": [], "conditionAspects": [],
            "forms": [{"displayForm": "Normal", "unlockForms": ["Normal"]}], "variations": []})
    pools, herds = spawn_files()
    for sp in W.SPECIES:
        i = sp["id"]
        write_json(os.path.join(data, "spawn_pool_world/windwave", f"{folder(sp)}.json"),
                   {"enabled": True, "neededInstalledMods": [], "neededUninstalledMods": [], "spawns": pools[i]})
        write_json(os.path.join(data, "spawn_pool_world/windwave/herds", f"{folder(sp)}_alpha.json"),
                   {"neededInstalledMods": [], "neededUninstalledMods": [], "spawns": herds[i]})
    write_json(os.path.join(data, "dexes", "windwave.json"), {
        "type": "cobblemon:simple_pokedex_def", "id": "cobblemon:windwave", "sortOrder": 12,
        "entries": [f"cobblemon:{sp['id']}" for sp in W.SPECIES]})
    write_json(os.path.join(data, "dex_additions", "windwave_national.json"),
               {"dexId": "cobblemon:national", "entries": ["cobblemon:windwave"]})
    for move, (type_, recipe) in TM_RECIPES.items():
        write_json(os.path.join(data, "tms", move + ".json"), {
            "moveName": move, "obtainMethods": [{"variant": "cobblemon:unlockable"}], "type": type_,
            "recipe": [{"item": it, "count": c} for it, c in recipe]})
    for move, timeline in ACTION_EFFECTS.items():
        write_json(os.path.join(data, "action_effects/moves", move + ".json"), {"timeline": timeline})
    write_json(os.path.join(data, "habitat_pools", "windwave_sanctuary.json"), HABITAT_POOL)
    write_json(os.path.join(DP, "pack.mcmeta"), {"pack": {
        "pack_format": DP_FORMAT,
        "supported_formats": [48, 48],
        "description": f"§bWindwave§r Pokémon v{PACK_VERSION} §7(Cobblemon 1.8.1)§r\n종·진화·전용기·스폰·도감·TM"}})
    shutil.copy(os.path.join(RP, "pack.png"), os.path.join(DP, "pack.png"))


# =============================================================================================== zips

def zip_dir(src, dst):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(src):
            for f in sorted(files):
                full = os.path.join(base, f)
                rel = os.path.relpath(full, src).replace(os.sep, "/")
                info = zipfile.ZipInfo(rel, date_time=(2026, 10, 2, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                with open(full, "rb") as fh:
                    z.writestr(info, fh.read())


def main():
    print("Building resource pack...")
    build_resourcepack()
    print("Building data pack...")
    build_datapack()
    rp_zip = os.path.join(DIST, f"Windwave-ResourcePack-{PACK_VERSION}-cobblemon-1.8.1.zip")
    dp_zip = os.path.join(DIST, f"Windwave-DataPack-{PACK_VERSION}-cobblemon-1.8.1.zip")
    zip_dir(RP, rp_zip)
    zip_dir(DP, dp_zip)
    print("Wrote", os.path.relpath(rp_zip, ROOT), os.path.getsize(rp_zip), "bytes")
    print("Wrote", os.path.relpath(dp_zip, ROOT), os.path.getsize(dp_zip), "bytes")


if __name__ == "__main__":
    main()
