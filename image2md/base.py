"""Base interface for image-to-markdown converters."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any


class Image2MarkdownConverter(ABC):
    """Base class for image-to-markdown converters."""
    
    @abstractmethod
    def convert(self, image_path: Path, **kwargs) -> str:
        """
        Convert an image to markdown text representation.
        
        Args:
            image_path: Path to the image file
            **kwargs: Additional conversion parameters
            
        Returns:
            str: Markdown representation of the image content
        """
        pass
    
    def save_markdown(self, image_path: Path, output_path: Optional[Path] = None, **kwargs) -> Path:
        """
        Convert an image and save the markdown to a file.
        
        Args:
            image_path: Path to the image file
            output_path: Path where to save the markdown file. If None, will use the same name as the image with .md extension.
            **kwargs: Additional conversion parameters
            
        Returns:
            Path: Path to the saved markdown file
        """
        markdown_content = self.convert(image_path, **kwargs)
        
        if output_path is None:
            output_path = image_path.with_suffix('.md')
            
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        return output_path 