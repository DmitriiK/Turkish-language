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


def get_available_models():
    """Get list of available models from DIAL API"""
    api_key = os.getenv('DIAL_API_KEY')
    if not api_key:
        return []
    
    api_url = "https://ai-proxy.lab.epam.com/openai/models"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [m['id'] for m in data.get("data", [])]
    except:
        pass
    
    return []


def check_model_availability(model_id: str) -> tuple[bool, str]:
    """Check if a specific model is available (listed in API)
    
    Returns:
        (is_available, message)
    """
    available_models = get_available_models()
    if not available_models:
        return False, "⚠️  Could not retrieve available models"
    
    if model_id in available_models:
        return True, f"📋 Model '{model_id}' is listed"
    else:
        # Try to find similar models
        similar = [m for m in available_models if model_id.split('-')[0] in m]
        if similar:
            suggestions = ", ".join(similar[:3])
            return False, f"❌ Model '{model_id}' not listed. Similar: {suggestions}"
        return False, f"❌ Model '{model_id}' not listed"


def check_model_access(model_id: str) -> tuple[bool, str]:
    """Check if you actually have access to use the model (not just listed)
    
    Returns:
        (has_access, message)
    """
    api_key = os.getenv('DIAL_API_KEY')
    if not api_key:
        return False, "⚠️  No API key"
    
    # Check if model is listed first
    is_listed, _ = check_model_availability(model_id)
    if not is_listed:
        return False, "❌ Not listed"
    
    # Try to make an actual API call with minimal tokens
    api_url = f"https://ai-proxy.lab.epam.com/openai/deployments/{model_id}/chat/completions"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5,
        "temperature": 0
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "✅ Access granted"
        elif response.status_code == 403:
            return False, "🔒 Listed but access denied (403)"
        elif response.status_code == 429:
            return True, "⏳ Rate limited (but accessible)"
        else:
            return False, f"❓ Status {response.status_code}"
    except Exception as e:
        return False, f"⚠️  Error: {str(e)[:50]}"


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
    
    # Check for GPT-5 variants
    gpt5_models = [m for m in models if 'gpt-5' in m['id'].lower()]
    if gpt5_models:
        print(f"\n   📊 Found {len(gpt5_models)} GPT-5 models:")
        for model in gpt5_models:
            print(f"      • {model['id']}")
    else:
        print(f"\n   ⚠️  No GPT-5 models found")
    
    # Check for Claude 4.5 variants
    claude_models = [m for m in models if 'claude' in m['id'].lower() and ('4.5' in m['id'] or '4-5' in m['id'])]
    if claude_models:
        print(f"\n   🤖 Found {len(claude_models)} Claude 4.5 models:")
        for model in claude_models:
            print(f"      • {model['id']}")
    
    # Check for Gemini models
    gemini_models = [m for m in models if 'gemini' in m['id'].lower()]
    if gemini_models:
        print(f"\n   💎 Found {len(gemini_models)} Gemini models:")
        for model in gemini_models:
            print(f"      • {model['id']}")
    
    assert len(models) > 0, "No models returned from API"
    
    return models


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


def test_gpt41_connection(config):
    """Test GPT-4.1 model"""
    model_id: str = config.get("DIAL_API", {}).get("GPT41_MODEL_NAME", "gpt-4.1-2025-04-14")
    test_dial_connection(model_id=model_id, config=config)


def test_gpt5_connection(config):
    """Test GPT-5 Chat model (may require special permissions)"""
    model_id: str = "gpt-5-chat-2025-08-07"
    test_dial_connection(model_id=model_id, config=config)


def test_all_configured_models(config):
    """Test availability AND access for all models configured in config.toml"""
    print("\n🔍 Checking all configured models (listing + access test)...")
    
    # Get model names from config
    dial_config = config.get("DIAL_API", {})
    models_to_check = {
        "OpenAI": dial_config.get("OPENAI_MODEL_NAME"),
        "GPT-4.1": dial_config.get("GPT41_MODEL_NAME"),
        "GPT-5": dial_config.get("GPT5_MODEL_NAME"),
        "Gemini": dial_config.get("GEMINI_MODEL_NAME"),
        "DeepSeek": dial_config.get("DEEP_SEEK_MODEL_NAME"),
        "Claude (AWS)": dial_config.get("CLOUD_MODEL_NAME"),
    }
    
    # Check Claude rotation models
    claude_rotation = dial_config.get("CLAUDE_MODEL_ROTATION", [])
    for i, model in enumerate(claude_rotation, 1):
        models_to_check[f"Claude Rotation {i}"] = model
    
    results = {}
    print("\n   Model Status (Listed | Access):")
    print("   " + "=" * 90)
    
    for name, model_id in models_to_check.items():
        if not model_id:
            continue
        
        # Check both listing and access
        has_access, access_msg = check_model_access(model_id)
        results[name] = has_access
        
        # Truncate model_id if too long
        display_id = model_id if len(model_id) <= 45 else model_id[:42] + "..."
        print(f"   {name:20s} -> {display_id:45s} | {access_msg}")
    
    print("   " + "=" * 90)
    
    # Summary
    accessible_count = sum(results.values())
    total_count = len(results)
    print(f"\n   Summary: {accessible_count}/{total_count} models are accessible")
    
    # Show accessible models for easy copy-paste
    if accessible_count > 0:
        print(f"\n   ✅ Accessible models:")
        for name, has_access in results.items():
            if has_access:
                print(f"      • {name}")
    
    if accessible_count == 0:
        pytest.fail("No configured models are accessible!")
    
    return results


def test_dial_connection(config, model_id: str = "gpt-4"):
    """Test DIAL API chat completion"""
    print(f"\n🔍 Testing DIAL API Connection with {model_id}...")
    
    # Check model availability first
    is_available, msg = check_model_availability(model_id)
    print(f"   {msg}")
    
    if not is_available:
        pytest.skip(f"Model {model_id} is not available")
    
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

