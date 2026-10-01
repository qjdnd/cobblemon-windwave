"""Bedrock geometry builder for Cobblemon models.

Coordinates follow Blockbench/Bedrock conventions used by Cobblemon:
  * units are model pixels (16 per block)
  * the Pokemon faces -Z (north), +X is the Pokemon's left, +Y is up
  * cubes use box UV only (Cobblemon ignores per-face UV)
"""
import json
import math
from collections import OrderedDict


def _ceil(v):
    return int(math.ceil(v - 1e-6))


def _num(v):
    """Format a float the way Blockbench writes numbers."""
    if isinstance(v, bool):
        return v
    r = round(float(v), 4)
    if r == int(r):
        return int(r)
    return r


class Cube:
    def __init__(self, origin, size, inflate=0.0, mirror=False, rotation=None,
                 pivot=None, tag=None, share=None, uv=None):
        self.origin = [float(v) for v in origin]
        self.size = [float(v) for v in size]
        self.inflate = float(inflate)
        self.mirror = bool(mirror)
        self.rotation = rotation
        self.pivot = pivot
        self.tag = tag
        # Another cube (same size) whose UV island this cube re-uses.
        self.share = share
        self.uv = uv
        self.bone = None

    def footprint(self):
        w, h, d = (_ceil(s) for s in self.size)
        return 2 * (d + w), d + h

    def owner(self):
        c = self
        while c.share is not None:
            c = c.share
        return c


class Bone:
    def __init__(self, name, parent=None, pivot=(0, 0, 0), rotation=None):
        self.name = name
        self.parent = parent
        self.pivot = [float(v) for v in pivot]
        self.rotation = rotation
        self.cubes = []
        self.locators = OrderedDict()
        self.tag = None

    def add(self, origin, size, **kw):
        c = Cube(origin, size, **kw)
        c.bone = self
        self.cubes.append(c)
        return c

    def locator(self, name, pos):
        self.locators[name] = [float(v) for v in pos]


class Model:
    def __init__(self, identifier, tex_w, tex_h):
        self.identifier = identifier
        self.tex_w = tex_w
        self.tex_h = tex_h
        self.bones = OrderedDict()
        self.visible_bounds = (3, 3, (0, 1, 0))

    def bone(self, name, parent=None, pivot=(0, 0, 0), rotation=None):
        if name in self.bones:
            raise ValueError("duplicate bone " + name)
        if parent is not None and parent not in self.bones:
            raise ValueError("unknown parent %s for %s" % (parent, name))
        b = Bone(name, parent, pivot, rotation)
        self.bones[name] = b
        return b

    def cubes(self):
        for b in self.bones.values():
            for c in b.cubes:
                yield c

    # ------------------------------------------------------------------ UVs
    def pack(self, pad=0, order=None):
        """Skyline bottom-left packing of every UV-owning cube."""
        owners = [c for c in self.cubes() if c.share is None and c.uv is None]
        if order is None:
            owners.sort(key=lambda c: (-c.footprint()[1], -c.footprint()[0]))
        sky = [(0, self.tex_w, 0)]  # (x, width, y)

        def place(w, h):
            best = None
            for i in range(len(sky)):
                x = sky[i][0]
                if x + w > self.tex_w:
                    break
                # max height across the span
                y = 0
                span = 0
                j = i
                while span < w and j < len(sky):
                    y = max(y, sky[j][2])
                    span += sky[j][1]
                    j += 1
                if span < w:
                    continue
                if y + h > self.tex_h:
                    continue
                if best is None or (y, x) < (best[1], best[0]):
                    best = (x, y)
            return best

        def commit(x, y, w, h):
            nonlocal sky
            new = []
            for (sx, sw, sy) in sky:
                ex = sx + sw
                if ex <= x or sx >= x + w:
                    new.append((sx, sw, sy))
                    continue
                if sx < x:
                    new.append((sx, x - sx, sy))
                if ex > x + w:
                    new.append((x + w, ex - (x + w), sy))
            new.append((x, w, y + h))
            new.sort()
            merged = []
            for seg in new:
                if merged and merged[-1][2] == seg[2] and merged[-1][0] + merged[-1][1] == seg[0]:
                    merged[-1] = (merged[-1][0], merged[-1][1] + seg[1], seg[2])
                else:
                    merged.append(seg)
            sky = merged

        for c in owners:
            w, h = c.footprint()
            w += pad
            h += pad
            if w == 0 or h == 0:
                c.uv = [0, 0]
                continue
            p = place(w, h)
            if p is None:
                raise RuntimeError("texture %dx%d too small for %s/%s (%dx%d)"
                                   % (self.tex_w, self.tex_h, c.bone.name, c.tag, w, h))
            c.uv = [p[0], p[1]]
            commit(p[0], p[1], w, h)
        for c in self.cubes():
            if c.share is not None:
                c.uv = list(c.owner().uv)
        used = max((s[2] for s in sky), default=0)
        return used

    # --------------------------------------------------------------- export
    def geo_dict(self):
        bones = []
        for b in self.bones.values():
            d = OrderedDict()
            d["name"] = b.name
            if b.parent:
                d["parent"] = b.parent
            d["pivot"] = [_num(v) for v in b.pivot]
            if b.rotation and any(abs(r) > 1e-9 for r in b.rotation):
                d["rotation"] = [_num(v) for v in b.rotation]
            if b.cubes:
                cubes = []
                for c in b.cubes:
                    cd = OrderedDict()
                    cd["origin"] = [_num(v) for v in c.origin]
                    cd["size"] = [_num(v) for v in c.size]
                    if c.inflate:
                        cd["inflate"] = _num(c.inflate)
                    if c.pivot is not None and c.rotation is not None:
                        cd["pivot"] = [_num(v) for v in c.pivot]
                        cd["rotation"] = [_num(v) for v in c.rotation]
                    cd["uv"] = [int(c.uv[0]), int(c.uv[1])]
                    if c.mirror:
                        cd["mirror"] = True
                    cubes.append(cd)
                d["cubes"] = cubes
            if b.locators:
                d["locators"] = OrderedDict((k, [_num(x) for x in v]) for k, v in b.locators.items())
            bones.append(d)
        vw, vh, vo = self.visible_bounds
        return OrderedDict([
            ("format_version", "1.12.0"),
            ("minecraft:geometry", [OrderedDict([
                ("description", OrderedDict([
                    ("identifier", "geometry." + self.identifier),
                    ("texture_width", self.tex_w),
                    ("texture_height", self.tex_h),
                    ("visible_bounds_width", vw),
                    ("visible_bounds_height", vh),
                    ("visible_bounds_offset", list(vo)),
                ])),
                ("bones", bones),
            ])]),
        ])

    def write_geo(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(dump_blockbench_style(self.geo_dict()))
            f.write("\n")


def dump_blockbench_style(obj):
    """JSON layout similar to Blockbench exports (tabs, one cube per line)."""
    def compact(v):
        return json.dumps(v, separators=(", ", ": "))

    def fmt(v, ind, key=None):
        pad = "\t" * ind
        if isinstance(v, dict):
            if key in ("cubes",):
                pass
            items = []
            for k, x in v.items():
                if k in ("pivot", "rotation", "origin", "size", "uv", "visible_bounds_offset"):
                    items.append(pad + "\t" + json.dumps(k) + ": " + compact(x))
                else:
                    items.append(pad + "\t" + json.dumps(k) + ": " + fmt(x, ind + 1, k))
            return "{\n" + ",\n".join(items) + "\n" + pad + "}"
        if isinstance(v, list):
            if key == "cubes":
                return "[\n" + ",\n".join(pad + "\t" + compact(c) for c in v) + "\n" + pad + "]"
            if all(not isinstance(x, (dict, list)) for x in v):
                return compact(v)
            return "[\n" + ",\n".join(pad + "\t" + fmt(x, ind + 1) for x in v) + "\n" + pad + "]"
        return json.dumps(v)

    return fmt(obj, 0)


# ---------------------------------------------------------------- helpers
def rounded_blob(bone, center, size, tag, inflate=0.0, steps=1, mirror=False, share=None):
    """A box with chamfered edges built from three overlapping boxes (a 3D plus).

    Returns the list of cubes so a mirrored twin can share their UVs.
    """
    cx, cy, cz = center
    sx, sy, sz = size
    cubes = []
    k = steps
    specs = [
        (sx, sy - 2 * k, sz - 2 * k),
        (sx - 2 * k, sy, sz - 2 * k),
        (sx - 2 * k, sy - 2 * k, sz),
    ]
    for i, (a, b, c) in enumerate(specs):
        if a <= 0 or b <= 0 or c <= 0:
            continue
        cubes.append(bone.add([cx - a / 2, cy - b / 2, cz - c / 2], [a, b, c], inflate=inflate,
                              tag=tag, mirror=mirror,
                              share=None if share is None else share[len(cubes)]))
    return cubes


def mirror_x(v):
    return [-v[0], v[1], v[2]]


def check_integer_sizes(model):
    bad = []
    for c in model.cubes():
        for v in c.size:
            if abs(v - round(v)) > 1e-6:
                bad.append((c.bone.name, c.tag, c.size))
                break
    return bad
