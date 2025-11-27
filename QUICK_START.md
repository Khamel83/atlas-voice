# 🚀 Atlas Voice - Quick Start Guide

## **What This Does**

Turn any AI into your voice twin by analyzing your writing and generating a custom AI prompt that makes AI sound like you.

## **Complete Workflow (5 Minutes)**

### **Step 1: Process Your Data**
```bash
# Process your emails, documents, chats, etc.
python3 src/main.py nuclear-process /path/to/your/data
```

**What happens:**
- 🏢 **Room One**: Processes all your files (any format)
- 🔐 **Airlock**: Validates and secures the data
- 🚪 **Room Two**: Stores only linguistic patterns (no original content)

### **Step 2: Generate Your Voice Prompt**
```bash
# Create your voice profile from processed data
python3 src/main.py generate-voice-prompt
```

**What you get:**
- 📝 **Voice Prompt**: Custom AI instructions to sound like you
- 📊 **Profile Data**: Your linguistic patterns and style metrics
- 🔒 **Privacy**: Zero original content stored

### **Step 3: Use Your Voice**
```bash
# View your generated voice prompt
python3 src/main.py show-prompt profiles/your_voice_profile.txt

# Copy and paste this prompt into any AI (ChatGPT, Claude, etc.)
# The AI will now respond in YOUR voice!
```

---

## **🔧 Smart Commands**

### **For Natural Language Users:**
```bash
# Just talk naturally to the system
python3 src/main.py smart "analyze my emails and create my voice profile"

# Interactive mode
python3 src/main.py smart --interactive
```

### **Privacy Management:**
```bash
# Check privacy status
python3 src/main.py privacy-dashboard

# Manage data sources
python3 src/main.py data-sources

# Run security checks
python3 src/main.py privacy-check
```

### **Profile Management:**
```bash
# List all your voice profiles
python3 src/main.py voice-profiles

# Delete old profiles
python3 src/main.py delete-profile profile_name
```

---

## **📁 What Data Can You Use?**

**✅ Supported Formats:**
- Text files (.txt, .md)
- Emails (.eml)
- Spreadsheets (.csv)
- JSON data
- Chat logs
- Social media exports
- Any document with text

**📊 Example Sources:**
- Your email exports
- Chat conversations
- Social media posts
- Writing samples
- Work documents
- Personal journals

---

## **🔒 Privacy Guarantees**

### **Nuclear Safe Room Architecture:**
- **Room One**: Processes your data (temporary)
- **Airlock**: Validates and secures transfer
- **Room Two**: Stores ONLY linguistic patterns

### **What's NOT Stored:**
- ❌ Original content or messages
- ❌ Personal information or names
- ❌ File paths or locations
- ❌ Sensitive data or secrets

### **What IS Stored:**
- ✅ Function word frequencies (the, and, I, you, etc.)
- ✅ Sentence structure patterns
- ✅ Vocabulary complexity metrics
- ✅ Style markers (casual vs formal tendencies)

---

## **🎯 Example Use Cases**

### **Professional Communication:**
```bash
# Process your work emails and documents
python3 src/main.py nuclear-process ~/Documents/work_emails

# Generate professional voice profile
python3 src/main.py generate-voice-prompt

# Use the prompt to write work emails in your voice
```

### **Creative Writing:**
```bash
# Process your stories, blogs, creative writing
python3 src/main.py nuclear-process ~/writing/projects

# Generate creative voice profile
python3 src/main.py generate-voice-prompt

# Use AI to continue writing in your unique style
```

### **Social Media:**
```bash
# Process your social media posts and messages
python3 src/main.py nuclear-process ~/social_media_exports

# Generate conversational voice profile
python3 src/main.py generate-voice-prompt

# Create social media content that sounds like you
```

---

## **🚀 Advanced Features**

### **Privacy Controls:**
```bash
# Full privacy management dashboard
python3 -m privacy_controls

# Automatically clean up old data
python3 -m privacy_controls --cleanup
```

### **Data Source Management:**
```bash
# Manage all your data source references
python3 -m data_source_manager

# Check data integrity
python3 -m data_source_manager --verify
```

### **Intelligent Interface:**
```bash
# Natural language requests
python3 src/main.py smart "create my voice from my Google takeout"

# Interactive assistant
python3 src/main.py smart --interactive
```

---

## **📋 Requirements**

- **Python 3.8+**
- **OpenRouter API Key** (for intelligent format detection)
- **Your writing data** (emails, chats, documents, etc.)

### **Setup:**
```bash
# Install dependencies
pip install click openai sqlite3

# Set your API key
export OPENROUTER_API_KEY="your_key_here"

# Run the system
python3 src/main.py --help
```

---

## **🎉 You're Ready!**

**Start creating AI voices that sound like you:**

```bash
# 1. Process your data
python3 src/main.py nuclear-process /path/to/your/data

# 2. Generate your voice prompt
python3 src/main.py generate-voice-prompt

# 3. Use your voice with any AI!
python3 src/main.py show-prompt profiles/your_voice_profile.txt
```

**The future of AI communication is here - and it sounds like you!** 🎤✨

---

*For advanced usage and privacy controls, see the full documentation.*
