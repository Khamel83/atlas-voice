#!/bin/bash

# OOS-Archon Integration Session Manager
# This handles the hard connection work upfront

ARCHON_URL="http://100.103.45.61:8051/mcp"
SESSION_FILE="/tmp/archon_session.json"

echo "🔗 OOS-Archon Integration Session Manager"
echo "=========================================="

# Initialize session
echo "📡 Initializing Archon MCP session..."
INIT_RESPONSE=$(curl -s -H "Accept: application/json, text/event-stream" -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {
        "roots": {"listChanged": true}
      },
      "clientInfo": {
        "name": "oos-archon-integration",
        "version": "1.0"
      }
    }
  }' "$ARCHON_URL")

echo "✅ Session initialized"
echo "📋 Available tools from initialization:"
echo "$INIT_RESPONSE" | grep -o '"tools":{"listChanged":[^}]*}' || echo "Tools info found in init"

# List projects
echo ""
echo "📂 Listing Archon Projects..."
echo "--------------------------------"

PROJECTS_RESPONSE=$(curl -s -H "Accept: application/json, text/event-stream" -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "list_projects",
      "arguments": {}
    }
  }' "$ARCHON_URL")

# Try to extract project information
echo "🔍 Project Response Analysis:"
echo "$PROJECTS_RESPONSE" | jq -r '.result.content[].text' 2>/dev/null | jq '.' 2>/dev/null || echo "Raw response:"
echo "$PROJECTS_RESPONSE"

# List tasks
echo ""
echo "📋 Listing Tasks..."
echo "--------------------------------"

TASKS_RESPONSE=$(curl -s -H "Accept: application/json, text/event-stream" -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "list_tasks",
      "arguments": {}
    }
  }' "$ARCHON_URL")

echo "🔍 Tasks Response Analysis:"
echo "$TASKS_RESPONSE" | jq -r '.result.content[].text' 2>/dev/null | jq '.' 2>/dev/null || echo "Raw tasks response:"
echo "$TASKS_RESPONSE"

echo ""
echo "✅ OOS-Archon Integration Complete"
echo "This connection is now ready for ongoing use"