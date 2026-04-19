#!/usr/bin/env python3
"""
Prepare training data for LoRA fine-tuning from email corpus.
Uses OpenRouter + Gemini 2.5 Flash Lite to auto-generate instruction-output pairs.
"""

import json
import csv
import random
import requests
import os
from pathlib import Path
from typing import List, Dict
import click


def call_gemini_flash_lite(prompt: str, api_key: str) -> str:
    """Call Gemini 2.5 Flash Lite via OpenRouter."""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "google/gemini-2.5-flash-lite",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API call failed: {e}")
        return None


def clean_email_text(text: str) -> str:
    """Clean email artifacts from text."""
    if not text:
        return ""

    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Skip email quote lines
        if line.strip().startswith('>'):
            continue

        # Skip reply headers
        if 'wrote:' in line.lower() or 'from:' in line.lower():
            continue

        # Skip signature markers
        if line.strip() in ['--', '___', '---']:
            break

        # Skip auto-replies
        skip_phrases = [
            'sent from my iphone',
            'sent from my android',
            'out of office',
            'automatic reply',
            'unsubscribe',
            'privacy policy'
        ]
        if any(phrase in line.lower() for phrase in skip_phrases):
            continue

        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines).strip()


def generate_instruction_pair(email_text: str, api_key: str) -> Dict:
    """Generate an instruction-output pair from an email."""

    prompt = f"""You are analyzing an email to create training data for a language model.

Given this email text, create a training example in this exact JSON format:
{{
  "instruction": "A natural prompt that would generate this type of email (e.g., 'Write a professional email about database optimization')",
  "output": "The actual email text (cleaned and formatted)"
}}

EMAIL TEXT:
{email_text[:1000]}

Return ONLY valid JSON, no other text.
"""

    response = call_gemini_flash_lite(prompt, api_key)
    if not response:
        return None

    try:
        # Parse the JSON response
        data = json.loads(response)

        # Validate format
        if "instruction" in data and "output" in data:
            return data
        else:
            return None
    except json.JSONDecodeError:
        return None


@click.command()
@click.option('--emails', required=True, help='Path to extracted_emails.csv')
@click.option('--output', default='training_data.jsonl', help='Output JSONL file')
@click.option('--num-samples', default=500, type=int, help='Number of training examples to generate')
@click.option('--api-key', help='OpenRouter API key (or set OPENROUTER_API_KEY env var)')
def main(emails: str, output: str, num_samples: int, api_key: str):
    """Generate training data from email corpus using Gemini 2.5 Flash Lite."""

    # Get API key
    if not api_key:
        api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        click.echo("❌ Error: Need OpenRouter API key")
        click.echo("Set OPENROUTER_API_KEY env var or use --api-key")
        return

    click.echo(f"📧 Loading emails from: {emails}")

    # Load emails
    emails_data = []
    with open(emails, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get content from any available column
            content = row.get('body') or row.get('content') or row.get('text') or row.get('message')
            if content and len(content) > 100:  # Skip very short emails
                cleaned = clean_email_text(content)
                if cleaned and len(cleaned) > 100:
                    emails_data.append(cleaned)

    click.echo(f"✓ Loaded {len(emails_data):,} emails")

    # Sample random emails
    sample_emails = random.sample(emails_data, min(num_samples * 2, len(emails_data)))
    click.echo(f"📊 Generating {num_samples} training examples...")

    training_examples = []
    successful = 0
    failed = 0

    for i, email_text in enumerate(sample_emails):
        if successful >= num_samples:
            break

        click.echo(f"Processing {i+1}/{len(sample_emails)} (success: {successful}, failed: {failed})", nl=False)

        example = generate_instruction_pair(email_text, api_key)

        if example:
            training_examples.append(example)
            successful += 1
            click.echo(" ✓")
        else:
            failed += 1
            click.echo(" ✗")

    # Save to JSONL
    click.echo(f"\n💾 Saving to: {output}")
    with open(output, 'w') as f:
        for example in training_examples:
            f.write(json.dumps(example) + '\n')

    click.echo(f"✅ Done!")
    click.echo(f"   Generated: {successful} examples")
    click.echo(f"   Failed: {failed} attempts")
    click.echo(f"   Output: {output}")
    click.echo(f"\n💰 Estimated cost: ~${(successful * 2000 / 1_000_000 * 0.30):.4f}")
    click.echo(f"   (Gemini 2.5 Flash Lite: ~$0.30/1M tokens)")


if __name__ == '__main__':
    main()
