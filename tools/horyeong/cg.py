"""
cg.py - Cobblemon geometry toolkit.

Replicates exactly how Cobblemon 1.8.1 (TexturedModel.createWithUvOverride) turns a
Bedrock .geo.json into Minecraft ModelParts, and how MC's ModelPart.Cube lays out box UVs,
so that texture painting and preview rendering match the game 1:1.

Coordinate spaces
  B : Bedrock file space (what goes into the json). +Y up, front = -Z, creature-left = +X
  J : Java ModelPart space, J = (xb, -yb, zb)
  W : world/view space after LivingEntityRenderer scale(-1,-1,1): W = (-xj, -yj, zj) = (-xb, yb, zb)
"""
import math, json, re
import numpy as np

# ---------------------------------------------------------------- data model
class Cube:
    def __init__(self, origin, size, tag="fur", uv=None, pivot=None, rotation=None, inflate=0.0, meta=None):
        self.origin = [float(v) for v in origin]
        self.size = [float(v) for v in size]
        self.tag = tag
        self.uv = uv
        self.pivot = pivot
        self.rotation = rotation
        self.inflate = inflate
        self.meta = meta or {}

class Bone:
    def __init__(self, name, parent=None, pivot=(0, 0, 0), rotation=None, locators=None):
        self.name = name
        self.parent = parent
        self.pivot = [float(v) for v in pivot]
        self.rotation = rotation
        self.cubes = []
        self.locators = locators or {}

    def cube(self, origin, size, tag="fur", **kw):
        c = Cube(origin, size, tag, **kw)
        c.bone = self.name
        self.cubes.append(c)
        return c

class Model:
    def __init__(self, identifier, tex_w=256, tex_h=256):
        self.identifier = identifier
        self.tex_w, self.tex_h = tex_w, tex_h
        self.bones = []
        self.by_name = {}

    def bone(self, name, parent=None, pivot=(0, 0, 0), rotation=None, locators=None):
        assert name not in self.by_name, name
        b = Bone(name, parent, pivot, rotation, locators)
        self.bones.append(b)
        self.by_name[name] = b
        return b

    def all_cubes(self):
        for b in self.bones:
            for c in b.cubes:
                yield b, c

    # ------------------------------------------------------------ uv packing
    def pack_uvs(self, width, height=None, order=None):
        """Skyline packer for box-uv footprints. Integer offsets."""
        height = height or self.tex_h
        items = []
        for b, c in self.all_cubes():
            dx, dy, dz = c.size
            w = int(math.ceil(2 * (dx + dz) - 1e-6))
            h = int(math.ceil(dz + dy - 1e-6))
            items.append((max(w, 1), max(h, 1), c))
        items.sort(key=lambda t: (-t[1], -t[0]))
        sky = [0] * width
        for w, h, c in items:
            best = None
            for x in range(0, width - w + 1):
                y = max(sky[x:x + w])
                if best is None or y < best[1] or (y == best[1] and x < best[0]):
                    best = (x, y)
            if best is None or best[1] + h > height:
                raise RuntimeError("uv atlas overflow")
            x, y = best
            for i in range(x, x + w):
                sky[i] = y + h
            c.uv = [x, y]
        self.tex_w, self.tex_h = width, height
        return max(sky)

    # ------------------------------------------------------------ export
    def to_geo_json(self, visible_bounds=(6, 5, (0, 2, 0))):
        def r(v):
            v = round(float(v), 4)
            return int(v) if v == int(v) else v
        bones = []
        for b in self.bones:
            d = {"name": b.name}
            if b.parent:
                d["parent"] = b.parent
            d["pivot"] = [r(v) for v in b.pivot]
            if b.rotation and any(abs(v) > 1e-9 for v in b.rotation):
                d["rotation"] = [r(v) for v in b.rotation]
            if b.cubes:
                cl = []
                for c in b.cubes:
                    cd = {"origin": [r(v) for v in c.origin], "size": [r(v) for v in c.size]}
                    if c.pivot is not None and c.rotation is not None:
                        cd["pivot"] = [r(v) for v in c.pivot]
                        cd["rotation"] = [r(v) for v in c.rotation]
                    if c.inflate:
                        cd["inflate"] = r(c.inflate)
                    cd["uv"] = [int(c.uv[0]), int(c.uv[1])]
                    cl.append(cd)
                d["cubes"] = cl
            if b.locators:
                d["locators"] = {k: [r(x) for x in v] for k, v in b.locators.items()}
            bones.append(d)
        vb = visible_bounds
        return {
            "format_version": "1.12.0",
            "minecraft:geometry": [{
                "description": {
                    "identifier": self.identifier,
                    "texture_width": self.tex_w,
                    "texture_height": self.tex_h,
                    "visible_bounds_width": vb[0],
                    "visible_bounds_height": vb[1],
                    "visible_bounds_offset": list(vb[2]),
                },
                "bones": bones,
            }],
        }


# ---------------------------------------------------------------- java conversion
def rot_zyx(xr, yr, zr):
    """Quaternionf().rotationZYX(z, y, x) as 3x3 matrix = Rz * Ry * Rx"""
    cx, sx = math.cos(xr), math.sin(xr)
    cy, sy = math.cos(yr), math.sin(yr)
    cz, sz = math.cos(zr), math.sin(zr)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


class JPart:
    """A java ModelPart (bone or rotated-cube sub part)."""
    def __init__(self, name, parent, offset, rot_rad):
        self.name = name
        self.parent = parent
        self.offset = np.array(offset, float)
        self.rot = np.array(rot_rad, float)
        self.boxes = []   # (min(3), dims(3), grow, cube)
        self.children = []


def build_java(model):
    """Port of TexturedModel.createWithUvOverride. Returns dict name->JPart (incl. locator parts)."""
    bones = list(model.bones)
    loc_bones = []
    for b in bones:
        for lname, off in b.locators.items():
            lb = Bone("@" + lname, b.name, off[:3], None)
            loc_bones.append(lb)
    allb = bones + loc_bones
    bmap = {}
    parts = {}
    for b in allb:
        bmap[b.name] = b
        if b.parent is None:
            off = (0, 0, 0)
        else:
            p = bmap[b.parent].pivot
            off = (-(p[0] - b.pivot[0]), p[1] - b.pivot[1], -(p[2] - b.pivot[2]))
        rot = [math.radians(v) for v in (b.rotation or (0, 0, 0))]
        jp = JPart(b.name, b.parent, off, rot)
        parts[b.name] = jp
        for ci, c in enumerate(b.cubes):
            if c.rotation is not None:
                piv = c.pivot
                sub = JPart("%" + b.name + "%" + str(ci), b.name,
                            (-(b.pivot[0] - piv[0]), b.pivot[1] - piv[1], -(b.pivot[2] - piv[2])),
                            [math.radians(v) for v in c.rotation])
                parts[sub.name] = sub
                target = sub
            else:
                piv = b.pivot
                target = jp
            mn = (c.origin[0] - piv[0], -(c.origin[1] - piv[1] + c.size[1]), c.origin[2] - piv[2])
            target.boxes.append((np.array(mn, float), np.array(c.size, float), c.inflate, c))
    for p in parts.values():
        if p.parent:
            parts[p.parent].children.append(p)
    return parts


def mc_polygons(mn, dims, grow, uv, tex_w, tex_h):
    """ModelPart.Cube constructor -> list of (dirname, [4 verts], [4 uvs(texel units)], normal)"""
    minX, minY, minZ = mn
    dX, dY, dZ = dims
    f = minX + dX; g = minY + dY; h = minZ + dZ
    minX -= grow; minY -= grow; minZ -= grow
    f += grow; g += grow; h += grow
    V = lambda x, y, z: np.array([x, y, z], float)
    v1 = V(minX, minY, minZ); v2 = V(f, minY, minZ); v3 = V(f, g, minZ); v4 = V(minX, g, minZ)
    v5 = V(minX, minY, h); v6 = V(f, minY, h); v7 = V(f, g, h); v8 = V(minX, g, h)
    u0, vv0 = uv
    j = u0; k = u0 + dZ; l = u0 + dZ + dX; m = u0 + dZ + dX + dX; n = u0 + dZ + dX + dZ; o = u0 + dZ + dX + dZ + dX
    p = vv0; q = vv0 + dZ; r = vv0 + dZ + dY
    polys = [
        ("DOWN",  [v6, v5, v1, v2], k, p, l, q, (0, -1, 0)),
        ("UP",    [v3, v4, v8, v7], l, q, m, p, (0, 1, 0)),
        ("WEST",  [v1, v5, v8, v4], j, q, k, r, (-1, 0, 0)),
        ("NORTH", [v2, v1, v4, v3], k, q, l, r, (0, 0, -1)),
        ("EAST",  [v6, v2, v3, v7], l, q, n, r, (1, 0, 0)),
        ("SOUTH", [v5, v6, v7, v8], n, q, o, r, (0, 0, 1)),
    ]
    out = []
    for name, verts, uA, vA, uB, vB, nrm in polys:
        uvs = [(uB, vA), (uA, vA), (uA, vB), (uB, vB)]
        out.append((name, verts, uvs, np.array(nrm, float)))
    return out

# java direction -> semantic face name in B space
FACE_NAME = {"DOWN": "top", "UP": "bottom", "WEST": "right", "EAST": "left", "NORTH": "front", "SOUTH": "back"}


# ---------------------------------------------------------------- posing
def world_mats(parts, overrides=None):
    """Returns name -> (R 3x3, t 3) mapping part-local java coords -> java model coords.
    overrides: name -> dict(pos=(x,y,z) bedrock units, rot=(deg), scale=(sx,sy,sz))"""
    overrides = overrides or {}
    res = {}

    def visit(p, R0, t0):
        off = p.offset.copy()
        rot = p.rot.copy()
        sc = np.ones(3)
        o = overrides.get(p.name)
        if o:
            if "pos" in o:
                px, py, pz = o["pos"]
                off += np.array([px, -py, pz])      # yMul = -1 for positions
            if "rot" in o:
                rot += np.radians(np.array(o["rot"], float))
            if "scale" in o:
                sc = sc * np.array(o["scale"], float)
        R = R0 @ rot_zyx(*rot) @ np.diag(sc)
        t = t0 + R0 @ off
        res[p.name] = (R, t)
        for ch in p.children:
            visit(ch, R, t)

    for p in parts.values():
        if p.parent is None:
            visit(p, np.eye(3), np.zeros(3))
    return res


def collect_quads(model, parts, mats):
    """All polygons transformed to java model space. Returns list of dicts."""
    quads = []
    for name, p in parts.items():
        R, t = mats[name]
        for mn, dims, grow, c in p.boxes:
            for dname, verts, uvs, nrm in mc_polygons(mn, dims, grow, c.uv or [0, 0], model.tex_w, model.tex_h):
                vw = [R @ v + t for v in verts]
                n = R @ nrm
                nl = np.linalg.norm(n)
                quads.append(dict(dir=dname, verts=vw, local=verts, uvs=uvs, normal=n / (nl if nl else 1),
                                  cube=c, part=name, box=(mn, dims)))
    return quads


# ---------------------------------------------------------------- animation evaluation
_MOLANG_SUBS = [
    (r"math\.sin\(", "_msin("), (r"math\.cos\(", "_mcos("), (r"math\.abs\(", "abs("),
    (r"math\.clamp\(", "_mclamp("), (r"math\.min\(", "min("), (r"math\.max\(", "max("),
    (r"math\.pow\(", "pow("), (r"math\.sqrt\(", "math.sqrt("), (r"math\.lerp\(", "_mlerp("),
    (r"math\.pi", "math.pi"), (r"(query|q)\.anim_time", "_t"), (r"(query|q)\.life_time", "_t"),
]
_ENV = {"_msin": lambda d: math.sin(math.radians(d)), "_mcos": lambda d: math.cos(math.radians(d)),
        "_mclamp": lambda x, a, b: max(a, min(b, x)), "_mlerp": lambda a, b, t: a + (b - a) * t, "math": math}


def mol(expr, t):
    if isinstance(expr, (int, float)):
        return float(expr)
    s = expr
    for a, b in _MOLANG_SUBS:
        s = re.sub(a, b, s)
    env = dict(_ENV)
    env["_t"] = t
    return float(eval(s, {"__builtins__": {"abs": abs, "min": min, "max": max, "pow": pow}}, env))


def _vec(v, t):
    if isinstance(v, (int, float, str)):
        x = mol(v, t)
        return [x, x, x]
    return [mol(e, t) for e in v]


def eval_channel(ch, t):
    if isinstance(ch, (list, int, float, str)):
        return _vec(ch, t)
    keys = sorted(((float(k), v) for k, v in ch.items()), key=lambda kv: kv[0])

    def pre(v):
        return v.get("pre", v.get("post")) if isinstance(v, dict) else v

    def post(v):
        return v.get("post", v.get("pre")) if isinstance(v, dict) else v

    if t <= keys[0][0]:
        return _vec(pre(keys[0][1]), t)
    if t >= keys[-1][0]:
        return _vec(post(keys[-1][1]), t)
    for i in range(len(keys) - 1):
        t0, a = keys[i]
        t1, b = keys[i + 1]
        if t0 <= t <= t1:
            alpha = (t - t0) / (t1 - t0) if t1 > t0 else 0
            A = _vec(post(a), t)
            Bv = _vec(pre(b), t)
            smooth = (isinstance(a, dict) and a.get("lerp_mode") == "catmullrom") or \
                     (isinstance(b, dict) and b.get("lerp_mode") == "catmullrom")
            if smooth:
                P0 = _vec(post(keys[i - 1][1]), t) if i > 0 else A
                P3 = _vec(pre(keys[i + 2][1]), t) if i + 2 < len(keys) else Bv
                s = alpha
                return [0.5 * ((2 * A[k]) + (-P0[k] + Bv[k]) * s + (2 * P0[k] - 5 * A[k] + 4 * Bv[k] - P3[k]) * s * s +
                               (-P0[k] + 3 * A[k] - 3 * Bv[k] + P3[k]) * s ** 3) for k in range(3)]
            return [A[k] + (Bv[k] - A[k]) * alpha for k in range(3)]
    return [0, 0, 0]


def anim_overrides(anim, t, weight=1.0, base=None):
    """Bedrock animation -> overrides dict at time t (seconds)."""
    out = {} if base is None else {k: dict(v) for k, v in base.items()}
    length = anim.get("animation_length")
    if anim.get("loop") is True and length:
        t = t % length
    for bname, ch in anim.get("bones", {}).items():
        o = out.setdefault(bname, {})
        if "rotation" in ch:
            r = [v * weight for v in eval_channel(ch["rotation"], t)]
            o["rot"] = [a + b for a, b in zip(o.get("rot", (0, 0, 0)), r)]
        if "position" in ch:
            p = [v * weight for v in eval_channel(ch["position"], t)]
            o["pos"] = [a + b for a, b in zip(o.get("pos", (0, 0, 0)), p)]
        if "scale" in ch:
            s = eval_channel(ch["scale"], t)
            s = [1 - (1 - v) * weight for v in s]
            o["scale"] = [a * b for a, b in zip(o.get("scale", (1, 1, 1)), s)]
    return out


# ---------------------------------------------------------------- renderer
LIGHT0 = np.array([0.2, 1.0, -0.7]); LIGHT0 /= np.linalg.norm(LIGHT0)
LIGHT1 = np.array([-0.2, 1.0, 0.7]); LIGHT1 /= np.linalg.norm(LIGHT1)


def to_w(v):
    return np.array([-v[0], -v[1], v[2]])


def render(model, parts, texture, overrides=None, yaw=35, pitch=12, scale=8, size=(520, 520),
           center=None, emissive=None, bg=(46, 52, 64), ground=True, quads=None, cull=True, idbuf=None):
    """Orthographic software render. texture/emissive: HxWx4 uint8 arrays. yaw rotates the model
    (0 = facing the camera)."""
    mats = world_mats(parts, overrides)
    quads = quads or collect_quads(model, parts, mats)
    W, H = size
    img = np.zeros((H, W, 3), float)
    img[:] = np.array(bg, float)
    zbuf = np.full((H, W), np.inf)
    cy_, sy_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(-pitch)), math.sin(math.radians(-pitch))
    # camera looks along +Z of view at a model that faces -Z in W
    Ry = np.array([[cy_, 0, sy_], [0, 1, 0], [-sy_, 0, cy_]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    V = Rx @ Ry
    if center is None:
        center = np.array([0, 22, 0])
    ctr = V @ np.array(center, float)
    texH, texW = texture.shape[:2]

    def proj(pw):
        pv = V @ pw - ctr
        return np.array([W / 2 - pv[0] * scale, H / 2 - pv[1] * scale, pv[2]])

    layers = [(texture, False)]
    if emissive is not None:
        layers.append((emissive, True))
    for tex, emis in layers:
        for qi, qd in enumerate(quads):
            vw = [to_w(v) for v in qd["verts"]]
            nw = to_w(qd["normal"])
            nv = V @ nw
            if cull and nv[2] > 1e-6:   # facing away (camera looks toward +z view, model faces -z)
                continue
            if np.linalg.norm(np.cross(vw[1] - vw[0], vw[3] - vw[0])) < 1e-9 and np.linalg.norm(np.cross(vw[2] - vw[1], vw[3] - vw[1])) < 1e-9:
                continue
            shade = min(1.0, 0.4 + 0.6 * (max(0, nw @ LIGHT0) + max(0, nw @ LIGHT1)))
            P = [proj(v) for v in vw]
            uv = [np.array(u, float) for u in qd["uvs"]]
            for tri in ((0, 1, 2), (0, 2, 3)):
                a, b, c = (P[i] for i in tri)
                ua, ub, uc = (uv[i] for i in tri)
                xmin = int(max(0, math.floor(min(a[0], b[0], c[0]))))
                xmax = int(min(W - 1, math.ceil(max(a[0], b[0], c[0]))))
                ymin = int(max(0, math.floor(min(a[1], b[1], c[1]))))
                ymax = int(min(H - 1, math.ceil(max(a[1], b[1], c[1]))))
                if xmax < xmin or ymax < ymin:
                    continue
                den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
                if abs(den) < 1e-12:
                    continue
                xs, ys = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
                w1 = ((b[1] - c[1]) * (xs - c[0]) + (c[0] - b[0]) * (ys - c[1])) / den
                w2 = ((c[1] - a[1]) * (xs - c[0]) + (a[0] - c[0]) * (ys - c[1])) / den
                w3 = 1 - w1 - w2
                inside = (w1 >= -1e-6) & (w2 >= -1e-6) & (w3 >= -1e-6)
                if not inside.any():
                    continue
                z = w1 * a[2] + w2 * b[2] + w3 * c[2]
                u = w1 * ua[0] + w2 * ub[0] + w3 * uc[0]
                v = w1 * ua[1] + w2 * ub[1] + w3 * uc[1]
                ui = np.clip(np.floor(u).astype(int), 0, texW - 1)
                vi = np.clip(np.floor(v).astype(int), 0, texH - 1)
                texel = tex[vi, ui]
                zs = zbuf[ymin:ymax + 1, xmin:xmax + 1]
                if emis:
                    ok = inside & (texel[..., 3] > 25) & (z <= zs + 0.02)
                else:
                    ok = inside & (texel[..., 3] > 25) & (z < zs)
                if not ok.any():
                    continue
                sub = img[ymin:ymax + 1, xmin:xmax + 1]
                col = texel[..., :3].astype(float)
                if emis:
                    al = texel[..., 3:4] / 255.0
                    sub[ok] = (sub * (1 - al) + col * al)[ok]
                else:
                    sub[ok] = (col * shade)[ok]
                    zs[ok] = z[ok]
                    if idbuf is not None:
                        idbuf[ymin:ymax + 1, xmin:xmax + 1][ok] = qi
    return np.clip(img, 0, 255).astype(np.uint8)


def load_geo(path):
    d = json.load(open(path))
    g = d["minecraft:geometry"][0]
    m = Model(g["description"]["identifier"], g["description"]["texture_width"], g["description"]["texture_height"])
    for b in g["bones"]:
        bo = m.bone(b["name"], b.get("parent"), b.get("pivot", [0, 0, 0]), b.get("rotation"),
                    {k: (v if isinstance(v, list) else v["offset"]) for k, v in b.get("locators", {}).items()})
        for c in b.get("cubes", []):
            cc = bo.cube(c["origin"], c["size"], uv=c.get("uv", [0, 0]), pivot=c.get("pivot"), rotation=c.get("rotation"), inflate=c.get("inflate", 0))
    return m
