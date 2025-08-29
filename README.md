# image2md

A Python library and CLI tool for converting images to well-formatted Markdown using multiple AI backends.

## Features

- **Multiple AI Providers**: OpenAI, Anthropic Claude, Google Gemini, Azure Document Intelligence
- **Basic Converters**: OCR, Vision, Structure-aware conversion
- **Provenance Tracking**: Full conversion history with model parameters
- **CLI & Python API**: Use via command line or integrate into your code
- **Flexible Configuration**: Environment files, API keys, custom models

## Installation

```bash
# Basic installation
pip install image2md

# With all AI providers
pip install image2md[all]

# Individual providers
pip install image2md[azure]    # Azure Document Intelligence
pip install image2md[llm]      # OpenAI, Anthropic, Gemini
```

## Quick Start

### CLI Usage

```bash
# Convert with different AI providers
image2md image.png --type openai --output result.md
image2md image.png --type anthropic --output result.md  
image2md image.png --type gemini --output result.md
image2md image.png --type azure --output result.md

# With provenance tracking
image2md image.png --type openai --save-json --output result.md
```

### Python API

```python
from pathlib import Path
from image2md import Image2MarkdownFactory

# OpenAI GPT
result = Image2MarkdownFactory.convert(
    Path("image.png"),
    converter_type="openai",
    output_path=Path("result.md"),
    model="gpt-4o",
    save_json=True
)

# Anthropic Claude
result = Image2MarkdownFactory.convert(
    Path("image.png"),
    converter_type="anthropic",
    output_path=Path("result.md"),
    model="claude-3-7-sonnet-20250219"
)

# Google Gemini
result = Image2MarkdownFactory.convert(
    Path("image.png"),
    converter_type="gemini",
    output_path=Path("result.md"),
    model="gemini-2.5-flash"
)
```

## Configuration

### Environment Variables

Create a `.env` file (automatically loaded):

```env
# AI Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Azure Document Intelligence
AZURE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_API_KEY=your_azure_key
```

### Direct Configuration

```python
# Pass credentials directly
Image2MarkdownFactory.convert(
    image_path,
    converter_type="openai",
    api_key="your-api-key",
    model="gpt-4o",
    max_tokens=4000,
    temperature=0.2
)
```

## Available Converters

| Converter | Description | Best For |
|-----------|-------------|----------|
| `openai` | OpenAI GPT models with vision | High-quality text extraction |
| `anthropic` | Anthropic Claude models | Detailed document analysis |
| `gemini` | Google Gemini models | Fast, cost-effective conversion |
| `azure` | Azure Document Intelligence | Professional document processing |
| `vision` | OpenAI Vision API | Quick image understanding |
| `ocr` | Basic OCR extraction | Simple text extraction |
| `structure` | Structure-aware conversion | Tables, headings, lists |

## Advanced Usage

### Custom Models

```python
# Use specific model versions
Image2MarkdownFactory.convert(
    image_path,
    converter_type="openai",
    model="gpt-5",  # Latest models
    max_completion_tokens=4000  # For newer models
)
```

### Provenance Tracking

```python
# Save full conversion details
Image2MarkdownFactory.convert(
    image_path,
    converter_type="anthropic",
    save_json=True,
    json_output_path=Path("conversion_details.json")
)
```

### Custom Converters

```python
from image2md.factory import Image2MarkdownFactory
from your_module import CustomConverter

# Register your own converter
Image2MarkdownFactory.register_converter("custom", CustomConverter)

# Use it
Image2MarkdownFactory.convert(
    image_path,
    converter_type="custom",
    **your_custom_options
)
```

## CLI Reference

```bash
# Basic usage
image2md <image_path> --type <converter> --output <output_path>

# Common options
--type {openai,anthropic,gemini,azure,vision,ocr,structure}
--output OUTPUT_FILE
--save-json                    # Save conversion details
--env-file CUSTOM_ENV         # Use custom .env file
--no-env-file                 # Disable .env loading

# Provider-specific options
--openai-model MODEL          # OpenAI model name
--anthropic-model MODEL       # Claude model name  
--gemini-model MODEL          # Gemini model name
--azure-endpoint URL          # Azure endpoint
```

## Development

```bash
# Install for development
pip install -e .[all]

# Run tests
python -m pytest tests/

# Build package
python -m build
```

## Examples

Complete working examples are available in the [`examples/`](examples/) directory:

- **Basic Usage**: [`examples/example_usage.py`](examples/example_usage.py)
- **Provider Comparison**: [`examples/compare_models.py`](examples/compare_models.py)
- **Custom Integration**: [`examples/anthropic_integration.py`](examples/anthropic_integration.py)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.