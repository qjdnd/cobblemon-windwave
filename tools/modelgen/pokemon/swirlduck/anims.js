// Animations for Swirlduck. Values are Blockbench-space (what Blockbench shows):
// rot +x = nose up, +y = turn to its left, +z = roll toward its left.
// pos +x = its right, +y = up, +z = backwards.
'use strict';
const S = (amp, speed, phase = 0, off = 0) => {
  if (!amp) return off;
  const core = `math.sin(q.anim_time*${speed}${phase ? (phase > 0 ? '+' + phase : phase) : ''})`;
  const a = amp === 1 ? core : `${amp}*${core}`;
  return off ? `${off}+${a}` : a;
};
// half-wave: amp * max(0, sin(...)), for steps and lifts
const H = (amp, speed, phase = 0) => `${amp}*math.max(0, math.sin(q.anim_time*${speed}${phase ? '+' + phase : ''}))`;
const cr = (v) => ({ v, lerp: 'catmullrom' });
const mirror = (v) => [v[0], -v[1], -v[2]];
const mirrorKeys = (keys) => Object.fromEntries(Object.entries(keys).map(([t, k]) => [t, Array.isArray(k) ? mirror(k) : { ...k, v: mirror(k.v) }]));

const SHOW = -0.5; // z offset that slides an expression plane out in front of the face
const shown = (t0, t1, d = 0.0417) => ({ 0: [0, 0, 0], [t0]: [0, 0, 0], [+(t0 + d).toFixed(4)]: [0, 0, SHOW], [t1]: [0, 0, SHOW], [+(t1 + d).toFixed(4)]: [0, 0, 0] });
const CRY = 'pokemon.golduck.cry';

// Arm poses for the right arm, added to the resting pose ({a: arm, f: forearm}); the left arm mirrors them.
const REST = { a: [0, 0, 0], f: [0, 0, 0] };
// both palms pressed to the sides of the shell, like Psyduck clutching its head (solved for the palm at x 9.5, y 22)
const HOLD_SHELL = { a: [30, -30, 85], f: [0, 16, 0] };
// hands thrust forward, palms out
const THRUST = { a: [20, -40, 40], f: [0, -30, 0] };
// arms spread wide
const SPREAD = { a: [10, -20, 40], f: [0, -30, 0] };
function armTracks(frames, smooth = true) {
  const k = (v) => (smooth ? cr(v) : v);
  const tr = { arm_right: { rotation: {} }, forearm_right: { rotation: {} }, arm_left: { rotation: {} }, forearm_left: { rotation: {} } };
  for (const [t, pose] of frames) {
    tr.arm_right.rotation[t] = k(pose.a); tr.forearm_right.rotation[t] = k(pose.f);
    tr.arm_left.rotation[t] = k(mirror(pose.a)); tr.forearm_left.rotation[t] = k(mirror(pose.f));
  }
  return tr;
}
// the shoulder feathers lift out of the way when the arms go up
const capeLift = (frames) => {
  const r = {}, l = {};
  for (const [t, z] of frames) { r[t] = cr([0, 0, z]); l[t] = cr([0, 0, -z]); }
  return { capelet_right: { rotation: r }, capelet_left: { rotation: l } };
};

module.exports = (m) => {
  // ------------------------------------------------------------ ground idle: blank Psyduck stare, laughing bill, swaying
  m.anim('ground_idle', {
    loop: true,
    bones: {
      torso: { scale: [S(0.01, 120, 0, 1), S(0.02, 120, 0, 1), S(0.01, 120, 0, 1)], rotation: [0, 0, S(1.5, 60)] },
      head: { rotation: [S(2, 120, -40), S(4, 40), S(3, 60, 30)], position: [0, S(0.15, 120, -40), 0] },
      jaw: { rotation: [S(3, 240, 0, -1), 0, 0] },
      pupil_right: { position: [S(0.6, 36), S(-0.3, 50, 90, -0.2), 0] },
      pupil_left: { position: [S(0.6, 36), S(-0.3, 50, 90, -0.2), 0] },
      capelet_right: { rotation: [0, 0, S(3, 120, 60)] },
      capelet_left: { rotation: [0, 0, S(-3, 120, 60)] },
      cape_back: { rotation: [S(2, 120, 60), 0, 0] },
      arm_right: { rotation: [S(4, 120, 20), 0, S(3, 60)] },
      arm_left: { rotation: [S(4, 120, 200), 0, S(-3, 60)] },
      forearm_right: { rotation: [0, S(5, 120, 60), 0] },
      forearm_left: { rotation: [0, S(-5, 120, 240), 0] },
      tail: { rotation: [S(2, 120), S(8, 60), 0] },
      tail2: { rotation: [0, S(8, 60, -40), 0] },
      tail3: { rotation: [0, S(10, 60, -80), 0] },
      gem: { scale: [S(0.05, 120, 0, 1), S(0.05, 120, 0, 1), 1] },
    },
  });

  // ------------------------------------------------------------ walk: bow-legged stomp, arms and cape swinging
  const W = 400; // 0.9 s stride
  m.anim('ground_walk', {
    loop: true,
    bones: {
      // the body dips when the legs are furthest apart so the planted foot stays on the ground
      body: { position: [0, `-0.5*math.abs(math.sin(q.anim_time*${W}))`, 0], rotation: [0, S(5, W), 0] },
      torso: { rotation: [-3, 0, S(4, W)] },
      head: { rotation: [S(2, W * 2, 60, 2), S(-4, W), S(-3, W)] },
      leg_right: { rotation: [S(24, W), 0, 0], position: [0, H(1, W, 90), 0] },
      leg_left: { rotation: [S(24, W, 180), 0, 0], position: [0, H(1, W, 270), 0] },
      foot_right: { rotation: [S(-24, W), 0, 0] },
      foot_left: { rotation: [S(-24, W, 180), 0, 0] },
      arm_right: { rotation: [S(-18, W), 0, 0] },
      arm_left: { rotation: [S(-18, W, 180), 0, 0] },
      capelet_right: { rotation: [0, 0, S(5, W * 2, 90, 2)] },
      capelet_left: { rotation: [0, 0, S(-5, W * 2, 90, -2)] },
      cape_back: { rotation: [S(4, W * 2, 90, -3), 0, 0] },
      jaw: { rotation: [S(4, W * 2, 30), 0, 0] },
      tail: { rotation: [0, S(12, W, -40), 0] },
      tail2: { rotation: [0, S(10, W, -80), 0] },
      tail3: { rotation: [0, S(12, W, -120), 0] },
    },
  });

  // ------------------------------------------------------------ water idle: floats with the shell above the water, paddling
  m.anim('water_idle', {
    loop: true,
    bones: {
      body: { position: [0, S(0.4, 100, 0, -9), 0], rotation: [S(2, 80, 90), 0, S(3, 80)] },
      head: { rotation: [S(2, 100, -60, 3), S(4, 40), 0] },
      arm_right: { rotation: [S(12, 240, 0, -10), S(-15, 240, 90, -10), 0] },
      arm_left: { rotation: [S(12, 240, 180, -10), S(15, 240, 270, 10), 0] },
      leg_right: { rotation: [S(20, 240, 0, 10), 0, 0] },
      leg_left: { rotation: [S(20, 240, 180, 10), 0, 0] },
      capelet_right: { rotation: [0, 0, S(3, 100, 60, 8)] },
      capelet_left: { rotation: [0, 0, S(-3, 100, 60, -8)] },
      tail: { rotation: [-10, S(12, 120), 0] },
    },
  });

  // ------------------------------------------------------------ water swim: lies forward, kicks and strokes
  const SW = 360;
  m.anim('water_swim', {
    loop: true,
    bones: {
      body: { position: [0, S(0.3, SW * 2, 0, -10), 3], rotation: [-62, S(3, SW), S(4, SW)] },
      head: { rotation: [S(3, SW * 2, 60, 38), 0, S(-3, SW)] },
      leg_right: { rotation: [S(30, SW * 2, 0, -20), 0, 0] },
      leg_left: { rotation: [S(30, SW * 2, 180, -20), 0, 0] },
      arm_right: { rotation: [S(30, SW, 0, 20), S(-35, SW, 90, -10), 0] },
      arm_left: { rotation: [S(30, SW, 180, 20), S(35, SW, 270, 10), 0] },
      capelet_right: { rotation: [0, 0, S(6, SW * 2, 90, 10)] },
      capelet_left: { rotation: [0, 0, S(-6, SW * 2, 90, -10)] },
      cape_back: { rotation: [S(5, SW * 2), 0, 0] },
      tail: { rotation: [-15, S(20, SW), 0] },
      tail2: { rotation: [0, S(18, SW, -60), 0] },
    },
  });

  // ------------------------------------------------------------ battle idle: wide stance, hands up, eyes focused, gem pulsing
  const B = 240;
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { position: [0, `0.35*math.abs(math.sin(q.anim_time*${B}))`, 0] },
      leg_right: { rotation: [0, 0, 6] },
      leg_left: { rotation: [0, 0, -6] },
      foot_right: { rotation: [0, 0, -6] },
      foot_left: { rotation: [0, 0, 6] },
      torso: { rotation: [S(1.5, B * 2, 0, -5), 0, 0] },
      head: { rotation: [S(2, B * 2, -60, -4), S(3, 60), 0] },
      jaw: { rotation: [S(3, B * 2, 0, 10), 0, 0] },
      pupil_right: { position: [0, -1, 0] },
      pupil_left: { position: [0, -1, 0] },
      arm_right: { rotation: [S(4, B * 2, 0, 25), -20, 30] },
      arm_left: { rotation: [S(4, B * 2, 0, 25), 20, -30] },
      forearm_right: { rotation: [0, 20, 0] },
      forearm_left: { rotation: [0, -20, 0] },
      capelet_right: { rotation: [0, 0, S(3, B * 2, 90, 14)] },
      capelet_left: { rotation: [0, 0, S(-3, B * 2, 90, -14)] },
      gem: { scale: [S(0.12, B * 2, 0, 1.08), S(0.12, B * 2, 0, 1.08), 1] },
      tail: { rotation: [-6, S(14, B), 0] },
      tail2: { rotation: [0, S(12, B, -60), 0] },
    },
  });

  // ------------------------------------------------------------ sleep: sits on its tail, head and shell nodding forward
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { position: [0, -3.55, 0] },
      leg_right: { rotation: [62, -18, 0], position: [0, 1.5, -1] },
      leg_left: { rotation: [62, 18, 0], position: [0, 1.5, -1] },
      foot_right: { rotation: [-62, 0, 0] },
      foot_left: { rotation: [-62, 0, 0] },
      torso: { rotation: [6, 0, 0], scale: [S(0.012, 80, 0, 1.01), S(0.025, 80, 0, 0.99), S(0.012, 80, 0, 1.01)] },
      head: { rotation: [S(1.5, 80, -60, -16), 4, 8], position: [0, S(0.1, 80, -60, -0.3), 0] },
      jaw: { rotation: [S(2, 80, -60, 17), 0, 0] },
      eyes_closed: { position: [0, 0, SHOW] },
      arm_right: { rotation: [-10, 10, 20] },
      arm_left: { rotation: [-10, -10, -20] },
      forearm_right: { rotation: [0, 30, 0] },
      forearm_left: { rotation: [0, -30, 0] },
      capelet_right: { rotation: [0, 0, -6] },
      capelet_left: { rotation: [0, 0, 6] },
      tail: { rotation: [-10, 30, 0] },
      tail2: { rotation: [0, 25, 0] },
      tail3: { rotation: [0, 25, 0] },
      gem: { scale: [S(0.06, 80, 0, 0.95), S(0.06, 80, 0, 0.95), 1] },
    },
  });

  // ------------------------------------------------------------ blink
  m.anim('blink', {
    length: 0.25,
    bones: { eyes_closed: { position: shown(0, 0.1667) } },
  });

  // ------------------------------------------------------------ headache (quirk): clutches its shell and sways, eyes screwed shut
  m.anim('headache', {
    length: 3.6,
    bones: {
      ...armTracks([[0, REST], [0.4, HOLD_SHELL], [3.0, HOLD_SHELL], [3.4, REST], [3.6, REST]]),
      ...capeLift([[0, 0], [0.4, 28], [3.0, 28], [3.4, 0]]),
      head: {
        rotation: {
          0: cr([0, 0, 0]), 0.45: cr([6, 0, 0]), 0.95: cr([6, 5, 10]), 1.55: cr([6, -5, -10]), 2.15: cr([6, 5, 10]),
          2.75: cr([6, -3, -7]), 3.25: cr([0, 0, 0]), 3.6: cr([0, 0, 0]),
        },
      },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.95: cr([0, 0, -3]), 1.55: cr([0, 0, 3]), 2.15: cr([0, 0, -3]), 2.75: cr([0, 0, 2]), 3.25: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.4: [14, 0, 0], 3.0: [14, 0, 0], 3.3: [0, 0, 0] } },
      eyes_closed: { position: shown(0.35, 3.0) },
      tail: { rotation: { 0: [0, 0, 0], 0.95: [0, 12, 0], 1.55: [0, -12, 0], 2.15: [0, 12, 0], 2.75: [0, -8, 0], 3.25: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ laugh (quirk): rolls its eyes up and cackles, bill clacking
  m.anim('laugh', {
    length: 2.2,
    bones: {
      head: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([12, 0, 4]), 1.8: cr([10, 0, -3]), 2.2: cr([0, 0, 0]) } },
      jaw: {
        rotation: {
          0: [0, 0, 0], 0.25: [-18, 0, 0], 0.4: [4, 0, 0], 0.55: [-18, 0, 0], 0.7: [4, 0, 0], 0.85: [-18, 0, 0],
          1.0: [4, 0, 0], 1.15: [-18, 0, 0], 1.3: [4, 0, 0], 1.45: [-18, 0, 0], 1.9: [-6, 0, 0], 2.2: [0, 0, 0],
        },
      },
      eyes_happy: { position: shown(0.2, 1.8) },
      torso: {
        rotation: { 0: cr([0, 0, 0]), 0.3: cr([6, 0, 0]), 1.8: cr([5, 0, 0]), 2.2: cr([0, 0, 0]) },
        position: { 0: [0, 0, 0], 0.25: [0, 0, 0], 0.4: [0, 0.5, 0], 0.55: [0, 0, 0], 0.7: [0, 0.5, 0], 0.85: [0, 0, 0], 1.0: [0, 0.5, 0], 1.15: [0, 0, 0], 1.3: [0, 0.5, 0], 1.45: [0, 0, 0] },
      },
      ...armTracks([[0, REST], [0.3, { a: [0, 0, 18], f: [0, -20, 0] }], [1.8, { a: [0, 0, 18], f: [0, -20, 0] }], [2.2, REST]]),
      tail: { rotation: { 0: [0, 0, 0], 0.4: [0, 15, 0], 0.8: [0, -15, 0], 1.2: [0, 15, 0], 1.6: [0, -15, 0], 2.0: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ cry: shell thrown back, bill wide open, arms and cape spread
  m.anim('cry', {
    length: 1.25,
    sounds: { 0.125: CRY },
    bones: {
      head: { rotation: { 0: cr([0, 0, 0]), 0.15: cr([-5, 0, 0]), 0.35: cr([18, 0, 0]), 0.9: cr([15, 0, 3]), 1.25: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.12: [0, 0, 0], 0.3: [-26, 0, 0], 0.5: [-20, 0, 0], 0.7: [-26, 0, 0], 1.0: [0, 0, 0] } },
      eyes_happy: { position: shown(0.12, 0.95) },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.35: cr([6, 0, 0]), 0.9: cr([5, 0, 0]), 1.25: cr([0, 0, 0]) } },
      ...armTracks([[0, REST], [0.35, SPREAD], [0.9, SPREAD], [1.25, REST]]),
      ...capeLift([[0, 0], [0.35, 24], [0.9, 24], [1.25, 0]]),
      gem: { scale: { 0: [1, 1, 1], 0.3: [1.3, 1.3, 1], 0.9: [1.2, 1.2, 1], 1.2: [1, 1, 1] } },
      tail: { rotation: { 0: [0, 0, 0], 0.3: [-12, 18, 0], 0.6: [-12, -18, 0], 0.9: [-8, 12, 0], 1.25: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ physical: charges and rams with the spiked shell
  m.anim('physical', {
    length: 1.3,
    bones: {
      body: {
        position: { 0: cr([0, 0, 0]), 0.3: cr([0, 0.6, 2]), 0.5: cr([0, 1.4, -4]), 0.62: cr([0, 1.5, -6]), 0.95: cr([0, 0.2, -1.5]), 1.3: cr([0, 0, 0]) },
      },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([10, 0, 0]), 0.5: cr([-26, 0, 0]), 0.62: cr([-30, 0, 0]), 0.95: cr([-5, 0, 0]), 1.3: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([8, 0, 0]), 0.5: cr([-18, 0, 0]), 0.7: cr([-14, 0, 0]), 1.1: cr([0, 0, 0]), 1.3: cr([0, 0, 0]) } },
      leg_right: { rotation: { 0: [0, 0, 0], 0.3: [-10, 0, 0], 0.55: [30, 0, 0], 0.9: [0, 0, 0] } },
      leg_left: { rotation: { 0: [0, 0, 0], 0.3: [10, 0, 0], 0.55: [-28, 0, 0], 0.9: [0, 0, 0] } },
      eyes_closed: { position: shown(0.48, 0.8) },
      jaw: { rotation: { 0: [0, 0, 0], 0.45: [16, 0, 0], 0.8: [16, 0, 0], 1.1: [0, 0, 0] } },
      ...armTracks([[0, REST], [0.3, { a: [30, 20, 10], f: [0, 20, 0] }], [0.55, { a: [-40, 10, -10], f: [0, 0, 0] }], [0.95, REST], [1.3, REST]]),
      ...capeLift([[0, 0], [0.55, 18], [1.0, 0]]),
      tail: { rotation: { 0: [0, 0, 0], 0.3: [-15, 0, 0], 0.6: [15, 0, 0], 1.0: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ special: floats up holding its shell, the gem flares, then psychic blast
  const JITTER = 'math.sin(q.anim_time*2200)*0.25';
  m.anim('special', {
    length: 2.0,
    bones: {
      ...armTracks([[0, REST], [0.35, HOLD_SHELL], [1.2, HOLD_SHELL], [1.4, THRUST], [1.65, THRUST], [2.0, REST]]),
      ...capeLift([[0, 0], [0.35, 28], [1.2, 28], [1.4, 30], [1.65, 30], [2.0, 0]]),
      body: { position: { 0: cr([0, 0, 0]), 0.4: cr([0, 2.5, 0]), 1.2: cr([0, 3, 0]), 1.45: cr([0, 2.5, 0]), 1.8: cr([0, 0.3, 0]), 2.0: cr([0, 0, 0]) } },
      leg_right: { rotation: { 0: [0, 0, 0], 0.4: [8, 0, 4], 1.5: [8, 0, 4], 2.0: [0, 0, 0] } },
      leg_left: { rotation: { 0: [0, 0, 0], 0.4: [8, 0, -4], 1.5: [8, 0, -4], 2.0: [0, 0, 0] } },
      torso: {
        position: { 0: [0, 0, 0], 0.35: [JITTER, 0, 0], 1.2: [JITTER, 0, 0], 1.25: [0, 0, 0] },
        rotation: { 0: cr([0, 0, 0]), 0.35: cr([4, 0, 0]), 1.2: cr([4, 0, 0]), 1.4: cr([-8, 0, 0]), 2.0: cr([0, 0, 0]) },
      },
      head: { rotation: { 0: cr([0, 0, 0]), 0.35: cr([8, 0, 0]), 1.2: cr([8, 0, 0]), 1.4: cr([-6, 0, 0]), 2.0: cr([0, 0, 0]) } },
      gem: { scale: { 0: [1, 1, 1], 0.35: [1.3, 1.3, 1], 1.2: [1.5, 1.5, 1.2], 1.35: [1.9, 1.9, 1.4], 1.6: [1, 1, 1] } },
      eyes_closed: { position: shown(0.3, 1.2) },
      pupil_right: { position: { 0: [0, 0, 0], 1.25: [0, -1, 0], 1.8: [0, -1, 0], 2.0: [0, 0, 0] } },
      pupil_left: { position: { 0: [0, 0, 0], 1.25: [0, -1, 0], 1.8: [0, -1, 0], 2.0: [0, 0, 0] } },
      jaw: { rotation: { 0: [0, 0, 0], 0.35: [16, 0, 0], 1.2: [16, 0, 0], 1.4: [-24, 0, 0], 1.7: [-24, 0, 0], 1.95: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: { position: { 0: cr([0, 0, 0]), 0.1: cr([0, 0.6, 2.5]), 0.3: cr([0, 0, 1.2]), 0.6: cr([0, 0, 0]) } },
      torso: { rotation: { 0: [0, 0, 0], 0.1: [12, 0, 0], 0.35: [2, 0, 0], 0.6: [0, 0, 0] } },
      head: { rotation: { 0: [0, 0, 0], 0.1: [12, 0, 6], 0.35: [2, 0, 0], 0.6: [0, 0, 0] } },
      eyes_closed: { position: shown(0, 0.4) },
      ...armTracks([[0, REST], [0.1, { a: [40, -30, 35], f: [0, -20, 0] }], [0.5, REST], [0.6, REST]], false),
      ...capeLift([[0, 0], [0.1, 20], [0.5, 0]]),
    },
  });

  // ------------------------------------------------------------ faint: dizzy eyes, wobbles, then topples backwards under the heavy shell
  // body lift per fall angle keeps the lowest point on the ground (measured with groundcheck.js)
  m.anim('faint', {
    length: 3,
    bones: {
      eyes_dizzy: { position: { 0: [0, 0, 0], 0.05: [0, 0, SHOW] } },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.25: cr([0, 0, 8]), 0.5: cr([-2, 0, -8]), 0.75: cr([-2, 0, 6]), 0.95: cr([0, 0, 0]), 1.2: cr([0, 0, 0]) } },
      body: {
        rotation: { 0: [0, 0, 0], 0.8: [0, 0, 0], 0.95: [-3, 0, 0], 1.15: [40, 0, 0], 1.22: [58, 0, 0], 1.3: [76, 0, 0], 1.42: [66, 0, 0], 1.55: [72, 0, 0] },
        position: { 0: [0, 0, 0], 0.8: [0, 0, 0], 0.95: [0, 0.3, -0.3], 1.15: [0, -0.4, 2], 1.22: [0, -0.1, 3], 1.3: [0, 3.24, 4], 1.42: [0, 2.3, 4], 1.55: [0, 2.6, 4] },
      },
      head: { rotation: { 0: cr([0, 0, 0]), 0.25: cr([0, 0, -6]), 0.5: cr([0, 0, 6]), 0.75: cr([0, 0, -5]), 0.95: cr([0, 0, 0]), 1.3: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 1.2: [0, 0, 0], 1.4: [-16, 0, 0] } },
      ...armTracks([[0, REST], [0.95, { a: [10, -10, 10], f: [0, 0, 0] }], [1.3, { a: [60, -30, 60], f: [0, -20, 0] }], [1.6, { a: [50, -30, 50], f: [0, -20, 0] }]], false),
      leg_right: { rotation: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.35: [-30, 0, 8], 1.6: [-20, 0, 6] } },
      leg_left: { rotation: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.35: [-30, 0, -8], 1.6: [-20, 0, -6] } },
      // the long tail lifts before the fall so it doesn't dig into the ground
      tail: { rotation: { 0: [0, 0, 0], 0.9: [0, 0, 0], 1.1: [-55, 0, 0] } },
    },
  });
};
