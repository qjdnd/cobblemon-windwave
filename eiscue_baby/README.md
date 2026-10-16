# 아기 빙큐보 (Baby Eiscue) — 아이스페이스 / 나이스페이스

Cobblemon 1.8.2용 블록벤치 모델 2종(폼별), 텍스처, 애니메이션입니다. 리소스팩/데이터팩으로는 아직 묶지 않았습니다.

| 파일 | 내용 |
| --- | --- |
| `eiscue_baby_ice.bbmodel` | 아이스페이스 블록벤치 프로젝트. 머리에 깨진 얼음 알껍데기를 쓰고 있습니다. |
| `eiscue_baby_noice.bbmodel` | 나이스페이스 블록벤치 프로젝트. 알껍데기가 없고, 작은 머리털이 나 있으며, 걱정스러운 눈입니다. |
| `eiscue_baby_ice.geo.json` / `eiscue_baby_noice.geo.json` | 위 두 프로젝트를 블록벤치에서 내보낸 것과 같은 지오메트리 |
| `eiscue_baby.animation.json` | 두 폼이 같이 쓰는 애니메이션 (`animation.eiscue_baby.*`) |
| `eiscue_baby_ice.json` / `eiscue_baby_noice.json` | 폼별 포저. 서 있을 때 대기 동작만 다르고 나머지는 같습니다. |
| `eiscue_baby.png` | 일반 텍스처 (두 폼 공용) |
| `eiscue_baby_shiny.png` | 이로치 텍스처 (두 폼 공용) |
| `eiscue_baby_alpha.png` | 알파 눈 레이어 (발광, 두 폼 공용) |

두 모델은 뼈 이름이 같습니다. 그래서 애니메이션 파일 하나로 둘 다 움직입니다.
한쪽에만 있는 뼈(아이스의 `shell*`, 나이스의 `hair*`)는 Cobblemon이 다른 폼에서 건너뜁니다.

## 텍스처

새로 그리지 않았습니다. Cobblemon의 빙큐보 텍스처(`0875_eiscue`, 64x64)에서 **색만** 바꿨고, 배치(UV)는 원본과 같습니다.
Cobblemon도 빙큐보 두 폼에 같은 텍스처를 쓰기 때문에, 아기도 텍스처 한 장을 두 폼이 같이 씁니다.

- 일반 (`eiscue.png` 기준)
  - 빙큐보의 하늘색 머리 → 검은 머리(황제펭귄 새끼)
  - 남색 몸 → 회청색 솜털
  - 흰 배 → 흰 얼굴 마스크와 연회색 가슴털
  - 얼음 → 연한 알껍데기 하늘색
  - 주황 → 황토색 부리와 발
- 이로치 (`eiscue_shiny.png` 기준): Cobblemon 빙큐보 이로치처럼 핑크 얼음 알껍데기, 자두색 머리, 연보라 솜털입니다.
- 알파 (`eiscue_no_ice_alpha.png`): 빨간 발광 눈 레이어를 그대로 썼습니다.
  아기의 눈(홍채, 눈동자)이 빙큐보 나이스페이스 눈 픽셀 자리를 쓰기 때문에, 두 폼 모두 눈 위치가 맞습니다.

색 변환은 원본 픽셀의 색을 기준으로 합니다. 일부 영역은 따로 바꿨습니다.

- 몸통 앞면(빙큐보의 흰 배)은 연회색 가슴털로 바꿨습니다.
- 나이스페이스 눈 픽셀 6개는 홍채/눈동자 색으로 바꿨습니다.

픽셀 위치는 원본 그대로입니다.

> 원본 텍스처: Cobblemon 빙큐보 텍스처 (Cobblemon Contributors, CC BY-NC 3.0). 색상을 변경했습니다.

## 모델 구성

- 크기: 높이 약 23px(알껍데기 포함), 날개를 편 폭 약 27px입니다.
- `body`: 통통한 솜털 몸통입니다. 날개(`wing_*`, `wing_*2`, `wing_*3`)는 그림처럼 위로 들고 있습니다. 꼬리(`tail`)와 발(`foot_*`)이 있습니다.
- `head`: 큰 검은 머리와 흰 얼굴 마스크(`face`)입니다.
  - 눈(`eye_*`): 회색 홍채, 검은 눈동자와 하이라이트(`eye_*_pupil`)로 되어 있습니다.
  - 무거운 눈꺼풀(`eye_*_lid`)이 위쪽을 덮어서 졸린 눈입니다.
  - 깜빡임용 눈꺼풀(`eye_*_eyelid`)은 눈 뒤에 숨어 있다가 앞으로 나옵니다.
  - 부리(`beak`)가 있습니다.
- 아이스페이스: 깨진 얼음 알껍데기(`shell`)와 지그재그 금(`shell_teeth`)이 있습니다.
- 나이스페이스: 알껍데기 대신 작은 머리털(`hair`, `hair2`)이 있습니다. 눈꺼풀이 조금 올라가 있고, 눈 기울기가 더 커서 걱정스러운 표정입니다.
- 머리 뼈 이름이 `head`라서 `q.look('head')`로 플레이어를 쳐다봅니다.

> Cobblemon은 Box UV만 읽습니다. 블록벤치에서 Per-face UV로 바꾸지 마세요.
> 블록벤치에서 애니메이션을 고쳐 내보낼 때, 한쪽 프로젝트에는 다른 폼 전용 뼈(`shell*`/`hair*`)가 없습니다.
> 그래서 그 채널이 빠질 수 있습니다. 공용 `eiscue_baby.animation.json`에 합쳐 주세요.

## 애니메이션

| 이름 | 용도 |
| --- | --- |
| `ground_idle` | 아이스페이스 대기. 꾸벅꾸벅 졸며 좌우로 흔들림, 날개 파닥, 알껍데기 흔들림 |
| `noice_idle` | 나이스페이스 대기. 얼음이 없어 오들오들 떨며 두리번거림, 날개를 몸에 붙임, 머리털 떨림 |
| `battle_idle` | 배틀 대기. 통통 뛰며 날개를 크게 파닥임 |
| `walk` | 뒤뚱뒤뚱 걷기, 발 번갈아 들기 |
| `water_idle` | 물 위(FLOAT). 둥둥 떠서 물장구 |
| `swim` | 잠수(SWIM). 몸을 눕히고 날개로 노 젓기 |
| `sleep` | 수면. 고개 떨구고 눈 감기, 날개 내림 |
| `blink` | 눈 깜빡임 (quirk) |
| `cry` / `battle_cry` | 울음. 고개 들고 날개 파닥, 알껍데기 들썩, 효과음 `pokemon.eiscueice.cry` |
| `physical` | 물리 공격. 배치기 박치기 |
| `special` | 특수 공격. 아이스는 알껍데기가 위로 튀어 올라 빙글 돌고 다시 씌워짐, 나이스는 머리털이 빙글 |
| `status` | 변화기. 눈 감고 한 바퀴 빙글, 날개 파닥 |
| `recoil` | 피격 |
| `faint` | 기절. 뒤로 벌러덩, 알껍데기가 굴러떨어짐 |

초상화/프로필 배율(`portraitScale` 1.1, `profileScale` 1.0)은 계산으로 잡은 값이라 게임에서 확인 후 조정이 필요할 수 있습니다.

## 나중에 팩으로 묶을 때

이번에는 리졸버, 종 데이터, 팩 구조를 만들지 않았습니다.

- Cobblemon 1.8.2는 빙큐보의 폼을 `penguin_head` 특성으로 나눕니다. 선택지는 `ice_face`(기본)와 `noice_face`입니다.
  아기 종에도 이 특성을 배정하면 같은 aspect를 그대로 쓸 수 있습니다 (`species_feature_assignments`).
- 리졸버 예시 (종 ID와 `<폴더>`는 정해지면 바꾸세요):

```json
{
  "species": "cobblemon:eiscue_baby",
  "order": 0,
  "variations": [
    {
      "aspects": [],
      "poser": "cobblemon:eiscue_baby_ice",
      "model": "cobblemon:eiscue_baby_ice.geo",
      "texture": "cobblemon:textures/pokemon/<폴더>/eiscue_baby.png",
      "layers": []
    },
    { "aspects": ["noice_face"], "poser": "cobblemon:eiscue_baby_noice", "model": "cobblemon:eiscue_baby_noice.geo" },
    { "aspects": ["shiny"], "texture": "cobblemon:textures/pokemon/<폴더>/eiscue_baby_shiny.png" },
    {
      "aspects": ["alpha_eyes"],
      "layers": [{ "name": "alpha_eyes", "texture": "cobblemon:textures/pokemon/<폴더>/eiscue_baby_alpha.png", "emissive": true }]
    }
  ]
}
```
