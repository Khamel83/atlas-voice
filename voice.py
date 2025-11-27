#!/usr/bin/env python3
"""
Atlas Voice - Simple Entry Point
Just run this and tell me what you want to do!
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from intelligent_interface import IntelligentInterface

def main():
    """Main entry point - just ask naturally!"""
    print("🤖 Atlas Voice - Smart Interface")
    print("=" * 50)
    print("💬 I understand natural requests! Just tell me what you want.")
    print("   Examples:")
    print("   • 'Analyze my emails once and delete them after'")
    print("   • 'Create my voice profile from my documents'")
    print("   • 'How would I say hello in my voice?'")
    print("   • 'Show me my voice analysis'")
    print("   • 'Clean up all my data'")
    print("=" * 50)

    if len(sys.argv) > 1:
        # Process command line request
        request = " ".join(sys.argv[1:])
        print(f"🎯 Understanding: '{request}'")
        print("-" * 30)

        interface = IntelligentInterface()
        response = interface.execute_request(request)
        print(response)
    else:
        # Start interactive mode
        interface = IntelligentInterface()
        interface.interactive_session()

if __name__ == "__main__":
    main()
