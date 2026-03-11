---
name: podcast-gen
description: "Generate AI podcast scripts and audio from source content. Use this skill whenever the user wants to create a podcast, generate a podcast script, convert documents/articles/analysis into audio conversations, or mentions 'podcast', '팟캐스트', 'audio conversation', 'NotebookLM style', or 'GenFM'. Also trigger when the user wants two speakers to discuss a topic, asks for a conversational summary of content, or wants to listen to their notes/analysis during a commute. This skill handles both script generation (in Person1/Person2 tag format) and optional audio generation via podcast_tts.py."
---

# Podcast Generator Skill

소스 콘텐츠를 2인 대화형 팟캐스트 스크립트로 변환하고, 선택적으로 ElevenLabs TTS를 통해 오디오를 생성하는 스킬.

## Workflow Overview

```
소스 콘텐츠 → 스크립트 생성 (<Person1>/<Person2>) → (선택) podcast_tts.py → MP3
```

## Step 1: Determine Parameters

사용자의 요청에서 다음을 파악한다:

| 파라미터 | 기본값 | 설명 |
|---------|--------|------|
| language | 소스 언어 자동 감지 | `ko` 또는 `en` |
| duration | 30분 | 목표 길이 (분) |
| style | casual | `casual`, `deep-dive`, `debate`, `storytelling` |
| audio | false | 오디오까지 생성할지 여부 |

### Duration → Word Count 매핑

| 목표 시간 | 한국어 단어 수 | 영어 단어 수 | 대사 수 (약) |
|----------|-------------|------------|------------|
| 10분 | ~3,000 | ~3,200 | 80-100 |
| 30분 | ~9,000 | ~9,600 | 240-300 |
| 60분 | ~18,000 | ~19,200 | 500-600 |

## Step 2: Generate Script

### Script Format

반드시 아래 포맷으로 생성한다:

```
<Person1>대사 내용</Person1>
<Person2>대사 내용</Person2>
<Person1>대사 내용</Person1>
<Person2>대사 내용</Person2>
```

- `<Person1>` = 진행자/호스트 (질문, 소개, 전환 담당)
- `<Person2>` = 전문가/게스트 (설명, 인사이트 담당)
- 태그 사이에 빈 줄 없이 연속으로 작성
- 한 대사는 1-4문장이 적절 (너무 길면 독백이 됨)

### Script Generation Guidelines

소스 콘텐츠를 분석한 뒤, 아래 원칙에 따라 스크립트를 생성한다.
**장편(30분+)의 경우 references/longform-strategy.md를 먼저 읽는다.**

#### 한국어 스크립트 원칙

1. **자연스러운 대화체**: 문어체 금지. "~입니다" 보다 "~거든요", "~잖아요" 사용
2. **추임새 필수**: "음...", "아~", "맞아요", "오~", "진짜요?", "흥미롭네요", "그렇죠"
3. **비유와 사례**: 추상적 설명 대신 구체적 비유 활용
4. **질문-답변 리듬**: Person1이 질문 → Person2가 답변 → Person1이 반응/후속 질문
5. **전환 브릿지**: 챕터 간 "그런데 이 부분에서 한 가지 더...", "근데 여기서 궁금한 게 있는데요"
6. **청취자 의식**: "듣고 계신 분들도 아마...", "출퇴근길에 이 부분 꼭 기억해두시면..."

#### 영어 스크립트 원칙

1. **Conversational tone**: No academic writing. Use contractions, informal phrasing
2. **Fillers**: "Right...", "Hmm", "Exactly!", "Oh that's interesting", "You know what..."
3. **Analogies**: Explain complex ideas with everyday comparisons
4. **Q&A rhythm**: Person1 asks → Person2 explains → Person1 reacts/follows up
5. **Bridges**: "But here's where it gets really interesting...", "That reminds me of..."
6. **Listener awareness**: "If you're driving right now, this is the part to pay attention to..."

### Script Structure Template

스크립트는 다음 구조를 따른다:

```
[인트로] (전체의 5%)
- Person1: 주제 소개, 왜 중요한지
- Person2: 동의 + 오늘 다룰 내용 예고

[본론 1-N] (전체의 80%)
- 핵심 주제를 3-6개 섹션으로 나눠서 진행
- 각 섹션마다 질문→설명→사례→반응 패턴
- 섹션 간 자연스러운 전환

[인사이트/시사점] (전체의 10%)
- 실용적 takeaway
- 청취자가 바로 적용할 수 있는 것

[마무리] (전체의 5%)
- 핵심 요약
- 다음 주제 예고 또는 마무리 인사
```

## Step 3: Save Script

생성된 스크립트를 파일로 저장:

```bash
# 파일명 규칙: podcast_YYYYMMDD_주제.txt
# 저장 위치: 현재 작업 디렉토리 또는 사용자 지정 경로
```

## Step 4: Audio Generation (Optional)

사용자가 오디오 생성도 요청한 경우에만 실행.
`${CLAUDE_SKILL_DIR}/podcast_tts.py` 스크립트를 사용한다.

### Prerequisites

```bash
pip install pydub
pip install fish-audio-sdk    # Fish Audio (기본, 저렴)
pip install elevenlabs        # ElevenLabs (고품질, 고가)
brew install ffmpeg           # macOS
```

FISH_API_KEY 또는 ELEVENLABS_API_KEY 환경변수 또는 .env 파일이 필요하다.

### Default Voice IDs

반드시 아래 Voice ID를 사용할 것. 다른 음성을 임의로 선택하지 않는다.

#### Fish Audio (기본 백엔드)

| 언어 | Person1 (Host) | Person2 (Expert) |
|------|---------------|-----------------|
| English | `860323c9e1354f6ea14079788b0bca0d` | `933563129e564b19a115bedd57b7406a` |
| Korean | `4cfdf04caeee49178c49c024d7a672e3` | `d5daef3484474a63a429f5952857f70c` |

#### ElevenLabs (대안)

| 언어 | Person1 (Host) | Person2 (Expert) |
|------|---------------|-----------------|
| English | `gs0tAILXbY5DNrJrsM6F` | `tnSpp4vdxKPjI9w0GnoV` |
| Korean | `CxErO97xpQgQXYmapDKX` | `8jHHF8rMqMlg8if2mOUe` |

### 실행 명령

```bash
# .env에서 API 키 로드 후 실행
export $(grep -v '^#' .env | xargs)

# Fish Audio 영어 팟캐스트
python ${CLAUDE_SKILL_DIR}/podcast_tts.py ./podcast_script.txt \
  -o ./podcast_output.mp3 \
  --backend fish \
  --voice-a 860323c9e1354f6ea14079788b0bca0d \
  --voice-b 933563129e564b19a115bedd57b7406a

# Fish Audio 한국어 팟캐스트
python ${CLAUDE_SKILL_DIR}/podcast_tts.py ./podcast_script.txt \
  -o ./podcast_output.mp3 \
  --backend fish \
  --voice-a 4cfdf04caeee49178c49c024d7a672e3 \
  --voice-b d5daef3484474a63a429f5952857f70c

# ElevenLabs 영어 팟캐스트
python ${CLAUDE_SKILL_DIR}/podcast_tts.py ./podcast_script.txt \
  -o ./podcast_output.mp3 \
  --backend elevenlabs \
  --voice-a gs0tAILXbY5DNrJrsM6F \
  --voice-b tnSpp4vdxKPjI9w0GnoV
```

추가 옵션은 `references/audio-generation.md`를 참고.

## Style Presets

### casual (기본)
- 친근하고 가벼운 톤
- 유머와 개인 일화 포함
- 추임새 빈도 높음

### deep-dive
- 분석적이고 체계적
- 데이터와 근거 중심
- 추임새는 적당히, 전문성 강조

### debate
- Person1과 Person2가 다른 입장
- 반론과 재반론 구조
- "그건 좀 다르게 볼 수도 있는데요..." 패턴

### storytelling
- 내러티브 중심
- 시간순 또는 인물 중심 전개
- 감성적 표현과 묘사 활용

## Important Notes

- 장편(30분+) 생성 시 반드시 `references/longform-strategy.md`를 읽을 것
- 스크립트 포맷은 반드시 `<Person1>`/`<Person2>` 태그 사용
- 한 대사가 4문장을 넘지 않도록 (자연스러운 대화 리듬 유지)
- 60분 스크립트는 context window 한계로 여러 번에 나눠 생성할 수 있음
  → 이 경우 이전 파트 요약을 context에 포함하여 연속성 유지
