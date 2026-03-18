---
name: podcast-gen
description: "Transforms source content into natural two-person conversational podcast scripts and optionally generates audio via Fish Audio or ElevenLabs TTS. Handles research papers, technical docs, articles, code repos, and any text content. Use this skill whenever the user wants to create a podcast, generate a podcast script, convert documents or analysis into audio conversations, or mentions 'podcast', 'audio conversation', 'NotebookLM style', or 'GenFM'. Also trigger when the user wants two speakers to discuss a topic, asks for a conversational summary, or wants to listen to content during a commute. Trigger even if the user says things like 'make this listenable', 'turn this into a conversation', 'discuss this paper', or uses Korean terms like '팟캐스트' or '대화형으로 만들어줘'."
argument-hint: "[source file, URL, or topic]"
---

# Podcast Generator

Transform source content into a two-person conversational podcast script, with optional audio generation.

```
Source content → Script (<Person1>/<Person2>) → (optional) podcast_tts.py → MP3
```

## Language Matching

Generate the podcast script in the same language as the user's request — not the source content's language. If the user writes in English, produce an English podcast even if the source is in Korean (and vice versa). If ambiguous, ask.

This matters because TTS voice selection depends on the output language, and listeners expect the podcast language to match what they asked for.

## Step 1: Determine Parameters

Extract these from the user's request (use defaults if unspecified):

| Parameter | Default | Options |
|-----------|---------|---------|
| language | match user's request language | `ko`, `en` |
| duration | 30min | `10`, `30`, `60` (minutes) |
| style | casual | `casual`, `deep-dive`, `debate`, `storytelling` |
| audio | false | whether to generate MP3 audio |

Source content comes from `$ARGUMENTS` — typically a file path, URL, or topic description.

### Duration to Word Count

These word counts are calibrated to real TTS output timing. Hitting the target word count is important — undershoot means the podcast ends early, overshoot means it runs long and the user loses trust in duration estimates.

| Target | Korean words | English words | Approx. lines |
|--------|-------------|--------------|---------------|
| 10 min | ~1,500 | ~1,600 | 40–50 |
| 30 min | ~4,500 | ~4,800 | 120–150 |
| 60 min | ~9,000 | ~9,600 | 250–300 |

For durations not listed (e.g., 20 or 40 minutes), interpolate using ~150 Korean words/min or ~160 English words/min.

## Step 2: Generate Script

### Output Format

```
<Person1>Line of dialogue here</Person1>
<Person2>Line of dialogue here</Person2>
<Person1>Line of dialogue here</Person1>
<Person2>Line of dialogue here</Person2>
```

- `<Person1>` = Host (asks questions, introduces topics, handles transitions)
- `<Person2>` = Expert/Guest (explains, provides insight, gives depth)
- No blank lines between tags — consecutive lines only
- Keep each utterance to 1–4 sentences. Longer than that and it starts sounding like a monologue instead of a conversation.

### Conversation Guidelines

The goal is to sound like two real people having an engaging conversation — not a scripted presentation read by two voices.

**Making it sound natural:**
- Use contractions and informal phrasing (spoken language, not written)
- Include verbal fillers and reactions — these are what make dialogue feel human
- Use analogies and concrete examples instead of abstract explanations
- Maintain a Q&A rhythm: Person1 asks → Person2 explains → Person1 reacts → follow-up

**Korean-specific patterns:**
- Use conversational endings: "~거든요", "~잖아요", "~인 거죠" (not formal "~입니다")
- Reactions: "음...", "아~", "맞아요", "오~", "진짜요?", "흥미롭네요"
- Bridges: "근데 여기서 궁금한 게 있는데요", "그런데 이 부분에서 한 가지 더..."
- Listener hooks: "듣고 계신 분들도 아마...", "출퇴근길에 이 부분 꼭 기억해두시면..."

**English-specific patterns:**
- Contractions: "it's", "doesn't", "we're" (not "it is", "does not")
- Reactions: "Right...", "Hmm", "Exactly!", "Oh that's interesting", "You know what..."
- Bridges: "But here's where it gets really interesting...", "That reminds me of..."
- Listener hooks: "If you're driving right now, this is the part to pay attention to..."

### Script Structure

```
[Intro] (5% of total)
  Person1: Introduce the topic and why it matters
  Person2: Agree + preview what's coming

[Main sections 1–N] (80% of total)
  3–6 sections covering the key ideas
  Each section: question → explanation → example → reaction
  Natural transitions between sections

[Insights/Takeaways] (10% of total)
  Practical takeaways the listener can act on

[Wrap-up] (5% of total)
  Recap key points, closing remarks
```

For 30min+ episodes, read `references/longform-strategy.md` first — it covers attention management, section pacing, and split-generation strategy for 60min episodes.

## Style Presets

### casual (default)
Friendly, light tone. The speakers genuinely enjoy the topic and each other's company. Include humor, personal anecdotes, and relatable comparisons. Reactions are frequent and enthusiastic. Think: two friends chatting over coffee about something they find fascinating.

### deep-dive
Analytical, structured, thorough. The speakers respect the complexity of the topic and want to do it justice. Data and evidence take center stage. Reactions are measured but appreciative. Think: a well-prepared interview on a serious podcast like Lex Fridman or a good NPR segment.

### debate
Person1 and Person2 take different positions. They push back on each other respectfully but firmly. The tension comes from genuine disagreement, not hostility. Include concessions when the other side makes a good point. Think: an Oxford-style debate or an intelligence squared episode.

### storytelling
Narrative-driven, chronological or character-focused. One speaker often takes the lead in telling the story while the other reacts, asks clarifying questions, and draws out key moments. Emotional beats matter. Think: a true-crime or history podcast where the story itself is the draw.

## Step 3: Save Script

Save the generated script to a file:
- Filename pattern: `podcast_YYYYMMDD_topic.txt`
- Location: current working directory or user-specified path

## Step 4: Audio Generation (optional)

Only run this when the user explicitly asks for audio. Use `${CLAUDE_SKILL_DIR}/podcast_tts.py`.

### Prerequisites

```bash
pip install pydub
pip install fish-audio-sdk    # Fish Audio (default, affordable)
pip install elevenlabs        # ElevenLabs (premium alternative)
brew install ffmpeg           # macOS
```

Requires `FISH_API_KEY` or `ELEVENLABS_API_KEY` in environment or `.env` file.

### Voice IDs

Use these specific voice IDs — they've been selected for natural podcast-style delivery. Using arbitrary voices often results in mismatched tone or pacing that sounds off for conversational content.

#### Fish Audio (default — ~$9/10hrs English, ~$27/10hrs Korean)

| Language | Person1 (Host) | Person2 (Expert) |
|----------|---------------|-----------------|
| English | `e3f4539c9a2544e7ada516a4323006f8` | `933563129e564b19a115bedd57b7406a` |
| Korean | `4cfdf04caeee49178c49c024d7a672e3` | `d5daef3484474a63a429f5952857f70c` |

#### ElevenLabs (premium — ~$180/10hrs)

| Language | Person1 (Host) | Person2 (Expert) |
|----------|---------------|-----------------|
| English | `gs0tAILXbY5DNrJrsM6F` | `tnSpp4vdxKPjI9w0GnoV` |
| Korean | `CxErO97xpQgQXYmapDKX` | `8jHHF8rMqMlg8if2mOUe` |

### Running TTS

```bash
# Load API keys from .env
export $(grep -v '^#' .env | xargs)

# Fish Audio (default) — substitute voice IDs from the tables above based on output language
python ${CLAUDE_SKILL_DIR}/podcast_tts.py ./podcast_script.txt \
  -o ./podcast_output.mp3 \
  --backend fish \
  --voice-a e3f4539c9a2544e7ada516a4323006f8 \
  --voice-b 933563129e564b19a115bedd57b7406a

# ElevenLabs — substitute voice IDs from the tables above based on output language
python ${CLAUDE_SKILL_DIR}/podcast_tts.py ./podcast_script.txt \
  -o ./podcast_output.mp3 \
  --backend elevenlabs \
  --voice-a gs0tAILXbY5DNrJrsM6F \
  --voice-b tnSpp4vdxKPjI9w0GnoV
```

The examples above use English voice IDs. For Korean, swap them with the Korean IDs from the tables above. See `references/audio-generation.md` for additional options (speed, pause duration, model selection).

### Crash Recovery

The TTS script caches each audio segment to disk as it's generated. If the process fails mid-generation (API timeout, connection drop, etc.), **just re-run the exact same command** — it will skip already-generated segments and resume from where it left off. Do not regenerate the script or change any arguments. Make sure to re-export the `.env` file before re-running if using environment variables for API keys.
