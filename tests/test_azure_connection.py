"""
Test Azure OpenAI connection with current configuration
"""
import os
import toml
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Load environment variables
load_dotenv()

def load_config():
    """Load configuration from config.toml file."""
    config_path = Path(__file__).parent.parent / "config.toml"
    return toml.load(config_path)

def test_azure_connection():
    """Test Azure OpenAI connection"""
    print("🔍 Testing Azure OpenAI Connection...\n")
    
    # Load configuration
    config = load_config()
    azure_config = config.get('azure_model', {})
    
    # Get credentials
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = azure_config.get('AZURE_OPENAI_ENDPOINT')
    api_version = azure_config.get('OPENAI_API_VERSION')
    model_name = azure_config.get('MODEL_NAME')
    
    print(f"📋 Configuration:")
    print(f"   Endpoint: {endpoint}")
    print(f"   API Version: {api_version}")
    print(f"   Model: {model_name}")
    print(f"   API Key: {'*' * 20}{api_key[-8:] if api_key else 'NOT FOUND'}")
    print()
    
    if not api_key:
        print("❌ Error: AZURE_OPENAI_API_KEY not found in environment variables")
        return False
    
    try:
        # Initialize Azure OpenAI client
        print("🔌 Connecting to Azure OpenAI...")
        llm = AzureChatOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
            model=model_name,
            temperature=0.7,
            max_retries=0  # Fail fast on rate limits
        )
        
        # Test with a simple message
        print("📤 Sending test message: 'Hello, how are you?'")
        response = llm.invoke("Hello, how are you?")
        
        print("✅ Connection successful!")
        print(f"\n📨 Response:")
        print(f"   {response.content}")
        print(f"\n📊 Response metadata:")
        print(f"   Model: {response.response_metadata.get('model_name', 'N/A')}")
        token_usage = response.response_metadata.get('token_usage', {})
        print(f"   Tokens used: {token_usage}")
        print(f"   Input tokens: {token_usage.get('prompt_tokens', 0)}")
        print(f"   Output tokens: {token_usage.get('completion_tokens', 0)}")
        print(f"   Total tokens: {token_usage.get('total_tokens', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed!")
        print(f"\n🔴 Error details:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        if "401" in str(e):
            print("\n💡 Suggestion: This is an authentication error.")
            print("   - Check that AZURE_OPENAI_API_KEY is correct in .env file")
            print("   - Verify the endpoint URL is correct in config.toml")
            print("   - Make sure the API key hasn't expired")
        elif "429" in str(e):
            print("\n💡 Suggestion: This is a rate limit error.")
            print("   - You've hit your quota limit (S0 tier: 50K tokens/minute)")
            print("   - Wait 60-90 seconds for quota to reset")
            print("   - Or upgrade to Standard tier for higher limits")
        elif "404" in str(e):
            print("\n💡 Suggestion: Resource not found.")
            print("   - Check the endpoint URL in config.toml")
            print("   - Verify the model deployment name is correct")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Azure OpenAI Connection Test")
    print("=" * 60)
    print()
    
    success = test_azure_connection()
    
    print()
    print("=" * 60)
    if success:
        print("✅ TEST PASSED - Azure OpenAI is working correctly!")
    else:
        print("❌ TEST FAILED - Please fix the errors above")
    print("=" * 60)
