#!/usr/bin/env python3
"""Example of extending the LLM converter to support additional models."""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the current directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Example image
example_image_path = Path(__file__).parent / "83635935.png"
if not example_image_path.exists():
    print(f"Error: Example image not found at {example_image_path}")
    sys.exit(1)

# Create output directory for results
output_dir = Path("extended_llm_converter_output")
output_dir.mkdir(exist_ok=True)

print("Example: Extending the LLM Converter to Support Additional Models")
print("=" * 80)

try:
    from image2md.llm_converter import LLMConverter, ProvenenanceInfo
    from image2md.factory import Image2MarkdownFactory
    
    #---------------------------------------------------------------------------
    # Example 1: Creating a Custom LLM Converter subclass for Claude
    #---------------------------------------------------------------------------
    print("\nExample 1: Creating a Claude Converter Subclass")
    print("-" * 70)
    
    class ClaudeLLMConverter(LLMConverter):
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
            temperature=0.5,
            **kwargs
        ):
            """Initialize Claude converter with specific defaults."""
            # Don't call parent's __init__ to avoid provider validation
            # Instead, initialize all the attributes manually
            self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
            self.model = model
            self.provider = "anthropic"
            self.max_tokens = max_tokens
            self.temperature = temperature
            self.llm_options = kwargs
            
            # Claude-specific setup here
            print("  🔹 Initializing Claude converter")
            print(f"  🔹 Model: {self.model}")
            
            # In a real implementation, you would do something like:
            # from anthropic import Anthropic
            # self.client = Anthropic(api_key=self.api_key)
            
            # Instead we'll create a mock client for demonstration
            self.client = type('MockClient', (), {
                'messages': type('Messages', (), {
                    'create': lambda **kwargs: type('Response', (), {
                        'content': type('Content', (), {
                            'text': "# Claude Simulated Response\n\nThis is a sample response from Claude."
                        })()
                    })()
                })()
            })()
        
        def convert(self, image_path, save_json=False, json_output_path=None, 
                   custom_prompt=None, **kwargs):
            """
            Convert an image to markdown using Claude.
            
            In a real implementation, this would use Anthropic's API.
            For this example, we'll simulate the response.
            """
            print(f"  🔹 Converting {image_path} using Claude")
            
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Get base64-encoded image 
            base64_image = self._encode_image(image_path)
            
            # Get additional parameters
            prompt = custom_prompt or self.DEFAULT_PROMPT
            
            # In a real implementation, you would send the image to Claude
            # and get back a response.
            
            # For this example, we'll return simulated markdown
            markdown = f"""# Converted with Claude ({self.model})

## Image Analysis
This is a document from Loews Corporation, converted using the Claude model.

## Document Content
**Loews Corporation**
687 Madison Avenue, New York, N.Y. 10021-8087
(212) 545-2920 Fax (212) 935-6801

**Barry Hirsch**
Senior Vice President
Secretary & General Counsel

---

*Note: This is a simulation of Claude's output for demonstration purposes.*
"""
            
            # Create provenance information
            params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                **kwargs
            }
            
            # Create provenance information
            if save_json:
                provenance = self._create_provenance(params, prompt)
                
                if json_output_path is None:
                    json_output_path = image_path.with_suffix('.json')
                
                # Create JSON response with markdown and provenance
                json_result = {
                    "markdown": markdown,
                    "provenance": provenance.as_dict(),
                    "timestamp": provenance.timestamp,
                    "image_path": str(image_path),
                    "conversion_type": "claude",
                }
                
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, indent=2, ensure_ascii=False)
            
            return markdown
    
    
    #---------------------------------------------------------------------------
    # Example 2: Creating a Custom LLM Converter subclass for Gemini
    #---------------------------------------------------------------------------
    print("\nExample 2: Creating a Gemini Converter Subclass")
    print("-" * 70)
    
    class GeminiLLMConverter(LLMConverter):
        """Gemini-specific implementation of the LLM converter."""
        
        DEFAULT_PROMPT = (
            "Convert this image to well-formatted markdown with proper headings, lists, "
            "and tables. Preserve the original formatting as much as possible."
        )
        
        def __init__(
            self,
            api_key=None,
            model="gemini-pro-vision",
            max_tokens=2048,
            temperature=0.4,
            **kwargs
        ):
            """Initialize Gemini converter with specific defaults."""
            # Don't call parent's __init__ to avoid provider validation
            # Instead, initialize all the attributes manually
            self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
            self.model = model
            self.provider = "google"
            self.max_tokens = max_tokens
            self.temperature = temperature
            self.llm_options = kwargs
            
            # Gemini-specific setup
            print("  🔹 Initializing Gemini converter")
            print(f"  🔹 Model: {self.model}")
            
            # In a real implementation:
            # import google.generativeai as genai
            # genai.configure(api_key=self.api_key)
            # self.client = genai.GenerativeModel(self.model)
        
        def convert(self, image_path, save_json=False, json_output_path=None,
                  custom_prompt=None, **kwargs):
            """
            Convert an image to markdown using Gemini.
            
            In a real implementation, this would use Google's Generative AI API.
            For this example, we'll simulate the response.
            """
            print(f"  🔹 Converting {image_path} using Gemini")
            
            if not image_path.exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Get base64-encoded image
            base64_image = self._encode_image(image_path)
            
            # Get additional parameters
            prompt = custom_prompt or self.DEFAULT_PROMPT
            
            # Simulated markdown response
            markdown = f"""# Document Analysis by Gemini

## Loews Corporation Fax Cover Sheet

**From**: Barry Hirsch  
**Title**: Senior Vice President, Secretary & General Counsel  
**Company**: Loews Corporation  
**Address**: 687 Madison Avenue, New York, NY 10021-8087  
**Phone**: (212) 545-2920  
**Fax**: (212) 935-6801  

*Note: This is a simulation of Gemini's output for demonstration purposes.*
"""
            
            # Create provenance information
            params = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                **kwargs
            }
            
            if save_json:
                provenance = self._create_provenance(params, prompt)
                
                if json_output_path is None:
                    json_output_path = image_path.with_suffix('.json')
                
                # Create JSON response with markdown and provenance
                json_result = {
                    "markdown": markdown,
                    "provenance": provenance.as_dict(),
                    "timestamp": provenance.timestamp,
                    "image_path": str(image_path),
                    "conversion_type": "gemini",
                }
                
                with open(json_output_path, 'w', encoding='utf-8') as f:
                    json.dump(json_result, f, indent=2, ensure_ascii=False)
            
            return markdown
    
    
    #---------------------------------------------------------------------------
    # Example 3: Registering custom converters with the factory
    #---------------------------------------------------------------------------
    print("\nExample 3: Registering Custom Converters with the Factory")
    print("-" * 70)
    
    # Register our custom converters with the factory
    Image2MarkdownFactory.register_converter("claude", ClaudeLLMConverter)
    Image2MarkdownFactory.register_converter("gemini", GeminiLLMConverter)
    
    # Get available converters
    converters = Image2MarkdownFactory.available_converters()
    print(f"Available converters: {', '.join(converters.keys())}")
    
    # Use the factory to create instances of our custom converters
    claude_converter = Image2MarkdownFactory.get_converter("claude", api_key="simulated_claude_key")
    output_path = output_dir / "claude_output.md"
    json_output_path = output_dir / "claude_output.json"
    
    # Save the result
    claude_markdown = claude_converter.save_markdown(
        example_image_path,
        output_path,
        save_json=True,
        json_output_path=json_output_path,
        custom_prompt="Convert this image to markdown focusing on document structure."
    )
    
    print(f"  ✅ Claude markdown saved to: {output_path}")
    print(f"  ✅ Provenance information saved to: {json_output_path}")
    
    
    # Do the same with Gemini
    gemini_converter = Image2MarkdownFactory.get_converter("gemini", api_key="simulated_gemini_key")
    output_path = output_dir / "gemini_output.md"
    json_output_path = output_dir / "gemini_output.json"
    
    # Save the result
    gemini_markdown = gemini_converter.save_markdown(
        example_image_path,
        output_path,
        save_json=True,
        json_output_path=json_output_path,
        custom_prompt="Convert this image to markdown with attention to details."
    )
    
    print(f"  ✅ Gemini markdown saved to: {output_path}")
    print(f"  ✅ Provenance information saved to: {json_output_path}")
    
    
    #---------------------------------------------------------------------------
    # Example 4: Using the factory directly with converter_type
    #---------------------------------------------------------------------------
    print("\nExample 4: Using the Factory Directly with Custom Converters")
    print("-" * 70)
    
    # Convert using claude directly from factory
    claude_result = Image2MarkdownFactory.convert(
        example_image_path,
        converter_type="claude",
        output_path=output_dir / "claude_factory_output.md",
        api_key="simulated_claude_key",
        save_json=True,
        json_output_path=output_dir / "claude_factory_output.json",
        custom_prompt="Analyze this document in detail."
    )
    
    print(f"  ✅ Claude conversion via factory saved to: {claude_result}")
    
    # Convert using gemini directly from factory
    gemini_result = Image2MarkdownFactory.convert(
        example_image_path,
        converter_type="gemini",
        output_path=output_dir / "gemini_factory_output.md",
        api_key="simulated_gemini_key",
        save_json=True,
        json_output_path=output_dir / "gemini_factory_output.json",
        temperature=0.3,
        custom_prompt="Extract all text from this image."
    )
    
    print(f"  ✅ Gemini conversion via factory saved to: {gemini_result}")
    
    
    print("\n✨ All examples completed successfully!")
    print(f"📁 Results saved in: {output_dir.absolute()}")

except ImportError as e:
    print(f"Error: {e}")
    print("Make sure you have the required packages installed.")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 