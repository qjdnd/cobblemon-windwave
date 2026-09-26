// Re-imports the exported Bedrock files (geo.json + animation.json, Bedrock space) and renders them
// next to the Blockbench project for a set of poses; the two must match pixel for pixel.
'use strict';
const fs = require('fs');
const path = require('path');
const geo2bb = require('./geo2bb');
const { render, close } = require('./render');
const { PNG } = require('pngjs');

const ID = 'babypsyduck';
const POSES = [['-', 0], ['ground_idle', 0.7], ['ground_walk', 0.3], ['water_swim', 0.3], ['battle_idle', 0.4], ['sleep', 1], ['blink', 0.1],
  ['headache', 1.0], ['cry', 0.35], ['physical', 0.55], ['special', 0.8], ['recoil', 0.1], ['faint', 0.5], ['faint', 1.9]];

function anim2bb(animPath) {
  const d = JSON.parse(fs.readFileSync(animPath, 'utf8'));
  const inv = (v) => (typeof v === 'number' ? -v : `-(${v})`);
  const out = [];
  for (const [name, a] of Object.entries(d.animations)) {
    const animators = {};
    for (const [bone, chans] of Object.entries(a.bones || {})) {
      const kfs = [];
      for (const ch of ['rotation', 'position', 'scale']) {
        if (!chans[ch]) continue;
        const conv = (arr) => {
          arr = arr.slice();
          if (ch === 'rotation') { arr[0] = inv(arr[0]); arr[1] = inv(arr[1]); }
          if (ch === 'position') arr[0] = inv(arr[0]);
          return { x: arr[0], y: arr[1], z: arr[2] };
        };
        if (Array.isArray(chans[ch])) kfs.push({ channel: ch, time: 0, data_points: [conv(chans[ch])], interpolation: 'linear' });
        else for (const [t, v] of Object.entries(chans[ch])) {
          if (Array.isArray(v)) kfs.push({ channel: ch, time: +t, data_points: [conv(v)], interpolation: 'linear' });
          else if (v.pre && !v.lerp_mode) kfs.push({ channel: ch, time: +t, data_points: [conv(v.pre), conv(v.post)], interpolation: 'linear' });
          else kfs.push({ channel: ch, time: +t, data_points: [conv(v.post)], interpolation: v.lerp_mode || 'linear' });
        }
      }
      animators[bone] = { name: bone, keyframes: kfs };
    }
    out.push({ name, loop: a.loop === true ? 'loop' : 'once', length: a.animation_length || 0, animators });
  }
  return out;
}

(async () => {
  const dir = path.join(__dirname, 'out', ID);
  const bb = JSON.parse(fs.readFileSync(path.join(dir, `${ID}.bbmodel`), 'utf8'));
  const g = geo2bb(path.join(dir, `${ID}.geo.json`), [path.join(dir, `${ID}.png`)]);
  g.animations = anim2bb(path.join(dir, `${ID}.animation.json`));
  const frames = POSES.map(([n, t]) => ({ yaw: 30, pitch: 15, anim: n === '-' ? null : n, time: t }));
  const a = path.join(__dirname, 'out', 'rt_a.png'), b = path.join(__dirname, 'out', 'rt_b.png');
  await render(bb, a, { frames, cols: 7, tile: 240, ground: false });
  await render(g, b, { frames, cols: 7, tile: 240, ground: false });
  await close();
  const A = PNG.sync.read(fs.readFileSync(a)), B = PNG.sync.read(fs.readFileSync(b));
  let diff = 0;
  for (let i = 0; i < A.data.length; i += 4) if (Math.abs(A.data[i] - B.data[i]) + Math.abs(A.data[i + 1] - B.data[i + 1]) + Math.abs(A.data[i + 2] - B.data[i + 2]) > 24) diff++;
  console.log(`${ID}: ${POSES.length} poses, pixels differing: ${diff} of ${A.data.length / 4}`);
  if (diff > 0) process.exitCode = 1;
})();
