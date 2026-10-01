"""Blockbench project (.bbmodel, Bedrock Entity format) exporter.

Blockbench keeps Bedrock models with the X axis mirrored internally, so on the
way out positions/pivots get x negated and rotations get x/y negated - the exact
inverse of what Blockbench's bedrock codec does on import/export. Animation
values are stored unchanged (Blockbench writes them back verbatim).
"""
import base64
import io
import json
import uuid
from collections import OrderedDict

from PIL import Image


def _uid():
    return str(uuid.uuid4())


def _num(v):
    r = round(float(v), 4)
    return int(r) if r == int(r) else r


def _box_faces(cube, w, h, d, tex_index):
    """Blockbench box-UV face layout (Cube.updateUV)."""
    u0, v0 = cube.uv
    fl = [
        ["north", [d, d], [w, h]],
        ["east", [0, d], [d, h]],
        ["south", [d * 2 + w, d], [w, h]],
        ["west", [d + w, d], [d, h]],
        ["up", [d + w, d], [-w, -d]],
        ["down", [d + w * 2, 0], [-w, d]],
    ]
    if cube.mirror:
        for f in fl:
            f[1][0] += f[2][0]
            f[2][0] *= -1
        fl[1][1], fl[3][1] = fl[3][1][:], fl[1][1][:]
        fl[1][2], fl[3][2] = fl[3][2][:], fl[1][2][:]
    faces = OrderedDict()
    for name, frm, size in fl:
        faces[name] = OrderedDict([
            ("uv", [_num(frm[0] + u0), _num(frm[1] + v0), _num(frm[0] + size[0] + u0), _num(frm[1] + size[1] + v0)]),
            ("texture", tex_index),
        ])
    return faces


def _png_data_uri(arr):
    buf = io.BytesIO()
    Image.fromarray(arr, "RGBA").save(buf, format="PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def _texture(name, arr, idx):
    h, w = arr.shape[:2]
    return OrderedDict([
        ("path", ""), ("name", name), ("folder", ""), ("namespace", ""), ("id", str(idx)), ("group", ""),
        ("width", w), ("height", h), ("uv_width", w), ("uv_height", h),
        ("particle", False), ("use_as_default", idx == 0), ("layers_enabled", False), ("sync_to_project", ""),
        ("render_mode", "default"), ("render_sides", "auto"), ("frame_time", 1), ("frame_order_type", "loop"),
        ("frame_order", ""), ("frame_interpolate", False), ("visible", True), ("internal", True), ("saved", False),
        ("uuid", _uid()), ("relative_path", ""), ("source", _png_data_uri(arr)),
    ])


def _keyframe(channel, time, values, interp="linear", pre=None):
    def dp(v):
        return OrderedDict((k, x if isinstance(x, str) else _num(x)) for k, x in zip("xyz", v))
    points = [dp(values)] if pre is None else [dp(pre), dp(values)]
    return OrderedDict([
        ("channel", channel), ("data_points", points), ("uuid", _uid()), ("time", _num(time)), ("color", -1),
        ("interpolation", interp), ("bezier_linked", True),
        ("bezier_left_time", [-0.1, -0.1, -0.1]), ("bezier_left_value", [0, 0, 0]),
        ("bezier_right_time", [0.1, 0.1, 0.1]), ("bezier_right_value", [0, 0, 0]),
    ])


def _animation(full_name, adict, group_ids):
    animators = OrderedDict()
    for bone, chans in adict["bones"].items():
        if bone not in group_ids:
            continue
        kfs = []
        for ch, val in chans.items():
            if isinstance(val, list):
                kfs.append(_keyframe(ch, 0, val))
                continue
            for t, kv in val.items():
                if isinstance(kv, dict):
                    post = kv.get("post", kv.get("pre"))
                    pre = kv.get("pre")
                    interp = "catmullrom" if kv.get("lerp_mode") == "catmullrom" else "linear"
                    kfs.append(_keyframe(ch, float(t), post, interp, pre if pre is not None and pre != post else None))
                else:
                    kfs.append(_keyframe(ch, float(t), kv))
        animators[group_ids[bone]] = OrderedDict([("name", bone), ("type", "bone"), ("keyframes", kfs)])
    length = adict.get("animation_length", 0)
    loop = "loop" if adict.get("loop") else "once"
    return OrderedDict([
        ("uuid", _uid()), ("name", full_name), ("loop", loop), ("override", False), ("length", _num(length)),
        ("snapping", 24), ("selected", False), ("saved", True), ("path", ""), ("anim_time_update", ""),
        ("blend_weight", ""), ("start_delay", ""), ("loop_delay", ""), ("animators", animators),
    ])


def export(model, textures, anim_file, path, face_texture=None):
    """textures: list of (name, rgba array); first one is the default texture.
    anim_file: dict in Bedrock animation file form ({"animations": {...}}).
    face_texture: optional callable(cube) -> texture index override for that cube."""
    elements = []
    group_ids = {}
    groups = OrderedDict()
    for b in model.bones.values():
        gid = _uid()
        group_ids[b.name] = gid
        g = OrderedDict([
            ("name", b.name), ("origin", [_num(-b.pivot[0]), _num(b.pivot[1]), _num(b.pivot[2])]),
            ("color", len(groups) % 8), ("uuid", gid), ("export", True), ("mirror_uv", False),
            ("isOpen", False), ("locked", False), ("visibility", True), ("autouv", 0),
        ])
        if b.rotation and any(abs(r) > 1e-9 for r in b.rotation):
            g["rotation"] = [_num(-b.rotation[0]), _num(-b.rotation[1]), _num(b.rotation[2])]
        g["children"] = []
        groups[b.name] = g
        for i, c in enumerate(b.cubes):
            w, h, d = (int(round(s)) for s in c.size)
            ox, oy, oz = c.origin
            sx, sy, sz = c.size
            frm = [-(ox + sx), oy, oz]
            to = [frm[0] + sx, oy + sy, oz + sz]
            if c.rotation is not None:
                origin = [-c.pivot[0], c.pivot[1], c.pivot[2]]
                rot = [-c.rotation[0], -c.rotation[1], c.rotation[2]]
            else:
                origin = [-b.pivot[0], b.pivot[1], b.pivot[2]]
                rot = [0, 0, 0]
            tex_idx = face_texture(c) if face_texture else 0
            cid = _uid()
            el = OrderedDict([
                ("name", c.tag or b.name), ("box_uv", True), ("rescale", False), ("locked", False),
                ("render_order", "default"), ("allow_mirror_modeling", True),
                ("from", [_num(v) for v in frm]), ("to", [_num(v) for v in to]),
                ("autouv", 0), ("color", groups[b.name]["color"]), ("inflate", _num(c.inflate)),
                ("rotation", [_num(v) for v in rot]), ("origin", [_num(v) for v in origin]),
                ("uv_offset", [int(c.uv[0]), int(c.uv[1])]), ("mirror_uv", bool(c.mirror)),
                ("faces", _box_faces(c, w, h, d, tex_idx)), ("type", "cube"), ("uuid", cid),
            ])
            elements.append(el)
            g["children"].append(cid)
        for ln, lp in b.locators.items():
            lid = _uid()
            elements.append(OrderedDict([
                ("name", ln), ("position", [_num(-lp[0]), _num(lp[1]), _num(lp[2])]), ("rotation", [0, 0, 0]),
                ("ignore_inherited_scale", False), ("visibility", True), ("locked", False),
                ("type", "locator"), ("uuid", lid),
            ]))
            g["children"].append(lid)
    roots = []
    for b in model.bones.values():
        if b.parent is None:
            roots.append(groups[b.name])
        else:
            groups[b.parent]["children"].append(groups[b.name])

    vw, vh, vo = model.visible_bounds
    anims = [_animation(n, a, group_ids) for n, a in anim_file["animations"].items()]
    proj = OrderedDict([
        ("meta", OrderedDict([("format_version", "4.10"), ("model_format", "bedrock"), ("box_uv", True)])),
        ("name", model.identifier),
        ("model_identifier", model.identifier),
        ("visible_box", [vw, vh, vo[1]]),
        ("variable_placeholders", ""),
        ("variable_placeholder_buttons", []),
        ("timeline_setups", []),
        ("unhandled_root_fields", OrderedDict()),
        ("resolution", OrderedDict([("width", model.tex_w), ("height", model.tex_h)])),
        ("elements", elements),
        ("outliner", roots),
        ("textures", [_texture(n, arr, i) for i, (n, arr) in enumerate(textures)]),
        ("animations", anims),
    ])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(proj, f, ensure_ascii=False)
    return proj


def to_geo_bones(proj):
    """Inverse conversion (what Blockbench exports) - used to round-trip test the exporter."""
    els = {e["uuid"]: e for e in proj["elements"]}
    out = {}

    def walk(g, parent):
        cubes, locs = [], {}
        for ch in g["children"]:
            if isinstance(ch, dict):
                continue
            e = els[ch]
            if e["type"] == "locator":
                locs[e["name"]] = [-e["position"][0], e["position"][1], e["position"][2]]
                continue
            size = [e["to"][i] - e["from"][i] for i in range(3)]
            origin = [-(e["from"][0] + size[0]), e["from"][1], e["from"][2]]
            cubes.append((origin, size, e["uv_offset"], e["mirror_uv"], e["inflate"]))
        rot = g.get("rotation")
        out[g["name"]] = {
            "parent": parent, "pivot": [-g["origin"][0], g["origin"][1], g["origin"][2]],
            "rotation": [-rot[0], -rot[1], rot[2]] if rot else None, "cubes": cubes, "locators": locs,
        }
        for ch in g["children"]:
            if isinstance(ch, dict):
                walk(ch, g["name"])

    for r in proj["outliner"]:
        walk(r, None)
    return out
