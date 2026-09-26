// node previews.js [id ...]
// Renders the preview frames used by previews.py (docs/<id>):
//   out/<id>_gif/f###.png   animation grid, one PNG per GIF frame
//   out/<id>_prev_*.png     variants, turnaround, expressions
'use strict';
const fs = require('fs');
const path = require('path');
const { render, close } = require('./render');

const CYCLE = 4.0, FPS = 12.5;
const out = (f) => path.join(__dirname, 'out', f);

(async () => {
  const ids = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(path.join(__dirname, 'pokemon')).sort();
  for (const id of ids) {
    const V = require(`./pokemon/${id}`).preview;
    const bb = JSON.parse(fs.readFileSync(out(`${id}/${id}.bbmodel`), 'utf8'));
    const lengths = Object.fromEntries(bb.animations.map((a) => [a.name.split('.').pop(), a.length]));
    const em = V.emissive || [];
    const bg = 0x2b2d3a;
    // static images
    const v = { ...V.view, anim: V.still.anim, time: V.still.time };
    const t = V.still.tile;
    await render(bb, out(`${id}_prev_normal.png`), { frames: [v], cols: 1, tile: t, ground: false, bg, emissive: em.slice(0, 1) });
    await render(bb, out(`${id}_prev_shiny.png`), { frames: [v], cols: 1, tile: t, texture: 1, ground: false, bg, emissive: em.slice(1, 2) });
    // alpha: glowing eyes layer over the base texture, in a dark scene so the glow reads
    await render(bb, out(`${id}_prev_alpha.png`), { frames: [v], cols: 1, tile: t, emissive: [V.alpha, ...em.slice(0, 1)], ambient: 0.35, diffuse: 0.35, ground: false, bg: 0x16171f });
    const views = [0, 45, 90, 135, 180, 270].map((yaw) => ({ yaw, pitch: 12 }));
    await render(bb, out(`${id}_prev_views.png`), { frames: views, cols: 6, tile: 240, ground: false, bg, emissive: em.slice(0, 1) });
    await render(bb, out(`${id}_prev_views_shiny.png`), { frames: views, cols: 6, tile: 240, texture: 1, ground: false, bg, emissive: em.slice(1, 2) });
    await render(bb, out(`${id}_prev_expr.png`), {
      frames: V.faces.map(([, anim, time]) => ({ yaw: 10, pitch: 4, anim, time })),
      cols: V.faces.length, tile: 240, ground: false, bg, center: V.face.center, radius: V.face.radius, emissive: em.slice(0, 1),
    });
    // animation grid frames
    fs.rmSync(out(`${id}_gif`), { recursive: true, force: true });
    fs.mkdirSync(out(`${id}_gif`), { recursive: true });
    const n = Math.round(CYCLE * FPS);
    for (let k = 0; k < n; k++) {
      const time = k / FPS;
      // one-shots play once, hold the last pose, then restart with the loop
      const frames = V.cells.map(([anim, loop]) => ({ ...V.view, anim, time: loop ? time : Math.min(time, lengths[anim]) }));
      await render(bb, out(`${id}_gif/f${String(k).padStart(3, '0')}.png`), { frames, cols: V.grid.cols, tile: V.grid.tile, radius: V.grid.radius, center: V.grid.center, emissive: em.slice(0, 1) });
    }
    fs.writeFileSync(out(`${id}_gif/meta.json`), JSON.stringify({ labels: V.cells.map((c) => c[0]), cols: V.grid.cols, tile: V.grid.tile, faces: V.faces.map((f) => f[0]) }));
    console.log(`${id}: previews rendered`);
  }
  await close();
})();
