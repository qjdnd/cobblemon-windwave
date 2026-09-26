// Baby Onix: everything the build, verify and preview scripts need.
'use strict';
module.exports = {
  ...require('./cobblemon'),
  build: require('./model').build,
  // poses rendered by roundtrip.js ('-' = rest pose)
  verifyPoses: [['-', 0], ['ground_idle', 0.7], ['ground_walk', 0.3], ['battle_idle', 0.4], ['sleep', 1], ['blink', 0.1], ['yawn', 1.2],
    ['tail_wag', 1.0], ['cry', 0.5], ['physical', 0.7], ['special', 0.8], ['recoil', 0.1], ['faint', 0.5], ['faint', 2.5]],
  preview: {
    view: { yaw: 40, pitch: 14 },
    cells: [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true],
      ['yawn', false], ['tail_wag', false], ['cry', false], ['physical', false],
      ['special', false], ['recoil', false], ['faint', false]],
    grid: { cols: 4, tile: 220, radius: 21, center: [-2, 13, 3] },
    still: { anim: 'ground_idle', time: 0.4, tile: 400 },
    // close-ups of the left eye (it sits on the side of the head; at positive yaw the camera is on its left)
    faces: [['open (glancing back)', null, 0], ['blink / sleep', 'blink', 0.1], ['battle (glare)', 'battle_idle', 0.4], ['faint (dizzy)', 'faint', 0.5]],
    face: { center: [-4, 24, 1], radius: 7, yaw: 75 },
    emissive: [],
    alpha: 2,
  },
};
