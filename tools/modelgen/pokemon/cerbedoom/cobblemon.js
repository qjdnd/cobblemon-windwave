// Cobblemon 1.8.1 client files for Cerbedoom: poser (poses, quirks, portrait framing) and resolver (textures).
'use strict';
const ID = 'cerbedoom';
const FOLDER = 'cerbedoom';

// portrait (party slot) and profile (summary screen) framing, checked with portrait.js
const FRAMING = {
  portraitScale: 0.92, portraitTranslation: [-0.35, 1.85, 0],
  profileScale: 0.46, profileTranslation: [0, 1.25, 0],
};
// Suggested species value (not written here: this pack only has the client files). The model is
// 48 units tall to the horn tips, so baseScale 0.8 makes it about 2.4 blocks tall, a size up from
// Houndoom (baseScale 0.7).
const SUGGESTED_BASE_SCALE = 0.8;

function poserJson() {
  const b = (anim) => `q.bedrock('${ID}', '${anim}')`;
  // the leader (middle head) follows the player; the side heads keep looking around on their own
  const look = "q.look('head', 1, 1, 12, -12, 30, -30)";
  const blink = `q.bedrock_quirk('${ID}', 'blink')`;
  const quirks = `q.bedrock_quirk('${ID}', q.array('squabble', 'howl'), 20, 50, 1)`;
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
      // like Houndoom: it stands in water (FLOAT) and walks through it (SWIM)
      standing: { poseTypes: ['STAND', 'NONE', 'FLOAT', 'PORTRAIT', 'PROFILE'], isBattle: false, animations: [look, b('ground_idle')], quirks: [blink, quirks] },
      walking: { poseTypes: ['WALK', 'SWIM'], animations: [look, b('ground_walk')], quirks: [blink] },
      sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
    },
  };
}

function resolverJson() {
  const tex = (n) => `cobblemon:textures/pokemon/${FOLDER}/${n}.png`;
  // eyes, mouths, the skull's sockets and the tail's arrowhead glow (emissive layer, set up like Cobblemon's Litwick)
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
