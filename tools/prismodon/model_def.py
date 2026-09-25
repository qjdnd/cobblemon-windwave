"""Geometry of Prismodon (working name) - the scrapped steel/rock sauropod.

Bedrock coordinates: +Y up, -Z forward (head), +X = the Pokemon's left.
Ground is y = 0. 1 unit = 1 texel (box UV), atlas 256 x 256.
"""

import math

from bedrock import Model, bar_between, mirror_origin, shift_subtree

NAME = "prismodon"
NECK_LIFT = 2.5   # extra neck length (head subtree is authored at the base height)


def rhombus(base, angle_deg, length, width, side_at=0.36):
    """Kite/rhombus in the sagittal plane.  Returns (B, F, T, K) as (z, y).

    base: bottom vertex; the long axis leans back (towards +Z) by angle_deg
    from vertical.  F = front corner, K = rear corner.
    """
    a = math.radians(angle_deg)
    ax, ay = math.sin(a), math.cos(a)          # axis direction (z, y)
    px, py = -math.cos(a), math.sin(a)         # perpendicular, pointing forward/up
    bz, by = base
    T = (bz + ax * length, by + ay * length)
    mz, my = bz + ax * length * side_at, by + ay * length * side_at
    F = (mz + px * width / 2, my + py * width / 2)
    K = (mz - px * width / 2, my - py * width / 2)
    return (bz, by), F, T, K


def add_plate(m, name, parent, base, angle, length, width, spike=True):
    """A stegosaur-like diamond plate: steel frame + purple glass pane + orange spike."""
    B, F, T, K = rhombus(base, angle, length, width)
    bone = m.bone(name, parent, pivot=(0, B[1], B[0]))
    zs = [p[0] for p in (B, F, T, K)]
    ys = [p[1] for p in (B, F, T, K)]
    z0, y0 = math.floor(min(zs)), math.floor(min(ys))
    dz, dy = math.ceil(max(zs)) - z0, math.ceil(max(ys)) - y0
    bone.cube((0, y0, z0), (0, dy, dz), "glass", occluder=False,
              params={"poly": [B, F, T, K], "axis": (B, T)})
    for p0, p1 in ((B, F), (F, T), (T, K), (K, B)):
        bar_between(bone, p0, p1, width=1, thick=2, mat="steel", inflate=0.2, extend=0.3,
                    params={"frame": True})
    if spike:
        # orange spike rising from the back through the lower part of the pane
        a = math.radians(angle)
        sz, sy = B[0] + math.sin(a) * length * 0.13, B[1] + math.cos(a) * length * 0.13
        ang = -angle
        bone.cube((-1, sy, sz - 1), (2, 2, 2), "orange", inflate=-0.15,
                  pivot=(0, sy, sz), rotation=(ang, 0, 0), params={"spike": 0})
        bone.cube((-0.5, sy + 1.6, sz - 0.5), (1, 2, 1), "orange", inflate=0.05,
                  pivot=(0, sy, sz), rotation=(ang, 0, 0), params={"spike": 1})
        bone.cube((-0.5, sy + 3.2, sz - 0.5), (1, 1, 1), "orange", inflate=-0.2,
                  pivot=(0, sy, sz), rotation=(ang, 0, 0), params={"spike": 2})
    return bone, (B, F, T, K)


def leg(m, side, front):
    """side: +1 = left (+X), -1 = right. front: True for fore legs."""
    sname = "left" if side > 0 else "right"
    pname = "front" if front else "back"
    zc = -7.5 if front else 9.0
    xc = 8.0 * side

    def X(origin, size):
        """Author left side; mirror for right."""
        return origin if side > 0 else mirror_origin(origin, size)

    up = m.bone(f"leg_{pname}_{sname}", "body", pivot=(xc, 15, zc))
    if front:
        o, s = (4.5, 5, zc - 3.5), (7, 11, 7)
        up.cube(X(o, s), s, "skin", params={"part": "leg"})
        for y in (11.0, 6.6):
            o, s = (4, y, zc - 4), (8, 4, 8)
            up.cube(X(o, s), s, "steel", inflate=0.15, params={"band": True})
    else:
        o, s = (4, 5, zc - 4), (8, 11, 8)
        up.cube(X(o, s), s, "skin", params={"part": "leg"})
        o, s = (3.5, 7, zc - 4.5), (9, 7, 9)
        up.cube(X(o, s), s, "steel", inflate=0.15, params={"band": True, "ridge": True})

    low = m.bone(f"leg_{pname}_{sname}2", up, pivot=(xc, 5.5, zc))
    o, s = (4.5, 1.5, zc - 3.5), (7, 5, 7)
    low.cube(X(o, s), s, "skin", params={"part": "shin"})

    foot = m.bone(f"foot_{pname}_{sname}", low, pivot=(xc, 1.5, zc))
    o, s = (4, 0, zc - 4.5), (8, 2, 8)
    foot.cube(X(o, s), s, "skin", inflate=0.1, params={"part": "foot"})
    claw_x = (5.0, 7.0, 9.0, 11.0)
    zf = zc - 4.5
    for i, cx in enumerate(claw_x):
        splay = (i - 1.5) * 9
        rot = (24, -splay * side, 0)
        o, s = (cx - 1, 0.6, zf - 1.8), (2, 2, 2)
        foot.cube(X(o, s), s, "claw", inflate=0.05, pivot=(cx * side, 2.0, zf),
                  rotation=rot, params={"claw": 0})
        o, s = (cx - 0.5, 0.45, zf - 3.3), (1, 1, 2)
        foot.cube(X(o, s), s, "claw", inflate=0.12, pivot=(cx * side, 2.0, zf),
                  rotation=rot, params={"claw": 1})
    return up, low, foot


def build() -> Model:
    m = Model(NAME, 256, 256)

    root = m.bone(NAME, None, (0, 0, 0))
    m.bone("locator_root", root, (0, 0, 0), locators={"root": (0, 0, 0)})
    m.bone("locator_top", root, (0, 57.5, -15), locators={"top": (0, 57.5, -15)})

    body = m.bone("body", root, (0, 15, 0))
    m.bone("locator_target", body, (0, 22, -26), locators={"target": (0, 22, -26)})
    m.bone("locator_middle", body, (0, 17, 0), locators={"middle": (0, 17, 0)})

    torso = m.bone("torso", body, (0, 15, 1), rotation=(-3, 0, 0))
    torso.cube((-8.5, 8, -14), (17, 13, 29), "skin", params={"part": "body"})
    torso.cube((-9.5, 10, -12), (19, 9, 25), "skin", params={"part": "body"})
    torso.cube((-7, 21, -12), (14, 2, 25), "skin", params={"part": "body"})
    torso.cube((-7.5, 9.5, -16), (15, 10, 2), "skin", params={"part": "chest", "hex": True})
    torso.cube((-7.5, 9.5, 15), (15, 10, 2), "skin", params={"part": "body"})
    torso.cube((-7, 7, -12), (14, 1, 24), "belly", params={})
    torso.cube((-4, 22.6, -11), (8, 1, 21), "steel", inflate=0.15, params={"dorsal": True})
    # big pauldron-like plates on the front corners of the chest
    for side in (1, -1):
        o, s = (7.2, 7.5, -19), (2, 12, 9)
        torso.cube(o if side > 0 else mirror_origin(o, s), s, "steel", inflate=0.1,
                   pivot=(8.2 * side, 13, -14.5), rotation=(-6, 44 * side, 0), params={"shoulder": True})
        o, s = (7.2, 19.3, -18), (2, 2, 7)
        torso.cube(o if side > 0 else mirror_origin(o, s), s, "steel", inflate=0.1,
                   pivot=(8.2 * side, 13, -14.5), rotation=(-6, 44 * side, 0), params={"shoulder": True, "cap": True})

    # ------------------------------------------------------------------ neck
    neck = m.bone("neck", torso, (0, 19, -11.5), rotation=(-5, 0, 0))
    neck.cube((-5.5, 15, -17.5), (11, 10, 10), "skin", params={"part": "neck", "hex": True})
    neck2 = m.bone("neck2", neck, (0, 24.5, -12.5), rotation=(-3, 0, 0))
    neck2.cube((-4.5, 24, -16.5), (9, 7, 8), "skin", params={"part": "neck", "hex": True})
    neck3 = m.bone("neck3", neck2, (0, 30.5, -12.5), rotation=(5, 0, 0))
    neck3.cube((-3.5, 30, -15.5), (7, 6, 6), "skin", params={"part": "neck", "hex": True})

    # ------------------------------------------------------------------ head
    head = m.bone("head", neck3, (0, 34, -13))
    head.cube((-3.5, 33.5, -21), (7, 4, 10), "skin", params={"part": "skull"})
    head.cube((-3.5, 32.5, -11.5), (7, 5, 3), "skin", params={"part": "nape"})
    head.cube((-2.5, 32.6, -22), (5, 1, 9), "mouth", params={})
    # knight-like helm; the eyes sit in dark sockets on its sides
    head.cube((-4, 36.5, -22), (8, 7, 12), "steel", inflate=0.1, params={"helmet": True, "socket": True})
    head.cube((-3, 43.5, -20.5), (6, 1, 10), "steel", params={"helmet": True, "crown": True})
    head.cube((-3.5, 36, -11.5), (7, 6, 2), "steel", inflate=0.12, params={"helmet": True, "rear": True})
    # hooked beak / nose guard flowing down from the helm
    head.cube((-3.5, 40.5, -24.5), (7, 3, 3), "steel", inflate=0.06, pivot=(0, 43.5, -22),
              rotation=(28, 0, 0), params={"beak": 0, "bridge": True})
    head.cube((-3.5, 35.5, -24.5), (7, 6, 3), "steel", inflate=0.08, pivot=(0, 41.5, -22),
              rotation=(10, 0, 0), params={"beak": 0})
    head.cube((-2.5, 33.6, -26.4), (5, 5, 2), "steel", inflate=0.1, pivot=(0, 41.5, -22),
              rotation=(17, 0, 0), params={"beak": 1})
    head.cube((-1.5, 32.6, -27.4), (3, 3, 2), "steel", inflate=0.1, pivot=(0, 41.5, -22),
              rotation=(24, 0, 0), params={"beak": 2})
    for side in (1, -1):
        o, s = (3.6, 32.5, -13.8), (1, 5, 3)
        head.cube(o if side > 0 else mirror_origin(o, s), s, "steel", inflate=0.08,
                  params={"cheek": True})
    m.bone("locator_head", head, (0, 41, -17), locators={"head": (0, 41, -17)})
    m.bone("locator_face", head, (0, 37, -27), locators={"face": (0, 37, -27)})
    m.bone("locator_item_hat", head, (0, 45, -14), locators={"item_hat": (0, 45, -14)})
    m.bone("locator_item_face", head, (0, 37, -26), locators={"item_face": (0, 37, -26)})
    m.bone("locator_physical", head, (0, 38, -28), locators={"physical": (0, 38, -28)})
    m.bone("locator_special", head, (0, 32.5, -25), locators={"special": (0, 32.5, -25)})
    m.bone("locator_mouth", head, (0, 32.5, -23), locators={"mouth": (0, 32.5, -23)})

    jaw = m.bone("jaw", head, (0, 33, -11.5), rotation=(3, 0, 0))
    jaw.cube((-2.5, 31, -22.5), (5, 2, 11), "steel", params={"jaw": True})
    jaw.cube((-1.5, 30.2, -22), (3, 1, 4), "steel", inflate=-0.05, params={"jaw": True, "chin": True})

    eyes = m.bone("eyes", head, (0, 39, -16.5))
    for side, sname in ((1, "left"), (-1, "right")):
        e = m.bone(f"eye_{sname}", eyes, (4.13 * side, 39, -16.5))
        e.cube((4.13 * side, 37.5, -19), (0, 3, 5), "eye", occluder=False, params={"side": side})
        m.bone(f"locator_eye_{sname}", e, (4.2 * side, 39, -17.5),
               locators={("eye2" if side > 0 else "eye1"): (4.2 * side, 39, -17.5)})
        lid = m.bone(f"eyelid_{sname}", eyes, (4.05 * side, 39, -16.5))
        lid.cube((4.05 * side, 37.5, -19), (0, 3, 5), "eyelid", occluder=False, params={"side": side})

    crest = m.bone("crest", head, (0, 44.5, -16))
    F, A, K = (-20.3, 44.3), (-18.9, 54.6), (-11.8, 44.3)
    crest.cube((0, 43.5, -21), (0, 12, 10), "glass", occluder=False,
               params={"poly": [F, A, K], "axis": ((-16.3, 44.3), A), "crest": True})
    bar_between(crest, F, A, width=1, thick=2, mat="steel", inflate=0.2, extend=0.3, params={"frame": True})
    bar_between(crest, K, A, width=1, thick=2, mat="steel", inflate=0.2, extend=0.3, params={"frame": True})
    for i in range(8):
        t = (i + 0.55) / 8.6
        z = F[0] + t * (A[0] - F[0])
        y = F[1] + t * (A[1] - F[1])
        crest.cube((-0.5, y - 0.5, z - 1.3), (1, 1, 1), "steel", inflate=0.12 - 0.015 * i,
                   pivot=(0, y, z - 0.8), rotation=(45, 0, 0), params={"serration": True})
    crest.cube((-1, 44.2, -17.4), (2, 2, 2), "orange", inflate=-0.15, params={"spike": 0})
    crest.cube((-0.5, 46.0, -16.9), (1, 2, 1), "orange", inflate=0.08, params={"spike": 1})
    crest.cube((-0.5, 47.8, -16.9), (1, 1, 1), "orange", inflate=-0.18, params={"spike": 2})

    shift_subtree(m, head, NECK_LIFT)

    # ---------------------------------------------------------------- back plates
    plates = m.bone("back_plates", torso, (0, 23, 0))
    fin = m.bone("back_fin", plates, (0, 23, -6))
    for o, s_, infl in (((-0.5, 22.5, -7.5), (1, 7, 3), 0.3), ((-0.5, 29.2, -7.0), (1, 4, 2), 0.25),
                        ((-0.5, 33.0, -6.5), (1, 2, 1), 0.2)):
        fin.cube(o, s_, "steel", inflate=infl, pivot=(0, 23, -6), rotation=(-14, 0, 0), params={"fin": True})
    add_plate(m, "back_plate_front", plates, base=(-4.0, 22.6), angle=40, length=20.5, width=7.2)
    add_plate(m, "back_plate_rear", plates, base=(6.0, 22.2), angle=45, length=17.5, width=6.2)

    # ---------------------------------------------------------------- tail
    tail = m.bone("tail", torso, (0, 16, 15.5), rotation=(8, 0, 0))
    tail.cube((-4.5, 12, 15), (9, 8, 5), "skin", params={"part": "tailbase"})
    m.bone("locator_tail", tail, (0, 16, 25), locators={"tail": (0, 16, 25)})
    tail2 = m.bone("tail2", tail, (0, 16, 19.5), rotation=(5, 0, 0))
    tail2.cube((-3.5, 13, 19), (7, 6, 6), "steel", inflate=0.1, params={"tailcone": 0})
    tail3 = m.bone("tail3", tail2, (0, 16, 24.5), rotation=(4, 0, 0))
    tail3.cube((-2.5, 14, 24.5), (5, 4, 6), "steel", inflate=0.1, params={"tailcone": 1})
    tail4 = m.bone("tail4", tail3, (0, 16, 30), rotation=(4, 0, 0))
    tail4.cube((-1.5, 14.5, 30), (3, 3, 5), "steel", inflate=0.1, params={"tailcone": 2})
    tail4.cube((-1, 15, 34.5), (2, 2, 3), "steel", params={"tailcone": 3})
    tail4.cube((-0.5, 15.5, 37), (1, 1, 2), "steel", inflate=-0.05, params={"tailcone": 4})
    m.bone("locator_tail_tip", tail4, (0, 16, 38), locators={"tail_tip": (0, 16, 38)})

    # ---------------------------------------------------------------- legs
    for front in (True, False):
        for side in (1, -1):
            leg(m, side, front)
    for bone_name, loc, pos in (
        ("foot_front_right", "foot_primary", (-8, 0, -11)),
        ("foot_front_left", "foot_secondary1", (8, 0, -11)),
        ("foot_back_right", "foot_secondary2", (-8, 0, 5)),
        ("foot_back_left", "foot_secondary3", (8, 0, 5)),
    ):
        m.bone(f"locator_{loc}", bone_name, pos, locators={loc: pos})

    return m


if __name__ == "__main__":
    mdl = build()
    print(len(mdl.bones), "bones", sum(1 for _ in mdl.cubes()), "cubes")
    print("atlas used height:", mdl.pack_uv())
