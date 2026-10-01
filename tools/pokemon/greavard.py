"""Greavard (#971) for Cobblemon 1.8.1 - model and textures.

Shaggy ghost puppy: huge head with a permanently open, zig-zag edged mouth,
fringe hiding its eyes, long white-tipped ear locks, a bone on its head that
holds a lavender/yellow candle flame, stubby legs and a wispy tail.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from cobblegen import geom, blob, paint  # noqa: E402

NAME = "greavard"
DEX = "0971_greavard"
PREVIEW_SIZE = (440, 440)
FLAME_FRAMES = 4

EYE_X = 4.4
EYE_Y = 10.6


def _mirror(bone, cubes, tag=None):
    out = []
    for cu in cubes:
        o = cu.origin
        out.append(bone.add([-(o[0] + cu.size[0]), o[1], o[2]], cu.size, mirror=True, share=cu,
                            tag=tag or cu.tag, inflate=cu.inflate))
    return out


def build_model():
    m = geom.Model(NAME, 128, 128)
    m.visible_bounds = (2.5, 2.5, (0, 0.75, 0))
    root = m.bone(NAME, None, [0, 0, 0])
    root.locator("root", [0, 0, 0])
    m.bone("locator_top", NAME, [0, 0, 0]).locator("top", [0, 33, -8])
    body = m.bone("body", NAME, [0, 6, 2])

    # ---------------------------------------------------------------- torso
    torso = m.bone("torso", "body", [0, 6, 2])
    torso.add([-5, 1.5, -3], [10, 1, 10], tag="fur")
    torso.add([-5.5, 2, -4], [11, 8, 12], tag="fur")
    torso.add([-4.5, 2, -5], [9, 8, 14], tag="fur")
    torso.add([-4.5, 10, -3], [9, 1, 10], tag="fur")
    # shaggy skirt planes hanging around the belly
    skirt_l = torso.add([5.55, 1.6, -3.5], [0, 4, 11], tag="skirt")
    _mirror(torso, [skirt_l])
    torso.add([-5, 1.6, 8.05], [10, 4, 0], tag="skirt_back")

    # ----------------------------------------------------------------- legs
    def leg(name, x, z):
        b = m.bone(name, "body", [x, 4, z])
        b.add([x - 1.5, 1.5, z - 1.5], [3, 3, 3], tag="leg")
        cubes = geom.rounded_blob(b, (x, 1.0, z - 0.4), (4, 2, 4), "paw", steps=0.5)
        return b, cubes

    _, fl = leg("leg_front_left", 3.4, -4.0)
    flr = m.bone("leg_front_right", "body", [-3.4, 4, -4.0])
    fl_upper = m.bones["leg_front_left"].cubes[0]
    _mirror(flr, [fl_upper] + fl)
    _, bl = leg("leg_back_left", 3.4, 4.6)
    blr = m.bone("leg_back_right", "body", [-3.4, 4, 4.6])
    _mirror(blr, [m.bones["leg_back_left"].cubes[0]] + bl)

    # ----------------------------------------------------------------- tail
    tail_specs = [(3, 3, -38), (3, 3, 26), (3, 2, 18), (2, 1, -30)]  # (length, width, x-rotation)
    parent = "torso"
    y, z = 9.0, 7.6
    for i, (ln, wd, rx) in enumerate(tail_specs):
        name = "tail" if i == 0 else "tail%d" % (i + 1)
        b = m.bone(name, parent, [0, y, z], [rx, 0, 0])
        c = b.add([-0.5, y, z - wd / 2.0], [1, ln, wd], inflate=0.15, tag="tail")
        c.seg = i
        parent = name
        y += ln

    # ----------------------------------------------------------------- head
    head = m.bone("head", "torso", [0, 8, -3])
    for (y0, y1, rings) in (
            (8, 14, [(14, -12.0, -3.0), (12, -13.0, -3.0), (10, -13.5, -2.5)]),   # cranium
            (14, 15, [(12, -11.5, -3.5), (9, -12.5, -3.5)]),                       # crown
            (15, 16, [(7, -10.5, -4.5)])):
        for (w, z0, z1) in rings:
            head.add([-w / 2.0, y0, z0], [w, y1 - y0, z1 - z0], tag="fur")
    muzzle = m.bone("muzzle", "head", [0, 10, -13])
    muzzle.add([-5.5, 8, -14.5], [11, 1, 1], tag="muzzle")       # upper lip band
    muzzle.add([-3, 8, -15], [6, 3, 2], tag="muzzle")            # snout bulge
    geom.rounded_blob(muzzle, (0, 11.0, -15.4), (4, 3, 2), "nose", steps=0.5)
    # cheeks close the sides of the open mouth
    ck = head.add([5, 3, -11.5], [2, 5, 8], tag="cheek")
    _mirror(head, [ck])
    head.add([-5, 3, -7], [10, 5, 2], tag="throat")
    # upper zig-zag fur edge of the mouth + little fangs
    head.add([-5.5, 5.5, -14.56], [11, 3, 0], tag="fringe_top")
    tooth = head.add([3.7, 6.1, -14.3], [1, 2, 1], tag="tooth", inflate=-0.1)
    _mirror(head, [tooth])

    jaw = m.bone("jaw", "head", [0, 3.2, -6])
    jaw.add([-6, 0.2, -12], [12, 3, 6], tag="jaw")
    jaw.add([-5, 0.2, -13], [10, 3, 7], tag="jaw")
    jaw.add([-4, 0.2, -13.5], [8, 3, 7], tag="jaw")
    jaw.add([-4.5, 3.23, -12.6], [9, 0, 6], tag="tongue")
    jaw.add([-5, 2.2, -13.56], [10, 3, 0], tag="fringe_bottom")
    ft = jaw.add([3.3, 3.0, -13.3], [1, 2, 1], tag="tooth", inflate=-0.1)
    _mirror(jaw, [ft])

    # fringe over the eyes
    bangs = m.bone("bangs", "head", [0, 15, -12])
    bangs.add([-7.5, 9, -14], [15, 6, 2], tag="bangs")
    bangs.add([-6.5, 15, -12.5], [13, 1, 5], tag="bangs_top")

    # eyes hide under the fringe (only shown by the alpha glow)
    eyes = m.bone("eyes", "head", [0, EYE_Y, -13.56])
    el = m.bone("eye_left", "eyes", [EYE_X, EYE_Y, -13.56])
    ec = el.add([EYE_X - 1.5, EYE_Y - 0.5, -13.56], [3, 1, 0], tag="eye")
    el.locator("eye2", [EYE_X, EYE_Y, -13.8])
    er = m.bone("eye_right", "eyes", [-EYE_X, EYE_Y, -13.56])
    _mirror(er, [ec])
    er.locator("eye1", [-EYE_X, EYE_Y, -13.8])

    # long ear locks
    for side, sx in (("left", 1), ("right", -1)):
        e1 = m.bone("ear_" + side, "head", [sx * 7.2, 14.5, -6.5], [0, 0, -7 * sx])
        e2 = m.bone("ear_%s2" % side, "ear_" + side, [sx * 7.6, 6.0, -6.5], [0, 0, -6 * sx])
        if sx > 0:
            a = e1.add([6.5, 5.5, -9.5], [2, 9, 6], tag="ear")
            b = e2.add([6.6, 1.5, -9.5], [2, 5, 6], tag="ear_tip", inflate=-0.05)
            ear_cubes = (a, b)
        else:
            _mirror(e1, [ear_cubes[0]])
            _mirror(e2, [ear_cubes[1]])

    # bone + candle on the head
    candle = m.bone("candle", "head", [0, 15.5, -8])
    candle.add([-1, 15.5, -9], [2, 3, 2], tag="bone")
    lobe = geom.rounded_blob(candle, (1.6, 19.1, -8), (4, 3, 3), "bone_knob", steps=0.5)
    _mirror(candle, lobe)
    candle.add([-0.5, 20.1, -8.5], [1, 2, 1], tag="wick")
    flame = m.bone("flame", "candle", [0, 21.4, -8])
    flame.add([-3.5, 21.1, -8], [7, 12, 0], tag="flame", rotation=[0, 45, 0], pivot=[0, 25, -8])
    flame.add([0, 21.1, -11.5], [0, 12, 7], tag="flame", rotation=[0, 45, 0], pivot=[0, 25, -8])
    m.pack()
    return m


# --------------------------------------------------------------- palettes
PALETTES = {
    "normal": {
        "fur": paint.ramp("#4d5e78", "#5b6d88", "#6a7d99", "#7a8eaa", "#8b9fbb", "#9cb0ca", "#aabdd4",
                          "#b7c9dd", "#c6d5e6", "#d8e3ef", "#ecf2f8"),
    },
    "shiny": {
        "fur": paint.ramp("#5e4c12", "#715d18", "#856f20", "#99822a", "#ab9434", "#bba43f", "#c6ae48",
                          "#d0b857", "#dbc86f", "#e7da94", "#f3edc6"),
    },
}
WHITE = paint.ramp("#9aa3b0", "#b3bbc6", "#c9d0d9", "#dce2e9", "#ebeff4", "#f7f9fb")
MOUTH = paint.ramp("#3a0f16", "#561821", "#72222b", "#8e2f34", "#a8443f")
TONGUE = paint.ramp("#a63f45", "#c45652", "#dc6e66", "#ec857a", "#f6a090")
NOSE = paint.ramp("#1d1c1f", "#2b2a2e", "#3d3c41", "#55545a", "#77767c")
BONE = paint.ramp("#b4afc2", "#c9c5d6", "#dcd9e6", "#ebe9f2", "#f5f4fa", "#ffffff")
WICK = paint.ramp("#141215", "#232026", "#353039")

LIGHT = np.array([0.0, 0.86, -0.5])
LIGHT /= np.linalg.norm(LIGHT)


def head_field(p):
    c = np.array([0.0, 8.0, -7.8])
    r = np.array([7.2, 7.4, 7.0])
    q = (p - c) / r
    return np.sqrt((q ** 2).sum(1)) - 1


def torso_field(p):
    c = np.array([0.0, 6.0, 2.0])
    r = np.array([5.8, 5.0, 7.5])
    q = (p - c) / r
    return np.sqrt((q ** 2).sum(1)) - 1


def _fur_level(p, n, noise, streak):
    d = np.clip(n @ LIGHT, -1, 1)
    return 0.70 + 0.13 * d + 0.06 * noise + 0.10 * (streak - 0.5)


def _streaks(p, seed):
    """Long vertical hair strands: high frequency across, low frequency along y."""
    q = p * np.array([1.6, 0.18, 1.6])
    s = paint.value_noise(q, 1.0, seed)
    s2 = paint.value_noise(q * 2.1, 1.0, seed + 3)
    return 0.65 * s + 0.35 * s2


def zigzag(s, count, depth, phase=0.0):
    """Triangle wave in 0..depth across s (0..1)."""
    x = (s * count + phase) % 1.0
    return depth * (1 - np.abs(2 * x - 1))


def paint_textures(model, palette, seed=7):
    pal = PALETTES[palette]
    fur = pal["fur"]
    cv = paint.Canvas(model.tex_w, model.tex_h)
    for fs in paint.face_samples(model):
        p = fs.pos
        N = len(p)
        ui, vi = fs.ui, fs.vi
        tag = fs.tag
        noise = paint.fbm(p, 3.0, 2, seed) - 0.5
        streak = _streaks(p, seed)
        face = fs.face
        if tag in ("fur", "muzzle", "jaw", "cheek", "chin", "leg", "paw"):
            if fs.bone in ("torso",) or fs.bone.startswith("leg"):
                n = blob.implicit_normal(torso_field, p)
            else:
                n = blob.implicit_normal(head_field, p)
            if tag in ("leg", "paw"):
                n = 0.5 * n + 0.5 * np.repeat(fs.normal[None], N, 0)
                n /= np.linalg.norm(n, axis=1, keepdims=True)
            lvl = _fur_level(p, n, noise, streak)
            ao = np.ones(N)
            if face == "down":
                ao *= 0.55
            if tag in ("leg", "paw"):
                lvl -= 0.12
                ao *= 0.75 + 0.25 * blob.smoothstep(0, 2.0, p[:, 1])
            if tag == "jaw":
                lvl -= 0.05
            if fs.bone == "torso":
                # darker underneath the head and toward the belly
                ao *= 1 - 0.3 * (1 - blob.smoothstep(-5, -1.5, p[:, 2]))
                lvl += 0.06 * blob.smoothstep(4, 10, p[:, 1])
            if fs.bone in ("head",) and face == "front":
                under = (p[:, 1] < 14.0) & (p[:, 1] > 8.0) & (np.abs(p[:, 0]) > 3.0) & (p[:, 2] > -14.1)
                ao *= np.where(under, 0.3, 1.0)
            if fs.bone == "head" and face in ("left", "right"):
                ao *= 1 - 0.35 * blob.smoothstep(-10.5, -8.5, p[:, 2]) * (1 - blob.smoothstep(-3.5, -2.5, p[:, 2]))
            lvl = lvl - 0.32 * (1 - ao)
            rgb = paint.shade_to_ramp(lvl, fur, ui, vi, dither=0.5)
            # white tufts: chin, belly fringe line
            white = np.zeros(N, dtype=bool)
            if tag in ("chin",) or (tag == "jaw" and face in ("down",)):
                white |= True
            if tag == "jaw":
                tip = p[:, 1] < 1.9 + zigzag(p[:, 0] / 12 + 0.5, 6, 0.9)
                white |= tip & (face in ("front", "left", "right"))
            if fs.bone == "torso" and face != "up":
                white |= p[:, 1] < 2.6 + zigzag((p[:, 0] + p[:, 2]) / 14, 5, 1.0)
            if white.any():
                wl = 0.62 + 0.18 * (n @ LIGHT) + 0.1 * (streak - 0.5)
                wrgb = paint.shade_to_ramp(wl, WHITE, ui, vi, dither=0.45)
                rgb = np.where(white[:, None], wrgb, rgb)
            # mouth interior faces
            mouth = np.zeros(N, dtype=bool)
            if tag == "cheek":
                inner = (face == "right") if fs.cube.share is None and fs.cube.origin[0] > 0 else (face == "left")
                mouth |= inner
            if tag in ("fur", "muzzle") and face == "down" and fs.bone in ("head", "muzzle"):
                mouth |= (np.abs(p[:, 0]) < 5.6) & (p[:, 2] < -5.5) & (p[:, 1] < 8)
            if tag == "jaw" and face == "up":
                mouth |= (np.abs(p[:, 0]) < 5.2) & (p[:, 2] > -13.4)
            if mouth.any():
                ml = 0.35 + 0.25 * blob.smoothstep(-6, -13, p[:, 2]) + 0.1 * noise
                mrgb = paint.shade_to_ramp(ml, MOUTH, ui, vi, dither=0.4)
                rgb = np.where(mouth[:, None], mrgb, rgb)
            # muzzle detail: lip line under the nose
            if tag == "muzzle" and face == "front":
                x, y = p[:, 0], p[:, 1]
                line = (np.abs(x) < 0.5) & (y > 8.0) & (y < 9.5) & (p[:, 2] < -14.9)
                ink = paint.shade_to_ramp(np.full(N, 0.32), fur, ui, vi, dither=0)
                rgb = np.where(line[:, None], ink, rgb)
            # paw toe lines
            if tag == "paw" and face == "front":
                x = p[:, 0] - np.sign(p[:, 0]) * 3.4
                toe = (np.abs(np.abs(x) - 0.5) < 0.5) & (p[:, 1] < 1.6)
                toe &= (np.abs(x) > 0.0)
                ink = paint.shade_to_ramp(np.full(N, 0.15), fur, ui, vi, dither=0)
                rgb = np.where(toe[:, None], ink, rgb)
            cv.put(ui, vi, rgb)
        elif tag in ("skirt", "skirt_back", "ear", "ear_tip", "bangs", "bangs_top", "fringe_top", "fringe_bottom", "tail"):
            n = np.repeat(fs.normal[None], N, 0)
            alpha = np.full(N, 255.0)
            t = fs.t
            s = fs.s
            lvl = 0.68 + 0.12 * (n @ LIGHT) + 0.14 * (streak - 0.5) + 0.05 * noise
            use_white = np.zeros(N, dtype=bool)
            if tag in ("skirt", "skirt_back"):
                if face in ("up", "down"):
                    continue
                edge = 0.55 + zigzag(s, 5 if tag == "skirt" else 4, 0.4)
                alpha = np.where(t > edge, 0, 255)
                use_white = t > 0.35
                lvl -= 0.05
            elif tag == "ear":
                lvl += 0.04 - 0.1 * (face == "down")
                use_white = p[:, 1] < 6.5 + zigzag(p[:, 2] / 6, 3, 1.2)
            elif tag == "ear_tip":
                if face in ("left", "right", "front", "back"):
                    edge = 0.55 + zigzag(s, 3, 0.45)
                    alpha = np.where(t > edge, 0, 255)
                use_white |= True
            elif tag == "bangs":
                if face == "front":
                    edge = 0.4 + zigzag(s, 4, 0.6, 0.5)
                    alpha = np.where(t > edge, 0, 255)
                    col = np.floor(s * 15).astype(int)
                    strand = ((col * 7) % 5) / 4.0
                    lvl = lvl + 0.1 * (strand - 0.5) + 0.12 * blob.smoothstep(0.3, 1.0, t) * (strand > 0.4)
                    sep = np.abs((s * 8 + 0.5) % 1.0 - 0.5) < 0.07
                    lvl = np.where(sep & (t > 0.15), lvl - 0.3, lvl)
                elif face in ("left", "right"):
                    alpha = np.where(t > 0.5 + zigzag(s, 1, 0.4), 0, 255)
                lvl += 0.1 - 0.06 * fs.t
            elif tag == "bangs_top":
                if face == "front":
                    edge = 0.45 + zigzag(s, 7, 0.55)
                    alpha = np.where(t > edge, 0, 255)
                lvl += 0.1
            elif tag == "fringe_top":
                if face == "back":
                    continue
                edge = 0.3 + zigzag(s, 3.5, 0.7, 0.5)
                alpha = np.where(t > edge, 0, 255)
                lvl += 0.04 - 0.12 * t
            elif tag == "fringe_bottom":
                if face == "back":
                    continue
                edge = 0.7 - zigzag(s, 3, 0.7, 0.0)
                alpha = np.where(t < edge, 0, 255)
                lvl -= 0.02 - 0.1 * t
            elif tag == "tail":
                seg = getattr(fs.cube, "seg", 0)
                along = (seg + (1 - t if face not in ("up", "down") else 0.5)) / 4.0
                use_white = along > 0.45
                lvl += 0.12
            rgb = paint.shade_to_ramp(lvl, fur, ui, vi, dither=0.45)
            use_white = np.broadcast_to(np.asarray(use_white, dtype=bool), (N,))
            lvl = np.broadcast_to(lvl, (N,))
            if use_white.any():
                wrgb = paint.shade_to_ramp(lvl + 0.02, WHITE, ui, vi, dither=0.45)
                rgb = np.where(use_white[:, None], wrgb, rgb)
            # darker strand lines on hair locks
            lines = (streak < 0.33) & (alpha > 0)
            rgb = np.where(lines[:, None], rgb * 0.88, rgb)
            cv.put(ui, vi, rgb, alpha)
        elif tag == "throat":
            if face != "front":
                continue
            lvl = 0.2 + 0.25 * blob.smoothstep(4, 7, p[:, 1]) + 0.05 * noise
            cv.put(ui, vi, paint.shade_to_ramp(lvl, MOUTH, ui, vi, dither=0.3))
        elif tag == "tongue":
            if face != "up":
                continue
            r = np.abs(p[:, 0]) / 4.5
            lvl = 0.75 - 0.4 * r ** 2 - 0.25 * blob.smoothstep(-8, -4, p[:, 2]) + 0.05 * noise
            groove = (np.abs(p[:, 0]) < 0.5) & (p[:, 2] < -7.5)
            lvl = np.where(groove, lvl - 0.25, lvl)
            cv.put(ui, vi, paint.shade_to_ramp(lvl, TONGUE, ui, vi, dither=0.35))
        elif tag == "tooth":
            lvl = 0.75 + 0.2 * (fs.normal @ LIGHT)
            cv.put(ui, vi, paint.shade_to_ramp(np.full(N, lvl), WHITE, ui, vi, dither=0))
        elif tag == "nose":
            n = blob.sphere_normal(p, (0, 11.0, -15.4), (2, 1.5, 1))
            hl = np.clip(n @ np.array([-0.3, 0.8, -0.5]), 0, 1) ** 6
            lvl = 0.3 + 0.2 * (n @ LIGHT) + 0.5 * hl
            cv.put(ui, vi, paint.shade_to_ramp(lvl, NOSE, ui, vi, dither=0.3))
        elif tag in ("bone", "bone_knob"):
            if tag == "bone_knob":
                c = np.array([np.sign(p[:, 0].mean()) * 1.6, 19.1, -8.0])
                n = blob.sphere_normal(p, c)
            else:
                n = np.repeat(fs.normal[None], N, 0)
            lvl = 0.72 + 0.2 * (n @ LIGHT) + 0.04 * noise
            if tag == "bone":
                lvl -= 0.15 * (1 - blob.smoothstep(15.5, 18, p[:, 1]))
            cv.put(ui, vi, paint.shade_to_ramp(lvl, BONE, ui, vi, dither=0.35))
        elif tag == "wick":
            lvl = 0.4 + 0.3 * (fs.normal @ LIGHT) + 0.4 * blob.smoothstep(21.0, 22.1, p[:, 1])
            cv.put(ui, vi, paint.shade_to_ramp(np.full(N, 1) * lvl, WICK, ui, vi, dither=0))
        # "eye" and "flame" stay transparent in the base texture
    return cv.rgba.clip(0, 255).astype(np.uint8)


# ----------------------------------------------------------------- flame
FLAME_OUT = paint.hex_rgb("#b89fd0")
FLAME_RIM = paint.hex_rgb("#9a7fc4")
FLAME_MID = paint.hex_rgb("#f2c98a")
FLAME_IN = paint.hex_rgb("#fbd89a")
FLAME_CORE = paint.hex_rgb("#fff3cf")


def _flame_pixels(s, t, frame):
    """Teardrop candle flame on a plane. s across (0..1), t down (0 top .. 1 bottom)."""
    h = 1 - t  # 0 bottom .. 1 top
    sway = [0.0, 0.07, 0.0, -0.07][frame % 4]
    stretch = [1.0, 0.93, 1.05, 0.96][frame % 4]
    hh = h / stretch
    lo = np.sqrt(np.clip(1 - ((0.28 - hh) / 0.30) ** 2, 0, 1))
    hi = np.clip(1 - (hh - 0.28) / 0.72, 0, 1) ** 0.9
    w = np.where(hh < 0.28, lo, hi) * 0.5
    cx = 0.5 + sway * np.clip(hh, 0, 1) ** 2
    d = np.abs(s - cx) / np.maximum(w, 1e-3)
    inside = (d < 1.0) & (hh <= 1.0) & (hh > 0.02)
    yellow = inside & (d < 0.75) & (hh < 0.62) & (hh > 0.05)
    core = inside & (d < 0.45) & (hh < 0.45) & (hh > 0.08)
    rim = inside & ~yellow & (d > 0.8)
    rgb = np.where(inside[:, None], FLAME_OUT[None], 0)
    rgb = np.where(rim[:, None], FLAME_RIM[None], rgb)
    rgb = np.where(yellow[:, None], FLAME_IN[None], rgb)
    rgb = np.where((yellow & (d > 0.6))[:, None], FLAME_MID[None], rgb)
    rgb = np.where(core[:, None], FLAME_CORE[None], rgb)
    a = np.where(inside, 170, 0)
    a = np.where(rim, 200, a)
    a = np.where(yellow, 240, a)
    a = np.where(core, 255, a)
    return rgb, a


def paint_flame_frames(model):
    frames = []
    samples = [fs for fs in paint.face_samples(model) if fs.tag == "flame"]
    for f in range(FLAME_FRAMES):
        cv = paint.Canvas(model.tex_w, model.tex_h)
        for fs in samples:
            if fs.face not in ("front", "back", "left", "right"):
                continue
            s = fs.s if fs.face in ("front", "left") else 1 - fs.s
            rgb, a = _flame_pixels(s, fs.t, f)
            cv.put(fs.ui, fs.vi, rgb, a)
        frames.append(cv.rgba.clip(0, 255).astype(np.uint8))
    return frames


def paint_alpha(model):
    cv = paint.Canvas(model.tex_w, model.tex_h)
    for fs in paint.face_samples(model):
        if fs.tag != "eye" or fs.face != "front":
            continue
        lu = fs.ui - fs.ui.min()
        col = np.where((lu == 1)[:, None], paint.hex_rgb("#ff5a40")[None], paint.hex_rgb("#e01818")[None])
        cv.put(fs.ui, fs.vi, col)
    return cv.rgba.clip(0, 255).astype(np.uint8)


if __name__ == "__main__":
    mdl = build_model()
    print(sum(1 for _ in mdl.cubes()), "cubes")


PREVIEW_SHADOW = (8, 10)


def data_files():
    """Data-pack side: enable the species and give it spawns (night / graveyard-like places)."""
    return {
        "species_additions/greavard.json": {
            "target": "cobblemon:greavard",
            "implemented": True,
            "baseScale": 0.55,
            "hitbox": {"width": 1.1, "height": 1.35, "fixed": False},
        },
        "spawn_pool_world/0971_greavard.json": {
            "enabled": True,
            "neededInstalledMods": [],
            "neededUninstalledMods": [],
            "spawns": [
                {
                    "id": "greavard-1", "pokemon": "greavard", "presets": ["natural"], "type": "pokemon",
                    "spawnablePositionType": "grounded", "bucket": "uncommon", "level": "10-29", "weight": 6.0,
                    "weightMultipliers": [
                        {"multiplier": 2.5, "condition": {"timeRange": "night"}},
                        {"multiplier": 1.25, "condition": {"isPokeSnack": True}},
                    ],
                    "condition": {"biomes": ["#cobblemon:is_spooky", "#cobblemon:is_plains", "#cobblemon:is_grassland"]},
                },
                {
                    "id": "greavard-2", "pokemon": "greavard", "presets": ["natural"], "type": "pokemon",
                    "spawnablePositionType": "grounded", "bucket": "rare", "level": "10-29", "weight": 4.0,
                    "weightMultipliers": [{"multiplier": 2.0, "condition": {"timeRange": "night"}}],
                    "condition": {"biomes": ["#cobblemon:is_overworld"], "structures": ["#minecraft:village"]},
                },
            ],
        },
        "spawn_pool_world/herds/0971_greavard_alpha.json": {
            "neededInstalledMods": [],
            "neededUninstalledMods": [],
            "spawns": [
                {
                    "id": "greavard-alpha-1", "presets": ["natural"], "type": "pokemon-herd", "bucket": "boss",
                    "spawnablePositionType": "grounded", "maxHerdSize": 4, "levelRange": "20-100", "weight": 30.0,
                    "weightMultiplier": {"multiplier": 2.0, "condition": {"timeRange": "night"}},
                    "condition": {"biomes": ["#cobblemon:is_spooky", "#cobblemon:is_plains", "#cobblemon:is_grassland"]},
                    "herdablePokemon": [
                        {"pokemon": "greavard held_item=cobblemon:spell_tag alpha=true", "weight": 30.0,
                         "levelRange": "1-100", "maxTimes": 1, "isLeader": True, "isFollower": False},
                        {"pokemon": "greavard", "weight": 80.0, "levelRange": "10-28", "levelRangeOffset": "-3-3",
                         "maxTimes": 4, "isLeader": False, "isFollower": True},
                    ],
                }
            ],
        },
    }
