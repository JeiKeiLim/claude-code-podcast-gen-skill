# Audio Generation Reference

`podcast_tts.py`를 사용한 오디오 생성 상세 가이드.

## Prerequisites

```bash
pip install pydub
pip install fish-audio-sdk    # Fish Audio (기본)
pip install elevenlabs        # ElevenLabs (대안)
brew install ffmpeg           # macOS
```

### .env 파일

```
FISH_API_KEY=your_fish_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

## CLI 사용법

```bash
python podcast_tts.py <transcript.txt> -o <output.mp3> \
    --backend <fish|elevenlabs> \
    --voice-a <PERSON1_VOICE_ID> \
    --voice-b <PERSON2_VOICE_ID> \
    [options]
```

### 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--backend` | `fish` | TTS 백엔드 (`fish` 또는 `elevenlabs`) |
| `-o, --output` | `podcast.mp3` | 출력 파일 경로 |
| `--voice-a` | (필수) | Person1 Voice ID |
| `--voice-b` | (필수) | Person2 Voice ID |
| `--model` | (백엔드별 기본값) | TTS 모델 |
| `--lang` | (자동) | 언어 코드 (`ko`, `en` 등) |
| `--speaker-pause` | `500` | 화자 전환 시 silence (ms) |
| `--speed` | `1.0` | 음성 속도 (0.7-1.2) |
| `--api-key` | 환경변수 | API 키 (`FISH_API_KEY` 또는 `ELEVENLABS_API_KEY`) |

## Default Voice IDs

### Fish Audio (기본 백엔드)

| 언어 | Person1 (Host) | Person2 (Expert) |
|------|---------------|-----------------|
| English | `860323c9e1354f6ea14079788b0bca0d` | `933563129e564b19a115bedd57b7406a` |
| Korean | `4cfdf04caeee49178c49c024d7a672e3` | `d5daef3484474a63a429f5952857f70c` |

### ElevenLabs (대안)

| 언어 | Person1 (Host) | Person2 (Expert) |
|------|---------------|-----------------|
| English | `gs0tAILXbY5DNrJrsM6F` | `tnSpp4vdxKPjI9w0GnoV` |
| Korean | `CxErO97xpQgQXYmapDKX` | `8jHHF8rMqMlg8if2mOUe` |

## 음성 커스터마이징

### Fish Audio

1. https://fish.audio/voice-library/ 접속
2. 카테고리/언어/성별로 필터
3. 원하는 음성의 URL에서 Voice ID 복사
4. `--voice-a`/`--voice-b` 옵션에 전달

### ElevenLabs

1. https://elevenlabs.io/voice-library 접속
2. 원하는 언어/성별로 필터
3. 음성 선택 → "Add to My Voices"
4. My Voices에서 Voice ID 복사
5. `--voice-a`/`--voice-b` 옵션에 전달

## 모델 선택

### Fish Audio

| 모델 | 용도 |
|------|------|
| `speech-02-turbo` | 기본 (빠르고 저렴) |

### ElevenLabs

| 모델 | 크레딧/글자 | 용도 |
|------|-----------|------|
| `eleven_multilingual_v2` | 1 | 최종 출력 (추천) |
| `eleven_flash_v2_5` | 0.5 | 드래프트/테스트 |
| `eleven_v3` | 1 | 최고 감정 표현 |

## 비용 비교 (10시간/월 기준)

| 백엔드 | 영어 10시간 | 한국어 10시간 | 비고 |
|--------|-----------|-------------|------|
| Fish Audio | ~$9 | ~$27 | UTF-8 바이트 과금 (한국어 3x) |
| ElevenLabs | ~$180 | ~$180 | 글자 수 과금 |

## podcast_tts.py의 특징

### previous_text / next_text (ElevenLabs only)

같은 화자의 연속 대사에서 앞뒤 텍스트를 ElevenLabs에 전달하여
세그먼트 간 prosody(억양/리듬) 연속성을 유지한다.

### 화자 전환 silence

- 화자가 바뀔 때: 500ms silence (대화의 자연스러운 텀)
- 같은 화자가 계속할 때: 200ms silence (문장 간 짧은 호흡)

### 볼륨 노멀라이제이션

출력 오디오를 -16 dBFS (팟캐스트 표준)로 자동 노멀라이즈한다.
