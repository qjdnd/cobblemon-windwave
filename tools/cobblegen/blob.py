"""Shared helpers for soft, slime-like bodies built from layered box rings."""
import math
import numpy as np


def superellipse_rings(a, bf, bb, n, count):
    """Rectangles (half-width, front z, back z) approximating a plan-view superellipse.

    a: half width (x); bf: distance to the front (-z); bb: distance to the back (+z).
    """
    rects = []
    if count == 1:
        phis = [math.radians(45)]
    else:
        lo, hi = 16.0, 74.0
        phis = [math.radians(lo + (hi - lo) * i / (count - 1)) for i in range(count)]
    for phi in phis:
        c = math.cos(phi) ** (2.0 / n)
        s = math.sin(phi) ** (2.0 / n)
        rects.append((a * c, bf * s, bb * s))
    return rects


def snap_half(v, parity_width=None):
    return round(v * 2) / 2.0


def ring_boxes(bone, y0, y1, a, bf, bb, n=2.6, count=3, tag="body", min_w=2, cx=0.0):
    """Add boxes for one horizontal layer; widths are snapped to whole pixels so
    the texture stays crisp. Returns created cubes."""
    out = []
    seen = set()
    for (hw, fz, bz) in superellipse_rings(a, bf, bb, n, count):
        w = max(min_w, int(round(hw * 2)))
        z0 = -round(fz)
        z1 = round(bz)
        d = z1 - z0
        if d <= 0:
            continue
        key = (w, z0, z1)
        if key in seen:
            continue
        seen.add(key)
        out.append(bone.add([cx - w / 2.0, y0, z0], [w, y1 - y0, d], tag=tag))
    return out


def implicit_normal(f, p, eps=0.05):
    p = np.asarray(p, dtype=np.float64)
    g = np.zeros_like(p)
    for i in range(3):
        d = np.zeros(3)
        d[i] = eps
        g[:, i] = (f(p + d) - f(p - d)) / (2 * eps)
    ln = np.linalg.norm(g, axis=1, keepdims=True)
    return g / np.maximum(ln, 1e-9)


def sphere_normal(p, center, radii=(1, 1, 1)):
    q = (np.asarray(p) - np.asarray(center)) / np.asarray(radii, dtype=np.float64) ** 2
    ln = np.linalg.norm(q, axis=1, keepdims=True)
    return q / np.maximum(ln, 1e-9)


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def front_z(model, x, y, tags=("body",)):
    """Front-most (-Z) surface of unrotated boxes with the given tags at (x, y)."""
    best = None
    for c in model.cubes():
        if c.tag not in tags:
            continue
        ox, oy, oz = c.origin
        sx, sy, sz = c.size
        if ox <= x <= ox + sx and oy <= y <= oy + sy:
            best = oz if best is None else min(best, oz)
    return best


def side_x(model, y, z, tags=("body",), sign=1):
    """Outer-most surface along +X (sign=1) or -X (sign=-1) at (y, z)."""
    best = None
    for c in model.cubes():
        if c.tag not in tags:
            continue
        ox, oy, oz = c.origin
        sx, sy, sz = c.size
        if oy <= y <= oy + sy and oz <= z <= oz + sz:
            v = ox + sx if sign > 0 else ox
            best = v if best is None else (max(best, v) if sign > 0 else min(best, v))
    return best
