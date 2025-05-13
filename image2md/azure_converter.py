"""Azure Document Intelligence-based image-to-markdown converter."""
import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
import datetime
import platform
from dataclasses import dataclass, field

try:
    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.ai.documentintelligence.models import (
        AnalyzeDocumentRequest,
        AnalyzeResult,
        DocumentAnalysisFeature,
        DocumentContentFormat
    )
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from .base import Image2MarkdownConverter


@dataclass
class AzureProvenanceInfo:
    """Information about the conversion process for provenance tracking."""
    timestamp: str
    model_id: str
    api_version: str
    system_info: Dict[str, str] = field(default_factory=dict)
    conversion_params: Dict[str, Any] = field(default_factory=dict)
    
    def as_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "model_id": self.model_id,
            "api_version": self.api_version,
            "system_info": self.system_info,
            "conversion_params": self.conversion_params
        }


class AzureDocumentConverter(Image2MarkdownConverter):
    """Converts images to markdown using Azure Document Intelligence service."""
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-11-30",
        model_id: str = "prebuilt-layout",
        **azure_options
    ):
        """
        Initialize Azure Document Intelligence converter.
        
        Args:
            endpoint: Azure Document Intelligence endpoint URL. If None, will use AZURE_ENDPOINT env var.
            api_key: Azure Document Intelligence API key. If None, will use AZURE_API_KEY env var.
            api_version: API version to use, must be >= 2024-11-30 for markdown support
            model_id: Model ID to use, must be "prebuilt-layout" for markdown support
            **azure_options: Additional Azure Document Intelligence options
        
        Raises:
            ImportError: If Azure SDK is not installed
            ValueError: If endpoint or api_key are not provided and not found in environment variables
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure Document Intelligence SDK is not installed. "
                "Please install it with: pip install azure-ai-documentintelligence>=1.0.0"
            )
        
        # Get credentials from environment variables if not provided
        self.endpoint = endpoint or os.environ.get("AZURE_ENDPOINT")
        self.api_key = api_key or os.environ.get("AZURE_API_KEY")
        
        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure Document Intelligence endpoint and API key must be provided "
                "either as parameters or as environment variables "
                "(AZURE_ENDPOINT and AZURE_API_KEY)"
            )
        
        self.api_version = api_version
        self.model_id = model_id
        self.azure_options = azure_options
        
        # Initialize the Azure Document Intelligence client
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.api_key),
            api_version=self.api_version
        )
    
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
    
    def _create_provenance(self, params: Dict[str, Any]) -> AzureProvenanceInfo:
        """
        Create provenance information for the conversion.
        
        Args:
            params: Parameters used for the conversion
            
        Returns:
            AzureProvenanceInfo: Provenance information
        """
        # Get current timestamp in ISO format
        timestamp = datetime.datetime.now().isoformat()
        
        # Get system information
        system_info = self._get_system_info()
        
        # Filter out sensitive information from params
        # Mask endpoint and remove api_key
        safe_params = {k: v for k, v in params.items() if k not in ["api_key"]}
        
        # Mask endpoint if present (keep domain visible but mask path/query)
        if "endpoint" in safe_params and safe_params["endpoint"]:
            from urllib.parse import urlparse
            parsed_url = urlparse(safe_params["endpoint"])
            safe_params["endpoint"] = f"{parsed_url.scheme}://{parsed_url.netloc}/***"
        
        return AzureProvenanceInfo(
            timestamp=timestamp,
            model_id=self.model_id,
            api_version=self.api_version,
            system_info=system_info,
            conversion_params=safe_params
        )
    
    def convert(self, image_path: Path, save_json: bool = False, 
                json_output_path: Optional[Path] = None, **kwargs) -> str:
        """
        Convert an image to markdown using Azure Document Intelligence.
        
        Args:
            image_path: Path to the image file
            save_json: Whether to save the full JSON response with provenance
            json_output_path: Path to save the JSON response (if save_json is True)
            **kwargs: Additional conversion parameters passed to Azure
            
        Returns:
            str: Markdown representation of the image content
            
        Raises:
            FileNotFoundError: If the image file does not exist
            Exception: If Azure Document Intelligence API returns an error
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Prepare features based on kwargs
        features = kwargs.pop('features', [
            DocumentAnalysisFeature.KEY_VALUE_PAIRS,
            DocumentAnalysisFeature.LANGUAGES
        ])
        
        # Collect parameters for provenance before removing conflicting ones
        provenance_params = {
            "model_id": self.model_id,
            "api_version": self.api_version,
            "endpoint": self.endpoint,
            "features": [str(feature) for feature in features],
            **kwargs
        }
        
        # Create provenance information
        provenance = self._create_provenance(provenance_params)
        
        # Remove parameters that would conflict with those already in self
        # These parameters would cause conflicts when passed to the Azure SDK
        params_to_remove = [
            'model_id', 'api_version',  # Already set in __init__
            'endpoint', 'api_key', 'credential',  # Client is already created
            'json_output_path',  # Not used by Azure SDK
            # Add any other possible conflicting parameters here
        ]
        
        for param in params_to_remove:
            kwargs.pop(param, None)
        
        # Prepare the request
        with open(image_path, "rb") as f:
            document_bytes = f.read()
        
        # Analyze the document - creating request object properly
        poller = self.client.begin_analyze_document(
            self.model_id,
            document_bytes,  # Pass binary data directly, not as AnalyzeDocumentRequest
            features=features,
            string_index_type="utf16CodeUnit",
            output_content_format=DocumentContentFormat.MARKDOWN,
            **kwargs
        )
        
        # Get the result
        result: AnalyzeResult = poller.result()
        markdown_content = result.content
        
        # Save JSON response if requested
        if save_json:
            if json_output_path is None:
                json_output_path = image_path.with_suffix('.json')
            
            # Create JSON with both Azure API result and provenance info
            azure_result_dict = result.as_dict()
            
            # Create enhanced JSON with provenance
            enhanced_json = {
                "markdown": markdown_content,
                "provenance": provenance.as_dict(),
                "timestamp": datetime.datetime.now().isoformat(),
                "image_path": str(image_path),
                "conversion_type": "azure",
                "azure_result": azure_result_dict
            }
            
            with open(json_output_path, 'w', encoding='utf-8') as f:
                json.dump(enhanced_json, f, indent=2, ensure_ascii=False)
        
        # Return the markdown content
        return markdown_content 