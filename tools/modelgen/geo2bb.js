// Convert a bedrock .geo.json (+ png) into a minimal bbmodel for the viewer.
const fs = require('fs');
const { Model } = require('./lib');
module.exports = function geo2bb(geoPath, pngPaths) {
  const g = JSON.parse(fs.readFileSync(geoPath, 'utf8'))['minecraft:geometry'][0];
  const W = g.description.texture_width, H = g.description.texture_height;
  const groups = [], elements = [], nodes = {};
  const helper = Object.create(Model.prototype);
  let n = 0;
  for (const b of g.bones) {
    const uuid = 'g' + (n++);
    const origin = b.pivot ? [-b.pivot[0], b.pivot[1], b.pivot[2]] : [0, 0, 0];
    const rotation = b.rotation ? [-b.rotation[0], -b.rotation[1], b.rotation[2]] : [0, 0, 0];
    groups.push({ uuid, name: b.name, origin, rotation });
    const node = { uuid, children: [] };
    nodes[b.name] = node;
    for (const c of b.cubes || []) {
      const size = c.size;
      const from = [-(c.origin[0] + size[0]), c.origin[1], c.origin[2]];
      const to = [from[0] + size[0], from[1] + size[1], from[2] + size[2]];
      const e = { uuid: 'e' + (n++), type: 'cube', from, to, inflate: c.inflate || 0,
        origin: c.pivot ? [-c.pivot[0], c.pivot[1], c.pivot[2]] : origin.slice(),
        rotation: c.rotation ? [-c.rotation[0], -c.rotation[1], c.rotation[2]] : [0, 0, 0] };
      if (Array.isArray(c.uv)) {
        const cc = { size: size.map((v) => Math.floor(v + 1e-7)), uv: c.uv, mirror: c.mirror ?? b.mirror ?? false };
        const uvs = helper.boxUV.call(helper, cc);
        e.faces = Object.fromEntries(Object.entries(uvs).map(([k, v]) => [k, { uv: v, texture: 0 }]));
      } else {
        e.faces = {};
        for (const [k, f] of Object.entries(c.uv)) {
          let uv = [f.uv[0], f.uv[1], f.uv[0] + f.uv_size[0], f.uv[1] + f.uv_size[1]];
          if (k === 'up' || k === 'down') uv = [uv[2], uv[3], uv[0], uv[1]];
          e.faces[k] = { uv, texture: 0 };
        }
      }
      elements.push(e);
      node.children.push(e.uuid);
    }
    if (b.parent) nodes[b.parent].children.push(node); else node.root = true;
  }
  const outliner = Object.values(nodes).filter((x) => x.root);
  const textures = pngPaths.map((p) => ({ name: p, source: 'data:image/png;base64,' + fs.readFileSync(p).toString('base64') }));
  return { resolution: { width: W, height: H }, elements, groups, outliner, textures, animations: [] };
};
