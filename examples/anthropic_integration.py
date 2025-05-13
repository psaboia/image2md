#!/usr/bin/env python3
"""
Anthropic integration with image2md framework.
This example demonstrates how to use Anthropic's Claude with the Image2MarkdownFactory.
"""
import os
import sys
from pathlib import Path
import json
import base64
import anthropic
from datetime import datetime
import platform
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Get Anthropic API key
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    print("Please set it in your .env file or environment variables")
    sys.exit(1)

# Example image
example_image_path = Path(__file__).parent / "83635935.png"
if not example_image_path.exists():
    print(f"Error: Example image not found at {example_image_path}")
    sys.exit(1)

# Create output directory for results
output_dir = Path("anthropic_integration_output")
output_dir.mkdir(exist_ok=True)

print("Example: Anthropic Integration with image2md")
print("=" * 80)

# Import the base converter class from image2md
from image2md.base import Image2MarkdownConverter
from image2md.factory import Image2MarkdownFactory

#---------------------------------------------------------------------------
# Create an Anthropic converter class
#---------------------------------------------------------------------------
class AnthropicConverter(Image2MarkdownConverter):
    """Anthropic-specific implementation for image-to-markdown conversion."""
    
    DEFAULT_PROMPT = (
        "Convert this image to well-formatted markdown. Maintain the structure "
        "and formatting as much as possible, including headings, lists, and tables."
    )
    
    def __init__(
        self,
        api_key=None,
        model="claude-3-7-sonnet-20250219",  # Default to Claude 3.7 Sonnet
        max_tokens=4000,
        temperature=0.3,
        **kwargs
    ):
        """Initialize Anthropic converter with specific defaults."""
        # Get API key from environment if not provided
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment variables")
            
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.options = kwargs
        
        # Initialize Anthropic client
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "Anthropic SDK is not installed. "
                "Please install it with: pip install anthropic"
            )
    
    def _encode_image(self, image_path):
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def convert(self, image_path, **kwargs):
        """
        Convert an image to markdown using Anthropic's Claude models.
        
        Args:
            image_path: Path to the image file
            **kwargs: Additional parameters
        
        Returns:
            Markdown string representation of the image
        """
        print(f"Converting {image_path} using Claude model: {self.model}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Get base64-encoded image
        base64_image = self._encode_image(image_path)
        
        # Get prompt (use custom if provided)
        custom_prompt = kwargs.get("custom_prompt", self.DEFAULT_PROMPT)
        
        # Make API request to Claude
        message = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": custom_prompt},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_image}}
                    ]
                }
            ]
        )
        
        # Extract markdown content
        markdown = message.content[0].text
        
        # Save provenance if requested
        save_json = kwargs.get("save_json", False)
        if save_json:
            json_output_path = kwargs.get("json_output_path")
            if json_output_path is None:
                json_output_path = image_path.with_suffix('.json')
            
            # Create provenance information
            timestamp = datetime.now().isoformat()
            provenance = {
                "timestamp": timestamp,
                "model": self.model,
                "provider": "Anthropic",
                "system_info": {
                    "os": platform.system(),
                    "os_version": platform.version(),
                    "python_version": platform.python_version(),
                    "hostname": platform.node()
                },
                "conversion_params": {
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "prompt": custom_prompt
                }
            }
            
            # Create JSON response
            json_result = {
                "markdown": markdown,
                "provenance": provenance,
                "timestamp": timestamp,
                "image_path": str(image_path),
                "conversion_type": "anthropic"
            }
            
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False)
        
        return markdown
        
    def save_markdown(self, image_path, output_path=None, **kwargs):
        """
        Convert an image to markdown and save it.
        
        Args:
            image_path: Path to the image file
            output_path: Path to save the markdown output
            **kwargs: Additional parameters for the conversion
        
        Returns:
            Path: Path to the saved markdown file
        """
        # Generate markdown
        markdown = self.convert(image_path, **kwargs)
        
        # Determine output path if not provided
        if output_path is None:
            output_path = image_path.with_suffix('.md')
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save markdown to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return output_path

#---------------------------------------------------------------------------
# Register the converter with the Image2MarkdownFactory
#---------------------------------------------------------------------------
print("\nRegistering Anthropic converter with Image2MarkdownFactory...")
Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)

# Get available converters
converters = Image2MarkdownFactory.available_converters()
print(f"Available converters: {', '.join(converters.keys())}")

#---------------------------------------------------------------------------
# Use the converter through the factory
#---------------------------------------------------------------------------
print("\nConverting image using Anthropic's Claude through Image2MarkdownFactory...")
result_path = Image2MarkdownFactory.convert(
    example_image_path,
    converter_type="anthropic",
    output_path=output_dir / "anthropic_result.md",
    api_key=api_key,
    model="claude-3-7-sonnet-20250219",
    save_json=True,
    json_output_path=output_dir / "anthropic_result.json",
    custom_prompt="Convert this image to well-formatted markdown with proper headings and structure."
)

print(f"\n✅ Conversion successful!")
print(f"✅ Result saved to: {result_path}")
print(f"✅ Provenance saved to: {output_dir / 'anthropic_result.json'}")

# If someone imports this module, these examples won't run automatically
if __name__ == "__main__":
    print("\nThis script has finished executing.")
    print(f"📁 Results saved in: {output_dir.absolute()}") 