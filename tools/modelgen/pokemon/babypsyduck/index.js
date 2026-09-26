// Baby Psyduck: everything the build, verify and preview scripts need.
'use strict';
module.exports = {
  ...require('./cobblemon'),
  build: require('./model').build,
  // poses rendered by roundtrip.js ('-' = rest pose)
  verifyPoses: [['-', 0], ['ground_idle', 0.7], ['ground_walk', 0.3], ['water_swim', 0.3], ['battle_idle', 0.4], ['sleep', 1], ['blink', 0.1],
    ['headache', 1.0], ['cry', 0.35], ['physical', 0.55], ['special', 0.8], ['recoil', 0.1], ['faint', 0.5], ['faint', 1.9]],
  preview: {
    view: { yaw: 28, pitch: 14 },
    // animation grid: [animation, loops]
    cells: [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true],
      ['water_idle', true], ['water_swim', true], ['headache', false], ['cry', false],
      ['physical', false], ['special', false], ['recoil', false], ['faint', false]],
    grid: { cols: 4, tile: 200, radius: 19, center: [0, 11, 0] },
    still: { anim: 'ground_idle', time: 0.4, tile: 360 },
    // close-ups of the face: [label, animation, time]
    faces: [['open', null, 0], ['blink / sleep', 'blink', 0.1], ['cry (happy)', 'cry', 0.35], ['headache', 'headache', 1.0], ['faint (dizzy)', 'faint', 0.5]],
    face: { center: [0, 16, -6], radius: 11 },
    emissive: [],
    alpha: 2,
  },
};
