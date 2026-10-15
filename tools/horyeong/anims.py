"""
Horyeong bedrock animations.

Conventions (bedrock file values, as Cobblemon applies them):
  rotation x+ : nose pitches down / hanging limbs swing backward / tail rises
  rotation y+ : nose turns to the creature's right (-X)
  rotation z+ : top rolls toward the creature's left (+X)
  position y+ : up, z+ : backward
Pose animations (idle/walk/sleep and the primary physical/special/status/faint) are full poses
relative to the standing rest pose; stateful ones (cry, recoil, blink, quirks) are additive.
"""
import json
import numpy as np

NAME = "horyeong"
SIDES = (("left", 1), ("right", -1))


def fmt(v):
    v = float(v)
    if abs(v) < 5e-4:
        return "0"
    s = ("%.3f" % v).rstrip("0").rstrip(".")
    return s


def osc(base=0.0, amp=0.0, freq=90.0, phase=0.0, fn="sin"):
    """molang: base + sin(t*freq + phase) * amp ; numbers when static"""
    if abs(amp) < 1e-6:
        return round(float(base), 3)
    ph = "" if abs(phase) < 1e-6 else ("+%s" % fmt(phase) if phase > 0 else "-%s" % fmt(-phase))
    term = "math.%s(q.anim_time*%s%s)*%s" % (fn, fmt(freq), ph, fmt(abs(amp)))
    sign = "+" if amp > 0 else "-"
    if abs(base) < 1e-6:
        return term if amp > 0 else "0-" + term
    return "%s%s%s" % (fmt(base), sign, term)


def lift(freq, phase, amp, base=0.0):
    """only-positive half wave: base + max(0, -cos(t*f+p)) * amp  (raised while the leg swings forward)"""
    ph = "" if abs(phase) < 1e-6 else ("+%s" % fmt(phase) if phase > 0 else "-%s" % fmt(-phase))
    term = "math.max(0,0-math.cos(q.anim_time*%s%s))*%s" % (fmt(freq), ph, fmt(abs(amp)))
    sign = "+" if amp > 0 else "-"
    if abs(base) < 1e-6:
        return term if amp > 0 else "0-" + term
    return "%s%s%s" % (fmt(base), sign, term)


class Anim:
    def __init__(self, length=None, loop=False, hold=False):
        self.length = length
        self.loop = loop
        self.hold = hold
        self.bones = {}

    def set(self, bone, ch, value):
        self.bones.setdefault(bone, {})[ch] = [v if isinstance(v, str) else round(float(v), 3) for v in value]

    def keys(self, bone, ch, frames, smooth=True):
        d = {}
        for t, v in frames:
            vv = [x if isinstance(x, str) else round(float(x), 3) for x in v]
            key = fmt(t) if fmt(t) != "0" else "0.0"
            if "." not in key:
                key += ".0"
            d[key] = {"post": vv, "lerp_mode": "catmullrom"} if smooth else vv
        self.bones.setdefault(bone, {})[ch] = d

    def to_json(self):
        out = {}
        if self.loop:
            out["loop"] = True
        elif self.hold:
            out["loop"] = "hold_on_last_frame"
        if self.length:
            out["animation_length"] = round(self.length, 4)
        out["bones"] = self.bones
        return out


def pose_values(ov):
    """overrides from poses.py -> {bone: {'rotation': [...], 'position': [...], 'scale': [...]}}"""
    res = {}
    for b, o in ov.items():
        d = {}
        if "rot" in o:
            d["rotation"] = [float(x) for x in o["rot"]]
        if "pos" in o:
            d["position"] = [float(x) for x in o["pos"]]
        if "scale" in o:
            d["scale"] = [float(x) for x in o["scale"]]
        res[b] = d
    return res


def P(pose, bone, ch, default=(0, 0, 0)):
    return list(pose.get(bone, {}).get(ch, default))


# ------------------------------------------------------------------ fur secondary motion helpers
def fur_sway(a, f, amp=1.0, phase=0.0, base=None):
    """gentle drifting of beard / mustache / brows / cheek tufts"""
    base = base or {}
    def b(n, ch="rotation"):
        return base.get(n, {}).get(ch, [0, 0, 0])
    for i, n in enumerate(("beard", "beard2", "beard3")):
        r = b(n)
        a.set(n, "rotation", [osc(r[0], 3 * amp, f, phase - 40 * i), osc(r[1], 0, f), osc(r[2], 2 * amp, f, phase - 50 * i)])
    for s, sx in SIDES:
        for i, n in enumerate(("mustache_%s" % s, "mustache_%s2" % s, "mustache_%s3" % s, "mustache_%s4" % s)):
            r = b(n)
            a.set(n, "rotation", [osc(r[0], 1.5 * amp, f, phase - 30 * i), osc(r[1], 0, f),
                                  osc(r[2], 3.5 * amp * sx, f, phase - 45 * i)])
        for i, n in enumerate(("brow_%s2" % s, "brow_%s3" % s)):
            r = b(n)
            a.set(n, "rotation", [osc(r[0], 0, f), osc(r[1], 0, f), osc(r[2], 3 * amp * sx, f, phase - 60 - 50 * i)])
        r = b("cheek_%s2" % s)
        a.set("cheek_%s2" % s, "rotation", [osc(r[0], 0, f), osc(r[1], 3 * amp * sx, f, phase - 90), osc(r[2], 2 * amp * sx, f, phase - 30)])


def tail_motion(a, f, base, amp_y=6.0, amp_x=2.0, phase=0.0, lag=35.0, start=0, scale=None):
    names = ["tail"] + ["tail%d" % i for i in range(2, 8)]
    for i, n in enumerate(names):
        r = base.get(n, {}).get("rotation", [0, 0, 0])
        k = 1.0 if scale is None else scale[i]
        if i < start:
            a.set(n, "rotation", r)
            continue
        a.set(n, "rotation", [osc(r[0], amp_x * k, 2 * f, phase - lag * i), osc(r[1], amp_y * k, f, phase - lag * i), r[2]])


# ------------------------------------------------------------------ animations
def ground_idle(sit):
    """Sitting like the concept art: slow breathing, drifting beard, idle tail tip."""
    L = 4.0
    f = 90.0
    a = Anim(L, loop=True)
    for bone, d in sit.items():
        if bone.startswith("tail"):
            continue
        for ch, v in d.items():
            a.set(bone, ch, v)
    bp = P(sit, "body", "position"); br = P(sit, "body", "rotation")
    a.set("body", "position", [bp[0], osc(bp[1], 0.12, f * 2), bp[2]])
    a.set("body", "rotation", [osc(br[0], 0.6, f * 2, 30), br[1], br[2]])
    a.set("chest", "rotation", [osc(P(sit, "chest", "rotation")[0], 1.0, f * 2, 60), 0, 0])
    hr = P(sit, "head", "rotation")
    a.set("neck", "rotation", [osc(P(sit, "neck", "rotation")[0], 0.8, f * 2, 120), 0, 0])
    a.set("head", "rotation", [osc(hr[0], 1.2, f * 2, 160), osc(0, 2.0, f, 0), osc(0, 1.2, f, 60)])
    for s, sx in SIDES:
        a.set("ear_%s" % s, "rotation", [0, 0, osc(0, 2.5 * sx, f * 2, 20 + 40 * (sx < 0))])
    fur_sway(a, f, 1.0)
    # tail stays on the ground, last segments flick lazily
    names = ["tail"] + ["tail%d" % i for i in range(2, 8)]
    for i, n in enumerate(names):
        r = P(sit, n, "rotation")
        if i < 4:
            a.set(n, "rotation", r)
        else:
            k = (i - 3) / 3.0
            a.set(n, "rotation", [osc(r[0], -5 * k, f, -50 * i), osc(r[1], 7 * k, f, -45 * i), r[2]])
    return a


def battle_idle():
    """Standing, low guarded stance, tail swishing."""
    L = 2.0
    f = 180.0
    a = Anim(L, loop=True)
    a.set("body", "position", [0, osc(-1.2, 0.25, f, 0), osc(0.6, 0, f)])
    a.set("body", "rotation", [osc(2.5, 0.8, f, 40), 0, 0])
    a.set("chest", "rotation", [osc(-1, 1.2, f, 80), 0, 0])
    a.set("neck", "rotation", [osc(10, 1.5, f, 110), 0, 0])
    a.set("head", "rotation", [osc(-6, 1.5, f, 150), 0, 0])
    for s, sx in SIDES:
        a.set("leg_front_%s" % s, "rotation", [osc(-6, 0.8, f, 40), 0, -3 * sx])
        a.set("leg_front_%s" % s, "position", [0, osc(0.6, 0.15, f), 0])
        a.set("leg_front_%s2" % s, "rotation", [osc(4, 0.8, f, 40), 0, 0])
        a.set("foot_front_%s" % s, "rotation", [osc(4, 0.8, f, 220), 0, 3 * sx])
        a.set("leg_back_%s" % s, "rotation", [osc(-8, 0.8, f, 40), 0, -2 * sx])
        a.set("leg_back_%s2" % s, "rotation", [osc(14, 1.2, f, 40), 0, 0])
        a.set("leg_back_%s3" % s, "rotation", [osc(-8, 0.8, f, 40), 0, 0])
        a.set("leg_back_%s" % s, "position", [0, 0.9, 0])
        a.set("ear_%s" % s, "rotation", [-8, 0, -6 * sx])
    tail_motion(a, f, {"tail": {"rotation": [10, 0, 0]}, "tail2": {"rotation": [8, 0, 0]}, "tail6": {"rotation": [10, 0, 0]},
                       "tail7": {"rotation": [15, 0, 0]}}, amp_y=10, amp_x=3, lag=30)
    fur_sway(a, f, 1.2)
    return a


def ground_walk():
    """Lateral-sequence walk, 1.2 s per stride."""
    L = 1.2
    f = 300.0
    a = Anim(L, loop=True)
    ph = {"back_left": 0, "front_left": 90, "back_right": 180, "front_right": 270}
    a.set("body", "position", [0, osc(0, 0.35, 2 * f, 60), 0])
    a.set("body", "rotation", [osc(0, 1.2, 2 * f, 120), osc(0, 2.0, f, 0), osc(0, 1.5, f, 90)])
    a.set("chest", "rotation", [osc(0, 1.5, 2 * f, 150), osc(0, -2.5, f, 20), 0])
    a.set("neck", "rotation", [osc(4, 2.0, 2 * f, 180), osc(0, -2, f, 40), 0])
    a.set("head", "rotation", [osc(-2, 2.5, 2 * f, 210), osc(0, -2, f, 60), osc(0, 1.5, f, 90)])
    for s, sx in SIDES:
        p = ph["front_%s" % s]
        a.set("leg_front_%s" % s, "rotation", [osc(0, 22, f, p), 0, 0])
        a.set("leg_front_%s2" % s, "rotation", [lift(f, p, 38), 0, 0])
        a.set("foot_front_%s" % s, "rotation", [lift(f, p + 25, -30, 0), 0, 0])
        p = ph["back_%s" % s]
        a.set("leg_back_%s" % s, "rotation", [osc(0, 20, f, p), 0, 0])
        a.set("leg_back_%s2" % s, "rotation", [lift(f, p, 28), 0, 0])
        a.set("leg_back_%s3" % s, "rotation", [lift(f, p - 20, -30), 0, 0])
        a.set("foot_back_%s" % s, "rotation", [lift(f, p + 20, 18), 0, 0])
        a.set("ear_%s" % s, "rotation", [osc(0, 3, 2 * f, 200), 0, 0])
    tail_motion(a, f, {"tail": {"rotation": [8, 0, 0]}, "tail2": {"rotation": [4, 0, 0]}}, amp_y=9, amp_x=3, lag=40)
    fur_sway(a, 2 * f, 1.6, phase=-90)
    return a


def ground_run():
    """Bounding run, 0.6 s per stride."""
    L = 0.6
    f = 600.0
    a = Anim(L, loop=True)
    a.set("body", "position", [0, osc(0.5, 1.2, f, 90), 0])
    a.set("body", "rotation", [osc(0, 6, f, 0), 0, 0])
    a.set("chest", "rotation", [osc(0, -3, f, 30), 0, 0])
    a.set("neck", "rotation", [osc(6, -5, f, 40), 0, 0])
    a.set("head", "rotation", [osc(-6, -4, f, 70), 0, 0])
    for s, sx in SIDES:
        off = 0 if s == "left" else 25
        p = 180 + off
        a.set("leg_front_%s" % s, "rotation", [osc(-5, 38, f, p), 0, 0])
        a.set("leg_front_%s2" % s, "rotation", [lift(f, p, 55), 0, 0])
        a.set("foot_front_%s" % s, "rotation", [lift(f, p + 30, -35), 0, 0])
        p = 0 + off
        a.set("leg_back_%s" % s, "rotation", [osc(0, 34, f, p), 0, 0])
        a.set("leg_back_%s2" % s, "rotation", [lift(f, p, 30), 0, 0])
        a.set("leg_back_%s3" % s, "rotation", [lift(f, p - 30, -35), 0, 0])
        a.set("foot_back_%s" % s, "rotation", [lift(f, p + 20, 25), 0, 0])
        a.set("ear_%s" % s, "rotation", [-18, 0, -8 * sx])
    tail_motion(a, f, {"tail": {"rotation": [22, 0, 0]}, "tail2": {"rotation": [6, 0, 0]}}, amp_y=5, amp_x=8, lag=45)
    for n in ("beard", "beard2", "beard3"):
        a.set(n, "rotation", [osc(-25 if n == "beard" else -8, 6, f, -60), 0, 0])
    for s, sx in SIDES:
        a.set("mustache_%s2" % s, "rotation", [osc(0, 4, f, -40), 0, osc(-12 * sx, 6 * sx, f, -60)])
        a.set("mustache_%s3" % s, "rotation", [osc(0, 4, f, -80), 0, osc(-14 * sx, 8 * sx, f, -100)])
        a.set("brow_%s3" % s, "rotation", [0, osc(8 * sx, 0, f), osc(-10 * sx, 6 * sx, f, -70)])
        a.set("cheek_%s2" % s, "rotation", [0, 12 * sx, osc(-8 * sx, 5 * sx, f, -50)])
    return a


def sleep(sl):
    L = 6.0
    f = 60.0
    a = Anim(L, loop=True)
    for bone, d in sl.items():
        for ch, v in d.items():
            a.set(bone, ch, v)
    bp = P(sl, "body", "position")
    a.set("body", "position", [bp[0], osc(bp[1], 0.15, f * 2), bp[2]])
    a.set("chest", "rotation", [osc(0, 1.5, f * 2, 40), 0, 0])
    nr = P(sl, "neck", "rotation")
    a.set("neck", "rotation", [osc(nr[0], 0.8, f * 2, 90), 0, 0])
    for s, sx in SIDES:
        a.set("ear_%s" % s, "rotation", [10, 0, osc(-10 * sx, 2 * sx, f, 30)])
        r = [0, 0, 0]
        a.set("mustache_%s2" % s, "rotation", [0, 0, osc(-8 * sx, 3 * sx, f * 2, 60)])
    br = P(sl, "beard", "rotation")
    a.set("beard", "rotation", [osc(br[0], 2, f * 2, 70), 0, 0])
    return a


def blink():
    a = Anim(0.25)
    for s, sx in SIDES:
        a.keys("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.08, [1, 3, 1]), (0.15, [1, 3, 1]), (0.25, [1, 1, 1])], smooth=False)
    return a


def cry():
    """additive: head lifts, jaw drops in a deep roar, whiskers flare."""
    a = Anim(1.6)
    a.keys("neck", "rotation", [(0, [0, 0, 0]), (0.25, [6, 0, 0]), (0.55, [-14, 0, 0]), (1.1, [-12, 0, 0]), (1.6, [0, 0, 0])])
    a.keys("head", "rotation", [(0, [0, 0, 0]), (0.25, [8, 0, 0]), (0.55, [-16, 0, 0]), (1.1, [-14, 0, 0]), (1.6, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0, [0, 0, 0]), (0.3, [0, 0, 0]), (0.55, [32, 0, 0]), (1.1, [30, 0, 0]), (1.4, [0, 0, 0]), (1.6, [0, 0, 0])])
    a.keys("chest", "rotation", [(0, [0, 0, 0]), (0.55, [-5, 0, 0]), (1.1, [-5, 0, 0]), (1.6, [0, 0, 0])])
    for s, sx in SIDES:
        a.keys("mustache_%s" % s, "rotation", [(0, [0, 0, 0]), (0.55, [0, 0, -12 * sx]), (0.7, [0, 0, -8 * sx]),
                                               (0.85, [0, 0, -13 * sx]), (1.1, [0, 0, -10 * sx]), (1.6, [0, 0, 0])])
        a.keys("mustache_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.6, [0, -6 * sx, -15 * sx]), (0.8, [0, -4 * sx, -9 * sx]),
                                                (1.0, [0, -6 * sx, -15 * sx]), (1.6, [0, 0, 0])])
        a.keys("brow_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.55, [0, 0, -14 * sx]), (1.1, [0, 0, -12 * sx]), (1.6, [0, 0, 0])])
        a.keys("brow_%s3" % s, "rotation", [(0, [0, 0, 0]), (0.6, [0, 0, -10 * sx]), (1.1, [0, 0, -8 * sx]), (1.6, [0, 0, 0])])
        a.keys("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.5, [-15, 0, -10 * sx]), (1.2, [-15, 0, -10 * sx]), (1.6, [0, 0, 0])])
        a.keys("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.4, [1, 0.1, 1]), (1.2, [1, 0.1, 1]), (1.5, [1, 1, 1])])
        a.keys("cheek_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.6, [0, -10 * sx, -10 * sx]), (1.1, [0, -8 * sx, -8 * sx]), (1.6, [0, 0, 0])])
    a.keys("beard", "rotation", [(0, [0, 0, 0]), (0.55, [-12, 0, 0]), (0.8, [-6, 0, 0]), (1.0, [-12, 0, 0]), (1.6, [0, 0, 0])])
    a.keys("beard2", "rotation", [(0, [0, 0, 0]), (0.6, [-8, 0, 0]), (0.9, [-3, 0, 0]), (1.6, [0, 0, 0])])
    return a


def recoil():
    a = Anim(0.75)
    a.keys("body", "position", [(0, [0, 0, 0]), (0.12, [0, 0.3, 2.0]), (0.35, [0, 0, 1.0]), (0.75, [0, 0, 0])])
    a.keys("neck", "rotation", [(0, [0, 0, 0]), (0.1, [-12, 6, 0]), (0.35, [-5, 3, 0]), (0.75, [0, 0, 0])])
    a.keys("head", "rotation", [(0, [0, 0, 0]), (0.1, [-14, 8, -6]), (0.35, [-6, 4, -2]), (0.75, [0, 0, 0])])
    for s, sx in SIDES:
        a.keys("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.08, [1, 3, 1]), (0.4, [1, 3, 1]), (0.6, [1, 1, 1])], smooth=False)
        a.keys("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.1, [20, 0, 12 * sx]), (0.5, [10, 0, 6 * sx]), (0.75, [0, 0, 0])])
        a.keys("mustache_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.12, [0, 10 * sx, -10 * sx]), (0.4, [0, 4 * sx, 6 * sx]), (0.75, [0, 0, 0])])
    a.keys("beard", "rotation", [(0, [0, 0, 0]), (0.12, [18, 0, 0]), (0.35, [-8, 0, 0]), (0.75, [0, 0, 0])])
    a.keys("tail7", "rotation", [(0, [0, 0, 0]), (0.15, [20, 0, 0]), (0.75, [0, 0, 0])])
    return a


def yawn():
    """idle quirk (additive): a slow old-man yawn."""
    a = Anim(2.6)
    a.keys("neck", "rotation", [(0, [0, 0, 0]), (0.6, [-10, 0, 0]), (1.6, [-14, 0, 0]), (2.1, [2, 0, 0]), (2.6, [0, 0, 0])])
    a.keys("head", "rotation", [(0, [0, 0, 0]), (0.6, [-12, 0, 4]), (1.6, [-16, 0, 6]), (2.1, [3, 0, -2]), (2.6, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0, [0, 0, 0]), (0.5, [6, 0, 0]), (0.9, [38, 0, 0]), (1.6, [40, 0, 0]), (2.0, [0, 0, 0]), (2.6, [0, 0, 0])])
    for s, sx in SIDES:
        a.keys("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.6, [1, 3, 1]), (1.9, [1, 3, 1]), (2.3, [1, 1, 1])])
        a.keys("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.8, [-12, 0, 10 * sx]), (1.8, [-12, 0, 10 * sx]), (2.6, [0, 0, 0])])
        a.keys("mustache_%s" % s, "rotation", [(0, [0, 0, 0]), (0.9, [0, 0, -8 * sx]), (1.7, [0, 0, -8 * sx]), (2.2, [0, 0, 0])])
    a.keys("beard", "rotation", [(0, [0, 0, 0]), (0.9, [-10, 0, 0]), (1.7, [-10, 0, 0]), (2.2, [3, 0, 0]), (2.6, [0, 0, 0])])
    return a


def doze():
    """idle quirk (additive): nods off, then jerks awake."""
    a = Anim(3.2)
    a.keys("neck", "rotation", [(0, [0, 0, 0]), (1.6, [5, 0, 0]), (2.2, [8, 0, 0]), (2.35, [-4, 0, 0]), (2.7, [1, 0, 0]), (3.2, [0, 0, 0])])
    a.keys("head", "rotation", [(0, [0, 0, 0]), (1.6, [6, 0, -3]), (2.2, [9, 0, -5]), (2.35, [-4, 0, 2]), (2.7, [1, 0, 0]), (3.2, [0, 0, 0])])
    a.keys("chest", "rotation", [(0, [0, 0, 0]), (2.2, [4, 0, 0]), (2.35, [-2, 0, 0]), (3.2, [0, 0, 0])])
    for s, sx in SIDES:
        a.keys("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.8, [1, 2, 1]), (1.4, [1, 3, 1]), (2.25, [1, 3, 1]), (2.35, [1, 0.2, 1]),
                                          (2.8, [1, 0.2, 1]), (3.1, [1, 1, 1])], smooth=False)
        a.keys("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (2.2, [12, 0, 12 * sx]), (2.35, [-14, 0, -8 * sx]), (3.2, [0, 0, 0])])
    a.keys("beard", "rotation", [(0, [0, 0, 0]), (2.2, [-6, 0, 0]), (2.4, [10, 0, 0]), (2.8, [-3, 0, 0]), (3.2, [0, 0, 0])])
    return a


def physical():
    """primary: crouch, then lunging swipe with the left forepaw and a snap of the jaws."""
    a = Anim(1.3)
    k = lambda bone, ch, fr: a.keys(bone, ch, fr)
    k("body", "position", [(0, [0, 0, 0]), (0.3, [0, -2.5, 2.5]), (0.55, [0, 0.5, -5]), (0.8, [0, -0.5, -4]), (1.3, [0, 0, 0])])
    k("body", "rotation", [(0, [0, 0, 0]), (0.3, [6, 0, 0]), (0.55, [-10, 0, 3]), (0.8, [2, 0, 2]), (1.3, [0, 0, 0])])
    k("neck", "rotation", [(0, [0, 0, 0]), (0.3, [14, 0, 0]), (0.55, [-6, 0, 0]), (0.8, [12, 0, 0]), (1.3, [0, 0, 0])])
    k("head", "rotation", [(0, [0, 0, 0]), (0.3, [-6, 0, 0]), (0.55, [-10, 0, 0]), (0.8, [6, 0, 0]), (1.3, [0, 0, 0])])
    k("jaw", "rotation", [(0, [0, 0, 0]), (0.45, [30, 0, 0]), (0.62, [4, 0, 0]), (1.3, [0, 0, 0])])
    k("leg_front_left", "rotation", [(0, [0, 0, 0]), (0.3, [10, 0, 0]), (0.5, [-75, 0, -10]), (0.68, [-20, 0, -4]), (1.3, [0, 0, 0])])
    k("leg_front_left2", "rotation", [(0, [0, 0, 0]), (0.3, [20, 0, 0]), (0.5, [-10, 0, 0]), (0.68, [30, 0, 0]), (1.3, [0, 0, 0])])
    k("foot_front_left", "rotation", [(0, [0, 0, 0]), (0.5, [40, 0, 0]), (0.68, [-10, 0, 0]), (1.3, [0, 0, 0])])
    k("leg_front_right", "rotation", [(0, [0, 0, 0]), (0.3, [12, 0, 0]), (0.55, [8, 0, 0]), (1.3, [0, 0, 0])])
    for s, sx in SIDES:
        k("leg_back_%s" % s, "rotation", [(0, [0, 0, 0]), (0.3, [-18, 0, 0]), (0.55, [20, 0, 0]), (0.8, [5, 0, 0]), (1.3, [0, 0, 0])])
        k("leg_back_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.3, [25, 0, 0]), (0.55, [-10, 0, 0]), (1.3, [0, 0, 0])])
        k("leg_back_%s3" % s, "rotation", [(0, [0, 0, 0]), (0.3, [-12, 0, 0]), (0.55, [-5, 0, 0]), (1.3, [0, 0, 0])])
        k("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.3, [25, 0, 10 * sx]), (0.9, [25, 0, 10 * sx]), (1.3, [0, 0, 0])])
        k("mustache_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.55, [0, 12 * sx, -8 * sx]), (0.8, [0, 4 * sx, 6 * sx]), (1.3, [0, 0, 0])])
        k("brow_%s3" % s, "rotation", [(0, [0, 0, 0]), (0.55, [0, 10 * sx, -6 * sx]), (1.3, [0, 0, 0])])
    k("beard", "rotation", [(0, [0, 0, 0]), (0.3, [-8, 0, 0]), (0.55, [30, 0, 0]), (0.8, [-10, 0, 0]), (1.3, [0, 0, 0])])
    k("beard2", "rotation", [(0, [0, 0, 0]), (0.6, [15, 0, 0]), (0.9, [-6, 0, 0]), (1.3, [0, 0, 0])])
    k("tail", "rotation", [(0, [0, 0, 0]), (0.3, [25, 0, 0]), (0.6, [10, -15, 0]), (1.3, [0, 0, 0])])
    k("tail3", "rotation", [(0, [0, 0, 0]), (0.4, [15, 10, 0]), (0.8, [5, -10, 0]), (1.3, [0, 0, 0])])
    k("tail6", "rotation", [(0, [0, 0, 0]), (0.5, [20, 15, 0]), (0.9, [5, -15, 0]), (1.3, [0, 0, 0])])
    return a


def special():
    """primary: the sage draws breath, rears up and bellows - whiskers and brows flare."""
    a = Anim(1.6)
    k = lambda bone, ch, fr: a.keys(bone, ch, fr)
    k("body", "position", [(0, [0, 0, 0]), (0.45, [0, 1.5, 1.0]), (0.75, [0, 2.0, 0.5]), (1.2, [0, 1.5, 0.5]), (1.6, [0, 0, 0])])
    k("body", "rotation", [(0, [0, 0, 0]), (0.45, [-12, 0, 0]), (0.75, [-6, 0, 0]), (1.2, [-6, 0, 0]), (1.6, [0, 0, 0])])
    k("neck", "rotation", [(0, [0, 0, 0]), (0.45, [8, 0, 0]), (0.75, [-4, 0, 0]), (1.2, [-2, 0, 0]), (1.6, [0, 0, 0])])
    k("head", "rotation", [(0, [0, 0, 0]), (0.45, [10, 0, 0]), (0.75, [-6, 0, 0]), (1.2, [-4, 0, 0]), (1.6, [0, 0, 0])])
    k("jaw", "rotation", [(0, [0, 0, 0]), (0.5, [0, 0, 0]), (0.75, [34, 0, 0]), (1.2, [32, 0, 0]), (1.45, [0, 0, 0]), (1.6, [0, 0, 0])])
    for s, sx in SIDES:
        k("leg_front_%s" % s, "rotation", [(0, [0, 0, 0]), (0.45, [14, 0, 0]), (0.75, [6, 0, 0]), (1.2, [6, 0, 0]), (1.6, [0, 0, 0])])
        k("leg_front_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.45, [-4, 0, 0]), (1.6, [0, 0, 0])])
        k("leg_back_%s" % s, "rotation", [(0, [0, 0, 0]), (0.45, [-10, 0, 0]), (1.2, [-6, 0, 0]), (1.6, [0, 0, 0])])
        k("leg_back_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.45, [10, 0, 0]), (1.2, [6, 0, 0]), (1.6, [0, 0, 0])])
        k("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.3, [1, 3, 1]), (0.6, [1, 3, 1]), (0.7, [1, 0.05, 1]), (1.3, [1, 0.05, 1]), (1.5, [1, 1, 1])])
        k("brow_%s" % s, "rotation", [(0, [0, 0, 0]), (0.75, [0, 0, -8 * sx]), (1.2, [0, 0, -8 * sx]), (1.6, [0, 0, 0])])
        k("brow_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.75, [0, 0, -22 * sx]), (1.2, [0, 0, -20 * sx]), (1.6, [0, 0, 0])])
        k("brow_%s3" % s, "rotation", [(0, [0, 0, 0]), (0.75, [0, 0, -16 * sx]), (0.95, [0, 0, -10 * sx]), (1.2, [0, 0, -16 * sx]), (1.6, [0, 0, 0])])
        k("mustache_%s" % s, "rotation", [(0, [0, 0, 0]), (0.75, [0, 0, -10 * sx]), (1.2, [0, 0, -10 * sx]), (1.6, [0, 0, 0])])
        k("mustache_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.75, [0, -10 * sx, -22 * sx]), (0.95, [0, -6 * sx, -14 * sx]),
                                           (1.2, [0, -10 * sx, -22 * sx]), (1.6, [0, 0, 0])])
        k("mustache_%s3" % s, "rotation", [(0, [0, 0, 0]), (0.8, [0, -6 * sx, -20 * sx]), (1.0, [0, -4 * sx, -10 * sx]),
                                           (1.25, [0, -6 * sx, -20 * sx]), (1.6, [0, 0, 0])])
        k("cheek_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.75, [0, -14 * sx, -12 * sx]), (1.2, [0, -12 * sx, -10 * sx]), (1.6, [0, 0, 0])])
        k("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.75, [-15, 0, -14 * sx]), (1.2, [-15, 0, -14 * sx]), (1.6, [0, 0, 0])])
    k("beard", "rotation", [(0, [0, 0, 0]), (0.75, [-22, 0, 0]), (0.95, [-12, 0, 0]), (1.2, [-20, 0, 0]), (1.6, [0, 0, 0])])
    k("beard2", "rotation", [(0, [0, 0, 0]), (0.8, [-14, 0, 0]), (1.0, [-6, 0, 0]), (1.25, [-14, 0, 0]), (1.6, [0, 0, 0])])
    k("beard3", "rotation", [(0, [0, 0, 0]), (0.85, [-10, 0, 0]), (1.05, [-4, 0, 0]), (1.3, [-10, 0, 0]), (1.6, [0, 0, 0])])
    k("tail", "rotation", [(0, [0, 0, 0]), (0.75, [30, 0, 0]), (1.2, [28, 0, 0]), (1.6, [0, 0, 0])])
    k("tail4", "rotation", [(0, [0, 0, 0]), (0.8, [15, 0, 0]), (1.2, [12, 0, 0]), (1.6, [0, 0, 0])])
    k("tail7", "rotation", [(0, [0, 0, 0]), (0.85, [25, 0, 0]), (1.2, [20, 0, 0]), (1.6, [0, 0, 0])])
    return a


def status():
    """primary: a slow, knowing double nod with closed eyes."""
    a = Anim(1.4)
    k = lambda bone, ch, fr: a.keys(bone, ch, fr)
    k("neck", "rotation", [(0, [0, 0, 0]), (0.3, [10, 0, 0]), (0.55, [0, 0, 0]), (0.8, [12, 0, 0]), (1.05, [0, 0, 0]), (1.4, [0, 0, 0])])
    k("head", "rotation", [(0, [0, 0, 0]), (0.3, [12, 0, 0]), (0.55, [0, 0, 0]), (0.8, [14, 0, 0]), (1.05, [0, 0, 0]), (1.4, [0, 0, 0])])
    k("body", "position", [(0, [0, 0, 0]), (0.3, [0, -0.6, 0]), (0.55, [0, 0, 0]), (0.8, [0, -0.6, 0]), (1.05, [0, 0, 0])])
    for s, sx in SIDES:
        k("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.2, [1, 3, 1]), (1.1, [1, 3, 1]), (1.3, [1, 1, 1])])
        k("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.3, [10, 0, 6 * sx]), (0.55, [-5, 0, -4 * sx]), (0.8, [10, 0, 6 * sx]), (1.4, [0, 0, 0])])
        k("mustache_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.35, [0, 0, 6 * sx]), (0.6, [0, 0, -4 * sx]), (0.85, [0, 0, 6 * sx]), (1.4, [0, 0, 0])])
    k("beard", "rotation", [(0, [0, 0, 0]), (0.35, [-10, 0, 0]), (0.6, [6, 0, 0]), (0.85, [-10, 0, 0]), (1.1, [4, 0, 0]), (1.4, [0, 0, 0])])
    k("beard2", "rotation", [(0, [0, 0, 0]), (0.4, [-8, 0, 0]), (0.65, [5, 0, 0]), (0.9, [-8, 0, 0]), (1.4, [0, 0, 0])])
    k("tail", "rotation", [(0, [0, 0, 0]), (0.5, [12, 12, 0]), (1.0, [12, -12, 0]), (1.4, [0, 0, 0])])
    k("tail4", "rotation", [(0, [0, 0, 0]), (0.6, [6, 15, 0]), (1.1, [6, -15, 0]), (1.4, [0, 0, 0])])
    return a


def faint():
    """primary (curve one): staggers, front legs buckle, rolls onto its side, eyes shut."""
    a = Anim(2.0, hold=True)
    k = lambda bone, ch, fr: a.keys(bone, ch, fr)
    k("body", "position", [(0, [0, 0, 0]), (0.4, [0, -1.5, 0]), (0.9, [0, -4.5, 0]), (1.3, [0.5, -6.6, 0]), (1.5, [0.5, -6.3, 0]),
                           (2.0, [0.5, -6.5, 0])])
    k("body", "rotation", [(0, [0, 0, 0]), (0.4, [6, 0, -4]), (0.9, [10, 0, 30]), (1.3, [2, 0, 86]), (1.5, [2, 0, 80]), (2.0, [2, 0, 82])])
    k("chest", "rotation", [(0, [0, 0, 0]), (0.9, [6, 0, 0]), (2.0, [4, 0, 0])])
    k("neck", "rotation", [(0, [0, 0, 0]), (0.4, [15, 0, 0]), (0.9, [10, 0, -10]), (1.3, [0, 0, -20]), (2.0, [-4, 0, -18])])
    k("head", "rotation", [(0, [0, 0, 0]), (0.4, [12, 0, 0]), (1.3, [0, 10, -10]), (2.0, [-6, 10, -8])])
    k("jaw", "rotation", [(0, [0, 0, 0]), (1.1, [0, 0, 0]), (1.5, [10, 0, 0]), (2.0, [8, 0, 0])])
    for s, sx in SIDES:
        k("eyelid_%s" % s, "scale", [(0, [1, 1, 1]), (0.3, [1, 2, 1]), (0.9, [1, 3, 1]), (2.0, [1, 3, 1])])
        k("leg_front_%s" % s, "rotation", [(0, [0, 0, 0]), (0.4, [-15, 0, 0]), (0.9, [-35, 0, 0]), (1.3, [-25, 0, -10 * sx]),
                                           (2.0, [-20, 0, -12 * sx])])
        k("leg_front_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.4, [30, 0, 0]), (0.9, [40, 0, 0]), (1.3, [25, 0, 0]), (2.0, [20, 0, 0])])
        k("leg_back_%s" % s, "rotation", [(0, [0, 0, 0]), (0.6, [-10, 0, 0]), (1.3, [-25, 0, -6 * sx]), (2.0, [-20, 0, -8 * sx])])
        k("leg_back_%s2" % s, "rotation", [(0, [0, 0, 0]), (0.6, [15, 0, 0]), (1.3, [20, 0, 0]), (2.0, [15, 0, 0])])
        k("ear_%s" % s, "rotation", [(0, [0, 0, 0]), (0.9, [25, 0, 18 * sx]), (2.0, [25, 0, 20 * sx])])
        k("mustache_%s2" % s, "rotation", [(0, [0, 0, 0]), (1.3, [0, 0, 10 * sx]), (1.5, [0, 0, 4 * sx]), (2.0, [0, 0, 8 * sx])])
    k("beard", "rotation", [(0, [0, 0, 0]), (0.9, [-10, 0, -10]), (1.3, [-5, 0, -40]), (1.5, [-5, 0, -30]), (2.0, [-5, 0, -36])])
    k("tail", "rotation", [(0, [0, 0, 0]), (0.9, [-30, 0, 0]), (2.0, [-25, 10, 0])])
    k("tail3", "rotation", [(0, [0, 0, 0]), (1.3, [10, 15, 0]), (2.0, [8, 12, 0])])
    k("tail6", "rotation", [(0, [0, 0, 0]), (1.5, [10, 12, 0]), (2.0, [6, 10, 0])])
    return a


def build_all(sit_ov, sleep_ov):
    sit = pose_values(sit_ov)
    sl = pose_values(sleep_ov)
    anims = {
        "ground_idle": ground_idle(sit),
        "battle_idle": battle_idle(),
        "ground_walk": ground_walk(),
        "ground_run": ground_run(),
        "sleep": sleep(sl),
        "blink": blink(),
        "cry": cry(),
        "recoil": recoil(),
        "yawn": yawn(),
        "doze": doze(),
        "physical": physical(),
        "special": special(),
        "status": status(),
        "faint": faint(),
    }
    return {"format_version": "1.8.0",
            "animations": {"animation.%s.%s" % (NAME, k): v.to_json() for k, v in anims.items()}}


def check_loops(doc):
    import re
    bad = []
    for name, an in doc["animations"].items():
        if an.get("loop") is not True:
            continue
        L = an["animation_length"]
        txt = json.dumps(an["bones"])
        for f in re.findall(r"anim_time\*([0-9.]+)", txt):
            k = float(f) * L / 360.0
            if abs(k - round(k)) > 1e-6:
                bad.append((name, f, L))
    return bad
