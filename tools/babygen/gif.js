// Renders an animation-grid preview (frames as PNG sheets) for a model.
//   node gif.js <id> <outDir>
'use strict';
const fs = require('fs');
const path = require('path');
const { render, close } = require('./render');

const PLANS = {
  babymeowth: { yaw: 28, pitch: 16, cells: [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true], ['cry', false], ['physical', false], ['special', false], ['look_quirk', false], ['faint', false]] },
  babyzubat: { yaw: 22, pitch: 10, cells: [['air_idle', true], ['air_fly', true], ['battle_idle', true], ['sleep', true], ['cry', false], ['physical', false], ['special', false], ['look_quirk', false], ['faint', false]] },
  babylitwick: { yaw: 25, pitch: 10, cells: [['ground_idle', true], ['ground_walk', true], ['battle_idle', true], ['sleep', true], ['cry', false], ['physical', false], ['special', false], ['recoil', false], ['faint', false]], emissive: [2] },
};
const CYCLE = 4.0, FPS = 12.5;

(async () => {
  const [, , id, outDir] = process.argv;
  const plan = PLANS[id];
  const bb = JSON.parse(fs.readFileSync(path.join(__dirname, 'out', id, `${id}.bbmodel`), 'utf8'));
  fs.mkdirSync(outDir, { recursive: true });
  const n = Math.round(CYCLE * FPS);
  for (let k = 0; k < n; k++) {
    const t = k / FPS;
    const frames = plan.cells.map(([anim, loop]) => {
      const a = bb.animations.find((x) => x.name.endsWith('.' + anim));
      let time = t;
      if (!loop) time = Math.min(t, a.length); // one-shots play once then hold
      return { yaw: plan.yaw, pitch: plan.pitch, anim, time };
    });
    await render(bb, path.join(outDir, `f${String(k).padStart(3, '0')}.png`), { frames, cols: 3, tile: 240, emissive: plan.emissive || [], radius: plan.radius });
  }
  await close();
  fs.writeFileSync(path.join(outDir, 'labels.json'), JSON.stringify(plan.cells.map((c) => c[0])));
})();
