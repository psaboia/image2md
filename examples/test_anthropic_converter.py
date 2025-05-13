#!/usr/bin/env python3
"""
Test script for Anthropic converter integration with image2md.
This script tests the AnthropicConverter class and its integration with the Image2MarkdownFactory.
"""
import os
import sys
import unittest
from pathlib import Path
import json
import shutil
from dotenv import load_dotenv

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Import image2md components and Anthropic converter
try:
    from image2md.base import Image2MarkdownConverter
    from image2md.factory import Image2MarkdownFactory
    from anthropic_integration import AnthropicConverter
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure the image2md package is installed and anthropic_integration.py is in the examples directory")
    sys.exit(1)

class TestAnthropicConverter(unittest.TestCase):
    """Test cases for the Anthropic converter."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once before all tests."""
        # Check if ANTHROPIC_API_KEY is set
        cls.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not cls.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set in environment variables")
        
        # Example image
        cls.image_path = Path(__file__).parent / "83635935.png"
        if not cls.image_path.exists():
            raise FileNotFoundError(f"Test image not found at {cls.image_path}")
        
        # Test output directory
        cls.test_dir = Path(__file__).parent / "anthropic_test_output"
        cls.test_dir.mkdir(exist_ok=True)
        
        # Register Anthropic converter with the factory
        Image2MarkdownFactory.register_converter("anthropic", AnthropicConverter)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        # Comment out the line below to keep test outputs
        # shutil.rmtree(cls.test_dir, ignore_errors=True)
        pass
    
    def setUp(self):
        """Set up before each test."""
        # Create a new instance of the converter for each test
        self.converter = AnthropicConverter(api_key=self.api_key)
    
    def test_converter_initialization(self):
        """Test that the converter initializes correctly."""
        self.assertEqual(self.converter.model, "claude-3-7-sonnet-20250219")
        self.assertEqual(self.converter.max_tokens, 4000)
        self.assertEqual(self.converter.temperature, 0.3)
        self.assertIsNotNone(self.converter.client)
    
    def test_factory_registration(self):
        """Test that the converter is registered with the factory."""
        converters = Image2MarkdownFactory.available_converters()
        self.assertIn("anthropic", converters)
        
        # Test that we can get a converter from the factory
        factory_converter = Image2MarkdownFactory.get_converter("anthropic", api_key=self.api_key)
        self.assertIsInstance(factory_converter, AnthropicConverter)
    
    def test_convert_method(self):
        """Test the convert method."""
        # Use a small max_tokens to speed up the test
        self.converter.max_tokens = 1000
        
        # Convert the image
        result = self.converter.convert(
            self.image_path, 
            custom_prompt="Convert this to very brief markdown."
        )
        
        # Check that we got some markdown
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 100)  # Should have a reasonable length
        
        # Check for markdown elements
        self.assertIn("#", result)  # Should have at least one heading
    
    def test_save_markdown_method(self):
        """Test the save_markdown method."""
        # Use a small max_tokens to speed up the test
        self.converter.max_tokens = 1000
        
        # Output paths
        output_md = self.test_dir / "save_method_test.md"
        output_json = self.test_dir / "save_method_test.json"
        
        # Save markdown
        result_path = self.converter.save_markdown(
            self.image_path,
            output_md,
            save_json=True,
            json_output_path=output_json,
            custom_prompt="Convert this to very brief markdown."
        )
        
        # Check that files were created
        self.assertTrue(output_md.exists())
        self.assertTrue(output_json.exists())
        self.assertEqual(result_path, output_md)
        
        # Check JSON content
        with open(output_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Check JSON structure
        self.assertIn("markdown", json_data)
        self.assertIn("provenance", json_data)
        self.assertIn("timestamp", json_data)
        self.assertIn("image_path", json_data)
        self.assertIn("conversion_type", json_data)
        
        # Check provenance information
        provenance = json_data["provenance"]
        self.assertIn("model", provenance)
        self.assertIn("provider", provenance)
        self.assertIn("system_info", provenance)
        self.assertIn("conversion_params", provenance)
        
        # Check that the model is correct
        self.assertEqual(provenance["model"], "claude-3-7-sonnet-20250219")
        self.assertEqual(provenance["provider"], "Anthropic")
    
    def test_factory_convert_method(self):
        """Test the factory convert method with the Anthropic converter."""
        # Output paths
        output_md = self.test_dir / "factory_test.md"
        output_json = self.test_dir / "factory_test.json"
        
        # Convert through factory
        result_path = Image2MarkdownFactory.convert(
            self.image_path,
            converter_type="anthropic",
            output_path=output_md,
            api_key=self.api_key,
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            save_json=True,
            json_output_path=output_json,
            custom_prompt="Convert this to very brief markdown."
        )
        
        # Check that files were created
        self.assertTrue(output_md.exists())
        self.assertTrue(output_json.exists())
        self.assertEqual(result_path, output_md)
        
        # Check JSON content
        with open(output_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Check that we have the same structure
        self.assertIn("markdown", json_data)
        self.assertIn("provenance", json_data)
        
        # Check that markdown is also in the file
        with open(output_md, 'r', encoding='utf-8') as f:
            markdown = f.read()
        
        self.assertEqual(json_data["markdown"], markdown)
        
    def test_with_custom_model(self):
        """Test with a custom Claude model."""
        # Initialize with a different model
        custom_converter = AnthropicConverter(
            api_key=self.api_key,
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.5
        )
        
        # Output paths
        output_md = self.test_dir / "custom_model_test.md"
        output_json = self.test_dir / "custom_model_test.json"
        
        # Convert
        result_path = custom_converter.save_markdown(
            self.image_path,
            output_md,
            save_json=True,
            json_output_path=output_json,
            custom_prompt="Convert this to very brief markdown."
        )
        
        # Check JSON content
        with open(output_json, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Check that the model is correct
        self.assertEqual(json_data["provenance"]["model"], "claude-3-haiku-20240307")
        self.assertEqual(json_data["provenance"]["conversion_params"]["temperature"], 0.5)

if __name__ == "__main__":
    # Run tests with more verbose output
    unittest.main(verbosity=2) 