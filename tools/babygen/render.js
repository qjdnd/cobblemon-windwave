// Node driver: node render.js <model.bbmodel> <out.png> '<json opts>'
// opts: {frames:[{yaw,pitch,anim,time}], cols, tile, texture, emissive:[idx], bg}
const path = require('path');
const fs = require('fs');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) { ({ chromium } = require('/opt/node22/lib/node_modules/playwright')); }

const HERE = __dirname;
const HTML = `<!doctype html><html><head><style>body{margin:0;background:#222}</style>
<script type="importmap">{"imports":{"three":"http://local/node_modules/three/build/three.module.js"}}</script>
<script type="module" src="http://local/viewer.js"></script></head><body></body></html>`;

let browserP = null;
async function getBrowser() {
  // CHROMIUM_PATH lets you point at an already installed Chromium instead of running `npx playwright install`
  if (!browserP) browserP = chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined, args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  return browserP;
}

async function render(modelOrPath, out, opts) {
  const model = typeof modelOrPath === 'string' ? JSON.parse(fs.readFileSync(modelOrPath, 'utf8')) : modelOrPath;
  const browser = await getBrowser();
  const page = await browser.newPage();
  page.on('console', (m) => { if (m.type() === 'error') console.error('[page]', m.text()); });
  page.on('pageerror', (e) => console.error('[pageerror]', e.message));
  await page.route('http://local/**', async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname === '/' || url.pathname === '/index.html') return route.fulfill({ body: HTML, contentType: 'text/html' });
    const p = path.join(HERE, decodeURIComponent(url.pathname));
    route.fulfill({ body: fs.readFileSync(p), contentType: p.endsWith('.js') ? 'text/javascript' : 'application/octet-stream' });
  });
  await page.goto('http://local/');
  await page.waitForFunction(() => window.ready === true);
  const dataUrl = await page.evaluate(([m, o]) => window.renderSheet(m, o), [model, opts]);
  fs.writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'));
  await page.close();
}

module.exports = { render, close: async () => { if (browserP) (await browserP).close(); browserP = null; } };

if (require.main === module) {
  const [, , inp, out, o] = process.argv;
  const opts = o ? JSON.parse(o) : { frames: [{ yaw: 0 }, { yaw: 45 }, { yaw: 90 }, { yaw: 180 }] };
  render(inp, out, opts).then(() => module.exports.close()).catch((e) => { console.error(e); process.exit(1); });
}
