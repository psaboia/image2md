# Claude Model Comparison for Image-to-Markdown Conversion

This document compares the output of two Claude models converting the same image to markdown.

## Models Used

| Model | Version | Temperature | Max Tokens |
|-------|---------|-------------|------------|
| claude-3-opus-20240229 | None | 0.3 | 4000 |
| claude-3-7-sonnet-20250219 | 3.7 Sonnet | 0.2 | 4000 |

## Output Metrics

| Metric | Claude 3 Opus | Claude 3.7 Sonnet | Difference |
|--------|--------------|-------------------|------------|
| Characters | 1134 | 1097 | -37 (-3.26%) |
| Lines | 24 | 26 | 2 |
| File Size (bytes) | 1134 | 1113 | -21 (-1.85%) |

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
Convert this image to well-formatted markdown with proper headings, lists, and tables. Maintain the document structure as much as possible.
```

### Claude 3.7 Sonnet Prompt:
```

Convert this image to well-formatted markdown with proper headings, lists, and tables.
Maintain the document structure as much as possible.
Make sure to preserve:
1. Hierarchical structure with appropriate heading levels
2. Any tabular data with proper markdown table formatting
3. Text emphasis (bold, italics) when visually indicated
4. Lists and bullet points

```

## Conclusion

Both models successfully converted the image to well-formatted markdown, preserving the key information and structure of the document. The Claude 3.7 Sonnet model produced output with more explicit markdown formatting (headings, bold, italics) while the Claude 3 Opus model produced slightly more compact output.

The HTML diff file provides a side-by-side comparison of the outputs, highlighting specific differences in formatting and content.
