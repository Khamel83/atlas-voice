#!/usr/bin/env python3
"""
Smart CLI for Atlas Voice
Understands natural language requests and executes appropriate actions
"""

import click
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from intelligent_interface import IntelligentInterface

@click.command()
@click.argument('request', required=False, default="")
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
@click.option('--quiet', '-q', is_flag=True, help='Minimal output')
def smart_cli(request, interactive, quiet):
    """Atlas Voice - Smart Interface that understands natural requests"""

    interface = IntelligentInterface()

    if interactive or not request:
        # Start interactive mode
        interface.interactive_session()
    else:
        # Process single request
        if not quiet:
            print("🤖 Processing your request...")

        response = interface.execute_request(request)

        if not quiet:
            print(f"\n{response}")
        else:
            # Just return the essential result for scripting
            lines = response.split('\n')
            for line in lines:
                if line.startswith('✅') or line.startswith('📄') or line.startswith('🎭'):
                    print(line)

if __name__ == '__main__':
    smart_cli()
