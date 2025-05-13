#!/usr/bin/env python3
"""Example of using Azure Document Intelligence with image2md module."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv  # pip install python-dotenv

# Add the current directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get credentials
endpoint = os.environ.get("AZURE_ENDPOINT")
api_key = os.environ.get("AZURE_API_KEY")

if not endpoint or not api_key:
    print("Error: Azure credentials not found in environment variables")
    print("Please set AZURE_ENDPOINT and AZURE_API_KEY environment variables")
    print("You can create a .env file with these variables or set them directly")
    sys.exit(1)

# Example image
example_image_path = Path(__file__).parent / "83635935.png"
if not example_image_path.exists():
    print(f"Error: Example image not found at {example_image_path}")
    sys.exit(1)

# Create output directory for results
output_dir = Path("azure_example_output")
output_dir.mkdir(exist_ok=True)

print(f"Example: Converting {example_image_path} to markdown using Azure Document Intelligence")
print("-" * 80)

try:
    # Method 1: Using AzureDocumentConverter directly
    print("\nMethod 1: Using AzureDocumentConverter directly")
    print("-" * 50)
    
    from image2md import AzureDocumentConverter
    
    # Initialize converter with explicit credentials
    converter = AzureDocumentConverter(
        endpoint=endpoint,
        api_key=api_key,
        # Optional parameters
        api_version="2024-11-30",
        model_id="prebuilt-layout"
    )
    
    # Convert image to markdown and save it
    output_path = output_dir / "direct_converter_output.md"
    result_path = converter.save_markdown(
        example_image_path,
        output_path,
        save_json=True  # Also save the full JSON response
    )
    
    print(f"✅ Markdown saved to: {result_path}")
    print(f"✅ JSON saved to: {result_path.with_suffix('.json')}")
    
    # Method 2: Using the Image2MarkdownFactory
    print("\nMethod 2: Using Image2MarkdownFactory")
    print("-" * 50)
    
    from image2md import Image2MarkdownFactory
    
    # One-step conversion using the factory
    output_path = output_dir / "factory_output.md"
    result_path = Image2MarkdownFactory.convert(
        example_image_path,
        converter_type="azure",
        output_path=output_path,
        endpoint=endpoint,
        api_key=api_key,
        save_json=True
    )
    
    print(f"✅ Markdown saved to: {result_path}")
    print(f"✅ JSON saved to: {result_path.with_suffix('.json')}")
    
    # Method 3: Using the factory to get a converter
    print("\nMethod 3: Using factory to get a converter")
    print("-" * 50)
    
    # Get converter through factory
    factory_converter = Image2MarkdownFactory.get_converter(
        converter_type="azure",
        endpoint=endpoint,
        api_key=api_key
    )
    
    # Use the converter to convert the image
    output_path = output_dir / "factory_converter_output.md"
    result_path = factory_converter.save_markdown(
        example_image_path,
        output_path,
        save_json=True
    )
    
    print(f"✅ Markdown saved to: {result_path}")
    print(f"✅ JSON saved to: {result_path.with_suffix('.json')}")
    
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
    print("  pip install azure-ai-documentintelligence>=1.0.0")
    print("  pip install image2md")
    sys.exit(1)
except Exception as e:
    print(f"Error during conversion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 