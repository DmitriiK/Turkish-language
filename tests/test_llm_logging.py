#!/usr/bin/env python3
"""Test LLM call logging functionality"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import after path setup
from pipelines.create_traing_example import main  # noqa: E402


if __name__ == "__main__":
    """Test LLM call logging with a simple example"""
    
    print("=" * 80)
    print("Testing LLM Call Logging")
    print("=" * 80)
    print("\nThis test will generate one example and verify that:")
    print("1. Pipeline log is created")
    print("2. LLM call log (CSV) is created")
    print("3. CSV contains timestamp, model, tokens, duration, and error columns")
    print()
    
    # Run pipeline with minimal parameters to generate one example
    main(
        language_level="A1",
        specific_verbs=["be"],
        tenses=["şimdiki_zaman"],
        pronouns=["ben"],
        polarities=["positive"],
        provider="claude",
        skip_existing=False
    )
    
    print("\n" + "=" * 80)
    print("✅ Test complete! Check the logs/ directory for:")
    print("   - pipeline_log_*.txt (general pipeline log)")
    print("   - llm_calls_*.csv (detailed LLM call log)")
    print("=" * 80)
