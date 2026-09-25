// Headless preview renderer: node render.mjs job.json out_prefix
// Serves viewer.html + three.js + any local file under /files/<absolute path>
// and screenshots every shot of the job with Chromium (software WebGL).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';

const here = path.dirname(fileURLToPath(import.meta.url));
const require = createRequire(process.env.PREVIEW_NODE_MODULES ? path.join(process.env.PREVIEW_NODE_MODULES, 'x.js') : import.meta.url);
const { chromium } = require('playwright');
const threeDir = path.dirname(path.dirname(require.resolve('three')));

const [, , jobPath, outPrefix] = process.argv;
const job = JSON.parse(fs.readFileSync(jobPath, 'utf8'));

const types = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  let file;
  if (url === '/' || url === '/viewer.html') file = path.join(here, 'viewer.html');
  else if (url.startsWith('/three/')) file = path.join(threeDir, url.slice(7));
  else if (url.startsWith('/files/')) file = url.slice(6);
  if (!file || !fs.existsSync(file)) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Cache-Control': 'no-store' });
  fs.createReadStream(file).pipe(res);
});
await new Promise(r => server.listen(0, r));
const port = server.address().port;
const toUrl = p => (p ? `/files${path.resolve(p)}` : p);
job.geo = toUrl(job.geo);
job.texture = toUrl(job.texture);
job.animation = job.animation ? toUrl(job.animation) : undefined;
job.layers = (job.layers || []).map(toUrl);

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM_PATH || undefined,
  args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'],
});
const page = await browser.newPage({ viewport: { width: job.width || 800, height: job.height || 800 } });
page.on('console', m => { if (m.type() === 'error') console.error('[page]', m.text()); });
page.on('pageerror', e => console.error('[page]', e.message));
await page.goto(`http://127.0.0.1:${port}/viewer.html`);
await page.waitForFunction(() => window.ready === true);
const shots = await page.evaluate(j => window.render(j), job);
shots.forEach((d, i) => {
  const name = job.shots[i].name || String(i).padStart(4, '0');
  fs.writeFileSync(`${outPrefix}${name}.png`, Buffer.from(d.split(',')[1], 'base64'));
});
await browser.close();
server.close();
console.log(`rendered ${shots.length} shot(s)`);
