#!/usr/bin/env python3
"""
Full integration of Claude models with image2md framework.
This example demonstrates how to create custom converters for Claude models
and register them with the Image2MarkdownFactory.
"""
import os
import sys
from pathlib import Path
import json
import base64
import anthropic
from datetime import datetime
import platform
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import image2md components
try:
    from image2md.llm_converter import LLMConverter, ProvenanceInfo
    from image2md.factory import Image2MarkdownFactory
except ImportError:
    print("Error: Could not import image2md components.")
    print("Make sure the package is installed: pip install -e ..")
    sys.exit(1)

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
output_dir = Path("claude_integration_output")
output_dir.mkdir(exist_ok=True)

print("Example: Full Integration of Claude Models with image2md")
print("=" * 80)

#---------------------------------------------------------------------------
# Step 1: Create a custom ProvenanceInfo dataclass for Claude
#---------------------------------------------------------------------------
@dataclass
class ClaudeProvenanceInfo(ProvenanceInfo):
    """Provenance information specific to Claude models"""
    # Add Claude-specific fields
    provider: str = "Anthropic"
    model_family: str = "Claude"
    request_id: Optional[str] = None
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields"""
        return asdict(self)

#---------------------------------------------------------------------------
# Step 2: Create a custom ClaudeConverter class
#---------------------------------------------------------------------------
class ClaudeConverter(LLMConverter):
    """Claude-specific implementation of the LLM converter."""
    
    DEFAULT_PROMPT = (
        "Convert this image to well-formatted markdown. Maintain the structure "
        "and formatting as much as possible, including headings, lists, and tables."
    )
    
    def __init__(
        self,
        api_key=None,
        model="claude-3-opus-20240229",
        max_tokens=4000,
        temperature=0.3,
        **kwargs
    ):
        """Initialize Claude converter with specific defaults."""
        # Initialize base attributes
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment variables")
            
        self.model = model
        self.provider = "anthropic"  # Used for internal tracking
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.llm_options = kwargs
        
        # Claude-specific setup
        print(f"  🔹 Initializing Claude converter with model: {self.model}")
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def _create_provenance(self, params, prompt) -> ClaudeProvenanceInfo:
        """Create Claude-specific provenance information"""
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Get system information
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "anthropic_version": anthropic.__version__
        }
        
        # Determine model information
        model_version = None
        if self.model.startswith("claude-3-7"):
            model_version = "3.7"
        elif self.model.startswith("claude-3"):
            model_version = "3"
        
        # Get model family from model name
        model_family = self.model.split("-")[0].capitalize()  # "Claude"
        
        # Return custom provenance object
        return ClaudeProvenanceInfo(
            timestamp=timestamp,
            model=self.model,
            model_version=model_version,
            model_family=model_family,
            provider="Anthropic",
            system_info=system_info,
            conversion_params={**params, "prompt": prompt}
        )
    
    def convert(self, image_path, save_json=False, json_output_path=None, 
               custom_prompt=None, **kwargs):
        """
        Convert an image to markdown using Claude.
        
        Args:
            image_path: Path to the image file
            save_json: Whether to save provenance information to JSON
            json_output_path: Path to save the JSON file
            custom_prompt: Custom prompt to use for conversion
            **kwargs: Additional parameters to pass to Claude API
        
        Returns:
            Markdown string representation of the image
        """
        print(f"  🔹 Converting {image_path} using Claude model: {self.model}")
        
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Get base64-encoded image 
        base64_image = self._encode_image(image_path)
        
        # Get parameters
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            **kwargs
        }
        
        # Get prompt
        prompt = custom_prompt or self.DEFAULT_PROMPT
        
        # Make API request to Claude
        try:
            message = self.client.messages.create(
                model=params["model"],
                max_tokens=params["max_tokens"],
                temperature=params["temperature"],
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
            
            # Extract markdown content
            markdown = message.content[0].text
            
            # Save provenance information if requested
            if save_json:
                provenance = self._create_provenance(params, prompt)
                
                # Add request-specific information
                try:
                    provenance.request_id = message.id
                except (AttributeError, TypeError):
                    # If message doesn't have an id field
                    pass
                
                if json_output_path is None:
                    json_output_path = image_path.with_suffix('.json')
                
                # Create JSON response with markdown and provenance
                json_result = {
                    "markdown": markdown,
                    "provenance": provenance.as_dict(),
                    "timestamp": provenance.timestamp,
                    "image_path": str(image_path),
                    "conversion_type": "claude",
                    "model": self.model
                }
                
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, indent=2, ensure_ascii=False)
            
            return markdown
            
        except Exception as e:
            print(f"Error during Claude API call: {e}")
            raise

#---------------------------------------------------------------------------
# Step 3: Create specific converters for different Claude models
#---------------------------------------------------------------------------
class ClaudeOpusConverter(ClaudeConverter):
    """Specific implementation for Claude 3 Opus"""
    
    def __init__(
        self,
        api_key=None,
        max_tokens=4000,
        temperature=0.3,
        **kwargs
    ):
        """Initialize with Claude 3 Opus model"""
        super().__init__(
            api_key=api_key,
            model="claude-3-opus-20240229",
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

class ClaudeSonnetConverter(ClaudeConverter):
    """Specific implementation for Claude 3.7 Sonnet"""
    
    def __init__(
        self,
        api_key=None,
        max_tokens=4000,
        temperature=0.2,  # Lower default temperature
        **kwargs
    ):
        """Initialize with Claude 3.7 Sonnet model"""
        super().__init__(
            api_key=api_key,
            model="claude-3-7-sonnet-20250219",
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )

#---------------------------------------------------------------------------
# Step 4: Register the converters with the Image2MarkdownFactory
#---------------------------------------------------------------------------
print("\nRegistering Claude converters with Image2MarkdownFactory...")
Image2MarkdownFactory.register_converter("claude", ClaudeConverter)
Image2MarkdownFactory.register_converter("claude-opus", ClaudeOpusConverter)
Image2MarkdownFactory.register_converter("claude-sonnet", ClaudeSonnetConverter)

# Get available converters
converters = Image2MarkdownFactory.available_converters()
print(f"Available converters: {', '.join(converters.keys())}")

#---------------------------------------------------------------------------
# Step 5: Use the registered converters through the factory
#---------------------------------------------------------------------------
print("\nUsing Claude converters through Image2MarkdownFactory...")

# Convert using Claude Opus
print("\n1. Converting with Claude 3 Opus:")
opus_result = Image2MarkdownFactory.convert(
    example_image_path,
    converter_type="claude-opus",
    output_path=output_dir / "claude_opus_output.md",
    api_key=api_key,
    save_json=True,
    json_output_path=output_dir / "claude_opus_output.json",
    custom_prompt="Convert this image to well-formatted markdown, preserving structure."
)
print(f"  ✅ Claude Opus conversion saved to: {opus_result}")

# Convert using Claude Sonnet
print("\n2. Converting with Claude 3.7 Sonnet:")
sonnet_result = Image2MarkdownFactory.convert(
    example_image_path,
    converter_type="claude-sonnet",
    output_path=output_dir / "claude_sonnet_output.md",
    api_key=api_key,
    save_json=True,
    json_output_path=output_dir / "claude_sonnet_output.json",
    custom_prompt="Convert this image to well-formatted markdown, preserving structure."
)
print(f"  ✅ Claude Sonnet conversion saved to: {sonnet_result}")

# Convert using generic Claude constructor with model specification
print("\n3. Converting with generic Claude converter and custom model:")
custom_result = Image2MarkdownFactory.convert(
    example_image_path,
    converter_type="claude",
    output_path=output_dir / "claude_custom_output.md",
    api_key=api_key,
    model="claude-3-haiku-20240307",  # Using Haiku model
    max_tokens=1000,
    temperature=0.4,
    save_json=True,
    json_output_path=output_dir / "claude_custom_output.json",
    custom_prompt="Convert this image to simple markdown."
)
print(f"  ✅ Custom Claude model conversion saved to: {custom_result}")

#---------------------------------------------------------------------------
# Step 6: Using the converter directly (without factory) for more control
#---------------------------------------------------------------------------
print("\n4. Using Claude converter directly (without factory):")

# Create a custom Claude converter instance
custom_claude = ClaudeConverter(
    api_key=api_key,
    model="claude-3-5-sonnet-20240620",  # Another model variant
    max_tokens=2000,
    temperature=0.3
)

# Use the converter directly
direct_result = custom_claude.save_markdown(
    example_image_path,
    output_dir / "claude_direct_output.md",
    save_json=True,
    json_output_path=output_dir / "claude_direct_output.json",
    custom_prompt="Convert this image to markdown with special attention to table formatting."
)
print(f"  ✅ Direct Claude conversion saved to: {direct_result}")

print("\n✨ All conversions completed successfully!")
print(f"📁 Results saved in: {output_dir.absolute()}")

# If someone imports this module, these examples won't run automatically
if __name__ == "__main__":
    print("\nThis script has finished executing.")
    print("You can now examine the output files to compare the different Claude model outputs.") 