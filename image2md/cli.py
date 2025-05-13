"""Command-line interface for image2md."""
import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Dict

from .factory import Image2MarkdownFactory, AZURE_AVAILABLE, LLM_AVAILABLE


def load_env_file(env_file: str) -> Dict[str, str]:
    """
    Load environment variables from a .env file without dependencies.
    
    Args:
        env_file: Path to the environment file
        
    Returns:
        Dict[str, str]: Dictionary of loaded environment variables
    """
    loaded_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Simple regex to match key=value pairs
                match = re.match(r'^([A-Za-z0-9_]+)=(.*)$', line)
                if match:
                    key, value = match.groups()
                    # Remove quotes if present
                    value = value.strip('\'"')
                    loaded_vars[key] = value
                    # Set environment variable
                    os.environ[key] = value
    except Exception as e:
        print(f"Warning: Error reading {env_file}: {e}", file=sys.stderr)
    
    return loaded_vars


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Convert images to markdown content",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Env file options
    env_group = parser.add_argument_group("Environment options")
    env_group.add_argument(
        "--no-env-file",
        action="store_true",
        help="Disable automatic loading of .env file"
    )
    env_group.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Path to the environment file (default: .env)"
    )
    
    parser.add_argument(
        "image",
        type=str,
        help="Path to the input image file"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output markdown file path (default: same as input with .md extension)"
    )
    
    # Get available converter types
    available_converters = list(Image2MarkdownFactory.available_converters().keys())
    
    parser.add_argument(
        "-t", "--type",
        choices=available_converters,
        default="vision",
        help="Type of converter to use"
    )
    
    # OCR converter options
    ocr_group = parser.add_argument_group("OCR converter options")
    ocr_group.add_argument(
        "--ocr-language",
        type=str,
        default="eng",
        help="OCR language code (for OCR converter)"
    )
    
    # Vision converter options
    vision_group = parser.add_argument_group("Vision converter options")
    vision_group.add_argument(
        "--vision-model",
        type=str,
        default="gpt-4-vision",
        help="Vision model name (for Vision converter)"
    )
    vision_group.add_argument(
        "--vision-prompt",
        type=str,
        help="Custom prompt for the Vision model"
    )
    vision_group.add_argument(
        "--max-tokens",
        type=int,
        default=1000,
        help="Maximum tokens for the Vision model response"
    )
    
    # Structure converter options
    structure_group = parser.add_argument_group("Structure converter options")
    structure_group.add_argument(
        "--no-tables", 
        action="store_true",
        help="Disable table detection in structure analysis"
    )
    structure_group.add_argument(
        "--no-headings",
        action="store_true",
        help="Disable heading detection in structure analysis"
    )
    structure_group.add_argument(
        "--no-lists",
        action="store_true",
        help="Disable list detection in structure analysis"
    )
    
    # Azure Document Intelligence converter options (if available)
    if AZURE_AVAILABLE:
        azure_group = parser.add_argument_group("Azure Document Intelligence converter options")
        azure_group.add_argument(
            "--azure-endpoint",
            type=str,
            help="Azure Document Intelligence endpoint URL (if not provided, uses AZURE_ENDPOINT env var)"
        )
        azure_group.add_argument(
            "--azure-api-key",
            type=str,
            help="Azure Document Intelligence API key (if not provided, uses AZURE_API_KEY env var)"
        )
        azure_group.add_argument(
            "--azure-api-version",
            type=str,
            default="2024-11-30",
            help="Azure Document Intelligence API version (must be >= 2024-11-30 for markdown support)"
        )
        azure_group.add_argument(
            "--azure-model-id",
            type=str,
            default="prebuilt-layout",
            help="Azure Document Intelligence model ID (must be 'prebuilt-layout' for markdown support)"
        )
        azure_group.add_argument(
            "--azure-save-json",
            action="store_true",
            help="Save the full JSON response from Azure Document Intelligence"
        )
        azure_group.add_argument(
            "--azure-json-output",
            type=str,
            help="Path to save the Azure JSON response (default: same as input with .json extension)"
        )
    
    # LLM converter options (if available)
    if LLM_AVAILABLE:
        llm_group = parser.add_argument_group("LLM converter options")
        llm_group.add_argument(
            "--llm-api-key",
            type=str,
            help="API key for LLM provider (if not provided, uses OPENAI_API_KEY env var)"
        )
        llm_group.add_argument(
            "--llm-model",
            type=str,
            default="gpt-4o",
            help="Model name for LLM provider (e.g., 'gpt-4o', 'gpt-4-turbo')"
        )
        llm_group.add_argument(
            "--llm-provider",
            type=str,
            default="openai",
            help="LLM provider (currently only 'openai' is supported)"
        )
        llm_group.add_argument(
            "--llm-prompt",
            type=str,
            help="Custom prompt for the LLM (default prompt asks for markdown conversion)"
        )
        llm_group.add_argument(
            "--llm-max-tokens",
            type=int,
            default=4000,
            help="Maximum tokens for the LLM response"
        )
        llm_group.add_argument(
            "--llm-temperature",
            type=float,
            default=0.2,
            help="Temperature for the LLM response generation"
        )
        llm_group.add_argument(
            "--save-json",
            action="store_true",
            help="Save the full response with provenance information as JSON"
        )
        llm_group.add_argument(
            "--json-output",
            type=str,
            help="Path to save the JSON response (default: same as input with .json extension)"
        )
    
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv[1:])
        
    Returns:
        int: Exit code (0 for success, non-zero for errors)
    """
    # Parse arguments first to get env-file options
    parsed_args = parse_args(args)
    
    # Handle .env loading by default unless --no-env-file is specified
    if not parsed_args.no_env_file:
        env_file = parsed_args.env_file
        env_path = Path(env_file)
        
        if env_path.exists():
            loaded_vars = load_env_file(str(env_path))
            if loaded_vars:
                #env_vars_str = ", ".join([f"{k}=***" for k in loaded_vars.keys()])
                #print(f"Loaded environment variables from {env_file}: {env_vars_str}")
                print(f"Loaded environment variables from {env_file}")
            else:
                print(f"Note: No environment variables were loaded from {env_file}")
        else:
            print(f"Note: Environment file {env_file} not found, using system environment variables", file=sys.stderr)
    
    # Validate image path
    image_path = Path(parsed_args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {image_path}", file=sys.stderr)
        return 1
    
    # Prepare output path
    output_path = None
    if parsed_args.output:
        output_path = Path(parsed_args.output)
    
    # Prepare converter options based on the converter type
    converter_options = {}
    
    if parsed_args.type == "ocr":
        converter_options["language"] = parsed_args.ocr_language
    
    elif parsed_args.type == "vision":
        converter_options["model_name"] = parsed_args.vision_model
        converter_options["max_tokens"] = parsed_args.max_tokens
        if parsed_args.vision_prompt:
            converter_options["prompt"] = parsed_args.vision_prompt
    
    elif parsed_args.type == "structure":
        converter_options["detect_tables"] = not parsed_args.no_tables
        converter_options["detect_headings"] = not parsed_args.no_headings
        converter_options["detect_lists"] = not parsed_args.no_lists
    
    elif parsed_args.type == "azure" and AZURE_AVAILABLE:
        # Azure specific options
        if parsed_args.azure_endpoint:
            converter_options["endpoint"] = parsed_args.azure_endpoint
        if parsed_args.azure_api_key:
            converter_options["api_key"] = parsed_args.azure_api_key
        converter_options["api_version"] = parsed_args.azure_api_version
        converter_options["model_id"] = parsed_args.azure_model_id
        
        # Options for the convert method
        converter_options["save_json"] = parsed_args.azure_save_json
        if parsed_args.azure_json_output:
            converter_options["json_output_path"] = Path(parsed_args.azure_json_output)
    
    elif parsed_args.type == "llm" and LLM_AVAILABLE:
        # LLM specific options for initializing the converter
        if parsed_args.llm_api_key:
            converter_options["api_key"] = parsed_args.llm_api_key
        converter_options["model"] = parsed_args.llm_model
        converter_options["provider"] = parsed_args.llm_provider
        converter_options["max_tokens"] = parsed_args.llm_max_tokens
        converter_options["temperature"] = parsed_args.llm_temperature
        
        # Options for the convert method
        if parsed_args.save_json:
            converter_options["save_json"] = True
        if parsed_args.json_output:
            converter_options["json_output_path"] = Path(parsed_args.json_output)
        if parsed_args.llm_prompt:
            converter_options["custom_prompt"] = parsed_args.llm_prompt
    
    try:
        # Convert image to markdown and save it
        output_file = Image2MarkdownFactory.convert(
            image_path, 
            converter_type=parsed_args.type,
            output_path=output_path,
            **converter_options
        )
        
        print(f"Conversion successful! Output saved to: {output_file}")
        return 0
    
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        
        # Provide helpful guidance when API keys are missing
        if "API key" in str(e) and "environment variable" in str(e):
            print("\nTo configure API keys, you have three options:", file=sys.stderr)
            print("1. Create a .env file in the current directory with the required API keys", file=sys.stderr)
            print("   Example for OpenAI: OPENAI_API_KEY=your_key_here", file=sys.stderr)
            print("   Example for Azure: AZURE_ENDPOINT=your_endpoint AZURE_API_KEY=your_key", file=sys.stderr)
            print("2. Set environment variables directly in your shell", file=sys.stderr)
            print("   Example: export OPENAI_API_KEY=your_key_here", file=sys.stderr)
            print("3. Provide API keys directly via command line arguments", file=sys.stderr)
            print("   Example: --llm-api-key=your_key_here", file=sys.stderr)
        
        return 1


if __name__ == "__main__":
    sys.exit(main()) 