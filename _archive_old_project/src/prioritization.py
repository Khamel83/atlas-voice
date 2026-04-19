#!/usr/bin/env python3
"""
OOS Consultant Prioritization Utilities
RICE scoring and Impact/Effort matrix calculations
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Quadrant(Enum):
    QUICK_WINS = "Quick Wins"
    BIG_BETS = "Big Bets"
    FILL_INS = "Fill-Ins"
    MONEY_PITS = "Money Pits"

@dataclass
class RICEScore:
    """RICE scoring components"""
    reach: float
    impact: float
    confidence: float
    effort: float
    rice_score: float

@dataclass
class ImpactEffortPoint:
    """Point in Impact/Effort matrix"""
    name: str
    impact: float
    effort: float
    quadrant: Quadrant

class RICECalculator:
    """Calculate RICE scores for initiatives"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config["scoring"]["rice_weights"]

    def calculate_rice(self, initiatives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate RICE scores for a list of initiatives"""
        results = []

        for initiative in initiatives:
            try:
                rice_score = self._calculate_single_rice(initiative)
                result = {
                    "initiative": initiative.get("name", "Unknown"),
                    "description": initiative.get("description", ""),
                    "reach": rice_score.reach,
                    "impact": rice_score.impact,
                    "confidence": rice_score.confidence,
                    "effort": rice_score.effort,
                    "rice_score": rice_score.rice_score,
                    "normalized_score": self._normalize_score(rice_score.rice_score)
                }
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to calculate RICE for {initiative.get('name', 'Unknown')}: {e}")
                continue

        # Sort by RICE score (descending)
        results.sort(key=lambda x: x["rice_score"], reverse=True)
        return results

    def _calculate_single_rice(self, initiative: Dict[str, Any]) -> RICEScore:
        """Calculate RICE score for a single initiative"""
        reach = float(initiative.get("reach", 1))
        impact = float(initiative.get("impact", 1))
        confidence = float(initiative.get("confidence", 0.5))
        effort = float(initiative.get("effort", 1))

        # Apply weights
        weighted_reach = reach * self.weights["reach_weight"]
        weighted_impact = impact * self.weights["impact_weight"]
        weighted_confidence = confidence * self.weights["confidence_weight"]
        weighted_effort = effort * self.weights["effort_weight"]

        # Calculate RICE score: (Reach * Impact * Confidence) / Effort
        if weighted_effort > 0:
            rice_score = (weighted_reach * weighted_impact * weighted_confidence) / weighted_effort
        else:
            rice_score = 0

        return RICEScore(
            reach=reach,
            impact=impact,
            confidence=confidence,
            effort=effort,
            rice_score=rice_score
        )

    def _normalize_score(self, score: float) -> float:
        """Normalize RICE score to 0-100 scale"""
        # Simple normalization - in practice might use min/max scaling
        return min(100, max(0, score * 10))

    def get_top_initiatives(self, rice_scores: List[Dict[str, Any]], count: int = 5) -> List[Dict[str, Any]]:
        """Get top N initiatives by RICE score"""
        return rice_scores[:count]

class ImpactEffortMatrix:
    """Calculate Impact/Effort matrix and categorize initiatives"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.thresholds = config["scoring"]["impact_effort_thresholds"]

    def calculate_matrix(self, initiatives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate Impact/Effort matrix for initiatives"""
        results = []

        for initiative in initiatives:
            try:
                point = self._calculate_single_point(initiative)
                result = {
                    "initiative": initiative.get("name", "Unknown"),
                    "description": initiative.get("description", ""),
                    "impact": point.impact,
                    "effort": point.effort,
                    "quadrant": point.quadrant.value,
                    "priority_score": self._calculate_priority_score(point.impact, point.effort)
                }
                results.append(result)
            except Exception as e:
                logger.warning(f"Failed to calculate Impact/Effort for {initiative.get('name', 'Unknown')}: {e}")
                continue

        return results

    def _calculate_single_point(self, initiative: Dict[str, Any]) -> ImpactEffortPoint:
        """Calculate single point in Impact/Effort matrix"""
        impact = float(initiative.get("impact", 5))
        effort = float(initiative.get("effort", 5))

        quadrant = self._determine_quadrant(impact, effort)

        return ImpactEffortPoint(
            name=initiative.get("name", "Unknown"),
            impact=impact,
            effort=effort,
            quadrant=quadrant
        )

    def _determine_quadrant(self, impact: float, effort: float) -> Quadrant:
        """Determine which quadrant an initiative falls into"""
        high_impact = self.thresholds["high_impact"]
        high_effort = self.thresholds["high_effort"]
        low_impact = self.thresholds["low_impact"]
        low_effort = self.thresholds["low_effort"]

        if impact >= high_impact and effort <= low_effort:
            return Quadrant.QUICK_WINS
        elif impact >= high_impact and effort >= high_effort:
            return Quadrant.BIG_BETS
        elif impact <= low_impact and effort <= low_effort:
            return Quadrant.FILL_INS
        else:
            return Quadrant.MONEY_PITS

    def _calculate_priority_score(self, impact: float, effort: float) -> float:
        """Calculate priority score (impact/effort ratio)"""
        if effort > 0:
            return impact / effort
        return 0

    def get_quick_wins(self, initiatives: List[Dict[str, Any]], max_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get quick wins from initiatives"""
        quick_wins = [i for i in initiatives if i.get("quadrant") == Quadrant.QUICK_WINS.value]
        quick_wins.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

        if max_count:
            return quick_wins[:max_count]
        return quick_wins

    def get_big_bets(self, initiatives: List[Dict[str, Any]], max_count: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get big bets from initiatives"""
        big_bets = [i for i in initiatives if i.get("quadrant") == Quadrant.BIG_BETS.value]
        big_bets.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

        if max_count:
            return big_bets[:max_count]
        return big_bets

    def get_fill_ins(self, initiatives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get fill-ins from initiatives"""
        return [i for i in initiatives if i.get("quadrant") == Quadrant.FILL_INS.value]

    def get_money_pits(self, initiatives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get money pits from initiatives"""
        return [i for i in initiatives if i.get("quadrant") == Quadrant.MONEY_PITS.value]

    def get_quadrant_summary(self, matrix: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Get summary statistics for each quadrant"""
        summary = {}

        for quadrant in Quadrant:
            quadrant_items = [i for i in matrix if i.get("quadrant") == quadrant.value]
            if quadrant_items:
                summary[quadrant.value] = {
                    "count": len(quadrant_items),
                    "avg_impact": sum(i.get("impact", 0) for i in quadrant_items) / len(quadrant_items),
                    "avg_effort": sum(i.get("effort", 0) for i in quadrant_items) / len(quadrant_items),
                    "avg_priority": sum(i.get("priority_score", 0) for i in quadrant_items) / len(quadrant_items),
                    "top_initiatives": [i.get("initiative") for i in quadrant_items[:3]]
                }

        return summary

class InitiativeScorer:
    """Combine RICE and Impact/Effort scoring for comprehensive prioritization"""

    def __init__(self, config: Dict[str, Any]):
        self.rice_calculator = RICECalculator(config)
        self.impact_effort_matrix = ImpactEffortMatrix(config)

    def score_initiatives(self, initiatives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score initiatives using both RICE and Impact/Effort"""
        # Calculate RICE scores
        rice_scores = self.rice_calculator.calculate_rice(initiatives)

        # Calculate Impact/Effort matrix
        ie_matrix = self.impact_effort_matrix.calculate_matrix(initiatives)

        # Combine results
        combined_scores = self._combine_scores(rice_scores, ie_matrix)

        # Get categorizations
        quick_wins = self.impact_effort_matrix.get_quick_wins(ie_matrix)
        big_bets = self.impact_effort_matrix.get_big_bets(ie_matrix)

        return {
            "rice_scores": rice_scores,
            "impact_effort_matrix": ie_matrix,
            "combined_scores": combined_scores,
            "quick_wins": quick_wins,
            "big_bets": big_bets,
            "quadrant_summary": self.impact_effort_matrix.get_quadrant_summary(ie_matrix)
        }

    def _combine_scores(self, rice_scores: List[Dict[str, Any]],
                       ie_matrix: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine RICE and Impact/Effort scores"""
        combined = []

        # Create lookup dictionary for Impact/Effort data
        ie_lookup = {i["initiative"]: i for i in ie_matrix}

        for rice in rice_scores:
            initiative_name = rice["initiative"]
            ie_data = ie_lookup.get(initiative_name, {})

            combined_score = {
                "initiative": initiative_name,
                "description": rice["description"],
                "rice_score": rice["rice_score"],
                "rice_normalized": rice["normalized_score"],
                "impact": ie_data.get("impact", 5),
                "effort": ie_data.get("effort", 5),
                "quadrant": ie_data.get("quadrant", "Unknown"),
                "priority_score": ie_data.get("priority_score", 0),
                "combined_priority": self._calculate_combined_priority(rice, ie_data)
            }
            combined.append(combined_score)

        # Sort by combined priority
        combined.sort(key=lambda x: x["combined_priority"], reverse=True)
        return combined

    def _calculate_combined_priority(self, rice_data: Dict[str, Any],
                                   ie_data: Dict[str, Any]) -> float:
        """Calculate combined priority score"""
        rice_weight = 0.6
        ie_weight = 0.4

        rice_normalized = rice_data.get("normalized_score", 0) / 100
        ie_priority = ie_data.get("priority_score", 0) / 10  # Normalize to 0-1

        return (rice_normalized * rice_weight) + (ie_priority * ie_weight)

# Utility functions
def validate_initiative(initiative: Dict[str, Any]) -> bool:
    """Validate initiative has required fields"""
    required_fields = ["name", "reach", "impact", "confidence", "effort"]
    return all(field in initiative for field in required_fields)

def generate_sample_initiatives() -> List[Dict[str, Any]]:
    """Generate sample initiatives for testing"""
    return [
        {
            "name": "Process Automation",
            "description": "Automate manual data entry processes",
            "reach": 8,
            "impact": 9,
            "confidence": 8,
            "effort": 6
        },
        {
            "name": "System Migration",
            "description": "Migrate legacy system to modern platform",
            "reach": 9,
            "impact": 8,
            "confidence": 6,
            "effort": 9
        },
        {
            "name": "UI Redesign",
            "description": "Redesign user interface for better UX",
            "reach": 6,
            "impact": 7,
            "confidence": 9,
            "effort": 4
        },
        {
            "name": "Documentation Update",
            "description": "Update outdated documentation",
            "reach": 4,
            "impact": 3,
            "confidence": 10,
            "effort": 3
        }
    ]