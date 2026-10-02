"""
Design data for the Windwave Pokémon (Cobblemon 1.8.1).

Everything that is "game design" lives here so the pack builder stays generic:
stats, typings, abilities, evolution methods, learnsets, spawns and all text.
"""

NAMESPACE = "cobblemon"

# --------------------------------------------------------------------------- shared learnset helpers

EEVEE_EGG = ["captivate", "curse", "detect", "doublekick", "flail", "mudslap", "naturalgift", "synchronoise", "tickle", "wish", "yawn"]
EEVEE_TM = ["alluringvoice", "babydolleyes", "batonpass", "bodyslam", "calmmind", "charm", "covet", "curse", "dig", "doubleedge",
            "echoedvoice", "endure", "facade", "faketears", "focusenergy", "headbutt", "healbell", "helpinghand", "hypervoice",
            "irontail", "laserfocus", "lastresort", "mudslap", "payday", "protect", "raindance", "rest", "retaliate", "roar",
            "shadowball", "sleeptalk", "storedpower", "substitute", "sunnyday", "swift", "takedown", "terablast", "trailblaze",
            "weatherball", "workup"]


def learnset(level, egg=(), tm=(), tutor=(), legacy=(), special=()):
    moves = [f"{lvl}:{m}" for lvl, m in level]
    moves += [f"egg:{m}" for m in egg]
    moves += [f"tm:{m}" for m in sorted(set(tm))]
    moves += [f"tutor:{m}" for m in sorted(set(tutor))]
    moves += [f"legacy:{m}" for m in sorted(set(legacy))]
    moves += [f"special:{m}" for m in special]
    return moves


# --------------------------------------------------------------------------- species

SPECIES = [
    # ======================================================================= EEVEEON
    {
        "id": "eeveeon",
        "dex": 1079,
        "model": "eeveeon",
        "names": {"en": "Eeveeon", "ko": "이브이온"},
        "dex_text": {
            "en": "Said to be the form Eevee takes when it refuses to be swayed by any stone or element. It draws its strength from the bonds it shares with every Eeveelution it has ever met.",
            "ko": "어떤 돌이나 환경에도 휩쓸리지 않고 스스로의 의지로 진화한 이브이의 모습이라고 전해진다. 지금까지 만난 모든 이브이 진화형과의 유대에서 힘을 끌어낸다.",
        },
        "species": {
            "primaryType": "normal",
            "maleRatio": 0.875,
            "height": 11,
            "weight": 320,
            "abilities": ["adaptability", "scrappy", "h:serenegrace"],
            "eggGroups": ["field"],
            "baseStats": {"hp": 95, "attack": 75, "defence": 70, "special_attack": 110, "special_defence": 100, "speed": 75},
            "evYield": {"hp": 0, "attack": 0, "defence": 0, "special_attack": 2, "special_defence": 0, "speed": 0},
            "baseExperienceYield": 184,
            "experienceGroup": "medium_fast",
            "catchRate": 45,
            "eggCycles": 35,
            "baseFriendship": 50,
            "baseScale": 0.5,
            "hitbox": {"width": 2.2, "height": 3.3, "fixed": False},
            "drops": {"amount": 2, "entries": [
                {"item": "cobblemon:silk_scarf", "percentage": 10.0},
                {"item": "cobblemon:normal_gem", "percentage": 5.0},
                {"item": "minecraft:white_wool", "quantityRange": "0-1"},
            ]},
            "riding": {
                "behaviours": {
                    "LAND": {"key": "cobblemon:land/horse", "rideSounds": [],
                             "stats": {"ACCELERATION": "55-75", "JUMP": "45-65", "SKILL": "50-75", "SPEED": "50-70", "STAMINA": "40-65"}},
                },
                "seats": [{"locator": "seat_1"}],
            },
            "behaviour": {
                "resting": {"canSleep": True, "willSleepOnBed": True, "light": "0-15", "drowsyChance": 0.0333, "rouseChance": 0.0042},
                "moving": {"walk": {"walkSpeed": 0.3}, "swim": {"avoidsWater": True}},
                "combat": {"willDefendOwner": True, "willDefendSelf": True, "willFlee": False},
                "herd": {"maxSize": 6, "toleratedLeaders": [{"pokemon": "eeveeon alpha", "tier": 1}]},
            },
        },
        "pre_evolution": "eevee",
        "evolutions": [
            {
                "id": "eevee_eeveeon_gem", "variant": "item_interact", "result": "eeveeon", "consumeHeldItem": False,
                "learnableMoves": ["lastevolution"], "requirements": [], "requiredContext": "cobblemon:normal_gem",
            },
            {
                "id": "eevee_eeveeon_scarf", "variant": "level_up", "result": "eeveeon", "consumeHeldItem": True,
                "learnableMoves": ["lastevolution"],
                "requirements": [
                    {"variant": "friendship", "amount": 200},
                    {"variant": "held_item", "itemCondition": "cobblemon:silk_scarf"},
                ],
            },
            {
                "id": "eevee_eeveeon_lastresort", "variant": "level_up", "result": "eeveeon", "consumeHeldItem": False,
                "learnableMoves": ["lastevolution"],
                "requirements": [
                    {"variant": "level", "minLevel": 30},
                    {"variant": "has_move", "move": "lastresort"},
                ],
                "drops": {"amount": 1, "entries": [{"type": "evolution", "item": "cobblemon:normal_gem", "percentage": 100.0, "requirements": []}]},
            },
        ],
        "moves": learnset(
            level=[(1, "lastevolution"), (1, "tackle"), (1, "tailwhip"), (1, "helpinghand"), (1, "growl"), (1, "covet"),
                   (5, "sandattack"), (10, "quickattack"), (15, "babydolleyes"), (20, "swift"), (25, "bite"),
                   (30, "triattack"), (35, "batonpass"), (40, "hypervoice"), (45, "calmmind"), (50, "boomburst"),
                   (55, "lastresort"), (60, "hyperbeam")],
            egg=EEVEE_EGG,
            tm=EEVEE_TM + ["lastevolution", "triattack", "hyperbeam", "gigaimpact", "psyshock", "dazzlinggleam", "uproar",
                           "snarl", "playrough", "drainingkiss"],
            tutor=["hypervoice", "irontail", "lastresort", "healbell", "shadowball", "swift", "covet", "helpinghand",
                   "hyperbeam", "gigaimpact", "uproar", "boomburst"],
            legacy=["attract", "captivate", "confide", "doubleteam", "frustration", "hiddenpower", "naturalgift", "return",
                    "round", "secretpower", "snore", "swagger", "toxic"],
        ),
        "signature": "lastevolution",
    },

    # ======================================================================= THREISCUE
    {
        "id": "threiscue",
        "dex": 1080,
        "model": "threiscue",
        "names": {"en": "Threiscue", "ko": "트리큐보"},
        "dex_text": {
            "en": "Each of the three ice cubes stacked on its head has a face of its own. When all three glare in the same direction, they fire freezing beams strong enough to stop a blizzard in its tracks.",
            "ko": "머리 위에 쌓인 세 개의 얼음 큐브에는 저마다 다른 얼굴이 있다. 세 얼굴이 같은 방향을 노려보면 눈보라마저 멈추게 하는 냉동 광선을 쏜다.",
        },
        "species": {
            "primaryType": "ice",
            "secondaryType": "water",
            "maleRatio": 0.5,
            "height": 21,
            "weight": 1500,
            "abilities": ["icebody", "swiftswim", "h:slushrush"],
            "eggGroups": ["water_1", "field"],
            "baseStats": {"hp": 95, "attack": 80, "defence": 115, "special_attack": 110, "special_defence": 100, "speed": 50},
            "evYield": {"hp": 0, "attack": 0, "defence": 1, "special_attack": 2, "special_defence": 0, "speed": 0},
            "baseExperienceYield": 190,
            "experienceGroup": "slow",
            "catchRate": 45,
            "eggCycles": 25,
            "baseFriendship": 50,
            "baseScale": 0.42,
            "hitbox": {"width": 3.0, "height": 6.6, "fixed": False},
            "drops": {"amount": 4, "entries": [
                {"item": "minecraft:blue_ice", "quantityRange": "1-2"},
                {"item": "minecraft:feather", "quantityRange": "0-2"},
                {"item": "minecraft:cod", "quantityRange": "0-2"},
                {"item": "cobblemon:never_melt_ice", "percentage": 5.0},
                {"item": "cobblemon:aspear_berry", "percentage": 5.0},
            ]},
            "lightingData": {"lightLevel": 8, "liquidGlowMode": "BOTH"},
            "behaviour": {
                "resting": {"canSleep": True, "light": "0-4", "drowsyChance": 0.0333, "rouseChance": 0.0042},
                "moving": {"walk": {"walkSpeed": 0.18}, "swim": {"swimSpeed": 0.25, "canBreatheUnderwater": True, "canWalkOnWater": False}},
                "combat": {"willDefendOwner": True, "willDefendSelf": True, "willFlee": False},
                "herd": {"maxSize": 8, "toleratedLeaders": [{"pokemon": "threiscue alpha", "tier": 1}, {"pokemon": "empoleon", "tier": 2}]},
            },
        },
        "pre_evolution": "eiscue",
        "evolutions": [
            {
                "id": "eiscue_threiscue_stone", "variant": "item_interact", "result": "threiscue", "consumeHeldItem": False,
                "learnableMoves": ["triplefreezebeam"], "requirements": [], "requiredContext": "cobblemon:ice_stone",
            },
            {
                "id": "eiscue_threiscue_blizzard", "variant": "level_up", "result": "threiscue", "consumeHeldItem": False,
                "learnableMoves": ["triplefreezebeam"],
                "requirements": [
                    {"variant": "level", "minLevel": 45},
                    {"variant": "weather", "isRaining": True},
                    {"variant": "biome", "biomeCondition": "#cobblemon:is_freezing"},
                ],
            },
            {
                "id": "eiscue_threiscue_ice", "variant": "level_up", "result": "threiscue", "consumeHeldItem": True,
                "learnableMoves": ["triplefreezebeam"],
                "requirements": [
                    {"variant": "level", "minLevel": 40},
                    {"variant": "held_item", "itemCondition": "cobblemon:never_melt_ice"},
                ],
            },
        ],
        "moves": learnset(
            level=[(1, "triplefreezebeam"), (1, "powdersnow"), (1, "tackle"), (1, "waterpulse"), (6, "mist"),
                   (12, "weatherball"), (18, "icywind"), (24, "headbutt"), (30, "amnesia"), (36, "freezedry"),
                   (42, "snowscape"), (48, "auroraveil"), (54, "surf"), (60, "blizzard"), (66, "hydropump")],
            egg=["aquaring", "bellydrum", "doubleedge", "headsmash", "iciclecrash", "soak"],
            tm=["agility", "amnesia", "auroraveil", "avalanche", "blizzard", "bodyslam", "brine", "chillingwater", "dive",
                "doubleedge", "endure", "facade", "featherdance", "flipturn", "gigaimpact", "hail", "headbutt", "hydropump",
                "hyperbeam", "icebeam", "icepunch", "icespinner", "iciclespear", "icywind", "irondefense", "ironhead",
                "liquidation", "protect", "raindance", "reflect", "rest", "reversal", "sleeptalk", "snowscape", "substitute",
                "surf", "takedown", "terablast", "waterfall", "waterpulse", "weatherball", "whirlpool", "zenheadbutt",
                "triplefreezebeam", "scald", "frostbreath", "calmmind", "lightscreen"],
            tutor=["dive", "flipturn", "gigaimpact", "hyperbeam", "icebeam", "icepunch", "icywind", "irondefense", "ironhead",
                   "liquidation", "rest", "sleeptalk", "waterpulse", "zenheadbutt"],
            legacy=["attract", "round", "snore"],
        ),
        "signature": "triplefreezebeam",
    },

    # ======================================================================= CRYPTONIX
    {
        "id": "cryptonix",
        "dex": 1081,
        "model": "cryptonix",
        "names": {"en": "Cryptonix", "ko": "크립토닉스"},
        "dex_text": {
            "en": "An Onix that slept for centuries beneath an ancient graveyard. Gravestones grew from its body, and the restless spirits of the crypt now glow in the gaps between its stones.",
            "ko": "오래된 묘지 아래에서 수백 년 동안 잠들어 있던 롱스톤. 몸에서 묘비가 자라났으며, 묘지를 떠돌던 혼이 바위 틈새에서 희미하게 빛난다.",
        },
        "species": {
            "primaryType": "rock",
            "secondaryType": "ghost",
            "maleRatio": 0.5,
            "height": 95,
            "weight": 4500,
            "abilities": ["cursedbody", "sturdy", "h:rockhead"],
            "eggGroups": ["mineral"],
            "baseStats": {"hp": 85, "attack": 110, "defence": 165, "special_attack": 55, "special_defence": 90, "speed": 30},
            "evYield": {"hp": 0, "attack": 0, "defence": 2, "special_attack": 0, "special_defence": 0, "speed": 0},
            "baseExperienceYield": 179,
            "experienceGroup": "medium_fast",
            "catchRate": 25,
            "eggCycles": 25,
            "baseFriendship": 50,
            "baseScale": 0.5,
            "hitbox": {"width": 4.4, "height": 7.2, "fixed": False},
            "drops": {"amount": 6, "entries": [
                {"item": "minecraft:cobblestone", "quantityRange": "1-3"},
                {"item": "minecraft:soul_sand", "quantityRange": "0-2"},
                {"item": "cobblemon:hard_stone", "percentage": 5.0},
                {"item": "cobblemon:spell_tag", "percentage": 5.0},
                {"item": "cobblemon:reaper_cloth", "percentage": 2.5},
                {"item": "cobblemon:kasib_berry", "percentage": 2.5},
            ]},
            "lightingData": {"lightLevel": 7, "liquidGlowMode": "LAND"},
            "riding": {
                "behaviours": {
                    "LAND": {"key": "cobblemon:land/horse", "rideSounds": [],
                             "stats": {"ACCELERATION": "20-40", "JUMP": "10-25", "SKILL": "30-55", "SPEED": "30-50", "STAMINA": "60-90"}},
                },
                "seats": [
                    {"locator": "seat_1"},
                    {"locator": "seat_2", "condition": "q.entity.is_alpha"},
                ],
            },
            "behaviour": {
                "resting": {"canSleep": True, "light": "0-7", "times": ["night"], "drowsyChance": 0.0014, "rouseChance": 0.0042},
                "moving": {"walk": {"walkSpeed": 0.3}, "swim": {"avoidsWater": True, "canSwimInLava": True}},
                "combat": {"willDefendSelf": True, "willDefendOwner": True, "willFlee": False},
                "fireImmune": True,
                "herd": {"maxSize": 4, "toleratedLeaders": [{"pokemon": "cryptonix alpha", "tier": 1}]},
            },
        },
        "pre_evolution": "onix",
        "evolutions": [
            {
                "id": "onix_cryptonix_trade", "variant": "trade", "result": "cryptonix", "consumeHeldItem": True,
                "learnableMoves": ["graveuprising"],
                "requirements": [{"variant": "held_item", "itemCondition": "cobblemon:reaper_cloth"}],
            },
            {
                "id": "onix_cryptonix_cloth", "variant": "item_interact", "result": "cryptonix", "consumeHeldItem": False,
                "learnableMoves": ["graveuprising"],
                "requirements": [{"variant": "time_range", "range": "night"}],
                "requiredContext": "cobblemon:reaper_cloth",
            },
            {
                "id": "onix_cryptonix_crypt", "variant": "level_up", "result": "cryptonix", "consumeHeldItem": False,
                "learnableMoves": ["graveuprising"],
                "requirements": [
                    {"variant": "level", "minLevel": 40},
                    {"variant": "any", "possibilities": [
                        {"variant": "structure", "structureCondition": "minecraft:ancient_city"},
                        {"variant": "biome", "biomeCondition": "#cobblemon:is_deep_dark"},
                    ]},
                ],
                "drops": {"amount": 1, "entries": [{"type": "evolution", "item": "minecraft:soul_sand", "percentage": 100.0, "requirements": []}]},
            },
        ],
        "moves": learnset(
            level=[(1, "graveuprising"), (1, "astonish"), (1, "mudsport"), (1, "tackle"), (1, "harden"), (1, "bind"),
                   (1, "rockthrow"), (4, "smackdown"), (8, "rockpolish"), (12, "shadowsneak"), (16, "curse"),
                   (20, "rockslide"), (24, "screech"), (28, "hex"), (32, "stealthrock"), (36, "shadowclaw"),
                   (40, "sandstorm"), (44, "phantomforce"), (48, "poltergeist"), (52, "stoneedge"), (56, "doubleedge"),
                   (60, "destinybond")],
            egg=["block", "defensecurl", "dragontail", "flail", "headsmash", "rollout", "rototiller", "wideguard"],
            tm=["ancientpower", "bind", "block", "bodypress", "bodyslam", "breakingswipe", "brutalswing", "bulldoze",
                "curse", "dig", "doubleedge", "dragondance", "dragonpulse", "dragontail", "drillrun", "earthpower",
                "earthquake", "endure", "explosion", "facade", "flashcannon", "gyroball", "headbutt", "heavyslam",
                "highhorsepower", "ironhead", "irontail", "meteorbeam", "mudslap", "payback", "protect", "psychup", "rest",
                "roar", "rockblast", "rockclimb", "rockpolish", "rockslide", "rocksmash", "rocktomb", "rollout", "sandstorm",
                "sandtomb", "scaryface", "scorchingsands", "screech", "selfdestruct", "sleeptalk", "smackdown",
                "stealthrock", "stompingtantrum", "stoneedge", "strength", "substitute", "sunnyday", "taunt", "terablast",
                "torment", "twister", "graveuprising", "shadowball", "shadowclaw", "phantomforce", "poltergeist", "hex",
                "willowisp", "spite", "nightshade", "painsplit", "hyperbeam", "gigaimpact", "trick", "darkpulse"],
            tutor=["block", "bodypress", "bulldoze", "dragonpulse", "earthpower", "earthquake", "irontail", "ironhead",
                   "meteorbeam", "rest", "rockslide", "rocksmash", "sleeptalk", "stealthrock", "stoneedge", "shadowball",
                   "painsplit", "spite"],
            legacy=["attract", "confide", "doubleteam", "frustration", "hiddenpower", "return", "round", "secretpower",
                    "snore", "swagger", "toxic"],
        ),
        "signature": "graveuprising",
    },

    # ======================================================================= AVALOTT
    {
        "id": "avalott",
        "dex": 1082,
        "model": "avalott",
        "names": {"en": "Avalott", "ko": "아발롯"},
        "dex_text": {
            "en": "It shed most of its ice after being traded alongside a Frigibax, growing a bladed sail that vents its heat. When threatened, it curls up and spins like a top, slicing everything around it.",
            "ko": "드니차와 함께 통신교환되면서 얼음 대부분을 벗어 던지고, 열을 식히는 칼날 돛이 자라났다. 위협을 받으면 몸을 말아 팽이처럼 회전하며 주변을 모두 베어 버린다.",
        },
        "species": {
            "primaryType": "steel",
            "secondaryType": "ice",
            "maleRatio": 0.5,
            "height": 16,
            "weight": 2600,
            "abilities": ["sharpness", "icebody", "h:sturdy"],
            "eggGroups": ["monster", "mineral"],
            "baseStats": {"hp": 75, "attack": 125, "defence": 140, "special_attack": 45, "special_defence": 70, "speed": 65},
            "evYield": {"hp": 0, "attack": 2, "defence": 0, "special_attack": 0, "special_defence": 0, "speed": 0},
            "baseExperienceYield": 180,
            "experienceGroup": "medium_fast",
            "catchRate": 55,
            "eggCycles": 20,
            "baseFriendship": 50,
            "baseScale": 0.5,
            "hitbox": {"width": 3.2, "height": 4.4, "fixed": False},
            "drops": {"amount": 3, "entries": [
                {"item": "minecraft:iron_nugget", "quantityRange": "1-4"},
                {"item": "minecraft:packed_ice", "quantityRange": "0-1"},
                {"item": "cobblemon:metal_coat", "percentage": 5.0},
                {"item": "cobblemon:never_melt_ice", "percentage": 5.0},
                {"item": "cobblemon:babiri_berry", "percentage": 2.5},
            ]},
            "behaviour": {
                "resting": {"canSleep": True, "light": "0-4", "drowsyChance": 0.0333, "rouseChance": 0.0042},
                "moving": {"walk": {"walkSpeed": 0.24}, "swim": {"swimSpeed": 0.1, "canWalkOnWater": True}},
                "combat": {"willDefendSelf": True, "willDefendOwner": True, "willFlee": False},
                "herd": {"maxSize": 6, "toleratedLeaders": [{"pokemon": "avalott alpha", "tier": 1}, {"pokemon": "avalugg alpha", "tier": 2}]},
            },
            "ai": [{"type": "apply_behaviours", "behaviours": ["cobblemon:fights_melee"]}],
        },
        "pre_evolution": "bergmite",
        "evolutions": [
            {
                "id": "bergmite_avalott_trade", "variant": "trade", "result": "avalott", "consumeHeldItem": False,
                "learnableMoves": ["frostsaw"], "requirements": [], "requiredContext": "frigibax",
                "drops": {"amount": 1, "entries": [{"type": "evolution", "item": "minecraft:blue_ice", "percentage": 100.0, "requirements": []}]},
            },
            {
                "id": "bergmite_avalott_link", "variant": "item_interact", "result": "avalott", "consumeHeldItem": False,
                "learnableMoves": ["frostsaw"],
                "requirements": [{"variant": "party_member", "target": "frigibax", "contains": True}],
                "requiredContext": "cobblemon:link_cable",
                "drops": {"amount": 1, "entries": [{"type": "evolution", "item": "minecraft:blue_ice", "percentage": 100.0, "requirements": []}]},
            },
            {
                "id": "bergmite_avalott_coat", "variant": "item_interact", "result": "avalott", "consumeHeldItem": False,
                "learnableMoves": ["frostsaw"],
                "requirements": [
                    {"variant": "level", "minLevel": 30},
                    {"variant": "biome", "biomeCondition": "#cobblemon:is_freezing"},
                ],
                "requiredContext": "cobblemon:metal_coat",
            },
        ],
        "moves": learnset(
            level=[(1, "frostsaw"), (1, "harden"), (1, "rapidspin"), (1, "metalclaw"), (3, "tackle"), (6, "powdersnow"),
                   (9, "curse"), (12, "icywind"), (15, "protect"), (18, "avalanche"), (21, "icefang"), (24, "irondefense"),
                   (27, "icespinner"), (30, "recover"), (33, "ironhead"), (36, "crunch"), (41, "iciclecrash"),
                   (46, "swordsdance"), (51, "heavyslam")],
            egg=["auroraveil", "barrier", "mirrorcoat", "mist", "sharpen"],
            tm=["afteryou", "auroraveil", "avalanche", "blizzard", "bodyslam", "bulldoze", "chillingwater", "crunch",
                "curse", "doubleedge", "endure", "facade", "flash", "frostbreath", "gyroball", "hail", "iceball", "icebeam",
                "icefang", "icespinner", "iciclespear", "icywind", "irondefense", "protect", "raindance", "rest",
                "rockpolish", "rockslide", "rocksmash", "rocktomb", "safeguard", "sleeptalk", "snowscape", "stoneedge",
                "strength", "substitute", "takedown", "terablast", "frostsaw", "ironhead", "flashcannon", "smartstrike",
                "heavyslam", "swordsdance", "steelbeam", "metalclaw", "aerialace", "xscissor", "bodypress", "gigaimpact",
                "hyperbeam", "bulletpunch"],
            tutor=["afteryou", "bulldoze", "iceball", "icebeam", "icefang", "icywind", "irondefense", "ironhead", "rest",
                   "rockslide", "rocksmash", "sleeptalk", "stoneedge", "gigaimpact", "hyperbeam"],
            legacy=["attract", "confide", "doubleteam", "frustration", "hiddenpower", "return", "round", "secretpower",
                    "snore", "swagger", "toxic"],
        ),
        "signature": "frostsaw",
    },

    # ======================================================================= CLEAWEED
    {
        "id": "cleaweed",
        "dex": 1083,
        "model": "cleaweed",
        "names": {"en": "Cleaweed", "ko": "클리위드"},
        "dex_text": {
            "en": "A Skrelp that grew up in clean water. It weaves its long leaves into nets to scoop up polluted sludge and break it down. The more it cleans, the greener its body becomes.",
            "ko": "깨끗한 물에서 자란 수레기. 긴 잎을 엮어 그물을 만들고 오염된 찌꺼기를 건져 분해한다. 청소를 많이 할수록 몸빛이 더욱 초록색이 된다.",
        },
        "species": {
            "primaryType": "water",
            "secondaryType": "dragon",
            "maleRatio": 0.5,
            "height": 19.6,
            "weight": 1120,
            "abilities": ["purify", "adaptability", "h:regenerator"],
            "eggGroups": ["water_1", "dragon"],
            "baseStats": {"hp": 80, "attack": 70, "defence": 95, "special_attack": 107, "special_defence": 113, "speed": 45},
            "evYield": {"hp": 0, "attack": 0, "defence": 0, "special_attack": 0, "special_defence": 2, "speed": 0},
            "baseExperienceYield": 173,
            "experienceGroup": "medium_fast",
            "catchRate": 55,
            "eggCycles": 20,
            "baseFriendship": 50,
            "baseScale": 0.85,
            "hitbox": {"width": 1.4, "height": 3.1, "fixed": False},
            "drops": {"amount": 3, "entries": [
                {"item": "minecraft:kelp", "quantityRange": "1-3"},
                {"item": "minecraft:seagrass", "quantityRange": "0-2"},
                {"item": "cobblemon:mystic_water", "percentage": 5.0},
                {"item": "cobblemon:miracle_seed", "percentage": 5.0},
                {"item": "cobblemon:pecha_berry", "percentage": 5.0},
            ]},
            "riding": {
                "behaviours": {
                    "LAND": {"key": "cobblemon:land/horse", "rideSounds": [], "canJump": False, "canSprint": False,
                             "stats": {"ACCELERATION": "10-40", "JUMP": "10-40", "SKILL": "60-80", "SPEED": "10-30", "STAMINA": "20-40"}},
                    "LIQUID": {"key": "cobblemon:liquid/dolphin", "rideSounds": [
                        {"muffleEnabled": True, "pitchExpr": "math.max(1.0 ,0.2 + math.pow(math.min(q.ride_velocity() / 1.5, 1.0),2))",
                         "playForNonPassengers": False, "playForPassengers": True,
                         "soundLocation": "cobblemon:ride.loop.water_surface.stereo",
                         "volumeExpr": "math.pow(math.min(q.ride_velocity() / 1.5, 1.0),2)"},
                        {"muffleEnabled": True, "pitchExpr": "math.max(1.0 ,0.2 + math.pow(math.min(q.ride_velocity() / 1.5, 1.0),2))",
                         "playForNonPassengers": True, "playForPassengers": False,
                         "soundLocation": "cobblemon:ride.loop.water_surface.mono", "submerged": False,
                         "volumeExpr": "math.pow(math.min(q.ride_velocity() / 1.5, 1.0),2)"},
                        {"muffleEnabled": True, "pitchExpr": "math.max(1.0 ,0.2 + math.pow(math.min(q.ride_velocity() / 1.5, 1.0),2))",
                         "playForNonPassengers": False, "playForPassengers": True,
                         "soundLocation": "cobblemon:ride.loop.underwater.stereo", "submerged": True,
                         "volumeExpr": "math.pow(math.min(q.ride_velocity() / 1.5, 1.0),2)"},
                    ],
                               "stats": {"ACCELERATION": "45-60", "JUMP": "30-45", "SKILL": "70-95", "SPEED": "50-70", "STAMINA": "50-70"}},
                },
                "seats": [{"locator": "seat_1"}],
            },
            "behaviour": {
                "resting": {"canSleep": True, "light": "0-15", "drowsyChance": 0.0333, "rouseChance": 0.0042},
                "moving": {"walk": {"walkSpeed": 0.2}, "swim": {"canBreatheUnderwater": True, "swimSpeed": 0.3}},
                "combat": {"willDefendSelf": True, "willDefendOwner": True, "willFlee": False},
                "herd": {"maxSize": 6, "toleratedLeaders": [{"pokemon": "cleaweed alpha", "tier": 1}, {"pokemon": "dragalge alpha", "tier": 2}]},
            },
            "ai": [{
                "type": "cobblemon:add_tasks_to_activity",
                "activity": "idle",
                "tasksByPriority": {"7": [{
                    "type": "cobblemon:hate_entity",
                    "entityCondition": "q.entity.is_pokemon && (q.entity.species.identifier == 'cobblemon:trubbish' || q.entity.species.identifier == 'cobblemon:garbodor' || q.entity.species.identifier == 'cobblemon:grimer' || q.entity.species.identifier == 'cobblemon:muk')",
                }]},
            }],
        },
        "pre_evolution": "skrelp",
        "evolutions": [
            {
                "id": "skrelp_cleaweed_stone", "variant": "item_interact", "result": "cleaweed", "consumeHeldItem": False,
                "learnableMoves": ["cleansingnet"],
                "requirements": [{"variant": "any", "possibilities": [
                    {"variant": "biome", "biomeCondition": "#cobblemon:is_ocean"},
                    {"variant": "biome", "biomeCondition": "#cobblemon:is_freshwater"},
                    {"variant": "biome", "biomeCondition": "#cobblemon:is_swamp"},
                    {"variant": "biome", "biomeCondition": "#cobblemon:is_coast"},
                ]}],
                "requiredContext": "cobblemon:leaf_stone",
            },
            {
                "id": "skrelp_cleaweed_cleanup", "variant": "level_up", "result": "cleaweed", "consumeHeldItem": False,
                "learnableMoves": ["cleansingnet"],
                "requirements": [
                    {"variant": "level", "minLevel": 30},
                    {"variant": "defeat", "target": "type=poison", "amount": 10},
                ],
            },
            {
                "id": "skrelp_cleaweed_pulse", "variant": "level_up", "result": "cleaweed", "consumeHeldItem": False,
                "learnableMoves": ["cleansingnet"],
                "requirements": [{"variant": "use_move", "move": "waterpulse", "amount": 20}],
            },
        ],
        "moves": learnset(
            level=[(1, "cleansingnet"), (1, "tackle"), (1, "smokescreen"), (1, "feintattack"), (1, "bubble"),
                   (1, "twister"), (5, "acid"), (10, "watergun"), (15, "tailwhip"), (20, "doubleteam"), (25, "aquaring"),
                   (30, "waterpulse"), (35, "gigadrain"), (40, "dragonpulse"), (45, "aquatail"), (50, "sludgebomb"),
                   (55, "hydropump"), (60, "dracometeor")],
            egg=["acidarmor", "camouflage", "dragontail", "haze", "twister"],
            tm=["acidspray", "aquatail", "bounce", "chillingwater", "dive", "doubleteam", "dragonpulse", "dragontail",
                "endure", "facade", "flipturn", "gunkshot", "hail", "haze", "hydropump", "icywind", "irontail",
                "liquidation", "muddywater", "mudshot", "mudslap", "outrage", "playrough", "poisontail", "protect",
                "raindance", "rest", "scaleshot", "scaryface", "shadowball", "shockwave", "sleeptalk", "sludgebomb",
                "sludgewave", "snowscape", "spite", "substitute", "surf", "takedown", "terablast", "thief", "thunderbolt",
                "toxic", "toxicspikes", "twister", "venomdrench", "venoshock", "waterfall", "waterpulse", "whirlpool",
                "cleansingnet", "dracometeor", "gigadrain", "energyball", "grassknot", "scald", "hyperbeam", "gigaimpact",
                "dragondance", "leafstorm"],
            tutor=["aquatail", "dive", "dragonpulse", "hydropump", "icywind", "irontail", "liquidation", "outrage", "rest",
                   "sleeptalk", "sludgebomb", "surf", "waterpulse", "dracometeor", "gigadrain"],
            legacy=["attract", "confide", "frustration", "hiddenpower", "return", "round", "secretpower", "snore", "swagger"],
        ),
        "signature": "cleansingnet",
    },
]


# --------------------------------------------------------------------------- signature moves / ability text

MOVE_TEXT = {
    "lastevolution": {
        "en": ("Last Evolution", "The user unleashes the power of every evolution it could have become. Its power rises for each different Eevee or Eeveelution in the user's party."),
        "ko": ("라스트에볼루션", "될 수 있었던 모든 진화의 힘을 해방하여 공격한다. 파티에 있는 서로 다른 이브이와 이브이 진화형의 수만큼 위력이 올라간다."),
    },
    "triplefreezebeam": {
        "en": ("Triple Freeze Beam", "The three ice cubes on the user's head each fire a freezing beam. This move hits three times in a row and may freeze the target."),
        "ko": ("트리플프리즈빔", "머리 위의 세 얼음 큐브에서 냉동 광선을 쏜다. 3회 연속으로 공격하며 상대를 얼음 상태로 만들 때가 있다."),
    },
    "graveuprising": {
        "en": ("Grave Uprising", "Gravestones and spectral hands burst out of the ground and seize the target. The target can no longer flee or be switched out."),
        "ko": ("무덤봉기", "땅속에서 묘비와 망령의 손이 솟아나 상대를 붙잡는다. 상대는 도망치거나 교체할 수 없게 된다."),
    },
    "frostsaw": {
        "en": ("Frostsaw", "The user tucks in its limbs and spins like a saw, slicing the target with its frozen blade. Critical hits land more easily. It also blows away hazards and binding on the user's side and may freeze the target."),
        "ko": ("서리톱날", "팔다리를 넣고 톱처럼 회전하여 얼어붙은 칼날로 벤다. 급소에 맞기 쉽다. 자신의 진영의 설치 기술과 조이기 효과를 날려 버리며 상대를 얼음 상태로 만들 때가 있다."),
    },
    "cleansingnet": {
        "en": ("Cleansing Net", "The user casts a net of woven leaves that scoops away the target's lingering power. It resets the target's stat changes and cures the user's status condition."),
        "ko": ("정화그물", "엮은 잎으로 만든 그물을 던져 공격한다. 상대의 능력 변화를 원래대로 되돌리고 자신의 상태 이상을 회복한다."),
    },
}

ABILITY_TEXT = {
    "purify": {
        "en": ("Purify", "Poison-type moves become Water-type moves and are powered up. The Pokémon also cannot be poisoned."),
        "ko": ("정화", "독 타입 기술이 물 타입이 되며 위력이 올라간다. 또한 독 상태가 되지 않는다."),
    },
}

EXTRA_LANG = {
    "en": {
        "cobblemon.ui.pokedex.region.windwave": "Windwave",
        "cobblemon.habitat.windwave_sanctuary.name": "Windwave Sanctuary",
        "cobblemon.battle.activate.purify": "%1$s's Purify washed the poison away!",
    },
    "ko": {
        "cobblemon.ui.pokedex.region.windwave": "윈드웨이브",
        "cobblemon.habitat.windwave_sanctuary.name": "윈드웨이브 성역",
        "cobblemon.battle.activate.purify": "%1$s의 정화로 독이 씻겨 나갔다!",
    },
}
