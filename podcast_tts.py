#!/usr/bin/env python3
"""
podcast_tts.py — Podcast TTS Engine

Converts <Person1>/<Person2> transcript format into MP3 podcast audio via TTS.

Supported backends:
- elevenlabs: ElevenLabs TTS (high quality, expensive)
- fish: Fish Audio TTS (high quality, affordable)

Dependencies:
    pip install pydub
    pip install elevenlabs        # for ElevenLabs backend
    pip install fish-audio-sdk    # for Fish Audio backend

Usage:
    # ElevenLabs
    python podcast_tts.py transcript.txt -o podcast.mp3 \
        --backend elevenlabs \
        --voice-a VOICE_ID_A --voice-b VOICE_ID_B

    # Fish Audio
    python podcast_tts.py transcript.txt -o podcast.mp3 \
        --backend fish \
        --voice-a VOICE_ID_A --voice-b VOICE_ID_B
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
    backend: str = "elevenlabs"         # "elevenlabs" or "fish"
    model: str = ""                     # backend-specific model
    language_code: Optional[str] = None # "ko", "en", etc.
    speed: float = 1.0
    speaker_pause_ms: int = 500         # silence between different speakers
    same_speaker_pause_ms: int = 200    # silence between same speaker
    # ElevenLabs-specific
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.3
    output_format: str = "mp3_44100_128"

    def __post_init__(self):
        if not self.model:
            self.model = {
                "elevenlabs": "eleven_multilingual_v2",
                "fish": "speech-02-turbo",
            }.get(self.backend, "")


# ──────────────────────────────────────────────
# 1. Transcript Parser
# ──────────────────────────────────────────────

def parse_transcript(text: str) -> list[Utterance]:
    pattern = r"<(Person[12])>(.*?)</\1>"
    matches = re.findall(pattern, text, re.DOTALL)

    if not matches:
        raise ValueError(
            "No <Person1>/<Person2> tags found in transcript."
        )

    utterances = []
    for i, (speaker, content) in enumerate(matches):
        clean = " ".join(content.split()).strip()
        if clean:
            utterances.append(Utterance(speaker=speaker, text=clean, index=i))

    print(f"  Parsed: {len(utterances)} utterances")
    return utterances


# ──────────────────────────────────────────────
# 2. Disk Cache
# ──────────────────────────────────────────────

def _transcript_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def _cache_dir(output_path: str, transcript_hash: str) -> Path:
    parent = Path(output_path).resolve().parent
    return parent / f"podcast_tts_cache_{transcript_hash}"


def _cache_meta_path(cache: Path) -> Path:
    return cache / "meta.json"


def _segment_path(cache: Path, index: int, speaker: str) -> Path:
    return cache / f"{index:04d}_{speaker}.mp3"


def init_cache(output_path: str, transcript_text: str) -> Path:
    full_hash = _transcript_hash(transcript_text)
    cache = _cache_dir(output_path, full_hash)
    meta_path = _cache_meta_path(cache)

    if cache.exists():
        if meta_path.exists():
            meta = json.loads(meta_path.read_text())
            if meta.get("transcript_hash") == full_hash:
                cached = len(list(cache.glob("*_Person*.mp3")))
                print(f"  Cache found: {cache.name} ({cached} segments cached)")
                return cache
        # Hash mismatch — stale cache
        print(f"  Script changed, resetting cache: {cache.name}")
        shutil.rmtree(cache)

    cache.mkdir(parents=True)
    meta_path.write_text(json.dumps({"transcript_hash": full_hash}))
    print(f"  Cache directory created: {cache.name}")
    return cache


def cleanup_cache(cache: Path) -> None:
    if cache.exists():
        shutil.rmtree(cache)
        print(f"  Cache cleaned up: {cache.name}")


# ──────────────────────────────────────────────
# 3. TTS Backends
# ──────────────────────────────────────────────

def _generate_elevenlabs(
    utterance: Utterance,
    config: TTSConfig,
    el_client,
    prev_utterance: Optional[Utterance] = None,
    next_utterance: Optional[Utterance] = None,
) -> bytes:
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


def _generate_fish(
    utterance: Utterance,
    config: TTSConfig,
    fish_client,
) -> bytes:
    from fishaudio.types import TTSConfig as FishTTSConfig, Prosody

    voice_id = config.voice_a if utterance.speaker == "Person1" else config.voice_b

    fish_config = FishTTSConfig(
        reference_id=voice_id,
        format="mp3",
        prosody=Prosody(speed=config.speed),
        latency="balanced",
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            audio = fish_client.tts.convert(
                text=utterance.text,
                config=fish_config,
            )
            return bytes(audio)
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"\n  ⚠ Retry {attempt+1}/{max_retries} after error: {e}. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def generate_all_audio(
    utterances: list[Utterance],
    config: TTSConfig,
    cache: Path,
) -> list[tuple[Utterance, Path]]:
    # Initialize backend client
    if config.backend == "elevenlabs":
        from elevenlabs import client as elevenlabs_client
        client = elevenlabs_client.ElevenLabs(api_key=config.api_key)
    elif config.backend == "fish":
        from fishaudio import FishAudio
        client = FishAudio(api_key=config.api_key)
    else:
        raise ValueError(f"Unknown backend: {config.backend}")

    results = []
    total = len(utterances)
    skipped = 0
    start_time = time.time()

    for i, utt in enumerate(utterances):
        seg_path = _segment_path(cache, i, utt.speaker)

        # Resume: skip already-cached segments
        if seg_path.exists() and seg_path.stat().st_size > 0:
            results.append((utt, seg_path))
            skipped += 1
            continue

        if config.backend == "elevenlabs":
            prev_utt = utterances[i - 1] if i > 0 else None
            next_utt = utterances[i + 1] if i < total - 1 else None
            audio_bytes = _generate_elevenlabs(
                utt, config, client, prev_utt, next_utt
            )
        else:
            audio_bytes = _generate_fish(utt, config, client)

        # Write to disk immediately
        seg_path.write_bytes(audio_bytes)
        results.append((utt, seg_path))

        elapsed = time.time() - start_time
        generated = (i + 1) - skipped
        pct = (i + 1) / total * 100
        eta = elapsed / generated * (total - i - 1) if generated > 0 else 0
        speaker_label = "A" if utt.speaker == "Person1" else "B"
        print(
            f"  [{i+1}/{total}] ({pct:.0f}%) "
            f"Speaker {speaker_label} | "
            f"{len(audio_bytes):,} bytes | "
            f"ETA {eta:.0f}s",
            end="\r",
        )

    print()
    if skipped > 0:
        print(f"  Loaded {skipped} segments from cache, generated {total - skipped} new")
    return results


# ──────────────────────────────────────────────
# 4. Audio Assembly
# ──────────────────────────────────────────────

def assemble_audio(
    segments: list[tuple[Utterance, Path]],
    config: TTSConfig,
) -> AudioSegment:
    combined = AudioSegment.empty()
    speaker_pause = AudioSegment.silent(duration=config.speaker_pause_ms)
    same_pause = AudioSegment.silent(duration=config.same_speaker_pause_ms)

    prev_speaker = None
    for utt, seg_path in segments:
        segment = AudioSegment.from_file(str(seg_path), format="mp3")

        if prev_speaker is not None:
            if utt.speaker != prev_speaker:
                combined += speaker_pause
            else:
                combined += same_pause

        combined += segment
        prev_speaker = utt.speaker

    return combined


def normalize_audio(audio: AudioSegment, target_dbfs: float = -16.0) -> AudioSegment:
    change = target_dbfs - audio.dBFS
    return audio.apply_gain(change)


# ──────────────────────────────────────────────
# 5. Main Pipeline
# ──────────────────────────────────────────────

def generate_podcast(
    transcript_path: str,
    output_path: str,
    config: TTSConfig,
) -> str:
    print(f"\nPodcast TTS Engine ({config.backend})")
    print(f"{'─' * 40}")

    # 1. Parse transcript
    print(f"\nLoading transcript: {transcript_path}")
    with open(transcript_path, "r", encoding="utf-8") as f:
        text = f.read()
    utterances = parse_transcript(text)

    # 2. Initialize cache
    cache = init_cache(output_path, text)

    # 3. Cost estimate
    total_chars = sum(len(u.text) for u in utterances)
    total_bytes_utf8 = sum(len(u.text.encode("utf-8")) for u in utterances)
    print(f"  Total characters: {total_chars:,}")
    if config.backend == "fish":
        print(f"  Total UTF-8 bytes: {total_bytes_utf8:,}")
    print(f"  Model: {config.model}")

    # 4. Generate TTS (segments cached to disk)
    print(f"\nGenerating TTS...")
    segments = generate_all_audio(utterances, config, cache)

    # 5. Merge audio
    print(f"\nMerging audio...")
    combined = assemble_audio(segments, config)

    # 6. Normalize
    print(f"  Volume normalization (-16 dBFS)...")
    combined = normalize_audio(combined)

    # 7. Save
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    combined.export(output_path, format="mp3", bitrate="192k")

    duration_min = len(combined) / 1000 / 60
    file_size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"\nDone!")
    print(f"  File: {output_path}")
    print(f"  Duration: {duration_min:.1f} min")
    print(f"  Size: {file_size_mb:.1f} MB")
    print(f"{'─' * 40}\n")

    # 8. Clean up cache on success
    cleanup_cache(cache)

    return output_path


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Podcast TTS — Convert <Person1>/<Person2> transcript to MP3"
    )
    parser.add_argument("transcript", help="Transcript file path (.txt)")
    parser.add_argument("-o", "--output", default="podcast.mp3", help="Output file path")
    parser.add_argument(
        "--backend",
        choices=["elevenlabs", "fish"],
        default="fish",
        help="TTS backend (default: fish)",
    )
    parser.add_argument("--voice-a", required=True, help="Person1 Voice ID")
    parser.add_argument("--voice-b", required=True, help="Person2 Voice ID")
    parser.add_argument("--model", default=None, help="TTS model (uses backend default if omitted)")
    parser.add_argument("--lang", default=None, help="Language code (ko, en, etc.)")
    parser.add_argument(
        "--speaker-pause", type=int, default=500, help="Silence between speakers (ms)"
    )
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed (0.7-1.2)")
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (falls back to ELEVENLABS_API_KEY or FISH_API_KEY env var)",
    )

    args = parser.parse_args()

    # Resolve API key
    env_key = {
        "elevenlabs": "ELEVENLABS_API_KEY",
        "fish": "FISH_API_KEY",
    }[args.backend]
    api_key = args.api_key or os.environ.get(env_key)
    if not api_key:
        print(f"API key required.")
        print(f"  Set --api-key or {env_key} environment variable.")
        sys.exit(1)

    config = TTSConfig(
        api_key=api_key,
        voice_a=args.voice_a,
        voice_b=args.voice_b,
        backend=args.backend,
        model=args.model or "",
        language_code=args.lang,
        speed=args.speed,
        speaker_pause_ms=args.speaker_pause,
    )

    generate_podcast(args.transcript, args.output, config)


if __name__ == "__main__":
    main()
