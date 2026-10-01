"""Swalot animations, poser and resolver.

Motion notes: Swalot is a heavy, jelly-like stomach. Every motion travels up
its body (base -> middle -> head) like a wobbling pudding, its long whiskers
trail behind, it opens its puckered lips into a huge gulping mouth (Swallow /
Stockpile / Spit Up), spits sludge, and body-slams by hopping and splatting.
"""
from collections import OrderedDict

from cobblegen.anim import Anim, wave, swave, awave

P = "swalot"
WL = ["whisker_left", "whisker_left2", "whisker_left3", "whisker_left4"]
WR = ["whisker_right", "whisker_right2", "whisker_right3", "whisker_right4"]
EYES = ("eye_left", "eye_right")
LIDS = ("eyelid_left", "eyelid_right")


def _jelly(a, speed, amp_x, amp_z, lag=35, base_x=0.0):
    """Wobble that travels lower -> upper -> head."""
    for i, b in enumerate(("lower", "upper", "head")):
        k = [0.5, 0.8, 1.0][i]
        a.expr(b, "rotation", [wave(amp_x * k, speed, -lag * i, base_x * k), 0, wave(amp_z * k, speed / 2, -lag * i)])


def _whiskers_follow(a, speed, amp_x, amp_z, lag=30, start=-60, z_speed=None):
    zs = z_speed if z_speed is not None else speed / 2
    for chain, sg in ((WL, 1), (WR, -1)):
        ax, az = amp_x, amp_z
        for i, b in enumerate(chain):
            ph = start - lag * i
            a.expr(b, "rotation", [wave(ax, speed, ph), 0, wave(az * sg, zs, ph)])
            ax *= 1.15
            az *= 1.15


def _whisker_keys(a, frames, lag=0.05, out_scale=0.6):
    """frames: (t, swing_x, flare) totals spread along both whisker chains."""
    w = [0.35, 0.25, 0.22, 0.18]
    end = frames[-1][0]
    for chain, sg in ((WL, 1), (WR, -1)):
        for i, b in enumerate(chain):
            seen = OrderedDict()
            for t, sx, fl in frames:
                tt = min(round(t + (lag * i if 0 < t < end else 0), 3), end)
                seen[tt] = [sx * w[i], 0, -fl * w[i] * sg * out_scale]
            a.keys(b, "rotation", list(seen.items()))


def _mouth_open(a, frames):
    a.keys("lip_top", "position", [(t, [0, 2.2 * k, -0.4 * k]) for t, k in frames])
    a.keys("lip_bottom", "position", [(t, [0, -2.0 * k, -0.3 * k]) for t, k in frames])
    a.keys("lip_top", "scale", [(t, [1 + 0.15 * k, 1, 1 + 0.1 * k]) for t, k in frames])
    a.keys("lip_bottom", "scale", [(t, [1 + 0.2 * k, 1, 1 + 0.1 * k]) for t, k in frames])
    a.keys("lip_corner_left", "position", [(t, [1.0 * k, 0, 0]) for t, k in frames])
    a.keys("lip_corner_right", "position", [(t, [-1.0 * k, 0, 0]) for t, k in frames])
    a.keys("mouth_inner", "scale", [(t, [1 + 0.5 * max(k, 0), 1 + 1.6 * max(k, 0), 1]) for t, k in frames])


def _lids(a, frames):
    """frames: (t, closed 0..1)."""
    for b in LIDS:
        a.keys(b, "position", [(t, [0, 0, -0.32 * k]) for t, k in frames], smooth=False)


def ground_idle():
    a = Anim("ground_idle", loop=True)
    s = 90  # 4 s breath
    a.expr("body", "scale", [swave(0.018, s), swave(-0.026, s), swave(0.018, s)])
    _jelly(a, s, 0.8, 1.0)
    a.expr("head", "position", [0, wave(0.15, s, -50), 0])
    a.expr("arm_left", "rotation", [wave(3, s, -30), wave(4, s, -20), wave(5, s, -40, 4)])
    a.expr("arm_right", "rotation", [wave(3, s, -30), wave(-4, s, -20), wave(-5, s, -40, -4)])
    a.expr("lip_top", "scale", [swave(0.03, s * 2), 1, swave(0.04, s * 2)])
    a.expr("lip_bottom", "scale", [swave(0.03, s * 2, -60), 1, swave(0.04, s * 2, -60)])
    a.expr("skirt", "scale", [swave(0.01, s, 60), 1, swave(0.01, s, 60)])
    _whiskers_follow(a, s, 2.5, 2.0, lag=30)
    return a


def battle_idle():
    a = Anim("battle_idle", loop=True)
    s = 200
    a.expr("body", "position", [0, awave(0.4, s / 2), 0])
    a.expr("body", "scale", [swave(0.03, s, 90), swave(-0.045, s, 90), swave(0.03, s, 90)])
    _jelly(a, s, 1.6, 1.4, lag=40, base_x=-1)
    a.expr("arm_left", "rotation", [wave(6, s, -40, -8), wave(6, s, -20, 10), wave(6, s, -30, -16)])
    a.expr("arm_right", "rotation", [wave(6, s, -40, -8), wave(-6, s, -20, -10), wave(-6, s, -30, 16)])
    a.expr("lip_top", "scale", [swave(0.05, s), 1, swave(0.06, s)])
    a.expr("lip_bottom", "scale", [swave(0.05, s, -60), 1, swave(0.06, s, -60)])
    _whiskers_follow(a, s, 4.0, 3.0, lag=35)
    return a


def ground_walk():
    a = Anim("ground_walk", loop=True)
    s = 300  # one heavy hop every 1.2 s
    a.expr("body", "position", [0, awave(1.2, s / 2), 0])
    a.expr("body", "scale", [wave(0.05, s, 0, 1, "cos"), wave(-0.07, s, 0, 1, "cos"), wave(0.04, s, 0, 1, "cos")])
    a.expr("body", "rotation", [wave(2, s, 0, 2), 0, wave(2, s / 2)])
    _jelly(a, s, 2.4, 2.0, lag=45)
    a.expr("arm_left", "rotation", [wave(14, s / 2), wave(8, s / 2, 90, 4), wave(10, s, -30, 0)])
    a.expr("arm_right", "rotation", [wave(-14, s / 2), wave(8, s / 2, 90, -4), wave(-10, s, -30, 0)])
    a.expr("skirt", "scale", [wave(0.03, s, 0, 1, "cos"), 1, wave(0.03, s, 0, 1, "cos")])
    _whiskers_follow(a, s, 6.0, 4.0, lag=35, start=-90)
    return a


def sleep():
    a = Anim("sleep", loop=True)
    s = 60
    a.expr("body", "scale", [wave(0.012, s, 0, 1.06), wave(-0.02, s, 0, 0.88), wave(0.012, s, 0, 1.06)])
    a.expr("head", "rotation", [wave(1.0, s, -60, 6), 0, 0])
    a.expr("upper", "rotation", [wave(0.6, s, -30, 3), 0, 0])
    a.expr("arm_left", "rotation", [0, 8, 14])
    a.expr("arm_right", "rotation", [0, -8, -14])
    a.expr("lip_bottom", "position", [0, wave(0.15, s, -90, -0.4), 0])
    a.expr("mouth_inner", "scale", [1, wave(0.2, s, -90, 1.3), 1])
    for b in LIDS:
        a.expr(b, "position", [0, 0, -0.32])
    for chain, sg in ((WL, 1), (WR, -1)):
        for i, b in enumerate(chain):
            a.expr(b, "rotation", [wave(1.2, s, -40 * i, 4), 0, (8 if i < 2 else 6) * sg])
    return a


def blink():
    a = Anim("blink", length=0.25)
    _lids(a, [(0.0, 0), (0.05, 1), (0.17, 1), (0.25, 0)])
    return a


def cry():
    a = Anim("cry", length=1.8)
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.2, [1.06, 0.92, 1.06]), (0.45, [0.95, 1.1, 0.95]),
                            (1.1, [0.96, 1.08, 0.96]), (1.4, [1.03, 0.96, 1.03]), (1.8, [1, 1, 1])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.2, [5, 0, 0]), (0.45, [-12, 0, 0]), (0.8, [-10, 0, 4]),
                               (1.1, [-10, 0, -4]), (1.4, [2, 0, 0]), (1.8, [0, 0, 0])])
    a.keys("upper", "rotation", [(0.0, [0, 0, 0]), (0.2, [3, 0, 0]), (0.45, [-5, 0, 0]), (1.1, [-4, 0, 0]), (1.4, [1, 0, 0]), (1.8, [0, 0, 0])])
    _mouth_open(a, [(0.0, 0), (0.2, -0.1), (0.45, 1.0), (1.1, 0.9), (1.35, 0), (1.8, 0)])
    _lids(a, [(0.0, 0), (0.4, 0), (0.42, 1), (1.15, 1), (1.2, 0), (1.8, 0)])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.45, [-10, 12, -28]), (0.8, [-10, 12, -20]), (1.1, [-10, 12, -28]), (1.4, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.45, [-10, -12, 28]), (0.8, [-10, -12, 20]), (1.1, [-10, -12, 28]), (1.4, [0, 0, 0])])
    _whisker_keys(a, [(0.0, 0, 0), (0.2, 8, -10), (0.45, -30, 50), (0.7, -10, 30), (0.95, -26, 45), (1.25, 10, -8),
                      (1.55, -4, 4), (1.8, 0, 0)])
    return a


def physical():
    a = Anim("physical", length=1.3)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 0, 1.0]), (0.5, [0, 5.0, -2.0]), (0.68, [0, 0, -4.5]),
                               (0.9, [0, 0, -3.5]), (1.3, [0, 0, 0])])
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.25, [1.1, 0.85, 1.1]), (0.5, [0.93, 1.12, 0.93]),
                            (0.68, [1.2, 0.76, 1.2]), (0.85, [0.96, 1.05, 0.96]), (1.05, [1.02, 0.98, 1.02]), (1.3, [1, 1, 1])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.25, [-6, 0, 0]), (0.5, [6, 0, 0]), (0.68, [4, 0, 0]), (1.0, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.5, [-8, 0, 0]), (0.72, [10, 0, 0]), (0.9, [-4, 0, 0]), (1.1, [2, 0, 0]), (1.3, [0, 0, 0])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, 10]), (0.5, [0, 0, -40]), (0.68, [0, 25, 15]), (1.0, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, -10]), (0.5, [0, 0, 40]), (0.68, [0, -25, -15]), (1.0, [0, 0, 0])])
    _lids(a, [(0.0, 0), (0.62, 0), (0.64, 1), (0.85, 1), (0.88, 0), (1.3, 0)])
    _whisker_keys(a, [(0.0, 0, 0), (0.25, -10, 0), (0.5, 25, -20), (0.7, -35, 40), (0.9, 15, -10), (1.1, -6, 4), (1.3, 0, 0)])
    return a


def special(name="special"):
    a = Anim(name, length=1.5)
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.5, [1.08, 1.1, 1.08]), (0.65, [0.92, 0.94, 0.9]),
                            (0.85, [1.03, 0.98, 1.03]), (1.1, [0.99, 1.01, 0.99]), (1.5, [1, 1, 1])])
    a.keys("upper", "rotation", [(0.0, [0, 0, 0]), (0.5, [-5, 0, 0]), (0.65, [6, 0, 0]), (0.9, [-1, 0, 0]), (1.5, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.5, [-8, 0, 0]), (0.65, [12, 0, 0]), (0.95, [-2, 0, 0]), (1.5, [0, 0, 0])])
    a.keys("mouth", "position", [(0.0, [0, 0, 0]), (0.5, [0, 0, 0.4]), (0.65, [0, 0, -1.8]), (0.95, [0, 0, -0.5]), (1.5, [0, 0, 0])])
    _mouth_open(a, [(0.0, 0), (0.5, -0.15), (0.63, 0.7), (0.9, 0.55), (1.15, 0), (1.5, 0)])
    _lids(a, [(0.0, 0), (0.58, 0), (0.6, 1), (0.95, 1), (1.0, 0), (1.5, 0)])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.5, [0, -10, -20]), (0.65, [0, 20, 10]), (1.1, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.5, [0, 10, 20]), (0.65, [0, -20, -10]), (1.1, [0, 0, 0])])
    _whisker_keys(a, [(0.0, 0, 0), (0.5, 12, -8), (0.68, -28, 30), (0.9, 12, -6), (1.15, -5, 3), (1.5, 0, 0)])
    return a


def status():
    a = Anim("status", length=1.8)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 10, 5]), (0.55, [0, -10, -5]), (0.85, [0, 8, 4]),
                               (1.15, [0, -6, -3]), (1.45, [0, 2, 1]), (1.8, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 0.9, 0]), (0.4, [0, 0.2, 0]), (0.55, [0, 0.9, 0]),
                               (0.7, [0, 0.2, 0]), (0.85, [0, 0.7, 0]), (1.15, [0, 0.5, 0]), (1.8, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.3, [0, 0, -6]), (0.6, [0, 0, 6]), (0.9, [0, 0, -5]),
                               (1.2, [0, 0, 4]), (1.5, [0, 0, -1]), (1.8, [0, 0, 0])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, -30]), (0.55, [0, 0, 5]), (0.85, [0, 0, -30]),
                                   (1.15, [0, 0, 5]), (1.5, [0, 0, -8]), (1.8, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, -5]), (0.55, [0, 0, 30]), (0.85, [0, 0, -5]),
                                    (1.15, [0, 0, 30]), (1.5, [0, 0, 8]), (1.8, [0, 0, 0])])
    _lids(a, [(0.0, 0), (0.15, 1), (1.5, 1), (1.6, 0), (1.8, 0)])
    _whisker_keys(a, [(0.0, 0, 0), (0.3, -12, 25), (0.6, 12, -10), (0.9, -12, 25), (1.2, 10, -8), (1.5, -3, 4), (1.8, 0, 0)])
    return a


def recoil():
    a = Anim("recoil", length=0.8)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.1, [0, 1.6, 2.0]), (0.35, [0, 0.6, 1.0]), (0.55, [0, 0.2, 0.3]), (0.8, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.1, [-8, 0, 0]), (0.3, [4, 0, 0]), (0.5, [-1.5, 0, 0]), (0.8, [0, 0, 0])])
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.1, [1.08, 0.86, 1.08]), (0.28, [0.95, 1.06, 0.95]),
                            (0.48, [1.02, 0.98, 1.02]), (0.8, [1, 1, 1])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.15, [-10, 0, 0]), (0.35, [6, 0, 0]), (0.55, [-2, 0, 0]), (0.8, [0, 0, 0])])
    _lids(a, [(0.0, 0), (0.05, 1), (0.5, 1), (0.55, 0), (0.8, 0)])
    _mouth_open(a, [(0.0, 0), (0.1, 0.3), (0.4, 0.15), (0.6, 0), (0.8, 0)])
    _whisker_keys(a, [(0.0, 0, 0), (0.12, 30, -15), (0.35, -15, 10), (0.55, 6, -3), (0.8, 0, 0)], lag=0.03)
    return a


def faint():
    a = Anim("faint", length=2.8)
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.25, [0.95, 1.08, 0.95]), (0.7, [1.12, 0.75, 1.12]),
                            (1.1, [1.22, 0.58, 1.2]), (1.6, [1.26, 0.54, 1.24]), (2.8, [1.28, 0.52, 1.26])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 0.8, 0]), (0.7, [0, 0, 0]), (2.8, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.25, [-6, 0, 0]), (0.7, [10, 0, 4]), (1.1, [16, 0, 2]), (2.8, [16, 0, 2])])
    a.keys("upper", "rotation", [(0.0, [0, 0, 0]), (0.7, [5, 0, -2]), (2.8, [6, 0, -2])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, -15]), (0.7, [0, 10, 25]), (2.8, [0, 12, 30])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, 15]), (0.7, [0, -10, -25]), (2.8, [0, -12, -30])])
    a.keys("lip_bottom", "position", [(0.0, [0, 0, 0]), (0.7, [0, -0.8, 0]), (2.8, [0, -1.0, 0])])
    a.keys("mouth_inner", "scale", [(0.0, [1, 1, 1]), (0.7, [1.2, 1.6, 1]), (2.8, [1.2, 1.7, 1])])
    _lids(a, [(0.0, 0), (0.3, 0), (0.35, 1), (2.8, 1)])
    for chain, sg in ((WL, 1), (WR, -1)):
        for i, b in enumerate(chain):
            a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.25 + 0.04 * i, [-8, 0, -6 * sg]), (0.7 + 0.04 * i, [10, 0, 10 * sg]),
                                   (1.1 + 0.04 * i, [6, 0, 12 * sg]), (2.8, [6, 0, 12 * sg])])
    return a


def gulp():
    a = Anim("gulp", length=1.6)
    _mouth_open(a, [(0.0, 0), (0.2, 0.6), (0.35, 0.6), (0.5, 0), (1.6, 0)])
    a.keys("head", "scale", [(0.0, [1, 1, 1]), (0.5, [1.0, 1.0, 1.0]), (0.62, [1.05, 1.04, 1.05]), (0.8, [1, 1, 1])])
    a.keys("upper", "scale", [(0.0, [1, 1, 1]), (0.7, [1, 1, 1]), (0.85, [1.06, 1.0, 1.06]), (1.05, [1, 1, 1])])
    a.keys("lower", "scale", [(0.0, [1, 1, 1]), (0.95, [1, 1, 1]), (1.1, [1.06, 0.98, 1.06]), (1.35, [1, 1, 1])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (1.1, [0, 0, 0]), (1.22, [0, 0.4, 0]), (1.35, [0, 0, 0])])
    _lids(a, [(0.0, 0), (0.45, 0), (0.48, 1), (0.95, 1), (1.0, 0), (1.6, 0)])
    _whisker_keys(a, [(0.0, 0, 0), (0.2, -8, 8), (0.5, 4, -3), (1.2, 6, -4), (1.4, -3, 2), (1.6, 0, 0)])
    return a


def all_animations():
    return [ground_idle(), battle_idle(), ground_walk(), sleep(), blink(), cry(), physical(), special(),
            special("spray"), status(), recoil(), faint(), gulp()]


PREVIEW_ORDER = ["ground_idle", "ground_walk", "battle_idle", "sleep", "cry", "physical", "special",
                 "status", "recoil", "faint", "blink", "gulp"]
OVER_IDLE = ("cry", "blink", "gulp")


def poser(female=False):
    look = "q.look('head', 0.4, 0.5, 8, -8, 20, -20)"
    quirks = ["q.bedrock_quirk('swalot', 'blink')", "q.bedrock_quirk('swalot', 'gulp', 12, 30, 1)"]
    fix = [{"part": "whisker_left", "scale": [1, 0.7, 1]}, {"part": "whisker_right", "scale": [1, 0.7, 1]}] if female else []

    def pose(types, anims, battle=None, q=True, named=None):
        d = OrderedDict()
        d["poseTypes"] = types
        if battle is not None:
            d["isBattle"] = battle
        d["animations"] = anims
        if q:
            d["quirks"] = list(quirks if q is True else q)
        if named:
            d["namedAnimations"] = named
        if fix:
            d["transformedParts"] = list(fix)
        return d

    out = OrderedDict()
    out["portraitScale"] = 1.3
    out["portraitTranslation"] = [-0.3, 0.45, 0]
    out["profileScale"] = 0.58
    out["profileTranslation"] = [0, 0.78, 0]
    out["rootBone"] = P
    out["animations"] = OrderedDict([
        ("cry", "q.bedrock_stateful('swalot', 'cry')"),
        ("recoil", "q.bedrock_stateful('swalot', 'recoil')"),
        ("faint", "q.bedrock_primary('swalot', 'faint', q.curve('one'))"),
        ("physical", "q.bedrock_primary('swalot', 'physical', q.curve('symmetrical_wide'))"),
        ("special", "q.bedrock_primary('swalot', 'special', q.curve('symmetrical_wide'))"),
        ("spray", "q.bedrock_primary('swalot', 'spray', q.curve('symmetrical_wide'))"),
        ("status", "q.bedrock_primary('swalot', 'status', q.curve('symmetrical_wide'))"),
    ])
    poses = OrderedDict()
    poses["battle-standing"] = pose(["STAND"], [look, "q.bedrock('swalot', 'battle_idle')"], battle=True,
                                    q=["q.bedrock_quirk('swalot', 'blink')"])
    poses["standing"] = pose(["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"],
                             [look, "q.bedrock('swalot', 'ground_idle')"], battle=False)
    poses["walking"] = pose(["WALK", "SWIM"], ["q.bedrock('swalot', 'ground_walk')"],
                            q=["q.bedrock_quirk('swalot', 'blink')"])
    poses["sleep"] = pose(["SLEEP"], ["q.bedrock('swalot', 'sleep')"], q=False,
                          named={"cry": "q.bedrock_stateful('dummy', 'cry')"})
    out["poses"] = poses
    return out


def resolver():
    tex = "cobblemon:textures/pokemon/0317_swalot/"
    return OrderedDict([
        ("species", "cobblemon:swalot"),
        ("order", 0),
        ("variations", [
            OrderedDict([("aspects", []), ("poser", "cobblemon:swalot"), ("model", "cobblemon:swalot.geo"),
                         ("texture", tex + "swalot.png"), ("layers", [])]),
            OrderedDict([("aspects", ["female"]), ("poser", "cobblemon:swalot_female")]),
            OrderedDict([("aspects", ["shiny"]), ("texture", tex + "swalot_shiny.png")]),
            OrderedDict([("aspects", ["alpha_eyes"]), ("layers", [OrderedDict([
                ("name", "alpha_eyes"), ("texture", tex + "swalot_alpha.png"), ("emissive", True)])])]),
        ]),
    ])
