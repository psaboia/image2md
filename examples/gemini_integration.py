#!/usr/bin/env python3
"""
Gemini integration with image2md framework.
This example demonstrates how to use Google's Gemini with the Image2MarkdownFactory.
"""
import os
import sys
from pathlib import Path
import json
import base64
from datetime import datetime
import platform
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get Google API key
api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables")
    print("Please set it in your .env file or environment variables")
    sys.exit(1)

# Example image
example_image_path = Path(__file__).parent / "83635935.png"
if not example_image_path.exists():
    print(f"Error: Example image not found at {example_image_path}")
    sys.exit(1)

# Create output directory for results
output_dir = Path("gemini_integration_output")
output_dir.mkdir(exist_ok=True)

print("Example: Gemini Integration with image2md")
print("=" * 80)

# Import from image2md
from image2md.base import Image2MarkdownConverter
from image2md.factory import Image2MarkdownFactory

try:
    # Import the GeminiConverter (should already be implemented)
    from image2md.gemini_converter import GeminiConverter, GEMINI_AVAILABLE
    
    if not GEMINI_AVAILABLE:
        print("Google Generative AI SDK is not available. Make sure it's installed:")
        print("pip install google-generativeai>=0.3.0")
        sys.exit(1)
except ImportError:
    print("Failed to import GeminiConverter. Make sure it's implemented correctly.")
    sys.exit(1)

#---------------------------------------------------------------------------
# Use the converter through the factory
#---------------------------------------------------------------------------
print("\nConverting image using Google's Gemini through Image2MarkdownFactory...")
result_path = Image2MarkdownFactory.convert(
    example_image_path,
    converter_type="gemini",
    output_path=output_dir / "gemini_result.md",
    api_key=api_key,
    model="gemini-2.5-flash-preview-04-17",
    save_json=True,
    json_output_path=output_dir / "gemini_result.json",
    custom_prompt="Convert this image to well-formatted markdown with proper headings and structure."
)

print(f"\n✅ Conversion successful!")
print(f"✅ Result saved to: {result_path}")
print(f"✅ Provenance saved to: {output_dir / 'gemini_result.json'}")

# If someone imports this module, these examples won't run automatically
if __name__ == "__main__":
    print("\nThis script has finished executing.")
    print(f"📁 Results saved in: {output_dir.absolute()}") 