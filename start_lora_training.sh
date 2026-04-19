#!/bin/bash
# Quick start script for LoRA training

set -e

echo "🎯 Atlas Voice - LoRA Training Setup"
echo "===================================="
echo ""

# Check Python
echo "✓ Checking Python..."
python3 --version || { echo "❌ Python 3 not found"; exit 1; }

# Check email data
EMAIL_PATH="/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv"
if [ -f "$EMAIL_PATH" ]; then
    echo "✓ Email data found ($(du -h "$EMAIL_PATH" | cut -f1))"
else
    echo "❌ Email data not found at: $EMAIL_PATH"
    exit 1
fi

# Check API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ OPENROUTER_API_KEY not set"
    echo ""
    echo "Get your API key from: https://openrouter.ai/keys"
    echo "Then run: export OPENROUTER_API_KEY='sk-or-v1-YOUR-KEY-HERE'"
    echo "Or add to .env file"
    exit 1
else
    echo "✓ OpenRouter API key found"
fi

# Check dependencies
echo ""
echo "📦 Checking dependencies..."

if python3 -c "import unsloth" 2>/dev/null; then
    echo "✓ Unsloth installed"
else
    echo "⚠️  Unsloth not installed"
    echo ""
    echo "Install with:"
    echo "  pip install unsloth"
    echo ""
    echo "Or:"
    echo "  pip install 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'"
    echo ""
    read -p "Install now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip install unsloth
    else
        exit 1
    fi
fi

# Check Ollama models
echo ""
echo "🤖 Available Ollama models:"
ollama list | grep "llama3.1:8b" || echo "  (llama3.1:8b not found - will download from Hugging Face)"

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Generate training data (~15 mins, costs ~$0.15):"
echo "   python3 prep_training_data.py \\"
echo "     --emails \"$EMAIL_PATH\" \\"
echo "     --output training_data.jsonl \\"
echo "     --num-samples 500"
echo ""
echo "2. Train the model (~2-3 hours, free):"
echo "   python3 train_lora_local.py \\"
echo "     --data training_data.jsonl \\"
echo "     --output omar-voice-lora"
echo ""
echo "3. Test it:"
echo "   python3 test_omar_model.py --model omar-voice-lora"
echo ""
echo "See LORA_TRAINING_GUIDE.md for full details."
