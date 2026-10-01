"""Emulates Cobblemon's Bedrock -> Java ModelPart conversion (TexturedModel.kt)
and Minecraft's ModelPart/Cube math, so previews match what the game draws.

"J space" is Java model space (Y down). World space used by the previews is
(x, -y, -z) of J space, which puts the Pokemon's face towards +Z (the camera).
"""
import math
import numpy as np


def rot_zyx(xr, yr, zr):
    """JOML Quaternionf.rotationZYX(z, y, x) as a matrix: Rz @ Ry @ Rx."""
    cx, sx = math.cos(xr), math.sin(xr)
    cy, sy = math.cos(yr), math.sin(yr)
    cz, sz = math.cos(zr), math.sin(zr)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


class Part:
    __slots__ = ("name", "bone", "parent", "offset", "rot", "boxes", "is_sub", "locator")

    def __init__(self, name, bone, parent, offset, rot):
        self.name = name
        self.bone = bone
        self.parent = parent
        self.offset = np.array(offset, dtype=float)
        self.rot = np.array(rot, dtype=float)
        self.boxes = []
        self.is_sub = False
        self.locator = None


class Box:
    __slots__ = ("x", "y", "z", "w", "h", "d", "grow", "mirror", "u", "v", "cube")

    def __init__(self, x, y, z, w, h, d, grow, mirror, u, v, cube):
        self.x, self.y, self.z = x, y, z
        self.w, self.h, self.d = w, h, d
        self.grow = grow
        self.mirror = mirror
        self.u, self.v = u, v
        self.cube = cube


def build_rig(model):
    """Returns an ordered list of Parts (parents before children)."""
    parts = []
    by_name = {}
    bones = list(model.bones.values())
    # locators become empty bones appended after the regular bones
    loc_bones = []
    for b in bones:
        for ln, lp in b.locators.items():
            loc_bones.append((ln, b, lp))
    for b in bones:
        if b.parent is None:
            offset = (0, 0, 0)
            rot = (0, 0, 0)
            parent = None
        else:
            pp = model.bones[b.parent].pivot
            offset = (b.pivot[0] - pp[0], pp[1] - b.pivot[1], b.pivot[2] - pp[2])
            r = b.rotation or (0, 0, 0)
            rot = tuple(math.radians(v) for v in r)
            parent = by_name[b.parent]
        p = Part(b.name, b, parent, offset, rot)
        parts.append(p)
        by_name[b.name] = p
        for c in b.cubes:
            if c.rotation is not None:
                cp = c.pivot
                sub = Part("%" + b.name, b, p,
                           (cp[0] - b.pivot[0], b.pivot[1] - cp[1], cp[2] - b.pivot[2]),
                           tuple(math.radians(v) for v in c.rotation))
                sub.is_sub = True
                pivot = cp
                target = sub
                parts.append(sub)
            else:
                pivot = b.pivot
                target = p
            ox, oy, oz = c.origin
            sx, sy, sz = c.size
            target.boxes.append(Box(ox - pivot[0], -(oy - pivot[1] + sy), oz - pivot[2],
                                    sx, sy, sz, c.inflate, c.mirror, c.uv[0], c.uv[1], c))
    for (ln, b, lp) in loc_bones:
        parent = by_name[b.name]
        pp = b.pivot
        p = Part("locator:" + ln, b, parent, (lp[0] - pp[0], pp[1] - lp[1], lp[2] - pp[2]), (0, 0, 0))
        p.locator = ln
        parts.append(p)
    return parts


def pose_matrices(parts, pose=None):
    """pose: {bone: {"pos": (x,y,z), "rot": (deg x,y,z), "scale": (x,y,z)}} in Bedrock
    animation units. Returns {id(part): 4x4} in J space (pixel units)."""
    pose = pose or {}
    mats = {}
    for p in parts:
        off = p.offset.copy()
        rot = p.rot.copy()
        scale = np.ones(3)
        if not p.is_sub and p.locator is None and p.name in pose:
            a = pose[p.name]
            if "pos" in a:
                # Cobblemon negates Y for position channels (MolangBoneValue.yMul)
                off += np.array([a["pos"][0], -a["pos"][1], a["pos"][2]])
            if "rot" in a:
                rot += np.radians(np.array(a["rot"], dtype=float))
            if "scale" in a:
                scale *= np.array(a["scale"], dtype=float)
        m = np.eye(4)
        m[:3, 3] = off
        r = np.eye(4)
        r[:3, :3] = rot_zyx(*rot)
        s = np.diag([scale[0], scale[1], scale[2], 1.0])
        local = m @ r @ s
        if p.parent is not None:
            mats[id(p)] = mats[id(p.parent)] @ local
        else:
            mats[id(p)] = local
    return mats


# Java Cube polygon definitions: (vertex indices, u1, v1, u2, v2 keys, direction normal in J)
def _cube_polys(b):
    x0, y0, z0 = b.x, b.y, b.z
    w, h, d = b.w, b.h, b.d
    f, g, hh = x0 + w, y0 + h, z0 + d
    gr = b.grow
    x0 -= gr; y0 -= gr; z0 -= gr
    f += gr; g += gr; hh += gr
    if b.mirror:
        x0, f = f, x0
    v = [
        (x0, y0, z0), (f, y0, z0), (f, g, z0), (x0, g, z0),
        (x0, y0, hh), (f, y0, hh), (f, g, hh), (x0, g, hh),
    ]
    u = b.u
    vv = b.v
    j = u
    k = u + d
    l = u + d + w
    m = u + d + w + w
    n = u + d + w + d
    o = u + d + w + d + w
    p = vv
    q = vv + d
    r = vv + d + h
    polys = [
        ((5, 4, 0, 1), k, p, l, q, (0, -1, 0), "up"),      # Java DOWN -> visual top
        ((2, 3, 7, 6), l, q, m, p, (0, 1, 0), "down"),     # Java UP -> visual bottom
        ((0, 4, 7, 3), j, q, k, r, (-1, 0, 0), "right"),   # Java WEST (-x = Pokemon's right)
        ((1, 0, 3, 2), k, q, l, r, (0, 0, -1), "front"),   # Java NORTH
        ((5, 1, 2, 6), l, q, n, r, (1, 0, 0), "left"),     # Java EAST
        ((4, 5, 6, 7), n, q, o, r, (0, 0, 1), "back"),     # Java SOUTH
    ]
    out = []
    for idx, u1, v1, u2, v2, nrm, name in polys:
        verts = [v[i] for i in idx]
        uvs = [(u2, v1), (u1, v1), (u1, v2), (u2, v2)]
        nrm = list(nrm)
        if b.mirror:
            verts = verts[::-1]
            uvs = uvs[::-1]
            nrm[0] = -nrm[0]
            if name == "right":
                name = "left"
            elif name == "left":
                name = "right"
        out.append((verts, uvs, nrm, name))
    return out


def build_mesh(parts, mats):
    """Returns dict of arrays: quads (N,4,3) J-space, uvs (N,4,2), normals (N,3), info list."""
    quads, uvs, normals, info = [], [], [], []
    for p in parts:
        if not p.boxes:
            continue
        M = mats[id(p)]
        R = M[:3, :3]
        for b in p.boxes:
            for verts, uv, nrm, name in _cube_polys(b):
                vs = np.array(verts, dtype=float)
                # degenerate check in local space
                e1 = vs[1] - vs[0]
                e2 = vs[3] - vs[0]
                if np.linalg.norm(np.cross(e1, e2)) < 1e-9 and np.linalg.norm(np.cross(vs[2] - vs[1], vs[3] - vs[1])) < 1e-9:
                    continue
                uva = np.array(uv, dtype=float)
                if abs(uva[:, 0].max() - uva[:, 0].min()) < 1e-9 or abs(uva[:, 1].max() - uva[:, 1].min()) < 1e-9:
                    continue
                vw = (M @ np.c_[vs, np.ones(4)].T).T[:, :3]
                n = R @ np.array(nrm, dtype=float)
                ln = np.linalg.norm(n)
                if ln > 0:
                    n = n / ln
                quads.append(vw)
                uvs.append(uva)
                normals.append(n)
                info.append((p.bone.name, b.cube, name))
    return {
        "quads": np.array(quads).reshape(-1, 4, 3),
        "uvs": np.array(uvs).reshape(-1, 4, 2),
        "normals": np.array(normals).reshape(-1, 3),
        "info": info,
    }


def locator_positions(parts, mats):
    out = {}
    for p in parts:
        if p.locator is not None:
            out[p.locator] = mats[id(p)][:3, 3].copy()
    return out


def j_to_world(a):
    a = np.asarray(a, dtype=float).copy()
    a[..., 1] *= -1
    a[..., 2] *= -1
    return a


def j_to_bedrock(a):
    a = np.asarray(a, dtype=float).copy()
    a[..., 1] *= -1
    return a
