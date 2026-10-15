"""Static key poses solved with forward kinematics so paws/rump rest exactly on the ground."""
import numpy as np
from scipy.optimize import least_squares
import cg


class FK:
    def __init__(self, model):
        self.m = model
        self.parts = cg.build_java(model)

    def mats(self, ov):
        return cg.world_mats(self.parts, ov)

    def point(self, mats, bone, p):
        pv = self.m.by_name[bone].pivot
        loc = np.array([p[0] - pv[0], -(p[1] - pv[1]), p[2] - pv[2]])
        R, t = mats[bone]
        w = R @ loc + t
        return np.array([w[0], -w[1], w[2]])

    def bone_min_y(self, mats, bones):
        ys = []
        for bn in bones:
            b = self.m.by_name[bn]
            for c in b.cubes:
                o, s = c.origin, c.size
                for dx in (0, s[0]):
                    for dy in (0, s[1]):
                        for dz in (0, s[2]):
                            ys.append(self.point(mats, bn, (o[0] + dx, o[1] + dy, o[2] + dz))[1])
        return min(ys)


def sit_pose(model, body_pitch=-38.0, verbose=False):
    fk = FK(model)
    m = model

    def make(params):
        py, pz, rt, rs = params
        ov = {}
        ov["body"] = {"pos": [0, py, pz], "rot": [body_pitch, 0, 0]}
        ov["chest"] = {"rot": [-4, 0, 0]}
        ov["neck"] = {"rot": [10, 0, 0]}
        ov["head"] = {"rot": [-body_pitch - 10 + 4 + 4, 0, 0]}
        # forelegs vertical, paws flat
        for s in ("left", "right"):
            ov["leg_front_%s" % s] = {"rot": [-body_pitch - 2, 0, 0]}
            ov["leg_front_%s2" % s] = {"rot": [0, 0, 0]}
            ov["foot_front_%s" % s] = {"rot": [2, 0, 0]}
            r0 = m.by_name["leg_back_%s" % s].rotation[0]
            r1 = m.by_name["leg_back_%s2" % s].rotation[0]
            r2 = m.by_name["leg_back_%s3" % s].rotation[0]
            sx = 1 if s == "left" else -1
            # thigh forward & splayed, shank folds back, metatarsus lies flat forward, paw flat
            ov["leg_back_%s" % s] = {"rot": [rt, -14 * sx, 0]}
            ov["leg_back_%s2" % s] = {"rot": [rs, 0, 0]}
            tot = body_pitch + r0 + rt + r1 + rs
            ov["leg_back_%s3" % s] = {"rot": [-90 - tot - r2, 0, 0]}
            ov["foot_back_%s" % s] = {"rot": [90, 0, 0]}
        return ov

    def resid(params):
        ov = make(params)
        mats = fk.mats(ov)
        front = fk.bone_min_y(mats, ["foot_front_left"])
        rump = fk.bone_min_y(mats, ["body"])
        paw = fk.bone_min_y(mats, ["foot_back_left"])
        hock = fk.bone_min_y(mats, ["leg_back_left3"])
        fz = fk.point(mats, "foot_front_left", (4.5, 0, -10))[2]
        return [front * 2, (rump - 0.3), paw, (hock - 0.2), (fz + 9) * 0.3, 0.02 * params[2], 0.01 * params[3]]

    sol = least_squares(resid, [-8, -4, -40, 60], bounds=([-20, -20, -100, 0], [5, 20, 30, 170]))
    if verbose:
        print("sit solution", sol.x, "resid", np.round(resid(sol.x), 2))
    return make(sol.x), sol.x


def sit_pose2(model, verbose=False, head_pitch=4.0, thigh_world=-62.0, splay=14.0, tail_side=-1, leg_ext=3.5):
    fk = FK(model)
    m = model
    rr = lambda n: (m.by_name[n].rotation or (0, 0, 0))[0]

    def upper(b, py, pz):
        ov = {"body": {"pos": [0, py, pz], "rot": [b, 0, 0]},
              "chest": {"rot": [-4, 0, 0]}, "neck": {"rot": [12, 0, 0]}}
        ov["head"] = {"rot": [head_pitch - b + 4 - 12, 0, 0]}
        for s in ("left", "right"):
            ov["leg_front_%s" % s] = {"rot": [-b - 2, 0, 0], "pos": [0, -leg_ext, 0]}
            ov["foot_front_%s" % s] = {"rot": [2, 0, 0]}
        return ov

    # 1) body pitch & height: front paws + rump on the ground, paws under the chest
    def r1(p):
        b, py, pz = p
        mats = fk.mats(upper(b, py, pz))
        front = fk.bone_min_y(mats, ["foot_front_left"])
        rump = fk.bone_min_y(mats, ["body"])
        fz = fk.point(mats, "foot_front_left", (4.5, 0, -10))[2]
        return [front, rump - 0.4, (fz + 8) * 0.5]
    s1 = least_squares(r1, [-45, -8, -2], bounds=([-75, -25, -20], [-20, 5, 20]))
    b, py, pz = s1.x
    ov = upper(b, py, pz)

    # 2) hind legs: thigh forward, hock and paw on the ground, metatarsus flat
    def legs(ts, s, sx):
        o = {}
        rt = thigh_world - b - rr("leg_back_%s" % s)
        o["leg_back_%s" % s] = {"rot": [rt, -splay * sx, 0]}
        rs = ts - thigh_world - rr("leg_back_%s2" % s)
        o["leg_back_%s2" % s] = {"rot": [rs, 0, 0]}
        o["leg_back_%s3" % s] = {"rot": [-90 - ts - rr("leg_back_%s3" % s), 0, 0]}
        o["foot_back_%s" % s] = {"rot": [90, 0, 0]}
        return o

    def r2(p):
        ts, dy = p
        o = dict(ov)
        o.update(legs(ts, "left", 1))
        o["leg_back_left"]["pos"] = [0, dy, 0]
        mats = fk.mats(o)
        return [fk.bone_min_y(mats, ["leg_back_left3"]) - 0.1, fk.bone_min_y(mats, ["foot_back_left"]), 0.05 * dy]
    s2 = least_squares(r2, [80, 0], bounds=([0, -6], [170, 6]))
    ts, dy = s2.x
    for s, sx in (("left", 1), ("right", -1)):
        ov.update(legs(ts, s, sx))
        ov["leg_back_%s" % s]["pos"] = [0, dy, 0]

    # 3) tail lies on the ground and curls forward around the side
    names = ["tail"] + ["tail%d" % i for i in range(2, 8)]
    z0, L = 11, 5

    def tail_ov(p):
        o = dict(ov)
        for i, n in enumerate(names):
            o[n] = {"rot": [p[2 * i], p[2 * i + 1] * tail_side, 0]}
        return o

    def r3(p):
        o = tail_ov(p)
        mats = fk.mats(o)
        res = []
        pts = []
        for i, n in enumerate(names):
            e = fk.point(mats, n, (0, 20, z0 + L * (i + 1)))
            pts.append(e)
            if i >= 1:
                res.append((e[1] - 2.0) * 2.0)
        tip = pts[-1]
        res += [(tip[0] - 11.5 * tail_side) * 0.6, (tip[2] + 7.0) * 0.6]
        mid = pts[3]
        res += [(abs(mid[0]) - 11.0) * 0.3 if abs(mid[0]) < 11 else 0.0]
        res += list(0.01 * np.asarray(p))
        return res
    p0 = np.zeros(14)
    p0[0] = -20
    s3 = least_squares(r3, p0, bounds=(-np.full(14, 80), np.full(14, 80)))
    ov = tail_ov(s3.x)
    if verbose:
        print("body", np.round(s1.x, 2), "res", np.round(r1(s1.x), 2))
        print("legs", np.round(s2.x, 2), "res", np.round(r2(s2.x), 2))
        print("tail", np.round(s3.x, 1), "res", np.round(r3(s3.x)[:9], 2))
    return ov


def solve_tail(fk, ov, tip_target, ground=2.0, tail_side=-1, mid_x=11.0, start=-20):
    names = ["tail"] + ["tail%d" % i for i in range(2, 8)]
    z0, L = 11, 5

    def tail_ov(p):
        o = dict(ov)
        for i, n in enumerate(names):
            o[n] = {"rot": [p[2 * i], p[2 * i + 1] * tail_side, 0]}
        return o

    def r(p):
        mats = fk.mats(tail_ov(p))
        res = []
        pts = []
        for i, n in enumerate(names):
            e = fk.point(mats, n, (0, 20, z0 + L * (i + 1)))
            pts.append(e)
            if i >= 1:
                res.append((e[1] - ground) * 2.0)
        tip = pts[-1]
        res += [(tip[0] - tip_target[0] * tail_side) * 0.6, (tip[2] - tip_target[1]) * 0.6]
        mid = pts[3]
        res += [(abs(mid[0]) - mid_x) * 0.3 if abs(mid[0]) < mid_x else 0.0]
        res += list(0.01 * np.asarray(p))
        return res
    p0 = np.zeros(14)
    p0[0] = start
    s = least_squares(r, p0, bounds=(-np.full(14, 80), np.full(14, 80)))
    return tail_ov(s.x)


def sleep_pose(model, verbose=False):
    fk = FK(model)
    m = model
    rr = lambda n: (m.by_name[n].rotation or (0, 0, 0))[0]

    # 1) body on the ground
    def r1(p):
        mats = fk.mats({"body": {"pos": [0, p[0], 0], "rot": [2, 0, 0]}})
        return [fk.bone_min_y(mats, ["body"]) - 0.3]
    py = least_squares(r1, [-6]).x[0]
    ov = {"body": {"pos": [0, py, 0], "rot": [2, 0, 0]}}

    # 2) forelegs stretched forward, forearms flat on the ground (sphinx)
    def fl(dy, s):
        return {"leg_front_%s" % s: {"rot": [-62, 0, 0], "pos": [0, dy, 0]}, "leg_front_%s2" % s: {"rot": [-30, 0, 0]},
                "foot_front_%s" % s: {"rot": [90, 0, 0]}}

    def r2(p):
        o = dict(ov); o.update(fl(p[0], "left"))
        mats = fk.mats(o)
        return [min(fk.bone_min_y(mats, ["foot_front_left"]), fk.bone_min_y(mats, ["leg_front_left2"])) - 0.1]
    fdy = least_squares(r2, [0], bounds=([-6], [6])).x[0]
    a, b = fdy, 0
    for s in ("left", "right"):
        ov.update(fl(fdy, s))

    # 3) hind legs tucked like sitting
    thigh_world = -70.0

    def legs(ts, s, sx):
        o = {}
        o["leg_back_%s" % s] = {"rot": [thigh_world - 2 - rr("leg_back_%s" % s), -10 * sx, 0]}
        o["leg_back_%s2" % s] = {"rot": [ts - thigh_world - rr("leg_back_%s2" % s), 0, 0]}
        o["leg_back_%s3" % s] = {"rot": [-90 - ts - rr("leg_back_%s3" % s), 0, 0]}
        o["foot_back_%s" % s] = {"rot": [90, 0, 0]}
        return o

    def r3(p):
        o = dict(ov); o.update(legs(p[0], "left", 1))
        o["leg_back_left"]["pos"] = [0, p[1], 0]
        mats = fk.mats(o)
        return [fk.bone_min_y(mats, ["leg_back_left3"]) - 0.1, fk.bone_min_y(mats, ["foot_back_left"]), 0.05 * p[1]]
    ts, dy = least_squares(r3, [60, 0], bounds=([-20, -6], [170, 8])).x
    for s, sx in (("left", 1), ("right", -1)):
        ov.update(legs(ts, s, sx))
        ov["leg_back_%s" % s]["pos"] = [0, dy, 0]

    # 4) head resting low on the paws, beard laid forward
    def head(n):
        return {"neck": {"rot": [n, 0, 0]}, "head": {"rot": [12 - n - 2, 0, 0]},
                "beard": {"rot": [-70, 0, 0]}, "beard2": {"rot": [-12, 0, 0]}, "beard3": {"rot": [-8, 0, 0]},
                "eyelid_left": {"scale": [1, 3, 1]}, "eyelid_right": {"scale": [1, 3, 1]}}

    def r4(p):
        o = dict(ov); o.update(head(p[0]))
        mats = fk.mats(o)
        return [fk.bone_min_y(mats, ["head"]) - 4.5]
    n = least_squares(r4, [20], bounds=([-10], [80])).x[0]
    ov.update(head(n))
    ov = solve_tail(fk, ov, (12.0, -10.0), ground=2.0, tail_side=-1, start=-30)
    if verbose:
        print("sleep body", py, "forelegs", a, b, "hind", ts, dy, "neck", n)
    return ov
