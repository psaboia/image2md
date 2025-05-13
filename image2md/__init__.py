"""Image-to-markdown conversion package."""

__version__ = "0.1.0"

from pathlib import Path
from typing import Optional

# Import base classes
from .base import Image2MarkdownConverter
from .factory import Image2MarkdownFactory

# Import converter implementations
from .ocr_converter import OCRConverter
from .vision_converter import VisionConverter
from .structure_converter import StructureConverter

# Import Azure converter conditionally
try:
    from .azure_converter import AzureDocumentConverter
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# Import LLM converter conditionally
try:
    from .llm_converter import LLMConverter, ProvenenanceInfo
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Import Anthropic converter conditionally
try:
    from .anthropic_converter import AnthropicConverter, AnthropicProvenance, ANTHROPIC_AVAILABLE
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import Gemini converter conditionally
try:
    from .gemini_converter import GeminiConverter, GeminiProvenance, GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False

# Simplified helper function
def convert_image(
    image_path: Path,
    output_path: Optional[Path] = None,
    converter_type: str = "vision",
    **kwargs
) -> Path:
    """
    Convert an image to markdown and save it.
    
    Args:
        image_path: Path to the image file
        output_path: Path where to save the resulting markdown
        converter_type: Type of converter to use
        **kwargs: Additional parameters for the converter
        
    Returns:
        Path: Path to the saved markdown file
    """
    return Image2MarkdownFactory.convert(
        image_path=image_path,
        output_path=output_path,
        converter_type=converter_type,
        **kwargs
    )

# Function alias for backward compatibility, matches the test's expected call format
def convert(image_path: Path, converter_type: str = "vision", output_path: Optional[Path] = None, **kwargs) -> Path:
    """
    Convert an image to markdown and save it.
    
    Args:
        image_path: Path to the image file
        converter_type: Type of converter to use
        output_path: Path where to save the resulting markdown
        **kwargs: Additional parameters for the converter
        
    Returns:
        Path: Path to the saved markdown file
    """
    return Image2MarkdownFactory.convert(
        image_path, 
        converter_type, 
        output_path, 
        **kwargs
    )

__all__ = [
    'Image2MarkdownConverter',
    'Image2MarkdownFactory',
    'OCRConverter',
    'VisionConverter',
    'StructureConverter',
    'AzureDocumentConverter',
    'LLMConverter', 
    'ProvenenanceInfo',
    'AnthropicConverter',
    'AnthropicProvenance',
    'GeminiConverter',
    'GeminiProvenance',
    'convert_image',
    'convert',
] 