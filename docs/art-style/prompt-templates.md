# 포켓몬 공식 스타일 이미지 생성 프롬프트 템플릿

[`pokemon-official-style-guide.md`](./pokemon-official-style-guide.md)의 분석을 프롬프트로 옮긴 것입니다.
대부분의 이미지 모델이 영어 프롬프트에서 가장 안정적이므로, 프롬프트는 영어로 쓰고 설명만 한국어로 적었습니다.

---

## 1. 조립 공식

```
[SUBJECT] + [DESIGN RULES] + [STYLE BASE] + [GENERATION MODIFIER] + [COMPOSITION]
NEGATIVE: [NEGATIVE BASE] (+ 상황별 추가)
```

- **SUBJECT**: 무엇을 그리는지(아래 작성법 참고)
- **DESIGN RULES**: 형태와 색의 규칙 (공통 블록)
- **STYLE BASE**: 선·음영·광원 (공통 블록)
- **GENERATION MODIFIER**: 어느 세대 느낌인지 (표에서 하나만 고르기, 기본값은 10세대)
- **COMPOSITION**: 구도와 배경 (템플릿마다 다름)

### 모델별 팁
- **부정 프롬프트 칸이 있는 모델**(Stable Diffusion 계열 등): NEGATIVE 블록을 그대로 넣습니다.
- **부정 프롬프트 칸이 없는 모델**(문장형 모델 대부분): 본문 끝에 `Avoid: ...` 문장으로 붙이거나, 핵심 몇 개만 `no 3D render, no background` 식으로 넣습니다.
- **문장형 모델**(자연어를 잘 이해하는 최신 모델): 태그를 나열하기보다 4번의 문장형 버전이 더 잘 먹힙니다.
- **참조 이미지 기능이 있으면** 앞 진화 단계나 고른 시안을 참조로 넣는 것이 텍스트보다 일관성에 훨씬 효과적입니다.
- **`Pokémon` 단어**: 넣으면 스타일 고정력은 세지만 기존 포켓몬(특히 피카츄)이 섞이거나, 서비스에 따라 상표 필터에 걸릴 수 있습니다. 결과가 기존 종을 닮아 가면 `Pokémon-style`을 `monster-collecting RPG official artwork style`로 바꾸세요.
- **작가 이름**보다 특징 서술이 모델을 바꿔도 결과가 안정적입니다. 이 템플릿은 작가 이름 없이 스타일 특징만으로 구성했습니다.

---

## 2. 공통 블록

### SUBJECT 작성법
```
a [단계: small basic-stage / middle-stage / fully evolved] [타입]-type creature
based on [실존 생물] and [사물/자연 요소],
[몸 형태: round chubby body / slender quadruped / bipedal stance ...],
[특징 부위 1~3개],
colors: [주색] body, [보조색] belly/face, [포인트색] markings on [부위]
```
- 특징 부위는 **실루엣 밖으로 튀어나오는 것** 위주로 1~3개만 적습니다.
- 색은 3~4개로 제한하고, **부위와 함께** 적습니다. 가능하면 HEX 값을 씁니다(`#4FA3E0 sky blue`).

### DESIGN RULES
```
original creature design, simple readable silhouette built from a few large rounded shapes,
one or two clear motifs, limited palette of 3 to 4 flat colors in large color blocks,
minimal surface detail, fur and feathers simplified into a few large clumps,
simple eyes with a single white highlight
```

### STYLE BASE
```
official Pokémon-style character artwork, 2D illustration,
clean dark outlines with tapered line weight, outer contour thicker than interior lines,
dark brownish-navy line color instead of pure black,
flat base colors with one level of hard-edged cel shadow,
soft diffused highlights, single light source from the upper left,
hue-shifted shadows (warm colors shade toward red-brown, cool colors toward blue-violet),
small white specular dots only on glossy parts
```

### GENERATION MODIFIER (하나만 선택)
| 세대 | 영어 수식어 |
|---|---|
| 1세대 | `1996 traditional watercolor and ink illustration, slightly rough uneven ink lines, light translucent washes, paper white highlights, muted desaturated palette, stiff pose, monster-like proportions` |
| 2세대 | `late-1990s watercolor illustration, cleaner even ink lines, softer rounder shapes, gentle wash shading, bright clear palette` |
| 3세대 | `early-2000s digital painting with watercolor feel, bold clean outlines, stronger contrast, glossy soft highlights, saturated colors, dynamic pose` |
| 4세대 | `mid-2000s clean digital cel shading, thin even linework, geometric sculpted forms, slightly muted palette, metallic accents` |
| 5세대 | `crisp graphic shapes, bold color blocking, angular silhouettes, sharp clean cel shadows, high contrast` |
| 6세대 | `smooth volumetric cel shading, simple primitive 3D-friendly forms, polished clean rendering, vivid colors` |
| 7세대 | `bright tropical palette, warm sunlight feel, clean soft cel shading, playful rounded shapes` |
| 8세대 | `polished modern cel shading, clean color separation, slightly flat rendering` |
| 9세대 | `contemporary official artwork, cel-shaded forms with soft airbrushed gradients, subtle rim light, refined but restrained detail` |
| **10세대 (기본값)** | `modern official artwork, very rounded plush-friendly shapes, large head, simple color blocks, bright tropical Southeast Asian palette, clean cel shading with soft gradients` |

> 1~2세대 수식어는 STYLE BASE의 `hard-edged cel shadow`와 충돌합니다. 레트로 버전은 템플릿 B를 쓰세요.

### NEGATIVE BASE
```
realistic, photorealistic, 3D render, CGI, plastic, clay, fur strands, hyper-detailed texture,
painterly brush strokes, sketch lines, hatching, multiple shadow layers, dramatic lighting,
heavy rim light, background scenery, gradient background, ground shadow, props,
multiple characters, text, letters, logo, watermark, signature, frame, border, cropped body,
extra limbs, extra eyes, deformed anatomy, anime screenshot, chibi, sparkly anime eyes,
western cartoon, existing Pokémon, Pikachu
```

---

## 3. 템플릿

### A. 공식 일러스트 (기본, 현대 스타일)
```
[SUBJECT], [DESIGN RULES], [STYLE BASE], [GENERATION MODIFIER: 10세대],
full body, three-quarter view, standing pose that shows every key feature,
centered, isolated on a pure white background, no ground shadow
NEGATIVE: [NEGATIVE BASE]
```

### B. 레트로 수채 (1~2세대 느낌)
STYLE BASE 대신 아래 블록을 씁니다.
```
[SUBJECT], [DESIGN RULES],
1996 official monster artwork, traditional watercolor and ink on paper,
slightly uneven hand-inked outlines, light translucent watercolor washes,
shadows as soft single wash layer, white of the paper left for highlights,
muted desaturated colors, subtle paper texture,
full body, side or three-quarter view, slightly stiff pose, plain white paper background
NEGATIVE: digital painting, cel shading, glossy, 3D render, gradient background, [NEGATIVE BASE 중 나머지]
```

### C. 진화 라인 시트
```
evolution line sheet of an original creature family, three stages side by side from left to right,
stage 1: [SUBJECT 1], stage 2: [SUBJECT 2], stage 3: [SUBJECT 3],
consistent main color and marking placement across all stages,
size and complexity increase with each stage, head proportion shrinks from about half to a fifth of body height,
[STYLE BASE], [GENERATION MODIFIER],
all three full body, same three-quarter angle, evenly spaced on a pure white background
NEGATIVE: [NEGATIVE BASE] (multiple characters 는 빼기)
```

### D. 턴어라운드 시트 (Cobblemon 모델링 참고용)
```
character turnaround reference sheet of [SUBJECT],
orthographic front view, side view, back view and three-quarter view in one row,
same scale, same neutral standing pose in every view,
clean dark outlines, flat colors with minimal soft shading, even flat lighting,
consistent proportions and markings across views, pure white background
NEGATIVE: perspective distortion, dynamic pose, dramatic lighting, background, text, labels, [NEGATIVE BASE 중 나머지]
```
- 생성 결과 여러 장 사이에서 비율이 어긋나기 쉬우니, 고른 공식 일러스트(A)를 **참조 이미지로 같이 넣는 것**을 권장합니다.

### E. 리전폼 (기존 종의 10세대 지방 재해석)
```
regional variant of [기존 종 이름], adapted to a tropical Southeast Asian archipelago,
keeps the original's silhouette and body plan but changes [바뀌는 부위 1~2개] and colors to [새 팔레트],
new type: [타입], inspired by [지역 생물/문화 요소],
[STYLE BASE], [GENERATION MODIFIER: 10세대],
full body, three-quarter view, isolated on a pure white background
NEGATIVE: [NEGATIVE BASE] (existing Pokémon 는 빼기)
```

### F. 이로치(색이 다른 모습) 비교
```
two versions of the same creature side by side, identical pose and design,
left: normal colors [팔레트 A], right: alternate shiny colors [팔레트 B],
[SUBJECT 의 형태 부분], [STYLE BASE], [GENERATION MODIFIER],
pure white background
NEGATIVE: [NEGATIVE BASE] (multiple characters 는 빼기)
```
- 공식 이로치는 보통 **주색 1~2개만 바꾸고** 마킹 위치와 명암 구조는 그대로입니다.

---

## 4. 문장형 버전 (문장형 모델용)

```
An official-style monster-collecting RPG character illustration of an original creature: [SUBJECT].
Draw it as a clean 2D illustration with dark, tapered outlines (thicker on the outer contour),
flat colors, a single hard-edged cel shadow and soft, diffused highlights, lit from the upper left.
Shadows shift in hue rather than just getting darker.
Keep the design simple: a readable silhouette made of a few large rounded shapes,
three to four colors in large blocks, fur simplified into a few clumps, and simple eyes with one highlight.
Modern style with very rounded, plush-friendly proportions and a bright tropical palette.
Show the full body in a three-quarter view, alone, on a pure white background with no ground shadow.
Avoid realism, 3D rendering, fine fur texture, background scenery, text and any existing Pokémon.
```

---

## 5. 완성 예시 (10세대풍 오리지널 포켓몬)

**콘셉트**: 날원숭이(콜루고) + 말레이 달 연(와우 불란), 비행 타입 기본형. "바람" 테마.

```
a small basic-stage Flying-type creature based on a colugo (flying lemur) and a traditional Malaysian moon kite,
round chubby body with a kite-shaped gliding membrane stretched between its short limbs,
large round head with big simple eyes, a short fluffy tail with a ribbon-like tip,
colors: #6EC6F0 sky blue body, #FFF4DC cream belly and face, #D8344A crimson and #F2C14E gold crescent markings on the membrane,
original creature design, simple readable silhouette built from a few large rounded shapes,
one or two clear motifs, limited palette of 3 to 4 flat colors in large color blocks,
minimal surface detail, fur simplified into a few large clumps, simple eyes with a single white highlight,
official Pokémon-style character artwork, 2D illustration,
clean dark outlines with tapered line weight, outer contour thicker than interior lines,
dark brownish-navy line color instead of pure black,
flat base colors with one level of hard-edged cel shadow, soft diffused highlights,
single light source from the upper left, hue-shifted shadows,
modern official artwork, very rounded plush-friendly shapes, large head, simple color blocks,
bright tropical Southeast Asian palette, clean cel shading with soft gradients,
full body, three-quarter view, membrane spread to show the kite markings,
centered, isolated on a pure white background, no ground shadow

NEGATIVE: realistic, photorealistic, 3D render, CGI, fur strands, hyper-detailed texture,
painterly brush strokes, multiple shadow layers, background scenery, ground shadow,
multiple characters, text, watermark, cropped body, extra limbs, anime screenshot, chibi,
existing Pokémon, Pikachu
```

생성 후에는 가이드의 **5. 검수 체크리스트**로 확인하고, 통과한 시안으로 템플릿 D(턴어라운드)를 만듭니다.
