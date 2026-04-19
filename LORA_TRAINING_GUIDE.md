# LoRA Fine-Tuning Guide - Train Omar's Voice Model

**Goal:** Fine-tune Llama 3.1 8B on your email writing style using LoRA
**Cost:** ~$0.15 for data prep + $0 for training (runs locally)
**Time:** 30 min prep + 2-3 hours training

---

## Step 1: Get OpenRouter API Key (5 minutes)

1. Go to: https://openrouter.ai/keys
2. Sign up (free)
3. Create a new API key
4. Add $5 credit (you'll use ~$0.15)

5. Add to `.env` file:
   ```bash
   echo 'OPENROUTER_API_KEY=sk-or-v1-YOUR-KEY-HERE' >> .env
   ```

---

## Step 2: Install Dependencies (10 minutes)

```bash
# Install Unsloth (optimized LoRA training)
pip install unsloth

# If that fails, use:
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Install other deps
pip install transformers trl datasets accelerate peft bitsandbytes
```

**Note for M1/M2 Macs:**
- Unsloth works on Apple Silicon
- Training will use CPU/GPU unified memory
- Expect 2-3 hours for training

---

## Step 3: Prepare Training Data (15 minutes)

**Generate 500 training examples from your emails:**

```bash
python3 prep_training_data.py \
  --emails "/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv" \
  --output training_data.jsonl \
  --num-samples 500
```

**What happens:**
- Loads your 91,457 emails
- Randomly samples emails
- Uses Gemini 2.5 Flash Lite to generate instruction-output pairs
- Saves to `training_data.jsonl`

**Cost:** ~$0.15 (500 examples × 2000 tokens × $0.30/1M tokens)

**Output format:**
```jsonl
{"instruction": "Write a professional email about database optimization", "output": "Hey team,\n\nI think we should..."}
{"instruction": "Respond to a question about microservices", "output": "The real question is..."}
...
```

---

## Step 4: Train LoRA Model (2-3 hours)

**Fine-tune Llama 3.1 8B on your writing style:**

```bash
python3 train_lora_local.py \
  --data training_data.jsonl \
  --output omar-voice-lora \
  --epochs 3 \
  --batch-size 2
```

**What happens:**
- Loads Llama 3.1 8B in 4-bit (uses ~6GB RAM)
- Trains LoRA adapters on your examples
- Saves adapter to `omar-voice-lora/`

**Expected output:**
```
🚀 Starting LoRA fine-tuning...
📚 Loading training data...
✓ Loaded 500 examples
🤖 Loading Llama 3.1 8B in 4-bit mode...
✓ Model loaded
⚙️  Configuring LoRA...
✓ LoRA configured
🏋️  Training configuration:
   Epochs: 3
   Batch size: 2
   Learning rate: 2e-4
🔥 Starting training (this will take 1-3 hours)...

[Training progress bars...]

✅ Training complete!
💾 Saving LoRA adapter to: omar-voice-lora
✓ Saved!
```

**Cost:** $0 (runs locally on your Mac)
**Time:** 2-3 hours

---

## Step 5: Test Your Model (5 minutes)

**Generate text in your voice:**

```bash
python3 test_omar_model.py --model omar-voice-lora
```

**Or with a custom prompt:**

```bash
python3 test_omar_model.py \
  --model omar-voice-lora \
  --prompt "Write an email about the database migration project being delayed"
```

**Expected output:**
```
======================================================================
PROMPT: Write an email about the database migration project being delayed
======================================================================

RESPONSE:
Hey team,

I think we need to talk about the migration timeline. The database work is taking longer than expected, and I'm not convinced we should rush it.

Here's what I'm seeing:
1. The data validation scripts are still failing on edge cases
2. We haven't fully tested the rollback procedure
3. The monitoring setup isn't complete

Actually, I'd rather delay by 2 weeks and do this right than ship something half-baked and have to scramble when things break in production.

What do you think? Can we push the go-live date to the 15th?

Omar
======================================================================

🎯 Does this sound like you?
```

---

## Troubleshooting

### Issue: Out of Memory (OOM)

**Solution:** Reduce batch size
```bash
python3 train_lora_local.py --data training_data.jsonl --batch-size 1
```

### Issue: Unsloth installation fails

**Alternative method:**
```bash
# Use Google Colab (free)
# Upload training_data.jsonl
# Run training in Colab notebook
# Download omar-voice-lora.zip
```

### Issue: Training is too slow

**Speed it up:**
- Reduce `--epochs` to 2
- Reduce `--num-samples` to 300
- Use `--batch-size 1` (paradoxically faster with small RAM)

### Issue: Model doesn't sound like you

**Improvements:**
1. **More data:** Increase `--num-samples` to 1000
2. **Better data:** Manually curate 100-200 high-quality examples
3. **More training:** Increase `--epochs` to 5
4. **Better prompts:** Improve instruction quality in training data

---

## Cost Breakdown

| Step | Service | Cost |
|------|---------|------|
| Data prep | Gemini 2.5 Flash Lite (OpenRouter) | ~$0.15 |
| Training | Local (Llama 3.1 8B) | $0.00 |
| Testing | Local | $0.00 |
| **TOTAL** | | **~$0.15** |

**Compare to:**
- OpenAI fine-tuning: ~$360
- Claude fine-tuning: Not available
- Anthropic Claude: $3/M tokens (ongoing cost)

---

## Next Steps After Training

### Option 1: Use Locally

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="omar-voice-lora",
    max_seq_length=2048,
    load_in_4bit=True,
)

# Generate text
response = model.generate(...)
```

### Option 2: Export to Ollama

```bash
# Convert LoRA to full model
python3 export_to_ollama.py --model omar-voice-lora

# Use with Ollama
ollama run omar-voice "Write an email about..."
```

### Option 3: Deploy as API

```bash
# Run as FastAPI server
python3 serve_model.py --model omar-voice-lora --port 8000

# Query via API
curl http://localhost:8000/generate -d '{"prompt": "Write..."}'
```

---

## FAQ

**Q: Will this actually sound like me?**
A: Much better than statistical prompts. Expect 70-80% accuracy. Try it and see!

**Q: Can I train on more data?**
A: Yes! Increase `--num-samples` to 1000 or 2000. Will cost more (~$0.30-0.60) but may improve quality.

**Q: How long does training take?**
A: On M1 Mac with 16GB: 2-3 hours for 500 examples, 3 epochs.

**Q: Can I use this commercially?**
A: Llama 3.1 is commercially licensed. Yes, you can.

**Q: Will this work offline?**
A: After training, yes! Model runs 100% locally.

**Q: Can I fine-tune other models?**
A: Yes! Try: Qwen2.5-Coder, Mistral, Phi-3. Same process.

---

## Files Created

After running all steps:

```
atlas-voice/
├── prep_training_data.py      # Data preparation script
├── train_lora_local.py         # Training script
├── test_omar_model.py          # Testing script
├── training_data.jsonl         # Generated training data (500 examples)
└── omar-voice-lora/            # Your fine-tuned model
    ├── adapter_config.json
    ├── adapter_model.safetensors
    └── tokenizer files...
```

---

## Ready to Start?

1. **Get API key:** https://openrouter.ai/keys
2. **Add to .env:** `OPENROUTER_API_KEY=sk-or-v1-...`
3. **Run prep:** `python3 prep_training_data.py --emails ... --output training_data.jsonl --num-samples 500`
4. **Wait 15 mins**
5. **Run training:** `python3 train_lora_local.py --data training_data.jsonl`
6. **Wait 2-3 hours**
7. **Test:** `python3 test_omar_model.py`
8. **Ship it!**

---

**Total cost: $0.15 | Total time: 3 hours | Result: AI that writes like you**
