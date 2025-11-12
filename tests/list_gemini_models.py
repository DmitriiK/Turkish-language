"""
Test script to list all available Gemini models via AI Studio API
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

print("🔍 Fetching available Gemini models via AI Studio API...\n")

# List all available models
models = genai.list_models()

print("=" * 80)
print("AVAILABLE MODELS:")
print("=" * 80)

for model in models:
    print(f"\n📦 Model: {model.name}")
    print(f"   Display Name: {model.display_name}")
    print(f"   Description: {model.description}")
    print(f"   Supported Generation Methods: {model.supported_generation_methods}")
    print(f"   Input Token Limit: {model.input_token_limit:,}")
    print(f"   Output Token Limit: {model.output_token_limit:,}")
    print("-" * 80)

print("\n" + "=" * 80)
print("MODELS SUPPORTING generateContent:")
print("=" * 80)

generate_content_models = [
    model for model in genai.list_models() 
    if 'generateContent' in model.supported_generation_methods
]

for model in generate_content_models:
    # Extract just the model name without the 'models/' prefix
    model_name = model.name.replace('models/', '')
    print(f"✅ {model_name}")

print(f"\n📊 Total models supporting generateContent: {len(generate_content_models)}")
