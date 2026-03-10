# Podcastfy Configuration Reference

Podcastfy로 오디오를 생성할 때 필요한 설정 가이드.

## Prerequisites

```bash
pip install podcastfy
brew install ffmpeg  # macOS
```

### .env 파일 (프로젝트 루트)
```
ELEVENLABS_API_KEY=your_key_here
```

## Config YAML 템플릿

### 한국어 팟캐스트

```yaml
text_to_speech:
  default_tts_model: "elevenlabs"
  elevenlabs:
    default_voices:
      question: "CxErO97xpQgQXYmapDKX"
      answer: "8jHHF8rMqMlg8if2mOUe"
    model: "eleven_multilingual_v2"
```

### 영어 팟캐스트

```yaml
text_to_speech:
  default_tts_model: "elevenlabs"
  elevenlabs:
    default_voices:
      question: "gs0tAILXbY5DNrJrsM6F"
      answer: "tnSpp4vdxKPjI9w0GnoV"
    model: "eleven_multilingual_v2"
```

## 한국어 음성 설정 방법

ElevenLabs 기본 음성은 영어이므로 한국어 음성을 별도로 설정해야 한다.

1. https://elevenlabs.io/voice-library 접속
2. 언어 필터 → "Korean" 선택
3. 남성/여성 음성 각 1개 선택 → "Add to My Voices"
4. My Voices에서 Voice ID 복사
5. config YAML의 `question`/`answer`에 Voice ID 입력

## CLI 실행

```bash
# 스크립트에서 오디오 생성
python -m podcastfy.client \
  --transcript ./podcast_script.txt \
  --tts-model elevenlabs \
  --conversation-config podcast_config.yaml
```

## ElevenLabs 모델 선택

| 모델 | 크레딧/글자 | 최대 글자수 | 용도 |
|------|-----------|-----------|------|
| eleven_multilingual_v2 | 1 | 10,000 | 최종 출력 (추천) |
| eleven_flash_v2_5 | 0.5 | 40,000 | 드래프트/테스트 |
| eleven_v3 | 1 | 3,000 | 최고 감정 표현 |

## 비용 추정

| 시간 | 한국어 글자 수 | Multilingual v2 | Flash v2.5 |
|------|-------------|----------------|------------|
| 10분 | ~5,000 | 5,000 크레딧 | 2,500 크레딧 |
| 30분 | ~15,000 | 15,000 크레딧 | 7,500 크레딧 |
| 60분 | ~30,000 | 30,000 크레딧 | 15,000 크레딧 |

## 후처리 (ffmpeg)

```bash
# 볼륨 노멀라이제이션 (팟캐스트 표준)
ffmpeg -i input.mp3 -af loudnorm=I=-16:TP=-1.5:LRA=11 output.mp3
```
