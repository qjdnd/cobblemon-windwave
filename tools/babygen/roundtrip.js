// Re-import exported geo.json + animation.json (bedrock space) and render them next to the bbmodel.
const fs = require('fs');
const geo2bb = require('./geo2bb');
const { render, close } = require('./render');
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
  const [, , id, ...anims] = process.argv;
  const dir = `out/${id}`;
  const bb = JSON.parse(fs.readFileSync(`${dir}/${id}.bbmodel`, 'utf8'));
  const g = geo2bb(`${dir}/${id}.geo.json`, [`${dir}/${id}.png`]);
  g.animations = anim2bb(`${dir}/${id}.animation.json`);
  const frames = [];
  for (const a of anims) { const [n, t] = a.split(':'); frames.push({ yaw: 30, pitch: 15, anim: n === '-' ? null : n, time: +t }); }
  await render(bb, `out/rt_${id}_a.png`, { frames, cols: frames.length, tile: 240, ground: false });
  await render(g, `out/rt_${id}_b.png`, { frames, cols: frames.length, tile: 240, ground: false });
  await close();
  const { PNG } = require('pngjs');
  const A = PNG.sync.read(fs.readFileSync(`out/rt_${id}_a.png`)), B = PNG.sync.read(fs.readFileSync(`out/rt_${id}_b.png`));
  let diff = 0; for (let i = 0; i < A.data.length; i += 4) if (Math.abs(A.data[i] - B.data[i]) + Math.abs(A.data[i + 1] - B.data[i + 1]) + Math.abs(A.data[i + 2] - B.data[i + 2]) > 24) diff++;
  console.log(id, 'pixels differing:', diff, 'of', A.data.length / 4);
})();
