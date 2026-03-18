# Audio Generation Reference

Detailed guide for generating audio with `podcast_tts.py`.

## Prerequisites

```bash
pip install pydub
pip install fish-audio-sdk    # Fish Audio (default)
pip install elevenlabs        # ElevenLabs (alternative)
brew install ffmpeg           # macOS
```

### .env File

```
FISH_API_KEY=your_fish_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

## CLI Usage

```bash
python podcast_tts.py <transcript.txt> -o <output.mp3> \
    --backend <fish|elevenlabs> \
    --voice-a <PERSON1_VOICE_ID> \
    --voice-b <PERSON2_VOICE_ID> \
    [options]
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--backend` | `fish` | TTS backend (`fish` or `elevenlabs`) |
| `-o, --output` | `podcast.mp3` | Output file path |
| `--voice-a` | (required) | Person1 Voice ID |
| `--voice-b` | (required) | Person2 Voice ID |
| `--model` | (backend default) | TTS model |
| `--lang` | (auto) | Language code (`ko`, `en`, etc.) |
| `--speaker-pause` | `500` | Silence on speaker change (ms) |
| `--speed` | `1.0` | Speech speed (0.7-1.2) |
| `--api-key` | env var | API key (`FISH_API_KEY` or `ELEVENLABS_API_KEY`) |

## Default Voice IDs

### Fish Audio (default backend)

| Language | Person1 (Host) | Person2 (Expert) |
|----------|---------------|-----------------|
| English | `e3f4539c9a2544e7ada516a4323006f8` | `933563129e564b19a115bedd57b7406a` |
| Korean | `4cfdf04caeee49178c49c024d7a672e3` | `d5daef3484474a63a429f5952857f70c` |

### ElevenLabs (alternative)

| Language | Person1 (Host) | Person2 (Expert) |
|----------|---------------|-----------------|
| English | `gs0tAILXbY5DNrJrsM6F` | `tnSpp4vdxKPjI9w0GnoV` |
| Korean | `CxErO97xpQgQXYmapDKX` | `8jHHF8rMqMlg8if2mOUe` |

## Voice Customization

### Fish Audio

1. Visit https://fish.audio/voice-library/
2. Filter by category, language, or gender
3. Copy the Voice ID from the desired voice's URL
4. Pass to `--voice-a`/`--voice-b` options

### ElevenLabs

1. Visit https://elevenlabs.io/voice-library
2. Filter by language/gender
3. Select a voice → "Add to My Voices"
4. Copy the Voice ID from My Voices
5. Pass to `--voice-a`/`--voice-b` options

## Model Selection

### Fish Audio

| Model | Use case |
|-------|----------|
| `speech-02-turbo` | Default (fast, affordable) |

### ElevenLabs

| Model | Credits/char | Use case |
|-------|-------------|----------|
| `eleven_multilingual_v2` | 1 | Final output (recommended) |
| `eleven_flash_v2_5` | 0.5 | Drafts/testing |
| `eleven_v3` | 1 | Best emotional expression |

## Cost Comparison (per 10 hours/month)

| Backend | English 10hrs | Korean 10hrs | Notes |
|---------|--------------|-------------|-------|
| Fish Audio | ~$9 | ~$27 | Billed by UTF-8 bytes (Korean ~3x) |
| ElevenLabs | ~$180 | ~$180 | Billed by character count |

## podcast_tts.py Features

### previous_text / next_text (ElevenLabs only)

For consecutive utterances by the same speaker, the surrounding text is passed to
ElevenLabs to maintain prosody (intonation/rhythm) continuity across segments.

### Speaker Transition Silence

- Speaker change: 500ms silence (natural conversational pause)
- Same speaker continues: 200ms silence (short breath between sentences)

### Volume Normalization

Output audio is automatically normalized to -16 dBFS (podcast standard).
