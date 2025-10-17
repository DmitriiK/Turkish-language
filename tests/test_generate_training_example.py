import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add the pipelines directory to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "pipelines"))

from create_traing_example import generate_training_example, VerbData, load_config, load_prompt_template
from grammer_metadata import VerbTense, PersonalPronoun, LanguageLevel, TrainingExample, TurkishVerb, VerbFormInfo


class TestGenerateTrainingExample:
    """Test suite for the generate_training_example function"""
    
    @pytest.fixture
    def sample_verb_data(self):
        """Create a sample VerbData instance for testing"""
        return VerbData(rank=1, english="to be", russian="быть", turkish="olmak")
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration dictionary"""
        return {
            'model': {
                'name': 'gemini-2.5-flash'
            },
            'generation': {
                'temperature': 0.7,
                'max_output_tokens': 1000,
                'top_p': 0.9,
                'top_k': 40
            }
        }
    
    @pytest.fixture
    def sample_prompt_template(self):
        """Create a simple prompt template for testing"""
        return """
        You are a Turkish language expert. Create a training example for:
        - Verb (English): {verb_english}
        - Verb (Turkish): {verb_infinitive}
        - Tense: {verb_tense}
        - Pronoun: {personal_pronoun}
        - Level: {language_level}
        
        Generate the training example now.
        """
    
    def test_training_example_creation_manual(self):
        """Test manual creation of TrainingExample to understand the structure"""
        # First, let's create a TurkishVerb manually
        verb_form_info = VerbFormInfo(
            verb_tense=VerbTense.ŞimdikiZaman,
            language_level=LanguageLevel.A1,
            type_of_personal_pronoun=1
        )
        
        turkish_verb = TurkishVerb(
            verb_full="oluyorum",
            root="ol",
            tense_affix="uyor",
            verb_tense=verb_form_info,
            personal_pronoun=PersonalPronoun.Ben,
            personal_affix="um"
        )
        
        # Now create a TrainingExample
        training_example = TrainingExample(
            verb_rank=1,
            verb_english="to be",
            verb_russian="быть",
            verb_turkish=turkish_verb,
            english_example_sentence="I am happy.",
            russian_example_sentence="Я счастлив.",
            turkish_example_sentence="Ben mutlu oluyorum.",
            turkish_example_sentence_with_blank="Ben mutlu ______."
        )
        
        # Verify the structure
        assert training_example.verb_rank == 1
        assert training_example.verb_english == "to be"
        assert training_example.verb_russian == "быть"
        assert training_example.verb_turkish.verb_full == "oluyorum"
        assert training_example.verb_turkish.personal_pronoun == PersonalPronoun.Ben
        assert training_example.turkish_example_sentence_with_blank == "Ben mutlu ______."
        
        print("✅ Manual TrainingExample creation successful!")
        print(f"Created example: {training_example}")
    
    @patch.dict(os.environ, {"GEMINI_API_KEY": "test_api_key"})
    def test_generate_training_example_with_mock_llm(self, sample_verb_data, sample_config, sample_prompt_template):
        """Test generate_training_example with a mocked LLM response"""
        
        # Create the expected TrainingExample structure that the LLM should return
        verb_form_info = VerbFormInfo(
            verb_tense=VerbTense.ŞimdikiZaman,
            language_level=LanguageLevel.A1,
            type_of_personal_pronoun=1
        )
        
        turkish_verb = TurkishVerb(
            verb_full="oluyorum",
            root="ol",
            tense_affix="uyor",
            verb_tense=verb_form_info,
            personal_pronoun=PersonalPronoun.Ben,
            personal_affix="um"
        )
        
        mock_training_example = TrainingExample(
            verb_rank=1,
            verb_english="to be",
            verb_russian="быть",
            verb_turkish=turkish_verb,
            english_example_sentence="I am happy.",
            russian_example_sentence="Я счастлив.",
            turkish_example_sentence="Ben mutlu oluyorum.",
            turkish_example_sentence_with_blank="Ben mutlu ______."
        )
        
        # Mock the LangChain components
        with patch('create_traing_example.ChatGoogleGenerativeAI') as mock_chat_llm:
            with patch('create_traing_example.PromptTemplate') as mock_prompt:
                # Setup the mock LLM to return our expected structure
                mock_structured_llm = MagicMock()
                mock_structured_llm.invoke.return_value = mock_training_example
                
                mock_llm_instance = MagicMock()
                mock_llm_instance.with_structured_output.return_value = mock_structured_llm
                mock_chat_llm.return_value = mock_llm_instance
                
                mock_prompt_instance = MagicMock()
                mock_prompt.return_value = mock_prompt_instance
                
                # Create a mock chain that returns our training example
                mock_chain = mock_prompt_instance.__or__.return_value
                mock_chain.invoke.return_value = mock_training_example
                
                # Call the function
                result = generate_training_example(
                    verb=sample_verb_data,
                    tense=VerbTense.ŞimdikiZaman,
                    pronoun=PersonalPronoun.Ben,
                    prompt_template_str=sample_prompt_template,
                    language_level=LanguageLevel.A1,
                    config=sample_config
                )
                
                # Verify the result
                assert result is not None
                assert isinstance(result, TrainingExample)
                assert result.verb_english == "to be"
                assert result.verb_turkish.verb_full == "oluyorum"
                
                print("✅ Mocked generate_training_example test successful!")
                print(f"Generated result: {result}")
    
    def test_training_example_json_serialization(self):
        """Test that TrainingExample can be properly serialized to JSON"""
        # Create a complete TrainingExample
        verb_form_info = VerbFormInfo(
            verb_tense=VerbTense.ŞimdikiZaman,
            language_level=LanguageLevel.A1,
            type_of_personal_pronoun=1
        )
        
        turkish_verb = TurkishVerb(
            verb_full="oluyorum",
            root="ol",
            tense_affix="uyor",
            verb_tense=verb_form_info,
            personal_pronoun=PersonalPronoun.Ben,
            personal_affix="um"
        )
        
        training_example = TrainingExample(
            verb_rank=1,
            verb_english="to be",
            verb_russian="быть",
            verb_turkish=turkish_verb,
            english_example_sentence="I am happy.",
            russian_example_sentence="Я счастлив.",
            turkish_example_sentence="Ben mutlu oluyorum.",
            turkish_example_sentence_with_blank="Ben mutlu ______."
        )
        
        # Test JSON serialization
        json_data = training_example.model_dump()
        
        # Verify key fields are present
        assert "verb_rank" in json_data
        assert "verb_english" in json_data
        assert "verb_turkish" in json_data
        assert "turkish_example_sentence_with_blank" in json_data
        
        # Verify nested structure
        assert "verb_full" in json_data["verb_turkish"]
        assert "personal_pronoun" in json_data["verb_turkish"]
        
        print("✅ JSON serialization test successful!")
        print(f"JSON keys: {list(json_data.keys())}")
        print(f"Turkish verb keys: {list(json_data['verb_turkish'].keys())}")


if __name__ == "__main__":
    # Run tests manually if executed directly
    test_instance = TestGenerateTrainingExample()
    
    print("🧪 Running TrainingExample structure tests...")
    
    try:
        test_instance.test_training_example_creation_manual()
    except Exception as e:
        print(f"❌ Manual creation test failed: {e}")
    
    try:
        test_instance.test_training_example_json_serialization()
    except Exception as e:
        print(f"❌ JSON serialization test failed: {e}")
    
    # Test with sample data
    try:
        sample_verb = VerbData(rank=1, english="to be", russian="быть", turkish="olmak")
        sample_config = {
            'model': {'name': 'gemini-2.5-flash'},
            'generation': {
                'temperature': 0.7,
                'max_output_tokens': 1000,
                'top_p': 0.9,
                'top_k': 40
            }
        }
        sample_template = "Test template: {verb_english}, {verb_infinitive}, {verb_tense}, {personal_pronoun}, {language_level}"
        
        test_instance.test_generate_training_example_with_mock_llm(sample_verb, sample_config, sample_template)
    except Exception as e:
        print(f"❌ Mocked LLM test failed: {e}")