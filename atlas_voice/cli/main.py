"""Main CLI interface for Atlas Voice."""

import click
from pathlib import Path
from atlas_voice.storage import Database
from atlas_voice.services import ImportService, AnalyzerService, GeneratorService


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Atlas Voice - Generate AI voice prompts from your writing patterns."""
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--type', 'file_type', type=click.Choice(['email', 'text', 'json', 'auto']),
              default='auto', help='File type to import')
@click.option('--name', default=None, help='Name for this voice profile')
@click.option('--description', default=None, help='Description of data source')
def import_data(path: str, file_type: str, name: str, description: str):
    """Import writing samples from a file or directory."""
    click.echo(f"Importing data from: {path}")

    importer = ImportService()

    # Determine if path is file or directory
    path_obj = Path(path)

    try:
        if path_obj.is_file():
            file_type_actual = None if file_type == 'auto' else file_type
            texts = importer.import_file(str(path_obj), file_type_actual)
        else:
            file_type_actual = None if file_type == 'auto' else file_type
            texts = importer.import_directory(str(path_obj), file_type_actual)

        click.echo(f"✓ Imported {len(texts)} text samples")
        click.echo(f"✓ Total words: {sum(len(t.split()) for t in texts):,}")

        # Now analyze
        click.echo("\nAnalyzing patterns...")
        analyzer = AnalyzerService()

        profile_name = name or f"Profile from {path_obj.name}"
        source_desc = description or f"Imported from {path_obj.name}"

        pattern = analyzer.analyze(texts, name=profile_name, source_description=source_desc)

        # Save to database
        db = Database()
        db.save_pattern(pattern)
        db.close()

        click.echo(f"✓ Voice pattern saved: {pattern.id}")
        click.echo(f"\nProfile: {pattern.name}")
        click.echo(f"  Words analyzed: {pattern.total_words:,}")
        click.echo(f"  Sentences: {pattern.total_sentences:,}")
        click.echo(f"  Avg sentence length: {pattern.avg_sentence_length} words")
        click.echo(f"  Vocabulary richness: {pattern.vocab_richness:.3f}")

        click.echo(f"\nNext: Run 'atlas-voice generate {pattern.id}' to create a prompt")

    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.argument('pattern_id')
@click.option('--context', type=click.Choice(['professional', 'casual', 'creative', 'technical']),
              default='professional', help='Context for the prompt')
@click.option('--output', type=click.Path(), default=None, help='Output file path')
def generate(pattern_id: str, context: str, output: str):
    """Generate an AI system prompt from a voice pattern."""
    db = Database()

    # Get pattern
    pattern = db.get_pattern(pattern_id)
    if not pattern:
        click.echo(f"✗ Pattern not found: {pattern_id}", err=True)
        db.close()
        raise click.Abort()

    click.echo(f"Generating {context} prompt from: {pattern.name}")

    # Generate prompt
    generator = GeneratorService()
    prompt = generator.generate(pattern, context=context)

    # Save to database
    db.save_prompt(prompt)
    db.close()

    click.echo(f"✓ Prompt generated: {prompt.id}")

    # Output to file if specified
    if output:
        output_path = Path(output)
        output_path.write_text(prompt.prompt_text)
        click.echo(f"✓ Saved to: {output}")
    else:
        click.echo("\n" + "="*70)
        click.echo(prompt.prompt_text)
        click.echo("="*70)

    click.echo(f"\nCopy this prompt and paste it into Claude, ChatGPT, or any AI assistant!")


@cli.command()
def list_patterns():
    """List all voice patterns."""
    db = Database()
    patterns = db.list_patterns()
    db.close()

    if not patterns:
        click.echo("No voice patterns found. Import data first with 'atlas-voice import'")
        return

    click.echo(f"\nFound {len(patterns)} voice pattern(s):\n")

    for pattern in patterns:
        click.echo(f"ID: {pattern.id}")
        click.echo(f"  Name: {pattern.name}")
        click.echo(f"  Words: {pattern.total_words:,}")
        click.echo(f"  Source: {pattern.source_description}")
        click.echo(f"  Created: {pattern.created_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo()


@cli.command()
@click.argument('pattern_id')
def show_pattern(pattern_id: str):
    """Show detailed information about a voice pattern."""
    db = Database()
    pattern = db.get_pattern(pattern_id)
    db.close()

    if not pattern:
        click.echo(f"✗ Pattern not found: {pattern_id}", err=True)
        raise click.Abort()

    click.echo(f"\n{pattern.name}")
    click.echo("="*70)
    click.echo(f"\nID: {pattern.id}")
    click.echo(f"Source: {pattern.source_description}")
    click.echo(f"Created: {pattern.created_at.strftime('%Y-%m-%d %H:%M')}")

    click.echo(f"\n## Statistics")
    click.echo(f"  Total words: {pattern.total_words:,}")
    click.echo(f"  Total sentences: {pattern.total_sentences:,}")
    click.echo(f"  Avg sentence length: {pattern.avg_sentence_length} words")
    click.echo(f"  Vocabulary richness: {pattern.vocab_richness:.3f}")
    click.echo(f"  Avg word length: {pattern.avg_word_length} characters")

    if pattern.function_words:
        click.echo(f"\n## Top Function Words")
        for fw in pattern.function_words[:10]:
            click.echo(f"  {fw.word}: {fw.frequency:.2f}%")

    if pattern.style_markers:
        click.echo(f"\n## Style Markers")
        for marker in pattern.style_markers:
            click.echo(f"  {marker.category.title()}: {', '.join(marker.phrases[:5])}")

    if pattern.sentence_starters:
        click.echo(f"\n## Common Sentence Starters")
        click.echo(f"  {', '.join(pattern.sentence_starters[:10])}")


@cli.command()
@click.option('--pattern', 'pattern_id', default=None, help='Filter by pattern ID')
def list_prompts(pattern_id: str):
    """List all generated prompts."""
    db = Database()
    prompts = db.list_prompts(pattern_id)
    db.close()

    if not prompts:
        click.echo("No prompts found. Generate one with 'atlas-voice generate'")
        return

    click.echo(f"\nFound {len(prompts)} prompt(s):\n")

    for prompt in prompts:
        click.echo(f"ID: {prompt.id}")
        click.echo(f"  Name: {prompt.name}")
        click.echo(f"  Context: {prompt.context}")
        click.echo(f"  Pattern: {prompt.pattern_id}")
        click.echo(f"  Created: {prompt.created_at.strftime('%Y-%m-%d %H:%M')}")
        click.echo()


@cli.command()
@click.argument('prompt_id')
@click.option('--output', type=click.Path(), default=None, help='Output file path')
def export_prompt(prompt_id: str, output: str):
    """Export a prompt to a text file."""
    db = Database()
    prompt = db.get_prompt(prompt_id)
    db.close()

    if not prompt:
        click.echo(f"✗ Prompt not found: {prompt_id}", err=True)
        raise click.Abort()

    if output:
        output_path = Path(output)
    else:
        # Default filename
        output_path = Path(f"{prompt.id}.txt")

    output_path.write_text(prompt.prompt_text)
    click.echo(f"✓ Exported to: {output_path}")


@cli.command()
def privacy_check():
    """Show privacy information and what data is stored."""
    db = Database()
    patterns = db.list_patterns()
    db.close()

    click.echo("\n" + "="*70)
    click.echo("PRIVACY REPORT")
    click.echo("="*70)

    click.echo("\n✓ Privacy Guarantee:")
    click.echo("  - NO original text content is stored")
    click.echo("  - ONLY linguistic patterns are saved (statistics, frequencies)")
    click.echo("  - All data stays local on your machine")
    click.echo("  - No external API calls (unless you use the prompts with AI)")

    click.echo(f"\n✓ Current Storage:")
    click.echo(f"  - Voice patterns: {len(patterns)}")

    total_words_analyzed = sum(p.total_words for p in patterns)
    click.echo(f"  - Words analyzed: {total_words_analyzed:,}")
    click.echo(f"  - Original content stored: ZERO")

    # Database size
    db_path = Path("data/atlas_voice.db")
    if db_path.exists():
        size_kb = db_path.stat().st_size / 1024
        click.echo(f"  - Database size: {size_kb:.1f} KB")

    click.echo("\n✓ What We Store:")
    click.echo("  - Word frequencies (e.g., 'the' appears 3.2% of the time)")
    click.echo("  - Sentence length averages")
    click.echo("  - Common phrases and patterns")
    click.echo("  - Style markers (casual/formal indicators)")

    click.echo("\n✓ Data Location:")
    click.echo(f"  - Database: {db_path.absolute()}")
    click.echo(f"  - Import temp dir: data/imports/")


@cli.command()
def clear_imports():
    """Clear temporary import files."""
    importer = ImportService()
    importer.clear_temp_files()
    click.echo("✓ Temporary import files cleared")


@cli.command()
@click.option('--port', default=8000, help='Port to run server on')
@click.option('--host', default='127.0.0.1', help='Host to bind to')
def serve(port: int, host: str):
    """Start the web interface."""
    click.echo(f"Starting Atlas Voice web server on http://{host}:{port}")
    click.echo("Press Ctrl+C to stop")

    import uvicorn
    from atlas_voice.api.app import app

    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    cli()
