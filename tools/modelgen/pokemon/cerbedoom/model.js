// Cerbedoom (working name): a new evolution of Houndoom, designed from its motifs (see docs/cerbedoom).
// The gatekeeper hellhound: three heads (Cerberus) - the leader in the middle with its horns raked far
// back, two smaller heads on the sides - a bone collar with a skull "lock" on the chest and broken
// vertebra chains (Garmr, chained at Hel's gate), a scorched glowing chest, glowing red eyes (the black
// dogs of folklore), Houndoom's rib bones, ankle cuffs and ram horns grown larger, and a long serpent-
// like tail (Cerberus) ending in an ember arrowhead.
//
// Texture: made from Cobblemon's Houndoom texture (source/houndoom.png). Fur, orange and bone texels are
// copied 1:1 from pure fur / orange / bone areas of it (the same texel density as Houndoom), kept on
// Houndoom's own five-step ramps and moved a step lighter or darker for shading. The shiny is the same
// texels on the matching shiny ramps from houndoom_shiny.png (every Houndoom colour has one shiny colour).
'use strict';
const fs = require('fs');
const path = require('path');
const { PNG } = require('pngjs');
const L = require('../../lib');
const { Model, hex, clamp, smooth, ellipsoidLight, norm3 } = L;

const ID = 'cerbedoom';

// Houndoom's ramps (dark to light) and their shiny counterparts, colour for colour
const RAMPS = {
  fur: [['#23232f', '#323095'], ['#2c2d37', '#3a3fa9'], ['#35353f', '#454cba'], ['#3f4048', '#4f5cce'], ['#4a4b51', '#5a6eda']],
  orange: [['#cc5b39', '#c97d36'], ['#db6841', '#d89043'], ['#e8764a', '#e6a552'], ['#f28857', '#f4bb64'], ['#fc9a62', '#ffcf70']],
  bone: [['#a0a5c8', '#af9dcb'], ['#b4bad5', '#beb1d7'], ['#c5cae0', '#cdc3e2'], ['#dcdff0', '#e2daf1'], ['#ebeef8', '#eeeaf9']],
  mouth: [['#4f1b23', '#5e343b'], ['#64262f', '#713e46'], ['#78303b', '#824851']],
  tongue: [['#b56569', '#b9787b'], ['#ca7a7a', '#cc8b8b'], ['#d6938d', '#d7a09c']],
  eye: [['#be0a2b', '#99351e']],
};
const ramp = (name, v) => RAMPS[name].map((p) => hex(p[v === 'base' ? 0 : 1]));
const PALETTES = Object.fromEntries(['base', 'shiny'].map((v) => [v, {
  fur: ramp('fur', v), orange: ramp('orange', v), bone: ramp('bone', v), mouth: ramp('mouth', v), tongue: ramp('tongue', v),
  eye: ramp('eye', v)[0], white: hex('#fafafa'),
}]));

// ------------------------------------------------------------------ Houndoom texture source
const SRC = path.join(__dirname, 'source');
const hd = PNG.sync.read(fs.readFileSync(path.join(SRC, 'houndoom.png')));
const baseRamps = { fur: ramp('fur', 'base'), orange: ramp('orange', 'base'), bone: ramp('bone', 'base') };
function sourceIndex(mat, x, y) {
  const k = (y * hd.width + x) * 4;
  const px = [hd.data[k], hd.data[k + 1], hd.data[k + 2]];
  let best = 0, bd = Infinity;
  baseRamps[mat].forEach((c, i) => { const d = Math.abs(c[0] - px[0]) + Math.abs(c[1] - px[1]) + Math.abs(c[2] - px[2]); if (d < bd) { bd = d; best = i; } });
  return best;
}
// the largest pure areas of houndoom.png, [x, y, w, h] (found by scanning it; checked texel by texel
// below: only that material's colours)
const WINDOWS = {
  fur: [[0, 55, 68, 9], [0, 44, 72, 6], [46, 0, 12, 23], [0, 12, 34, 6]],
  orange: [[19, 19, 9, 11], [20, 0, 8, 12]],
  bone: [[64, 13, 40, 4], [68, 4, 48, 3], [64, 7, 16, 3], [88, 7, 16, 3]],
};
for (const [mat, list] of Object.entries(WINDOWS)) {
  for (const [x0, y0, w, h] of list) for (let y = y0; y < y0 + h; y++) for (let x = x0; x < x0 + w; x++) {
    const k = (y * hd.width + x) * 4;
    const c = [hd.data[k], hd.data[k + 1], hd.data[k + 2]];
    if (hd.data[k + 3] === 0 || !baseRamps[mat].some((r) => r[0] === c[0] && r[1] === c[1] && r[2] === c[2])) throw new Error(`houndoom.png ${x},${y} is not pure ${mat}`);
  }
}
const strHash = (s) => { let h = 2166136261; for (const ch of s) h = Math.imul(h ^ ch.charCodeAt(0), 16777619); return h >>> 0; };
// mirrored tiling, so faces bigger than a window have no hard seam
const reflect = (n, size) => { const m = ((n % (2 * size)) + 2 * size) % (2 * size); return m < size ? m : 2 * size - 1 - m; };

// light from the front-top (symmetric left/right so it reads well at any yaw)
const KEY = norm3([0, 0.85, -0.75]);

// Paint with Houndoom's texels. zone(ctx) picks the material of a texel ('fur' | 'orange' | 'bone').
function houndoom(zone, ell, opts = {}) {
  return (ctx) => {
    const mat = typeof zone === 'string' ? zone : zone(ctx);
    if (!mat) return null;
    const h = strHash(`${ctx.cube.name}:${ctx.face}:${mat}${opts.seed || ''}`);
    const wins = WINDOWS[mat];
    const [sx, sy, sw, sh] = wins[h % wins.length];
    let i = sourceIndex(mat, sx + reflect(ctx.col + (h >>> 8) % sw, sw), sy + reflect(ctx.row + (h >>> 16) % sh, sh));
    const { l } = ellipsoidLight(ctx.p, ell.c, ell.r, KEY, 0.7);
    if (l > (opts.hi ?? 0.82)) i += 1;
    if (l < (opts.lo ?? 0.3)) i -= 1;
    if (ctx.face === 'down') i -= 1;
    if (opts.shade) i -= opts.shade(ctx.p) || 0;
    return ctx.pal[mat][clamp(i, 0, 4)].slice();
  };
}
const ellOf = (from, to, pad = 1.5) => ({ c: from.map((v, i) => (v + to[i]) / 2), r: from.map((v, i) => (to[i] - v) / 2 + pad) });

function build() {
  const m = new Model({ id: ID, texW: 256, texH: 128, visibleBox: [4, 4, 1.4], palettes: PALETTES, emissive: true });
  const A = L.ALPHA_REDS;

  // Left/right pairs: the right side (+x) is modelled and painted, the left side mirrors it and shares
  // its texture (Box UV mirror), like a mirrored cube in Blockbench.
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
  // cube helper: paint with a zone function over the cube's own ellipsoid
  const box = (cube, bone, name, from, to, zone, opts = {}) => cube(bone, { name, from, to, paint: houndoom(zone, opts.ell || ellOf(from, to), opts), ...(opts.extra || {}) });
  const plain = (bone, spec) => m.cube(bone, spec);

  const root = m.bone(ID, [0, 0, 0]);
  const body = m.bone('body', [0, 20, 0], { parent: root });
  const torso = m.bone('torso', [0, 20, 0], { parent: body });

  // ----------------------------------------------------------------- torso: deep chest, belly, hips
  const bodyEll = { c: [0, 21, 0], r: [9, 8, 17] };
  // scorched chest (Garmr): the lower front of the chest and the underside are Houndoom's orange
  const chestZone = (ctx) => ((ctx.face === 'down' || (ctx.face === 'north' && ctx.p[1] < 22 && Math.abs(ctx.p[0]) < 5)) ? 'orange' : 'fur');
  box(plain, torso, 'chest', [-6.5, 15, -15], [6.5, 28, -3], chestZone, { ell: bodyEll });
  box(plain, torso, 'belly', [-5.5, 16, -4], [5.5, 26, 10], (ctx) => (ctx.face === 'down' ? 'orange' : 'fur'), { ell: bodyEll });
  box(plain, torso, 'hips', [-6, 16.5, 9], [6, 26.5, 16], 'fur', { ell: bodyEll });
  // Houndoom's rib bones, more of them: a shell over the back with bone bands, transparent in between
  const ribs = (zs) => (ctx) => {
    if (ctx.face === 'down' || ctx.face === 'north' || ctx.face === 'south') return null;
    const z = ctx.p[2];
    if (!zs.some((z0) => z >= z0 && z < z0 + 1)) return null;
    if (ctx.face !== 'up' && ctx.p[1] < 19.5) return null; // ribs wrap down the flanks, not the belly
    return houndoom('bone', bodyEll, { hi: 0.75 })(ctx);
  };
  m.cube(torso, { name: 'ribs', from: [-5.5, 16, -4], to: [5.5, 26, 10], inflate: 0.4, paint: ribs([-2, 0, 2, 4, 6]) });
  m.cube(torso, { name: 'ribs_hips', from: [-6, 16.5, 9], to: [6, 26.5, 16], inflate: 0.4, paint: ribs([11, 13]) });

  // ----------------------------------------------------------------- collar, skull lock, broken chains
  const collar = m.bone('collar', [0, 27, -10], { parent: torso });
  const boneMat = (from, to) => ({ ell: ellOf(from, to, 2), hi: 0.75 });
  box(plain, collar, 'collar_front', [-7, 25, -16], [7, 28, -14], 'bone', boneMat([-7, 25, -16], [7, 28, -14]));
  box(plain, collar, 'collar_back', [-7, 25.5, -6], [7, 28.5, -4], 'bone', boneMat([-7, 25.5, -6], [7, 28.5, -4]));
  symmetric((s, cube) => box(cube, collar, 'collar_' + side(s), [6.5, 25, -15], [7.5, 28, -5], 'bone', boneMat([6.5, 25, -15], [7.5, 28, -5])));
  // the skull "lock" on the chest (Houndoom's skull ornament grown up): dark sockets that glow, a row of teeth
  const SKULL = [
    '.bbbb.',
    'bBBBBb',
    'bSbbSb',
    'bSbbSb',
    'bbbbbb',
    '.TTTT.',
  ];
  const skullCh = (ctx) => (ctx.face === 'north' ? SKULL[ctx.row][ctx.col] : 'b');
  const skullBone = houndoom('bone', ellOf([-3, 19, -17], [3, 25, -15], 3), { hi: 0.7 });
  m.cube(collar, {
    name: 'skull_lock', from: [-3, 19, -17], to: [3, 25, -15],
    paint: (ctx) => {
      const ch = skullCh(ctx);
      if (ch === '.') return null;
      if (ch === 'S') return ctx.pal.mouth[0].slice();
      if (ch === 'T') return (ctx.col % 2 ? ctx.pal.bone[4] : ctx.pal.bone[2]).slice();
      return skullBone(ctx);
    },
    emissive: (ctx) => (skullCh(ctx) === 'S' ? ctx.pal.orange[ctx.row === 2 ? 4 : 2].slice() : null),
  });
  // broken vertebra chains hanging from both sides of the collar
  symmetric((s, cube) => {
    const ch = m.bone('chain_' + side(s), P(s, [7.5, 26, -9]), { parent: collar, rotation: R(s, [0, 0, 8]) });
    box(cube, ch, `chain_${side(s)}_0`, [7, 23, -10], [8, 26, -8], 'bone', boneMat([7, 20, -10], [8, 26, -8]));
    box(cube, ch, `chain_${side(s)}_1`, [6.5, 21, -9.5], [8.5, 23, -8.5], 'bone', boneMat([7, 20, -10], [8, 26, -8]));
    box(cube, ch, `chain_${side(s)}_2`, [7, 19, -10], [8, 21, -8], 'bone', boneMat([7, 18, -10], [8, 26, -8]));
  });

  // ----------------------------------------------------------------- legs, with Houndoom's bone cuffs and white claws
  const claws = (cube, bone, name, x0, y, z) => {
    [0, 1.5, 3].forEach((dx, i) => box(cube, bone, `${name}_${i}`, [x0 + dx, y, z - 1], [x0 + dx + 1, y + 1, z], 'bone', { ell: ellOf([x0, y, z - 1], [x0 + 4, y + 1, z], 2), hi: 0.6 }));
  };
  symmetric((s, cube) => {
    const fl = m.bone('leg_front_' + side(s), P(s, [5.5, 20, -9.5]), { parent: body });
    box(cube, fl, 'leg_front_' + side(s), [3.5, 10, -12], [7.5, 22, -7], 'fur', { ell: { c: [5.5, 16, -9.5], r: [4, 10, 4] } });
    const fl2 = m.bone('leg_front_' + side(s) + '2', P(s, [5.5, 10.5, -9.5]), { parent: fl });
    box(cube, fl2, 'shin_front_' + side(s), [4, 2, -11], [7, 11, -8], 'fur', { ell: { c: [5.5, 7, -9.5], r: [3, 8, 3] } });
    box(cube, fl2, 'cuff_front_' + side(s), [3.5, 3, -11.5], [7.5, 6, -7.5], 'bone', boneMat([3.5, 3, -11.5], [7.5, 6, -7.5]));
    const fp = m.bone('paw_front_' + side(s), P(s, [5.5, 1, -9.5]), { parent: fl2 });
    box(cube, fp, 'paw_front_' + side(s), [3.5, 0, -12.5], [7.5, 2, -7.5], 'fur', { ell: { c: [5.5, 1.5, -10], r: [4, 3, 4] } });
    claws(cube, fp, 'claw_front_' + side(s), 3.5, 0, -12.5);

    // hind leg: thigh down-forward, shin down-back to the hock, then straight down to the paw
    const bl = m.bone('leg_back_' + side(s), P(s, [5.5, 21, 12.5]), { parent: body, rotation: R(s, [14, 0, 0]) });
    box(cube, bl, 'thigh_' + side(s), [3, 12, 9.5], [8, 24, 15.5], 'fur', { ell: { c: [5.5, 18, 12.5], r: [5, 9, 5] } });
    const bl2 = m.bone('leg_back_' + side(s) + '2', P(s, [5.5, 13, 12.5]), { parent: bl, rotation: R(s, [-46, 0, 0]) });
    box(cube, bl2, 'hock_' + side(s), [4, 6, 11], [7, 14, 14], 'fur', { ell: { c: [5.5, 10, 12.5], r: [3, 6, 3] } });
    const bl3 = m.bone('leg_back_' + side(s) + '3', P(s, [5.5, 6.5, 12.5]), { parent: bl2, rotation: R(s, [32, 0, 0]) });
    box(cube, bl3, 'shin_back_' + side(s), [4, 1, 11], [7, 7, 14], 'fur', { ell: { c: [5.5, 4, 12.5], r: [3, 5, 3] } });
    box(cube, bl3, 'cuff_back_' + side(s), [3.5, 2, 10.5], [7.5, 5, 14.5], 'bone', boneMat([3.5, 2, 10.5], [7.5, 5, 14.5]));
    const bp = m.bone('paw_back_' + side(s), P(s, [5.5, 1, 12.5]), { parent: bl3 });
    box(cube, bp, 'paw_back_' + side(s), [3.5, 0, 9], [7.5, 2, 14], 'fur', { ell: { c: [5.5, 1.5, 11.5], r: [4, 3, 4] } });
    claws(cube, bp, 'claw_back_' + side(s), 3.5, 0, 9);
  });

  // ----------------------------------------------------------------- serpent tail with an ember arrowhead
  const tailEll = { c: [0, 26, 30], r: [4, 4, 18] };
  let parent = m.bone('tail', [0, 24, 15.5], { parent: torso, rotation: [-24, 0, 0] });
  box(plain, parent, 'tail', [-1.5, 22.5, 15], [1.5, 25.5, 21], 'fur', { ell: tailEll });
  const segs = [[2, 21, 6, 12], [1, 27, 6, 10], [1, 33, 5, 8]];
  segs.forEach(([w, z0, len, rot], i) => {
    parent = m.bone('tail' + (i + 2), [0, 24, z0], { parent, rotation: [rot, 0, 0] });
    box(plain, parent, 'tail' + (i + 2), [-w / 2, 24 - w / 2, z0 - 0.5], [w / 2, 24 + w / 2, z0 + len - 0.5], 'fur', { ell: tailEll });
  });
  const tip = m.bone('tail_tip', [0, 24, 38], { parent, rotation: [8, 0, 0] });
  const arrow = [[5, 38, 2], [3, 40, 2], [1, 42, 2]];
  arrow.forEach(([w, z0, len], i) => {
    const from = [-w / 2, 23.5, z0], to = [w / 2, 24.5, z0 + len];
    m.cube(tip, {
      name: 'tail_tip' + (i ? '_' + i : ''), from, to,
      paint: houndoom('orange', ellOf([-2.5, 23.5, 38], [2.5, 24.5, 44], 2)),
      // the arrowhead smoulders: its edges glow
      emissive: (ctx) => ((ctx.face === 'east' || ctx.face === 'west' || ctx.face === 'south' || i === 2) ? ctx.pal.orange[3].slice() : null),
    });
  });

  // ----------------------------------------------------------------- necks and heads
  // A head is built around its pivot (x0, y0, z0) at the top of its neck, in right-hand coordinates
  // (cube() mirrors it for the left head). big = the leader in the middle.
  const headZone = (snoutTop) => (ctx) => ((ctx.p[1] < snoutTop && ctx.face !== 'up') || ctx.face === 'down' ? 'orange' : 'fur');
  // eyes: 2 x 1 each on the front of the skull, red iris on the inner side, an angry brow above it;
  // the closed-eye overlay (for blinking and sleep) hides 0.4 inside the skull and slides 0.5 forward
  function head(cube, parentBone, name, x0, y0, z0, big, s = 1, rot = [0, 0, 0]) {
    const hb = m.bone(name, P(s, [x0, y0, z0]), { parent: parentBone, rotation: R(s, rot) });
    const W = big ? 4.5 : 3.5, Hh = big ? 8 : 7, D = big ? 8 : 7;
    const skullFrom = [x0 - W, y0 - 1, z0 - D / 2 - 1], skullTo = [x0 + W, y0 - 1 + Hh, z0 + D / 2 - 1];
    const hEll = ellOf(skullFrom, skullTo, 2);
    const front = skullFrom[2];
    const eyeY = skullFrom[1] + (big ? 4 : 3);
    const eyeX = big ? [x0 + 1.5, x0 + 3.5] : [x0 + 0.5, x0 + 2.5];
    const eyeAt = (ctx) => {
      if (ctx.face !== 'north') return '.';
      const [x, y] = ctx.lp;
      const lx = Math.abs(x - x0) + x0; // both eyes, mirrored about the middle of the head
      if (lx > eyeX[0] && lx < eyeX[1]) {
        if (y > eyeY && y < eyeY + 1) return lx < eyeX[0] + 1 ? 'R' : 'W';
        if (y > eyeY + 1 && y < eyeY + 2 && lx < eyeX[0] + 1) return 'D';
      }
      return '.';
    };
    box(cube, hb, name + '_skull', skullFrom, skullTo, 'fur', {
      ell: hEll,
      extra: {
        emissive: (ctx) => ({ R: hex('#ff4a3a'), W: ctx.pal.eye }[eyeAt(ctx)]?.slice() ?? null),
        alpha: (ctx) => ({ R: A.hi, W: A.mid }[eyeAt(ctx)]?.slice() ?? null),
      },
    });
    m.decal({ cubes: [name + '_skull'], face: 'north', fn: (ctx) => ({ R: ctx.pal.eye, W: ctx.pal.white, D: ctx.pal.fur[0] }[eyeAt(ctx)]?.slice()) });
    const closed = m.bone(name + '_eyes_closed', P(s, [x0, eyeY, front + 0.4]), { parent: hb });
    for (const [a, b] of [[eyeX[0], eyeX[1]], [2 * x0 - eyeX[1], 2 * x0 - eyeX[0]]]) {
      cube(closed, {
        name: `${name}_eyes_closed_${a > x0 ? 'r' : 'l'}`, from: [a, eyeY, front + 0.4], to: [b, eyeY + 2, front + 0.4],
        paint: (ctx) => {
          if (ctx.face !== 'north') return null;
          // bottom row: the closed lid line; top row: the fur above, keeping the dark brow over the inner corner
          if (ctx.row === 1) return ctx.pal.fur[0].slice();
          if (Math.abs(ctx.lp[0] - x0) < eyeX[0] - x0 + 1) return ctx.pal.fur[0].slice();
          return ctx.sampleLocal(name + '_skull', 'north', ctx.lp);
        },
      });
    }
    // muzzle: black on top, Houndoom's orange underneath; the roof of the mouth glows like embers
    const sn = big ? [2.5, 3, 6] : [2, 3, 5];
    const snFrom = [x0 - sn[0], y0 - 0.5, front - sn[2]], snTo = [x0 + sn[0], y0 - 0.5 + sn[1], front];
    const snPaint = houndoom(headZone(y0 + 1), ellOf(snFrom, snTo, 2));
    cube(hb, {
      name: name + '_snout', from: snFrom, to: snTo,
      paint: (ctx) => {
        if (ctx.face === 'down') return ctx.pal.mouth[1].slice();
        if (ctx.face === 'north' && ctx.row === 0 && Math.abs(ctx.lp[0] - x0) < 1.5) return ctx.pal.fur[0].slice(); // nose
        return snPaint(ctx);
      },
      emissive: (ctx) => (ctx.face === 'down' ? ctx.pal.orange[1].slice() : null),
    });
    const fang = houndoom('bone', hEll, { hi: 0.5 });
    cube(hb, { name: name + '_fang_r', from: [x0 + sn[0] - 1.5, y0 - 1.5, front - sn[2] + 0.5], to: [x0 + sn[0] - 0.5, y0 - 0.5, front - sn[2] + 1.5], paint: fang });
    cube(hb, { name: name + '_fang_l', from: [x0 - sn[0] + 0.5, y0 - 1.5, front - sn[2] + 0.5], to: [x0 - sn[0] + 1.5, y0 - 0.5, front - sn[2] + 1.5], paint: fang });
    // jaw, hinged at the back
    const jaw = m.bone(name + '_jaw', P(s, [x0, y0 - 0.5, front]), { parent: hb });
    const jw = big ? 2 : 1.5;
    const jFrom = [x0 - jw, y0 - 2.5, front - sn[2] + 1], jTo = [x0 + jw, y0 - 0.5, front + 1];
    const jawPaint = houndoom('orange', ellOf(jFrom, jTo, 2));
    cube(jaw, {
      name: name + '_jaw', from: jFrom, to: jTo,
      paint: (ctx) => {
        if (ctx.face !== 'up') return jawPaint(ctx);
        return (Math.abs(ctx.lp[0] - x0) < jw - 0.5 && ctx.lp[2] < front - 1 ? ctx.pal.tongue[(ctx.tu + ctx.tv) % 2 ? 1 : 2] : ctx.pal.mouth[0]).slice();
      },
      emissive: (ctx) => (ctx.face === 'up' ? ctx.pal.orange[ctx.lp[2] < front - 3 ? 2 : 0].slice() : null),
    });
    // horns: Houndoom's ram horns on both sides; the leader's are bigger and raked far back (in a
    // Houndoom pack, the one whose horns are raked back is the leader)
    const hs = big ? [[3, 5, 3], [2, 6, 2], [1, 5, 1]] : [[2, 4, 2], [2, 4, 1], [1, 3, 1]];
    const hr = big ? [[26, 22, -28], [58, 0, 0], [48, 0, 0]] : [[-6, 18, -34], [40, 0, 0], [40, 0, 0]];
    for (const hs2 of [1, -1]) {
      let hp = hb;
      const hx = x0 + hs2 * (W - 1.5), hz = z0 - 1;
      let hy = skullTo[1] - 1;
      hs.forEach(([w, h, d], i) => {
        const bn = `${name}_horn_${hs2 * s > 0 ? 'r' : 'l'}${i ? i + 1 : ''}`; // the side it really ends up on
        hp = m.bone(bn, P(s, [hx, hy, hz]), { parent: hp, rotation: R(s, [hr[i][0], hs2 * hr[i][1], hs2 * hr[i][2]]) });
        box(cube, hp, bn, [hx - w / 2, hy, hz - d / 2], [hx + w / 2, hy + h, hz + d / 2], 'bone', { ell: ellOf([hx - 2, hy, hz - 2], [hx + 2, hy + h, hz + 2], 2), hi: 0.6 });
        hy += h;
      });
    }
    return { bone: hb, jaw };
  }

  // leader (centre) neck and head
  const neck = m.bone('neck', [0, 26, -10], { parent: torso, rotation: [-16, 0, 0] });
  box(plain, neck, 'neck', [-3.5, 25, -13.5], [3.5, 36, -6.5], (ctx) => (ctx.face === 'north' && ctx.p[1] < 30 ? 'orange' : 'fur'), { ell: { c: [0, 30, -10], r: [5, 8, 5] } });
  const lh = head(plain, neck, 'head', 0, 36, -10, true, 1, [12, 0, 0]);

  // side necks and heads (followers: smaller, horns curling forward); the left one mirrors the right one
  symmetric((s, cube) => {
    const n = m.bone('neck_' + side(s), P(s, [4.5, 26, -10]), { parent: torso, rotation: R(s, [-12, 0, -36]) });
    box(cube, n, 'neck_' + side(s), [2, 25, -12.5], [7, 34, -7.5], (ctx) => (ctx.face === 'north' && ctx.p[1] < 29 ? 'orange' : 'fur'), { ell: { c: [4.5, 29, -10], r: [4, 7, 4] } });
    // level the head again (the neck leans out) and turn it a little outwards
    head(cube, n, 'head_' + side(s), 4.5, 34, -10, false, s, [10, -16, 36]);
  });

  // ----------------------------------------------------------------- locators
  m.locator(root, 'root', [0, 0, 0]);
  m.locator(root, 'top', [0, 50, -8]);
  m.locator(torso, 'middle', [0, 21, 0]);
  m.locator(lh.bone, 'target', [0, 38, -24]);
  m.locator(lh.bone, 'head', [0, 43, -10], { extra: ['item_hat'] });
  m.locator(lh.bone, 'face', [0, 38, -15], { extra: ['item_face'] });
  m.locator(lh.bone, 'mouth', [0, 35, -21], { extra: ['special'] });
  m.locator(lh.jaw, 'item', [0, 34.5, -19]);
  m.locator(lh.bone, 'eye_right', [2.5, 39.5, -15]);
  m.locator(lh.bone, 'eye_left', [-2.5, 39.5, -15]);
  m.locator(m.boneMap.head_right, 'mouth_right', [4.5, 33.5, -19]);
  m.locator(m.boneMap.head_left, 'mouth_left', [-4.5, 33.5, -19]);
  m.locator(m.boneMap.paw_front_right, 'foot_primary', [5.5, 0.5, -10], { extra: ['physical'] });
  m.locator(m.boneMap.tail_tip, 'tail', [0, 24, 41]);

  require('./anims')(m);
  return m;
}

module.exports = { ID, build, PALETTES };
