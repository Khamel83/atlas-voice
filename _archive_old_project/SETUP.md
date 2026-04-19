# 🛠️ Installation & Setup

## **Quick Install**

### **1. Clone the Repository**
```bash
git clone https://github.com/Khamel83/atlas-voice
cd atlas-voice
```

### **2. Install Dependencies**
```bash
pip install click openai sqlite3 pathlib
```

### **3. Set Up API Key**
```bash
# For macOS/Linux
export OPENROUTER_API_KEY="your_openrouter_api_key_here"

# For Windows (Command Prompt)
set OPENROUTER_API_KEY=your_openrouter_api_key_here

# For Windows (PowerShell)
$env:OPENROUTER_API_KEY="your_openrouter_api_key_here"
```

### **4. Test Installation**
```bash
python3 src/main.py --help
```

## **API Key Setup**

### **Get OpenRouter API Key:**
1. Go to [OpenRouter.ai](https://openrouter.ai)
2. Create an account
3. Generate an API key
4. Add funds to your account (free tier available)

### **Environment Setup:**

**macOS/Linux (add to ~/.bashrc or ~/.zshrc):**
```bash
export OPENROUTER_API_KEY="sk-or-..."
```

**Windows (add to System Environment Variables):**
```
OPENROUTER_API_KEY=sk-or-...
```

**Or create a .env file:**
```bash
echo "OPENROUTER_API_KEY=sk-or-..." > .env
```

## **System Requirements**

### **Minimum:**
- Python 3.8+
- 100MB disk space
- Internet connection (for LLM format detection)

### **Recommended:**
- Python 3.9+
- 1GB+ disk space (for data processing)
- 4GB+ RAM (for large datasets)

## **Directory Structure**

```
atlas-voice/
├── src/                    # Source code
│   ├── main.py            # Main CLI interface
│   ├── nuclear_safe_room.py # Privacy architecture
│   ├── voice_prompt_generator.py # Voice prompt creation
│   ├── intelligent_interface.py # Natural language processing
│   └── ...               # Other modules
├── data/                  # Data directory
│   ├── room_two_database/ # Clean pattern database
│   └── ...               # Your data files
├── profiles/              # Generated voice profiles
├── prompts/               # Generated voice prompts
├── QUICK_START.md         # Get started in 5 minutes
├── NUCLEAR_SAFE_ROOM_DOCS.md # Privacy architecture
└── SETUP.md              # This file
```

## **First Run**

### **1. Privacy Check**
```bash
python3 src/main.py privacy-check
```

### **2. Prepare Your Data**
Put your writing samples in a directory:
```bash
# Example structure
mkdir my_data
cp ~/emails/*.eml my_data/
cp ~/documents/*.txt my_data/
cp ~/chat_logs/*.json my_data/
```

### **3. Process Data**
```bash
python3 src/main.py nuclear-process ./my_data
```

### **4. Generate Voice Prompt**
```bash
python3 src/main.py generate-voice-prompt
```

### **5. View Results**
```bash
python3 src/main.py voice-profiles
python3 src/main.py show-prompt profiles/your_profile.txt
```

## **Troubleshooting**

### **Common Issues:**

**❌ "Module not found" errors:**
```bash
# Install missing dependencies
pip install click openai
```

**❌ "OPENROUTER_API_KEY not found":**
```bash
# Set your API key
export OPENROUTER_API_KEY="your_key_here"
```

**❌ "No data found" errors:**
```bash
# Check your data path exists
ls /path/to/your/data

# Use absolute paths
python3 src/main.py nuclear-process /full/path/to/data
```

**❌ Permission errors:**
```bash
# Check file permissions
ls -la /path/to/your/data

# Make files readable
chmod 644 /path/to/your/data/*
```

### **Getting Help:**

**Command help:**
```bash
python3 src/main.py --help
python3 src/main.py [command] --help
```

**Smart interface (natural language):**
```bash
python3 src/main.py smart "help me get started"
python3 src/main.py smart --interactive
```

**Privacy dashboard:**
```bash
python3 src/main.py privacy-dashboard
```

## **Advanced Setup**

### **Docker Setup:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install click openai sqlite3

ENV OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

CMD ["python3", "src/main.py", "--help"]
```

### **Web Deployment (Vercel/Netlify):**
The system is web-deployment ready:
- No persistent source data
- Clean database architecture
- Privacy controls built-in
- API key management through environment variables

### **Large Data Processing:**
For datasets larger than 1GB:
```bash
# Process in chunks
python3 src/main.py nuclear-process ./large_data --batch-size 1000

# Enable cleanup after processing
python3 src/main.py nuclear-process ./large_data --cleanup-after

# Monitor memory usage
python3 src/main.py privacy-dashboard
```

## **Security Best Practices**

### **API Key Security:**
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly
- Monitor usage on OpenRouter dashboard

### **Data Privacy:**
- The system never stores original content
- Only linguistic patterns are retained
- All processing is local
- Complete deletion capabilities

### **File Permissions:**
```bash
# Set proper permissions
chmod 700 data/
chmod 600 profiles/*
chmod 600 prompts/*
```

## **Updating the System**

### **Update Dependencies:**
```bash
pip install --upgrade click openai sqlite3
```

### **Update Code:**
```bash
git pull origin main
```

### **Clean Install:**
```bash
# Remove old data
rm -rf data/room_two_database/
rm -rf profiles/
rm -rf prompts/

# Reinitialize
python3 src/main.py privacy-check
```

---

## **🎉 Ready to Go!**

Once you're set up, head to **QUICK_START.md** to create your first AI voice profile in minutes!

**Need help?** Use the smart interface:
```bash
python3 src/main.py smart "help me understand how to use this"
```
