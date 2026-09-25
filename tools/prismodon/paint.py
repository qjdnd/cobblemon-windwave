"""Procedural texture painter.

Every texel of the box-UV atlas is mapped back onto the model surface (rest
pose) and shaded from its 3D position/normal: hand-painted style gradients,
steel bevels and glints, glass panes, hexagonal scales on the throat and baked
ambient occlusion.  The same pass is run with the normal and shiny palettes;
the alpha texture is an emissive "alpha_eyes" layer (Cobblemon 1.8 style).
"""

import math

import numpy as np

from bedrock import Model

# ------------------------------------------------------------------ palettes
# normal colours sampled from the reference artwork (k-means)
NORMAL = {
    "skin_dd": (84, 101, 95),
    "skin_d": (98, 117, 110),
    "skin_md": (130, 149, 142),
    "skin_m": (157, 185, 173),
    "skin_l": (193, 220, 209),
    "skin_h": (208, 234, 223),
    "steel_dd": (112, 108, 108),
    "steel_d": (141, 135, 131),
    "steel_s": (169, 164, 158),
    "steel_m": (201, 200, 196),
    "steel_l": (216, 215, 211),
    "steel_h": (230, 230, 225),
    "steel_w": (246, 246, 242),
    "glass_dd": (88, 58, 84),
    "glass_d": (116, 78, 108),
    "glass_m": (142, 104, 134),
    "glass_l": (164, 124, 156),
    "glass_h": (206, 184, 202),
    "orange_d": (140, 78, 48),
    "orange_m": (182, 108, 70),
    "orange_l": (214, 134, 88),
    "orange_h": (236, 172, 124),
    "claw_d": (128, 125, 121),
    "claw_m": (180, 178, 172),
    "claw_l": (212, 210, 204),
    "iris_d": (52, 104, 90),
    "iris": (96, 164, 142),
    "iris_l": (168, 222, 200),
    "eye_k": (18, 20, 22),
    "pupil": (14, 30, 26),
    "glint": (236, 248, 244),
    "mouth_d": (84, 50, 78),
    "mouth_m": (122, 76, 112),
    "mouth_l": (150, 100, 138),
}

SHINY = dict(NORMAL)
SHINY.update({
    # dusty desert sand hide
    "skin_dd": (122, 96, 64),
    "skin_d": (143, 114, 78),
    "skin_md": (170, 142, 100),
    "skin_m": (198, 172, 126),
    "skin_l": (228, 209, 168),
    "skin_h": (240, 225, 190),
    # sapphire glass
    "glass_dd": (30, 50, 110),
    "glass_d": (44, 74, 148),
    "glass_m": (62, 104, 184),
    "glass_l": (88, 140, 214),
    "glass_h": (178, 216, 246),
    # crimson spikes
    "orange_d": (122, 30, 48),
    "orange_m": (168, 48, 66),
    "orange_l": (206, 78, 92),
    "orange_h": (232, 128, 132),
    # amber eyes
    "iris_d": (150, 92, 24),
    "iris": (214, 152, 48),
    "iris_l": (246, 214, 120),
    "pupil": (46, 24, 8),
    "mouth_d": (70, 44, 88),
    "mouth_m": (104, 70, 128),
    "mouth_l": (132, 98, 156),
})

ALPHA_EYES = {
    "iris": (194, 36, 63),
    "iris_d": (167, 0, 51),
    "iris_l": (223, 72, 80),
    "glint": (240, 110, 110),
    "pupil": (109, 0, 11),
}


def C(pal, key):
    return np.array(pal[key], dtype=float)


def mix(a, b, t):
    t = np.clip(np.asarray(t, dtype=float), 0.0, 1.0)
    if t.ndim == 1:
        t = t[:, None]
    return a * (1 - t) + b * t


def smooth(e0, e1, x):
    t = np.clip((np.asarray(x, dtype=float) - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def hash2(x, y, seed=0):
    h = (x.astype(np.int64) * 374761393 + y.astype(np.int64) * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def value_noise3(P, scale, seed=0):
    """Smooth 3D value noise in [0, 1]."""
    p = P / scale
    i = np.floor(p).astype(np.int64)
    f = p - i
    f = f * f * (3 - 2 * f)

    def h(dx, dy, dz):
        x, y, z = i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz
        v = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (seed * 2654435761)
        v = (v * 2246822519) & 0xFFFFFFFF
        v = (v ^ (v >> 15)) & 0xFFFF
        return v / 65535.0

    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * h(dx, dy, dz)
    return out


def point_in_poly(z, y, poly, grow=0.0):
    """Vectorised point-in-convex-polygon with optional outward growth.
    Returns (inside mask, signed distance to border, positive inside)."""
    n = len(poly)
    # orientation
    area = 0
    for i in range(n):
        z0, y0 = poly[i]
        z1, y1 = poly[(i + 1) % n]
        area += z0 * y1 - z1 * y0
    sign = 1 if area > 0 else -1
    dmin = np.full(z.shape, np.inf)
    for i in range(n):
        z0, y0 = poly[i]
        z1, y1 = poly[(i + 1) % n]
        ez, ey = z1 - z0, y1 - y0
        ln = math.hypot(ez, ey)
        # inward normal
        nz, ny = -ey * sign / ln, ez * sign / ln
        d = (z - z0) * nz + (y - y0) * ny
        dmin = np.minimum(dmin, d)
    return dmin > -grow, dmin


def hex_border(u, v, R):
    """Distance to the nearest edge of a pointy-top hex grid of circumradius R."""
    # axial coordinates
    q = (math.sqrt(3) / 3 * u - 1.0 / 3 * v) / R
    r = (2.0 / 3 * v) / R
    x, z = q, r
    y = -x - z
    rx, ry, rz = np.round(x), np.round(y), np.round(z)
    dx, dy, dz = np.abs(rx - x), np.abs(ry - y), np.abs(rz - z)
    m1 = (dx > dy) & (dx > dz)
    m2 = (~m1) & (dy > dz)
    rx = np.where(m1, -ry - rz, rx)
    ry = np.where(m2, -rx - rz, ry)
    rz = np.where(~m1 & ~m2, -rx - ry, rz)
    cu = R * math.sqrt(3) * (rx + rz / 2)
    cv = R * 1.5 * rz
    pu, pv = u - cu, v - cv
    inner = R * math.sqrt(3) / 2
    d = np.zeros_like(u)
    for ang in (0, 60, 120):
        a = math.radians(ang)
        d = np.maximum(d, np.abs(pu * math.cos(a) + pv * math.sin(a)))
    return inner - d, cu, cv, pv


# ------------------------------------------------------------------ AO bake
def gather(m: Model):
    out = []
    for c in m.cubes():
        for smp in m.texels(c):
            smp["cube"] = c
            out.append(smp)
    return out


def occluder_boxes(m: Model):
    boxes = []
    for c in m.cubes():
        if not c.occluder or c.is_plane():
            continue
        frm, to = m.cube_bounds_bb(c)
        W = m.cube_world(c)
        inv = np.linalg.inv(W)
        corners = np.array([[x, y, z] for x in (frm[0], to[0]) for y in (frm[1], to[1]) for z in (frm[2], to[2])])
        wc = (W @ np.c_[corners, np.ones(8)].T).T[:, :3]
        center = wc.mean(0)
        radius = np.linalg.norm(wc - center, axis=1).max()
        boxes.append((c, inv, frm, to, center, radius))
    return boxes


def bake_ao(m: Model, samples, rays=40, max_dist=7.0, seed=3):
    rng = np.random.default_rng(seed)
    # cosine-weighted hemisphere directions (local, z-up)
    u1, u2 = rng.random(rays), rng.random(rays)
    rr = np.sqrt(u1)
    th = 2 * np.pi * u2
    local = np.stack([rr * np.cos(th), rr * np.sin(th), np.sqrt(1 - u1)], 1)
    boxes = occluder_boxes(m)
    for smp in samples:
        c = smp["cube"]
        n = len(smp["px"])
        if not c.occluder or smp["cube"].params.get("no_ao"):
            smp["ao"] = np.ones(n)
            continue
        P = smp["P"].copy()
        N = smp["N"][0].copy()
        P[:, 0] *= -1  # back to Blockbench space for the ray test
        N[0] *= -1
        # tangent frame
        a = np.array([0, 1, 0]) if abs(N[1]) < 0.9 else np.array([1, 0, 0])
        tx = np.cross(a, N)
        tx /= np.linalg.norm(tx)
        ty = np.cross(N, tx)
        dirs = local[:, 0:1] * tx + local[:, 1:2] * ty + local[:, 2:3] * N  # (rays, 3)
        O = P + N * 0.03
        occl = np.zeros((n, rays))
        for (bc, inv, frm, to, center, radius) in boxes:
            if bc is c:
                continue
            near = np.linalg.norm(O - center, axis=1) < radius + max_dist
            if not near.any():
                continue
            Oi = O[near]
            ol = (inv[:3, :3] @ Oi.T).T + inv[:3, 3]            # (k, 3)
            dl = (inv[:3, :3] @ dirs.T).T                        # (rays, 3)
            with np.errstate(divide="ignore", invalid="ignore"):
                invd = np.where(np.abs(dl) < 1e-9, 1e9, 1.0 / dl)
            t1 = (frm[None, None, :] - ol[:, None, :]) * invd[None, :, :]
            t2 = (to[None, None, :] - ol[:, None, :]) * invd[None, :, :]
            tmin = np.minimum(t1, t2).max(2)
            tmax = np.maximum(t1, t2).min(2)
            hit = (tmax >= np.maximum(tmin, 0)) & (tmin < max_dist)
            dist = np.clip(np.maximum(tmin, 0), 0, max_dist)
            w = np.where(hit, 1.0 - (dist / max_dist) ** 0.8, 0.0)
            occl[near] = np.maximum(occl[near], w)
        smp["ao"] = 1.0 - occl.mean(1)


# ------------------------------------------------------------------ materials
def light_term(smp):
    N = smp["N"]
    return 0.93 + 0.07 * N[:, 1]


def edge_dist(smp):
    s, t, fw, fh = smp["s"], smp["t"], smp["fw"], smp["fh"]
    top = t * fh
    bottom = (1 - t) * fh
    left = s * fw
    right = (1 - s) * fw
    return top, bottom, left, right


def mat_skin(smp, pal):
    P, N, c = smp["P"], smp["N"], smp["cube"]
    part = c.params.get("part", "body")
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    n = len(x)
    mott = value_noise3(P, 2.4, seed=1)
    up = smooth(-0.1, 0.9, N[:, 1])
    down = smooth(-0.1, -0.9, N[:, 1])
    col = np.tile(C(pal, "skin_md"), (n, 1))
    if part in ("body", "chest"):
        front = smooth(8, -15, z)                          # 1 at the chest
        barrel = smooth(8.5, 12.5, y) * (1 - smooth(18.5, 22.5, y))
        col = mix(col, C(pal, "skin_m"), 0.9 * smooth(9, 16, y) * (1 - down))
        col = mix(col, C(pal, "skin_d"), 0.45 * smooth(13, 9, y) * (1 - up))
        col = mix(col, C(pal, "skin_l"), 0.9 * front * barrel * (1 - up) * (1 - down))
        col = mix(col, C(pal, "skin_h"), 0.55 * front * barrel * smooth(0.3, 0.9, -N[:, 2]))
        col = mix(col, C(pal, "skin_d"), 0.55 * smooth(12, 8, y) + 0.35 * smooth(4, 17, z) * (1 - up))
        col = mix(col, C(pal, "skin_md"), 0.35 * up * smooth(-6, 10, z))
    elif part in ("leg", "shin", "foot"):
        col = mix(col, C(pal, "skin_m"), 0.5 * smooth(0.0, -0.9, N[:, 2]) * smooth(4, 11, y))
        col = mix(col, C(pal, "skin_d"), 0.7 * smooth(6.5, 1.0, y))
        col = mix(col, C(pal, "skin_dd"), 0.6 * down + 0.35 * smooth(0.2, 0.9, N[:, 2]))
    elif part == "neck":
        frontal = smooth(0.2, -0.9, N[:, 2])
        side = 1 - frontal
        col = mix(col, C(pal, "skin_m"), 0.55 * frontal + 0.25 * up)
        col = mix(col, C(pal, "skin_l"), 0.8 * frontal * smooth(26, 17, y))
        col = mix(col, C(pal, "skin_d"), 0.45 * smooth(-0.1, 0.9, N[:, 2]) + 0.2 * side * smooth(24, 32, y))
    elif part in ("skull", "nape"):
        col = mix(col, C(pal, "skin_d"), 0.35 + 0.4 * down)
    elif part == "tailbase":
        col = mix(col, C(pal, "skin_d"), 0.35 + 0.4 * smooth(15, 12, y))
    mott2 = value_noise3(P, 1.1, seed=5)
    col = col * (0.94 + 0.08 * mott + 0.05 * mott2)[:, None]
    # pixel-art form cues: lit upper rim, shaded lower rim on side faces
    top, bottom, left, right = edge_dist(smp)
    if smp["face"] not in ("up", "down"):
        col = mix(col, C(pal, "skin_l"), 0.35 * (top < 1) * (y > 9))
        col = mix(col, C(pal, "skin_dd"), 0.4 * (bottom < 1))
    elif smp["face"] == "up":
        col = mix(col, C(pal, "skin_l"), 0.25 * ((top < 1) | (bottom < 1) | (left < 1) | (right < 1)))
    # pebbly hide: sparse darker / lighter specks
    r1 = hash2(smp["px"], smp["py"], 41)
    r2 = hash2(smp["px"] * 3 + 1, smp["py"] * 7 + 2, 43)
    col = mix(col, C(pal, "skin_d"), 0.45 * (r1 < 0.05))
    col = mix(col, C(pal, "skin_l"), 0.35 * (r2 < 0.035) * (y > 8))
    if c.params.get("hex") and part == "neck":
        col = hex_pattern(smp, col, pal)
    elif c.params.get("hex"):
        col = crack_pattern(smp, col, pal)
    return col, np.full(n, 255.0)


def crack_pattern(smp, col, pal):
    """A few hairline cracks continuing the throat scales onto the chest."""
    P, face = smp["P"], smp["face"]
    if face != "north":
        return col
    x, y = P[:, 0], P[:, 1]
    lines = np.zeros(len(x), dtype=bool)
    for x0, x1, y0, y1 in ((-2.5, -3.5, 19.5, 16.0), (2.5, 3.6, 19.5, 15.5), (-3.5, -5.5, 16.0, 14.0),
                           (3.6, 5.2, 15.5, 13.0), (0.0, 0.3, 19.5, 17.0)):
        t = np.clip((y - y0) / (y1 - y0), 0, 1)
        xl = x0 + (x1 - x0) * t
        lines |= (np.abs(x - xl) < 0.5) & (y <= max(y0, y1)) & (y >= min(y0, y1))
    return mix(col, C(pal, "skin_md"), 0.8 * lines)


def hex_pattern(smp, col, pal):
    P, c = smp["P"], smp["cube"]
    x, y, z = P[:, 0], P[:, 1], P[:, 2]
    face = smp["face"]
    o, s = c.origin, c.size
    zfront = o[2]
    half = s[0] / 2.0
    if face == "north":
        u = x
    elif face in ("east", "west"):
        side = np.sign(x)
        u = side * (half + (z - zfront))
    else:
        return col
    R = 2.75
    border, cu, cv, pv = hex_border(u, y - 1.0, R)
    # the scales only cover the throat: fade out around the neck sides
    around = np.abs(u) - half
    cover = smooth(3.8, 1.2, around) if face != "north" else np.ones_like(u)
    cover = cover * smooth(33, 29, y) * smooth(16.5, 19.5, y)
    # break some edges to look like cracked plates
    rnd = hash2(np.round(cu * 3).astype(int), np.round(cv * 3).astype(int), 7)
    line = (border < 0.42) & (cover > 0.35) & ((rnd > 0.12) | (cover > 0.8))
    lit = (pv > 0.3 * R) & (border >= 0.42) & (cover > 0.35)
    col = mix(col, C(pal, "skin_h"), 0.35 * lit * cover)
    col = mix(col, C(pal, "skin_dd"), 0.85 * line)
    return col


def steel_base(smp, pal, glint=True):
    s, t, N, face = smp["s"], smp["t"], smp["N"], smp["face"]
    fw, fh = smp["fw"], smp["fh"]
    n = len(s)
    top, bottom, left, right = edge_dist(smp)
    col = np.tile(C(pal, "steel_m"), (n, 1))
    if face == "up":
        col = mix(col, C(pal, "steel_l"), 0.85)
    elif face == "down":
        col = mix(col, C(pal, "steel_d"), 0.75)
    else:
        # polished metal: bright upper third, mid band, dark lower third
        col = mix(col, C(pal, "steel_h"), 0.9 * smooth(0.42, 0.12, t))
        col = mix(col, C(pal, "steel_s"), 0.9 * smooth(0.55, 0.9, t))
        col = mix(col, C(pal, "steel_d"), 0.5 * smooth(0.85, 1.0, t))
    # plates rotated to face down / up
    col = mix(col, C(pal, "steel_s"), 0.4 * smooth(-0.3, -0.95, N[:, 1]) * (face != "down"))
    col = mix(col, C(pal, "steel_h"), 0.3 * smooth(0.4, 0.95, N[:, 1]) * (face != "up"))
    if glint and face != "down" and fw >= 4 and fh >= 3:
        # 2px diagonal reflection stripe
        u = s * fw - 0.55 * t * fh
        stripe = (np.abs(u - 0.3 * fw) < 1.0) & (t > 0.08) & (t < 0.8)
        col = mix(col, C(pal, "steel_w"), 0.55 * stripe)
    if face not in ("up", "down"):
        col = mix(col, C(pal, "steel_w"), 0.85 * (top < 1))
        col = mix(col, C(pal, "steel_dd"), 0.7 * (bottom < 1))
        col = mix(col, C(pal, "steel_s"), 0.35 * ((left < 1) | (right < 1)) * (top >= 1) * (bottom >= 1))
    else:
        edge = (top < 1) | (bottom < 1) | (left < 1) | (right < 1)
        col = mix(col, C(pal, "steel_w" if face == "up" else "steel_dd"), 0.55 * edge)
    d = hash2(smp["px"], smp["py"], 21) - 0.5
    return col * (1 + 0.05 * d)[:, None]


def rivets(smp, col, pal, points):
    """Paint 1-texel rivets (dark dot, bright upper-left pixel) at face-space points (s, t)."""
    fw, fh = smp["fw"], smp["fh"]
    pxs = np.floor(smp["s"] * fw)
    pys = np.floor(smp["t"] * fh)
    for (rs, rt) in points:
        cx, cy = math.floor(rs * fw), math.floor(rt * fh)
        dot = (pxs == cx) & (pys == cy)
        col = mix(col, C(pal, "steel_dd"), 0.85 * dot)
        hi = (pxs == cx - 1) & (pys == cy - 1)
        col = mix(col, C(pal, "steel_w"), 0.8 * hi)
    return col


def mat_steel(smp, pal):
    P, N, c, face = smp["P"], smp["N"], smp["cube"], smp["face"]
    s, t = smp["s"], smp["t"]
    L = smp["L"]
    n = len(s)
    prm = c.params
    col = steel_base(smp, pal)
    y, z = P[:, 1], P[:, 2]
    if prm.get("band"):
        # two grooves / a ridge running around the bracer
        ly = L[:, 1]
        side_face = face not in ("up", "down")
        if not prm.get("ridge"):
            col = mix(col, C(pal, "steel_s"), 0.55 * (np.abs(ly - c.size[1] / 2 + 0.5) < 0.5) * side_face)
        if side_face and smp["fw"] >= 7:
            col = rivets(smp, col, pal, [(0.2, 0.3), (0.8, 0.3)])
        if prm.get("ridge"):
            col = mix(col, C(pal, "steel_w"), 0.7 * (np.abs(ly - 4.5) < 0.5) * side_face)
            col = mix(col, C(pal, "steel_d"), 0.6 * (np.abs(ly - 3.5) < 0.5) * side_face)
            col = mix(col, C(pal, "steel_s"), 0.5 * (np.abs(ly - 1.5) < 0.5) * side_face)
        if face in ("up",):
            col = mix(col, C(pal, "steel_l"), 0.3)
    if prm.get("dorsal"):
        seg = (np.abs(((z + 10) % 5.0) - 0.5) < 0.5) & (face == "up")
        col = mix(col, C(pal, "steel_s"), 0.7 * seg)
        col = mix(col, C(pal, "steel_h"), 0.5 * ((((z + 10) % 5.0) > 1) & (((z + 10) % 5.0) < 2)) * (face == "up"))
    if prm.get("helmet"):
        # smooth cap: strong highlight on top-front, darker lower rim
        col = mix(col, C(pal, "steel_w"), 0.35 * smooth(0.5, 1.0, N[:, 1]) * smooth(-12, -19, z))
    if prm.get("socket") and face in ("east", "west"):
        # recessed eye socket under a bright brow ridge
        ez, ey = z + 16.5, y - 39.0
        r = np.sqrt((ez / 3.0) ** 2 + (ey / 1.75) ** 2)
        col = mix(col, C(pal, "steel_dd"), 0.9 * (r < 1.0))
        col = mix(col, C(pal, "steel_d"), 0.55 * (r >= 1.0) * (r < 1.4) * (ey < 0.3))
        col = mix(col, C(pal, "steel_w"), 0.85 * (r >= 1.0) * (r < 1.45) * (ey >= 0.3))
    if "beak" in prm:
        col = mix(col, C(pal, "steel_s"), 0.18 * prm["beak"])
        if face == "down":
            col = mix(col, C(pal, "steel_d"), 0.5)
    if prm.get("cheek"):
        # jagged lower edge
        jag = (t > 0.8) & (hash2(smp["px"], smp["py"], 3) > 0.5)
        col = mix(col, C(pal, "steel_d"), 0.6 * jag)
    if prm.get("jaw"):
        if face == "up":
            # inside of the mouth: tongue & gums
            lz = L[:, 2]
            col = np.tile(C(pal, "mouth_m"), (n, 1))
            col = mix(col, C(pal, "mouth_l"), 0.6 * (np.abs(L[:, 0] - c.size[0] / 2) < 1.2))
            col = mix(col, C(pal, "mouth_d"), 0.7 * smooth(4, 8, lz))
            col = mix(col, C(pal, "steel_l"), 1.0 * (lz < 0.9) + 0.0)
        elif face == "down":
            col = mix(col, C(pal, "steel_d"), 0.35)
    if "tailcone" in prm:
        col = mix(col, C(pal, "steel_s"), 0.12 * prm["tailcone"])
    if prm.get("serration"):
        col = mix(col, C(pal, "steel_l"), 0.3)
    if prm.get("shoulder") and face in ("east", "west"):
        # convex plate: bright core, shaded towards the rim, dark outline
        top, bottom, left, right = edge_dist(smp)
        rim = np.minimum.reduce([top, bottom, left, right])
        cx = (s - 0.4) / 0.5
        cy = (t - 0.35) / 0.6
        core = np.exp(-(cx ** 2 + cy ** 2) * 1.6)
        col = mix(col, C(pal, "steel_h"), 0.55 * core)
        col = mix(col, C(pal, "steel_s"), 0.5 * smooth(0.4, 1.0, np.sqrt(cx ** 2 + cy ** 2)))
        col = mix(col, C(pal, "steel_dd"), 0.75 * (rim < 1) * (top >= 1))
        col = mix(col, C(pal, "steel_w"), 0.35 * (rim >= 1) * (rim < 2) * (t < 0.5))
        if not prm.get("cap"):
            col = rivets(smp, col, pal, [(0.2, 0.14), (0.8, 0.14), (0.2, 0.86), (0.8, 0.86)])
    return col, np.full(n, 255.0)


def mat_belly(smp, pal):
    P, face = smp["P"], smp["face"]
    n = len(P)
    z = P[:, 2]
    col = np.tile(C(pal, "steel_m"), (n, 1))
    col = mix(col, C(pal, "steel_s"), 0.35)
    seg = np.abs(((z + 11) % 3.0) - 0.0) < 1.0
    col = mix(col, C(pal, "steel_d"), 0.45 * seg * (face == "down"))
    if face in ("east", "west", "north", "south"):
        col = mix(col, C(pal, "steel_l"), 0.4)
    return col, np.full(n, 255.0)


def mat_glass(smp, pal):
    L, c = smp["L"], smp["cube"]
    prm = c.params
    o = c.origin
    z = L[:, 2] + o[2]
    y = L[:, 1] + o[1]
    n = len(z)
    poly = prm["poly"]
    inside, dist = point_in_poly(z, y, poly, grow=0.6)
    (bz, by), (tz, ty) = prm["axis"]
    az, ay = tz - bz, ty - by
    alen = math.hypot(az, ay)
    az, ay = az / alen, ay / alen
    along = ((z - bz) * az + (y - by) * ay) / alen       # 0 bottom .. 1 top
    across = (z - bz) * (-ay) + (y - by) * az            # >0 behind the axis? (sign by geometry)
    across = -across                                      # >0 = front / upper side
    col = np.tile(C(pal, "glass_d"), (n, 1))
    col = mix(col, C(pal, "glass_m"), 0.8 * smooth(0.0, 0.7, along))
    upper = smooth(-0.8, 0.6, across)
    col = mix(col, C(pal, "glass_l"), 0.9 * upper * smooth(0.12, 0.55, along))
    # glossy reflection band running along the pane
    streak = np.exp(-((across - 1.2) / 0.55) ** 2) * smooth(0.2, 0.45, along) * smooth(0.95, 0.7, along)
    col = mix(col, C(pal, "glass_h"), 0.9 * streak)
    col = mix(col, C(pal, "glass_dd"), 0.6 * smooth(0.22, -0.1, along))
    # soft inner shadow next to the frame
    col = mix(col, C(pal, "glass_dd"), 0.5 * (dist < 0.9) * (dist > -0.6))
    d = hash2(smp["px"], smp["py"], 33) - 0.5
    col = col * (1 + 0.04 * d)[:, None]
    alpha = np.where(inside, 255.0, 0.0)
    return col, alpha


def mat_orange(smp, pal):
    L, c, s, face = smp["L"], smp["cube"], smp["s"], smp["face"]
    n = len(s)
    k = c.params.get("spike", 0)
    h = (k + L[:, 1] / max(c.size[1], 1)) / 3.0
    col = mix(np.tile(C(pal, "orange_d"), (n, 1)), C(pal, "orange_m"), smooth(0.0, 0.5, h))
    col = mix(col, C(pal, "orange_l"), smooth(0.4, 0.95, h))
    col = mix(col, C(pal, "orange_h"), 0.6 * (s < 0.4) * (face in ("east", "west", "north", "south")) * smooth(0.3, 0.9, h))
    return col, np.full(n, 255.0)


def mat_claw(smp, pal):
    N, face, t = smp["N"], smp["face"], smp["t"]
    n = len(t)
    k = smp["cube"].params.get("claw", 0)
    top, bottom, left, right = edge_dist(smp)
    col = np.tile(C(pal, "claw_m"), (n, 1))
    col = mix(col, C(pal, "claw_l"), 0.75 * smooth(0.2, 0.9, N[:, 1]))
    col = mix(col, C(pal, "claw_d"), 0.85 * smooth(-0.1, -0.9, N[:, 1]))
    if face not in ("up", "down"):
        col = mix(col, C(pal, "claw_l"), 0.5 * (top < 1))
        col = mix(col, C(pal, "claw_d"), 0.6 * (bottom < 1))
    if k == 0:
        # darker where the claw leaves the toe
        col = mix(col, C(pal, "skin_dd"), 0.55 * (face in ("east", "west")) * (right < 0.9))
    return col * 0.94, np.full(n, 255.0)


def mat_mouth(smp, pal):
    L = smp["L"]
    n = len(L)
    col = np.tile(C(pal, "mouth_d"), (n, 1))
    col = mix(col, C(pal, "mouth_m"), 0.6 * smooth(6, 1, L[:, 2]))
    return col, np.full(n, 255.0)


# 5 x 3 eye, columns from the front (-Z) to the back, rows bottom -> top
EYE_MAP = [
    ".kiik",
    "kIppk",
    "khIk.",
]
LID_MAP = [
    ".llll",
    "LLLLL",
    "LLLL.",
]


def pixel_map(smp, rows):
    L = smp["L"]
    col_i = np.clip(np.floor(L[:, 2]).astype(int), 0, len(rows[0]) - 1)
    row_i = np.clip(np.floor(L[:, 1]).astype(int), 0, len(rows) - 1)
    return np.array([rows[r][c] for r, c in zip(row_i, col_i)])


def mat_eye(smp, pal):
    keys = pixel_map(smp, EYE_MAP)
    n = len(keys)
    col = np.zeros((n, 3))
    alpha = np.full(n, 255.0)
    table = {"k": "eye_k", "i": "iris", "I": "iris_l", "p": "pupil", "h": "glint"}
    for ch, key in table.items():
        col[keys == ch] = C(pal, key)
    alpha[keys == "."] = 0
    return col, alpha


def mat_eyelid(smp, pal):
    keys = pixel_map(smp, LID_MAP)
    n = len(keys)
    col = np.tile(C(pal, "skin_md"), (n, 1))
    col[keys == "l"] = C(pal, "skin_d")
    alpha = np.where(keys == ".", 0.0, 255.0)
    return col, alpha


MATERIALS = {
    "skin": mat_skin,
    "steel": mat_steel,
    "belly": mat_belly,
    "glass": mat_glass,
    "orange": mat_orange,
    "claw": mat_claw,
    "eye": mat_eye,
    "eyelid": mat_eyelid,
    "mouth": mat_mouth,
}
UNLIT = {"eye", "eyelid", "glass"}


def paint(m: Model, samples, pal, seed=11):
    img = np.zeros((m.tex_h, m.tex_w, 4))
    for smp in samples:
        c = smp["cube"]
        col, alpha = MATERIALS[c.mat](smp, pal)
        if c.mat not in UNLIT:
            ao = smp.get("ao", np.ones(len(col)))
            shade = light_term(smp) * (0.55 + 0.45 * ao)
            col = col * shade[:, None]
            # tiny per-pixel dither so large faces don't look flat
            d = hash2(smp["px"], smp["py"], seed) - 0.5
            col = col * (1 + 0.035 * d)[:, None]
        elif c.mat == "glass":
            ao = smp.get("ao", np.ones(len(col)))
            d = hash2(smp["px"], smp["py"], seed) - 0.5
            col = col * (1 + 0.03 * d)[:, None]
        px, py = smp["px"], smp["py"]
        ok = (px >= 0) & (px < m.tex_w) & (py >= 0) & (py < m.tex_h)
        img[py[ok], px[ok], :3] = col[ok]
        img[py[ok], px[ok], 3] = alpha[ok]
    return np.round(img)


def paint_alpha(m: Model, samples):
    img = np.zeros((m.tex_h, m.tex_w, 4))
    for smp in samples:
        c = smp["cube"]
        if c.mat != "eye":
            continue
        keys = pixel_map(smp, EYE_MAP)
        table = {"i": "iris", "I": "iris_l", "p": "pupil", "h": "glint"}
        for ch, key in table.items():
            sel = keys == ch
            img[smp["py"][sel], smp["px"][sel], :3] = ALPHA_EYES[key]
            img[smp["py"][sel], smp["px"][sel], 3] = 255
    return img


def paint_all(m: Model):
    samples = gather(m)
    bake_ao(m, samples)
    return {
        "normal": paint(m, samples, NORMAL),
        "shiny": paint(m, samples, SHINY),
        "alpha": paint_alpha(m, samples),
    }
