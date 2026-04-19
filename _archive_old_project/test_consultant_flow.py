#!/usr/bin/env python3
"""
Unit tests for OOS Consultant flow
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch

from src.consultant_flow import ConsultantFlow, ConsultantState, IntakeData

class TestConsultantFlow:
    """Test consultant flow state machine"""

    @pytest.fixture
    def flow(self):
        """Create a test consultant flow"""
        with patch('src.consultant_flow.load_config') as mock_config:
            mock_config.return_value = {
                "intake_questions": {
                    "goal": {"text": "What's the goal?", "required": True},
                    "current_state": {"text": "Current state?", "required": True},
                    "stakeholders": {"text": "Stakeholders?", "required": True},
                    "constraints": {"text": "Constraints?", "required": False},
                    "risks": {"text": "Risks?", "required": False},
                    "assets": {"text": "Assets?", "required": False}
                },
                "output": {
                    "base_path": "./test_consulting",
                    "artifacts": {
                        "intake": "intake.json"
                    }
                },
                "external": {"allow_web": False},
                "planning": {"time_horizons": ["30 days", "60 days", "90 days"]},
                "portfolio": {"max_quick_wins": 3, "max_big_bets": 2}
            }
            return ConsultantFlow("Test Project")

    def test_initialization(self, flow):
        """Test flow initialization"""
        assert flow.project_name == "Test Project"
        assert flow.state == ConsultantState.INTAKE
        assert flow.current_question_index == 0
        assert flow.intake_data is None

    def test_get_current_question(self, flow):
        """Test getting current intake question"""
        question = flow.get_current_question()
        assert question is not None
        assert question["id"] == "goal"
        assert question["text"] == "What's the goal?"
        assert question["required"] is True

    def test_submit_answer(self, flow):
        """Test submitting an answer"""
        success = flow.submit_answer("goal", "Improve checkout process")
        assert success is True
        assert flow.current_question_index == 1
        assert flow.answers["goal"] == "Improve checkout process"

    def test_complete_intake(self, flow):
        """Test completing intake phase"""
        # Submit all required answers
        flow.submit_answer("goal", "Improve checkout process")
        flow.submit_answer("current_state", "Manual process with high error rate")
        flow.submit_answer("stakeholders", "Product team, engineering, customers")

        # Intake should be complete
        assert flow.state == ConsultantState.SYNTHESIZE
        assert flow.intake_data is not None
        assert flow.intake_data.goal == "Improve checkout process"
        assert flow.intake_data.current_state == "Manual process with high error rate"
        assert flow.intake_data.stakeholders == "Product team, engineering, customers"

    def test_intake_file_creation(self, flow, tmp_path):
        """Test that intake file is created"""
        # Override project directory for testing
        flow.project_dir = tmp_path / "test_project"
        flow.project_dir.mkdir(parents=True)

        # Complete intake
        flow.submit_answer("goal", "Test goal")
        flow.submit_answer("current_state", "Test state")
        flow.submit_answer("stakeholders", "Test stakeholders")

        # Check that intake file was created
        intake_file = flow.project_dir / "intake.json"
        assert intake_file.exists()

        # Check file contents
        with open(intake_file) as f:
            data = json.load(f)
            assert data["goal"] == "Test goal"
            assert data["current_state"] == "Test state"
            assert data["stakeholders"] == "Test stakeholders"

    @pytest.mark.asyncio
    async def test_synthesize(self, flow):
        """Test synthesis phase"""
        # Set up completed intake
        flow.intake_data = IntakeData(
            goal="Improve checkout process",
            current_state="Manual process with high error rate",
            stakeholders="Product team, engineering, customers"
        )
        flow.state = ConsultantState.SYNTHESIZE

        synthesis_data = await flow.synthesize()

        assert flow.state == ConsultantState.SCORE
        assert synthesis_data is not None
        assert synthesis_data.a3_data is not None
        assert synthesis_data.issue_tree is not None
        assert synthesis_data.opportunity_solution_tree is not None

        # Check A3 data structure
        a3_data = synthesis_data.a3_data
        assert "title" in a3_data
        assert "background" in a3_data
        assert "current_state" in a3_data
        assert "target_state" in a3_data
        assert "root_causes" in a3_data
        assert "countermeasures" in a3_data
        assert "plan" in a3_data
        assert "metrics" in a3_data

    @pytest.mark.asyncio
    async def test_score(self, flow):
        """Test scoring phase"""
        # Set up completed synthesis
        flow.state = ConsultantState.SCORE

        candidate_moves = [
            {"name": "Automation", "reach": 8, "impact": 9, "confidence": 8, "effort": 6},
            {"name": "Training", "reach": 5, "impact": 6, "confidence": 9, "effort": 3},
            {"name": "New System", "reach": 9, "impact": 8, "confidence": 6, "effort": 9}
        ]

        scoring_data = await flow.score(candidate_moves)

        assert flow.state == ConsultantState.PLAN
        assert scoring_data is not None
        assert scoring_data.impact_effort_matrix is not None
        assert scoring_data.rice_scores is not None
        assert scoring_data.quick_wins is not None
        assert scoring_data.big_bets is not None

        # Check that we have results
        assert len(scoring_data.impact_effort_matrix) == 3
        assert len(scoring_data.rice_scores) == 3

    @pytest.mark.asyncio
    async def test_plan(self, flow):
        """Test planning phase"""
        # Set up completed scoring
        flow.state = ConsultantState.PLAN
        flow.scoring_data = Mock()
        flow.scoring_data.quick_wins = [
            {"name": "Quick Win 1", "impact": 8, "effort": 3, "description": "Easy fix"}
        ]
        flow.scoring_data.big_bets = [
            {"name": "Big Bet 1", "impact": 9, "effort": 8, "description": "Major change"}
        ]

        plan_data = await flow.plan()

        assert flow.state == ConsultantState.EXPORT
        assert plan_data is not None
        assert plan_data.milestones is not None
        assert plan_data.portfolio is not None
        assert plan_data.risks is not None
        assert plan_data.owners is not None

        # Check milestones
        assert len(plan_data.milestones) == 3  # 30, 60, 90 days
        for milestone in plan_data.milestones:
            assert "horizon" in milestone
            assert "objectives" in milestone
            assert "metrics" in milestone

    @pytest.mark.asyncio
    async def test_export(self, flow, tmp_path):
        """Test export phase"""
        # Set up completed planning
        flow.state = ConsultantState.EXPORT
        flow.project_dir = tmp_path / "test_export"
        flow.project_dir.mkdir(parents=True)

        # Mock synthesis and planning data
        flow.synthesis_data = Mock()
        flow.synthesis_data.a3_data = {
            "title": "Test A3",
            "background": "Test background",
            "current_state": "Test current",
            "target_state": "Test target",
            "root_causes": ["Cause 1", "Cause 2"],
            "countermeasures": ["Fix 1", "Fix 2"],
            "plan": ["Step 1", "Step 2"],
            "metrics": ["Metric 1", "Metric 2"]
        }
        flow.synthesis_data.issue_tree = {
            "project": "Test Project",
            "main_problem": "Test problem",
            "branches": []
        }
        flow.synthesis_data.opportunity_solution_tree = {
            "outcome": "Test outcome",
            "opportunities": [],
            "solutions": [],
            "experiments": []
        }
        flow.synthesis_data.sources = []

        flow.scoring_data = Mock()
        flow.scoring_data.impact_effort_matrix = []
        flow.scoring_data.rice_scores = []

        flow.plan_data = Mock()
        flow.plan_data.milestones = []
        flow.plan_data.portfolio = []
        flow.plan_data.risks = []
        flow.plan_data.owners = {}

        # Mock renderer
        with patch('src.consultant_flow.ConsultingRenderer') as mock_renderer_class:
            mock_renderer = Mock()
            mock_renderer_class.return_value = mock_renderer

            mock_renderer.render_a3.return_value = tmp_path / "a3.md"
            mock_renderer.render_issue_tree.return_value = tmp_path / "issues.yaml"
            mock_renderer.render_ost.return_value = tmp_path / "ost.mmd"
            mock_renderer.render_impact_effort.return_value = tmp_path / "impact_effort.csv"
            mock_renderer.render_rice.return_value = tmp_path / "rice.csv"
            mock_renderer.render_plan.return_value = tmp_path / "plan.md"

            artifacts = await flow.export()

            assert flow.state == ConsultantState.COMPLETE
            assert artifacts is not None
            assert "a3" in artifacts
            assert "issue_tree" in artifacts
            assert "ost" in artifacts
            assert "impact_effort" in artifacts
            assert "rice_scores" in artifacts
            assert "plan" in artifacts

    def test_get_status(self, flow):
        """Test status reporting"""
        status = flow.get_status()
        assert "project" in status
        assert "state" in status
        assert "intake_complete" in status
        assert "synthesis_complete" in status
        assert "scoring_complete" in status
        assert "plan_complete" in status
        assert "export_complete" in status
        assert "project_directory" in status

        # Check initial state
        assert status["project"] == "Test Project"
        assert status["state"] == "intake"
        assert status["intake_complete"] is False
        assert status["export_complete"] is False

class TestIntakeData:
    """Test intake data structure"""

    def test_intake_data_creation(self):
        """Test IntakeData creation"""
        data = IntakeData(
            goal="Test goal",
            current_state="Test state",
            stakeholders="Test stakeholders",
            constraints="Test constraints",
            risks="Test risks",
            assets="Test assets",
            domain="Test domain"
        )

        assert data.goal == "Test goal"
        assert data.current_state == "Test state"
        assert data.stakeholders == "Test stakeholders"
        assert data.constraints == "Test constraints"
        assert data.risks == "Test risks"
        assert data.assets == "Test assets"
        assert data.domain == "Test domain"

    def test_intake_data_optional_fields(self):
        """Test IntakeData with optional fields"""
        data = IntakeData(
            goal="Test goal",
            current_state="Test state",
            stakeholders="Test stakeholders"
        )

        assert data.goal == "Test goal"
        assert data.current_state == "Test state"
        assert data.stakeholders == "Test stakeholders"
        assert data.constraints is None
        assert data.risks is None
        assert data.assets is None
        assert data.domain is None