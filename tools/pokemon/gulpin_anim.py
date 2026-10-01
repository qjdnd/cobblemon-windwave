"""Gulpin animations, poser and resolver.

Motion notes (from the games/anime): Gulpin is a sleepy, gluttonous stomach-
blob. It slides/bounces like a slime, its feather lags behind every motion,
its puckered lips open into a big round mouth when it cries, yawns (it learns
Yawn) or spits Sludge/Acid Spray, and it melts flat when it faints.
"""
from collections import OrderedDict

from cobblegen.anim import Anim, wave, swave, awave

FEATHER = ["feather", "feather2", "feather3", "feather4", "feather5"]
P = "gulpin"


def _feather_follow(a, speed, amp_x, amp_z, lag=30, base_x=0.0, start_phase=-60, grow=1.25, z_speed=None):
    zs = z_speed if z_speed is not None else speed / 2.0
    ax, az = amp_x, amp_z
    for i, b in enumerate(FEATHER):
        ph = start_phase - lag * i
        a.expr(b, "rotation", [wave(ax, speed, ph, base_x if i == 0 else 0.0), 0, wave(az, zs, ph + 20)])
        ax *= grow
        az *= 1.1


def ground_idle():
    a = Anim("ground_idle", loop=True)
    s = 120  # 3 s breathing cycle
    a.expr("body", "scale", [swave(0.022, s), swave(-0.032, s), swave(0.022, s)])
    a.expr("head", "position", [0, wave(0.12, s, -40), 0])
    a.expr("head", "rotation", [wave(1.2, s, -70), 0, wave(1.0, s / 2)])
    a.expr("arm_left", "rotation", [0, wave(3, s, -20), wave(4, s, -30, base=2)])
    a.expr("arm_right", "rotation", [0, wave(-3, s, -20), wave(-4, s, -30, base=-2)])
    a.expr("tail", "rotation", [wave(2, s, -90), wave(4, s / 2), 0])
    a.expr("tail2", "rotation", [wave(3, s, -130), wave(5, s / 2, -40), 0])
    a.expr("lip_top", "scale", [swave(0.03, s * 2), 1, swave(0.05, s * 2)])
    a.expr("lip_bottom", "scale", [swave(0.03, s * 2, -60), 1, swave(0.05, s * 2, -60)])
    _feather_follow(a, s, 2.4, 1.8, lag=28)
    return a


def battle_idle():
    a = Anim("battle_idle", loop=True)
    s = 240
    a.expr("body", "position", [0, awave(0.35, s / 2), 0])
    a.expr("body", "scale", [swave(0.035, s, 90), swave(-0.05, s, 90), swave(0.035, s, 90)])
    a.expr("body", "rotation", [wave(1.5, s, 30, base=1.5), 0, wave(1.5, s / 2)])
    a.expr("head", "rotation", [wave(1.5, s, -30, base=-2), 0, wave(-1.2, s / 2, -40)])
    a.expr("arm_left", "rotation", [0, wave(6, s, -20, base=8), wave(6, s, -30, base=-14)])
    a.expr("arm_right", "rotation", [0, wave(-6, s, -20, base=-8), wave(-6, s, -30, base=14)])
    a.expr("tail", "rotation", [wave(3, s, -90), wave(6, s / 2), 0])
    a.expr("tail2", "rotation", [wave(4, s, -130), wave(8, s / 2, -40), 0])
    _feather_follow(a, s, 3.0, 2.5, lag=32, base_x=8)
    return a


def ground_walk():
    a = Anim("ground_walk", loop=True)
    s = 400  # one hop every 0.9 s
    a.expr("body", "position", [0, awave(0.9, s / 2), 0])
    a.expr("body", "scale", [wave(0.045, s, 0, 1, "cos"), wave(-0.065, s, 0, 1, "cos"), wave(0.03, s, 0, 1, "cos")])
    a.expr("body", "rotation", [wave(2.5, s, 0, 2.5), 0, wave(2.2, s / 2)])
    a.expr("head", "rotation", [wave(-2.5, s, -60), 0, wave(-2.0, s / 2, -40)])
    a.expr("arm_left", "rotation", [wave(12, s / 2), wave(8, s / 2, 90, 4), wave(9, s, -30, 2)])
    a.expr("arm_right", "rotation", [wave(-12, s / 2), wave(8, s / 2, 90, -4), wave(-9, s, -30, -2)])
    a.expr("tail", "rotation", [wave(6, s, -90), wave(10, s / 2, -60), 0])
    a.expr("tail2", "rotation", [wave(8, s, -150), wave(12, s / 2, -120), 0])
    a.expr("lip_top", "position", [0, 0, wave(0.15, s, -40)])
    _feather_follow(a, s, 5.0, 3.0, lag=34, start_phase=-80, z_speed=s / 2, grow=1.18)
    return a


def sleep():
    a = Anim("sleep", loop=True)
    s = 72  # slow 5 s breaths
    a.expr("body", "scale", [wave(0.015, s, 0, 1.07), wave(-0.025, s, 0, 0.86), wave(0.015, s, 0, 1.06)])
    a.expr("head", "position", [0, wave(0.1, s, -40, -0.35), 0.2])
    a.expr("head", "rotation", [wave(1, s, -60, 4), 0, 0])
    a.expr("arm_left", "rotation", [0, 6, 12])
    a.expr("arm_right", "rotation", [0, -6, -12])
    a.expr("lip_bottom", "position", [0, wave(0.1, s, -90, -0.25), 0])
    a.expr("mouth_inner", "scale", [1, wave(0.2, s, -90, 1.2), 1])
    a.expr("tail", "rotation", [3, 0, 0])
    a.expr("eye_left", "scale", [1.1, 0.7, 1])
    a.expr("eye_right", "scale", [1.1, 0.7, 1])
    droop = [-10, -10, -10, -9, -8]
    for i, b in enumerate(FEATHER):
        a.expr(b, "rotation", [wave(1.5 + i * 0.4, s, -60 - 25 * i, droop[i]), 0, wave(1.5, s / 2, -40 * i, 6 if i == 0 else 2)])
    return a


def blink():
    a = Anim("blink", length=0.3)
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.08, [1.2, 0.25, 1]), (0.18, [1.2, 0.25, 1]), (0.3, [1, 1, 1])], smooth=False)
    return a


def cry():
    a = Anim("cry", length=1.6)
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.15, [1.07, 0.9, 1.07]), (0.38, [0.94, 1.14, 0.94]),
                            (0.9, [0.96, 1.1, 0.96]), (1.2, [1.04, 0.95, 1.04]), (1.6, [1, 1, 1])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.15, [0, 0, 0]), (0.38, [0, 0.6, 0]), (0.9, [0, 0.4, 0]), (1.2, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.15, [4, 0, 0]), (0.38, [-10, 0, 0]), (0.65, [-8, 0, 3]),
                               (0.9, [-8, 0, -3]), (1.2, [2, 0, 0]), (1.6, [0, 0, 0])])
    _mouth_open(a, [(0.0, 0), (0.15, -0.1), (0.38, 1.0), (0.9, 0.9), (1.15, 0.0), (1.6, 0)])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.3, [1.2, 0.4, 1]), (0.95, [1.2, 0.4, 1]), (1.2, [1, 1, 1])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.38, [0, 10, -22]), (0.65, [0, 10, -16]), (0.9, [0, 10, -22]), (1.2, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.38, [0, -10, 22]), (0.65, [0, -10, 16]), (0.9, [0, -10, 22]), (1.2, [0, 0, 0])])
    _feather_keys(a, [(0.0, 0), (0.18, -13), (0.4, 31), (0.6, -18), (0.8, 13), (1.05, -7), (1.35, 2), (1.6, 0)])
    return a


def _mouth_open(a, frames):
    """frames: (t, amount 0..1) -> lips part and the mouth hole grows."""
    a.keys("lip_top", "position", [(t, [0, 1.4 * k, -0.3 * k]) for t, k in frames])
    a.keys("lip_bottom", "position", [(t, [0, -1.2 * k, -0.2 * k]) for t, k in frames])
    a.keys("lip_top", "scale", [(t, [1 + 0.15 * k, 1, 1 + 0.1 * k]) for t, k in frames])
    a.keys("lip_bottom", "scale", [(t, [1 + 0.2 * k, 1, 1 + 0.1 * k]) for t, k in frames])
    a.keys("mouth_inner", "scale", [(t, [1 + 0.6 * max(k, 0), 1 + 1.4 * max(k, 0), 1]) for t, k in frames])


FEATHER_W = [0.3, 0.2, 0.2, 0.15, 0.15]


def _feather_keys(a, frames, lag=0.05):
    """frames: (t, total tip deflection in degrees), spread along the chain with lag."""
    end = frames[-1][0]
    for i, b in enumerate(FEATHER):
        w = FEATHER_W[i]
        seen = OrderedDict()
        for t, v in frames:
            tt = min(round(t + (lag * i if 0 < t < end else 0), 3), end)
            seen[tt] = [v * w, 0, 0]
        a.keys(b, "rotation", list(seen.items()))


def physical():
    a = Anim("physical", length=1.1)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 1.5, 1.8]), (0.42, [0, 2.6, -2.5]), (0.55, [0, 2.1, -4.5]),
                               (0.7, [0, 0.6, -3.8]), (0.9, [0, 0.3, -1]), (1.1, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.25, [-10, 0, 0]), (0.45, [8, 0, 0]), (0.55, [14, 0, 0]),
                               (0.7, [4, 0, 0]), (0.9, [-2, 0, 0]), (1.1, [0, 0, 0])])
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.25, [1.07, 0.9, 1.05]), (0.42, [0.94, 1.1, 1.05]),
                            (0.55, [1.12, 0.85, 1.06]), (0.75, [0.97, 1.04, 0.98]), (1.1, [1, 1, 1])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, -20, 0]), (0.55, [0, 35, -10]), (0.8, [0, 10, 0]), (1.1, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 20, 0]), (0.55, [0, -35, 10]), (0.8, [0, -10, 0]), (1.1, [0, 0, 0])])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.4, [1.15, 0.5, 1]), (0.7, [1.15, 0.5, 1]), (0.9, [1, 1, 1])])
    _feather_keys(a, [(0.0, 0), (0.25, 22), (0.5, -40), (0.7, 20), (0.88, -9), (1.1, 0)])
    a.keys("tail", "rotation", [(0.0, [0, 0, 0]), (0.25, [-8, 0, 0]), (0.55, [14, 0, 0]), (0.8, [-4, 0, 0]), (1.1, [0, 0, 0])])
    return a


def special(name="special"):
    a = Anim(name, length=1.4)
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.45, [1.1, 1.12, 1.1]), (0.6, [0.9, 0.92, 0.88]),
                            (0.8, [1.03, 0.98, 1.03]), (1.0, [0.99, 1.01, 0.99]), (1.4, [1, 1, 1])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.45, [-8, 0, 0]), (0.6, [10, 0, 0]), (0.85, [-2, 0, 0]), (1.4, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.45, [0, 1.0, 0.8]), (0.62, [0, 1.2, -0.6]), (0.9, [0, 0.2, 0.2]), (1.4, [0, 0, 0])])
    a.keys("mouth", "position", [(0.0, [0, 0, 0]), (0.45, [0, 0, 0.3]), (0.6, [0, 0, -1.4]), (0.9, [0, 0, -0.4]), (1.4, [0, 0, 0])])
    _mouth_open(a, [(0.0, 0), (0.45, -0.15), (0.58, 0.65), (0.85, 0.5), (1.1, 0), (1.4, 0)])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.4, [1.0, 1.0, 1]), (0.55, [1.2, 0.35, 1]), (0.95, [1.2, 0.35, 1]), (1.15, [1, 1, 1])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.45, [0, -10, -18]), (0.6, [0, 15, 8]), (1.0, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.45, [0, 10, 18]), (0.6, [0, -15, -8]), (1.0, [0, 0, 0])])
    _feather_keys(a, [(0.0, 0), (0.45, 26), (0.62, -31), (0.82, 15), (1.05, -7), (1.4, 0)])
    return a


def status():
    a = Anim("status", length=1.6)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.2, [0, 8, 8]), (0.45, [0, -8, -8]), (0.7, [0, 6, 6]),
                               (0.95, [0, -5, -5]), (1.2, [0, 2, 2]), (1.6, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.2, [0, 1.0, 0]), (0.32, [0, 0.2, 0]), (0.45, [0, 1.0, 0]),
                               (0.58, [0, 0.2, 0]), (0.7, [0, 0.8, 0]), (0.82, [0, 0.1, 0]), (0.95, [0, 0.6, 0]), (1.2, [0, 0.2, 0]), (1.6, [0, 0, 0])])
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.2, [1.04, 0.96, 1.04]), (0.45, [0.97, 1.05, 0.97]),
                            (0.7, [1.04, 0.96, 1.04]), (0.95, [0.98, 1.03, 0.98]), (1.6, [1, 1, 1])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.2, [0, 0, -25]), (0.45, [0, 0, 5]), (0.7, [0, 0, -25]),
                                   (0.95, [0, 0, 5]), (1.3, [0, 0, -8]), (1.6, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.2, [0, 0, -5]), (0.45, [0, 0, 25]), (0.7, [0, 0, -5]),
                                    (0.95, [0, 0, 25]), (1.3, [0, 0, 8]), (1.6, [0, 0, 0])])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.15, [1.2, 0.4, 1]), (1.3, [1.2, 0.4, 1]), (1.5, [1, 1, 1])])
    for i, b in enumerate(FEATHER):
        amp = 1 + 0.25 * i
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.2 + 0.04 * i, [3 * amp, 0, -10 * amp]), (0.45 + 0.04 * i, [-3 * amp, 0, 10 * amp]),
                               (0.7 + 0.04 * i, [3 * amp, 0, -8 * amp]), (0.95 + 0.04 * i, [-2 * amp, 0, 6 * amp]),
                               (1.25 + 0.04 * i, [0, 0, -2 * amp]), (1.6, [0, 0, 0])])
    return a


def recoil():
    a = Anim("recoil", length=0.75)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.1, [0, 1.8, 1.8]), (0.3, [0, 0.7, 1.0]), (0.5, [0, 0.3, 0.4]), (0.75, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.1, [-12, 0, 0]), (0.3, [5, 0, 0]), (0.5, [-2, 0, 0]), (0.75, [0, 0, 0])])
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.1, [1.1, 0.82, 1.1]), (0.25, [0.94, 1.08, 0.94]),
                            (0.45, [1.03, 0.97, 1.03]), (0.75, [1, 1, 1])])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.08, [1.25, 0.3, 1]), (0.45, [1.25, 0.3, 1]), (0.6, [1, 1, 1])])
    _mouth_open(a, [(0.0, 0), (0.1, 0.35), (0.4, 0.2), (0.6, 0), (0.75, 0)])
    _feather_keys(a, [(0.0, 0), (0.1, 35), (0.3, -22), (0.5, 11), (0.75, 0)], lag=0.03)
    return a


def faint():
    a = Anim("faint", length=2.6)
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (0.2, [0.95, 1.1, 0.95]), (0.6, [1.15, 0.72, 1.15]),
                            (1.0, [1.24, 0.56, 1.22]), (1.4, [1.27, 0.53, 1.24]), (2.6, [1.3, 0.5, 1.26])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.2, [0, 0.8, 0]), (0.6, [0, 0, 0]), (2.6, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.2, [-4, 0, 3]), (0.6, [3, 0, -2]), (1.0, [2, 0, 0]), (2.6, [2, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.6, [8, 0, 0]), (1.0, [12, 0, 0]), (2.6, [12, 0, 0])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (0.6, [0, 10, 22]), (2.6, [0, 12, 26])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (0.6, [0, -10, -22]), (2.6, [0, -12, -26])])
    a.keys("lip_bottom", "position", [(0.0, [0, 0, 0]), (0.6, [0, -0.5, 0]), (2.6, [0, -0.6, 0])])
    a.keys("mouth_inner", "scale", [(0.0, [1, 1, 1]), (0.6, [1.2, 1.6, 1]), (2.6, [1.2, 1.7, 1])])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.4, [1.2, 0.4, 1]), (2.6, [1.2, 0.4, 1])])
    droop = [(0.0, 0), (0.2, 10), (0.6, -18), (1.0, -26), (1.4, -24), (2.6, -25)]
    for i, b in enumerate(FEATHER):
        k = [0.9, 0.6, 0.55, 0.5, 0.45][i]
        a.keys(b, "rotation", [(t + (0.04 * i if 0 < t < 2.6 else 0), [v * k, 0, (14 if i == 0 else 3) * min(1, t / 1.0)]) for t, v in droop])
    a.keys("tail", "rotation", [(0.0, [0, 0, 0]), (0.6, [-6, 0, 0]), (2.6, [-6, 0, 0])])
    return a


def yawn():
    a = Anim("yawn", length=2.4)
    _mouth_open(a, [(0.0, 0), (0.5, 0.35), (1.2, 1.15), (1.6, 1.15), (1.85, 0.0), (2.0, 0.08), (2.2, 0), (2.4, 0)])
    a.keys("body", "scale", [(0.0, [1, 1, 1]), (1.2, [0.96, 1.1, 0.96]), (1.6, [0.96, 1.1, 0.96]),
                            (1.9, [1.05, 0.93, 1.05]), (2.15, [0.99, 1.01, 0.99]), (2.4, [1, 1, 1])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (1.2, [-9, 0, 2]), (1.6, [-9, 0, -2]), (1.9, [3, 0, 0]), (2.4, [0, 0, 0])])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.9, [1.2, 0.35, 1]), (1.75, [1.2, 0.35, 1]), (2.05, [1, 1, 1])])
    a.keys("arm_left", "rotation", [(0.0, [0, 0, 0]), (1.2, [0, 8, -18]), (1.6, [0, 8, -18]), (1.9, [0, 0, 0])])
    a.keys("arm_right", "rotation", [(0.0, [0, 0, 0]), (1.2, [0, -8, 18]), (1.6, [0, -8, 18]), (1.9, [0, 0, 0])])
    _feather_keys(a, [(0.0, 0), (1.2, 20), (1.6, 15), (1.9, -15), (2.15, 7), (2.4, 0)])
    return a


def gulp():
    a = Anim("gulp", length=1.3)
    for lip in ("lip_top", "lip_bottom"):
        a.keys(lip, "scale", [(0.0, [1, 1, 1]), (0.15, [1.2, 1.15, 1.3]), (0.3, [1.2, 1.15, 1.3]), (0.42, [0.9, 0.9, 0.9]), (0.6, [1, 1, 1])])
    a.keys("mouth", "position", [(0.0, [0, 0, 0]), (0.15, [0, 0, -0.6]), (0.3, [0, 0, -0.6]), (0.45, [0, 0, 0])])
    a.keys("head", "scale", [(0.0, [1, 1, 1]), (0.42, [1.06, 1.05, 1.06]), (0.62, [0.99, 1, 0.99]), (0.8, [1, 1, 1])])
    a.keys("base", "scale", [(0.0, [1, 1, 1]), (0.5, [1, 1, 1]), (0.7, [1.06, 0.97, 1.06]), (0.95, [0.99, 1.01, 0.99]), (1.3, [1, 1, 1])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.7, [0, 0, 0]), (0.82, [0, 0.4, 0]), (0.95, [0, 0, 0])])
    for e in ("eye_left", "eye_right"):
        a.keys(e, "scale", [(0.0, [1, 1, 1]), (0.35, [1.2, 0.4, 1]), (0.7, [1.2, 0.4, 1]), (0.85, [1, 1, 1])])
    _feather_keys(a, [(0.0, 0), (0.7, 0), (0.82, 13), (1.0, -7), (1.3, 0)])
    return a


def all_animations():
    return [ground_idle(), battle_idle(), ground_walk(), sleep(), blink(), cry(), physical(), special(),
            special("spray"), status(), recoil(), faint(), yawn(), gulp()]


# ------------------------------------------------------------------ poser
def poser(female=False):
    look = "q.look('head', 0.4, 0.6, 10, -10, 25, -25)"
    quirks = ["q.bedrock_quirk('gulpin', 'blink')",
              "q.bedrock_quirk('gulpin', 'gulp', 10, 25, 1)",
              "q.bedrock_quirk('gulpin', 'yawn', 25, 60, 1)"]
    feather_fix = [{"part": "feather", "scale": [1, 0.72, 0.85]}] if female else []

    def pose(types, anims, battle=None, q=True, named=None, extra=None):
        d = OrderedDict()
        d["poseTypes"] = types
        if battle is not None:
            d["isBattle"] = battle
        d["animations"] = anims
        if q:
            d["quirks"] = list(quirks if q is True else q)
        if named:
            d["namedAnimations"] = named
        tp = list(feather_fix) + (extra or [])
        if tp:
            d["transformedParts"] = tp
        return d

    out = OrderedDict()
    out["portraitScale"] = 1.75
    out["portraitTranslation"] = [-0.18, -0.85, 0]
    out["profileScale"] = 0.95
    out["profileTranslation"] = [0, 0.22, 0]
    out["rootBone"] = P
    out["animations"] = OrderedDict([
        ("cry", "q.bedrock_stateful('gulpin', 'cry')"),
        ("recoil", "q.bedrock_stateful('gulpin', 'recoil')"),
        ("faint", "q.bedrock_primary('gulpin', 'faint', q.curve('one'))"),
        ("physical", "q.bedrock_primary('gulpin', 'physical', q.curve('symmetrical_wide'))"),
        ("special", "q.bedrock_primary('gulpin', 'special', q.curve('symmetrical_wide'))"),
        ("spray", "q.bedrock_primary('gulpin', 'spray', q.curve('symmetrical_wide'))"),
        ("status", "q.bedrock_primary('gulpin', 'status', q.curve('symmetrical_wide'))"),
    ])
    poses = OrderedDict()
    poses["battle-standing"] = pose(["STAND"], [look, "q.bedrock('gulpin', 'battle_idle')"], battle=True,
                                    q=["q.bedrock_quirk('gulpin', 'blink')"])
    poses["standing"] = pose(["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"],
                             [look, "q.bedrock('gulpin', 'ground_idle')"], battle=False)
    poses["walking"] = pose(["WALK", "SWIM"], ["q.bedrock('gulpin', 'ground_walk')"],
                            q=["q.bedrock_quirk('gulpin', 'blink')"])
    poses["sleep"] = pose(["SLEEP"], ["q.bedrock('gulpin', 'sleep')"], q=False,
                          named={"cry": "q.bedrock_stateful('dummy', 'cry')"})
    out["poses"] = poses
    return out


def resolver():
    tex = "cobblemon:textures/pokemon/0316_gulpin/"
    return OrderedDict([
        ("species", "cobblemon:gulpin"),
        ("order", 0),
        ("variations", [
            OrderedDict([("aspects", []), ("poser", "cobblemon:gulpin"), ("model", "cobblemon:gulpin.geo"),
                         ("texture", tex + "gulpin.png"), ("layers", [])]),
            OrderedDict([("aspects", ["female"]), ("poser", "cobblemon:gulpin_female")]),
            OrderedDict([("aspects", ["shiny"]), ("texture", tex + "gulpin_shiny.png")]),
            OrderedDict([("aspects", ["alpha_eyes"]), ("layers", [OrderedDict([
                ("name", "alpha_eyes"), ("texture", tex + "gulpin_alpha.png"), ("emissive", True)])])]),
        ]),
    ])


PREVIEW_ORDER = ["ground_idle", "ground_walk", "battle_idle", "sleep", "cry", "physical", "special",
                 "status", "recoil", "faint", "blink", "yawn", "gulp"]
OVER_IDLE = ("cry", "blink", "yawn", "gulp")
