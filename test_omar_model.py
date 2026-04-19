#!/usr/bin/env python3
"""
Test your fine-tuned Omar voice model.
"""

import click


@click.command()
@click.option('--model', default='omar-voice-lora', help='Path to LoRA adapter')
@click.option('--prompt', help='Custom prompt to test')
def main(model: str, prompt: str):
    """Test the fine-tuned model."""

    click.echo(f"🤖 Loading model from: {model}")

    try:
        from unsloth import FastLanguageModel
    except ImportError:
        click.echo("❌ Unsloth not installed!")
        click.echo("Install with: pip install unsloth")
        return

    # Load the fine-tuned model
    model_obj, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model,
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )

    # Enable fast inference
    FastLanguageModel.for_inference(model_obj)

    click.echo("✓ Model loaded\n")

    # Default test prompts if none provided
    test_prompts = [
        "Write a professional email about a database migration project",
        "Respond to a technical question about microservices architecture",
        "Write an email declining a meeting request politely",
    ] if not prompt else [prompt]

    for test_prompt in test_prompts:
        click.echo("="*70)
        click.echo(f"PROMPT: {test_prompt}")
        click.echo("="*70)

        # Format as Llama 3.1 chat
        formatted_prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{test_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

        inputs = tokenizer([formatted_prompt], return_tensors="pt").to("cpu")

        # Generate
        outputs = model_obj.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
        )

        # Decode
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract just the assistant's response
        if "assistant" in response:
            response = response.split("assistant")[-1].strip()

        click.echo(f"\nRESPONSE:\n{response}\n")

    click.echo("="*70)
    click.echo("\n🎯 Does this sound like you?")
    click.echo("If yes: The fine-tuning worked!")
    click.echo("If no: Try more/better training data or more epochs")


if __name__ == '__main__':
    main()
