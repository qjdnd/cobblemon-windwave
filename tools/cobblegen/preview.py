"""Preview helpers: turntable sheets and animation GIFs."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from . import rig, raster, anim as animlib


def _font(size=14):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _bg(size, top=(122, 168, 214), bottom=(176, 208, 232), flat=False):
    w, h = size
    if flat:
        bottom = top
    g = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - g) + np.array(bottom)[None, None, :] * g
    arr = np.repeat(arr, w, axis=1)
    img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    # grass strip
    d = ImageDraw.Draw(img)
    d.rectangle([0, int(h * 0.80), w, h], fill=(110, 158, 82, 255))
    d.rectangle([0, int(h * 0.80), w, int(h * 0.80) + 3], fill=(92, 138, 66, 255))
    return img


class Scene:
    def __init__(self, model, texture, emissive=None, size=(420, 420), yaw=-32, pitch=16,
                 fit_pose=None, scale=None, ground_frac=0.78):
        self.model = model
        self.parts = rig.build_rig(model)
        self.texture = texture
        self.emissive = emissive
        self.size = size
        self.cam = raster.Camera(yaw=yaw, pitch=pitch, size=size)
        mats = rig.pose_matrices(self.parts, fit_pose)
        mesh = rig.build_mesh(self.parts, mats)
        pts = rig.j_to_world(mesh["quads"].reshape(-1, 3))
        self.cam.fit(pts, margin=0.16)
        if scale:
            self.cam.scale = scale
        # place the ground plane (y=0) at a fixed screen height
        g = raster.project(np.array([[0.0, 0.0, 0.0]]), self.cam)[0]
        self.cam.center = self.cam.center + np.array([0, -(size[1] * ground_frac - g[1]) / self.cam.scale])

    def frame(self, pose=None, glow=False, bg=True, label=None, flat=False):
        mats = rig.pose_matrices(self.parts, pose)
        mesh = rig.build_mesh(self.parts, mats)
        img = raster.render(mesh, self.texture, self.cam, emissive=self.emissive)
        if glow:
            locs = rig.locator_positions(self.parts, mats)
            eyes = [v for k, v in locs.items() if "eye" in k]
            if eyes:
                pr = raster.project(rig.j_to_world(np.array(eyes)), self.cam)
                img = raster.add_glow(img, [(p[0], p[1]) for p in pr], radius=self.cam.scale * 1.6)
        if bg:
            base = _bg(self.size, flat=flat)
            sh = raster.ground_shadow(self.size, self.cam, (0, 0, 0), (9, 8))
            dark = Image.new("RGBA", self.size, (40, 60, 30, 255))
            base = Image.composite(dark, base, sh)
            base.alpha_composite(img)
            img = base
        if label:
            d = ImageDraw.Draw(img)
            f = _font(15)
            d.text((10, 8), label, fill=(255, 255, 255, 255), font=f, stroke_width=2, stroke_fill=(30, 30, 30, 255))
        return img


def sheet(images, cols, pad=4, bg=(30, 30, 30, 255)):
    w, h = images[0].size
    rows = int(math.ceil(len(images) / cols))
    out = Image.new("RGBA", (cols * w + (cols + 1) * pad, rows * h + (rows + 1) * pad), bg)
    for i, im in enumerate(images):
        r, c = divmod(i, cols)
        out.alpha_composite(im, (pad + c * (w + pad), pad + r * (h + pad)))
    return out


def gif(path, frames, fps=20):
    fr = [f.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for f in frames]
    fr[0].save(path, save_all=True, append_images=fr[1:], duration=int(1000 / fps), loop=0, disposal=2)


def animate(scene, anim_dicts, seconds, fps=20, glow=False, label=None, base_pose=None, flat=False):
    frames = []
    n = max(1, int(round(seconds * fps)))
    for i in range(n):
        t = i / fps
        pose = {}
        if base_pose:
            for k, v in base_pose.items():
                pose[k] = dict(v)
        for ad in anim_dicts:
            animlib.eval_anim(ad, t, pose)
        frames.append(scene.frame(pose, glow=glow, label=label, flat=flat))
    return frames
