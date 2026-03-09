# podcast-gen

A Claude Code skill that transforms source content into two-person conversational podcast scripts, with optional audio generation via [Podcastfy](https://github.com/souzatharsis/podcastfy).

Inspired by Google NotebookLM's audio overview feature.

## Features

- Generates natural two-person dialogue scripts in `<Person1>`/`<Person2>` tag format
- Supports Korean and English
- Multiple style presets: `casual`, `deep-dive`, `debate`, `storytelling`
- Configurable duration (10min / 30min / 60min)
- Long-form strategy with structured section breaks for 30min+ episodes
- Optional TTS audio generation via Podcastfy + ElevenLabs

## Installation

Clone this repository into your Claude Code skills directory:

```bash
git clone https://github.com/JeiKeiLim/claude-code-podcast-gen-skill.git ~/.claude/skills/podcast-gen
```

The skill will be available in your next Claude Code session.

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
| audio | false | Set to true to generate MP3 via Podcastfy |

## Audio Generation (Optional)

To generate audio from scripts, you need:

1. [Podcastfy](https://github.com/souzatharsis/podcastfy) installed (`pip install podcastfy`)
2. [ffmpeg](https://ffmpeg.org/) installed (`brew install ffmpeg` on macOS)
3. An [ElevenLabs](https://elevenlabs.io/) API key in your `.env` file

See [references/podcastfy-config.md](references/podcastfy-config.md) for detailed configuration.

## File Structure

```
podcast-gen/
├── SKILL.md                          # Main skill definition
├── references/
│   ├── podcastfy-config.md           # Podcastfy & ElevenLabs configuration guide
│   └── longform-strategy.md          # Strategy for 30min+ episodes
├── README.md
└── LICENSE
```

## License

MIT
