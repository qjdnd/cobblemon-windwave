// node build.js <modelName> [outDir]
const path = require('path');
const name = process.argv[2];
const out = process.argv[3] || path.join(__dirname, 'out', name);
const mod = require('./models/' + name);
const m = mod.build();
const res = m.build(out);
console.log(`${name}: ${m.cubes.length} cubes, ${m.bones.length} bones, tex ${m.texW}x${m.texH}, uv usage ${(m.uvUsage * 100).toFixed(1)}%, anims ${m.animations.length}`);
