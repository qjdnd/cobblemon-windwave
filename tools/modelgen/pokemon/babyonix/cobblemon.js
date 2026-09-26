// Cobblemon 1.8.1 client files for Baby Onix: poser (poses, quirks, portrait framing) and resolver (textures).
'use strict';
const ID = 'babyonix';
const FOLDER = 'babyonix';

// portrait (party slot) and profile (summary screen) framing, checked with portrait.js
const FRAMING = {
  portraitScale: 1.1, portraitTranslation: [-0.15, 1.13, 0],
  profileScale: 0.7, profileTranslation: [0, 0.85, 0],
};
// Suggested species value (not written here: this pack only has the client files). The model is
// 30 units tall, so baseScale 0.5 makes it about 0.95 blocks tall.
const SUGGESTED_BASE_SCALE = 0.5;

function poserJson() {
  const b = (anim) => `q.bedrock('${ID}', '${anim}')`;
  const look = "q.look('head', 1, 1, 12, -12, 30, -30)";
  const blink = `q.bedrock_quirk('${ID}', 'blink')`;
  const quirks = `q.bedrock_quirk('${ID}', q.array('yawn', 'tail_wag'), 20, 45, 1)`;
  return {
    ...FRAMING,
    rootBone: ID,
    animations: {
      faint: `q.bedrock_primary('${ID}', 'faint', q.curve('one'))`,
      cry: `q.bedrock_stateful('${ID}', 'cry')`,
      recoil: `q.bedrock_stateful('${ID}', 'recoil')`,
      physical: `q.bedrock_primary('${ID}', 'physical', q.curve('symmetrical_wide'))`,
      special: `q.bedrock_primary('${ID}', 'special', q.curve('symmetrical_wide'))`,
    },
    poses: {
      'battle-standing': { poseTypes: ['STAND'], isBattle: true, animations: [look, b('battle_idle')], quirks: [blink] },
      // like Onix: it stays on the ground in water (STAND/FLOAT) and slithers along the bottom (WALK/SWIM)
      standing: { poseTypes: ['STAND', 'FLOAT', 'NONE', 'PORTRAIT', 'PROFILE'], isBattle: false, animations: [look, b('ground_idle')], quirks: [blink, quirks] },
      walking: { poseTypes: ['WALK', 'SWIM'], animations: [look, b('ground_walk')], quirks: [blink] },
      sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
    },
  };
}

function resolverJson() {
  const tex = (n) => `cobblemon:textures/pokemon/${FOLDER}/${n}.png`;
  return {
    species: `cobblemon:${ID}`,
    order: 0,
    variations: [
      { aspects: [], poser: `cobblemon:${ID}`, model: `cobblemon:${ID}.geo`, texture: tex(ID), layers: [] },
      { aspects: ['shiny'], texture: tex(`${ID}_shiny`) },
      { aspects: ['alpha_eyes'], layers: [{ name: 'alpha_eyes', texture: tex(`${ID}_alpha`), emissive: true }] },
    ],
  };
}

module.exports = { ID, FOLDER, SUGGESTED_BASE_SCALE, poserJson, resolverJson };
