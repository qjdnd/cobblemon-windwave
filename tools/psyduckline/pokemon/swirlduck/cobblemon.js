// Cobblemon 1.8.1 client files for Swirlduck: poser (poses, quirks, portrait framing) and resolver (textures).
'use strict';
const ID = 'swirlduck';
const FOLDER = 'swirlduck';

// portrait (party slot) and profile (summary screen) framing, checked with portrait.js
const FRAMING = {
  portraitScale: 1.08, portraitTranslation: [0, 1.3, 0],
  profileScale: 0.55, profileTranslation: [0, 1.08, 0],
};
// Suggested species value (not written here: this pack only has the client files). The model is
// 37 units tall, so baseScale 0.85 makes it about 2 blocks tall, like Golduck (27 units x 1.2).
const SUGGESTED_BASE_SCALE = 0.85;

function poserJson() {
  const b = (anim) => `q.bedrock('${ID}', '${anim}')`;
  const look = "q.look('head', 1, 1, 12, -12, 30, -30)";
  const blink = `q.bedrock_quirk('${ID}', 'blink')`;
  // now and then it clutches its shell like Psyduck clutching its head, or rolls its eyes and laughs
  const quirks = `q.bedrock_quirk('${ID}', q.array('headache', 'laugh'), 20, 45, 1)`;
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
      standing: { poseTypes: ['STAND', 'NONE', 'PORTRAIT', 'PROFILE'], isBattle: false, animations: [look, b('ground_idle')], quirks: [blink, quirks] },
      walking: { poseTypes: ['WALK'], animations: [look, b('ground_walk')], quirks: [blink] },
      float: { poseTypes: ['FLOAT'], animations: [look, b('water_idle')], quirks: [blink] },
      swim: { poseTypes: ['SWIM'], animations: [look, b('water_swim')], quirks: [blink] },
      sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
    },
  };
}

function resolverJson() {
  const tex = (n) => `cobblemon:textures/pokemon/${FOLDER}/${n}.png`;
  // the gem glows (emissive layer, same setup as Cobblemon's Litwick)
  const glow = (n) => [{ name: 'emissive', texture: tex(n), emissive: true, translucent: true }];
  return {
    species: `cobblemon:${ID}`,
    order: 0,
    variations: [
      { aspects: [], poser: `cobblemon:${ID}`, model: `cobblemon:${ID}.geo`, texture: tex(ID), layers: glow(`${ID}_emissive`) },
      { aspects: ['shiny'], texture: tex(`${ID}_shiny`), layers: glow(`${ID}_emissive_shiny`) },
      { aspects: ['alpha_eyes'], layers: [{ name: 'alpha_eyes', texture: tex(`${ID}_alpha`), emissive: true }] },
    ],
  };
}

module.exports = { ID, FOLDER, SUGGESTED_BASE_SCALE, poserJson, resolverJson };
