// Animations for baby Litwick (Blockbench space: rot +x tips the top backwards,
// +z rolls toward its left; pos +z = backwards).
'use strict';
const f = (n) => (Number.isInteger(n) ? String(n) : String(+n.toFixed(4)));
const S = (amp, speed, phase = 0, off = 0) => {
  const core = `math.sin(q.anim_time*${f(speed)}${phase ? (phase > 0 ? '+' : '') + f(phase) : ''})`;
  const a = amp === 1 ? core : `${f(amp)}*${core}`;
  return off ? `${f(off)}+${a}` : a;
};
const CRY = 'pokemon.litwick.cry';
const CLOSE = -0.3;  // slides the closed-eye overlay in front of the face
const HAPPY = -0.4;
const MOUTH = -0.3;
const FLAME = ['flame', 'flame2', 'flame3', 'flame4', 'flame5', 'flame6', 'flame7', 'flame_tip'];

// waving flame: each tier sways a bit more and a bit later than the one below it
function flameWave(speed, amp = 1, { lean = 0, flicker = 0.04 } = {}) {
  // Tiers are nested bones, so rotations and scales accumulate up the chain:
  // keep per-tier values small and only flicker the base tier's scale noticeably.
  const out = {};
  FLAME.forEach((nm, i) => {
    const a = (1.2 + i * 0.9) * amp;
    const fl = i === 0 ? flicker : flicker * 0.25;
    out[nm] = {
      rotation: [S(a * 0.5, speed * 0.8, -i * 35, lean * (i ? 0.6 : 0.5)), 0, S(a, speed, -i * 40)],
      scale: [S(fl, speed * 6, -i * 50, 1), S(fl * 1.6, speed * 5, -i * 70, 1), S(fl, speed * 6, -i * 50, 1)],
    };
  });
  return out;
}
function flameKeys(frames) {
  // frames: {t: {rot: [x,y,z] (grows slightly per tier), scale: s (base tier only, children inherit it)}}
  const out = {};
  FLAME.forEach((nm, i) => {
    const rot = {}, scl = {};
    for (const [t, fr] of Object.entries(frames)) {
      const k = 0.6 + i * 0.12;
      rot[t] = { v: (fr.rot || [0, 0, 0]).map((v) => +(v * k).toFixed(3)), lerp: 'catmullrom' };
      const sc = fr.scale ?? 1;
      scl[t] = { v: [sc, sc, sc], lerp: 'catmullrom' };
    }
    out[nm] = i === 0 ? { rotation: rot, scale: scl } : { rotation: rot };
  });
  return out;
}

module.exports = (m) => {
  // ------------------------------------------------------------ floating idle
  m.anim('ground_idle', {
    loop: true,
    bones: {
      body: { position: [0, S(0.9, 90), 0], rotation: [S(1.5, 90, -60), S(3, 45), S(2, 60)] },
      arm_right: { rotation: [S(6, 90, -40), 0, S(5, 90, -80)] },
      arm_left: { rotation: [S(6, 90, -40), 0, S(-5, 90, -80)] },
      tail: { rotation: [S(8, 90, -90), 0, S(10, 60, -60)] },
      tail2: { rotation: [S(10, 90, -130), 0, S(12, 60, -100)] },
      ...flameWave(150),
    },
  });

  // ------------------------------------------------------------ gliding forwards
  m.anim('ground_walk', {
    loop: true,
    bones: {
      body: { position: [0, `0.8+${S(0.6, 240)}`, 0], rotation: [`-9+${S(1.5, 240, -40)}`, 0, S(3, 120)] },
      arm_right: { rotation: [`25+${S(6, 240, -40)}`, 0, 0] },
      arm_left: { rotation: [`25+${S(6, 240, -40)}`, 0, 0] },
      tail: { rotation: [`30+${S(6, 240, -90)}`, 0, S(10, 120, -60)] },
      tail2: { rotation: [`20+${S(8, 240, -130)}`, 0, 0] },
      ...flameWave(220, 1.1, { lean: 7 }),
    },
  });

  // ------------------------------------------------------------ battle: flame flared, arms up
  m.anim('battle_idle', {
    loop: true,
    bones: {
      body: { position: [0, `-0.4+${S(0.6, 150)}`, 0], rotation: [`-3+${S(1.5, 150, -60)}`, 0, S(2, 75)] },
      arm_right: { rotation: [`-15+${S(8, 300)}`, 0, `-20+${S(6, 150)}`] },
      arm_left: { rotation: [`-15+${S(8, 300, 180)}`, 0, `20+${S(-6, 150)}`] },
      tail: { rotation: [S(10, 150, -90), 0, S(12, 75, -60)] },
      tail2: { rotation: [S(12, 150, -130), 0, 0] },
      ...flameWave(260, 1.25, { flicker: 0.07 }),
      flame: { rotation: [S(1.5, 200), 0, S(2.5, 260)], scale: [S(0.04, 1300, 0, 1.08), S(0.07, 1100, 0, 1.12), S(0.04, 1300, 0, 1.08)] },
    },
  });

  // ------------------------------------------------------------ sleep: settles on the ground, flame burns low
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { position: [0, -1.4, 0], rotation: [S(1, 45), 0, 3], scale: [S(0.015, 45, 0, 1.02), S(0.03, 45, 0, 0.97), S(0.015, 45, 0, 1.02)] },
      eyes_closed: { position: [0, 0, CLOSE] },
      arm_right: { rotation: [30, -10, 20] },
      arm_left: { rotation: [30, 10, -20] },
      tail: { rotation: [0, 60, -60] },
      tail2: { rotation: [0, 0, -40] },
      flame: { rotation: [S(1, 60), 0, S(2, 70, 0, -3)], scale: [0.9, S(0.03, 400, 0, 0.82), 0.9] },
      flame2: { rotation: [S(1.2, 60, -30), 0, S(2.5, 70, -30, -5)] },
      flame3: { rotation: [S(1.5, 60, -60), 0, S(3, 70, -60, -6)] },
      flame4: { rotation: [S(1.8, 60, -90), 0, S(3.5, 70, -90, -7)] },
      flame5: { rotation: [S(2.1, 60, -120), 0, S(4, 70, -120, -8)] },
      flame6: { rotation: [S(2.4, 60, -150), 0, S(4.5, 70, -150, -9)] },
      flame7: { rotation: [S(2.7, 60, -180), 0, S(5, 70, -180, -10)] },
      flame_tip: { rotation: [S(3, 60, -210), 0, S(5.5, 70, -210, -10)] },
    },
  });

  // ------------------------------------------------------------ blink
  m.anim('blink', {
    length: 0.1667,
    bones: { eyes_closed: { position: { 0: [0, 0, 0], 0.0417: [0, 0, CLOSE], 0.125: [0, 0, CLOSE], 0.1667: [0, 0, 0] } } },
  });

  // ------------------------------------------------------------ cry: happy squint, flame flares up
  m.anim('cry', {
    length: 1.25,
    sounds: { 0.0833: CRY },
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.15: { v: [0, -0.8, 0], lerp: 'catmullrom' }, 0.4: { v: [0, 1.6, 0], lerp: 'catmullrom' }, 0.8: { v: [0, 0.8, 0], lerp: 'catmullrom' }, 1.25: { v: [0, 0, 0], lerp: 'catmullrom' } },
        scale: { 0: [1, 1, 1], 0.15: [1.06, 0.94, 1.06], 0.4: [0.97, 1.05, 0.97], 0.7: [1, 1, 1] },
        rotation: { 0: [0, 0, 0], 0.4: [6, 0, 0], 0.8: [4, 0, -3], 1.1: [0, 0, 0] },
      },
      eyes_happy: { position: { 0: [0, 0, 0], 0.125: [0, 0, 0], 0.1667: [0, 0, HAPPY], 1.0: [0, 0, HAPPY], 1.0417: [0, 0, 0] } },
      mouth: { position: { 0: [0, 0, 0], 0.125: [0, 0, 0], 0.1667: [0, 0, MOUTH], 0.9: [0, 0, MOUTH], 0.9417: [0, 0, 0] } },
      arm_right: { rotation: { 0: [0, 0, 0], 0.3: [-50, 0, -40], 0.6: [-40, 0, -30], 0.9: [-50, 0, -40], 1.2: [0, 0, 0] } },
      arm_left: { rotation: { 0: [0, 0, 0], 0.3: [-50, 0, 40], 0.6: [-40, 0, 30], 0.9: [-50, 0, 40], 1.2: [0, 0, 0] } },
      ...flameKeys({ 0: { rot: [0, 0, 0], scale: 1 }, 0.3: { rot: [4, 0, 6], scale: 1.18 }, 0.55: { rot: [2, 0, -6], scale: 1.12 }, 0.8: { rot: [3, 0, 5], scale: 1.16 }, 1.25: { rot: [0, 0, 0], scale: 1 } }),
    },
  });

  // ------------------------------------------------------------ physical: ghostly tackle
  m.anim('physical', {
    length: 1.25,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.3: { v: [0, 1, 2.5], lerp: 'catmullrom' }, 0.55: { v: [0, -0.5, -6], lerp: 'catmullrom' }, 0.75: { v: [0, 0, -5], lerp: 'catmullrom' }, 1.25: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.3: [8, 0, 0], 0.55: [-16, 0, 0], 0.8: [-4, 0, 0], 1.2: [0, 0, 0] },
      },
      arm_right: { rotation: { 0: [0, 0, 0], 0.3: [-30, 0, -20], 0.55: [50, 0, 10], 1.0: [0, 0, 0] } },
      arm_left: { rotation: { 0: [0, 0, 0], 0.3: [-30, 0, 20], 0.55: [50, 0, -10], 1.0: [0, 0, 0] } },
      ...flameKeys({ 0: { rot: [0, 0, 0] }, 0.3: { rot: [-6, 0, 0] }, 0.55: { rot: [12, 0, 0], scale: 1.1 }, 0.8: { rot: [5, 0, 0] }, 1.25: { rot: [0, 0, 0] } }),
    },
  });

  // ------------------------------------------------------------ special: the flame blazes up
  m.anim('special', {
    length: 1.5,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.35: { v: [0, 2, 0], lerp: 'catmullrom' }, 1.1: { v: [0, 2, 0], lerp: 'catmullrom' }, 1.5: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.35: [5, 0, 0], 1.1: [5, 0, 0], 1.5: [0, 0, 0] },
      },
      arm_right: { rotation: { 0: [0, 0, 0], 0.35: [-70, 0, -30], 1.1: [-70, 0, -30], 1.5: [0, 0, 0] } },
      arm_left: { rotation: { 0: [0, 0, 0], 0.35: [-70, 0, 30], 1.1: [-70, 0, 30], 1.5: [0, 0, 0] } },
      eyes_happy: { position: { 0: [0, 0, 0], 0.3: [0, 0, 0], 0.3417: [0, 0, HAPPY], 1.1: [0, 0, HAPPY], 1.1417: [0, 0, 0] } },
      ...flameKeys({ 0: { rot: [0, 0, 0], scale: 1 }, 0.35: { rot: [0, 0, 5], scale: 1.35 }, 0.6: { rot: [0, 0, -5], scale: 1.28 }, 0.85: { rot: [0, 0, 5], scale: 1.35 }, 1.1: { rot: [0, 0, -2], scale: 1.3 }, 1.5: { rot: [0, 0, 0], scale: 1 } }),
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.1: { v: [0, 0.8, 2.5], lerp: 'catmullrom' }, 0.35: { v: [0, 0.2, 1], lerp: 'catmullrom' }, 0.6: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.1: [14, 0, 8], 0.35: [2, 0, -2], 0.6: [0, 0, 0] },
      },
      eyes_closed: { position: { 0: [0, 0, 0], 0.05: [0, 0, CLOSE], 0.35: [0, 0, CLOSE], 0.4: [0, 0, 0] } },
      ...flameKeys({ 0: { rot: [0, 0, 0] }, 0.12: { rot: [10, 0, -6], scale: 0.9 }, 0.35: { rot: [-4, 0, 3] }, 0.6: { rot: [0, 0, 0] } }),
    },
  });

  // ------------------------------------------------------------ faint: sinks to the ground as the flame gutters out
  m.anim('faint', {
    length: 1.5, hold: true,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.25: { v: [0, 1, 0], lerp: 'catmullrom' }, 0.8: { v: [0, -2.2, 0], lerp: 'catmullrom' }, 1.0: { v: [0, -1.8, 0], lerp: 'catmullrom' }, 1.2: { v: [0, -2.2, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.8: [-6, 0, 14], 1.2: [-5, 0, 12] },
        scale: { 0: [1, 1, 1], 0.8: [1, 1, 1], 0.9: [1.06, 0.92, 1.06], 1.05: [1.02, 0.97, 1.02] },
      },
      eyes_closed: { position: { 0: [0, 0, 0], 0.5: [0, 0, 0], 0.55: [0, 0, CLOSE] } },
      arm_right: { rotation: { 0: [0, 0, 0], 0.8: [40, 0, 30] } },
      arm_left: { rotation: { 0: [0, 0, 0], 0.8: [40, 0, -30] } },
      ...flameKeys({ 0: { rot: [0, 0, 0], scale: 1 }, 0.3: { rot: [0, 0, 4], scale: 1.08 }, 0.9: { rot: [2, 0, -10], scale: 0.62 }, 1.2: { rot: [2, 0, -12], scale: 0.55 } }),
    },
  });

  // ------------------------------------------------------------ shoulder perch
  for (const side of ['left', 'right']) {
    m.anim('shoulder_' + side, {
      loop: true,
      bones: {
        body: { position: [0, S(0.4, 90), 0], rotation: [0, 0, S(2, 60)] },
        arm_right: { rotation: [S(5, 90, -40), 0, 0] },
        arm_left: { rotation: [S(5, 90, -40), 0, 0] },
        ...flameWave(150, 0.8),
      },
    });
  }
};
