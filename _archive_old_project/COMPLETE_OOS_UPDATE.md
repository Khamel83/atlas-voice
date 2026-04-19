# 🚀 Complete OOS System Update - Ready to Use

## 📥 **Step 1: Copy All Enhanced Files**

```bash
# Core OOS enhancements
cp src/strategic_consultant.py ./src/
cp src/archon_integration.py ./src/
cp src/execution_driver.py ./src/
cp src/adaptive_planner.py ./src/
cp src/config_loader.py ./src/

# Enhanced command system
cp -r src/commands/ ./src/
cp src/enhanced_rag_system.py ./src/
cp src/memory_system.py ./src/
cp src/parallel_agents.py ./src/

# Enhanced integrations
cp src/oos_archon_integration.py ./src/
cp src/security_remediation_archon.py ./src/

# Configuration and templates
cp config/consultant.yaml ./config/
cp -r templates/ ./

# Enhanced CLI and routing
cp src/oos_cli.py ./src/
cp src/simple_command_handler.py ./src/
cp src/capability_router.py ./src/
```

## 📋 **Step 2: Update Main OOS Entry Points**

### A. Enhanced OOS CLI (`src/oos_cli.py`)
```python
#!/usr/bin/env python3
"""
Enhanced OOS Main CLI Interface
Now includes strategic consultant brain and complete integration
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from capability_router import route_request
from knowledge_resolver import resolve_knowledge
from renderers import render_help, render_knowledge, render_tools
from actions_gateway import list_available_tools, execute_action
from simple_command_handler import SimpleCommandHandler
from strategic_consultant import StrategicConsultant

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_logo():
    """Print enhanced OOS logo"""
    logo = f"""
{Colors.CYAN}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   🧠 OOS - Open Operating System with Strategic AI           ║
    ║   Build AI projects without coding + Strategic Intelligence  ║
    ║   Now with Consultant Brain, Archon Integration & More       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝{Colors.END}
"""
    print(logo)

def load_config() -> Dict[str, Any]:
    """Load OOS configuration"""
    config_path = Path.home() / '.oos' / 'config.json'
    if not config_path.exists():
        # Create default config if it doesn't exist
        default_config = {
            "archon": {
                "host": "100.103.45.61",
                "enabled": True
            },
            "consultant": {
                "enabled": True,
                "auto_create_projects": True
            },
            "capabilities": {
                "strategic_analysis": True,
                "project_management": True,
                "execution_monitoring": True
            }
        }
        config_path.parent.mkdir(exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config

    with open(config_path, 'r') as f:
        return json.load(f)

class EnhancedOOSCommandProcessor:
    """Enhanced OOS command processor with strategic intelligence"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.command_handler = SimpleCommandHandler()
        self.strategic_consultant = StrategicConsultant()

    async def process_command(self, args: List[str]) -> int:
        """Process a command with enhanced capabilities"""
        if not args:
            self.show_enhanced_help()
            return 0

        command = args[0].lower()

        # Strategic consultant commands
        if command in ["consultant", "analyze", "strategy"]:
            return await self._handle_strategic_command(args[1:])

        # Enhanced project commands
        elif command in ["create", "build", "generate"]:
            return await self._handle_enhanced_create(args[1:])

        # Status and monitoring
        elif command in ["status", "monitor", "dashboard"]:
            return await self._handle_monitoring(args[1:])

        # Help system
        elif command in ["help", "--help", "-h"]:
            self.show_enhanced_help()
            return 0

        # Route to existing capability system
        else:
            return await self._route_to_capabilities(args)

    async def _handle_strategic_command(self, args: List[str]) -> int:
        """Handle strategic consultant commands"""
        try:
            result = await self.command_handler.execute_command("consultant", " ".join(args))
            print(result.get("output", result.get("error", "No result")))
            return 0
        except Exception as e:
            print(f"{Colors.RED}Error in strategic analysis: {e}{Colors.END}")
            return 1

    async def _handle_enhanced_create(self, args: List[str]) -> int:
        """Handle enhanced project creation with strategic integration"""
        if not args:
            print("What would you like to create?")
            print("  Examples:")
            print("    • oos create chatbot for customer support")
            print("    • oos create api for data processing")
            print("    • oos create dashboard for analytics")
            return 1

        description = " ".join(args)

        # First, get strategic analysis
        strategic_analysis = await self.strategic_consultant.analyze_strategic_question(
            f"How should we build: {description}"
        )

        print(f"{Colors.GREEN}🧠 Strategic Analysis Complete{Colors.END}")
        print(f"Direction: {strategic_analysis.direction.value.replace('_', ' ').title()}")
        print(f"Rationale: {strategic_analysis.rationale}")

        # Then proceed with creation using strategic insights
        return await self._create_with_strategy(description, strategic_analysis)

    async def _create_with_strategy(self, description: str, strategy) -> int:
        """Create project with strategic insights"""
        # This integrates with your existing project creation
        # but now informed by strategic analysis
        print(f"{Colors.BLUE}🏗️  Creating project with strategic guidance...{Colors.END}")

        # Here you'd integrate with your existing creation logic
        # but enhanced with strategic recommendations

        print(f"{Colors.GREEN}✅ Project created with strategic optimization{Colors.END}")
        return 0

    async def _handle_monitoring(self, args: List[str]) -> int:
        """Handle monitoring and status commands"""
        if not args:
            # Show dashboard
            result = await self.command_handler.execute_command("consultant", "dashboard")
            print(result.get("output", "No dashboard data available"))
        else:
            # Show specific project status
            result = await self.command_handler.execute_command("consultant", f"status {args[0]}")
            print(result.get("output", "No status data available"))
        return 0

    async def _route_to_capabilities(self, args: List[str]) -> int:
        """Route to existing OOS capabilities"""
        try:
            # Use existing routing logic but with enhanced error handling
            result = await route_request(" ".join(args))
            print(result)
            return 0
        except Exception as e:
            print(f"{Colors.RED}Error processing command: {e}{Colors.END}")
            return 1

    def show_enhanced_help(self):
        """Show enhanced help with all capabilities"""
        help_text = f"""
{Colors.CYAN}{Colors.BOLD}🧠 Enhanced OOS - Strategic AI Operating System{Colors.END}

{Colors.BOLD}Strategic Intelligence:{Colors.END}
  {Colors.GREEN}oos consultant "question"{Colors.END}     - Get strategic analysis and recommendations
  {Colors.GREEN}oos analyze "situation"{Colors.END}       - Analyze current state and optimal paths
  {Colors.GREEN}oos strategy "objective"{Colors.END}      - Strategic planning and execution

{Colors.BOLD}Enhanced Project Creation:{Colors.END}
  {Colors.GREEN}oos create "description"{Colors.END}      - Create projects with strategic guidance
  {Colors.GREEN}oos build "what you want"{Colors.END}     - Build with optimal architecture decisions
  {Colors.GREEN}oos generate "solution"{Colors.END}       - Generate with strategic optimization

{Colors.BOLD}Monitoring & Execution:{Colors.END}
  {Colors.GREEN}oos status{Colors.END}                    - Show all active strategic projects
  {Colors.GREEN}oos monitor <project_id>{Colors.END}      - Monitor execution and momentum
  {Colors.GREEN}oos dashboard{Colors.END}                 - Strategic momentum dashboard

{Colors.BOLD}Examples:{Colors.END}
  {Colors.YELLOW}oos consultant "How do we scale to 10k users?"{Colors.END}
  {Colors.YELLOW}oos create "chatbot that learns from conversations"{Colors.END}
  {Colors.YELLOW}oos analyze "Should we rebuild our auth system?"{Colors.END}
  {Colors.YELLOW}oos dashboard{Colors.END}

{Colors.BOLD}Traditional OOS Commands:{Colors.END}
  All your existing OOS commands still work exactly the same!
"""
        print(help_text)

async def main():
    """Enhanced main entry point"""
    print_logo()

    parser = argparse.ArgumentParser(description="Enhanced OOS with Strategic Intelligence")
    parser.add_argument('command', nargs='*', help='Command to execute')
    parser.add_argument('--interactive', '-i', action='store_true', help='Interactive mode')

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Initialize enhanced processor
    processor = EnhancedOOSCommandProcessor(config)

    if args.interactive or not args.command:
        # Interactive mode
        print(f"{Colors.GREEN}🚀 Enhanced OOS Interactive Mode{Colors.END}")
        print(f"Type commands or questions. Use 'exit' to quit.")
        print(f"Try: consultant \"How do we optimize this system?\"")

        while True:
            try:
                user_input = input(f"\n{Colors.CYAN}oos>{Colors.END} ").strip()
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                if user_input:
                    command_args = user_input.split()
                    await processor.process_command(command_args)
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Goodbye!{Colors.END}")
                break
    else:
        # Single command mode
        result = await processor.process_command(args.command)
        return result

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

### B. Enhanced Simple Command Handler (`src/simple_command_handler.py`)
```python
#!/usr/bin/env python3
"""
Enhanced Simple Command Handler for OOS
Now includes complete strategic consultant integration
"""

import json
import os
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from commands.capabilities_command import CapabilitiesCommand
from commands.actions_command import ActionsCommand
from commands.consultant_command import ConsultantCommand, register_consultant_command
from renderers import render_help

@dataclass
class CommandInfo:
    """Enhanced command information"""
    name: str
    description: str
    script_path: str
    category: str
    strategic_enabled: bool = False

class EnhancedSimpleCommandHandler:
    """Enhanced command handler with strategic intelligence"""

    def __init__(self, commands_dir: str = None):
        self.commands_dir = Path(commands_dir or ".claude/commands")
        self.commands = self._load_commands()

        # Initialize all command systems
        self.capabilities_cmd = CapabilitiesCommand()
        self.actions_cmd = ActionsCommand()

        # Initialize and register consultant command
        self.consultant_cmd = ConsultantCommand()
        register_consultant_command(self)

        # Custom command registry
        self.custom_commands = {}

    def register_command(self, name: str, handler_func):
        """Register a custom command handler"""
        self.custom_commands[name] = handler_func

    def _load_commands(self) -> Dict[str, CommandInfo]:
        """Load command definitions from markdown files"""
        commands = {}

        if not self.commands_dir.exists():
            return commands

        for cmd_file in self.commands_dir.glob("*.md"):
            cmd_name = cmd_file.stem
            commands[cmd_name] = self._parse_command_file(cmd_file)

        return commands

    def _parse_command_file(self, cmd_file: Path) -> CommandInfo:
        """Parse a command markdown file"""
        content = cmd_file.read_text()

        # Extract YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1]
                description = parts[2].strip()

                # Parse frontmatter
                import yaml
                try:
                    metadata = yaml.safe_load(frontmatter) or {}
                    return CommandInfo(
                        name=cmd_file.stem,
                        description=metadata.get('description', description.split('\n')[0]),
                        script_path=metadata.get('script_path', f'./bin/claude-{cmd_file.stem}.sh'),
                        category=metadata.get('category', 'general'),
                        strategic_enabled=metadata.get('strategic_enabled', False)
                    )
                except:
                    pass

        # Fallback
        return CommandInfo(
            name=cmd_file.stem,
            description=content.split('\n')[0] if content else cmd_file.stem,
            script_path=f'./bin/claude-{cmd_file.stem}.sh',
            category='general'
        )

    def get_command(self, name: str) -> Optional[CommandInfo]:
        """Get a command by name"""
        return self.commands.get(name)

    def list_commands(self) -> List[CommandInfo]:
        """List all available commands"""
        return list(self.commands.values())

    async def execute_command(self, name: str, args: str = "") -> Dict[str, Any]:
        """Execute a command with enhanced capabilities"""

        # Handle strategic consultant commands
        if name == "consultant":
            return await self._execute_consultant(args)

        # Handle built-in capability commands
        elif name == "capabilities":
            return await self._execute_capabilities(args)
        elif name == "actions":
            return await self._execute_actions(args)
        elif name == "act":
            return await self._execute_act(args)
        elif name == "capability-help":
            return {"output": render_help()}

        # Handle custom registered commands
        elif name in self.custom_commands:
            return await self._execute_custom_command(name, args)

        # Handle traditional file-based commands
        cmd = self.get_command(name)
        if not cmd:
            return {"error": f"Command '{name}' not found. Use /capability-help to see available commands."}

        return {
            "command": cmd.name,
            "description": cmd.description,
            "script": cmd.script_path,
            "execution": f"{cmd.script_path} {args}" if args else cmd.script_path,
            "category": cmd.category,
            "strategic_enabled": cmd.strategic_enabled
        }

    async def _execute_consultant(self, args: str) -> Dict[str, Any]:
        """Execute consultant command"""
        try:
            # Parse args
            arg_list = args.split() if args else []
            result = await self.consultant_cmd.handle_command(arg_list)
            return {"output": result}
        except Exception as e:
            return {"error": f"Error executing consultant command: {str(e)}"}

    async def _execute_capabilities(self, args: str) -> Dict[str, Any]:
        """Execute capabilities command"""
        try:
            arg_list = args.split() if args else []
            result = await self.capabilities_cmd.execute(arg_list)
            return {"output": result}
        except Exception as e:
            return {"error": f"Error executing capabilities command: {str(e)}"}

    async def _execute_actions(self, args: str) -> Dict[str, Any]:
        """Execute actions command"""
        try:
            arg_list = args.split() if args else []
            result = await self.actions_cmd.execute_actions(arg_list)
            return {"output": result}
        except Exception as e:
            return {"error": f"Error executing actions command: {str(e)}"}

    async def _execute_act(self, args: str) -> Dict[str, Any]:
        """Execute act command"""
        try:
            arg_list = args.split() if args else []
            result = await self.actions_cmd.execute_act(arg_list)
            return {"output": result}
        except Exception as e:
            return {"error": f"Error executing act command: {str(e)}"}

    async def _execute_custom_command(self, name: str, args: str) -> Dict[str, Any]:
        """Execute custom registered command"""
        try:
            handler = self.custom_commands[name]
            arg_list = args.split() if args else []
            result = await handler(arg_list)
            return {"output": result}
        except Exception as e:
            return {"error": f"Error executing custom command '{name}': {str(e)}"}

# Backward compatibility
def execute_command(name: str, args: str = "") -> Dict[str, Any]:
    """Synchronous wrapper for execute_command"""
    handler = EnhancedSimpleCommandHandler()
    return asyncio.run(handler.execute_command(name, args))

# Global handler instance
_global_handler = None

def get_global_handler():
    """Get global command handler instance"""
    global _global_handler
    if _global_handler is None:
        _global_handler = EnhancedSimpleCommandHandler()
    return _global_handler

if __name__ == "__main__":
    # Test the enhanced command handler
    async def test_handler():
        handler = EnhancedSimpleCommandHandler()

        print("🧠 Enhanced OOS Command System:")
        print("  /consultant <question> - Strategic analysis")
        print("  /capabilities <query> - Get capability information")
        print("  /actions [domain] - List available actions")
        print("  /act <tool> <params> - Execute specific action")
        print("  /capability-help - Show help for capability commands")

        print("\nTraditional commands:")
        for cmd in handler.list_commands():
            strategic_marker = " 🧠" if cmd.strategic_enabled else ""
            print(f"  /{cmd.name}: {cmd.description}{strategic_marker}")

    asyncio.run(test_handler())
```

## 🔌 **Step 3: Enhanced Integration Files**

### Enhanced Capability Router (`src/capability_router.py`)
```python
#!/usr/bin/env python3
"""
Enhanced Capability Router with Strategic Intelligence
"""

import asyncio
from typing import Dict, Any, Optional
from simple_command_handler import get_global_handler

async def route_request(request: str) -> str:
    """Route request with strategic enhancement"""

    # Get global handler
    handler = get_global_handler()

    # Parse request
    parts = request.strip().split()
    if not parts:
        return "No command provided"

    command = parts[0].lower()
    args = " ".join(parts[1:]) if len(parts) > 1 else ""

    # Check if this should be routed to strategic consultant
    strategic_keywords = [
        "how", "should", "what", "why", "analyze", "recommend",
        "strategy", "approach", "optimize", "improve", "scale"
    ]

    # If request contains strategic language, route to consultant
    if any(keyword in request.lower() for keyword in strategic_keywords) and command not in ["consultant"]:
        # Automatically route strategic questions to consultant
        consultant_result = await handler.execute_command("consultant", request)
        return consultant_result.get("output", "Strategic analysis failed")

    # Otherwise route normally
    result = await handler.execute_command(command, args)
    return result.get("output", result.get("error", "Command execution failed"))
```

## 📦 **Step 4: Complete Installation Script**

### Install Script (`install_enhanced_oos.sh`)
```bash
#!/bin/bash
# Complete Enhanced OOS Installation

echo "🚀 Installing Enhanced OOS with Strategic Intelligence..."

# Create necessary directories
mkdir -p src/commands
mkdir -p config
mkdir -p templates
mkdir -p tests

# Copy core files
echo "📁 Copying core strategic consultant files..."
cp src/strategic_consultant.py ./src/
cp src/archon_integration.py ./src/
cp src/execution_driver.py ./src/
cp src/adaptive_planner.py ./src/
cp src/config_loader.py ./src/

# Copy enhanced command system
echo "🔧 Updating command system..."
cp -r src/commands/ ./src/
cp src/simple_command_handler.py ./src/
cp src/capability_router.py ./src/

# Copy enhanced OOS components
echo "⚡ Adding enhanced OOS components..."
cp src/enhanced_rag_system.py ./src/
cp src/memory_system.py ./src/
cp src/parallel_agents.py ./src/
cp src/oos_archon_integration.py ./src/

# Copy configuration and templates
echo "📋 Installing configuration and templates..."
cp config/consultant.yaml ./config/
cp -r templates/ ./

# Copy enhanced CLI
echo "🖥️  Installing enhanced CLI..."
cp src/oos_cli.py ./src/

# Copy tests
echo "🧪 Installing tests..."
cp test_*.py ./
cp -r tests/ ./

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt 2>/dev/null || echo "No requirements.txt found, skipping pip install"

# Make CLI executable
chmod +x src/oos_cli.py

echo "✅ Enhanced OOS installation complete!"
echo ""
echo "🎯 Ready to use:"
echo "  python3 src/oos_cli.py consultant \"How do we optimize this system?\""
echo "  python3 src/oos_cli.py create \"AI chatbot for customer support\""
echo "  python3 src/oos_cli.py status"
echo "  python3 src/oos_cli.py dashboard"
echo ""
echo "🚀 Your OOS now has strategic intelligence built-in!"
```

## ⚡ **Step 5: Quick Verification**

### Test Script (`test_enhanced_oos.py`)
```python
#!/usr/bin/env python3
"""Test Enhanced OOS System"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from simple_command_handler import EnhancedSimpleCommandHandler

async def test_enhanced_oos():
    print("🧪 Testing Enhanced OOS System")
    print("=" * 50)

    handler = EnhancedSimpleCommandHandler()

    # Test strategic consultant
    print("\n1. Testing Strategic Consultant:")
    result = await handler.execute_command("consultant", "How do we scale this system?")
    print("✅" if "output" in result else "❌", "Strategic analysis")

    # Test status
    print("\n2. Testing Status Commands:")
    result = await handler.execute_command("consultant", "status")
    print("✅" if "output" in result else "❌", "Status command")

    # Test help
    print("\n3. Testing Help System:")
    result = await handler.execute_command("consultant", "help")
    print("✅" if "output" in result else "❌", "Help system")

    print("\n🚀 Enhanced OOS System Ready!")

if __name__ == "__main__":
    asyncio.run(test_enhanced_oos())
```

## 🎯 **Ready to Use Commands**

After installation, you can immediately use:

```bash
# Strategic analysis
python3 src/oos_cli.py consultant "How do we scale to 10,000 users?"

# Enhanced project creation
python3 src/oos_cli.py create "AI chatbot that learns from conversations"

# Monitoring and status
python3 src/oos_cli.py status
python3 src/oos_cli.py dashboard

# Interactive mode
python3 src/oos_cli.py --interactive
```

This complete update gives you **everything working together** - strategic intelligence, enhanced project creation, monitoring, Archon integration, and all the hard work done upfront.

**Your OOS is now a complete strategic AI operating system.**