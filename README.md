# image2md - Image to Markdown Conversion Tool

A Python library and command-line tool for converting images to well-formatted Markdown content.

## Features

- Multiple converter backends:
  - **OCR**: Basic OCR-based text extraction
  - **Vision**: AI-powered image understanding using OpenAI's Vision models
  - **Structure**: Structure-aware conversion with table, heading, and list detection
  - **Azure**: Integration with Azure Document Intelligence for high-quality document conversion
  - **LLM**: LLM-based conversion with provenance tracking using OpenAI models
  - **Custom Extensions**: Support for custom converters (Claude, Gemini, etc.)

## Installation

```bash
# Basic installation
pip install image2md

# With Azure Document Intelligence support
pip install image2md[azure]

# For LLM and Claude extensions
pip install image2md[llm]

```

## Quick Start

### Python API

```python
from pathlib import Path
from image2md import Image2MarkdownFactory

# Basic conversion using Vision model (OpenAI)
markdown = Image2MarkdownFactory.convert(
    Path("path/to/image.png"), 
    converter_type="vision"
)

# Using Azure Document Intelligence
markdown = Image2MarkdownFactory.convert(
    Path("path/to/image.png"), 
    converter_type="azure",
    endpoint="your-azure-endpoint",
    api_key="your-azure-api-key"
)
```

### Command Line

```bash
# Basic usage with Vision model
image2md path/to/image.png --type vision --output output.md

# Using Azure Document Intelligence
image2md path/to/image.png --type azure --output output.md
```

## Environment Configuration

image2md supports multiple ways to configure API keys and other sensitive settings:

### Using .env Files (Recommended)

The CLI automatically loads environment variables from a `.env` file in the current directory. Create a `.env` file with your API keys:

```
# .env file example
OPENAI_API_KEY=your_openai_key_here
AZURE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_API_KEY=your_azure_key_here
```

This behavior is enabled by default and doesn't require any additional dependencies.

#### CLI Options for .env Files

- Use a custom .env file path: `--env-file /path/to/custom.env`
- Disable automatic .env loading: `--no-env-file`

### Alternative Configuration Methods

You can also provide configuration:

1. As system environment variables
2. Directly in code when using the library
3. As command-line arguments

Examples:

```bash
# As environment variables
export OPENAI_API_KEY=your_key_here
image2md image.png -t llm

# As command-line arguments
image2md image.png -t llm --llm-api-key your_key_here
```

## Azure Document Intelligence Integration

The `AzureDocumentConverter` integrates with Azure Document Intelligence to provide high-quality markdown conversion with support for complex documents, tables, headings, and more.

### Setting Up Azure Document Intelligence

1. Create an Azure Document Intelligence resource in the Azure portal
2. Get your endpoint URL and API key
3. Install the required dependencies:
   ```bash
   pip install azure-ai-documentintelligence>=1.0.0 image2md
   ```

### Authentication Options

You can authenticate in multiple ways:

#### Environment Variables

Set these environment variables:
```bash
export AZURE_ENDPOINT="https://your-resource-name.cognitiveservices.azure.com"
export AZURE_API_KEY="your-api-key"
```

#### Direct Parameters

Provide credentials directly:
```python
from image2md import AzureDocumentConverter

converter = AzureDocumentConverter(
    endpoint="https://your-resource-name.cognitiveservices.azure.com",
    api_key="your-api-key"
)
```

### Python API Examples

#### Basic Usage

```python
from pathlib import Path
from image2md import AzureDocumentConverter

# Initialize converter
converter = AzureDocumentConverter()  # Uses environment variables

# Convert image to markdown
markdown = converter.convert(Path("path/to/image.png"))

# Save to file
with open("output.md", "w", encoding="utf-8") as f:
    f.write(markdown)

# Or use save_markdown method
output_path = converter.save_markdown(
    Path("path/to/image.png"), 
    Path("output.md")
)
```

#### Using the Factory

```python
from pathlib import Path
from image2md.factory import Image2MarkdownFactory

# Get Azure converter with specific options
converter = Image2MarkdownFactory.get_converter(
    converter_type="azure",
    endpoint="https://your-resource-name.cognitiveservices.azure.com",
    api_key="your-azure-api-key",
    api_version="2024-11-30",  # Optional, must be >= 2024-11-30 for markdown support
    model_id="prebuilt-layout"  # Optional, must be "prebuilt-layout" for markdown support
)

# Convert image
markdown = converter.convert(Path("path/to/image.png"))

# One-step conversion and save
output_path = Image2MarkdownFactory.convert(
    Path("path/to/image.png"),
    converter_type="azure",
    output_path=Path("output.md"),
    save_json=True  # Save the full JSON response from Azure
)
```

### Command Line Examples

#### Basic Usage

```bash
# Using environment variables for authentication
image2md --type azure path/to/image.png --output output.md

# Save the full JSON response
image2md --type azure path/to/image.png --output output.md --save-json

# Specify output path for the JSON response
image2md --type azure path/to/image.png --output output.md --save-json --json-output output.json
```

#### With Explicit Credentials

```bash
# Provide Azure credentials directly
image2md --type azure path/to/image.png \
  --output output.md \
  --azure-endpoint "https://your-resource-name.cognitiveservices.azure.com" \
  --azure-api-key "your-api-key"
```

#### Advanced Configuration

```bash
# Using a specific API version
image2md --type azure path/to/image.png \
  --output output.md \
  --azure-api-version "2024-11-30"

# Using a specific model ID
image2md --type azure path/to/image.png \
  --output output.md \
  --azure-model-id "prebuilt-layout"
```

### Azure Document Intelligence Features

Azure Document Intelligence provides several benefits for Markdown conversion:

- Maintainance of document structure and layout
- Excellent detection of tables and conversion to Markdown tables
- Preservation of headings, lists, formatting, etc.
- Multi-language support
- OCR capabilities for text extraction

### Customizing Azure Document Intelligence

The Azure converter accepts additional parameters that are passed to the Azure SDK:

```python
from image2md import AzureDocumentConverter
from azure.ai.documentintelligence.models import DocumentAnalysisFeature

converter = AzureDocumentConverter()

# Customize features
markdown = converter.convert(
    Path("path/to/image.png"),
    features=[
        DocumentAnalysisFeature.KEY_VALUE_PAIRS,
        DocumentAnalysisFeature.LANGUAGES,
        # Add other features as needed
    ],
    string_index_type="utf16CodeUnit",
    # Add other Azure-specific parameters
)
```

### Troubleshooting Azure Integration

1. **Authentication Issues**:
   - Verify your endpoint URL and API key
   - Try setting them explicitly rather than using environment variables

2. **Conversion Issues**:
   - Ensure you're using API version >= 2024-11-30
   - Ensure you're using the "prebuilt-layout" model

3. **Import Errors**:
   - Ensure you have the Azure SDK installed: `pip install azure-ai-documentintelligence>=1.0.0`

4. **Parameter Conflicts**:
   - Avoid passing the same parameters in both constructor and convert method
   - The converter automatically handles conflicting parameters

## LLM-Based Conversion with Provenance

The `LLMConverter` uses Large Language Models to convert images to markdown with detailed provenance tracking.

### Setting Up LLM Conversion

1. Get your OpenAI API key
2. Install the required dependencies:
   ```bash
   pip install openai>=1.0.0 image2md[llm]
   ```

### Authentication Options

You can authenticate in multiple ways:

#### Environment Variables

Set the environment variable:
```bash
export OPENAI_API_KEY="your-api-key"
```

#### Direct Parameters

Provide credentials directly:
```python
from image2md import LLMConverter

converter = LLMConverter(
    api_key="your-openai-api-key",
    model="gpt-4o",
    provider="openai",
    max_tokens=4000,
    temperature=0.3
)
```

### Python API Examples

#### Basic Usage

```python
from pathlib import Path
from image2md import LLMConverter

# Initialize converter
converter = LLMConverter()  # Uses environment variables

# Convert image to markdown with provenance tracking
result_path = converter.save_markdown(
    Path("path/to/image.png"),
    Path("output.md"),
    save_json=True,                   # Save provenance information
    json_output_path=Path("output.json"),
    custom_prompt="Convert this image to well-formatted markdown with proper headings and structure."
)
```

#### Using the Factory

```python
from pathlib import Path
from image2md.factory import Image2MarkdownFactory

# One-step conversion using the factory
result_path = Image2MarkdownFactory.convert(
    Path("path/to/image.png"),
    converter_type="llm",
    output_path=Path("output.md"),
    api_key="your-openai-api-key",
    model="gpt-4o",
    provider="openai",
    max_tokens=4000,
    temperature=0.3,
    save_json=True,
    json_output_path=Path("output.json"),
    custom_prompt="Convert this image to well-formatted markdown."
)
```

### Command Line Examples

```bash
# Basic usage
python -m image2md.cli --type llm path/to/image.png --output output.md

# With custom parameters and provenance tracking
python -m image2md.cli \
  --type llm \
  path/to/image.png \
  --output output.md \
  --llm-model "gpt-4o" \
  --llm-provider "openai" \
  --llm-max-tokens 4000 \
  --llm-temperature 0.3 \
  --llm-prompt "Convert this image to markdown with proper structure." \
  --save-json \
  --json-output output.json
```

## Extending with Custom Converters

### Claude (Anthropic) Integration

You can easily extend image2md with other LLM providers, such as Anthropic's Claude models:

1. Install the required dependencies:
   ```bash
   pip install anthropic>=0.8.0 image2md[llm]
   ```

2. Create a custom converter class:
   ```python
   from image2md.base import Image2MarkdownConverter
   from image2md.factory import Image2MarkdownFactory
   import anthropic
   import base64
   import json
   from pathlib import Path
   from datetime import datetime
   import platform
   
   class AnthropicConverter(Image2MarkdownConverter):
       """Anthropic-specific implementation for image-to-markdown conversion."""
       
       DEFAULT_PROMPT = "Convert this image to well-formatted markdown."
       
       def __init__(
           self,
           api_key=None,
           model="claude-3-7-sonnet-20250219",  # Default to Claude 3.7 Sonnet
           max_tokens=4000,
           temperature=0.3,
           **kwargs
       ):
           # Get API key from environment if not provided
           self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
           if not self.api_key:
               raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")
               
           self.model = model
           self.max_tokens = max_tokens
           self.temperature = temperature
           self.options = kwargs
           
           # Initialize Anthropic client
           self.client = anthropic.Anthropic(api_key=self.api_key)
       
       def _encode_image(self, image_path):
           """Encode image to base64 string"""
           with open(image_path, "rb") as image_file:
               return base64.b64encode(image_file.read()).decode("utf-8")
       
       def convert(self, image_path, **kwargs):
           """Convert image to markdown using Claude"""
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
                   "conversion_type": "claude"
               }
               
               with open(json_output_path, 'w', encoding='utf-8') as f:
                   json.dump(json_result, f, indent=2, ensure_ascii=False)
           
           return markdown
           
       def save_markdown(self, image_path, output_path=None, **kwargs):
           """Convert an image and save the markdown output"""
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
   ```

3. Register Anthropic converter with the factory:
   ```python
   # Register Anthropic converter with the factory
   Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)
   
   # Use the converter through the factory
   result_path = Image2MarkdownFactory.convert(
       Path("path/to/image.png"),
       converter_type="anthropic",
       output_path=Path("result.md"),
       api_key="your_anthropic_api_key",
       model="claude-3-7-sonnet-20250219",
       save_json=True,
       json_output_path=Path("result.json"),
       custom_prompt="Convert this image to well-formatted markdown."
   )
   ```

4. Compare results between different models:
   ```python
   # Create a comparison script
   from pathlib import Path
   import json
   import difflib
   
   # Paths to conversion results
   openai_md_path = Path("openai_output/result.md")
   claude_md_path = Path("claude_output/result.md")
   
   # Create HTML diff to compare outputs
   diff = difflib.HtmlDiff()
   diff_html = diff.make_file(
       openai_md_path.read_text().splitlines(),
       claude_md_path.read_text().splitlines(),
       fromdesc="OpenAI GPT-4o",
       todesc="Claude 3.7 Sonnet"
   )
   
   # Write comparison to file
   with open("model_comparison.html", "w") as f:
       f.write(diff_html)
   ```

A complete implementation example with tests is available in the `examples/` directory.

### Testing the Claude Extension

Comprehensive tests have been created to verify the Claude integration:

```python
# examples/test_anthropic_converter.py
import unittest
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

from image2md.factory import Image2MarkdownFactory
from claude_integration import AnthropicConverter

class TestAnthropicConverter(unittest.TestCase):
    """Test cases for the Anthropic converter."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Check for API key and test image
        cls.api_key = os.environ.get("ANTHROPIC_API_KEY")
        cls.image_path = Path(__file__).parent / "83635935.png"
        cls.test_dir = Path(__file__).parent / "claude_test_output"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Register Anthropic converter with the factory
        Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)
    
    def test_convert_method(self):
        """Test the convert method."""
        # Initialize converter with small max_tokens to speed up test
        converter = AnthropicConverter(api_key=self.api_key)
        converter.max_tokens = 1000
        
        # Convert the image
        result = converter.convert(
            self.image_path, 
            custom_prompt="Convert this to very brief markdown."
        )
        
        # Verify we got reasonable markdown
        self.assertGreater(len(result), 100)
        self.assertIn("#", result)  # Should have at least one heading
    
    # Additional tests...

if __name__ == "__main__":
    unittest.main(verbosity=2)
```

Run the test with:

```bash
# Run the standalone test
python examples/test_anthropic_converter.py

# Or run as part of the test suite
python -m pytest tests/test_anthropic_converter.py
```

### Comparing Specific Claude Models

You can compare the output from different Claude models (or any other models) to evaluate their performance:

```bash
python examples/claude_sonnet_conversion.py    # Generate Claude 3.7 Sonnet output
python examples/claude_conversion.py           # Generate Claude 3 Opus output
python examples/compare_claude_models.py       # Compare the outputs
```

The comparison output includes:
- Side-by-side HTML diff of the markdown outputs
- Comparison of metrics like character count and line count
- Analysis of formatting differences
- Comparison of model parameters used

### Command Line Integration for Custom Converters

To use custom converters like Claude with the CLI, you need to register them with the factory before invocation. You can create a simple wrapper script:

```python
# claude_cli_wrapper.py
#!/usr/bin/env python3
import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the CLI module
from image2md.cli import main as image2md_cli
from image2md.factory import Image2MarkdownFactory

# Import and register your custom converter
from claude_integration import AnthropicConverter
Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)

# Run the CLI with the original arguments
if __name__ == "__main__":
    image2md_cli()
```

Then use it like this:

```bash
# Make sure ANTHROPIC_API_KEY is set in your environment or .env file
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Basic usage with Claude model
python claude_cli_wrapper.py path/to/image.png --type anthropic --output output.md

# With custom parameters and provenance tracking
python claude_cli_wrapper.py \
  --type anthropic \
  path/to/image.png \
  --output output.md \
  --claude-model "claude-3-7-sonnet-20250219" \
  --claude-max-tokens 2000 \
  --claude-temperature 0.2 \
  --claude-prompt "Convert this image to markdown with proper structure." \
  --save-json \
  --json-output output.json
```

The wrapper script approach allows you to extend the CLI with custom converters without modifying the core code.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Complete Examples

### Converting an Image to Markdown with LLM

```python
from image2md import LLMConverter
from pathlib import Path
import os

# Initialize converter with options
converter = LLMConverter(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    provider="openai",
    max_tokens=4000,
    temperature=0.3
)

# Convert image to markdown with provenance tracking
result_path = converter.save_markdown(
    Path("path/to/image.png"),
    Path("output/result.md"),
    save_json=True,
    json_output_path=Path("output/provenance.json"),
    custom_prompt="Convert this image to well-formatted markdown."
)

print(f"Conversion complete! Output saved to: {result_path}")
```

### Converting an Image with Claude and Comparing to OpenAI

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from image2md import LLMConverter
from image2md.factory import Image2MarkdownFactory
from claude_integration import AnthropicConverter
import json
import difflib

# Load environment variables
load_dotenv()

# Prepare output directories
output_dir = Path("model_comparison")
output_dir.mkdir(exist_ok=True)

# Register Anthropic converter with the factory
Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)

# Convert with OpenAI
openai_result = Image2MarkdownFactory.convert(
    Path("path/to/image.png"),
    converter_type="llm",
    output_path=output_dir / "openai_result.md",
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    save_json=True,
    json_output_path=output_dir / "openai_result.json",
    custom_prompt="Convert this image to well-formatted markdown."
)

# Convert with Claude
claude_result = Image2MarkdownFactory.convert(
    Path("path/to/image.png"),
    converter_type="anthropic",
    output_path=output_dir / "claude_result.md",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-7-sonnet-20250219",
    save_json=True,
    json_output_path=output_dir / "claude_result.json",
    custom_prompt="Convert this image to well-formatted markdown."
)

# Compare results
with open(output_dir / "openai_result.md", "r") as f1:
    openai_content = f1.read()

with open(output_dir / "claude_result.md", "r") as f2:
    claude_content = f2.read()

# Generate HTML diff
diff = difflib.HtmlDiff()
diff_html = diff.make_file(
    openai_content.splitlines(),
    claude_content.splitlines(),
    fromdesc="OpenAI GPT-4o",
    todesc="Claude 3.7 Sonnet"
)
with open(output_dir / "comparison.html", "w") as f:
    f.write(diff_html)

print(f"Comparison complete! HTML diff saved to: {output_dir / 'comparison.html'}")
```

## License

MIT 

### Using Different Converters from CLI

The image2md module supports various converters that can be selected from the command line:

```bash
# OCR converter - basic OCR-based text extraction
python -m image2md.cli --type ocr path/to/image.png --output output.md

# Vision converter - AI-powered image understanding
python -m image2md.cli --type vision path/to/image.png --output output.md

# Structure converter - structure-aware conversion
python -m image2md.cli --type structure path/to/image.png --output output.md

# Azure Document Intelligence converter
python -m image2md.cli --type azure path/to/image.png --output output.md

# LLM-based converter with OpenAI
python -m image2md.cli --type llm path/to/image.png --output output.md
```

This approach makes it easy to compare the output quality of different conversion methods for the same image.

## Complete Examples

### Converting an Image to Markdown with LLM

```python
from image2md import LLMConverter
from pathlib import Path
import os

# Initialize converter with options
converter = LLMConverter(
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    provider="openai",
    max_tokens=4000,
    temperature=0.3
)

# Convert image to markdown with provenance tracking
result_path = converter.save_markdown(
    Path("path/to/image.png"),
    Path("output/result.md"),
    save_json=True,
    json_output_path=Path("output/provenance.json"),
    custom_prompt="Convert this image to well-formatted markdown."
)

print(f"Conversion complete! Output saved to: {result_path}")
```

### Converting an Image with Claude and Comparing to OpenAI

```python
import os
from pathlib import Path
from dotenv import load_dotenv
from image2md import LLMConverter
from image2md.factory import Image2MarkdownFactory
from claude_integration import AnthropicConverter
import json
import difflib

# Load environment variables
load_dotenv()

# Prepare output directories
output_dir = Path("model_comparison")
output_dir.mkdir(exist_ok=True)

# Register Anthropic converter with the factory
Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)

# Convert with OpenAI
openai_result = Image2MarkdownFactory.convert(
    Path("path/to/image.png"),
    converter_type="llm",
    output_path=output_dir / "openai_result.md",
    api_key=os.environ.get("OPENAI_API_KEY"),
    model="gpt-4o",
    save_json=True,
    json_output_path=output_dir / "openai_result.json",
    custom_prompt="Convert this image to well-formatted markdown."
)

# Convert with Claude
claude_result = Image2MarkdownFactory.convert(
    Path("path/to/image.png"),
    converter_type="anthropic",
    output_path=output_dir / "claude_result.md",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    model="claude-3-7-sonnet-20250219",
    save_json=True,
    json_output_path=output_dir / "claude_result.json",
    custom_prompt="Convert this image to well-formatted markdown."
)

# Compare results
with open(output_dir / "openai_result.md", "r") as f1:
    openai_content = f1.read()

with open(output_dir / "claude_result.md", "r") as f2:
    claude_content = f2.read()

# Generate HTML diff
diff = difflib.HtmlDiff()
diff_html = diff.make_file(
    openai_content.splitlines(),
    claude_content.splitlines(),
    fromdesc="OpenAI GPT-4o",
    todesc="Claude 3.7 Sonnet"
)
with open(output_dir / "comparison.html", "w") as f:
    f.write(diff_html)

print(f"Comparison complete! HTML diff saved to: {output_dir / 'comparison.html'}")
``` 