// Animations for Cerbedoom. Values are Blockbench-space (what Blockbench shows):
// rot +x = nose up, +y = turn to its left, +z = roll toward its left.
// pos +x = its right, +y = up, +z = backwards. For a leg hanging down +x swings the paw forward;
// for the tail (pointing backwards) -x lifts it.
'use strict';
const S = (amp, speed, phase = 0, off = 0) => {
  if (!amp) return off;
  const core = `math.sin(q.anim_time*${speed}${phase ? (phase > 0 ? '+' + phase : phase) : ''})`;
  const a = amp === 1 ? core : `${amp}*${core}`;
  return off ? `${off}+${a}` : a;
};
const H = (amp, speed, phase = 0) => `${amp}*math.max(0, math.sin(q.anim_time*${speed}${phase ? '+' + phase : ''}))`;
const cr = (v) => ({ v, lerp: 'catmullrom' });
const keys = (obj) => Object.fromEntries(Object.entries(obj).map(([t, v]) => [t, cr(v)]));

const SHOW = -0.5; // slides a closed-eye plane out in front of its head
const HEADS = ['head', 'head_right', 'head_left'];
// eyes of one head shut from t0 to t1 (and stay shut when t1 is null)
const shut = (h, t0, t1, d = 0.0417) => ({
  [`${h}_eyes_closed`]: {
    position: t1 === null
      ? { 0: [0, 0, 0], [t0]: [0, 0, 0], [+(t0 + d).toFixed(4)]: [0, 0, SHOW] }
      : { 0: [0, 0, 0], [t0]: [0, 0, 0], [+(t0 + d).toFixed(4)]: [0, 0, SHOW], [t1]: [0, 0, SHOW], [+(t1 + d).toFixed(4)]: [0, 0, 0] },
  },
});
const shutAlways = (h) => ({ [`${h}_eyes_closed`]: { position: [0, 0, SHOW] } });
const CRY = 'pokemon.houndoom.cry';

// tail: a travelling wave from the base to the arrowhead
const tailWave = (amp, speed, lift = 0, up = 0) => ({
  tail: { rotation: [S(lift, speed, 0, up), S(amp, speed), 0] },
  tail2: { rotation: [S(lift, speed, -40), S(amp * 1.2, speed, -50), 0] },
  tail3: { rotation: [S(lift, speed, -80), S(amp * 1.4, speed, -100), 0] },
  tail4: { rotation: [0, S(amp * 1.6, speed, -150), 0] },
  tail_tip: { rotation: [0, S(amp * 1.8, speed, -200), 0] },
});

module.exports = (m) => {
  // ------------------------------------------------------------ ground idle: breathing; each head looks around on its own
  m.anim('ground_idle', {
    loop: true,
    bones: {
      torso: { scale: [S(0.01, 110, 0, 1), S(0.02, 110, 0, 1), S(0.01, 110, 0, 1)] },
      neck: { rotation: [S(2, 110, -40), S(4, 30), 0] },
      head: { rotation: [S(2, 110, -80), S(10, 30, 40), S(3, 45)] },
      neck_right: { rotation: [S(3, 90, 60), S(5, 42, 120), 0] },
      head_right: { rotation: [S(3, 90, 20), S(14, 42, 160), S(5, 60)] },
      head_right_jaw: { rotation: [`-4-4*math.pow(math.max(0, math.sin(q.anim_time*300)), 2)`, 0, 0] }, // panting
      neck_left: { rotation: [S(3, 70, 200), S(-5, 36, 30), 0] },
      head_left: { rotation: [S(3, 70, 160), S(-12, 36, 70), S(-4, 50)] },
      head_left_jaw: { rotation: [S(2, 140, 0, -1), 0, 0] },
      head_jaw: { rotation: [S(1.5, 110, -40), 0, 0] },
      chain_right: { rotation: [S(3, 110), 0, S(3, 55)] },
      chain_left: { rotation: [S(3, 110, 90), 0, S(-3, 55, 90)] },
      ...tailWave(6, 60, 3, 0),
    },
  });

  // ------------------------------------------------------------ walk: diagonal gait, heads bobbing out of step, tail swaying
  const W = 330;
  const legs = (amp, speed) => ({
    leg_front_right: { rotation: [S(amp, speed), 0, 0], position: [0, H(0.6, speed, 90), 0] },
    leg_front_right2: { rotation: [H(-38, speed, 90), 0, 0] },
    leg_front_left: { rotation: [S(amp, speed, 180), 0, 0], position: [0, H(0.6, speed, 270), 0] },
    leg_front_left2: { rotation: [H(-38, speed, 270), 0, 0] },
    leg_back_right: { rotation: [S(amp * 0.8, speed, 180), 0, 0], position: [0, H(0.6, speed, 270), 0] },
    leg_back_right2: { rotation: [H(24, speed, 270), 0, 0] },
    leg_back_left: { rotation: [S(amp * 0.8, speed), 0, 0], position: [0, H(0.6, speed, 90), 0] },
    leg_back_left2: { rotation: [H(24, speed, 90), 0, 0] },
  });
  m.anim('ground_walk', {
    loop: true,
    bones: {
      // the planted feet sit 0.22 lower mid-stride than at full stride: the body bobs to match
      body: { position: [0, S(-0.11, W * 2, 90, 0.11), 0], rotation: [S(1, W * 2), 0, S(1.5, W)] },
      ...legs(22, W),
      neck: { rotation: [S(3, W * 2, 30), 0, 0] },
      head: { rotation: [S(3, W * 2, 60, -2), 0, 0] },
      neck_right: { rotation: [S(3, W * 2, 90), S(4, W, 60), 0] },
      head_right: { rotation: [S(3, W * 2, 120), S(6, W, 90), 0] },
      neck_left: { rotation: [S(3, W * 2, 150), S(-4, W, 120), 0] },
      head_left: { rotation: [S(3, W * 2, 180), S(-6, W, 150), 0] },
      head_right_jaw: { rotation: [`-3-3*math.max(0, math.sin(q.anim_time*${W * 2}))`, 0, 0] },
      chain_right: { rotation: [S(6, W * 2), 0, S(4, W)] },
      chain_left: { rotation: [S(6, W * 2, 90), 0, S(-4, W)] },
      ...tailWave(10, W, 4, -4),
    },
  });

  // ------------------------------------------------------------ battle idle: crouched, all three heads low and snarling in turn, tail lashing
  const B = 260;
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { position: [0, -1.2, 0], rotation: [-4, 0, 0] },
      // the body pitches nose-down, so the front legs are pushed down less than the hind legs are pulled up
      leg_front_right: { rotation: [-8, 0, 0], position: [0, 2.26, 0] },
      leg_front_left: { rotation: [-8, 0, 0], position: [0, 2.26, 0] },
      leg_back_right: { rotation: [4, 0, 0], position: [0, -0.89, 0] },
      leg_back_left: { rotation: [4, 0, 0], position: [0, -0.89, 0] },
      torso: { scale: [1, S(0.02, B * 2, 0, 1), 1] },
      neck: { rotation: [S(2, B, 0, -8), S(4, 60), 0] },
      head: { rotation: [S(2, B, 40, -2), S(5, 60, 40), 0] },
      head_jaw: { rotation: [`-4-10*math.pow(math.max(0, math.sin(q.anim_time*${B / 2})), 8)`, 0, 0] },
      neck_right: { rotation: [S(3, B, 120, -6), S(6, 50, 60), 0] },
      head_right: { rotation: [S(3, B, 160), S(8, 50, 100), 0] },
      head_right_jaw: { rotation: [`-4-10*math.pow(math.max(0, math.sin(q.anim_time*${B / 2}+120)), 8)`, 0, 0] },
      neck_left: { rotation: [S(3, B, 240, -6), S(-6, 55, 30), 0] },
      head_left: { rotation: [S(3, B, 280), S(-8, 55, 70), 0] },
      head_left_jaw: { rotation: [`-4-10*math.pow(math.max(0, math.sin(q.anim_time*${B / 2}+240)), 8)`, 0, 0] },
      chain_right: { rotation: [S(5, B), 0, S(3, B / 2)] },
      chain_left: { rotation: [S(5, B, 90), 0, S(-3, B / 2)] },
      ...tailWave(14, B, 6, -22),
    },
  });

  // ------------------------------------------------------------ sleep: lies down; the middle and left heads sleep, the right one keeps watch
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { position: [0, -12.36, 0] },
      torso: { scale: [S(0.012, 60, 0, 1.01), S(0.025, 60, 0, 0.99), S(0.012, 60, 0, 1.01)] },
      leg_front_right: { rotation: [78, 0, -4] },
      leg_front_left: { rotation: [78, 0, 4] },
      leg_front_right2: { rotation: [4, 0, 0] },
      leg_front_left2: { rotation: [4, 0, 0] },
      paw_front_right: { rotation: [-82, 0, 0] },
      paw_front_left: { rotation: [-82, 0, 0] },
      // hind legs folded under the body (angles chosen by sweeping them against the ground)
      leg_back_right: { rotation: [70, -20, -8] },
      leg_back_left: { rotation: [70, 20, 8] },
      leg_back_right2: { rotation: [-120, 0, 0] },
      leg_back_left2: { rotation: [-120, 0, 0] },
      leg_back_right3: { rotation: [60, 0, 0] },
      leg_back_left3: { rotation: [60, 0, 0] },
      neck: { rotation: [S(1, 60, -40, -22), 0, 0] },
      head: { rotation: [S(1.5, 60, -60, -6), 8, 0] },
      ...shutAlways('head'),
      neck_left: { rotation: [-26, 10, 16] },
      head_left: { rotation: [S(1.5, 60, 120, -10), 4, -24] },
      ...shutAlways('head_left'),
      // the watch head: raised, slowly scanning, ears (horns) up
      neck_right: { rotation: [4, S(6, 25), 0] },
      head_right: { rotation: [S(2, 40, 30, 4), S(22, 25, 20), 0] },
      tail: { rotation: [14, 40, 0] },
      tail2: { rotation: [0, 36, 0] },
      tail3: { rotation: [0, 36, 0] },
      tail4: { rotation: [0, S(6, 40, 0, 30), 0] },
      tail_tip: { rotation: [0, S(10, 40, -60, 20), 0] },
    },
  });

  // ------------------------------------------------------------ blink: the three heads blink slightly out of step
  m.anim('blink', {
    length: 0.45,
    bones: { ...shut('head', 0, 0.1667), ...shut('head_right', 0.12, 0.2867), ...shut('head_left', 0.2, 0.3667) },
  });

  // ------------------------------------------------------------ squabble (quirk): the side heads snap at each other, the leader cuts in
  m.anim('squabble', {
    length: 3.2,
    bones: {
      neck_right: { rotation: keys({ 0: [0, 0, 0], 0.4: [0, 20, 6], 2.4: [0, 20, 6], 2.9: [0, 0, 0], 3.2: [0, 0, 0] }) },
      head_right: { rotation: keys({ 0: [0, 0, 0], 0.4: [-4, 34, 0], 0.8: [-8, 38, 0], 1.2: [-2, 30, 0], 1.6: [-8, 38, 0], 2.4: [0, 26, 0], 2.9: [0, 0, 0], 3.2: [0, 0, 0] }) },
      head_right_jaw: { rotation: { 0: [0, 0, 0], 0.5: [0, 0, 0], 0.65: [-26, 0, 0], 0.8: [0, 0, 0], 1.3: [0, 0, 0], 1.45: [-26, 0, 0], 1.6: [0, 0, 0] } },
      neck_left: { rotation: keys({ 0: [0, 0, 0], 0.5: [0, -20, -6], 2.4: [0, -20, -6], 2.9: [0, 0, 0], 3.2: [0, 0, 0] }) },
      head_left: { rotation: keys({ 0: [0, 0, 0], 0.5: [-4, -34, 0], 1.0: [-8, -38, 0], 1.4: [-2, -30, 0], 1.8: [-8, -38, 0], 2.4: [0, -26, 0], 2.9: [0, 0, 0], 3.2: [0, 0, 0] }) },
      head_left_jaw: { rotation: { 0: [0, 0, 0], 0.9: [0, 0, 0], 1.05: [-26, 0, 0], 1.2: [0, 0, 0], 1.65: [0, 0, 0], 1.8: [-26, 0, 0], 1.95: [0, 0, 0] } },
      // the leader has had enough: rears up, snaps once, and both side heads flinch back
      neck: { rotation: keys({ 0: [0, 0, 0], 1.8: [0, 0, 0], 2.1: [10, 0, 0], 2.4: [-4, 0, 0], 2.9: [0, 0, 0], 3.2: [0, 0, 0] }) },
      head: { rotation: keys({ 0: [0, 0, 0], 0.8: [0, 14, 0], 1.4: [0, -14, 0], 1.9: [8, 0, 0], 2.2: [-10, 0, 0], 2.9: [0, 0, 0], 3.2: [0, 0, 0] }) },
      head_jaw: { rotation: { 0: [0, 0, 0], 2.0: [0, 0, 0], 2.15: [-30, 0, 0], 2.35: [0, 0, 0] } },
      ...shut('head_right', 2.2, 2.6), ...shut('head_left', 2.2, 2.6),
    },
  });

  // ------------------------------------------------------------ howl (quirk): the three heads raise their muzzles and howl one after another
  const howl = (h, n, t0, dir) => ({
    [n]: { rotation: keys({ 0: [0, 0, 0], [t0]: [0, 0, 0], [t0 + 0.4]: [20, 0, dir * 6], [t0 + 1.6]: [20, 0, dir * 6], [t0 + 2.0]: [0, 0, 0] }) },
    [h]: { rotation: keys({ 0: [0, 0, 0], [t0]: [0, 0, 0], [t0 + 0.4]: [28, 0, 0], [t0 + 1.6]: [26, 0, 0], [t0 + 2.0]: [0, 0, 0] }) },
    [`${h}_jaw`]: { rotation: { 0: [0, 0, 0], [t0 + 0.3]: [0, 0, 0], [t0 + 0.5]: [-24, 0, 0], [t0 + 1.5]: [-22, 0, 0], [t0 + 1.8]: [0, 0, 0] } },
    ...shut(h, t0 + 0.35, t0 + 1.6),
  });
  m.anim('howl', {
    length: 3.2,
    bones: { ...howl('head', 'neck', 0.2, 0), ...howl('head_right', 'neck_right', 0.6, 1), ...howl('head_left', 'neck_left', 1.0, -1), ...tailWave(6, 90, 0, -10) },
  });

  // ------------------------------------------------------------ cry: all three roar, staggered
  const roar = (h, n, t0) => ({
    [n]: { rotation: keys({ 0: [0, 0, 0], [t0]: [0, 0, 0], [t0 + 0.25]: [12, 0, 0], [t0 + 0.9]: [10, 0, 0], [t0 + 1.2]: [0, 0, 0] }) },
    [h]: { rotation: keys({ 0: [0, 0, 0], [t0]: [0, 0, 0], [t0 + 0.25]: [14, 0, 0], [t0 + 0.9]: [12, 0, 0], [t0 + 1.2]: [0, 0, 0] }) },
    [`${h}_jaw`]: { rotation: { 0: [0, 0, 0], [t0 + 0.1]: [0, 0, 0], [t0 + 0.25]: [-30, 0, 0], [t0 + 0.85]: [-28, 0, 0], [t0 + 1.05]: [0, 0, 0] } },
  });
  m.anim('cry', {
    length: 1.6,
    sounds: { 0.1667: CRY },
    bones: {
      ...roar('head', 'neck', 0.1), ...roar('head_right', 'neck_right', 0.25), ...roar('head_left', 'neck_left', 0.35),
      torso: { rotation: keys({ 0: [0, 0, 0], 0.3: [4, 0, 0], 1.1: [3, 0, 0], 1.6: [0, 0, 0] }) },
      ...tailWave(10, 200, 0, -12),
    },
  });

  // ------------------------------------------------------------ physical: lunges and bites with all three heads, one after the other
  const bite = (h, n, t0) => ({
    [n]: { rotation: keys({ 0: [0, 0, 0], 0.3: [8, 0, 0], [t0]: [-18, 0, 0], [t0 + 0.2]: [-10, 0, 0], 1.3: [0, 0, 0] }) },
    [`${h}_jaw`]: { rotation: { 0: [0, 0, 0], [t0 - 0.12]: [-34, 0, 0], [t0]: [0, 0, 0], [t0 + 0.1]: [0, 0, 0] } },
  });
  m.anim('physical', {
    length: 1.4,
    bones: {
      body: { position: keys({ 0: [0, 0, 0], 0.3: [0, 0.6, 2], 0.55: [0, 1.4, -5], 0.8: [0, 0.4, -6], 1.1: [0, 0, -2], 1.4: [0, 0, 0] }) },
      leg_front_right: { rotation: keys({ 0: [0, 0, 0], 0.3: [-10, 0, 0], 0.55: [26, 0, 0], 0.8: [8, 0, 0], 1.2: [0, 0, 0] }) },
      leg_front_left: { rotation: keys({ 0: [0, 0, 0], 0.3: [-10, 0, 0], 0.55: [22, 0, 0], 0.8: [6, 0, 0], 1.2: [0, 0, 0] }) },
      leg_back_right: { rotation: keys({ 0: [0, 0, 0], 0.3: [10, 0, 0], 0.55: [-18, 0, 0], 0.8: [-6, 0, 0], 1.2: [0, 0, 0] }) },
      leg_back_left: { rotation: keys({ 0: [0, 0, 0], 0.3: [10, 0, 0], 0.55: [-20, 0, 0], 0.8: [-6, 0, 0], 1.2: [0, 0, 0] }) },
      ...bite('head', 'neck', 0.62), ...bite('head_right', 'neck_right', 0.72), ...bite('head_left', 'neck_left', 0.82),
      ...tailWave(8, 300, 0, -16),
    },
  });

  // ------------------------------------------------------------ special: three streams of fire - heads pull back, then thrust forward with jaws wide open
  const breathe = (h, n, spread) => ({
    [n]: { rotation: keys({ 0: [0, 0, 0], 0.35: [14, 0, 0], 0.65: [-14, spread, 0], 1.35: [-12, spread, 0], 1.7: [0, 0, 0] }) },
    [h]: { rotation: keys({ 0: [0, 0, 0], 0.35: [16, 0, 0], 0.65: [-6, 0, 0], 1.0: [-4, spread * 0.5, 0], 1.35: [-6, 0, 0], 1.7: [0, 0, 0] }) },
    [`${h}_jaw`]: { rotation: { 0: [0, 0, 0], 0.3: [0, 0, 0], 0.55: [-40, 0, 0], 1.35: [-38, 0, 0], 1.6: [0, 0, 0] } },
  });
  m.anim('special', {
    length: 1.8,
    bones: {
      ...breathe('head', 'neck', 0), ...breathe('head_right', 'neck_right', -6), ...breathe('head_left', 'neck_left', 6),
      torso: { rotation: keys({ 0: [0, 0, 0], 0.35: [5, 0, 0], 0.65: [-3, 0, 0], 1.4: [-3, 0, 0], 1.8: [0, 0, 0] }), position: { 0: [0, 0, 0], 0.65: [0, 0, 0], 0.7: ['math.sin(q.anim_time*2000)*0.2', 0, 0], 1.3: ['math.sin(q.anim_time*2000)*0.2', 0, 0], 1.35: [0, 0, 0] } },
      ...tailWave(8, 300, 0, -26),
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: { position: keys({ 0: [0, 0, 0], 0.1: [0, 0.4, 2.2], 0.3: [0, 0, 1], 0.6: [0, 0, 0] }) },
      neck: { rotation: { 0: [0, 0, 0], 0.1: [14, 0, 0], 0.4: [2, 0, 0], 0.6: [0, 0, 0] } },
      neck_right: { rotation: { 0: [0, 0, 0], 0.1: [12, -10, 0], 0.4: [0, 0, 0] } },
      neck_left: { rotation: { 0: [0, 0, 0], 0.1: [12, 10, 0], 0.4: [0, 0, 0] } },
      ...shut('head', 0, 0.4), ...shut('head_right', 0, 0.4), ...shut('head_left', 0, 0.4),
      tail: { rotation: { 0: [0, 0, 0], 0.1: [-20, 0, 0], 0.5: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ faint: the legs buckle, it sinks to the ground and the heads drop one by one
  m.anim('faint', {
    length: 3,
    bones: {
      body: { position: { 0: [0, 0, 0], 0.4: [0, 0, 0], 0.75: [0, -4.6, 0], 1.0: [0, -12.6, 0], 1.1: [0, -12.2, 0], 1.2: [0, -12.33, 0] } },
      leg_front_right: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [78, 0, -4] } },
      leg_front_left: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [78, 0, 4] } },
      paw_front_right: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [-82, 0, 0] } },
      paw_front_left: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [-82, 0, 0] } },
      // hind legs fold like in the sleep pose
      leg_back_right: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [70, -24, -10] } },
      leg_back_left: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [70, 24, 10] } },
      leg_back_right2: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [-120, 0, 0] } },
      leg_back_left2: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [-120, 0, 0] } },
      leg_back_right3: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [60, 0, 0] } },
      leg_back_left3: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.0: [60, 0, 0] } },
      neck_right: { rotation: keys({ 0: [0, 0, 0], 1.1: [0, 0, 0], 1.5: [-30, -10, -20], 3: [-30, -10, -20] }) },
      head_right: { rotation: keys({ 0: [0, 0, 0], 1.1: [0, 0, 0], 1.5: [-12, 0, 26], 3: [-12, 0, 26] }) },
      neck_left: { rotation: keys({ 0: [0, 0, 0], 1.3: [0, 0, 0], 1.7: [-30, 10, 20], 3: [-30, 10, 20] }) },
      head_left: { rotation: keys({ 0: [0, 0, 0], 1.3: [0, 0, 0], 1.7: [-12, 0, -26], 3: [-12, 0, -26] }) },
      neck: { rotation: keys({ 0: [0, 0, 0], 1.5: [4, 0, 0], 1.95: [-28, 0, 0], 3: [-28, 0, 0] }) },
      head: { rotation: keys({ 0: [0, 0, 0], 1.5: [6, 0, 0], 1.95: [-8, 0, 10], 3: [-8, 0, 10] }) },
      ...shut('head_right', 1.2, null), ...shut('head_left', 1.4, null), ...shut('head', 1.7, null),
      head_jaw: { rotation: { 0: [0, 0, 0], 1.8: [0, 0, 0], 2.0: [-12, 0, 0] } },
      tail: { rotation: { 0: [0, 0, 0], 0.4: [0, 0, 0], 1.1: [20, 30, 0] } },
      tail2: { rotation: { 0: [0, 0, 0], 1.1: [0, 20, 0] } },
    },
  });
};
