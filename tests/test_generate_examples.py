#!/usr/bin/env python3
"""
Comprehensive test suite for training example generation
Tests single mode, batch mode, and full pipeline scenarios
"""
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "pipelines"))

# Import after path setup
from create_traing_example import (  # noqa: E402
    load_config, load_verbs_from_csv,
    generate_training_example, main
)
from grammer_metadata import (  # noqa: E402
    VerbTense, PersonalPronoun, LanguageLevel, VerbPolarity
)


def find_verb(verb_name: str):
    """Helper to load and find a specific verb"""
    project_root = Path(__file__).parent.parent
    verbs_file = project_root / "data" / "input" / "verbs.csv"
    all_verbs = load_verbs_from_csv(str(verbs_file))
    
    for verb in all_verbs:
        if verb.english.lower() == verb_name.lower():
            return verb
    
    return None


def test_single_mode():
    """Test 1: Single mode - Generate one example for specific pronoun and polarity"""
    
    print("=" * 80)
    print("TEST 1: Single Mode - One Example Generation")
    print("=" * 80)
    print()
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return False
    
    # Find "say" verb
    say_verb = find_verb("say")
    if not say_verb:
        print("❌ Could not find 'say' verb in verbs.csv")
        return False
    
    print(f"📚 Verb: {say_verb.english} ({say_verb.turkish})")
    print(f"   Rank: {say_verb.rank}, Russian: {say_verb.russian}")
    print()
    
    # Test parameters
    tense = VerbTense.ŞimdikiZaman
    pronoun = PersonalPronoun.Ben
    polarity = VerbPolarity.Positive
    language_level = LanguageLevel.A1
    provider = 'claude'
    
    print(f"🎯 Parameters: {tense.value}, {pronoun.value}, {polarity.value}, {language_level.value}")
    print(f"   Provider: {provider}")
    print()
    
    # Generate example
    print("🤖 Generating single training example...")
    
    try:
        examples, prompt_tokens, completion_tokens = generate_training_example(
            verb=say_verb,
            tense=tense,
            pronoun=pronoun,
            polarity=polarity,
            language_level=language_level,
            config=config,
            provider=provider,
            rate_limiter=None,
            max_retries=3
        )
        
        if not examples or len(examples) == 0:
            print("❌ Failed to generate example")
            return False
        
        example = examples[0]
        
        # Display results
        print("✅ Successfully generated!")
        print()
        print(json.dumps(example.model_dump(), indent=2, ensure_ascii=False))
        print()
        
        # Token usage
        total = prompt_tokens + completion_tokens
        print(f"📊 Tokens: {total:,} ({prompt_tokens:,} in + {completion_tokens:,} out)")
        print()
        
        # Verification
        print("🔍 Verification:")
        tv = example.turkish_verb
        
        # Reconstruct verb
        root = tv.root
        if root and tv.tense_affix:
            if root[-1] in 'aeıioöuü' and tv.tense_affix[0] in 'aeıioöuü':
                root = root[:-1]  # Vowel drop
        
        reconstructed = root
        if tv.negative_affix:
            reconstructed += tv.negative_affix
        reconstructed += tv.tense_affix
        if tv.personal_affix:
            reconstructed += tv.personal_affix
        
        verb_ok = reconstructed == tv.verb_full
        in_sentence = tv.verb_full in example.turkish_example_sentence
        words = len([w for w in example.turkish_example_sentence.split()
                    if w.lower() not in ['ben', 'sen', 'o', 'biz', 'siz', 'onlar']])
        word_count_ok = words >= 4
        
        print(f"  ✓ Verb construction: {reconstructed} == {tv.verb_full} → {'✅' if verb_ok else '❌'}")
        print(f"  ✓ Verb in sentence: {tv.verb_full} in text → {'✅' if in_sentence else '❌'}")
        print(f"  ✓ Word count: {words} words (excl. pronoun) → {'✅' if word_count_ok else '❌'}")
        print()
        
        success = verb_ok and in_sentence and word_count_ok
        print(f"{'✅ TEST 1 PASSED' if success else '❌ TEST 1 FAILED'}")
        print()
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_mode():
    """Test 2: Batch mode - Generate all pronoun×polarity combinations"""
    
    print("=" * 80)
    print("TEST 2: Batch Mode - All Pronoun×Polarity Combinations")
    print("=" * 80)
    print()
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return False
    
    # Find "say" verb
    say_verb = find_verb("say")
    if not say_verb:
        print("❌ Could not find 'say' verb")
        return False
    
    print(f"📚 Verb: {say_verb.english} ({say_verb.turkish})")
    print()
    
    # Test parameters
    tense = VerbTense.ŞimdikiZaman
    language_level = LanguageLevel.A1
    provider = 'claude'
    
    print(f"🎯 Parameters: {tense.value}, BATCH mode (pronoun=None, polarity=None)")
    print(f"   Expected: 12 examples (6 pronouns × 2 polarities)")
    print(f"   Provider: {provider}")
    print()
    
    # Generate batch
    print("🤖 Generating batch training examples...")
    
    try:
        examples, prompt_tokens, completion_tokens = generate_training_example(
            verb=say_verb,
            tense=tense,
            pronoun=None,  # Batch mode
            polarity=None,  # Batch mode
            language_level=language_level,
            config=config,
            provider=provider,
            rate_limiter=None,
            max_retries=3
        )
        
        if not examples:
            print("❌ Failed to generate examples")
            return False
        
        print(f"✅ Generated {len(examples)} examples!")
        print()
        
        # Display by polarity
        positive = [ex for ex in examples if ex.turkish_verb.polarity == VerbPolarity.Positive]
        negative = [ex for ex in examples if ex.turkish_verb.polarity == VerbPolarity.Negative]
        
        print(f"POSITIVE ({len(positive)}):")
        for ex in positive:
            p = ex.turkish_verb.personal_pronoun.value if ex.turkish_verb.personal_pronoun else "none"
            print(f"  {p:6} | {ex.turkish_verb.verb_full:15} | {ex.turkish_example_sentence}")
        
        print(f"\nNEGATIVE ({len(negative)}):")
        for ex in negative:
            p = ex.turkish_verb.personal_pronoun.value if ex.turkish_verb.personal_pronoun else "none"
            print(f"  {p:6} | {ex.turkish_verb.verb_full:15} | {ex.turkish_example_sentence}")
        print()
        
        # Token usage
        total = prompt_tokens + completion_tokens
        avg = total // len(examples) if examples else 0
        print(f"📊 Tokens: {total:,} ({prompt_tokens:,} in + {completion_tokens:,} out)")
        print(f"   Average per example: {avg:,}")
        print()
        
        # Verification
        print("🔍 Verification:")
        expected_count = 12
        count_ok = len(examples) == expected_count
        
        expected_pronouns = {PersonalPronoun.Ben, PersonalPronoun.Sen, PersonalPronoun.O_Third,
                           PersonalPronoun.Biz, PersonalPronoun.Siz, PersonalPronoun.Onlar}
        pos_pronouns = {ex.turkish_verb.personal_pronoun for ex in positive}
        neg_pronouns = {ex.turkish_verb.personal_pronoun for ex in negative}
        
        pronouns_ok = (pos_pronouns == expected_pronouns and neg_pronouns == expected_pronouns)
        unique_ok = len(set(ex.turkish_example_sentence for ex in examples)) == len(examples)
        
        print(f"  ✓ Count: {len(examples)}/{expected_count} examples → {'✅' if count_ok else '❌'}")
        print(f"  ✓ All pronouns (pos): {len(pos_pronouns)}/6 → {'✅' if len(pos_pronouns) == 6 else '❌'}")
        print(f"  ✓ All pronouns (neg): {len(neg_pronouns)}/6 → {'✅' if len(neg_pronouns) == 6 else '❌'}")
        print(f"  ✓ Unique sentences: {len(set(ex.turkish_example_sentence for ex in examples))}/{len(examples)} → {'✅' if unique_ok else '⚠️'}")
        print()
        
        success = count_ok and pronouns_ok
        print(f"{'✅ TEST 2 PASSED' if success else '❌ TEST 2 FAILED'}")
        print()
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline_b2():
    """Test 3: Full pipeline - Generate all B2 grammar forms for ben/positive"""
    
    print("=" * 80)
    print("TEST 3: Full Pipeline - All B2 Grammar Forms")
    print("=" * 80)
    print()
    
    print("📚 Generating: say (söylemek)")
    print("   Parameters: pronoun=ben, polarity=positive, level=B2")
    print("   Expected: 14+ examples (all B2 tenses)")
    print()
    
    print("🤖 Running full pipeline...")
    print()
    
    try:
        # Run main pipeline
        main(
            language_level="B2",
            specific_verbs=["say"],
            pronouns=["ben"],
            polarities=["positive"],
            provider="claude",
            skip_existing=False
        )
        
        print()
        print("✅ TEST 3 COMPLETED")
        print("   Check logs/ directory for detailed results")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all test scenarios"""
    
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TRAINING EXAMPLE GENERATION TESTS" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    results = []
    
    # Test 1: Single mode
    results.append(("Single Mode", test_single_mode()))
    print()
    
    # Test 2: Batch mode
    results.append(("Batch Mode", test_batch_mode()))
    print()
    
    # Test 3: Full pipeline
    results.append(("Full Pipeline (B2)", test_full_pipeline_b2()))
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {name:25} {status}")
    print()
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 80)
    
    return all(p for _, p in results)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test training example generation")
    parser.add_argument("--test", choices=["single", "batch", "pipeline", "all"],
                       default="all", help="Which test to run")
    
    args = parser.parse_args()
    
    if args.test == "single":
        success = test_single_mode()
    elif args.test == "batch":
        success = test_batch_mode()
    elif args.test == "pipeline":
        success = test_full_pipeline_b2()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
