// node build.js            -> builds into out/babypsyduck (bbmodel, geo, animation, textures, poser, resolver)
// node build.js <repoRoot> -> also writes the Cobblemon resource-pack files and the .bbmodel into the repo
'use strict';
const fs = require('fs');
const path = require('path');
const { build } = require('./model');
const { ID, FOLDER, poserJson, resolverJson } = require('./cobblemon');

const m = build();
const outDir = path.join(__dirname, 'out', ID);
const { bb, geo, anim, textures } = m.build(outDir);
fs.writeFileSync(path.join(outDir, `${ID}.poser.json`), JSON.stringify(poserJson(), null, 2) + '\n');
fs.writeFileSync(path.join(outDir, `${ID}.resolver.json`), JSON.stringify(resolverJson(), null, 2) + '\n');
console.log(`${ID}: ${m.cubes.length} cubes, ${m.bones.length} bones, tex ${m.texW}x${m.texH}, uv usage ${(m.uvUsage * 100).toFixed(1)}%, ${m.animations.length} animations, ${textures.length} textures`);

const repo = process.argv[2];
if (repo) {
  const root = path.resolve(repo);
  const w = (rel, data) => {
    const p = path.join(root, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, typeof data === 'string' || Buffer.isBuffer(data) ? data : JSON.stringify(data, null, 2) + '\n');
    return rel;
  };
  const written = [
    w(`blockbench/${ID}.bbmodel`, JSON.stringify(bb)),
    w(`assets/cobblemon/bedrock/pokemon/models/${FOLDER}/${ID}.geo.json`, geo),
    w(`assets/cobblemon/bedrock/pokemon/animations/${FOLDER}/${ID}.animation.json`, anim),
    w(`assets/cobblemon/bedrock/pokemon/posers/${FOLDER}/${ID}.json`, poserJson()),
    w(`assets/cobblemon/bedrock/pokemon/resolvers/${FOLDER}/0_${ID}_base.json`, resolverJson()),
    ...textures.map((t) => w(`assets/cobblemon/textures/pokemon/${FOLDER}/${t.name}`, t.png)),
  ];
  console.log(`wrote ${written.length} files to ${root}:\n  ` + written.join('\n  '));
}
