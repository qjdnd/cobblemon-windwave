#!/usr/bin/env python3
"""Cobblemon 1.8.2에서 새로 구현된 포켓몬 17종을 Cobblemon 1.8.1용 리소스팩+데이터팩으로 옮긴다.

사용법:
    # Cobblemon 1.8.2 소스 받기 (필요한 폴더만)
    git clone --filter=blob:none --no-checkout --depth 1 --branch 1.8.2 \
        https://gitlab.com/cable-mc/cobblemon.git cobblemon-1.8.2
    git -C cobblemon-1.8.2 sparse-checkout set --no-cone /LICENSE \
        /common/src/main/resources/data/ /common/src/main/resources/assets/cobblemon/lang/ \
        /common/src/main/resources/assets/cobblemon/bedrock/pokemon/ \
        /common/src/main/resources/assets/cobblemon/textures/pokemon/
    git -C cobblemon-1.8.2 checkout 1.8.2

    python3 tools/backport_pokemon.py cobblemon-1.8.2   # pack-1.8.2/ 다시 만들고 검사 후 dist/ zip 생성
    python3 tools/backport_pokemon.py --check           # pack-1.8.2/ 참조 검사만
    python3 tools/backport_pokemon.py --zip             # pack-1.8.2/ 로 dist/ zip만 다시 생성
"""
import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK = ROOT / "pack-1.8.2"
DIST = ROOT / "dist"
ZIP_PREFIX = "cobblemon-windwave-1.8.2-pokemon"

# Minecraft 1.21.1
RESOURCE_PACK_FORMAT = 34
DATA_PACK_FORMAT = 48
DESCRIPTION = "Cobblemon 1.8.2 new Pokémon (17) for Cobblemon 1.8.1"

# (에셋 폴더, species 폴더, 종 이름) - CHANGELOG.md 1.8.2 "Pokémon Added"
SPECIES = [
    ("0412_burmy", "generation4", "burmy"),
    ("0413_wormadam", "generation4", "wormadam"),
    ("0414_mothim", "generation4", "mothim"),
    ("0459_snover", "generation4", "snover"),
    ("0460_abomasnow", "generation4", "abomasnow"),
    ("0535_tympole", "generation5", "tympole"),
    ("0536_palpitoad", "generation5", "palpitoad"),
    ("0537_seismitoad", "generation5", "seismitoad"),
    ("0694_helioptile", "generation6", "helioptile"),
    ("0695_heliolisk", "generation6", "heliolisk"),
    ("0736_grubbin", "generation7", "grubbin"),
    ("0737_charjabug", "generation7", "charjabug"),
    ("0738_vikavolt", "generation7", "vikavolt"),
    ("0774_minior", "generation7", "minior"),
    ("0890_eternatus", "generation8", "eternatus"),
    ("0971_greavard", "generation9", "greavard"),
    ("0972_houndstone", "generation9", "houndstone"),
]

# 1.8.2에서 바뀐 파일 중 위 포켓몬을 위해 필요한 것
EXTRA_DATA = [
    # 메테노 코어 색 폼 (1.8.2에서 기본값 red -> random, 도감 폼 목록 변경)
    "species_features/core_color.json",
    "dex_entries/pokemon/alola/minior.json",
    # 1.8.2에서 새 포켓몬이 추가된 서식지(habitat) 스폰 풀
    "habitat_pools/deep_roots.json",
    "habitat_pools/lost_cave_ruins.json",
    "habitat_pools/lush_peat_bog.json",
    "habitat_pools/meteorite_impact.json",
    "habitat_pools/parched_peat_bog.json",
    "habitat_pools/root_nursery.json",
    "habitat_pools/sandpit_clearing.json",
    "habitat_pools/skeletal_fall.json",
    "habitat_pools/snowy_grotto.json",
    "habitat_pools/sunscorched_clearing.json",
]

# 1.8.1 언어 파일에 없는 키 (1.8.2 메테노 빨간색 코어 폼 설명)
LANG_KEYS = ["cobblemon.species.minior-red.desc"]
# 1.8.2 ko_kr에도 아직 없는 키는 다른 코어 설명과 같은 문장으로 채운다
LANG_FALLBACK = {
    "ko_kr": {
        "cobblemon.species.minior-red.desc":
            "겉껍질이 벗겨진 모습. 코어의 색이 다른 이유는 먹은 먹이의 성분이 다르기 때문이다.",
    },
}

BEDROCK_KINDS = ["animations", "models", "posers", "resolvers"]


def copy_tree(src: Path, dst: Path) -> int:
    if not src.is_dir():
        sys.exit(f"없음: {src}")
    count = 0
    for f in sorted(src.rglob("*")):
        if f.is_file():
            out = dst / f.relative_to(src)
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, out)
            count += 1
    return count


def copy_file(src: Path, dst: Path):
    if not src.is_file():
        sys.exit(f"없음: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def mark_implemented(path: Path):
    """1.8.2 종 파일 일부(턱지충이 계열, 망망이, 묘두기)에 implemented가 빠져 있어 도감에 미구현으로 나온다."""
    text = path.read_text(encoding="utf-8")
    if json.loads(text).get("implemented") is True:
        return False
    if '"implemented"' in text:
        text = re.sub(r'"implemented"\s*:\s*false', '"implemented": true', text, count=1)
    else:
        text = re.sub(r"^\{\s*\n", '{\n  "implemented": true,\n', text, count=1)
    if json.loads(text).get("implemented") is not True:
        sys.exit(f"implemented 설정 실패: {path}")
    path.write_text(text, encoding="utf-8")
    return True


def import_from(cobblemon: Path):
    res = cobblemon / "common/src/main/resources"
    assets = res / "assets/cobblemon"
    data = res / "data/cobblemon"
    if not (data / "species").is_dir():
        sys.exit(f"Cobblemon 소스가 아님: {cobblemon}")

    for sub in ("assets", "data"):
        shutil.rmtree(PACK / sub, ignore_errors=True)
    out_assets = PACK / "assets/cobblemon"
    out_data = PACK / "data/cobblemon"

    patched = []
    for folder, gen, name in SPECIES:
        n = 0
        for kind in BEDROCK_KINDS:
            n += copy_tree(assets / "bedrock/pokemon" / kind / folder,
                           out_assets / "bedrock/pokemon" / kind / folder)
        n += copy_tree(assets / "textures/pokemon" / folder, out_assets / "textures/pokemon" / folder)

        species = out_data / "species" / gen / f"{name}.json"
        copy_file(data / "species" / gen / f"{name}.json", species)
        if mark_implemented(species):
            patched.append(name)

        spawn = data / "spawn_pool_world" / f"{folder}.json"
        if spawn.is_file():  # 무한다이노는 야생 스폰 없음
            copy_file(spawn, out_data / "spawn_pool_world" / spawn.name)
        for herd in sorted((data / "spawn_pool_world/herds").glob(f"{folder}_*.json")):
            copy_file(herd, out_data / "spawn_pool_world/herds" / herd.name)
        print(f"  {folder}: 에셋 {n}개")

    for rel in EXTRA_DATA:
        copy_file(data / rel, out_data / rel)

    for lang in ("en_us", "ko_kr"):
        source = json.loads((assets / "lang" / f"{lang}.json").read_text(encoding="utf-8"))
        entries = {}
        for key in LANG_KEYS:
            value = source.get(key) or LANG_FALLBACK.get(lang, {}).get(key)
            if value:
                entries[key] = value
        if entries:
            out = out_assets / "lang" / f"{lang}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    copy_file(cobblemon / "LICENSE", PACK / "LICENSE-Cobblemon.txt")
    if patched:
        print("implemented: true 추가:", ", ".join(patched))


def check() -> bool:
    """리졸버/포저/애니메이션/텍스처/스폰 참조가 팩 안(또는 Cobblemon 기본 파일)에서 풀리는지 검사."""
    errors = []
    assets = PACK / "assets/cobblemon"
    data = PACK / "data/cobblemon"
    bedrock = assets / "bedrock/pokemon"

    for f in sorted(PACK.rglob("*.json")):
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except ValueError as e:
            errors.append(f"JSON 오류 {f.relative_to(PACK)}: {e}")

    models = {}
    for f in bedrock.glob("models/*/*.geo.json"):
        geo = json.loads(f.read_text(encoding="utf-8"))
        for g in geo["minecraft:geometry"]:
            models[g["description"]["identifier"].removeprefix("geometry.")] = {
                b["name"] for b in g.get("bones", [])}
    animations = {}
    for f in bedrock.glob("animations/*/*.animation.json"):
        for full, anim in json.loads(f.read_text(encoding="utf-8"))["animations"].items():
            group, _, anim_name = full.removeprefix("animation.").partition(".")
            animations.setdefault(group, {})[anim_name] = anim
    posers = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in bedrock.glob("posers/*/*.json")}

    anim_call = re.compile(r"q\.bedrock(?:_primary|_quirk|_stateful)?\(\s*'([^']+)'\s*,\s*'([^']+)'")
    for name, poser in posers.items():
        text = json.dumps(poser)
        for group, anim_name in anim_call.findall(text):
            if anim_name not in animations.get(group, {}):
                errors.append(f"포저 {name}: 애니메이션 없음 {group}.{anim_name}")
        for bone in re.findall(r"q\.look\(\s*'([^']+)'", text):
            if not any(bone in bones for bones in models.values()):
                errors.append(f"포저 {name}: 본 없음 {bone}")

    used_models, used_posers = set(), set()
    for f in sorted(bedrock.glob("resolvers/*/*.json")):
        resolver = json.loads(f.read_text(encoding="utf-8"))
        for v in resolver["variations"]:
            if "model" in v:
                model = v["model"].split(":")[-1].removesuffix(".geo")
                used_models.add(model)
                if model not in models:
                    errors.append(f"{f.name}: 모델 없음 {v['model']}")
            if "poser" in v:
                poser = v["poser"].split(":")[-1]
                used_posers.add(poser)
                if poser not in posers:
                    errors.append(f"{f.name}: 포저 없음 {v['poser']}")
            textures = [v.get("texture")] + [layer.get("texture") for layer in v.get("layers", [])]
            for tex in textures:
                if isinstance(tex, dict):  # 애니메이션 텍스처
                    tex_list = tex.get("frames", [])
                else:
                    tex_list = [tex] if tex else []
                for t in tex_list:
                    if not (assets / t.split(":")[-1]).is_file():
                        errors.append(f"{f.name}: 텍스처 없음 {t}")
    for model in models:
        if model not in used_models:
            errors.append(f"쓰이지 않는 모델 {model}")
    for poser in posers:
        if poser not in used_posers:
            errors.append(f"쓰이지 않는 포저 {poser}")

    names = {name for _, _, name in SPECIES}
    for f in sorted(data.glob("spawn_pool_world/**/*.json")):
        pool = json.loads(f.read_text(encoding="utf-8"))
        for spawn in pool["spawns"]:
            refs = [spawn.get("pokemon", "")] + [p["pokemon"] for p in spawn.get("herdablePokemon", [])]
            for ref in refs:
                if ref and ref.split()[0] not in names:
                    errors.append(f"{f.name}: 이 팩에 없는 포켓몬 {ref}")
    for f in sorted(data.glob("species/*/*.json")):
        if json.loads(f.read_text(encoding="utf-8")).get("implemented") is not True:
            errors.append(f"{f.name}: implemented가 true가 아님")

    for e in errors:
        print("  ✗", e)
    print(f"검사: 모델 {len(models)}, 포저 {len(posers)}, 애니메이션 그룹 {len(animations)}, 오류 {len(errors)}")
    return not errors


def mcmeta(pack_format: int, supported=None) -> str:
    pack = {"pack_format": pack_format}
    if supported:
        pack["supported_formats"] = {"min_inclusive": supported[0], "max_inclusive": supported[1]}
    pack["description"] = DESCRIPTION
    return json.dumps({"pack": pack}, ensure_ascii=False, indent=2) + "\n"


def write_zip(path: Path, meta: str, roots):
    files = [PACK / "LICENSE-Cobblemon.txt"]
    for r in roots:
        files += [f for f in (PACK / r).rglob("*") if f.is_file()]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        def add(name, content):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, content)
        add("pack.mcmeta", meta.encode("utf-8"))
        for f in sorted(files):
            add(f.relative_to(PACK).as_posix(), f.read_bytes())
    print(f"  {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB, 파일 {len(files) + 1}개)")


def make_zips():
    DIST.mkdir(exist_ok=True)
    (PACK / "pack.mcmeta").write_text(
        mcmeta(RESOURCE_PACK_FORMAT, (RESOURCE_PACK_FORMAT, DATA_PACK_FORMAT)), encoding="utf-8")
    write_zip(DIST / f"{ZIP_PREFIX}_resourcepack.zip", mcmeta(RESOURCE_PACK_FORMAT), ["assets"])
    write_zip(DIST / f"{ZIP_PREFIX}_datapack.zip", mcmeta(DATA_PACK_FORMAT), ["data"])
    write_zip(DIST / f"{ZIP_PREFIX}.zip",
              mcmeta(RESOURCE_PACK_FORMAT, (RESOURCE_PACK_FORMAT, DATA_PACK_FORMAT)), ["assets", "data"])


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cobblemon", nargs="?", type=Path, help="Cobblemon 1.8.2 소스 폴더")
    parser.add_argument("--check", action="store_true", help="검사만")
    parser.add_argument("--zip", action="store_true", help="zip만 다시 생성")
    args = parser.parse_args()

    if args.cobblemon:
        print("가져오는 중:", args.cobblemon)
        import_from(args.cobblemon)
    elif not (args.check or args.zip):
        parser.error("Cobblemon 소스 폴더나 --check / --zip 중 하나가 필요합니다")

    if not check():
        sys.exit(1)
    if args.cobblemon or args.zip:
        make_zips()


if __name__ == "__main__":
    main()
