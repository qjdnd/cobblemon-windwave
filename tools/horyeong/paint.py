"""
Texture painter for Horyeong.

Every texel of the box-UV atlas is mapped back to its 3D rest-pose position (using the exact
Minecraft cube/UV construction from cg.py) and painted by a material function. The material
step produces (class, tone) per texel; palettes then turn that into the normal / shiny textures,
so the shiny is a true palette swap of the same painting, like the official games.
"""
import math
import numpy as np
import cg

# ------------------------------------------------------------------ palettes
PAL_NORMAL = {
    "fur":       [(140, 58, 28), (178, 80, 36), (208, 104, 46), (226, 128, 60), (238, 152, 82), (246, 176, 108)],
    "stripe":    [(30, 22, 21), (44, 32, 29), (58, 43, 37), (72, 54, 45)],
    "cream":     [(196, 168, 128), (219, 197, 156), (236, 220, 186), (246, 236, 211), (252, 247, 232)],
    "white":     [(168, 173, 194), (198, 203, 218), (222, 226, 236), (238, 240, 246), (248, 249, 252), (255, 255, 255)],
    "nose":      [(170, 86, 98), (204, 120, 130), (226, 152, 160), (242, 186, 192)],
    "nostril":   [(92, 44, 54), (112, 56, 66)],
    "mouth":     [(70, 22, 30), (104, 34, 44), (134, 50, 60)],
    "tongue":    [(186, 82, 96), (214, 112, 124)],
    "iris":      [(176, 108, 22), (214, 148, 34), (238, 184, 58), (250, 214, 104)],
    "pupil":     [(24, 16, 14), (40, 28, 22)],
    "shine":     [(255, 252, 236)],
    "lash":      [(34, 24, 22), (50, 36, 32)],
    "inner_ear": [(206, 150, 140), (226, 178, 168)],
    "claw":      [(214, 206, 188), (238, 232, 216)],
}

PAL_SHINY = dict(PAL_NORMAL)
PAL_SHINY.update({
    # Baekho - the white tiger of the west
    "fur":    [(138, 146, 166), (168, 176, 194), (194, 201, 216), (216, 221, 233), (233, 236, 244), (246, 248, 252)],
    "stripe": [(28, 32, 48), (40, 46, 66), (54, 62, 86), (70, 80, 106)],
    "cream":  [(178, 188, 210), (202, 211, 229), (222, 229, 241), (238, 242, 249), (250, 252, 255)],
    # beard / brows / mustache become pale gold
    "white":  [(168, 128, 58), (196, 156, 78), (220, 184, 104), (236, 206, 134), (246, 224, 164), (253, 240, 196)],
    "iris":   [(40, 104, 170), (64, 142, 206), (110, 186, 236), (170, 222, 250)],
    "inner_ear": [(196, 170, 200), (220, 198, 224)],
})

PAL_ALPHA = {  # emissive red glow for alpha eyes
    "iris": [(196, 16, 16), (230, 30, 26), (255, 60, 48), (255, 110, 92)],
    "pupil": [(150, 0, 0), (170, 10, 10)],
    "shine": [(255, 200, 190)],
}

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0 - 0.5


def hash2(a, b, seed=0):
    h = (a.astype(np.int64) * 374761393 + b.astype(np.int64) * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def vnoise3(p, scale, seed=0):
    """cheap value noise in 3D (trilinear)"""
    q = p / scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)

    def h(dx, dy, dz):
        x = i[:, 0] + dx; y = i[:, 1] + dy; z = i[:, 2] + dz
        v = (x * 73856093 ^ y * 19349663 ^ z * 83492791 ^ seed * 2654435761) & 0xFFFFFFFF
        v = (v ^ (v >> 13)) * 1274126177 & 0xFFFFFFFF
        return ((v ^ (v >> 16)) & 0xFFFF) / 65535.0
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * h(dx, dy, dz)
    return out


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ texel sampling
class Texels:
    """All texels of one quad with their geometric context."""
    pass


def quad_texels(q, tex_w, tex_h):
    uvs = q["uvs"]
    uB, vA = uvs[0]
    uA, vB = uvs[2]
    if abs(uB - uA) < 1e-6 or abs(vB - vA) < 1e-6:
        return None
    u0, u1 = sorted((uA, uB)); v0, v1 = sorted((vA, vB))
    us = np.arange(int(math.floor(u0 + 1e-6)), int(math.ceil(u1 - 1e-6)))
    vs = np.arange(int(math.floor(v0 + 1e-6)), int(math.ceil(v1 - 1e-6)))
    if len(us) == 0 or len(vs) == 0:
        return None
    U, V = np.meshgrid(us, vs)
    U = U.ravel(); V = V.ravel()
    s = (U + 0.5 - uA) / (uB - uA)
    t = (V + 0.5 - vA) / (vB - vA)
    s = np.clip(s, 0, 1); t = np.clip(t, 0, 1)
    L0, L1, L2, L3 = [np.asarray(v) for v in q["local"]]
    W0, W1, W2, W3 = [np.asarray(v) for v in q["verts"]]
    a = ((1 - s) * (1 - t))[:, None]; b = (s * (1 - t))[:, None]; c = ((1 - s) * t)[:, None]; d = (s * t)[:, None]
    loc = a * L1 + b * L0 + c * L2 + d * L3
    wj = a * W1 + b * W0 + c * W2 + d * W3
    T = Texels()
    T.u, T.v = U, V
    T.pos = np.stack([wj[:, 0], -wj[:, 1], wj[:, 2]], 1)          # rest pose, bedrock space
    mn, dims = q["box"]
    dims_safe = np.where(np.abs(dims) < 1e-6, 1, dims)
    ln = (loc - mn) / dims_safe
    ln = np.where(np.abs(dims) < 1e-6, 0.5, ln)
    T.loc = np.stack([ln[:, 0], 1 - ln[:, 1], ln[:, 2]], 1)       # normalized box coords, bedrock orientation
    n = q["normal"]
    T.normal = np.array([n[0], -n[1], n[2]])
    T.face = cg.FACE_NAME[q["dir"]]
    T.cube = q["cube"]
    T.n = len(U)
    return T


# ------------------------------------------------------------------ masks for fur planes
def zig(x, period, amp, seed=0):
    """saw-tooth with jitter (for jagged fur edges)"""
    ph = x / period
    k = np.floor(ph)
    jit = hash2(k.astype(np.int64), np.full_like(k, 7, dtype=np.int64), seed) * 0.6 + 0.7
    return np.abs((ph - k) - 0.5) * 2 * amp * jit


def shape_mask(shape, ox, ly, W, H):
    """ox: 0 at inner/attached end -> 1 at outer end ; ly: 0 bottom -> 1 top. W,H plane size in px."""
    x = ox * W; y = ly * H
    if shape == "brow_tip":
        # long tuft drooping out-and-down, tapering to a point
        c = H * (0.62 - 0.42 * ox ** 1.3)
        half = H * 0.42 * (1 - ox) ** 0.85 + 0.15
        e = zig(x, 2.0, 0.9, 3)
        return np.abs(y - c) < half - e * (ox > 0.15)
    if shape == "cheek_tuft":
        # three spikes fanning outward/down
        m = np.zeros_like(x, dtype=bool)
        for k, (cy, sl, ln) in enumerate(((0.82, -0.12, 1.0), (0.5, -0.3, 0.92), (0.2, -0.3, 0.7))):
            cc = H * (cy + sl * ox)
            half = H * 0.24 * np.clip(1 - ox / ln, 0, 1) ** 0.7 + 0.2
            m |= (np.abs(y - cc) < half) & (ox < ln)
        m &= ~((zig(x, 1.6, 0.35, 23) > 0.28) & (ox > 0.5))
        return m
    if shape == "mustache_tip":
        top = H * (0.8 - 0.55 * ox ** 1.1)
        bot = H * (0.4 - 0.38 * ox ** 0.8)
        return (y < top + 0.3) & (y > bot - 0.2) & (ox < 0.97)
    if shape == "beard_tip":
        cx = W / 2
        half = (W / 2) * np.clip((ly - 0.02) / 0.98, 0, 1) ** 0.9
        e = zig(y, 2.0, 0.7, 5)
        return np.abs(x - cx) < half - e * (ly < 0.85)
    if shape == "beard_side":
        cx = W / 2
        half = W / 2 * (0.35 + 0.65 * smooth(0.0, 0.8, ly))
        e = zig(y, 2.0, 1.2, 9)
        bottom = ly > 0.04 + zig(x, 2.0, 0.12, 11)
        return (np.abs(x - cx) < half - e) & bottom
    if shape == "brow_top":
        # fluffy upper edge of the brow
        top = H * 0.62 + zig(x, 1.5, 0.9, 41)
        return (y < top) & (y > H * 0.15)
    if shape == "chest_tuft":
        e = zig(x, 2.0, 0.6, 13) * H + H * 0.15
        return y > e
    if shape == "ear_tuft":
        cx = W / 2
        top = H * (0.95 - 0.5 * np.abs(x - cx) / (W / 2)) - zig(x, 1.5, 0.12, 17) * H
        return (y < top) & (np.abs(x - cx) < W * 0.42)
    return np.ones_like(x, dtype=bool)


# ------------------------------------------------------------------ materials
def base_tone(T, light=0.0):
    """shading: vertical gradient within the cube + face orientation + per-texel grain."""
    ly = T.loc[:, 1]
    tone = 0.52 + 0.28 * (ly - 0.5)
    f = T.face
    if f == "top":
        tone = tone + 0.12
    elif f == "bottom":
        tone = tone - (0.12 if T.cube.tag in ("torso", "belly", "chest", "thigh", "neck") else 0.28)
    elif f == "back":
        tone = tone - 0.04
    grain = hash2(T.u, T.v, 1) - 0.5
    streak = hash2(T.u, np.zeros_like(T.v), 2) - 0.5
    tone = tone + 0.16 * grain + 0.08 * streak + light
    tone = tone + 0.07 * (vnoise3(T.pos, 3.0, 4) - 0.5)
    return tone


def body_stripes(p):
    """3D stripe field on the torso/rump (bands running down from the spine, sweeping back)."""
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    s = np.zeros(len(p), bool)
    centers = [-8.0, -4.0, 0.0, 4.0, 8.0, 11.5]
    for i, c in enumerate(centers):
        bend = 0.32 * (24.5 - y) + 0.5 * np.sin(y * 0.9 + i * 1.7)
        side_w = 0.95 * smooth(10.5 + (i % 2) * 1.5, 18, y) + 0.15
        top_w = np.where(np.abs(x) < 1.0, 0.55, 1.0)       # thin gap at the spine
        d = np.abs(z - (c + bend * np.sign(x + 1e-6) * 0 + bend))
        s |= d < side_w * top_w
        # small forks
        if i in (1, 3):
            d2 = np.abs(z - (c + 1.6 + bend * 1.25))
            s |= (d2 < 0.45) & (y > 15) & (y < 20)
    return s


def chevron(p_axis_u, p_axis_v, center_v, width, depth):
    """V shaped band: v - |u|*depth near center_v"""
    return np.abs(p_axis_v - center_v + np.abs(p_axis_u) * depth) < width


def paint_quad(T):
    """returns (cls array of str, tone array, alpha bool)"""
    n = T.n
    cls = np.full(n, "fur", dtype=object)
    tone = base_tone(T)
    alpha = np.ones(n, bool)
    tag = T.cube.tag
    meta = T.cube.meta
    side = meta.get("side", 1)
    p = T.pos
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    ax = np.abs(x)
    f = T.face
    jitter = (hash2(T.u, T.v, 21) - 0.5)

    if tag == "flank":
        st = body_stripes(p)
        cls[st] = "stripe"
        tone[st] = 0.45 + 0.3 * (T.loc[st, 1] - 0.5) + 0.25 * jitter[st]
        if f in ("bottom", "top"):
            tone = tone + (0.16 if f == "bottom" else -0.05)

    elif tag in ("torso", "belly", "chest", "neck"):
        # cream underside: belly, chest front, throat
        under = y < 9.6
        if tag == "belly" or (f == "bottom" and y.mean() < 10.5):
            under = np.ones(n, bool)
        if tag == "chest":
            front = (f == "front")
            under = under | (front & (y < 21.5 + 1.2 * np.sin(x * 1.1) - 0.8 * (ax > 4.5)))
            under = under | ((f in ("left", "right")) & (z < -12.5) & (y < 18))
        if tag == "neck":
            under = under | ((f == "front") | ((f == "bottom")))
        if tag == "torso" and f == "front":
            under = y < 10.5
        cls[under] = "cream"
        st = body_stripes(p) & ~under & (tag != "belly")
        if tag == "chest":
            # shoulder stripes
            st = (np.abs(z + 11.5 + 0.35 * (23 - y)) < 0.8 * smooth(15, 20, y)) & (ax > 6.9) & ~under
            st |= (np.abs(z + 12.6 + 0.2 * (23 - y)) < 0.5) & (y > 20) & ~under
        cls[st] = "stripe"
        tone[st] = 0.45 + 0.3 * (T.loc[st, 1] - 0.5) + 0.25 * jitter[st]

    elif tag == "skull":
        cls[:] = "fur"
        # forehead mark: vertical bar + two arcs (reads like the king character)
        top_like = (f == "top") | ((f == "front") & (y > 30.9))
        bar = (ax < 0.75) & (z < -21) & top_like
        arcs = (np.abs(z + 24.5 - 0.35 * (ax - 3.5) ** 2 * 0.25) < 0.6) & (ax > 1.6) & (ax < 6) & (f == "top")
        arcs2 = (np.abs(z + 22.0 - 0.06 * ax ** 2) < 0.55) & (ax > 0.9) & (ax < 4.5) & (f == "top")
        crown = (f == "top") & (z > -20.5) & (np.abs(z + 19.0) < 0.6) & (ax < 4.5)
        mark = bar | arcs | arcs2 | crown
        # temple stripes on the sides
        sidef = f in ("left", "right")
        temples = sidef & ((np.abs(y - 30.0 - 0.18 * (z + 20)) < 0.55) | (np.abs(y - 27.2 - 0.25 * (z + 20)) < 0.5)) & (z > -24.5 + 0.4 * (31 - y))
        back_st = (f == "back") & ((np.abs(y - 30) < 0.6) | (np.abs(y - 27) < 0.6)) & (ax > 2.5)
        mark |= temples | back_st
        # eye surround on the front face (dark eyeliner that sweeps out)
        if f == "front":
            ey = y; ex = ax
            liner = (ex > 5.0) & (ex < 7.3) & (np.abs(ey - (28.6 - 0.55 * (ex - 5.0))) < 0.55)
            under_eye = (ex > 1.0) & (ex < 6.0) & (ey < 27.6) & (ey > 26.4)
            muzzle_area = (ey < 27.2) & (ex < 6.5)
            cls[muzzle_area] = "cream"
            between = (ex < 1.5) & (ey < 30.5) & (ey > 27)
            cls[between] = "fur"
            mark |= liner
            cls[under_eye & ~liner] = "cream"
        cls[mark] = "stripe"
        tone[mark] = 0.5 + 0.25 * jitter[mark]
        if f == "bottom":
            cls[:] = "cream"

    elif tag == "cheek":
        cls[:] = "white"
        tone = tone + 0.12
        if f == "top":
            cls[:] = "fur"
        if f in ("left", "right"):
            st = np.abs(y - 26.2 - 0.3 * (z + 22)) < 0.5
            cls[st & (y > 25)] = "fur"

    elif tag in ("muzzle", "jaw"):
        cls[:] = "white"
        tone = tone + 0.1
        if tag == "jaw" and f == "top":
            cls[:] = "mouth"
            tng = (ax < 2) & (z > -27) & (z < -23)
            cls[tng] = "tongue"
        if tag == "muzzle" and f == "bottom":
            cls[:] = "mouth"
        if tag == "muzzle" and f == "front":
            # mouth line under the nose
            ml = (np.abs(y - 21.5) < 0.5) & (ax < 2.5) | ((ax < 0.5) & (y < 24.5) & (y > 21.5))
            cls[ml] = "lash"
        if tag == "muzzle" and f == "top":
            cls[:] = "fur"

    elif tag == "bridge":
        cls[:] = "fur"
        tone = tone + 0.05

    elif tag == "nose":
        cls[:] = "nose"
        tone = 0.55 + 0.35 * (T.loc[:, 1] - 0.5) + 0.1 * jitter
        if f == "front":
            nostril = (T.loc[:, 1] < 0.5) & (np.abs(T.loc[:, 0] - 0.5) > 0.3)
            cls[nostril] = "nostril"
            hl = (T.loc[:, 1] > 0.5) & (np.abs(T.loc[:, 0] - 0.5) < 0.2)
            tone[hl] = 0.95

    elif tag == "eye":
        # 4 x 3 pixel eye, row 0 (top) hidden under the heavy lid at rest
        lx = T.loc[:, 0]; ly = T.loc[:, 1]
        col = np.floor(np.clip(lx, 0, 0.999) * 4).astype(int)
        row = 2 - np.floor(np.clip(ly, 0, 0.999) * 3).astype(int)        # 0 top
        outer = col if side > 0 else 3 - col                                # 0 = inner corner (bedrock +X side for left)
        # outer: 0 at nose side ... 3 at temple side
        cls[:] = "iris"
        tone = np.where(row == 0, 0.25, np.where(row == 1, 0.45, 0.75))
        pupil = ((outer == 1) | (outer == 2)) & (row <= 1)
        cls[pupil] = "pupil"
        tone[pupil] = 0.3
        shine = (outer == 2) & (row == 1)
        cls[shine] = "shine"
        lash = (row == 0)
        cls[lash & ~pupil] = "lash"
        corner = (outer == 3) & (row == 2)
        cls[corner] = "lash"
        inner_c = (outer == 0) & (row == 2)
        tone[inner_c] = 0.55
        if f == "back":
            cls[:] = "fur"
        alpha[:] = True

    elif tag == "eyelid":
        cls[:] = "fur"
        tone = tone + 0.06
        lx = T.loc[:, 0]
        if f == "front":
            ly = T.loc[:, 1]
            lash = ly < 0.5
            cls[lash] = "lash"
            tone[lash] = 0.3

    elif tag == "ear":
        cls[:] = "fur"
        if f == "front":
            lx = T.loc[:, 0]; ly = T.loc[:, 1]
            rim = (lx < 0.2) | (lx > 0.8) | (ly > 0.8)
            cls[~rim] = "inner_ear"
            cls[rim] = "stripe"
        if f == "back":
            spot = (T.loc[:, 1] > 0.3) & (T.loc[:, 1] < 0.8) & (np.abs(T.loc[:, 0] - 0.5) < 0.25)
            cls[:] = "stripe"
            cls[spot] = "cream"
            tone[:] = 0.5

    elif tag == "white":
        cls[:] = "white"
        # long hair strands follow the lock direction (cube local x for locks)
        hair = meta.get("hair", "h")
        if hair == "v" and f in ("front", "back", "left", "right"):
            # vertical strands: constant along the hanging direction
            key = np.floor(T.u).astype(np.int64)
            strand = hash2(key, np.zeros(n, dtype=np.int64), 31) - 0.5
            gap = (hash2(key, np.ones(n, dtype=np.int64), 33) > 0.72)
            strand = strand - 0.35 * gap
        else:
            strand = hash2(np.floor(T.v).astype(np.int64), np.zeros(n, dtype=np.int64), 31) - 0.5
        tone = 0.66 + 0.30 * (T.loc[:, 1] - 0.5) + 0.12 * strand + 0.1 * jitter
        if f == "top":
            tone = tone + 0.1
        if f == "bottom":
            tone = tone - 0.25
        if f == "back":
            tone = tone - 0.12

    elif tag in ("fluff_white", "fluff"):
        cls[:] = "white" if tag == "fluff_white" else "cream"
        c = T.cube
        dims = c.size
        lx, ly, lz = T.loc[:, 0], T.loc[:, 1], T.loc[:, 2]
        if dims[2] == 0:     # XY plane
            ox = lx if side > 0 else 1 - lx
            if meta.get("shape") in ("beard_tip", "beard_side", "chest_tuft", "ear_tuft"):
                ox = lx
            W, H = dims[0], dims[1]
        elif dims[0] == 0:   # YZ plane
            ox = lz; W, H = dims[2], dims[1]
        else:
            ox = lx; W, H = dims[0], dims[1]
        alpha = shape_mask(meta.get("shape"), ox, ly, W, H)
        strand = hash2(np.floor(T.v).astype(np.int64), np.zeros(n, dtype=np.int64), 37) - 0.5
        tone = 0.68 + 0.25 * (ly - 0.5) + 0.12 * strand + 0.1 * jitter
        if f == "back":
            tone = tone - 0.15
        # darker toward the root of the tuft
        tone = tone - 0.15 * (1 - smooth(0.0, 0.35, ox))

    elif tag in ("leg", "paw", "toe", "thigh"):
        cls[:] = "fur"
        # inner faces and backs of the lower legs are cream (tiger white points)
        inner = ((f == "right") & (side > 0)) | ((f == "left") & (side < 0))
        if tag == "thigh":
            # haunch stripes: arcs on the outer face
            outer = ((f == "left") & (side > 0)) | ((f == "right") & (side < 0))
            arc = np.zeros(n, bool)
            for k, c0 in enumerate((15.5, 12.0, 8.6)):
                r = np.sqrt((y - 21.5) ** 2 + (z - 6.0) ** 2)
                arc |= (np.abs(r - (21.5 - c0)) < 0.55 + 0.25 * np.sin(z * 0.8 + k)) & (y < 20.5)
            cls[arc & (outer | (f == "back") | (f == "top"))] = "stripe"
            cls[inner & (y < 15)] = "cream"
            cls[(f == "front") & (y < 12)] = "cream"
        elif tag == "leg":
            front_face = f == "front"
            # chevrons on the front of the forelegs
            if T.cube.bone.startswith("leg_front"):
                lx = T.loc[:, 0] - 0.5
                chev = (chevron(lx * 6, y, 14.5, 0.55, 0.6) | chevron(lx * 6, y, 11.6, 0.5, 0.5) |
                        chevron(lx * 5, y, 6.5, 0.5, 0.45))
                cls[chev & front_face] = "stripe"
                outer = ((f == "left") & (side > 0)) | ((f == "right") & (side < 0))
                band = (np.abs(y - 15.2 + 0.3 * (z + 8)) < 0.55) | (np.abs(y - 7.5 + 0.25 * (z + 8)) < 0.5)
                cls[band & outer] = "stripe"
                cls[inner & (y < 13)] = "cream"
                cls[(f == "back") & (y < 9)] = "cream"
            else:
                outer = ((f == "left") & (side > 0)) | ((f == "right") & (side < 0))
                band = np.abs((y + 0.5 * (z - 6)) % 5.0 - 2.5) < 0.5
                cls[band & (outer | (f == "back"))] = "stripe"
                cls[inner] = "cream"
                cls[f == "front"] = "cream"
        elif tag in ("paw", "toe"):
            cls[:] = "fur"
            tone = tone + 0.08
            if tag == "toe":
                tone = tone + 0.05
                if f == "front":
                    claw = T.loc[:, 1] < 0.35
                    cls[claw & (np.abs(T.loc[:, 0] - 0.5) < 0.3)] = "claw"
            if tag == "paw" and f == "front":
                cls[:] = "fur"
            if f == "bottom":
                # paw pads: one main pad behind three toe beans on cream fur
                cls[:] = "cream"
                tone[:] = 0.45 + 0.1 * jitter
                lx = T.loc[:, 0]; lz = T.loc[:, 2]
                if tag == "paw":
                    main = (np.abs(lx - 0.5) < 0.3) & (lz > 0.45) & (lz < 0.85)
                    toes = (lz > 0.1) & (lz < 0.35) & ((np.abs(lx - 0.2) < 0.1) | (np.abs(lx - 0.5) < 0.1) | (np.abs(lx - 0.8) < 0.1))
                    pad = main | toes
                else:
                    pad = np.abs(lx - 0.5) < 0.3
                cls[pad] = "stripe"
                tone[pad] = 0.7
            if tag == "paw":
                cls[inner] = "cream"
        if f == "bottom" and tag not in ("paw", "thigh"):
            cls[cls == "fur"] = "cream"

    elif tag == "tail":
        seg = meta.get("seg", 0)
        # rings along the tail length (bone local z within each segment)
        lz = T.loc[:, 2]
        seglen = T.cube.size[2]
        dist = seg * 5 + lz * seglen
        ring = (np.abs(((dist + 1.2 + 0.4 * np.sin(x * 2 + y)) % 5.0) - 2.5) > 1.6) & (dist > 6)
        cls[ring] = "stripe"
        if seg == 6:
            cls[lz > 0.45] = "stripe"
        under = f == "bottom"
        cls[under & ~ring] = "cream"
        tone[cls == "stripe"] = 0.45 + 0.2 * jitter[cls == "stripe"]

    return cls, np.clip(tone, 0, 0.999), alpha


def paint(model, palettes):
    """Returns dict name -> RGBA uint8 arrays."""
    parts = cg.build_java(model)
    mats = cg.world_mats(parts)
    quads = cg.collect_quads(model, parts, mats)
    outs = {k: np.zeros((model.tex_h, model.tex_w, 4), np.uint8) for k in palettes}
    for q in quads:
        T = quad_texels(q, model.tex_w, model.tex_h)
        if T is None:
            continue
        cls, tone, alpha = paint_quad(T)
        dith = BAYER[T.v % 4, T.u % 4] * 0.18
        for key, pal in palettes.items():
            img = outs[key]
            rgba = np.zeros((T.n, 4), np.uint8)
            for c in set(cls):
                sel = cls == c
                ramp = pal.get(c)
                if ramp is None:
                    continue
                idx = np.clip(np.floor((tone[sel] + dith[sel]) * len(ramp)), 0, len(ramp) - 1).astype(int)
                rgba[sel, :3] = np.array(ramp)[idx]
                rgba[sel, 3] = 255
            rgba[~alpha] = 0
            if key == "alpha":
                eye = T.cube.tag == "eye"
                if not eye or T.face != "front":
                    rgba[:] = 0
            img[T.v, T.u] = rgba
    return outs
