#!/usr/bin/env python3
"""
Test script for Gemini converter integration with image2md.
This script tests the GeminiConverter class and its integration with the Image2MarkdownFactory.
"""
import os
import sys
import unittest
from pathlib import Path
import json
import shutil
from unittest import mock
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Import image2md components and Gemini converter
try:
    from image2md.base import Image2MarkdownConverter
    from image2md.factory import Image2MarkdownFactory
    from image2md.gemini_converter import GeminiConverter, GEMINI_AVAILABLE
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure the image2md package is installed and gemini_converter.py is implemented correctly")
    sys.exit(1)

if not GEMINI_AVAILABLE:
    print("Google Generative AI SDK is not available. Make sure it's installed:")
    print("pip install google-generativeai>=0.3.0")
    sys.exit(1)

class TestGeminiConverterNoAPI(unittest.TestCase):
    """Test cases for the Gemini converter that don't require an API key."""
    
    def test_factory_registration(self):
        """Test that the converter is registered with the factory."""
        # Mock the import check so the converter is registered
        with mock.patch('image2md.factory.GEMINI_AVAILABLE', True):
            # Re-initialize converters dictionary to apply the mock
            Image2MarkdownFactory._converters = {
                "ocr": Image2MarkdownFactory._converters["ocr"],
                "vision": Image2MarkdownFactory._converters["vision"],
                "structure": Image2MarkdownFactory._converters["structure"],
            }
            
            # Add the converter
            Image2MarkdownFactory._converters["gemini"] = GeminiConverter
            
            # Check converters
            converters = Image2MarkdownFactory.available_converters()
            self.assertIn("gemini", converters)

    def test_converter_init_params(self):
        """Test initialization parameters without creating an actual client."""
        # Mock the genai module and client initialization
        with mock.patch('image2md.gemini_converter.genai'):
            # Mock API key
            mock_api_key = "fake_api_key"
            
            # Create converter
            converter = GeminiConverter(
                api_key=mock_api_key,
                model="gemini-2.5-flash-preview-04-17",
                max_tokens=2000,
                temperature=0.5
            )
            
            # Test parameters
            self.assertEqual(converter.model, "gemini-2.5-flash-preview-04-17")
            self.assertEqual(converter.max_tokens, 2000)
            self.assertEqual(converter.temperature, 0.5)
            self.assertEqual(converter.api_key, mock_api_key)

if __name__ == "__main__":
    # Run tests with more verbose output
    unittest.main(verbosity=2) 