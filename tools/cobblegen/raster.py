"""Tiny numpy software rasterizer used to preview models the way Minecraft
draws entities (box-UV textures, cutout alpha, backface culling and the
vanilla two-light entity shading)."""
import math
import numpy as np
from PIL import Image, ImageFilter

from . import rig

L0 = np.array([0.2, 1.0, -0.7]); L0 /= np.linalg.norm(L0)
L1 = np.array([-0.2, 1.0, 0.7]); L1 /= np.linalg.norm(L1)


def mc_light(n_world):
    a = np.maximum(0, n_world @ L0) + np.maximum(0, n_world @ L1)
    return np.minimum(1.0, a * 0.6 + 0.4)


def view_matrix(yaw_deg, pitch_deg):
    """Camera orbit. yaw rotates the model around Y (positive shows its left side)."""
    y = math.radians(yaw_deg)
    p = math.radians(pitch_deg)
    ry = np.array([[math.cos(y), 0, math.sin(y)], [0, 1, 0], [-math.sin(y), 0, math.cos(y)]])
    rx = np.array([[1, 0, 0], [0, math.cos(p), -math.sin(p)], [0, math.sin(p), math.cos(p)]])
    return rx @ ry


class Camera:
    def __init__(self, yaw=-30, pitch=18, size=(512, 512), scale=None, center=None):
        self.yaw = yaw
        self.pitch = pitch
        self.size = size
        self.scale = scale
        self.center = center
        self.R = view_matrix(yaw, pitch)

    def fit(self, pts_world, margin=0.12):
        v = pts_world @ self.R.T
        mn = v[:, :2].min(0)
        mx = v[:, :2].max(0)
        ext = (mx - mn).max()
        w, h = self.size
        self.scale = (min(w, h) * (1 - 2 * margin)) / max(ext, 1e-6)
        self.center = (mn + mx) / 2


def render(mesh, texture, cam, emissive=None, light_model_rot=None, ss=2, bg=(0, 0, 0, 0),
           world_rot=None, ground_shadow=True, extra_world=None, layers=None, clip_ground=False):
    """mesh: output of rig.build_mesh (J space). texture: RGBA uint8 array (H,W,4)."""
    W, H = cam.size
    W2, H2 = W * ss, H * ss
    quads = rig.j_to_world(mesh["quads"])
    normals = rig.j_to_world(mesh["normals"])
    if world_rot is not None:
        quads = quads @ world_rot.T
        normals = normals @ world_rot.T
    light = mc_light(normals)
    v = quads @ cam.R.T
    nv = normals @ cam.R.T
    sx = (v[..., 0] - cam.center[0]) * cam.scale * ss + W2 / 2
    sy = -(v[..., 1] - cam.center[1]) * cam.scale * ss + H2 / 2
    sz = v[..., 2]
    color = np.zeros((H2, W2, 4), dtype=np.float32)
    color[...] = np.array(bg, dtype=np.float32) / 255.0
    depth = np.full((H2, W2), -1e9, dtype=np.float32)
    tex = texture.astype(np.float32) / 255.0
    th, tw = tex.shape[:2]
    emi = emissive.astype(np.float32) / 255.0 if emissive is not None else None
    uvs = mesh["uvs"]
    for i in range(quads.shape[0]):
        if nv[i, 2] <= 1e-6:
            continue  # backface (camera looks down -Z of view space)
        for tri in ((0, 1, 2), (0, 2, 3)):
            xs = sx[i, list(tri)]
            ys = sy[i, list(tri)]
            zs = sz[i, list(tri)]
            us = uvs[i, list(tri), 0]
            vs = uvs[i, list(tri), 1]
            x0 = max(int(math.floor(xs.min())), 0)
            x1 = min(int(math.ceil(xs.max())), W2 - 1)
            y0 = max(int(math.floor(ys.min())), 0)
            y1 = min(int(math.ceil(ys.max())), H2 - 1)
            if x1 < x0 or y1 < y0:
                continue
            area = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
            if abs(area) < 1e-9:
                continue
            px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            w0 = ((xs[1] - px) * (ys[2] - py) - (xs[2] - px) * (ys[1] - py)) / area
            w1 = ((xs[2] - px) * (ys[0] - py) - (xs[0] - px) * (ys[2] - py)) / area
            w2 = 1 - w0 - w1
            inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
            if not inside.any():
                continue
            z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
            u = w0 * us[0] + w1 * us[1] + w2 * us[2]
            vv = w0 * vs[0] + w1 * vs[1] + w2 * vs[2]
            ui = np.clip(np.floor(u).astype(int), 0, tw - 1)
            vi = np.clip(np.floor(vv).astype(int), 0, th - 1)
            texel = tex[vi, ui]
            ok = inside & (texel[..., 3] > 0.1)
            if clip_ground:
                wy = quads[i, list(tri), 1]
                ok &= (w0 * wy[0] + w1 * wy[1] + w2 * wy[2]) > -0.02
            dsub = depth[y0:y1 + 1, x0:x1 + 1]
            ok &= z > dsub + 1e-5
            if not ok.any():
                continue
            rgb = texel[..., :3] * light[i]
            if emi is not None:
                e = emi[vi, ui]
                m = e[..., 3] > 0.1
                rgb = np.where(m[..., None], e[..., :3], rgb)
            csub = color[y0:y1 + 1, x0:x1 + 1]
            csub[ok, :3] = rgb[ok]
            csub[ok, 3] = 1.0
            dsub[ok] = z[ok]
    # extra resolver layers: (texture, translucent) drawn unlit after the base pass
    for ltex, translucent in (layers or []):
        lt = ltex.astype(np.float32) / 255.0
        lh, lw = lt.shape[:2]
        for i in range(quads.shape[0]):
            if nv[i, 2] <= 1e-6 and not translucent:
                continue
            for tri in ((0, 1, 2), (0, 2, 3)):
                xs = sx[i, list(tri)]
                ys = sy[i, list(tri)]
                zs = sz[i, list(tri)]
                us = uvs[i, list(tri), 0]
                vs = uvs[i, list(tri), 1]
                x0 = max(int(math.floor(xs.min())), 0)
                x1 = min(int(math.ceil(xs.max())), W2 - 1)
                y0 = max(int(math.floor(ys.min())), 0)
                y1 = min(int(math.ceil(ys.max())), H2 - 1)
                if x1 < x0 or y1 < y0:
                    continue
                area = (xs[1] - xs[0]) * (ys[2] - ys[0]) - (xs[2] - xs[0]) * (ys[1] - ys[0])
                if abs(area) < 1e-9:
                    continue
                px, py = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                w0 = ((xs[1] - px) * (ys[2] - py) - (xs[2] - px) * (ys[1] - py)) / area
                w1 = ((xs[2] - px) * (ys[0] - py) - (xs[0] - px) * (ys[2] - py)) / area
                w2 = 1 - w0 - w1
                inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
                if not inside.any():
                    continue
                z = w0 * zs[0] + w1 * zs[1] + w2 * zs[2]
                u = w0 * us[0] + w1 * us[1] + w2 * us[2]
                vv = w0 * vs[0] + w1 * vs[1] + w2 * vs[2]
                ui = np.clip(np.floor(u).astype(int), 0, lw - 1)
                vi = np.clip(np.floor(vv).astype(int), 0, lh - 1)
                tx = lt[vi, ui]
                dsub = depth[y0:y1 + 1, x0:x1 + 1]
                ok = inside & (tx[..., 3] > 0.02) & (z >= dsub - 1e-3)
                if clip_ground:
                    wy = quads[i, list(tri), 1]
                    ok &= (w0 * wy[0] + w1 * wy[1] + w2 * wy[2]) > -0.02
                if not ok.any():
                    continue
                csub = color[y0:y1 + 1, x0:x1 + 1]
                a = tx[..., 3:4] if translucent else np.ones_like(tx[..., 3:4])
                blended = csub[..., :3] * (1 - a) + tx[..., :3] * a
                csub[ok, :3] = blended[ok]
                csub[ok, 3] = np.maximum(csub[ok, 3], a[ok, 0])
                if not translucent:
                    dsub[ok] = z[ok]
    img = Image.fromarray((np.clip(color, 0, 1) * 255).astype(np.uint8), "RGBA")
    if ss > 1:
        img = img.resize((W, H), Image.LANCZOS)
    return img


def project(points_world, cam, world_rot=None):
    p = np.asarray(points_world, dtype=float)
    if world_rot is not None:
        p = p @ world_rot.T
    v = p @ cam.R.T
    W, H = cam.size
    sx = (v[..., 0] - cam.center[0]) * cam.scale + W / 2
    sy = -(v[..., 1] - cam.center[1]) * cam.scale + H / 2
    return np.stack([sx, sy, v[..., 2]], -1)


def add_glow(img, points, radius, color=(255, 30, 30), strength=0.9):
    """Soft additive glow (approximates Cobblemon's alpha eye bloom)."""
    W, H = img.size
    glow = np.zeros((H, W, 3), dtype=np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    for (x, y) in points:
        d2 = ((xx - x) ** 2 + (yy - y) ** 2) / float(radius * radius)
        glow += np.exp(-d2 * 2.5)[..., None] * np.array(color, dtype=np.float32) / 255.0
    a = np.array(img).astype(np.float32) / 255.0
    rgb = a[..., :3] + glow * strength
    alpha = np.maximum(a[..., 3], np.clip(glow.max(-1) * strength, 0, 1))
    out = np.dstack([np.clip(rgb, 0, 1), alpha])
    return Image.fromarray((out * 255).astype(np.uint8), "RGBA")


def ground_shadow(img_size, cam, center_world, radius_world, world_rot=None, ss=1):
    """Elliptic contact shadow on the ground plane (y=0)."""
    W, H = img_size
    n = 48
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        pts.append([center_world[0] + math.cos(a) * radius_world[0], 0.0,
                    center_world[2] + math.sin(a) * radius_world[1]])
    pr = project(np.array(pts), cam, world_rot)
    from PIL import ImageDraw
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).polygon([(float(x), float(y)) for x, y, _ in pr], fill=110)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    return sh
