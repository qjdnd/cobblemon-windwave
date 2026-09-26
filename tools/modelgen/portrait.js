// Emulates Cobblemon's party portrait (drawPosablePortrait) and summary profile framing.
// node portrait.js <bbmodel|geo:...> <poser.json> <portraitAnim> <out.png>
const fs = require('fs');
const { render, close } = require('./render');
const geo2bb = require('./geo2bb');
function frames(poser, anim, time = 0) {
  const ps = poser.portraitScale, [tx, ty] = poser.portraitTranslation;
  // PartyOverlay translates to (slotY - 12), then drawPosablePortrait adds 21 + 2 and -(21/18) * 13
  const R = -12 + 23 - (21 / 18) * 13 + 13 * (ty + 1.5 * ps);   // GUI y (down) of the model origin, relative to the 21px circle top
  const pxPerUnit = 13 * ps / 16;
  const centerY = (R - 10.5) / pxPerUnit;                       // model units above the origin shown at the circle centre
  const half = 10.5 / pxPerUnit;
    // yaw -32 / +tx matches how the game frames official quadrupeds (checked against Glameow & Growlithe)
  const f1 = { yaw: -32, pitch: 5, anim, time, ortho: { center: [tx * 16 / ps, centerY, 0], half } };
  // profile/summary: model feet at S*(ty+1.5ps) (S = gui scale); show a window 1.2S tall centred at 1.25S
  const qs = poser.profileScale, [, qy] = poser.profileTranslation;
  const feet = qy + 1.5 * qs;                                   // in S units, down from the anchor
  const c2 = (feet - 1.25) / qs * 16;                           // model units above origin shown at the window centre
  const f2 = { yaw: -32, pitch: 5, anim, time, ortho: { center: [0, c2, 0], half: 0.75 / qs * 16 } };
  return [f1, f2];
}
module.exports = { frames };
if (require.main === module) {
  const [, , model, poserPath, anim, out] = process.argv;
  const poser = JSON.parse(fs.readFileSync(poserPath, 'utf8'));
  let m;
  if (model.startsWith('geo:')) { const [g, png] = model.slice(4).split(','); m = geo2bb(g, [png]); }
  else m = JSON.parse(fs.readFileSync(model, 'utf8'));
  render(m, out, { frames: frames(poser, anim === '-' ? null : anim), cols: 2, tile: 240, ground: false }).then(close);
}
