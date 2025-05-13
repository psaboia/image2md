#!/usr/bin/env python3
"""Minimal example for image2md with Azure Document Intelligence using .env file."""
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow importing image2md
sys.path.insert(0, str(Path(__file__).parent.parent))

# Required imports
try:
    from dotenv import load_dotenv
    from image2md import AzureDocumentConverter
except ImportError as e:
    print(f"Error: {e}")
    print("Please install required packages:")
    print("pip install python-dotenv azure-ai-documentintelligence>=1.0.0")
    sys.exit(1)

# Load .env file which should contain:
# AZURE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com
# AZURE_API_KEY=your-api-key
load_dotenv()

# Simple usage - .env file must contain AZURE_ENDPOINT and AZURE_API_KEY
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python azure_minimal_example.py <image_path>")
        sys.exit(1)
    
    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"Error: Image {image_path} not found")
        sys.exit(1)
    
    try:
        # Create Azure converter (uses credentials from .env)
        converter = AzureDocumentConverter()
        
        # Convert image to markdown
        print(f"Converting {image_path}...")
        output_path = converter.save_markdown(image_path)
        
        print(f"Conversion successful! Output saved to: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 