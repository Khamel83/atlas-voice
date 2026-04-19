#!/usr/bin/env python3
"""
Parallelism and Specialized Agents Architecture
Implements research learnings: multi-agent coordination, parallel processing, specialization
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import aiohttp

# Import our integrated systems
from oos_archon_integration import OOSArchonIntegration
from enhanced_rag_system import EnhancedRAGSystem
from memory_system import MultiLevelMemorySystem

class AgentType(Enum):
    """Types of specialized agents"""
    RESEARCH = "research_agent"
    KNOWLEDGE = "knowledge_agent"
    SYNTHESIS = "synthesis_agent"
    SECURITY = "security_agent"
    CODE = "code_agent"
    PLANNING = "planning_agent"

@dataclass
class AgentTask:
    id: str
    task_type: AgentType
    query: str
    context: Dict[str, Any]
    priority: int
    created_at: datetime
    timeout: float = 30.0

@dataclass
class AgentResult:
    task_id: str
    agent_type: AgentType
    result: Dict[str, Any]
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Message:
    id: str
    from_agent: str
    to_agent: str
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime

class SpecializedAgent:
    """Base class for specialized agents"""

    def __init__(self, agent_type: AgentType, integration: OOSArchonIntegration):
        self.agent_type = agent_type
        self.integration = integration
        self.logger = logging.getLogger(f"Agent-{agent_type.value}")
        self.message_queue = asyncio.Queue()
        self.is_running = False

    async def start(self):
        """Start the agent"""
        self.is_running = True
        self.logger.info(f"🤖 {self.agent_type.value} started")

    async def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.logger.info(f"🛑 {self.agent_type.value} stopped")

    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process a task - to be implemented by subclasses"""
        raise NotImplementedError

    async def send_message(self, to_agent: str, message_type: str, content: Dict[str, Any]):
        """Send message to another agent"""
        message = Message(
            id=str(uuid.uuid4()),
            from_agent=self.agent_type.value,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            timestamp=datetime.now()
        )
        # In a real implementation, this would go through a message broker
        await self.integration.message_queue.put(message)

    async def receive_message(self, message: Message):
        """Receive message from another agent"""
        await self.message_queue.put(message)

class ResearchAgent(SpecializedAgent):
    """Specialized in web research and API calls"""

    def __init__(self, integration: OOSArchonIntegration):
        super().__init__(AgentType.RESEARCH, integration)
        self.supported_apis = [
            "web_search",
            "wikipedia",
            "documentation",
            "api_calls"
        ]

    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process research task"""
        start_time = datetime.now()

        try:
            # Perform web research
            research_results = await self._perform_research(task.query, task.context)

            return AgentResult(
                task_id=task.id,
                agent_type=self.agent_type,
                result={
                    "research_findings": research_results,
                    "sources_used": ["web", "apis"],
                    "query_processed": task.query,
                    "research_type": "external"
                },
                success=True,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={"research_depth": "comprehensive"}
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_type=self.agent_type,
                result={},
                success=False,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )

    async def _perform_research(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform web research"""
        # Simulate web research (in production, use actual web APIs)
        research_data = {
            "query": query,
            "findings": [
                f"Research finding 1 for: {query}",
                f"Research finding 2 for: {query}",
                f"Research finding 3 for: {query}"
            ],
            "sources": [
                {"type": "web", "url": "https://example.com/research1"},
                {"type": "api", "endpoint": "/api/research"}
            ],
            "confidence": 0.85,
            "timestamp": datetime.now().isoformat()
        }

        # Add context-aware research
        if "security" in query.lower():
            research_data["findings"].extend([
                "Security vulnerabilities identified in system",
                "Recommended security best practices",
                "Compliance requirements analysis"
            ])

        return research_data

class KnowledgeAgent(SpecializedAgent):
    """Specialized in internal knowledge retrieval and management"""

    def __init__(self, integration: OOSArchonIntegration):
        super().__init__(AgentType.KNOWLEDGE, integration)
        self.rag_system = integration.rag_system
        self.memory_system = integration.memory_system

    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process knowledge retrieval task"""
        start_time = datetime.now()

        try:
            # Retrieve knowledge from multiple sources
            rag_context = await self.rag_system.retrieve_context(task.query, max_tokens=2000)
            memory_context = await self.memory_system.retrieve_relevant_context(task.query, max_tokens=1000)

            # Process and synthesize knowledge
            knowledge_synthesis = await self._synthesize_knowledge(rag_context, memory_context, task.query)

            return AgentResult(
                task_id=task.id,
                agent_type=self.agent_type,
                result={
                    "knowledge_synthesis": knowledge_synthesis,
                    "rag_context_used": bool(rag_context),
                    "memory_context_used": bool(memory_context),
                    "internal_sources": ["vector_db", "memory_system"],
                    "confidence": 0.92
                },
                success=True,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={"knowledge_sources": "internal"}
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_type=self.agent_type,
                result={},
                success=False,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )

    async def _synthesize_knowledge(self, rag_context: str, memory_context: str, query: str) -> Dict[str, Any]:
        """Synthesize knowledge from multiple sources"""
        synthesis = {
            "query": query,
            "integrated_knowledge": f"Combined RAG and Memory context for: {query}",
            "key_points": [],
            "context_sources": [],
            "synthesis_quality": "high"
        }

        # Extract key points from RAG context
        if rag_context:
            synthesis["key_points"].extend([
                "Knowledge retrieved from vector database",
                "Semantic search results applied",
                "Context-optimized retrieval"
            ])
            synthesis["context_sources"].append("rag_system")

        # Extract key points from memory context
        if memory_context:
            synthesis["key_points"].extend([
                "Historical context retrieved",
                "User preferences considered",
                "Previous interactions referenced"
            ])
            synthesis["context_sources"].append("memory_system")

        return synthesis

class SynthesisAgent(SpecializedAgent):
    """Specialized in synthesizing results from multiple agents"""

    def __init__(self, integration: OOSArchonIntegration):
        super().__init__(AgentType.SYNTHESIS, integration)

    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process synthesis task"""
        start_time = datetime.now()

        try:
            # Wait for results from other agents
            agent_results = task.context.get("agent_results", [])

            # Synthesize the results
            synthesis = await self._synthesize_results(agent_results, task.query)

            return AgentResult(
                task_id=task.id,
                agent_type=self.agent_type,
                result={
                    "synthesis": synthesis,
                    "agents_synthesized": len(agent_results),
                    "synthesis_approach": "hierarchical",
                    "final_confidence": synthesis.get("confidence", 0.0)
                },
                success=True,
                execution_time=(datetime.now() - start_time).total_seconds(),
                metadata={"synthesis_method": "multi_agent"}
            )

        except Exception as e:
            return AgentResult(
                task_id=task.id,
                agent_type=self.agent_type,
                result={},
                success=False,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )

    async def _synthesize_results(self, agent_results: List[AgentResult], query: str) -> Dict[str, Any]:
        """Synthesize results from multiple agents"""
        synthesis = {
            "query": query,
            "integrated_response": "",
            "key_insights": [],
            "confidence_factors": [],
            "recommendations": [],
            "confidence": 0.0
        }

        # Process results from each agent
        research_insights = []
        knowledge_insights = []
        overall_confidence = 0.0

        for result in agent_results:
            if result.success:
                if result.agent_type == AgentType.RESEARCH:
                    research_data = result.result.get("research_findings", {})
                    research_insights.extend(research_data.get("findings", []))
                    overall_confidence += 0.3

                elif result.agent_type == AgentType.KNOWLEDGE:
                    knowledge_data = result.result.get("knowledge_synthesis", {})
                    knowledge_insights.append(knowledge_data.get("integrated_knowledge", ""))
                    overall_confidence += 0.4

        # Generate integrated response
        synthesis["integrated_response"] = self._generate_integrated_response(query, research_insights, knowledge_insights)
        synthesis["key_insights"] = research_insights + knowledge_insights
        synthesis["confidence_factors"] = [
            f"Research quality: {len(research_insights)} findings",
            f"Knowledge depth: {len(knowledge_insights)} insights"
        ]
        synthesis["confidence"] = min(overall_confidence, 1.0)

        # Generate recommendations
        synthesis["recommendations"] = self._generate_recommendations(query, synthesis["key_insights"])

        return synthesis

    def _generate_integrated_response(self, query: str, research_insights: List[str], knowledge_insights: List[str]) -> str:
        """Generate integrated response from multiple sources"""
        response_parts = [f"**Comprehensive Analysis for: {query}**\n"]

        if research_insights:
            response_parts.append("\n📊 **External Research Findings:**")
            for insight in research_insights[:3]:  # Top 3 insights
                response_parts.append(f"• {insight}")

        if knowledge_insights:
            response_parts.append("\n🧠 **Internal Knowledge & Context:**")
            for insight in knowledge_insights[:2]:  # Top 2 insights
                response_parts.append(f"• {insight}")

        response_parts.append("\n💡 **Key Takeaways:**")
        response_parts.append("This analysis combines external research with internal knowledge to provide a comprehensive understanding of the topic.")

        return "\n".join(response_parts)

    def _generate_recommendations(self, query: str, insights: List[str]) -> List[str]:
        """Generate recommendations based on insights"""
        recommendations = []

        if "security" in query.lower():
            recommendations.extend([
                "Prioritize security remediation based on risk level",
                "Implement secure coding practices",
                "Conduct regular security audits"
            ])

        if "integration" in query.lower() or "system" in query.lower():
            recommendations.extend([
                "Focus on modular architecture design",
                "Implement proper error handling",
                "Consider scalability requirements"
            ])

        if not recommendations:
            recommendations = [
                "Continue monitoring and refining the approach",
                "Gather additional context if needed",
                "Validate findings with additional sources"
            ]

        return recommendations

class ParallelAgentOrchestrator:
    """Orchestrates parallel execution of specialized agents"""

    def __init__(self, integration: OOSArchonIntegration):
        self.integration = integration
        self.agents = {}
        self.message_queue = asyncio.Queue()
        self.task_queue = asyncio.Queue()
        self.logger = logging.getLogger("AgentOrchestrator")
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize specialized agents
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize all specialized agents"""
        self.agents = {
            AgentType.RESEARCH: ResearchAgent(self.integration),
            AgentType.KNOWLEDGE: KnowledgeAgent(self.integration),
            AgentType.SYNTHESIS: SynthesisAgent(self.integration)
        }

        # Set up message queue for integration
        self.integration.message_queue = self.message_queue

    async def start_all_agents(self):
        """Start all specialized agents"""
        for agent_type, agent in self.agents.items():
            await agent.start()
        self.logger.info("🚀 All specialized agents started")

    async def stop_all_agents(self):
        """Stop all specialized agents"""
        for agent_type, agent in self.agents.items():
            await agent.stop()
        self.logger.info("🛑 All specialized agents stopped")

    async def process_query_parallel(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query using parallel agent execution"""
        start_time = datetime.now()

        try:
            # Determine which agents to use based on query
            agent_types = self._determine_agent_types(query)

            # Create tasks for parallel execution
            tasks = []
            for agent_type in agent_types:
                task = AgentTask(
                    id=str(uuid.uuid4()),
                    task_type=agent_type,
                    query=query,
                    context=context or {},
                    priority=1,
                    created_at=datetime.now()
                )
                tasks.append(task)

            # Execute tasks in parallel
            agent_results = await self._execute_tasks_parallel(tasks)

            # Synthesize results
            if len(agent_results) > 1:
                synthesis_task = AgentTask(
                    id=str(uuid.uuid4()),
                    task_type=AgentType.SYNTHESIS,
                    query=query,
                    context={"agent_results": agent_results},
                    priority=1,
                    created_at=datetime.now()
                )
                synthesis_result = await self.agents[AgentType.SYNTHESIS].process_task(synthesis_task)
                final_result = synthesis_result.result
            else:
                # Single agent result
                final_result = agent_results[0].result if agent_results else {}

            # Track execution metrics
            execution_time = (datetime.now() - start_time).total_seconds()
            final_result["execution_metrics"] = {
                "total_time": execution_time,
                "agents_used": len(agent_types),
                "parallel_efficiency": len(agent_types) / max(execution_time, 0.1)
            }

            self.logger.info(f"🎯 Parallel processing completed in {execution_time:.2f}s using {len(agent_types)} agents")

            return final_result

        except Exception as e:
            self.logger.error(f"❌ Parallel processing failed: {e}")
            return {"error": str(e), "execution_metrics": {"total_time": (datetime.now() - start_time).total_seconds()}}

    def _determine_agent_types(self, query: str) -> List[AgentType]:
        """Determine which agents should process the query"""
        agent_types = []

        query_lower = query.lower()

        # Always use knowledge agent for internal context
        agent_types.append(AgentType.KNOWLEDGE)

        # Use research agent for external information
        if any(keyword in query_lower for keyword in ["research", "find", "search", "what is", "who is", "external"]):
            agent_types.append(AgentType.RESEARCH)

        # Use synthesis agent if multiple agents are involved
        if len(agent_types) > 1:
            agent_types.append(AgentType.SYNTHESIS)

        return agent_types

    async def _execute_tasks_parallel(self, tasks: List[AgentTask]) -> List[AgentResult]:
        """Execute tasks in parallel"""
        tasks_by_agent = {}

        # Group tasks by agent type
        for task in tasks:
            if task.task_type not in tasks_by_agent:
                tasks_by_agent[task.task_type] = []
            tasks_by_agent[task.task_type].append(task)

        # Execute tasks for each agent type in parallel
        async def execute_agent_tasks(agent_type, agent_tasks):
            agent = self.agents[agent_type]
            results = []
            for task in agent_tasks:
                result = await agent.process_task(task)
                results.append(result)
            return results

        # Create parallel tasks for each agent type
        parallel_tasks = []
        for agent_type, agent_tasks in tasks_by_agent.items():
            task = execute_agent_tasks(agent_type, agent_tasks)
            parallel_tasks.append(task)

        # Execute all agent tasks in parallel
        results_lists = await asyncio.gather(*parallel_tasks, return_exceptions=True)

        # Flatten results
        all_results = []
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
            elif isinstance(results, Exception):
                self.logger.error(f"Agent execution failed: {results}")

        return all_results

    async def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator and agent status"""
        return {
            "orchestrator_running": True,
            "agents": {
                agent_type.value: {
                    "running": agent.is_running,
                    "type": agent_type.value
                }
                for agent_type, agent in self.agents.items()
            },
            "message_queue_size": self.message_queue.qsize(),
            "task_queue_size": self.task_queue.qsize()
        }

async def main():
    """Demo the parallel agent system"""
    print("🚀 Parallel Agent Architecture Demo")
    print("=" * 50)

    # Initialize integration
    integration = OOSArchonIntegration()
    await integration.initialize()

    # Initialize orchestrator
    orchestrator = ParallelAgentOrchestrator(integration)
    await orchestrator.start_all_agents()

    # Test queries
    test_queries = [
        "What are the security vulnerabilities in our system?",
        "How does the OOS-Archon integration work?",
        "Research the latest AI agent architectures",
        "What are the best practices for knowledge management?"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        print("-" * 40)

        result = await orchestrator.process_query_parallel(query)
        print("📊 Parallel Processing Result:")
        print(f"   Agents Used: {result.get('execution_metrics', {}).get('agents_used', 0)}")
        print(f"   Execution Time: {result.get('execution_metrics', {}).get('total_time', 0):.2f}s")
        print(f"   Parallel Efficiency: {result.get('execution_metrics', {}).get('parallel_efficiency', 0):.2f}")

        if "synthesis" in result:
            synthesis = result["synthesis"]
            print(f"   Confidence: {synthesis.get('confidence', 0):.2f}")
            print(f"   Key Insights: {len(synthesis.get('key_insights', []))}")

    # Show orchestrator status
    status = await orchestrator.get_orchestrator_status()
    print(f"\n📋 Orchestrator Status:")
    print("-" * 30)
    for agent_name, agent_status in status["agents"].items():
        print(f"   {agent_name}: {'🟢 Running' if agent_status['running'] else '🔴 Stopped'}")

    await orchestrator.stop_all_agents()
    print("\n✅ Parallel Agent Architecture Demo Complete!")

if __name__ == "__main__":
    asyncio.run(main())