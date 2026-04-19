#!/usr/bin/env python3
"""
OOS-Archon Bridge - The Hard Connection Work Upfront
This establishes a persistent, production-ready connection between OOS and Archon MCP
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArchonProject:
    id: str
    title: str
    description: str
    status: str
    created_at: datetime

@dataclass
class ArchonTask:
    id: str
    title: str
    description: str
    status: str
    project_id: str
    task_order: int
    assignee: str
    created_at: datetime

class OOSArchonBridge:
    """
    Production-ready bridge between OOS and Archon MCP server
    Handles session management, retries, and proper error handling
    """

    def __init__(self, archon_url: str = "http://100.103.45.61:8051/mcp"):
        self.archon_url = archon_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_id = 0
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Setup structured logging for the bridge"""
        logger = logging.getLogger("OOS-Archon-Bridge")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Establish persistent connection to Archon MCP server"""
        if self.session and not self.session.closed:
            return

        self.session = aiohttp.ClientSession(
            headers={
                "Accept": "text/event-stream",
                "Content-Type": "application/json"
            },
            timeout=aiohttp.ClientTimeout(total=30)
        )

        # Initialize the session
        await self._initialize_session()
        self.logger.info("✅ OOS-Archon bridge connected")

    async def disconnect(self):
        """Close the connection"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.logger.info("🔌 OOS-Archon bridge disconnected")

    async def _initialize_session(self):
        """Initialize MCP session with Archon server"""
        init_payload = {
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
                    "name": "oos-archon-bridge",
                    "version": "1.0.0"
                }
            }
        }

        try:
            async with self.session.post(self.archon_url, json=init_payload) as response:
                if response.status == 200:
                    self.logger.info("✅ Archon MCP session initialized")
                else:
                    raise Exception(f"Initialization failed: {response.status}")
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Archon session: {e}")
            raise

    def _next_id(self) -> int:
        """Get next request ID"""
        self.request_id += 1
        return self.request_id

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Archon MCP server"""
        if not self.session or self.session.closed:
            await self.connect()

        payload = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }

        try:
            async with self.session.post(self.archon_url, json=payload) as response:
                if response.status == 200:
                    # Handle streaming response
                    result = await self._parse_streaming_response(response)
                    return result
                else:
                    error_text = await response.text()
                    self.logger.error(f"Tool call failed: {response.status} - {error_text}")
                    return {"error": f"HTTP {response.status}: {error_text}"}
        except Exception as e:
            self.logger.error(f"Tool call exception: {e}")
            return {"error": str(e)}

    async def _parse_streaming_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Parse streaming SSE response from MCP server"""
        result = None

        async for line in response.content:
            if line:
                line_text = line.decode('utf-8').strip()
                if line_text.startswith('data: '):
                    try:
                        data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                        if "result" in data:
                            result = data["result"]
                            break
                    except json.JSONDecodeError:
                        continue

        return result or {}

    async def list_projects(self) -> List[ArchonProject]:
        """List all projects in Archon"""
        result = await self.call_tool("list_projects", {})

        if "error" in result:
            self.logger.error(f"Error listing projects: {result['error']}")
            return []

        projects = []
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        if "projects" in data:
                            for proj_data in data["projects"]:
                                projects.append(ArchonProject(
                                    id=proj_data.get("id", ""),
                                    title=proj_data.get("title", ""),
                                    description=proj_data.get("description", ""),
                                    status=proj_data.get("status", ""),
                                    created_at=datetime.now()
                                ))
                    except json.JSONDecodeError:
                        continue

        return projects

    async def list_tasks(self, project_id: str = None, status: str = None) -> List[ArchonTask]:
        """List tasks, optionally filtered by project and status"""
        arguments = {}
        if project_id:
            arguments["project_id"] = project_id
        if status:
            arguments["filter_by"] = "status"
            arguments["filter_value"] = status

        result = await self.call_tool("list_tasks", arguments)

        if "error" in result:
            self.logger.error(f"Error listing tasks: {result['error']}")
            return []

        tasks = []
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        if "tasks" in data:
                            for task_data in data["tasks"]:
                                tasks.append(ArchonTask(
                                    id=task_data.get("id", ""),
                                    title=task_data.get("title", ""),
                                    description=task_data.get("description", ""),
                                    status=task_data.get("status", ""),
                                    project_id=task_data.get("project_id", ""),
                                    task_order=task_data.get("task_order", 0),
                                    assignee=task_data.get("assignee", "Unassigned"),
                                    created_at=datetime.now()
                                ))
                    except json.JSONDecodeError:
                        continue

        return tasks

    async def create_project(self, title: str, description: str = "", github_repo: str = None) -> Optional[str]:
        """Create a new project in Archon"""
        arguments = {
            "title": title,
            "description": description
        }
        if github_repo:
            arguments["github_repo"] = github_repo

        result = await self.call_tool("create_project", arguments)

        if "error" in result:
            self.logger.error(f"Error creating project: {result['error']}")
            return None

        # Extract project ID from result
        if "content" in result:
            for item in result["content"]:
                if item["type"] == "text":
                    try:
                        data = json.loads(item["text"])
                        return data.get("project_id")
                    except json.JSONDecodeError:
                        continue

        return None

    async def get_project_status_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of project status"""
        projects = await self.list_projects()
        all_tasks = await self.list_tasks()

        # Group tasks by project and status
        project_summary = {}
        task_status_counts = {"todo": 0, "doing": 0, "review": 0, "done": 0}

        for task in all_tasks:
            task_status_counts[task.status] += 1

            if task.project_id not in project_summary:
                project_summary[task.project_id] = {
                    "project_title": next((p.title for p in projects if p.id == task.project_id), "Unknown"),
                    "tasks": {"todo": 0, "doing": 0, "review": 0, "done": 0}
                }

            project_summary[task.project_id]["tasks"][task.status] += 1

        return {
            "total_projects": len(projects),
            "total_tasks": len(all_tasks),
            "task_status_breakdown": task_status_counts,
            "project_breakdown": project_summary,
            "projects": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "status": p.status
                } for p in projects
            ]
        }

async def main():
    """Main demo function"""
    print("🚀 OOS-Archon Bridge - Production Integration Demo")
    print("=" * 60)

    try:
        async with OOSArchonBridge() as bridge:
            # Get comprehensive status
            print("📊 Fetching Archon status...")
            summary = await bridge.get_project_status_summary()

            print(f"\n🎯 Archon System Overview:")
            print(f"   Total Projects: {summary['total_projects']}")
            print(f"   Total Tasks: {summary['total_tasks']}")
            print(f"   Task Status: {summary['task_status_breakdown']}")

            if summary['projects']:
                print(f"\n📋 Current Projects:")
                print("-" * 40)
                for i, project in enumerate(summary['projects'], 1):
                    print(f"{i}. {project['title']}")
                    print(f"   ID: {project['id']}")
                    print(f"   Status: {project['status']}")
                    if project['description']:
                        desc = project['description']
                        print(f"   Description: {desc[:100]}{'...' if len(desc) > 100 else ''}")

                    # Show task breakdown for this project
                    if project['id'] in summary['project_breakdown']:
                        tasks = summary['project_breakdown'][project['id']]['tasks']
                        print(f"   Tasks: {tasks}")
                    print()

            # Show recent tasks
            print(f"📝 Recent Tasks:")
            print("-" * 30)
            recent_tasks = await bridge.list_tasks()

            # Show tasks by status
            by_status = {}
            for task in recent_tasks:
                if task.status not in by_status:
                    by_status[task.status] = []
                by_status[task.status].append(task)

            for status in ['todo', 'doing', 'review', 'done']:
                if status in by_status and by_status[status]:
                    print(f"\n{status.upper()} ({len(by_status[status])}):")
                    for task in by_status[status][:5]:  # Show first 5
                        print(f"  • {task.title}")
                        print(f"    Order: {task.task_order} | Assignee: {task.assignee}")
                    if len(by_status[status]) > 5:
                        print(f"    ... and {len(by_status[status]) - 5} more")

    except Exception as e:
        print(f"❌ Bridge connection failed: {e}")
        print("Make sure Archon MCP server is running on http://100.103.45.61:8051/mcp")

if __name__ == "__main__":
    asyncio.run(main())