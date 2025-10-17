"""
Pytest configuration and fixtures.
"""

import pytest
import os
from unittest.mock import MagicMock
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment by loading environment variables."""
    load_dotenv()


@pytest.fixture
def mock_config():
    """Mock configuration for testing without real config file."""
    return {
        'model': {
            'name': 'gemini-2.5-flash'
        },
        'generation': {
            'temperature': 0.7,
            'max_output_tokens': 1024,
            'top_p': 0.8,
            'top_k': 40
        }
    }


@pytest.fixture
def api_key():
    """Get API key from environment or return None for mocked tests."""
    return os.getenv('GOOGLE_API_KEY')


@pytest.fixture
def has_real_api_key(api_key):
    """Check if we have a real API key for integration tests."""
    return api_key and api_key != 'your_google_api_key_here'


@pytest.fixture
def mock_gemini_model():
    """Mock Gemini model for unit testing."""
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked Turkish response: Merhaba! (Hello!)"
    mock_model.generate_content.return_value = mock_response
    return mock_model


@pytest.fixture
def sample_turkish_prompts():
    """Sample Turkish prompts for testing."""
    return [
        "Write a simple Turkish greeting",
        "Create a sentence using 'kitap' (book)",
        "Explain Turkish possessive constructions"
    ]