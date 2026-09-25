// Load the generated Bedrock assets into a locally built Blockbench web app
// (headless Chromium), let Blockbench itself compile the .bbmodel project and
// take screenshots of Blockbench's own viewport as a cross-check.
//
//   BLOCKBENCH_DIR=/path/to/blockbench (built with `npm run build-web`)
//   PREVIEW_NODE_MODULES=/path/to/node_modules (with playwright)
//   node blockbench_export.mjs <geo.json> <anim.json> <out.bbmodel> <screenshot_prefix> tex1.png [tex2.png ...]
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(path.join(process.env.PREVIEW_NODE_MODULES, 'x.js'));
const { chromium } = require('playwright');
const BB = process.env.BLOCKBENCH_DIR;
const [, , geoPath, animPath, outPath, shotPrefix, ...texPaths] = process.argv;

const types = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff', '.ttf': 'font/ttf' };
const server = http.createServer((req, res) => {
  let url = decodeURIComponent(req.url.split('?')[0]);
  if (url === '/') url = '/index.html';
  const file = path.join(BB, url);
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});
await new Promise(r => server.listen(0, r));

const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 1000 } });
page.on('pageerror', e => console.error('[blockbench]', e.message));
await page.goto(`http://127.0.0.1:${server.address().port}/index.html`);
await page.waitForFunction(() => typeof Codecs !== 'undefined' && Codecs.bedrock && typeof AnimationCodec !== 'undefined', null, { timeout: 60000 });
await page.waitForTimeout(1500);

const data = {
  geo: JSON.parse(fs.readFileSync(geoPath, 'utf8')),
  anim: fs.readFileSync(animPath, 'utf8'),
  textures: texPaths.map(p => ({ name: path.basename(p), url: 'data:image/png;base64,' + fs.readFileSync(p).toString('base64') })),
  name: path.basename(outPath, '.bbmodel'),
};

page.on('console', m => { if (process.env.BB_DEBUG) console.error('[bb console]', m.text()); });
const step = async (label, fn, arg) => { const t0 = Date.now(); const r = await page.evaluate(fn, arg); if (process.env.BB_DEBUG) console.error('step', label, Date.now() - t0, 'ms'); return r; };
await step('geo', (d) => { Codecs.bedrock.load(d.geo, { path: `models/entity/${d.name}.geo.json`, no_file: true }); }, data);
await step('tex', async (d) => {
  for (const t of d.textures) {
    const tex = new Texture({ name: t.name }).fromDataURL(t.url).add(false);
    for (let i = 0; i < 100 && !(tex.img && tex.img.complete && tex.img.naturalWidth); i++) await new Promise(r => setTimeout(r, 50));
  }
}, data);
const result = await page.evaluate(async (d) => {
  Texture.all[0].setAsDefaultTexture?.();
  Canvas.updateAllFaces?.();
  AnimationCodec.codecs.bedrock.loadFile({ path: `${d.name}.animation.json`, content: d.anim });
  Project.name = d.name;
  Project.geometry_name = d.name;
  Project.model_identifier = d.name;
  const out = Codecs.project.compile({ bitmaps: true, absolute_paths: false, raw: true });
  return {
    project: out,
    stats: { groups: Group.all.length, cubes: Cube.all.length, locators: Locator.all.length,
             textures: Texture.all.length, animations: Animation.all.map(a => a.name) },
  };
}, data);

fs.writeFileSync(outPath, JSON.stringify(result.project));
console.log(JSON.stringify(result.stats));

// screenshots from Blockbench's own renderer
if (shotPrefix && shotPrefix.length) {
  const shoot = async (name, yaw, pitch, anim, time) => {
    await page.evaluate(({ yaw, pitch, anim, time }) => {
      const preview = Preview.selected;
      if (anim) {
        Modes.options.animate.select();
        const a = Animation.all.find(x => x.name === anim);
        a.select();
        Timeline.setTime(time);
        Animator.preview();
      } else if (!Modes.edit) {
        Modes.options.edit.select();
      }
      const r = 150, y = yaw * Math.PI / 180, p = pitch * Math.PI / 180;
      // Blockbench space: the model faces -Z like in bedrock
      preview.camera.position.set(Math.sin(y) * Math.cos(p) * r, 26 + Math.sin(p) * r, -Math.cos(y) * Math.cos(p) * r);
      preview.controls.target.set(0, 26, 0);
      preview.controls.update();
      preview.render();
    }, { yaw, pitch, anim, time });
    await page.waitForTimeout(400);
    const canvas = await page.$('#preview canvas, .preview canvas');
    await (canvas || page).screenshot({ path: `${shotPrefix}${name}.png` });
  };
  // Blockbench mirrors bedrock X: the Pokemon's left side is at -X in its viewport
  await shoot('bb_left', 90, 5);
  await shoot('bb_threequarter', 55, 12);
  await shoot('bb_walk', 55, 12, `animation.${data.name}.ground_walk`, 0.5);
}

// round trip: make sure Blockbench can load its own project again
const reload = await page.evaluate((p) => {
  Codecs.project.load(p, { path: 'roundtrip.bbmodel', no_file: true });
  return { cubes: Cube.all.length, groups: Group.all.length, animations: Animation.all.length };
}, result.project);
console.log('reload', JSON.stringify(reload));

await browser.close();
server.close();
