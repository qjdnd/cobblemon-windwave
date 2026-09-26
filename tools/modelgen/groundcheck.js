// node groundcheck.js [id ...]
// Prints the lowest point (model units, ground = 0) of every animation sampled over its length,
// to catch poses that sink into the ground or float above it.
'use strict';
const fs = require('fs');
const path = require('path');
const { bounds, close } = require('./render');
(async () => {
  const ids = process.argv.slice(2).length ? process.argv.slice(2) : fs.readdirSync(path.join(__dirname, 'pokemon')).sort();
  for (const id of ids) {
    const bb = JSON.parse(fs.readFileSync(path.join(__dirname, 'out', id, `${id}.bbmodel`), 'utf8'));
    const poses = [[null, 0]];
    for (const a of bb.animations) {
      const n = a.name.split('.').pop();
      const len = a.length || 2;
      for (let i = 0; i <= 8; i++) poses.push([n, +(len * i / 8).toFixed(3)]);
    }
    const res = await bounds(bb, poses);
    const byAnim = {};
    poses.forEach(([n, t], i) => { const k = n || 'rest'; (byAnim[k] = byAnim[k] || []).push(`${t}:${res[i].min[1].toFixed(2)}`); });
    console.log(`== ${id}`);
    for (const [k, v] of Object.entries(byAnim)) console.log(k.padEnd(12), v.join('  '));
  }
  await close();
})();
