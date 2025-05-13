#!/usr/bin/env python3
"""Script to compare Claude model outputs for image-to-markdown conversion"""
import os
import sys
from pathlib import Path
import json
import difflib
import time

# Create output directory for results
output_dir = Path("claude_comparison")
output_dir.mkdir(exist_ok=True)

# Paths to the conversion results
opus_md_path = Path("claude_conversion_output/claude_result.md")
sonnet_md_path = Path("claude_sonnet_output/claude_sonnet_result.md")
opus_json_path = Path("claude_conversion_output/claude_result.json")
sonnet_json_path = Path("claude_sonnet_output/claude_sonnet_result.json")

# Output files
diff_path = output_dir / "claude_model_diff.html"
comparison_path = output_dir / "model_comparison.md"

print("Comparing Claude models for image-to-markdown conversion...")

# Function to clean markdown text 
def clean_markdown(text):
    """Clean markdown text by removing the ```markdown and ``` delimiters if present"""
    text = text.strip()
    if text.startswith("```markdown\n"):
        text = text[len("```markdown\n"):]
    if text.endswith("\n```"):
        text = text[:-4]
    return text

# Function to load data
def load_conversion_data(json_path):
    """Load conversion data from JSON file"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {json_path}: {e}")
        return None

# Load the JSON data
opus_data = load_conversion_data(opus_json_path)
sonnet_data = load_conversion_data(sonnet_json_path)

if not opus_data or not sonnet_data:
    print("Error: Could not load conversion results.")
    sys.exit(1)

# Load and clean the markdown content
try:
    with open(opus_md_path, 'r', encoding='utf-8') as f:
        opus_md = f.read()
    
    with open(sonnet_md_path, 'r', encoding='utf-8') as f:
        sonnet_md = f.read()
    
    # Clean markdown
    opus_md_clean = clean_markdown(opus_md)
    sonnet_md_clean = clean_markdown(sonnet_md)
    
except FileNotFoundError as e:
    print(f"Error reading markdown files: {e}")
    sys.exit(1)

# Create HTML diff
diff = difflib.HtmlDiff()
diff_html = diff.make_file(
    opus_md_clean.splitlines(),
    sonnet_md_clean.splitlines(),
    fromdesc=f"Claude 3 Opus ({opus_data['provenance']['model']})",
    todesc=f"Claude 3.7 Sonnet ({sonnet_data['provenance']['model']})"
)

# Write HTML diff to file
with open(diff_path, 'w', encoding='utf-8') as f:
    f.write(diff_html)

# Collect metrics
opus_chars = len(opus_md_clean)
sonnet_chars = len(sonnet_md_clean)
opus_lines = len(opus_md_clean.splitlines())
sonnet_lines = len(sonnet_md_clean.splitlines())

# Collect timing info
opus_time = opus_data.get("provenance", {}).get("timestamp", "Unknown")
sonnet_time = sonnet_data.get("provenance", {}).get("timestamp", "Unknown")

# Create comparison markdown
comparison_md = f"""# Claude Model Comparison for Image-to-Markdown Conversion

This document compares the output of two Claude models converting the same image to markdown.

## Models Used

| Model | Version | Temperature | Max Tokens |
|-------|---------|-------------|------------|
| {opus_data['provenance']['model']} | {opus_data['provenance'].get('model_version', 'N/A')} | {opus_data['provenance']['conversion_params']['temperature']} | {opus_data['provenance']['conversion_params']['max_tokens']} |
| {sonnet_data['provenance']['model']} | {sonnet_data['provenance'].get('model_version', 'N/A')} | {sonnet_data['provenance']['conversion_params']['temperature']} | {sonnet_data['provenance']['conversion_params']['max_tokens']} |

## Output Metrics

| Metric | Claude 3 Opus | Claude 3.7 Sonnet | Difference |
|--------|--------------|-------------------|------------|
| Characters | {opus_chars} | {sonnet_chars} | {sonnet_chars - opus_chars} ({((sonnet_chars - opus_chars) / opus_chars) * 100:.2f}%) |
| Lines | {opus_lines} | {sonnet_lines} | {sonnet_lines - opus_lines} |
| File Size (bytes) | {os.path.getsize(opus_md_path)} | {os.path.getsize(sonnet_md_path)} | {os.path.getsize(sonnet_md_path) - os.path.getsize(opus_md_path)} ({((os.path.getsize(sonnet_md_path) - os.path.getsize(opus_md_path)) / os.path.getsize(opus_md_path)) * 100:.2f}%) |

## Formatting Differences

A detailed view of the differences can be seen in the [HTML diff file](claude_model_diff.html).

### Key Differences:

1. **Markdown Fencing**: 
   - Claude 3.7 Sonnet wrapped the output in markdown code fences (```markdown)
   - Claude 3 Opus provided raw markdown

2. **Formatting Style**:
   - Claude 3.7 Sonnet used more hierarchical headings (# and ##)
   - Claude 3.7 Sonnet used more text emphasis (**bold** and *italic*)

3. **Structure**:
   - Claude 3 Opus used a simple table format for the date and recipient
   - Claude 3.7 Sonnet used bold text with labels for the same information

## Prompts Used

### Claude 3 Opus Prompt:
```
{opus_data['provenance']['conversion_params']['prompt']}
```

### Claude 3.7 Sonnet Prompt:
```
{sonnet_data['provenance']['conversion_params']['prompt']}
```

## Conclusion

Both models successfully converted the image to well-formatted markdown, preserving the key information and structure of the document. The Claude 3.7 Sonnet model produced output with more explicit markdown formatting (headings, bold, italics) while the Claude 3 Opus model produced slightly more compact output.

The HTML diff file provides a side-by-side comparison of the outputs, highlighting specific differences in formatting and content.
"""

# Write comparison markdown to file
with open(comparison_path, 'w', encoding='utf-8') as f:
    f.write(comparison_md)

print(f"✅ Comparison completed!")
print(f"✅ HTML diff saved to: {diff_path}")
print(f"✅ Comparison report saved to: {comparison_path}")

# Print a summary
print("\nSummary of differences:")
print(f"  - Claude 3 Opus: {opus_chars} characters, {opus_lines} lines")
print(f"  - Claude 3.7 Sonnet: {sonnet_chars} characters, {sonnet_lines} lines")
print(f"  - Size difference: {((sonnet_chars - opus_chars) / opus_chars) * 100:.2f}%") 