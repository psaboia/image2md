# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

image2md is a Python library and CLI tool for converting images to well-formatted Markdown content using multiple AI backends including OCR, OpenAI Vision, Azure Document Intelligence, OpenAI GPT models, Anthropic Claude, and Google Gemini.

## Development Commands

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_image2md.py

# Run tests with verbose output
python -m pytest -v tests/

# Test a specific converter
python -m pytest tests/test_azure_converter.py
```

### Package Management
```bash
# Install in development mode
pip install -e .

# Install with optional dependencies
pip install -e .[azure]    # Azure Document Intelligence
pip install -e .[llm]      # LLM support (OpenAI, Anthropic, Gemini)
pip install -e .[all]      # All optional dependencies

# Build package
python -m build
```

### CLI Usage
```bash
# Basic usage
python -m image2md.cli path/to/image.png --type vision --output result.md

# Using different converters
python -m image2md.cli image.png --type azure --output result.md
python -m image2md.cli image.png --type llm --output result.md --save-json
python -m image2md.cli image.png --type anthropic --output result.md  # requires custom registration

# With environment file
python -m image2md.cli --env-file custom.env image.png --type llm --output result.md
```

## Architecture

### Core Components

- **Base Interface**: `image2md/base.py` - Abstract `Image2MarkdownConverter` class that all converters implement
- **Factory Pattern**: `image2md/factory.py` - `Image2MarkdownFactory` manages converter instantiation and registration
- **CLI Interface**: `image2md/cli.py` - Command-line interface with automatic .env file loading

### Converter Types

1. **OCRConverter** (`ocr_converter.py`) - Basic OCR text extraction
2. **VisionConverter** (`vision_converter.py`) - OpenAI Vision API integration  
3. **StructureConverter** (`structure_converter.py`) - Structure-aware conversion with table/heading detection
4. **AzureDocumentConverter** (`azure_converter.py`) - Azure Document Intelligence integration
5. **LLMConverter** (`llm_converter.py`) - OpenAI GPT models with provenance tracking
6. **AnthropicConverter** (`anthropic_converter.py`) - Anthropic Claude integration
7. **GeminiConverter** (`gemini_converter.py`) - Google Gemini integration

### Extension Pattern

New converters can be registered with the factory:
```python
from image2md.factory import Image2MarkdownFactory
from your_module import CustomConverter

# Register custom converter
Image2MarkdownFactory.register_converter("custom", CustomConverter)

# Use through factory
result = Image2MarkdownFactory.convert(
    image_path, 
    converter_type="custom", 
    output_path=output_path,
    **custom_options
)
```

### Environment Configuration

- Automatic .env file loading in CLI (disable with `--no-env-file`)
- Supports multiple authentication methods per converter
- Common environment variables:
  - `OPENAI_API_KEY` - For Vision and LLM converters
  - `AZURE_ENDPOINT`, `AZURE_API_KEY` - For Azure converter
  - `ANTHROPIC_API_KEY` - For Anthropic converter  
  - `GOOGLE_API_KEY` - For Gemini converter

### Testing Strategy

- Unit tests in `tests/` directory using pytest
- Integration examples in `examples/` directory
- Test coverage includes converter functionality, factory pattern, and CLI interface
- Examples demonstrate real API usage and model comparisons

### Key Files

- `image2md/__init__.py` - Package exports with conditional imports
- `image2md/factory.py` - Central converter registration and instantiation
- `image2md/cli.py` - CLI with environment handling and argument parsing
- `pyproject.toml` - Package configuration with optional dependencies
- `examples/` - Working integration examples and test scripts

### Optional Dependencies

The project uses optional dependencies to avoid requiring all AI SDKs:
- `[azure]` - Azure Document Intelligence SDK
- `[llm]` - OpenAI, Anthropic, and Google GenerativeAI SDKs  
- `[all]` - All optional dependencies

Converters are conditionally imported and registered only when their dependencies are available.