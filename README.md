# cobblemon-windwave
Cobblemon 1.8.1 Wind Wave Project

## Cobblemon 1.8.2 신규 포켓몬 17종 (1.8.1용 팩)

2026년 10월 11일 나온 Cobblemon 1.8.2에서 새로 추가된 포켓몬 17종을 **Cobblemon 1.8.1(Minecraft 1.21.1)** 에서
쓸 수 있게 리소스팩 + 데이터팩으로 옮겼습니다. 모델·애니메이션·포저·리졸버·텍스처·종 데이터·스폰은
[Cobblemon 1.8.2 공식 소스](https://gitlab.com/cable-mc/cobblemon/-/tree/1.8.2)의 파일을 그대로 가져왔습니다.

| No. | 포켓몬 | 폼 / 성별 차이 | 이로치 | 알파 | 야생 스폰 |
|---|---|---|---|---|---|
| #412 | 도롱충이 (Burmy) | 초목도롱 · 모래땅도롱 · 슈레도롱 | ✔ | ✔ | ✔ |
| #413 | 도롱마담 (Wormadam) | 초목도롱 · 모래땅도롱 · 슈레도롱 | ✔ | ✔ | ✔ |
| #414 | 나메일 (Mothim) | | ✔ | ✔ | ✔ |
| #459 | 눈쓰개 (Snover) | 암컷 모델 따로 | ✔ | ✔ | ✔ |
| #460 | 눈설왕 (Abomasnow) | 암컷 모델 따로 | ✔ | ✔ | ✔ |
| #535 | 동챙이 (Tympole) | | ✔ | ✔ | ✔ |
| #536 | 두까비 (Palpitoad) | | ✔ | ✔ | ✔ |
| #537 | 두빅굴 (Seismitoad) | | ✔ | ✔ | ✔ |
| #694 | 목도리키텔 (Helioptile) | 발광 레이어 | ✔ | ✔ | ✔ |
| #695 | 일레도리자드 (Heliolisk) | 발광 레이어 | ✔ | ✔ | ✔ |
| #736 | 턱지충이 (Grubbin) | | ✔ | ✔ | ✔ |
| #737 | 전지충이 (Charjabug) | 발광 레이어 | ✔ | ✔ | ✔ |
| #738 | 투구뿌논 (Vikavolt) | | ✔ | ✔ | ✔ |
| #774 | 메테노 (Minior) | 유성의 모습 + 코어 7색 (발광) | ✔ | ✔ | ✔ |
| #890 | 무한다이노 (Eternatus) | 발광 레이어 | ✔ | ✔ | ✘ (전설, 1.8.2에도 스폰 없음) |
| #971 | 망망이 (Greavard) | 발광 레이어 | ✔ | ✔ | ✔ |
| #972 | 묘두기 (Houndstone) | | ✔ | ✔ | ✔ |

### 들어 있는 것

| 종류 | 내용 |
|---|---|
| 리소스팩 (`assets/`) | 모델 23개, 애니메이션 21개, 포저 22개, 리졸버 19개, 텍스처 81장, 메테노 빨간색 코어 도감 설명(en_us/ko_kr) |
| 데이터팩 (`data/`) | 종 파일 17개(`implemented: true`, 1.8.2 크기/히트박스), 스폰 풀 16개 + 무리/알파 무리 14개 |
| 메테노 | 코어 색 기능(`species_features/core_color.json`, 1.8.2처럼 랜덤 색) + 도감 폼 목록 |
| 서식지(habitat) | 1.8.2에서 이 포켓몬들이 추가된 서식지 스폰 풀 10개 (`deep_roots`, `lost_cave_ruins`, `lush_peat_bog`, `meteorite_impact`, `parched_peat_bog`, `root_nursery`, `sandpit_clearing`, `skeletal_fall`, `snowy_grotto`, `sunscorched_clearing`) |

울음소리와 포켓몬 이름/도감 설명은 Cobblemon 1.8.1에 이미 들어 있어서 따로 넣지 않았습니다.

### 1.8.2 원본과 다른 점

- **턱지충이·전지충이·투구뿌논·망망이·묘두기**: 1.8.2 종 파일에 `"implemented": true`가 빠져 있어서
  (체인지로그에는 추가된 포켓몬으로 나옴) 도감 등에서 미구현으로 표시됩니다. 이 팩에서는 `implemented: true`를 넣었습니다.
- **도롱충이 전투 후 도롱(망토) 변경**은 1.8.2에 새로 생긴 코드(`battle_ended` 콜백, `battle_pokemon` 등)가 필요해서
  1.8.1에서는 동작하지 않습니다. 도롱충이는 바이옴에 맞는 도롱으로 스폰되고, 도롱마담으로 진화하는 것은 그대로 됩니다.
- 그 외 파일은 1.8.2 원본과 바이트 단위로 같습니다.

### 설치

`dist/` 폴더:

| 파일 | 넣는 곳 |
|---|---|
| `cobblemon-windwave-1.8.2-pokemon_resourcepack.zip` | `.minecraft/resourcepacks/` → 게임 설정에서 리소스팩 활성화 |
| `cobblemon-windwave-1.8.2-pokemon_datapack.zip` | `saves/<월드>/datapacks/` → `/reload` 또는 월드 다시 열기 |
| `cobblemon-windwave-1.8.2-pokemon.zip` | 리소스팩+데이터팩 합본 (두 곳에 같은 파일을 넣어도 됨) |

서버라면 데이터팩은 서버 월드의 `datapacks/` 폴더에, 리소스팩은 각 클라이언트에 넣습니다. 두 팩이 모두 있어야 합니다.

- Cobblemon을 1.8.2로 올리면 이 팩은 빼세요. (그대로 둬도 내용은 1.8.2와 같지만, 이후 버전에서 바뀐 내용을 덮어쓸 수 있습니다.)
- 다른 브랜치의 직접 만든 망망이/묘두기 팩과 같은 파일 경로를 쓰므로, 같이 넣으면 우선순위가 높은 팩의 모델이 보입니다.

테스트 명령어:

```
/pokespawn snover gender=female
/pokespawn burmy bagworm_cloak=sandy shiny
/pokespawn wormadam bagworm_cloak=trash
/pokespawn minior
/pokespawn minior meteor_shield=core core_color=blue
/pokespawn eternatus alpha=true
/pokespawn vikavolt shiny
```

### 다시 만들기

```
git clone --filter=blob:none --no-checkout --depth 1 --branch 1.8.2 https://gitlab.com/cable-mc/cobblemon.git cobblemon-1.8.2
git -C cobblemon-1.8.2 sparse-checkout set --no-cone /LICENSE \
    /common/src/main/resources/data/ /common/src/main/resources/assets/cobblemon/lang/ \
    /common/src/main/resources/assets/cobblemon/bedrock/pokemon/ \
    /common/src/main/resources/assets/cobblemon/textures/pokemon/
git -C cobblemon-1.8.2 checkout 1.8.2

python3 tools/backport_pokemon.py cobblemon-1.8.2   # pack-1.8.2/ 생성 → 참조 검사 → dist/ zip
python3 tools/backport_pokemon.py --check           # 참조 검사만 (리졸버→모델/포저/텍스처, 포저→애니메이션)
```

### 라이선스

`pack-1.8.2/`의 파일은 [Cobblemon](https://gitlab.com/cable-mc/cobblemon)(Mozilla Public License 2.0)에서 가져온 것입니다.
라이선스 전문은 `pack-1.8.2/LICENSE-Cobblemon.txt`에 있고 zip에도 들어 있습니다.
