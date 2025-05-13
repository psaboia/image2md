#!/usr/bin/env python3
"""
Compare markdown conversion results between OpenAI, Anthropic Claude, and Google Gemini models.
This script converts the same image using different providers and creates a comparison.
"""
import os
import sys
from pathlib import Path
import difflib
import json
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to sys.path to import image2md
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Import image2md components
from image2md.factory import Image2MarkdownFactory

def get_api_keys():
    """Get API keys from environment variables."""
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    google_key = os.environ.get("GOOGLE_API_KEY")
    
    missing_keys = []
    if not openai_key:
        missing_keys.append("OPENAI_API_KEY")
    if not anthropic_key:
        missing_keys.append("ANTHROPIC_API_KEY")
    if not google_key:
        missing_keys.append("GOOGLE_API_KEY")
    
    if missing_keys:
        print(f"Warning: The following API keys are missing: {', '.join(missing_keys)}")
        print("Some conversions may fail. Set these environment variables or use a .env file.")
    
    return openai_key, anthropic_key, google_key

def convert_with_provider(image_path, output_dir, provider, model, api_key):
    """Convert an image with a specific provider and model."""
    if not api_key:
        print(f"Skipping {provider} ({model}) conversion due to missing API key.")
        return None
    
    print(f"Converting with {provider} ({model})...")
    provider_dir = output_dir / f"{provider}__{model.replace(':', '-')}"
    provider_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = provider_dir / f"{image_path.stem}.md"
    json_output_path = provider_dir / f"{image_path.stem}.json"
    
    # Determine converter type based on provider
    if provider == "openai":
        converter_type = "llm"
        provider_param = "openai" 
    elif provider == "anthropic":
        converter_type = "anthropic"
        provider_param = None
    elif provider == "google":
        converter_type = "gemini"
        provider_param = None
    else:
        raise ValueError(f"Unsupported provider: {provider}")
    
    try:
        # Set up parameters based on provider
        params = {
            "converter_type": converter_type,
            "output_path": output_path,
            "api_key": api_key,
            "model": model,
            "save_json": True,
            "json_output_path": json_output_path,
            "custom_prompt": "Convert this image to well-formatted markdown, preserving the original structure and formatting.",
        }
        
        # Add provider parameter only for openai
        if provider_param:
            params["provider"] = provider_param
            
        # Convert with the appropriate provider
        result_path = Image2MarkdownFactory.convert(image_path, **params)
        print(f"  Output saved to: {result_path}")
        return output_path
    except Exception as e:
        print(f"  Error converting with {provider} ({model}): {e}")
        return None

def create_comparison(outputs, output_dir):
    """Create an HTML comparison of the markdown outputs."""
    valid_outputs = {k: v for k, v in outputs.items() if v is not None}
    if len(valid_outputs) < 2:
        print("Not enough successful conversions to create a comparison.")
        return
    
    # Create a comparison directory
    comparison_dir = output_dir / "comparison"
    comparison_dir.mkdir(parents=True, exist_ok=True)
    
    # Create pairwise comparisons
    providers = list(valid_outputs.keys())
    for i in range(len(providers)):
        for j in range(i+1, len(providers)):
            provider1, path1 = providers[i], valid_outputs[providers[i]]
            provider2, path2 = providers[j], valid_outputs[providers[j]]
            
            try:
                with open(path1, "r", encoding="utf-8") as f1:
                    content1 = f1.read()
                
                with open(path2, "r", encoding="utf-8") as f2:
                    content2 = f2.read()
                
                # Generate HTML diff
                diff = difflib.HtmlDiff()
                diff_html = diff.make_file(
                    content1.splitlines(),
                    content2.splitlines(),
                    fromdesc=provider1,
                    todesc=provider2
                )
                
                # Write comparison to file
                comparison_file = comparison_dir / f"comparison_{provider1}_vs_{provider2}.html"
                with open(comparison_file, "w", encoding="utf-8") as f:
                    f.write(diff_html)
                
                print(f"Comparison created: {comparison_file}")
            except Exception as e:
                print(f"Error creating comparison between {provider1} and {provider2}: {e}")

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare markdown conversion between different providers.")
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to the image file to convert"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="model_comparison",
        help="Directory to save outputs and comparison"
    )
    parser.add_argument(
        "--openai-model",
        type=str,
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--anthropic-model",
        type=str,
        default="claude-3-7-sonnet-20250219",
        help="Anthropic model to use (default: claude-3-7-sonnet-20250219)"
    )
    parser.add_argument(
        "--gemini-model",
        type=str,
        default="gemini-2.5-flash-preview-04-17",
        help="Google Gemini model to use (default: gemini-2.5-flash-preview-04-17)"
    )
    
    args = parser.parse_args()
    
    # Convert paths to Path objects
    image_path = Path(args.image_path)
    output_dir = Path(args.output_dir)
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get API keys
    openai_key, anthropic_key, google_key = get_api_keys()
    
    # Define conversion configurations
    outputs = {}
    
    # Convert with OpenAI
    if openai_key:
        outputs["openai"] = convert_with_provider(
            image_path, output_dir, "openai", args.openai_model, openai_key
        )
    
    # Convert with Anthropic
    if anthropic_key:
        outputs["anthropic"] = convert_with_provider(
            image_path, output_dir, "anthropic", args.anthropic_model, anthropic_key
        )
    
    # Convert with Google Gemini
    if google_key:
        outputs["google"] = convert_with_provider(
            image_path, output_dir, "google", args.gemini_model, google_key
        )
    
    # Create comparison
    create_comparison(outputs, output_dir)
    
    print("\nConversion complete!")
    print(f"Check the '{output_dir}' directory for results and comparisons.")

if __name__ == "__main__":
    main() 