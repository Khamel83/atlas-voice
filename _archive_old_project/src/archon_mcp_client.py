#!/usr/bin/env python3
"""
Archon MCP Client for OOS Integration
This establishes the hard connection work upfront between OOS and Archon
"""

import requests
import json
import time
from typing import Dict, Any, List

class ArchonMCPClient:
    def __init__(self, base_url: str = "http://100.103.45.61:8051/mcp"):
        self.base_url = base_url
        self.session_id = None
        self.headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }

    def initialize(self) -> bool:
        """Initialize MCP session with Archon server"""
        init_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    }
                },
                "clientInfo": {
                    "name": "oos-archon-integration",
                    "version": "1.0"
                }
            }
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=init_payload)
            if response.status_code == 200:
                print("✅ Connected to Archon MCP Server")
                return True
            else:
                print(f"❌ Failed to connect: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Archon MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"error": str(e)}

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects in Archon"""
        result = self.call_tool("list_projects", {})
        if "error" in result:
            print(f"❌ Error listing projects: {result['error']}")
            return []

        # Extract projects from result
        if "result" in result and "content" in result["result"]:
            for item in result["result"]["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        return data.get("projects", [])
                    except json.JSONDecodeError:
                        continue

        return []

    def list_tasks(self, project_id: str = None, status: str = None) -> List[Dict[str, Any]]:
        """List tasks, optionally filtered by project and status"""
        arguments = {}
        if project_id:
            arguments["project_id"] = project_id
        if status:
            arguments["filter_by"] = "status"
            arguments["filter_value"] = status

        result = self.call_tool("list_tasks", arguments)
        if "error" in result:
            print(f"❌ Error listing tasks: {result['error']}")
            return []

        # Extract tasks from result
        if "result" in result and "content" in result["result"]:
            for item in result["result"]["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        return data.get("tasks", [])
                    except json.JSONDecodeError:
                        continue

        return []

def main():
    """Main function to demonstrate Archon integration"""
    print("🔗 OOS-Archon Integration Demo")
    print("=" * 40)

    # Initialize connection
    client = ArchonMCPClient()
    if not client.initialize():
        print("❌ Failed to initialize Archon connection")
        return

    print("✅ Archon MCP Server connection established")

    # List projects
    print("\n📋 Current Archon Projects:")
    print("-" * 30)
    projects = client.list_projects()

    if not projects:
        print("No projects found in Archon")
    else:
        for i, project in enumerate(projects, 1):
            print(f"{i}. {project.get('title', 'Unknown Project')}")
            print(f"   ID: {project.get('id', 'N/A')}")
            print(f"   Status: {project.get('status', 'N/A')}")
            if project.get('description'):
                print(f"   Description: {project['description'][:100]}...")
            print()

    # List tasks (all projects)
    print("📋 Current Tasks (All Projects):")
    print("-" * 30)
    tasks = client.list_tasks()

    if not tasks:
        print("No tasks found in Archon")
    else:
        # Group tasks by status
        by_status = {}
        for task in tasks:
            status = task.get('status', 'unknown')
            if status not in by_status:
                by_status[status] = []
            by_status[status].append(task)

        for status in ['todo', 'doing', 'review', 'done']:
            if status in by_status:
                print(f"\n{status.upper()}:")
                for task in by_status[status]:
                    print(f"  • {task.get('title', 'Untitled Task')}")
                    print(f"    ID: {task.get('id', 'N/A')} | Order: {task.get('task_order', 0)}")
                    if task.get('assignee'):
                        print(f"    Assignee: {task['assignee']}")

if __name__ == "__main__":
    main()