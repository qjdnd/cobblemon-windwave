// Animations for baby Meowth. Values are Blockbench-space (what Blockbench shows):
// rot +x = nose up, +y = turn to its left, +z = roll toward its left.
// pos +x = its right, +y = up, +z = backwards.
'use strict';
const S = (amp, speed, phase = 0, off = 0) => {
  if (!amp) return off;
  const core = `math.sin(q.anim_time*${speed}${phase ? (phase > 0 ? '+' + phase : phase) : ''})`;
  const a = amp === 1 ? core : `${amp}*${core}`;
  return off ? `${off}+${a}` : a;
};
// short twitch pulse: 1 when the slow wave peaks, 0 otherwise
const pulse = (amp, speed, phase = 0, sharp = 24) => `${amp}*math.pow(math.max(0, math.sin(q.anim_time*${speed}${phase ? '+' + phase : ''})), ${sharp})`;
const EYES_OPEN = -0.45; // z offset that brings the open-eye planes in front of the face
const MOUTH_OPEN = -0.45;
const CRY = 'pokemon.meowth.cry';

module.exports = (m) => {
  const coinBob = (speed, amp, spin) => ({
    coin_left: { position: [0, S(amp, speed, 0), 0], rotation: [0, `q.anim_time*${spin}`, S(4, speed, 40)] },
    coin_middle: { position: [0, S(amp, speed, 120), 0], rotation: [0, `q.anim_time*${spin}+60`, S(4, speed, 160)] },
    coin_right: { position: [0, S(amp, speed, 240), 0], rotation: [0, `q.anim_time*${spin}+120`, S(4, speed, 280)] },
  });

  // ------------------------------------------------------------ ground idle
  m.anim('ground_idle', {
    loop: true,
    bones: {
      body: { scale: [S(0.012, 144, 0, 1), S(0.025, 144, 0, 1), S(0.012, 144, 0, 1)] },
      head: { rotation: [S(1.5, 144, -40), S(3, 60), S(2.5, 72, 30)], position: [0, S(0.12, 144, -40), 0] },
      ear_right: { rotation: [pulse(-10, 90, 0), 0, pulse(-14, 90, 0)] },
      ear_left: { rotation: [pulse(-10, 90, 200), 0, pulse(14, 90, 200)] },
      tail: { rotation: [S(3, 100, 0), S(10, 100, 0), S(4, 100, -30)] },
      tail2: { rotation: [S(6, 100, -60), S(8, 100, -60), 0] },
      tail3: { rotation: [S(10, 100, -110), S(8, 100, -120), S(5, 100, -120)] },
      arm_right: { rotation: [`-4*math.max(0, math.sin(q.anim_time*120))`, 0, 0] },
      arm_left: { rotation: [`-4*math.max(0, math.sin(q.anim_time*120+180))`, 0, 0] },
      coins: { rotation: [0, S(8, 45), 0], position: [0, S(0.3, 72), 0] },
      coin_forehead: { rotation: [0, 0, S(3, 144, 90)] },
      ...coinBob(120, 0.6, 90),
    },
  });

  // ------------------------------------------------------------ walk (little waddle)
  const W = 540; // deg/s -> 0.667s stride
  m.anim('ground_walk', {
    loop: true,
    bones: {
      body: { rotation: [S(1.5, W * 2, 90), S(2, W), S(3.5, W)], position: [0, `0.45*math.abs(math.sin(q.anim_time*${W}))`, 0] },
      head: { rotation: [S(2.5, W * 2, 40, 2), S(-3, W, 20), S(-2.5, W, 20)] },
      arm_right: { rotation: [`18*math.max(0, math.sin(q.anim_time*${W}))`, 0, 0], position: [0, `0.6*math.max(0, math.sin(q.anim_time*${W}))`, S(-0.9, W, 90)] },
      arm_left: { rotation: [`18*math.max(0, math.sin(q.anim_time*${W}+180))`, 0, 0], position: [0, `0.6*math.max(0, math.sin(q.anim_time*${W}+180))`, S(-0.9, W, 270)] },
      leg_right: { position: [0, `0.4*math.max(0, math.sin(q.anim_time*${W}+180))`, S(-0.8, W, 270)] },
      leg_left: { position: [0, `0.4*math.max(0, math.sin(q.anim_time*${W}))`, S(-0.8, W, 90)] },
      ear_right: { rotation: [S(-4, W * 2, 60), 0, S(-3, W, 60)] },
      ear_left: { rotation: [S(-4, W * 2, 60), 0, S(-3, W, 60)] },
      tail: { rotation: [S(-6, W * 2, 0, -6), S(16, W, -20), 0] },
      tail2: { rotation: [S(6, W * 2, -40), S(12, W, -70), 0] },
      tail3: { rotation: [S(8, W * 2, -80), S(14, W, -120), 0] },
      coins: { position: [0, S(0.5, W * 2, -90), 0.6], rotation: [S(3, W * 2, -90), 0, S(3, W, -60)] },
      eyes: { position: [0, 0, EYES_OPEN] },
      ...coinBob(W / 2, 0.7, 140),
    },
  });

  // ------------------------------------------------------------ battle idle (alert, coins circling)
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { rotation: [-2, 0, 0], scale: [S(0.015, 240, 0, 1), S(0.03, 240, 0, 1), S(0.015, 240, 0, 1)] },
      head: { rotation: [S(1.5, 240, -40, 5), S(4, 80), S(2, 120)], position: [0, S(0.1, 240, -40, 0.4), 0] },
      ear_right: { rotation: [S(3, 240, 0, 8), 0, pulse(-12, 120, 0)] },
      ear_left: { rotation: [S(3, 240, 0, 8), 0, pulse(12, 120, 150)] },
      tail: { rotation: [-18, S(14, 160), S(4, 160, -30)] },
      tail2: { rotation: [S(8, 160, -60, -8), S(10, 160, -60), 0] },
      tail3: { rotation: [S(10, 160, -110, 4), S(10, 160, -120), 0] },
      arm_right: { rotation: [S(3, 240, 0, 4), 0, 0], position: [0, 0, -0.4] },
      arm_left: { rotation: [S(3, 240, 180, 4), 0, 0], position: [0, 0, -0.4] },
      coins: { rotation: [0, 'q.anim_time*60', 0], position: [0, S(0.5, 120, 0, 1), 0] },
      coin_forehead: { rotation: [0, 0, S(4, 240, 90)] },
      eyes: { position: [0, 0, EYES_OPEN] },
      ...coinBob(200, 0.7, 200),
    },
  });

  // ------------------------------------------------------------ sleep (curled loaf, coins drift low)
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { scale: [S(0.015, 90, 0, 1.02), S(0.035, 90, 0, 0.94), S(0.015, 90, 0, 1.02)] },
      head: { rotation: [S(1.2, 90, -60, -7), 6, 8], position: [0, S(0.12, 90, -60, -1.1), 0] },
      ear_right: { rotation: [-12, 0, -18] },
      ear_left: { rotation: [-12, 0, 18] },
      tail: { rotation: [36, 70, 0], position: [0, -1.4, 0] },
      tail2: { rotation: [50, 58, 0] },
      tail3: { rotation: [55, S(3, 90, -60, 48), 0] },
      tail4: { rotation: [65, S(6, 90, -120, 38), 0] },
      arm_right: { rotation: [0, -8, 0], position: [0.5, 0, 0.5] },
      arm_left: { rotation: [0, 8, 0], position: [-0.5, 0, 0.5] },
      coins: { position: [0, S(0.4, 60, 0, -3.5), 1], rotation: [0, 'q.anim_time*20', 0] },
      ...coinBob(60, 0.4, 25),
    },
  });

  // ------------------------------------------------------------ blink (quirk; only visible while eyes are open)
  m.anim('blink', {
    length: 0.1667,
    bones: {
      eyes: { position: { 0: [0, 0, 0], 0.0417: [0, 0, 0.45], 0.125: [0, 0, 0.45], 0.1667: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ look quirk: opens its eyes and peeks around
  m.anim('look_quirk', {
    length: 3.5,
    bones: {
      eyes: { position: { 0: [0, 0, 0], 0.25: [0, 0, 0], 0.2917: [0, 0, EYES_OPEN], 3.0: [0, 0, EYES_OPEN], 3.0417: [0, 0, 0] } },
      head: {
        rotation: {
          0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.5: { v: [4, 0, 0], lerp: 'catmullrom' }, 1.0: { v: [3, 22, 6], lerp: 'catmullrom' },
          1.6: { v: [3, 22, 6], lerp: 'catmullrom' }, 2.1: { v: [3, -20, -6], lerp: 'catmullrom' }, 2.7: { v: [3, -20, -6], lerp: 'catmullrom' },
          3.2: { v: [0, 0, 0], lerp: 'catmullrom' }, 3.5: { v: [0, 0, 0], lerp: 'catmullrom' },
        },
      },
      ear_right: { rotation: { 0: [0, 0, 0], 0.3: [6, 0, 6], 1.0: [4, 10, 2], 2.1: [4, -6, 8], 3.2: [0, 0, 0] } },
      ear_left: { rotation: { 0: [0, 0, 0], 0.3: [6, 0, -6], 1.0: [4, 6, -8], 2.1: [4, -10, -2], 3.2: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ cry: nose up, happy mew, coins jump
  m.anim('cry', {
    length: 1.25,
    sounds: { 0.0833: CRY },
    bones: {
      head: {
        rotation: {
          0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.1667: { v: [-4, 0, 0], lerp: 'catmullrom' }, 0.375: { v: [14, 0, -4], lerp: 'catmullrom' },
          0.7: { v: [12, 0, 5], lerp: 'catmullrom' }, 1.0: { v: [2, 0, 0], lerp: 'catmullrom' }, 1.25: { v: [0, 0, 0], lerp: 'catmullrom' },
        },
      },
      body: { scale: { 0: [1, 1, 1], 0.1667: [1.03, 0.94, 1.03], 0.375: [0.98, 1.05, 0.98], 0.7: [1, 1.02, 1], 1.0: [1, 1, 1] } },
      mouth: { position: { 0: [0, 0, 0], 0.125: [0, 0, 0], 0.1667: [0, 0, MOUTH_OPEN], 0.875: [0, 0, MOUTH_OPEN], 0.9167: [0, 0, 0] } },
      ear_right: { rotation: { 0: [0, 0, 0], 0.2: [-8, 0, -6], 0.375: [10, 0, 8], 0.9: [6, 0, 4], 1.2: [0, 0, 0] } },
      ear_left: { rotation: { 0: [0, 0, 0], 0.2: [-8, 0, 6], 0.375: [10, 0, -8], 0.9: [6, 0, -4], 1.2: [0, 0, 0] } },
      tail: { rotation: { 0: [0, 0, 0], 0.25: [-15, 20, 0], 0.5: [-15, -20, 0], 0.75: [-15, 20, 0], 1.0: [-8, -8, 0], 1.25: [0, 0, 0] } },
      coins: {
        position: {
          0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.2: { v: [0, -0.8, 0], lerp: 'catmullrom' }, 0.45: { v: [0, 3.2, 0], lerp: 'catmullrom' },
          0.8: { v: [0, 0.6, 0], lerp: 'catmullrom' }, 1.0: { v: [0, 1, 0], lerp: 'catmullrom' }, 1.25: { v: [0, 0, 0], lerp: 'catmullrom' },
        },
        rotation: { 0: [0, 0, 0], 0.3: [0, 0, 0], 1.0: [0, 360, 0], 1.25: [0, 360, 0] },
      },
      coin_left: { rotation: { 0: [0, 0, 0], 0.35: [0, 0, 0], 0.9: [0, 360, 0] } },
      coin_middle: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 0.95: [0, -360, 0] } },
      coin_right: { rotation: { 0: [0, 0, 0], 0.45: [0, 0, 0], 1.0: [0, 360, 0] } },
    },
  });

  // ------------------------------------------------------------ physical: wind up and pounce with a paw swipe
  m.anim('physical', {
    length: 1.5,
    bones: {
      body: {
        position: {
          0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.3: { v: [0, -0.4, 1.4], lerp: 'catmullrom' }, 0.55: { v: [0, 2.2, -3.5], lerp: 'catmullrom' },
          0.75: { v: [0, 0, -4.5], lerp: 'catmullrom' }, 1.1: { v: [0, 0, -1], lerp: 'catmullrom' }, 1.5: { v: [0, 0, 0], lerp: 'catmullrom' },
        },
        rotation: { 0: [0, 0, 0], 0.3: [4, 0, 0], 0.55: [-8, 0, 0], 0.75: [3, 0, 0], 1.1: [0, 0, 0] },
        scale: { 0: [1, 1, 1], 0.3: [1.05, 0.9, 1.05], 0.55: [0.96, 1.06, 0.96], 0.75: [1.04, 0.95, 1.04], 1.0: [1, 1, 1] },
      },
      head: { rotation: { 0: [0, 0, 0], 0.3: [-6, 0, 0], 0.55: [8, 0, 0], 0.8: [-2, 0, 0], 1.2: [0, 0, 0] } },
      arm_right: {
        rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 0.55: [40, -20, 0], 0.7: [-10, 25, 0], 0.9: [0, 0, 0] },
        position: { 0: [0, 0, 0], 0.4: [0, 0, 0], 0.55: [0, 2, -1], 0.7: [-1.5, 0.2, -1.5], 0.95: [0, 0, 0] },
      },
      ear_right: { rotation: { 0: [0, 0, 0], 0.3: [-12, 0, -10], 0.75: [-6, 0, -6], 1.2: [0, 0, 0] } },
      ear_left: { rotation: { 0: [0, 0, 0], 0.3: [-12, 0, 10], 0.75: [-6, 0, 6], 1.2: [0, 0, 0] } },
      tail: { rotation: { 0: [0, 0, 0], 0.3: [-25, 0, 0], 0.6: [10, 0, 0], 1.0: [0, 0, 0] } },
      coins: { position: { 0: [0, 0, 0], 0.55: [0, 0.5, 2.5], 0.8: [0, 0, -1.5], 1.2: [0, 0, 0] } },
      eyes: { position: [0, 0, EYES_OPEN] },
    },
  });

  // ------------------------------------------------------------ special: coins whirl around it (Pay Day style)
  m.anim('special', {
    length: 1.75,
    bones: {
      head: { rotation: { 0: [0, 0, 0], 0.3: [10, 0, 0], 1.3: [10, 0, 0], 1.75: [0, 0, 0] } },
      coins: {
        rotation: { 0: [0, 0, 0], 0.2: [0, 0, 0], 1.4: [0, 720, 0], 1.75: [0, 720, 0] },
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.3: { v: [0, 2.5, 0], lerp: 'catmullrom' }, 1.2: { v: [0, 3, 0], lerp: 'catmullrom' }, 1.75: { v: [0, 0, 0], lerp: 'catmullrom' } },
        scale: { 0: [1, 1, 1], 0.3: [1.25, 1.25, 1.25], 1.3: [1.25, 1.25, 1.25], 1.75: [1, 1, 1] },
      },
      coin_forehead: { scale: { 0: [1, 1, 1], 0.25: [1.3, 1.3, 1.3], 0.4: [1, 1, 1], 1.1: [1, 1, 1], 1.25: [1.3, 1.3, 1.3], 1.45: [1, 1, 1] } },
      ...Object.fromEntries(['coin_left', 'coin_middle', 'coin_right'].map((n, i) => [n, { rotation: { 0: [0, 0, 0], 1.6: [0, (i % 2 ? -1 : 1) * 1080, 0] } }])),
      eyes: { position: { 0: [0, 0, 0], 0.2: [0, 0, EYES_OPEN], 1.5: [0, 0, EYES_OPEN], 1.55: [0, 0, 0] } },
      mouth: { position: { 0: [0, 0, 0], 0.25: [0, 0, MOUTH_OPEN], 0.6: [0, 0, MOUTH_OPEN], 0.65: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.1: { v: [0, 0.8, 2.2], lerp: 'catmullrom' }, 0.3: { v: [0, 0, 1.2], lerp: 'catmullrom' }, 0.6: { v: [0, 0, 0], lerp: 'catmullrom' } },
        scale: { 0: [1, 1, 1], 0.1: [0.94, 1.06, 0.94], 0.3: [1.04, 0.95, 1.04], 0.5: [1, 1, 1] },
      },
      head: { rotation: { 0: [0, 0, 0], 0.1: [12, 0, 6], 0.35: [2, 0, 0], 0.6: [0, 0, 0] } },
      ear_right: { rotation: { 0: [0, 0, 0], 0.1: [-20, 0, -18], 0.5: [0, 0, 0] } },
      ear_left: { rotation: { 0: [0, 0, 0], 0.1: [-20, 0, 18], 0.5: [0, 0, 0] } },
      coins: { position: { 0: [0, 0, 0], 0.15: [0, 1.5, 2], 0.6: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ faint: flops flat, coins drop to the ground
  m.anim('faint', {
    length: 1.5, hold: true,
    bones: {
      body: {
        scale: { 0: [1, 1, 1], 0.25: [0.97, 1.05, 0.97], 0.6: [1.08, 0.82, 1.08], 0.8: [1.05, 0.88, 1.05], 1.0: [1.07, 0.84, 1.07] },
        rotation: { 0: [0, 0, 0], 0.6: [0, 0, 6], 1.0: [0, 0, 5] },
      },
      head: { rotation: { 0: [0, 0, 0], 0.25: [8, 0, 0], 0.7: [-10, 0, 10], 1.0: [-9, 0, 9] }, position: { 0: [0, 0, 0], 0.7: [0, -1.2, 0] } },
      ear_right: { rotation: { 0: [0, 0, 0], 0.7: [-20, 0, -30], 0.9: [-16, 0, -26] } },
      ear_left: { rotation: { 0: [0, 0, 0], 0.7: [-20, 0, 30], 0.9: [-16, 0, 26] } },
      tail: { rotation: { 0: [0, 0, 0], 0.6: [20, 30, 0] } },
      tail2: { rotation: { 0: [0, 0, 0], 0.6: [-60, 0, 0] } },
      tail3: { rotation: { 0: [0, 0, 0], 0.6: [-40, 0, 0] } },
      coins: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.2: { v: [0, 1, 0], lerp: 'catmullrom' }, 0.7: { v: [0, -16.5, -2], lerp: 'catmullrom' }, 0.85: { v: [0, -15.5, -2.3], lerp: 'catmullrom' }, 1.0: { v: [0, -16.5, -2.5], lerp: 'catmullrom' } },
        scale: { 0: [1, 1, 1], 0.6: [1, 1, 1], 0.75: [1.3, 1.3, 1.3] },
      },
      coin_left: { rotation: { 0: [0, 0, 0], 0.7: [90, 25, 0] }, position: { 0: [0, 0, 0], 0.7: [-2.5, 2, -1] } },
      coin_middle: { rotation: { 0: [0, 0, 0], 0.75: [90, -40, 0] }, position: { 0: [0, 0, 0], 0.75: [0, -0.5, -3] } },
      coin_right: { rotation: { 0: [0, 0, 0], 0.8: [90, 60, 0] }, position: { 0: [0, 0, 0], 0.8: [2.5, 2, 0] } },
    },
  });
};
