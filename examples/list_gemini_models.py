#!/usr/bin/env python3
"""
Script to list available Gemini models.
"""
import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to sys.path to import image2md
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Check if the Google Generative AI SDK is installed
try:
    import google.generativeai as genai
except ImportError:
    print("Google Generative AI SDK is not installed.")
    print("Install it with: pip install google-generativeai>=0.3.0")
    sys.exit(1)

def list_gemini_models(api_key=None):
    """
    List all available Gemini models.
    
    Args:
        api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
    """
    # Get API key
    api_key = api_key or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: Google API key not provided.")
        print("Set GOOGLE_API_KEY environment variable or pass it as an argument.")
        sys.exit(1)
    
    # Configure the genai library
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Google AI client: {e}")
        sys.exit(1)
    
    # List models
    try:
        models = genai.list_models()
        print("\nAvailable Gemini Models:")
        print("=" * 70)
        for model in models:
            if "gemini" in model.name:
                print(f"Model: {model.name}")
                print(f"Display Name: {model.display_name}")
                print(f"Description: {model.description}")
                print(f"Input Token Limit: {model.input_token_limit}")
                print(f"Output Token Limit: {model.output_token_limit}")
                print(f"Supported Generation Methods: {', '.join(model.supported_generation_methods)}")
                print("-" * 70)
        
        # Print models suitable for vision tasks
        print("\nGemini Models Supporting Vision Tasks:")
        print("=" * 70)
        for model in models:
            if "gemini" in model.name and hasattr(model, 'supported_generation_methods') and 'generateContent' in model.supported_generation_methods:
                if hasattr(model, 'input_control_supported') and model.input_control_supported and 'image' in model.input_control_supported:
                    print(f"Model: {model.name}")
                    print(f"Display Name: {model.display_name}")
                    print("-" * 70)
                
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="List available Gemini models")
    parser.add_argument(
        "--api-key",
        type=str,
        help="Google API key (if not provided, uses GOOGLE_API_KEY env var)"
    )
    args = parser.parse_args()
    
    list_gemini_models(api_key=args.api_key)

if __name__ == "__main__":
    main() 