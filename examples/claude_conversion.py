#!/usr/bin/env python3
"""Script to convert an image to markdown using Claude/Anthropic API"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json
import base64
import anthropic
from datetime import datetime
import platform

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get Anthropic API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    sys.exit(1)

# Example image
example_image_path = Path(__file__).parent / "83635935.png"
if not example_image_path.exists():
    print(f"Error: Example image not found at {example_image_path}")
    sys.exit(1)

# Create output directory for results
output_dir = Path("claude_conversion_output")
output_dir.mkdir(exist_ok=True)

# Output files
output_md = output_dir / "claude_result.md"
output_json = output_dir / "claude_result.json"

print(f"Converting image {example_image_path} using Anthropic Claude...")

def encode_image(image_path):
    """Encode image to base64 string"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Encode the image
base64_image = encode_image(example_image_path)

# Parameters
model = "claude-3-opus-20240229"
max_tokens = 4000
temperature = 0.3
prompt = "Convert this image to well-formatted markdown with proper headings, lists, and tables. Maintain the document structure as much as possible."

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=api_key)

try:
    # Create the request for Claude with vision capabilities
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_image}}
                ]
            }
        ]
    )
    
    # Extract the markdown content from the response
    markdown = message.content[0].text
    
    # Create provenance information
    timestamp = datetime.now().isoformat()
    provenance = {
        "timestamp": timestamp,
        "model": model,
        "model_version": None,
        "provider": "Anthropic",
        "system_info": {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        },
        "conversion_params": {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "prompt": prompt
        }
    }
    
    # Save markdown to file
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    # Save JSON with provenance
    json_result = {
        "markdown": markdown,
        "provenance": provenance,
        "timestamp": timestamp,
        "image_path": str(example_image_path),
        "conversion_type": "claude"
    }
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(json_result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Conversion successful!")
    print(f"✅ Markdown saved to: {output_md}")
    print(f"✅ Provenance information saved to: {output_json}")
    
    # Print a preview of the result
    print("\nPreview of conversion result:")
    print("-" * 80)
    print(markdown[:500] + "..." if len(markdown) > 500 else markdown)
    print("-" * 80)

except Exception as e:
    print(f"Error during conversion: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 