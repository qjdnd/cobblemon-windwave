// node sheet.js <id> <out.png> [--tex=N] [--pitch=P] [--tile=T] [--cols=C] [--noground] [--emissive=i,j] yaw[:anim:time] ...
// Renders out/<id>/<id>.bbmodel from several angles (quick look while modelling).
'use strict';
const fs = require('fs');
const path = require('path');
const { render, close } = require('./render');
const args = process.argv.slice(2);
const id = args.shift();
const out = args.shift();
let texture = 0, pitch = 12, tile = 300, cols = 0, ground = true, emissive = [], center, radius;
const frames = [];
for (const a of args) {
  if (a.startsWith('--tex=')) { texture = +a.slice(6); continue; }
  if (a.startsWith('--pitch=')) { pitch = +a.slice(8); continue; }
  if (a.startsWith('--tile=')) { tile = +a.slice(7); continue; }
  if (a.startsWith('--cols=')) { cols = +a.slice(7); continue; }
  if (a.startsWith('--emissive=')) { emissive = a.slice(11).split(',').map(Number); continue; }
  if (a.startsWith('--center=')) { center = a.slice(9).split(',').map(Number); continue; }
  if (a.startsWith('--radius=')) { radius = +a.slice(9); continue; }
  if (a === '--noground') { ground = false; continue; }
  const [yaw, anim, time] = a.split(':');
  frames.push({ yaw: +yaw, pitch, anim: anim || null, time: time ? +time : 0 });
}
const bb = JSON.parse(fs.readFileSync(path.join(__dirname, 'out', id, `${id}.bbmodel`), 'utf8'));
render(bb, out, { frames, cols: cols || frames.length, tile, texture, ground, emissive, center, radius }).then(close);
