// Swirlduck (working name): the other evolution of Psyduck, next to Golduck in the concept art.
// A yellow Psyduck body under a big white spiked shell helmet (the baby's egg shell grown up)
// with blue swirls and a gold gem, a white-and-blue feather cape on the shoulders, blue swirls
// on the belly, Psyduck's dazed eyes and a wide-open laughing bill, three-fingered hands and a
// pointed tail.
//
// Body, bill, mouth, eye and claw colours come straight from Cobblemon's Psyduck texture
// (0054_psyduck), the shiny ones from psyduck_shiny.png. The shell, swirls, cape and gem are new.
'use strict';
const L = require('../../lib');
const { Model, hex, makeRamp, pick, clamp, smooth, ellipsoidLight, norm3 } = L;

const ID = 'swirlduck';

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
  eyeW: [hex('#dfdfdf'), hex('#eeeeee'), hex('#f8f8f8')],
  pupil: hex('#131313'),
  lid: hex('#5f3131'),
};
const PALETTES = {
  base: {
    ...shared,
    body: PSYDUCK.body.map((c) => hex(c)),
    bill: PSYDUCK.bill.map((c) => hex(c)),
    shell: makeRamp(['#9aabc2', '#b6c5d7', '#cfdbe7', '#e3ebf2', '#f2f6f9', '#fdfeff'], 6),
    swirl: makeRamp(['#3d78b8', '#4f8fcf', '#66a6df', '#84bce9'], 4),
    gem: makeRamp(['#b8742c', '#dc9b5b', '#f9c772', '#ffe39a', '#fff8dc'], 5),
    ring: hex('#8fa3bb'),
  },
  shiny: {
    ...shared,
    body: PSYDUCK.shinyBody.map((c) => hex(c)),
    bill: PSYDUCK.shinyBill.map((c) => hex(c)),
    // same idea as the shiny baby: warm cream shell; the blue and gold swap places
    shell: makeRamp(['#c2a987', '#d8c3a2', '#e8dbbf', '#f3ead4', '#faf5e6', '#fffdf6'], 6),
    swirl: makeRamp(['#b86a26', '#d6862f', '#eaa446', '#f6c26a'], 4),
    gem: makeRamp(['#2f5f9e', '#4f8fcf', '#72b0e8', '#a6d4f7', '#e6f5ff'], 5),
    ring: hex('#b39c7c'),
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

// 5 x 5 swirl (as seen from outside the face it is painted on), a smaller cousin of the baby's forehead swirl
const CURL5 = ['.BBB.', 'B...B', 'B.B.B', 'B.BB.', '.B...'];
const flipRows = (rows) => rows.map((r) => r.split('').reverse().join(''));

// Front of the head: 12 x 10 texels, x from +6 (col 0, the Pokemon's right) to -6, y from 27 (row 0)
// down to 17. Rows 0-3 are under the shell; the eyes (3 x 2, Psyduck's) sit just under its rim, the
// bill covers cols 3-8 of rows 6-7 and the jaw rows 8-9; 'M' is the throat seen when the bill opens.
const FACE = [
  '............',
  '............',
  '............',
  '............',
  '.WWW....WWW.',
  '.wWw....wWw.',
  '...MMMMMM...',
  '...MMMMMM...',
  '...MMMMMM...',
  '...MMMMMM...',
];
// expression overlays, 3 x 2 texels per eye (the size of the eye they cover)
const CLOSED = ['...', 'SSS'];
const HAPPY = ['.S.', 'S.S'];
const DIZZY = ['S.S', '.S.'];

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 128, visibleBox: [3, 3, 1.1], palettes: PALETTES, emissive: true });
  const A = L.ALPHA_REDS;

  // Left/right pairs: the right side (+x) is modelled and painted, the left side mirrors it and
  // shares its texture (Box UV mirror), like a mirrored cube in Blockbench.
  const mirrorBox = (from, to) => ({ from: [-to[0], from[1], from[2]], to: [-from[0], to[1], to[2]] });
  function symmetric(buildSide) {
    const right = [];
    buildSide(1, (bone, spec) => { const c = m.cube(bone, spec); right.push(c); return c; });
    let i = 0;
    buildSide(-1, (bone, spec) => m.cube(bone, { name: spec.name, ...mirrorBox(spec.from, spec.to), uvShare: right[i++], mirror: true }));
  }
  const P = (s, v) => [v[0] * s, v[1], v[2]];
  const R = (s, v) => [v[0], v[1] * s, v[2] * s];
  const side = (s) => (s > 0 ? 'right' : 'left');

  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', [0, 9, 0], { parent: root });

  // ----------------------------------------------------------------- torso (pear-shaped, belly swirls)
  const torso = m.bone('torso', [0, 9, 0], { parent: body });
  const torsoEll = { c: [0, 10.5, -0.5], r: [8, 8.5, 6] };
  const torsoShade = (p) => 0.18 * smooth(15, 18, p[1]) + 0.2 * (1 - smooth(4.5, 7, p[1]));
  const torsoPaint = mottled('body', torsoEll, { shade: torsoShade });
  m.cube(torso, { name: 'belly', from: [-6.5, 5, -4.5], to: [6.5, 13, 4.5], paint: torsoPaint });
  m.cube(torso, { name: 'belly_front', from: [-5, 6, -5.5], to: [5, 13, -4.5], paint: torsoPaint });
  m.cube(torso, { name: 'hips', from: [-5.5, 4, -4], to: [5.5, 5, 4], paint: torsoPaint });
  m.cube(torso, { name: 'chest', from: [-5.5, 13, -4], to: [5.5, 17, 4], paint: torsoPaint });
  m.cube(torso, { name: 'neck', from: [-4, 17, -3.5], to: [4, 19, 3.5], paint: torsoPaint });
  // two blue swirls on the belly, curling towards the middle
  const bellySwirl = (ctx, col) => {
    const c0 = ctx.col <= 4 ? 0 : 5, rows = ctx.col <= 4 ? CURL5 : flipRows(CURL5);
    const r = ctx.row - 1, c = ctx.col - c0;
    if (r < 0 || r > 4 || rows[r][c] !== 'B') return undefined;
    return pick(ctx.pal.swirl, 0.35 + (4 - r) * 0.12, ctx, 0.3);
  };
  m.decal({ cubes: ['belly_front'], face: 'north', fn: bellySwirl });

  // ----------------------------------------------------------------- head (Psyduck's face)
  const head = m.bone('head', [0, 18, -0.5], { parent: torso });
  const headEll = { c: [0, 21, -1], r: [7.5, 7, 6.5] };
  const headPaint = mottled('body', headEll, { shade: (p) => 0.14 * (1 - smooth(16, 19, p[1])) });
  m.cube(head, { name: 'head', from: [-6, 17, -6], to: [6, 27, 4], paint: headPaint });
  m.cube(head, { name: 'chin', from: [-5, 16, -5], to: [5, 17, 3], paint: headPaint });
  const faceCh = (ctx) => (ctx.face === 'north' ? FACE[ctx.row][ctx.col] : '.');
  m.decal({
    cubes: ['head'], face: 'north',
    fn: (ctx) => {
      const P = ctx.pal;
      switch (faceCh(ctx)) {
        case 'W': return P.eyeW[ctx.row === 4 ? 2 : 1].slice();
        case 'w': return P.eyeW[0].slice();
        case 'M': return P.mouth[ctx.row >= 8 ? 0 : 1].slice(); // throat, seen through the open bill
        default: return undefined;
      }
    },
  });
  m.cubes.find((c) => c.name === 'head').alpha = (ctx) => ({ W: A.lo, w: A.deep }[faceCh(ctx)]?.slice() ?? null);
  const under = (ctx) => ctx.sample('head', 'north', [ctx.p[0], ctx.p[1], -6]);

  // pupils: rolled up to the top of the eyes like Psyduck's dazed stare; they move in the animations
  for (const s of [1, -1]) {
    const pu = m.bone('pupil_' + side(s), P(s, [3.5, 22.5, -6]), { parent: head });
    m.cube(pu, {
      name: 'pupil_' + side(s), from: s > 0 ? [3, 22, -6.05] : [-4, 22, -6.05], to: s > 0 ? [4, 23, -6.05] : [-3, 23, -6.05],
      paint: (ctx) => (ctx.face === 'north' ? ctx.pal.pupil.slice() : null),
      alpha: (ctx) => (ctx.face === 'north' ? A.hi.slice() : null),
    });
  }
  // expression overlays: hidden just inside the face, animations slide them 0.5 forward
  const overlay = (rows) => (ctx) => {
    if (ctx.face !== 'north') return null;
    if (rows[ctx.row][ctx.col] === 'S') return ctx.pal.lid.slice();
    return under(ctx);
  };
  const eyeSet = (name, rows, z) => {
    const b = m.bone(name, [0, 22, z], { parent: head });
    m.cube(b, { name: name + '_right', from: [2, 21, z], to: [5, 23, z], paint: overlay(rows) });
    m.cube(b, { name: name + '_left', from: [-5, 21, z], to: [-2, 23, z], paint: overlay(rows) });
  };
  eyeSet('eyes_closed', CLOSED, -5.6);
  eyeSet('eyes_happy', HAPPY, -5.65);
  eyeSet('eyes_dizzy', DIZZY, -5.7);

  // ----------------------------------------------------------------- bill (open in a goofy laugh at rest)
  const beak = m.bone('beak', [0, 19, -6], { parent: head });
  const billPaint = mottled('bill', { c: [0, 20.5, -8.5], r: [4, 2, 5] }, { base: 0.42, gain: 0.55, noise: 0.28, scale: 1.4, seed: 5 });
  m.cube(beak, {
    name: 'bill', from: [-3, 19, -12.5], to: [3, 21, -5.5],
    paint: (ctx) => {
      if (ctx.face === 'down') return pick(ctx.pal.mouth, 0.25 + (ctx.lp[2] + 12.5) * 0.08, ctx, 0.5); // roof of the mouth
      // nostrils near the base
      if (ctx.face === 'up' && Math.abs(Math.abs(ctx.lp[0]) - 1.5) < 0.5 && ctx.lp[2] > -8.5 && ctx.lp[2] < -7.5) return ctx.pal.bill[0].slice();
      return billPaint(ctx);
    },
  });
  m.cube(beak, { name: 'bill_tip', from: [-2.5, 20, -13.5], to: [2.5, 21, -12.5], paint: billPaint });
  const jaw = m.bone('jaw', [0, 19, -6], { parent: beak, rotation: [-20, 0, 0] });
  const jawPaint = mottled('bill', { c: [0, 17.5, -8.5], r: [4, 2, 4] }, { base: 0.26, gain: 0.5, noise: 0.28, scale: 1.4, seed: 6 });
  m.cube(jaw, {
    name: 'jaw', from: [-3, 17, -11.5], to: [3, 19, -5.5],
    paint: (ctx) => {
      if (ctx.face !== 'up') return jawPaint(ctx);
      const x = Math.abs(ctx.lp[0]), z = ctx.lp[2];
      if (x > 2) return jawPaint(ctx); // rim of the lower bill
      if (x < 1.5 && z < -6.5 && z > -10.5) return ((ctx.tu + ctx.tv) % 2 ? ctx.pal.tongue : ctx.pal.tongueHi).slice();
      return ctx.pal.mouth[z < -9.5 ? 3 : 1].slice();
    },
  });

  // ----------------------------------------------------------------- shell helmet
  const shell = m.bone('shell', [0, 24, 0], { parent: head });
  const shellEll = { c: [0, 27, 0], r: [10, 10, 9] };
  const shellShade = (p) => 0.18 * (1 - smooth(19, 25, p[1]));
  const shellPaint = mottled('shell', shellEll, { base: 0.5, gain: 0.52, noise: 0.12, grain: 0.05, scale: 1.6, seed: 21, dither: 0.35, shade: shellShade });
  m.cube(shell, { name: 'shell', from: [-8, 23, -7.5], to: [8, 31, 7.5], paint: shellPaint });
  m.cube(shell, { name: 'shell_wide', from: [-9, 24, -6.5], to: [9, 30, 6.5], paint: shellPaint });
  m.cube(shell, { name: 'shell_upper', from: [-7, 31, -6.5], to: [7, 33, 6.5], paint: shellPaint });
  m.cube(shell, { name: 'shell_top', from: [-5, 33, -5], to: [5, 35, 5], paint: shellPaint });
  m.cube(shell, { name: 'shell_crown', from: [-3, 35, -3], to: [3, 36, 3], paint: shellPaint });
  m.cube(shell, { name: 'shell_back', from: [-6, 18, 5], to: [6, 23, 7], paint: shellPaint });
  // hood sides framing the face, with a blue rim along the face opening
  const wallPaint = (ctx) => {
    if (ctx.face === 'north' && ctx.col === 1) return pick(ctx.pal.swirl, 0.55, ctx, 0.2); // inner edge (col 1 = x 6..7)
    return shellPaint(ctx);
  };
  symmetric((s, cube) => cube(shell, { name: 'shell_side_' + side(s), from: [6, 18, -6.5], to: [8, 23, 6.5], paint: wallPaint }));

  // swirls around the dome and the blue rim over the face opening
  const curlAt = (rows, c0, r0) => (ctx) => {
    const r = ctx.row - r0, c = ctx.col - c0;
    if (r < 0 || c < 0 || r >= rows.length || c >= rows[0].length || rows[r][c] !== 'B') return false;
    return true;
  };
  const swirlCol = (ctx) => pick(ctx.pal.swirl, clamp(0.25 + (ctx.p[1] - 23) * 0.06, 0, 1), ctx, 0.3);
  // shell front (16 x 8, col 0 = x 8, row 0 = y 31): a curl either side of the gem, rim on the bottom row
  const frontCurls = [curlAt(CURL5, 1, 1), curlAt(flipRows(CURL5), 10, 1)];
  // shell back (seen from behind, col 0 = x -8): a curl low in each corner, curling outwards
  // (a centred pair would read as a second face)
  const backCurls = [curlAt(flipRows(CURL5), 0, 3), curlAt(CURL5, 11, 3)];
  // sides of shell_wide (13 x 6, row 0 = y 30; the front is col 12 on the east face, col 0 on the west): one curl each, near the front
  const sideCurl = { east: curlAt(flipRows(CURL5), 7, 0), west: curlAt(CURL5, 1, 0) };
  const GEM_C = [0, 29];
  m.decal({
    cubes: ['shell'], face: 'north',
    fn: (ctx) => {
      if (ctx.row === 7 && ctx.col >= 2 && ctx.col <= 13) return pick(ctx.pal.swirl, 0.55, ctx, 0.2);
      if (frontCurls.some((f) => f(ctx))) return swirlCol(ctx);
      // thin ring around the gem
      const d = Math.hypot(ctx.p[0] - GEM_C[0], ctx.p[1] - GEM_C[1]);
      if (d > 1.9 && d < 2.6) return ctx.pal.ring.slice();
      return undefined;
    },
  });
  m.decal({ cubes: ['shell'], face: 'south', fn: (ctx) => (backCurls.some((f) => f(ctx)) ? swirlCol(ctx) : undefined) });
  m.decal({
    cubes: ['shell_wide'],
    fn: (ctx) => (sideCurl[ctx.face] && sideCurl[ctx.face](ctx) ? swirlCol(ctx) : undefined),
  });

  // gold gem on the front of the dome (glows: emissive layer)
  const gem = m.bone('gem', [0, 29, -8], { parent: shell });
  const gemPaint = (ctx) => {
    if (ctx.face === 'south') return null;
    if (ctx.face !== 'north') return pick(ctx.pal.gem, 0.3, ctx, 0.2);
    const k = [[1, 2, 1], [2, 4, 3], [1, 3, 1]][ctx.row][ctx.col];
    return ctx.pal.gem[k].slice();
  };
  m.cube(gem, { name: 'gem', from: [-1.5, 27.5, -8.5], to: [1.5, 30.5, -7.5], paint: gemPaint, emissive: gemPaint });

  // spikes: three per side, stacked boxes narrowing to a point along the bone's +x
  const spikePaint = mottled('shell', { c: [0, 27, 0], r: [16, 12, 10] }, { base: 0.5, gain: 0.5, noise: 0.1, grain: 0.04, seed: 22, dither: 0.3 });
  const spike = (s, cube, name, pivot, rot, segs) => {
    const b = m.bone(`${name}_${side(s)}`, P(s, pivot), { parent: shell, rotation: R(s, rot) });
    let x = pivot[0];
    segs.forEach(([len, h, d], i) => {
      cube(b, { name: `${name}_${side(s)}${i ? '_' + i : ''}`, from: [x, pivot[1] - h / 2, pivot[2] - d / 2], to: [x + len, pivot[1] + h / 2, pivot[2] + d / 2], paint: spikePaint });
      x += len;
    });
    return b;
  };
  symmetric((s, cube) => {
    spike(s, cube, 'spike_top', [5.5, 32, 0], [0, 0, 46], [[2, 5, 3], [2, 4, 2], [2, 2, 1], [1, 1, 1]]);
    spike(s, cube, 'spike_side', [8.5, 26, -0.5], [0, 8, 6], [[2, 5, 3], [2, 4, 2], [2, 2, 1], [1, 1, 1]]);
    spike(s, cube, 'spike_low', [7.5, 19.5, -1.5], [0, 12, -38], [[2, 2, 2], [2, 1, 1]]);
  });

  // ----------------------------------------------------------------- cape: feather collar and shoulder capelets
  // a blue stripe along the middle of the top of each feather, white towards the tip
  const featherPaint = (ctx) => {
    if (ctx.face !== 'up') return spikePaint(ctx);
    const c = ctx.cube;
    const along = c.to[0] - c.from[0] >= c.to[2] - c.from[2] ? 0 : 2; // long axis
    const across = along === 0 ? 2 : 0;
    const a = (ctx.lp[along] - c.from[along]) / (c.to[along] - c.from[along]);
    const w = (ctx.lp[across] - c.from[across]) / (c.to[across] - c.from[across]);
    return Math.abs(w - 0.5) < 0.3 && a < 0.75 ? pick(ctx.pal.swirl, 0.45 + a * 0.3, ctx, 0.2) : spikePaint(ctx);
  };
  const cape = m.bone('cape', [0, 18, 0], { parent: torso });
  m.cube(cape, { name: 'collar', from: [-6.5, 16, -2], to: [6.5, 19, 5], paint: featherPaint });
  symmetric((s, cube) => {
    cube(cape, { name: 'collar_' + side(s), from: [3.5, 16, -5], to: [6.5, 19, -2], paint: featherPaint });
    // three long feathers fanning out over the upper arm like a short wing
    const cl = m.bone('capelet_' + side(s), P(s, [6, 18.5, 0]), { parent: cape, rotation: R(s, [0, 0, -40]) });
    cube(cl, { name: `feather_${side(s)}_front`, from: [5.5, 18, -5], to: [13.5, 19, -2], paint: featherPaint });
    cube(cl, { name: `feather_${side(s)}_mid`, from: [5.5, 18, -2], to: [15.5, 19, 1], paint: featherPaint });
    cube(cl, { name: `feather_${side(s)}_back`, from: [5.5, 18, 1], to: [14.5, 19, 4], paint: featherPaint });
  });
  // back of the cape: four short feathers over the shoulder blades, flaring out a little
  const capeBack = m.bone('cape_back', [0, 18, 5], { parent: cape, rotation: [-8, 0, 0] });
  const backFeather = (ctx) => {
    const base = spikePaint(ctx);
    if (ctx.face !== 'south') return base;
    const c = ctx.cube;
    const w = (ctx.lp[0] - c.from[0]) / (c.to[0] - c.from[0]);
    const a = (c.to[1] - ctx.lp[1]) / (c.to[1] - c.from[1]);
    return Math.abs(w - 0.5) < 0.3 && a < 0.45 ? pick(ctx.pal.swirl, 0.4 + a * 0.3, ctx, 0.2) : base;
  };
  [[-6, 12], [-3, 11], [0, 11], [3, 12]].forEach(([x, y], i) => {
    m.cube(capeBack, { name: 'feather_back_' + i, from: [x, y, 5], to: [x + 3, 18, 6], paint: backFeather });
  });

  // ----------------------------------------------------------------- arms (three-fingered hands)
  const armPaint = mottled('body', { c: [10, 15, -0.5], r: [7, 4, 4] });
  const clawPaint = mottled('bill', { c: [17, 15.5, -0.5], r: [3, 2, 3] }, { base: 0.5, gain: 0.45, noise: 0.2, seed: 8 });
  symmetric((s, cube) => {
    const arm = m.bone('arm_' + side(s), P(s, [6, 15.5, -0.5]), { parent: torso, rotation: R(s, [0, 16, -44]) });
    cube(arm, { name: 'arm_' + side(s), from: [5.5, 14, -2], to: [9.5, 17, 1], paint: armPaint });
    const fore = m.bone('forearm_' + side(s), P(s, [9.5, 15.5, -0.5]), { parent: arm, rotation: R(s, [0, 38, 14]) });
    cube(fore, { name: 'forearm_' + side(s), from: [9.5, 14.5, -1.5], to: [13.5, 16.5, 0.5], paint: armPaint });
    const hand = m.bone('hand_' + side(s), P(s, [13.5, 15.5, -0.5]), { parent: fore });
    cube(hand, { name: 'hand_' + side(s), from: [13.5, 14, -2], to: [15.5, 17, 1], paint: armPaint });
    [-2.5, -1, 0.5].forEach((z, i) => cube(hand, { name: `finger_${side(s)}_${i}`, from: [15.5, 15, z], to: [17.5, 16, z + 1], paint: clawPaint }));
  });

  // ----------------------------------------------------------------- legs
  const legPaint = mottled('body', { c: [3.5, 5, 0], r: [4, 6, 4] }, { shade: (p) => 0.2 * (1 - smooth(1.5, 4, p[1])) });
  symmetric((s, cube) => {
    const leg = m.bone('leg_' + side(s), P(s, [3.5, 7, 0]), { parent: body, rotation: R(s, [0, -10, 4]) });
    cube(leg, { name: 'thigh_' + side(s), from: [1.5, 2, -2.5], to: [5.5, 8, 2.5], paint: legPaint });
    const foot = m.bone('foot_' + side(s), P(s, [3.5, 1.5, 0]), { parent: leg, rotation: R(s, [0, 0, -4]) }); // keeps the sole flat
    cube(foot, { name: 'foot_' + side(s), from: [1, 0, -5], to: [6, 2, 1], paint: legPaint });
    [2, 4].forEach((x, i) => cube(foot, { name: `claw_${side(s)}_${i}`, from: [x, 0, -6], to: [x + 1, 1, -5], paint: clawPaint }));
  });

  // ----------------------------------------------------------------- tail (long and pointed)
  const tailPaint = mottled('body', { c: [0, 7, 9], r: [4, 3, 8] });
  const tail = m.bone('tail', [0, 7, 3.5], { parent: torso, rotation: [12, 0, 0] });
  m.cube(tail, { name: 'tail', from: [-2.5, 5, 3.5], to: [2.5, 9, 8.5], paint: tailPaint });
  const tail2 = m.bone('tail2', [0, 7, 8.5], { parent: tail, rotation: [6, 0, 0] });
  m.cube(tail2, { name: 'tail2', from: [-2, 5.5, 8], to: [2, 8.5, 12], paint: tailPaint });
  const tail3 = m.bone('tail3', [0, 7, 12], { parent: tail2, rotation: [4, 0, 0] });
  m.cube(tail3, { name: 'tail3', from: [-1.5, 6, 11.5], to: [1.5, 8, 14.5], paint: tailPaint });
  m.cube(tail3, { name: 'tail_tip', from: [-0.5, 6.5, 14.5], to: [0.5, 7.5, 16.5], paint: tailPaint });

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 38, 0]);
  m.locator(torso, 'middle', [0, 14, 0]);
  m.locator(head, 'target', [0, 21, -6.5]);
  m.locator(shell, 'head', [0, 36, 0], { extra: ['item_hat'] });
  m.locator(head, 'face', [0, 21, -6], { extra: ['item_face'] });
  m.locator(beak, 'mouth', [0, 19, -12.5]);
  m.locator(head, 'eye_right', [3.5, 22, -6]);
  m.locator(head, 'eye_left', [-3.5, 22, -6]);
  m.locator(gem, 'special', [0, 29, -9]);
  // hand locators use the arms' unrotated coordinates; they follow the arm bones' rotation
  m.locator(m.boneMap.hand_right, 'hand_primary', [16, 15.5, -0.5], { extra: ['physical'] });
  m.locator(m.boneMap.hand_left, 'hand_secondary', [-16, 15.5, -0.5]);
  m.locator(m.boneMap.hand_right, 'item', [16.5, 15, -0.5]);
  m.locator(tail3, 'tail', [0, 7, 15]);

  require('./anims')(m);
  return m;
}

module.exports = { ID, build, PALETTES, FACE };
