// Animations for Baby Psyduck. Values are Blockbench-space (what Blockbench shows):
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
// short smooth pulse once per period
const pulse = (amp, speed, phase = 0, sharp = 10) => `${amp}*math.pow(math.max(0, math.sin(q.anim_time*${speed}${phase ? '+' + phase : ''})), ${sharp})`;
const cr = (v) => ({ v, lerp: 'catmullrom' });
const mirror = (v) => [v[0], -v[1], -v[2]];
const mirrorKeys = (keys) => Object.fromEntries(Object.entries(keys).map(([t, k]) => [t, Array.isArray(k) ? mirror(k) : { ...k, v: mirror(k.v) }]));

const SHOW = -0.45; // z offset that slides an expression plane out in front of the face
const shown = (t0, t1, d = 0.0417) => ({ 0: [0, 0, 0], [t0]: [0, 0, 0], [+(t0 + d).toFixed(4)]: [0, 0, SHOW], [t1]: [0, 0, SHOW], [+(t1 + d).toFixed(4)]: [0, 0, 0] });
const CRY = 'pokemon.psyduck.cry';

// Arm keyframes for the right arm as [time, rotation, position]; armTracks() also returns the mirrored left arm.
// Rotations are added to the arms' resting pose (reaching forward and inward to the clasped hands).
const REST = { r: [0, 0, 0], p: [0, 0, 0] };
// both hands pressed to the sides of the head, Psyduck's headache pose (shoulders shrug up to reach)
const HOLD_HEAD = { r: [108, -30, -50], p: [0.5, 2.5, -0.5] };
// hands thrust forward
const THRUST = { r: [22, -38, 6], p: [0, 0.5, -0.5] };
function armTracks(frames) {
  const rot = {}, pos = {}, rotL = {}, posL = {};
  for (const [t, pose] of frames) {
    rot[t] = cr(pose.r); pos[t] = cr(pose.p);
    rotL[t] = cr(mirror(pose.r)); posL[t] = cr([-pose.p[0], pose.p[1], pose.p[2]]);
  }
  return { arm_right: { rotation: rot, position: pos }, arm_left: { rotation: rotL, position: posL } };
}

module.exports = (m) => {
  // ------------------------------------------------------------ ground idle: breathing, a slow baby wobble, the odd clap
  m.anim('ground_idle', {
    loop: true,
    bones: {
      torso: { scale: [S(0.012, 144, 0, 1), S(0.025, 144, 0, 1), S(0.012, 144, 0, 1)] },
      head: { rotation: [S(1.5, 144, -40), S(3, 48), S(3.5, 72)], position: [0, S(0.12, 144, -40), 0] },
      swirl: { rotation: [0, 0, S(6, 72, 90)] },
      arm_right: { rotation: [S(3, 144, 20), pulse(-14, 90, 0), 0] },
      arm_left: { rotation: [S(3, 144, 20), pulse(14, 90, 0), 0] },
      tail: { rotation: [S(3, 144, -60), S(12, 144), 0] },
      tail2: { rotation: [0, S(10, 144, -50), 0] },
    },
  });

  // ------------------------------------------------------------ walk: short-legged waddle
  const W = 560;
  m.anim('ground_walk', {
    loop: true,
    bones: {
      // the waddle rolls the torso so the planted foot stays on the ground
      torso: { rotation: [0, S(4, W), S(7, W)], position: [0, `0.4*math.abs(math.sin(q.anim_time*${W}))`, 0] },
      head: { rotation: [S(2, W * 2, 60, 1), S(-3, W), S(-4.5, W, 20)] },
      foot_right: { position: [0, H(1, W), S(1.4, W, 90)], rotation: [H(22, W), 0, 0] },
      foot_left: { position: [0, H(1, W, 180), S(1.4, W, 270)], rotation: [H(22, W, 180), 0, 0] },
      arm_right: { rotation: [S(8, W * 2, 30), S(4, W), 0] },
      arm_left: { rotation: [S(8, W * 2, 30), S(4, W), 0] },
      tail: { rotation: [0, S(18, W, -40), 0] },
      tail2: { rotation: [0, S(14, W, -90), 0] },
      swirl: { rotation: [0, 0, S(5, W, 40)] },
    },
  });

  // ------------------------------------------------------------ water idle: floats like an egg, paddling
  m.anim('water_idle', {
    loop: true,
    bones: {
      body: { position: [0, S(0.35, 120, 0, -3), 0], rotation: [S(3, 90, 90), 0, S(4, 90)] },
      head: { rotation: [S(2, 120, -60, 2), S(3, 45), S(-2, 90)] },
      foot_right: { rotation: [S(28, 360, 0, 12), 0, 0], position: [0, 0.5, 0] },
      foot_left: { rotation: [S(28, 360, 180, 12), 0, 0], position: [0, 0.5, 0] },
      arm_right: { rotation: [S(10, 360, 90, 10), S(-12, 360, 90, -18), 0] },
      arm_left: { rotation: [S(10, 360, 270, 10), S(12, 360, 270, 18), 0] },
      tail: { rotation: [-10, S(15, 180), 0] },
      swirl: { rotation: [0, 0, S(5, 90, 45)] },
    },
  });

  // ------------------------------------------------------------ water swim: leans forward, kicks and paddles
  const SW = 480;
  m.anim('water_swim', {
    loop: true,
    bones: {
      body: { position: [0, S(0.3, SW * 2, 0, -3.5), 0], rotation: [-38, S(3, SW), S(4, SW)] },
      head: { rotation: [S(2, SW * 2, 60, 30), 0, S(-3, SW)] },
      foot_right: { rotation: [S(35, SW * 2, 0, -20), 0, 0], position: [0, 0, 1] },
      foot_left: { rotation: [S(35, SW * 2, 180, -20), 0, 0], position: [0, 0, 1] },
      arm_right: { rotation: [S(25, SW, 0, 10), S(-25, SW, 90, -30), 0] },
      arm_left: { rotation: [S(25, SW, 180, 10), S(25, SW, 270, 30), 0] },
      tail: { rotation: [10, S(22, SW), 0] },
      swirl: { rotation: [0, 0, S(6, SW)] },
    },
  });

  // ------------------------------------------------------------ battle idle: bouncing, fists up, the swirl slowly turning
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { position: [0, `0.4*math.abs(math.sin(q.anim_time*300))`, 0] },
      torso: { rotation: [-4, 0, 0], scale: [1, S(0.02, 600, 0, 1), 1] },
      head: { rotation: [S(2, 300, -60, -3), S(4, 75), S(3, 100)] },
      arm_right: { rotation: [S(5, 600, 0, 38), -18, -6] },
      arm_left: { rotation: [S(5, 600, 0, 38), 18, 6] },
      tail: { rotation: [S(5, 300), S(15, 200), 0] },
      swirl: { rotation: [0, 0, 'q.anim_time*-120'] },
    },
  });

  // ------------------------------------------------------------ sleep: sits down, head nodding, bill slightly open
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { position: [0, -1.2, 0] },
      foot_right: { position: [0.4, 1.2, -0.6], rotation: [0, -18, 0] },
      foot_left: { position: [-0.4, 1.2, -0.6], rotation: [0, 18, 0] },
      torso: { rotation: [4, 0, 0], scale: [S(0.015, 90, 0, 1.01), S(0.03, 90, 0, 0.99), S(0.015, 90, 0, 1.01)] },
      head: { rotation: [S(1.5, 90, -60, -13), 3, 9], position: [0, S(0.1, 90, -60, -0.2), 0] },
      jaw: { rotation: [S(3, 90, -60, -6), 0, 0] },
      eyes_closed: { position: [0, 0, SHOW] },
      arm_right: { rotation: [-14, -6, 0] },
      arm_left: { rotation: [-14, 6, 0] },
      tail: { rotation: [24, 0, 0] },
      swirl: { rotation: [0, 0, S(4, 45)] },
    },
  });

  // ------------------------------------------------------------ blink
  m.anim('blink', {
    length: 0.25,
    bones: { eyes_closed: { position: shown(0, 0.1667) } },
  });

  // ------------------------------------------------------------ headache (quirk): clutches its head and sways, eyes screwed shut
  m.anim('headache', {
    length: 3.6,
    bones: {
      ...armTracks([[0, REST], [0.35, HOLD_HEAD], [3.0, HOLD_HEAD], [3.4, REST], [3.6, REST]]),
      head: {
        rotation: {
          0: cr([0, 0, 0]), 0.4: cr([5, 0, 0]), 0.9: cr([5, 4, 11]), 1.5: cr([5, -4, -11]), 2.1: cr([5, 4, 11]),
          2.7: cr([5, -3, -8]), 3.2: cr([0, 0, 0]), 3.6: cr([0, 0, 0]),
        },
      },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.9: cr([0, 0, -3]), 1.5: cr([0, 0, 3]), 2.1: cr([0, 0, -3]), 2.7: cr([0, 0, 2]), 3.2: cr([0, 0, 0]) } },
      swirl: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 2.9: [0, 0, -360], 3.6: [0, 0, -360] } },
      eyes_closed: { position: shown(0.3, 3.0) },
      tail: { rotation: { 0: [0, 0, 0], 0.9: [0, 12, 0], 1.5: [0, -12, 0], 2.1: [0, 12, 0], 2.7: [0, -8, 0], 3.2: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ cry: beak up, happy eyes, arms up
  m.anim('cry', {
    length: 0.9167,
    sounds: { 0.0833: CRY },
    bones: {
      head: { rotation: { 0: cr([0, 0, 0]), 0.15: cr([-4, 0, 0]), 0.3: cr([14, 0, 0]), 0.65: cr([12, 0, 3]), 0.9167: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.1: [0, 0, 0], 0.25: [-32, 0, 0], 0.4: [-24, 0, 0], 0.55: [-32, 0, 0], 0.75: [0, 0, 0] } },
      eyes_happy: { position: shown(0.1, 0.7) },
      torso: { scale: { 0: [1, 1, 1], 0.15: [1.04, 0.95, 1.04], 0.3: [0.97, 1.05, 0.97], 0.6: [1, 1.02, 1], 0.9167: [1, 1, 1] } },
      arm_right: { rotation: { 0: cr([0, 0, 0]), 0.25: cr([40, -30, -10]), 0.4: cr([30, -30, -10]), 0.55: cr([40, -30, -10]), 0.9167: cr([0, 0, 0]) } },
      arm_left: { rotation: mirrorKeys({ 0: cr([0, 0, 0]), 0.25: cr([40, -30, -10]), 0.4: cr([30, -30, -10]), 0.55: cr([40, -30, -10]), 0.9167: cr([0, 0, 0]) }) },
      tail: { rotation: { 0: [0, 0, 0], 0.2: [-10, 20, 0], 0.4: [-10, -20, 0], 0.6: [-10, 20, 0], 0.9167: [0, 0, 0] } },
      swirl: { rotation: { 0: [0, 0, 0], 0.2: [0, 0, 0], 0.8: [0, 0, -360] } },
    },
  });

  // ------------------------------------------------------------ physical: winds up and headbutts with its big head
  m.anim('physical', {
    length: 1.25,
    bones: {
      body: {
        position: { 0: cr([0, 0, 0]), 0.3: cr([0, 0, 1.8]), 0.48: cr([0, 1.2, -3.5]), 0.6: cr([0, 0.5, -5]), 0.9: cr([0, 0, -1]), 1.25: cr([0, 0, 0]) },
      },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([10, 0, 0]), 0.5: cr([-24, 0, 0]), 0.62: cr([-28, 0, 0]), 0.9: cr([-4, 0, 0]), 1.25: cr([0, 0, 0]) } },
      head: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([6, 0, 0]), 0.5: cr([-10, 0, 0]), 0.7: cr([-6, 0, 0]), 1.1: cr([0, 0, 0]), 1.25: cr([0, 0, 0]) } },
      eyes_closed: { position: shown(0.46, 0.76) },
      arm_right: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([20, -30, 0]), 0.55: cr([-35, -10, 0]), 0.9: cr([0, 0, 0]), 1.25: cr([0, 0, 0]) } },
      arm_left: { rotation: mirrorKeys({ 0: cr([0, 0, 0]), 0.3: cr([20, -30, 0]), 0.55: cr([-35, -10, 0]), 0.9: cr([0, 0, 0]), 1.25: cr([0, 0, 0]) }) },
      foot_right: { rotation: { 0: [0, 0, 0], 0.3: [0, 0, 0], 0.48: [14, 0, 0], 0.7: [0, 0, 0] } },
      foot_left: { rotation: { 0: [0, 0, 0], 0.3: [0, 0, 0], 0.48: [14, 0, 0], 0.7: [0, 0, 0] } },
      tail: { rotation: { 0: [0, 0, 0], 0.3: [-20, 0, 0], 0.6: [15, 0, 0], 1.0: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ special: psychic power, the swirl spins up while it holds its head
  const JITTER = 'math.sin(q.anim_time*2400)*0.25';
  m.anim('special', {
    length: 1.85,
    bones: {
      ...armTracks([[0, REST], [0.3, HOLD_HEAD], [1.15, HOLD_HEAD], [1.35, THRUST], [1.55, THRUST], [1.85, REST]]),
      swirl: {
        rotation: { 0: [0, 0, 0], 0.2: [0, 0, 0], 1.2: [0, 0, -1080], 1.85: [0, 0, -1440] },
        scale: { 0: [1, 1, 1], 0.3: [1.35, 1.35, 1.35], 1.15: [1.35, 1.35, 1.35], 1.3: [1.5, 1.5, 1.5], 1.5: [1, 1, 1] },
      },
      torso: {
        position: { 0: [0, 0, 0], 0.3: [JITTER, 0, 0], 1.15: [JITTER, 0, 0], 1.2: [0, 0, 0] },
        rotation: { 0: cr([0, 0, 0]), 0.3: cr([4, 0, 0]), 1.15: cr([4, 0, 0]), 1.35: cr([-8, 0, 0]), 1.85: cr([0, 0, 0]) },
      },
      head: { rotation: { 0: cr([0, 0, 0]), 0.3: cr([6, 0, 0]), 1.15: cr([6, 0, 0]), 1.35: cr([-6, 0, 0]), 1.85: cr([0, 0, 0]) } },
      eyes_closed: { position: shown(0.25, 1.15) },
      jaw: { rotation: { 0: [0, 0, 0], 1.2: [0, 0, 0], 1.35: [-28, 0, 0], 1.6: [-28, 0, 0], 1.8: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: { position: { 0: cr([0, 0, 0]), 0.1: cr([0, 0.6, 2.2]), 0.3: cr([0, 0, 1.2]), 0.6: cr([0, 0, 0]) } },
      torso: { rotation: { 0: [0, 0, 0], 0.1: [12, 0, 0], 0.35: [2, 0, 0], 0.6: [0, 0, 0] } },
      head: { rotation: { 0: [0, 0, 0], 0.1: [10, 0, 6], 0.35: [2, 0, 0], 0.6: [0, 0, 0] } },
      eyes_closed: { position: shown(0, 0.4) },
      arm_right: { rotation: { 0: [0, 0, 0], 0.1: [45, -40, -20], 0.5: [0, 0, 0] } },
      arm_left: { rotation: mirrorKeys({ 0: [0, 0, 0], 0.1: [45, -40, -20], 0.5: [0, 0, 0] }) },
    },
  });

  // ------------------------------------------------------------ faint: dizzy X eyes, wobbles, then topples onto its back (heavy head)
  // body lift per fall angle keeps the lowest point on the ground (measured with groundcheck.js)
  // 3 s like Cobblemon's own faint animations; the fallen pose holds after 1.55 s
  m.anim('faint', {
    length: 3,
    bones: {
      eyes_dizzy: { position: { 0: [0, 0, 0], 0.05: [0, 0, SHOW] } },
      swirl: { rotation: { 0: [0, 0, 0], 1.3: [0, 0, -900] } },
      torso: { rotation: { 0: cr([0, 0, 0]), 0.25: cr([0, 0, 10]), 0.5: cr([-2, 0, -10]), 0.75: cr([-2, 0, 8]), 0.95: cr([0, 0, 0]), 1.2: cr([0, 0, 0]) } },
      body: {
        rotation: { 0: [0, 0, 0], 0.8: [0, 0, 0], 0.95: [-3, 0, 0], 1.15: [40, 0, 0], 1.3: [76, 0, 0], 1.42: [64, 0, 0], 1.55: [72, 0, 0] },
        position: { 0: [0, 0, 0], 0.8: [0, 0, 0], 0.95: [0, 0.3, -0.3], 1.15: [0, 0.25, 1.2], 1.3: [0, 2.4, 2.2], 1.42: [0, 1.9, 2.2], 1.55: [0, 1.57, 2.2] },
      },
      head: { rotation: { 0: cr([0, 0, 0]), 0.25: cr([0, 0, -6]), 0.5: cr([0, 0, 6]), 0.75: cr([0, 0, -5]), 0.95: cr([0, 0, 0]), 1.9: cr([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 1.2: [0, 0, 0], 1.4: [-18, 0, 0] } },
      arm_right: { rotation: { 0: [0, 0, 0], 0.95: [10, -20, 0], 1.3: [60, -40, -40], 1.6: [50, -40, -35] } },
      arm_left: { rotation: mirrorKeys({ 0: [0, 0, 0], 0.95: [10, -20, 0], 1.3: [60, -40, -40], 1.6: [50, -40, -35] }) },
      foot_right: { rotation: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.35: [-30, 0, 10], 1.6: [-20, 0, 8] } },
      foot_left: { rotation: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.35: [-30, 0, -10], 1.6: [-20, 0, -8] } },
      tail: { rotation: { 0: [0, 0, 0], 1.0: [0, 0, 0], 1.3: [-60, 0, 0] } },
    },
  });
};
