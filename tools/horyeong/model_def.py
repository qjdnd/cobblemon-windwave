"""
Horyeong geometry definition (Bedrock file space: +Y up, front = -Z, creature-left = +X).
Rest pose = standing on all fours. Sitting (as in the concept art) is the idle animation.
"""
import numpy as np
from cg import Model
import cg

NAME = "horyeong"


class Sym:
    """Builds a left (+X) part and its mirrored right (-X) twin."""
    def __init__(self, model):
        self.m = model

    def bone(self, name, parent, pivot, rotation=None, locators=None):
        out = []
        for side, sx in (("left", 1), ("right", -1)):
            rot = None
            if rotation:
                rot = [rotation[0], rotation[1] * sx, rotation[2] * sx]
            locs = None
            if locators:
                locs = {k.format(s=side, n=("2" if side == "left" else "1")): [v[0] * sx, v[1], v[2]]
                        for k, v in locators.items()}
            b = self.m.bone(name.format(s=side), parent.format(s=side) if parent else None,
                            [pivot[0] * sx, pivot[1], pivot[2]], rot, locs)
            out.append((b, sx))
        return out

    def cube(self, bones, origin, size, tag="fur", pivot=None, rotation=None, inflate=0.0, meta=None):
        for b, sx in bones:
            o = list(origin)
            if sx < 0:
                o[0] = -(origin[0] + size[0])
            pv = rt = None
            if pivot is not None:
                pv = [pivot[0] * sx, pivot[1], pivot[2]]
                rt = [rotation[0], rotation[1] * sx, rotation[2] * sx]
            md = dict(meta or {})
            md["side"] = sx
            b.cube(o, size, tag, pivot=pv, rotation=rt, inflate=inflate, meta=md)


def shift_chain(m, names, dy):
    for n in names:
        b = m.by_name[n]
        b.pivot[1] += dy
        for c in b.cubes:
            c.origin[1] += dy
            if c.pivot is not None:
                c.pivot[1] += dy
        for k in b.locators:
            b.locators[k][1] += dy


def chain_min_y(m, names):
    parts = cg.build_java(m)
    mats = cg.world_mats(parts)
    ys = []
    for q in cg.collect_quads(m, parts, mats):
        if q["cube"].bone in names:
            ys += [-v[1] for v in q["verts"]]
    return min(ys)


def build():
    m = Model("geometry." + NAME, 256, 256)
    S = Sym(m)

    m.bone(NAME, None, (0, 0, 0))
    m.bone("locator_root", NAME, (0, 0, 0), locators={"root": [0, 0, 0]})
    m.bone("locator_top", NAME, (0, 40, 0), locators={"top": [0, 40, 0]})

    # ---------------------------------------------------------------- body
    body = m.bone("body", NAME, (0, 15, 6))
    body.cube((-8, 9, -10), (16, 15, 17), "torso")             # main barrel
    body.cube((-7, 24, -9), (14, 1, 16), "torso")              # back rounding
    body.cube((-7, 7, -8), (14, 2, 14), "belly")               # sagging old belly
    body.cube((-7.5, 10, 7), (15, 13, 4), "torso")             # rump
    body.cube((-6.5, 11, 11), (13, 10, 1), "torso")            # rump rounding
    body.cube((-6, 23, 7), (12, 1, 4), "torso")                # rump top rounding
    body.cube((-8.5, 12, -7), (1, 9, 12), "flank")             # flank bulge R
    body.cube((7.5, 12, -7), (1, 9, 12), "flank")              # flank bulge L
    m.bone("locator_middle", "body", (0, 16, -1), locators={"middle": [0, 16, -1]})
    m.bone("locator_target", "body", (0, 26, -24), locators={"target": [0, 26, -24]})

    chest = m.bone("chest", "body", (0, 16, -10))
    chest.cube((-8, 8, -14), (16, 15, 4), "chest")
    chest.cube((-6.5, 23, -13), (13, 1, 3), "torso")
    chest.cube((-6, 5, -14.5), (12, 5, 0), "fluff", meta={"shape": "chest_tuft"})

    neck = m.bone("neck", "chest", (0, 21, -12))
    neck.cube((-6.5, 16, -17), (13, 10, 6), "neck")

    # ---------------------------------------------------------------- head
    head = m.bone("head", "neck", (0, 25, -16))
    head.cube((-8, 22, -26), (16, 12, 10), "skull")
    head.cube((-7, 34, -25), (14, 1, 8), "skull")                # crown rounding
    head.cube((-6.5, 31, -27), (13, 3, 1), "skull")              # brow ridge / forehead
    head.cube((-9, 21, -25), (18, 6, 7), "cheek")                # puffy white cheeks
    head.cube((-3.5, 21, -29), (7, 5, 3), "muzzle")
    head.cube((-2, 26, -28), (4, 2, 2), "bridge")
    head.cube((-1.5, 24.5, -30), (3, 2, 1), "nose")
    m.bone("locator_head", "head", (0, 35, -20), locators={"head": [0, 35, -20]})
    m.bone("locator_face", "head", (0, 27, -30), locators={"face": [0, 27, -30]})
    m.bone("locator_mouth", "head", (0, 22, -29),
           locators={"mouth": [0, 22, -29], "special": [0, 22, -29], "physical": [0, 22, -29]})
    m.bone("locator_item_hat", "head", (0, 35, -20), locators={"item_hat": [0, 35, -20]})

    jaw = m.bone("jaw", "head", (0, 21, -21))
    jaw.cube((-3, 19, -28), (6, 2, 7), "jaw")

    # eyes (planes) + heavy half-closed eyelids; locators drive the alpha eye glow
    eyes = S.bone("eye_{s}", "head", (3.5, 29, -26.05), locators={"eye{n}": [3.5, 29, -26.3]})
    S.cube(eyes, (1.5, 27.5, -26.05), (4, 3, 0), "eye")
    lids = S.bone("eyelid_{s}", "head", (3.5, 30.5, -26.15))
    S.cube(lids, (1.5, 29.5, -26.15), (4, 1, 0), "eyelid")

    # bushy brows: thick over the eye, then drooping long tufts past the temples
    brow = S.bone("brow_{s}", "head", (1, 31.5, -27), rotation=(0, 0, -10))
    S.cube(brow, (1, 30.5, -28.5), (5, 2, 2), "white", meta={"hair": "h"})
    S.cube(brow, (0.5, 31, -28.6), (6, 3, 0), "fluff_white", meta={"shape": "brow_top"})
    brow2 = S.bone("brow_{s}2", "brow_{s}", (6, 31.5, -27.5), rotation=(0, -20, 28))
    S.cube(brow2, (5.5, 30.5, -28.5), (4, 2, 2), "white", meta={"hair": "h"})
    brow3 = S.bone("brow_{s}3", "brow_{s}2", (9.5, 31.5, -27.5), rotation=(0, -15, 14))
    S.cube(brow3, (9, 27, -27.5), (8, 6, 0), "fluff_white", meta={"shape": "brow_tip"})

    # ears
    ear = S.bone("ear_{s}", "head", (5.5, 33, -20), rotation=(-5, -10, -14))
    S.cube(ear, (3, 33, -21), (5, 4, 2), "ear")
    S.cube(ear, (4, 37, -21), (3, 1, 2), "ear")
    S.cube(ear, (3.5, 33.5, -21.3), (4, 4, 0), "fluff_white", meta={"shape": "ear_tuft"})

    # cheek ruff / sideburns
    cheek = S.bone("cheek_{s}", "head", (8.5, 25, -21))
    S.cube(cheek, (8, 19, -24), (2, 7, 4), "white", meta={"hair": "v"})
    cheek2 = S.bone("cheek_{s}2", "cheek_{s}", (10, 24, -21.5), rotation=(0, -15, 30))
    S.cube(cheek2, (10, 15, -23.5), (7, 10, 0), "fluff_white", meta={"shape": "cheek_tuft"})
    S.cube(cheek2, (10, 16, -20.5), (6, 9, 0), "fluff_white", meta={"shape": "cheek_tuft"})

    # mustache (3 locks + pointed tip)
    mus = S.bone("mustache_{s}", "head", (0.5, 23, -29.5), rotation=(0, 0, 8))
    S.cube(mus, (0, 21, -31), (6, 3, 3), "white", meta={"hair": "h"})
    mus2 = S.bone("mustache_{s}2", "mustache_{s}", (6, 22.5, -29.5), rotation=(0, -18, 20))
    S.cube(mus2, (5.5, 20.5, -30.5), (5, 3, 2), "white", meta={"hair": "h"})
    mus3 = S.bone("mustache_{s}3", "mustache_{s}2", (10.5, 22, -29.5), rotation=(0, -8, 26))
    S.cube(mus3, (10, 20.5, -30), (5, 2, 1), "white", meta={"hair": "h"})
    mus4 = S.bone("mustache_{s}4", "mustache_{s}3", (15, 21.5, -29.5), rotation=(0, 0, -22))
    S.cube(mus4, (14.5, 18.5, -29.5), (5, 5, 0), "fluff_white", meta={"shape": "mustache_tip"})

    # beard hangs from the jaw
    beard = m.bone("beard", "jaw", (0, 20, -26))
    beard.cube((-4, 14, -28), (8, 6, 3), "white", meta={"hair": "v"})
    beard.cube((-5.5, 12, -26.5), (11, 8, 0), "fluff_white", meta={"shape": "beard_side"})
    beard2 = m.bone("beard2", "beard", (0, 14, -26.5))
    beard2.cube((-3, 9, -28), (6, 5, 3), "white", meta={"hair": "v"})
    beard3 = m.bone("beard3", "beard2", (0, 9, -27))
    beard3.cube((-2, 5, -27.5), (4, 4, 2), "white", meta={"hair": "v"})
    beard3.cube((-3, 1, -26.5), (6, 6, 0), "fluff_white", meta={"shape": "beard_tip"})

    # ---------------------------------------------------------------- front legs
    fl = S.bone("leg_front_{s}", "body", (4.5, 17, -8))
    S.cube(fl, (1, 8, -11.5), (7, 10, 7), "leg")
    fl2 = S.bone("leg_front_{s}2", "leg_front_{s}", (4.5, 9, -8))
    S.cube(fl2, (1.5, 2, -11), (6, 7, 6), "leg")
    pawf = S.bone("foot_front_{s}", "leg_front_{s}2", (4.5, 2, -8))
    S.cube(pawf, (1, 0, -13), (7, 3, 7), "paw")
    for x in (1.5, 3.5, 5.5):
        S.cube(pawf, (x, 0, -14), (2, 2, 1), "toe")
    m.bone("locator_foot_primary2", "foot_front_left", (4.5, 0, -10), locators={"foot_primary2": [4.5, 0, -10]})
    m.bone("locator_foot_primary1", "foot_front_right", (-4.5, 0, -10), locators={"foot_primary1": [-4.5, 0, -10]})

    # ---------------------------------------------------------------- back legs
    bl = S.bone("leg_back_{s}", "body", (5, 18, 4), rotation=(-16, 0, 0))
    S.cube(bl, (1, 9, -1), (8, 12, 11), "thigh")
    bl2 = S.bone("leg_back_{s}2", "leg_back_{s}", (5, 9, 5), rotation=(46, 0, 0))
    S.cube(bl2, (2.5, 3, 3), (5, 7, 5), "leg")
    bl3 = S.bone("leg_back_{s}3", "leg_back_{s}2", (5, 4, 5.5), rotation=(-30, 0, 0))
    S.cube(bl3, (2.5, -2, 3.5), (5, 7, 4), "leg")
    pawb = S.bone("foot_back_{s}", "leg_back_{s}3", (5, -1.5, 5.5))
    S.cube(pawb, (1.5, -4, 0.5), (7, 3, 7), "paw")
    for x in (2, 4, 6):
        S.cube(pawb, (x, -4, -0.5), (2, 2, 1), "toe")
    m.bone("locator_foot_secondary2", "foot_back_left", (5, -4, 3), locators={"foot_secondary2": [5, -4, 3]})
    m.bone("locator_foot_secondary1", "foot_back_right", (-5, -4, 3), locators={"foot_secondary1": [-5, -4, 3]})

    # ---------------------------------------------------------------- tail
    tail_rot = [(-30, 0, 0), (-12, 0, 0), (-4, 0, 0), (6, 0, 0), (12, 0, 0), (14, 0, 0), (12, 0, 0)]
    sizes = [4, 4, 4, 4, 3, 3, 3]
    seg_len = 5
    z0 = 11
    parent = "body"
    for i in range(7):
        name = "tail" if i == 0 else "tail%d" % (i + 1)
        t = m.bone(name, parent, (0, 20, z0 + seg_len * i), rotation=tail_rot[i])
        s = sizes[i]
        start = z0 + seg_len * i - (1 if i > 0 else 0)
        t.cube((-s / 2, 20 - s / 2, start), (s, s, seg_len + (1 if i > 0 else 0)), "tail",
               inflate=(0.08 if i % 2 else 0.0), meta={"seg": i})
        parent = name
    m.bone("locator_tail_tip", parent, (0, 20, z0 + seg_len * 7), locators={"tail_tip": [0, 20, z0 + seg_len * 7]})

    # ---------------------------------------------------------------- ground the legs
    for side in ("left", "right"):
        back = ["leg_back_%s" % side, "leg_back_%s2" % side, "leg_back_%s3" % side, "foot_back_%s" % side,
                "locator_foot_secondary%s" % ("2" if side == "left" else "1")]
        dy = round(-chain_min_y(m, back[:4]) * 4) / 4
        shift_chain(m, back, dy)
        front = ["leg_front_%s" % side, "leg_front_%s2" % side, "foot_front_%s" % side]
        dy = round(-chain_min_y(m, front) * 4) / 4
        shift_chain(m, front, dy)
    return m
