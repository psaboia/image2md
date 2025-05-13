#!/usr/bin/env python3
"""Example of using LLM-based image-to-markdown conversion with provenance tracking."""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv  # pip install python-dotenv

# Add the current directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("Error: OpenAI API key not found in environment variables")
    print("Please set OPENAI_API_KEY environment variable")
    print("You can create a .env file with this variable or set it directly")
    sys.exit(1)

# Example image
example_image_path = Path(__file__).parent / "83635935.png"
if not example_image_path.exists():
    print(f"Error: Example image not found at {example_image_path}")
    sys.exit(1)

# Create output directory for results
output_dir = Path("llm_converter_output")
output_dir.mkdir(exist_ok=True)

print(f"Example: Converting {example_image_path} to markdown using LLM with provenance tracking")
print("-" * 80)

try:
    # Method 1: Using LLMConverter directly
    print("\nMethod 1: Using LLMConverter directly")
    print("-" * 50)
    
    from image2md import LLMConverter
    
    # Initialize converter with API key
    converter = LLMConverter(
        api_key=api_key,
        model="gpt-4o",
        provider="openai",
        max_tokens=4000,
        temperature=0.3
    )
    
    # Convert image to markdown and save it with provenance info
    output_path = output_dir / "direct_converter_output.md"
    json_output_path = output_dir / "direct_converter_output.json"
    
    result_path = converter.save_markdown(
        example_image_path,
        output_path,
        save_json=True,
        json_output_path=json_output_path
    )
    
    print(f"✅ Markdown saved to: {result_path}")
    print(f"✅ JSON with provenance saved to: {json_output_path}")
    
    # Display provenance information
    with open(json_output_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)
        
    print("\nProvenance Information:")
    print(f"  Timestamp: {json_data['provenance']['timestamp']}")
    print(f"  Model: {json_data['provenance']['model']}")
    print(f"  Provider: {json_data['provenance']['provider']}")
    print(f"  System Info: {json_data['provenance']['system_info']}")
    
    # Method 2: Using the Image2MarkdownFactory
    print("\nMethod 2: Using Image2MarkdownFactory")
    print("-" * 50)
    
    from image2md import Image2MarkdownFactory
    
    # One-step conversion using the factory
    output_path = output_dir / "factory_output.md"
    json_output_path = output_dir / "factory_output.json"
    
    result_path = Image2MarkdownFactory.convert(
        example_image_path,
        converter_type="llm",
        output_path=output_path,
        api_key=api_key,
        model="gpt-4o",
        provider="openai",
        max_tokens=4000,
        temperature=0.3,
        save_json=True,
        json_output_path=json_output_path,
        custom_prompt="Convert this image to well-formatted markdown with proper headings, lists, and tables."
    )
    
    print(f"✅ Markdown saved to: {result_path}")
    print(f"✅ JSON with provenance saved to: {json_output_path}")
    
    # Print a preview of the markdown content
    with open(result_path, "r", encoding="utf-8") as f:
        content = f.read()
        preview_length = min(500, len(content))
        print("\nPreview of markdown content:")
        print("=" * 80)
        print(content[:preview_length] + ("..." if len(content) > preview_length else ""))
        print("=" * 80)
    
    print("\n✨ All examples completed successfully!")
    print(f"📁 Results saved in: {output_dir.absolute()}")

except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you have the required packages installed:")
    print("  pip install openai>=1.0.0")
    print("  pip install python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"Error during conversion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 