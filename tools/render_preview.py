"""
Tiny software renderer for .bbmodel files (rest pose, textured, orthographic).
Used to verify the UV/texture conversion and to generate README preview images.
"""

import base64
import io
import json
import math
import sys

import numpy as np
from PIL import Image, ImageDraw


def rot_matrix(rx, ry, rz):
    rx, ry, rz = (math.radians(a) for a in (rx, ry, rz))
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    mx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    my = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    mz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return mz @ my @ mx  # Blockbench Bedrock euler order ZYX


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    groups = {g["uuid"]: g for g in data["groups"]}
    elements = {e["uuid"]: e for e in data["elements"]}
    parent = {}
    owner = {}

    def walk(nodes, p):
        for n in nodes:
            if isinstance(n, dict):
                parent[n["uuid"]] = p
                walk(n.get("children", []), n["uuid"])
            else:
                owner[n] = p

    walk(data["outliner"], None)
    return data, groups, elements, parent, owner


def chain(uuid, groups, parent):
    out = []
    while uuid is not None:
        out.append(groups[uuid])
        uuid = parent[uuid]
    return out  # innermost first


def _molang(value, t):
    if value is None or value == "":
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except ValueError:
        pass
    expr = value.replace("query.anim_time", "T").replace("q.anim_time", "T")
    expr = expr.replace("math.sin", "_sin").replace("math.cos", "_cos").replace("math.abs", "abs")
    expr = expr.replace("math.clamp", "_clamp").replace("math.max", "max").replace("math.min", "min")
    env = {"T": t, "_sin": lambda d: math.sin(math.radians(d)), "_cos": lambda d: math.cos(math.radians(d)),
           "_clamp": lambda v, a, b: max(a, min(b, v)), "abs": abs, "max": max, "min": min}
    return float(eval(expr, {"__builtins__": {}}, env))


def sample_channel(kfs, t, default):
    """Linear sample of a Blockbench keyframe channel at time t (catmullrom approximated linearly)."""
    if not kfs:
        return np.array(default, dtype=float)
    kfs = sorted(kfs, key=lambda k: k["time"])

    def val(k, dp):
        d = k["data_points"][min(dp, len(k["data_points"]) - 1)]
        return np.array([_molang(d.get(a), t) for a in "xyz"])

    if t <= kfs[0]["time"]:
        return val(kfs[0], 0)
    if t >= kfs[-1]["time"]:
        return val(kfs[-1], 1)
    for a, b in zip(kfs, kfs[1:]):
        if a["time"] <= t <= b["time"]:
            if a.get("interpolation") == "step":
                return val(a, 1)
            f = (t - a["time"]) / max(1e-9, b["time"] - a["time"])
            return val(a, 1) * (1 - f) + val(b, 0) * f
    return np.array(default, dtype=float)


class Pose:
    """Per-group animated transform (offset, rotation, scale) at a given time."""

    def __init__(self, data, anim_name=None, t=0.0):
        self.offsets, self.rots, self.scales = {}, {}, {}
        if not anim_name:
            return
        anim = next((a for a in data["animations"] if a["name"].endswith("." + anim_name) or a["name"] == anim_name), None)
        if anim is None:
            raise KeyError(anim_name)
        for uuid, an in anim.get("animators", {}).items():
            kfs = an.get("keyframes", [])
            self.rots[uuid] = sample_channel([k for k in kfs if k["channel"] == "rotation"], t, [0, 0, 0])
            self.offsets[uuid] = sample_channel([k for k in kfs if k["channel"] == "position"], t, [0, 0, 0])
            self.scales[uuid] = sample_channel([k for k in kfs if k["channel"] == "scale"], t, [1, 1, 1])


def transform_point(p, cube, groups_chain, pose=None):
    p = np.array(p, dtype=float)
    rot = cube.get("rotation", [0, 0, 0])
    if any(rot):
        o = np.array(cube.get("origin", [0, 0, 0]), dtype=float)
        p = rot_matrix(*rot) @ (p - o) + o
    for g in groups_chain:
        r = np.array(g.get("rotation", [0, 0, 0]), dtype=float)
        off = np.zeros(3)
        sc = np.ones(3)
        if pose is not None:
            r = r + pose.rots.get(g["uuid"], 0)
            off = pose.offsets.get(g["uuid"], off)
            sc = pose.scales.get(g["uuid"], sc)
        o = np.array(g.get("origin", [0, 0, 0]), dtype=float)
        p = rot_matrix(*r) @ ((p - o) * sc) + o + off
    return p


FACE_CORNERS = {
    # corners ordered (top-left, top-right, bottom-right, bottom-left) as seen in the uv rectangle
    "north": lambda f, t: [(t[0], t[1], f[2]), (f[0], t[1], f[2]), (f[0], f[1], f[2]), (t[0], f[1], f[2])],
    "south": lambda f, t: [(f[0], t[1], t[2]), (t[0], t[1], t[2]), (t[0], f[1], t[2]), (f[0], f[1], t[2])],
    "east": lambda f, t: [(t[0], t[1], t[2]), (t[0], t[1], f[2]), (t[0], f[1], f[2]), (t[0], f[1], t[2])],
    "west": lambda f, t: [(f[0], t[1], f[2]), (f[0], t[1], t[2]), (f[0], f[1], t[2]), (f[0], f[1], f[2])],
    "up": lambda f, t: [(f[0], t[1], f[2]), (t[0], t[1], f[2]), (t[0], t[1], t[2]), (f[0], t[1], t[2])],
    "down": lambda f, t: [(f[0], f[1], t[2]), (t[0], f[1], t[2]), (t[0], f[1], f[2]), (f[0], f[1], f[2])],
}


def model_quads(path, texture_index=0, anim=None, t=0.0, skip_fx=False):
    data, groups, elements, parent, owner = load(path)
    pose = Pose(data, anim, t) if anim else None
    tex_meta = data["textures"][texture_index]
    img = Image.open(io.BytesIO(base64.b64decode(tex_meta["source"].split(",", 1)[1]))).convert("RGBA")
    res_w, res_h = data["resolution"]["width"], data["resolution"]["height"]
    sx, sy = img.width / res_w, img.height / res_h
    pix = np.array(img)
    quads = []
    for uuid, el in elements.items():
        if el.get("type", "cube") != "cube" or el.get("export") is False:
            continue
        gch = chain(owner.get(uuid), groups, parent) if owner.get(uuid) else []
        if skip_fx and any(g["name"].startswith("fx") for g in gch):
            continue
        inf = el.get("inflate", 0) or 0
        f = [el["from"][i] - inf for i in range(3)]
        tt = [el["to"][i] + inf for i in range(3)]
        for fname, face in el["faces"].items():
            if face.get("texture") is None:
                continue
            u1, v1, u2, v2 = face["uv"]
            corners = [transform_point(c, el, gch, pose) for c in FACE_CORNERS[fname](f, tt)]
            quads.append((corners, (u1, v1, u2, v2)))
    return quads, pix, (sx, sy)


def render(path, out, yaw=35, pitch=20, size=768, texture_index=0, background=(0, 0, 0, 0), anim=None, t=0.0, skip_fx=True):
    quads, pix, (tsx, tsy) = model_quads(path, texture_index, anim, t, skip_fx)
    R = rot_matrix(pitch, 0, 0) @ rot_matrix(0, yaw, 0)
    # Blockbench: model faces -z (north). View from the front-left.
    polys = []
    for corners, (u1, v1, u2, v2) in quads:
        pts = [R @ c for c in corners]
        # sub-divide per texel for texturing
        nu = max(1, int(round(abs(u2 - u1))))
        nv = max(1, int(round(abs(v2 - v1))))
        nu, nv = min(nu, 64), min(nv, 64)
        a, b, c, d = pts
        for i in range(nu):
            for j in range(nv):
                s0, s1 = i / nu, (i + 1) / nu
                t0, t1 = j / nv, (j + 1) / nv

                def lerp(s, tt):
                    top = a + (b - a) * s
                    bot = d + (c - d) * s
                    return top + (bot - top) * tt

                q = [lerp(s0, t0), lerp(s1, t0), lerp(s1, t1), lerp(s0, t1)]
                uu = u1 + (u2 - u1) * (s0 + s1) / 2
                vv = v1 + (v2 - v1) * (t0 + t1) / 2
                px = int(min(pix.shape[1] - 1, max(0, uu * tsx)))
                py = int(min(pix.shape[0] - 1, max(0, vv * tsy)))
                col = pix[py, px]
                if col[3] < 20:
                    continue
                depth = sum(p[2] for p in q) / 4
                polys.append((depth, q, tuple(int(x) for x in col[:3])))
    if not polys:
        return
    allp = np.array([p for _, q, _ in polys for p in q])
    minx, maxx = allp[:, 0].min(), allp[:, 0].max()
    miny, maxy = allp[:, 1].min(), allp[:, 1].max()
    span = max(maxx - minx, maxy - miny) * 1.08
    scale = size / span
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    im = Image.new("RGBA", (size, size), background)
    dr = ImageDraw.Draw(im)
    # painter: far (large z after rotation, since camera looks toward +z... ) first
    polys.sort(key=lambda p: -p[0])
    for _, q, col in polys:
        dr.polygon([(size / 2 - (p[0] - cx) * scale, size / 2 - (p[1] - cy) * scale) for p in q], fill=col)
    im.save(out)


def bounds(path, anim=None, t=0.0):
    quads, _, _ = model_quads(path, 0, anim, t, True)
    pts = np.array([c for corners, _ in quads for c in corners])
    return pts.min(axis=0), pts.max(axis=0)


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2], yaw=float(sys.argv[3]) if len(sys.argv) > 3 else 35)
