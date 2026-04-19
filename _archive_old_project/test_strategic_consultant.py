#!/usr/bin/env python3
"""
Test the Strategic Consultant implementation
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.strategic_consultant import StrategicConsultant

async def test_strategic_consultant():
    """Test the strategic consultant with sample questions"""
    print("🧪 Testing Strategic Consultant")
    print("=" * 50)

    consultant = StrategicConsultant()

    # Test questions
    test_questions = [
        "How do we scale from 100 to 10,000 users with current team?",
        "What's the fastest path to enterprise security compliance?",
        "Should we rebuild or refactor the legacy payment system?",
        "How is our security? Could we reasonably sell this?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n📋 Test {i}: {question}")
        print("-" * 60)

        try:
            recommendation = await consultant.analyze_strategic_question(question)

            print(f"✅ Analysis Complete")
            print(f"🎯 Strategic Direction: {recommendation.direction.value.replace('_', ' ').title()}")
            print(f"📝 Rationale: {recommendation.rationale}")
            print(f"🚀 Immediate Actions: {len(recommendation.immediate_actions)}")
            print(f"📋 Success Metrics: {len(recommendation.success_metrics)}")
            print(f"⚠️  Early Warnings: {len(recommendation.early_warnings)}")

        except Exception as e:
            print(f"❌ Error: {e}")

    print(f"\n🎯 Strategic Consultant Test Complete!")

def test_current_state_analysis():
    """Test current state analysis"""
    print("\n🔍 Testing Current State Analysis")
    print("=" * 50)

    consultant = StrategicConsultant()

    try:
        import asyncio
        current_state = asyncio.run(consultant._analyze_current_state())

        print("✅ Current State Analysis Complete")
        print(f"📁 Project Structure: {len(current_state.project_structure.get('directories', []))} directories")
        print(f"🛠️  Tech Stack: {', '.join(current_state.tech_stack) or 'Not detected'}")
        print(f"📚 Documentation Quality: {current_state.documentation_quality:.2f}")
        print(f"📊 Code Quality Metrics: {len(current_state.code_quality_metrics)} metrics")
        print(f"👥 Team Capacity: {current_state.team_capacity.get('team_size', 'Unknown')}")
        print(f"🗺️  Current Roadmap: {'Present' if current_state.current_roadmap else 'Not found'}")
        print(f"⚠️  Risks: {len(current_state.risks)} identified")
        print(f"💡 Opportunities: {len(current_state.opportunities)} identified")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run current state analysis first
    test_current_state_analysis()

    # Run strategic analysis tests
    asyncio.run(test_strategic_consultant())