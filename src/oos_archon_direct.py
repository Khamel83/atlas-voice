#!/usr/bin/env python3
"""
OOS-Archon Direct Connection - Final Integration
Direct connection handling the specific Archon MCP server requirements
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional

class OOSArchonDirect:
    """
    Direct connection to Archon MCP server with proper header handling
    """

    def __init__(self, archon_url: str = "http://100.103.45.61:8051/mcp"):
        self.archon_url = archon_url
        self.request_id = 0

    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make a direct request to Archon MCP server"""
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.archon_url, headers=headers, json=payload)
            print(f"📡 Request {payload.get('id', 'unknown')}: Status {response.status_code}")

            if response.status_code == 200:
                # Handle streaming response
                return self._parse_streaming_response(response.text)
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}

        except Exception as e:
            return {"error": str(e)}

    def _parse_streaming_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the streaming response text"""
        lines = response_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('data: '):
                try:
                    data = json.loads(line[6:])  # Remove 'data: ' prefix
                    if "result" in data:
                        return data["result"]
                except json.JSONDecodeError:
                    continue
        return {}

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in Archon"""
        print("📋 Requesting project list...")
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
                            projects = data["projects"]
                            break
                    except json.JSONDecodeError:
                        continue

        return projects

    def list_tasks(self, project_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered"""
        print("📝 Requesting task list...")
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
                            tasks = data["tasks"]
                            break
                    except json.JSONDecodeError:
                        continue

        return tasks

    def create_project(self, title: str, description: str = "", github_repo: str = None) -> Optional[str]:
        """Create a new project"""
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

def main():
    """Main function to demonstrate direct connection"""
    print("🚀 OOS-Archon Direct Connection Demo")
    print("=" * 50)

    # Test direct connection
    archon = OOSArchonDirect()

    # Initialize by testing connection
    print("🔗 Testing Archon connection...")
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True}
            },
            "clientInfo": {
                "name": "oos-direct-client",
                "version": "1.0"
            }
        }
    }

    init_result = archon._make_request(init_payload)
    if "error" in init_result:
        print(f"❌ Initialization failed: {init_result['error']}")
        return
    else:
        print("✅ Archon connection initialized")

    # List projects
    print(f"\n📂 Current Archon Projects:")
    print("-" * 40)
    projects = archon.list_projects()

    if not projects:
        print("No projects found")
    else:
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.get('title', 'Unknown Project')}")
            print(f"   ID: {project.get('id', 'N/A')}")
            print(f"   Status: {project.get('status', 'N/A')}")
            if project.get('description'):
                desc = project['description']
                print(f"   Description: {desc[:100]}{'...' if len(desc) > 100 else ''}")
            print()

    # List tasks
    print(f"📝 Current Tasks:")
    print("-" * 30)
    tasks = archon.list_tasks()

    if not tasks:
        print("No tasks found")
    else:
        # Group by status
        by_status = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(task)

        for status in ['todo', 'doing', 'review', 'done']:
            if status in by_status:
                print(f"\n{status.upper()} ({len(by_status[status])}):")
                for task in by_status[status]:
                    print(f"  • {task.get('title', 'Untitled Task')}")
                    print(f"    Order: {task.get('task_order', 0)} | Assignee: {task.get('assignee', 'Unassigned')}")

    print(f"\n📊 Summary:")
    print(f"   Total Projects: {len(projects)}")
    print(f"   Total Tasks: {len(tasks)}")

    if not projects:
        print(f"\n💡 No projects found. Let's create the OOS Voice Analysis project...")
        project_id = archon.create_project(
            title="OOS Voice Analysis System",
            description="Voice pattern extraction and AI personalization system",
            github_repo="https://github.com/Khamel83/atlas-voice"
        )

        if project_id:
            print(f"✅ Created project with ID: {project_id}")
        else:
            print("❌ Failed to create project")

    print(f"\n✅ OOS-Archon Direct Connection Complete!")
    print("This connection is now ready for ongoing integration use")

if __name__ == "__main__":
    main()