"""LLM-based image-to-markdown converter with provenance tracking."""
import os
import base64
import json
import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
import platform
# Add type ignore comment for mypy
import requests  # type: ignore
from dataclasses import dataclass, field

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from .base import Image2MarkdownConverter


@dataclass
class ProvenenanceInfo:
    """Information about the conversion process for provenance tracking."""
    timestamp: str
    model: str
    model_version: Optional[str] = None
    provider: str = "OpenAI"
    system_info: Dict[str, str] = field(default_factory=dict)
    conversion_params: Dict[str, Any] = field(default_factory=dict)
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "model": self.model,
            "model_version": self.model_version,
            "provider": self.provider,
            "system_info": self.system_info,
            "conversion_params": self.conversion_params
        }


class LLMConverter(Image2MarkdownConverter):
    """Converts images to markdown using LLM APIs with provenance tracking."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        provider: str = "openai",
        max_tokens: int = 4000,
        temperature: float = 0.2,
        **llm_options
    ):
        """
        Initialize LLM converter.
        
        Args:
            api_key: API key for the LLM provider. If None, will use environment variables.
            model: Model name to use (e.g., "gpt-4o", "claude-3-opus")
            provider: LLM provider, currently supports "openai"
            max_tokens: Maximum tokens for the response
            temperature: Temperature for response generation
            **llm_options: Additional LLM API options
        
        Raises:
            ImportError: If required SDK is not installed
            ValueError: If api_key is not provided and not found in environment variables
        """
        self.provider = provider.lower()
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.llm_options = llm_options
        
        # OpenAI provider configuration
        if self.provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError(
                    "OpenAI SDK is not installed. "
                    "Please install it with: pip install openai>=1.0.0"
                )
            
            # Get API key from environment variables if not provided
            self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
            
            if not self.api_key:
                raise ValueError(
                    "OpenAI API key must be provided either as a parameter "
                    "or as the OPENAI_API_KEY environment variable"
                )
            
            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=self.api_key)
        
        # Add support for other providers here
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
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
            "hostname": platform.node()
        }
    
    def _create_provenance(self, params: Dict[str, Any], prompt: str) -> ProvenenanceInfo:
        """
        Create provenance information for the conversion.
        
        Args:
            params: Parameters used for the conversion
            prompt: The prompt used for the conversion
            
        Returns:
            ProvenenanceInfo: Provenance information
        """
        # Get current timestamp in ISO format
        timestamp = datetime.datetime.now().isoformat()
        
        # Get system information
        system_info = self._get_system_info()
        
        # Get model version information if available
        model_version = None
        if self.provider == "openai":
            model_version = self.llm_options.get("model_version", None)
        
        # Filter out sensitive information from params
        safe_params = {k: v for k, v in params.items() if k not in ["api_key"]}
        
        # Add the prompt to the parameters
        safe_params["prompt"] = prompt
        
        return ProvenenanceInfo(
            timestamp=timestamp,
            model=self.model,
            model_version=model_version,
            provider=self.provider.capitalize(),
            system_info=system_info,
            conversion_params=safe_params
        )
    
    def convert(self, image_path: Path, save_json: bool = False, 
                json_output_path: Optional[Path] = None, 
                custom_prompt: Optional[str] = None,
                **kwargs) -> str:
        """
        Convert an image to markdown using LLM API.
        
        Args:
            image_path: Path to the image file
            save_json: Whether to save the full response with provenance as JSON
            json_output_path: Path to save the JSON response (if save_json is True)
            custom_prompt: Optional custom prompt to use for the conversion
            **kwargs: Additional conversion parameters passed to the LLM API
            
        Returns:
            str: Markdown representation of the image content
            
        Raises:
            FileNotFoundError: If the image file does not exist
            Exception: If LLM API returns an error
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Get base64-encoded image
        base64_image = self._encode_image(image_path)
        
        # Prepare prompt
        default_prompt = (
            "Convert this image to well-formatted markdown. Maintain the structure "
            "and layout of the document, including proper formatting for headings, "
            "lists, tables, and other elements. Output only the markdown content "
            "without any explanations."
        )
        prompt = custom_prompt or default_prompt
        
        # Combined parameters
        params = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            **kwargs
        }
        
        # Create provenance information
        provenance = self._create_provenance(params, prompt)
        
        markdown_content = ""
        
        # Call appropriate LLM API based on provider
        if self.provider == "openai":
            # Create API parameters
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Convert this image to markdown:"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
            }
            
            # Add any additional parameters from kwargs
            # Filter valid parameters to avoid API errors
            valid_openai_params = [
                "frequency_penalty", "logit_bias", "logprobs", "top_logprobs",
                "presence_penalty", "response_format", "seed", "stop", "stream",
                "tools", "tool_choice", "top_p", "user"
            ]
            
            for k, v in kwargs.items():
                if k in valid_openai_params:
                    api_params[k] = v
            
            # Make the API call
            response = self.client.chat.completions.create(**api_params)  # type: ignore
            
            # Extract markdown from response
            markdown_content = response.choices[0].message.content
        
        # Save JSON response with provenance if requested
        if save_json:
            if json_output_path is None:
                json_output_path = image_path.with_suffix('.json')
            
            # Create JSON response with markdown and provenance
            json_result = {
                "markdown": markdown_content,
                "provenance": provenance.as_dict(),
                "timestamp": datetime.datetime.now().isoformat(),
                "image_path": str(image_path),
                "conversion_type": "llm",
            }
            
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(json_result, f, indent=2, ensure_ascii=False)
        
        return markdown_content 