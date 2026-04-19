# 🎤 Atlas Voice

**Generate AI system prompts from your writing patterns**

Turn any AI (Claude, ChatGPT, Gemini) into your voice twin using privacy-first prompt engineering.

[![Privacy First](https://img.shields.io/badge/Privacy-First-green)](#privacy)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-purple)](#license)

---

## 🎯 What It Does

Atlas Voice analyzes your writing and generates custom AI prompts that make any AI sound exactly like you.

**3-Step Process:**
1. **Import** your emails, documents, or text files
2. **Analyze** your linguistic patterns (sentence structure, vocabulary, style)
3. **Generate** a custom system prompt for Claude, ChatGPT, or any AI

**Privacy Guarantee:** Your original content is NEVER stored. Only linguistic patterns are extracted.

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Khamel83/atlas-voice.git
cd atlas-voice

# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### 3-Step Usage

```bash
# 1. Import your writing
atlas-voice import /path/to/your/emails.csv --type email --name "My Professional Voice"

# 2. Pattern analysis happens automatically during import

# 3. Generate your prompt
atlas-voice generate <pattern-id> --context professional --output my_voice_prompt.txt
```

### Or Use the Web Interface

```bash
atlas-voice serve

# Open http://localhost:8000 in your browser
# Upload files → Generate prompt → Copy to clipboard
```

---

## 📊 Supported Data Sources

- **Email CSV** (Gmail export, Outlook, etc.)
- **Text files** (.txt, .md)
- **JSON** (chat logs, message exports)
- **Directories** (batch import)

---

## 🎛️ CLI Commands

### Import & Analyze

```bash
# Import a single file
atlas-voice import emails.csv --type email

# Import a directory
atlas-voice import /path/to/documents --type text

# Custom naming
atlas-voice import data.csv --name "Work Voice" --description "Professional emails 2020-2024"
```

### View Patterns

```bash
# List all voice patterns
atlas-voice list-patterns

# Show detailed pattern information
atlas-voice show-pattern <pattern-id>
```

### Generate Prompts

```bash
# Generate with context
atlas-voice generate <pattern-id> --context professional
atlas-voice generate <pattern-id> --context casual
atlas-voice generate <pattern-id> --context creative
atlas-voice generate <pattern-id> --context technical

# Save to file
atlas-voice generate <pattern-id> --output my_prompt.txt
```

### Manage Prompts

```bash
# List generated prompts
atlas-voice list-prompts

# Export a prompt
atlas-voice export-prompt <prompt-id> --output prompt.txt
```

### Privacy

```bash
# View privacy report
atlas-voice privacy-check

# Clear temporary import files
atlas-voice clear-imports
```

### Web Interface

```bash
# Start web server
atlas-voice serve

# Custom host/port
atlas-voice serve --host 0.0.0.0 --port 3000
```

---

## 🔒 Privacy Features

### What We Store

- Word frequencies (e.g., "the" appears 3.2%)
- Sentence length averages
- Common phrases and patterns
- Style markers (casual/formal indicators)

### What We DON'T Store

- ❌ Original text content
- ❌ Personal information
- ❌ Email addresses
- ❌ Actual messages or documents

### How It Works

1. **Import:** Temporarily load your data
2. **Analyze:** Extract linguistic patterns only
3. **Store:** Save patterns to local SQLite database
4. **Delete:** Remove original content immediately

**Result:** Privacy-preserving voice analysis. No original content ever persisted.

Run `atlas-voice privacy-check` to see exactly what's stored.

---

## 📖 How It Works

### Voice Pattern Analysis

Atlas Voice extracts:

1. **Statistical Patterns**
   - Average sentence length
   - Vocabulary richness
   - Word length distribution

2. **Function Words**
   - High-frequency words like "I", "you", "the", "to"
   - Your personal usage patterns

3. **Style Markers**
   - Casual phrases ("actually", "basically", "you know")
   - Formal phrases ("however", "therefore", "consequently")
   - Personal markers ("I think", "in my opinion")
   - Technical terms (if applicable)

4. **Sentence Starters**
   - How you typically begin sentences
   - Common opening patterns

### Prompt Generation

The generator creates a structured system prompt with:

- **Writing Style**: Tone, sentence length, vocabulary
- **Language Patterns**: Characteristic words and phrases
- **Communication Approach**: Personal, direct, collaborative styles
- **Context Guidance**: Tailored for professional, casual, creative, or technical use
- **Quality Checklist**: Verification points for AI consistency

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=atlas_voice --cov-report=html

# Run specific test
pytest tests/test_analyzer.py
```

### Real Data Scale Testing

The project includes a critical test that validates voice analysis at different time scales:

```bash
# Test with real email data (if available)
pytest tests/test_real_data_scale.py -v
```

This test compares voice patterns extracted from:
- 1 week of writing
- 1 month of writing
- 1 year of writing
- 5 years of writing
- 20 years of writing (all data)

**Key Question:** Does 20 years of data produce significantly better results than 1 month?

Results show whether you need extensive data or if smaller samples are sufficient.

---

## 🏗️ Project Structure

```
atlas-voice/
├── atlas_voice/
│   ├── models/          # Data models (VoicePattern, VoicePrompt)
│   ├── services/        # Business logic (import, analyze, generate)
│   ├── api/             # FastAPI web application
│   ├── cli/             # Click CLI commands
│   └── storage/         # SQLite database layer
├── tests/               # Test suite
├── web/                 # HTML/CSS/JS frontend
├── data/                # Local data (gitignored)
│   ├── atlas_voice.db   # SQLite database
│   └── imports/         # Temporary import directory
├── pyproject.toml       # Project configuration
└── README.md            # This file
```

---

## 🌐 Web API

If you want to integrate Atlas Voice into your own application:

### Endpoints

```
GET  /health                    - Health check
GET  /                          - Web interface

POST /api/import                - Upload and analyze file
GET  /api/patterns              - List all patterns
GET  /api/patterns/{id}         - Get pattern details
POST /api/generate              - Generate prompt from pattern
GET  /api/prompts               - List all prompts
GET  /api/prompts/{id}          - Get prompt details
GET  /api/prompts/{id}/download - Download prompt as .txt
GET  /api/privacy               - Privacy information
DELETE /api/patterns/{id}       - Delete pattern
```

### Example API Usage

```python
import requests

# Import file
with open('emails.csv', 'rb') as f:
    response = requests.post('http://localhost:8000/api/import',
        files={'file': f},
        data={'name': 'My Voice', 'file_type': 'email'}
    )
pattern_id = response.json()['pattern_id']

# Generate prompt
response = requests.post('http://localhost:8000/api/generate',
    data={'pattern_id': pattern_id, 'context': 'professional'}
)
prompt = response.json()['prompt_text']

# Use with Claude/ChatGPT
print(prompt)
```

---

## 🎨 Example Output

Here's what a generated prompt looks like:

```
You are writing in a specific person's voice. Follow these patterns closely:

## WRITING STYLE
- Tone: balanced between formal and casual
- Average sentence length: 17.4 words
- Vocabulary: Clear and concise

## SENTENCE STRUCTURE
- Average 17.4 words per sentence
- Common sentence starters: i think, let's, what, we should, the

## LANGUAGE PATTERNS
- Frequently uses: i, to, the, and, you, we, this
- Personal phrases: i think, i would say, in my opinion
- Casual expressions: actually, basically, you know, i mean

## COMMUNICATION APPROACH
- Uses first person ('I think', 'I would') to express opinions clearly
- Directly engages the reader with 'you'
- Uses 'we' for collaborative thinking
- Asks questions to drive thinking forward

## QUALITY CHECKLIST
Before responding, verify:
- ✓ Sentences average ~17 words with natural flow
- ✓ Uses characteristic function words naturally
- ✓ Maintains balanced between formal and casual tone
- ✓ Sounds like something this person would actually say

_Based on analysis of 8,621,385 words from 18,147 professional emails_
```

---

## 🔧 Configuration

Create a `.env` file (optional):

```bash
# Database path (default: data/atlas_voice.db)
DATABASE_PATH=data/atlas_voice.db

# Temporary import directory (default: data/imports)
TEMP_IMPORT_DIR=data/imports

# Log level (default: INFO)
LOG_LEVEL=INFO

# Web server settings
WEB_HOST=127.0.0.1
WEB_PORT=8000
```

---

## 🚀 Deployment

### Local (Default)

```bash
atlas-voice serve
# Access at http://localhost:8000
```

### Homelab / VM

```bash
# Install as systemd service
sudo cp scripts/atlas-voice.service /etc/systemd/system/
sudo systemctl enable atlas-voice
sudo systemctl start atlas-voice

# Expose via Tailscale
tailscale serve https / http://localhost:8000
# Access at https://hostname.your-tailnet.ts.net
```

### Production Considerations

- Use environment variables for configuration
- Set up proper logging
- Configure CORS if needed
- Use reverse proxy (Caddy/Nginx) for SSL
- Back up the SQLite database regularly

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure tests pass (`pytest`)
5. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Built with FastAPI, Click, and modern Python
- Privacy-first architecture inspired by security best practices
- Linguistic analysis based on NLP fundamentals

---

## 📬 Support

- **Issues**: [GitHub Issues](https://github.com/Khamel83/atlas-voice/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Khamel83/atlas-voice/discussions)

---

**🎤 Make AI sound like you. Privately.** ✨

Made with ❤️ for privacy and authenticity.
