"""Minimal Bedrock-geometry toolkit used to generate the Prismodon model.

Everything here mirrors how Blockbench interprets a ``*.geo.json`` file
(Blockbench is what Cobblemon models are authored and checked in):

* Blockbench mirrors bedrock X on import: ``from.x = -(origin.x + size.x)``,
  pivots get ``x *= -1`` and rotations get ``[-rx, -ry, rz]``.
* Bone and cube rotations are three.js Euler angles in ``ZYX`` order
  (matrix = Rz * Ry * Rx).
* Box UV layout per cube (w, h, d = size x, y, z):
  east  (0, d)      d x h        north (d, d)       w x h
  west  (d+w, d)    d x h        south (2d+w, d)    w x h
  up    (d+w, d) -> (d, 0)       down  (d+2w, 0) -> (d+w, d)

All public coordinates in this module are *bedrock* coordinates, i.e. what
ends up in the json file (+X = the Pokemon's left, -Z = forward).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

FACES = ("east", "west", "up", "down", "south", "north")


# --------------------------------------------------------------------------
# math helpers (Blockbench space)
# --------------------------------------------------------------------------

def rot_zyx(deg_xyz) -> np.ndarray:
    """three.js Euler(x, y, z, 'ZYX') -> 3x3 matrix (Rz @ Ry @ Rx)."""
    x, y, z = (math.radians(v) for v in deg_xyz)
    cx, sx, cy, sy, cz, sz = math.cos(x), math.sin(x), math.cos(y), math.sin(y), math.cos(z), math.sin(z)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return rz @ ry @ rx


def affine(rot: np.ndarray, trans) -> np.ndarray:
    m = np.eye(4)
    m[:3, :3] = rot
    m[:3, 3] = trans
    return m


def bb_vec(v):
    """bedrock position -> Blockbench position (mirror X)."""
    return np.array([-v[0], v[1], v[2]], dtype=float)


def bb_rot(r):
    """bedrock rotation -> Blockbench rotation."""
    return (-r[0], -r[1], r[2])


def mirror_rot(r):
    """Rotation of the mirror image (through the x = 0 plane), in bedrock space."""
    return (r[0], -r[1], -r[2])


# --------------------------------------------------------------------------
# model description
# --------------------------------------------------------------------------

@dataclass
class Cube:
    origin: tuple
    size: tuple
    mat: str
    inflate: float = 0.0
    pivot: Optional[tuple] = None
    rotation: Optional[tuple] = None
    params: dict = field(default_factory=dict)
    occluder: bool = True           # takes part in ambient-occlusion baking
    name: str = ""
    bone: "Bone" = None
    uv: tuple = (0, 0)

    def __post_init__(self):
        for s in self.size:
            if abs(s - round(s)) > 1e-9:
                raise ValueError(f"cube sizes must be integers for box UV: {self.size}")
        self.size = tuple(int(round(s)) for s in self.size)

    @property
    def uv_footprint(self):
        w, h, d = self.size
        return 2 * (d + w), d + h

    def is_plane(self):
        return 0 in self.size


@dataclass
class Bone:
    name: str
    parent: Optional["Bone"]
    pivot: tuple
    rotation: tuple = (0, 0, 0)
    cubes: list = field(default_factory=list)
    locators: dict = field(default_factory=dict)

    def cube(self, origin, size, mat, **kw) -> Cube:
        c = Cube(tuple(origin), tuple(size), mat, **kw)
        c.bone = self
        if not c.name:
            c.name = f"{self.name}_{len(self.cubes)}"
        self.cubes.append(c)
        return c


class Model:
    def __init__(self, name: str, tex_w: int, tex_h: int):
        self.name = name
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.bones: list[Bone] = []
        self._by_name: dict[str, Bone] = {}

    def bone(self, name, parent=None, pivot=(0, 0, 0), rotation=(0, 0, 0), locators=None) -> Bone:
        if name in self._by_name:
            raise ValueError(f"duplicate bone {name}")
        p = self._by_name[parent] if isinstance(parent, str) else parent
        b = Bone(name, p, tuple(pivot), tuple(rotation), locators=dict(locators or {}))
        self.bones.append(b)
        self._by_name[name] = b
        return b

    def __getitem__(self, name) -> Bone:
        return self._by_name[name]

    def cubes(self):
        for b in self.bones:
            yield from b.cubes

    # ---------------------------------------------------------------- transforms
    def bone_world(self, bone: Bone, pose: Optional[dict] = None) -> np.ndarray:
        """4x4 world matrix of a bone in Blockbench space (rest pose unless ``pose``)."""
        chain = []
        b = bone
        while b is not None:
            chain.append(b)
            b = b.parent
        m = np.eye(4)
        parent_origin = np.zeros(3)
        for b in reversed(chain):
            origin = bb_vec(b.pivot)
            rot = np.array(bb_rot(b.rotation), dtype=float)
            pos = origin - parent_origin
            if pose and b.name in pose:
                pr, pp = pose[b.name]
                rot = rot + np.array(bb_rot(pr))
                pos = pos + bb_vec(pp)
            m = m @ affine(rot_zyx(rot), pos)
            parent_origin = origin
        return m

    def cube_world(self, cube: Cube, pose=None) -> np.ndarray:
        """Matrix mapping cube-local Blockbench coordinates (relative to cube pivot) to world."""
        bw = self.bone_world(cube.bone, pose)
        c_origin = bb_vec(cube.pivot) if cube.pivot is not None else np.zeros(3)
        rot = bb_rot(cube.rotation) if cube.rotation is not None else (0, 0, 0)
        return bw @ affine(rot_zyx(rot), c_origin - bb_vec(cube.bone.pivot)) @ affine(np.eye(3), -c_origin)

    @staticmethod
    def cube_bounds_bb(cube: Cube):
        """from/to (Blockbench space, inflate applied)."""
        o, s = cube.origin, cube.size
        frm = np.array([-(o[0] + s[0]), o[1], o[2]], dtype=float)
        to = frm + np.array(s, dtype=float)
        return frm - cube.inflate, to + cube.inflate

    # ---------------------------------------------------------------- UV
    def pack_uv(self, order_key=None):
        cubes = list(self.cubes())
        cubes.sort(key=lambda c: (-c.uv_footprint[1], -c.uv_footprint[0]))
        # skyline packer
        sky = [0] * self.tex_w
        for c in cubes:
            fw, fh = c.uv_footprint
            if fw == 0 or fh == 0:
                c.uv = (0, 0)
                continue
            best = None
            for x in range(0, self.tex_w - fw + 1):
                y = max(sky[x:x + fw])
                if y + fh > self.tex_h:
                    continue
                if best is None or y < best[1] or (y == best[1] and x < best[0]):
                    best = (x, y)
            if best is None:
                raise RuntimeError(f"UV atlas full while placing {c.name} {c.size}")
            x, y = best
            for i in range(x, x + fw):
                sky[i] = y + fh
            c.uv = (x, y)
        return max(sky)

    @staticmethod
    def face_uv_rects(cube: Cube):
        """[u1, v1, u2, v2] per face exactly like Blockbench's box UV."""
        w, h, d = cube.size
        u0, v0 = cube.uv
        fl = {
            "east": ([0, d], [d, h]),
            "west": ([d + w, d], [d, h]),
            "up": ([d + w, d], [-w, -d]),
            "down": ([d + 2 * w, 0], [-w, d]),
            "south": ([2 * d + w, d], [w, h]),
            "north": ([d, d], [w, h]),
        }
        out = {}
        for f, (frm, size) in fl.items():
            out[f] = [frm[0] + u0, frm[1] + v0, frm[0] + size[0] + u0, frm[1] + size[1] + v0]
        return out

    @staticmethod
    def face_vertices(frm, to):
        """v0..v3 per face in Blockbench order (v0=uv top-left, v1=top-right, v2=bottom-left)."""
        f, t = frm, to
        return {
            "east": [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2])],
            "west": [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], f[2]), (f[0], f[1], t[2])],
            "up": [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (f[0], t[1], t[2]), (t[0], t[1], t[2])],
            "down": [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])],
            "south": [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (f[0], f[1], t[2]), (t[0], f[1], t[2])],
            "north": [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])],
        }

    FACE_NORMALS_BB = {
        "east": (1, 0, 0), "west": (-1, 0, 0), "up": (0, 1, 0),
        "down": (0, -1, 0), "south": (0, 0, 1), "north": (0, 0, -1),
    }

    def texels(self, cube: Cube):
        """Yield per-face texel samples for painting.

        For each face returns dict with integer pixel coords (px, py) arrays,
        world positions / normals in *bedrock* space, cube-local positions in
        bedrock space (measured from the cube's origin corner, un-rotated) and
        s/t face parameters plus face size in texels.
        """
        frm, to = self.cube_bounds_bb(cube)
        # un-inflated bounds for local coordinates
        o, s = cube.origin, cube.size
        raw_from = np.array([-(o[0] + s[0]), o[1], o[2]], dtype=float)
        m = self.cube_world(cube)
        rects = self.face_uv_rects(cube)
        verts = self.face_vertices(frm, to)
        vraw = self.face_vertices(raw_from, raw_from + np.array(s, dtype=float))
        for face in FACES:
            u1, v1, u2, v2 = rects[face]
            if u1 == u2 or v1 == v2:
                continue
            ulo, uhi = sorted((u1, u2))
            vlo, vhi = sorted((v1, v2))
            pxs = np.arange(int(math.floor(ulo)), int(math.ceil(uhi)))
            pys = np.arange(int(math.floor(vlo)), int(math.ceil(vhi)))
            PX, PY = np.meshgrid(pxs, pys)
            PX = PX.ravel()
            PY = PY.ravel()
            sc = (PX + 0.5 - u1) / (u2 - u1)
            tc = (PY + 0.5 - v1) / (v2 - v1)
            vv = np.array(verts[face])
            p_local = vv[0] + sc[:, None] * (vv[1] - vv[0]) + tc[:, None] * (vv[2] - vv[0])
            vr = np.array(vraw[face])
            p_raw = vr[0] + sc[:, None] * (vr[1] - vr[0]) + tc[:, None] * (vr[2] - vr[0])
            p_h = np.c_[p_local, np.ones(len(p_local))]
            p_world = (m @ p_h.T).T[:, :3]
            n_world = m[:3, :3] @ np.array(self.FACE_NORMALS_BB[face], dtype=float)
            # back to bedrock space
            p_world[:, 0] *= -1
            n_b = n_world.copy()
            n_b[0] *= -1
            local = p_raw - raw_from
            # local x measured in bedrock direction: bedrock x = -(bb x)
            local_b = local.copy()
            local_b[:, 0] = s[0] - local[:, 0]
            yield {
                "face": face,
                "px": PX, "py": PY,
                "s": sc, "t": tc,
                "P": p_world, "N": np.tile(n_b, (len(PX), 1)),
                "L": local_b,
                "fw": abs(u2 - u1), "fh": abs(v2 - v1),
            }

    # ---------------------------------------------------------------- export
    def to_geo(self, bounds_w, bounds_h, bounds_off):
        bones = []
        for b in self.bones:
            jb = {"name": b.name}
            if b.parent:
                jb["parent"] = b.parent.name
            jb["pivot"] = [r(v) for v in b.pivot]
            if any(abs(v) > 1e-9 for v in b.rotation):
                jb["rotation"] = [r(v) for v in b.rotation]
            if b.locators:
                jb["locators"] = {k: [r(v) for v in p] for k, p in b.locators.items()}
            if b.cubes:
                jc = []
                for c in b.cubes:
                    cc = {"origin": [r(v) for v in c.origin], "size": list(c.size)}
                    if c.inflate:
                        cc["inflate"] = r(c.inflate)
                    if c.rotation is not None and any(abs(v) > 1e-9 for v in c.rotation):
                        cc["pivot"] = [r(v) for v in c.pivot]
                        cc["rotation"] = [r(v) for v in c.rotation]
                    cc["uv"] = list(c.uv)
                    jc.append(cc)
                jb["cubes"] = jc
            bones.append(jb)
        return {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": f"geometry.{self.name}",
                    "texture_width": self.tex_w,
                    "texture_height": self.tex_h,
                    "visible_bounds_width": bounds_w,
                    "visible_bounds_height": bounds_h,
                    "visible_bounds_offset": bounds_off,
                },
                "bones": bones,
            }],
        }


def r(v, nd=4):
    v = round(float(v), nd)
    if v == int(v):
        return int(v)
    return v


# --------------------------------------------------------------------------
# helpers for building symmetric parts
# --------------------------------------------------------------------------

def shift_subtree(model: Model, bone: Bone, dy: float, dz: float = 0.0):
    """Translate a bone, its cubes, locators and all descendants (bedrock space)."""
    todo = [bone]
    seen = []
    while todo:
        b = todo.pop()
        seen.append(b)
        todo.extend(c for c in model.bones if c.parent is b)
    for b in seen:
        b.pivot = (b.pivot[0], b.pivot[1] + dy, b.pivot[2] + dz)
        b.locators = {k: (v[0], v[1] + dy, v[2] + dz) for k, v in b.locators.items()}
        for c in b.cubes:
            c.origin = (c.origin[0], c.origin[1] + dy, c.origin[2] + dz)
            if c.pivot is not None:
                c.pivot = (c.pivot[0], c.pivot[1] + dy, c.pivot[2] + dz)
            for k in ("poly", "axis"):
                if k in c.params:
                    c.params[k] = [(p[0] + dz, p[1] + dy) for p in c.params[k]]


def mirror_origin(origin, size):
    return (-(origin[0] + size[0]), origin[1], origin[2])


def mirror_point(p):
    return (-p[0], p[1], p[2])


def bar_between(bone: Bone, p0, p1, width=1, thick=2, mat="steel", inflate=0.0, extend=0.0, x=0.0, **kw):
    """A rectangular bar in the sagittal (y/z) plane from p0=(z, y) to p1=(z, y).

    The bar is a cube extruded along +Y from p0 and rotated about X so its
    axis points at p1 (bedrock +X rotation tilts +Y towards -Z).
    """
    z0, y0 = p0
    z1, y1 = p1
    dz, dy = z1 - z0, y1 - y0
    edge = math.hypot(dz, dy)
    L = max(1, int(round(edge + 2 * extend)))
    ang = -math.degrees(math.atan2(dz, dy))
    # box UV needs integer sizes: keep the bar centred on the edge midpoint
    origin = (x - thick / 2.0, y0 + edge / 2.0 - L / 2.0, z0 - width / 2.0)
    c = bone.cube(origin, (thick, L, width), mat, inflate=inflate, pivot=(x, y0, z0), rotation=(ang, 0, 0), **kw)
    return c
