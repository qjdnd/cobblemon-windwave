// Baby Zubat (pre-evolution of Zubat): a round sky-blue eyeball with a big
// black pupil and two oversized pastel bat wings.
'use strict';
const L = require('../lib');
const { Model, hex, makeRamp, pick, clamp, smooth, ellipsoidLight, norm3 } = L;

const ID = 'babyzubat';

const PALETTES = {
  base: {
    orb: makeRamp(['#24587a', '#3a7fa6', '#57a2c7', '#7cc0dc', '#a6d9ea', '#d4f0f7'], 6),
    orbLine: hex('#1f4a66'),
    arm: makeRamp(['#2a6388', '#3f84ab', '#5aa4c8', '#83c3dd'], 4),
    membrane: makeRamp(['#8e6aa3', '#ad8cc0', '#c8aad6', '#ddc6e7', '#efe2f4'], 5),
    finger: makeRamp(['#4f8fb4', '#6aaccb'], 2),
    pupil: hex('#14161d'), shine: hex('#ffffff'), shine2: hex('#8fb3c9'),
    lid: hex('#1f4a66'),
  },
  shiny: {
    orb: makeRamp(['#1f5714', '#33781c', '#4e952a', '#6aac3a', '#94c862', '#c8e6a2'], 6),
    orbLine: hex('#1a4610'),
    arm: makeRamp(['#245f16', '#387f1f', '#56992b', '#80b85a'], 4),
    membrane: makeRamp(['#9c8058', '#b69d70', '#cbb785', '#e0d29e', '#f0e8c8'], 5),
    finger: makeRamp(['#4a8a28', '#66a33a'], 2),
    pupil: hex('#14161d'), shine: hex('#ffffff'), shine2: hex('#a9c79a'),
    lid: hex('#1a4610'),
  },
};

const O = [0, 12, 0]; // orb centre
const R = 5.5;        // orb radius
const KEY = norm3([-0.35, 0.8, -0.7]); // soft key light from the upper left of the eye

// ------------------------------------------------------------------ orb shading
function orbPaint(ctx) {
  const P = ctx.pal;
  const { l, n } = ellipsoidLight(ctx.p, O, [R, R, R], KEY, 0.35);
  let v = 0.08 + l * 0.95;
  // specular-ish highlight on the upper left
  const spec = Math.max(0, n[0] * KEY[0] + n[1] * KEY[1] + n[2] * KEY[2]);
  v += Math.pow(spec, 12) * 0.25;
  v += (L.vnoise(ctx.p, 1.7, 21) - 0.5) * 0.14;
  // darker rim where the sphere turns away from the face we are painting on (reads as an outline)
  const facing = Math.abs(n[0] * ctx.n[0] + n[1] * ctx.n[1] + n[2] * ctx.n[2]);
  if (facing < 0.38) v -= 0.22;
  if (ctx.face === 'down') v -= 0.1;
  return pick(P.orb, clamp(v, 0, 1), ctx, 0.55);
}

// ------------------------------------------------------------------ wing shape (right wing, mirrored for the left)
// Coordinates are (x, y) in the wing plane at rest, x measured outwards from the body centre.
const ARM = [[4.2, 13.2], [7, 17], [10.5, 19.6], [14, 20.6], [17.5, 20], [20.5, 17.6], [23, 13.4], [24.8, 7.5], [25.8, 0.8]];
const FINGER_TIPS = [[10.8, 4.2], [16.2, 3.4], [21.4, 2.2]];
const FINGER_ROOTS = [[8.6, 18.4], [13.4, 20.4], [18.4, 19.4]];
const ROOT_BOTTOM = [4.2, 8.2];
const TIP = ARM[ARM.length - 1];

function catmull(pts, steps = 8) {
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
    for (let s = 0; s < steps; s++) {
      const t = s / steps, t2 = t * t, t3 = t2 * t;
      out.push([0, 1].map((k) => 0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)));
    }
  }
  out.push(pts[pts.length - 1]);
  return out;
}
const ARM_CURVE = catmull(ARM, 10);
// scalloped trailing edge: arcs between the finger tips
const BOTTOM = (() => {
  const pts = [ROOT_BOTTOM, ...FINGER_TIPS, TIP];
  const out = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const a = pts[i], b = pts[i + 1];
    const depth = i === 0 ? 2.0 : 3.1;
    for (let s = 0; s < 12; s++) {
      const t = s / 12;
      out.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t + depth * Math.sin(Math.PI * t)]);
    }
  }
  out.push(TIP);
  return out;
})();
const POLY = [[4.0, 13.4], ...ARM_CURVE, ...BOTTOM.slice().reverse(), [4.0, 8.2]];

function inPoly(x, y, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}
function distSeg(px, py, a, b) {
  const dx = b[0] - a[0], dy = b[1] - a[1];
  const t = clamp(((px - a[0]) * dx + (py - a[1]) * dy) / (dx * dx + dy * dy || 1), 0, 1);
  return [Math.hypot(px - (a[0] + dx * t), py - (a[1] + dy * t)), t];
}
function distPoly(px, py, pts) {
  let best = [1e9, 0, 0];
  for (let i = 0; i < pts.length - 1; i++) {
    const [d, t] = distSeg(px, py, pts[i], pts[i + 1]);
    if (d < best[0]) best = [d, (i + t) / (pts.length - 1), i];
  }
  return best;
}

function wingPaint(ctx) {
  const P = ctx.pal;
  if (ctx.face !== 'north' && ctx.face !== 'south') return null;
  const x = Math.abs(ctx.lp[0]), y = ctx.lp[1];
  const [dArm, uArm] = distPoly(x, y, ARM_CURVE);
  const armHalf = 1.25 - uArm * 0.65;              // arm thins out towards the claw tip
  const inside = inPoly(x, y, POLY);
  if (dArm < armHalf) {
    // leading-edge arm: lighter on top, darker underneath
    const above = y > ARM_CURVE[Math.min(ARM_CURVE.length - 1, Math.round(uArm * (ARM_CURVE.length - 1)))][1];
    let v = 0.62 + (above ? 0.25 : -0.2) - uArm * 0.15;
    if (dArm > armHalf - 0.45) v -= 0.25;           // outline
    return pick(P.arm, clamp(v, 0, 1), ctx, 0.35);
  }
  if (!inside) return null;
  // fingers
  for (let i = 0; i < FINGER_TIPS.length; i++) {
    const [d, t] = distSeg(x, y, FINGER_ROOTS[i], FINGER_TIPS[i]);
    if (d < 0.62 - t * 0.12) return pick(P.finger, t > 0.5 ? 0 : 1, ctx, 0.3);
  }
  // membrane: pale just under the arm, deeper towards the scalloped trailing edge
  const [dBot] = distPoly(x, y, BOTTOM);
  let v = 0.35 + smooth(0, 7, dBot) * 0.3 + (1 - smooth(0, 2.8, dArm)) * 0.35;
  if (dBot < 0.85) v -= 0.25;                      // darker trailing edge line
  v += (L.vnoise([x, y, 0], 2.2, 9) - 0.5) * 0.18;
  return pick(P.membrane, clamp(v, 0, 1), ctx, 0.28);
}

// ------------------------------------------------------------------ eye (pupil + lid)
const PUPIL = [
  '.KKK.',
  'KWWKK',
  'KWKKK',
  'KKKSK',
  '.KKK.',
];
const LID = [
  '.......',
  '.......',
  '.......',
  '.L...L.',
  '..LLL..',
  '.......',
  '.......',
];

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 64, visibleBox: [3.5, 2.5, 0.8], palettes: PALETTES });
  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', O.slice(), { parent: root });

  // voxel sphere: the union of four boxes reads as a round ball
  m.cube(body, { name: 'orb_x', from: [-5.5, 8.5, -3.5], to: [5.5, 15.5, 3.5], paint: orbPaint });
  m.cube(body, { name: 'orb_core', from: [-4.5, 7.5, -4.5], to: [4.5, 16.5, 4.5], paint: orbPaint });
  m.cube(body, { name: 'orb_y', from: [-3.5, 6.5, -3.5], to: [3.5, 17.5, 3.5], paint: orbPaint });
  m.cube(body, { name: 'orb_z', from: [-3.5, 8.5, -5.5], to: [3.5, 15.5, 5.5], paint: orbPaint });

  // pupil (own bone so it can dart around / dilate)
  const eye = m.bone('eye', [0, 12, -5.5], { parent: body });
  const pupil = m.bone('pupil', [0, 12, -5.55], { parent: eye });
  m.cube(pupil, {
    name: 'pupil', from: [-2.5, 9.5, -5.55], to: [2.5, 14.5, -5.55],
    paint: (ctx) => {
      if (ctx.face !== 'north' && ctx.face !== 'south') return null;
      const col = ctx.face === 'south' ? 4 - ctx.col : ctx.col;
      const ch = PUPIL[ctx.row][col];
      if (ch === 'K') return ctx.pal.pupil.slice();
      if (ch === 'W') return ctx.pal.shine.slice();
      if (ch === 'S') return ctx.pal.shine2.slice();
      return null;
    },
    alpha: (ctx) => {
      if (ctx.face !== 'north' && ctx.face !== 'south') return null;
      const col = ctx.face === 'south' ? 4 - ctx.col : ctx.col;
      const A = L.ALPHA_REDS;
      return { K: A.deep, W: A.hi, S: A.mid }[PUPIL[ctx.row][col]]?.slice() ?? null;
    },
  });
  // eyelid: sits just inside the orb, blink/sleep animations slide it in front of the pupil
  const lid = m.bone('eyelid', [0, 12, -5.4], { parent: eye });
  m.cube(lid, {
    name: 'eyelid', from: [-3.5, 8.5, -5.4], to: [3.5, 15.5, -5.4],
    paint: (ctx) => {
      if (ctx.face !== 'north' && ctx.face !== 'south') return null;
      const col = ctx.face === 'south' ? 6 - ctx.col : ctx.col;
      if (LID[ctx.row][col] === 'L') return ctx.pal.lid.slice();
      return ctx.sample('orb_z', 'north', [ctx.p[0], ctx.p[1], -5.5]);
    },
  });

  // wings: three hinged plane segments per side, the left side mirrors the right side's texture
  const segs = [[4, 12, 5, 22], [12, 19, 3, 22], [19, 26, 0, 21]];
  const joints = [[4.2, 13.2], [12, 20.2], [19, 19]];
  let first = [];
  for (const [side, sign] of [['right', 1], ['left', -1]]) {
    let parent = body;
    segs.forEach(([x0, x1, y0, y1], i) => {
      const nm = i === 0 ? `wing_${side}` : `wing_${side}${i + 1}`;
      const [jx, jy] = joints[i];
      const b = m.bone(nm, [sign * jx, jy, 0.5], { parent });
      const from = sign > 0 ? [x0, y0, 0.5] : [-x1, y0, 0.5];
      const to = sign > 0 ? [x1, y1, 0.5] : [-x0, y1, 0.5];
      const c = m.cube(b, { name: nm, from, to, paint: wingPaint, mirror: sign < 0, uvShare: sign < 0 ? first[i] : undefined });
      if (sign > 0) first.push(c);
      parent = b;
    });
  }

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 23, 0]);
  m.locator(body, 'middle', [0, 12, 0]);
  m.locator(body, 'target', [0, 12, -6]);
  m.locator(body, 'head', [0, 17.5, -1], { extra: ['item_hat'] });
  m.locator(body, 'face', [0, 12, -5.6], { extra: ['item_face'] });
  m.locator(body, 'mouth', [0, 9.5, -5.5], { extra: ['physical', 'special'] });
  m.locator(body, 'item', [0, 7, -2]);
  m.locator(m.boneMap.wing_right3, 'wing_right', [22.5, 12, 0.5]);
  m.locator(m.boneMap.wing_left3, 'wing_left', [-22.5, 12, 0.5]);

  require('./babyzubat.anim')(m);
  return m;
}

module.exports = { ID, build, PALETTES };
