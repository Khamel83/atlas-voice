#!/usr/bin/env python3
"""
Test the /consultant command integration
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.commands.consultant_command import ConsultantCommand

async def test_consultant_command():
    """Test the consultant command"""
    print("🧪 Testing /consultant Command")
    print("=" * 50)

    cmd = ConsultantCommand()

    # Test help
    print("\n1. Testing help command:")
    result = await cmd.handle_command(["help"])
    print(result[:200] + "..." if len(result) > 200 else result)

    # Test strategic analysis
    print("\n2. Testing strategic analysis:")
    test_question = "How do we scale from 100 to 10,000 users with current team?"
    result = await cmd.handle_command(test_question.split())
    print(result)

    print("\n✅ Consultant command test complete!")

if __name__ == "__main__":
    asyncio.run(test_consultant_command())