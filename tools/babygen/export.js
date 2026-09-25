// Builds every model and writes the complete Cobblemon 1.8.1 add-on (resource + data pack)
// plus the Blockbench project files into <repoRoot>.
//   node export.js <repoRoot>
'use strict';
const fs = require('fs');
const path = require('path');
const { POKEMON, speciesJson, poserJson, resolverJson, spawnJson, dexEntryJson } = require('./pokemon');

const root = path.resolve(process.argv[2] || path.join(__dirname, '..', '..'));
const w = (rel, data) => {
  const p = path.join(root, rel);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, typeof data === 'string' || Buffer.isBuffer(data) ? data : JSON.stringify(data, null, 2) + '\n');
  return rel;
};

const written = [];
const lang = { en_us: {}, ko_kr: {} };
for (const p of POKEMON) {
  const m = require(`./models/${p.id}`).build();
  const { bb, geo, anim, textures } = m.build(null);
  const folder = `${p.dex}_${p.id}`;
  written.push(w(`blockbench/${p.id}.bbmodel`, JSON.stringify(bb)));
  written.push(w(`assets/cobblemon/bedrock/pokemon/models/${folder}/${p.id}.geo.json`, geo));
  written.push(w(`assets/cobblemon/bedrock/pokemon/animations/${folder}/${p.id}.animation.json`, anim));
  written.push(w(`assets/cobblemon/bedrock/pokemon/posers/${folder}/${p.id}.json`, poserJson(p)));
  written.push(w(`assets/cobblemon/bedrock/pokemon/resolvers/${folder}/0_${p.id}_base.json`, resolverJson(p)));
  for (const t of textures) written.push(w(`assets/cobblemon/textures/pokemon/${folder}/${t.name}`, t.png));
  written.push(w(`data/cobblemon/species/custom/${p.id}.json`, speciesJson(p)));
  written.push(w(`data/cobblemon/species_additions/${p.evolvesTo}_${p.id}.json`, { target: `cobblemon:${p.evolvesTo}`, preEvolution: p.id }));
  written.push(w(`data/cobblemon/spawn_pool_world/${folder}.json`, spawnJson(p)));
  written.push(w(`data/cobblemon/dex_entries/pokemon/custom/${p.id}.json`, dexEntryJson(p)));
  lang.en_us[`cobblemon.species.${p.id}.name`] = p.name.en;
  lang.en_us[`cobblemon.species.${p.id}.desc`] = p.desc.en;
  lang.ko_kr[`cobblemon.species.${p.id}.name`] = p.name.ko;
  lang.ko_kr[`cobblemon.species.${p.id}.desc`] = p.desc.ko;
  console.log(`${p.id}: ${m.cubes.length} cubes, ${m.bones.length} bones, ${m.animations.length} animations, ${textures.length} textures (${m.texW}x${m.texH})`);
}
written.push(w('assets/cobblemon/lang/en_us.json', lang.en_us));
written.push(w('assets/cobblemon/lang/ko_kr.json', lang.ko_kr));
written.push(w('data/cobblemon/dexes/windwave.json', {
  type: 'cobblemon:simple_pokedex_def', id: 'cobblemon:windwave', sortOrder: 20, entries: POKEMON.map((p) => `cobblemon:${p.id}`),
}));
written.push(w('data/cobblemon/dex_additions/windwave_national.json', { dexId: 'cobblemon:national', entries: ['cobblemon:windwave'] }));
written.push(w('pack.mcmeta', {
  pack: {
    pack_format: 48,
    supported_formats: [34, 48],
    description: 'Cobblemon Wind Wave - baby Meowth, Zubat & Litwick',
  },
}));
console.log(`wrote ${written.length} files to ${root}`);
