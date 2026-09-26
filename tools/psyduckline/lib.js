// Cobblemon / Blockbench model generator library.
// Everything is authored in Blockbench space (the space .bbmodel files use):
//   +Y up, the Pokemon faces -Z (north), +X is the Pokemon's right side.
// Geometry/animation conversion to Bedrock (.geo.json/.animation.json) follows
// Blockbench's own bedrock codec (x-mirroring of pivots/origins, negated X/Y rotations).
'use strict';
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { PNG } = require('pngjs');

// ------------------------------------------------------------------ utils
const uuidFrom = (seed) => {
  const h = crypto.createHash('md5').update(seed).digest('hex');
  return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20, 32)}`;
};
const r4 = (v) => Math.round(v * 10000) / 10000;
const clamp = (v, a, b) => Math.min(Math.max(v, a), b);
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = (e0, e1, x) => { const t = clamp((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t); };

function hex(h, a = 255) {
  h = h.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16), a];
}
function mix(c1, c2, t) { return [0, 1, 2, 3].map((i) => Math.round(lerp(c1[i], c2[i], t))); }
function shadeCol(c, f) { return [clamp(Math.round(c[0] * f), 0, 255), clamp(Math.round(c[1] * f), 0, 255), clamp(Math.round(c[2] * f), 0, 255), c[3]]; }
// hue-shifted ramp between shadow and highlight via mid colour
function makeRamp(stops, n) {
  // stops: array of hex colours (dark->light); returns n colours interpolated
  const cols = stops.map((s) => (typeof s === 'string' ? hex(s) : s));
  const out = [];
  for (let i = 0; i < n; i++) {
    const t = (i / (n - 1)) * (cols.length - 1);
    const k = Math.min(Math.floor(t), cols.length - 2);
    out.push(mix(cols[k], cols[k + 1], t - k));
  }
  return out;
}

const BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]].map((r) => r.map((v) => (v + 0.5) / 16));
function bayer(x, y) { return BAYER4[((y % 4) + 4) % 4][((x % 4) + 4) % 4]; }

// hash based value noise (deterministic)
function hash3(x, y, z, seed = 0) {
  let h = (x * 374761393 + y * 668265263 + z * 2147483647 + seed * 144665) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  h = h ^ (h >>> 16);
  return ((h >>> 0) % 100000) / 100000;
}
function vnoise(p, scale = 1, seed = 0) {
  const x = p[0] / scale, y = p[1] / scale, z = p[2] / scale;
  const xi = Math.floor(x), yi = Math.floor(y), zi = Math.floor(z);
  const xf = x - xi, yf = y - yi, zf = z - zi;
  const s = (t) => t * t * (3 - 2 * t);
  const u = s(xf), v = s(yf), w = s(zf);
  let acc = 0;
  for (let dx = 0; dx < 2; dx++) for (let dy = 0; dy < 2; dy++) for (let dz = 0; dz < 2; dz++) {
    const wgt = (dx ? u : 1 - u) * (dy ? v : 1 - v) * (dz ? w : 1 - w);
    acc += wgt * hash3(xi + dx, yi + dy, zi + dz, seed);
  }
  return acc;
}
function pick(ramp, v, ctx, dither = 0.6) {
  const n = ramp.length;
  // irregular (hash) dither: reads as soft mottling instead of the regular Bayer cross-hatch
  const b = ctx ? (hash3(ctx.tu, ctx.tv, 17, 5) * 0.65 + bayer(ctx.tu, ctx.tv) * 0.35) - 0.5 : 0;
  const idx = clamp(Math.round(v * (n - 1) + b * dither), 0, n - 1);
  return ramp[idx].slice();
}

// ------------------------------------------------------------------ matrices
function matMul(a, b) {
  const o = new Array(16).fill(0);
  for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) for (let k = 0; k < 4; k++) o[r * 4 + c] += a[r * 4 + k] * b[k * 4 + c];
  return o;
}
const I4 = () => [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
function T4(x, y, z) { return [1, 0, 0, x, 0, 1, 0, y, 0, 0, 1, z, 0, 0, 0, 1]; }
function Rzyx(rx, ry, rz) {
  const d = Math.PI / 180;
  const [a, b, c] = [rx * d, ry * d, rz * d];
  const Rx = [1, 0, 0, 0, 0, Math.cos(a), -Math.sin(a), 0, 0, Math.sin(a), Math.cos(a), 0, 0, 0, 0, 1];
  const Ry = [Math.cos(b), 0, Math.sin(b), 0, 0, 1, 0, 0, -Math.sin(b), 0, Math.cos(b), 0, 0, 0, 0, 1];
  const Rz = [Math.cos(c), -Math.sin(c), 0, 0, Math.sin(c), Math.cos(c), 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
  return matMul(Rz, matMul(Ry, Rx));
}
function pivotRot(origin, rot) {
  if (!rot || (rot[0] === 0 && rot[1] === 0 && rot[2] === 0)) return I4();
  return matMul(T4(...origin), matMul(Rzyx(...rot), T4(-origin[0], -origin[1], -origin[2])));
}
function xform(m, p, w = 1) {
  return [0, 1, 2].map((r) => m[r * 4] * p[0] + m[r * 4 + 1] * p[1] + m[r * 4 + 2] * p[2] + m[r * 4 + 3] * w);
}
const norm3 = (v) => { const l = Math.hypot(...v) || 1; return v.map((x) => x / l); };

// ------------------------------------------------------------------ model
// reds used by Cobblemon's alpha-eye textures (brightest to darkest)
const ALPHA_REDS = { hi: [223, 72, 80, 255], mid: [208, 54, 70, 255], lo: [194, 36, 63, 255], deep: [181, 14, 56, 255], dark: [123, 0, 13, 255], darkest: [109, 0, 11, 255] };

const FACE_NORMALS = { east: [1, 0, 0], west: [-1, 0, 0], up: [0, 1, 0], down: [0, -1, 0], south: [0, 0, 1], north: [0, 0, -1] };

class Model {
  constructor(opts) {
    this.id = opts.id;
    this.texW = opts.texW || 64;
    this.texH = opts.texH || 64;
    this.visibleBox = opts.visibleBox || [2, 2, 0.5];
    this.bones = [];
    this.boneMap = {};
    this.cubes = [];
    this.animations = [];
    this.decals = [];
    this.palettes = opts.palettes; // {base:{...}, shiny:{...}}
    this.textureSets = opts.textureSets || ['base', 'shiny'];
    this.emissive = opts.emissive || false;
  }
  bone(name, pivot, opts = {}) {
    if (this.boneMap[name]) throw new Error('duplicate bone ' + name);
    const parent = opts.parent ? (typeof opts.parent === 'string' ? this.boneMap[opts.parent] : opts.parent) : null;
    if (opts.parent && !parent) throw new Error('missing parent for ' + name);
    const b = { name, origin: pivot.slice(), rotation: (opts.rotation || [0, 0, 0]).slice(), parent, children: [], locators: [], cubes: [] };
    if (parent) parent.children.push(b);
    this.bones.push(b);
    this.boneMap[name] = b;
    return b;
  }
  // Cobblemon convention: bone "locator_<name>" holding a locator "<name>"
  locator(parent, name, pos, opts = {}) {
    const b = this.bone(opts.boneName || 'locator_' + name, pos, { parent, rotation: opts.boneRotation });
    b.locators.push({ name, position: pos.slice(), rotation: opts.rotation || [0, 0, 0] });
    for (const extra of opts.extra || []) b.locators.push({ name: extra, position: pos.slice(), rotation: opts.rotation || [0, 0, 0] });
    return b;
  }
  cube(bone, spec) {
    bone = typeof bone === 'string' ? this.boneMap[bone] : bone;
    const c = Object.assign({ inflate: 0, rotation: [0, 0, 0], mirror: false }, spec);
    c.bone = bone;
    c.origin = (spec.origin || spec.pivot || bone.origin).slice();
    c.size = [0, 1, 2].map((i) => Math.floor(c.to[i] - c.from[i] + 1e-7));
    for (let i = 0; i < 3; i++) if (Math.abs(c.to[i] - c.from[i] - c.size[i]) > 1e-6) throw new Error(`cube ${c.name} non-integer size`);
    bone.cubes.push(c);
    this.cubes.push(c);
    return c;
  }
  // symmetric helper: creates cube on +X side and its mirror on -X side
  anim(name, spec) { this.animations.push(Object.assign({ name }, spec)); }
  decal(spec) { this.decals.push(spec); }

  // ---------------------------------------------------------------- transforms
  boneWorld(b) {
    if (b._world) return b._world;
    const parent = b.parent ? this.boneWorld(b.parent) : I4();
    b._world = matMul(parent, pivotRot(b.origin, b.rotation));
    return b._world;
  }
  cubeWorld(c) { return matMul(this.boneWorld(c.bone), pivotRot(c.origin, c.rotation)); }

  // ---------------------------------------------------------------- UV
  boxUV(c) {
    const [w, h, d] = c.size;
    const fl = {
      east: { from: [0, d], size: [d, h] },
      west: { from: [d + w, d], size: [d, h] },
      up: { from: [d + w, d], size: [-w, -d] },
      down: { from: [d + w * 2, 0], size: [-w, d] },
      south: { from: [d * 2 + w, d], size: [w, h] },
      north: { from: [d, d], size: [w, h] },
    };
    if (c.mirror) {
      for (const f of Object.values(fl)) { f.from[0] += f.size[0]; f.size[0] *= -1; }
      const e = fl.east; fl.east = fl.west; fl.west = e;
    }
    const out = {};
    for (const [k, f] of Object.entries(fl)) {
      out[k] = [f.from[0] + c.uv[0], f.from[1] + c.uv[1], f.from[0] + f.size[0] + c.uv[0], f.from[1] + f.size[1] + c.uv[1]];
    }
    return out;
  }
  packUV() {
    const items = this.cubes.filter((c) => !c.uvShare);
    for (const c of items) { const [w, h, d] = c.size; c._rw = 2 * (w + d); c._rh = d + h; }
    items.sort((a, b) => b._rh - a._rh || b._rw - a._rw);
    const W = this.texW;
    let H = this.texH;
    const occ = [];
    const fits = (x, y, w, h) => {
      if (x + w > W || y + h > H) return false;
      for (let j = y; j < y + h; j++) for (let i = x; i < x + w; i++) if (occ[j] && occ[j][i]) return false;
      return true;
    };
    const mark = (x, y, w, h) => { for (let j = y; j < y + h; j++) { occ[j] = occ[j] || []; for (let i = x; i < x + w; i++) occ[j][i] = true; } };
    for (const c of items) {
      if (c._rw > W) throw new Error('cube too wide for texture ' + c.name);
      let placed = false;
      for (let y = 0; y <= H - c._rh && !placed; y++) {
        for (let x = 0; x <= W - c._rw; x++) {
          if (fits(x, y, c._rw, c._rh)) { c.uv = [x, y]; mark(x, y, c._rw, c._rh); placed = true; break; }
        }
      }
      if (!placed) throw new Error(`texture ${W}x${H} too small (${c.name})`);
    }
    for (const c of this.cubes) if (c.uvShare) c.uv = c.uvShare.uv.slice();
    // usage stats
    let used = 0; for (const row of occ) if (row) used += row.filter(Boolean).length;
    this.uvUsage = used / (W * H);
  }

  // ---------------------------------------------------------------- painting
  faceCorners(c) {
    const [f0, f1, f2] = c.from, [t0, t1, t2] = c.to;
    return {
      east: [[t0, t1, t2], [t0, t1, f2], [t0, f1, t2]],
      west: [[f0, t1, f2], [f0, t1, t2], [f0, f1, f2]],
      up: [[f0, t1, f2], [t0, t1, f2], [f0, t1, t2]],
      down: [[f0, f1, t2], [t0, f1, t2], [f0, f1, f2]],
      south: [[f0, t1, t2], [t0, t1, t2], [f0, f1, t2]],
      north: [[t0, t1, f2], [f0, t1, f2], [t0, f1, f2]],
    };
  }
  paint(variant, layer = 'color') {
    const W = this.texW, H = this.texH;
    const img = new Uint8ClampedArray(W * H * 4);
    const owner = new Array(W * H).fill(null);
    const pal = this.palettes[variant];
    const store = {};
    const keyOf = (p) => p.map((v) => v.toFixed(2)).join('|');
    const planeOf = { north: 2, south: 2, east: 0, west: 0, up: 1, down: 1 };
    const cubeByName = Object.fromEntries(this.cubes.map((c) => [c.name, c]));
    // sample the (pre-decal) colour already painted on another cube's face at the same spot
    const storePost = {};
    const sample = (cubeName, face, p, post = false) => {
      const c = cubeByName[cubeName];
      const ax = planeOf[face];
      const q = p.slice();
      q[ax] = (face === 'north' || face === 'west' || face === 'down') ? c.from[ax] : c.to[ax];
      const st = post ? storePost : store;
      const r = st[cubeName + ':' + face] && st[cubeName + ':' + face][keyOf(q)];
      return r ? r.slice() : null;
    };
    for (const c of this.cubes) {
      if (c.uvShare) continue;
      const fn = layer === 'color' ? c.paint : c[layer];
      if (!fn) continue;
      const M = this.cubeWorld(c);
      const uvs = this.boxUV(c);
      const corners = this.faceCorners(c);
      for (const face of Object.keys(uvs)) {
        const [u1, v1, u2, v2] = uvs[face];
        if (u1 === u2 || v1 === v2) continue;
        const [TL, TR, BL] = corners[face];
        const ex = TR.map((v, i) => v - TL[i]), ey = BL.map((v, i) => v - TL[i]);
        const fw = Math.hypot(...ex), fh = Math.hypot(...ey);
        const n = norm3(xform(M, FACE_NORMALS[face], 0));
        for (let v = Math.min(v1, v2); v < Math.max(v1, v2); v++) {
          for (let u = Math.min(u1, u2); u < Math.max(u1, u2); u++) {
            const s = (u + 0.5 - u1) / (u2 - u1), t = (v + 0.5 - v1) / (v2 - v1);
            const lp = [0, 1, 2].map((i) => TL[i] + s * ex[i] + t * ey[i]);
            const p = xform(M, lp);
            const ctx = {
              p, lp, n, face, cube: c, variant, pal, tu: u, tv: v,
              col: Math.floor(s * fw), row: Math.floor(t * fh), W: fw, H: fh, s, t,
              // normalised position inside the cube (0..1 per axis, cube-local)
              q: [0, 1, 2].map((i) => (c.to[i] === c.from[i] ? 0.5 : (lp[i] - c.from[i]) / (c.to[i] - c.from[i]))),
              sample,
            };
            let col = fn(ctx);
            if (col) { const sk = c.name + ':' + face; (store[sk] = store[sk] || {})[keyOf(p)] = col.slice(); }
            if (layer === 'color') col = this.applyDecals(ctx, col);
            if (col) { const sk = c.name + ':' + face; (storePost[sk] = storePost[sk] || {})[keyOf(p)] = col.slice(); }
            if (!col) continue;
            const k = v * W + u;
            if (owner[k] && owner[k] !== c) throw new Error(`UV overlap ${owner[k].name} / ${c.name} at ${u},${v}`);
            owner[k] = c;
            img[k * 4] = col[0]; img[k * 4 + 1] = col[1]; img[k * 4 + 2] = col[2]; img[k * 4 + 3] = col[3] === undefined ? 255 : col[3];
          }
        }
      }
    }
    return img;
  }
  applyDecals(ctx, col) {
    for (const d of this.decals) {
      if (d.cubes && !d.cubes.includes(ctx.cube.name)) continue;
      if (d.face && d.face !== ctx.face) continue;
      const r = d.fn(ctx, col);
      if (r !== undefined) col = r;
    }
    return col;
  }

  // ---------------------------------------------------------------- export: bbmodel
  toBBModel(textures) {
    const id = this.id;
    const U = (s) => uuidFrom(id + ':' + s);
    const elements = [];
    const groups = [];
    const outlinerFor = (b) => {
      const children = [];
      for (const c of b.cubes) children.push(U('cube:' + b.name + ':' + c.name + ':' + b.cubes.indexOf(c)));
      for (const l of b.locators) children.push(U('loc:' + b.name + ':' + l.name));
      for (const ch of b.children) children.push(outlinerFor(ch));
      return { uuid: U('bone:' + b.name), isOpen: !b.name.startsWith('locator_'), children };
    };
    for (const b of this.bones) {
      groups.push({
        uuid: U('bone:' + b.name), export: true, locked: false, origin: b.origin.map(r4), rotation: b.rotation.map(r4),
        bedrock_binding: '', color: 0, name: b.name, children: [], reset: false, shade: true, mirror_uv: false,
        selected: false, visibility: true, autouv: 0, isOpen: true, primary_selected: false,
      });
      b.cubes.forEach((c, ci) => {
        const uvs = this.boxUV(c);
        const faces = {};
        for (const f of ['north', 'east', 'south', 'west', 'up', 'down']) faces[f] = { uv: uvs[f], texture: 0 };
        const e = {
          name: c.name, box_uv: true, render_order: 'default', locked: false, allow_mirror_modeling: true,
          from: c.from.map(r4), to: c.to.map(r4), autouv: 0, color: c.color ?? (ci % 8), origin: c.origin.map(r4),
          uv_offset: c.uv.slice(), faces, type: 'cube', uuid: U('cube:' + b.name + ':' + c.name + ':' + ci),
        };
        if (c.inflate) e.inflate = c.inflate;
        if (c.rotation.some((v) => v !== 0)) e.rotation = c.rotation.map(r4);
        if (c.mirror) e.mirror_uv = true;
        elements.push(e);
      });
      for (const l of b.locators) {
        elements.push({ name: l.name, position: l.position.map(r4), rotation: l.rotation.map(r4), ignore_inherited_scale: false, visibility: true, locked: false, uuid: U('loc:' + b.name + ':' + l.name), type: 'locator' });
      }
    }
    const outliner = this.bones.filter((b) => !b.parent).map(outlinerFor);
    const texJson = textures.map((t, i) => ({
      name: t.name, relative_path: t.name, folder: '', namespace: '', id: String(i), group: '', width: this.texW, height: this.texH,
      uv_width: this.texW, uv_height: this.texH, particle: false, use_as_default: false, layers_enabled: false, sync_to_project: '',
      render_mode: 'default', render_sides: 'auto', pbr_channel: 'color', frame_time: 1, frame_order_type: 'loop', frame_order: '',
      frame_interpolate: false, visible: true, internal: true, saved: true, uuid: U('tex:' + t.name),
      source: 'data:image/png;base64,' + t.png.toString('base64'),
    }));
    const animations = this.animations.map((a) => this.animToBB(a, U));
    return {
      meta: { format_version: '5.0', model_format: 'bedrock', box_uv: true },
      name: id, model_identifier: id, visible_box: this.visibleBox, variable_placeholders: '', variable_placeholder_buttons: [],
      bedrock_animation_mode: 'entity', timeline_setups: [], unhandled_root_fields: {},
      resolution: { width: this.texW, height: this.texH },
      elements, groups, outliner, textures: texJson, animations,
    };
  }
  // animation spec: {loop:bool, length, bones:{bone:{rotation|position|scale: channelSpec}}, sounds:{t:effect}, timeline:{t:script}}
  // channelSpec: [x,y,z] (constant/molang) or {time:[x,y,z]|{v:[..], lerp:'catmullrom'|'linear'|'step'}}
  normChannel(spec) {
    if (Array.isArray(spec)) return [{ time: 0, v: spec, lerp: 'linear' }];
    return Object.entries(spec).map(([t, v]) => (Array.isArray(v) ? { time: +t, v, lerp: 'linear' } : { time: +t, v: v.v, lerp: v.lerp || 'linear' })).sort((a, b) => a.time - b.time);
  }
  animToBB(a, U) {
    const animators = {};
    for (const [bname, chans] of Object.entries(a.bones || {})) {
      const bone = this.boneMap[bname];
      if (!bone) throw new Error(`animation ${a.name}: unknown bone ${bname}`);
      const kfs = [];
      for (const ch of ['rotation', 'position', 'scale']) {
        if (!chans[ch]) continue;
        for (const k of this.normChannel(chans[ch])) {
          const dp = { x: String(k.v[0]), y: String(k.v[1]), z: String(k.v[2]) };
          const kf = { channel: ch, data_points: [dp], uuid: U(`kf:${a.name}:${bname}:${ch}:${k.time}`), time: k.time, color: -1, interpolation: k.lerp };
          if (ch === 'scale') kf.uniform = false;
          kfs.push(kf);
        }
      }
      animators[U('bone:' + bname)] = { name: bname, type: 'bone', rotation_global: false, quaternion_interpolation: false, keyframes: kfs };
    }
    const fx = [];
    for (const [t, eff] of Object.entries(a.sounds || {})) fx.push({ channel: 'sound', data_points: [{ effect: eff, file: '' }], uuid: U(`snd:${a.name}:${t}`), time: +t, color: -1, interpolation: 'linear' });
    for (const [t, sc] of Object.entries(a.timeline || {})) fx.push({ channel: 'timeline', data_points: [{ script: sc }], uuid: U(`tl:${a.name}:${t}`), time: +t, color: -1, interpolation: 'linear' });
    if (fx.length) animators.effects = { name: 'Effects', type: 'effect', keyframes: fx };
    return {
      uuid: U('anim:' + a.name), name: `animation.${this.id}.${a.name}`, loop: a.loop ? 'loop' : (a.hold ? 'hold' : 'once'), override: false,
      length: a.length || 0, snapping: 24, selected: false, saved: true, path: '', anim_time_update: '', blend_weight: '',
      start_delay: '', loop_delay: '', animators,
    };
  }

  // ---------------------------------------------------------------- export: bedrock geo
  toGeo() {
    const bones = this.bones.map((b) => {
      const o = { name: b.name };
      if (b.parent) o.parent = b.parent.name;
      o.pivot = [r4(-b.origin[0]), r4(b.origin[1]), r4(b.origin[2])];
      if (b.rotation.some((v) => v !== 0)) o.rotation = [r4(-b.rotation[0]), r4(-b.rotation[1]), r4(b.rotation[2])];
      if (b.cubes.length) {
        o.cubes = b.cubes.map((c) => {
          const cc = { origin: [r4(-(c.from[0] + c.size[0])), r4(c.from[1]), r4(c.from[2])], size: c.size.slice() };
          if (c.inflate) cc.inflate = c.inflate;
          if (c.rotation.some((v) => v !== 0)) {
            cc.pivot = [r4(-c.origin[0]), r4(c.origin[1]), r4(c.origin[2])];
            cc.rotation = [r4(-c.rotation[0]), r4(-c.rotation[1]), r4(c.rotation[2])];
          }
          cc.uv = c.uv.slice();
          if (c.mirror) cc.mirror = true;
          return cc;
        });
      }
      if (b.locators.length) {
        o.locators = {};
        for (const l of b.locators) {
          const off = [r4(-l.position[0]), r4(l.position[1]), r4(l.position[2])];
          o.locators[l.name] = l.rotation.some((v) => v !== 0) ? { offset: off, rotation: [r4(-l.rotation[0]), r4(-l.rotation[1]), r4(l.rotation[2])] } : off;
        }
      }
      return o;
    });
    // visible bounds
    return {
      format_version: '1.12.0',
      'minecraft:geometry': [{
        description: {
          identifier: 'geometry.' + this.id, texture_width: this.texW, texture_height: this.texH,
          visible_bounds_width: this.visibleBox[0], visible_bounds_height: this.visibleBox[1], visible_bounds_offset: [0, this.visibleBox[2], 0],
        },
        bones,
      }],
    };
  }

  // ---------------------------------------------------------------- export: bedrock animation
  static invert(v) {
    if (typeof v === 'number') return v === 0 ? 0 : -v;
    const s = String(v).trim();
    if (/^-?\d+(\.\d+)?$/.test(s)) { const n = -parseFloat(s); return n === 0 ? 0 : n; }
    return `-(${s})`;
  }
  static num(v) {
    if (typeof v === 'number') return r4(v);
    const s = String(v).trim();
    if (/^-?\d+(\.\d+)?$/.test(s)) return r4(parseFloat(s));
    return s;
  }
  toAnimationJson() {
    const anims = {};
    for (const a of this.animations) {
      const out = {};
      if (a.loop) out.loop = true; // one-shots (incl. faint) omit 'loop' like Cobblemon's own files
      if (a.length) out.animation_length = a.length;
      const bones = {};
      for (const [bname, chans] of Object.entries(a.bones || {})) {
        const bo = {};
        for (const ch of ['rotation', 'position', 'scale']) {
          if (!chans[ch]) continue;
          const kfs = this.normChannel(chans[ch]);
          const conv = (v) => {
            let arr = v.slice();
            if (ch === 'rotation') arr = [Model.invert(arr[0]), Model.invert(arr[1]), arr[2]];
            if (ch === 'position') arr = [Model.invert(arr[0]), arr[1], arr[2]];
            return arr.map(Model.num);
          };
          if (kfs.length === 1 && kfs[0].time === 0 && kfs[0].lerp !== 'catmullrom') { bo[ch] = conv(kfs[0].v); continue; }
          const o = {};
          kfs.forEach((k, i) => {
            const key = (Math.round(k.time * 10000) / 10000).toString().includes('.') ? String(Math.round(k.time * 10000) / 10000) : k.time.toFixed(1);
            if (k.lerp === 'catmullrom') o[key] = { post: conv(k.v), lerp_mode: 'catmullrom' };
            else if (i > 0 && kfs[i - 1].lerp === 'step') o[key] = { pre: conv(kfs[i - 1].v), post: conv(k.v) };
            else o[key] = conv(k.v);
          });
          bo[ch] = o;
        }
        bones[bname] = bo;
      }
      out.bones = bones;
      if (a.sounds) { out.sound_effects = {}; for (const [t, e] of Object.entries(a.sounds)) out.sound_effects[(+t).toFixed(4).replace(/0+$/, '').replace(/\.$/, '.0')] = { effect: e }; }
      if (a.timeline) { out.timeline = {}; for (const [t, s] of Object.entries(a.timeline)) out.timeline[(+t).toFixed(4).replace(/0+$/, '').replace(/\.$/, '.0')] = s; }
      anims[`animation.${this.id}.${a.name}`] = out;
    }
    return { format_version: '1.8.0', animations: anims };
  }

  // ---------------------------------------------------------------- build
  build(outDir) {
    this.packUV();
    const textures = [];
    const pngOf = (img) => { const png = new PNG({ width: this.texW, height: this.texH }); png.data = Buffer.from(img); return PNG.sync.write(png); };
    for (const v of this.textureSets) {
      const suffix = v === 'base' ? '' : '_' + v;
      textures.push({ name: `${this.id}${suffix}.png`, png: pngOf(this.paint(v, 'color')), variant: v, layer: 'color' });
    }
    if (this.emissive) {
      for (const v of this.textureSets) {
        const suffix = v === 'base' ? '' : '_' + v;
        textures.push({ name: `${this.id}_emissive${suffix}.png`, png: pngOf(this.paint(v, 'emissive')), variant: v, layer: 'emissive' });
      }
    }
    // glowing red eyes shown on alpha Pokemon (Cobblemon "alpha_eyes" aspect layer)
    if (this.cubes.some((c) => c.alpha)) {
      textures.push({ name: `${this.id}_alpha.png`, png: pngOf(this.paint('base', 'alpha')), variant: 'base', layer: 'alpha' });
    }
    const bb = this.toBBModel(textures);
    const geo = this.toGeo();
    const anim = this.toAnimationJson();
    if (outDir) {
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(path.join(outDir, `${this.id}.bbmodel`), JSON.stringify(bb));
      fs.writeFileSync(path.join(outDir, `${this.id}.geo.json`), JSON.stringify(geo, null, 2));
      fs.writeFileSync(path.join(outDir, `${this.id}.animation.json`), JSON.stringify(anim, null, 2));
      for (const t of textures) fs.writeFileSync(path.join(outDir, t.name), t.png);
    }
    return { bb, geo, anim, textures };
  }
}

// ------------------------------------------------------------------ shading helpers
// Pseudo-rounded lighting: treat the texel as lying on an ellipsoid (center c, radii r)
// and light it with a key light from the front-top. Returns 0..1.
const KEY = norm3([-0.35, 0.85, -0.55]);
function ellipsoidLight(p, c, r, key = KEY, wrap = 0.35) {
  const n = norm3([(p[0] - c[0]) / (r[0] * r[0]), (p[1] - c[1]) / (r[1] * r[1]), (p[2] - c[2]) / (r[2] * r[2])]);
  const d = n[0] * key[0] + n[1] * key[1] + n[2] * key[2];
  return { l: clamp((d + wrap) / (1 + wrap), 0, 1), n };
}

// Draw pixel-art from string rows. rows[0] is the top row. '.' = transparent (no change).
function sprite(rows, palette) {
  return (col, row) => {
    if (row < 0 || row >= rows.length) return undefined;
    const ch = rows[row][col];
    if (ch === undefined || ch === '.' || ch === ' ') return undefined;
    const c = palette[ch];
    if (!c) throw new Error('sprite palette missing ' + ch);
    return typeof c === 'string' ? hex(c) : c;
  };
}

module.exports = { ALPHA_REDS, Model, hex, mix, shadeCol, makeRamp, pick, bayer, vnoise, hash3, clamp, lerp, smooth, ellipsoidLight, norm3, sprite, KEY, uuidFrom };
