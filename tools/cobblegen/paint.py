"""3D texture painting for box-UV models.

Every texel of every cube face is mapped back to its rest-pose position on the
model (Bedrock space, pixels) so that shading and markings can be described
as functions of 3D space. The result is quantised onto hand-picked colour
ramps with light dithering to keep the pixel-art look of Cobblemon textures.
"""
import math
import numpy as np

from . import rig


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def ramp(*hexes):
    return np.stack([hex_rgb(h) for h in hexes])


class FaceSample:
    """Texel samples of one cube face."""

    def __init__(self, cube, bone, face, ui, vi, pos, normal, s, t):
        self.cube = cube
        self.bone = bone
        self.face = face          # up/down/front/back/left/right (Bedrock semantic)
        self.ui = ui              # texel x indices (N,)
        self.vi = vi              # texel y indices (N,)
        self.pos = pos            # (N,3) Bedrock-space rest positions (pixels)
        self.normal = normal      # (3,) Bedrock-space normal
        self.s = s                # (N,) 0..1 across the face (u direction)
        self.t = t                # (N,) 0..1 across the face (v direction)
        self.tag = cube.tag


def face_samples(model):
    """Yield FaceSample for each face of every UV-owning cube in rest pose."""
    parts = rig.build_rig(model)
    mats = rig.pose_matrices(parts)
    out = []
    for p in parts:
        if not p.boxes:
            continue
        M = mats[id(p)]
        R = M[:3, :3]
        for b in p.boxes:
            if b.cube.share is not None:
                continue
            for verts, uvs, nrm, name in rig._cube_polys(b):
                vs = np.array(verts, dtype=float)
                vw = (M @ np.c_[vs, np.ones(4)].T).T[:, :3]
                vb = rig.j_to_bedrock(vw)
                (u2, v1), (u1, _), (_, v2), _ = uvs if not b.mirror else uvs[::-1]
                umin, umax = sorted((u1, u2))
                vmin, vmax = sorted((v1, v2))
                iu = np.arange(int(math.floor(umin + 1e-6)), int(math.ceil(umax - 1e-6)))
                iv = np.arange(int(math.floor(vmin + 1e-6)), int(math.ceil(vmax - 1e-6)))
                if len(iu) == 0 or len(iv) == 0:
                    continue
                UU, VV = np.meshgrid(iu, iv)
                uc = UU.ravel() + 0.5
                vc = VV.ravel() + 0.5
                # vertex order (non-mirrored): 0:(u2,v1) 1:(u1,v1) 2:(u1,v2) 3:(u2,v2)
                if b.mirror:
                    vb_o = vb[::-1]
                else:
                    vb_o = vb
                du = (u2 - u1) if abs(u2 - u1) > 1e-9 else 1.0
                dv = (v2 - v1) if abs(v2 - v1) > 1e-9 else 1.0
                s = (uc - u1) / du
                t = (vc - v1) / dv
                P = vb_o[1][None, :] + s[:, None] * (vb_o[0] - vb_o[1])[None, :] + t[:, None] * (vb_o[2] - vb_o[1])[None, :]
                n = rig.j_to_bedrock(R @ np.array(nrm, dtype=float))
                ln = np.linalg.norm(n)
                n = n / ln if ln > 0 else n
                out.append(FaceSample(b.cube, p.bone.name, name, UU.ravel(), VV.ravel(), P, n,
                                      (uc - umin) / max(umax - umin, 1e-9), (vc - vmin) / max(vmax - vmin, 1e-9)))
    return out


# ------------------------------------------------------------------ noise
def hash3(x, y, z, seed=0):
    h = (np.asarray(x, dtype=np.int64) * 374761393 + np.asarray(y, dtype=np.int64) * 668265263
         + np.asarray(z, dtype=np.int64) * 2147483647 + seed * 974711) & 0xFFFFFFFF
    h = (h ^ (h >> 13)) * 1274126177 & 0xFFFFFFFF
    h = h ^ (h >> 16)
    return (h & 0xFFFF) / 65535.0


def value_noise(p, scale, seed=0):
    q = np.asarray(p, dtype=np.float64) / scale
    i = np.floor(q).astype(np.int64)
    f = q - i
    f = f * f * (3 - 2 * f)
    acc = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                acc = acc + w * hash3(i[:, 0] + dx, i[:, 1] + dy, i[:, 2] + dz, seed)
    return acc


def fbm(p, scale, octaves=3, seed=0):
    total = 0
    amp = 1.0
    norm = 0
    for o in range(octaves):
        total = total + amp * value_noise(p, scale / (2 ** o), seed + o * 17)
        norm += amp
        amp *= 0.5
    return total / norm


BAYER4 = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.47


def shade_to_ramp(level, ramp_rgb, ui, vi, dither=0.45, jitter=None):
    """Map continuous level (0..1) to ramp colours with ordered dithering."""
    n = len(ramp_rgb)
    x = np.clip(level, 0, 1) * (n - 1)
    d = BAYER4[vi % 4, ui % 4] * dither
    if jitter is not None:
        d = d + jitter
    idx = np.clip(np.floor(x + 0.5 + d), 0, n - 1).astype(int)
    return ramp_rgb[idx]


class Canvas:
    def __init__(self, w, h):
        self.rgba = np.zeros((h, w, 4), dtype=np.float32)

    def put(self, ui, vi, rgb, alpha=255.0):
        self.rgba[vi, ui, :3] = rgb
        self.rgba[vi, ui, 3] = alpha

    def image(self):
        from PIL import Image
        return Image.fromarray(np.clip(self.rgba, 0, 255).astype(np.uint8), "RGBA")


def lambert(n, light=(-0.35, 0.8, -0.5)):
    l = np.array(light, dtype=np.float64)
    l /= np.linalg.norm(l)
    return np.clip(n @ l, -1, 1)


def ellipsoid_normal(p, center, radii):
    q = (p - np.asarray(center)) / (np.asarray(radii) ** 2)
    ln = np.linalg.norm(q, axis=1, keepdims=True)
    return q / np.maximum(ln, 1e-9)
