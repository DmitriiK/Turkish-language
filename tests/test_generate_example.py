"""
Test script to generate a training example for a specific verb and tense
without saving to file (for testing purposes)
"""
import sys
import json
from pathlib import Path

# Add pipelines to path
sys.path.insert(0, str(Path(__file__).parent.parent / "pipelines"))

from pipelines.create_traing_example import (
    load_config, load_verbs_from_csv, load_prompt_template,
    generate_training_example
)
from grammer_metadata import VerbTense, PersonalPronoun, LanguageLevel, VerbPolarity


def test_generate_example_for_say_simdiki_zaman():
    """Test generating training example for 'say' verb in şimdiki_zaman (present continuous)"""
    
    print("=" * 80)
    print("Testing Training Example Generation")
    print("=" * 80)
    print()
    
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Failed to load configuration")
        return
    
    # Load verbs
    project_root = Path(__file__).parent.parent
    verbs_file = project_root / "data" / "input" / "verbs.csv"
    all_verbs = load_verbs_from_csv(str(verbs_file))
    
    # Find "say" verb (or "söylemek" in Turkish)
    say_verb = None
    for verb in all_verbs:
        if verb.english.lower() == "say":
            say_verb = verb
            break
    
    if not say_verb:
        print("❌ Could not find 'say' verb in verbs.csv")
        return
    
    print(f"📚 Verb: {say_verb.english} ({say_verb.turkish})")
    print(f"   Rank: {say_verb.rank}")
    print(f"   Russian: {say_verb.russian}")
    print()
    
    # Load prompt template
    prompt_template = load_prompt_template()
    
    # Test parameters
    tense = VerbTense.ŞimdikiZaman
    pronoun = PersonalPronoun.Ben
    polarity = VerbPolarity.Positive
    language_level = LanguageLevel.A1
    provider = 'claude'  # Test with Claude
    
    print(f"🎯 Test Parameters:")
    print(f"   Tense: {tense.value}")
    print(f"   Pronoun: {pronoun.value}")
    print(f"   Polarity: {polarity.value}")
    print(f"   Language Level: {language_level.value}")
    print(f"   Provider: {provider}")
    print()
    
    # Generate example
    print("🤖 Generating training example...")
    print()
    
    try:
        example, prompt_tokens, completion_tokens = generate_training_example(
            verb=say_verb,
            tense=tense,
            pronoun=pronoun,
            polarity=polarity,
            prompt_template_str=prompt_template,
            language_level=language_level,
            config=config,
            provider=provider,
            rate_limiter=None,
            max_retries=3
        )
        
        if example is None:
            print("❌ Failed to generate example")
            return
        
        # Display results
        print("✅ Successfully generated training example!")
        print()
        print("=" * 80)
        print("GENERATED TRAINING EXAMPLE")
        print("=" * 80)
        print()
        
        # Convert to dict for pretty printing
        example_dict = example.model_dump()
        
        print(json.dumps(example_dict, indent=2, ensure_ascii=False))
        print()
        
        print("=" * 80)
        print("TOKEN USAGE")
        print("=" * 80)
        print(f"Prompt tokens: {prompt_tokens:,}")
        print(f"Completion tokens: {completion_tokens:,}")
        print(f"Total tokens: {prompt_tokens + completion_tokens:,}")
        print()
        
        print("=" * 80)
        print("VERIFICATION")
        print("=" * 80)
        
        # Verify verb_full construction
        tv = example.turkish_verb
        
        # Handle vowel dropping: if root ends in vowel and tense_affix starts with vowel, drop last vowel from root
        root = tv.root
        if root and tv.tense_affix:
            root_ends_vowel = root[-1] in 'aeıioöuü'
            affix_starts_vowel = tv.tense_affix[0] in 'aeıioöuü'
            if root_ends_vowel and affix_starts_vowel:
                root = root[:-1]  # Drop last vowel
        
        reconstructed = root
        if tv.negative_affix:
            reconstructed += tv.negative_affix
        reconstructed += tv.tense_affix
        if tv.personal_affix:
            reconstructed += tv.personal_affix
        
        verb_full_match = reconstructed == tv.verb_full
        vowel_drop_note = " (vowel dropped)" if root != tv.root else ""
        print(f"✓ Verb construction: {tv.verb_full} = {tv.root}{vowel_drop_note} + "
              f"{tv.negative_affix or '∅'} + {tv.tense_affix} + {tv.personal_affix or '∅'}")
        print(f"  Reconstruction check: {reconstructed} == {tv.verb_full} → "
              f"{'✅ PASS' if verb_full_match else '❌ FAIL'}")
        print()
        
        # Verify verb appears in sentence
        verb_in_sentence = tv.verb_full in example.turkish_example_sentence
        print(f"✓ Verb in sentence: '{tv.verb_full}' in '{example.turkish_example_sentence}' → "
              f"{'✅ PASS' if verb_in_sentence else '❌ FAIL'}")
        print()
        
        # Count words (excluding pronoun)
        words = example.turkish_example_sentence.split()
        word_count = len([w for w in words if w.lower() not in ['ben', 'sen', 'o', 'biz', 'siz', 'onlar']])
        word_count_ok = word_count >= 4
        print(f"✓ Word count (excl. pronoun): {word_count} words → {'✅ PASS' if word_count_ok else '❌ FAIL (need >= 4)'}")
        print()
        
        print("=" * 80)
        print("TEST COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_generate_example_for_say_simdiki_zaman()
