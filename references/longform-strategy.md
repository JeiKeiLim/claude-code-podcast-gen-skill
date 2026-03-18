# Long-form Podcast Strategy (30min+)

Long-form podcasts need structural thinking, not just more words. Listeners' attention fades in 5–7 minute cycles, so the script needs "reset points" — moments that re-engage the listener.

## Reset Point Techniques

1. **Topic shift**: "That said, let's look at this from a completely different angle..."
2. **Surprise reveal**: "But here's where it gets unexpected..."
3. **Listener address**: "Now if you're listening to this, you're probably thinking..."
4. **Personal anecdote**: "I actually had a similar experience where..."
5. **Recap + tease**: "So to summarize what we've covered... but honestly the real story is what comes next"

## Section Structure

### 30-minute podcast (~9,000 words KO / ~9,600 words EN)

```
[Intro]         2 min    ~600 words
[Section 1]     6 min    ~1,800 words    ← Core topic introduction
[Transition]    0.5 min  ~150 words
[Section 2]     6 min    ~1,800 words    ← Deep analysis
[Transition]    0.5 min  ~150 words
[Section 3]     6 min    ~1,800 words    ← Counterpoint / different angle
[Transition]    0.5 min  ~150 words
[Section 4]     5 min    ~1,500 words    ← Practical implications
[Wrap-up]       3 min    ~900 words
Total          30 min   ~8,850 words
```

### 60-minute podcast (~18,000 words KO / ~19,200 words EN)

```
[Intro]         3 min    ~900 words
[Section 1]     7 min    ~2,100 words
[Transition]    0.5 min
[Section 2]     7 min    ~2,100 words
[Mid-summary]   2 min    ~600 words      ← "So let's recap..."
[Section 3]     7 min    ~2,100 words
[Transition]    0.5 min
[Section 4]     7 min    ~2,100 words
[Transition]    0.5 min
[Section 5]     7 min    ~2,100 words
[Mid-summary]   2 min    ~600 words      ← "Before we move to the second half..."
[Section 6]     7 min    ~2,100 words
[Transition]    0.5 min
[Section 7]     5 min    ~1,500 words    ← Implications / outlook
[Wrap-up]       4 min    ~1,200 words
Total          60 min   ~17,500 words
```

## Context Window Management

60-minute scripts (~18,000 words) can lose quality if generated in one shot. Split into parts:

### Split Generation Strategy

1. **Generate outline first** — full structure with key points per section. Keep this in context for all parts.

2. **Generate by part:**
   - Part 1: Intro + Sections 1–3 + mid-summary (~20 min)
   - Part 2: Sections 4–5 + mid-summary (~20 min)
   - Part 3: Sections 6–7 + wrap-up (~20 min)

3. **Maintain continuity** — include the last 2–3 lines from the previous part as context, plus a brief summary of what was covered.

4. **Merge** — concatenate all parts into one .txt file. Check that transitions at part boundaries sound natural.

### Split Generation Prompt Template

```
Full outline:
{outline}

Previous part summary:
{previous_summary}

Last lines from previous part:
<Person1>{last_p1_line}</Person1>
<Person2>{last_p2_line}</Person2>

Sections to cover in this part:
{current_sections}

Continue from where the previous part left off. The dialogue should flow naturally
from the last lines above. Use <Person1>/<Person2> format.
```

## Conversation Pattern Variety

Long episodes become monotonous if they repeat the same pattern. Alternate between these:

### Pattern 1: Standard Q&A
```
<Person1>Question</Person1>
<Person2>Answer + explanation</Person2>
<Person1>Reaction + follow-up</Person1>
<Person2>Further detail</Person2>
```

### Pattern 2: Debate / Pushback
```
<Person1>States claim or common belief</Person1>
<Person2>Challenges or offers alternative view</Person2>
<Person1>Concedes partially, but counters</Person1>
<Person2>Finds middle ground or conclusion</Person2>
```

### Pattern 3: Storytelling
```
<Person1>Begins an anecdote or case study</Person1>
<Person1>Continues the story</Person1>
<Person2>Analyzes what the story means</Person2>
<Person1>Surprised reaction</Person1>
```

### Pattern 4: Rapid-fire
```
<Person1>Short question</Person1>
<Person2>Short answer</Person2>
<Person1>Another quick question</Person1>
<Person2>Short answer + expansion</Person2>
```

### Pattern 5: Recap / Transition
```
<Person2>Summarizes what's been covered</Person2>
<Person1>Agrees + pivots to next topic</Person1>
```

## Filler and Reaction Guide

Fillers make dialogue sound human. Use them naturally — roughly once every 10–15 lines.

### Korean
- Agreement: "맞아요", "그렇죠", "오~", "아~", "진짜요?"
- Surprise: "와", "대박", "흥미롭네요", "신기하다"
- Transition: "근데요", "그런데 말이죠", "아 그리고"
- Thinking: "음...", "글쎄요", "그건 좀..."
- Emphasis: "진짜", "솔직히", "사실은"

### English
- Agreement: "Right", "Exactly", "Oh interesting", "Hmm", "Yeah"
- Surprise: "Wow", "That's wild", "No way", "Fascinating"
- Transition: "But here's the thing", "Now", "Speaking of which"
- Thinking: "Well...", "I mean...", "You know..."
- Emphasis: "Actually", "Literally", "Honestly"

## Quality Checklist

After generating, verify:

- [ ] All lines wrapped in `<Person1>` or `<Person2>` tags
- [ ] No utterance exceeds 4 sentences (exception: storytelling pattern)
- [ ] Reset points every 5–7 minutes
- [ ] Conversation patterns vary across sections
- [ ] Fillers distributed naturally
- [ ] Intro clearly introduces the topic
- [ ] Wrap-up summarizes key points
- [ ] Total word count matches target duration
