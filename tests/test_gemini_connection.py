#!/usr/bin/env python3
"""
Test script to verify Google Gemini API connection
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import toml
from pathlib import Path

# Load environment variables
load_dotenv()


def test_gemini_connection():
    """Test basic Gemini API connection"""
    print("=" * 60)
    print("Google Gemini Connection Test")
    print("=" * 60)
    print()
    
    # Load config
    config_path = Path(__file__).parent.parent / "config.toml"
    config = toml.load(config_path)
    
    print("🔍 Testing Google Gemini Connection...")
    print()
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    
    print("📋 Configuration:")
    print(f"   Model: {config['model']['name']}")
    print(f"   Temperature: {config['generation']['temperature']}")
    print(f"   Max tokens: {config['generation']['max_output_tokens']}")
    print(f"   API Key: {'*' * 20}{api_key[-10:] if api_key else 'NOT SET'}")
    print()
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables!")
        print("   Please set it in your .env file")
        return False
    
    try:
        # Initialize Gemini
        print("🔌 Connecting to Google Gemini...")
        llm = ChatGoogleGenerativeAI(
            model=config['model']['name'],
            google_api_key=api_key,
            temperature=config['generation']['temperature'],
            max_output_tokens=config['generation']['max_output_tokens'],
        )
        
        # Test simple completion
        print("📤 Sending test message: 'Hello, how are you?'")
        response = llm.invoke("Hello, how are you?")
        
        print("✅ Connection successful!")
        print()
        print("📨 Response:")
        print(f"   {response.content}")
        print()
        
        # Display response metadata
        print("📊 Response metadata:")
        print(f"   Model: {response.response_metadata.get('model_name', 'N/A')}")
        
        # Token usage (if available)
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            usage = response.usage_metadata
            print(f"   Tokens used: {dict(usage)}")
            print(f"   Input tokens: {usage.get('input_tokens', 'N/A')}")
            print(f"   Output tokens: {usage.get('output_tokens', 'N/A')}")
            print(f"   Total tokens: {usage.get('total_tokens', 'N/A')}")
        
        print()
        print("=" * 60)
        print("✅ TEST PASSED - Google Gemini is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("❌ Connection failed!")
        print(f"   Error: {str(e)}")
        print()
        print("=" * 60)
        print("❌ TEST FAILED")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_gemini_connection()
    exit(0 if success else 1)
