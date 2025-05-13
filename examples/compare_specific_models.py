#!/usr/bin/env python3
"""
Compare markdown conversion results between two specific models.
This script generates a comparison between gpt-4o and o4-mini.
"""
import os
import sys
import difflib
from pathlib import Path
import argparse

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def generate_html_diff(path1, path2, output_path):
    """Generate HTML diff between two files."""
    with open(path1, 'r') as f1:
        text1 = f1.readlines()
    with open(path2, 'r') as f2:
        text2 = f2.readlines()
    
    # Generate the comparison
    diff = difflib.HtmlDiff().make_file(
        text1, text2, 
        fromdesc=f"Model 1: {path1.name}", 
        todesc=f"Model 2: {path2.name}"
    )
    
    # Save the comparison to a file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(diff)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description='Compare specific model outputs')
    parser.add_argument('--image-name', default='83635935.png', 
                        help='Name of the image to compare (default: 83635935.png)')
    parser.add_argument('--output-dir', default='./model_comparison', 
                        help='Output directory for comparison (default: ./model_comparison)')
    args = parser.parse_args()
    
    # Define paths to model outputs
    output_dir = Path(args.output_dir)
    
    model1_path = output_dir / "openai__gpt-4o" / f"{Path(args.image_name).stem}.md"
    model2_path = output_dir / "openai__o4-mini-2025-04-16" / f"{Path(args.image_name).stem}.md"
    
    if not model1_path.exists() or not model2_path.exists():
        print(f"Error: Could not find both model outputs at {model1_path} and {model2_path}")
        return
    
    # Create comparison directory
    comparison_dir = output_dir / "comparison"
    comparison_dir.mkdir(exist_ok=True)
    
    # Generate comparison
    output_path = comparison_dir / "comparison_gpt4o_vs_o4mini.html"
    generate_html_diff(model1_path, model2_path, output_path)
    print(f"Comparison created: {output_path}")

if __name__ == "__main__":
    main() 