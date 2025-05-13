"""OCR-based image-to-markdown converter."""
from pathlib import Path
from .base import Image2MarkdownConverter


class OCRConverter(Image2MarkdownConverter):
    """Converts images to markdown using OCR (Optical Character Recognition)."""
    
    def __init__(self, language: str = "eng", **ocr_options):
        """
        Initialize OCR converter.
        
        Args:
            language: OCR language code (default: "eng")
            **ocr_options: Additional OCR engine options
        """
        self.language = language
        self.ocr_options = ocr_options
    
    def convert(self, image_path: Path, **kwargs) -> str:
        """
        Convert an image to markdown using OCR.
        
        Args:
            image_path: Path to the image file
            **kwargs: Additional conversion parameters
            
        Returns:
            str: Markdown representation of the image content
        """
        # Mock implementation (in a real implementation, this would use an OCR library)
        
        # For mock purposes, we'll return a simple markdown content
        return f"""# Content from {image_path.name}

This text was extracted using OCR ({self.language}) from the image.

- First detected text item
- Second detected text item
- Third detected text item

> Some quoted text detected in the image

""" 