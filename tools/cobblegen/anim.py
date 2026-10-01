"""Bedrock animation authoring + a small evaluator for previews.

Molang support in the evaluator is limited to what the generators emit:
q.anim_time, math.sin/cos (degrees), math.abs, math.clamp, math.lerp,
math.min/max, math.pow, math.sqrt, math.mod, math.floor, math.pi and
arithmetic / ternary-free expressions.
"""
import json
import math
import re
from collections import OrderedDict


def _n(v):
    if isinstance(v, str):
        return v
    r = round(float(v), 4)
    return int(r) if r == int(r) else r


class Anim:
    def __init__(self, name, length=None, loop=False):
        self.name = name
        self.length = length
        self.loop = loop
        self.bones = OrderedDict()

    def _ch(self, bone, ch):
        return self.bones.setdefault(bone, OrderedDict()).setdefault(ch, None)

    def expr(self, bone, ch, xyz):
        """Static or Molang channel: xyz is a list of 3 numbers/strings."""
        self.bones.setdefault(bone, OrderedDict())[ch] = [_n(v) for v in xyz]
        return self

    def keys(self, bone, ch, frames, smooth=True):
        """frames: list of (time, [x,y,z]) or (time, [x,y,z], 'linear'|'smooth')."""
        d = OrderedDict()
        for fr in frames:
            t, v = fr[0], fr[1]
            mode = fr[2] if len(fr) > 2 else ("smooth" if smooth else "linear")
            key = "%s" % _n(t)
            if isinstance(_n(t), int):
                key = "%d.0" % _n(t)
            if mode == "smooth":
                d[key] = OrderedDict([("post", [_n(x) for x in v]), ("lerp_mode", "catmullrom")])
            else:
                d[key] = [_n(x) for x in v]
        self.bones.setdefault(bone, OrderedDict())[ch] = d
        return self

    def to_dict(self):
        d = OrderedDict()
        if self.loop:
            d["loop"] = True
        if self.length is not None:
            d["animation_length"] = _n(self.length)
        d["bones"] = self.bones
        return d


def animation_file(prefix, anims):
    out = OrderedDict()
    out["format_version"] = "1.8.0"
    a = OrderedDict()
    for an in anims:
        a["animation.%s.%s" % (prefix, an.name)] = an.to_dict()
    out["animations"] = a
    return out


def write_animation_file(path, prefix, anims):
    data = animation_file(prefix, anims)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent="\t")
        f.write("\n")
    return data


# ------------------------------------------------------------- evaluator
_MOLANG_FUNCS = {
    "math.sin": "_sin", "math.cos": "_cos", "math.abs": "abs", "math.clamp": "_clamp",
    "math.lerp": "_lerp", "math.min": "min", "math.max": "max", "math.pow": "pow",
    "math.sqrt": "_sqrt", "math.mod": "_mod", "math.floor": "_floor", "math.exp": "_exp",
}


def _env(t):
    return {
        "_sin": lambda d: math.sin(math.radians(d)),
        "_cos": lambda d: math.cos(math.radians(d)),
        "_clamp": lambda v, a, b: max(a, min(b, v)),
        "_lerp": lambda a, b, x: a + (b - a) * x,
        "_sqrt": lambda v: math.sqrt(max(v, 0)),
        "_mod": lambda a, b: math.fmod(a, b),
        "_floor": math.floor,
        "_exp": math.exp,
        "abs": abs, "min": min, "max": max, "pow": pow,
        "t": t, "_pi": math.pi,
    }


_cache = {}


def molang(expr, t):
    if isinstance(expr, (int, float)):
        return float(expr)
    code = _cache.get(expr)
    if code is None:
        s = expr.lower()
        for k, v in _MOLANG_FUNCS.items():
            s = s.replace(k, v)
        s = re.sub(r"\b(q|query)\.anim_time\b", "t", s)
        s = s.replace("math.pi", "_pi")
        code = compile(s, "<molang>", "eval")
        _cache[expr] = code
    return float(eval(code, {"__builtins__": {}}, _env(t)))


def _vec(v, t):
    return [molang(x, t) for x in v]


def _keyframes(d):
    ks = []
    for k, v in d.items():
        tt = float(k)
        if isinstance(v, dict):
            pre = v.get("pre", v.get("post"))
            post = v.get("post", v.get("pre"))
            smooth = v.get("lerp_mode") == "catmullrom"
        else:
            pre = post = v
            smooth = False
        ks.append((tt, pre, post, smooth))
    ks.sort(key=lambda x: x[0])
    return ks


def _catmull(p0, p1, p2, p3, w):
    return 0.5 * ((2 * p1) + (-p0 + p2) * w + (2 * p0 - 5 * p1 + 4 * p2 - p3) * w * w
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * w * w * w)


def eval_channel(ch, t):
    if isinstance(ch, list):
        return _vec(ch, t)
    ks = _keyframes(ch)
    after = next((i for i, k in enumerate(ks) if k[0] > t), None)
    if after is None:
        return _vec(ks[-1][2], t)
    if after == 0:
        return _vec(ks[0][1], t)
    b = ks[after - 1]
    a = ks[after]
    alpha = (t - b[0]) / (a[0] - b[0])
    bv = _vec(b[2], t)
    av = _vec(a[1], t)
    if b[3] or a[3]:
        pb = _vec(ks[after - 2][2], t) if after - 2 >= 0 else bv
        pa = _vec(ks[after + 1][1], t) if after + 1 < len(ks) else av
        return [_catmull(pb[i], bv[i], av[i], pa[i], alpha) for i in range(3)]
    return [bv[i] + (av[i] - bv[i]) * alpha for i in range(3)]


def eval_anim(adict, t, pose=None, weight=1.0):
    """Accumulate an animation (dict form) at time t into pose."""
    pose = pose if pose is not None else {}
    length = adict.get("animation_length")
    if adict.get("loop") and length:
        t = math.fmod(t, length)
    elif length and t > length:
        t = length
    for bone, chans in adict["bones"].items():
        p = pose.setdefault(bone, {})
        for ch, val in chans.items():
            v = eval_channel(val, t)
            if ch == "position":
                cur = p.get("pos", [0, 0, 0])
                p["pos"] = [cur[i] + v[i] * weight for i in range(3)]
            elif ch == "rotation":
                cur = p.get("rot", [0, 0, 0])
                p["rot"] = [cur[i] + v[i] * weight for i in range(3)]
            elif ch == "scale":
                cur = p.get("scale", [1, 1, 1])
                p["scale"] = [cur[i] * (1 + (v[i] - 1) * weight) for i in range(3)]
    return pose


def _f(v):
    r = round(float(v), 3)
    if r == int(r):
        return str(int(r))
    return ("%.3f" % r).rstrip("0").rstrip(".")


def wave(amp, speed, phase=0.0, base=0.0, fn="sin"):
    """Molang: base + math.<fn>(q.anim_time*speed + phase)*amp (degrees)."""
    if amp == 0:
        return float(base)
    ph = ""
    if phase:
        ph = ("+" if phase > 0 else "-") + _f(abs(phase))
    core = "math.%s(q.anim_time*%s%s)*%s" % (fn, _f(speed), ph, _f(amp))
    if base:
        return "%s+%s" % (_f(base), core)
    return core


def awave(amp, speed, phase=0.0, base=0.0):
    """Molang: base + |sin(...)|*amp (hops)."""
    ph = ""
    if phase:
        ph = ("+" if phase > 0 else "-") + _f(abs(phase))
    core = "math.abs(math.sin(q.anim_time*%s%s))*%s" % (_f(speed), ph, _f(amp))
    if base:
        return "%s+%s" % (_f(base), core)
    return core


def swave(amp, speed, phase=0.0):
    """Scale channel value 1 + sin*amp."""
    return wave(amp, speed, phase, base=1.0)
