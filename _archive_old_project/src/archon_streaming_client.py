#!/usr/bin/env python3
"""
Streaming Archon MCP Client for proper session management
"""

import requests
import json
import sseclient
from typing import Dict, Any, List

class ArchonStreamingClient:
    def __init__(self, base_url: str = "http://100.103.45.61:8051/mcp"):
        self.base_url = base_url
        self.headers = {
            "Accept": "text/event-stream",
            "Content-Type": "application/json"
        }

    def send_request(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send request and get streaming response"""
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload, stream=True)
            client = sseclient.SSEClient(response)

            results = []
            for event in client.events():
                if event.event == "message":
                    try:
                        data = json.loads(event.data)
                        results.append(data)
                    except json.JSONDecodeError:
                        continue

            return results
        except Exception as e:
            print(f"❌ Request error: {e}")
            return []

    def initialize_and_list_projects(self):
        """Initialize session and list projects"""
        print("🔗 Initializing Archon MCP Session...")

        # First initialize
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
                    "name": "oos-archon-integration",
                    "version": "1.0"
                }
            }
        }

        init_results = self.send_request(init_payload)
        print(f"✅ Initialization response: {len(init_results)} events")

        # Now list projects
        print("\n📋 Listing Projects...")
        list_payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "list_projects",
                "arguments": {}
            }
        }

        project_results = self.send_request(list_payload)
        print(f"📊 Project query results: {len(project_results)} responses")

        # Parse and display results
        for result in project_results:
            if "result" in result and "content" in result["result"]:
                for content in result["result"]["content"]:
                    if content["type"] == "text":
                        try:
                            data = json.loads(content["text"])
                            if "projects" in data:
                                return data["projects"]
                        except json.JSONDecodeError:
                            continue

        return []

def main():
    """Main function to demonstrate streaming Archon connection"""
    print("🚀 OOS-Archon Streaming Integration Demo")
    print("=" * 50)

    try:
        client = ArchonStreamingClient()
        projects = client.initialize_and_list_projects()

        if projects:
            print(f"\n🎉 Found {len(projects)} projects in Archon:")
            print("-" * 40)
            for i, project in enumerate(projects, 1):
                print(f"{i}. {project.get('title', 'Unknown Project')}")
                print(f"   ID: {project.get('id', 'N/A')}")
                print(f"   Status: {project.get('status', 'N/A')}")
                if project.get('description'):
                    desc = project['description']
                    print(f"   Description: {desc[:100]}{'...' if len(desc) > 100 else ''}")
                print()

        else:
            print("❌ No projects found or unable to retrieve projects")

    except ImportError:
        print("❌ Missing required package. Installing sseclient...")
        import subprocess
        subprocess.run(["pip3", "install", "sseclient-py"])
        print("✅ Package installed. Please run the script again.")

if __name__ == "__main__":
    main()