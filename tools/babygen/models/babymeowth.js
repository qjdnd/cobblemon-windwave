// Baby Meowth (pre-evolution of Meowth): a round cream kitten lying in a
// "loaf" pose, a holed coin on its forehead, three coins floating above its
// head, curled tail with an orange tip and contented closed eyes.
'use strict';
const L = require('../lib');
const { Model, hex, makeRamp, pick, vnoise, clamp, smooth, ellipsoidLight, norm3, sprite } = L;

const ID = 'babymeowth';

const PALETTES = {
  base: {
    cream: makeRamp(['#b0934f', '#cdb271', '#e3cf91', '#f2e4b1', '#fbf2d0', '#fffce9'], 6),
    tail: makeRamp(['#a24c14', '#c8691f', '#e08a2e', '#f0ab45', '#f9cd70', '#fde6a2'], 6),
    earIn: makeRamp(['#1c2420', '#29352f', '#3a4841', '#4f5f56'], 4),
    coin: { rimHi: hex('#f3c64a'), rim: hex('#d69a26'), rimLo: hex('#a86c14'), face: hex('#f6d45c'), faceHi: hex('#fff3b4'), faceLo: hex('#e5b43c'), edge: hex('#c48a1e') },
    line: hex('#4a3322'),
    mouthLine: hex('#7a5638'),
    toe: hex('#c3ab74'),
    mouthIn: hex('#a8404f'),
    tongue: hex('#f2929c'),
    eyeK: hex('#231c22'),
    eyeW: hex('#ffffff'),
    eyeHi: hex('#5e4c73'),
    blush: hex('#f7cdb0'),
  },
  shiny: {
    cream: makeRamp(['#9c7440', '#b98f52', '#d2aa69', '#e3c282', '#f0d7a0', '#f9eac4'], 6),
    tail: makeRamp(['#5e2210', '#7c3116', '#9a441d', '#b65d28', '#cf7c3a', '#e5a35e'], 6),
    earIn: makeRamp(['#1c2420', '#29352f', '#3a4841', '#4f5f56'], 4),
    coin: { rimHi: hex('#d65b7c'), rim: hex('#b23e5d'), rimLo: hex('#7e2240'), face: hex('#e0718f'), faceHi: hex('#f8b7ca'), faceLo: hex('#c24c6b'), edge: hex('#9e3050') },
    line: hex('#4a3322'),
    mouthLine: hex('#7a5638'),
    toe: hex('#b08650'),
    mouthIn: hex('#a8404f'),
    tongue: hex('#f2929c'),
    eyeK: hex('#231c22'),
    eyeW: hex('#ffffff'),
    eyeHi: hex('#5e4c73'),
    blush: hex('#f2b995'),
  },
};

// light from the front-top (symmetric left/right so it reads well at any yaw)
const KEY = norm3([0, 0.85, -0.75]);

function fur(ell, opts = {}) {
  return (ctx) => {
    const { l } = ellipsoidLight(ctx.p, ell.c, ell.r, KEY, opts.wrap ?? 0.7);
    let v = 0.4 + l * 0.55;
    v -= 0.32 * (1 - smooth(0, 2.2, ctx.p[1]));                   // contact shadow at the ground
    if (ctx.face === 'down') v -= 0.25;
    if (opts.ao) v -= opts.ao(ctx.p) || 0;
    v += (L.vnoise(ctx.p, 2.1, 11) - 0.5) * 0.34;                 // soft fur blotches (Cobblemon-style mottling)
    v += (L.hash3(Math.floor(ctx.p[0] + 50), Math.floor(ctx.p[1] + 50), Math.floor(ctx.p[2] + 50), 3) - 0.5) * 0.1;
    return pick(ctx.pal.cream, clamp(v, 0, 1), ctx, 0.45);
  };
}

// 5x5 coin with a hole in the middle, lit from the upper left of the viewer
const COIN_FRONT = [
  '.RRR.',
  'RHFFr',
  'RF.FL',
  'rFFfL',
  '.LLL.',
];
function coinPaint(ctx) {
  const C = ctx.pal.coin;
  const c = ctx.cube;
  const cx = Math.floor(ctx.lp[0] - c.from[0]), cy = 4 - Math.floor(ctx.lp[1] - c.from[1]); // cy: 0 = top row
  if (ctx.face === 'north' || ctx.face === 'south') {
    const col = ctx.face === 'north' ? 4 - cx : cx; // as seen by a viewer looking at that side
    const ch = COIN_FRONT[cy][col];
    return { '.': null, R: C.rimHi, r: C.rim, L: C.rimLo, H: C.faceHi, F: C.face, f: C.faceLo }[ch]?.slice() ?? null;
  }
  const along = ctx.face === 'up' || ctx.face === 'down' ? cx : cy;
  if (along === 0 || along === 4) return null;
  return (ctx.face === 'up' ? C.rimHi : ctx.face === 'down' ? C.rimLo : C.edge).slice();
}

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 64, visibleBox: [2.5, 2, 0.6], palettes: PALETTES });
  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', [0, 0, 2], { parent: root });

  // ----------------------------------------------------------------- body (loaf)
  const bodyEll = { c: [0, 1.5, 2.5], r: [10, 9, 9.5] };
  const aoBody = (p) => 0.22 * smooth(-1, -3.5, p[2]) * smooth(5, 7.5, p[1]); // tucked under the back of the head
  const bodyFur = fur(bodyEll, { ao: aoBody });
  m.cube(body, { name: 'body_main', from: [-7.5, 0, -3], to: [7.5, 7, 8], paint: bodyFur });
  m.cube(body, { name: 'body_low', from: [-8.5, 0, -2], to: [8.5, 4, 7], paint: bodyFur });
  m.cube(body, { name: 'body_top', from: [-5.5, 7, -1], to: [5.5, 8, 6], paint: bodyFur });

  // ----------------------------------------------------------------- head
  const head = m.bone('head', [0, 3, -4], { parent: body });
  const headEll = { c: [0, 4.5, -7.5], r: [9.5, 8, 7] };
  const headFur = fur(headEll);
  m.cube(head, { name: 'head_main', from: [-7.5, 0, -12], to: [7.5, 10, -3], paint: headFur });
  m.cube(head, { name: 'head_cheeks', from: [-8.5, 0, -11], to: [8.5, 6, -4], paint: headFur });
  m.cube(head, { name: 'head_top', from: [-6.5, 10, -11], to: [6.5, 11, -4], paint: headFur });

  // face painted onto the front of the head (15 x 10 texels, col 0 = viewer's left = the Pokemon's right)
  const FACE_ROWS = [
    '...............',
    '...............',
    '...............',
    '...............',
    '...............',
    '.L..L.....L..L.',
    '..LL.......LL..',
    '.BB..M.M.M..BB.',
    '......MMM......',
    '...............',
  ];
  const A = L.ALPHA_REDS;
  m.cubes.find((c) => c.name === 'head_main').alpha = (ctx) => (ctx.face === 'north' && FACE_ROWS[ctx.row][ctx.col] === 'L' ? A.mid.slice() : null);
  const faceAt = (ctx) => (ctx.cube.name === 'head_main' && ctx.face === 'north' ? FACE_ROWS[ctx.row][ctx.col] : '.');
  m.decal({
    cubes: ['head_main'], face: 'north',
    fn: (ctx, col) => {
      const ch = FACE_ROWS[ctx.row][ctx.col];
      if (ch === 'L') return ctx.pal.line.slice();
      if (ch === 'M') return ctx.pal.mouthLine.slice();
      if (ch === 'B') return L.mix(col, ctx.pal.blush, 0.55);
      return undefined;
    },
  });
  // colour of the face underneath an overlay plane: keeps blush, drops the closed eye / mouth lines
  const faceUnder = (ctx) => {
    const q = [ctx.p[0], ctx.p[1], -12];
    const post = ctx.sample('head_main', 'north', q, true);
    const pre = ctx.sample('head_main', 'north', q, false);
    const col = Math.round(7 - ctx.p[0]), row = Math.round(9.5 - ctx.p[1]);
    const ch = FACE_ROWS[row] && FACE_ROWS[row][col];
    return (ch === 'L' || ch === 'M') ? pre : post;
  };

  // open eyes: hidden just behind the face, animations push them 0.45 forward
  const eyes = m.bone('eyes', [0, 4, -11.5], { parent: head });
  const OPEN_EYE = [
    '.KK.',
    'KWKK',
    'KKHK',
    '.KK.',
  ];
  const eyePaint = (ctx) => {
    if (ctx.face !== 'north' && ctx.face !== 'south') return null;
    const col = ctx.face === 'south' ? 3 - ctx.col : ctx.col; // column as seen from the front
    const ch = OPEN_EYE[ctx.row][col];
    if (ch === 'K') return ctx.pal.eyeK.slice();
    if (ch === 'W') return ctx.pal.eyeW.slice();
    if (ch === 'H') return ctx.pal.eyeHi.slice();
    return faceUnder(ctx);
  };
  const eyeAlpha = (ctx) => {
    if (ctx.face !== 'north' && ctx.face !== 'south') return null;
    const col = ctx.face === 'south' ? 3 - ctx.col : ctx.col;
    return { K: A.deep, W: A.hi, H: A.lo }[OPEN_EYE[ctx.row][col]]?.slice() ?? null;
  };
  const eyeR = m.bone('eye_right', [4.5, 4, -11.5], { parent: eyes });
  m.cube(eyeR, { name: 'eye_right', from: [2.5, 2, -11.6], to: [6.5, 6, -11.6], paint: eyePaint, alpha: eyeAlpha });
  const eyeL = m.bone('eye_left', [-4.5, 4, -11.5], { parent: eyes });
  m.cube(eyeL, { name: 'eye_left', from: [-6.5, 2, -11.6], to: [-2.5, 6, -11.6], paint: eyePaint, alpha: eyeAlpha });

  // open mouth (hidden by default)
  const mouth = m.bone('mouth', [0, 2, -11.5], { parent: head });
  const MOUTH_OPEN = ['M.M.M', 'MPPPM', '.MTM.'];
  m.cube(mouth, {
    name: 'mouth_open', from: [-2.5, 1, -11.6], to: [2.5, 4, -11.6],
    paint: (ctx) => {
      if (ctx.face !== 'north' && ctx.face !== 'south') return null;
      const col = ctx.face === 'south' ? 4 - ctx.col : ctx.col;
      const ch = MOUTH_OPEN[ctx.row][col];
      if (ch === 'M') return ctx.pal.mouthLine.slice();
      if (ch === 'P') return ctx.pal.mouthIn.slice();
      if (ch === 'T') return ctx.pal.tongue.slice();
      return faceUnder(ctx);
    },
  });

  // forehead coin
  const coinF = m.bone('coin_forehead', [0, 7.5, -12], { parent: head });
  m.cube(coinF, { name: 'coin_forehead', from: [-2.5, 5, -12.5], to: [2.5, 10, -11.5], paint: coinPaint });

  // ears (2 thick stepped triangles, dark inner ear on the front)
  const earPaint = (sign) => {
    const earFur = fur({ c: [sign * 5, 9, -8], r: [5, 7, 4] });
    return (ctx) => {
      const base = earFur(ctx);
      if (ctx.face !== 'north') return base;
      const x = sign * ctx.lp[0], y = ctx.lp[1];
      const dx = Math.abs(x - 5);
      const inner = (y > 11 && y < 12 && dx < 2) || (y > 12 && y < 14 && dx < 1);
      if (!inner) return base;
      return pick(ctx.pal.earIn, clamp(0.2 + (y - 11) * 0.22, 0, 1), ctx, 0.4);
    };
  };
  for (const [side, sign] of [['right', 1], ['left', -1]]) {
    const ear = m.bone('ear_' + side, [sign * 5, 11, -9.5], { parent: head, rotation: [-8, sign * 8, sign * -12] });
    const span = (a, b) => (sign > 0 ? [a, b] : [-b, -a]);
    const [b0, b1] = span(2, 8), [m0, m1] = span(3, 7), [t0, t1] = span(4, 6);
    m.cube(ear, { name: `ear_${side}`, from: [b0, 10, -10], to: [b1, 12, -9], paint: earPaint(sign) });
    m.cube(ear, { name: `ear_${side}_mid`, from: [m0, 12, -10], to: [m1, 14, -9], paint: earPaint(sign) });
    m.cube(ear, { name: `ear_${side}_tip`, from: [t0, 14, -10], to: [t1, 15, -9], paint: earPaint(sign) });
    // back of the ear: a second layer so the ear has some thickness at the base
    m.cube(ear, { name: `ear_${side}_back`, from: [sign > 0 ? 2.5 : -7.5, 10, -9], to: [sign > 0 ? 7.5 : -2.5, 12, -8], paint: earPaint(sign) });
  }

  // ----------------------------------------------------------------- paws
  const pawPaint = (cx) => {
    const pawFur = fur({ c: [cx, 0.5, -13], r: [3.5, 3.5, 4] }, { wrap: 0.8 });
    return (ctx) => {
      const base = pawFur(ctx);
      const lx = Math.floor(ctx.lp[0] - ctx.cube.from[0]);
      const groove = lx === 1 || lx === 3; // three toes
      if (ctx.face === 'north' && groove && ctx.row <= 1) return ctx.pal.toe.slice();
      if (ctx.face === 'up' && groove && ctx.lp[2] < ctx.cube.from[2] + 1.5) return ctx.pal.toe.slice();
      return base;
    };
  };
  const armR = m.bone('arm_right', [5, 1.5, -11], { parent: body });
  m.cube(armR, { name: 'paw_right', from: [2.5, 0, -16], to: [7.5, 3, -11], paint: pawPaint(5) });
  const armL = m.bone('arm_left', [-5, 1.5, -11], { parent: body });
  m.cube(armL, { name: 'paw_left', from: [-7.5, 0, -16], to: [-2.5, 3, -11], paint: pawPaint(-5) });

  const hindPaint = (cx) => {
    const hindFur = fur({ c: [cx, 0.5, 3.5], r: [3, 3.5, 5] }, { wrap: 0.8 });
    return (ctx) => {
      const base = hindFur(ctx);
      const lx = Math.floor(ctx.lp[0] - ctx.cube.from[0]);
      if (ctx.face === 'north' && ctx.row <= 1 && lx === 1) return ctx.pal.toe.slice();
      if (ctx.face === 'up' && ctx.lp[2] < ctx.cube.from[2] + 1.5 && lx === 1) return ctx.pal.toe.slice();
      return base;
    };
  };
  const legR = m.bone('leg_right', [9, 1.5, 3], { parent: body });
  m.cube(legR, { name: 'hindpaw_right', from: [7.5, 0, 0], to: [10.5, 3, 6], paint: hindPaint(9) });
  const legL = m.bone('leg_left', [-9, 1.5, 3], { parent: body });
  m.cube(legL, { name: 'hindpaw_left', from: [-10.5, 0, 0], to: [-7.5, 3, 6], paint: hindPaint(-9) });

  // ----------------------------------------------------------------- tail (curl with an orange tip)
  const tailPaint = (orangeAt) => (ctx) => {
    const d = ctx.n[0] * KEY[0] + ctx.n[1] * KEY[1] + ctx.n[2] * KEY[2];
    const nz = (L.vnoise(ctx.p, 1.8, 5) - 0.5) * 0.32;
    let v = 0.45 + d * 0.35 + nz;
    // soften towards the edges of each face so the segments read rounder
    const e = Math.min(ctx.s, 1 - ctx.s, ctx.t, 1 - ctx.t) * Math.min(ctx.W, ctx.H);
    if (e < 0.6 && Math.min(ctx.W, ctx.H) > 2) v -= 0.08;
    const cream = pick(ctx.pal.cream, clamp(v + 0.08, 0, 1), ctx, 0.45);
    const t = orangeAt(ctx.p, ctx.lp);
    if (t <= 0) return cream;
    const orange = pick(ctx.pal.tail, clamp(v, 0, 1), ctx, 0.45);
    return t + (L.bayer(ctx.tu, ctx.tv) - 0.5) * 0.8 > 0.5 ? orange : cream;
  };
  // four segments, each rotated further so the tail spirals up and over into a curl
  const tail = m.bone('tail', [4, 4.5, 8], { parent: body, rotation: [-40, 0, 0] });
  m.cube(tail, { name: 'tail', from: [2.5, 3, 7.5], to: [5.5, 6, 11.5], paint: tailPaint(() => 0) });
  const tail2 = m.bone('tail2', [4, 4.5, 11.5], { parent: tail, rotation: [-50, 0, 0] });
  m.cube(tail2, { name: 'tail2', from: [2.5, 3, 11], to: [5.5, 6, 14], paint: tailPaint((p, lp) => (lp[2] - 13.2) / 1.2) });
  const tail3 = m.bone('tail3', [4, 4.5, 14], { parent: tail2, rotation: [-55, 0, 0] });
  m.cube(tail3, { name: 'tail3', from: [2, 2.5, 13.5], to: [6, 6.5, 17.5], paint: tailPaint(() => 1) });
  const tail4 = m.bone('tail4', [4, 4.5, 17.5], { parent: tail3, rotation: [-65, 0, 0] });
  m.cube(tail4, { name: 'tail4', from: [2.5, 3, 17], to: [5.5, 6, 19], paint: tailPaint(() => 1) });
  m.locator(tail3, 'tail_tip', [4, 4.5, 16]);
  m.locator(tail, 'tail', [4, 4.5, 10]);

  // ----------------------------------------------------------------- floating coins
  const coins = m.bone('coins', [0, 18.5, -6], { parent: body });
  const coinDefs = [['coin_left', -6.5, 17.5], ['coin_middle', 0, 20], ['coin_right', 6.5, 17.5]];
  let firstCoin = null;
  for (const [nm, x, y] of coinDefs) {
    const b = m.bone(nm, [x, y, -6], { parent: coins });
    const c = m.cube(b, { name: nm, from: [x - 2.5, y - 2.5, -6.5], to: [x + 2.5, y + 2.5, -5.5], paint: coinPaint, uvShare: firstCoin || undefined });
    if (!firstCoin) firstCoin = c;
  }

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 23, -6]);
  m.locator(body, 'middle', [0, 5, 0]);
  m.locator(body, 'target', [0, 5, -12]);
  m.locator(head, 'head', [0, 11, -8]);
  m.locator(head, 'face', [0, 4, -12]);
  m.locator(head, 'item_face', [0, 4, -12.5]);
  m.locator(head, 'item_hat', [0, 11, -7.5]);
  m.locator(head, 'mouth', [0, 2, -12]);
  m.locator(head, 'eye_right', [4.5, 4, -12]);
  m.locator(head, 'eye_left', [-4.5, 4, -12]);
  m.locator(armR, 'hand_primary', [5, 1.5, -16], { extra: ['physical'] });
  m.locator(armL, 'hand_secondary', [-5, 1.5, -16]);
  m.locator(armR, 'item', [5, 1, -17]);
  m.locator(coins, 'special', [0, 20, -6]);

  require('./babymeowth.anim')(m);
  return m;
}

module.exports = { ID, build, PALETTES };
