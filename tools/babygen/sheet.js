// node sheet.js <bbmodel> <out.png> <yaw> <pitch> anim1:t0,t1,.. anim2:... [--emissive=1] [--center=x,y,z]
const { render, close } = require('./render');
const args = process.argv.slice(2);
const [inp, out, yaw, pitch, ...rest] = args;
const frames = []; let emissive = []; let center; let cols = 6; let zoom = 1; let texture = 0;
for (const r of rest) {
  if (r.startsWith('--emissive=')) { emissive = r.slice(11).split(',').map(Number); continue; }
  if (r.startsWith('--center=')) { center = r.slice(9).split(',').map(Number); continue; }
  if (r.startsWith('--cols=')) { cols = +r.slice(7); continue; }
  if (r.startsWith('--zoom=')) { zoom = +r.slice(7); continue; }
  if (r.startsWith('--tex=')) { texture = +r.slice(6); continue; }
  const [anim, ts] = r.split(':');
  for (const t of ts.split(',')) frames.push({ yaw: +yaw, pitch: +pitch, anim: anim === '-' ? null : anim, time: +t, zoom });
}
render(inp, out, { frames, cols, tile: 300, emissive, center, texture }).then(close);
