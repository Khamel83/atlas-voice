#!/usr/bin/env python3
"""
Simple test for OOS Consultant components
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.consultant_flow import ConsultantFlow
from src.prioritization import generate_sample_initiatives, InitiativeScorer
import yaml

def test_configuration():
    """Test configuration loading"""
    print("🧪 Testing Configuration Loading")
    print("=" * 40)

    try:
        with open("config/consultant.yaml", "r") as f:
            config = yaml.safe_load(f)

        print("✅ Configuration loaded successfully")
        print(f"  • Intake questions: {len(config['intake_questions'])}")
        print(f"  • Output artifacts: {len(config['output']['artifacts'])}")
        print(f"  • Portfolio limits: {config['portfolio']['max_quick_wins']} quick wins, {config['portfolio']['max_big_bets']} big bets")

        return config
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return None

def test_prioritization():
    """Test prioritization functionality"""
    print("\n🧪 Testing Prioritization")
    print("=" * 40)

    try:
        config = test_configuration()
        if not config:
            return

        scorer = InitiativeScorer(config)
        initiatives = generate_sample_initiatives()

        print(f"📊 Generated {len(initiatives)} sample initiatives")

        results = scorer.score_initiatives(initiatives)

        print(f"📈 Results:")
        print(f"  • RICE scores calculated: {len(results['rice_scores'])}")
        print(f"  • Impact/Effort matrix: {len(results['impact_effort_matrix'])}")
        print(f"  • Quick wins identified: {len(results['quick_wins'])}")
        print(f"  • Big bets identified: {len(results['big_bets'])}")

        # Show top initiative
        if results['combined_scores']:
            top = results['combined_scores'][0]
            print(f"  • Top initiative: {top['initiative']} (RICE: {top['rice_score']:.2f}, Priority: {top['combined_priority']:.2f})")

        print("✅ Prioritization test successful")
        return True
    except Exception as e:
        print(f"❌ Prioritization test failed: {e}")
        return False

def test_templates():
    """Test template files"""
    print("\n🧪 Testing Templates")
    print("=" * 40)

    template_files = [
        "templates/a3.md.j2",
        "templates/ost.mmd.j2",
        "templates/impact_effort.csv.j2",
        "templates/rice.csv.j2",
        "templates/plan.md.j2"
    ]

    missing_templates = []
    for template_file in template_files:
        if Path(template_file).exists():
            print(f"✅ {template_file}")
        else:
            print(f"❌ {template_file}")
            missing_templates.append(template_file)

    if missing_templates:
        print(f"❌ Missing {len(missing_templates)} templates")
        return False
    else:
        print("✅ All templates present")
        return True

def test_consultant_flow():
    """Test consultant flow initialization"""
    print("\n🧪 Testing Consultant Flow")
    print("=" * 40)

    try:
        # Create a mock configuration
        mock_config = {
            "intake_questions": {
                "goal": {"text": "What's the goal?", "required": True},
                "current_state": {"text": "Current state?", "required": True},
                "stakeholders": {"text": "Stakeholders?", "required": True}
            },
            "output": {
                "base_path": "./test_consulting",
                "artifacts": {"intake": "intake.json"}
            },
            "external": {"allow_web": False},
            "planning": {"time_horizons": ["30 days", "60 days", "90 days"]},
            "portfolio": {"max_quick_wins": 3, "max_big_bets": 2},
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

        # Mock the config loader
        import src.consultant_flow
        original_load_config = src.consultant_flow.load_config
        src.consultant_flow.load_config = lambda x: mock_config

        try:
            flow = ConsultantFlow("TestProject")
            print("✅ ConsultantFlow initialized successfully")

            # Test question retrieval
            question = flow.get_current_question()
            if question:
                print(f"✅ First question: {question['id']} - {question['text']}")
            else:
                print("❌ No questions available")
                return False

            # Test answer submission
            success = flow.submit_answer("goal", "Test goal")
            print(f"✅ Answer submission: {'successful' if success else 'failed'}")

            # Test status
            status = flow.get_status()
            print(f"✅ Status retrieved: {status['state']}")

            return True
        finally:
            # Restore original config loader
            src.consultant_flow.load_config = original_load_config

    except Exception as e:
        print(f"❌ Consultant flow test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 OOS Consultant Integration Test")
    print("=" * 50)

    results = {
        "configuration": test_configuration(),
        "prioritization": test_prioritization(),
        "templates": test_templates(),
        "flow": test_consultant_flow()
    }

    print("\n📊 Test Results Summary")
    print("=" * 40)

    passed = 0
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 Overall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! OOS Consultant is ready for use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()