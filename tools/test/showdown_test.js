/*
 * Battle-tests the Windwave datapack scripts inside Cobblemon's bundled Showdown.
 * Usage: node tools/test/showdown_test.js <path-to-unzipped-cobblemon-showdown> <datapack-dir>
 * (showdown.zip lives in the Cobblemon jar at data/cobblemon/showdown.zip)
 */
const fs = require('fs');
const path = require('path');
const sd = path.resolve(process.argv[2]);
const dp = path.resolve(process.argv[3]);
const { Cobblemon } = require(path.join(sd, 'sim/cobblemon/cobblemon'));
const { Dex, toID } = require(path.join(sd, 'sim/dex'));
const BS = require(path.join(sd, 'sim/battle-stream'));

// Exactly what GraalShowdownService.sendRegistryData + index.js receiveData do.
function sendRegistryData(map, type) {
  const payload = '{' + Object.entries(map).map(([k, v]) => `"${k}": ${v.replace(/[\r\n]+/g, ' ')}`).join(', ') + '}';
  const registry = Cobblemon.getRegistry(type);
  let obj;
  try { obj = JSON.parse(payload); } catch { obj = eval(`(${payload})`); }
  for (const [key, value] of Object.entries(obj)) registry.register(value, toID(key));
  registry.invalidate();
}
function scripts(dir) {
  const out = {};
  for (const f of fs.readdirSync(dir)) if (f.endsWith('.js')) out[path.basename(f, '.js')] = fs.readFileSync(path.join(dir, f), 'utf8');
  return out;
}
sendRegistryData(scripts(path.join(dp, 'data/cobblemon/abilities')), 'ability');
sendRegistryData(scripts(path.join(dp, 'data/cobblemon/moves')), 'move');

// Species, shaped like PokemonSpecies.ShowdownSpecies
function showdownSpecies(name, types, stats, extra = {}) {
  return JSON.stringify(Object.assign({ num: 0, name, baseSpecies: name, abilities: { 0: 'No Ability', 1: 'No Ability', H: 'No Ability', S: 'No Ability' },
    types, baseStats: stats, heightm: 1, weightkg: 30, eggGroups: ['Field'], evos: [], nfe: false }, extra));
}
const species = {};
for (const id of ['eevee', 'vaporeon', 'jolteon', 'flareon', 'espeon', 'snorlax', 'skarmory', 'grimer', 'ferrothorn', 'gyarados']) {
  const s = Dex.species.get(id);
  species[id] = showdownSpecies(s.name, s.types, s.baseStats);
}
// The Windwave species, read straight from the data pack (same fields Cobblemon sends).
const cap = (t) => t.charAt(0).toUpperCase() + t.slice(1);
const speciesDir = path.join(dp, 'data/cobblemon/species/windwave');
for (const f of fs.readdirSync(speciesDir)) {
  const s = JSON.parse(fs.readFileSync(path.join(speciesDir, f), 'utf8'));
  const b = s.baseStats;
  const types = [s.primaryType, s.secondaryType].filter(Boolean).map(cap);
  species[path.basename(f, '.json')] = showdownSpecies(s.name, types,
    { hp: b.hp, atk: b.attack, def: b.defence, spa: b.special_attack, spd: b.special_defence, spe: b.speed },
    { num: s.nationalPokedexNumber, weightkg: s.weight / 10 });
}
Cobblemon.getRegistry('species').reset();
sendRegistryData(species, 'species');
Dex.modsLoaded = false;
Dex.includeMods();

const format = { mod: 'cobblemon', gameType: 'SINGLES', gen: 9, ruleset: ['Obtainable', '+Past', '+Unobtainable'], effectType: 'Format' };
let uuidCounter = 0;
function mon(species, ability, moves, item = '', level = 60) {
  // Cobblemon packed format: NAME|SPECIES|UUID|HP|STATUS|STATUSDURATION|ITEM|ABILITY|MOVES|MOVEPP|NATURE|EVS|GENDER|IVS|SHINY|LEVEL|MISC
  const pp = moves.map(() => '10/10').join(',');
  return `${species}||00000000-0000-0000-0000-${String(++uuidCounter).padStart(12, '0')}|||-1|${item}|${ability}|${moves.join(',')}|${pp}|hardy|0,0,0,0,0,0|M|31,31,31,31,31,31||${level}|255,pokeball,,,,Normal`;
}
async function battle(name, t1, t2, turns) {
  const stream = new BS.BattleStream({ debug: true });
  const log = [];
  const reader = (async () => { for await (const chunk of stream) log.push(chunk); })();
  stream.write(`>start {"format": ${JSON.stringify(format)}, "seed": [1,2,3,4]}`);
  stream.write(`>player p1 {"name":"A","team":"${t1.join(']')}"}`);
  stream.write(`>player p2 {"name":"B","team":"${t2.join(']')}"}`);
  for (const [a, b] of turns) { stream.write(`>p1 ${a}`); stream.write(`>p2 ${b}`); }
  await new Promise(r => setTimeout(r, 300));
  stream.writeEnd();
  await reader;
  const text = log.join('\n');
  const lines = text.split('\n').filter(l => /\|(move|-damage|-hitcount|-status|-clearboost|-sideend|-activate|-immune|-boost|-sidestart|error|debug|-fail|switch|cant|-crit|-curestatus)\|/.test(l) || l.startsWith('|error') || l.includes('trapped'));
  console.log(`\n===== ${name}`);
  console.log(lines.filter(l => !l.startsWith('|debug|') || l.includes('Windwave') || l.includes('Last Evolution') || l.includes('BP')).slice(0, 60).join('\n'));
  return text;
}
(async () => {
  let t;
  t = await battle('Last Evolution (2 kin in party)',
    [mon('eeveeon', 'adaptability', ['lastevolution']), mon('vaporeon', 'waterabsorb', ['tackle']), mon('jolteon', 'voltabsorb', ['tackle'])],
    [mon('snorlax', 'thickfat', ['splash'])], [['move 1', 'move 1']]);
  if (!/Last Evolution BP: 120/.test(t)) throw new Error('Last Evolution BP mismatch');

  t = await battle('Triple Freeze Beam',
    [mon('threiscue', 'icebody', ['triplefreezebeam'])], [mon('snorlax', 'thickfat', ['splash'])], [['move 1', 'move 1']]);
  if (!/-hitcount\|p2a: [^|]*\|3/.test(t)) throw new Error('Triple Freeze Beam did not hit 3 times');

  t = await battle('Grave Uprising traps',
    [mon('cryptonix', 'cursedbody', ['graveuprising'])], [mon('snorlax', 'thickfat', ['splash']), mon('skarmory', 'sturdy', ['splash'])],
    [['move 1', 'move 1'], ['move 1', 'switch 2']]);
  if (!/"trapped":true/.test(t)) throw new Error('Grave Uprising did not trap');

  t = await battle('Frostsaw clears Stealth Rock',
    [mon('avalott', 'sharpness', ['frostsaw'])], [mon('skarmory', 'sturdy', ['stealthrock', 'splash'])],
    [['move 1', 'move 1'], ['switch 1', 'move 2']].slice(0, 1).concat([['move 1', 'move 2']]));
  if (!/-sideend\|p1: A\|Stealth Rock\|\[from\] move: Frostsaw/.test(t)) throw new Error('Frostsaw did not clear hazards');

  t = await battle('Cleansing Net clears boosts',
    [mon('cleaweed', 'purify', ['cleansingnet'])], [mon('gyarados', 'intimidate', ['dragondance'])],
    [['move 1', 'move 1']]);
  if (!/-clearboost\|p2a: /.test(t)) throw new Error('Cleansing Net did not clear boosts');

  t = await battle('Purify: Poison moves become Water (hits Steel) + poison immunity',
    [mon('cleaweed', 'purify', ['sludgebomb'])], [mon('grimer', 'stench', ['toxic'])],
    [['move 1', 'move 1']]);
  if (!/-immune\|p1a: [^|]*\|\[from\] ability: Purify/.test(t)) throw new Error('Purify did not block poison');
  t = await battle('Purify vs Steel type',
    [mon('cleaweed', 'purify', ['sludgebomb'])], [mon('ferrothorn', 'ironbarbs', ['splash'])],
    [['move 1', 'move 1']]);
  if (/-immune\|p2a/.test(t) || !/-damage\|p2a/.test(t)) throw new Error('Purify did not turn Sludge Bomb into a Water move');
  t = await battle('Control: no Purify vs Steel type',
    [mon('cleaweed', 'adaptability', ['sludgebomb'])], [mon('ferrothorn', 'ironbarbs', ['splash'])],
    [['move 1', 'move 1']]);
  if (!/-immune\|p2a/.test(t)) throw new Error('control failed: Sludge Bomb should not affect Steel');
  console.log('\nALL SHOWDOWN TESTS PASSED');
})().catch(e => { console.error('TEST FAILURE:', e.message); process.exit(1); });
