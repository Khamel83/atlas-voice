#!/usr/bin/env python3
"""
OOS Self-Documentation System
Automated documentation generation with git integration
"""

import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3
import markdown
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

class SelfDocumentation:
    """Self-documentation system for OOS"""

    def __init__(self, db_path: str = "~/.oos/oos.db"):
        self.db_path = Path(db_path).expanduser()
        self.conn = None
        self.initialize_database()

    def initialize_database(self):
        """Initialize documentation database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS documentation_entries (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                session_id TEXT,
                doc_type TEXT,
                content TEXT,
                metadata TEXT,
                git_commit TEXT,
                file_path TEXT
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS project_snapshots (
                id TEXT PRIMARY KEY,
                timestamp REAL,
                project_path TEXT,
                file_count INTEGER,
                total_size INTEGER,
                structure TEXT,
                dependencies TEXT
            )
        ''')

        self.conn.commit()

    def generate_session_documentation(self, session_id: str) -> Dict[str, Any]:
        """Generate documentation for a development session"""
        console.print(f"[bold blue]📝 Generating documentation for session {session_id}[/bold blue]")

        # Get session context
        session_context = self._get_session_context(session_id)

        # Generate session summary
        session_summary = self._generate_session_summary(session_id, session_context)

        # Generate file documentation
        file_docs = self._generate_file_documentation(session_id)

        # Generate git documentation
        git_docs = self._generate_git_documentation()

        # Compile complete documentation
        complete_doc = {
            "session_id": session_id,
            "timestamp": time.time(),
            "summary": session_summary,
            "files": file_docs,
            "git": git_docs,
            "metadata": {
                "generated_by": "OOS",
                "version": "1.0.0",
                "auto_generated": True
            }
        }

        # Store documentation
        self._store_documentation(session_id, complete_doc)

        return complete_doc

    def _get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get context for a session"""
        cursor = self.conn.execute('''
            SELECT * FROM context_entries
            WHERE session_id = ?
            ORDER BY timestamp ASC
        ''', (session_id,))

        context_entries = []
        for row in cursor.fetchall():
            context_entries.append({
                "id": row[0],
                "timestamp": row[1],
                "context_type": row[3],
                "content": json.loads(row[4]),
                "metadata": json.loads(row[5]),
                "confidence_score": row[6]
            })

        return {
            "session_id": session_id,
            "entries": context_entries,
            "entry_count": len(context_entries)
        }

    def _generate_session_summary(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate session summary"""
        # Analyze session activities
        activities = {}
        for entry in context["entries"]:
            activity_type = entry["context_type"]
            activities[activity_type] = activities.get(activity_type, 0) + 1

        # Determine session type
        session_type = self._determine_session_type(activities)

        # Calculate session duration
        if context["entries"]:
            start_time = min(entry["timestamp"] for entry in context["entries"])
            end_time = max(entry["timestamp"] for entry in context["entries"])
            duration = end_time - start_time
        else:
            duration = 0

        return {
            "session_type": session_type,
            "duration_seconds": duration,
            "activities": activities,
            "total_entries": context["entry_count"],
            "confidence_score": self._calculate_session_confidence(context)
        }

    def _determine_session_type(self, activities: Dict[str, int]) -> str:
        """Determine the type of development session"""
        if activities.get("request", 0) > activities.get("response", 0):
            return "development"
        elif activities.get("optimization", 0) > 0:
            return "optimization"
        elif activities.get("clarification", 0) > 0:
            return "planning"
        else:
            return "general"

    def _calculate_session_confidence(self, context: Dict[str, Any]) -> float:
        """Calculate confidence score for the session"""
        if not context["entries"]:
            return 0.0

        total_confidence = sum(entry["confidence_score"] for entry in context["entries"])
        return total_confidence / len(context["entries"])

    def _generate_file_documentation(self, session_id: str) -> List[Dict[str, Any]]:
        """Generate documentation for files touched in session"""
        file_docs = []

        # Get current directory files
        current_dir = Path.cwd()
        for file_path in current_dir.rglob("*"):
            if file_path.is_file() and self._is_relevant_file(file_path):
                file_doc = self._document_file(file_path)
                if file_doc:
                    file_docs.append(file_doc)

        return file_docs

    def _is_relevant_file(self, file_path: Path) -> bool:
        """Check if file is relevant for documentation"""
        relevant_extensions = {'.py', '.js', '.ts', '.json', '.md', '.txt', '.yml', '.yaml'}
        excluded_dirs = {'.git', 'node_modules', '__pycache__', '.venv'}

        # Check extension
        if file_path.suffix.lower() not in relevant_extensions:
            return False

        # Check if in excluded directory
        for part in file_path.parts:
            if part in excluded_dirs:
                return False

        return True

    def _document_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Generate documentation for a single file"""
        try:
            stat = file_path.stat()

            # Basic file information
            file_doc = {
                "path": str(file_path),
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": file_path.suffix.lower(),
                "type": self._get_file_type(file_path)
            }

            # Add content analysis for code files
            if file_path.suffix.lower() in {'.py', '.js', '.ts'}:
                file_doc.update(self._analyze_code_file(file_path))

            return file_doc

        except Exception as e:
            console.print(f"[yellow]Warning: Could not document {file_path}: {e}[/yellow]")
            return None

    def _get_file_type(self, file_path: Path) -> str:
        """Determine file type"""
        ext = file_path.suffix.lower()
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.json': 'json',
            '.md': 'markdown',
            '.txt': 'text',
            '.yml': 'yaml',
            '.yaml': 'yaml'
        }
        return type_map.get(ext, 'unknown')

    def _analyze_code_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a code file for documentation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            # Count lines of code (non-empty, non-comment lines)
            loc = 0
            comment_lines = 0
            for line in lines:
                stripped = line.strip()
                if stripped:
                    if stripped.startswith('#') or stripped.startswith('//'):
                        comment_lines += 1
                    else:
                        loc += 1

            # Count functions/classes
            function_count = content.count('def ') if file_path.suffix == '.py' else content.count('function ')
            class_count = content.count('class ')

            return {
                "lines_of_code": loc,
                "comment_lines": comment_lines,
                "function_count": function_count,
                "class_count": class_count,
                "total_lines": len(lines)
            }

        except Exception as e:
            return {"error": str(e)}

    def _generate_git_documentation(self) -> Dict[str, Any]:
        """Generate git-related documentation"""
        git_doc = {
            "repository_available": False,
            "current_branch": None,
            "recent_commits": [],
            "working_tree_clean": True
        }

        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                git_doc["repository_available"] = True

                # Get current branch
                branch_result = subprocess.run(['git', 'branch', '--show-current'],
                                             capture_output=True, text=True, timeout=5)
                if branch_result.returncode == 0:
                    git_doc["current_branch"] = branch_result.stdout.strip()

                # Get recent commits
                log_result = subprocess.run(['git', 'log', '--oneline', '-10'],
                                          capture_output=True, text=True, timeout=5)
                if log_result.returncode == 0:
                    git_doc["recent_commits"] = log_result.stdout.strip().split('\n')

                # Check working tree status
                status_result = subprocess.run(['git', 'status', '--porcelain'],
                                             capture_output=True, text=True, timeout=5)
                if status_result.returncode == 0:
                    git_doc["working_tree_clean"] = len(status_result.stdout.strip()) == 0

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return git_doc

    def _store_documentation(self, session_id: str, documentation: Dict[str, Any]):
        """Store documentation in database"""
        doc_id = f"doc_{session_id}_{int(time.time())}"

        metadata = {
            "generated_at": time.time(),
            "session_id": session_id,
            "doc_type": "session_summary"
        }

        # Get current git commit if available
        git_commit = None
        try:
            result = subprocess.run(['git', 'rev-parse', 'HEAD'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                git_commit = result.stdout.strip()
        except:
            pass

        self.conn.execute('''
            INSERT INTO documentation_entries VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            time.time(),
            session_id,
            "session_summary",
            json.dumps(documentation),
            json.dumps(metadata),
            git_commit,
            None
        ))

        self.conn.commit()

    def generate_project_documentation(self, project_path: str = None) -> Dict[str, Any]:
        """Generate comprehensive project documentation"""
        project_path = Path(project_path) if project_path else Path.cwd()

        console.print(f"[bold green]📚 Generating project documentation for {project_path}[/bold green]")

        # Take project snapshot
        snapshot = self._take_project_snapshot(project_path)

        # Generate project overview
        overview = self._generate_project_overview(project_path)

        # Generate API documentation
        api_docs = self._generate_api_documentation(project_path)

        # Generate setup instructions
        setup_docs = self._generate_setup_instructions(project_path)

        # Compile complete project documentation
        project_doc = {
            "project_path": str(project_path),
            "timestamp": time.time(),
            "snapshot": snapshot,
            "overview": overview,
            "api_documentation": api_docs,
            "setup_instructions": setup_docs,
            "generated_by": "OOS Self-Documentation"
        }

        return project_doc

    def _take_project_snapshot(self, project_path: Path) -> Dict[str, Any]:
        """Take a snapshot of the project state"""
        # Count files and sizes
        file_count = 0
        total_size = 0
        file_types = {}

        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                file_count += 1
                total_size += file_path.stat().st_size
                ext = file_path.suffix.lower()
                file_types[ext] = file_types.get(ext, 0) + 1

        # Get project structure
        structure = self._get_project_structure(project_path)

        # Get dependencies
        dependencies = self._get_project_dependencies(project_path)

        snapshot = {
            "file_count": file_count,
            "total_size": total_size,
            "file_types": file_types,
            "structure": structure,
            "dependencies": dependencies,
            "timestamp": time.time()
        }

        # Store snapshot
        self._store_project_snapshot(project_path, snapshot)

        return snapshot

    def _get_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Get project directory structure"""
        structure = {}

        for item in project_path.iterdir():
            if item.name.startswith('.'):
                continue

            if item.is_dir():
                structure[item.name] = {
                    "type": "directory",
                    "children": self._get_directory_contents(item)
                }
            elif item.is_file():
                structure[item.name] = {
                    "type": "file",
                    "size": item.stat().st_size
                }

        return structure

    def _get_directory_contents(self, directory: Path) -> Dict[str, Any]:
        """Get contents of a directory"""
        contents = {}

        try:
            for item in directory.iterdir():
                if item.name.startswith('.'):
                    continue

                if item.is_dir():
                    contents[item.name] = {
                        "type": "directory",
                        "item_count": len(list(item.iterdir()))
                    }
                elif item.is_file():
                    contents[item.name] = {
                        "type": "file",
                        "size": item.stat().st_size
                    }
        except PermissionError:
            pass

        return contents

    def _get_project_dependencies(self, project_path: Path) -> Dict[str, Any]:
        """Get project dependencies"""
        dependencies = {}

        # Python dependencies
        if (project_path / "requirements.txt").exists():
            try:
                with open(project_path / "requirements.txt") as f:
                    deps = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    dependencies["python"] = deps
            except:
                pass

        # Node.js dependencies
        if (project_path / "package.json").exists():
            try:
                with open(project_path / "package.json") as f:
                    pkg = json.load(f)
                    dependencies["nodejs"] = {
                        "dependencies": pkg.get("dependencies", {}),
                        "devDependencies": pkg.get("devDependencies", {})
                    }
            except:
                pass

        return dependencies

    def _store_project_snapshot(self, project_path: Path, snapshot: Dict[str, Any]):
        """Store project snapshot in database"""
        snapshot_id = f"snapshot_{int(time.time())}"

        self.conn.execute('''
            INSERT INTO project_snapshots VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            snapshot_id,
            time.time(),
            str(project_path),
            snapshot["file_count"],
            snapshot["total_size"],
            json.dumps(snapshot["structure"]),
            json.dumps(snapshot["dependencies"])
        ))

        self.conn.commit()

    def _generate_project_overview(self, project_path: Path) -> Dict[str, Any]:
        """Generate project overview"""
        return {
            "name": project_path.name,
            "description": self._extract_project_description(project_path),
            "type": self._detect_project_type(project_path),
            "technologies": self._detect_technologies(project_path),
            "features": self._extract_features(project_path)
        }

    def _extract_project_description(self, project_path: Path) -> str:
        """Extract project description from README or other files"""
        readme_path = project_path / "README.md"
        if readme_path.exists():
            try:
                with open(readme_path) as f:
                    lines = f.readlines()
                    # Get first non-empty, non-heading line
                    for line in lines[1:10]:  # Look in first 10 lines
                        line = line.strip()
                        if line and not line.startswith('#'):
                            return line
            except:
                pass

        return "Auto-generated project documentation"

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect project type"""
        if (project_path / "package.json").exists():
            return "Node.js Application"
        elif (project_path / "requirements.txt").exists() or (project_path / "setup.py").exists():
            return "Python Application"
        elif (project_path / "Cargo.toml").exists():
            return "Rust Application"
        elif (project_path / "go.mod").exists():
            return "Go Application"
        else:
            return "Generic Project"

    def _detect_technologies(self, project_path: Path) -> List[str]:
        """Detect technologies used in project"""
        technologies = []

        # Check for common technology indicators
        tech_indicators = {
            "react": ["package.json", "node_modules"],
            "vue": ["package.json", "node_modules"],
            "django": ["requirements.txt", "manage.py"],
            "flask": ["requirements.txt", "app.py"],
            "express": ["package.json", "node_modules"],
            "fastapi": ["requirements.txt", "main.py"]
        }

        for tech, indicators in tech_indicators.items():
            if any((project_path / indicator).exists() for indicator in indicators):
                technologies.append(tech)

        return technologies

    def _extract_features(self, project_path: Path) -> List[str]:
        """Extract project features from code analysis"""
        features = []

        # Look for common feature patterns
        feature_patterns = {
            "authentication": ["auth", "login", "user"],
            "database": ["database", "db", "sql"],
            "api": ["api", "rest", "endpoint"],
            "web_interface": ["html", "css", "templates"],
            "testing": ["test", "spec", "pytest"],
            "documentation": ["docs", "readme", "markdown"]
        }

        # Simple pattern matching (could be improved with actual code analysis)
        for feature, patterns in feature_patterns.items():
            if any(pattern in project_path.name.lower() for pattern in patterns):
                features.append(feature)

        return features

    def _generate_api_documentation(self, project_path: Path) -> Dict[str, Any]:
        """Generate API documentation"""
        # Mock API documentation
        return {
            "endpoints": [],
            "schemas": {},
            "authentication": "Not documented",
            "note": "API documentation requires manual annotation"
        }

    def _generate_setup_instructions(self, project_path: Path) -> Dict[str, Any]:
        """Generate setup instructions"""
        instructions = []

        # Detect project type and generate appropriate instructions
        if (project_path / "requirements.txt").exists():
            instructions.append({
                "step": 1,
                "title": "Install Python dependencies",
                "command": "pip install -r requirements.txt"
            })

        if (project_path / "package.json").exists():
            instructions.append({
                "step": 2,
                "title": "Install Node.js dependencies",
                "command": "npm install"
            })

        instructions.append({
            "step": len(instructions) + 1,
            "title": "Run the application",
            "command": "python main.py" if (project_path / "main.py").exists() else "npm start"
        })

        return {
            "prerequisites": ["Python 3.8+", "Node.js 14+"],
            "installation_steps": instructions,
            "configuration": "See config files for environment variables"
        }

    def export_documentation(self, documentation: Dict[str, Any], output_path: str) -> bool:
        """Export documentation to file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if output_path.suffix.lower() == '.md':
                # Export as Markdown
                self._export_markdown(documentation, output_path)
            elif output_path.suffix.lower() == '.json':
                # Export as JSON
                with open(output_path, 'w') as f:
                    json.dump(documentation, f, indent=2)
            else:
                # Default to JSON
                with open(output_path.with_suffix('.json'), 'w') as f:
                    json.dump(documentation, f, indent=2)

            console.print(f"[green]✓ Documentation exported to {output_path}[/green]")
            return True

        except Exception as e:
            console.print(f"[red]❌ Failed to export documentation: {e}[/red]")
            return False

    def _export_markdown(self, documentation: Dict[str, Any], output_path: Path):
        """Export documentation as Markdown"""
        md_content = f"""# OOS Generated Documentation

*Generated by OOS Self-Documentation System*
*Generated at: {datetime.fromtimestamp(documentation.get('timestamp', time.time()))}*

## Session Information

- **Session ID**: {documentation.get('session_id', 'Unknown')}
- **Session Type**: {documentation.get('summary', {}).get('session_type', 'Unknown')}
- **Duration**: {documentation.get('summary', {}).get('duration_seconds', 0)} seconds

## Activities

"""

        # Add activities
        activities = documentation.get('summary', {}).get('activities', {})
        for activity, count in activities.items():
            md_content += f"- **{activity}**: {count} occurrences\n"

        md_content += "\n## Files\n\n"

        # Add file documentation
        files = documentation.get('files', [])
        for file_doc in files:
            md_content += f"### {file_doc.get('path', 'Unknown')}\n\n"
            md_content += f"- **Type**: {file_doc.get('type', 'Unknown')}\n"
            md_content += f"- **Size**: {file_doc.get('size', 0)} bytes\n"
            if 'lines_of_code' in file_doc:
                md_content += f"- **Lines of Code**: {file_doc['lines_of_code']}\n"
            md_content += "\n"

        # Add git information
        git_info = documentation.get('git', {})
        if git_info.get('repository_available'):
            md_content += "## Git Information\n\n"
            md_content += f"- **Branch**: {git_info.get('current_branch', 'Unknown')}\n"
            md_content += f"- **Working Tree**: {'Clean' if git_info.get('working_tree_clean') else 'Dirty'}\n"
            md_content += "\n"

        with open(output_path, 'w') as f:
            f.write(md_content)

    def get_documentation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get documentation generation history"""
        cursor = self.conn.execute('''
            SELECT * FROM documentation_entries
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        history = []
        for row in cursor.fetchall():
            history.append({
                "id": row[0],
                "timestamp": row[1],
                "session_id": row[2],
                "doc_type": row[3],
                "git_commit": row[6]
            })

        return history

    def display_documentation(self, documentation: Dict[str, Any]):
        """Display documentation in a formatted way"""
        console.print(Panel.fit(
            f"[bold green]OOS Generated Documentation[/bold green]\n"
            f"Session: {documentation.get('session_id', 'Unknown')}\n"
            f"Generated: {datetime.fromtimestamp(documentation.get('timestamp', time.time()))}",
            title="Documentation"
        ))

        # Display session summary
        summary = documentation.get('summary', {})
        if summary:
            console.print("\n[bold cyan]Session Summary[/bold cyan]")
            console.print(f"Type: {summary.get('session_type', 'Unknown')}")
            console.print(f"Duration: {summary.get('duration_seconds', 0)} seconds")
            console.print(f"Entries: {summary.get('total_entries', 0)}")

        # Display activities
        activities = summary.get('activities', {})
        if activities:
            console.print("\n[bold yellow]Activities[/bold yellow]")
            for activity, count in activities.items():
                console.print(f"  {activity}: {count}")

        # Display files
        files = documentation.get('files', [])
        if files:
            console.print(f"\n[bold magenta]Files Documented ({len(files)})[/bold magenta]")
            table = Table()
            table.add_column("File", style="cyan")
            table.add_column("Type", style="white")
            table.add_column("Size", style="green")

            for file_doc in files[:10]:  # Show first 10 files
                table.add_row(
                    file_doc.get('path', 'Unknown')[-30:],  # Truncate long paths
                    file_doc.get('type', 'Unknown'),
                    f"{file_doc.get('size', 0)} bytes"
                )

            console.print(table)

            if len(files) > 10:
                console.print(f"[dim]... and {len(files) - 10} more files[/dim]")

        # Display git info
        git_info = documentation.get('git', {})
        if git_info.get('repository_available'):
            console.print(f"\n[bold blue]Git Information[/bold blue]")
            console.print(f"Branch: {git_info.get('current_branch', 'Unknown')}")
            console.print(f"Working Tree: {'✓ Clean' if git_info.get('working_tree_clean') else '⚠️  Dirty'}")

            recent_commits = git_info.get('recent_commits', [])
            if recent_commits and recent_commits != ['']:
                console.print("Recent Commits:")
                for commit in recent_commits[:3]:
                    console.print(f"  • {commit}")

# CLI Integration
@click.group()
def docs_cli():
    """OOS Self-Documentation CLI"""
    pass

@docs_cli.command()
@click.option('--session-id', '-s', help='Session ID to document')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'markdown']), default='json', help='Output format')
def session(session_id, output, format):
    """Generate documentation for a session"""
    doc_system = SelfDocumentation()

    if not session_id:
        # Get most recent session
        cursor = doc_system.conn.execute('''
            SELECT DISTINCT session_id FROM context_entries
            ORDER BY timestamp DESC
            LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            session_id = result[0]
        else:
            console.print("[red]❌ No sessions found[/red]")
            return

    documentation = doc_system.generate_session_documentation(session_id)

    if output:
        doc_system.export_documentation(documentation, output)
    else:
        doc_system.display_documentation(documentation)

@docs_cli.command()
@click.option('--project-path', '-p', help='Project path')
@click.option('--output', '-o', help='Output file path')
@click.option('--format', '-f', type=click.Choice(['json', 'markdown']), default='json', help='Output format')
def project(project_path, output, format):
    """Generate project documentation"""
    doc_system = SelfDocumentation()
    documentation = doc_system.generate_project_documentation(project_path)

    if output:
        doc_system.export_documentation(documentation, output)
    else:
        doc_system.display_documentation(documentation)

@docs_cli.command()
@click.option('--limit', '-l', default=10, help='Number of entries to show')
def history(limit):
    """Show documentation history"""
    doc_system = SelfDocumentation()
    history = doc_system.get_documentation_history(limit)

    console.print(f"[bold cyan]Documentation History (Last {limit})[/bold cyan]")

    table = Table()
    table.add_column("Timestamp", style="cyan")
    table.add_column("Session ID", style="white")
    table.add_column("Type", style="green")
    table.add_column("Git Commit", style="magenta")

    for entry in history:
        timestamp = datetime.fromtimestamp(entry['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        table.add_row(
            timestamp,
            entry['session_id'][:20] + '...' if len(entry['session_id']) > 20 else entry['session_id'],
            entry['doc_type'],
            entry['git_commit'][:8] if entry['git_commit'] else 'N/A'
        )

    console.print(table)

if __name__ == "__main__":
    docs_cli()
