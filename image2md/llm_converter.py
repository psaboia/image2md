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
        max_completion_tokens: Optional[int] = None,
        temperature: float = 0.2,
        **llm_options
    ):
        """
        Initialize LLM converter.
        
        Args:
            api_key: API key for the LLM provider. If None, will use environment variables.
            model: Model name to use (e.g., "gpt-4o", "claude-3-opus")
            provider: LLM provider, currently supports "openai"
            max_tokens: Maximum tokens for the response (used for older models)
            max_completion_tokens: Maximum completion tokens (used for newer models like o4-)
            temperature: Temperature for response generation
            **llm_options: Additional LLM API options
        
        Raises:
            ImportError: If required SDK is not installed
            ValueError: If api_key is not provided and not found in environment variables
        """
        self.provider = provider.lower()
        self.model = model
        self.max_tokens = max_tokens
        self.max_completion_tokens = max_completion_tokens
        
        # Special handling for o4- models which only support temperature=1.0
        if provider.lower() == "openai" and isinstance(model, str) and model.startswith("o4-"):
            # Force temperature to 1.0 for o4- models
            self.temperature = 1.0
            if temperature != 1.0:
                print(f"Warning: Model {model} only supports temperature=1.0. Overriding provided value.")
        else:
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
            "without any explanations. Do NOT wrap your response in markdown code blocks (```). "
            "Just provide the clean markdown content directly without any surrounding backticks."
        )
        prompt = custom_prompt or default_prompt
        
        # Process the image with OpenAI API
        if self.provider == "openai":
            # Prepare API parameters
            messages = [
                {"role": "system", "content": [
                    {"type": "text", "text": "You are a document layout specialist that converts images to markdown. Preserve the document structure and layout."}
                ]},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]}
            ]
            
            # Prepare API call parameters based on model
            api_params = {
                "model": self.model,
                "messages": messages,
            }
            
            # Choose the right token parameter based on model and handle special cases
            if isinstance(self.model, str) and (self.model.startswith("o4-") or self.model.startswith("gpt-5")):
                # Newer models use max_completion_tokens and only support temperature=1.0
                api_params["max_completion_tokens"] = kwargs.get("max_completion_tokens", 
                                                               self.max_completion_tokens or self.max_tokens)
                # Both o4- and gpt-5 models only support temperature=1.0 (default)
                # Don't set temperature parameter to use the default value
            else:
                # Older models use max_tokens and support custom temperature
                api_params["max_tokens"] = kwargs.get("max_tokens", self.max_tokens)
                api_params["temperature"] = kwargs.get("temperature", self.temperature)
                
            try:
                # Make the API call
                response = self.client.chat.completions.create(**api_params)
                
                # Extract the markdown content from the response
                markdown_content = response.choices[0].message.content
                
                # Post-process to remove triple backticks wrapping the markdown if present
                if markdown_content.startswith("```markdown\n") and markdown_content.endswith("\n```"):
                    markdown_content = markdown_content[12:-4]  # Remove ```markdown and ```
                elif markdown_content.startswith("```\n") and markdown_content.endswith("\n```"):
                    markdown_content = markdown_content[4:-4]  # Remove ``` and ```
                
                # Save the full response with provenance as JSON if requested
                if save_json and json_output_path:
                    # Create provenance information
                    provenance = self._create_provenance(api_params, prompt)
                    
                    # Prepare data for JSON serialization
                    json_data = {
                        "provider": self.provider,
                        "model": self.model,
                        "provenance": provenance.as_dict(),
                        "response": response.model_dump() if hasattr(response, 'model_dump') else response.dict(),
                        "image_path": str(image_path),
                        "markdown_content": markdown_content
                    }
                    
                    # Save to JSON file
                    with open(json_output_path, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                
                return markdown_content
            
            except Exception as e:
                error_message = str(e)
                # Check if this is an OpenAI error with a response
                if hasattr(e, "response") and e.response:
                    error_message += f" - {e.response.json()}"
                raise Exception(f"Error code: {getattr(e, 'status_code', 400)} - {error_message}")
            
        # Add support for other providers here
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
    
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