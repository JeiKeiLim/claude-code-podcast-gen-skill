#!/usr/bin/env python3
"""
podcast_tts.py — Podcast TTS Engine

<Person1>/<Person2> 포맷의 트랜스크립트를 ElevenLabs TTS로 변환하여
MP3 팟캐스트 오디오를 생성한다.

Features:
- previous_text/next_text로 세그먼트 간 연속성 유지
- 화자 전환 시 자연스러운 silence 삽입
- 볼륨 노멀라이제이션
- 진행률 표시

Dependencies:
    pip install elevenlabs pydub

Usage:
    python podcast_tts.py transcript.txt -o podcast.mp3 \
        --voice-a VOICE_ID_A --voice-b VOICE_ID_B
"""

import argparse
import io
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Optional

from elevenlabs import client as elevenlabs_client
from pydub import AudioSegment


# ──────────────────────────────────────────────
# Types
# ──────────────────────────────────────────────

@dataclass
class Utterance:
    speaker: str        # "Person1" or "Person2"
    text: str
    index: int


@dataclass
class TTSConfig:
    api_key: str
    voice_a: str                        # Person1 voice ID
    voice_b: str                        # Person2 voice ID
    model: str = "eleven_multilingual_v2"
    language_code: Optional[str] = None # "ko", "en", etc.
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.3
    speed: float = 1.0
    speaker_pause_ms: int = 500         # 화자 전환 시 silence
    same_speaker_pause_ms: int = 200    # 같은 화자 연속 시 silence
    output_format: str = "mp3_44100_128"


# ──────────────────────────────────────────────
# 1. Transcript Parser
# ──────────────────────────────────────────────

def parse_transcript(text: str) -> list[Utterance]:
    """
    <Person1>대사</Person1><Person2>대사</Person2> 형식의
    트랜스크립트를 Utterance 리스트로 파싱한다.

    Person1과 Person2가 반드시 교대할 필요는 없다.
    같은 화자가 연속으로 나올 수도 있다.
    """
    pattern = r"<(Person[12])>(.*?)</\1>"
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        raise ValueError(
            "트랜스크립트에서 <Person1>/<Person2> 태그를 찾을 수 없습니다."
        )

    utterances = []
    for i, (speaker, content) in enumerate(matches):
        clean = " ".join(content.split()).strip()
        if clean:
            utterances.append(Utterance(speaker=speaker, text=clean, index=i))

    print(f"  파싱 완료: {len(utterances)}개 대사")
    return utterances


# ──────────────────────────────────────────────
# 2. ElevenLabs TTS
# ──────────────────────────────────────────────

def generate_audio_segment(
    el_client: elevenlabs_client.ElevenLabs,
    utterance: Utterance,
    config: TTSConfig,
    prev_utterance: Optional[Utterance] = None,
    next_utterance: Optional[Utterance] = None,
) -> bytes:
    """
    단일 대사에 대해 ElevenLabs TTS를 호출하여 오디오 bytes를 반환한다.

    previous_text/next_text 파라미터를 사용하여
    세그먼트 간 prosody 연속성을 유지한다.
    """
    voice_id = config.voice_a if utterance.speaker == "Person1" else config.voice_b

    body = {
        "text": utterance.text,
        "model_id": config.model,
        "voice_settings": {
            "stability": config.stability,
            "similarity_boost": config.similarity_boost,
            "style": config.style,
            "use_speaker_boost": True,
            "speed": config.speed,
        },
    }

    if config.language_code:
        body["language_code"] = config.language_code

    # 연속성 유지: 같은 화자의 앞뒤 대사 텍스트를 전달
    if prev_utterance and prev_utterance.speaker == utterance.speaker:
        body["previous_text"] = prev_utterance.text
    if next_utterance and next_utterance.speaker == utterance.speaker:
        body["next_text"] = next_utterance.text

    audio_iter = el_client.text_to_speech.convert(
        voice_id=voice_id,
        output_format=config.output_format,
        **body,
    )

    return b"".join(chunk for chunk in audio_iter if chunk)


def generate_all_audio(
    utterances: list[Utterance],
    config: TTSConfig,
) -> list[tuple[Utterance, bytes]]:
    """
    모든 대사에 대해 순차적으로 TTS를 호출한다.
    진행률을 표시한다.
    """
    el_client = elevenlabs_client.ElevenLabs(api_key=config.api_key)
    results = []
    total = len(utterances)
    start_time = time.time()

    for i, utt in enumerate(utterances):
        prev_utt = utterances[i - 1] if i > 0 else None
        next_utt = utterances[i + 1] if i < total - 1 else None

        audio_bytes = generate_audio_segment(
            el_client, utt, config, prev_utt, next_utt
        )
        results.append((utt, audio_bytes))

        # 진행률 표시
        elapsed = time.time() - start_time
        pct = (i + 1) / total * 100
        eta = elapsed / (i + 1) * (total - i - 1)
        speaker_label = "A" if utt.speaker == "Person1" else "B"
        print(
            f"  [{i+1}/{total}] ({pct:.0f}%) "
            f"Speaker {speaker_label} | "
            f"{len(audio_bytes):,} bytes | "
            f"ETA {eta:.0f}s",
            end="\r",
        )

    print()  # 줄바꿈
    return results


# ──────────────────────────────────────────────
# 3. Audio Assembly
# ──────────────────────────────────────────────

def assemble_audio(
    segments: list[tuple[Utterance, bytes]],
    config: TTSConfig,
) -> AudioSegment:
    """
    개별 오디오 세그먼트를 하나의 오디오로 병합한다.
    화자 전환 시와 같은 화자 연속 시 다른 길이의 silence를 삽입한다.
    """
    combined = AudioSegment.empty()
    speaker_pause = AudioSegment.silent(duration=config.speaker_pause_ms)
    same_pause = AudioSegment.silent(duration=config.same_speaker_pause_ms)

    prev_speaker = None
    for utt, audio_bytes in segments:
        segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")

        if prev_speaker is not None:
            if utt.speaker != prev_speaker:
                combined += speaker_pause
            else:
                combined += same_pause

        combined += segment
        prev_speaker = utt.speaker

    return combined


def normalize_audio(audio: AudioSegment, target_dbfs: float = -16.0) -> AudioSegment:
    """
    볼륨을 팟캐스트 표준(-16 dBFS)으로 노멀라이즈한다.
    """
    change = target_dbfs - audio.dBFS
    return audio.apply_gain(change)


# ──────────────────────────────────────────────
# 4. Main Pipeline
# ──────────────────────────────────────────────

def generate_podcast(
    transcript_path: str,
    output_path: str,
    config: TTSConfig,
) -> str:
    """
    트랜스크립트 파일 → MP3 팟캐스트 생성 메인 파이프라인.

    Returns:
        output_path (str): 생성된 MP3 파일 경로
    """
    print(f"\nPodcast TTS Engine")
    print(f"{'─' * 40}")

    # 1. 트랜스크립트 파싱
    print(f"\n트랜스크립트 로드: {transcript_path}")
    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()
    utterances = parse_transcript(text)

    # 2. 비용 추정
    total_chars = sum(len(u.text) for u in utterances)
    print(f"  총 글자 수: {total_chars:,}")
    print(f"  예상 크레딧: ~{total_chars:,} (Multilingual v2 기준)")

    # 3. TTS 생성
    print(f"\nTTS 생성 중 (model: {config.model})...")
    segments = generate_all_audio(utterances, config)

    # 4. 오디오 병합
    print(f"\n오디오 병합 중...")
    combined = assemble_audio(segments, config)

    # 5. 노멀라이즈
    print(f"  볼륨 노멀라이제이션 (-16 dBFS)...")
    combined = normalize_audio(combined)

    # 6. 저장
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    combined.export(output_path, format="mp3", bitrate="192k")

    duration_min = len(combined) / 1000 / 60
    file_size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\n완료!")
    print(f"  파일: {output_path}")
    print(f"  길이: {duration_min:.1f}분")
    print(f"  크기: {file_size_mb:.1f}MB")
    print(f"{'─' * 40}\n")

    return output_path


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Podcast TTS — <Person1>/<Person2> 트랜스크립트를 MP3로 변환"
    )
    parser.add_argument("transcript", help="트랜스크립트 파일 경로 (.txt)")
    parser.add_argument("-o", "--output", default="podcast.mp3", help="출력 파일 경로")
    parser.add_argument("--voice-a", required=True, help="Person1 ElevenLabs Voice ID")
    parser.add_argument("--voice-b", required=True, help="Person2 ElevenLabs Voice ID")
    parser.add_argument(
        "--model",
        default="eleven_multilingual_v2",
        help="ElevenLabs 모델 (기본: eleven_multilingual_v2)",
    )
    parser.add_argument("--lang", default=None, help="언어 코드 (ko, en 등)")
    parser.add_argument(
        "--speaker-pause", type=int, default=500, help="화자 전환 silence (ms)"
    )
    parser.add_argument("--speed", type=float, default=1.0, help="음성 속도 (0.7-1.2)")
    parser.add_argument(
        "--api-key",
        default=None,
        help="ElevenLabs API 키 (미지정 시 ELEVENLABS_API_KEY 환경변수 사용)",
    )

    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print("ElevenLabs API 키가 필요합니다.")
        print("  --api-key 옵션 또는 ELEVENLABS_API_KEY 환경변수를 설정하세요.")
        sys.exit(1)

    config = TTSConfig(
        api_key=api_key,
        voice_a=args.voice_a,
        voice_b=args.voice_b,
        model=args.model,
        language_code=args.lang,
        speed=args.speed,
        speaker_pause_ms=args.speaker_pause,
    )

    generate_podcast(args.transcript, args.output, config)


if __name__ == "__main__":
    main()
