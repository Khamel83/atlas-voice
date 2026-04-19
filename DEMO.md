# Atlas Voice - Quick Demo

This demo shows how to use Atlas Voice with sample data.

## 1. Create Sample Data

First, let's create a sample text file with some writing:

```bash
cat > sample_writing.txt << 'EOF'
I think we should focus on building something people actually want. Let's start with the core features and iterate from there. What do you think about this approach?

Actually, I'm not sure that's the right direction. We might want to consider the user experience first. How does this align with our goals?

The implementation looks good. However, we need to think about edge cases. I would suggest adding some validation here.

We should prioritize performance in this section. It's critical that we optimize the database queries. Can we profile this to identify bottlenecks?

Let's schedule a meeting to discuss this further. I think we're on the right track, but we need to align on the details.

EOF
```

## 2. Import and Analyze

```bash
atlas-voice import sample_writing.txt --type text --name "Demo Profile"
```

Output:
```
Importing data from: sample_writing.txt
✓ Imported 5 text samples
✓ Total words: 135

Analyzing patterns...
✓ Voice pattern saved: pattern_20241126_123456

Profile: Demo Profile
  Words analyzed: 135
  Sentences: 17
  Avg sentence length: 7.9 words
  Vocabulary richness: 0.578

Next: Run 'atlas-voice generate pattern_20241126_123456' to create a prompt
```

## 3. List Patterns

```bash
atlas-voice list-patterns
```

Output:
```
Found 1 voice pattern(s):

ID: pattern_20241126_123456
  Name: Demo Profile
  Words: 135
  Source: Imported from sample_writing.txt
  Created: 2024-11-26 12:34
```

## 4. View Pattern Details

```bash
atlas-voice show-pattern pattern_20241126_123456
```

Output:
```
Demo Profile
======================================================================

ID: pattern_20241126_123456
Source: Imported from sample_writing.txt
Created: 2024-11-26 12:34

## Statistics
  Total words: 135
  Total sentences: 17
  Avg sentence length: 7.9 words
  Vocabulary richness: 0.578
  Avg word length: 4.2 characters

## Top Function Words
  we: 8.89%
  to: 7.41%
  i: 7.41%
  the: 5.93%
  this: 4.44%

## Style Markers
  Casual: actually, i think
  Personal: i think, i would
  Technical: implementation, optimize, database, queries, performance

## Common Sentence Starters
  i think, we should, the implementation, let's, actually
```

## 5. Generate Prompt

```bash
atlas-voice generate pattern_20241126_123456 --context professional
```

Output: (A complete AI system prompt that captures your voice)

## 6. Export for Use

```bash
atlas-voice generate pattern_20241126_123456 --context professional --output my_voice.txt

# Now use my_voice.txt with Claude, ChatGPT, etc.
cat my_voice.txt
```

## 7. Privacy Check

```bash
atlas-voice privacy-check
```

Output:
```
======================================================================
PRIVACY REPORT
======================================================================

✓ Privacy Guarantee:
  - NO original text content is stored
  - ONLY linguistic patterns are saved (statistics, frequencies)
  - All data stays local on your machine
  - No external API calls (unless you use the prompts with AI)

✓ Current Storage:
  - Voice patterns: 1
  - Words analyzed: 135
  - Original content stored: ZERO
  - Database size: 8.2 KB

✓ What We Store:
  - Word frequencies (e.g., 'the' appears 3.2% of the time)
  - Sentence length averages
  - Common phrases and patterns
  - Style markers (casual/formal indicators)

✓ Data Location:
  - Database: /path/to/atlas-voice/data/atlas_voice.db
  - Import temp dir: data/imports/
```

## 8. Web Interface

```bash
atlas-voice serve
```

Open http://localhost:8000 and:
1. Upload `sample_writing.txt`
2. Click "Generate Prompt"
3. Copy to clipboard
4. Paste into Claude/ChatGPT

## Next Steps

Try with your real data:

```bash
# Email export
atlas-voice import emails.csv --type email --name "Professional Voice"

# Collection of documents
atlas-voice import ~/Documents/writing --type text --name "Writing Voice"

# Chat history
atlas-voice import chat_export.json --type json --name "Casual Voice"
```

## Testing Different Contexts

Generate prompts for different use cases:

```bash
# For professional communication
atlas-voice generate <pattern-id> --context professional --output professional.txt

# For casual conversation
atlas-voice generate <pattern-id> --context casual --output casual.txt

# For creative writing
atlas-voice generate <pattern-id> --context creative --output creative.txt

# For technical documentation
atlas-voice generate <pattern-id> --context technical --output technical.txt
```

Then test each prompt with your AI of choice and see which works best!
