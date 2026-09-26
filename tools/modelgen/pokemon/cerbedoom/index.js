// Cerbedoom: everything the build, verify and preview scripts need.
'use strict';
module.exports = {
  ...require('./cobblemon'),
  build: require('./model').build,
  // poses rendered by roundtrip.js ('-' = rest pose)
  verifyPoses: [['-', 0], ['ground_idle', 0.7], ['ground_walk', 0.3], ['battle_idle', 0.4], ['sleep', 1], ['blink', 0.1], ['squabble', 1.45],
    ['howl', 1.0], ['cry', 0.5], ['physical', 0.62], ['special', 0.9], ['recoil', 0.1], ['faint', 0.75], ['faint', 2.5]],
  preview: {
    view: { yaw: 35, pitch: 14 },
    cells: [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true],
      ['squabble', false], ['howl', false], ['cry', false], ['physical', false],
      ['special', false], ['recoil', false], ['faint', false]],
    grid: { cols: 4, tile: 240, radius: 34, center: [0, 22, 6] },
    still: { anim: 'ground_idle', time: 0.4, tile: 440 },
    faces: [['awake', null, 0], ['blink / sleep', 'blink', 0.1], ['squabble', 'squabble', 1.45], ['fire breath', 'special', 0.9], ['howl', 'howl', 1.2]],
    face: { center: [0, 38, -12], radius: 16, yaw: 12 },
    emissive: [2, 3],
    alpha: 4,
  },
};
