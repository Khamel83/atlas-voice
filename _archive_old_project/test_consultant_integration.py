#!/usr/bin/env python3
"""
Quick integration test for OOS Consultant command
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.simple_command_handler import SimpleCommandHandler

async def test_consultant_command():
    """Test the consultant command integration"""
    print("🧪 Testing OOS Consultant Command Integration")
    print("=" * 50)

    handler = SimpleCommandHandler()

    # Test help command
    print("\n1. Testing /consultant help:")
    result = await handler.execute_command("consultant", "help")
    print(result.get("output", result.get("error", "No result")))

    # Test start command
    print("\n2. Testing /consultant start:")
    result = await handler.execute_command("consultant", "start TestProject ecommerce")
    print(result.get("output", result.get("error", "No result")))

    # Test invalid command
    print("\n3. Testing invalid consultant command:")
    result = await handler.execute_command("consultant", "invalid args")
    print(result.get("output", result.get("error", "No result")))

    print("\n✅ Consultant command integration test complete!")

if __name__ == "__main__":
    asyncio.run(test_consultant_command())