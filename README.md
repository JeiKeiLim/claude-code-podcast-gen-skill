# podcast-gen

A Claude Code skill that transforms source content into two-person conversational podcast scripts, with optional audio generation via Fish Audio or ElevenLabs TTS.

Inspired by Google NotebookLM's audio overview feature.

## Features

- Generates natural two-person dialogue scripts in `<Person1>`/`<Person2>` tag format
- Supports Korean and English
- Multiple style presets: `casual`, `deep-dive`, `debate`, `storytelling`
- Configurable duration (10min / 30min / 60min)
- Long-form strategy with structured section breaks for 30min+ episodes
- Built-in TTS engine (`podcast_tts.py`) with two backends:
  - **Fish Audio** (default) — high quality, affordable (~$9/10hrs English)
  - **ElevenLabs** — premium quality, higher cost (~$180/10hrs)

## Installation

Clone this repository into your Claude Code skills directory:

```bash
git clone https://github.com/JeiKeiLim/claude-code-podcast-gen-skill.git ~/.claude/skills/podcast-gen
```

The skill will be available in your next Claude Code session.

### Audio generation dependencies (optional)

```bash
pip install pydub
pip install fish-audio-sdk    # Fish Audio (default, affordable)
pip install elevenlabs        # ElevenLabs (alternative, premium)
brew install ffmpeg           # macOS
```

Set your API key in `.env` or as an environment variable:

```bash
# Fish Audio (default)
export FISH_API_KEY=your_key_here

# ElevenLabs (alternative)
export ELEVENLABS_API_KEY=your_key_here
```

## Usage

Once installed, Claude Code will automatically detect when you want to create a podcast. You can also invoke it directly:

```
/podcast-gen
```

### Examples

```
# Generate a Korean podcast script from a document
"이 논문을 30분짜리 팟캐스트로 만들어줘"

# Generate an English podcast from analysis
"Turn this analysis into a casual 10-minute podcast"

# Generate with audio output
"Create a deep-dive podcast from this article and generate the audio too"
```

### Parameters

| Parameter | Default | Options |
|-----------|---------|---------|
| language | auto-detect | `ko`, `en` |
| duration | 30min | `10`, `30`, `60` (minutes) |
| style | casual | `casual`, `deep-dive`, `debate`, `storytelling` |
| audio | false | Set to true to generate MP3 |

## Audio Generation

The included `podcast_tts.py` script converts transcript files to MP3. It features:

- **Two TTS backends** — Fish Audio (default, affordable) and ElevenLabs (premium)
- **Smart pauses** — 500ms for speaker switches, 200ms for same-speaker continuation
- **Volume normalization** to -16 dBFS (podcast standard)
- **Progress tracking** with ETA
- **Prosody continuity** via `previous_text`/`next_text` (ElevenLabs backend)

### Cost comparison (10 hours/month)

| Backend | English | Korean | Notes |
|---------|---------|--------|-------|
| Fish Audio | ~$9 | ~$27 | Billed per UTF-8 bytes |
| ElevenLabs | ~$180 | ~$180 | Billed per character |

See [references/audio-generation.md](references/audio-generation.md) for detailed options and voice IDs.

## File Structure

```
podcast-gen/
├── SKILL.md                          # Main skill definition
├── podcast_tts.py                    # TTS engine (Fish Audio / ElevenLabs)
├── references/
│   ├── audio-generation.md           # Audio generation detailed guide
│   └── longform-strategy.md          # Strategy for 30min+ episodes
├── README.md
└── LICENSE
```

## License

MIT
