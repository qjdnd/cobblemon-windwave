// Frillgator: a stand-alone (non-evolving) grass/dragon crocodile. Squats on
// its haunches with a round striped belly, huge googly eyes sitting on top of
// its head, a toothy half-open snout, spiky cream frills fanning out on both
// sides of the head, dangling clawed hands and a tail curled round to its left.
'use strict';
const L = require('../lib');
const { Model, hex, makeRamp, pick, clamp, smooth, ellipsoidLight, norm3 } = L;

const ID = 'frillgator';

const PALETTES = {
  base: {
    skin: makeRamp(['#3f5527', '#556f31', '#6b863e', '#819a4d', '#97ad5e', '#abbe70', '#c1cf8e', '#d9e3b9', '#f0f4e2'], 9),
    belly: makeRamp(['#a38a55', '#b9a067', '#ccb77f', '#dccc9b', '#e8dfba', '#f3eed8', '#fcfbf1'], 7),
    bellyLine: hex('#8d7648'),
    frill: makeRamp(['#b19552', '#c8ab62', '#d8c07a', '#e5d399', '#efe4bd', '#f8f3e0', '#fffffa'], 7),
    frillLine: hex('#7d6634'),
    mouth: makeRamp(['#4f1a1d', '#6e2a2d', '#94403f', '#b95c58', '#d37d75'], 5),
    tongue: makeRamp(['#b95c58', '#cf7a72', '#e09a90'], 3),
    ivory: makeRamp(['#9fa196', '#c4c6bb', '#e3e4dc', '#f7f7f2', '#ffffff'], 5),
    eye: makeRamp(['#7f8b97', '#a9b3bd', '#cdd4da', '#e9edf0', '#ffffff'], 5),
    pupil: hex('#141414'),
    nostril: hex('#34461f'),
    lash: hex('#33451e'),
  },
  shiny: {
    skin: makeRamp(['#1c434b', '#27585f', '#336d73', '#428287', '#56979a', '#6daaa9', '#8cbfbb', '#b6d9d3', '#e0f0ec'], 9),
    belly: makeRamp(['#a8826a', '#bf987f', '#d2ae96', '#e1c4ae', '#ecd8c8', '#f6eae0', '#fdf8f3'], 7),
    bellyLine: hex('#8f6b56'),
    frill: makeRamp(['#a3637f', '#bb7c98', '#cf97af', '#dfb3c6', '#ecd0dc', '#f7e8ee', '#fffafc'], 7),
    frillLine: hex('#86495f'),
    mouth: makeRamp(['#4f1a1d', '#6e2a2d', '#94403f', '#b95c58', '#d37d75'], 5),
    tongue: makeRamp(['#b95c58', '#cf7a72', '#e09a90'], 3),
    ivory: makeRamp(['#9fa196', '#c4c6bb', '#e3e4dc', '#f7f7f2', '#ffffff'], 5),
    eye: makeRamp(['#7f8b97', '#a9b3bd', '#cdd4da', '#e9edf0', '#ffffff'], 5),
    pupil: hex('#141414'),
    nostril: hex('#163439'),
    lash: hex('#163439'),
  },
};

// key light from the front-top, symmetric left/right so mirrored UVs stay correct
const KEY = norm3([0, 0.9, -0.6]);
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

// ------------------------------------------------------------------ skin
// Rounded shading on an ellipsoid + watercolour-like pale blotches on the lit
// side (the reference art is washed with white highlights) + a soft darker rim
// where the imagined surface turns away from the flat face (reads as an outline).
function skin(ell, opts = {}) {
  return (ctx) => {
    const p = opts.local ? ctx.lp : ctx.p;
    const c = typeof ell === 'function' ? ell(ctx) : ell;
    const { l, n } = ellipsoidLight(p, c.c, c.r, KEY, opts.wrap ?? 0.55);
    let v = 0.2 + l * 0.62;
    const fn = opts.local ? FACE_N[ctx.face] : ctx.n;
    const facing = Math.abs(dot(n, fn));
    if (facing < 0.3) v -= 0.12;
    if (ctx.face === 'down') v -= 0.12;
    if (!opts.noGround) v -= 0.26 * (1 - smooth(0, 2.2, ctx.p[1]));
    if (opts.ao) v -= opts.ao(ctx) || 0;
    v += (L.vnoise(ctx.p, 2.3, 31) - 0.5) * 0.2;
    // watercolour highlight: pale washes where the light hits hardest
    const wash = smooth(0.66, 0.92, l + (L.vnoise(ctx.p, 3.1, 7) - 0.5) * 0.4);
    v += wash * 0.22;
    return pick(ctx.pal.skin, clamp(v, 0, 1), ctx, 0.5);
  };
}
const FACE_N = { east: [1, 0, 0], west: [-1, 0, 0], up: [0, 1, 0], down: [0, -1, 0], south: [0, 0, 1], north: [0, 0, -1] };
// ellipsoid wrapped around the cube itself (for small parts)
const cubeEll = (grow = 1.3) => (ctx) => {
  const c = ctx.cube;
  return { c: [0, 1, 2].map((i) => (c.from[i] + c.to[i]) / 2), r: [0, 1, 2].map((i) => Math.max(0.8, (c.to[i] - c.from[i]) / 2 * grow)) };
};

// ------------------------------------------------------------------ 2D helpers (planes)
function inPoly(x, y, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if ((yi > y) !== (yj > y) && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
}
function edgeDist(x, y, poly) {
  let best = 1e9;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const a = poly[j], b = poly[i];
    const dx = b[0] - a[0], dy = b[1] - a[1];
    const t = clamp(((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy || 1), 0, 1);
    best = Math.min(best, Math.hypot(x - (a[0] + dx * t), y - (a[1] + dy * t)));
  }
  return best;
}

// ------------------------------------------------------------------ frills
// Right-side frill outlines in plane coordinates (u = distance out from the
// frill root, v = height). The left side reuses the texture mirrored.
const FRILL_ROOT_X = 5.5;
const FRILL_A = [
  [0, 30.0], [6.5, 33.2], [8.0, 29.0], [14.0, 28.4], [10.5, 25.0], [13.6, 21.4], [10.4, 19.2],
  [14.0, 13.4], [9.4, 14.2], [10.0, 6.3], [6.0, 11.5], [3.4, 7.1], [0.8, 14.0],
];
const FRILL_B = [
  [0, 28.0], [5.5, 30.4], [7.0, 26.5], [12.0, 24.4], [8.5, 21.5], [12.0, 17.4], [7.8, 16.4],
  [8.6, 9.5], [4.6, 13.6], [1.8, 9.9], [0.4, 17.0],
];
function frillPaint(poly, vmin, vmax, shade) {
  const hub = [-2, (vmin + vmax) / 2 + 1];
  return (ctx) => {
    if (ctx.face !== 'north' && ctx.face !== 'south') return null;
    const u = Math.abs(ctx.lp[0]) - FRILL_ROOT_X, v = ctx.lp[1];
    if (!inPoly(u, v, poly)) return null;
    const e = edgeDist(u, v, poly);
    const t = clamp((v - vmin) / (vmax - vmin), 0, 1);
    let val = 0.12 + smooth(0.05, 0.85, t) * 0.95;               // warm tan at the bottom, white at the top
    val -= 0.22 * (1 - smooth(0, 3.5, u));                       // shadowed where it grows out of the head
    const ang = Math.atan2(v - hub[1], u - hub[0]);
    val -= 0.07 * Math.pow(Math.abs(Math.sin(ang * 8 + L.vnoise([u, v, 0], 2.5, 3) * 2)), 8); // faint hair strands
    val += (L.vnoise([u, v, 3], 2.2, 12) - 0.5) * 0.12;
    val += shade;
    if (ctx.face === 'south') val -= 0.06;
    if (e < 0.6) return L.mix(ctx.pal.frillLine, ctx.pal.frill[Math.round(clamp(val, 0, 1) * 6)], 0.55);
    if (e < 1.3) val -= 0.07;
    return pick(ctx.pal.frill, clamp(val, 0, 1), ctx, 0.45);
  };
}

// ------------------------------------------------------------------ back spikes (plane at x = 0, in z/y)
const SPIKES = [
  [[3.0, 21.6], [7.2, 19.0], [3.2, 16.9]],
  [[4.2, 18.0], [8.5, 15.0], [4.6, 13.7]],
  [[5.4, 14.4], [9.6, 11.1], [5.8, 9.9]],
  [[5.8, 10.6], [9.8, 7.3], [6.0, 6.1]],
];

// ------------------------------------------------------------------ teeth (plane sprites)
// each tooth: [centre along the plane, length in texels]
function teethPaint(axis, teeth, down) {
  return (ctx) => {
    const a = ctx.lp[axis];
    const y = ctx.lp[1];
    const c = ctx.cube;
    const fromEdge = down ? c.to[1] - y : y - c.from[1];      // distance from the gum
    for (const [ctr, len] of teeth) {
      if (Math.abs(a - ctr) < 0.5 && fromEdge < len) {
        const tip = fromEdge > len - 1;
        return pick(ctx.pal.ivory, tip ? 0.95 : 0.7, ctx, 0.2);
      }
    }
    return null;
  };
}

function build() {
  const m = new Model({ id: ID, texW: 128, texH: 128, visibleBox: [4, 3, 0.9], palettes: PALETTES });
  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', [0, 6, 0], { parent: root });
  const A = L.ALPHA_REDS;

  // ----------------------------------------------------------------- body (round pot belly)
  const bodyEll = { c: [0, 6.8, 0], r: [8.2, 9.2, 7.2] };
  const bellyHalf = (y) => 5.6 * Math.sqrt(Math.max(0, 1 - Math.pow((y - 7) / 10, 2)));
  const bellySkin = skin(bodyEll);
  const bellyPaint = (ctx) => {
    const p = ctx.p;
    const { l, n } = ellipsoidLight(p, bodyEll.c, bodyEll.r, KEY, 0.6);
    const inBelly = n[2] < -0.28 && Math.abs(p[0]) < bellyHalf(p[1]) && p[1] < 17;
    if (!inBelly) return bellySkin(ctx);
    // plates: gently smiling horizontal seams every ~2.2 units
    const yy = p[1] + 0.045 * p[0] * p[0];
    const seam = Math.floor(yy / 2.6) !== Math.floor((yy - 0.9) / 2.6) && yy > 1.5 && p[1] < 15.5;
    let v = 0.5 + l * 0.38 + smooth(1, 11, p[1]) * 0.22;
    v -= 0.3 * (1 - smooth(0, 2.4, p[1]));
    v -= 0.16 * smooth(bellyHalf(p[1]) - 1.4, bellyHalf(p[1]), Math.abs(p[0]));
    v += (L.vnoise(p, 2.2, 41) - 0.5) * 0.16;
    v -= 0.14 * (1 - (((yy / 2.6) % 1) + 1) % 1);                  // each plate a touch darker towards its lower seam
    if (seam) return L.mix(ctx.pal.bellyLine, pick(ctx.pal.belly, clamp(v, 0, 1), ctx, 0.3), 0.32);
    return pick(ctx.pal.belly, clamp(v, 0, 1), ctx, 0.45);
  };
  m.cube(body, { name: 'body_core', from: [-7, 1, -4], to: [7, 12, 5], paint: bellyPaint });
  m.cube(body, { name: 'body_mid', from: [-5.5, 0, -5], to: [5.5, 14, 6], paint: bellyPaint });
  m.cube(body, { name: 'body_round', from: [-6.5, 0.5, -4.5], to: [6.5, 13.5, 5.5], paint: bellyPaint });
  m.cube(body, { name: 'body_belly', from: [-4.5, 1, -6], to: [4.5, 11, -5], paint: bellyPaint });
  m.cube(body, { name: 'chest', from: [-4.5, 13, -3.5], to: [4.5, 16, 4.5], paint: bellyPaint });
  m.cube(body, { name: 'neck', from: [-3.5, 14, -2.5], to: [3.5, 18, 3.5], paint: bellyPaint });

  // back spikes
  m.cube(body, {
    name: 'back_spikes', from: [0, 6, 2], to: [0, 22, 10],
    paint: (ctx) => {
      if (ctx.face !== 'east' && ctx.face !== 'west') return null;
      const z = ctx.lp[2], y = ctx.lp[1];
      for (const tri of SPIKES) {
        if (!inPoly(z, y, tri)) continue;
        // outline only along the two free edges (the base is buried in the body)
        const e = Math.min(edgeDist(z, y, [tri[0], tri[1]]), edgeDist(z, y, [tri[1], tri[2]]));
        const t = clamp((z - tri[0][0]) / (tri[1][0] - tri[0][0]), 0, 1);
        const v = clamp(0.62 + (y - tri[1][1]) * 0.07 - t * 0.12 + (ctx.face === 'west' ? -0.06 : 0), 0, 1);
        if (e < 0.45) return L.mix(ctx.pal.frillLine, pick(ctx.pal.frill, v, ctx, 0.3), 0.3);
        return pick(ctx.pal.frill, v, ctx, 0.4);
      }
      return null;
    },
  });

  // ----------------------------------------------------------------- head
  const head = m.bone('head', [0, 17, -1], { parent: body });
  const cranEll = { c: [0, 21.5, -1.5], r: [7.4, 5.8, 6] };
  const cranSkin = skin(cranEll);
  m.cube(head, { name: 'cranium', from: [-6, 17, -6], to: [6, 25, 3], paint: cranSkin });
  m.cube(head, { name: 'cranium_top', from: [-4.5, 25, -4.5], to: [4.5, 26, 1.5], paint: cranSkin });
  m.cube(head, { name: 'cranium_back', from: [-5, 18, 3], to: [5, 24, 4], paint: cranSkin });

  // snout (upper jaw): green outside, pink roof of the mouth underneath, nostrils on top
  const snoutEll = { c: [0, 19.2, -9.5], r: [5.4, 3.6, 6.2] };
  const snoutSkin = skin(snoutEll, { noGround: true });
  const roof = (ctx) => {
    const x = Math.abs(ctx.p[0]), z = ctx.p[2];
    if (x > ctx.cube.to[0] - 0.6) return snoutSkin(ctx);        // lip rim
    const depth = smooth(-13.5, -6.5, z);
    return pick(ctx.pal.mouth, clamp(0.85 - depth * 0.75 - smooth(2.5, 4, x) * 0.15, 0, 1), ctx, 0.4);
  };
  const snoutPaint = (ctx) => {
    if (ctx.face === 'down') return roof(ctx);
    const col = snoutSkin(ctx);
    // nostrils: two short dark slits near the tip
    if (ctx.face === 'up' && ctx.p[2] < -12 && ctx.p[2] > -13 && Math.abs(ctx.p[0]) > 1 && Math.abs(ctx.p[0]) < 2) return ctx.pal.nostril.slice();
    // darker lip line just above the mouth opening
    if (ctx.face !== 'up' && ctx.p[1] < 18) return L.mix(col, ctx.pal.lash, 0.35);
    return col;
  };
  m.cube(head, { name: 'snout', from: [-4.5, 17, -13], to: [4.5, 21, -6], paint: snoutPaint });
  m.cube(head, { name: 'snout_tip', from: [-3.5, 17, -14], to: [3.5, 20, -13], paint: snoutPaint });

  // upper teeth: a front row and two side rows hanging from the roof of the mouth
  m.cube(head, { name: 'teeth_upper_front', from: [-3.5, 15, -13.6], to: [3.5, 17, -13.6], paint: teethPaint(0, [[-3, 1], [-2, 2], [0, 1], [2, 2], [3, 1]], true) });
  const upperSide = teethPaint(2, [[-12.5, 2], [-10.5, 1], [-8.5, 1]], true);
  const tUR = m.cube(head, { name: 'teeth_upper_right', from: [4.1, 15, -13], to: [4.1, 17, -7], paint: upperSide });
  m.cube(head, { name: 'teeth_upper_left', from: [-4.1, 15, -13], to: [-4.1, 17, -7], paint: upperSide, mirror: true, uvShare: tUR });

  // inside of the mouth (fills the gap when the jaw drops)
  m.cube(head, {
    name: 'mouth_inside', from: [-3.5, 14.9, -12], to: [3.5, 16.9, -6],
    paint: (ctx) => pick(ctx.pal.mouth, clamp(0.12 + smooth(15, 17, ctx.p[1]) * 0.35 - smooth(-12, -7, ctx.p[2]) * 0.2, 0, 1), ctx, 0.4),
  });

  // lower jaw (rests slightly open so the teeth show)
  const jaw = m.bone('jaw', [0, 17, -6], { parent: head, rotation: [-20, 0, 0] });
  const jawSkin = skin({ c: [0, 16.2, -9.5], r: [4.8, 2.8, 5.2] }, { local: true, noGround: true });
  const jawPaint = (ctx) => {
    if (ctx.face === 'up') {
      const x = Math.abs(ctx.lp[0]), z = ctx.lp[2];
      if (x > ctx.cube.to[0] - 0.6) return jawSkin(ctx);
      // tongue
      if (x < 2.3 && z < -7 && z > -11.8) return pick(ctx.pal.tongue, clamp(0.9 - smooth(-11.5, -7, z) * 0.7 - smooth(1, 2.3, x) * 0.3, 0, 1), ctx, 0.4);
      return pick(ctx.pal.mouth, clamp(0.55 - smooth(-12, -7, z) * 0.35, 0, 1), ctx, 0.4);
    }
    const col = jawSkin(ctx);
    if (ctx.face !== 'down' && ctx.lp[1] > ctx.cube.to[1] - 1) return L.mix(col, ctx.pal.lash, 0.3);
    return col;
  };
  m.cube(jaw, { name: 'jaw', from: [-4, 15, -13], to: [4, 17, -6], paint: jawPaint });
  m.cube(jaw, { name: 'jaw_chin', from: [-3.5, 14, -12], to: [3.5, 15, -7], paint: jawPaint });
  m.cube(jaw, { name: 'teeth_lower_front', from: [-3, 17, -12.6], to: [3, 18, -12.6], paint: teethPaint(0, [[-1.5, 1], [1.5, 1]], false) });
  const lowerSide = teethPaint(2, [[-12, 1], [-10, 1]], false);
  const tLR = m.cube(jaw, { name: 'teeth_lower_right', from: [3.6, 17, -12.5], to: [3.6, 18, -8.5], paint: lowerSide });
  m.cube(jaw, { name: 'teeth_lower_left', from: [-3.6, 17, -12.5], to: [-3.6, 18, -8.5], paint: lowerSide, mirror: true, uvShare: tLR });

  // ----------------------------------------------------------------- eyes
  // Big white balls on top of the head. Each eye has a pupil plane and an
  // eyelid shell that rests folded behind the eye (green skin of the socket)
  // and swings over the front to close it.
  const EYE_C = [6, 26, -3];
  const LID_REST = 150; // folded down behind the eye, inside the socket
  const eyePaint = (ctx) => {
    const c = [Math.sign(ctx.p[0]) * EYE_C[0], EYE_C[1], EYE_C[2]];
    const { l, n } = ellipsoidLight(ctx.p, c, [4.2, 4.2, 4.2], KEY, 0.8);
    let v = 0.6 + l * 0.5;
    if (Math.abs(dot(n, ctx.n)) < 0.34) v -= 0.3;
    v -= 0.1 * smooth(-1, -4, ctx.p[1] - c[1]);
    return pick(ctx.pal.eye, clamp(v, 0, 1), ctx, 0.35);
  };
  const lidShade = skin({ c: [0, 23, -1], r: [10.5, 7.5, 6.5] }, { noGround: true });
  // The up face becomes the front of the closed lid (local z -> height). Paint a
  // sleepy curved lash line on it and keep the rest plain skin.
  const lidPaint = (ctx) => {
    if (ctx.face !== 'up') return lidShade(ctx);
    const x = Math.abs(ctx.lp[0]) - EYE_C[0], z = ctx.lp[2] - EYE_C[2];   // z = height above the eye centre once closed
    const line = -1.9 + 0.13 * x * x;
    const v0 = 0.72 - Math.max(0, -z - 1.5) * 0.08 + Math.max(0, z) * 0.03;
    if (z > line - 0.5 && z < line + 0.5 && Math.abs(x) < 3.2) return ctx.pal.lash.slice();
    if (z > line + 0.5 && z < line + 1.3 && Math.abs(x) < 2.6) return pick(ctx.pal.skin, 0.45, ctx, 0.3);
    return pick(ctx.pal.skin, clamp(v0 + (L.vnoise(ctx.p, 2, 4) - 0.5) * 0.12, 0, 1), ctx, 0.4);
  };
  const eyeCubes = [
    ['x', [2, 23, -6], [10, 29, 0]],
    ['y', [3, 22, -6], [9, 30, 0]],
    ['z', [3, 23, -7], [9, 29, 1]],
    ['c', [2.5, 22.5, -6.5], [9.5, 29.5, 0.5]],
  ];
  // three stacked shells (different inflate so no two faces are coplanar)
  const lidCubes = [
    ['a', [2, 26, -6], [10, 30, 0], 0.2],
    ['b', [3, 26, -7], [9, 30, 1], 0.3],
    ['c', [2.5, 26, -6.5], [9.5, 30, 0.5], 0.25],
  ];
  const mx = (v, s) => (s > 0 ? v : [-v[0], v[1], v[2]]);
  const span = (a, b, s) => (s > 0 ? [a, b] : [[-b[0], a[1], a[2]], [-a[0], b[1], b[2]]]);
  const firstEye = {}, firstLid = {};
  let firstPupil = null;
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    const eye = m.bone('eye_' + side, mx(EYE_C, s), { parent: head });
    for (const [k, f, t] of eyeCubes) {
      const [from, to] = span(f, t, s);
      const c = m.cube(eye, { name: `eye_${side}_${k}`, from, to, paint: eyePaint, mirror: s < 0, uvShare: s < 0 ? firstEye[k] : undefined });
      if (s > 0) firstEye[k] = c;
    }
    const pupil = m.bone('pupil_' + side, mx([6, 26, -7.05], s), { parent: eye });
    const [pf, pt] = span([5, 25, -7.05], [7, 27, -7.05], s);
    const pc = m.cube(pupil, {
      name: 'pupil_' + side, from: pf, to: pt,
      paint: (ctx) => (ctx.face === 'north' || ctx.face === 'south' ? ctx.pal.pupil.slice() : null),
      alpha: (ctx) => (ctx.face === 'north' || ctx.face === 'south' ? A.hi.slice() : null), // alpha: glowing red pupils
      uvShare: s < 0 ? firstPupil : undefined, mirror: s < 0,
    });
    if (s > 0) firstPupil = pc;
    const lid = m.bone('eyelid_' + side, mx(EYE_C, s), { parent: eye, rotation: [LID_REST, 0, 0] });
    for (const [k, f, t, inf] of lidCubes) {
      const [from, to] = span(f, t, s);
      const c = m.cube(lid, { name: `eyelid_${side}_${k}`, from, to, inflate: inf, paint: lidPaint, mirror: s < 0, uvShare: s < 0 ? firstLid[k] : undefined });
      if (s > 0) firstLid[k] = c;
    }
  }

  // ----------------------------------------------------------------- frills
  const firstFrill = {};
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    const fa = m.bone('frill_' + side, mx([FRILL_ROOT_X, 22, 0], s), { parent: head, rotation: [0, -16 * s, -5 * s] });
    const [aF, aT] = span([FRILL_ROOT_X, 6, 0], [FRILL_ROOT_X + 14, 34, 0], s);
    const ca = m.cube(fa, { name: 'frill_' + side, from: aF, to: aT, paint: frillPaint(FRILL_A, 6, 33, 0), mirror: s < 0, uvShare: s < 0 ? firstFrill.a : undefined });
    const fb = m.bone('frill_' + side + '_back', mx([FRILL_ROOT_X, 21, 1.5], s), { parent: head, rotation: [8, -46 * s, -10 * s] });
    const [bF, bT] = span([FRILL_ROOT_X, 9, 1.5], [FRILL_ROOT_X + 12, 31, 1.5], s);
    const cb = m.cube(fb, { name: 'frill_' + side + '_back', from: bF, to: bT, paint: frillPaint(FRILL_B, 9, 30.5, -0.1), mirror: s < 0, uvShare: s < 0 ? firstFrill.b : undefined });
    if (s > 0) { firstFrill.a = ca; firstFrill.b = cb; }
  }

  // ----------------------------------------------------------------- arms (bent, hands dangling in front of the belly)
  const clawPaint = (ctx) => {
    const c = ctx.cube;
    const t = clamp((c.to[1] - ctx.lp[1]) / (c.to[1] - c.from[1]), 0, 1);  // 0 at the root, 1 at the tip
    let v = 0.45 + t * 0.5;
    if (ctx.face === 'south' || ctx.face === 'down') v -= 0.15;
    return pick(ctx.pal.ivory, clamp(v, 0, 1), ctx, 0.3);
  };
  const toeClawPaint = (ctx) => {
    const c = ctx.cube;
    const t = clamp((c.to[2] - ctx.lp[2]) / (c.to[2] - c.from[2]), 0, 1);
    let v = 0.45 + t * 0.5;
    if (ctx.face === 'down') v -= 0.2;
    return pick(ctx.pal.ivory, clamp(v, 0, 1), ctx, 0.3);
  };
  const first = {};
  const share = (key, s, c) => { if (s > 0) first[key] = c; return c; };
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    const arm = m.bone('arm_' + side, mx([6, 12, -2], s), { parent: body, rotation: [0, 0, 0] });
    let [f, t] = span([5.5, 9.5, -7.5], [8.5, 12.5, -1.5], s);
    share('upper', s, m.cube(arm, { name: 'arm_' + side, from: f, to: t, paint: skin(cubeEll(1.35)), mirror: s < 0, uvShare: s < 0 ? first.upper : undefined }));
    const fore = m.bone('forearm_' + side, mx([7, 11, -7], s), { parent: arm });
    [f, t] = span([5.5, 9, -10.5], [8.5, 12, -6.5], s);
    share('fore', s, m.cube(fore, { name: 'forearm_' + side, from: f, to: t, paint: skin(cubeEll(1.35)), mirror: s < 0, uvShare: s < 0 ? first.fore : undefined }));
    const hand = m.bone('hand_' + side, mx([7, 10.5, -10.5], s), { parent: fore });
    [f, t] = span([5, 7, -12], [9, 11, -9], s);
    share('hand', s, m.cube(hand, { name: 'hand_' + side, from: f, to: t, paint: skin(cubeEll(1.3)), mirror: s < 0, uvShare: s < 0 ? first.hand : undefined }));
    [0, 1, 2].forEach((i) => {
      const x0 = 5 + i * 1.5, x1 = x0 + 1;
      [f, t] = span([x0, 4, -11.7], [x1, 7, -10.7], s);
      share('claw' + i, s, m.cube(hand, { name: `claw_${side}_${i}`, from: f, to: t, rotation: [12, 0, 0], origin: mx([x0 + 0.5, 7, -11.2], s), paint: clawPaint, mirror: s < 0, uvShare: s < 0 ? first['claw' + i] : undefined }));
    });

    // ----------------------------------------------------------------- legs (squatting, knees out, feet turned outwards)
    const leg = m.bone('leg_' + side, mx([5, 5, -1], s), { parent: body });
    [f, t] = span([4, 1, -6], [10, 8, 2], s);
    share('thigh', s, m.cube(leg, { name: 'thigh_' + side, from: f, to: t, paint: skin({ c: [7, 4.5, -2], r: [4.2, 4.5, 5.2] }), mirror: s < 0, uvShare: s < 0 ? first.thigh : undefined }));
    const shin = m.bone('shin_' + side, mx([9, 2.5, -4], s), { parent: leg });
    [f, t] = span([8, 0, -6], [13, 3, -3], s);
    share('shin', s, m.cube(shin, { name: 'shin_' + side, from: f, to: t, paint: skin(cubeEll(1.4)), mirror: s < 0, uvShare: s < 0 ? first.shin : undefined }));
    const foot = m.bone('foot_' + side, mx([12.5, 1, -4.5], s), { parent: shin, rotation: [0, -38 * s, 0] });
    [f, t] = span([10.5, 0, -9], [14.5, 2, -3], s);
    share('foot', s, m.cube(foot, { name: 'foot_' + side, from: f, to: t, paint: skin(cubeEll(1.35), { local: true }), mirror: s < 0, uvShare: s < 0 ? first.foot : undefined }));
    [0, 1, 2].forEach((i) => {
      const x0 = 10.6 + i * 1.4;
      [f, t] = span([x0, 0, -11], [x0 + 1, 1, -9], s);
      share('toe' + i, s, m.cube(foot, { name: `toe_${side}_${i}`, from: f, to: t, paint: toeClawPaint, mirror: s < 0, uvShare: s < 0 ? first['toe' + i] : undefined }));
    });
  }

  // ----------------------------------------------------------------- tail (curls round to its left)
  const tailSeg = [
    ['tail', [0, 3, 5], [0, 0, 0], [-3.5, 0, 4], [3.5, 6, 9]],
    ['tail2', [0, 2.5, 8.5], [0, -30, 0], [-3, 0, 8], [3, 5, 13]],
    ['tail3', [0, 2, 12.5], [0, -34, 0], [-2.5, 0, 12], [2.5, 4, 16]],
    ['tail4', [0, 1.5, 15.5], [6, -34, 0], [-2, 0, 15], [2, 3, 18]],
    ['tail5', [0, 1.2, 17.5], [14, -30, 0], [-1.5, 0.2, 17], [1.5, 2.2, 20]],
  ];
  let tparent = body;
  const tailBones = [];
  for (const [nm, piv, rot, f, t] of tailSeg) {
    const b = m.bone(nm, piv, { parent: tparent, rotation: rot });
    m.cube(b, { name: nm, from: f, to: t, paint: skin(cubeEll(1.3), { local: true }) });
    tailBones.push(b);
    tparent = b;
  }

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 32, -2]);
  m.locator(body, 'middle', [0, 9, 0]);
  m.locator(body, 'target', [0, 12, -9]);
  m.locator(head, 'head', [0, 26, -2]);
  m.locator(head, 'face', [0, 21, -9]);
  m.locator(head, 'item_face', [0, 22, -13.5]);
  m.locator(head, 'item_hat', [0, 30.5, -2]);
  m.locator(head, 'mouth', [0, 17, -13], { extra: ['special'] });
  m.locator(m.boneMap.eye_right, 'eye_right', [6, 26, -7.2]);
  m.locator(m.boneMap.eye_left, 'eye_left', [-6, 26, -7.2]);
  m.locator(jaw, 'physical', [0, 17, -13]);
  m.locator(m.boneMap.hand_right, 'hand_primary', [7, 6, -10.5]);
  m.locator(m.boneMap.hand_left, 'hand_secondary', [-7, 6, -10.5]);
  m.locator(m.boneMap.hand_right, 'item', [7, 5, -11.5]);
  m.locator(m.boneMap.foot_right, 'foot_primary', [12.5, 0.5, -6]);
  m.locator(m.boneMap.foot_left, 'foot_secondary', [-12.5, 0.5, -6]);
  m.locator(tailBones[1], 'tail', [0, 2.5, 11]);
  m.locator(tailBones[4], 'tail_tip', [0, 1.2, 19.5]);

  require('./frillgator.anim')(m);
  return m;
}

module.exports = { ID, build, PALETTES };
