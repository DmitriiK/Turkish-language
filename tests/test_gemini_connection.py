#!/usr/bin/env python3
"""
Test script to verify Google Gemini API connection
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import toml
from pathlib import Path
import requests

# Load environment variables
load_dotenv()


def list_available_models():
    """List all available Gemini models via AI Studio API"""
    print("=" * 80)
    print("LISTING AVAILABLE GEMINI MODELS")
    print("=" * 80)
    print()
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables!")
        return
    
    print("🔍 Fetching available models from AI Studio API...\n")
    
    try:
        # Make direct HTTP request to list models
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        models = data.get('models', [])
        
        # Filter models that support generateContent
        generate_content_models = [
            m for m in models
            if 'generateContent' in m.get('supportedGenerationMethods', [])
        ]
        
        print("=" * 80)
        print("MODELS SUPPORTING generateContent:")
        print("=" * 80)
        print()
        
        for model in generate_content_models:
            model_name = model['name'].replace('models/', '')
            print(f"✅ {model_name}")
            print(f"   Display Name: {model.get('displayName', 'N/A')}")
            print(f"   Description: {model.get('description', 'N/A')[:100]}...")
            print(f"   Input Token Limit: {model.get('inputTokenLimit', 'N/A'):,}")
            print(f"   Output Token Limit: {model.get('outputTokenLimit', 'N/A'):,}")
            print()
        
        print("=" * 80)
        print(f"📊 Total models available: {len(generate_content_models)}")
        print("=" * 80)
        print()
        
    except Exception as e:
        print(f"❌ Error listing models: {str(e)}")
        print()


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
    # First list available models
    list_available_models()
    
    # Then test connection
    success = test_gemini_connection()
    exit(0 if success else 1)
