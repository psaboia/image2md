#!/usr/bin/env python3
"""Example usage of the image2md module with Azure Document Intelligence."""
import os
import sys
from pathlib import Path
import argparse

# We'll handle dotenv import errors in the code itself
# The linter error can be ignored since this is just an example script

# Add the parent directory to sys.path to allow importing image2md
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try to import the Azure converter
try:
    from image2md import AzureDocumentConverter
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


def main():
    """Run an example conversion using the Azure Document Intelligence converter."""
    if not AZURE_AVAILABLE:
        print("Error: Azure Document Intelligence SDK is not installed.")
        print("Please install it with: pip install azure-ai-documentintelligence>=1.0.0")
        return 1
    
    # Try to load environment variables from .env file
    try:
        from dotenv import load_dotenv
        
        # Check if .env file exists
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv()
            print("Loaded environment variables from .env file")
        else:
            print("Warning: .env file not found in the current directory.")
            print("Expected .env file format:")
            print("AZURE_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com")
            print("AZURE_API_KEY=your-api-key")
    except ImportError:
        print("Note: python-dotenv is not installed. Environment variables won't be loaded from .env file.")
        print("Install it with: pip install python-dotenv")
    
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Example for using image2md with Azure Document Intelligence"
    )
    parser.add_argument(
        "image", 
        help="Path to an image file to convert"
    )
    parser.add_argument(
        "--endpoint", 
        help="Azure Document Intelligence endpoint URL (overrides AZURE_ENDPOINT from .env)"
    )
    parser.add_argument(
        "--api-key", 
        help="Azure Document Intelligence API key (overrides AZURE_API_KEY from .env)"
    )
    parser.add_argument(
        "--save-json", 
        action="store_true",
        help="Save the full JSON response from Azure"
    )
    args = parser.parse_args()

    # Get the image path
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image {image_path} not found")
        return 1

    # Create output directory
    output_dir = Path("azure_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    # Output paths
    output_md = output_dir / f"{image_path.stem}_azure.md"
    output_json = output_dir / f"{image_path.stem}_azure.json" if args.save_json else None
    
    # Read credentials from arguments or environment variables
    endpoint = args.endpoint or os.environ.get("AZURE_ENDPOINT")
    api_key = args.api_key or os.environ.get("AZURE_API_KEY")
    
    if not endpoint or not api_key:
        print("Error: Azure Document Intelligence endpoint and API key must be provided")
        print("Either:")
        print("  1. Pass them as arguments (--endpoint, --api-key)")
        print("  2. Set the AZURE_ENDPOINT and AZURE_API_KEY environment variables")
        print("  3. Create a .env file with AZURE_ENDPOINT and AZURE_API_KEY")
        return 1
    
    try:
        # Create and use the Azure converter
        converter = AzureDocumentConverter(
            endpoint=endpoint,
            api_key=api_key
        )
        
        print("Converting with Azure Document Intelligence...")
        result_path = converter.save_markdown(
            image_path, 
            output_md,
            save_json=args.save_json,
            json_output_path=output_json
        )
        
        print(f"Conversion successful! Markdown saved to: {result_path}")
        if args.save_json and output_json:
            print(f"Full JSON response saved to: {output_json}")
        
        return 0
    
    except Exception as e:
        print(f"Error during conversion: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 