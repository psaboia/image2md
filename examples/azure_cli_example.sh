#!/bin/bash
# Example of using Azure Document Intelligence with image2md command-line interface

# Set up output directory
OUTPUT_DIR="azure_cli_example_output"
mkdir -p "$OUTPUT_DIR"

# Image path
IMAGE_PATH="83635935.png"

if [ ! -f "$IMAGE_PATH" ]; then
  echo "Error: Image not found at $IMAGE_PATH"
  exit 1
fi

# Check if .env file exists and source it
if [ -f .env ]; then
  echo "Loading environment variables from .env file"
  export $(grep -v '^#' .env | xargs)
fi

# Check if Azure credentials are set
if [ -z "$AZURE_ENDPOINT" ] || [ -z "$AZURE_API_KEY" ]; then
  echo "Error: Azure credentials not found in environment variables"
  echo "Please set AZURE_ENDPOINT and AZURE_API_KEY environment variables"
  exit 1
fi

echo "Example: Converting $IMAGE_PATH to markdown using Azure Document Intelligence CLI"
echo "--------------------------------------------------------------------------------"

# Example 1: Basic usage with Azure (using environment variables)
echo ""
echo "Example 1: Basic usage with Azure (using environment variables)"
echo "--------------------------------------------------------------"
python -m image2md.cli \
  --type azure \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/basic_cli.md"

echo "✅ Conversion completed"

# Example 2: Save JSON alongside markdown
echo ""
echo "Example 2: Save JSON alongside markdown"
echo "--------------------------------------"
python -m image2md.cli \
  --type azure \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/with_json.md" \
  --save-json \
  --json-output "$OUTPUT_DIR/with_json.json"

echo "✅ Conversion with JSON output completed"

# Example 3: Using explicit credentials from environment variables
echo ""
echo "Example 3: Using explicit credentials from environment variables"
echo "--------------------------------------------------------------"
python -m image2md.cli \
  --type azure \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/with_explicit_creds.md" \
  --azure-endpoint "$AZURE_ENDPOINT" \
  --azure-api-key "$AZURE_API_KEY" \
  --save-json

echo "✅ Conversion with explicit credentials completed"

# Example 4: Using specific API version and model ID
echo ""
echo "Example 4: Using specific API version and model ID"
echo "------------------------------------------------"
python -m image2md.cli \
  --type azure \
  "$IMAGE_PATH" \
  --output "$OUTPUT_DIR/with_specific_version.md" \
  --azure-api-version "2024-11-30" \
  --azure-model-id "prebuilt-layout" \
  --save-json

echo "✅ Conversion with specific API version and model ID completed"

echo ""
echo "✨ All examples completed successfully!"
echo "📁 Results saved in: $OUTPUT_DIR"

# Show preview of the first conversion result
echo ""
echo "Preview of markdown content:"
echo "==================================================="
head -n 15 "$OUTPUT_DIR/basic_cli.md"
echo "===================================================" 