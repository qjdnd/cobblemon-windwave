"""
Blockbench (.bbmodel, Bedrock Entity format) -> Cobblemon assets converter.

Ports the parts of Blockbench's own Bedrock exporter that Cobblemon needs:
  * js/formats/bedrock/bedrock.js          (compileGroup / compileCube)
  * js/formats/bedrock/bedrock_animation.js (compileAnimation)
  * js/animations/keyframe.js              (compileBedrockKeyframe)
  * js/util/molang.ts                      (invertMolang)

so that the produced .geo.json / .animation.json are identical to what
"File > Export > Export Bedrock Geometry / Animations" would write.
"""

import base64
import json
import math
import re

STRING_NUM = re.compile(r"^-?\d+(\.\d+f?)?$")


# --------------------------------------------------------------------------- molang helpers

def _is_string_number(s):
    return bool(STRING_NUM.match(s))


def _process_molang_return(molang, callback):
    if "return " in molang:
        return re.sub(r"return (.+?)(;|$)", lambda m: "return " + callback(m.group(1)) + m.group(2), molang)
    molang = re.sub(r";+$", "", molang)
    last = molang.rfind(";")
    if last == -1:
        if "=" in molang:
            return molang + ";" + callback("")
        return callback(molang)
    before, after = molang[:last], molang[last + 1:]
    if "=" in after:
        return molang + ";" + callback("")
    return before + ";" + callback(after)


def invert_molang(molang):
    if isinstance(molang, (int, float)):
        return -molang
    if molang == "" or molang == "0":
        return molang
    if _is_string_number(molang):
        return str(-float(molang))

    def cb(expression):
        invert = True
        depth = 0
        last_operator = None
        result = ""
        for char in expression:
            if not depth:
                operator = None
                had_input = True
                if char == "-" and last_operator not in ("*", "/"):
                    if not invert and not last_operator:
                        result += "+"
                    invert = False
                    continue
                elif char in (" ", "\n"):
                    had_input = False
                elif char == "+" and last_operator not in ("*", "/"):
                    result += "-"
                    invert = False
                    continue
                elif char in "?:":
                    invert = True
                    operator = char
                elif invert:
                    result += "-"
                    invert = False
                elif char in "+-*/&|":
                    operator = char
                if had_input:
                    last_operator = operator
            if char in "{([":
                depth += 1
            elif char in "})]":
                depth -= 1
            result += char
        return result

    return _process_molang_return(molang, cb)


def export_molang(value):
    if not value:
        return 0
    if isinstance(value, str):
        try:
            num = float(value)
            return clean_num(num)
        except ValueError:
            return value.replace("\n", "")
    if isinstance(value, (int, float)):
        return clean_num(value)
    return 0


def clean_num(n):
    if isinstance(n, float):
        if n == 0:
            return 0
        if n.is_integer():
            return int(n)
        return round(n, 6)
    return n


def trim_float(val, digits=4):
    s = f"{val:.{digits}f}".rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s


# --------------------------------------------------------------------------- geometry

class Converter:
    def __init__(self, path):
        with open(path, encoding="utf-8") as fh:
            self.data = json.load(fh)
        self.groups = {g["uuid"]: g for g in self.data["groups"]}
        self.elements = {e["uuid"]: e for e in self.data["elements"]}
        self.parent_of = {}
        self.children_of = {}
        self.group_order = []
        self._walk(self.data["outliner"], None)
        self.extra_locators = {}

    def _walk(self, nodes, parent):
        for node in nodes:
            if isinstance(node, dict):
                uuid = node["uuid"]
                self.group_order.append(uuid)
                self.parent_of[uuid] = parent
                self.children_of[uuid] = []
                if parent is not None:
                    self.children_of[parent].append(("group", uuid))
                self._walk(node.get("children", []), uuid)
            else:
                if parent is not None:
                    self.children_of[parent].append(("element", node))

    @property
    def resolution(self):
        r = self.data["resolution"]
        return r["width"], r["height"]

    def group_by_name(self, name):
        for g in self.groups.values():
            if g["name"] == name:
                return g
        raise KeyError(name)

    def add_locator(self, bone_name, locator_name, position):
        """position is given in Blockbench (outliner) space, exactly like a Locator element."""
        self.extra_locators.setdefault(bone_name, {})[locator_name] = position

    def bone_pivot(self, bone_name):
        return list(self.group_by_name(bone_name)["origin"])

    def compile_cube(self, cube, bone_mirror):
        frm = cube["from"]
        to = cube["to"]
        size = [to[i] - frm[i] for i in range(3)]
        tpl = {
            "origin": [-(frm[0] + size[0]), frm[1], frm[2]],
            "size": size,
        }
        if cube.get("inflate"):
            tpl["inflate"] = cube["inflate"]
        rot = cube.get("rotation", [0, 0, 0])
        if any(r != 0 for r in rot):
            origin = cube.get("origin", [0, 0, 0])
            tpl["pivot"] = [-origin[0], origin[1], origin[2]]
            tpl["rotation"] = [-rot[0], -rot[1], rot[2]]
        box_uv = cube.get("box_uv", self.data["meta"].get("box_uv", False))
        if box_uv:
            tpl["uv"] = list(cube.get("uv_offset", [0, 0]))
            mirror = bool(cube.get("mirror_uv", False))
            if mirror == (not bone_mirror):
                tpl["mirror"] = mirror
        else:
            uv = {}
            for key, face in cube["faces"].items():
                if face.get("texture") is None:
                    continue
                fuv = face["uv"]
                entry = {"uv": [fuv[0], fuv[1]], "uv_size": [fuv[2] - fuv[0], fuv[3] - fuv[1]]}
                if face.get("rotation"):
                    entry["uv_rotation"] = face["rotation"]
                if key in ("up", "down"):
                    entry["uv"][0] += entry["uv_size"][0]
                    entry["uv"][1] += entry["uv_size"][1]
                    entry["uv_size"][0] *= -1
                    entry["uv_size"][1] *= -1
                uv[key] = entry
            tpl["uv"] = uv
        return _clean(tpl)

    def compile_group(self, uuid):
        g = self.groups[uuid]
        bone = {"name": g["name"]}
        parent = self.parent_of[uuid]
        if parent is not None:
            bone["parent"] = self.groups[parent]["name"]
        origin = g.get("origin", [0, 0, 0])
        bone["pivot"] = [-origin[0], origin[1], origin[2]]
        rot = g.get("rotation", [0, 0, 0])
        if any(r != 0 for r in rot):
            bone["rotation"] = [-rot[0], -rot[1], rot[2]]
        if g.get("bedrock_binding"):
            bone["binding"] = g["bedrock_binding"]
        if g.get("reset"):
            bone["reset"] = True
        bone_mirror = bool(g.get("mirror_uv")) and self.data["meta"].get("box_uv", False)
        if bone_mirror:
            bone["mirror"] = True
        cubes = []
        locators = {}
        for kind, child in self.children_of[uuid]:
            if kind != "element":
                continue
            el = self.elements.get(child)
            if el is None or el.get("export") is False:
                continue
            etype = el.get("type", "cube")
            if etype == "cube":
                cubes.append(self.compile_cube(el, bone_mirror))
            elif etype in ("locator", "null_object"):
                key = el["name"] if etype == "locator" else "_null_" + el["name"]
                pos = el.get("position", [0, 0, 0])
                offset = [-pos[0], pos[1], pos[2]]
                lrot = el.get("rotation", [0, 0, 0])
                if etype == "locator" and any(r != 0 for r in lrot):
                    locators[key] = {"offset": offset, "rotation": [-lrot[0], -lrot[1], lrot[2]]}
                else:
                    locators[key] = offset
        for name, pos in self.extra_locators.get(g["name"], {}).items():
            locators[name] = [-pos[0], pos[1], pos[2]]
        if cubes:
            bone["cubes"] = cubes
        if locators:
            bone["locators"] = _clean(locators)
        return _clean(bone)

    def geometry(self, identifier):
        w, h = self.resolution
        vb = self.data.get("visible_box", [1, 1, 0])
        desc = {
            "identifier": "geometry." + identifier,
            "texture_width": w,
            "texture_height": h,
            "visible_bounds_width": vb[0],
            "visible_bounds_height": vb[1],
            "visible_bounds_offset": [0, vb[2], 0],
        }
        bones = [self.compile_group(u) for u in self.group_order]
        return {"format_version": "1.12.0", "minecraft:geometry": [{"description": desc, "bones": bones}]}

    # ----------------------------------------------------------------------- animations

    def _kf_get(self, kf, axis, dp_index):
        dps = kf["data_points"]
        if dp_index:
            dp_index = max(0, min(dp_index, len(dps) - 1))
        dp = dps[dp_index] if dps else None
        if not dp or not dp.get(axis):
            return 0
        return export_molang(dp[axis])

    def _kf_array(self, kf, dp_index=0):
        return [self._kf_get(kf, a, dp_index) for a in ("x", "y", "z")]

    @staticmethod
    def _flip(channel, arr):
        if channel in ("position", "rotation"):
            arr[0] = invert_molang(arr[0])
        if channel == "rotation":
            arr[1] = invert_molang(arr[1])
        return [clean_num(v) if isinstance(v, (int, float)) else v for v in arr]

    def _compile_transform_kf(self, kf, previous):
        ch = kf["channel"]
        if kf.get("interpolation") == "catmullrom":
            include_pre = (previous is None and kf["time"] > 0) or (previous is not None and previous.get("interpolation") != "catmullrom")
            out = {}
            if include_pre:
                out["pre"] = self._flip(ch, self._kf_array(kf, 0))
            out["post"] = self._flip(ch, self._kf_array(kf, 1 if include_pre else 0))
            out["lerp_mode"] = "catmullrom"
            return out
        if len(kf["data_points"]) <= 1:
            if previous is not None and previous.get("interpolation") == "step":
                return {"pre": self._flip(ch, self._kf_array(previous, 1)), "post": self._flip(ch, self._kf_array(kf))}
            return self._flip(ch, self._kf_array(kf))
        return {"pre": self._flip(ch, self._kf_array(kf, 0)), "post": self._flip(ch, self._kf_array(kf, 1))}

    @staticmethod
    def _timecode(time, snapping):
        fps = max(1, min(snapping or 24, 120))
        t = max(0.0, round(time * fps) / fps)
        s = trim_float(t)
        if "." not in s:
            s += ".0"
        return s

    def compile_animation(self, anim):
        tag = {}
        keyframes_all = [k for a in anim.get("animators", {}).values() for k in a.get("keyframes", [])]
        max_len = max([anim.get("length") or 0] + [k["time"] for k in keyframes_all])
        if anim.get("loop") == "hold":
            tag["loop"] = "hold_on_last_frame"
        elif anim.get("loop") == "loop" or max_len == 0:
            tag["loop"] = True
        if anim.get("length"):
            tag["animation_length"] = round(anim["length"], 4)
        if anim.get("override"):
            tag["override_previous_animation"] = True
        for key, out in (("anim_time_update", "anim_time_update"), ("blend_weight", "blend_weight"), ("start_delay", "start_delay")):
            if anim.get(key):
                tag[out] = export_molang(anim[key])
        if anim.get("loop_delay") and tag.get("loop"):
            tag["loop_delay"] = export_molang(anim["loop_delay"])
        snapping = anim.get("snapping", 24)
        bones = {}
        sounds = {}
        particles = {}
        timeline = {}
        for uuid, animator in anim.get("animators", {}).items():
            kfs = animator.get("keyframes", [])
            if not kfs:
                continue
            if animator.get("type") == "effect" or uuid == "effects":
                for kf in sorted(kfs, key=lambda k: k["time"]):
                    tc = self._timecode(kf["time"], snapping)
                    if kf["channel"] == "sound":
                        pts = [{"effect": d["effect"]} for d in kf["data_points"] if d.get("effect")]
                        if pts:
                            sounds[tc] = pts[0] if len(pts) == 1 else pts
                    elif kf["channel"] == "particle":
                        pts = []
                        for d in kf["data_points"]:
                            if d.get("effect"):
                                p = {"effect": d["effect"]}
                                if d.get("locator"):
                                    p["locator"] = d["locator"]
                                pts.append(p)
                        if pts:
                            particles[tc] = pts[0] if len(pts) == 1 else pts
                    elif kf["channel"] == "timeline":
                        scripts = []
                        for d in kf["data_points"]:
                            if d.get("script"):
                                scripts.extend(d["script"].split("\n"))
                        scripts = [s for s in scripts if re.sub(r"[\n\s;.]+", "", s)]
                        scripts = [s if (re.search(r";\s*$", s) or s.startswith("/")) else s + ";" for s in scripts]
                        if scripts:
                            timeline[tc] = scripts[0] if len(scripts) == 1 else scripts
                continue
            group = self.groups.get(uuid)
            name = group["name"] if group else animator.get("name")
            bone_tag = {}
            for channel in ("rotation", "position", "scale"):
                ch_kfs = sorted([k for k in kfs if k["channel"] == channel], key=lambda k: k["time"])
                if not ch_kfs:
                    continue
                ch_tag = {}
                for i, kf in enumerate(ch_kfs):
                    previous = None
                    for p in ch_kfs:
                        if p["time"] < kf["time"]:
                            previous = p
                    ch_tag[self._timecode(kf["time"], snapping)] = self._compile_transform_kf(kf, previous)
                if len(ch_tag) == 1 and len(ch_kfs[0]["data_points"]) == 1 and ch_kfs[0].get("interpolation") != "catmullrom":
                    value = next(iter(ch_tag.values()))
                    if channel == "scale" and isinstance(value, list) and all(v == value[0] for v in value):
                        value = value[0]
                    bone_tag[channel] = value
                else:
                    bone_tag[channel] = ch_tag
            if bone_tag:
                bones[name] = bone_tag
        if sounds:
            tag["sound_effects"] = sounds
        if particles:
            tag["particle_effects"] = particles
        if timeline:
            tag["timeline"] = timeline
        if bones:
            tag["bones"] = bones
        return tag

    def animations(self, rename=None):
        rename = rename or {}
        out = {}
        for anim in self.data.get("animations", []):
            name = rename.get(anim["name"], anim["name"])
            out[name] = self.compile_animation(anim)
        return {"format_version": "1.8.0", "animations": out}

    # ----------------------------------------------------------------------- textures

    def textures(self):
        result = {}
        for tex in self.data.get("textures", []):
            src = tex.get("source", "")
            if not src.startswith("data:image/png;base64,"):
                raise ValueError("texture %s is not embedded" % tex["name"])
            result[tex["name"]] = base64.b64decode(src.split(",", 1)[1])
        return result


def _clean(obj):
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_clean(v) for v in obj]
    if isinstance(obj, float):
        return clean_num(obj)
    return obj
