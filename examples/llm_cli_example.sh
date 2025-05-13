#!/bin/bash
# Example of using LLM-based image-to-markdown conversion with CLI

# Set up output directory
OUTPUT_DIR="llm_cli_output"
mkdir -p "$OUTPUT_DIR"

# Image path
IMAGE_PATH="examples/83635935.png"

if [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: Image not found at $IMAGE_PATH"
  exit 1
fi

# Check if .env file exists and source it
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Error: OpenAI API key not found in environment variables"
  echo "Please set OPENAI_API_KEY environment variable"
  exit 1
fi

echo "Example: Converting $IMAGE_PATH to markdown using LLM-based converters"
echo "--------------------------------------------------------------------------------"

# Example 1: Basic usage with LLM converter (uses env var for API key)
echo ""
echo "Example 1: Basic usage with LLM converter"
echo "--------------------------------------------------------------"
python -m image2md.cli \
  --type llm \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/basic_llm.md"

echo "✅ Conversion completed"

# Example 2: Save JSON with provenance information
echo ""
echo "Example 2: Save JSON with provenance information"
echo "--------------------------------------------------------------"
python -m image2md.cli \
  --type llm \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/with_provenance.md" \
  --save-json \
  --json-output "$OUTPUT_DIR/with_provenance.json"

echo "✅ Conversion with provenance completed"

# Example 3: Using explicit API key and custom model
echo ""
echo "Example 3: Using explicit API key and custom model"
echo "--------------------------------------------------------------"
python -m image2md.cli \
  --type llm \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/custom_model.md" \
  --llm-api-key "$OPENAI_API_KEY" \
  --llm-model "gpt-4o" \
  --save-json

echo "✅ Conversion with custom model completed"

# Example 4: Using custom prompt and temperature
echo ""
echo "Example 4: Using custom prompt and temperature"
echo "--------------------------------------------------------------"
python -m image2md.cli \
  --type llm \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/custom_prompt.md" \
  --llm-prompt "Convert this image to markdown, ensuring all tables, lists, and headings are properly formatted. Preserve the structure of the document." \
  --llm-temperature 0.3 \
  --llm-max-tokens 4000 \
  --save-json

echo "✅ Conversion with custom prompt completed"

echo ""
echo "✨ All examples completed successfully!"
echo "📁 Results saved in: $OUTPUT_DIR"

# Show preview of the first conversion result
echo ""
echo "Preview of markdown content:"
echo "==================================================="
head -n 15 "$OUTPUT_DIR/basic_llm.md"
echo "==================================================="

# Show a preview of the JSON with provenance
echo ""
echo "Preview of JSON with provenance:"
echo "==================================================="
grep -A 10 "provenance" "$OUTPUT_DIR/with_provenance.json" | head -n 15
echo "===================================================" 