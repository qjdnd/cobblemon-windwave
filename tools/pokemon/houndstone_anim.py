"""Houndstone animations, poser and resolver.

Reference notes (Pokédex / SV):
* Spends most of its time sleeping in graveyards -> `sleep` sinks into a fur mound with
  the tombstone standing upright like a grave marker; it rests during the day.
* The most loyal of all dog Pokémon -> calm "guard" idle, `look` quirk scanning around,
  tail-wag quirk, heavy loyal trot.
* Its tombstone-like head protrusion is something it doesn't like being touched -> the
  stone barely moves except in big motions.
* Signature move Last Respects -> `physical` lunging chomp with the huge jaw.
* Ghost-type attacks -> `special`: rears up, howls with the jaw wide open and slams down.
"""
from collections import OrderedDict

from cobblegen.anim import Anim, wave, swave, awave

P = "houndstone"
TAIL = ["tail", "tail2", "tail3"]
LEGS_F = ("leg_front_left", "leg_front_right")
LEGS_B = ("leg_back_left", "leg_back_right")


def _tail(a, speed, amp_y, amp_x=2.0, base=0.0):
    for i, b in enumerate(TAIL):
        a.expr(b, "rotation", [wave(amp_x, speed / 2, -40 * i, base if i == 0 else 0), wave(amp_y * (0.7 + 0.3 * i), speed, -40 * i), 0])


def ground_idle():
    a = Anim("ground_idle", loop=True)
    s = 100
    a.expr("torso", "scale", [swave(0.012, s), swave(0.018, s), swave(0.008, s)])
    a.expr("neck", "rotation", [wave(1.2, s, -40), 0, 0])
    a.expr("head", "rotation", [wave(1.0, s, -70), wave(2.0, s / 3), wave(0.8, s / 2)])
    a.expr("jaw", "rotation", [wave(2.5, s, -90, 1.5), 0, 0])
    a.expr("collar", "rotation", [wave(1.0, s, -60), 0, wave(0.8, s / 2, -30)])
    a.expr("tombstone", "rotation", [wave(0.6, s, -100), 0, wave(0.5, s / 2, -60)])
    _tail(a, 160, 8, base=-3)
    return a


def battle_idle():
    a = Anim("battle_idle", loop=True)
    s = 220
    a.expr("body", "position", [0, wave(0.25, s, 0, -0.6), wave(0.2, s / 2)])
    a.expr("body", "rotation", [wave(1.0, s, 0, 4), 0, 0])
    a.expr("neck", "rotation", [wave(1.5, s, -40, 8), 0, 0])
    a.expr("head", "rotation", [wave(1.5, s, -60, -6), wave(3, s / 2), 0])
    # growling jaw chatter
    a.expr("jaw", "rotation", [wave(3, s * 3, 0, 8), 0, 0])
    for b, sg in (("leg_front_left", 1), ("leg_front_right", -1)):
        a.expr(b, "rotation", [wave(2, s, 0, -16), 0, 8 * sg])
    for b, sg in (("leg_back_left", 1), ("leg_back_right", -1)):
        a.expr(b, "rotation", [wave(2, s, 180, 10), 0, 4 * sg])
    a.expr("collar", "rotation", [wave(1.5, s, -60, -3), 0, 0])
    a.expr("torso", "scale", [swave(0.02, s), swave(0.03, s), 1])
    _tail(a, 300, 6, amp_x=3, base=-14)
    return a


def ground_walk():
    a = Anim("ground_walk", loop=True)
    s = 420
    a.expr("body", "position", [0, awave(0.5, s, 0), 0])
    a.expr("body", "rotation", [wave(1.2, s * 2, 60), wave(1.5, s), wave(2, s)])
    a.expr("neck", "rotation", [wave(2.5, s * 2, -60, 2), wave(-2, s, -40), 0])
    a.expr("head", "rotation", [wave(1.5, s * 2, -100), 0, wave(-2, s, -60)])
    a.expr("jaw", "rotation", [wave(3, s * 2, -30, 3), 0, 0])
    pairs = (("leg_front_left", 0), ("leg_back_right", 0), ("leg_front_right", 180), ("leg_back_left", 180))
    for b, ph in pairs:
        a.expr(b, "rotation", [wave(24, s, ph), 0, 0])
        a.expr(b, "position", [0, "math.clamp(math.sin(q.anim_time*%d%+d)*1.2,0,2)" % (s, ph - 90), 0])
    a.expr("collar", "rotation", [wave(2.5, s * 2, -90), 0, wave(2, s, -60)])
    a.expr("tombstone", "rotation", [wave(1.5, s * 2, -120), 0, wave(1.5, s, -90)])
    a.expr("torso", "scale", [1, wave(0.015, s * 2, -60, 1), 1])
    _tail(a, s, 10, amp_x=4, base=-4)
    return a


def sleep():
    """Lies flat like a grave mound, the tombstone standing over it."""
    a = Anim("sleep", loop=True)
    s = 50
    a.expr("body", "position", [0, wave(0.15, s, 0, -6.2), 0])
    a.expr("torso", "scale", [wave(0.01, s, 0, 1.06), wave(0.02, s, 0, 0.92), 1.02])
    for b in LEGS_F:
        a.expr(b, "rotation", [-82, 0, 0])
    for b in LEGS_B:
        a.expr(b, "rotation", [82, 0, 0])
    a.expr("neck", "rotation", [16, 0, 0])
    a.expr("head", "rotation", [6, 12, 0])
    a.expr("jaw", "rotation", [-8, 0, 0])
    a.expr("tombstone", "rotation", [-12, -12, 0])
    for i, b in enumerate(TAIL):
        a.expr(b, "rotation", [55 if i == 0 else 10, 0, 0])
    return a


def wag():
    a = Anim("wag", length=1.4)
    for i, b in enumerate(TAIL):
        k = 0.8 + 0.3 * i
        frames = [(0.0, [0, 0, 0])]
        t, sg = 0.05, 1
        while t < 1.1:
            frames.append((round(t, 3), [-10, 28 * k * sg, 0]))
            t += 0.1
            sg = -sg
        frames += [(1.25, [-4, 0, 0]), (1.4, [0, 0, 0])]
        a.keys(b, "rotation", frames, smooth=False)
    a.keys("torso", "rotation", [(0.0, [0, 0, 0]), (0.2, [0, 3, 0]), (0.4, [0, -3, 0]), (0.6, [0, 3, 0]),
                                (0.8, [0, -3, 0]), (1.0, [0, 2, 0]), (1.4, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.3, [-6, 0, 6]), (1.1, [-6, 0, 6]), (1.4, [0, 0, 0])])
    return a


def look():
    """Loyal guard: scans left and right."""
    a = Anim("look", length=3.2)
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.5, [-6, 28, 0]), (1.3, [-6, 28, 0]), (1.9, [-6, -28, 0]),
                               (2.7, [-6, -28, 0]), (3.2, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.6, [0, 10, 4]), (1.3, [0, 10, 4]), (2.0, [0, -10, -4]),
                               (2.7, [0, -10, -4]), (3.2, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.6, [-4, 0, 0]), (2.7, [-4, 0, 0]), (3.2, [0, 0, 0])])
    return a


def shake():
    a = Anim("shake", length=1.4)
    zs = [(0.0, 0), (0.1, 10), (0.2, -12), (0.3, 13), (0.4, -13), (0.5, 12), (0.6, -11), (0.7, 9), (0.8, -7),
          (0.9, 5), (1.0, -3), (1.15, 1), (1.4, 0)]
    a.keys("torso", "rotation", [(t, [0, 0, v * 0.5]) for t, v in zs])
    a.keys("collar", "rotation", [(min(t + 0.04, 1.4), [0, 0, -v * 0.8]) for t, v in zs])
    a.keys("neck", "rotation", [(t, [0, 0, v * 0.7]) for t, v in zs])
    a.keys("tombstone", "rotation", [(min(t + 0.05, 1.4), [0, 0, -v * 0.4]) for t, v in zs])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(min(t + 0.03 * i, 1.4), [0, v * 1.4, 0]) for t, v in zs])
    return a


def cry():
    """Mournful howl."""
    a = Anim("cry", length=2.0)
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.3, [6, 0, 0]), (0.6, [-30, 0, 0]), (1.4, [-32, 0, 0]), (1.8, [0, 0, 0])])
    a.keys("head", "rotation", [(0.0, [0, 0, 0]), (0.6, [-14, 0, 0]), (1.0, [-16, 0, 3]), (1.4, [-14, 0, -3]), (1.8, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.3, [-6, 0, 0]), (0.6, [24, 0, 0]), (1.4, [22, 0, 0]), (1.75, [0, 0, 0])])
    a.keys("tombstone", "rotation", [(0.0, [0, 0, 0]), (0.6, [-10, 0, 0]), (1.4, [-10, 0, 0]), (1.8, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.6, [-6, 0, 0]), (1.4, [-6, 0, 0]), (1.8, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.6, [0, 0.8, 0]), (1.4, [0, 0.8, 0]), (1.8, [0, 0, 0])])
    for b in LEGS_F:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.6, [6, 0, 0]), (1.4, [6, 0, 0]), (1.8, [0, 0, 0])])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.6, [-14, 0, 0]), (1.4, [-14, 0, 0]), (1.8, [0, 0, 0])])
    a.keys("torso", "scale", [(0.0, [1, 1, 1]), (0.6, [1.03, 1.05, 1.0]), (1.4, [1.03, 1.05, 1.0]), (1.8, [1, 1, 1])])
    return a


def physical():
    """Last Respects: lunging bite."""
    a = Anim("physical", length=1.2)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.3, [0, 0.5, 2.5]), (0.5, [0, 2.5, -3.0]), (0.65, [0, 1.8, -6.0]),
                               (0.85, [0, 0.8, -4.0]), (1.2, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.3, [-5, 0, 0]), (0.55, [6, 0, 0]), (0.8, [2, 0, 0]), (1.2, [0, 0, 0])])
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.3, [-14, 0, 0]), (0.55, [4, 0, 0]), (0.7, [4, 8, 0]),
                               (0.8, [4, -8, 0]), (0.9, [3, 4, 0]), (1.2, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.35, [20, 0, 0]), (0.55, [24, 0, 0]), (0.62, [-10, 0, 0]),
                              (0.9, [-10, 0, 0]), (1.2, [0, 0, 0])], smooth=False)
    for b in LEGS_F:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.5, [-32, 0, 0]), (0.7, [-10, 0, 0]), (1.0, [0, 0, 0])])
    for b in LEGS_B:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.5, [28, 0, 0]), (0.7, [10, 0, 0]), (1.0, [0, 0, 0])])
    a.keys("tombstone", "rotation", [(0.0, [0, 0, 0]), (0.5, [-8, 0, 0]), (0.7, [10, 0, 0]), (0.9, [-3, 0, 0]), (1.2, [0, 0, 0])])
    a.keys("collar", "rotation", [(0.0, [0, 0, 0]), (0.5, [-8, 0, 0]), (0.7, [8, 0, 0]), (1.0, [0, 0, 0])])
    return a


def special(name="special"):
    """Rears up and howls, then slams down with a ghostly bite."""
    a = Anim(name, length=1.6)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.45, [-16, 0, 0]), (0.75, [6, 0, 0]), (1.0, [0, 0, 0])])
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.45, [0, 2.5, 1.5]), (0.75, [0, 1.6, -1.5]), (1.1, [0, 0.4, 0]), (1.4, [0, 0, 0])])
    for b in LEGS_F:
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.45, [-40, 0, 0]), (0.75, [-6, 0, 0]), (1.0, [0, 0, 0])])
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.45, [-20, 0, 0]), (0.75, [5, 0, 0]), (1.1, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.45, [26, 0, 0]), (0.8, [22, 0, 0]), (1.2, [10, 0, 0]), (1.5, [0, 0, 0])])
    a.keys("tombstone", "rotation", [(0.0, [0, 0, 0]), (0.45, [-12, 0, 0]), (0.75, [12, 0, 0]), (1.0, [-4, 0, 0]), (1.4, [0, 0, 0])])
    a.keys("torso", "scale", [(0.0, [1, 1, 1]), (0.45, [1.04, 1.08, 1.0]), (0.75, [1.06, 0.94, 1.04]), (1.1, [1, 1, 1])])
    return a


def status():
    a = Anim("status", length=1.8)
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.3, [0, -30, 0]), (1.4, [0, -30, 0]), (1.8, [0, 0, 0])])
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.3, [-6, 28, 0]), (1.4, [-6, 28, 0]), (1.8, [0, 0, 0])])
    for i, b in enumerate(TAIL):
        frames = [(0.0, [0, 0, 0]), (0.3, [-12, 0, 0])]
        t, sg = 0.3, 1
        while t < 1.35:
            t = round(t + 0.09, 3)
            frames.append((t, [-12, 30 * (0.8 + 0.3 * i) * sg, 0]))
            sg = -sg
        frames += [(1.5, [-4, 0, 0]), (1.8, [0, 0, 0])]
        a.keys(b, "rotation", frames, smooth=False)
    a.keys("torso", "rotation", [(t, [0, 0, (4 if k % 2 else -4) if 0.3 <= t <= 1.4 else 0])
                                 for k, t in enumerate([0.0, 0.3, 0.48, 0.66, 0.84, 1.02, 1.2, 1.4, 1.8])])
    return a


def recoil():
    a = Anim("recoil", length=0.8)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.1, [0, 0.8, 2.4]), (0.35, [0, 0.2, 1.2]), (0.8, [0, 0, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.1, [-8, 0, 0]), (0.3, [4, 0, 0]), (0.5, [-1.5, 0, 0]), (0.8, [0, 0, 0])])
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.1, [-14, 0, 6]), (0.35, [6, 0, -3]), (0.8, [0, 0, 0])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.1, [16, 0, 0]), (0.45, [6, 0, 0]), (0.8, [0, 0, 0])])
    a.keys("tombstone", "rotation", [(0.0, [0, 0, 0]), (0.12, [10, 0, -6]), (0.35, [-5, 0, 3]), (0.6, [2, 0, 0]), (0.8, [0, 0, 0])])
    return a


def faint():
    """Sinks into a mound of fur, leaving the tombstone standing like a grave."""
    a = Anim("faint", length=2.6)
    a.keys("body", "position", [(0.0, [0, 0, 0]), (0.25, [0, 1.0, 0]), (0.8, [0, -5.0, 0]), (1.0, [0, -6.0, 0]), (2.6, [0, -6.2, 0])])
    a.keys("body", "rotation", [(0.0, [0, 0, 0]), (0.25, [-5, 0, 0]), (0.8, [3, 0, 4]), (2.6, [3, 0, 5])])
    for b, k in (("leg_front_left", 1), ("leg_front_right", -1)):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.8, [-70, 0, 20 * k]), (1.0, [-82, 0, 24 * k]), (2.6, [-82, 0, 24 * k])])
    for b, k in (("leg_back_left", 1), ("leg_back_right", -1)):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (0.8, [70, 0, 20 * k]), (1.0, [82, 0, 24 * k]), (2.6, [82, 0, 24 * k])])
    a.keys("neck", "rotation", [(0.0, [0, 0, 0]), (0.25, [-12, 0, 0]), (0.9, [18, 0, -6]), (2.6, [20, 0, -8])])
    a.keys("jaw", "rotation", [(0.0, [0, 0, 0]), (0.25, [18, 0, 0]), (1.0, [6, 0, 0]), (2.6, [8, 0, 0])])
    a.keys("tombstone", "rotation", [(0.0, [0, 0, 0]), (0.9, [-14, 0, 6]), (1.2, [-10, 0, 4]), (2.6, [-12, 0, 5])])
    for i, b in enumerate(TAIL):
        a.keys(b, "rotation", [(0.0, [0, 0, 0]), (1.0, [55 if i == 0 else 14, 0, 0]), (2.6, [60 if i == 0 else 16, 0, 0])])
    a.keys("torso", "scale", [(0.0, [1, 1, 1]), (1.0, [1.06, 0.92, 1.02]), (2.6, [1.07, 0.9, 1.03])])
    return a


def all_animations():
    return [ground_idle(), battle_idle(), ground_walk(), sleep(), wag(), look(), shake(), cry(), physical(),
            special(), special("spray"), status(), recoil(), faint()]


PREVIEW_ORDER = ["ground_idle", "ground_walk", "battle_idle", "sleep", "cry", "physical", "special", "status",
                 "recoil", "faint", "wag", "look", "shake"]
OVER_IDLE = ("cry", "wag", "look", "shake")
HAS_FEMALE = False


def poser(female=False):
    look_ai = "q.look('head', 0.7, 0.7, 20, -20, 30, -30)"
    quirks = ["q.bedrock_quirk('houndstone', 'wag', 10, 25, 1)",
              "q.bedrock_quirk('houndstone', 'look', 15, 40, 1)",
              "q.bedrock_quirk('houndstone', 'shake', 30, 80, 1)"]

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
    out["portraitScale"] = 1.15
    out["portraitTranslation"] = [-0.65, 0.05, 0]
    out["profileScale"] = 0.5
    out["profileTranslation"] = [0, 0.85, 0]
    out["rootBone"] = P
    out["animations"] = OrderedDict([
        ("cry", "q.bedrock_stateful('houndstone', 'cry')"),
        ("recoil", "q.bedrock_stateful('houndstone', 'recoil')"),
        ("faint", "q.bedrock_primary('houndstone', 'faint', q.curve('one'))"),
        ("physical", "q.bedrock_primary('houndstone', 'physical', q.curve('symmetrical_wide'))"),
        ("special", "q.bedrock_primary('houndstone', 'special', q.curve('symmetrical_wide'))"),
        ("spray", "q.bedrock_primary('houndstone', 'spray', q.curve('symmetrical_wide'))"),
        ("status", "q.bedrock_primary('houndstone', 'status', q.curve('symmetrical_wide'))"),
    ])
    poses = OrderedDict()
    poses["battle-standing"] = pose(["STAND"], [look_ai, "q.bedrock('houndstone', 'battle_idle')"], battle=True,
                                    q=["q.bedrock_quirk('houndstone', 'wag', 8, 20, 1)"])
    poses["standing"] = pose(["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"],
                             [look_ai, "q.bedrock('houndstone', 'ground_idle')"], battle=False)
    poses["walking"] = pose(["WALK", "SWIM"], [look_ai, "q.bedrock('houndstone', 'ground_walk')"], q=False)
    poses["sleep"] = pose(["SLEEP"], ["q.bedrock('houndstone', 'sleep')"], q=False,
                          named={"cry": "q.bedrock_stateful('dummy', 'cry')"})
    out["poses"] = poses
    return out


def resolver():
    tex = "cobblemon:textures/pokemon/0972_houndstone/"
    return OrderedDict([
        ("species", "cobblemon:houndstone"),
        ("order", 0),
        ("variations", [
            OrderedDict([("aspects", []), ("poser", "cobblemon:houndstone"), ("model", "cobblemon:houndstone.geo"),
                         ("texture", tex + "houndstone.png"), ("layers", [])]),
            OrderedDict([("aspects", ["shiny"]), ("texture", tex + "houndstone_shiny.png")]),
            OrderedDict([("aspects", ["alpha_eyes"]), ("layers", [OrderedDict([
                ("name", "alpha_eyes"), ("texture", tex + "houndstone_alpha.png"), ("emissive", True)])])]),
        ]),
    ])
