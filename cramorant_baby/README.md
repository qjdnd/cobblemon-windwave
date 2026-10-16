# 아기 윽우지 (Baby Cramorant)

Cobblemon 1.8.2용 블록벤치 모델, 텍스처, 애니메이션입니다. 리소스팩/데이터팩으로는 아직 묶지 않았습니다.

| 파일 | 내용 |
| --- | --- |
| `cramorant_baby.bbmodel` | 블록벤치 프로젝트 (Bedrock Entity 포맷, Box UV). 텍스처 3장과 애니메이션 15종이 들어 있습니다. |
| `cramorant_baby.geo.json` | 위 프로젝트를 블록벤치에서 내보낸 것과 같은 지오메트리 (`geometry.cramorant_baby`) |
| `cramorant_baby.animation.json` | 애니메이션 (`animation.cramorant_baby.*`) |
| `cramorant_baby.json` | 포저: 포즈와 애니메이션 연결, 초상화/프로필 배율 |
| `cramorant_baby.png` | 일반 텍스처 |
| `cramorant_baby_shiny.png` | 이로치 텍스처 |
| `cramorant_baby_alpha.png` | 알파 눈 레이어 (발광) |

## 텍스처

새로 그리지 않았습니다. Cobblemon의 윽우지 텍스처(`0845_cramorant`)에서 **색만** 1:1로 바꿨습니다.
배치(UV)는 원본과 같습니다.

- 일반 (`cramorant.png` 기준): 몸은 연한 청회색(페리윙클), 가슴 털은 라벤더, 부리는 부드러운 노랑, 눈은 초록입니다.
- 이로치 (`cramorant_shiny.png` 기준): Cobblemon 윽우지 이로치(주황)를 파스텔 살구색으로 바꿨습니다. 가슴 털은 크림 핑크입니다.
- 알파 (`cramorant_alpha.png`): 빨간 발광 눈 레이어를 그대로 썼습니다. 아기 모델의 눈이 윽우지 눈 UV를 그대로 쓰기 때문에 위치가 맞습니다.

> 원본 텍스처: Cobblemon 윽우지 텍스처 (Cobblemon Contributors, CC BY-NC 3.0). 색상을 변경했습니다.

## 모델 구성

- 크기: 높이 약 25px(깃털 포함), 폭 약 17px입니다.
- `body`: 통통한 몸통과 라벤더 턱받이(`bib`)입니다. 아래에 날개(`wing_*`, `wing_*_tip`), 꼬리(`tail`, `tail_feathers`), 발(`foot_*`)이 달려 있습니다.
- `head`: 큰 머리와 볼(`cheek_*`), 머리 깃털 3개(`tuft`, `tuft_left`, `tuft_right`)입니다.
- 눈(`eye_*`): 초록 눈에 검은 눈동자와 하이라이트(`eye_*_pupil`)가 있습니다.
  깜빡임용 눈꺼풀(`eye_*_eyelid`)은 눈 뒤에 숨어 있다가 앞으로 나옵니다.
- 부리(`beak`): 넓적한 오리 부리입니다. 아래 부리(`jaw`)가 열립니다.
- 물고기(`fish`, `fish_tail`): 부리에 문 작은 물고기입니다. 윗부리에 붙어 있어 입을 벌려도 떨어지지 않습니다.
- 머리 뼈 이름이 `head`라서 `q.look('head')`로 플레이어를 쳐다봅니다.

> Cobblemon은 Box UV만 읽습니다. 블록벤치에서 Per-face UV로 바꾸지 마세요.

## 애니메이션

| 이름 | 용도 |
| --- | --- |
| `ground_idle` | 평상시 대기. 숨쉬기, 고개 갸웃, 깃털과 꼬리 흔들림, 물고기 파닥, 오물오물 |
| `battle_idle` | 배틀 대기. 통통 뛰고, 날개를 살짝 벌리고, 물고기를 더 세게 파닥임 |
| `walk` | 걷기(WALK/SWIM). 뒤뚱뒤뚱, 발 번갈아 들기, 날개로 균형 잡기 |
| `air_idle` / `air_fly` | 공중(HOVER/FLY). 작은 날개를 빠르게 파닥임 |
| `sleep` | 수면. 고개 숙이고 눈 감기, 깃털 처짐, 숨쉬기 |
| `blink` | 눈 깜빡임 (quirk) |
| `nom` | 물고기 오물오물 씹기 (quirk) |
| `cry` / `battle_cry` | 울음. 고개 들고 부리 벌리고 날개 파닥, 효과음 `pokemon.cramorant.cry` |
| `physical` | 물리 공격. 뒤로 뺐다가 배치기 + 쪼기 |
| `special` | 특수 공격. 물고기를 휙 발사했다가 다시 물어옴 (그대로 받아먹기) |
| `status` | 변화기. 눈 감고 한 바퀴 빙글, 날개 파닥, 턱받이 부풀림 |
| `recoil` | 피격 |
| `faint` | 기절. 뒤로 벌러덩 넘어지고 물고기가 떨어짐 |

초상화/프로필 배율(`portraitScale` 1.0, `profileScale` 1.0)은 계산으로 잡은 값이라 게임에서 확인 후 조정이 필요할 수 있습니다.

## 나중에 팩으로 묶을 때

이번에는 리졸버, 종 데이터, 팩 구조를 만들지 않았습니다. 묶을 때 필요한 것은 다음과 같습니다.

- 위치
  - `assets/cobblemon/bedrock/pokemon/models/<폴더>/cramorant_baby.geo.json`
  - `.../animations/<폴더>/cramorant_baby.animation.json`
  - `.../posers/<폴더>/cramorant_baby.json`
  - `assets/cobblemon/textures/pokemon/<폴더>/*.png`
- 리졸버 예시 (종 ID는 정해지면 바꾸세요):

```json
{
  "species": "cobblemon:cramorant_baby",
  "order": 0,
  "variations": [
    {
      "aspects": [],
      "poser": "cobblemon:cramorant_baby",
      "model": "cobblemon:cramorant_baby.geo",
      "texture": "cobblemon:textures/pokemon/<폴더>/cramorant_baby.png",
      "layers": []
    },
    { "aspects": ["shiny"], "texture": "cobblemon:textures/pokemon/<폴더>/cramorant_baby_shiny.png" },
    {
      "aspects": ["alpha_eyes"],
      "layers": [{ "name": "alpha_eyes", "texture": "cobblemon:textures/pokemon/<폴더>/cramorant_baby_alpha.png", "emissive": true }]
    }
  ]
}
```
