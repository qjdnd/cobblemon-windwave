// Animations for baby Zubat (Blockbench space: rot +x nose up, +y turn left, +z roll left;
// right wing: +z raises it, +y sweeps it forward. The left wing uses the negated values).
'use strict';
const f = (n) => (Number.isInteger(n) ? String(n) : String(+n.toFixed(4)));
const S = (amp, speed, phase = 0, off = 0) => {
  const core = `math.sin(q.anim_time*${f(speed)}${phase ? (phase > 0 ? '+' : '') + f(phase) : ''})`;
  const a = amp === 1 ? core : `${f(amp)}*${core}`;
  return off ? `${f(off)}+${a}` : a;
};
const neg = (e) => (typeof e === 'number' ? -e : `-(${e})`);
const CRY = 'pokemon.zubat.cry';
const FLAP = "q.has_entity ? { q.sound('animation.leather.wing_flap.small'); };";
const LID_CLOSED = -0.22;

// flapping wings: speed in deg/s, amplitudes for raise (z) and sweep (y), plus a static base pose
function wings(speed, { z = [26, 18, 16], y = [22, 14, 16], baseZ = [8, -4, -10], baseY = [0, 0, 0], lag = 38 } = {}) {
  const out = {};
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    for (let i = 0; i < 3; i++) {
      const nm = i === 0 ? `wing_${side}` : `wing_${side}${i + 1}`;
      const zz = S(z[i], speed, -i * lag, baseZ[i]);
      const yy = S(y[i], speed, -90 - i * lag, baseY[i]);
      out[nm] = { rotation: [0, s > 0 ? yy : neg(yy), s > 0 ? zz : neg(zz)] };
    }
  }
  return out;
}
function flapTimeline(speed, length) {
  const period = 360 / speed;
  const tl = {};
  for (let t = period * 0.25; t < length - 1e-6; t += period) tl[t.toFixed(4)] = FLAP;
  return tl;
}
// static wing pose helper
function wingPose(zs, ys, xs = [0, 0, 0]) {
  const out = {};
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    for (let i = 0; i < 3; i++) {
      const nm = i === 0 ? `wing_${side}` : `wing_${side}${i + 1}`;
      out[nm] = { rotation: [xs[i], s * ys[i], s * zs[i]] };
    }
  }
  return out;
}
// keyframed wing pose over time: frames = {t: [zs, ys]}
function wingKeys(frames, lerp = 'catmullrom') {
  const out = {};
  for (const [side, s] of [['right', 1], ['left', -1]]) {
    for (let i = 0; i < 3; i++) {
      const nm = i === 0 ? `wing_${side}` : `wing_${side}${i + 1}`;
      const kf = {};
      for (const [t, [zs, ys, xs]] of Object.entries(frames)) kf[t] = { v: [xs ? xs[i] : 0, s * ys[i], s * zs[i]], lerp };
      out[nm] = { rotation: kf };
    }
  }
  return out;
}

module.exports = (m) => {
  // ------------------------------------------------------------ hovering (air idle)
  const IDLE = 900; // 2.5 flaps per second
  m.anim('air_idle', {
    loop: true, length: 4,
    timeline: flapTimeline(IDLE, 4),
    bones: {
      body: {
        position: [S(0.6, 90, 30), `4+${S(0.55, IDLE, 90)}+${S(1.1, 90)}`, 0],
        rotation: [S(3, IDLE, 120), S(4, 90), S(3, 90, 60)],
      },
      pupil: { position: ['math.round(math.sin(q.anim_time*90)*0.7)', 0, 0] },
      ...wings(IDLE),
    },
  });

  // ------------------------------------------------------------ ground idle: hovers low and lazily
  const LOW = 720;
  m.anim('ground_idle', {
    loop: true, length: 4,
    timeline: flapTimeline(LOW, 4),
    bones: {
      body: {
        position: [0, `3+${S(0.45, LOW, 90)}+${S(0.7, 90)}`, 0],
        rotation: [S(2.5, LOW, 120), S(5, 90), S(2.5, 90, 60)],
      },
      pupil: { position: ['math.round(math.sin(q.anim_time*90)*0.7)', 0, 0] },
      ...wings(LOW, { z: [22, 16, 14], y: [18, 12, 14], baseZ: [4, -6, -12] }),
    },
  });

  // ------------------------------------------------------------ flying
  const FLY = 1260;
  const flyBones = {
    body: { position: [0, `4+${S(0.7, FLY, 90)}`, 0], rotation: [`-16+${S(3, FLY, 120)}`, 0, S(4, 90)] },
    ...wings(FLY, { z: [34, 20, 18], y: [26, 16, 18], baseZ: [6, -4, -8], baseY: [-8, -6, -6] }),
  };
  m.anim('air_fly', { loop: true, length: 4, timeline: flapTimeline(FLY, 4), bones: flyBones });
  m.anim('ground_walk', { loop: true, length: 4, timeline: flapTimeline(FLY, 4), bones: {
    ...flyBones,
    body: { position: [0, `3+${S(0.6, FLY, 90)}`, 0], rotation: [`-10+${S(3, FLY, 120)}`, 0, S(4, 90)] },
  } });

  // ------------------------------------------------------------ battle idle: tense stare, quick flaps
  const BAT = 1080;
  m.anim('battle_idle', {
    loop: true, length: 4,
    timeline: flapTimeline(BAT, 4),
    bones: {
      body: { position: [S(0.8, 90), `4+${S(0.55, BAT, 90)}+${S(0.6, 180)}`, 0], rotation: [`-4+${S(2.5, BAT, 120)}`, S(3, 90), S(3, 180)] },
      pupil: { scale: [S(0.04, 180, 0, 0.92), S(0.04, 180, 0, 0.92), 1] },
      ...wings(BAT, { z: [30, 18, 16], y: [20, 14, 16], baseZ: [12, 0, -6] }),
    },
  });

  // ------------------------------------------------------------ sleep: wings wrapped around like a cocoon, resting on the ground
  m.anim('sleep', {
    loop: true,
    bones: {
      body: { position: [0, -4.6, 0], rotation: [S(1.2, 60), 0, 3], scale: [S(0.02, 60, 0, 1), S(0.035, 60, 0, 1), S(0.02, 60, 0, 1)] },
      eyelid: { position: [0, 0, LID_CLOSED] },
      pupil: { position: [0, -0.2, 0] },
      wing_right: { rotation: [-78, 58, S(1.5, 60, -30, -6)] },
      wing_right2: { rotation: [0, 52, 0] },
      wing_right3: { rotation: [0, S(3, 60, -60, 46), 0] },
      wing_left: { rotation: [-78, -58, S(-1.5, 60, -30, 6)] },
      wing_left2: { rotation: [0, -52, 0] },
      wing_left3: { rotation: [0, S(-3, 60, -60, -46), 0] },
    },
  });

  // ------------------------------------------------------------ blink
  m.anim('blink', {
    length: 0.1667,
    bones: { eyelid: { position: { 0: [0, 0, 0], 0.0417: [0, 0, LID_CLOSED], 0.125: [0, 0, LID_CLOSED], 0.1667: [0, 0, 0] } } },
  });

  // ------------------------------------------------------------ look quirk: the whole ball is an eye, so the pupil looks around
  m.anim('look_quirk', {
    length: 3,
    bones: {
      pupil: { position: { 0: [0, 0, 0], 0.3: [0, 0, 0], 0.3417: [1, 0, 0], 1.0: [1, 0, 0], 1.0417: [0, 1, 0], 1.6: [0, 1, 0], 1.6417: [-1, 0, 0], 2.4: [-1, 0, 0], 2.4417: [0, 0, 0] } },
      body: { rotation: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.5: { v: [0, 10, 3], lerp: 'catmullrom' }, 1.3: { v: [6, 0, 0], lerp: 'catmullrom' }, 2.0: { v: [0, -10, -3], lerp: 'catmullrom' }, 2.7: { v: [0, 0, 0], lerp: 'catmullrom' }, 3.0: { v: [0, 0, 0], lerp: 'catmullrom' } } },
      eyelid: { position: { 0: [0, 0, 0], 2.6: [0, 0, 0], 2.6417: [0, 0, LID_CLOSED], 2.75: [0, 0, LID_CLOSED], 2.7917: [0, 0, 0] } },
    },
  });

  // ------------------------------------------------------------ cry: wings thrown up, eye goes wide
  m.anim('cry', {
    length: 1.25,
    sounds: { 0.0417: CRY },
    timeline: { 0.25: FLAP, 0.5: FLAP },
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.15: { v: [0, -0.8, 0], lerp: 'catmullrom' }, 0.35: { v: [0, 1.8, 0], lerp: 'catmullrom' }, 0.8: { v: [0, 1.2, 0], lerp: 'catmullrom' }, 1.25: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.35: [10, 0, 0], 0.9: [6, 0, 0], 1.25: [0, 0, 0] },
        scale: { 0: [1, 1, 1], 0.15: [1.08, 0.92, 1.08], 0.35: [0.95, 1.08, 0.95], 0.55: [1.02, 0.98, 1.02], 0.8: [1, 1, 1] },
      },
      pupil: { scale: { 0: [1, 1, 1], 0.15: [1, 1, 1], 0.3: [0.6, 0.6, 1], 0.9: [0.6, 0.6, 1], 1.1: [1, 1, 1] } },
      ...wingKeys({
        0: [[0, 0, 0], [0, 0, 0]],
        0.15: [[-10, -8, -6], [10, 6, 4]],
        0.35: [[38, 20, 14], [-12, -8, -6]],
        0.5: [[10, -4, -10], [14, 8, 8]],
        0.65: [[36, 18, 12], [-10, -6, -6]],
        0.9: [[24, 10, 6], [0, 0, 0]],
        1.25: [[0, 0, 0], [0, 0, 0]],
      }),
    },
  });

  // ------------------------------------------------------------ physical: dive-bomb forwards with wings swept back
  m.anim('physical', {
    length: 1.25,
    timeline: { 0.2: FLAP },
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.25: { v: [0, 1.5, 2], lerp: 'catmullrom' }, 0.5: { v: [0, -1, -7], lerp: 'catmullrom' }, 0.7: { v: [0, 0, -6], lerp: 'catmullrom' }, 1.25: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.25: [12, 0, 0], 0.5: [-28, 0, 0], 0.75: [-8, 0, 0], 1.1: [0, 0, 0] },
      },
      pupil: { scale: { 0: [1, 1, 1], 0.3: [0.75, 0.75, 1], 0.9: [0.75, 0.75, 1], 1.1: [1, 1, 1] } },
      ...wingKeys({
        0: [[0, 0, 0], [0, 0, 0]],
        0.25: [[30, 16, 10], [10, 8, 6]],
        0.5: [[-6, -8, -8], [-55, -30, -20]],
        0.75: [[4, 0, -4], [-30, -16, -10]],
        1.25: [[0, 0, 0], [0, 0, 0]],
      }),
    },
  });

  // ------------------------------------------------------------ special: hypnotic stare, wings spread wide
  m.anim('special', {
    length: 1.75,
    timeline: { 0.3: FLAP },
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.3: { v: [0, 2, 0], lerp: 'catmullrom' }, 1.4: { v: [0, 2, 0], lerp: 'catmullrom' }, 1.75: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.3: [8, 0, 0], 0.6: [8, 0, 6], 0.9: [8, 0, -6], 1.2: [8, 0, 6], 1.5: [4, 0, 0], 1.75: [0, 0, 0] },
      },
      pupil: { scale: { 0: [1, 1, 1], 0.3: [1.25, 1.25, 1], 0.5: [0.8, 0.8, 1], 0.7: [1.25, 1.25, 1], 0.9: [0.8, 0.8, 1], 1.1: [1.25, 1.25, 1], 1.3: [0.8, 0.8, 1], 1.6: [1, 1, 1] } },
      ...wingKeys({
        0: [[0, 0, 0], [0, 0, 0]],
        0.3: [[24, 10, 14], [-6, -4, -4]],
        1.4: [[24, 10, 14], [-6, -4, -4]],
        1.75: [[0, 0, 0], [0, 0, 0]],
      }),
    },
  });

  // ------------------------------------------------------------ recoil
  m.anim('recoil', {
    length: 0.6,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.12: { v: [0, 1, 3], lerp: 'catmullrom' }, 0.35: { v: [0, 0.3, 1.5], lerp: 'catmullrom' }, 0.6: { v: [0, 0, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.12: [18, 0, 10], 0.35: [4, 0, -3], 0.6: [0, 0, 0] },
      },
      eyelid: { position: { 0: [0, 0, 0], 0.05: [0, 0, LID_CLOSED], 0.3: [0, 0, LID_CLOSED], 0.35: [0, 0, 0] } },
      ...wingKeys({ 0: [[0, 0, 0], [0, 0, 0]], 0.12: [[30, 20, 20], [-20, -10, -10]], 0.35: [[-8, -4, -4], [6, 4, 4]], 0.6: [[0, 0, 0], [0, 0, 0]] }),
    },
  });

  // ------------------------------------------------------------ faint: wings go limp and it drops to the ground
  m.anim('faint', {
    length: 1.5, hold: true,
    bones: {
      body: {
        position: { 0: { v: [0, 0, 0], lerp: 'catmullrom' }, 0.2: { v: [0, 1.2, 0], lerp: 'catmullrom' }, 0.7: { v: [0, -6.4, 0], lerp: 'catmullrom' }, 0.85: { v: [0, -5.6, 0], lerp: 'catmullrom' }, 1.0: { v: [0, -6.4, 0], lerp: 'catmullrom' } },
        rotation: { 0: [0, 0, 0], 0.7: [-12, 0, 18], 1.0: [-10, 0, 22] },
        scale: { 0: [1, 1, 1], 0.7: [1, 1, 1], 0.78: [1.08, 0.9, 1.08], 0.9: [1, 1, 1] },
      },
      eyelid: { position: { 0: [0, 0, 0], 0.4: [0, 0, 0], 0.45: [0, 0, LID_CLOSED] } },
      ...wingKeys({
        0: [[0, 0, 0], [0, 0, 0], [0, 0, 0]],
        0.2: [[20, 10, 6], [0, 0, 0], [0, 0, 0]],
        0.75: [[-10, -6, -4], [-8, -4, 0], [-78, 0, 0]],
        0.85: [[-4, -2, -2], [-8, -4, 0], [-70, 0, 0]],
        1.0: [[-8, -6, -4], [-8, -4, 0], [-80, 0, 0]],
      }),
    },
  });

  // ------------------------------------------------------------ perched on a shoulder: wings folded back
  for (const side of ['left', 'right']) {
    m.anim('shoulder_' + side, {
      loop: true,
      bones: {
        body: { position: [0, `-5+${S(0.15, 90)}`, 0], scale: [S(0.015, 90, 0, 0.85), S(0.025, 90, 0, 0.85), 0.85] },
        pupil: { position: ['math.round(math.sin(q.anim_time*90)*0.7)', 0, 0] },
        ...wingPose([-20, -16, -30], [-62, -58, -40]),
      },
    });
  }
};
