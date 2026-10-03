"""Houndstone (#972) for Cobblemon 1.8.1 - model and textures.

Skeletal ghost dog: a skull-like head with nostril holes and a huge, rocky
lower jaw hanging wide open, a carved tombstone growing from the top of its
head, a shaggy fur mantle (lavender on top, white strands hanging to the
ground), a fur ruff around the neck, bony legs with claws and a bony tail.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from cobblegen import geom, blob, paint  # noqa: E402
from greavard import zigzag, _streaks, _mirror  # noqa: E402

NAME = "houndstone"
DEX = "0972_houndstone"
PREVIEW_SIZE = (460, 460)
PREVIEW_SHADOW = (12, 16)

EYE_X = 3.0
EYE_Y = 15.5


def build_model():
    m = geom.Model(NAME, 256, 128)
    m.visible_bounds = (3.5, 3, (0, 1.25, 0))
    root = m.bone(NAME, None, [0, 0, 0])
    root.locator("root", [0, 0, 0])
    m.bone("locator_top", NAME, [0, 0, 0]).locator("top", [0, 31, -12])
    m.bone("body", NAME, [0, 9, 4])

    # ------------------------------------------------------------ fur mantle
    torso = m.bone("torso", "body", [0, 9, 4])
    for (y0, y1, rings) in (
            (4, 12, [(18, -4.0, 16.0), (16, -5.0, 17.0), (14, -5.5, 17.5)]),
            (12, 16, [(17, -3.0, 15.0), (15, -4.0, 16.0), (12, -4.5, 16.5)]),
            (16, 18, [(14, -1.0, 13.0), (11, -2.0, 14.0)]),
            (18, 19, [(9, 1.0, 11.0)])):
        for (w, z0, z1) in rings:
            torso.add([-w / 2.0, y0, z0], [w, y1 - y0, z1 - z0], tag="mantle")
    # hanging strands around the hem
    hem_l = torso.add([9.05, 2.4, -3.5], [0, 6, 19], tag="hem")
    _mirror(torso, [hem_l])
    torso.add([-8, 2.4, 17.55], [16, 6, 0], tag="hem_back")

    # ruff around the neck + long beard strands in front of the forelegs
    collar = m.bone("collar", "torso", [0, 14, -6])
    collar.add([-8, 9, -9], [16, 7, 6], tag="collar")
    collar.add([-7, 16, -8], [14, 1, 5], tag="collar")
    collar.add([-7.5, 2.6, -9.05], [15, 8, 0], tag="beard")
    beard_side = collar.add([8.05, 3.0, -9], [0, 8, 5], tag="beard_side")
    _mirror(collar, [beard_side])

    # ------------------------------------------------------------------ tail
    tail_specs = [(4, -38, 2), (4, 22, 2), (3, 18, 1)]
    parent = "torso"
    y, z = 17.0, 14.5
    for i, (ln, rx, w) in enumerate(tail_specs):
        name = "tail" if i == 0 else "tail%d" % (i + 1)
        b = m.bone(name, parent, [0, y, z], [rx, 0, 0])
        c = b.add([-w / 2.0, y, z - w / 2.0], [w, ln, w], tag="tail_bone", inflate=-0.25 if w > 1 else 0.05)
        c.seg = i
        if i < 2:
            b.add([-1, y + ln - 1, z - 1], [2, 2, 2], tag="tail_joint", inflate=-0.1)
        parent = name
        y += ln

    # ------------------------------------------------------------------ legs
    def leg(name, x, z, toe_dir=-1):
        b = m.bone(name, "body", [x, 9, z])
        b.add([x - 1, 1, z - 1], [2, 8, 2], tag="leg_bone", inflate=-0.2)
        b.add([x - 1.5, 3.0, z - 1.5], [3, 2, 3], tag="leg_joint", inflate=-0.15)
        b.add([x - 1.5, 0, z - 1.5], [3, 1, 3], tag="paw")
        toes = []
        for i in range(3):
            toes.append(b.add([x - 1.5 + i, 0, z - 4.5], [1, 1, 3], tag="claw", inflate=-0.1))
        return b

    for (nm, x, z) in (("leg_front_left", 5.5, -6.5), ("leg_back_left", 6.0, 12.5)):
        lb = leg(nm, x, z)
        rb = m.bone(nm.replace("left", "right"), "body", [-x, 9, z])
        _mirror(rb, list(lb.cubes))

    # ------------------------------------------------------------------ head
    neck = m.bone("neck", "torso", [0, 12, -7])
    head = m.bone("head", "neck", [0, 11, -9])
    for (y0, y1, rings) in (
            (10, 15, [(10, -19.0, -8.0), (8, -20.0, -8.0)]),
            (15, 16, [(8, -17.0, -9.0), (6, -18.0, -9.0)])):
        for (w, z0, z1) in rings:
            head.add([-w / 2.0, y0, z0], [w, y1 - y0, z1 - z0], tag="skull")
    head.add([-4.5, 8.4, -20.06], [9, 2, 0], tag="teeth_top")
    side_t = head.add([5.04, 8.4, -19], [0, 2, 10], tag="teeth_top_side")
    _mirror(head, [side_t])
    head.add([-4, 7, -10.5], [8, 3, 2], tag="throat")
    # eyes are hidden; only the alpha glow shows two slits above the snout
    eyes = m.bone("eyes", "head", [0, EYE_Y, -17.06])
    el = m.bone("eye_left", "eyes", [EYE_X, EYE_Y, -17.06])
    ec = el.add([EYE_X - 1, EYE_Y - 0.5, -17.06], [2, 1, 0], tag="eye")
    el.locator("eye2", [EYE_X, EYE_Y, -17.3])
    er = m.bone("eye_right", "eyes", [-EYE_X, EYE_Y, -17.06])
    _mirror(er, [ec])
    er.locator("eye1", [-EYE_X, EYE_Y, -17.3])

    jaw = m.bone("jaw", "head", [0, 7, -10])
    for (y0, y1, rings) in (
            (2, 7, [(13, -21.0, -8.0), (11, -22.0, -9.0), (9, -22.5, -9.5)]),
            (1, 2, [(10, -20.0, -11.0)])):
        for (w, z0, z1) in rings:
            jaw.add([-w / 2.0, y0, z0], [w, y1 - y0, z1 - z0], tag="jaw")
    jaw.add([-4.5, 7.03, -21.0], [9, 0, 11], tag="mouth_floor")
    jaw.add([-5, 6.0, -22.56], [10, 2, 0], tag="teeth_bottom")
    side_b = jaw.add([5.55, 6.0, -20.5], [0, 2, 11], tag="teeth_bottom_side")
    _mirror(jaw, [side_b])
    # lumpy rocks on the jaw
    lump = geom.rounded_blob(jaw, (4.6, 3.6, -18.5), (4, 4, 5), "jaw", steps=0.5)
    _mirror(jaw, lump)

    # tombstone growing from the top of the head
    stone = m.bone("tombstone", "head", [0, 15, -12], [-8, 0, 0])
    stone.add([-2, 15, -13], [4, 5, 2], tag="stone_post")
    stone.add([-3.5, 20, -13.5], [7, 9, 3], tag="stone")
    stone.add([-2.5, 29, -13.5], [5, 1, 3], tag="stone")
    stone.add([-1.5, 30, -13.5], [3, 1, 3], tag="stone_top", inflate=-0.05)
    m.pack()
    return m


# --------------------------------------------------------------- palettes
PALETTES = {
    "normal": {
        "fur": paint.ramp("#7e7f8c", "#8f909c", "#a1a2ad", "#b3b4be", "#c3c4cd", "#d1d2da", "#dddee4",
                          "#e7e8ec", "#f0f1f4", "#f8f8fa"),
        "cap": paint.ramp("#5f5a9a", "#6d68aa", "#7c77b9", "#8b86c6", "#9a95d0", "#a9a4d9", "#b8b4e1",
                          "#c7c4e9"),
    },
    "shiny": {
        "fur": paint.ramp("#5e573f", "#6e6649", "#7f7755", "#8f8762", "#9f976f", "#afa87e", "#beb88f",
                          "#ccc6a1", "#dad5b5", "#e7e3cc"),
        "cap": paint.ramp("#4c412e", "#5a4d36", "#685a40", "#776849", "#867654", "#94835f", "#a1916c",
                          "#ae9e7a"),
    },
}
BONE = paint.ramp("#7c7c84", "#8f8f97", "#a2a2aa", "#b4b4bb", "#c5c5cb", "#d4d4d9", "#e1e1e5", "#ececef", "#f6f6f8")
STONE = paint.ramp("#5d5e66", "#6c6d75", "#7b7c84", "#8a8b93", "#9a9ba2", "#a9aab0", "#b8b9be", "#c7c8cc")
MOUTH = paint.ramp("#0c0c0e", "#18181b", "#252529", "#333338", "#45454b")

LIGHT = np.array([0.0, 0.86, -0.5])
LIGHT /= np.linalg.norm(LIGHT)


def mantle_field(p):
    c = np.array([0.0, 8.0, 6.0])
    r = np.array([9.5, 11.0, 12.0])
    q = (p - c) / r
    return np.sqrt((q ** 2).sum(1)) - 1


def head_field(p):
    c = np.array([0.0, 9.0, -15.0])
    r = np.array([6.5, 7.0, 7.5])
    q = (p - c) / r
    return np.sqrt((q ** 2).sum(1)) - 1


def _fur(p, n, noise, streak, pal, ui, vi, cap_from=14.5, cap_mix=None):
    d = np.clip(n @ LIGHT, -1, 1)
    lvl = 0.8 + 0.12 * d + 0.05 * noise + 0.12 * (streak - 0.5)
    rgb = paint.shade_to_ramp(lvl, pal["fur"], ui, vi, dither=0.45)
    # lavender cap on top, with a wavy, strand-wise lower boundary
    edge = cap_from + 1.2 * np.sin(p[:, 0] * 0.9 + p[:, 2] * 0.55) + 1.5 * (streak - 0.5)
    cap = p[:, 1] > edge if cap_mix is None else cap_mix
    if np.any(cap):
        crgb = paint.shade_to_ramp(lvl - 0.08, pal["cap"], ui, vi, dither=0.45)
        rgb = np.where(cap[:, None], crgb, rgb)
    # strand lines
    lines = streak < 0.3
    rgb = np.where(lines[:, None], rgb * 0.9, rgb)
    return rgb


def paint_textures(model, palette, seed=13):
    pal = PALETTES[palette]
    cv = paint.Canvas(model.tex_w, model.tex_h)
    for fs in paint.face_samples(model):
        p = fs.pos
        N = len(p)
        ui, vi = fs.ui, fs.vi
        tag = fs.tag
        face = fs.face
        noise = paint.fbm(p, 3.0, 2, seed) - 0.5
        streak = _streaks(p, seed)
        s, t = fs.s, fs.t
        if tag == "mantle":
            n = blob.implicit_normal(mantle_field, p)
            rgb = _fur(p, n, noise, streak, pal, ui, vi)
            if face == "down":
                rgb = rgb * 0.7
            cv.put(ui, vi, rgb)
        elif tag == "collar":
            n = blob.implicit_normal(head_field, p) * 0.3 + np.repeat(fs.normal[None], N, 0) * 0.7
            n /= np.linalg.norm(n, axis=1, keepdims=True)
            rgb = _fur(p, n, noise, streak, pal, ui, vi, cap_from=12.5)
            cv.put(ui, vi, rgb)
        elif tag in ("hem", "hem_back", "beard", "beard_side"):
            if face in ("up", "down"):
                continue
            count = {"hem": 9, "hem_back": 8, "beard": 7, "beard_side": 3}[tag]
            edge = 0.55 + zigzag(s, count, 0.45, 0.3)
            alpha = np.where(t > edge, 0, 255)
            n = np.repeat(fs.normal[None], N, 0)
            capmix = (p[:, 1] > 9.5) & (tag in ("beard", "beard_side"))
            rgb = _fur(p, n, noise, streak, pal, ui, vi, cap_mix=capmix)
            rgb = rgb * (0.92 + 0.08 * (1 - t))[:, None]
            cv.put(ui, vi, rgb, alpha)
        elif tag in ("skull", "jaw", "leg_bone", "leg_joint", "paw", "claw", "tail_bone", "tail_joint"):
            if tag in ("skull", "jaw"):
                n = blob.implicit_normal(head_field, p) * 0.6 + np.repeat(fs.normal[None], N, 0) * 0.4
                n /= np.linalg.norm(n, axis=1, keepdims=True)
            else:
                n = np.repeat(fs.normal[None], N, 0)
            lvl = 0.66 + 0.18 * (n @ LIGHT) + 0.07 * noise
            if tag == "jaw":
                lvl -= 0.05 + 0.1 * (1 - blob.smoothstep(1.0, 4.0, p[:, 1]))
                # rocky cracks
                crack = paint.value_noise(p * np.array([1.2, 1.2, 1.2]), 1.0, seed + 5)
                lvl = np.where(np.abs(crack - 0.5) < 0.03, lvl - 0.2, lvl)
            if tag == "claw":
                lvl += 0.08
            if face == "down":
                lvl -= 0.15
            rgb = paint.shade_to_ramp(lvl, BONE, ui, vi, dither=0.4)
            if tag == "skull":
                # nostril holes on the top-front of the snout
                x = p[:, 0]
                z = p[:, 2]
                nost = (face == "up") & (np.abs(np.abs(x) - 1.6) < 1.0) & (z < -17.5) & (z > -19.6) & \
                       (np.abs(np.abs(x) - 1.6) < (z + 19.8) * 0.55)
                rgb = np.where(nost[:, None], MOUTH[0][None], rgb)
                # mouth roof
                if face == "down":
                    rgb = np.where(((np.abs(x) < 4.6) & (z < -10))[:, None],
                                   paint.shade_to_ramp(np.full(N, 0.35), MOUTH, ui, vi, dither=0), rgb)
            if tag == "jaw" and face == "up":
                inside = (np.abs(p[:, 0]) < 4.4) & (p[:, 2] > -20.8) & (p[:, 1] > 6.9)
                rgb = np.where(inside[:, None], paint.shade_to_ramp(np.full(N, 0.3), MOUTH, ui, vi, dither=0), rgb)
            cv.put(ui, vi, rgb)
        elif tag in ("teeth_top", "teeth_bottom", "teeth_top_side", "teeth_bottom_side"):
            if face in ("back",) and tag in ("teeth_top", "teeth_bottom"):
                continue
            top = tag.startswith("teeth_top")
            count = 4 if tag in ("teeth_top", "teeth_bottom") else 4.5
            if top:
                edge = 0.25 + zigzag(s, count, 0.75, 0.5)
                alpha = np.where(t > edge, 0, 255)
            else:
                edge = 0.75 - zigzag(s, count, 0.75)
                alpha = np.where(t < edge, 0, 255)
            lvl = 0.72 + 0.1 * (fs.normal @ LIGHT) + 0.05 * noise
            cv.put(ui, vi, paint.shade_to_ramp(np.broadcast_to(lvl, (N,)), BONE, ui, vi, dither=0.3), alpha)
        elif tag in ("throat", "mouth_floor"):
            lvl = 0.15 + 0.25 * blob.smoothstep(-11, -20, p[:, 2]) + 0.04 * noise
            cv.put(ui, vi, paint.shade_to_ramp(lvl, MOUTH, ui, vi, dither=0.3))
        elif tag in ("stone", "stone_post", "stone_top"):
            n = np.repeat(fs.normal[None], N, 0)
            grain = paint.fbm(p * np.array([1.5, 1.5, 1.5]), 2.0, 3, seed + 9) - 0.5
            lvl = 0.62 + 0.18 * (n @ LIGHT) + 0.12 * grain
            if tag == "stone_post":
                lvl -= 0.08
            rgb = paint.shade_to_ramp(lvl, STONE, ui, vi, dither=0.35)
            if tag == "stone" and face in ("front", "back"):
                # three engraved wavy lines
                x = p[:, 0]
                y = p[:, 1]
                carve = np.zeros(N, dtype=bool)
                for row in (26.5, 24.0, 21.5):
                    wave_y = row + 0.55 * np.sign(np.sin((x + 2.2) * 1.6))
                    carve |= (np.abs(y - wave_y) < 0.35) & (np.abs(x) < 2.3)
                rim = (np.abs(x) > 2.9) | (y > 28.4)
                rgb = np.where(carve[:, None], STONE[1][None], rgb)
                rgb = np.where((rim & ~carve)[:, None], rgb * 0.92, rgb)
            cv.put(ui, vi, rgb)
        # "eye" stays transparent in the base texture
    return cv.rgba.clip(0, 255).astype(np.uint8)


def paint_alpha(model):
    cv = paint.Canvas(model.tex_w, model.tex_h)
    for fs in paint.face_samples(model):
        if fs.tag != "eye" or fs.face != "front":
            continue
        lu = fs.ui - fs.ui.min()
        col = np.where((lu == 0)[:, None], paint.hex_rgb("#ff5a40")[None], paint.hex_rgb("#e01818")[None])
        cv.put(fs.ui, fs.vi, col)
    return cv.rgba.clip(0, 255).astype(np.uint8)


def data_files():
    return {
        "species_additions/houndstone.json": {
            "target": "cobblemon:houndstone",
            "implemented": True,
            "baseScale": 0.7,
            "hitbox": {"width": 1.7, "height": 1.9, "fixed": False},
        },
        "spawn_pool_world/0972_houndstone.json": {
            "enabled": True,
            "neededInstalledMods": [],
            "neededUninstalledMods": [],
            "spawns": [
                {
                    "id": "houndstone-1", "pokemon": "houndstone", "presets": ["natural"], "type": "pokemon",
                    "spawnablePositionType": "grounded", "bucket": "rare", "level": "30-50", "weight": 3.0,
                    "weightMultipliers": [{"multiplier": 3.0, "condition": {"timeRange": "night"}}],
                    "condition": {"biomes": ["#cobblemon:is_spooky", "#cobblemon:is_plains", "#cobblemon:is_grassland"]},
                },
                {
                    "id": "houndstone-2", "pokemon": "houndstone", "presets": ["natural"], "type": "pokemon",
                    "spawnablePositionType": "grounded", "bucket": "rare", "level": "30-50", "weight": 2.0,
                    "weightMultipliers": [{"multiplier": 3.0, "condition": {"timeRange": "night"}}],
                    "condition": {"biomes": ["#cobblemon:is_overworld"], "structures": ["#minecraft:village"]},
                },
            ],
        },
        "spawn_pool_world/herds/0972_houndstone_alpha.json": {
            "neededInstalledMods": [],
            "neededUninstalledMods": [],
            "spawns": [
                {
                    "id": "houndstone-alpha-1", "presets": ["natural"], "type": "pokemon-herd", "bucket": "boss",
                    "spawnablePositionType": "grounded", "maxHerdSize": 4, "levelRange": "36-100", "weight": 50.0,
                    "weightMultiplier": {"multiplier": 2.0, "condition": {"timeRange": "night"}},
                    "condition": {"biomes": ["#cobblemon:is_spooky", "#cobblemon:is_plains", "#cobblemon:is_grassland"]},
                    "herdablePokemon": [
                        {"pokemon": "houndstone held_item=cobblemon:spell_tag alpha=true", "weight": 30.0,
                         "levelRange": "1-100", "maxTimes": 1, "isLeader": True, "isFollower": False},
                        {"pokemon": "greavard", "weight": 80.0, "levelRange": "12-29", "levelRangeOffset": "-3-3",
                         "maxTimes": 4, "isLeader": False, "isFollower": True},
                        {"pokemon": "houndstone", "weight": 40.0, "levelRange": "30-45", "levelRangeOffset": "-2-4",
                         "maxTimes": 2, "isLeader": False, "isFollower": True},
                    ],
                }
            ],
        },
    }


if __name__ == "__main__":
    mdl = build_model()
    print(sum(1 for _ in mdl.cubes()), "cubes")
