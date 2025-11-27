#!/usr/bin/env python3
"""
Atlas Voice - Main CLI Interface
Privacy-first voice pattern analysis and prompt generation
"""

import click
import os
import sys
import json
import sqlite3
from pathlib import Path
import glob
import shutil
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from style_analyzer import FinalStylePreservationSystem
from intelligent_data_processor import IntelligentDataProcessor
from voice_integration_engine import VoiceIntegrationEngine

class VoiceMatchCLI:
    """Main CLI class for Atlas Voice"""

    def __init__(self):
        self.data_dir = Path("data")
        self.profiles_dir = Path("profiles")
        self.prompts_dir = Path("prompts")

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.profiles_dir.mkdir(exist_ok=True)
        self.prompts_dir.mkdir(exist_ok=True)

        # Initialize analyzer
        self.analyzer = None

    def _init_analyzer(self):
        """Initialize the style analyzer"""
        if self.analyzer is None:
            self.analyzer = FinalStylePreservationSystem(str(self.data_dir))

    def _privacy_check_import_dir(self, import_dir):
        """Check if import directory contains safe files"""
        dangerous_patterns = ['*.db', '*.sqlite', '*.sqlite3', '*.key', 'secrets.txt']
        import_path = Path(import_dir)

        for pattern in dangerous_patterns:
            matches = list(import_path.glob(pattern))
            if matches:
                click.echo(f"⚠️  Warning: Found potentially sensitive files: {matches}")
                if not click.confirm("Continue anyway?"):
                    sys.exit(1)

    def _cleanup_source_files(self, import_dir, delete_files=True):
        """Clean up source files after import"""
        if not delete_files:
            return

        import_path = Path(import_dir)
        supported_extensions = ['.txt', '.md', '.eml']

        for ext in supported_extensions:
            for file_path in import_path.glob(f"**/*{ext}"):
                try:
                    file_path.unlink()
                    click.echo(f"🗑️  Deleted: {file_path}")
                except Exception as e:
                    click.echo(f"❌ Failed to delete {file_path}: {e}")

    def _verify_no_private_data(self):
        """Verify no private data is in current directory"""
        private_patterns = [
            "*.db", "*.sqlite", "*.sqlite3",
            "data/*.db", "data/*.sqlite",
            ".env", "api_keys.txt", "secrets.txt"
        ]

        for pattern in private_patterns:
            matches = glob.glob(pattern)
            if matches:
                click.echo(f"❌ Found private data that should be excluded: {matches}")
                return False
        return True

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Atlas Voice - Turn any AI into your voice twin using prompt engineering"""
    pass

@cli.command()
@click.option('--data-dir', '-d', required=True,
              help='Directory containing your data files (.txt, .md, .eml)')
@click.option('--delete-source/--keep-source', default=True,
              help='Delete source files after import (default: delete)')
@click.option('--profile-name', '-p', default='my_voice',
              help='Name for your voice profile')
def import_data(data_dir, delete_source, profile_name):
    """Import your writing data for voice analysis"""

    voice_cli = VoiceMatchCLI()

    # Privacy check
    voice_cli._privacy_check_import_dir(data_dir)

    click.echo(f"📥 Importing data from {data_dir}")
    click.echo("🔒 Privacy: Source files will be deleted after processing")

    # Initialize analyzer
    voice_cli._init_analyzer()

    # Import data using intelligent processor
    import_path = Path(data_dir)
    texts_processed = 0

    for file_path in import_path.rglob("*"):
        if file_path.is_file() and file_path.suffix in ['.txt', '.md', '.eml']:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if len(content.strip()) > 100:  # Minimum length threshold
                        voice_cli.analyzer.analyze_text(content)
                        texts_processed += 1
                        click.echo(f"📄 Processed: {file_path.name}")
            except Exception as e:
                click.echo(f"❌ Error processing {file_path}: {e}")

    if texts_processed == 0:
        click.echo("❌ No valid text files found for import")
        return

    # Generate voice profile
    profile_path = voice_cli.profiles_dir / f"{profile_name}.json"
    profile_data = voice_cli.analyzer.generate_voice_profile()

    with open(profile_path, 'w') as f:
        json.dump(profile_data, f, indent=2)

    click.echo(f"✅ Generated voice profile: {profile_path}")
    click.echo(f"📊 Analyzed {voice_cli.analyzer.total_words:,} words")
    click.echo(f"📄 Processed {texts_processed} files")

    # Clean up source files
    if delete_source:
        voice_cli._cleanup_source_files(data_dir, delete_source=True)
        click.echo("🗑️  Source files deleted for privacy")

    # Generate prompt
    prompt = voice_cli.analyzer.generate_final_prompt()
    prompt_path = voice_cli.prompts_dir / f"{profile_name}.txt"

    with open(prompt_path, 'w') as f:
        f.write(prompt)

    click.echo(f"🎭 Generated voice prompt: {prompt_path}")

@cli.command()
@click.option('--profile-name', '-p', default='my_voice',
              help='Voice profile to use')
@click.option('--question', '-q', required=True,
              help='Question to ask in your voice')
@click.option('--model', '-m', default='manual',
              help='Model to use (manual, openrouter)')
@click.option('--output', '-o',
              help='Output file for response')
def ask(profile_name, question, model, output):
    """Ask a question using your voice profile"""

    voice_cli = VoiceMatchCLI()
    prompt_path = voice_cli.prompts_dir / f"{profile_name}.txt"

    if not prompt_path.exists():
        click.echo(f"❌ Voice profile not found: {prompt_path}")
        click.echo("💡 Run 'import-data' first to create your voice profile")
        return

    # Read voice prompt
    with open(prompt_path, 'r') as f:
        voice_prompt = f.read()

    click.echo(f"🎤 Using voice profile: {profile_name}")
    click.echo(f"❓ Question: {question}")

    if model == 'manual':
        # Show the prompt for manual use
        click.echo("\n" + "="*50)
        click.echo("📋 VOICE PROMPT (copy this to your AI):")
        click.echo("="*50)
        click.echo(voice_prompt)
        click.echo("="*50)
        click.echo(f"\n🤖 Then ask: {question}")

        if output:
            with open(output, 'w') as f:
                f.write(f"VOICE PROMPT:\n{voice_prompt}\n\nQUESTION:\n{question}")
            click.echo(f"💾 Saved to: {output}")

    elif model == 'openrouter':
        # Use OpenRouter API (if available)
        try:
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.getenv('OPENROUTER_API_KEY')
            if not api_key:
                click.echo("❌ OPENROUTER_API_KEY not found in environment")
                click.echo("💡 Create a .env file with your API key")
                return

            # Make API call (implementation needed)
            click.echo("🤖 OpenRouter integration coming soon!")

        except ImportError:
            click.echo("❌ python-dotenv not installed")
            click.echo("💡 Run: pip install python-dotenv requests")

    else:
        click.echo(f"❌ Unknown model: {model}")

@cli.command()
@click.option('--profile-name', '-p', default='my_voice',
              help='Voice profile to export')
@click.option('--output', '-o',
              help='Output file (default: stdout)')
def export_prompt(profile_name, output):
    """Export your voice prompt for manual use"""

    voice_cli = VoiceMatchCLI()
    prompt_path = voice_cli.prompts_dir / f"{profile_name}.txt"

    if not prompt_path.exists():
        click.echo(f"❌ Voice prompt not found: {prompt_path}")
        click.echo("💡 Run 'import-data' first to create your voice profile")
        return

    with open(prompt_path, 'r') as f:
        prompt = f.read()

    if output:
        with open(output, 'w') as f:
            f.write(prompt)
        click.echo(f"📄 Exported voice prompt to: {output}")
    else:
        click.echo("\n" + "="*50)
        click.echo("🎭 YOUR VOICE PROMPT:")
        click.echo("="*50)
        click.echo(prompt)
        click.echo("="*50)

@cli.command()
@click.option('--profile-name', '-p', default='my_voice',
              help='Voice profile to analyze')
def analyze_profile(profile_name):
    """Analyze and show details about your voice profile"""

    voice_cli = VoiceMatchCLI()
    profile_path = voice_cli.profiles_dir / f"{profile_name}.json"

    if not profile_path.exists():
        click.echo(f"❌ Voice profile not found: {profile_path}")
        return

    with open(profile_path, 'r') as f:
        profile = json.load(f)

    click.echo(f"📊 Voice Profile Analysis: {profile_name}")
    click.echo("=" * 40)

    if 'function_word_freq' in profile:
        click.echo("📝 Top Function Words:")
        sorted_words = sorted(profile['function_word_freq'].items(),
                             key=lambda x: x[1], reverse=True)[:10]
        for word, freq in sorted_words:
            click.echo(f"   {word}: {freq:.1%}")

    if 'avg_sentence_length' in profile:
        click.echo(f"📏 Average Sentence Length: {profile['avg_sentence_length']:.1f} words")

    if 'total_words' in profile:
        click.echo(f"📚 Total Words Analyzed: {profile['total_words']:,}")

    if 'unique_words' in profile:
        click.echo(f"🔤 Unique Words: {profile['unique_words']:,}")

@cli.command()
def list_profiles():
    """List all available voice profiles"""

    voice_cli = VoiceMatchCLI()
    profiles = list(voice_cli.profiles_dir.glob("*.json"))

    if not profiles:
        click.echo("❌ No voice profiles found")
        click.echo("💡 Run 'import-data' to create your first profile")
        return

    click.echo("🎭 Available Voice Profiles:")
    for profile in profiles:
        prompt_file = voice_cli.prompts_dir / f"{profile.stem}.txt"
        status = "✅" if prompt_file.exists() else "❌"
        click.echo(f"   {status} {profile.stem}")

@cli.command()
@click.argument('request', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Start intelligent interactive mode')
def smart(request, interactive):
    """Smart interface that understands natural requests"""
    from intelligent_interface import IntelligentInterface

    interface = IntelligentInterface()

    if interactive or not request:
        interface.interactive_session()
    else:
        response = interface.execute_request(request)
        click.echo(response)

@cli.command()
def privacy_check():
    """Run privacy and security checks"""

    voice_cli = VoiceMatchCLI()

    click.echo("🔒 Running Privacy & Security Checks")
    click.echo("=" * 40)

    # Check for private data
    if voice_cli._verify_no_private_data():
        click.echo("✅ No private data detected in repository")
    else:
        click.echo("❌ Private data found - check .gitignore")

    # Check environment file
    env_file = Path(".env")
    if env_file.exists():
        click.echo("⚠️  .env file found - ensure it's not committed")
    else:
        click.echo("✅ No .env file (safe for commit)")

    # Check database files
    db_files = list(Path(".").glob("*.db")) + list(Path(".").glob("*.sqlite*"))
    if db_files:
        click.echo(f"❌ Database files found: {db_files}")
    else:
        click.echo("✅ No database files in root directory")

    # Check API keys in code
    api_key_patterns = ["sk-", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    for pattern in api_key_patterns:
        result = os.system(f"grep -r '{pattern}' src/ 2>/dev/null || true")
        if result == 0:
            click.echo(f"❌ Found potential API key pattern: {pattern}")
        else:
            click.echo(f"✅ No {pattern} patterns found in source")

    click.echo("\n🔒 Privacy check complete")

@cli.command()
@click.option('--profile-name', '-p', default='my_voice',
              help='Voice profile to delete')
@click.confirmation_option(prompt='Are you sure you want to delete this profile?')
def delete_profile(profile_name):
    """Delete a voice profile and associated data"""

    voice_cli = VoiceMatchCLI()

    profile_path = voice_cli.profiles_dir / f"{profile_name}.json"
    prompt_path = voice_cli.prompts_dir / f"{profile_name}.txt"

    deleted = False

    if profile_path.exists():
        profile_path.unlink()
        click.echo(f"🗑️  Deleted profile: {profile_path}")
        deleted = True

    if prompt_path.exists():
        prompt_path.unlink()
        click.echo(f"🗑️  Deleted prompt: {prompt_path}")
        deleted = True

    if not deleted:
        click.echo(f"❌ Profile '{profile_name}' not found")

@cli.command()
@click.argument('data_source', type=click.Path(exists=True))
@click.option('--cleanup-after', is_flag=True, help='Clean up source files after processing')
@click.option('--batch-id', help='Use specific batch ID')
def nuclear_process(data_source, cleanup_after, batch_id):
    """Process data using nuclear safe room architecture"""
    from nuclear_safe_room import NuclearSafeRoom

    print("🏢 NUCLEAR SAFE ROOM PROCESSING")
    print("=" * 40)

    safe_room = NuclearSafeRoom()

    # Complete transfer process
    success = safe_room.transfer_data_source(str(data_source), cleanup_after=cleanup_after)

    if success:
        print("\n✅ Processing complete!")

        # Show Room Two status
        status = safe_room.get_room_two_status()
        print(f"📊 Room Two Status:")
        print(f"   Total batches: {status['total_batches']}")
        print(f"   Total words: {status['total_words_processed']:,}")
        print(f"   Total patterns: {status['total_patterns']}")

        if cleanup_after:
            print(f"🧹 Room One cleaned up - source files processed")
    else:
        print("❌ Processing failed")

@cli.command()
def privacy_dashboard():
    """Open privacy controls dashboard"""
    from privacy_controls import PrivacyControls

    print("🔐 PRIVACY DASHBOARD")
    print("=" * 30)

    controls = PrivacyControls()

    # Run privacy check
    check = controls.run_privacy_check()
    print(f"Privacy Score: {check['privacy_score']}/100")

    if check['issues']:
        print(f"\n⚠️  Issues ({len(check['issues'])}):")
        for issue in check['issues']:
            print(f"  • {issue}")

    # Show current status
    status = controls.get_privacy_status()
    stats = status['database_stats']

    if stats['exists']:
        print(f"\n📊 Database:")
        print(f"   Size: {stats['file_size_mb']:.1f} MB")
        print(f"   Patterns: {stats['total_patterns']:,}")
        print(f"   Batches: {stats['batches'].get('complete', 0)} complete")

    print(f"\n🔧 Settings:")
    print(f"   Auto cleanup: {'✅' if status['settings']['auto_cleanup_enabled'] else '❌'}")
    print(f"   Retention: {status['settings']['retention_days']} days")
    print(f"   Audit log: {'✅' if status['settings']['audit_enabled'] else '❌'}")

    print(f"\n💡 Use 'python3 -m privacy_controls' for full dashboard")

@cli.command()
def data_sources():
    """Manage data source references"""
    from data_source_manager import DataSourceManager

    print("📋 DATA SOURCE MANAGER")
    print("=" * 30)

    manager = DataSourceManager()

    # Show statistics
    stats = manager.get_statistics()
    print(f"📊 Statistics:")
    print(f"   Total sources: {stats['total_sources']}")
    print(f"   Unique paths: {stats['unique_paths']}")
    print(f"   Integrity rate: {stats['integrity_status']['verification_rate']:.1%}")

    if stats['integrity_status']['missing'] > 0:
        print(f"   ⚠️  Missing sources: {stats['integrity_status']['missing']}")

    # Show recent sources
    print(f"\n📁 Recent Sources:")
    sources = list(manager.sources.values())
    sources.sort(key=lambda x: x['registered_at'], reverse=True)

    for source in sources[:5]:
        status = "✅" if manager.verify_source_integrity(source['source_id']) else "❌"
        print(f"   {status} {source['file_name']} ({source['batch_id']})")

    print(f"\n💡 Use 'python3 -m data_source_manager' for full management")

@cli.command()
@click.option('--batch-id', help='Use specific batch ID')
@click.option('--output-dir', default='profiles', help='Output directory for profiles')
def generate_voice_prompt(batch_id, output_dir):
    """Generate voice prompt from processed Room Two data"""
    from voice_prompt_generator import VoicePromptGenerator

    print("🎤 VOICE PROMPT GENERATOR")
    print("=" * 40)

    generator = VoicePromptGenerator()

    try:
        profile_path, prompt_path = generator.create_complete_voice_profile(
            batch_id=batch_id,
            output_dir=output_dir
        )

        print(f"\n✅ Voice profile successfully created!")
        print(f"📄 Profile: {profile_path}")
        print(f"📝 Prompt: {prompt_path}")

        # Show prompt preview
        with open(prompt_path, 'r') as f:
            prompt_content = f.read()
            print(f"\n📋 Prompt Preview (first 300 chars):")
            print("=" * 30)
            print(prompt_content[:300] + "...")
            print("=" * 30)

    except ValueError as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure you've processed data first:")
        print("   python3 src/main.py nuclear-process /path/to/data")

@cli.command()
def voice_profiles():
    """List available voice profiles"""
    from voice_prompt_generator import VoicePromptGenerator

    print("🎭 AVAILABLE VOICE PROFILES")
    print("=" * 40)

    generator = VoicePromptGenerator()
    profiles = generator.get_available_profiles()

    if not profiles:
        print("❌ No voice profiles found")
        print("💡 Create one by processing data:")
        print("   python3 src/main.py nuclear-process /path/to/data")
        print("   python3 src/main.py generate-voice-prompt")
    else:
        print(f"📊 Found {len(profiles)} voice profile(s):")
        print()

        for profile in profiles:
            status = "✅" if profile['has_prompt'] else "⚠️"
            created = profile['created_at'][:19].replace('T', ' ')
            print(f"   {status} {profile['profile_id']}")
            print(f"      📅 Created: {created}")
            print(f"      📊 Words: {profile['total_words']:,}")
            print(f"      📁 Profile: {profile['file_path']}")
            if profile['has_prompt']:
                prompt_file = Path(profile['file_path']).with_suffix('.txt')
                print(f"      📝 Prompt: {prompt_file}")
            print()

@cli.command()
@click.argument('profile_path')
def show_prompt(profile_path):
    """Display a voice prompt"""
    profile_path = Path(profile_path)

    if not profile_path.exists():
        # Try to find prompt file
        if profile_path.suffix == '.json':
            prompt_path = profile_path.with_suffix('.txt')
        else:
            prompt_path = profile_path

        if not prompt_path.exists():
            print(f"❌ Prompt not found: {profile_path}")
            return
    else:
        prompt_path = profile_path

    with open(prompt_path, 'r') as f:
        prompt_content = f.read()

    print("📝 YOUR VOICE PROMPT")
    print("=" * 50)
    print(prompt_content)
    print("=" * 50)
    print(f"📄 Prompt file: {prompt_path}")
    print(f"📏 Length: {len(prompt_content)} characters")

@cli.command()
@click.argument('data_path', type=click.Path(exists=True))
@click.option('-o', '--output', default='personalized_voice_prompt.txt',
              help='Output file for the generated prompt')
@click.option('--no-code', is_flag=True, help='Skip code style analysis')
@click.option('--no-safe-room', is_flag=True, help='Disable nuclear safe room processing')
def create_my_voice(data_path, output, no_code, no_safe_room):
    """Create your personalized AI voice prompt from your data"""

    click.echo("🎤 Creating your personalized AI voice...")
    click.echo(f"📁 Analyzing: {data_path}")

    # Initialize the integration engine
    engine = VoiceIntegrationEngine(safe_room_mode=not no_safe_room)

    # Process the data and generate voice prompt
    with click.progressbar(length=100, label='Processing your voice patterns') as bar:
        result = engine.create_personalized_voice(
            data_path=str(data_path),
            output_path=output,
            include_code_analysis=not no_code
        )
        bar.update(100)

    if result.success:
        click.echo("✅ Success! Your personalized AI voice is ready!")
        click.echo(f"📝 Voice prompt saved to: {output}")
        if result.processing_stats:
            click.echo(f"📊 Processed {result.processing_stats['files_processed']} files")
            click.echo(f"📈 Generated {result.processing_stats['prompt_tokens']} tokens")
            click.echo(f"🎯 Voice confidence: {result.processing_stats['voice_confidence']:.0%}")

        click.echo("\n🚀 Next steps:")
        click.echo("1. Copy your personalized prompt")
        click.echo("2. Use it with Claude, GPT, or your favorite AI")
        click.echo("3. The AI will now sound like you!")
    else:
        click.echo(f"❌ Failed to create voice: {result.error_message}")
        raise click.ClickException(result.error_message)

if __name__ == '__main__':
    cli()
