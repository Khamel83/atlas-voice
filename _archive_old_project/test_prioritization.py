#!/usr/bin/env python3
"""
Unit tests for OOS Consultant prioritization utilities
"""

import pytest
from src.prioritization import RICECalculator, ImpactEffortMatrix, InitiativeScorer, generate_sample_initiatives

class TestRICECalculator:
    """Test RICE scoring functionality"""

    def test_rice_calculation_basic(self):
        """Test basic RICE calculation"""
        config = {"scoring": {"rice_weights": {
            "reach_weight": 1.0,
            "impact_weight": 1.0,
            "confidence_weight": 1.0,
            "effort_weight": 1.0
        }}}

        calculator = RICECalculator(config)
        initiative = {
            "name": "Test Initiative",
            "description": "Test description",
            "reach": 10,
            "impact": 8,
            "confidence": 7,
            "effort": 5
        }

        scores = calculator.calculate_rice([initiative])
        assert len(scores) == 1

        score = scores[0]
        assert score["initiative"] == "Test Initiative"
        assert score["reach"] == 10
        assert score["impact"] == 8
        assert score["confidence"] == 7
        assert score["effort"] == 5
        assert score["rice_score"] == (10 * 8 * 7) / 5  # RICE formula

    def test_rice_calculation_multiple_initiatives(self):
        """Test RICE calculation with multiple initiatives"""
        config = {"scoring": {"rice_weights": {
            "reach_weight": 1.0,
            "impact_weight": 1.0,
            "confidence_weight": 1.0,
            "effort_weight": 1.0
        }}}

        calculator = RICECalculator(config)
        initiatives = [
            {"name": "Initiative A", "reach": 10, "impact": 8, "confidence": 7, "effort": 5},
            {"name": "Initiative B", "reach": 5, "impact": 6, "confidence": 9, "effort": 3},
            {"name": "Initiative C", "reach": 8, "impact": 9, "confidence": 6, "effort": 8}
        ]

        scores = calculator.calculate_rice(initiatives)
        assert len(scores) == 3
        assert scores[0]["rice_score"] >= scores[1]["rice_score"]  # Should be sorted

    def test_rice_calculation_zero_effort(self):
        """Test RICE calculation with zero effort"""
        config = {"scoring": {"rice_weights": {
            "reach_weight": 1.0,
            "impact_weight": 1.0,
            "confidence_weight": 1.0,
            "effort_weight": 1.0
        }}}

        calculator = RICECalculator(config)
        initiative = {
            "name": "Zero Effort",
            "reach": 10,
            "impact": 8,
            "confidence": 7,
            "effort": 0
        }

        scores = calculator.calculate_rice([initiative])
        assert scores[0]["rice_score"] == 0  # Should handle division by zero

    def test_get_top_initiatives(self):
        """Test getting top initiatives"""
        config = {"scoring": {"rice_weights": {
            "reach_weight": 1.0,
            "impact_weight": 1.0,
            "confidence_weight": 1.0,
            "effort_weight": 1.0
        }}}

        calculator = RICECalculator(config)
        initiatives = generate_sample_initiatives()
        scores = calculator.calculate_rice(initiatives)

        top_2 = calculator.get_top_initiatives(scores, 2)
        assert len(top_2) == 2
        assert top_2[0]["rice_score"] >= top_2[1]["rice_score"]

class TestImpactEffortMatrix:
    """Test Impact/Effort matrix functionality"""

    def test_quadrant_determination(self):
        """Test correct quadrant determination"""
        config = {"scoring": {"impact_effort_thresholds": {
            "high_impact": 7.0,
            "high_effort": 7.0,
            "low_impact": 4.0,
            "low_effort": 4.0
        }}}

        matrix = ImpactEffortMatrix(config)

        # Test Quick Wins (high impact, low effort)
        point = matrix._calculate_single_point({"name": "Quick Win", "impact": 8, "effort": 3})
        assert point.quadrant.value == "Quick Wins"

        # Test Big Bets (high impact, high effort)
        point = matrix._calculate_single_point({"name": "Big Bet", "impact": 8, "effort": 8})
        assert point.quadrant.value == "Big Bets"

        # Test Fill-Ins (low impact, low effort)
        point = matrix._calculate_single_point({"name": "Fill-In", "impact": 3, "effort": 3})
        assert point.quadrant.value == "Fill-Ins"

        # Test Money Pits (low impact, high effort)
        point = matrix._calculate_single_point({"name": "Money Pit", "impact": 3, "effort": 8})
        assert point.quadrant.value == "Money Pits"

    def test_matrix_calculation(self):
        """Test matrix calculation with multiple initiatives"""
        config = {"scoring": {"impact_effort_thresholds": {
            "high_impact": 7.0,
            "high_effort": 7.0,
            "low_impact": 4.0,
            "low_effort": 4.0
        }}}

        matrix = ImpactEffortMatrix(config)
        initiatives = [
            {"name": "Quick Win", "impact": 8, "effort": 3},
            {"name": "Big Bet", "impact": 8, "effort": 8},
            {"name": "Fill-In", "impact": 3, "effort": 3},
            {"name": "Money Pit", "impact": 3, "effort": 8}
        ]

        results = matrix.calculate_matrix(initiatives)
        assert len(results) == 4

        # Check that each initiative is in correct quadrant
        quick_wins = [r for r in results if r["quadrant"] == "Quick Wins"]
        big_bets = [r for r in results if r["quadrant"] == "Big Bets"]
        fill_ins = [r for r in results if r["quadrant"] == "Fill-Ins"]
        money_pits = [r for r in results if r["quadrant"] == "Money Pits"]

        assert len(quick_wins) == 1
        assert len(big_bets) == 1
        assert len(fill_ins) == 1
        assert len(money_pits) == 1

    def test_get_quadrant_initiatives(self):
        """Test getting initiatives by quadrant"""
        config = {"scoring": {"impact_effort_thresholds": {
            "high_impact": 7.0,
            "high_effort": 7.0,
            "low_impact": 4.0,
            "low_effort": 4.0
        }}}

        matrix = ImpactEffortMatrix(config)
        initiatives = generate_sample_initiatives()
        results = matrix.calculate_matrix(initiatives)

        quick_wins = matrix.get_quick_wins(results)
        big_bets = matrix.get_big_bets(results)
        fill_ins = matrix.get_fill_ins(results)
        money_pits = matrix.get_money_pits(results)

        assert len(quick_wins) + len(big_bets) + len(fill_ins) + len(money_pits) == len(initiatives)

    def test_quadrant_summary(self):
        """Test quadrant summary generation"""
        config = {"scoring": {"impact_effort_thresholds": {
            "high_impact": 7.0,
            "high_effort": 7.0,
            "low_impact": 4.0,
            "low_effort": 4.0
        }}}

        matrix = ImpactEffortMatrix(config)
        initiatives = [
            {"name": "Quick Win 1", "impact": 8, "effort": 3},
            {"name": "Quick Win 2", "impact": 9, "effort": 4},
            {"name": "Big Bet", "impact": 8, "effort": 8},
            {"name": "Fill-In", "impact": 3, "effort": 3}
        ]

        results = matrix.calculate_matrix(initiatives)
        summary = matrix.get_quadrant_summary(results)

        assert "Quick Wins" in summary
        assert "Big Bets" in summary
        assert "Fill-Ins" in summary

        # Check Quick Wins summary
        quick_wins_summary = summary["Quick Wins"]
        assert quick_wins_summary["count"] == 2
        assert quick_wins_summary["avg_impact"] == 8.5
        assert quick_wins_summary["avg_effort"] == 3.5

class TestInitiativeScorer:
    """Test combined initiative scoring"""

    def test_combined_scoring(self):
        """Test combined RICE and Impact/Effort scoring"""
        config = {
            "scoring": {
                "rice_weights": {
                    "reach_weight": 1.0,
                    "impact_weight": 1.0,
                    "confidence_weight": 1.0,
                    "effort_weight": 1.0
                },
                "impact_effort_thresholds": {
                    "high_impact": 7.0,
                    "high_effort": 7.0,
                    "low_impact": 4.0,
                    "low_effort": 4.0
                }
            }
        }

        scorer = InitiativeScorer(config)
        initiatives = generate_sample_initiatives()

        results = scorer.score_initiatives(initiatives)

        # Check that all expected data is present
        assert "rice_scores" in results
        assert "impact_effort_matrix" in results
        assert "combined_scores" in results
        assert "quick_wins" in results
        assert "big_bets" in results
        assert "quadrant_summary" in results

        # Check combined scores structure
        combined = results["combined_scores"]
        assert len(combined) == len(initiatives)
        for score in combined:
            assert "initiative" in score
            assert "rice_score" in score
            assert "impact" in score
            assert "effort" in score
            assert "quadrant" in score
            assert "combined_priority" in score

        # Check that scores are sorted by combined priority
        for i in range(1, len(combined)):
            assert combined[i-1]["combined_priority"] >= combined[i]["combined_priority"]

def test_generate_sample_initiatives():
    """Test sample initiative generation"""
    initiatives = generate_sample_initiatives()
    assert len(initiatives) > 0

    for initiative in initiatives:
        assert "name" in initiative
        assert "description" in initiative
        assert "reach" in initiative
        assert "impact" in initiative
        assert "confidence" in initiative
        assert "effort" in initiative

        # Check that scores are within expected ranges
        assert 1 <= initiative["reach"] <= 10
        assert 1 <= initiative["impact"] <= 10
        assert 1 <= initiative["confidence"] <= 10
        assert 1 <= initiative["effort"] <= 10