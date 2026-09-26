// node build.js [id ...] [--repo <root>]
// Builds each Pokemon (default: all in pokemon/) into out/<id>; with --repo also writes the
// Cobblemon resource-pack files and the .bbmodel into the repository.
'use strict';
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const repoAt = args.indexOf('--repo');
const repo = repoAt >= 0 ? path.resolve(args.splice(repoAt, 2)[1]) : null;
const ids = args.length ? args : fs.readdirSync(path.join(__dirname, 'pokemon')).sort();

for (const id of ids) {
  const P = require(`./pokemon/${id}`);
  const m = P.build();
  const outDir = path.join(__dirname, 'out', id);
  const { bb, geo, anim, textures } = m.build(outDir);
  fs.writeFileSync(path.join(outDir, `${id}.poser.json`), JSON.stringify(P.poserJson(), null, 2) + '\n');
  fs.writeFileSync(path.join(outDir, `${id}.resolver.json`), JSON.stringify(P.resolverJson(), null, 2) + '\n');
  console.log(`${id}: ${m.cubes.length} cubes, ${m.bones.length} bones, tex ${m.texW}x${m.texH}, uv usage ${(m.uvUsage * 100).toFixed(1)}%, ${m.animations.length} animations, ${textures.length} textures`);
  if (!repo) continue;
  const w = (rel, data) => {
    const p = path.join(repo, rel);
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, typeof data === 'string' || Buffer.isBuffer(data) ? data : JSON.stringify(data, null, 2) + '\n');
    return rel;
  };
  const F = P.FOLDER;
  const written = [
    w(`blockbench/${id}.bbmodel`, JSON.stringify(bb)),
    w(`assets/cobblemon/bedrock/pokemon/models/${F}/${id}.geo.json`, geo),
    w(`assets/cobblemon/bedrock/pokemon/animations/${F}/${id}.animation.json`, anim),
    w(`assets/cobblemon/bedrock/pokemon/posers/${F}/${id}.json`, P.poserJson()),
    w(`assets/cobblemon/bedrock/pokemon/resolvers/${F}/0_${id}_base.json`, P.resolverJson()),
    ...textures.map((t) => w(`assets/cobblemon/textures/pokemon/${F}/${t.name}`, t.png)),
  ];
  console.log(`  wrote ${written.length} files to ${repo}`);
}
