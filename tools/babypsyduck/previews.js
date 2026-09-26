// Renders the preview frames used by previews.py (docs/babypsyduck):
//   out/gif/f###.png   animation grid, one PNG per GIF frame
//   out/prev_*.png     variants, turnaround, expressions
'use strict';
const fs = require('fs');
const path = require('path');
const { render, close } = require('./render');

const ID = 'babypsyduck';
const CELLS = [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true],
  ['water_idle', true], ['water_swim', true], ['headache', false], ['cry', false],
  ['physical', false], ['special', false], ['recoil', false], ['faint', false]];
const COLS = 4, TILE = 200, CYCLE = 4.0, FPS = 12.5;
const out = (f) => path.join(__dirname, 'out', f);

(async () => {
  const bb = JSON.parse(fs.readFileSync(out(`${ID}/${ID}.bbmodel`), 'utf8'));
  const lengths = Object.fromEntries(bb.animations.map((a) => [a.name.split('.').pop(), a.length]));
  // static images
  const v = { yaw: 28, pitch: 14, anim: 'ground_idle', time: 0.4 };
  await render(bb, out('prev_normal.png'), { frames: [v], cols: 1, tile: 360, ground: false, bg: 0x2b2d3a });
  await render(bb, out('prev_shiny.png'), { frames: [v], cols: 1, tile: 360, texture: 1, ground: false, bg: 0x2b2d3a });
  // alpha: glowing eyes layer drawn over the base texture, in a dark scene so the glow reads
  await render(bb, out('prev_alpha.png'), { frames: [v], cols: 1, tile: 360, emissive: [2], ambient: 0.35, diffuse: 0.35, ground: false, bg: 0x16171f });
  await render(bb, out('prev_views.png'), { frames: [0, 45, 90, 135, 180, 270].map((yaw) => ({ yaw, pitch: 12 })), cols: 6, tile: 240, ground: false, bg: 0x2b2d3a });
  await render(bb, out('prev_views_shiny.png'), { frames: [0, 45, 90, 135, 180, 270].map((yaw) => ({ yaw, pitch: 12 })), cols: 6, tile: 240, texture: 1, ground: false, bg: 0x2b2d3a });
  const face = (anim, time) => ({ yaw: 10, pitch: 4, anim, time });
  await render(bb, out('prev_expr.png'), {
    frames: [face(null, 0), face('blink', 0.1), face('cry', 0.35), face('headache', 1.0), face('faint', 0.5)],
    cols: 5, tile: 240, ground: false, bg: 0x2b2d3a, center: [0, 16, -6], radius: 11,
  });
  // animation grid frames
  fs.mkdirSync(out('gif'), { recursive: true });
  const n = Math.round(CYCLE * FPS);
  for (let k = 0; k < n; k++) {
    const t = k / FPS;
    const frames = CELLS.map(([anim, loop]) => {
      const len = lengths[anim];
      // one-shots play once, hold the last pose, then restart with the loop
      return { yaw: 28, pitch: 14, anim, time: loop ? t : Math.min(t, len) };
    });
    await render(bb, out(`gif/f${String(k).padStart(3, '0')}.png`), { frames, cols: COLS, tile: TILE, radius: 19, center: [0, 11, 0] });
  }
  fs.writeFileSync(out('gif/labels.json'), JSON.stringify(CELLS.map((c) => c[0])));
  await close();
})();
