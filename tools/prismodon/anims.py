"""Bedrock animations for Prismodon.

Conventions (bedrock values, as stored in the json / shown in Blockbench):
* rotation x > 0 tilts forward-pointing parts down (head nods, jaw opens),
  raises backward-pointing parts (tail) and swings legs' feet backwards.
* position x > 0 moves towards the Pokemon's left.
"""

NAME = "prismodon"
LEGS = ("front_left", "front_right", "back_left", "back_right")


def f(v):
    v = round(float(v), 3)
    return int(v) if v == int(v) else v


def _arg(speed, phase):
    """'q.anim_time*speed - phase' with the phase wrapped into (-180, 180]."""
    p = (float(phase) + 180.0) % 360.0 - 180.0
    if abs(p) < 1e-9:
        return f"q.anim_time*{f(speed)}"
    return f"q.anim_time*{f(speed)}{'-' if p > 0 else '+'}{f(abs(p))}"


def sin(amp, speed, phase=0.0, offset=0.0):
    """offset + sin(t * speed - phase) * amp   (degrees per second)."""
    if amp == 0:
        return f(offset)
    expr = f"math.sin({_arg(speed, phase)})*{f(amp)}"
    return f"{f(offset)}+{expr}" if offset else expr


def cos(amp, speed, phase=0.0, offset=0.0):
    return sin(amp, speed, phase - 90.0, offset)


def lift(amp, speed, phase=0.0):
    """max(0, -cos(t*speed - phase)) * amp, written with abs() only."""
    c = f"math.cos({_arg(speed, phase)})"
    return f"(math.abs({c})-{c})*{f(amp / 2)}"


def kf(frames, lerp="catmullrom"):
    """{time: [x, y, z]} -> bedrock keyframe dict."""
    out = {}
    for t, v in sorted(frames.items()):
        key = f"{t:.4f}".rstrip("0").rstrip(".")
        if "." not in key:
            key += ".0"
        vv = [f(x) if isinstance(x, (int, float)) else x for x in v]
        out[key] = {"post": vv, "lerp_mode": lerp} if lerp == "catmullrom" else vv
    return out


def leg_phase(leg):
    # diagonal pairs move together
    return 0.0 if leg in ("front_left", "back_right") else 180.0


def gait(speed, amp, knee, bob, roll, tail_amp, neck_amp, head_pitch=0.0, torso_pitch=0.0):
    """Shared quadruped gait (walk / run)."""
    bones = {
        "body": {"position": [0, cos(bob, speed * 2, 20), 0]},
        "torso": {"rotation": [cos(1.2, speed * 2, 60, torso_pitch), sin(roll * 0.6, speed), sin(roll, speed, 30)]},
        "neck": {"rotation": [cos(neck_amp, speed * 2, 60), sin(1.0, speed, 40), 0]},
        "neck2": {"rotation": [cos(neck_amp, speed * 2, 100), 0, 0]},
        "neck3": {"rotation": [cos(neck_amp * 0.8, speed * 2, 140), 0, 0]},
        "head": {"rotation": [cos(neck_amp * 1.2, speed * 2, 180, head_pitch), 0, sin(roll * -0.8, speed, 60)]},
        "jaw": {"rotation": [cos(1.5, speed * 2, 200), 0, 0]},
        "crest": {"rotation": [cos(1.5, speed * 2, 220), 0, 0]},
        "back_fin": {"rotation": [cos(1.5, speed * 2, 120), 0, 0]},
        "back_plate_front": {"rotation": [cos(1.5, speed * 2, 150), 0, sin(1.0, speed, 90)]},
        "back_plate_rear": {"rotation": [cos(2.0, speed * 2, 190), 0, sin(1.2, speed, 120)]},
        "tail": {"rotation": [cos(1.5, speed * 2, 60), sin(tail_amp * 0.6, speed, 60), 0]},
        "tail2": {"rotation": [0, sin(tail_amp * 0.8, speed, 100), 0]},
        "tail3": {"rotation": [0, sin(tail_amp, speed, 140), 0]},
        "tail4": {"rotation": [0, sin(tail_amp * 1.2, speed, 180), 0]},
    }
    for leg in LEGS:
        p = leg_phase(leg)
        bones[f"leg_{leg}"] = {"rotation": [sin(amp, speed, p), 0, 0]}
        bones[f"leg_{leg}2"] = {"rotation": [lift(knee, speed, p), 0, 0]}
        # keep the sole roughly parallel to the ground
        bones[f"foot_{leg}"] = {"rotation": [f"-({sin(amp, speed, p)})*0.9-({lift(knee, speed, p)})*0.85", 0, 0]}
    return bones


def ground_idle():
    s = 90.0  # 4 s period
    return {
        "loop": True,
        "animation_length": 4,
        "bones": {
            "body": {"position": [0, sin(0.18, s, 0), 0]},
            "torso": {"rotation": [sin(0.6, s, 0), 0, sin(0.4, s / 2, 0)]},
            "neck": {"rotation": [sin(1.4, s, 30), sin(1.5, s / 2, 20), 0]},
            "neck2": {"rotation": [sin(1.4, s, 60), sin(1.5, s / 2, 50), 0]},
            "neck3": {"rotation": [sin(1.2, s, 90), 0, 0]},
            "head": {"rotation": [sin(2.0, s, 130), 0, sin(1.6, s / 2, 90)]},
            "jaw": {"rotation": [sin(1.5, s, 150, 0.5), 0, 0]},
            "crest": {"rotation": [sin(1.2, s, 170), 0, 0]},
            "back_fin": {"rotation": [sin(1.0, s, 60), 0, 0]},
            "back_plate_front": {"rotation": [sin(1.0, s, 80), 0, sin(0.6, s / 2, 30)]},
            "back_plate_rear": {"rotation": [sin(1.2, s, 110), 0, sin(0.8, s / 2, 60)]},
            "tail": {"rotation": [sin(1.2, s, 40), sin(3.0, s / 2, 0), 0]},
            "tail2": {"rotation": [sin(1.0, s, 70), sin(4.0, s / 2, 40), 0]},
            "tail3": {"rotation": [sin(1.0, s, 100), sin(5.0, s / 2, 80), 0]},
            "tail4": {"rotation": [sin(1.0, s, 130), sin(6.0, s / 2, 120), 0]},
        },
    }


def ground_walk():
    return {"loop": True, "animation_length": 1.6,
            "bones": gait(speed=225, amp=17, knee=22, bob=0.35, roll=1.6, tail_amp=6, neck_amp=1.6)}


def ground_run():
    b = gait(speed=400, amp=27, knee=34, bob=0.7, roll=2.4, tail_amp=9, neck_amp=2.6,
             head_pitch=4, torso_pitch=2)
    b["neck"]["rotation"][0] = cos(2.6, 800, 60, 8)
    b["tail"]["rotation"][0] = cos(3, 800, 60, 6)
    return {"loop": True, "animation_length": 0.9, "bones": b}


def battle_idle():
    s = 180.0  # 2 s period
    bones = {
        "body": {"position": [0, sin(0.25, s, 0, -0.6), 0]},
        "torso": {"rotation": [sin(0.8, s, 0, 2.5), 0, sin(0.6, s / 2, 0)]},
        "neck": {"rotation": [sin(1.5, s, 30, 7), sin(2, s / 2, 20), 0]},
        "neck2": {"rotation": [sin(1.5, s, 60, 5), 0, 0]},
        "neck3": {"rotation": [sin(1.2, s, 90, 2), 0, 0]},
        "head": {"rotation": [sin(2.2, s, 120, -10), 0, sin(1.5, s / 2, 60)]},
        "jaw": {"rotation": [sin(2.5, s * 2, 0, 7), 0, 0]},
        "crest": {"rotation": [sin(2.0, s, 150, -3), 0, 0]},
        "back_fin": {"rotation": [sin(1.5, s, 60), 0, 0]},
        "back_plate_front": {"rotation": [sin(1.5, s, 90, -2), 0, sin(1.0, s, 0)]},
        "back_plate_rear": {"rotation": [sin(2.0, s, 120, -2), 0, sin(1.2, s, 40)]},
        "tail": {"rotation": [sin(2, s, 30, 10), sin(5, s / 2, 0), 0]},
        "tail2": {"rotation": [sin(2, s, 60, 4), sin(6, s / 2, 40), 0]},
        "tail3": {"rotation": [0, sin(7, s / 2, 80), 0]},
        "tail4": {"rotation": [0, sin(8, s / 2, 120), 0]},
    }
    for leg in LEGS:
        front = leg.startswith("front")
        spread = 4 if leg.endswith("left") else -4
        bones[f"leg_{leg}"] = {"rotation": [-7 if front else 7, 0, spread * (1 if front else 0.6)]}
        bones[f"leg_{leg}2"] = {"rotation": [5 if front else -4, 0, 0]}
        bones[f"foot_{leg}"] = {"rotation": [2 if front else -3, 0, -spread * (1 if front else 0.6)]}
    return {"loop": True, "animation_length": 2, "bones": bones}


def blink():
    return {
        "animation_length": 0.25,
        "bones": {
            "eyelid_left": {"position": {"0.0": [0.12, 0, 0], "0.2": [0.12, 0, 0], "0.25": [0, 0, 0]}},
            "eyelid_right": {"position": {"0.0": [-0.12, 0, 0], "0.2": [-0.12, 0, 0], "0.25": [0, 0, 0]}},
        },
    }


def shake(amp, speed=2200):
    return f"math.sin(q.anim_time*{speed})*{amp}"


def cry():
    return {
        "animation_length": 2.4,
        "bones": {
            "torso": {"rotation": kf({0: [0, 0, 0], 0.25: [2, 0, 0], 0.6: [-5, 0, 0], 1.5: [-5, 0, 0], 2.2: [0, 0, 0]})},
            "body": {"position": kf({0: [0, 0, 0], 0.25: [0, -0.4, 0], 0.6: [0, 0.4, 0], 1.5: [0, 0.4, 0], 2.2: [0, 0, 0]})},
            "neck": {"rotation": kf({0: [0, 0, 0], 0.25: [3, 0, 0], 0.6: [-9, 0, 0], 1.5: [-10, 0, 0], 2.2: [0, 0, 0]})},
            "neck2": {"rotation": kf({0: [0, 0, 0], 0.25: [3, 0, 0], 0.6: [-8, 0, 0], 1.5: [-8, 0, 0], 2.2: [0, 0, 0]})},
            "head": {"rotation": kf({0: [0, 0, 0], 0.25: [10, 0, 0], 0.6: [-26, 0, shake(1.5)],
                                     1.5: [-28, 0, shake(1.5)], 1.7: [-20, 0, 0], 2.2: [0, 0, 0]})},
            "jaw": {"rotation": kf({0: [0, 0, 0], 0.25: [3, 0, 0], 0.6: [34, 0, 0], 1.5: [32, 0, 0], 1.9: [2, 0, 0], 2.2: [0, 0, 0]})},
            "crest": {"rotation": kf({0: [0, 0, 0], 0.6: [-6, 0, shake(2.5)], 1.5: [-6, 0, shake(2.5)], 2.0: [0, 0, 0]})},
            "back_plate_front": {"rotation": kf({0: [0, 0, 0], 0.6: [-3, 0, shake(2.5, 2400)], 1.5: [-3, 0, shake(2.5, 2400)], 2.0: [0, 0, 0]})},
            "back_plate_rear": {"rotation": kf({0: [0, 0, 0], 0.6: [-3, 0, shake(3, 2600)], 1.5: [-3, 0, shake(3, 2600)], 2.0: [0, 0, 0]})},
            "back_fin": {"rotation": kf({0: [0, 0, 0], 0.6: [-4, 0, shake(2, 2300)], 1.5: [-4, 0, shake(2, 2300)], 2.0: [0, 0, 0]})},
            "tail": {"rotation": kf({0: [0, 0, 0], 0.6: [12, 0, 0], 1.5: [12, 0, 0], 2.2: [0, 0, 0]})},
            "tail2": {"rotation": kf({0: [0, 0, 0], 0.6: [6, 0, 0], 1.5: [6, 0, 0], 2.2: [0, 0, 0]})},
        },
    }


def faint():
    bones = {
        "body": {
            "rotation": kf({0: [0, 0, 0], 1.1: [0, 0, 0], 1.55: [0, 0, 62], 1.75: [0, 0, 84], 1.95: [0, 0, 78], 2.8: [0, 0, 80]}),
            "position": kf({0: [0, 0, 0], 0.4: [0, 0.4, 0], 1.1: [0, -3.5, 0], 1.55: [0, -4.5, 0], 1.75: [0, -6, 0], 2.8: [0, -5.6, 0]}),
        },
        "neck": {"rotation": kf({0: [0, 0, 0], 0.4: [-8, 0, 0], 1.1: [10, 0, 0], 1.8: [28, 0, -10], 2.8: [30, 0, -12]})},
        "neck2": {"rotation": kf({0: [0, 0, 0], 0.4: [-5, 0, 0], 1.1: [6, 0, 0], 1.8: [16, 0, -8], 2.8: [18, 0, -8]})},
        "neck3": {"rotation": kf({0: [0, 0, 0], 1.1: [4, 0, 0], 1.8: [8, 0, 0], 2.8: [10, 0, 0]})},
        "head": {"rotation": kf({0: [0, 0, 0], 0.4: [-18, 0, 0], 1.1: [6, 0, 0], 1.8: [18, 0, -12], 2.8: [20, 0, -14]})},
        "jaw": {"rotation": kf({0: [0, 0, 0], 0.4: [24, 0, 0], 1.1: [8, 0, 0], 1.9: [14, 0, 0], 2.8: [12, 0, 0]})},
        "tail": {"rotation": kf({0: [0, 0, 0], 1.1: [-4, 0, 0], 2.0: [-10, -8, 0], 2.8: [-10, -8, 0]})},
        "tail2": {"rotation": kf({0: [0, 0, 0], 2.0: [-6, -8, 0], 2.8: [-6, -8, 0]})},
        "tail3": {"rotation": kf({0: [0, 0, 0], 2.0: [-4, -6, 0], 2.8: [-4, -6, 0]})},
        "eyelid_left": {"position": {"0.0": [0, 0, 0], "1.6": [0, 0, 0], "1.65": [0.12, 0, 0]}},
        "eyelid_right": {"position": {"0.0": [0, 0, 0], "1.6": [0, 0, 0], "1.65": [-0.12, 0, 0]}},
    }
    for leg in LEGS:
        front = leg.startswith("front")
        s = 1 if leg.endswith("left") else -1
        up = [-18, 0, 0] if front else [22, 0, 0]
        low = [34, 0, 0] if front else [-28, 0, 0]
        bones[f"leg_{leg}"] = {"rotation": kf({0: [0, 0, 0], 0.4: [0, 0, 0], 1.1: up, 1.8: [up[0] * 0.5, 0, -14 * s], 2.8: [up[0] * 0.5, 0, -16 * s]})}
        bones[f"leg_{leg}2"] = {"rotation": kf({0: [0, 0, 0], 0.4: [0, 0, 0], 1.1: low, 1.8: [low[0] * 0.4, 0, 0], 2.8: [low[0] * 0.4, 0, 0]})}
    return {"loop": "hold_on_last_frame", "animation_length": 2.8, "bones": bones}


def sleep():
    s = 72.0  # 5 s breathing
    bones = {
        "body": {"position": [0, sin(0.15, s, 0, -6.3), 0]},
        "torso": {"rotation": [sin(0.5, s, 0, 1.5), 0, 0]},
        "neck": {"rotation": [sin(0.5, s, 40, 74), -10, 0]},
        "neck2": {"rotation": [30, -12, 0]},
        "neck3": {"rotation": [12, -10, 0]},
        "head": {"rotation": [sin(0.8, s, 80, -104), -8, 8]},
        "jaw": {"rotation": [-5, 0, 0]},
        "crest": {"rotation": [4, 0, 0]},
        "tail": {"rotation": [-8, 22, 0]},
        "tail2": {"rotation": [-4, 24, 0]},
        "tail3": {"rotation": [0, 24, 0]},
        "tail4": {"rotation": [0, 22, 0]},
        "eyelid_left": {"position": [0.12, 0, 0]},
        "eyelid_right": {"position": [-0.12, 0, 0]},
    }
    for leg in LEGS:
        front = leg.startswith("front")
        s_ = 1 if leg.endswith("left") else -1
        if front:
            bones[f"leg_{leg}"] = {"rotation": [-62, 0, 6 * s_]}
            bones[f"leg_{leg}2"] = {"rotation": [30, 0, 0]}
            bones[f"foot_{leg}"] = {"rotation": [34, 0, 0]}
        else:
            bones[f"leg_{leg}"] = {"rotation": [66, 0, 4 * s_]}
            bones[f"leg_{leg}2"] = {"rotation": [-24, 0, 0]}
            bones[f"foot_{leg}"] = {"rotation": [-40, 0, 0]}
    return {"loop": True, "animation_length": 5, "bones": bones}


def physical():
    return {
        "animation_length": 1.0,
        "bones": {
            "body": {"position": kf({0: [0, 0, 0], 0.3: [0, 0.3, 2], 0.5: [0, -0.4, -3.5], 1.0: [0, 0, 0]})},
            "torso": {"rotation": kf({0: [0, 0, 0], 0.3: [-4, 0, 0], 0.5: [5, 0, 0], 1.0: [0, 0, 0]})},
            "neck": {"rotation": kf({0: [0, 0, 0], 0.3: [-10, 0, 0], 0.5: [20, 0, 0], 1.0: [0, 0, 0]})},
            "neck2": {"rotation": kf({0: [0, 0, 0], 0.3: [-6, 0, 0], 0.5: [10, 0, 0], 1.0: [0, 0, 0]})},
            "head": {"rotation": kf({0: [0, 0, 0], 0.3: [-12, 0, 0], 0.5: [26, 0, 0], 1.0: [0, 0, 0]})},
            "jaw": {"rotation": kf({0: [0, 0, 0], 0.3: [16, 0, 0], 0.5: [4, 0, 0], 1.0: [0, 0, 0]})},
            "crest": {"rotation": kf({0: [0, 0, 0], 0.5: [8, 0, 0], 1.0: [0, 0, 0]})},
            "leg_front_left": {"rotation": kf({0: [0, 0, 0], 0.3: [-16, 0, 0], 0.5: [6, 0, 0], 1.0: [0, 0, 0]})},
            "leg_front_left2": {"rotation": kf({0: [0, 0, 0], 0.3: [18, 0, 0], 0.5: [0, 0, 0], 1.0: [0, 0, 0]})},
            "leg_front_right": {"rotation": kf({0: [0, 0, 0], 0.3: [-10, 0, 0], 0.5: [8, 0, 0], 1.0: [0, 0, 0]})},
            "tail": {"rotation": kf({0: [0, 0, 0], 0.3: [8, 0, 0], 0.5: [-4, 0, 0], 1.0: [0, 0, 0]})},
        },
    }


def special():
    jit = shake(2.2, 2400)
    return {
        "animation_length": 1.3,
        "bones": {
            "body": {"position": kf({0: [0, 0, 0], 0.4: [0, 1.6, 1], 0.9: [0, 1.6, 1], 1.3: [0, 0, 0]})},
            "torso": {"rotation": kf({0: [0, 0, 0], 0.4: [-11, 0, 0], 0.9: [-11, 0, 0], 1.3: [0, 0, 0]})},
            "neck": {"rotation": kf({0: [0, 0, 0], 0.4: [-6, 0, 0], 0.9: [-6, 0, 0], 1.3: [0, 0, 0]})},
            "head": {"rotation": kf({0: [0, 0, 0], 0.4: [-18, 0, 0], 0.9: [-16, 0, 0], 1.3: [0, 0, 0]})},
            "jaw": {"rotation": kf({0: [0, 0, 0], 0.4: [26, 0, 0], 0.9: [24, 0, 0], 1.3: [0, 0, 0]})},
            "crest": {"rotation": kf({0: [0, 0, 0], 0.4: [-6, 0, jit], 0.9: [-6, 0, jit], 1.3: [0, 0, 0]})},
            "back_plate_front": {"rotation": kf({0: [0, 0, 0], 0.4: [-4, 0, jit], 0.9: [-4, 0, jit], 1.3: [0, 0, 0]})},
            "back_plate_rear": {"rotation": kf({0: [0, 0, 0], 0.4: [-4, 0, jit], 0.9: [-4, 0, jit], 1.3: [0, 0, 0]})},
            "leg_front_left": {"rotation": kf({0: [0, 0, 0], 0.4: [-26, 0, 0], 0.9: [-26, 0, 0], 1.3: [0, 0, 0]})},
            "leg_front_left2": {"rotation": kf({0: [0, 0, 0], 0.4: [24, 0, 0], 0.9: [24, 0, 0], 1.3: [0, 0, 0]})},
            "leg_front_right": {"rotation": kf({0: [0, 0, 0], 0.4: [-26, 0, 0], 0.9: [-26, 0, 0], 1.3: [0, 0, 0]})},
            "leg_front_right2": {"rotation": kf({0: [0, 0, 0], 0.4: [24, 0, 0], 0.9: [24, 0, 0], 1.3: [0, 0, 0]})},
            "leg_back_left": {"rotation": kf({0: [0, 0, 0], 0.4: [-8, 0, 0], 0.9: [-8, 0, 0], 1.3: [0, 0, 0]})},
            "leg_back_right": {"rotation": kf({0: [0, 0, 0], 0.4: [-8, 0, 0], 0.9: [-8, 0, 0], 1.3: [0, 0, 0]})},
            "tail": {"rotation": kf({0: [0, 0, 0], 0.4: [-8, 0, 0], 0.9: [-8, 0, 0], 1.3: [0, 0, 0]})},
        },
    }


def status():
    return {
        "animation_length": 1.2,
        "bones": {
            "neck3": {"rotation": kf({0: [0, 0, 0], 0.25: [0, 8, 0], 0.55: [0, -8, 0], 0.85: [0, 5, 0], 1.2: [0, 0, 0]})},
            "head": {"rotation": kf({0: [0, 0, 0], 0.25: [-6, 14, 4], 0.55: [-6, -14, -4], 0.85: [-3, 8, 2], 1.2: [0, 0, 0]})},
            "crest": {"rotation": kf({0: [0, 0, 0], 0.25: [0, 0, -5], 0.55: [0, 0, 5], 0.85: [0, 0, -3], 1.2: [0, 0, 0]})},
            "tail": {"rotation": kf({0: [0, 0, 0], 0.3: [4, -8, 0], 0.7: [4, 8, 0], 1.2: [0, 0, 0]})},
        },
    }


def recoil():
    return {
        "animation_length": 0.6,
        "bones": {
            "body": {"position": kf({0: [0, 0, 0], 0.12: [0, 0.3, 1.8], 0.6: [0, 0, 0]})},
            "torso": {"rotation": kf({0: [0, 0, 0], 0.12: [-6, 0, 0], 0.6: [0, 0, 0]})},
            "neck": {"rotation": kf({0: [0, 0, 0], 0.12: [-7, 0, 0], 0.6: [0, 0, 0]})},
            "head": {"rotation": kf({0: [0, 0, 0], 0.12: [-16, 0, 4], 0.6: [0, 0, 0]})},
            "jaw": {"rotation": kf({0: [0, 0, 0], 0.12: [14, 0, 0], 0.6: [0, 0, 0]})},
            "eyelid_left": {"position": {"0.0": [0, 0, 0], "0.05": [0.12, 0, 0], "0.35": [0.12, 0, 0], "0.4": [0, 0, 0]}},
            "eyelid_right": {"position": {"0.0": [0, 0, 0], "0.05": [-0.12, 0, 0], "0.35": [-0.12, 0, 0], "0.4": [0, 0, 0]}},
        },
    }


def build(model=None):
    anims = {
        "ground_idle": ground_idle(),
        "ground_walk": ground_walk(),
        "ground_run": ground_run(),
        "battle_idle": battle_idle(),
        "blink": blink(),
        "cry": cry(),
        "faint": faint(),
        "sleep": sleep(),
        "physical": physical(),
        "special": special(),
        "status": status(),
        "recoil": recoil(),
    }
    if model is not None:
        names = {b.name for b in model.bones}
        for an, a in anims.items():
            missing = set(a["bones"]) - names
            if missing:
                raise ValueError(f"{an}: unknown bones {sorted(missing)}")
    return {
        "format_version": "1.8.0",
        "animations": {f"animation.{NAME}.{k}": v for k, v in anims.items()},
    }
