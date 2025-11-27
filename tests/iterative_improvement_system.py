#!/usr/bin/env python3
"""
Iterative Improvement System
Automatically iterate prompt improvements until 90% authenticity achieved
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import statistics
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent))

from final_comprehensive_system import FinalStylePreservationSystem
from authenticity_testing_system import LetterComparisonTester

class IterativeImprovementEngine:
    """Engine to iteratively improve style preservation until 90% threshold"""

    def __init__(self):
        self.target_threshold = 0.90
        self.max_iterations = 10
        self.current_iteration = 0
        self.improvement_history = []

        # Paths
        self.base_dir = Path("/Users/khamel83/dev/atlas-voice")
        self.data_dir = self.base_dir / "data"
        self.prompts_dir = self.base_dir / "prompts"
        self.tests_dir = self.base_dir / "tests"

        # Initialize systems
        self.style_system = FinalStylePreservationSystem(str(self.data_dir))
        self.tester = None

    def initialize_testing_system(self):
        """Initialize the testing system with required files"""
        reference_analysis = self.data_dir / "final_comprehensive_analysis.json"
        original_letters = self.data_dir / "omars_personal_letters.txt"

        if not reference_analysis.exists() or not original_letters.exists():
            print("⚠️  Required files missing. Running initial analysis...")
            self.run_initial_analysis()

        self.tester = LetterComparisonTester(str(reference_analysis), str(original_letters))

    def run_initial_analysis(self):
        """Run initial comprehensive analysis"""
        print("🔄 Running initial analysis...")
        analysis, prompt = self.style_system.run_full_analysis(email_limit=5000)
        self.style_system.save_results(analysis, prompt, str(self.prompts_dir))
        print("✅ Initial analysis complete")

    def analyze_test_results(self, results: Dict) -> Dict:
        """Analyze test results to identify improvement areas"""
        if not results or 'test_results' not in results:
            return {'needs_improvement': True, 'issues': ['No test results available']}

        test_results = results['test_results']
        success_rate = results.get('success_rate', 0)
        avg_authenticity = results.get('average_new_authenticity', 0)

        analysis = {
            'success_rate': success_rate,
            'avg_authenticity': avg_authenticity,
            'threshold_met': success_rate >= self.target_threshold,
            'needs_improvement': success_rate < self.target_threshold,
            'issues': []
        }

        if success_rate < self.target_threshold:
            # Analyze component scores to identify weak areas
            component_issues = self.identify_component_weaknesses(test_results)
            analysis['issues'] = component_issues

        return analysis

    def identify_component_weaknesses(self, test_results: List[Dict]) -> List[str]:
        """Identify which components need improvement"""
        issues = []

        # Analyze authenticity scores
        low_scores = [r for r in test_results if r['new_authenticity'] < 0.8]

        if len(low_scores) > len(test_results) * 0.3:  # More than 30% are low
            issues.append("Overall authenticity too low")

        if any(r['new_authenticity'] < 0.6 for r in test_results):
            issues.append("Some segments severely lacking authenticity")

        improvements = [r['improvement'] for r in test_results]
        avg_improvement = statistics.mean(improvements) if improvements else 0

        if avg_improvement < 0.1:
            issues.append("Insufficient improvement over original")

        return issues

    def generate_improved_prompt(self, current_prompt: str, issues: List[str]) -> str:
        """Generate improved prompt based on identified issues"""
        print(f"🔧 Generating improved prompt to address: {', '.join(issues)}")

        # Load current analysis
        analysis_file = self.data_dir / "final_comprehensive_analysis.json"
        if analysis_file.exists():
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
        else:
            print("❌ No analysis file found")
            return current_prompt

        # Adjust prompt based on issues
        improvements = []

        if "Overall authenticity too low" in issues:
            improvements.append("CRITICAL: Emphasize exact function word patterns")
            improvements.append("MANDATORY: Match sentence rhythm precisely")

        if "Insufficient improvement over original" in issues:
            improvements.append("FOCUS: Personal expression patterns are essential")
            improvements.append("PRIORITY: Casual markers must be natural")

        if "severely lacking authenticity" in issues:
            improvements.append("STRICT: No generic AI language allowed")
            improvements.append("ENFORCE: Vocabulary complexity must match exactly")

        # Create enhanced prompt
        enhanced_sections = [
            "# ENHANCED WRITING STYLE PRESERVATION SYSTEM",
            f"## ITERATION {self.current_iteration + 1} - CRITICAL IMPROVEMENTS REQUIRED",
            "",
            "### IDENTIFIED ISSUES TO RESOLVE:",
        ]

        for issue in issues:
            enhanced_sections.append(f"- {issue}")

        enhanced_sections.extend([
            "",
            "### MANDATORY IMPROVEMENTS:",
        ])

        for improvement in improvements:
            enhanced_sections.append(f"- {improvement}")

        enhanced_sections.extend([
            "",
            "### ORIGINAL PROMPT (ENHANCED):",
            "",
            current_prompt,
            "",
            "## STRICT ENFORCEMENT RULES",
            "",
            "1. **NEVER use generic AI language**",
            "2. **ALWAYS match function word ratios exactly**",
            "3. **PRESERVE sentence rhythm at all costs**",
            "4. **INTEGRATE personal expressions naturally**",
            "5. **MAINTAIN vocabulary complexity precisely**",
            "",
            f"## SUCCESS REQUIREMENT: {self.target_threshold:.0%} AUTHENTICITY",
            "",
            "This prompt MUST achieve 90%+ authenticity scores.",
            "Any score below 90% indicates system failure.",
            "Prioritize authenticity over all other considerations."
        ])

        enhanced_prompt = '\n'.join(enhanced_sections)

        # Limit length
        if len(enhanced_prompt) > 4000:
            # Keep the most important parts
            keep_sections = enhanced_sections[:50]  # First 50 lines
            enhanced_prompt = '\n'.join(keep_sections)

        return enhanced_prompt

    def run_iteration(self) -> Dict:
        """Run one iteration of testing and improvement"""
        self.current_iteration += 1
        print(f"\n🔄 ITERATION {self.current_iteration}")
        print("=" * 40)

        # Get current prompt
        prompt_file = self.prompts_dir / "final_style_preservation_prompt.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                current_prompt = f.read()
        else:
            print("❌ No prompt file found")
            return {}

        # Run tests
        print("🧪 Running authenticity tests...")
        results = self.tester.run_comparison_test(str(prompt_file))

        if not results:
            print("❌ Testing failed")
            return {}

        # Analyze results
        analysis = self.analyze_test_results(results)

        iteration_result = {
            'iteration': self.current_iteration,
            'timestamp': datetime.now().isoformat(),
            'success_rate': analysis['success_rate'],
            'avg_authenticity': analysis['avg_authenticity'],
            'threshold_met': analysis['threshold_met'],
            'issues': analysis['issues'],
            'test_results': results
        }

        self.improvement_history.append(iteration_result)

        # Check if threshold met
        if analysis['threshold_met']:
            print(f"🎉 SUCCESS! Achieved {analysis['success_rate']:.1%} success rate")
            return iteration_result

        # Generate improved prompt
        if analysis['needs_improvement'] and self.current_iteration < self.max_iterations:
            improved_prompt = self.generate_improved_prompt(current_prompt, analysis['issues'])

            # Save improved prompt
            iteration_prompt_file = self.prompts_dir / f"prompt_iteration_{self.current_iteration}.txt"
            with open(iteration_prompt_file, 'w') as f:
                f.write(improved_prompt)

            # Update main prompt file
            with open(prompt_file, 'w') as f:
                f.write(improved_prompt)

            print(f"💾 Saved improved prompt for iteration {self.current_iteration}")

        return iteration_result

    def run_full_improvement_cycle(self) -> Dict:
        """Run complete improvement cycle until threshold achieved"""
        print("🚀 STARTING ITERATIVE IMPROVEMENT CYCLE")
        print(f"🎯 Target: {self.target_threshold:.0%} authenticity")
        print(f"📊 Max iterations: {self.max_iterations}")
        print("=" * 60)

        # Initialize
        self.initialize_testing_system()

        # Run iterations
        while self.current_iteration < self.max_iterations:
            result = self.run_iteration()

            if not result:
                print("❌ Iteration failed")
                break

            if result['threshold_met']:
                print(f"\n🎉 SUCCESS ACHIEVED IN {self.current_iteration} ITERATIONS!")
                break

            print(f"📊 Iteration {self.current_iteration} results:")
            print(f"   Success rate: {result['success_rate']:.1%}")
            print(f"   Avg authenticity: {result['avg_authenticity']:.3f}")
            print(f"   Issues: {', '.join(result['issues'])}")

        # Save complete history
        history_file = self.tests_dir / "improvement_history.json"
        with open(history_file, 'w') as f:
            json.dump({
                'target_threshold': self.target_threshold,
                'total_iterations': self.current_iteration,
                'final_success': self.improvement_history[-1]['threshold_met'] if self.improvement_history else False,
                'improvement_history': self.improvement_history
            }, f, indent=2)

        print(f"💾 Complete improvement history saved to: {history_file}")

        # Return final summary
        if self.improvement_history:
            final_result = self.improvement_history[-1]
            return {
                'success': final_result['threshold_met'],
                'iterations_used': self.current_iteration,
                'final_success_rate': final_result['success_rate'],
                'final_authenticity': final_result['avg_authenticity'],
                'improvement_history': self.improvement_history
            }
        else:
            return {'success': False, 'iterations_used': 0}

def main():
    """Main execution for iterative improvement"""
    engine = IterativeImprovementEngine()
    results = engine.run_full_improvement_cycle()

    print("\n" + "=" * 60)
    print("🏁 ITERATIVE IMPROVEMENT COMPLETE")
    print("=" * 60)

    if results['success']:
        print(f"✅ SUCCESS! Achieved 90%+ authenticity in {results['iterations_used']} iterations")
        print(f"📊 Final success rate: {results['final_success_rate']:.1%}")
        print(f"🎯 Final authenticity: {results['final_authenticity']:.3f}")
    else:
        print(f"❌ Failed to achieve 90% threshold in {results['iterations_used']} iterations")

    return results

if __name__ == "__main__":
    main()
