# 거다이맥스 가라르 또도가스 (Gigantamax Galarian Weezing)

Cobblemon 1.8.2용 블록벤치 모델과 애니메이션입니다. 아직 리소스팩/데이터팩으로는 묶지 않았습니다.

| 파일 | 내용 |
| --- | --- |
| `weezing_galar_gmax.bbmodel` | 블록벤치 프로젝트 (Bedrock Entity 포맷, Box UV). 지오메트리와 애니메이션 13종이 들어 있습니다. |
| `weezing_galar_gmax.geo.json` | 위 프로젝트를 블록벤치에서 내보낸 것과 같은 지오메트리 (`geometry.weezing_galar_gmax`) |
| `weezing_galar_gmax.animation.json` | 애니메이션 (`animation.weezing_galar_gmax.*`) |
| `weezing_galar_gmax.json` | 포저: 포즈와 애니메이션 연결, 초상화/프로필 배율 |

## 텍스처

새 텍스처는 만들지 않았습니다. Cobblemon에 들어 있는 가라르 또도가스 텍스처(128x64)를 그대로 씁니다.
모델의 UV는 원본 Box UV 배치에 맞춰 배치했습니다.

- 일반: `cobblemon:textures/pokemon/0110_weezing/weezing_galar.png`
- 이로치: `cobblemon:textures/pokemon/0110_weezing/weezing_galar_shiny.png`

두 텍스처는 UV 배치가 같습니다. 그래서 이로치는 텍스처만 바꾸면 그대로 맞습니다.

블록벤치에서 텍스처를 보려면 Cobblemon jar의 `assets/cobblemon/textures/pokemon/0110_weezing/`에서
`weezing_galar.png`, `weezing_galar_shiny.png`를 꺼내 `.bbmodel` 파일 옆에 두세요.
프로젝트에 두 텍스처가 모두 등록되어 있어, 텍스처 패널에서 일반/이로치를 바꿔 볼 수 있습니다.

> Cobblemon은 Box UV(`"uv": [u, v]`)만 읽습니다. 블록벤치에서 Per-face UV로 바꾸지 마세요.
> 큐브 크기는 정수로 두고, 크기는 `inflate`로 키웠습니다.
> 정수가 아닌 크기는 블록벤치와 게임에서 UV가 다르게 보입니다.

## 모델 구성

- **몸통**: 또도가스 머리 두 개가 붙은 쌍둥이 몸통입니다. 원본 15³ 몸통 UV를 회전시켜, 해골 무늬 면이 안쪽으로 숨도록 했습니다. 아래쪽은 불룩하고 윗부분은 2단 돔입니다. 이끼 패치가 붙어 있습니다.
- **얼굴 2개** (`face_right` = 화면 왼쪽, `face_left` = 화면 오른쪽, 포켓몬 기준 좌우)
  - 각 얼굴에 졸린 눈 2개가 있습니다. 눈꺼풀(`*_lid`), 깜빡임용 눈꺼풀(`*_eyelid`), 눈동자(`*_pupil`)로 나뉩니다.
  - 이끼 콧수염(`*_moustache`)은 좌우와 끝(`*_tip`)이 따로 움직입니다.
  - 입은 닫힌 입(`*_mouth_closed`)과 벌린 입(`*_mouth_open`, 평소에는 몸 안에 숨어 있음)이 있습니다.
  - `face_left`에는 혀(`tongue`)가 있습니다.
- **굴뚝 8개**: 가운데 큰 굴뚝(`chimney_center*`)과 주변 굴뚝 7개(`chimney_*`, `*_mid`, `*_top`)입니다.
- **연기**: 굴뚝마다 흰 연기 구름(`smoke_*`)이 있고, 가운데 굴뚝에는 붉은 독연기(`smoke_red_*`)가 있습니다.
  각 연기 뼈의 피벗은 굴뚝 입구라서, 스케일 애니메이션을 주면 입구에서 부풀어 오릅니다.
- **꽃**: 몸통에 붙은 꽃(`flower_1`~`10`)과 주변에 떠다니는 꽃(`petal_1`~`4`)이 있습니다.
- 크기: 폭 약 46px(약 2.9블록)입니다. 원본 가라르 또도가스의 약 2배입니다.
- 알파: 알파용 눈 레이어/텍스처는 넣지 않았습니다.

## 애니메이션

| 이름 | 용도 |
| --- | --- |
| `ground_idle` | 평상시 대기. 둥실거림, 굴뚝 흔들림, 연기 뭉게뭉게, 콧수염과 혀 움직임, 꽃잎 떠다님 |
| `battle_idle` | 배틀 대기. 더 크게 움직이고, 화난 눈썹과 진한 연기 |
| `air_fly` | 이동(WALK/SWIM). 앞으로 기울이고, 연기가 뒤로 흩날림 |
| `sleep` | 수면. 눈 감음, 숨쉬기, 연기 작아짐, 콧수염 처짐 |
| `blink` / `blink2` | 오른쪽 / 왼쪽 얼굴 눈 깜빡임 (quirk) |
| `cry` / `battle_cry` | 울음. 입 벌림, 연기 분출, 효과음 `pokemon.weezing.cry` |
| `physical` | 물리 공격. 뒤로 뺐다가 몸통 박치기 |
| `special` | 특수 공격. 굴뚝이 들썩이며 연기와 독연기 폭발, 꽃잎 퍼짐 |
| `status` | 변화기. 몸 흔들기, 꽃 만개, 독연기가 굴뚝 주위를 한 바퀴 회전 |
| `recoil` | 피격 |
| `faint` | 기절. 가라앉으며 기울어지고, 연기가 사라짐 |

포저(`weezing_galar_gmax.json`)는 Cobblemon 기본 또도가스 포저와 같은 구조입니다.
초상화/프로필 배율(`portraitScale` 0.7, `profileScale` 0.6)은 계산으로 잡은 값이라 게임에서 확인 후 조정이 필요할 수 있습니다.

## 나중에 팩으로 묶을 때 (메가쇼다운 연동)

이번에는 리졸버와 팩 구조를 만들지 않았습니다. 팩으로 묶을 때는 아래 위치에 두면 됩니다.

- `assets/cobblemon/bedrock/pokemon/models/0110_weezing/weezing_galar_gmax.geo.json`
- `assets/cobblemon/bedrock/pokemon/animations/0110_weezing/weezing_galar_gmax.animation.json`
- `assets/cobblemon/bedrock/pokemon/posers/0110_weezing/weezing_galar_gmax.json`
- 리졸버 (메가쇼다운 연동 시 작성): `galarian` + 거다이맥스 aspect일 때 이 모델과 `weezing_galar.png`를 쓰고, `shiny`가 붙으면 `weezing_galar_shiny.png`를 쓰게 합니다.
  - Cobblemon 1.8.x의 `dynamax_form` 특성은 거다이맥스 aspect를 `gmax`로 씁니다.
    다만 기본 배정 목록에 또도가스는 없습니다.
  - 기존 가라르 리졸버의 알파 눈 레이어(`alpha_eyes`)가 상속되므로, 리졸버에서 `"enabled": false`로 꺼야 합니다.
