// Browser-side bbmodel viewer. Reproduces Blockbench's cube geometry, box-UV
// corner mapping, group hierarchy (Euler ZYX) and bone animation application.
import * as THREE from 'three';

const DEG = Math.PI / 180;

// ---------- Molang (subset) -> JS ----------
const M = {
  sin: (d) => Math.sin(d * DEG), cos: (d) => Math.cos(d * DEG),
  abs: Math.abs, sqrt: Math.sqrt, pow: Math.pow, floor: Math.floor, ceil: Math.ceil,
  round: Math.round, min: Math.min, max: Math.max, exp: Math.exp, ln: Math.log,
  clamp: (v, a, b) => Math.min(Math.max(v, a), b), lerp: (a, b, t) => a + (b - a) * t,
  mod: (a, b) => a % b, pi: Math.PI, trunc: Math.trunc,
  asin: (v) => Math.asin(v) / DEG, acos: (v) => Math.acos(v) / DEG, atan: (v) => Math.atan(v) / DEG,
  atan2: (y, x) => Math.atan2(y, x) / DEG,
  hermite_blend: (t) => 3 * t * t - 2 * t * t * t,
  lerprotate: (a, b, t) => a + (b - a) * t,
};
const molangCache = new Map();
function molang(expr, t) {
  if (typeof expr === 'number') return expr;
  if (expr === undefined || expr === null || expr === '') return 0;
  let fn = molangCache.get(expr);
  if (!fn) {
    let src = String(expr).toLowerCase()
      .replace(/\bquery\./g, 'q.').replace(/\bq\.anim_time\b/g, 't').replace(/\bq\.life_time\b/g, 't')
      .replace(/\bmath\.pi\b/g, 'M.pi').replace(/\bmath\.(\w+)/g, 'M.$1');
    fn = new Function('t', 'M', 'return (' + src + ');');
    molangCache.set(expr, fn);
  }
  const v = fn(t, M);
  return Number.isFinite(v) ? v : 0;
}

// ---------- Model building ----------
function buildModel(model, textures) {
  const texW = model.resolution.width, texH = model.resolution.height;
  const groupsByUuid = Object.fromEntries((model.groups || []).map((g) => [g.uuid, g]));
  const elsByUuid = Object.fromEntries(model.elements.map((e) => [e.uuid, e]));
  const root = new THREE.Group();
  const bones = {}; // name -> {obj, group}
  const baseMats = textures.map((tex) => new THREE.MeshLambertMaterial({ map: tex, alphaTest: 0.1, side: THREE.DoubleSide }));

  function makeCubeMesh(e, mats) {
    const from = e.from.slice(), to = e.to.slice();
    const inf = e.inflate || 0;
    for (let i = 0; i < 3; i++) { from[i] -= inf + e.origin[i]; to[i] += inf - e.origin[i]; if (from[i] === to[i]) to[i] += 0.001; }
    const [fx, fy, fz] = from, [tx, ty, tz] = to;
    const pos = [
      tx, ty, tz, tx, ty, fz, tx, fy, tz, tx, fy, fz, // east
      fx, ty, fz, fx, ty, tz, fx, fy, fz, fx, fy, tz, // west
      fx, ty, fz, tx, ty, fz, fx, ty, tz, tx, ty, tz, // up
      fx, fy, tz, tx, fy, tz, fx, fy, fz, tx, fy, fz, // down
      fx, ty, tz, tx, ty, tz, fx, fy, tz, tx, fy, tz, // south
      tx, ty, fz, fx, ty, fz, tx, fy, fz, fx, fy, fz, // north
    ];
    const order = ['east', 'west', 'up', 'down', 'south', 'north'];
    const uvs = [], idx = [], normals = [];
    const nrm = { east: [1, 0, 0], west: [-1, 0, 0], up: [0, 1, 0], down: [0, -1, 0], south: [0, 0, 1], north: [0, 0, -1] };
    order.forEach((f, i) => {
      const face = e.faces[f];
      let uv = face && face.texture !== null && face.texture !== undefined ? face.uv.slice() : null;
      if (!uv) { uvs.push(0, 0, 0, 0, 0, 0, 0, 0); }
      else {
        for (let si = 0; si < 2; si++) { let m = 1 / 64; if (uv[si] > uv[si + 2]) m = -m; uv[si] += m; uv[si + 2] -= m; }
        uvs.push(uv[0] / texW, 1 - uv[1] / texH, uv[2] / texW, 1 - uv[1] / texH, uv[0] / texW, 1 - uv[3] / texH, uv[2] / texW, 1 - uv[3] / texH);
        const b = i * 4; idx.push(b, b + 2, b + 1, b + 2, b + 3, b + 1);
      }
      for (let k = 0; k < 4; k++) normals.push(...nrm[f]);
    });
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
    geo.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    geo.setIndex(idx);
    const group = new THREE.Group();
    for (const mat of mats) {
      const mesh = new THREE.Mesh(geo, mat);
      group.add(mesh);
    }
    group.rotation.order = 'ZYX';
    group.rotation.set((e.rotation?.[0] || 0) * DEG, (e.rotation?.[1] || 0) * DEG, (e.rotation?.[2] || 0) * DEG);
    return group;
  }

  function walk(node, parentObj, parentOrigin) {
    if (typeof node === 'string') {
      const e = elsByUuid[node];
      if (!e || e.type === 'locator' || e.type === 'null_object') return;
      if (e.visibility === false) return;
      const mesh = makeCubeMesh(e, baseMats);
      mesh.position.set(e.origin[0] - parentOrigin[0], e.origin[1] - parentOrigin[1], e.origin[2] - parentOrigin[2]);
      parentObj.add(mesh);
      return;
    }
    const g = groupsByUuid[node.uuid] || node;
    const obj = new THREE.Group();
    obj.name = g.name;
    obj.rotation.order = 'ZYX';
    obj.position.set(g.origin[0] - parentOrigin[0], g.origin[1] - parentOrigin[1], g.origin[2] - parentOrigin[2]);
    obj.rotation.set((g.rotation?.[0] || 0) * DEG, (g.rotation?.[1] || 0) * DEG, (g.rotation?.[2] || 0) * DEG);
    obj.userData.rest = { p: obj.position.clone(), r: obj.rotation.clone() };
    parentObj.add(obj);
    bones[g.name] = obj;
    for (const c of node.children || []) walk(c, obj, g.origin);
  }
  for (const n of model.outliner) walk(n, root, [0, 0, 0]);
  return { root, bones };
}

// ---------- Animation ----------
function sampleChannel(kfs, t) {
  // kfs sorted by time. Returns [x,y,z] or null
  if (!kfs.length) return null;
  const val = (kf, pt = 0) => { const d = kf.data_points[Math.min(pt, kf.data_points.length - 1)]; return [molang(d.x, t), molang(d.y, t), molang(d.z, t)]; };
  if (t <= kfs[0].time) return val(kfs[0], 0);
  const last = kfs[kfs.length - 1];
  if (t >= last.time) return val(last, last.data_points.length - 1);
  let i = 0; while (i < kfs.length - 1 && kfs[i + 1].time <= t) i++;
  const a = kfs[i], b = kfs[i + 1];
  const alpha = (t - a.time) / (b.time - a.time);
  const va = val(a, a.data_points.length - 1), vb = val(b, 0);
  if (a.interpolation === 'step') return va;
  if (a.interpolation === 'catmullrom' || b.interpolation === 'catmullrom') {
    const p0 = i > 0 ? val(kfs[i - 1]) : va, p3 = i + 2 < kfs.length ? val(kfs[i + 2]) : vb;
    const s = alpha, s2 = s * s, s3 = s2 * s;
    return va.map((_, k) => 0.5 * ((2 * va[k]) + (-p0[k] + vb[k]) * s + (2 * p0[k] - 5 * va[k] + 4 * vb[k] - p3[k]) * s2 + (-p0[k] + 3 * va[k] - 3 * vb[k] + p3[k]) * s3));
  }
  return va.map((v, k) => v + (vb[k] - v) * alpha);
}
function applyAnimation(model, bones, animName, t) {
  for (const b of Object.values(bones)) { b.position.copy(b.userData.rest.p); b.rotation.copy(b.userData.rest.r); b.scale.set(1, 1, 1); }
  if (!animName) return;
  const names = Array.isArray(animName) ? animName : [animName];
  for (const nm of names) {
    const anim = model.animations.find((a) => a.name === nm || a.name.endsWith('.' + nm));
    if (!anim) throw new Error('no animation ' + nm);
    let tt = t;
    if (anim.loop === 'loop' && anim.length > 0) tt = t % anim.length;
    for (const an of Object.values(anim.animators || {})) {
      const bone = bones[an.name];
      if (!bone) continue;
      for (const ch of ['rotation', 'position', 'scale']) {
        const kfs = (an.keyframes || []).filter((k) => k.channel === ch).sort((a, b) => a.time - b.time);
        const v = sampleChannel(kfs, tt);
        if (!v) continue;
        if (ch === 'rotation') { bone.rotation.x += v[0] * DEG; bone.rotation.y += v[1] * DEG; bone.rotation.z += v[2] * DEG; }
        else if (ch === 'position') { bone.position.x += v[0]; bone.position.y += v[1]; bone.position.z += v[2]; }
        else { bone.scale.x *= v[0] || 1e-5; bone.scale.y *= v[1] || 1e-5; bone.scale.z *= v[2] || 1e-5; }
      }
    }
  }
}

// ---------- Rendering ----------
async function loadTex(src) {
  const img = new Image(); img.src = src; await img.decode();
  const tex = new THREE.Texture(img);
  tex.magFilter = THREE.NearestFilter; tex.minFilter = THREE.NearestFilter; tex.generateMipmaps = false;
  tex.colorSpace = THREE.SRGBColorSpace; tex.needsUpdate = true; tex.flipY = true;
  return tex;
}

window.renderSheet = async function (model, opts) {
  const tile = opts.tile || 360;
  const frames = opts.frames; // [{yaw,pitch,anim,time,label}]
  const cols = opts.cols || Math.min(frames.length, 4);
  const rows = Math.ceil(frames.length / cols);
  const canvas = document.createElement('canvas');
  canvas.width = cols * tile; canvas.height = rows * tile;
  document.body.appendChild(canvas);
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, alpha: false });
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setScissorTest(true);
  const texIdx = opts.texture || 0;
  const tex = await loadTex(model.textures[texIdx].source);
  const layers = [];
  for (const li of opts.emissive || []) layers.push(await loadTex(model.textures[li].source));
  const { root, bones } = buildModel(model, [tex]);
  // emissive overlay
  if (layers.length) {
    const lm = layers.map((lt) => new THREE.MeshBasicMaterial({ map: lt, transparent: true, side: THREE.DoubleSide, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1 }));
    root.traverse((o) => { if (o.isMesh && o.parent && o.parent.children.length === 1) { for (const m of lm) { const e = new THREE.Mesh(o.geometry, m); e.renderOrder = 2; o.parent.add(e); } } });
  }
  const scene = new THREE.Scene();
  scene.add(root);
  scene.add(new THREE.AmbientLight(0xffffff, opts.ambient ?? 1.25));
  const l1 = new THREE.DirectionalLight(0xffffff, opts.diffuse ?? 1.1); l1.position.set(0.2, 1, -0.7); scene.add(l1);
  const l2 = new THREE.DirectionalLight(0xffffff, (opts.diffuse ?? 1.1) * 0.55); l2.position.set(-0.2, 1, 0.7); scene.add(l2);
  // ground grid
  if (opts.ground !== false) {
    const grid = new THREE.GridHelper(48, 48, 0x6a6a7a, 0x55555f); grid.position.y = 0; scene.add(grid);
  }
  // bounds at rest
  applyAnimation(model, bones, null, 0); root.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(root);
  const center = opts.center ? new THREE.Vector3(...opts.center) : box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const radius = opts.radius || Math.max(size.x, size.y, size.z) * 0.62 + 1;
  const cam = new THREE.PerspectiveCamera(opts.fov || 30, 1, 0.1, 1000);
  const ctxs = [];
  for (let i = 0; i < frames.length; i++) {
    const f = frames[i];
    applyAnimation(model, bones, f.anim, f.time || 0);
    root.updateMatrixWorld(true);
    const yaw = (f.yaw ?? 30) * DEG, pitch = (f.pitch ?? 15) * DEG;
    if (f.ortho) {
      // orthographic view of a model-space window: {center:[x,y,z], half}
      const h = f.ortho.half;
      const oc = new THREE.OrthographicCamera(-h, h, h, -h, 0.1, 2000);
      const c = new THREE.Vector3(...f.ortho.center);
      oc.position.set(c.x - Math.sin(yaw) * Math.cos(pitch) * 300, c.y + Math.sin(pitch) * 300, c.z - Math.cos(yaw) * Math.cos(pitch) * 300);
      oc.lookAt(c);
      const x = (i % cols) * tile, y = (rows - 1 - Math.floor(i / cols)) * tile;
      renderer.setViewport(x, y, tile, tile); renderer.setScissor(x, y, tile, tile);
      renderer.setClearColor(opts.bg ?? 0x8c8c9c); renderer.clear();
      renderer.render(scene, oc);
      continue;
    }
    const dist = radius / Math.tan((cam.fov * DEG) / 2) * (f.zoom ? 1 / f.zoom : 1);
    // Model front faces -Z. yaw 0 => camera in front (at -Z)
    cam.position.set(center.x - Math.sin(yaw) * Math.cos(pitch) * dist, center.y + Math.sin(pitch) * dist, center.z - Math.cos(yaw) * Math.cos(pitch) * dist);
    cam.lookAt(center);
    const x = (i % cols) * tile, y = (rows - 1 - Math.floor(i / cols)) * tile;
    renderer.setViewport(x, y, tile, tile); renderer.setScissor(x, y, tile, tile);
    renderer.setClearColor(opts.bg ?? 0x8c8c9c);
    renderer.clear();
    renderer.render(scene, cam);
  }
  return canvas.toDataURL('image/png');
};
// world-space bounding box of the model posed at (anim, time): {min:[x,y,z], max:[x,y,z]}
window.bounds = function (model, anim, time) {
  const { root, bones } = buildModel(model, [new THREE.Texture()]);
  applyAnimation(model, bones, anim, time || 0);
  root.updateMatrixWorld(true);
  const box = new THREE.Box3().setFromObject(root);
  return { min: box.min.toArray(), max: box.max.toArray() };
};
window.ready = true;
