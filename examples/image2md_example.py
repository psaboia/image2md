#!/usr/bin/env python3
"""Example usage of the image2md module."""
import os
from pathlib import Path
import argparse
import sys

# Add the parent directory to sys.path to allow importing image2md
sys.path.insert(0, str(Path(__file__).parent.parent))

import image2md  # noqa: E402


def main():
    """Run an example conversion using image2md."""
    parser = argparse.ArgumentParser(description="Example for image2md module")
    parser.add_argument("image", help="Path to an image file to convert")
    parser.add_argument(
        "--type", choices=["ocr", "vision", "structure"], default="vision",
        help="Converter type to use"
    )
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image {image_path} not found")
        return 1

    # Create a folder for outputs if it doesn't exist
    output_dir = Path("example_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    # Compare different converter types
    converters = {
        "ocr": image2md.OCRConverter(),
        "vision": image2md.VisionConverter(),
        "structure": image2md.StructureConverter()
    }
    
    if args.type != "all":
        # Use only the selected converter
        converters = {args.type: converters[args.type]}
    
    for name, converter in converters.items():
        output_path = output_dir / f"{image_path.stem}_{name}.md"
        
        print(f"Converting with {name} converter...")
        result_path = converter.save_markdown(image_path, output_path)
        print(f"  Output saved to: {result_path}")
    
    print("\nConversion complete!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 