// Baby Onix (pre-evolution of Onix): a little rock snake standing on its curled lower body. A flat-
// topped rock head with a long snout, a heavy brow over a half-lidded side eye glancing back, a short
// neck, a big body boulder, and a tail lying on the ground that ends in a flat rock and a small round one.
//
// Texture: the rock surface is Cobblemon's own Onix texture. Each rock of the baby is a smaller copy
// of one of Onix's boulders: its faces are that boulder's faces from source/onix.png, shrunk up to 1.5:1
// with the crack lines kept, and shaded one step lighter or darker for roundness. The shiny is the
// same pixels on Onix's shiny ramp: Onix's grey and shiny olive ramps have six matching steps (the
// same pixels in onix.png and onix_shiny.png). Eye and mouth colours are Onix's too.
'use strict';
const fs = require('fs');
const path = require('path');
const { PNG } = require('pngjs');
const L = require('../../lib');
const { Model, hex, clamp, ellipsoidLight, norm3 } = L;

const ID = 'babyonix';

// Onix's rock ramp (dark to light) and the shiny ramp with the same six steps
const ROCK = ['#4d4b4f', '#5b585e', '#6c6970', '#807e83', '#979396', '#a8a6a6'];
const ROCK_SHINY = ['#665f18', '#707021', '#7f8231', '#90963d', '#9fa850', '#b4ba64'];
const shared = {
  eyeW: hex('#e4e7e7'),
  eyeS: hex('#cdd3d7'),
  iris: hex('#4d4b4f'),
  irisLo: hex('#322f37'),
  glint: hex('#e4e7e7'),
  lid: hex('#24212a'),
  mouth: [hex('#0a0c0d'), hex('#16161b'), hex('#24212a'), hex('#322f37')],
};
const PALETTES = {
  base: { ...shared, rock: ROCK.map((c) => hex(c)) },
  shiny: { ...shared, rock: ROCK_SHINY.map((c) => hex(c)) },
};

// ------------------------------------------------------------------ Onix texture source
const SRC = path.join(__dirname, 'source');
const onixPng = PNG.sync.read(fs.readFileSync(path.join(SRC, 'onix.png')));
const rampIndex = ROCK.map((c) => hex(c));
function onixIndex(x, y) {
  const k = (y * onixPng.width + x) * 4;
  const px = [onixPng.data[k], onixPng.data[k + 1], onixPng.data[k + 2]];
  let best = 0, bd = Infinity;
  rampIndex.forEach((c, i) => { const d = Math.abs(c[0] - px[0]) + Math.abs(c[1] - px[1]) + Math.abs(c[2] - px[2]); if (d < bd) { bd = d; best = i; } });
  return best;
}
// Onix's boulders (plain rock, no eyes or mouth): for each, its six faces as [x, y, w, h] in onix.png
const BOULDERS = (() => {
  const g = JSON.parse(fs.readFileSync(path.join(SRC, 'onix.geo.json'), 'utf8'))['minecraft:geometry'][0];
  const out = {};
  for (const b of g.bones) {
    if (!/^boulder\d+$/.test(b.name)) continue;
    const c = b.cubes[0];
    const [w, h, d] = c.size, [u, v] = c.uv;
    out[b.name] = { east: [u, v + d, d, h], west: [u + d + w, v + d, d, h], north: [u + d, v + d, w, h], south: [u + 2 * d + w, v + d, w, h], up: [u + d, v, w, d], down: [u + d + w, v, w, d] };
  }
  return out;
})();
const strHash = (s) => { let h = 2166136261; for (const ch of s) h = Math.imul(h ^ ch.charCodeAt(0), 16777619); return h >>> 0; };
// corners of a face of a box as seen from outside (same convention as Box UV): top-left, top-right, bottom-left
const faceCorners = (f, t) => ({
  east: [[t[0], t[1], t[2]], [t[0], t[1], f[2]], [t[0], f[1], t[2]]],
  west: [[f[0], t[1], f[2]], [f[0], t[1], t[2]], [f[0], f[1], f[2]]],
  up: [[f[0], t[1], f[2]], [t[0], t[1], f[2]], [f[0], t[1], t[2]]],
  down: [[f[0], f[1], t[2]], [t[0], f[1], t[2]], [f[0], f[1], f[2]]],
  south: [[f[0], t[1], t[2]], [t[0], t[1], t[2]], [f[0], f[1], t[2]]],
  north: [[t[0], t[1], f[2]], [f[0], t[1], f[2]], [t[0], f[1], f[2]]],
});

// light from the front-top (symmetric left/right so it reads well at any yaw)
const KEY = norm3([0, 0.85, -0.75]);

// Rock paint: each baby rock is a smaller Onix boulder. A face of the rock shows the same face of
// the chosen Onix boulder shrunk to fit (at most 1.5:1), keeping its dark crack lines, then one ramp step
// lighter on the lit side and darker in the shade / underneath / at the ground. All bevel boxes of a
// rock use the rock's full bounds, so the pattern lines up across them.
const SCALE = 1.5;
function onixRock(boulder, bounds, ell, opts = {}) {
  const src = BOULDERS[boulder];
  if (!src) throw new Error('no Onix ' + boulder);
  return (ctx) => {
    const [TL, TR, BL] = faceCorners(bounds.from, bounds.to)[ctx.face];
    const ex = TR.map((v, i) => v - TL[i]), ey = BL.map((v, i) => v - TL[i]);
    const Wr = Math.hypot(...ex), Hr = Math.hypot(...ey);
    const d = ctx.lp.map((v, i) => v - TL[i]);
    const s = (d[0] * ex[0] + d[1] * ex[1] + d[2] * ex[2]) / (Wr * Wr), t = (d[0] * ey[0] + d[1] * ey[1] + d[2] * ey[2]) / (Hr * Hr);
    const [sx, sy, sw, sh] = src[ctx.face];
    const ku = Math.min(SCALE, sw / Wr), kv = Math.min(SCALE, sh / Hr);
    const h = strHash(boulder + ctx.face + (opts.seed || ''));
    const ox = (h % 997) / 997 * (sw - Wr * ku), oy = ((h >>> 10) % 997) / 997 * (sh - Hr * kv);
    // source footprint of this texel
    const x0 = sx + ox + s * Wr * ku - ku / 2, y0 = sy + oy + t * Hr * kv - kv / 2;
    const idx = [];
    for (let y = Math.floor(y0 + 0.001); y < Math.ceil(y0 + kv - 0.001); y++) for (let x = Math.floor(x0 + 0.001); x < Math.ceil(x0 + ku - 0.001); x++) {
      idx.push(onixIndex(clamp(x, sx, sx + sw - 1), clamp(y, sy, sy + sh - 1)));
    }
    // keep the cracks where they dominate the footprint, average the rest (compared visually with other rules)
    const dark = idx.filter((v) => v <= 1);
    let i = dark.length * 2 > idx.length ? Math.min(...dark) : Math.round(idx.reduce((a, b) => a + b, 0) / idx.length);
    const { l } = ellipsoidLight(ctx.p, ell.c, ell.r, KEY, 0.7);
    if (l > (opts.hi ?? 0.84) && i >= 3) i += 1;
    if (l < (opts.lo ?? 0.3)) i -= 1;
    if (ctx.face === 'down') i -= 1;
    if (ctx.p[1] < 1 && ctx.face !== 'up') i -= 1;
    return ctx.pal.rock[clamp(i, 0, 5)].slice();
  };
}

// Eye on the side of the head, 5 x 3, drawn with the snout on the left (the right eye is flipped):
// a heavy lid line on top, white sclera; the iris is a separate plane over the back three columns.
const EYE = ['LLLLL', 'wwwww', '.wwws'];
const IRIS = ['IgI', 'igi'];
// expression overlays over the eye ('R' rock, 'L' lid line, '.' see-through to the eye)
const CLOSED = ['RRRRR', 'RRRRR', 'LLLLR'];
const GLARE = ['RRRRR', 'LLLLL', '.....'];
const HAPPY = ['RRRRR', 'RRLRR', 'RLRLR'];
const DIZZY = ['RLRLR', 'RRLRR', 'RLRLR'];

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 128, visibleBox: [2, 2.5, 0.9], palettes: PALETTES });
  const A = L.ALPHA_REDS;

  // a rounded rock: three overlapping boxes, each inset by b on two axes, so all twelve edges are bevelled
  const rock = (bone, name, from, to, b, paint) => {
    const inset = (axes) => [0, 1, 2].map((i) => (axes.includes(i) ? [from[i] + b, to[i] - b] : [from[i], to[i]]));
    const box = (n, axes) => { const r = inset(axes); return m.cube(bone, { name: n, from: r.map((x) => x[0]), to: r.map((x) => x[1]), paint }); };
    return { x: box(name, [1, 2]), y: box(name + '_y', [0, 2]), z: box(name + '_z', [0, 1]) };
  };
  const center = (from, to) => from.map((v, i) => (v + to[i]) / 2);
  const rockAt = (bone, name, boulder, from, to, b, opts = {}) => {
    const c = center(from, to), r = from.map((v, i) => (to[i] - v) / 2 + 1.5);
    return rock(bone, name, from, to, b, onixRock(boulder, { from, to }, { c, r }, opts));
  };

  const root = m.bone(ID, [0, 0, 0]);
  // the curled lower body carries everything; the tail lies behind it on the ground
  const body = m.bone('body', [0, 3, 2.5], { parent: root });
  rockAt(body, 'base', 'boulder4', [-5, 0, -3], [5, 6, 8], 1);
  const torso = m.bone('torso', [0, 6, 0], { parent: body });
  rockAt(torso, 'belly', 'boulder1', [-5.5, 5, -5.5], [5.5, 15, 4.5], 1.5);
  const neck = m.bone('neck', [0, 15, 2.5], { parent: torso });
  rockAt(neck, 'neck', 'boulder3', [-3.5, 14, -1], [3.5, 20, 6], 1);

  // ----------------------------------------------------------------- head
  const head = m.bone('head', [0, 20, 2], { parent: neck, rotation: [8, 0, 0] });
  const cranium = rockAt(head, 'cranium', 'boulder2', [-5.5, 19, -3], [5.5, 28, 7], 1);
  rockAt(head, 'brow', 'boulder5', [-6, 26, -8.5], [6, 30, 4.5], 1);
  const snout = rockAt(head, 'snout', 'boulder6', [-5, 20, -9], [5, 26, -2], 1);
  rockAt(head, 'crown_back', 'boulder7', [-4.5, 21, 6], [4.5, 27, 9], 1, { hi: 0.9, lo: 0.45 });
  // roof of the mouth, seen when the jaw drops
  const roof = (c) => { const base = c.paint; c.paint = (ctx) => (ctx.face === 'down' ? ctx.pal.mouth[1].slice() : base(ctx)); };
  roof(snout.x); roof(snout.y); roof(snout.z); roof(cranium.y);

  const jaw = m.bone('jaw', [0, 20, 4], { parent: head });
  const jawRock = rockAt(jaw, 'jaw', 'boulder13', [-4.5, 17, -8], [4.5, 20, 4], 0.5);
  const jawTop = jawRock.y.paint;
  jawRock.y.paint = (ctx) => (ctx.face === 'up' ? ctx.pal.mouth[ctx.lp[2] < -6 ? 2 : 0].slice() : jawTop(ctx));

  // eyes painted on the sides of the cranium (cranium.x spans z -2..6, y 20..27)
  const eyeAt = (ctx) => {
    if (ctx.face !== 'east' && ctx.face !== 'west') return '.';
    const z = ctx.lp[2], y = ctx.lp[1];
    if (z < 0 || z > 5 || y < 23 || y > 26) return '.';
    const col = Math.floor(z), row = Math.floor(26 - y); // col 0 = the front (snout side)
    return EYE[row][col];
  };
  m.decal({
    cubes: [cranium.x.name],
    fn: (ctx) => ({ L: ctx.pal.lid, w: ctx.pal.eyeW, s: ctx.pal.eyeS }[eyeAt(ctx)]?.slice()),
  });
  cranium.x.alpha = (ctx) => ({ w: A.lo, s: A.deep }[eyeAt(ctx)]?.slice() ?? null);
  const under = (ctx, sign) => ctx.sample(cranium.x.name, sign > 0 ? 'east' : 'west', [ctx.p[0], ctx.p[1], ctx.p[2]]);

  for (const [sideName, s] of [['right', 1], ['left', -1]]) {
    const outward = s > 0 ? 'east' : 'west';
    // iris: glances back by default (like the concept art); animations slide it along z
    const iris = m.bone('iris_' + sideName, [s * 5.5, 25, 3.5], { parent: head });
    const cell = (rows, ctx) => rows[Math.floor(26 - ctx.lp[1])][Math.floor(ctx.lp[2] - 2)];
    m.cube(iris, {
      name: 'iris_' + sideName, from: [s * 5.53, 24, 2], to: [s * 5.53, 26, 5],
      paint: (ctx) => (ctx.face === outward ? { I: ctx.pal.iris, i: ctx.pal.irisLo, g: ctx.pal.glint }[cell(IRIS, ctx)].slice() : null),
      alpha: (ctx) => (ctx.face === outward ? { I: A.dark, i: A.darkest, g: A.hi }[cell(IRIS, ctx)].slice() : null),
    });
    // expression overlays: hidden 0.40-0.43 inside the head, animations slide them 0.5 outwards
    const overlay = (name, rows, depth) => {
      const b = m.bone(`${name}_${sideName}`, [s * 5.5, 24.5, 2.5], { parent: head });
      const x = s * (5.5 - depth);
      m.cube(b, {
        name: `${name}_${sideName}`, from: [x, 23, 0], to: [x, 26, 5],
        paint: (ctx) => {
          if (ctx.face !== outward) return null;
          const ch = rows[Math.floor(26 - ctx.lp[1])][Math.floor(ctx.lp[2])];
          if (ch === 'L') return ctx.pal.lid.slice();
          if (ch === 'R') return under(ctx, s);
          return null;
        },
      });
    };
    overlay('eyes_closed', CLOSED, 0.4);
    overlay('eyes_glare', GLARE, 0.41);
    overlay('eyes_happy', HAPPY, 0.42);
    overlay('eyes_dizzy', DIZZY, 0.43);
  }

  // ----------------------------------------------------------------- tail: a flat rock, then a small round one
  const tail = m.bone('tail', [0, 2, 8], { parent: body });
  rockAt(tail, 'tail', 'boulder9', [-3.5, 0, 8], [3.5, 4, 16], 1);
  const tip = m.bone('tail_tip', [0, 2, 16], { parent: tail });
  rockAt(tip, 'tail_tip', 'boulder11', [-2, 0, 16], [2, 4, 20], 1);

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 32, 0]);
  m.locator(torso, 'middle', [0, 11, 0]);
  m.locator(head, 'target', [0, 24, -9]);
  m.locator(head, 'head', [0, 30, -1], { extra: ['item_hat'] });
  m.locator(head, 'face', [0, 23, -9], { extra: ['item_face'] });
  m.locator(jaw, 'mouth', [0, 19, -8], { extra: ['item'] });
  m.locator(head, 'eye_right', [5.6, 24.5, 3]);
  m.locator(head, 'eye_left', [-5.6, 24.5, 3]);
  m.locator(tail, 'tail', [0, 2, 15]);
  m.locator(tip, 'tail_tip', [0, 2, 20], { extra: ['special'] });

  require('./anims')(m);
  return m;
}

module.exports = { ID, build, PALETTES };
