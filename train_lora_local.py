#!/usr/bin/env python3
"""
Fine-tune Llama 3.1 8B with LoRA on your email writing style.
Uses Unsloth for optimized QLoRA training on M1/M2 Macs.
"""

import json
import click
from pathlib import Path


@click.command()
@click.option('--data', required=True, help='Path to training_data.jsonl')
@click.option('--output', default='omar-voice-lora', help='Output directory for LoRA adapter')
@click.option('--epochs', default=3, type=int, help='Number of training epochs')
@click.option('--batch-size', default=2, type=int, help='Batch size (reduce if OOM)')
def main(data: str, output: str, epochs: int, batch_size: int):
    """Fine-tune Llama 3.1 8B with your writing style using LoRA."""

    click.echo("🚀 Starting LoRA fine-tuning...")
    click.echo(f"   Data: {data}")
    click.echo(f"   Output: {output}")

    # Check if Unsloth is installed
    try:
        from unsloth import FastLanguageModel
        import torch
    except ImportError:
        click.echo("\n❌ Unsloth not installed!")
        click.echo("Install with: pip install unsloth")
        click.echo("\nOr if that fails, use:")
        click.echo("pip install \"unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git\"")
        return

    # Load training data
    click.echo(f"\n📚 Loading training data...")
    training_data = []
    with open(data, 'r') as f:
        for line in f:
            example = json.loads(line)
            training_data.append(example)

    click.echo(f"✓ Loaded {len(training_data)} examples")

    # Load model with Unsloth
    click.echo(f"\n🤖 Loading Llama 3.1 8B in 4-bit mode...")

    max_seq_length = 2048
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/Meta-Llama-3.1-8B-bnb-4bit",
        max_seq_length=max_seq_length,
        dtype=None,  # Auto-detect
        load_in_4bit=True,
    )

    click.echo("✓ Model loaded")

    # Configure LoRA
    click.echo(f"\n⚙️  Configuring LoRA...")

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,  # LoRA rank
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    click.echo("✓ LoRA configured")

    # Format data for training
    click.echo(f"\n📝 Formatting training data...")

    def format_prompt(example):
        """Format as Llama 3.1 chat template."""
        return f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{example['instruction']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{example['output']}<|eot_id|>"""

    formatted_data = [
        {"text": format_prompt(ex)} for ex in training_data
    ]

    click.echo(f"✓ Formatted {len(formatted_data)} examples")

    # Create dataset
    from datasets import Dataset

    dataset = Dataset.from_list(formatted_data)

    # Training configuration
    click.echo(f"\n🏋️  Training configuration:")
    click.echo(f"   Epochs: {epochs}")
    click.echo(f"   Batch size: {batch_size}")
    click.echo(f"   Learning rate: 2e-4")
    click.echo(f"   Max seq length: {max_seq_length}")

    from transformers import TrainingArguments
    from trl import SFTTrainer

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=batch_size,
            gradient_accumulation_steps=4,
            warmup_steps=10,
            num_train_epochs=epochs,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_available(),
            bf16=torch.cuda.is_available(),
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="cosine",
            seed=42,
            output_dir=output,
            save_strategy="epoch",
        ),
    )

    # Train!
    click.echo(f"\n🔥 Starting training (this will take 1-3 hours)...")
    click.echo("You can monitor progress below:\n")

    trainer_stats = trainer.train()

    click.echo(f"\n✅ Training complete!")

    # Save the model
    click.echo(f"\n💾 Saving LoRA adapter to: {output}")

    model.save_pretrained(output)
    tokenizer.save_pretrained(output)

    click.echo(f"✓ Saved!")

    # Show stats
    click.echo(f"\n📊 Training Stats:")
    click.echo(f"   Total steps: {trainer_stats.global_step}")
    click.echo(f"   Final loss: {trainer_stats.training_loss:.4f}")

    click.echo(f"\n🎉 Done! Your personalized model is ready.")
    click.echo(f"\nTo test it:")
    click.echo(f"   python test_omar_model.py --model {output}")


if __name__ == '__main__':
    main()
