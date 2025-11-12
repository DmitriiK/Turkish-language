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


def load_config():
    """Load configuration from config.toml file."""
    config_path = Path(__file__).parent.parent / "config.toml"
    return toml.load(config_path)


def test_list_available_models():
    """Test listing available models from DIAL API"""
    print("\n🔍 Listing Available Models...")
    
    # Get API key from environment
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    # DIAL API configuration
    api_url = "https://ai-proxy.lab.epam.com/v1/models"
    
    print(f"   API URL: {api_url}")
    print(f"   API Key: {'*' * 20}{api_key[-8:] if api_key else 'NOT FOUND'}")
    
    assert api_key is not None, "AZURE_OPENAI_API_KEY not found in environment variables"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
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


def test_dial_connection():
    """Test DIAL API chat completion"""
    print("\n🔍 Testing DIAL API Connection...")
    
    # Get credentials from environment
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    
    # DIAL API configuration
    api_url = "https://ai-proxy.lab.epam.com/v1/chat/completions"
    model_id = "claude-haiku-4-5@20251001"
    
    print(f"   API URL: {api_url}")
    print(f"   Model: {model_id}")
    print(f"   API Key: {'*' * 20}{api_key[-8:] if api_key else 'NOT FOUND'}")
    
    assert api_key is not None, "AZURE_OPENAI_API_KEY not found in environment variables"
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "Hello, how are you?"}
        ],
        "temperature": 0.2
    }
    
    print("   Connecting to DIAL API...")
    print("   Sending test message: 'Hello, how are you?'")
    
    response = requests.post(api_url, headers=headers, json=payload)
    
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
    
    print(f"   ✅ Connection successful!")
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
        test_dial_connection()
        print("\n✅ Chat completion test passed")
    except AssertionError as e:
        print(f"\n❌ Chat completion test failed: {e}")
    
    print("\n" + "=" * 60)
    print("Run 'pytest tests/test_azure_connection.py -v' for detailed test results")
    print("=" * 60)

