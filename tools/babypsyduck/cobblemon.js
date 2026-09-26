// Cobblemon 1.8.1 client files for Baby Psyduck: poser (poses, quirks, portrait framing) and resolver (textures).
'use strict';
const ID = 'babypsyduck';
const FOLDER = 'babypsyduck';

// portrait (party slot) and profile (summary screen) framing, checked with portrait.js
const FRAMING = {
  portraitScale: 1.23, portraitTranslation: [0, 0.59, 0],
  profileScale: 0.7, profileTranslation: [0, 0.77, 0],
};
// Suggested species values (not written here: this pack only has the client files). The model is
// 26 units (1.6 blocks) tall, so baseScale 0.32 makes it about half as tall as Psyduck (baseScale 0.8).
const SUGGESTED_BASE_SCALE = 0.32;
// shoulder offset in model units: the same world offset (0.1755 blocks) as the other Wind Wave babies
const SHOULDER_X = +(0.1755 * 16 / SUGGESTED_BASE_SCALE).toFixed(1);

function poserJson() {
  const b = (anim) => `q.bedrock('${ID}', '${anim}')`;
  const look = "q.look('head', 1, 1, 10, -10, 25, -25)";
  const blink = `q.bedrock_quirk('${ID}', 'blink')`;
  // now and then it clutches its head like Psyduck does
  const headache = `q.bedrock_quirk('${ID}', 'headache', 20, 50, 1)`;
  const shoulder = (side) => ({
    poseTypes: [side === 'left' ? 'SHOULDER_LEFT' : 'SHOULDER_RIGHT'],
    animations: [look, b('ground_idle')],
    quirks: [blink],
    transformedParts: [{ part: 'body', position: [side === 'left' ? -SHOULDER_X : SHOULDER_X, 0, 0] }],
  });
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
      standing: { poseTypes: ['STAND', 'NONE', 'PORTRAIT', 'PROFILE'], isBattle: false, animations: [look, b('ground_idle')], quirks: [blink, headache] },
      walking: { poseTypes: ['WALK'], animations: [look, b('ground_walk')], quirks: [blink] },
      float: { poseTypes: ['FLOAT'], animations: [look, b('water_idle')], quirks: [blink] },
      swim: { poseTypes: ['SWIM'], animations: [look, b('water_swim')], quirks: [blink] },
      sleep: { poseTypes: ['SLEEP'], namedAnimations: { cry: "q.bedrock_stateful('dummy', 'cry')" }, animations: [b('sleep')] },
      shoulder_left: shoulder('left'),
      shoulder_right: shoulder('right'),
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
