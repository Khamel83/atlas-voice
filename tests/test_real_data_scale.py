"""
Test Atlas Voice with real email data at different time scales.

This critical test answers the question:
Does analyzing 20 years of emails produce a better voice profile than 1 week?

Test methodology:
1. Load the real email data (18K+ emails, 8.6M words from 2001-2024)
2. Create subsets by date: 1 week, 1 month, 1 year, 5 years, 20 years
3. Analyze each subset to extract voice patterns
4. Compare results to see how patterns stabilize over time
5. Generate prompts from each to validate quality
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from atlas_voice.services import ImportService, AnalyzerService, GeneratorService


# Path to the real email data
EMAIL_DATA_PATH = Path("/Users/khamel83/Library/Mobile Documents/com~apple~CloudDocs/Code/emailprocessing/extracted_emails.csv")


@pytest.mark.skipif(not EMAIL_DATA_PATH.exists(), reason="Real email data not available")
class TestRealDataScale:
    """Test voice analysis at different time scales using real data."""

    @classmethod
    def setup_class(cls):
        """Load the real email data once for all tests."""
        print(f"\n{'='*70}")
        print("LOADING REAL EMAIL DATA")
        print(f"{'='*70}\n")

        # Load email data
        df = pd.read_csv(EMAIL_DATA_PATH)

        # Filter for human emails only (assuming there's a 'from' or 'is_human' column)
        # Adapt this based on actual column names
        if 'body' in df.columns or 'content' in df.columns:
            content_col = 'body' if 'body' in df.columns else 'content'
            cls.df = df[[content_col]].dropna()
            cls.df.columns = ['text']
        else:
            pytest.skip("Email data format not recognized")

        # Try to extract dates if available
        if 'date' in df.columns:
            cls.df['date'] = pd.to_datetime(df['date'], errors='coerce')
            cls.df = cls.df.dropna(subset=['date'])
            cls.has_dates = True
        else:
            cls.has_dates = False
            print("⚠ No date column found - testing with random samples")

        print(f"Loaded {len(cls.df):,} text samples")
        if cls.has_dates:
            print(f"Date range: {cls.df['date'].min()} to {cls.df['date'].max()}")
        print()

    def test_1_week_sample(self):
        """Test voice analysis with 1 week of data."""
        if not self.has_dates:
            pytest.skip("No dates available")

        # Get most recent week
        max_date = self.df['date'].max()
        one_week_ago = max_date - timedelta(days=7)
        subset = self.df[self.df['date'] >= one_week_ago]

        self._analyze_and_report("1 Week", subset['text'].tolist())

    def test_1_month_sample(self):
        """Test voice analysis with 1 month of data."""
        if not self.has_dates:
            pytest.skip("No dates available")

        # Get most recent month
        max_date = self.df['date'].max()
        one_month_ago = max_date - timedelta(days=30)
        subset = self.df[self.df['date'] >= one_month_ago]

        self._analyze_and_report("1 Month", subset['text'].tolist())

    def test_1_year_sample(self):
        """Test voice analysis with 1 year of data."""
        if not self.has_dates:
            pytest.skip("No dates available")

        # Get most recent year
        max_date = self.df['date'].max()
        one_year_ago = max_date - timedelta(days=365)
        subset = self.df[self.df['date'] >= one_year_ago]

        self._analyze_and_report("1 Year", subset['text'].tolist())

    def test_5_years_sample(self):
        """Test voice analysis with 5 years of data."""
        if not self.has_dates:
            pytest.skip("No dates available")

        # Get most recent 5 years
        max_date = self.df['date'].max()
        five_years_ago = max_date - timedelta(days=365*5)
        subset = self.df[self.df['date'] >= five_years_ago]

        self._analyze_and_report("5 Years", subset['text'].tolist())

    def test_20_years_all_data(self):
        """Test voice analysis with all 20 years of data."""
        self._analyze_and_report("20 Years (All Data)", self.df['text'].tolist())

    def test_random_samples_comparison(self):
        """Compare random samples of different sizes (if no dates)."""
        if self.has_dates:
            pytest.skip("Dates available, using date-based tests instead")

        sizes = [100, 500, 1000, 5000, len(self.df)]

        for size in sizes:
            if size > len(self.df):
                size = len(self.df)

            subset = self.df.sample(n=size, random_state=42)
            self._analyze_and_report(f"{size} Random Samples", subset['text'].tolist())

    def _analyze_and_report(self, name: str, texts: list):
        """Analyze a subset and report key metrics."""
        print(f"\n{'='*70}")
        print(f"ANALYZING: {name}")
        print(f"{'='*70}\n")

        if not texts:
            print("⚠ No texts in this subset, skipping")
            return

        print(f"Sample size: {len(texts):,} texts")

        # Analyze
        analyzer = AnalyzerService()
        pattern = analyzer.analyze(texts, name=name, source_description=f"Test data: {name}")

        # Report key metrics
        print(f"\nVoice Pattern Metrics:")
        print(f"  Total words: {pattern.total_words:,}")
        print(f"  Total sentences: {pattern.total_sentences:,}")
        print(f"  Avg sentence length: {pattern.avg_sentence_length} words")
        print(f"  Vocabulary richness: {pattern.vocab_richness:.3f}")
        print(f"  Avg word length: {pattern.avg_word_length} characters")

        # Top function words
        if pattern.function_words:
            print(f"\n  Top 10 function words:")
            for fw in pattern.function_words[:10]:
                print(f"    {fw.word}: {fw.frequency:.2f}%")

        # Style markers
        if pattern.style_markers:
            print(f"\n  Style markers found:")
            for marker in pattern.style_markers:
                print(f"    {marker.category}: {len(marker.phrases)} phrases")

        # Generate prompt to validate
        generator = GeneratorService()
        prompt = generator.generate(pattern, context="professional")

        print(f"\n  Generated prompt length: {len(prompt.prompt_text)} characters")
        print(f"\n  Preview (first 200 chars):")
        print(f"  {prompt.prompt_text[:200]}...")

        # Assertions to ensure quality
        assert pattern.total_words > 0, "Should have analyzed some words"
        assert pattern.total_sentences > 0, "Should have found some sentences"
        assert pattern.avg_sentence_length > 0, "Should have sentence length"
        assert len(pattern.function_words) > 0, "Should have function words"
        assert len(prompt.prompt_text) > 100, "Prompt should be substantial"

        print(f"\n✓ Analysis complete for {name}")


@pytest.mark.skipif(not EMAIL_DATA_PATH.exists(), reason="Real email data not available")
def test_time_scale_comparison_summary():
    """
    Final summary test that compares all time scales.

    This test will show us whether 1 week vs 20 years makes a meaningful difference
    in the extracted voice patterns.
    """
    print(f"\n{'='*70}")
    print("TIME SCALE COMPARISON SUMMARY")
    print(f"{'='*70}\n")

    # Load data
    df = pd.read_csv(EMAIL_DATA_PATH)

    if 'body' in df.columns or 'content' in df.columns:
        content_col = 'body' if 'body' in df.columns else 'content'
        df = df[[content_col]].dropna()
        df.columns = ['text']
    else:
        pytest.skip("Email data format not recognized")

    if 'date' not in df.columns:
        pytest.skip("No date column for comparison")

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    # Analyze different time windows
    max_date = df['date'].max()
    time_windows = {
        "1 week": 7,
        "1 month": 30,
        "1 year": 365,
        "5 years": 365*5,
        "All data": None,
    }

    results = {}
    analyzer = AnalyzerService()

    for name, days in time_windows.items():
        if days:
            cutoff = max_date - timedelta(days=days)
            subset = df[df['date'] >= cutoff]
        else:
            subset = df

        texts = subset['text'].tolist()
        pattern = analyzer.analyze(texts, name=name)

        results[name] = {
            'samples': len(texts),
            'words': pattern.total_words,
            'sentences': pattern.total_sentences,
            'avg_sentence_length': pattern.avg_sentence_length,
            'vocab_richness': pattern.vocab_richness,
            'top_function_words': [fw.word for fw in pattern.function_words[:5]],
        }

    # Print comparison table
    print("\nComparison Table:")
    print(f"{'Time Window':<15} {'Samples':<10} {'Words':<12} {'Avg Sent Len':<12} {'Vocab Rich':<12}")
    print("-" * 70)

    for name, data in results.items():
        print(f"{name:<15} {data['samples']:<10,} {data['words']:<12,} "
              f"{data['avg_sentence_length']:<12.1f} {data['vocab_richness']:<12.3f}")

    # Analysis
    print("\n" + "="*70)
    print("KEY FINDINGS:")
    print("="*70)

    # Compare 1 week vs all data
    one_week = results['1 week']
    all_data = results['All data']

    sent_len_diff = abs(one_week['avg_sentence_length'] - all_data['avg_sentence_length'])
    vocab_diff = abs(one_week['vocab_richness'] - all_data['vocab_richness'])

    print(f"\n1 Week vs All Data:")
    print(f"  Sentence length difference: {sent_len_diff:.2f} words ({sent_len_diff/all_data['avg_sentence_length']*100:.1f}%)")
    print(f"  Vocabulary richness difference: {vocab_diff:.4f} ({vocab_diff/all_data['vocab_richness']*100:.1f}%)")

    # Check if top function words are similar
    one_week_words = set(one_week['top_function_words'])
    all_data_words = set(all_data['top_function_words'])
    overlap = len(one_week_words & all_data_words)

    print(f"  Top 5 function words overlap: {overlap}/5 ({overlap/5*100:.0f}%)")

    print(f"\n✓ Conclusion:")
    if sent_len_diff < 2 and vocab_diff < 0.02 and overlap >= 4:
        print("  Voice patterns are STABLE across time scales.")
        print("  Smaller samples (1 week - 1 month) appear sufficient for voice analysis.")
    elif sent_len_diff < 5 and vocab_diff < 0.05:
        print("  Voice patterns show MODERATE variation across time scales.")
        print("  Larger samples (1 year+) recommended for accuracy.")
    else:
        print("  Voice patterns show SIGNIFICANT variation across time scales.")
        print("  Maximum data (20 years) provides substantially better accuracy.")

    print()
