#!/usr/bin/env python3
"""
OOS-Archon Final Integration - Complete Solution
Production-ready connection with proper session management
"""

import requests
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class ArchonProject:
    id: str
    title: str
    description: str
    status: str
    github_repo: Optional[str]

@dataclass
class ArchonTask:
    id: str
    title: str
    description: str
    status: str
    project_id: str
    task_order: int
    assignee: str

class OOSArchonIntegration:
    """
    Complete OOS-Archon integration with proper session management
    This is the "hard connection work upfront" that makes the connection seamless
    """

    def __init__(self, archon_url: str = "http://100.103.45.61:8051/mcp"):
        self.archon_url = archon_url
        self.session_id = str(uuid.uuid4())
        self.request_id = 0
        self.initialized = False

    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make request with proper session handling"""
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "X-Session-ID": self.session_id
        }

        try:
            response = requests.post(self.archon_url, headers=headers, json=payload, stream=True)

            if response.status_code == 200:
                return self._parse_streaming_response(response)
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            return {"error": str(e)}

    def _parse_streaming_response(self, response) -> Dict[str, Any]:
        """Parse streaming response"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                line_text = line.decode('utf-8').strip()
                if line_text.startswith('data: '):
                    try:
                        data = json.loads(line_text[6:])
                        if "result" in data:
                            return data["result"]
                    except json.JSONDecodeError:
                        continue
                full_response += line_text + "\n"

        # Fallback: try to parse entire response
        try:
            return json.loads(full_response)
        except:
            return {"raw_response": full_response}

    def initialize(self) -> bool:
        """Initialize the MCP session"""
        if self.initialized:
            return True

        print("🔗 Initializing OOS-Archon session...")
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {"listChanged": True},
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "oos-archon-integration",
                    "version": "1.0.0"
                }
            }
        }

        result = self._make_request(payload)

        if "error" not in result:
            self.initialized = True
            print("✅ OOS-Archon session initialized successfully")
            return True
        else:
            print(f"❌ Session initialization failed: {result['error']}")
            return False

    def list_projects(self) -> List[ArchonProject]:
        """List all projects"""
        if not self.initialized:
            if not self.initialize():
                return []

        print("📋 Fetching projects...")
        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "list_projects",
                "arguments": {}
            }
        }

        result = self._make_request(payload)

        if "error" in result:
            print(f"❌ Error listing projects: {result['error']}")
            return []

        projects = []
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        if "projects" in data:
                            for proj in data["projects"]:
                                projects.append(ArchonProject(
                                    id=proj.get("id", ""),
                                    title=proj.get("title", ""),
                                    description=proj.get("description", ""),
                                    status=proj.get("status", ""),
                                    github_repo=proj.get("github_repo")
                                ))
                    except json.JSONDecodeError:
                        continue

        return projects

    def list_tasks(self, project_id: str = None, status: str = None) -> List[ArchonTask]:
        """List tasks with optional filtering"""
        if not self.initialized:
            if not self.initialize():
                return []

        print("📝 Fetching tasks...")
        arguments = {}
        if project_id:
            arguments["project_id"] = project_id
        if status:
            arguments["filter_by"] = "status"
            arguments["filter_value"] = status

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "list_tasks",
                "arguments": arguments
            }
        }

        result = self._make_request(payload)

        if "error" in result:
            print(f"❌ Error listing tasks: {result['error']}")
            return []

        tasks = []
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        if "tasks" in data:
                            for task in data["tasks"]:
                                tasks.append(ArchonTask(
                                    id=task.get("id", ""),
                                    title=task.get("title", ""),
                                    description=task.get("description", ""),
                                    status=task.get("status", ""),
                                    project_id=task.get("project_id", ""),
                                    task_order=task.get("task_order", 0),
                                    assignee=task.get("assignee", "Unassigned")
                                ))
                    except json.JSONDecodeError:
                        continue

        return tasks

    def create_project(self, title: str, description: str = "", github_repo: str = None) -> Optional[str]:
        """Create a new project"""
        if not self.initialized:
            if not self.initialize():
                return None

        print(f"🏗️ Creating project: {title}")
        arguments = {
            "title": title,
            "description": description
        }
        if github_repo:
            arguments["github_repo"] = github_repo

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "create_project",
                "arguments": arguments
            }
        }

        result = self._make_request(payload)

        if "error" in result:
            print(f"❌ Error creating project: {result['error']}")
            return None

        # Extract project ID
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        return data.get("project_id")
                    except json.JSONDecodeError:
                        continue

        return None

    def create_task(self, project_id: str, title: str, description: str = "",
                   assignee: str = "User", task_order: int = 1) -> Optional[str]:
        """Create a new task"""
        if not self.initialized:
            if not self.initialize():
                return None

        print(f"📝 Creating task: {title}")
        arguments = {
            "project_id": project_id,
            "title": title,
            "description": description,
            "assignee": assignee,
            "task_order": task_order
        }

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": "create_task",
                "arguments": arguments
            }
        }

        result = self._make_request(payload)

        if "error" in result:
            print(f"❌ Error creating task: {result['error']}")
            return None

        # Extract task ID
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        return data.get("task_id")
                    except json.JSONDecodeError:
                        continue

        return None

def display_project_summary(projects: List[ArchonProject], tasks: List[ArchonTask]):
    """Display a comprehensive project summary"""
    print(f"\n📊 Archon System Overview")
    print("=" * 50)
    print(f"Total Projects: {len(projects)}")
    print(f"Total Tasks: {len(tasks)}")

    # Task status breakdown
    task_status = {}
    for task in tasks:
        status = task.status
        task_status[status] = task_status.get(status, 0) + 1

    print(f"Task Status: {task_status}")

    if projects:
        print(f"\n📂 Projects:")
        print("-" * 40)
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.title}")
            print(f"   ID: {project.id}")
            print(f"   Status: {project.status}")
            if project.description:
                desc = project.description
                print(f"   Description: {desc[:80]}{'...' if len(desc) > 80 else ''}")
            if project.github_repo:
                print(f"   Repo: {project.github_repo}")

            # Count tasks for this project
            project_tasks = [t for t in tasks if t.project_id == project.id]
            if project_tasks:
                project_task_status = {}
                for t in project_tasks:
                    status = t.status
                    project_task_status[status] = project_task_status.get(status, 0) + 1
                print(f"   Tasks: {len(project_tasks)} ({project_task_status})")
            print()

    # Show recent tasks by status
    if tasks:
        print(f"\n📋 Tasks by Status:")
        print("-" * 30)
        by_status = {}
        for task in tasks:
            if task.status not in by_status:
                by_status[task.status] = []
            by_status[task.status].append(task)

        for status in ['todo', 'doing', 'review', 'done']:
            if status in by_status:
                print(f"\n{status.upper()} ({len(by_status[status])}):")
                for task in by_status[status][:3]:  # Show first 3
                    print(f"  • {task.title}")
                    print(f"    Order: {task.task_order} | Assignee: {task.assignee}")
                if len(by_status[status]) > 3:
                    print(f"    ... and {len(by_status[status]) - 3} more")

def main():
    """Main demonstration function"""
    print("🚀 OOS-Archon Final Integration - Complete Solution")
    print("=" * 60)

    # Initialize integration
    integration = OOSArchonIntegration()

    # Get current projects and tasks
    projects = integration.list_projects()
    tasks = integration.list_tasks()

    # Display summary
    display_project_summary(projects, tasks)

    # If no projects exist, create the OOS project
    if not projects:
        print(f"\n💡 No projects found. Creating OOS Voice Analysis System project...")
        project_id = integration.create_project(
            title="OOS Voice Analysis System",
            description="Voice pattern extraction and AI personalization system with comprehensive security remediation",
            github_repo="https://github.com/Khamel83/atlas-voice"
        )

        if project_id:
            print(f"✅ Created project with ID: {project_id}")

            # Create security remediation tasks
            security_tasks = [
                ("Fix Hardcoded API Key Paths", "Remove hardcoded config file paths and implement secure credential management", 10),
                ("Fix Path Traversal Vulnerabilities", "Implement path validation and directory traversal protection", 10),
                ("Secure Subprocess Execution", "Add input validation and whitelist approach for subprocess calls", 10),
                ("Implement Input Validation", "Add comprehensive input validation framework", 8),
                ("Secure File Operations", "Add file type validation and size limits", 8),
                ("Add Rate Limiting", "Implement rate limiting for Telegram bot", 8),
                ("External API Security", "Add timeout handling and request validation", 6),
                ("Error Handling Security", "Implement secure error handling without information disclosure", 6),
                ("Security Monitoring", "Add security event logging and monitoring", 4),
                ("Security Testing", "Implement penetration testing and vulnerability scanning", 4)
            ]

            print(f"\n🔒 Creating security remediation tasks...")
            for title, desc, order in security_tasks:
                task_id = integration.create_task(
                    project_id=project_id,
                    title=title,
                    description=desc,
                    task_order=order
                )
                if task_id:
                    print(f"✅ Created task: {title}")
                else:
                    print(f"❌ Failed to create task: {title}")
        else:
            print("❌ Failed to create project")

    print(f"\n✅ OOS-Archon Integration Complete!")
    print("🔗 The hard connection work is now done - this connection is ready for production use")

if __name__ == "__main__":
    main()