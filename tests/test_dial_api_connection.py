"""
Test LLM connection with current configuration (DIAL API)
"""
import os
import requests
import toml
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.fixture(scope="module")
def config():
    """Load configuration from config.toml file."""
    config_path = Path(__file__).parent.parent / "config.toml"
    return toml.load(config_path)


def test_list_available_models():
    """Test listing available models from DIAL API"""
    print("\n🔍 Listing Available Models...")
    
    # Get API key from environment
    api_key = os.getenv('DIAL_API_KEY')
    
    # DIAL API configuration - correct endpoint for DIAL
    api_url = "https://ai-proxy.lab.epam.com/openai/models"
    
    print(f"   API URL: {api_url}")
    print(f"   API Key: {'*' * 20}{api_key[-8:] if api_key else 'NOT FOUND'}")
    
    assert api_key is not None, "DIAL_API_KEY not found in environment variables"
    
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    print("   Connecting to DIAL API...")
    response = requests.get(api_url, headers=headers)
    
    # Assert successful response
    assert response.status_code == 200, (
        f"Failed to list models. Status: {response.status_code}, "
        f"Response: {response.text}"
    )
    
    data = response.json()
    models = data.get("data", [])
    
    print(f"   ✅ Successfully retrieved {len(models)} models")
    for model in models[:5]:  # Show first 5
        print(f"      • {model['id']}")
    if len(models) > 5:
        print(f"      ... and {len(models) - 5} more")
    
    assert len(models) > 0, "No models returned from API"


def test_claude_haiku_4_5_connection(config):
    """Test Claude 4.5 Haiku model"""
    model_id: str = "anthropic.claude-haiku-4-5-20251001-v1:0"
    test_dial_connection(model_id=model_id, config=config)


def test_claude_sonnet_4_connection(config):
    """Test Claude 4 Sonnet model"""
    model_id: str = "anthropic.claude-sonnet-4-20250514-v1:0"
    test_dial_connection(model_id=model_id, config=config)


def test_claude_sonnet_4_5_connection(config):
    """Test Claude 4.5 Sonnet model"""
    model_id: str = "anthropic.claude-sonnet-4-5-20250929-v1:0"
    test_dial_connection(model_id=model_id, config=config)


def test_claude_opus_4_connection(config):
    """Test Claude 4 Opus model"""
    model_id: str = "anthropic.claude-opus-4-20250514-v1:0"
    test_dial_connection(model_id=model_id, config=config)


def test_claude_opus_4_1_connection(config):
    """Test Claude 4.1 Opus model"""
    model_id: str = "anthropic.claude-opus-4-1-20250805-v1:0"
    test_dial_connection(model_id=model_id, config=config)


def test_deepseek_connection(config):
    model_id: str = config.get("DIAL_API", {}).get("DEEP_SEEK_MODEL_NAME", "deepseek-r1")
    test_dial_connection(model_id=model_id, config=config)


def test_gemini_connection(config):
    model_id: str = config.get("DIAL_API", {}).get("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    test_dial_connection(model_id=model_id, config=config)


def test_dial_connection(config, model_id: str = "gpt-4"):
    """Test DIAL API chat completion"""
    print("\n🔍 Testing DIAL API Connection...")
    
    # Get credentials from environment
    api_key = os.getenv('DIAL_API_KEY')
    
    # DIAL API configuration - get endpoint from config.toml
    api_url_template = config.get("DIAL_API", {}).get("DIAL_API_ENDPOINT")
    assert api_url_template, "DIAL_API_ENDPOINT not found in config.toml"
    api_url = api_url_template.format(model_id=model_id)
    
    print(f"   API URL: {api_url}")
    print(f"   Model: {model_id}")
    print(f"   API Key: {'*' * 20}{api_key[-8:] if api_key else 'NOT FOUND'}")
    
    assert api_key is not None, "DIAL_API_KEY not found in environment variables"
    
    # Prepare request with Api-Key header (not Authorization: Bearer)
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "temperature": 0.2,
        "stream": False  # Explicitly set streaming to false
    }
    
    print("   Connecting to DIAL API...")
    print("   Sending test message: 'Hello, how are you?'")
    
    response = requests.post(api_url, headers=headers, json=payload, timeout=300)
    
    # Assert successful response
    assert response.status_code == 200, (
        f"Failed to get chat completion. Status: {response.status_code}, "
        f"Response: {response.text}"
    )
    
    data = response.json()
    
    # Assert response structure
    assert "choices" in data, "Response missing 'choices' field"
    assert len(data["choices"]) > 0, "No choices in response"
    assert "message" in data["choices"][0], "Choice missing 'message' field"
    assert "content" in data["choices"][0]["message"], "Message missing 'content' field"
    
    content = data["choices"][0]["message"]["content"]
    
    print("   ✅ Connection successful!")
    print(f"   Response: {content[:100]}{'...' if len(content) > 100 else ''}")
    
    usage = data.get('usage', {})
    print(f"   Tokens - Input: {usage.get('prompt_tokens', 0)}, "
          f"Output: {usage.get('completion_tokens', 0)}, "
          f"Total: {usage.get('total_tokens', 0)}")
    
    assert len(content) > 0, "Response content is empty"


if __name__ == "__main__":
    print("=" * 60)
    print("DIAL API Connection Test")
    print("=" * 60)
    
    # Load config for manual execution
    config_path = Path(__file__).parent.parent / "config.toml"
    test_config = toml.load(config_path)
    
    # Run tests manually
    try:
        print("\nStep 1: Listing available models")
        print("-" * 60)
        test_list_available_models()
        print("\n✅ Models list test passed")
    except AssertionError as e:
        print(f"\n❌ Models list test failed: {e}")
    
    try:
        print("\nStep 2: Testing chat completion")
        print("-" * 60)
        test_dial_connection(test_config)
        print("\n✅ Chat completion test passed")
    except AssertionError as e:
        print(f"\n❌ Chat completion test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Run 'pytest tests/test_dial_api_connection.py -v' for detailed test results")
    print("=" * 60)

