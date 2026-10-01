"""Gulpin (#316) for Cobblemon 1.8.1 - model, textures, animations, poser, resolver."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from cobblegen import geom, blob, paint  # noqa: E402

NAME = "gulpin"
DEX = "0316_gulpin"

# ----------------------------------------------------------------- shape
H = 11.0      # dome height (without feather)
YW = 3.0      # height of the widest ring
A = 7.5       # half width
BF = 9.0      # front reach
BB = 9.0      # back reach
M_TOP = (2.8, 3.0, 2.2)  # superellipse exponents: width, front, back


def _prof(y, r, m_top, m_bot=2.0, base=3.0):
    if y >= YW:
        k = min(1.0, (y - YW) / (H - YW))
        return r * max(0.0, 1 - k ** m_top) ** (1.0 / m_top)
    k = (YW - y) / (YW + base)
    return r * max(0.0, 1 - k ** m_bot) ** (1.0 / m_bot)


def body_field(p):
    """Implicit surface (<0 inside) matching the layered body, for smooth shading."""
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    b = np.where(z < 0, BF, BB)
    up = y >= YW
    ky = np.where(up, np.clip((y - YW) / (H - YW), 0, 3), np.clip((YW - y) / (YW + 3.0), 0, 3))
    my = np.where(up, np.where(z < 0, M_TOP[1], M_TOP[2]), 2.0)
    return (np.abs(x) / A) ** 2.6 + (np.abs(z) / b) ** 2.6 + ky ** (my + 0.6) - 1.0


# Hand-tuned rings per layer: (y0, y1, [(width, z_front, z_back), ...])
LAYERS = [
    (0.0, 1.0, [(14, -7.0, 7.0), (12, -8.0, 8.0), (9, -8.5, 8.5)]),
    (1.0, 7.0, [(15, -7.0, 7.0), (13, -8.5, 8.5), (10, -9.0, 9.0)]),
    (7.0, 9.0, [(13, -6.5, 6.5), (11, -7.5, 7.5), (9, -8.0, 8.0)]),
    (9.0, 10.0, [(10, -5.0, 6.0), (7, -6.0, 6.0)]),
    (10.0, 11.0, [(6, -3.0, 4.0)]),
]

EYE_X = 2.9
EYE_Y = 7.9


def build_model():
    m = geom.Model(NAME, 128, 128)
    m.visible_bounds = (2, 2, (0, 0.5, 0))
    root = m.bone(NAME, None, [0, 0, 0])
    root.locator("root", [0, 0, 0])
    top = m.bone("locator_top", NAME, [0, 0, 0])
    top.locator("top", [0, 15.0, 0])
    m.bone("body", NAME, [0, 0, 0])
    base = m.bone("base", "body", [0, 0, 0])
    head = m.bone("head", "body", [0, 7.0, 1.0])

    for (y0, y1, rings) in LAYERS:
        target = base if y1 <= 7.0 else head
        for (w, z0, z1) in rings:
            target.add([-w / 2.0, y0, z0], [w, y1 - y0, z1 - z0], tag="body")

    # slime trailing behind (Gulpin's flat back drip)
    zb = max(c.origin[2] + c.size[2] for c in base.cubes)
    tail = m.bone("tail", "base", [0, 0.5, zb - 1.5])
    tail.add([-3.5, 0.2, zb - 2.0], [7, 1, 3], inflate=0.2, tag="tail")
    tail2 = m.bone("tail2", "tail", [0, 0.5, zb + 1.0])
    tail2.add([-2.5, 0, zb + 0.5], [5, 1, 2], tag="tail", inflate=0.01)
    tail2.add([-1.0, 0, zb + 2.5], [2, 1, 1], tag="tail")

    # arms: two fat finger bumps on each side
    arm_y = 3.0
    sx_l = blob.side_x(m, arm_y, -2.0, sign=1)
    left = m.bone("arm_left", "base", [sx_l - 0.5, arm_y, -2.0])
    right = m.bone("arm_right", "base", [-(sx_l - 0.5), arm_y, -2.0])
    lcubes = []
    for (dx, dy, dz) in ((0.7, -0.4, -1.5), (0.5, 0.4, 1.0)):
        lcubes += geom.rounded_blob(left, (sx_l + dx, arm_y + dy, -2.0 + dz), (3, 3, 3), "arm", steps=0.5)
    for cu in lcubes:
        o = cu.origin
        right.add([-(o[0] + cu.size[0]), o[1], o[2]], cu.size, mirror=True, share=cu, tag="arm")

    # face ------------------------------------------------------------
    face = m.bone("face", "head", [0, 7.0, -7.5])
    # eye planes sit just in front of the dome surface
    zs = [blob.front_z(m, x, y) for x in (EYE_X - 1.4, EYE_X, EYE_X + 1.4) for y in (EYE_Y - 0.9, EYE_Y + 0.9)]
    ez = min(z for z in zs if z is not None) - 0.04
    eyes = m.bone("eyes", "face", [0, EYE_Y, ez])
    eye_l = m.bone("eye_left", "eyes", [EYE_X, EYE_Y, ez])
    ec = eye_l.add([EYE_X - 1.5, EYE_Y - 1.0, ez], [3, 2, 0], tag="eye")
    eye_l.locator("eye2", [EYE_X, EYE_Y, ez - 0.1])
    eye_r = m.bone("eye_right", "eyes", [-EYE_X, EYE_Y, ez])
    eye_r.add([-(ec.origin[0] + ec.size[0]), ec.origin[1], ec.origin[2]], ec.size, mirror=True, share=ec, tag="eye")
    eye_r.locator("eye1", [-EYE_X, EYE_Y, ez - 0.1])

    mz = blob.front_z(m, 0.0, 6.0)
    mouth = m.bone("mouth", "face", [0, 6.0, mz])
    inner = m.bone("mouth_inner", "mouth", [0, 6.0, mz])
    inner.add([-2.0, 4.5, mz - 0.05], [4, 3, 0], tag="mouth")
    lip_top = m.bone("lip_top", "mouth", [0, 6.3, mz - 0.5])
    geom.rounded_blob(lip_top, (0, 7.45, mz - 1.1), (5, 3, 3), "lip", steps=0.5)
    lip_bottom = m.bone("lip_bottom", "mouth", [0, 5.7, mz - 0.5])
    geom.rounded_blob(lip_bottom, (0, 4.75, mz - 0.95), (4, 3, 3), "lip", steps=0.5)

    # feather -----------------------------------------------------------
    fseg = [(3, 2), (3, 3), (3, 3), (3, 2), (2, 1)]  # (length, width)
    fx_rot = [-30, -12, -12, -12, -10]
    parent = "head"
    y = H - 0.4
    z = 1.5
    for i, ((ln, wd), rx) in enumerate(zip(fseg, fx_rot)):
        name = "feather" if i == 0 else "feather%d" % (i + 1)
        b = m.bone(name, parent, [0, y, z], [rx, 0, 0])
        b.add([-0.5, y, z - wd / 2.0], [1, ln, wd], inflate=-0.2, tag="feather")
        b.tag = i
        parent = name
        y += ln
    m.pack()
    return m


# --------------------------------------------------------------- palettes
PALETTES = {
    "normal": {
        "body": paint.ramp("#4f6a3c", "#5f7d47", "#6f9052", "#82a35e", "#95b56b", "#a8c57a",
                           "#b9d38a", "#c9e09c", "#d9ecb2"),
        "feather": paint.ramp("#a87a26", "#c99631", "#e2b23f", "#f1c94f", "#f9db61", "#fde97e", "#fff3a8"),
        "spot": paint.ramp("#141812", "#1d231a", "#283023"),
        "eye": "#26301f",
        "mouth": paint.ramp("#170c0f", "#2a1219", "#3f1b24"),
    },
    "shiny": {
        "body": paint.ramp("#3f5b7a", "#4b6c8f", "#5980a4", "#6895b9", "#79a8cc", "#8bbadc",
                           "#9fcae8", "#b4d9f2", "#cbe7fa"),
        "feather": paint.ramp("#9a4f1d", "#b8632a", "#d27a37", "#e69145", "#f2a656", "#f9bb6f", "#fdd59a"),
        "spot": paint.ramp("#24272a", "#2e3236", "#3a3e42"),
        "eye": "#1d2a3a",
        "mouth": paint.ramp("#120c14", "#22121f", "#33192b"),
    },
}

LIGHT = np.array([0.0, 0.86, -0.5])
LIGHT /= np.linalg.norm(LIGHT)
VIEW = np.array([0.0, 0.25, -1.0])
VIEW /= np.linalg.norm(VIEW)
HALF = (LIGHT + VIEW) / np.linalg.norm(LIGHT + VIEW)


def _shade(n, p, ao, spec_amt=0.18, gloss=10.0):
    d = np.clip(n @ LIGHT, -1, 1)
    s = np.clip(n @ HALF, 0, 1) ** gloss
    g = np.clip(p[:, 1] / H, 0, 1)
    return 0.56 + 0.16 * d + 0.08 * g + spec_amt * s - 0.34 * (1 - ao)


def _arm_centers(model):
    out = []
    for c in model.cubes():
        if c.tag == "arm" and c.share is None:
            o, s = c.origin, c.size
            out.append([o[0] + s[0] / 2, o[1] + s[1] / 2, o[2] + s[2] / 2])
    cs = np.array(out)
    # dedupe overlapping blob parts
    uniq = []
    for c in cs:
        if not any(np.linalg.norm(c - u) < 0.6 for u in uniq):
            uniq.append(c)
    uniq = np.array(uniq)
    return np.vstack([uniq, uniq * np.array([-1, 1, 1])])


def paint_textures(model, palette, seed=3):
    pal = PALETTES[palette]
    cv = paint.Canvas(model.tex_w, model.tex_h)
    samples = paint.face_samples(model)
    arms = _arm_centers(model)
    lips = []
    for c in model.cubes():
        if c.tag == "lip":
            o, s = c.origin, c.size
            lips.append([o[0] + s[0] / 2, o[1] + s[1] / 2, o[2] + s[2] / 2])
    lips = np.array(lips)
    for fs in samples:
        p = fs.pos
        N = len(p)
        ui, vi = fs.ui, fs.vi
        tag = fs.tag
        noise = paint.fbm(p * np.array([1, 1.4, 1]), 3.0, 3, seed) - 0.5
        if tag in ("body", "tail"):
            n = blob.implicit_normal(body_field, p)
            if tag == "tail":
                n = 0.5 * n + 0.5 * np.repeat(fs.normal[None], N, 0)
                n /= np.linalg.norm(n, axis=1, keepdims=True)
            ao = blob.smoothstep(-0.2, 2.4, p[:, 1]) * 0.55 + 0.45
            if fs.face == "down":
                ao = ao * 0.6
            # contact shadows around arms and under the lips
            for c in arms:
                dd = np.linalg.norm((p - c) * np.array([0.8, 1.0, 0.8]), axis=1)
                ao = ao * (1 - 0.45 * (1 - blob.smoothstep(1.5, 3.2, dd)))
            for c in lips:
                dd = np.linalg.norm((p - c) * np.array([0.7, 1.0, 1.0]), axis=1)
                ao = ao * (1 - 0.55 * (1 - blob.smoothstep(2.0, 3.6, dd)))
            lvl = _shade(n, p, ao) + 0.07 * noise
            rgb = paint.shade_to_ramp(lvl, pal["body"], ui, vi, dither=0.55)
            # black spot on the back
            sd = (p[:, 0] / 2.4) ** 2 + ((p[:, 1] - 4.2) / 2.4) ** 2
            spot = sd < 1.0
            spot &= p[:, 2] > 3.0
            spot &= fs.normal[2] > -0.2
            if spot.any():
                srgb = paint.shade_to_ramp(0.3 + 0.6 * np.clip(n[:, 1], 0, 1) + 0.6 * np.clip(sd - 0.6, 0, 1) + 0.2 * noise,
                                           pal["spot"], ui, vi, dither=0.4)
                rgb = np.where(spot[:, None], srgb, rgb)
            cv.put(ui, vi, rgb)
        elif tag in ("arm", "lip"):
            centers = arms if tag == "arm" else lips
            # nearest bump centre for spherical shading
            dist = np.linalg.norm(p[:, None, :] - centers[None, :, :], axis=2)
            ci = centers[np.argmin(dist, axis=1)]
            n = blob.sphere_normal(p, ci)
            ao = np.ones(N)
            if tag == "arm":
                # darker where the bump meets the body
                ao *= 1 - 0.45 * np.clip(-n[:, 0] * np.sign(ci[:, 0]), 0, 1)
            else:
                ao *= 1 - 0.45 * np.clip(n[:, 2], 0, 1)
            ao *= 1 - 0.25 * np.clip(-n[:, 1], 0, 1)
            lvl = _shade(n, p, ao, spec_amt=0.22, gloss=6.0) + 0.06 + 0.05 * noise
            rgb = paint.shade_to_ramp(lvl, pal["body"], ui, vi, dither=0.5)
            cv.put(ui, vi, rgb)
        elif tag == "eye":
            if fs.face != "front":
                continue
            # 3x2: a sleepy closed-eye stroke that dips towards the outside
            lu = ui - ui.min()
            lv = vi - vi.min()
            on = ((lv == 0) & (lu <= 1)) | ((lv == 1) & (lu == 2))
            col = paint.hex_rgb(pal["eye"])
            cv.put(ui[on], vi[on], np.repeat(col[None], on.sum(), 0))
        elif tag == "mouth":
            if fs.face != "front":
                continue
            lv = (vi - vi.min()) / max(1, vi.max() - vi.min())
            lu = np.abs((ui - ui.min()) / max(1, ui.max() - ui.min()) - 0.5) * 2
            lvl = 0.9 - lv * 0.5 - lu * 0.4
            rgb = paint.shade_to_ramp(lvl, pal["mouth"], ui, vi, dither=0.3)
            cv.put(ui, vi, rgb)
        elif tag == "feather":
            seg = model.bones[fs.bone].tag
            seg_n = 5
            # position along the whole feather (0 base .. 1 tip)
            along = (seg + (1 - fs.t if fs.face in ("left", "right") else 0.5)) / seg_n
            if fs.face in ("left", "right"):
                across = np.abs(fs.s - 0.5) * 2
            else:
                across = np.full(N, 0.6)
            lvl = 0.55 + 0.25 * along - 0.22 * across ** 2 + 0.05 * noise
            if fs.face in ("left", "right"):
                vein = (np.abs(fs.s - 0.5) < 0.2) & (along < 0.85)
                lvl = np.where(vein, lvl - 0.13, lvl)
            if fs.face == "down":
                lvl -= 0.15
            lvl -= 0.18 * (1 - blob.smoothstep(0.0, 0.25, along))
            rgb = paint.shade_to_ramp(lvl, pal["feather"], ui, vi, dither=0.35)
            cv.put(ui, vi, rgb)
    return cv.rgba.clip(0, 255).astype(np.uint8)


def paint_alpha(model):
    cv = paint.Canvas(model.tex_w, model.tex_h)
    for fs in paint.face_samples(model):
        if fs.tag != "eye" or fs.face != "front":
            continue
        ui, vi = fs.ui, fs.vi
        lu = ui - ui.min()
        lv = vi - vi.min()
        on = ((lv == 0) & (lu <= 1)) | ((lv == 1) & (lu == 2))
        core = on & (lu == 1)
        col = np.where(core[:, None], paint.hex_rgb("#ff4a3a")[None], paint.hex_rgb("#e8211c")[None])
        cv.put(ui[on], vi[on], col[on])
    return cv.rgba.clip(0, 255).astype(np.uint8)


if __name__ == "__main__":
    mdl = build_model()
    print(sum(1 for _ in mdl.cubes()), "cubes")
