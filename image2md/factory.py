"""Factory for image-to-markdown converters."""
from typing import Dict, Type, Optional
from pathlib import Path

from .base import Image2MarkdownConverter
from .ocr_converter import OCRConverter
from .vision_converter import VisionConverter
from .structure_converter import StructureConverter

# Import Azure converter conditionally to handle case when Azure SDK is not installed
try:
    from .azure_converter import AzureDocumentConverter
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# Import LLM converter conditionally to handle case when OpenAI SDK is not installed
try:
    from .llm_converter import LLMConverter
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Import Claude converter conditionally to handle case when Anthropic SDK is not installed
try:
    from .anthropic_converter import AnthropicConverter, ANTHROPIC_AVAILABLE
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import Gemini converter conditionally to handle case when Google GenerativeAI SDK is not installed
try:
    from .gemini_converter import GeminiConverter, GEMINI_AVAILABLE
except ImportError:
    GEMINI_AVAILABLE = False


class Image2MarkdownFactory:
    """Factory for creating and managing image-to-markdown converters."""
    
    _converters: Dict[str, Type[Image2MarkdownConverter]] = {
        "ocr": OCRConverter,
        "vision": VisionConverter,
        "structure": StructureConverter,
    }
    
    # Add Azure converter if available
    if AZURE_AVAILABLE:
        _converters["azure"] = AzureDocumentConverter
    
    # Add LLM converter if available
    if LLM_AVAILABLE:
        _converters["llm"] = LLMConverter
    
    # Add Claude converter if available
    if ANTHROPIC_AVAILABLE:
        _converters["anthropic"] = AnthropicConverter
    
    # Add Gemini converter if available
    if GEMINI_AVAILABLE:
        _converters["gemini"] = GeminiConverter
    
    @classmethod
    def get_converter(cls, converter_type: str, **kwargs) -> Image2MarkdownConverter:
        """
        Get an instance of the specified converter type.
        
        Args:
            converter_type: Type of converter ('ocr', 'vision', 'structure', 'azure', 'llm', 'anthropic', or 'gemini')
            **kwargs: Additional parameters to pass to the converter constructor
            
        Returns:
            An instance of the specified converter
            
        Raises:
            ValueError: If converter_type is not recognized
            ImportError: If trying to use a converter but its SDK is not installed
        """
        converter_type = converter_type.lower()
        
        # Special handling for Azure converter
        if converter_type == "azure" and not AZURE_AVAILABLE:
            raise ImportError(
                "Azure Document Intelligence SDK is not installed. "
                "Please install it with: pip install azure-ai-documentintelligence>=1.0.0"
            )
        
        # Special handling for LLM converter
        if converter_type == "llm" and not LLM_AVAILABLE:
            raise ImportError(
                "OpenAI SDK is not installed. "
                "Please install it with: pip install openai>=1.0.0"
            )
        
        # Special handling for Claude converter
        if converter_type == "anthropic" and not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic SDK is not installed. "
                "Please install it with: pip install anthropic>=0.51.0"
            )
        
        # Special handling for Gemini converter
        if converter_type == "gemini" and not GEMINI_AVAILABLE:
            raise ImportError(
                "Google Generative AI SDK is not installed. "
                "Please install it with: pip install google-generativeai>=0.3.0"
            )
        
        # Special handling for newer OpenAI models - pass max_tokens as max_completion_tokens
        if converter_type == "llm" and "model" in kwargs:
            model = kwargs.get("model")
            if isinstance(model, str) and model.startswith("o4-"):
                # If max_tokens is provided but max_completion_tokens is not, 
                # use max_tokens value for max_completion_tokens
                if "max_tokens" in kwargs and "max_completion_tokens" not in kwargs:
                    kwargs["max_completion_tokens"] = kwargs.get("max_tokens")
        
        converter_class = cls._converters.get(converter_type)
        if not converter_class:
            available_types = ", ".join(cls._converters.keys())
            raise ValueError(f"Unknown converter type: {converter_type}. Available types: {available_types}")
        
        return converter_class(**kwargs)
    
    @classmethod
    def register_converter(cls, name: str, converter_class: Type[Image2MarkdownConverter]) -> None:
        """
        Register a new converter type.
        
        Args:
            name: Name to associate with the converter
            converter_class: The converter class to register
            
        Raises:
            TypeError: If converter_class is not a subclass of Image2MarkdownConverter
        """
        if not issubclass(converter_class, Image2MarkdownConverter):
            raise TypeError(f"Converter class must be a subclass of Image2MarkdownConverter")
        
        cls._converters[name.lower()] = converter_class
    
    @classmethod
    def available_converters(cls) -> Dict[str, Type[Image2MarkdownConverter]]:
        """
        Get a dictionary of available converters.
        
        Returns:
            Dict[str, Type[Image2MarkdownConverter]]: Dictionary of converter name to converter class
        """
        return cls._converters.copy()
    
    @classmethod
    def convert(cls, image_path: Path, converter_type: str = "vision", 
                output_path: Optional[Path] = None, **kwargs) -> Path:
        """
        Convenience method to convert an image to markdown and save it in one step.
        
        Args:
            image_path: Path to the image file
            converter_type: Type of converter to use
            output_path: Path where to save the resulting markdown
            **kwargs: Additional parameters to pass to the converter
            
        Returns:
            Path: Path to the saved markdown file
        """
        converter = cls.get_converter(converter_type, **kwargs)
        return converter.save_markdown(image_path, output_path, **kwargs) 