#!/usr/bin/env python3
"""
OOS MCP Server - Model Context Protocol Server
Provides OOS capabilities through MCP interface
"""

import asyncio
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
import aiohttp
from aiohttp import web
import aiohttp_cors

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OOSMCPServer:
    """MCP Server for OOS integration"""

    def __init__(self, host="localhost", port=8080):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.setup_cors()

    def setup_routes(self):
        """Set up HTTP routes for MCP endpoints"""
        self.app.add_routes([
            web.get('/context', self.handle_context),
            web.post('/optimize', self.handle_optimize),
            web.post('/clarify', self.handle_clarify),
            web.get('/health', self.handle_health),
            web.get('/metrics', self.handle_metrics),
        ])

    def setup_cors(self):
        """Set up CORS for cross-origin requests"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })

        for route in list(self.app.router.routes()):
            cors.add(route)

    async def handle_context(self, request):
        """Handle context management requests"""
        try:
            session_id = request.query.get('session_id', 'default')
            limit = int(request.query.get('limit', 10))

            # Get context from database
            context_data = await self.get_context_data(session_id, limit)

            return web.json_response({
                "status": "success",
                "session_id": session_id,
                "context": context_data,
                "timestamp": asyncio.get_event_loop().time()
            })

        except Exception as e:
            logger.error(f"Context request failed: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)

    async def handle_optimize(self, request):
        """Handle token optimization requests"""
        try:
            data = await request.json()
            content = data.get('content', '')
            strategies = data.get('strategies', ['all'])

            # Apply optimization strategies
            optimized = await self.optimize_content(content, strategies)

            return web.json_response({
                "status": "success",
                "original_size": len(content),
                "optimized_size": len(optimized),
                "reduction_ratio": (len(content) - len(optimized)) / len(content),
                "optimized_content": optimized
            })

        except Exception as e:
            logger.error(f"Optimization request failed: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)

    async def handle_clarify(self, request):
        """Handle meta-clarification requests"""
        try:
            data = await request.json()
            request_text = data.get('request', '')

            # Apply meta-clarification
            clarified = await self.clarify_request(request_text)

            return web.json_response({
                "status": "success",
                "original_request": request_text,
                "clarified_request": clarified,
                "intent_detected": self.detect_intent(request_text),
                "complexity_score": self.assess_complexity(request_text)
            })

        except Exception as e:
            logger.error(f"Clarification request failed: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)

    async def handle_health(self, request):
        """Health check endpoint"""
        return web.json_response({
            "status": "healthy",
            "service": "oos-mcp",
            "version": "1.0.0",
            "uptime": asyncio.get_event_loop().time()
        })

    async def handle_metrics(self, request):
        """Metrics endpoint"""
        try:
            metrics = await self.get_metrics()
            return web.json_response(metrics)
        except Exception as e:
            logger.error(f"Metrics request failed: {e}")
            return web.json_response({
                "status": "error",
                "message": str(e)
            }, status=500)

    async def get_context_data(self, session_id: str, limit: int) -> Dict[str, Any]:
        """Retrieve context data for session"""
        # Mock implementation - in real implementation, this would query the database
        return {
            "session_id": session_id,
            "entries": [],
            "project_structure": {},
            "recent_files": [],
            "user_preferences": {}
        }

    async def optimize_content(self, content: str, strategies: List[str]) -> str:
        """Apply optimization strategies to content"""
        optimized = content

        # Remove redundant whitespace
        if 'whitespace' in strategies or 'all' in strategies:
            optimized = ' '.join(optimized.split())

        # Remove redundant comments (simple implementation)
        if 'comments' in strategies or 'all' in strategies:
            lines = optimized.split('\n')
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                if not (stripped.startswith('#') and len(stripped) > 1):
                    filtered_lines.append(line)
            optimized = '\n'.join(filtered_lines)

        return optimized

    async def clarify_request(self, request_text: str) -> str:
        """Apply meta-clarification to request"""
        # Simple clarification - add context and structure
        clarification_prompt = f"""
Please clarify the following request by:
1. Identifying the main intent
2. Adding relevant context
3. Structuring for better understanding

Original request: {request_text}

Clarified request:
"""

        # In real implementation, this would use an LLM
        clarified = f"[CLARIFIED] {request_text} [Intent: Development]"

        return clarified

    def detect_intent(self, request_text: str) -> str:
        """Detect user intent"""
        text_lower = request_text.lower()

        if any(word in text_lower for word in ['create', 'make', 'build', 'write']):
            return 'creation'
        elif any(word in text_lower for word in ['fix', 'debug', 'error', 'bug']):
            return 'debugging'
        elif any(word in text_lower for word in ['optimize', 'improve', 'refactor']):
            return 'optimization'
        elif any(word in text_lower for word in ['test', 'check', 'verify']):
            return 'testing'
        else:
            return 'general'

    def assess_complexity(self, request_text: str) -> float:
        """Assess request complexity (0.0 to 1.0)"""
        # Simple complexity assessment
        complexity = 0.0

        # Length factor
        complexity += min(0.3, len(request_text) / 1000)

        # Technical terms
        tech_terms = ['api', 'database', 'algorithm', 'architecture', 'framework']
        for term in tech_terms:
            if term in request_text.lower():
                complexity += 0.1

        # Multiple requirements
        if ' and ' in request_text.lower() or request_text.count(',') > 2:
            complexity += 0.2

        return min(1.0, complexity)

    async def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        return {
            "requests_handled": 0,
            "optimizations_performed": 0,
            "clarifications_applied": 0,
            "average_response_time": 0.0,
            "token_reduction_rate": 0.0,
            "uptime": asyncio.get_event_loop().time()
        }

    async def start(self):
        """Start the MCP server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        logger.info(f"OOS MCP Server started on {self.host}:{self.port}")
        logger.info("Available endpoints:")
        logger.info("  GET  /context     - Context management")
        logger.info("  POST /optimize    - Token optimization")
        logger.info("  POST /clarify     - Meta-clarification")
        logger.info("  GET  /health      - Health check")
        logger.info("  GET  /metrics     - System metrics")

        return runner

async def main():
    """Main entry point"""
    server = OOSMCPServer()
    runner = await server.start()

    try:
        # Keep the server running
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour
    except KeyboardInterrupt:
        logger.info("Shutting down MCP server...")
    finally:
        await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
