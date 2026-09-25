// Baby Litwick (pre-evolution of Litwick): a floating flame-drop ghost. Round
// blue body turning purple towards a tall curling flame, pale face disk with big
// yellow eyes, a tiny "o" mouth, two nub arms and a little drip for a tail.
'use strict';
const L = require('../lib');
const { Model, hex, makeRamp, pick, clamp, smooth, ellipsoidLight, norm3 } = L;

const ID = 'babylitwick';

const PALETTES = {
  base: {
    blue: makeRamp(['#4f78bd', '#6c95d4', '#8ab3e7', '#a6cbf3', '#c3e0fa'], 5),
    purple: makeRamp(['#48417f', '#5a529a', '#6d66b0', '#837dc3', '#9c97d4', '#b6b4e6'], 6),
    faceLo: makeRamp(['#b3d3ec', '#c7e2f4', '#daeefa'], 3),
    faceHi: makeRamp(['#aaa4d3', '#bdb8e0', '#d0ccec'], 3),
    faceLine: hex('#5b5796'),
    inner: makeRamp(['#aca7d8', '#c0bbe4', '#d4d1ef', '#e8e6f8'], 4),
    eyeK: hex('#1f1b26'), eyeTop: hex('#9c882c'), eyeLow: hex('#e8cb38'), eyeHi: hex('#fbe78c'),
    mouth: hex('#2b2743'),
    tip: makeRamp(['#5d559e', '#7069b3'], 2),
    shut: hex('#3a3570'),
  },
  shiny: {
    blue: makeRamp(['#3f9fb0', '#5dbccb', '#80d4de', '#a6e5ea', '#caf3f4'], 5),
    purple: makeRamp(['#1f6f86', '#2a88a0', '#3aa2b8', '#55bacc', '#7ed0dc', '#a9e3ea'], 6),
    faceLo: makeRamp(['#bfe9ea', '#d3f3f2', '#e6fbfa'], 3),
    faceHi: makeRamp(['#a6dde4', '#bce8ec', '#d2f2f4'], 3),
    faceLine: hex('#2c6d80'),
    inner: makeRamp(['#a2e2e6', '#bdeef0', '#d6f7f7', '#ecfdfd'], 4),
    eyeK: hex('#1f1b26'), eyeTop: hex('#5c9a1c'), eyeLow: hex('#a4ea32'), eyeHi: hex('#e2fb9a'),
    mouth: hex('#1d3f4a'),
    tip: makeRamp(['#1f6f86', '#2e8fa6'], 2),
    shut: hex('#1d4f5e'),
  },
};

const KEY = norm3([0.45, 0.75, -0.55]); // light from the upper left of the viewer (the Pokemon's right)
const BODY_C = [0, 9, 0], BODY_R = [9.5, 7.5, 7.5];

// face disk (front), in world x/y
const DISK = { cx: 0, cy: 8.6, rx: 6.6, ry: 5.3 };
const diskD = (x, y) => Math.hypot((x - DISK.cx) / DISK.rx, (y - DISK.cy) / DISK.ry);
// the pale inner flame rises out of the face disk on the Pokemon's left (-x) side
function innerFlame(x, y) {
  if (y < 12.5 || y > 28.5) return 0;
  const t = (y - 12.5) / 16;                        // 0 at the disk, 1 at the tip
  const cx = -2.2 - 2.2 * Math.sin(t * Math.PI * 0.75) + t * 0.6;
  const half = 2.7 * Math.pow(1 - t, 0.75) + 0.15;
  return Math.abs(x - cx) < half ? 1 : 0;
}

function shell(ctx, { flame = false } = {}) {
  const P = ctx.pal;
  const p = ctx.p;
  const { l } = ellipsoidLight(p, flame ? [-(p[1] - 16) * 0.18, p[1], 0] : BODY_C, flame ? [6, 30, 5.5] : BODY_R, KEY, 0.5);
  let v = (flame ? 0.1 + l * 0.62 : 0.2 + l * 0.8) + (L.vnoise(p, 2.2, 13) - 0.5) * 0.2;
  // flame tiers: slightly lighter rim along the top edge of each tier (licking flame look)
  if (flame && ctx.face !== 'up' && ctx.face !== 'down' && ctx.row === 0) v += 0.12;
  if (ctx.face === 'down') v -= 0.2;
  // pale glossy highlight blob on the upper left of the body
  const hl = Math.hypot((p[0] - 5.5) / 2.6, (p[1] - 13.2) / 1.7);
  const front = ctx.n[2] < -0.5;
  if (!flame && front && hl < 1) v += 0.35;
  // blue below, purple above (dithered transition around eye height)
  const tr = (p[1] - 11.4) / 1.6 + (L.bayer(ctx.tu, ctx.tv) - 0.5) * 0.9;
  if (flame || tr > 0.5) return pick(P.purple, clamp(v, 0, 1), ctx, 0.45);
  return pick(P.blue, clamp(v, 0, 1), ctx, 0.45);
}

function bodyPaint(ctx) {
  const P = ctx.pal;
  const [x, y] = ctx.p;
  if (ctx.n[2] < -0.5) {
    const d = diskD(x, y);
    if (d < 1) {
      // outline one texel wide at the disk edge (checked with the neighbours outside the disk)
      const outside = (dx, dy) => diskD(x + dx, y + dy) >= 1;
      if (outside(1, 0) || outside(-1, 0) || outside(0, 1) || outside(0, -1)) {
        if (!(y > 12 && innerFlame(x, y + 1))) return P.faceLine.slice();
      }
      const n = (L.vnoise(ctx.p, 2, 5) - 0.5) * 0.3;
      const tr = (y - 9.6) / 1.5 + (L.bayer(ctx.tu, ctx.tv) - 0.5) * 0.9;
      const v = 0.55 + (1 - d) * 0.35 + n;
      return pick(tr > 0.5 ? P.faceHi : P.faceLo, clamp(v, 0, 1), ctx, 0.4);
    }
    if (innerFlame(x, y)) return innerPaint(ctx);
  }
  return shell(ctx);
}
function innerPaint(ctx) {
  const v = 0.35 + (L.vnoise(ctx.p, 1.8, 3) - 0.5) * 0.35 + (ctx.p[1] - 14) * 0.02;
  return pick(ctx.pal.inner, clamp(v, 0, 1), ctx, 0.45);
}
function flamePaint(ctx) {
  const [x, y] = ctx.p;
  if (ctx.n[2] < -0.5 && innerFlame(x, y)) return innerPaint(ctx);
  // wispy lighter edges near the top of each flame tier
  return shell(ctx, { flame: true });
}

// face features on the front of body_deep (17 wide x 10 tall, col 0 = viewer's left = +x)
const FACE = [
  '.................',
  '...KK.......KK...',
  '..KttK.....KttK..',
  '..KhtK.....KhtK..',
  '..KyyK.....KyyK..',
  '..KyyK.....KyyK..',
  '...KK.......KK...',
  '........o........',
  '........o........',
  '.................',
];
const CLOSED = [ // eyes-closed overlay, 5 x 6 texels per eye (col 0 = outer side of the right eye)
  '.....',
  '.....',
  '.....',
  'S..S.',
  '.SS..',
  '.....',
];
const HAPPY = [
  '.....',
  '.....',
  '.SS..',
  'S..S.',
  '.....',
  '.....',
];
const MOUTH_OPEN = ['.MM.', 'MRRM', 'MRRM', '.MM.'];

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 128, visibleBox: [2.5, 3, 1.1], palettes: PALETTES, emissive: true });
  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', [0, 8, 0], { parent: root });

  // rounded body: the union of several boxes
  m.cube(body, { name: 'body_wide', from: [-9.5, 5, -6], to: [9.5, 13, 6], paint: bodyPaint });
  m.cube(body, { name: 'body_deep', from: [-8.5, 4, -7], to: [8.5, 14, 7], paint: bodyPaint });
  m.cube(body, { name: 'body_tall', from: [-8.5, 3, -6], to: [7.5, 15, 6], paint: bodyPaint });
  m.cube(body, { name: 'body_top', from: [-8.5, 15, -5.5], to: [6.5, 16, 5.5], paint: bodyPaint });
  m.cube(body, { name: 'body_bottom', from: [-5.5, 2, -4], to: [5.5, 3, 4], paint: bodyPaint });

  m.decal({
    cubes: ['body_deep'], face: 'north',
    fn: (ctx) => {
      const ch = FACE[ctx.row] && FACE[ctx.row][ctx.col];
      const P = ctx.pal;
      return { K: P.eyeK, t: P.eyeTop, h: P.eyeHi, y: P.eyeLow, o: P.mouth }[ch]?.slice();
    },
  });
  const under = (ctx) => ctx.sample('body_deep', 'north', [ctx.p[0], ctx.p[1], -7]);

  // expression overlays (hidden just inside the body, animations slide them 0.3 forward)
  const expr = m.bone('face', [0, 9.5, -6.8], { parent: body });
  const overlay = (rows) => (ctx) => {
    if (ctx.face !== 'north' && ctx.face !== 'south') return null;
    const col = ctx.face === 'south' ? rows[0].length - 1 - ctx.col : ctx.col;
    if (rows[ctx.row][col] === 'S') return ctx.pal.shut.slice();
    return under(ctx);
  };
  const lidsC = m.bone('eyes_closed', [0, 9.5, -6.8], { parent: expr });
  m.cube(lidsC, { name: 'eye_closed_right', from: [1.5, 7, -6.8], to: [6.5, 13, -6.8], paint: overlay(CLOSED) });
  m.cube(lidsC, { name: 'eye_closed_left', from: [-6.5, 7, -6.8], to: [-1.5, 13, -6.8], paint: overlay(CLOSED.map((r) => r.split('').reverse().join(''))) });
  const lidsH = m.bone('eyes_happy', [0, 9.5, -6.75], { parent: expr });
  m.cube(lidsH, { name: 'eye_happy_right', from: [1.5, 7, -6.75], to: [6.5, 13, -6.75], paint: overlay(HAPPY) });
  m.cube(lidsH, { name: 'eye_happy_left', from: [-6.5, 7, -6.75], to: [-1.5, 13, -6.75], paint: overlay(HAPPY.map((r) => r.split('').reverse().join(''))) });
  const mouth = m.bone('mouth', [0, 6, -6.8], { parent: expr });
  m.cube(mouth, {
    name: 'mouth_open', from: [-2, 4, -6.8], to: [2, 8, -6.8],
    paint: (ctx) => {
      if (ctx.face !== 'north' && ctx.face !== 'south') return null;
      const col = ctx.face === 'south' ? 3 - ctx.col : ctx.col;
      const ch = MOUTH_OPEN[ctx.row][col];
      if (ch === 'M') return ctx.pal.mouth.slice();
      if (ch === 'R') return hex('#6e3a5c');
      return under(ctx);
    },
  });

  // nub arms at the lower corners of the face, pointing down and inwards
  const armPaint = (ctx) => {
    const P = ctx.pal;
    const c = ctx.cube;
    const right = c.name.endsWith('right');
    const tipX = right ? c.from[0] : c.to[0];
    const lx = Math.abs(ctx.lp[0] - tipX);            // 0 at the inner (tip) end
    if (lx < 1.01) return pick(P.tip, ctx.face === 'up' ? 1 : 0, ctx, 0.2);
    const v = ctx.face === 'up' ? 0.85 : ctx.face === 'down' ? 0.25 : 0.55;
    const edge = ctx.row === 0 || ctx.row >= ctx.H - 1;
    return pick(P.blue, clamp(v - (edge && ctx.face !== 'up' ? 0.25 : 0), 0, 1), ctx, 0.2);
  };
  const armR = m.bone('arm_right', [8, 6, -6], { parent: body, rotation: [8, 28, 32] });
  m.cube(armR, { name: 'arm_right', from: [4.5, 5, -8], to: [8.5, 7, -6], paint: armPaint });
  const armL = m.bone('arm_left', [-8, 6, -6], { parent: body, rotation: [8, -28, -32] });
  m.cube(armL, { name: 'arm_left', from: [-8.5, 5, -8], to: [-4.5, 7, -6], paint: armPaint });

  // drip tail underneath
  const tail = m.bone('tail', [1, 2.5, 0], { parent: body });
  m.cube(tail, { name: 'tail', from: [-0.5, 0.5, -1.5], to: [2.5, 2.5, 1.5], paint: (ctx) => shell(ctx) });
  const tail2 = m.bone('tail2', [1, 0.5, 0], { parent: tail });
  m.cube(tail2, { name: 'tail2', from: [0.5, -1, -0.5], to: [1.5, 0.5 + 0.5, 0.5], paint: (ctx) => pick(ctx.pal.tip, 0.5, ctx, 0.3) });

  // flame: a chain of tapering tiers traced from the artwork's outline; it leans and
  // curls towards the Pokemon's left (-x) and its right edge continues the body's side
  const tiers = [
    ['flame', [-8.5, 16, -5.5], [6.5, 18, 5.5], [-1, 16, 0]],
    ['flame2', [-8.5, 18, -5], [4.5, 20, 5], [-2, 18, 0]],
    ['flame3', [-7.5, 20, -4.5], [3.5, 22, 4.5], [-2, 20, 0]],
    ['flame4', [-6.5, 22, -4], [2.5, 25, 4], [-2, 22, 0]],
    ['flame5', [-5.5, 25, -3], [1.5, 28, 3], [-2, 25, 0]],
    ['flame6', [-4.5, 28, -2], [0.5, 30, 2], [-2, 28, 0]],
    ['flame7', [-5.5, 30, -1.5], [-2.5, 32, 1.5], [-4, 30, 0]],
    ['flame_tip', [-6.5, 32, -1], [-4.5, 34, 1], [-5.5, 32, 0]],
  ];
  let parent = body;
  for (const [nm, from, to, pivot] of tiers) {
    const b = m.bone(nm, pivot, { parent });
    m.cube(b, { name: nm, from, to, paint: flamePaint, emissive: flamePaint });
    parent = b;
  }
  // eyes glow too (emissive copy of the eye pixels only)
  m.cubes.find((c) => c.name === 'body_deep').emissive = (ctx) => {
    if (ctx.face !== 'north') return null;
    const ch = FACE[ctx.row] && FACE[ctx.row][ctx.col];
    const P = ctx.pal;
    const c = { t: P.eyeTop, h: P.eyeHi, y: P.eyeLow }[ch];
    return c ? c.slice() : null;
  };

  // alpha Pokemon: the eyes glow red
  m.cubes.find((c) => c.name === 'body_deep').alpha = (ctx) => {
    if (ctx.face !== 'north') return null;
    const A = L.ALPHA_REDS;
    return { K: A.darkest, t: A.deep, h: A.hi, y: A.mid }[FACE[ctx.row] && FACE[ctx.row][ctx.col]]?.slice() ?? null;
  };

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 35, 0]);
  m.locator(body, 'middle', [0, 9, 0]);
  m.locator(body, 'target', [0, 9, -8]);
  m.locator(body, 'head', [0, 16, -2], { extra: ['item_hat'] });
  m.locator(body, 'face', [0, 9, -7], { extra: ['item_face'] });
  m.locator(body, 'mouth', [0, 6, -7]);
  m.locator(body, 'eye_right', [3.5, 10, -7]);
  m.locator(body, 'eye_left', [-3.5, 10, -7]);
  m.locator(armR, 'hand_primary', [5, 4.5, -8.5], { extra: ['physical'] });
  m.locator(armL, 'hand_secondary', [-5, 4.5, -8.5]);
  m.locator(armR, 'item', [5, 4, -9]);
  m.locator(m.boneMap.flame3, 'special', [-2.5, 26, 0]);

  require('./babylitwick.anim')(m);
  return m;
}

module.exports = { ID, build, PALETTES };
