#!/usr/bin/env python3
"""
OOS Consultant Flow - State Machine for Structured Consulting
Implements intake → synthesize → score → plan → export workflow
"""

import asyncio
import json
import yaml
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import logging

from jinja2 import Environment, FileSystemLoader, Template

from config_loader import load_config
from src.prioritization import RICECalculator, ImpactEffortMatrix
from src.render_consulting import ConsultingRenderer

logger = logging.getLogger(__name__)

class ConsultantState(Enum):
    INTAKE = "intake"
    SYNTHESIZE = "synthesize"
    SCORE = "score"
    PLAN = "plan"
    EXPORT = "export"
    COMPLETE = "complete"

@dataclass
class IntakeData:
    goal: str
    current_state: str
    stakeholders: str
    constraints: Optional[str] = None
    risks: Optional[str] = None
    assets: Optional[str] = None
    domain: Optional[str] = None

@dataclass
class SynthesisData:
    a3_data: Dict[str, Any]
    issue_tree: Dict[str, Any]
    opportunity_solution_tree: Dict[str, Any]
    sources: List[Dict[str, Any]]

@dataclass
class ScoringData:
    impact_effort_matrix: List[Dict[str, Any]]
    rice_scores: List[Dict[str, Any]]
    quick_wins: List[Dict[str, Any]]
    big_bets: List[Dict[str, Any]]

@dataclass
class PlanData:
    milestones: List[Dict[str, Any]]
    portfolio: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    owners: Dict[str, str]

class ConsultantFlow:
    """
    State machine for structured consulting workflow
    """

    def __init__(self, project_name: str, domain: Optional[str] = None):
        self.project_name = project_name
        self.domain = domain
        self.state = ConsultantState.INTAKE
        self.config = load_config("consultant")

        # Initialize components
        self.rice_calculator = RICECalculator(self.config)
        self.impact_effort = ImpactEffortMatrix(self.config)
        self.renderer = ConsultingRenderer()

        # Data containers
        self.intake_data: Optional[IntakeData] = None
        self.synthesis_data: Optional[SynthesisData] = None
        self.scoring_data: Optional[ScoringData] = None
        self.plan_data: Optional[PlanData] = None

        # Setup project directory
        self.project_dir = Path(self.config["output"]["base_path"]) / project_name
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Current question tracking
        self.current_question_index = 0
        self.answers = {}

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current intake question"""
        if self.state != ConsultantState.INTAKE:
            return None

        questions = self.config["intake_questions"]
        question_keys = list(questions.keys())

        if self.current_question_index >= len(question_keys):
            return None

        question_key = question_keys[self.current_question_index]
        question_data = questions[question_key]

        return {
            "id": question_key,
            "text": question_data["text"],
            "required": question_data.get("required", False),
            "type": question_data.get("type", "text")
        }

    def submit_answer(self, question_id: str, answer: str) -> bool:
        """Submit an answer to the current question"""
        if self.state != ConsultantState.INTAKE:
            return False

        self.answers[question_id] = answer
        self.current_question_index += 1

        # Check if intake is complete
        questions = self.config["intake_questions"]
        required_questions = [k for k, v in questions.items() if v.get("required", False)]
        answered_required = [q for q in required_questions if q in self.answers]

        if len(answered_required) == len(required_questions):
            self._complete_intake()

        return True

    def _complete_intake(self):
        """Complete intake phase and create intake data"""
        self.intake_data = IntakeData(
            goal=self.answers.get("goal", ""),
            current_state=self.answers.get("current_state", ""),
            stakeholders=self.answers.get("stakeholders", ""),
            constraints=self.answers.get("constraints"),
            risks=self.answers.get("risks"),
            assets=self.answers.get("assets"),
            domain=self.domain
        )

        # Save intake data
        intake_file = self.project_dir / self.config["output"]["artifacts"]["intake"]
        with open(intake_file, 'w') as f:
            json.dump(asdict(self.intake_data), f, indent=2)

        self.state = ConsultantState.SYNTHESIZE
        logger.info(f"Intake complete for project {self.project_name}")

    async def synthesize(self) -> SynthesisData:
        """Synthesize intake data into structured artifacts"""
        if self.state != ConsultantState.SYNTHESIZE or not self.intake_data:
            raise ValueError("Intake data required for synthesis")

        logger.info(f"Starting synthesis for {self.project_name}")

        # Build A3 data
        a3_data = self._build_a3_data()

        # Build MECE issue tree
        issue_tree = self._build_issue_tree()

        # Build Opportunity Solution Tree
        ost = self._build_opportunity_solution_tree()

        # External research if enabled
        sources = []
        if self.config["external"].get("allow_web", False):
            sources = await self._conduct_external_research()

        self.synthesis_data = SynthesisData(
            a3_data=a3_data,
            issue_tree=issue_tree,
            opportunity_solution_tree=ost,
            sources=sources
        )

        # Save synthesis drafts
        await self._save_synthesis_drafts()

        self.state = ConsultantState.SCORE
        logger.info(f"Synthesis complete for {self.project_name}")

        return self.synthesis_data

    def _build_a3_data(self) -> Dict[str, Any]:
        """Build A3 problem-solving framework data"""
        return {
            "title": f"A3: {self.project_name}",
            "background": self.intake_data.goal,
            "current_state": self.intake_data.current_state,
            "target_state": self._derive_target_state(),
            "root_causes": self._identify_root_causes(),
            "countermeasures": self._propose_countermeasures(),
            "plan": self._create_initial_plan(),
            "metrics": self._define_success_metrics(),
            "created_at": datetime.now().isoformat()
        }

    def _build_issue_tree(self) -> Dict[str, Any]:
        """Build MECE issue tree from intake data"""
        return {
            "project": self.project_name,
            "main_problem": self.intake_data.goal,
            "branches": self._derive_issue_branches(),
            "generated_at": datetime.now().isoformat()
        }

    def _build_opportunity_solution_tree(self) -> Dict[str, Any]:
        """Build Opportunity Solution Tree"""
        return {
            "outcome": self.intake_data.goal,
            "opportunities": self._identify_opportunities(),
            "solutions": self._identify_solutions(),
            "experiments": self._design_experiments(),
            "generated_at": datetime.now().isoformat()
        }

    async def _conduct_external_research(self) -> List[Dict[str, Any]]:
        """Conduct external research for best practices"""
        # Placeholder for external research
        # In real implementation, this would call Context7, Docs-MCP, etc.
        return []

    def _derive_target_state(self) -> str:
        """Derive target state from goal"""
        return f"Achieved: {self.intake_data.goal}"

    def _identify_root_causes(self) -> List[str]:
        """Identify root causes using 5 Whys technique"""
        # Simple implementation - in practice this would be more sophisticated
        causes = []
        current = self.intake_data.current_state
        for i in range(5):
            causes.append(f"Why {i+1}: {current[:100]}...")
            current = current[100:] if len(current) > 100 else ""
        return causes

    def _propose_countermeasures(self) -> List[str]:
        """Propose countermeasures for root causes"""
        return [
            "Implement systematic process improvements",
            "Enhance stakeholder communication",
            "Optimize resource allocation",
            "Establish clear metrics and monitoring"
        ]

    def _create_initial_plan(self) -> List[str]:
        """Create initial plan steps"""
        return [
            "Assess current state and gaps",
            "Design solution approach",
            "Implement priority changes",
            "Monitor and measure results"
        ]

    def _define_success_metrics(self) -> List[str]:
        """Define success metrics"""
        return [
            "Goal achievement rate",
            "Stakeholder satisfaction",
            "Resource efficiency",
            "Timeline adherence"
        ]

    def _derive_issue_branches(self) -> List[Dict[str, Any]]:
        """Derive MECE issue tree branches"""
        return [
            {
                "category": "Process",
                "issues": ["Inefficient workflows", "Lack of standardization"]
            },
            {
                "category": "Technology",
                "issues": ["Outdated systems", "Integration challenges"]
            },
            {
                "category": "People",
                "issues": ["Skill gaps", "Resistance to change"]
            }
        ]

    def _identify_opportunities(self) -> List[Dict[str, Any]]:
        """Identify opportunities from intake data"""
        return [
            {"id": "opp1", "name": "Process Optimization", "description": "Streamline key workflows"},
            {"id": "opp2", "name": "Technology Upgrade", "description": "Modernize core systems"}
        ]

    def _identify_solutions(self) -> List[Dict[str, Any]]:
        """Identify potential solutions"""
        return [
            {"id": "sol1", "opportunity": "opp1", "name": "Workflow Automation", "description": "Automate manual processes"},
            {"id": "sol2", "opportunity": "opp2", "name": "System Migration", "description": "Migrate to modern platform"}
        ]

    def _design_experiments(self) -> List[Dict[str, Any]]:
        """Design experiments to test solutions"""
        return [
            {"id": "exp1", "solution": "sol1", "name": "Pilot Automation", "description": "Test automation on small scale"}
        ]

    async def _save_synthesis_drafts(self):
        """Save synthesis drafts to project directory"""
        if not self.synthesis_data:
            return

        drafts_dir = self.project_dir / "drafts"
        drafts_dir.mkdir(exist_ok=True)

        # Save A3 draft
        with open(drafts_dir / "a3_draft.json", 'w') as f:
            json.dump(self.synthesis_data.a3_data, f, indent=2)

        # Save issue tree draft
        with open(drafts_dir / "issues_draft.yaml", 'w') as f:
            yaml.dump(self.synthesis_data.issue_tree, f)

        # Save OST draft
        with open(drafts_dir / "ost_draft.json", 'w') as f:
            json.dump(self.synthesis_data.opportunity_solution_tree, f, indent=2)

    async def score(self, candidate_moves: List[Dict[str, Any]]) -> ScoringData:
        """Score candidate moves using RICE and Impact/Effort"""
        if self.state != ConsultantState.SCORE:
            raise ValueError("Must be in SCORE state")

        logger.info(f"Scoring {len(candidate_moves)} candidate moves")

        # Calculate Impact/Effort matrix
        ie_matrix = self.impact_effort.calculate_matrix(candidate_moves)

        # Calculate RICE scores
        rice_scores = self.rice_calculator.calculate_rice(candidate_moves)

        # Identify quick wins and big bets
        quick_wins = self.impact_effort.get_quick_wins(candidate_moves)
        big_bets = self.impact_effort.get_big_bets(candidate_moves)

        self.scoring_data = ScoringData(
            impact_effort_matrix=ie_matrix,
            rice_scores=rice_scores,
            quick_wins=quick_wins,
            big_bets=big_bets
        )

        self.state = ConsultantState.PLAN
        logger.info(f"Scoring complete for {self.project_name}")

        return self.scoring_data

    async def plan(self) -> PlanData:
        """Create execution plan based on scoring"""
        if self.state != ConsultantState.PLAN or not self.scoring_data:
            raise ValueError("Scoring data required for planning")

        logger.info(f"Creating plan for {self.project_name}")

        # Select portfolio
        portfolio = self._select_portfolio()

        # Create milestones
        milestones = self._create_milestones()

        # Identify risks
        risks = self._identify_plan_risks()

        # Assign owners
        owners = self._assign_owners()

        self.plan_data = PlanData(
            milestones=milestones,
            portfolio=portfolio,
            risks=risks,
            owners=owners
        )

        self.state = ConsultantState.EXPORT
        logger.info(f"Planning complete for {self.project_name}")

        return self.plan_data

    def _select_portfolio(self) -> List[Dict[str, Any]]:
        """Select portfolio of initiatives"""
        portfolio = []

        # Add quick wins
        quick_wins = self.scoring_data.quick_wins[:self.config["portfolio"]["max_quick_wins"]]
        portfolio.extend([{"type": "quick_win", **win} for win in quick_wins])

        # Add big bets
        big_bets = self.scoring_data.big_bets[:self.config["portfolio"]["max_big_bets"]]
        portfolio.extend([{"type": "big_bet", **bet} for bet in big_bets])

        return portfolio

    def _create_milestones(self) -> List[Dict[str, Any]]:
        """Create timeline milestones"""
        horizons = self.config["planning"]["time_horizons"]
        milestones = []

        for horizon in horizons:
            milestones.append({
                "horizon": horizon,
                "objectives": self._define_horizon_objectives(horizon),
                "metrics": self._define_horizon_metrics(horizon),
                "dependencies": []
            })

        return milestones

    def _identify_plan_risks(self) -> List[Dict[str, Any]]:
        """Identify plan-level risks"""
        return [
            {"risk": "Resource constraints", "mitigation": "Secure budget approval early"},
            {"risk": "Stakeholder resistance", "mitigation": "Engage stakeholders early and often"},
            {"risk": "Technical complexity", "mitigation": "Conduct technical feasibility study"}
        ]

    def _assign_owners(self) -> Dict[str, str]:
        """Assign owners to initiatives"""
        return {
            "project_lead": "TBD",
            "technical_lead": "TBD",
            "stakeholder_lead": "TBD"
        }

    def _define_horizon_objectives(self, horizon: str) -> List[str]:
        """Define objectives for time horizon"""
        if "30" in horizon:
            return ["Complete assessment", "Quick wins implementation"]
        elif "60" in horizon:
            return ["Expand successful initiatives", "Address medium priorities"]
        else:
            return ["Full implementation", "Sustained operations"]

    def _define_horizon_metrics(self, horizon: str) -> List[str]:
        """Define metrics for time horizon"""
        if "30" in horizon:
            return ["Assessment completion", "Quick win success rate"]
        elif "60" in horizon:
            return ["Initiative expansion rate", "Stakeholder satisfaction"]
        else:
            return ["Goal achievement", "ROI measurement"]

    async def export(self) -> Dict[str, str]:
        """Export all artifacts"""
        if self.state != ConsultantState.EXPORT:
            raise ValueError("Must be in EXPORT state")

        logger.info(f"Exporting artifacts for {self.project_name}")

        artifacts = {}

        # Export A3
        a3_path = await self.renderer.render_a3(
            self.synthesis_data.a3_data,
            self.project_dir / self.config["output"]["artifacts"]["a3"]
        )
        artifacts["a3"] = str(a3_path)

        # Export issue tree
        issues_path = await self.renderer.render_issue_tree(
            self.synthesis_data.issue_tree,
            self.project_dir / self.config["output"]["artifacts"]["issue_tree"]
        )
        artifacts["issue_tree"] = str(issues_path)

        # Export OST
        ost_path = await self.renderer.render_ost(
            self.synthesis_data.opportunity_solution_tree,
            self.project_dir / self.config["output"]["artifacts"]["ost"]
        )
        artifacts["ost"] = str(ost_path)

        # Export scoring
        ie_path = await self.renderer.render_impact_effort(
            self.scoring_data.impact_effort_matrix,
            self.project_dir / self.config["output"]["artifacts"]["impact_effort"]
        )
        artifacts["impact_effort"] = str(ie_path)

        rice_path = await self.renderer.render_rice(
            self.scoring_data.rice_scores,
            self.project_dir / self.config["output"]["artifacts"]["rice_scores"]
        )
        artifacts["rice_scores"] = str(rice_path)

        # Export plan
        plan_path = await self.renderer.render_plan(
            self.plan_data,
            self.project_dir / self.config["output"]["artifacts"]["plan"]
        )
        artifacts["plan"] = str(plan_path)

        # Export sources if available
        if self.synthesis_data.sources:
            sources_path = self.project_dir / self.config["output"]["artifacts"]["sources"]
            with open(sources_path, 'w') as f:
                json.dump(self.synthesis_data.sources, f, indent=2)
            artifacts["sources"] = str(sources_path)

        self.state = ConsultantState.COMPLETE
        logger.info(f"Export complete for {self.project_name}")

        return artifacts

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the consulting flow"""
        return {
            "project": self.project_name,
            "state": self.state.value,
            "intake_complete": self.intake_data is not None,
            "synthesis_complete": self.synthesis_data is not None,
            "scoring_complete": self.scoring_data is not None,
            "plan_complete": self.plan_data is not None,
            "export_complete": self.state == ConsultantState.COMPLETE,
            "project_directory": str(self.project_dir)
        }