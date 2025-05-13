"""Anthropic implementation for image-to-markdown conversion."""
import os
import sys
import json
import base64
from datetime import datetime
import platform
import mimetypes
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import Image2MarkdownConverter
from .llm_converter import ProvenenanceInfo

@dataclass
class AnthropicProvenance(ProvenenanceInfo):
    """Provenance information specific to Anthropic models"""
    provider: str = "Anthropic"
    model_family: str = "Claude"
    request_id: Optional[str] = None
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with all fields"""
        return {
            "timestamp": self.timestamp,
            "model": self.model,
            "model_version": self.model_version,
            "provider": self.provider,
            "model_family": self.model_family,
            "request_id": self.request_id,
            "system_info": self.system_info,
            "conversion_params": self.conversion_params
        }


class AnthropicConverter(Image2MarkdownConverter):
    """Converts images to markdown using Anthropic's Claude models."""
    
    DEFAULT_PROMPT = (
        "Convert this image to well-formatted markdown. Maintain the structure "
        "and formatting as much as possible, including headings, lists, and tables. "
        "Important: Do NOT wrap your response in markdown code blocks (```). "
        "Just provide the clean markdown content directly without any surrounding backticks."
    )
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-7-sonnet-20250219",
        max_tokens: int = 4000,
        temperature: float = 0.2,
        **kwargs
    ):
        """
        Initialize Anthropic converter.
        
        Args:
            api_key: API key for Anthropic. If None, uses ANTHROPIC_API_KEY env var.
            model: Claude model to use.
            max_tokens: Maximum tokens in the response.
            temperature: Temperature for response generation.
            **kwargs: Additional parameters for the API.
        """
        # Initialize attributes
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key must be provided either as a parameter "
                "or as the ANTHROPIC_API_KEY environment variable"
            )
        
        # Initialize Anthropic client
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic SDK is not installed. "
                "Please install it with: pip install anthropic>=0.51.0"
            )
            
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Error initializing Anthropic client: {str(e)}")
            
        # Store additional options
        self.kwargs = kwargs
        
    def _encode_image(self, image_path: Path) -> str:
        """
        Encode an image to base64.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Base64-encoded image
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _get_media_type(self, image_path: Path) -> str:
        """
        Get the media type for the image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            str: Media type (e.g., 'image/jpeg', 'image/png')
        """
        # Initialize mimetypes if not already done
        if not mimetypes.inited:
            mimetypes.init()
            
        # Get the media type based on the file extension
        mime_type, _ = mimetypes.guess_type(str(image_path))
        
        # If mimetypes couldn't determine the type, use a fallback based on extension
        if not mime_type:
            extension = image_path.suffix.lower()
            if extension == '.png':
                mime_type = 'image/png'
            elif extension in ['.jpg', '.jpeg']:
                mime_type = 'image/jpeg'
            elif extension == '.gif':
                mime_type = 'image/gif'
            elif extension == '.webp':
                mime_type = 'image/webp'
            else:
                # Default to png as a fallback
                mime_type = 'image/png'
                
        return mime_type
    
    def _get_system_info(self) -> Dict[str, str]:
        """
        Get system information for provenance tracking.
        
        Returns:
            Dict[str, str]: System information
        """
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "anthropic_version": anthropic.__version__ if ANTHROPIC_AVAILABLE else "N/A"
        }
    
    def _create_provenance(self, params: Dict[str, Any], prompt: str) -> AnthropicProvenance:
        """
        Create provenance information for the conversion.
        
        Args:
            params: Parameters used for the conversion
            prompt: The prompt used for the conversion
            
        Returns:
            AnthropicProvenance: Provenance information
        """
        # Get current timestamp in ISO format
        timestamp = datetime.now().isoformat()
        
        # Get system information
        system_info = self._get_system_info()
        
        # Determine model information
        model_version = None
        if self.model.startswith("claude-3-7"):
            model_version = "3.7"
        elif self.model.startswith("claude-3-5"):
            model_version = "3.5"
        elif self.model.startswith("claude-3"):
            model_version = "3"
        
        # Filter out sensitive information from params
        safe_params = {k: v for k, v in params.items() if k not in ["api_key"]}
        
        # Add the prompt to the parameters
        safe_params["prompt"] = prompt
        
        return AnthropicProvenance(
            timestamp=timestamp,
            model=self.model,
            model_version=model_version,
            provider="Anthropic",
            model_family="Claude",
            system_info=system_info,
            conversion_params=safe_params
        )
    
    def convert(self, image_path: Path, save_json: bool = False, 
                json_output_path: Optional[Path] = None, 
                custom_prompt: Optional[str] = None,
                **kwargs) -> str:
        """
        Convert an image to markdown using Anthropic's Claude models.
        
        Args:
            image_path: Path to the image file
            save_json: Whether to save the full response with provenance as JSON
            json_output_path: Path to save the JSON response (if save_json is True)
            custom_prompt: Optional custom prompt to use for the conversion
            **kwargs: Additional parameters for the Claude API
            
        Returns:
            str: Markdown representation of the image content
            
        Raises:
            FileNotFoundError: If the image file does not exist
            Exception: If Anthropic API returns an error
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Get base64-encoded image
        base64_image = self._encode_image(image_path)
        
        # Get the correct media type for the image
        media_type = self._get_media_type(image_path)
        
        # Prepare prompt
        prompt = custom_prompt or self.DEFAULT_PROMPT
        
        # Prepare API parameters
        api_params = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            **{k: v for k, v in kwargs.items() if k not in ["model", "max_tokens", "temperature"]}
        }
        
        try:
            # Make the API call to Claude
            message = self.client.messages.create(
                model=api_params["model"],
                max_tokens=api_params["max_tokens"],
                temperature=api_params["temperature"],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image}}
                        ]
                    }
                ]
            )
            
            # Extract the markdown content from the response
            markdown_content = message.content[0].text
            
            # Post-process to remove triple backticks wrapping the markdown if present
            if markdown_content.startswith("```markdown\n") and markdown_content.endswith("\n```"):
                markdown_content = markdown_content[12:-4]  # Remove ```markdown and ```
            elif markdown_content.startswith("```\n") and markdown_content.endswith("\n```"):
                markdown_content = markdown_content[4:-4]  # Remove ``` and ```
            
            # Save the full response with provenance as JSON if requested
            if save_json and json_output_path:
                # Create provenance information
                provenance = self._create_provenance(api_params, prompt)
                
                # Add request ID if available
                if hasattr(message, "id"):
                    provenance.request_id = message.id
                
                # Prepare data for JSON serialization
                json_data = {
                    "provider": "Anthropic",
                    "model": self.model,
                    "provenance": provenance.as_dict(),
                    "response": message.model_dump() if hasattr(message, 'model_dump') else message.dict(),
                    "image_path": str(image_path),
                    "markdown_content": markdown_content
                }
                
                # Save to JSON file
                with open(json_output_path, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            return markdown_content
            
        except Exception as e:
            error_message = str(e)
            raise Exception(f"Anthropic API error: {error_message}")
    
    def save_markdown(self, image_path: Path, output_path: Optional[Path] = None, 
                     **kwargs) -> Path:
        """
        Convert an image to markdown and save it to a file.
        
        Args:
            image_path: Path to the image file
            output_path: Path to save the markdown file (default: image_path with .md extension)
            **kwargs: Additional parameters to pass to convert method
            
        Returns:
            Path: Path to the saved markdown file
        """
        # Default output path if not provided
        if output_path is None:
            output_path = image_path.with_suffix(".md")
            
        # Convert image to markdown
        markdown_content = self.convert(image_path, **kwargs)
        
        # Save markdown to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        return output_path 