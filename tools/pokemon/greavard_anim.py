"""Greavard animations, poser and resolver.

Reference notes (Pokédex / SV behaviour):
* Rests underground with only its candle-like head showing, waiting for people;
  when approached it jumps out with a spooky cry  -> `sleep` (burrowed), `cry` (pop-up howl)
* Friendly, gamboling, roughhouse personality that follows anyone who pays it
  attention -> bouncy trot, panting idle, play-bow battle stance, `wag`/`shake`/`sniff` quirks
* Tail Whip: wags its tail cutely -> `status`
* Its mouth is strong enough to shatter bones -> `physical` is a lunging chomp
* The candle flame flickers constantly (animated emissive texture + flame bone wobble)
"""
from collections import OrderedDict

from cobblegen.anim import Anim, wave, swave, awave

P = "greavard"
TAIL = ["tail", "tail2", "tail3", "tail4"]
LEGS_F = ("leg_front_left", "leg_front_right")
LEGS_B = ("leg_back_left", "leg_back_right")


def _flame(a, s=1.0, base_scale=1.0):
    a.expr("flame", "scale", [wave(0.05 * s, 820, 0, base_scale), wave(0.09 * s, 1130, 40, base_scale),
                              wave(0.05 * s, 820, 0, base_scale)])
    a.expr("flame", "rotation", [wave(3 * s, 210, 60), 0, wave(4 * s, 170)])


def _tail_wag(a, speed, amp, lift=0.0):
    for i, b in enumerate(TAIL):
        a.expr(b, "rotation", [wave(2 + i, speed / 2, -40 * i, lift if i == 0 else 0), wave(amp * (0.6 + 0.25 * i), speed, -35 * i), 0])


def _ears(a, speed, amp, phase=-60, base=0.0):
    for side, sg in (("left", 1), ("right", -1)):
        a.expr("ear_" + side, "rotation", [wave(amp * 0.6, speed, phase), 0, wave(amp * sg, speed, phase, base * sg)])
        a.expr("ear_%s2" % side, "rotation", [wave(amp * 0.8, speed, phase - 40), 0, wave(amp * 1.2 * sg, speed, phase - 40)])


def ground_idle():
    a = Anim("ground_idle", loop=True)
    s = 150
    a.expr("torso", "scale", [swave(0.012, s), swave(0.02, s), 1])
    a.expr("head", "rotation", [wave(1.5, s, -50), wave(2.0, s / 3), wave(1.5, s / 2)])
    # happy panting
    a.expr("jaw", "rotation", [wave(4, 600, 0, 3), 0, 0])
    a.expr("muzzle", "position", [0, wave(0.08, 600, 40), 0])
    _ears(a, s, 2.0)
    _tail_wag(a, 420, 14, lift=-4)
    a.expr("bangs", "rotation", [wave(1.0, s, -90), 0, 0])
    _flame(a)
    return a


def battle_idle():
    a = Anim("battle_idle", loop=True)
    s = 260
    # play-bow: chest low, rump high, ready to pounce
    a.expr("body", "rotation", [wave(1.5, s, 0, 6), 0, 0])
    a.expr("body", "position", [0, awave(0.5, s / 2, 0, 0.6), wave(0.3, s)])
    a.expr("head", "rotation", [wave(2, s, -40, -10), wave(4, s / 2), 0])
    a.expr("jaw", "rotation", [wave(6, s * 2, 0, 6), 0, 0])
    for b in LEGS_F:
        a.expr(b, "rotation", [wave(2, s, 0, -14), 0, 6 if b.endswith("left") else -6])
    for b in LEGS_B:
        a.expr(b, "rotation", [wave(2, s, 180, -8), 0, 0])
    _ears(a, s, 4.0, base=-6)
    _tail_wag(a, 700, 20, lift=-12)
    _flame(a, 1.3)
    return a


def ground_walk():
    a = Anim("ground_walk", loop=True)
    s = 540  # trot, ~0.67 s per stride
    a.expr("body", "position", [0, awave(0.6, s, 0, 0.2), 0])
    a.expr("body", "rotation", [wave(1.5, s * 2, 60), wave(2, s), wave(2.5, s)])
    a.expr("head", "rotation", [wave(2.5, s * 2, -60, -2), wave(-2, s, -40), wave(-2, s, -40)])
    a.expr("jaw", "rotation", [wave(4, s * 2, 0, 4), 0, 0])
    # diagonal pairs: front-left with back-right
    pairs = (("leg_front_left", 0), ("leg_back_right", 0), ("leg_front_right", 180), ("leg_back_left", 180))
    for b, ph in pairs:
        a.expr(b, "rotation", [wave(28, s, ph), 0, 0])
        a.expr(b, "position", [0, "math.clamp(math.sin(q.anim_time*%d%+d)*1.1,0,2)" % (s, ph - 90), 0])
    _ears(a, s * 2, 4.0, phase=-90)
    _tail_wag(a, s, 16, lift=-6)
    a.expr("candle", "rotation", [wave(3, s * 2, -100), 0, wave(2, s, -80)])
    a.expr("flame", "rotation", [wave(8, s * 2, -140, -6), 0, wave(5, s, -120)])
    a.expr("flame", "scale", [wave(0.05, 820, 0, 1), wave(0.09, 1130, 40, 1), wave(0.05, 820, 0, 1)])
    return a


def sleep():
    """Burrowed underground with only the candle showing."""
    a = Anim("sleep", loop=True)
    s = 60
    a.expr("body", "position", [0, wave(0.25, s, 0, -13.2), 0])
    a.expr("head", "rotation", [6, 0, 0])
    a.expr("jaw", "rotation", [-3, 0, 0])
    for b in LEGS_F + LEGS_B:
        a.expr(b, "rotation", [0, 0, 0])
    for i, b in enumerate(TAIL):
        a.expr(b, "rotation", [-50 if i == 0 else 0, 0, 0])
    a.expr("candle", "rotation", [wave(1.5, s, -60), 0, wave(1.5, s / 2)])
    _flame(a, 0.6, base_scale=0.85)
    return a


def wag():
    a = Anim("wag", length=1.6)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.2, [0, 6, 3]), (0.4, [0, -6, -3]), (0.6, [0, 6, 3]),
                               (0.8, [0, -6, -3]), (1.0, [0, 5, 2]), (1.2, [0, -3, -1]), (1.6, [0, 0, 0])])
    for i, b in enumerate(TAIL):
        k = 0.8 + 0.3 * i
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.1, [-6, 30 * k, 0]), (0.2, [-6, -30 * k, 0]), (0.3, [-6, 30 * k, 0]),
                               (0.4, [-6, -30 * k, 0]), (0.5, [-6, 30 * k, 0]), (0.6, [-6, -30 * k, 0]), (0.7, [-6, 30 * k, 0]),
                               (0.8, [-6, -30 * k, 0]), (0.9, [-6, 24 * k, 0]), (1.0, [-6, -24 * k, 0]), (1.1, [-4, 16 * k, 0]),
                               (1.2, [-3, -12 * k, 0]), (1.4, [0, 6 * k, 0]), (1.6, [0, 0, 0])], smooth=False)
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.3, [-6, 0, 8]), (1.2, [-6, 0, 8]), (1.6, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.3, [10, 0, 0]), (1.2, [10, 0, 0]), (1.6, [0, 0, 0])])
    return a


def shake():
    """Wet-dog shake."""
    a = Anim("shake", length=1.4)
    zs = [(0.0, 0), (0.1, 14), (0.2, -16), (0.3, 18), (0.4, -18), (0.5, 18), (0.6, -16), (0.7, 14), (0.8, -12),
          (0.9, 8), (1.0, -5), (1.15, 2), (1.4, 0)]
    a.keys("torso", "rotation", [(t, [0, 0, v * 0.6]) for t, v in zs])
    a.keys("head", "rotation", [(t, [0, 0, v]) for t, v in zs])
    for side, sg in (("left", 1), ("right", -1)):
        a.keys("ear_" + side, "rotation", [(min(t + 0.04, 1.4), [0, 0, -v * 1.6]) for t, v in zs])
        a.keys("ear_%s2" % side, "rotation", [(min(t + 0.07, 1.4), [0, 0, -v * 1.8]) for t, v in zs])
    a.keys("candle", "rotation", [(min(t + 0.05, 1.4), [0, 0, -v * 0.6]) for t, v in zs])
    a.keys("flame", "rotation", [(min(t + 0.08, 1.4), [0, 0, -v * 1.2]) for t, v in zs])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(min(t + 0.03 * i, 1.4), [0, v * 1.5, 0]) for t, v in zs])
    return a


def sniff():
    a = Anim("sniff", length=2.4)
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.4, [22, -12, 0]), (0.8, [24, 8, 0]), (1.2, [22, -6, 0]),
                               (1.6, [24, 10, 0]), (2.0, [8, 0, 0]), (2.4, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.4, [6, 0, 0]), (2.0, [6, 0, 0]), (2.4, [0, 0, 0])])
    a.keys("muzzle", "scale", [(t, [1, 1 + (0.06 if k % 2 else 0), 1]) for k, t in enumerate(
        [0.0, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 2.4])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.4, [-4, 0, 0]), (2.0, [-4, 0, 0]), (2.4, [0, 0, 0])])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.4, [-8, 10, 0]), (0.8, [-8, -10, 0]), (1.2, [-8, 10, 0]),
                               (1.6, [-8, -10, 0]), (2.0, [-4, 4, 0]), (2.4, [0, 0, 0])])
    return a


def cry():
    """Pops up with a spooky howl."""
    a = Anim("cry", length=1.7)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.15, [0, -1.2, 0]), (0.35, [0, 3.5, 0]), (0.55, [0, 0, 0]), (1.7, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.15, [4, 0, 0]), (0.35, [-10, 0, 0]), (0.55, [0, 0, 0]), (1.7, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.15, [8, 0, 0]), (0.45, [-28, 0, 0]), (0.8, [-26, 0, 4]),
                               (1.1, [-26, 0, -4]), (1.35, [-6, 0, 0]), (1.7, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.15, [-4, 0, 0]), (0.45, [30, 0, 0]), (1.1, [28, 0, 0]), (1.4, [0, 0, 0])])
    for side, sg in (("left", 1), ("right", -1)):
        a.keys("ear_" + side, "rotation", [(0.0, [0, 0, 0]), (0.35, [-10, 0, 25 * sg]), (0.6, [0, 0, -8 * sg]),
                                          (0.9, [0, 0, 6 * sg]), (1.3, [0, 0, 0])])
    a.keys("flame", "scale", [(0.0, [1, 1, 1]), (0.35, [1.25, 1.5, 1.25]), (1.1, [1.2, 1.4, 1.2]), (1.5, [1, 1, 1])])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.35, [-10, 0, 0]), (0.6, [6, 0, 0]), (1.0, [-4, 0, 0]), (1.7, [0, 0, 0])])
    for b in LEGS_F + LEGS_B:
        k = -1 if b in LEGS_F else 1
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.35, [20 * k, 0, 0]), (0.55, [0, 0, 0])])
    return a


def physical():
    """Lunging chomp."""
    a = Anim("physical", length=1.1)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 0, 2.0]), (0.45, [0, 2.0, -3.0]), (0.6, [0, 0, -5.0]),
                               (0.8, [0, 0, -3.5]), (1.1, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.25, [-6, 0, 0]), (0.5, [8, 0, 0]), (0.7, [4, 0, 0]), (1.1, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.25, [-12, 0, 0]), (0.5, [10, 0, 0]), (0.65, [6, 8, 6]),
                               (0.75, [6, -8, -6]), (0.85, [4, 4, 3]), (1.1, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.3, [30, 0, 0]), (0.5, [34, 0, 0]), (0.58, [-6, 0, 0]),
                              (0.8, [-6, 0, 0]), (1.1, [0, 0, 0])], smooth=False)
    for b in LEGS_F:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.45, [-35, 0, 0]), (0.6, [-10, 0, 0]), (0.9, [0, 0, 0])])
    for b in LEGS_B:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.45, [30, 0, 0]), (0.6, [10, 0, 0]), (0.9, [0, 0, 0])])
    a.keys("flame", "rotation", [(0.0, [0, 0, 0]), (0.45, [-20, 0, 0]), (0.65, [25, 0, 0]), (0.85, [-8, 0, 0]), (1.1, [0, 0, 0])])
    _flame_keys_ears(a, [(0.0, 0), (0.45, -20), (0.65, 25), (0.85, -8), (1.1, 0)])
    return a


def _flame_keys_ears(a, frames):
    for side, sg in (("left", 1), ("right", -1)):
        a.keys("ear_" + side, "rotation", [(t, [v, 0, 0]) for t, v in frames])
        a.keys("ear_%s2" % side, "rotation", [(min(t + 0.05, frames[-1][0]), [v * 1.2, 0, 0]) for t, v in frames])


def special(name="special"):
    """Spooky ghost attack: rears back, the candle flares and the flame lashes forward."""
    a = Anim(name, length=1.5)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.45, [-8, 0, 0]), (0.65, [6, 0, 0]), (1.0, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.45, [0, 0.8, 1.2]), (0.65, [0, 0.3, -1.0]), (1.0, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.45, [-18, 0, 0]), (0.65, [12, 0, 0]), (0.95, [4, 0, 0]), (1.5, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.45, [8, 0, 0]), (0.65, [30, 0, 0]), (1.1, [24, 0, 0]), (1.4, [0, 0, 0])])
    a.keys("flame", "scale", [(0.0, [1, 1, 1]), (0.45, [1.4, 1.7, 1.4]), (0.7, [1.3, 1.5, 1.3]), (1.2, [1.1, 1.2, 1.1]), (1.5, [1, 1, 1])])
    a.keys("flame", "rotation", [(0.0, [0, 0, 0]), (0.45, [-15, 0, 0]), (0.65, [35, 0, 0]), (0.9, [10, 0, 0]), (1.2, [-5, 0, 0]), (1.5, [0, 0, 0])])
    a.keys("candle", "rotation", [(0.0, [0, 0, 0]), (0.45, [-6, 0, 0]), (0.65, [10, 0, 0]), (1.0, [0, 0, 0])])
    _flame_keys_ears(a, [(0.0, 0), (0.45, 18), (0.65, -22), (0.95, 8), (1.5, 0)])
    for b in LEGS_F:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.45, [-12, 0, 0]), (0.7, [8, 0, 0]), (1.0, [0, 0, 0])])
    return a


def status():
    """Tail Whip: turns its rump and wags its tail cutely."""
    a = Anim("status", length=2.0)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.3, [-4, -40, 0]), (1.6, [-4, -40, 0]), (2.0, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.3, [0, 0.4, 0]), (1.6, [0, 0.4, 0]), (2.0, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.3, [-8, 35, 10]), (1.6, [-8, 35, 10]), (2.0, [0, 0, 0])])
    a.keys("torso", "rotation", [(t, [0, 0, (6 if k % 2 else -6) if 0.3 <= t <= 1.5 else 0])
                                 for k, t in enumerate([0.0, 0.3, 0.45, 0.6, 0.75, 0.9, 1.05, 1.2, 1.35, 1.5, 1.6, 2.0])])
    for i, b in enumerate(TAIL):
        kk = 0.9 + 0.35 * i
        frames = [(0.0, [0, 0, 0]), (0.3, [-8, 0, 0])]
        t = 0.3
        sign = 1
        while t < 1.5:
            t = round(t + 0.075, 3)
            frames.append((t, [-8, 32 * kk * sign, 0]))
            sign = -sign
        frames += [(1.65, [-4, 0, 0]), (2.0, [0, 0, 0])]
        a.keys(b, "rotation", frames, smooth=False)
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.3, [12, 0, 0]), (1.6, [12, 0, 0]), (2.0, [0, 0, 0])])
    return a


def recoil():
    a = Anim("recoil", length=0.8)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.1, [0, 0.8, 2.2]), (0.35, [0, 0.2, 1.2]), (0.8, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.1, [-10, 0, 0]), (0.3, [5, 0, 0]), (0.5, [-2, 0, 0]), (0.8, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.1, [-14, 0, 6]), (0.35, [6, 0, -3]), (0.8, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.1, [18, 0, 0]), (0.45, [8, 0, 0]), (0.8, [0, 0, 0])])
    _flame_keys_ears(a, [(0.0, 0), (0.12, 25), (0.35, -12), (0.55, 5), (0.8, 0)])
    a.keys("flame", "rotation", [(0.0, [0, 0, 0]), (0.12, [25, 0, 0]), (0.35, [-12, 0, 0]), (0.55, [5, 0, 0]), (0.8, [0, 0, 0])])
    return a


def faint():
    """Flops down flat, legs splayed, while the candle gutters out."""
    a = Anim("faint", length=2.6)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 1.2, 0]), (0.7, [0, -2.2, 0]), (0.85, [0, -1.6, 0]),
                               (1.0, [0, -2.4, 0]), (2.6, [0, -2.4, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.25, [-6, 0, 0]), (0.7, [4, 0, 6]), (1.0, [3, 0, 8]), (2.6, [3, 0, 8])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.25, [-14, 0, 0]), (0.7, [10, 0, -4]), (1.0, [14, 0, -6]), (2.6, [14, 0, -6])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.25, [18, 0, 0]), (0.8, [6, 0, 0]), (2.6, [8, 0, 0])])
    for b, k in (("leg_front_left", 1), ("leg_front_right", -1)):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.7, [-62, 0, 14 * k]), (1.0, [-70, 0, 18 * k]), (2.6, [-70, 0, 18 * k])])
    for b, k in (("leg_back_left", 1), ("leg_back_right", -1)):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.7, [62, 0, 14 * k]), (1.0, [70, 0, 18 * k]), (2.6, [70, 0, 18 * k])])
    for side, sg in (("left", 1), ("right", -1)):
        a.keys("ear_" + side, "rotation", [(0.0, [0, 0, 0]), (0.25, [0, 0, 18 * sg]), (0.8, [0, 0, -28 * sg]),
                                          (1.0, [0, 0, -24 * sg]), (2.6, [0, 0, -26 * sg])])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (1.0, [40 if i == 0 else 14, 0, 0]), (2.6, [44 if i == 0 else 16, 0, 0])])
    a.keys("candle", "rotation", [(0.0, [0, 0, 0]), (0.8, [0, 0, -10]), (1.0, [0, 0, -14]), (2.6, [0, 0, -14])])
    a.keys("flame", "scale", [(0.0, [1, 1, 1]), (0.4, [1.1, 1.2, 1.1]), (1.2, [0.7, 0.55, 0.7]), (1.8, [0.45, 0.3, 0.45]),
                              (2.2, [0.3, 0.18, 0.3]), (2.6, [0.25, 0.15, 0.25])])
    return a


def all_animations():
    return [ground_idle(), battle_idle(), ground_walk(), sleep(), wag(), shake(), sniff(), cry(), physical(),
            special(), special("spray"), status(), recoil(), faint()]


PREVIEW_ORDER = ["ground_idle", "ground_walk", "battle_idle", "sleep", "cry", "physical", "special", "status",
                 "recoil", "faint", "wag", "shake", "sniff"]
OVER_IDLE = ("cry", "wag", "shake", "sniff")


def poser(female=False):
    look = "q.look('head', 0.8, 0.8, 25, -20, 35, -35)"
    quirks = ["q.bedrock_quirk('greavard', 'wag', 6, 18, 1)",
              "q.bedrock_quirk('greavard', 'shake', 30, 70, 1)",
              "q.bedrock_quirk('greavard', 'sniff', 15, 40, 1)"]

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
        return d

    out = OrderedDict()
    out["portraitScale"] = 1.45
    out["portraitTranslation"] = [-0.3, -0.35, 0]
    out["profileScale"] = 0.72
    out["profileTranslation"] = [0, 0.5, 0]
    out["rootBone"] = P
    out["animations"] = OrderedDict([
        ("cry", "q.bedrock_stateful('greavard', 'cry')"),
        ("recoil", "q.bedrock_stateful('greavard', 'recoil')"),
        ("faint", "q.bedrock_primary('greavard', 'faint', q.curve('one'))"),
        ("physical", "q.bedrock_primary('greavard', 'physical', q.curve('symmetrical_wide'))"),
        ("special", "q.bedrock_primary('greavard', 'special', q.curve('symmetrical_wide'))"),
        ("spray", "q.bedrock_primary('greavard', 'spray', q.curve('symmetrical_wide'))"),
        ("status", "q.bedrock_primary('greavard', 'status', q.curve('symmetrical_wide'))"),
    ])
    poses = OrderedDict()
    poses["battle-standing"] = pose(["STAND"], [look, "q.bedrock('greavard', 'battle_idle')"], battle=True,
                                    q=["q.bedrock_quirk('greavard', 'wag', 4, 10, 1)"])
    poses["standing"] = pose(["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"],
                             [look, "q.bedrock('greavard', 'ground_idle')"], battle=False)
    poses["walking"] = pose(["WALK", "SWIM"], [look, "q.bedrock('greavard', 'ground_walk')"], q=False)
    poses["sleep"] = pose(["SLEEP"], ["q.bedrock('greavard', 'sleep')"], q=False,
                          named={"cry": "q.bedrock_stateful('dummy', 'cry')"})
    out["poses"] = poses
    return out


def resolver():
    tex = "cobblemon:textures/pokemon/0971_greavard/"
    flame = OrderedDict([
        ("name", "emissive"),
        ("texture", OrderedDict([("loop", True), ("fps", 8),
                                 ("frames", [tex + "greavard_flame_%d.png" % i for i in range(4)])])),
        ("emissive", True),
        ("translucent", True),
    ])
    return OrderedDict([
        ("species", "cobblemon:greavard"),
        ("order", 0),
        ("variations", [
            OrderedDict([("aspects", []), ("poser", "cobblemon:greavard"), ("model", "cobblemon:greavard.geo"),
                         ("texture", tex + "greavard.png"), ("layers", [flame])]),
            OrderedDict([("aspects", ["shiny"]), ("texture", tex + "greavard_shiny.png")]),
            OrderedDict([("aspects", ["alpha_eyes"]), ("layers", [OrderedDict([
                ("name", "alpha_eyes"), ("texture", tex + "greavard_alpha.png"), ("emissive", True)])])]),
        ]),
    ])
HAS_FEMALE = False
