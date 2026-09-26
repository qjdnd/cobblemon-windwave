// Baby Psyduck (pre-evolution of Psyduck): a tiny yellow duckling under a big
// round white egg-shell head with a black swirl on the forehead, round black
// eyes, a cream bill, orange blush, stubby arms held together in front of the
// belly and cream feet.
//
// Colours come straight from Cobblemon's Psyduck texture (0054_psyduck):
// the 5-step body and bill ramps, mouth, eye and hair colours, and the shiny
// ramps from psyduck_shiny.png. The white egg-shell head is new.
'use strict';
const L = require('../../lib');
const { Model, hex, makeRamp, pick, clamp, smooth, ellipsoidLight, norm3 } = L;

const ID = 'babypsyduck';

const PSYDUCK = {
  body: ['#cd8652', '#dc9b5b', '#eab165', '#f9c772', '#ffdb7d'],
  bill: ['#c4ab93', '#d3bfa3', '#e2d3b3', '#f0e6c2', '#fffad3'],
  shinyBody: ['#5a9ba2', '#6aaeb4', '#7bc2c7', '#8ed8dc', '#9ee9e7'],
  shinyBill: ['#96bdbd', '#abcfd2', '#c0dee5', '#d4eef9', '#e9ffff'],
};
const shared = {
  mouth: makeRamp(['#5f3131', '#733f3f', '#874d4d', '#9b5e5e'], 4),
  tongue: hex('#ceaac2'),
  tongueHi: hex('#ddb9d4'),
  eyeK: hex('#131313'),
  eyeHi: hex('#f8f8f8'),
  swirl: hex('#1d1d1d'),
  swirlHi: hex('#313131'),
  lid: hex('#272727'),
};
const PALETTES = {
  base: {
    ...shared,
    body: PSYDUCK.body.map((c) => hex(c)),
    bill: PSYDUCK.bill.map((c) => hex(c)),
    // cool white egg shell, pale blue in the shade like the concept art
    shell: makeRamp(['#9aabc2', '#b6c5d7', '#cfdbe7', '#e3ebf2', '#f2f6f9', '#fdfeff'], 6),
    blush: hex('#f39a5e'),
  },
  shiny: {
    ...shared,
    body: PSYDUCK.shinyBody.map((c) => hex(c)),
    bill: PSYDUCK.shinyBill.map((c) => hex(c)),
    // warm cream shell so the pale blue bill still stands out
    shell: makeRamp(['#c2a987', '#d8c3a2', '#e8dbbf', '#f3ead4', '#faf5e6', '#fffdf6'], 6),
    blush: hex('#f28fa6'),
  },
};

// light from the front-top (symmetric left/right so it reads well at any yaw)
const KEY = norm3([0, 0.85, -0.75]);

// Psyduck-style mottled shading: rounded light + soft blotches, quantised to the ramp
function mottled(rampName, ell, opts = {}) {
  return (ctx) => {
    const { l } = ellipsoidLight(ctx.p, ell.c, ell.r, KEY, opts.wrap ?? 0.7);
    let v = (opts.base ?? 0.34) + l * (opts.gain ?? 0.6);
    if (opts.shade) v -= opts.shade(ctx.p) || 0;
    if (ctx.face === 'down') v -= 0.2;
    v += (L.vnoise(ctx.p, opts.scale ?? 1.7, opts.seed ?? 11) - 0.5) * (opts.noise ?? 0.4);
    v += (L.hash3(Math.floor(ctx.p[0] * 2 + 99), Math.floor(ctx.p[1] * 2 + 99), Math.floor(ctx.p[2] * 2 + 99), 3) - 0.5) * (opts.grain ?? 0.1);
    return pick(ctx.pal[rampName], clamp(v, 0, 1), ctx, opts.dither ?? 0.45);
  };
}

// ------------------------------------------------------------------ face
// Front of the head (the face plate): 12 x 14 texels, x from +6 (col 0, the
// Pokemon's right = viewer's left) to -6, y from 24 (row 0) down to 10.
// The swirl plane covers rows 0-5; the bill covers rows 11-12 of cols 3-8 and
// the lower bill row 13 of cols 4-7 (the 'M' texels are the throat).
const FACE = [
  '............',
  '............',
  '............',
  '............',
  '............',
  '............',
  '............',
  '.KK......KK.',
  'KWKK....KWKK',
  'KKKK....KKKK',
  '.KK......KK.',
  'bBbMMMMMMbBb',
  '.b.MMMMMM.b.',
  '....MMMM....',
];
// 6 x 6 swirl on a plane just in front of the forehead (as seen from the front)
const SWIRL = [
  '..KKK.',
  '.K...K',
  'K..K.K',
  'K.K..K',
  'K..KK.',
  '.K....',
];
// expression overlays, 4 x 4 texels per eye (same size as the open eye they cover)
const CLOSED = ['....', '....', 'S..S', '.SS.'];
const HAPPY = ['....', '.SS.', 'S..S', '....'];
const DIZZY = ['S..S', '.SS.', '.SS.', 'S..S'];

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 64, visibleBox: [2, 2.5, 0.75], palettes: PALETTES });
  const A = L.ALPHA_REDS;
  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', [0, 2, 0], { parent: root });

  // ----------------------------------------------------------------- torso
  const torso = m.bone('torso', [0, 5, 0], { parent: body });
  const bodyEll = { c: [0, 6, -0.5], r: [6, 6, 5] };
  // shadow under the head overhang and at the ground
  const torsoShade = (p) => 0.26 * smooth(6, 9, p[1]) + 0.22 * (1 - smooth(2, 3.5, p[1]));
  const torsoPaint = mottled('body', bodyEll, { shade: torsoShade });
  m.cube(torso, { name: 'torso', from: [-4.5, 2, -3.5], to: [4.5, 11, 3.5], paint: torsoPaint });
  m.cube(torso, { name: 'torso_hips', from: [-5, 2, -3], to: [5, 8, 3], paint: torsoPaint });
  m.cube(torso, { name: 'belly', from: [-3.5, 3, -4.5], to: [3.5, 8, -3.5], paint: torsoPaint });

  // ----------------------------------------------------------------- head (egg shell)
  // a stepped ball: the face plate plus three wider, shallower boxes and two caps
  const head = m.bone('head', [0, 9, 0], { parent: torso });
  const headEll = { c: [0, 17.5, 0], r: [8.5, 8.5, 7] };
  // pale blue towards the bottom of the shell, like the concept art
  const shellShade = (p) => 0.2 * (1 - smooth(9, 15, p[1]));
  const shellPaint = mottled('shell', headEll, { base: 0.5, gain: 0.52, noise: 0.12, grain: 0.05, scale: 1.6, seed: 21, dither: 0.35, shade: shellShade });
  m.cube(head, { name: 'head', from: [-6, 10, -7], to: [6, 24, 6], paint: shellPaint });
  m.cube(head, { name: 'head_mid', from: [-7, 10, -6], to: [7, 24, 6], paint: shellPaint });
  m.cube(head, { name: 'head_wide', from: [-8, 13, -5], to: [8, 22, 5], paint: shellPaint });
  m.cube(head, { name: 'head_back', from: [-5, 12, 6], to: [5, 22, 7], paint: shellPaint });
  m.cube(head, { name: 'head_top', from: [-5, 24, -5], to: [5, 25, 5], paint: shellPaint });
  m.cube(head, { name: 'head_crown', from: [-3, 25, -3], to: [3, 26, 3], paint: shellPaint });
  m.cube(head, { name: 'head_bottom', from: [-5, 9, -5], to: [5, 10, 5], paint: shellPaint });

  const faceCh = (ctx) => (ctx.face === 'north' ? FACE[ctx.row][ctx.col] : '.');
  m.decal({
    cubes: ['head'], face: 'north',
    fn: (ctx, col) => {
      const P = ctx.pal;
      switch (faceCh(ctx)) {
        case 'K': return P.eyeK.slice();
        case 'W': return P.eyeHi.slice();
        case 'B': return L.mix(col, P.blush, 0.8);
        case 'b': return L.mix(col, P.blush, 0.45);
        case 'M': return P.mouth[0].slice(); // throat, only seen when the bill opens
        default: return undefined;
      }
    },
  });
  m.cubes.find((c) => c.name === 'head').alpha = (ctx) => (
    { K: A.deep, W: A.hi }[faceCh(ctx)]?.slice() ?? null
  );
  // bare shell colour under an overlay plane (before the eyes were painted on)
  const under = (ctx) => ctx.sample('head', 'north', [ctx.p[0], ctx.p[1], -7]);

  // forehead swirl: its own plane so it can spin
  const swirl = m.bone('swirl', [0, 21, -7], { parent: head });
  m.cube(swirl, {
    name: 'swirl', from: [-3, 18, -7.05], to: [3, 24, -7.05],
    paint: (ctx) => {
      if (ctx.face !== 'north') return null;
      if (SWIRL[ctx.row][ctx.col] !== 'K') return null;
      // lighter texels on the upper left of the stroke, like Psyduck's hair
      return (ctx.row + ctx.col < 4 ? ctx.pal.swirlHi : ctx.pal.swirl).slice();
    },
  });

  // expression overlays: hidden just inside the head, animations slide them 0.45 forward
  // only the front is painted: a transparent back can't z-fight with the front of the same plane
  const overlay = (rows) => (ctx) => {
    if (ctx.face !== 'north') return null;
    if (rows[ctx.row][ctx.col] === 'S') return ctx.pal.lid.slice();
    return under(ctx);
  };
  const eyeSet = (name, rows, z) => {
    const b = m.bone(name, [0, 15, z], { parent: head });
    m.cube(b, { name: name + '_right', from: [2, 13, z], to: [6, 17, z], paint: overlay(rows) });
    m.cube(b, { name: name + '_left', from: [-6, 13, z], to: [-2, 17, z], paint: overlay(rows) });
    return b;
  };
  eyeSet('eyes_closed', CLOSED, -6.6);
  eyeSet('eyes_happy', HAPPY, -6.65);
  eyeSet('eyes_dizzy', DIZZY, -6.7);

  // ----------------------------------------------------------------- bill
  const billEll = { c: [0, 12.5, -8], r: [3.5, 1.6, 3] };
  const billTop = mottled('bill', billEll, { base: 0.42, gain: 0.55, noise: 0.28, scale: 1.4, seed: 5 });
  const beak = m.bone('beak', [0, 12, -7], { parent: head });
  m.cube(beak, {
    name: 'bill', from: [-3, 11, -10], to: [3, 13, -6],
    paint: (ctx) => {
      if (ctx.face === 'down') return pick(ctx.pal.mouth, 0.3 + (ctx.lp[2] + 10) * 0.12, ctx, 0.5); // roof of the mouth
      return billTop(ctx);
    },
  });
  const jaw = m.bone('jaw', [0, 11, -7], { parent: beak });
  const jawPaint = mottled('bill', { c: [0, 11, -8], r: [3, 1.5, 2.5] }, { base: 0.25, gain: 0.5, noise: 0.28, scale: 1.4, seed: 6 });
  m.cube(jaw, {
    name: 'jaw', from: [-2, 10, -9.5], to: [2, 11, -6.5],
    paint: (ctx) => {
      if (ctx.face !== 'up') return jawPaint(ctx);
      const x = Math.abs(ctx.lp[0]), z = ctx.lp[2];
      if (x < 1 && z < -7.5) return ((ctx.tu + ctx.tv) % 2 ? ctx.pal.tongue : ctx.pal.tongueHi).slice();
      return ctx.pal.mouth[z < -8.5 ? 2 : 1].slice();
    },
  });

  // ----------------------------------------------------------------- arms (held together in front of the belly)
  const armPaint = mottled('body', { c: [0, 6.5, -3], r: [6, 4, 5] }, { shade: (p) => 0.12 * smooth(7, 9, p[1]) });
  const handPaint = (cx) => mottled('bill', { c: [cx, 7, -6], r: [2, 2, 2] }, { base: 0.4, gain: 0.55, noise: 0.25, scale: 1.2, seed: 9 });
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    const arm = m.bone('arm_' + side, [s * 4, 8, -2], { parent: torso, rotation: [-24, s * 38, s * -6] });
    m.cube(arm, { name: 'arm_' + side, from: s > 0 ? [3, 7, -6] : [-5, 7, -6], to: s > 0 ? [5, 9, -2] : [-3, 9, -2], paint: armPaint });
    const hand = m.bone('hand_' + side, [s * 4, 8, -6], { parent: arm });
    m.cube(hand, { name: 'hand_' + side, from: s > 0 ? [3, 7, -8] : [-5, 7, -8], to: s > 0 ? [5, 9, -6] : [-3, 9, -6], paint: handPaint(s * 4) });
  }

  // ----------------------------------------------------------------- tail
  const tailPaint = mottled('body', { c: [0, 4, 4], r: [2.5, 2, 3.5] });
  const tail = m.bone('tail', [0, 4, 3], { parent: torso, rotation: [-22, 0, 0] });
  m.cube(tail, { name: 'tail', from: [-1.5, 3, 2.5], to: [1.5, 5, 5.5], paint: tailPaint });
  const tail2 = m.bone('tail2', [0, 4, 5.5], { parent: tail, rotation: [-12, 0, 0] });
  m.cube(tail2, { name: 'tail2', from: [-1, 3.5, 5], to: [1, 4.5, 7], paint: tailPaint });

  // ----------------------------------------------------------------- feet
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    const foot = m.bone('foot_' + side, [s * 2.5, 1.5, -0.5], { parent: body, rotation: [0, s * -12, 0] });
    const x0 = s * 2.5;
    m.cube(foot, { name: 'leg_' + side, from: [x0 - 1, 1, -1.5], to: [x0 + 1, 3, 0.5], paint: mottled('body', { c: [x0, 2, -0.5], r: [2, 2, 2] }, { shade: (p) => 0.2 * (1 - smooth(1, 2.5, p[1])) }) });
    const feetCream = mottled('bill', { c: [x0, 0.5, -2], r: [3, 1.5, 3] }, { base: 0.36, gain: 0.55, noise: 0.25, scale: 1.3, seed: 7 });
    m.cube(foot, {
      name: 'foot_' + side, from: [x0 - 2.5, 0, -4], to: [x0 + 2.5, 1, 0],
      paint: (ctx) => {
        // three webbed toes: darker grooves between them on the front and the tip of the top
        const lx = Math.floor(ctx.lp[0] - ctx.cube.from[0]);
        const groove = (lx === 1 || lx === 3) && (ctx.face === 'north' || (ctx.face === 'up' && ctx.lp[2] < -3));
        return groove ? ctx.pal.bill[0].slice() : feetCream(ctx);
      },
    });
  }

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 27, 0]);
  m.locator(torso, 'middle', [0, 12, 0]);
  m.locator(head, 'target', [0, 15, -7.5]);
  m.locator(head, 'head', [0, 26, 0], { extra: ['item_hat'] });
  m.locator(head, 'face', [0, 15, -7], { extra: ['item_face'] });
  m.locator(beak, 'mouth', [0, 11, -10]);
  m.locator(head, 'eye_right', [3.5, 15, -7]);
  m.locator(head, 'eye_left', [-3.5, 15, -7]);
  m.locator(swirl, 'special', [0, 21, -7.5]);
  // hand locators use the arms' unrotated coordinates; they follow the arm bones' rotation
  m.locator(m.boneMap.hand_right, 'hand_primary', [4, 8, -8], { extra: ['physical'] });
  m.locator(m.boneMap.hand_left, 'hand_secondary', [-4, 8, -8]);
  m.locator(m.boneMap.hand_right, 'item', [4, 7.5, -8.5]);
  m.locator(tail2, 'tail', [0, 4, 6.5]);

  require('./anims')(m);
  return m;
}

module.exports = { ID, build, PALETTES, FACE, SWIRL };
