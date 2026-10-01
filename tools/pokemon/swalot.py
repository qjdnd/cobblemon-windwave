"""Swalot (#317) for Cobblemon 1.8.1 - model and textures."""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from cobblegen import geom, blob, paint  # noqa: E402

NAME = "swalot"
DEX = "0317_swalot"
PREVIEW_SIZE = (460, 460)

H = 30.0
DEPTH = 0.88  # depth / width ratio of the body cross-section


def half_width(y):
    """Bell profile: flared skirt, slightly tapering sides, rounded dome."""
    if y < 2.0:
        return 13.0
    if y < 4.0:
        return 13.0 - 0.5 * (y - 2.0)
    if y < 18.0:
        return 12.0 - 1.0 * (y - 4.0) / 14.0
    k = min(1.0, (y - 18.0) / (H - 18.0))
    return 11.0 * max(0.0, 1 - k ** 2.7) ** (1 / 2.7)


LAYERS = [
    # (y0, y1, ring count, sample height)
    (0, 3, 3, 1.0),
    (3, 10, 3, 5.0),
    (10, 17, 3, 12.0),
    (17, 21, 3, 19.5),
    (21, 24, 3, 22.8),
    (24, 26, 3, 25.0),
    (26, 28, 2, 26.9),
    (28, 29, 2, 28.4),
    (29, 30, 1, 29.3),
]

EYE_X = 4.6
EYE_Y = 26.4
ARM_Y = 13.0
DIAMOND_Y = 8.2


def body_field(p):
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    a = np.array([max(half_width(v), 0.35) for v in np.clip(y, 0, H)])
    b = a * DEPTH
    r = ((np.abs(x) / a) ** 2.4 + (np.abs(z) / b) ** 2.4) ** (1 / 2.4)
    over = np.clip(y - H, 0, None)
    return r - 1 + over * 0.5


def build_model():
    m = geom.Model(NAME, 256, 256)
    m.visible_bounds = (3, 3.5, (0, 1.25, 0))
    root = m.bone(NAME, None, [0, 0, 0])
    root.locator("root", [0, 0, 0])
    top = m.bone("locator_top", NAME, [0, 0, 0])
    top.locator("top", [0, H + 1, 0])
    m.bone("body", NAME, [0, 0, 0])
    skirt = m.bone("skirt", "body", [0, 0, 0])
    lower = m.bone("lower", "body", [0, 3, 0])
    upper = m.bone("upper", "lower", [0, 10, 0])
    head = m.bone("head", "upper", [0, 17, 0])
    targets = {0: skirt, 3: lower, 10: upper, 17: head, 21: head, 24: head, 26: head, 28: head, 29: head}

    for (y0, y1, cnt, ys) in LAYERS:
        a = half_width(ys)
        blob.ring_boxes(targets[y0], y0, y1, a, a * DEPTH, a * DEPTH, n=2.4, count=cnt, tag="body")

    # scalloped skirt lobes, sharing one UV island
    first = None
    lobes = m.bone("skirt_lobes", "skirt", [0, 0, 0])
    for k in range(12):
        phi = 30.0 * k + 15.0
        pr = math.radians(phi)
        # radius of the skirt superellipse in this direction
        dx, dz = -math.sin(pr), -math.cos(pr)
        a = 13.0
        b = 13.0 * DEPTH
        r = 1.0 / ((abs(dx) / a) ** 2.4 + (abs(dz) / b) ** 2.4) ** (1 / 2.4)
        cx, cz = dx * (r + 0.1), dz * (r + 0.1)
        c = lobes.add([cx - 3, 0, cz - 1.5], [6, 3, 3], tag="lobe", rotation=[0, phi, 0], pivot=[cx, 1.5, cz],
                      inflate=0.1, share=first)
        if first is None:
            first = c

    # arms: three fat fingers, attached a little forward of the sides
    def arm_root(sign):
        ang = math.radians(62)
        a = half_width(ARM_Y)
        b = a * DEPTH
        dx, dz = sign * math.sin(ang), -math.cos(ang)
        r = 1.0 / ((abs(dx) / a) ** 2.4 + (abs(dz) / b) ** 2.4) ** (1 / 2.4)
        return dx * r, dz * r

    ax, az = arm_root(1)
    left = m.bone("arm_left", "upper", [ax - 0.8, ARM_Y, az])
    right = m.bone("arm_right", "upper", [-(ax - 0.8), ARM_Y, az])
    lc = []
    fingers = [((1.9, 1.3, -2.0), (5, 5, 5)), ((2.2, 1.6, 1.6), (5, 5, 5)), ((1.7, -1.6, -0.3), (5, 5, 5)),
               ((0.3, 0.0, 0.0), (4, 4, 4))]
    for (o, s) in fingers:
        lc += geom.rounded_blob(left, (ax + o[0], ARM_Y + o[1], az + o[2]), s, "arm", steps=0.5)
    for cu in lc:
        o = cu.origin
        right.add([-(o[0] + cu.size[0]), o[1], o[2]], cu.size, mirror=True, share=cu, tag="arm")

    # face --------------------------------------------------------------
    face = m.bone("face", "head", [0, 24, -9])
    zs = [blob.front_z(m, x, y) for x in (EYE_X - 1, EYE_X + 1) for y in (EYE_Y - 1, EYE_Y + 1)]
    ez = min(z for z in zs if z is not None)
    eyes = m.bone("eyes", "face", [0, EYE_Y, ez])
    eye_l = m.bone("eye_left", "eyes", [EYE_X, EYE_Y, ez - 0.1])
    e = eye_l.add([EYE_X - 1, EYE_Y - 1, ez - 0.35], [2, 2, 1], tag="eye", inflate=-0.1)
    eye_l.locator("eye2", [EYE_X, EYE_Y, ez - 0.5])
    lid_l = m.bone("eyelid_left", "eye_left", [EYE_X, EYE_Y, ez])
    lid = lid_l.add([EYE_X - 1.5, EYE_Y - 1.5, ez - 0.05], [3, 3, 1], tag="eyelid")
    eye_r = m.bone("eye_right", "eyes", [-EYE_X, EYE_Y, ez - 0.1])
    eye_r.add([-(e.origin[0] + e.size[0]), e.origin[1], e.origin[2]], e.size, mirror=True, share=e, tag="eye", inflate=-0.1)
    eye_r.locator("eye1", [-EYE_X, EYE_Y, ez - 0.5])
    lid_r = m.bone("eyelid_right", "eye_right", [-EYE_X, EYE_Y, ez])
    lid_r.add([-(lid.origin[0] + lid.size[0]), lid.origin[1], lid.origin[2]], lid.size, mirror=True, share=lid, tag="eyelid")

    mz = blob.front_z(m, 0, 24.0)
    mouth = m.bone("mouth", "face", [0, 24.0, mz])
    inner = m.bone("mouth_inner", "mouth", [0, 24.0, mz])
    inner.add([-2.5, 22.5, mz - 0.05], [5, 3, 0], tag="mouth")
    lip_top = m.bone("lip_top", "mouth", [0, 24.6, mz - 0.5])
    geom.rounded_blob(lip_top, (0, 26.1, mz - 1.8), (7, 4, 4), "lip", steps=0.5)
    lip_bottom = m.bone("lip_bottom", "mouth", [0, 23.4, mz - 0.5])
    geom.rounded_blob(lip_bottom, (0, 21.8, mz - 1.6), (6, 4, 4), "lip", steps=0.5)
    # puffy corners where the whiskers grow
    corner_l = m.bone("lip_corner_left", "mouth", [3.0, 23.6, mz - 0.5])
    cc = geom.rounded_blob(corner_l, (3.4, 23.6, mz - 1.0), (3, 3, 3), "lip", steps=0.5)
    corner_r = m.bone("lip_corner_right", "mouth", [-3.0, 23.6, mz - 0.5])
    for cu in cc:
        o = cu.origin
        corner_r.add([-(o[0] + cu.size[0]), o[1], o[2]], cu.size, mirror=True, share=cu, tag="lip")

    # whiskers: hang from the mouth corners, then curl outwards ---------------
    segs = [(5, -6), (4, -30), (4, -38), (3, -24)]  # (length, z-rotation for the left side)
    for side, sign in (("left", 1), ("right", -1)):
        parent = "lip_corner_" + side
        x = sign * 4.4
        y = 23.0
        z = mz - 1.2
        for i, (ln, rz) in enumerate(segs):
            name = "whisker_%s%s" % (side, "" if i == 0 else str(i + 1))
            b = m.bone(name, parent, [x, y, z], [0, 0, rz * sign])
            if sign > 0:
                c = b.add([x - 0.5, y - ln, z - 0.5], [1, ln, 1], tag="whisker", inflate=0.05)
                c.seg = i
            else:
                src = m.bones["whisker_left%s" % ("" if i == 0 else str(i + 1))].cubes[0]
                b.add([x - 0.5, y - ln, z - 0.5], [1, ln, 1], tag="whisker", inflate=0.05, mirror=True, share=src)
            parent = name
            y -= ln
    m.pack()
    return m


# --------------------------------------------------------------- palettes
PALETTES = {
    "normal": {
        "body": paint.ramp("#3a3168", "#463c7e", "#534893", "#6155a6", "#6f63b8", "#7e72c8", "#8e83d4",
                           "#9f95df", "#b2a9e9"),
        "diamond": paint.ramp("#121017", "#1b1822", "#26222f"),
        "eye": ("#e3405f", "#ff9fb4", "#9c1f3b"),
        "whisker": paint.ramp("#b48a28", "#cfa435", "#e4bc44", "#f2d055", "#fadf68", "#ffec8c"),
        "mouth": paint.ramp("#150a10", "#26101c", "#3a1829"),
    },
    "shiny": {
        "body": paint.ramp("#284684", "#315497", "#3b62aa", "#4671bc", "#5281cb", "#6191d8", "#72a2e3",
                           "#86b3ec", "#9dc5f4"),
        "diamond": paint.ramp("#28262c", "#333137", "#3f3d44"),
        "eye": ("#ee6d9c", "#ffd0e2", "#a8325f"),
        "whisker": paint.ramp("#a1501d", "#bd6629", "#d67d36", "#e89445", "#f4aa59", "#fbc47c"),
        "mouth": paint.ramp("#0e0b18", "#1a1430", "#281e45"),
    },
}

LIGHT = np.array([0.0, 0.86, -0.5])
LIGHT /= np.linalg.norm(LIGHT)
VIEW = np.array([0.0, 0.25, -1.0])
VIEW /= np.linalg.norm(VIEW)
HALF = (LIGHT + VIEW) / np.linalg.norm(LIGHT + VIEW)


def _shade(n, p, ao, spec_amt=0.16, gloss=10.0):
    d = np.clip(n @ LIGHT, -1, 1)
    s = np.clip(n @ HALF, 0, 1) ** gloss
    g = np.clip(p[:, 1] / H, 0, 1)
    return 0.58 + 0.15 * d + 0.12 * g + spec_amt * s - 0.34 * (1 - ao)


def _centers(model, tag):
    out = []
    for c in model.cubes():
        if c.tag == tag and c.share is None and c.rotation is None:
            o, s = c.origin, c.size
            out.append([o[0] + s[0] / 2, o[1] + s[1] / 2, o[2] + s[2] / 2])
    uniq = []
    for c in out:
        if not any(np.linalg.norm(np.array(c) - u) < 0.6 for u in uniq):
            uniq.append(np.array(c))
    return np.array(uniq)


def diamond_mask(p, y0=DIAMOND_Y, hw=4.3, hh=5.1):
    ang = np.degrees(np.arctan2(p[:, 0], -p[:, 2]))  # 0 = front, +90 = left side
    r = np.hypot(p[:, 0], p[:, 2])
    out = np.zeros(len(p))
    for c in (0.0, 90.0, 180.0, -90.0):
        d = (ang - c + 180.0) % 360.0 - 180.0
        du = np.radians(d) * r
        v = np.abs(du) / hw + np.abs(p[:, 1] - y0) / hh
        out = np.maximum(out, 1 - v)
    return out  # >0 inside


def paint_textures(model, palette, seed=11):
    pal = PALETTES[palette]
    cv = paint.Canvas(model.tex_w, model.tex_h)
    arms = _centers(model, "arm")
    arms = np.vstack([arms, arms * np.array([-1, 1, 1])])
    lips = _centers(model, "lip")
    lips = np.vstack([lips, lips * np.array([-1, 1, 1])])
    for fs in paint.face_samples(model):
        p = fs.pos
        N = len(p)
        ui, vi = fs.ui, fs.vi
        tag = fs.tag
        noise = paint.fbm(p * np.array([1, 1.3, 1]), 4.0, 3, seed) - 0.5
        if tag in ("body", "lobe", "eyelid"):
            if tag == "lobe":
                n = 0.55 * blob.implicit_normal(body_field, p) + 0.45 * np.repeat(fs.normal[None], N, 0)
                n /= np.linalg.norm(n, axis=1, keepdims=True)
            else:
                n = blob.implicit_normal(body_field, p)
            ao = blob.smoothstep(-0.3, 3.0, p[:, 1]) * 0.5 + 0.5
            if fs.face == "down":
                ao *= 0.6
            for c in arms:
                dd = np.linalg.norm(p - c, axis=1)
                ao *= 1 - 0.5 * (1 - blob.smoothstep(2.2, 4.4, dd))
            for c in lips:
                dd = np.linalg.norm((p - c) * np.array([0.8, 1.0, 1.0]), axis=1)
                ao *= 1 - 0.45 * (1 - blob.smoothstep(2.0, 4.0, dd))
            lvl = _shade(n, p, ao) + 0.07 * noise
            rgb = paint.shade_to_ramp(lvl, pal["body"], ui, vi, dither=0.55)
            if tag == "body":
                dm = diamond_mask(p)
                inside = (dm > 0) & (fs.face != "up") & (fs.face != "down")
                if inside.any():
                    spec = np.clip(n @ HALF, 0, 1) ** 6
                    rim = dm < 0.12
                    dl = 0.15 + 0.5 * spec + np.where(rim, 0.35, 0.0)
                    drgb = paint.shade_to_ramp(dl, pal["diamond"], ui, vi, dither=0.0)
                    rgb = np.where(inside[:, None], drgb, rgb)
            if tag == "eyelid":
                lv = vi - vi.min()
                lash = lv == lv.max()
                lrgb = np.repeat(pal["body"][1][None], N, 0)
                rgb = np.where(lash[:, None], lrgb, rgb)
                if fs.face != "front":
                    continue
            cv.put(ui, vi, rgb)
        elif tag in ("arm", "lip"):
            centers = arms if tag == "arm" else lips
            dist = np.linalg.norm(p[:, None, :] - centers[None, :, :], axis=2)
            ci = centers[np.argmin(dist, axis=1)]
            n = blob.sphere_normal(p, ci)
            ao = np.ones(N)
            if tag == "arm":
                ao *= 1 - 0.4 * np.clip(-(n[:, 0] * np.sign(ci[:, 0])), 0, 1)
            else:
                ao *= 1 - 0.4 * np.clip(n[:, 2], 0, 1)
            ao *= 1 - 0.25 * np.clip(-n[:, 1], 0, 1)
            # crease between neighbouring bumps
            srt = np.sort(dist, axis=1)
            crease = blob.smoothstep(0.0, 0.9, srt[:, 1] - srt[:, 0]) if srt.shape[1] > 1 else np.ones(N)
            lvl = _shade(n, p, ao, spec_amt=0.2, gloss=6.0) + 0.06 + 0.05 * noise - 0.12 * (1 - crease)
            rgb = paint.shade_to_ramp(lvl, pal["body"], ui, vi, dither=0.5)
            cv.put(ui, vi, rgb)
        elif tag == "eye":
            red, hi, dark = (paint.hex_rgb(h) for h in pal["eye"])
            if fs.face == "front":
                lu = ui - ui.min()
                lv = vi - vi.min()
                col = np.where(((lu == 0) & (lv == 0))[:, None], hi[None], red[None])
                col = np.where(((lu == 1) & (lv == 1))[:, None], dark[None], col)
            else:
                col = np.repeat(dark[None], N, 0)
            cv.put(ui, vi, col)
        elif tag == "mouth":
            if fs.face != "front":
                continue
            lv = (vi - vi.min()) / max(1, vi.max() - vi.min())
            lu = np.abs((ui - ui.min()) / max(1, ui.max() - ui.min()) - 0.5) * 2
            lvl = 0.9 - lv * 0.45 - lu * 0.45
            cv.put(ui, vi, paint.shade_to_ramp(lvl, pal["mouth"], ui, vi, dither=0.3))
        elif tag == "whisker":
            seg = getattr(fs.cube, "seg", 0)
            along = (seg + (fs.t if fs.face not in ("up", "down") else 0.5)) / 4.0
            side = {"front": 0.1, "left": 0.0, "right": 0.0, "back": -0.15, "up": 0.2, "down": -0.25}[fs.face]
            lvl = 0.62 + side + 0.12 * (1 - along) + 0.05 * noise
            cv.put(ui, vi, paint.shade_to_ramp(lvl, pal["whisker"], ui, vi, dither=0.3))
    return cv.rgba.clip(0, 255).astype(np.uint8)


def paint_alpha(model):
    cv = paint.Canvas(model.tex_w, model.tex_h)
    for fs in paint.face_samples(model):
        if fs.tag != "eye":
            continue
        ui, vi = fs.ui, fs.vi
        if fs.face == "front":
            lu = ui - ui.min()
            lv = vi - vi.min()
            col = np.where(((lu == 0) & (lv == 0))[:, None], paint.hex_rgb("#ff8a70")[None], paint.hex_rgb("#ff2a20")[None])
        else:
            col = np.repeat(paint.hex_rgb("#d81414")[None], len(ui), 0)
        cv.put(ui, vi, col)
    return cv.rgba.clip(0, 255).astype(np.uint8)


if __name__ == "__main__":
    mdl = build_model()
    print(sum(1 for _ in mdl.cubes()), "cubes")
