# ONE_SHOT: Atlas Voice - AI Voice Profile Generator

**Version**: 1.0
**Status**: Ready for autonomous build
**Philosophy**: Extract writing patterns, generate AI prompts, preserve privacy

---

# CORE QUESTIONS (ANSWERED)

## Q1. What Are You Building?

A tool that analyzes your writing (emails, documents, chat logs) and generates custom AI system prompts that make any AI (Claude, ChatGPT, etc.) sound exactly like you.

## Q2. What Problem Does This Solve?

People want AI assistants that match their communication style, but creating effective custom instructions requires expertise. Manual prompt writing is time-consuming and often misses subtle patterns. This automates it by analyzing thousands of writing samples to extract your authentic voice.

## Q3. Project Philosophy

- **Simplicity over features** - Core workflow: import → analyze → generate → export
- **Privacy-first** - Extract patterns, never store original content
- **CLI-first, web-optional** - Power users get CLI, everyone else gets web UI
- **Offline-capable** - Once patterns are extracted, works without network
- **Model-agnostic** - Generates prompts that work with any AI (Claude, GPT, Gemini, etc.)
- **Modular architecture** - Separate import, analysis, generation phases

## Q4. What Will It DO? (Features)

1. **Import writing samples** from multiple formats (email CSV, text files, JSON, Markdown)
2. **Extract linguistic patterns** (sentence structure, vocabulary, function words, style markers)
3. **Generate personalized AI system prompts** optimized for different contexts
4. **Support multiple voice profiles** (professional, casual, creative, technical)
5. **Export prompts** as text files ready to paste into any AI
6. **Privacy dashboard** showing exactly what patterns are stored (nothing else)
7. **Web UI** for non-technical users (upload → analyze → download prompt)

## Q5. What Will It NOT Do? (Non-Goals)

- **No real-time AI integration** - Just generates prompts, doesn't call APIs
- **No multi-user SaaS** - Single-user tool (CLI or local web server)
- **No model fine-tuning** - Prompt engineering only (works with any AI)
- **No content storage** - Original writing is never persisted
- **No cloud dependencies** - Works 100% locally
- **No authentication system** - Local-only app (add Tailscale if you want remote access)

## Q6. Project Type

**C. Web Application** (with full CLI interface as well)

- FastAPI backend (REST API + serves frontend)
- Simple HTML/JS frontend (no React/Vue bloat)
- CLI wraps the same backend logic
- Can run as web server OR pure CLI

## Q7. Data Shape (Example Objects)

```yaml
# Raw text sample (temporary during import)
text_sample:
  content: "I think we should focus on the core features first. Let's build something people actually want rather than over-engineering it. What do you think?"
  metadata:
    source: "email"
    date: "2024-01-15"
    type: "professional"

# Extracted pattern (what we actually store)
voice_pattern:
  id: "profile_20240115_123456"
  stats:
    total_words: 8621385
    total_sentences: 495537
    avg_sentence_length: 17.4
    vocab_richness: 0.071
    avg_word_length: 3.8
  function_words:
    - word: "i"
      frequency: 4.5
    - word: "to"
      frequency: 3.5
    - word: "the"
      frequency: 3.0
  style_markers:
    casual: ["actually", "basically", "like", "you know", "i mean", "sort of"]
    formal: ["however", "therefore", "consequently"]
    personal: ["i think", "i feel", "in my opinion"]
  sentence_starters:
    - "I think"
    - "Let's"
    - "What"
  created_at: "2024-01-15T12:34:56Z"

# Generated prompt
voice_prompt:
  profile_id: "profile_20240115_123456"
  name: "Omar - Professional"
  context: "professional emails and technical writing"
  prompt_text: |
    You are communicating in Omar's voice. Key characteristics:

    SENTENCE STRUCTURE:
    - Average 17 words per sentence with natural flow
    - Often starts with "I think" or "Let's"
    ...
  created_at: "2024-01-15T12:45:00Z"
```

## Q8. Data Scale

**B. Medium** (1K–100K items, 1–10 GB)

- Typical use case: 10K-50K emails/messages
- Pattern database: < 100 MB
- Import files: 1-5 GB (temporary, deleted after analysis)

## Q9. Storage Choice

**D. Mix** (files for import, SQLite for patterns)

- **Import files** → Temporary directory (deleted after pattern extraction)
- **Extracted patterns** → SQLite database
- **Generated prompts** → SQLite + exported text files
- **Config** → YAML file

File format for imports:
- CSV (email exports)
- JSON (chat logs)
- TXT (documents)
- Markdown (notes)

## Q10. Dependencies

```
# Core
click          # CLI interface
fastapi        # Web API
uvicorn        # ASGI server
sqlite3        # Built-in, no install needed
pyyaml         # Config files

# Analysis
pandas         # Data processing for large imports
numpy          # Statistical calculations

# Testing
pytest         # Test framework
pytest-cov     # Coverage reporting

# Optional (web UI)
jinja2         # Template rendering (included with FastAPI)
```

## Q11. User Interface Shape

### CLI Commands

```bash
# Import data
atlas-voice import /path/to/emails.csv --type email
atlas-voice import /path/to/documents --type text

# Analyze patterns
atlas-voice analyze --profile professional

# View patterns
atlas-voice show-patterns

# Generate prompts
atlas-voice generate --profile professional --output prompt.txt
atlas-voice generate --profile casual --output casual_prompt.txt

# Privacy
atlas-voice privacy-check
atlas-voice clear-imports  # Delete temp files

# Web UI
atlas-voice serve --port 8000
```

### Web Routes

```
GET  /                  - Landing page with upload form
POST /api/import        - Upload files for analysis
GET  /api/analyze       - Trigger pattern extraction
GET  /api/patterns      - View extracted patterns
POST /api/generate      - Generate prompt with options
GET  /api/export/:id    - Download prompt as .txt
GET  /api/privacy       - Privacy dashboard

GET  /health            - Health check
```

## Q12. "Done" and v1 Scope

### Q12a. What Does "Done" Look Like?

**Success Criteria:**
- ✅ Can import 10K+ emails without crashing
- ✅ Extracts accurate linguistic patterns (validated against test data)
- ✅ Generates prompts that make AI sound noticeably more like the user
- ✅ Zero original content stored (patterns only)
- ✅ Works via CLI and web UI
- ✅ Can export prompts as text files
- ✅ Clear documentation for usage

### Q12b. What Is "Good Enough v1"?

**Minimum viable features:**
- Import text/CSV files via CLI
- Extract basic patterns:
  - Sentence length distribution
  - Function word frequencies
  - Common phrases/patterns
  - Casual vs formal markers
- Generate single voice prompt (professional context)
- Export as .txt file
- Privacy guarantee: no content storage
- Basic web UI (upload → download prompt)

**Deferred to v2:**
- Multiple voice profiles per user
- Advanced pattern analysis (topic clustering, sentiment)
- Comparison tools (before/after AI outputs)
- Integration with email providers
- Scheduled re-analysis

## Q13. Naming

- **Project name**: atlas-voice
- **GitHub repo**: atlas-voice
- **Python module**: atlas_voice
- **CLI command**: atlas-voice

---

# ADVANCED OPTIONS

## Q16. Directory Structure

**C. Domain-driven** (`src/models/`, `src/services/`, `src/api/`)

```
atlas-voice/
├── atlas_voice/
│   ├── __init__.py
│   ├── models/          # Data models (Pattern, VoicePrompt)
│   ├── services/        # Business logic (import, analyze, generate)
│   ├── api/             # FastAPI routes
│   ├── cli/             # Click commands
│   └── storage/         # SQLite database layer
├── tests/
├── web/                 # Static HTML/CSS/JS
├── data/                # SQLite DB lives here
├── .env.example
├── pyproject.toml
└── README.md
```

## Q17. Testing Strategy

**B. Thorough** (~80% coverage target)

- Unit tests for all services
- Integration tests for import → analyze → generate pipeline
- CLI command tests
- API endpoint tests
- Privacy compliance tests (verify no content storage)

## Q18. Deployment Preference

**B + C. Tailscale HTTPS + systemd** (optional, works local-only by default)

**Default runtime**: Local development (works offline)

**Optional deployment**:
- **Homelab**: systemd service + Tailscale for remote access
- **OCI Free Tier**: If you want it always-on
- **Access**: `https://atlas-voice.your-tailnet.ts.net`

## Q19. Secrets & Env

**None required for v1** (no AI API calls, just generates prompts)

Optional for deployment:
```bash
# .env (optional)
DATABASE_PATH=./data/atlas_voice.db
TEMP_IMPORT_DIR=./data/imports
LOG_LEVEL=INFO
```

---

# WEB DESIGN

## Q20. Aesthetic

**A. Modern & Minimal**

- Clean interface inspired by Linear, Stripe
- Focus on content and clarity
- Generous whitespace
- Clear typography hierarchy

## Q21. Color Scheme

**D. ONE_SHOT decides**

Suggestion:
- Primary: Deep blue (#1e40af)
- Accent: Emerald (#10b981)
- Background: Off-white (#fafafa)
- Text: Charcoal (#1f2937)
- Emphasis on readability and professionalism

## Q22. Animation Level

**A. Minimal**

- Smooth transitions (200ms)
- Hover states
- Upload progress indicator
- No gratuitous animations

---

# AI FEATURES

## Q23. AI in the Tool

**No AI in the tool itself.**

Atlas Voice is a **prompt generator**, not an AI assistant.

**What it does**: Analyzes your writing → Generates custom system prompts

**What YOU do**: Copy prompt → Paste into Claude/ChatGPT/etc.

**Why**:
- Keeps it simple
- No API costs
- Works with any AI model
- User controls which AI they use

---

# ENVIRONMENT

## Q24. Validation

```bash
# Required
python3 --version  # >= 3.10
git --version

# Optional (for deployment)
systemctl --version
tailscale version
```

---

# PRD SUMMARY

## Overview

Atlas Voice analyzes your writing to extract linguistic patterns and generates personalized AI system prompts. Privacy-first architecture ensures no content storage.

## Core Value

**Problem**: Creating effective custom AI instructions is hard.
**Solution**: Automated pattern extraction from real writing samples.
**Benefit**: AI that sounds like you in 3 steps (import → analyze → export).

## Architecture

- **Backend**: Python + FastAPI + SQLite
- **Frontend**: Simple HTML/JS (no framework bloat)
- **CLI**: Click-based commands
- **Storage**: SQLite for patterns, temp files for imports
- **Deployment**: Local-first, optional systemd + Tailscale

## Success Metrics

1. Can process 10K+ writing samples without errors
2. Generated prompts measurably improve AI voice matching
3. Zero content leakage (privacy compliance)
4. Usable by both technical (CLI) and non-technical (web) users

---

# EXECUTION APPROVED

**Status**: Ready for autonomous build

**Build order**:
1. Project skeleton + dependencies
2. Database schema + models
3. Import service (CSV, text files)
4. Analysis service (pattern extraction)
5. Generation service (prompt creation)
6. CLI interface
7. Web API + frontend
8. Tests
9. Documentation

**Timeline**: Build complete implementation autonomously.

---

**Version**: 1.0
**Created**: 2024-11-26
**Ready for execution**: YES
