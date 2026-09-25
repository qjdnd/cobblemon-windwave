// Animations for Frillgator. Values are Blockbench-space (what Blockbench shows):
// rot +x = nose up / claws forward, +y = turn to its left, +z = roll toward its left.
// pos +x = its right, +y = up, +z = backwards.
// Rest pose: the jaw hangs 20 deg open and the eyelid shells are folded 150 deg
// down behind the eyes, so eyelid x -240 closes an eye and jaw x +20 shuts the mouth.
'use strict';
const S = (amp, speed, phase = 0, off = 0) => {
  if (!amp) return off;
  const ph = phase ? (phase > 0 ? `+${phase}` : `${phase}`) : '';
  const core = `math.sin(q.anim_time*${speed}${ph})`;
  const a = Math.abs(amp) === 1 ? core : `${Math.abs(amp)}*${core}`;
  if (!off) return amp < 0 ? `-${a}` : a;
  return `${off}${amp < 0 ? '-' : '+'}${a}`;
};
const lift = (amp, speed, phase = 0) => `${amp}*math.max(0, math.sin(q.anim_time*${speed}${phase ? '+' + phase : ''}))`;
const px = (expr) => `math.round(${expr})`; // pupils move in whole texels
const CRY = 'pokemon.croconaw.cry';
const CLOSED = -240;
const SQUINT = -195;

// right-side spec -> the mirrored left-side spec (rotation y/z and position x flip sign)
const flip = (v) => (typeof v === 'number' ? (v === 0 ? 0 : -v) : `-(${v})`);
function mirrorChan(ch, spec) {
  const f = (arr) => (ch === 'rotation' ? [arr[0], flip(arr[1]), flip(arr[2])] : ch === 'position' ? [flip(arr[0]), arr[1], arr[2]] : arr);
  if (Array.isArray(spec)) return f(spec);
  return Object.fromEntries(Object.entries(spec).map(([t, v]) => [t, Array.isArray(v) ? f(v) : { ...v, v: f(v.v) }]));
}
// both(bone, spec): right bone gets spec, left bone gets the mirror image ('%' marks where the side goes)
function both(name, spec) {
  const left = {};
  for (const [ch, v] of Object.entries(spec)) left[ch] = mirrorChan(ch, v);
  const nm = (side) => (name.includes('%') ? name.replace('%', side) : `${name}_${side}`);
  return { [nm('right')]: spec, [nm('left')]: left };
}
const cm = (v) => ({ v, lerp: 'catmullrom' });

module.exports = (m) => {
  // ------------------------------------------------------------ ground idle
  const I = 120, SW = 60, SL = 45;
  const tailSway = (speed, amp, lag = 40, lift0 = 0) => ({
    tail: { rotation: [0, S(amp * 0.5, speed, 0), 0] },
    tail2: { rotation: [0, S(amp * 0.6, speed, -lag), 0] },
    tail3: { rotation: [0, S(amp * 0.75, speed, -2 * lag), 0] },
    tail4: { rotation: [S(lift0 * 0.5, speed, -3 * lag), S(amp * 0.85, speed, -3 * lag), 0] },
    tail5: { rotation: [S(lift0, speed, -4 * lag), S(amp, speed, -4 * lag), 0] },
  });
  m.anim('ground_idle', {
    loop: true,
    bones: {
      body: { rotation: [0, 0, S(1, SL)], scale: [S(0.012, I, 0, 1), S(0.022, I, 0, 1), S(0.012, I, 0, 1)] },
      head: { rotation: [S(2, I, -60), S(4, SL), S(2.5, SW, 40)] },
      jaw: { rotation: [S(3, I, -100, 1), 0, 0] },
      eye_right: { rotation: [S(2, I, -150), 0, S(2.5, SW, -60)] },
      eye_left: { rotation: [S(2, I, -170), 0, S(2.5, SW, -80)] },
      pupil_right: { position: [px(S(0.9, 36)), px(S(0.7, 24, 90)), 0] },
      pupil_left: { position: [px(S(0.9, 36, -10)), px(S(0.7, 24, 80)), 0] },
      frill_right: { rotation: [S(2, I, -120), S(3, SW), S(3, I, -120)] },
      frill_left: { rotation: [S(2, I, -120), S(3, SW), S(-3, I, -120)] },
      frill_right_back: { rotation: [S(2, I, -150), S(3, SW, -40), S(4, I, -150)] },
      frill_left_back: { rotation: [S(2, I, -150), S(3, SW, -40), S(-4, I, -150)] },
      ...both('arm', { rotation: [S(2, I, -40), 0, S(1.5, I, -40)] }),
      ...both('hand', { rotation: [S(4, I, -80), 0, 0] }),
      ...tailSway(SW, 9, 40, 5),
    },
  });

  // ------------------------------------------------------------ walk: a squat, splay-legged waddle
  const W = 400; // deg/s -> 0.9 s per stride
  const walkBones = {
    body: { rotation: [S(2, W * 2, 90), S(5, W), S(4, W)], position: [0, `0.5*math.abs(math.sin(q.anim_time*${W}))`, 0] },
    head: { rotation: [S(3, W * 2, 40, 2), S(-4, W, 30), S(-3, W, 30)] },
    jaw: { rotation: [S(5, W * 2, 0, 2), 0, 0] },
    leg_right: { rotation: [S(8, W, 0), 0, 0], position: [0, lift(1.4, W), S(1.5, W, 90)] },
    leg_left: { rotation: [S(8, W, 180), 0, 0], position: [0, lift(1.4, W, 180), S(1.5, W, 270)] },
    foot_right: { rotation: [lift(12, W), 0, 0] },
    foot_left: { rotation: [lift(12, W, 180), 0, 0] },
    arm_right: { rotation: [S(10, W, 90), 0, 0] },
    arm_left: { rotation: [S(10, W, 270), 0, 0] },
    hand_right: { rotation: [S(12, W, 180), 0, 0] },
    hand_left: { rotation: [S(12, W, 0), 0, 0] },
    eye_right: { rotation: [S(4, W * 2, -60), 0, S(4, W, -40)] },
    eye_left: { rotation: [S(4, W * 2, -80), 0, S(4, W, -60)] },
    pupil_right: { position: [px(S(1.2, W, -40)), px(S(1.2, W * 2, -90)), 0] },
    pupil_left: { position: [px(S(1.2, W, -70)), px(S(1.2, W * 2, -120)), 0] },
    frill_right: { rotation: [S(4, W * 2, -60), S(5, W, -30), S(6, W * 2, -60)] },
    frill_left: { rotation: [S(4, W * 2, -60), S(5, W, -30), S(-6, W * 2, -60)] },
    frill_right_back: { rotation: [S(4, W * 2, -100), S(5, W, -70), S(6, W * 2, -100)] },
    frill_left_back: { rotation: [S(4, W * 2, -100), S(5, W, -70), S(-6, W * 2, -100)] },
    tail: { rotation: [0, S(10, W, -60), 0] },
    tail2: { rotation: [0, S(10, W, -100), 0] },
    tail3: { rotation: [0, S(12, W, -140), 0] },
    tail4: { rotation: [0, S(12, W, -180), 0] },
    tail5: { rotation: [S(6, W * 2, -200), S(14, W, -220), 0] },
  };
  m.anim('ground_walk', { loop: true, bones: walkBones });

  // ------------------------------------------------------------ water: floats upright paddling / swims leaning forward
  m.anim('water_idle', {
    loop: true,
    bones: {
      body: { rotation: [S(3, 90, 0, -6), 0, S(2, SW)], position: [0, S(0.4, 90, -60), 0] },
      head: { rotation: [S(2, 90, -60, 6), S(4, SL), 0] },
      jaw: { rotation: [S(3, 90, -100, 6), 0, 0] },
      leg_right: { rotation: [S(12, 180), 0, 0], position: [0, 0, S(1, 180, 90)] },
      leg_left: { rotation: [S(12, 180, 180), 0, 0], position: [0, 0, S(1, 180, 270)] },
      ...both('arm', { rotation: [S(8, 180, 90, 10), 0, 0] }),
      ...both('hand', { rotation: [S(10, 180, 0, 10), 0, 0] }),
      frill_right: { rotation: [S(2, 90, -90), S(3, SW), S(3, 90, -90, 8)] },
      frill_left: { rotation: [S(2, 90, -90), S(3, SW), S(-3, 90, -90, -8)] },
      frill_right_back: { rotation: [0, S(3, SW, -40), S(4, 90, -120, 8)] },
      frill_left_back: { rotation: [0, S(3, SW, -40), S(-4, 90, -120, -8)] },
      pupil_right: { position: [px(S(0.9, 36)), 0, 0] },
      pupil_left: { position: [px(S(0.9, 36, -10)), 0, 0] },
      ...tailSway(90, 16, 45, 4),
    },
  });
  const SWIM = 300;
  m.anim('water_swim', {
    loop: true,
    bones: {
      body: { rotation: [-28, S(4, SWIM), S(3, SWIM)], position: [0, S(0.4, SWIM * 2), 0] },
      head: { rotation: [S(3, SWIM * 2, -40, 24), S(-4, SWIM, -30), 0] },
      jaw: { rotation: [S(4, SWIM * 2, -40, 8), 0, 0] },
      leg_right: { rotation: [S(22, SWIM, 0, -20), 0, 0] },
      leg_left: { rotation: [S(22, SWIM, 180, -20), 0, 0] },
      foot_right: { rotation: [S(20, SWIM, -60), 0, 0] },
      foot_left: { rotation: [S(20, SWIM, 120), 0, 0] },
      ...both('arm', { rotation: [-24, 0, 0], position: [0, 0, 1.5] }),
      ...both('hand', { rotation: [-30, 0, 0] }),
      frill_right: { rotation: [-8, S(4, SWIM * 2, -60, 14), -6] },
      frill_left: { rotation: [-8, S(-4, SWIM * 2, -60, -14), 6] },
      frill_right_back: { rotation: [-8, S(4, SWIM * 2, -100, 10), -6] },
      frill_left_back: { rotation: [-8, S(-4, SWIM * 2, -100, -10), 6] },
      tail: { rotation: [24, S(10, SWIM, -60, 20), 0] },
      tail2: { rotation: [0, S(14, SWIM, -110, 22), 0] },
      tail3: { rotation: [0, S(16, SWIM, -160, 24), 0] },
      tail4: { rotation: [0, S(18, SWIM, -210, 24), 0] },
      tail5: { rotation: [-10, S(20, SWIM, -260, 20), 0] },
    },
  });

  // ------------------------------------------------------------ battle idle: crouched, frills flared, jaw snapping
  const B = 240;
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { rotation: [-3, 0, 0], position: [0, -0.6, 0], scale: [S(0.015, B, 0, 1), S(0.03, B, 0, 1), S(0.015, B, 0, 1)] },
      head: { rotation: [S(2, B, -50, 5), S(4, 80), 0] },
      jaw: { rotation: [S(5, B, -90, -9), 0, 0] },
      frill_right: { rotation: [S(3, B, -60, -4), S(4, B, -60, 18), S(4, B, -90, 12)] },
      frill_left: { rotation: [S(3, B, -60, -4), S(-4, B, -60, -18), S(-4, B, -90, -12)] },
      frill_right_back: { rotation: [S(3, B, -90, -2), S(4, B, -90, 20), S(5, B, -120, 10)] },
      frill_left_back: { rotation: [S(3, B, -90, -2), S(-4, B, -90, -20), S(-5, B, -120, -10)] },
      ...both('arm', { rotation: [S(4, B, 0, 20), 0, 0] }),
      ...both('hand', { rotation: [S(8, B, -60, 25), 0, 0] }),
      eye_right: { rotation: [S(2, B, -80), 0, 0] },
      eye_left: { rotation: [S(2, B, -100), 0, 0] },
      pupil_right: { position: [px(S(0.6, 90)), 0, 0] },
      pupil_left: { position: [px(S(0.6, 90, -20)), 0, 0] },
      tail: { rotation: [S(3, B), S(6, 120), 0] },
      tail2: { rotation: [0, S(10, 120, -40), 0] },
      tail3: { rotation: [0, S(12, 120, -80), 0] },
      tail4: { rotation: [S(6, B, -100), S(14, 120, -120), 0] },
      tail5: { rotation: [S(10, B, -140), S(16, 120, -160), 0] },
    },
  });

  // ------------------------------------------------------------ sleep: head drooped onto its chest, eyes shut
  const Z = 72;
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { rotation: [-6, 0, 0], position: [0, -0.6, 0], scale: [S(0.012, Z, 0, 1.01), S(0.03, Z, 0, 0.97), S(0.012, Z, 0, 1.01)] },
      head: { rotation: [S(1.5, Z, -60, -20), 6, 10], position: [0, -1, -0.5] },
      jaw: { rotation: [S(2, Z, -60, 18), 0, 0] },
      eyelid_right: { rotation: [CLOSED, 0, 0] },
      eyelid_left: { rotation: [CLOSED, 0, 0] },
      eye_right: { rotation: [-4, 0, -4] },
      eye_left: { rotation: [-4, 0, 4] },
      ...both('frill', { rotation: [10, 12, S(2, Z, -90, -16)] }),
      frill_right_back: { rotation: [8, 10, -12] },
      frill_left_back: { rotation: [8, -10, 12] },
      ...both('arm', { rotation: [-12, 0, 0] }),
      ...both('hand', { rotation: [10, 0, 0] }),
      tail2: { rotation: [0, -10, 0] },
      tail3: { rotation: [0, -14, 0] },
      tail4: { rotation: [0, -16, 0] },
      tail5: { rotation: [-8, S(4, Z), 0] },
    },
  });

  // ------------------------------------------------------------ blink (quirk): the lid sweeps over the top of each eye
  const lidBlink = { 0: [0, 0, 0], 0.0833: [CLOSED, 0, 0], 0.1667: [CLOSED, 0, 0], 0.25: [0, 0, 0] };
  m.anim('blink', { length: 0.25, bones: { eyelid_right: { rotation: lidBlink }, eyelid_left: { rotation: lidBlink } } });

  // ------------------------------------------------------------ look quirk: googly eyes roll round, go cross-eyed, blink it off
  m.anim('look_quirk', {
    length: 3,
    bones: {
      pupil_right: {
        position: {
          0: [0, 0, 0], 0.2: [0, 2, 0], 0.4: [2, 0, 0], 0.6: [0, -2, 0], 0.8: [-2, 0, 0], 1.0: [0, 2, 0], 1.2: [0, 0, 0],
          1.45: [-2, 0, 0], 2.3: [-2, 0, 0], 2.4: [0, 0, 0],
        },
      },
      pupil_left: {
        position: {
          0: [0, 0, 0], 0.2: [0, 2, 0], 0.4: [-2, 0, 0], 0.6: [0, -2, 0], 0.8: [2, 0, 0], 1.0: [0, 2, 0], 1.2: [0, 0, 0],
          1.45: [2, 0, 0], 2.3: [2, 0, 0], 2.4: [0, 0, 0],
        },
      },
      head: { rotation: { 0: cm([0, 0, 0]), 0.3: cm([4, 0, 6]), 1.0: cm([4, 0, -6]), 1.45: cm([-3, 0, 0]), 2.3: cm([-3, 0, 2]), 2.7: cm([0, 0, 0]), 3.0: cm([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 1.3: [0, 0, 0], 1.5: [-9, 0, 0], 2.3: [-9, 0, 0], 2.5: [0, 0, 0] } },
      eye_right: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, -6], 0.8: [0, 0, 6], 1.2: [0, 0, 0], 2.3: [0, 0, 0], 2.45: [0, 0, 5], 2.7: [0, 0, 0] } },
      eye_left: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 6], 0.8: [0, 0, -6], 1.2: [0, 0, 0], 2.3: [0, 0, 0], 2.45: [0, 0, -5], 2.7: [0, 0, 0] } },
      eyelid_right: { rotation: { 0: [0, 0, 0], 2.3: [0, 0, 0], 2.38: [CLOSED, 0, 0], 2.46: [CLOSED, 0, 0], 2.54: [0, 0, 0] } },
      eyelid_left: { rotation: { 0: [0, 0, 0], 2.3: [0, 0, 0], 2.38: [CLOSED, 0, 0], 2.46: [CLOSED, 0, 0], 2.54: [0, 0, 0] } },
      ...both('frill', { rotation: { 0: [0, 0, 0], 1.45: [0, 0, 0], 1.6: [-3, 8, 8], 2.3: [-3, 8, 8], 2.6: [0, 0, 0] } }),
    },
  });

  // ------------------------------------------------------------ cry: head up, jaws wide, frills flare and shiver
  const flare = (a) => ({ 0: [0, 0, 0], 0.3: [-6, 20 * a, 16 * a], 0.5: [-4, 16 * a, 12 * a], 0.7: [-6, 20 * a, 16 * a], 0.9: [-4, 16 * a, 12 * a], 1.3: [0, 0, 0] });
  m.anim('cry', {
    length: 1.5,
    sounds: { 0.1: CRY },
    bones: {
      head: { rotation: { 0: cm([0, 0, 0]), 0.15: cm([-4, 0, 0]), 0.35: cm([16, 0, 0]), 0.9: cm([14, 0, 4]), 1.2: cm([3, 0, 0]), 1.5: cm([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.15: [8, 0, 0], 0.35: [-22, 0, 0], 0.95: [-20, 0, 0], 1.2: [-4, 0, 0], 1.5: [0, 0, 0] } },
      body: { scale: { 0: [1, 1, 1], 0.15: [1.03, 0.95, 1.03], 0.35: [0.98, 1.04, 0.98], 1.0: [1, 1.02, 1], 1.5: [1, 1, 1] } },
      ...both('frill', { rotation: flare(1) }),
      ...both('frill_%_back', { rotation: flare(0.7) }),
      ...both('arm', { rotation: { 0: [0, 0, 0], 0.35: [18, 0, 0], 1.0: [14, 0, 0], 1.5: [0, 0, 0] } }),
      ...both('hand', { rotation: { 0: [0, 0, 0], 0.35: [20, 0, 0], 1.0: [16, 0, 0], 1.5: [0, 0, 0] } }),
      tail: { rotation: { 0: [0, 0, 0], 0.3: [0, -10, 0], 0.55: [0, 10, 0], 0.8: [0, -10, 0], 1.05: [0, 6, 0], 1.4: [0, 0, 0] } },
      tail5: { rotation: { 0: [0, 0, 0], 0.35: [16, 0, 0], 1.0: [12, 0, 0], 1.5: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ physical: lunge and double chomp
  m.anim('physical', {
    length: 1.5,
    bones: {
      body: {
        position: { 0: cm([0, 0, 0]), 0.3: cm([0, -0.5, 1.5]), 0.55: cm([0, 1, -4]), 0.75: cm([0, 0, -4.5]), 1.1: cm([0, 0, -1]), 1.5: cm([0, 0, 0]) },
        rotation: { 0: [0, 0, 0], 0.3: [4, 0, 0], 0.55: [-10, 0, 0], 0.75: [-6, 0, 0], 1.1: [0, 0, 0] },
      },
      head: { rotation: { 0: [0, 0, 0], 0.3: [10, 0, 0], 0.55: [-6, 0, 0], 0.75: [-2, 0, 0], 1.1: [0, 0, 0] } },
      jaw: { rotation: { 0: [0, 0, 0], 0.3: [-25, 0, 0], 0.55: [-25, 0, 0], 0.62: [20, 0, 0], 0.8: [18, 0, 0], 0.9: [-10, 0, 0], 0.98: [20, 0, 0], 1.15: [18, 0, 0], 1.4: [0, 0, 0] } },
      ...both('frill', { rotation: { 0: [0, 0, 0], 0.3: [-4, 18, 14], 0.7: [-4, 18, 14], 0.8: [4, -6, -6], 1.2: [0, 0, 0] } }),
      ...both('frill_%_back', { rotation: { 0: [0, 0, 0], 0.3: [-4, 14, 10], 0.7: [-4, 14, 10], 0.85: [4, -8, -6], 1.25: [0, 0, 0] } }),
      ...both('arm', { rotation: { 0: [0, 0, 0], 0.3: [25, 0, 0], 0.6: [10, 0, 0], 1.2: [0, 0, 0] } }),
      ...both('hand', { rotation: { 0: [0, 0, 0], 0.3: [30, 0, 0], 0.6: [-10, 0, 0], 1.2: [0, 0, 0] } }),
      tail: { rotation: { 0: [0, 0, 0], 0.3: [10, 0, 0], 0.6: [-6, 0, 0], 1.0: [0, 0, 0] } },
      pupil_right: { position: { 0: [0, 0, 0], 0.25: [-1, 0, 0], 1.2: [-1, 0, 0], 1.3: [0, 0, 0] } },
      pupil_left: { position: { 0: [0, 0, 0], 0.25: [1, 0, 0], 1.2: [1, 0, 0], 1.3: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ special: frills fan out and rattle while it breathes out
  const rattle = (a) => {
    const o = { 0: [0, 0, 0], 0.4: [-6, 24 * a, 20 * a] };
    let k = 0;
    for (let t = 0.5; t < 1.36; t += 0.1) o[t.toFixed(2)] = k++ % 2 ? [-6, 24 * a, 20 * a] : [-4, 19 * a, 15 * a];
    o['1.75'] = [0, 0, 0];
    return o;
  };
  m.anim('special', {
    length: 1.75,
    bones: {
      body: {
        rotation: { 0: cm([0, 0, 0]), 0.3: cm([4, 0, 0]), 0.55: cm([-4, 0, 0]), 1.3: cm([-3, 0, 0]), 1.75: cm([0, 0, 0]) },
        scale: { 0: [1, 1, 1], 0.3: [1.04, 0.95, 1.04], 0.55: [0.98, 1.04, 0.98], 1.3: [1, 1.02, 1], 1.75: [1, 1, 1] },
      },
      head: { rotation: { 0: cm([0, 0, 0]), 0.3: cm([-6, 0, 0]), 0.55: cm([12, 0, 0]), 1.3: cm([12, 0, 0]), 1.75: cm([0, 0, 0]) } },
      jaw: { rotation: { 0: [0, 0, 0], 0.3: [6, 0, 0], 0.55: [-24, 0, 0], 1.3: [-22, 0, 0], 1.55: [0, 0, 0] } },
      ...both('frill', { rotation: rattle(1) }),
      ...both('frill_%_back', { rotation: rattle(0.8) }),
      ...both('arm', { rotation: { 0: [0, 0, 0], 0.4: [16, 0, 0], 1.3: [16, 0, 0], 1.75: [0, 0, 0] } }),
      ...both('hand', { rotation: { 0: [0, 0, 0], 0.4: [24, 0, 0], 1.3: [24, 0, 0], 1.75: [0, 0, 0] } }),
      tail5: { rotation: { 0: [0, 0, 0], 0.4: [18, 0, 0], 1.3: [18, 0, 0], 1.75: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: {
        position: { 0: cm([0, 0, 0]), 0.1: cm([0, 0.6, 2]), 0.3: cm([0, 0, 1]), 0.6: cm([0, 0, 0]) },
        rotation: { 0: [0, 0, 0], 0.1: [6, 0, 0], 0.4: [0, 0, 0] },
        scale: { 0: [1, 1, 1], 0.1: [0.95, 1.05, 0.95], 0.3: [1.03, 0.96, 1.03], 0.5: [1, 1, 1] },
      },
      head: { rotation: { 0: [0, 0, 0], 0.1: [14, 0, 6], 0.35: [3, 0, 0], 0.6: [0, 0, 0] } },
      jaw: { rotation: { 0: [0, 0, 0], 0.1: [-10, 0, 0], 0.4: [0, 0, 0] } },
      eyelid_right: { rotation: { 0: [0, 0, 0], 0.08: [SQUINT, 0, 0], 0.35: [SQUINT, 0, 0], 0.5: [0, 0, 0] } },
      eyelid_left: { rotation: { 0: [0, 0, 0], 0.08: [SQUINT, 0, 0], 0.35: [SQUINT, 0, 0], 0.5: [0, 0, 0] } },
      ...both('frill', { rotation: { 0: [0, 0, 0], 0.1: [10, -10, -10], 0.5: [0, 0, 0] } }),
      ...both('frill_%_back', { rotation: { 0: [0, 0, 0], 0.12: [10, -8, -8], 0.55: [0, 0, 0] } }),
    },
  });

  // ------------------------------------------------------------ faint: sways, then slumps forward onto its snout
  m.anim('faint', {
    length: 1.6, hold: true,
    bones: {
      body: {
        rotation: { 0: [0, 0, 0], 0.2: [4, 0, 0], 0.45: [-6, 0, 4], 0.8: [-28, 0, -3], 0.95: [-23, 0, -2], 1.1: [-26, 0, -2] },
        position: { 0: [0, 0, 0], 0.45: [0, 0.4, 0], 0.8: [0, 1.6, -1], 1.1: [0, 1.6, -1] },
        scale: { 0: [1, 1, 1], 0.8: [1, 1, 1], 0.9: [1.04, 0.95, 1.04], 1.1: [1, 1, 1] },
      },
      head: { rotation: { 0: [0, 0, 0], 0.2: [8, 0, 0], 0.45: [0, 0, -8], 0.8: [-36, 0, 6], 0.95: [-30, 0, 5], 1.1: [-34, 0, 6] } },
      jaw: { rotation: { 0: [0, 0, 0], 0.45: [-6, 0, 0], 0.8: [-10, 0, 0], 1.0: [-8, 0, 0] } },
      eyelid_right: { rotation: { 0: [0, 0, 0], 0.5: [0, 0, 0], 0.7: [CLOSED, 0, 0] } },
      eyelid_left: { rotation: { 0: [0, 0, 0], 0.55: [0, 0, 0], 0.75: [CLOSED, 0, 0] } },
      ...both('eye', { rotation: { 0: [0, 0, 0], 0.8: [-6, 0, -8], 0.95: [0, 0, 4], 1.1: [-3, 0, -4] } }),
      ...both('leg', { rotation: { 0: [0, 0, 0], 0.45: [6, 0, 0], 0.8: [28, 0, 0], 0.95: [23, 0, 0], 1.1: [26, 0, 0] } }),
      // the head ends up pitched ~60 deg nose-down: the frills flop open sideways instead of standing up
      ...both('frill', { rotation: { 0: [0, 0, 0], 0.45: [4, 6, 6], 0.8: [0, 30, -20], 1.0: [0, 26, -16], 1.2: [0, 28, -18] } }),
      ...both('frill_%_back', { rotation: { 0: [0, 0, 0], 0.5: [4, 6, 6], 0.85: [0, 24, -16], 1.2: [0, 22, -14] } }),
      ...both('arm', { rotation: { 0: [0, 0, 0], 0.45: [10, 0, 0], 0.8: [16, 0, -6], 1.1: [14, 0, -6] } }),
      ...both('hand', { rotation: { 0: [0, 0, 0], 0.8: [24, 0, 0], 1.1: [20, 0, 0] } }),
      tail: { rotation: { 0: [0, 0, 0], 0.45: [-8, 0, 0], 0.8: [36, 0, 0], 0.95: [30, 0, 0], 1.1: [34, 0, 0] } },
      tail5: { rotation: { 0: [0, 0, 0], 0.8: [-10, 0, 0] } },
    },
  });
};
