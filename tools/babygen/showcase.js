const fs = require('fs');
const { render, close } = require('./render');
(async () => {
  const specs = [
    ['babymeowth', { yaw: 25, pitch: 14, anim: 'ground_idle', time: 0.4 }, [0, 1], [], []],
    ['babyzubat', { yaw: 18, pitch: 8, anim: 'air_idle', time: 0.18 }, [0, 1], [], []],
    ['babylitwick', { yaw: 22, pitch: 8, anim: 'ground_idle', time: 0.6 }, [0, 1], [2], [3]],
    ['frillgator', { yaw: -24, pitch: 10, anim: 'ground_idle', time: 0.4, zoom: 0.9 }, [0, 1], [], []],
  ];
  for (const [id, f, texs, em, emS] of specs) {
    const bb = JSON.parse(fs.readFileSync(`out/${id}/${id}.bbmodel`, 'utf8'));
    await render(bb, `out/sc_${id}_n.png`, { frames: [f], cols: 1, tile: 420, emissive: em, ground: false, bg: 0x2b2d3a });
    await render(bb, `out/sc_${id}_s.png`, { frames: [f], cols: 1, tile: 420, texture: 1, emissive: emS, ground: false, bg: 0x2b2d3a });
  }
  await close();
})();
