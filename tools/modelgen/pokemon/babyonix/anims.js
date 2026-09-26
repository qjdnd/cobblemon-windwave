// Animations for Baby Onix. Values are Blockbench-space (what Blockbench shows):
// rot +x = nose up, +y = turn to its left, +z = roll toward its left.
// pos +x = its right, +y = up, +z = backwards. For the tail (which points backwards) -x lifts the tip.
'use strict';
const S = (amp, speed, phase = 0, off = 0) => {
  if (!amp) return off;
  const core = `math.sin(q.anim_time*${speed}${phase ? (phase > 0 ? '+' + phase : phase) : ''})`;
  const a = amp === 1 ? core : `${amp}*${core}`;
  return off ? `${off}+${a}` : a;
};
const cr = (v) => ({ v, lerp: 'catmullrom' });

// the expression planes sit 0.40-0.43 inside each side of the head; sliding them out by 0.5 puts them
// 0.07-0.1 outside it, in front of the iris planes (0.03 outside)
const SHOW = 0.5;
const showKeys = (t0, t1, s, d = 0.0417) => ({ 0: [0, 0, 0], [t0]: [0, 0, 0], [+(t0 + d).toFixed(4)]: [s * SHOW, 0, 0], [t1]: [s * SHOW, 0, 0], [+(t1 + d).toFixed(4)]: [0, 0, 0] });
// both eyes of one expression: shown between t0 and t1 (always when t0 is null, from t0 on when t1 is null)
const keys = (t0, t1, s) => {
  if (t0 === null) return [s * SHOW, 0, 0];
  if (t1 === null) return { 0: [0, 0, 0], [t0]: [s * SHOW, 0, 0] };
  return showKeys(t0, t1, s);
};
const eyes = (name, t0, t1) => ({
  [`${name}_right`]: { position: keys(t0, t1, 1) },
  [`${name}_left`]: { position: keys(t0, t1, -1) },
});
// irises: z offset (negative = glancing forward, towards the snout; 0 = glancing back, the resting look)
const iris = (z) => ({ iris_right: { position: [0, 0, z] }, iris_left: { position: [0, 0, z] } });
const CRY = 'pokemon.onix.cry';

module.exports = (m) => {
  // ------------------------------------------------------------ ground idle: slow snake sway, tail tip wiggling, eyes glancing
  m.anim('ground_idle', {
    loop: true,
    bones: {
      torso: { rotation: [S(1.5, 60, 90), S(2, 40), S(2, 60)] },
      neck: { rotation: [S(2, 60, 30), S(3, 40, 60), S(3, 60, 180)] },
      head: { rotation: [S(2.5, 90, -40), S(6, 40, 120), S(2, 60, 240)] },
      jaw: { rotation: [S(1.5, 90, -40), 0, 0] },
      tail: { rotation: [0, S(5, 72), 0] },
      tail_tip: { rotation: [S(-8, 72, 90, -6), S(12, 72, -60), 0] },
      ...iris(S(1, 30, 0, -1)),
    },
  });

  // ------------------------------------------------------------ walk: slithers, the sway travelling from the head down the tail
  const W = 300; // 1.2 s cycle
  m.anim('ground_walk', {
    loop: true,
    bones: {
      body: { rotation: [0, S(6, W), 0], position: [S(0.5, W, 90), `0.25*math.abs(math.sin(q.anim_time*${W * 2}))`, 0] },
      torso: { rotation: [S(2, W * 2), S(-8, W, 60), S(4, W, 60)] },
      neck: { rotation: [S(2, W * 2, 60), S(7, W, 120), S(-3, W, 120)] },
      head: { rotation: [S(2, W * 2, 120, 2), S(-6, W, 180), 0] },
      tail: { rotation: [0, S(16, W, -60), 0] },
      tail_tip: { rotation: [-8, S(24, W, -120), 0] },
      ...iris(-1.5),
    },
  });

  // ------------------------------------------------------------ battle idle: rears up and glares, tail tip rattling
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { position: [0, `0.3*math.abs(math.sin(q.anim_time*240))`, 0] },
      torso: { rotation: [S(1.5, 240, 0, -4), S(3, 60), 0] },
      neck: { rotation: [S(2, 240, 40, 10), S(3, 60, 90), 0] },
      head: { rotation: [S(2, 240, 80, -14), S(4, 60, 180), 0] },
      jaw: { rotation: [S(3, 480, 0, -3), 0, 0] },
      tail: { rotation: [-6, S(8, 120), 0] },
      tail_tip: { rotation: [-38, S(10, 720), 0] },
      ...eyes('eyes_glare', null),
      ...iris(-2),
    },
  });

  // ------------------------------------------------------------ sleep: lays its head down in front of its body, tail curled round
  m.anim('sleep', {
    loop: true,
    bones: {
      torso: { rotation: [S(1, 72, 0, -12), 0, 0], scale: [1, S(0.015, 72, 0, 1), 1] },
      neck: { rotation: [-34, 0, 0] },
      head: { rotation: [S(1.5, 72, -60, -30), 6, 10] },
      jaw: { rotation: [S(1.5, 72, -60, 1.5), 0, 0] },
      tail: { rotation: [0, 38, 0] },
      tail_tip: { rotation: [0, 55, 0] },
      ...eyes('eyes_closed', null),
    },
  });

  // ------------------------------------------------------------ blink
  m.anim('blink', {
    length: 0.25,
    bones: { ...eyes('eyes_closed', 0, 0.1667) },
  });

  // ------------------------------------------------------------ yawn (quirk): big stretch upwards, jaw wide, eyes screwed shut
  m.anim('yawn', {
    length: 2.6,
    bones: {
      torso: { rotation: { 0: cr([0, 0, 0]), 0.6: cr([6, 0, 0]), 1.8: cr([6, 0, 0]), 2.6: cr([0, 0, 0]) } },
      neck: { rotation: { 0: cr([0, 0, 0]), 0.6: cr([10, 0, 0]), 1.8: cr([10, 0, 0]), 2.2: cr([-4, 0, 3]), 2.6: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.6: cr([22, 0, 4]), 1.8: cr([20, 0, -4]), 2.1: cr([-6, 8, 0]), 2.35: cr([-6, -8, 0]), 2.6: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: cr([0, 0, 0]), 0.5: cr([-4, 0, 0]), 1.0: cr([-34, 0, 0]), 1.6: cr([-30, 0, 0]), 1.9: cr([0, 0, 0]), 2.6: cr([0, 0, 0]) } },
      tail_tip: { rotation: { 0: [0, 0, 0], 0.8: [-30, 0, 0], 1.8: [-30, 0, 0], 2.3: [0, 0, 0] } },
      ...eyes('eyes_closed', 0.45, 1.9),
    },
  });

  // ------------------------------------------------------------ tail wag (quirk): looks back at its tail, which wags like a pup's
  m.anim('tail_wag', {
    length: 2.8,
    bones: {
      neck: { rotation: { 0: cr([0, 0, 0]), 0.5: cr([0, 20, 0]), 2.2: cr([0, 20, 0]), 2.8: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.5: cr([-8, 32, 6]), 2.2: cr([-8, 32, 6]), 2.8: cr([0, 0, 0]) } },
      tail: { rotation: { 0: [0, 0, 0], 0.6: [0, 20, 0], 0.8: [0, -20, 0], 1.0: [0, 20, 0], 1.2: [0, -20, 0], 1.4: [0, 20, 0], 1.6: [0, -20, 0], 1.8: [0, 20, 0], 2.2: [0, 0, 0] } },
      tail_tip: { rotation: { 0: [0, 0, 0], 0.5: [-35, 0, 0], 0.7: [-35, 30, 0], 0.9: [-35, -30, 0], 1.1: [-35, 30, 0], 1.3: [-35, -30, 0], 1.5: [-35, 30, 0], 1.7: [-35, -30, 0], 1.9: [-35, 0, 0], 2.3: [0, 0, 0] } },
      ...eyes('eyes_happy', 0.55, 2.1),
    },
  });

  // ------------------------------------------------------------ cry: rears up and roars
  m.anim('cry', {
    length: 1.5,
    sounds: { 0.125: CRY },
    bones: {
      torso: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([8, 0, 0]), 1.1: cr([7, 0, 0]), 1.5: cr([0, 0, 0]) } },
      neck: { rotation: { 0: cr([0, 0, 0]), 0.15: cr([-5, 0, 0]), 0.35: cr([14, 0, 0]), 1.1: cr([12, 0, 0]), 1.5: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.35: cr([20, 0, 0]), 0.7: cr([18, 0, 4]), 1.0: cr([18, 0, -4]), 1.5: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.12: [0, 0, 0], 0.3: [-34, 0, 0], 0.9: [-30, 0, 0], 1.2: [0, 0, 0] } },
      tail_tip: { rotation: { 0: [0, 0, 0], 0.3: [-30, 0, 0], 1.1: [-30, 0, 0], 1.4: [0, 0, 0] } },
      ...eyes('eyes_glare', 0.12, 1.15),
    },
  });

  // ------------------------------------------------------------ physical: rears back and slams its rock head forward
  m.anim('physical', {
    length: 1.3,
    bones: {
      body: { position: { 0: cr([0, 0, 0]), 0.35: cr([0, 0, 1.2]), 0.55: cr([0, 0.4, -3]), 0.7: cr([0, 0, -3.5]), 1.0: cr([0, 0, -1]), 1.3: cr([0, 0, 0]) } },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.35: cr([10, 0, 0]), 0.55: cr([-16, 0, 0]), 0.7: cr([-20, 0, 0]), 1.0: cr([-4, 0, 0]), 1.3: cr([0, 0, 0]) } },
      neck: { rotation: { 0: cr([0, 0, 0]), 0.35: cr([12, 0, 0]), 0.55: cr([-18, 0, 0]), 0.7: cr([-22, 0, 0]), 1.0: cr([-4, 0, 0]), 1.3: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.35: cr([10, 0, 0]), 0.55: cr([-14, 0, 0]), 0.75: cr([-8, 0, 0]), 1.3: cr([0, 0, 0]) } },
      tail: { rotation: { 0: [0, 0, 0], 0.35: [0, 0, 0], 0.55: [-10, 0, 0], 0.9: [0, 0, 0] } },
      tail_tip: { rotation: { 0: [0, 0, 0], 0.35: [-30, 0, 0], 0.6: [10, 0, 0], 1.0: [0, 0, 0] } },
      ...eyes('eyes_glare', 0, 0.5),
      ...eyes('eyes_closed', 0.52, 0.8),
    },
  });

  // ------------------------------------------------------------ special: whips its tail up over its back and slams it down (rock throw)
  m.anim('special', {
    length: 1.8,
    bones: {
      torso: { rotation: { 0: cr([0, 0, 0]), 0.4: cr([6, 0, -4]), 0.9: cr([8, 0, 4]), 1.15: cr([-6, 0, 0]), 1.8: cr([0, 0, 0]) } },
      neck: { rotation: { 0: cr([0, 0, 0]), 0.4: cr([8, 0, 0]), 1.15: cr([-8, 0, 0]), 1.8: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.4: cr([14, 0, 0]), 1.0: cr([16, 0, 0]), 1.2: cr([-10, 0, 0]), 1.8: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.9: [0, 0, 0], 1.1: [-30, 0, 0], 1.45: [-26, 0, 0], 1.7: [0, 0, 0] } },
      // the slam is linear so the tail stops on the ground instead of overshooting into it
      tail: { rotation: { 0: [0, 0, 0], 0.3: [-20, 0, 0], 0.8: [-58, 0, 0], 1.05: [0, 0, 0], 1.15: [-6, 0, 0], 1.3: [0, 0, 0] } },
      tail_tip: { rotation: { 0: [0, 0, 0], 0.3: [-30, 0, 0], 0.8: [-70, 0, 0], 1.05: [0, 0, 0], 1.15: [-10, 0, 0], 1.3: [0, 0, 0] } },
      body: { position: { 0: [0, 0, 0], 1.05: [0, 0, 0], 1.1: [0, 0.6, 0], 1.25: [0, 0, 0] } },
      ...eyes('eyes_glare', 0.1, 1.55),
      ...iris(-2),
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: { position: { 0: cr([0, 0, 0]), 0.1: cr([0, 0.4, 2]), 0.3: cr([0, 0, 1]), 0.6: cr([0, 0, 0]) } },
      torso: { rotation: { 0: [0, 0, 0], 0.1: [10, 0, 0], 0.35: [2, 0, 0], 0.6: [0, 0, 0] } },
      neck: { rotation: { 0: [0, 0, 0], 0.1: [10, 0, 6], 0.4: [0, 0, 0] } },
      head: { rotation: { 0: [0, 0, 0], 0.1: [14, 0, 8], 0.4: [2, 0, 0], 0.6: [0, 0, 0] } },
      tail_tip: { rotation: { 0: [0, 0, 0], 0.1: [-25, 0, 0], 0.5: [0, 0, 0] } },
      ...eyes('eyes_closed', 0, 0.4),
    },
  });

  // ------------------------------------------------------------ faint: dizzy eyes, wobbles, then topples onto its side
  m.anim('faint', {
    length: 3,
    bones: {
      ...eyes('eyes_dizzy', 0.05, null),
      neck: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([0, 0, 8]), 0.6: cr([0, 0, -8]), 0.9: cr([0, 0, 6]), 1.1: cr([-10, 0, 0]), 1.5: cr([-20, 0, -6]), 3: cr([-20, 0, -6]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([0, 0, -8]), 0.6: cr([0, 0, 8]), 0.9: cr([0, 0, -6]), 1.1: cr([-6, 0, 0]), 1.5: cr([-16, 0, -10]), 3: cr([-16, 0, -10]) } },
      jaw: { rotation: { 0: [0, 0, 0], 1.2: [0, 0, 0], 1.45: [-18, 0, 0] } },
      body: {
        // lift per tilt angle keeps its side on the ground (measured with groundcheck.js)
        rotation: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.15: [0, 0, 28], 1.3: [0, 0, 55], 1.45: [0, 0, 82], 1.55: [0, 0, 76], 1.65: [0, 0, 80] },
        position: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.15: [0, 2.3, 0], 1.3: [0, 3.3, 0], 1.45: [0, 3.5, 0], 1.55: [0, 3.6, 0], 1.65: [0, 3.52, 0] },
      },
      tail: { rotation: { 0: [0, 0, 0], 1.2: [0, 0, 0], 1.6: [0, -20, 0] } },
      tail_tip: { rotation: { 0: [0, 0, 0], 1.2: [0, 0, 0], 1.6: [0, -25, 0] } },
    },
  });
};
