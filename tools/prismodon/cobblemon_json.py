"""Cobblemon 1.8 poser + resolver for Prismodon (MoLang poser format)."""

NAME = "prismodon"
TEX = f"cobblemon:textures/pokemon/{NAME}"


def poser():
    look = "q.look('head')"
    blink = f"q.bedrock_quirk('{NAME}', 'blink')"

    def anim(name):
        return f"q.bedrock('{NAME}', '{name}')"

    return {
        "portraitScale": 1.55,
        "portraitTranslation": [-0.55, 2.75, 0],
        "profileScale": 0.5,
        "profileTranslation": [0, 1.0, -6],
        "rootBone": NAME,
        "animations": {
            "faint": f"q.bedrock_primary('{NAME}', 'faint', q.curve('one'))",
            "cry": f"q.bedrock_stateful('{NAME}', 'cry')",
            "recoil": f"q.bedrock_stateful('{NAME}', 'recoil')",
            "physical": f"q.bedrock_primary('{NAME}', 'physical', q.curve('symmetrical_wide'))",
            "special": f"q.bedrock_primary('{NAME}', 'special', q.curve('symmetrical_wide'))",
            "status": f"q.bedrock_primary('{NAME}', 'status', q.curve('symmetrical_wide'))",
        },
        "poses": {
            "battle-standing": {
                "poseTypes": ["STAND"],
                "isBattle": True,
                "animations": [look, anim("battle_idle")],
                "quirks": [blink],
            },
            "standing": {
                "poseTypes": ["STAND", "NONE", "PORTRAIT", "PROFILE", "FLOAT"],
                "isBattle": False,
                "animations": [look, anim("ground_idle")],
                "quirks": [blink],
            },
            "walk": {
                "poseTypes": ["WALK", "SWIM"],
                "condition": "!q.is_sprinting",
                "animations": [look, anim("ground_walk")],
                "quirks": [blink],
            },
            "run": {
                "poseTypes": ["WALK", "SWIM"],
                "condition": "q.is_sprinting",
                "animations": [look, anim("ground_run")],
                "quirks": [blink],
            },
            "sleep": {
                "poseTypes": ["SLEEP"],
                "namedAnimations": {"cry": "q.bedrock_stateful('dummy', 'cry')"},
                "animations": [anim("sleep")],
            },
        },
    }


def resolver():
    return {
        "species": f"cobblemon:{NAME}",
        "order": 0,
        "variations": [
            {
                "aspects": [],
                "poser": f"cobblemon:{NAME}",
                "model": f"cobblemon:{NAME}.geo",
                "texture": f"{TEX}/{NAME}.png",
                "layers": [],
            },
            {
                "aspects": ["shiny"],
                "texture": f"{TEX}/{NAME}_shiny.png",
            },
            {
                "aspects": ["alpha_eyes"],
                "layers": [
                    {
                        "name": "alpha_eyes",
                        "texture": f"{TEX}/{NAME}_alpha.png",
                        "emissive": True,
                    }
                ],
            },
        ],
    }
