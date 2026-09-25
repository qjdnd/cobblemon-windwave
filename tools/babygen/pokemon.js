// Cobblemon (1.8.1) data for the three baby Pokemon: species, poser, resolver, dex, spawns, lang.
'use strict';

const EVOLVED_MOVES = require('./evolved_moves.json'); // egg / tm / tutor / legacy / special lists of the evolved forms

const q = (id) => (s) => s.replace(/\$/g, id);

const POKEMON = [
  {
    id: 'babymeowth', dex: 2001, evolvesTo: 'meowth', evolvedFolder: '0052_meowth',
    name: { en: 'Baby Meowth', ko: '아기나옹' },
    desc: {
      en: 'It naps the day away curled up like a loaf of bread. The coin on its forehead and the ones floating above it are said to be the first coins it ever found.',
      ko: '식빵처럼 몸을 웅크린 채 하루 종일 낮잠을 잔다. 이마의 금화와 머리 위를 떠다니는 금화는 처음으로 주운 동전이라고 전해진다.',
    },
    species: {
      primaryType: 'normal', maleRatio: 0.5, height: 2, weight: 15,
      abilities: ['pickup', 'technician', 'h:unnerve'],
      baseStats: { hp: 30, attack: 30, defence: 25, special_attack: 30, special_defence: 30, speed: 65 },
      evYield: { hp: 0, attack: 0, defence: 0, special_attack: 0, special_defence: 0, speed: 1 },
      baseExperienceYield: 38, experienceGroup: 'medium_fast', catchRate: 190, eggCycles: 10, baseFriendship: 70,
      baseScale: 0.36, hitbox: { width: 0.6, height: 0.4, fixed: false },
      levelMoves: ['1:scratch', '1:growl', '4:fakeout', '8:payday', '12:charm', '16:covet', '20:bite'],
      behaviour: {
        resting: { canSleep: true, willSleepOnBed: true, light: '0-4', times: ['day'], drowsyChance: 0.0033, rouseChance: 0.0042 },
        moving: { swim: { avoidsWater: true } },
        combat: { willDefendOwner: true },
        entityInteract: { avoidedByCreeper: true, avoidedByPhantom: true },
        herd: { maxSize: 4, toleratedLeaders: [{ pokemon: 'babymeowth', tier: 1 }, { pokemon: 'meowth galarian=false', tier: 2 }, { pokemon: 'persian galarian=false', tier: 3 }] },
      },
      drops: { amount: 2, entries: [{ item: 'minecraft:gold_nugget', quantityRange: '0-1' }, { item: 'cobblemon:pinap_berry', percentage: 2.5 }] },
    },
    poser: {
      look: "q.look('head', 1, 1, 10, -10, 25, -25)",
      portraitScale: 1.25, portraitTranslation: [-0.62, -0.36, 0],
      profileScale: 0.62, profileTranslation: [0, 0.78, 0],
      shoulderX: 7.8,
    },
    spawns: [
      { id: 1, bucket: 'uncommon', level: '1-15', weight: 6.0, presets: ['natural', 'urban'], condition: { minSkyLight: 8, maxSkyLight: 15, biomes: ['#cobblemon:is_overworld'], isRaining: false }, anticondition: { biomes: ['#cobblemon:is_arid', '#cobblemon:is_freezing', '#cobblemon:is_taiga'] } },
      { id: 2, bucket: 'uncommon', level: '1-15', weight: 12.0, presets: ['natural'], condition: { minSkyLight: 8, maxSkyLight: 15, biomes: ['#cobblemon:is_overworld'], structures: ['#minecraft:village'] } },
    ],
  },
  {
    id: 'babyzubat', dex: 2002, evolvesTo: 'zubat', evolvedFolder: '0041_zubat',
    name: { en: 'Baby Zubat', ko: '아기주뱃' },
    desc: {
      en: 'Before its body grows, it is nothing but one huge eye and a pair of wings. It cannot bear bright light, so it keeps its eye shut and wrapped in its wings during the day.',
      ko: '몸이 자라기 전에는 커다란 눈 하나와 날개뿐이다. 밝은 빛을 견디지 못해 낮에는 날개로 눈을 감싸고 지낸다.',
    },
    species: {
      primaryType: 'poison', secondaryType: 'flying', maleRatio: 0.5, height: 3, weight: 20,
      abilities: ['innerfocus', 'h:infiltrator'],
      baseStats: { hp: 30, attack: 35, defence: 25, special_attack: 25, special_defence: 30, speed: 60 },
      evYield: { hp: 0, attack: 0, defence: 0, special_attack: 0, special_defence: 0, speed: 1 },
      baseExperienceYield: 36, experienceGroup: 'medium_fast', catchRate: 190, eggCycles: 10, baseFriendship: 70,
      baseScale: 0.36, hitbox: { width: 0.6, height: 0.55, fixed: false },
      levelMoves: ['1:absorb', '1:supersonic', '4:astonish', '8:meanlook', '12:leechlife', '16:confuseray', '20:wingattack'],
      behaviour: {
        moving: { fly: { canFly: true }, swim: { avoidsWater: true }, walk: { canWalk: false } },
        resting: { canSleep: true, willSleepOnBed: true, light: '0-4', times: ['any'], drowsyChance: 0.0014, rouseChance: 0.0042 },
        combat: { willDefendOwner: true },
        herd: { maxSize: 6, toleratedLeaders: [{ pokemon: 'babyzubat', tier: 1 }, { pokemon: 'zubat', tier: 2 }, { pokemon: 'golbat', tier: 3 }, { pokemon: 'crobat', tier: 4 }] },
      },
      drops: { amount: 2, entries: [{ item: 'minecraft:phantom_membrane', percentage: 2.5 }, { item: 'cobblemon:persim_berry', percentage: 2.5 }] },
    },
    poser: {
      look: "q.look('body')",
      pitchTilt: true,
      portraitScale: 1.25, portraitTranslation: [-0.14, 0.34, 0],
      profileScale: 0.56, profileTranslation: [0, 0.78, 0],
      shoulderX: 7.8,
    },
    spawns: [
      { id: 1, bucket: 'uncommon', level: '1-15', weight: 4.0, presets: ['natural'], condition: { minSkyLight: 0, maxSkyLight: 7, biomes: ['#cobblemon:is_overworld'] }, anticondition: { biomes: ['#cobblemon:is_deep_dark'] } },
      { id: 2, bucket: 'uncommon', level: '1-15', weight: 6.0, presets: ['natural'], condition: { canSeeSky: false, biomes: ['#cobblemon:is_overworld'] }, anticondition: { biomes: ['#cobblemon:is_deep_dark'] } },
      { id: 3, bucket: 'uncommon', level: '1-15', weight: 4.0, presets: ['natural'], condition: { minSkyLight: 8, maxSkyLight: 15, biomes: ['#cobblemon:is_forest', '#cobblemon:is_swamp'], timeRange: 'night', isRaining: false } },
    ],
  },
  {
    id: 'babylitwick', dex: 2003, evolvesTo: 'litwick', evolvedFolder: '0607_litwick',
    name: { en: 'Baby Litwick', ko: '아기불켜미' },
    desc: {
      en: 'A wisp of ghostly fire that has not yet found a candle to live in. It drifts after warm lights at night, and its flame flares up whenever it is happy.',
      ko: '아직 머물 양초를 찾지 못한 도깨비불이다. 밤이면 따뜻한 불빛을 따라 떠다니며, 기분이 좋으면 머리의 불꽃이 확 타오른다.',
    },
    species: {
      primaryType: 'ghost', secondaryType: 'fire', maleRatio: 0.5, height: 2, weight: 12,
      abilities: ['flashfire', 'flamebody', 'h:infiltrator'],
      baseStats: { hp: 35, attack: 20, defence: 40, special_attack: 50, special_defence: 40, speed: 15 },
      evYield: { hp: 0, attack: 0, defence: 0, special_attack: 1, special_defence: 0, speed: 0 },
      baseExperienceYield: 40, experienceGroup: 'medium_slow', catchRate: 190, eggCycles: 10, baseFriendship: 70,
      baseScale: 0.28, hitbox: { width: 0.6, height: 0.55, fixed: false },
      standingEyeHeight: 0.2, swimmingEyeHeight: 0.2, flyingEyeHeight: 0.2,
      levelMoves: ['1:astonish', '1:smog', '4:ember', '8:minimize', '12:confuseray', '16:hex', '20:flameburst'],
      behaviour: {
        resting: { canSleep: true, willSleepOnBed: true, light: '12-15', times: ['day'], drowsyChance: 0.0033, rouseChance: 0.0042 },
        moving: { swim: { avoidsWater: true, canSwimInLava: true } },
        combat: { willDefendOwner: true },
        fireImmune: true,
        herd: { maxSize: 3, toleratedLeaders: [{ pokemon: 'babylitwick', tier: 1 }, { pokemon: 'litwick', tier: 2 }, { pokemon: 'lampent', tier: 3 }, { pokemon: 'chandelure', tier: 4 }] },
      },
      lightingData: { lightLevel: 8, liquidGlowMode: 'LAND' },
      drops: { amount: 2, entries: [{ item: 'minecraft:candle', quantityRange: '0-1' }, { item: 'cobblemon:rawst_berry', percentage: 2.5 }] },
    },
    poser: {
      look: "q.look('body', 1, 1, 8, -8, 20, -20)",
      portraitScale: 1.05, portraitTranslation: [-0.16, -0.02, 0],
      profileScale: 0.5, profileTranslation: [0, 0.92, 0],
      shoulderX: 10,
    },
    emissive: true,
    spawns: [
      { id: 1, bucket: 'uncommon', level: '1-15', weight: 10.0, presets: ['mansion'], condition: { canSeeSky: false, biomes: ['#cobblemon:is_overworld'], timeRange: 'night' } },
      { id: 2, bucket: 'uncommon', level: '1-15', weight: 3.0, presets: ['natural'], condition: { biomes: ['#cobblemon:nether/is_soul_fire'] } },
      { id: 3, bucket: 'rare', level: '1-15', weight: 1.5, presets: ['natural'], condition: { maxSkyLight: 7, minSkyLight: 0, biomes: ['#cobblemon:is_spooky'], timeRange: 'night' } },
    ],
  },
];

// ------------------------------------------------------------------ builders
function speciesJson(p) {
  const s = p.species;
  const ev = EVOLVED_MOVES[p.evolvesTo];
  const out = {
    implemented: true,
    nationalPokedexNumber: p.dex,
    name: p.name.en,
    primaryType: s.primaryType,
  };
  if (s.secondaryType) out.secondaryType = s.secondaryType;
  Object.assign(out, {
    maleRatio: s.maleRatio, height: s.height, weight: s.weight,
    pokedex: [`cobblemon.species.${p.id}.desc`],
    labels: ['custom', 'baby', 'windwave'],
    aspects: [],
    abilities: s.abilities,
    eggGroups: ['undiscovered'],
    baseStats: s.baseStats,
    evYield: s.evYield,
    baseExperienceYield: s.baseExperienceYield,
    experienceGroup: s.experienceGroup,
    catchRate: s.catchRate,
    eggCycles: s.eggCycles,
    baseFriendship: s.baseFriendship,
    shoulderMountable: true,
  });
  for (const k of ['standingEyeHeight', 'swimmingEyeHeight', 'flyingEyeHeight']) if (s[k] !== undefined) out[k] = s[k];
  Object.assign(out, {
    baseScale: s.baseScale,
    hitbox: s.hitbox,
    behaviour: s.behaviour,
    drops: s.drops,
    moves: [...s.levelMoves, ...ev],
    evolutions: [{
      id: `${p.id}_${p.evolvesTo}`, variant: 'level_up', result: p.evolvesTo, consumeHeldItem: false, learnableMoves: [],
      requirements: [{ variant: 'friendship', amount: 160 }],
    }],
  });
  if (s.lightingData) out.lightingData = s.lightingData;
  return out;
}

function poserJson(p) {
  const id = p.id, P = p.poser;
  const b = (anim) => `q.bedrock('${id}', '${anim}')`;
  const look = P.look;
  const blink = `q.bedrock_quirk('${id}', 'blink')`;
  const shoulder = (side) => ({
    poseTypes: [side === 'left' ? 'SHOULDER_LEFT' : 'SHOULDER_RIGHT'],
    animations: [look, id === 'babyzubat' ? b('shoulder_' + side) : (id === 'babylitwick' ? b('shoulder_' + side) : b('ground_idle'))],
    quirks: id === 'babymeowth' ? [] : [blink],
    // same world-space offset Cobblemon uses for Pichu (hitbox width 0.6), expressed in this model's units
    transformedParts: [{ part: 'body', position: [side === 'left' ? -P.shoulderX : P.shoulderX, 0, 0] }],
  });
  const common = {
    portraitScale: P.portraitScale, portraitTranslation: P.portraitTranslation,
    profileScale: P.profileScale, profileTranslation: P.profileTranslation,
    rootBone: id,
  };
  if (id === 'babymeowth') {
    return {
      ...common,
      animations: {
        faint: `q.bedrock_primary('${id}', 'faint', q.curve('one'))`,
        cry: `q.bedrock_stateful('${id}', 'cry')`,
        recoil: `q.bedrock_stateful('${id}', 'recoil')`,
        physical: `q.bedrock_primary('${id}', 'physical', q.curve('symmetrical_wide'))`,
        special: `q.bedrock_primary('${id}', 'special', q.curve('symmetrical_wide'))`,
      },
      poses: {
        'battle-standing': { poseTypes: ['STAND'], isBattle: true, animations: [look, b('battle_idle')], quirks: [blink] },
        // eyes are closed and content by default; now and then it opens them and peeks around
        standing: { poseTypes: ['STAND', 'NONE', 'PORTRAIT', 'PROFILE', 'FLOAT'], isBattle: false, animations: [look, b('ground_idle')], quirks: [`q.bedrock_quirk('${id}', 'look_quirk', 15, 40, 1)`] },
        walking: { poseTypes: ['WALK', 'SWIM'], animations: [look, b('ground_walk')], quirks: [blink] },
        sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
        shoulder_left: shoulder('left'),
        shoulder_right: shoulder('right'),
      },
    };
  }
  if (id === 'babyzubat') {
    const tilt = "q.pitch_tilt('body')";
    return {
      ...common,
      animations: {
        faint: `q.bedrock_primary('${id}', 'faint', q.curve('one'))`,
        cry: `q.bedrock_stateful('${id}', 'cry')`,
        recoil: `q.bedrock_stateful('${id}', 'recoil')`,
        physical: `q.bedrock_primary('${id}', 'physical', q.curve('symmetrical'))`,
        special: `q.bedrock_primary('${id}', 'special', q.curve('symmetrical_wide'))`,
      },
      poses: {
        'battle-standing': { poseTypes: ['STAND', 'HOVER'], isBattle: true, animations: [look, b('battle_idle')], quirks: [blink] },
        standing: { poseTypes: ['STAND', 'NONE', 'PORTRAIT', 'PROFILE'], isBattle: false, animations: [look, b('ground_idle')], quirks: [blink, `q.bedrock_quirk('${id}', 'look_quirk', 20, 45, 1)`] },
        hover: { poseTypes: ['HOVER', 'FLOAT'], isBattle: false, animations: [tilt, look, b('air_idle')], quirks: [blink, `q.bedrock_quirk('${id}', 'look_quirk', 20, 45, 1)`] },
        walking: { poseTypes: ['WALK'], animations: [b('ground_walk')], quirks: [blink] },
        fly: { poseTypes: ['FLY', 'SWIM'], animations: [tilt, b('air_fly')], quirks: [blink] },
        sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
        shoulder_left: shoulder('left'),
        shoulder_right: shoulder('right'),
      },
    };
  }
  // babylitwick
  return {
    ...common,
    animations: {
      faint: `q.bedrock_primary('${id}', 'faint', q.curve('one'))`,
      cry: `q.bedrock_stateful('${id}', 'cry')`,
      recoil: `q.bedrock_stateful('${id}', 'recoil')`,
      physical: `q.bedrock_primary('${id}', 'physical', q.curve('symmetrical_wide'))`,
      special: `q.bedrock_primary('${id}', 'special', q.curve('symmetrical_wide'))`,
    },
    poses: {
      'battle-standing': { poseTypes: ['STAND'], isBattle: true, animations: [look, b('battle_idle')], quirks: [blink] },
      standing: { poseTypes: ['STAND', 'FLOAT', 'HOVER', 'NONE', 'PORTRAIT', 'PROFILE'], isBattle: false, animations: [look, b('ground_idle')], quirks: [blink] },
      walking: { poseTypes: ['WALK', 'SWIM', 'FLY'], animations: [look, b('ground_walk')], quirks: [blink] },
      sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
      shoulder_left: shoulder('left'),
      shoulder_right: shoulder('right'),
    },
  };
}

function resolverJson(p) {
  const tex = (n) => `cobblemon:textures/pokemon/${p.dex}_${p.id}/${n}.png`;
  const base = { aspects: [], poser: `cobblemon:${p.id}`, model: `cobblemon:${p.id}.geo`, texture: tex(p.id), layers: [] };
  const shiny = { aspects: ['shiny'], texture: tex(`${p.id}_shiny`) };
  if (p.emissive) {
    base.layers = [{ name: 'emissive', texture: tex(`${p.id}_emissive`), emissive: true, translucent: true }];
    shiny.layers = [{ name: 'emissive', texture: tex(`${p.id}_emissive_shiny`), emissive: true, translucent: true }];
  }
  const alpha = { aspects: ['alpha_eyes'], layers: [{ name: 'alpha_eyes', texture: tex(`${p.id}_alpha`), emissive: true }] };
  return { species: `cobblemon:${p.id}`, order: 0, variations: [base, shiny, alpha] };
}

function spawnJson(p) {
  return {
    enabled: true,
    neededInstalledMods: [],
    neededUninstalledMods: [],
    spawns: p.spawns.map((s) => {
      const o = {
        id: `${p.id}-${s.id}`, pokemon: p.id, presets: s.presets, type: 'pokemon', spawnablePositionType: 'grounded',
        bucket: s.bucket, level: s.level, weight: s.weight,
      };
      o.condition = s.condition;
      if (s.anticondition) o.anticondition = s.anticondition;
      return o;
    }),
  };
}

function dexEntryJson(p) {
  return {
    id: `cobblemon:${p.id}`, speciesId: `cobblemon:${p.id}`, displayAspects: [], conditionAspects: [],
    forms: [{ displayForm: 'Normal', unlockForms: ['Normal'] }], variations: [],
  };
}

module.exports = { POKEMON, speciesJson, poserJson, resolverJson, spawnJson, dexEntryJson };
