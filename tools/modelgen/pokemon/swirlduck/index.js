// Swirlduck: everything the build, verify and preview scripts need.
'use strict';
module.exports = {
  ...require('./cobblemon'),
  build: require('./model').build,
  // poses rendered by roundtrip.js ('-' = rest pose)
  verifyPoses: [['-', 0], ['ground_idle', 0.7], ['ground_walk', 0.3], ['water_swim', 0.3], ['battle_idle', 0.4], ['sleep', 1], ['blink', 0.1],
    ['headache', 1.0], ['laugh', 0.3], ['cry', 0.4], ['physical', 0.6], ['special', 1.45], ['recoil', 0.1], ['faint', 2.5]],
  preview: {
    view: { yaw: 28, pitch: 12 },
    cells: [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true],
      ['water_idle', true], ['water_swim', true], ['headache', false], ['laugh', false],
      ['cry', false], ['physical', false], ['special', false], ['faint', false]],
    grid: { cols: 4, tile: 220, radius: 27, center: [0, 17, 0] },
    still: { anim: 'ground_idle', time: 0.4, tile: 400 },
    faces: [['open (laughing)', null, 0], ['blink / sleep', 'blink', 0.1], ['cry (happy)', 'cry', 0.4], ['headache', 'headache', 1.0], ['faint (dizzy)', 'faint', 0.5]],
    face: { center: [0, 23, -6], radius: 12 },
    // texture indices of the glow layers: [normal, shiny], and the alpha layer
    emissive: [2, 3],
    alpha: 4,
  },
};
