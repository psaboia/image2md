#!/usr/bin/env python3
"""
Test that all converters properly remove triple backticks from model responses.
"""
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import image2md components
from image2md.llm_converter import LLMConverter
from image2md.anthropic_converter import AnthropicConverter
from image2md.gemini_converter import GeminiConverter

class BacktickRemovalTests(unittest.TestCase):
    """Test backtick removal for all converters."""
    
    def test_llm_converter_backticks_markdown(self):
        """Test LLMConverter removes ```markdown blocks."""
        with patch('openai.OpenAI') as mock_openai:
            # Mock API response with backticks
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            
            # Configure the mock to return a response with backticks
            mock_message.content = "```markdown\nThis is markdown content\n```"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # Create converter and test
            converter = LLMConverter(api_key="fake_key")
            converter.client = mock_client
            
            # Mock convert method to avoid actual API calls
            with patch.object(converter, '_encode_image', return_value="fake_base64"):
                with patch('pathlib.Path.exists', return_value=True):
                    # Call convert and check result
                    result = converter.convert(Path("fake_image.jpg"))
                    self.assertEqual(result, "This is markdown content")
    
    def test_llm_converter_backticks_simple(self):
        """Test LLMConverter removes simple ``` blocks."""
        with patch('openai.OpenAI') as mock_openai:
            # Mock API response with simple backticks
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_choice = MagicMock()
            mock_message = MagicMock()
            
            # Configure the mock to return a response with backticks
            mock_message.content = "```\nThis is markdown content\n```"
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai.return_value = mock_client
            
            # Create converter and test
            converter = LLMConverter(api_key="fake_key")
            converter.client = mock_client
            
            # Mock convert method to avoid actual API calls
            with patch.object(converter, '_encode_image', return_value="fake_base64"):
                with patch('pathlib.Path.exists', return_value=True):
                    # Call convert and check result
                    result = converter.convert(Path("fake_image.jpg"))
                    self.assertEqual(result, "This is markdown content")
    
    def test_anthropic_converter_backticks_markdown(self):
        """Test AnthropicConverter removes ```markdown blocks."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            # Mock API response with backticks
            mock_client = MagicMock()
            mock_message = MagicMock()
            mock_content = MagicMock()
            
            # Configure the mock to return a response with backticks
            mock_content.text = "```markdown\nThis is markdown content\n```"
            mock_message.content = [mock_content]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client
            
            # Create converter and test
            converter = AnthropicConverter(api_key="fake_key")
            converter.client = mock_client
            
            # Mock convert method to avoid actual API calls
            with patch.object(converter, '_encode_image', return_value="fake_base64"):
                with patch('pathlib.Path.exists', return_value=True):
                    # Call convert and check result
                    result = converter.convert(Path("fake_image.jpg"))
                    self.assertEqual(result, "This is markdown content")
    
    def test_anthropic_converter_backticks_simple(self):
        """Test AnthropicConverter removes simple ``` blocks."""
        with patch('anthropic.Anthropic') as mock_anthropic:
            # Mock API response with simple backticks
            mock_client = MagicMock()
            mock_message = MagicMock()
            mock_content = MagicMock()
            
            # Configure the mock to return a response with backticks
            mock_content.text = "```\nThis is markdown content\n```"
            mock_message.content = [mock_content]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client
            
            # Create converter and test
            converter = AnthropicConverter(api_key="fake_key")
            converter.client = mock_client
            
            # Mock convert method to avoid actual API calls
            with patch.object(converter, '_encode_image', return_value="fake_base64"):
                with patch('pathlib.Path.exists', return_value=True):
                    # Call convert and check result
                    result = converter.convert(Path("fake_image.jpg"))
                    self.assertEqual(result, "This is markdown content")
    
    def test_gemini_converter_backticks_markdown(self):
        """Test GeminiConverter removes ```markdown blocks."""
        with patch('google.generativeai.GenerativeModel') as mock_gemini:
            # Mock API response with backticks
            mock_model = MagicMock()
            mock_response = MagicMock()
            
            # Configure the mock to return a response with backticks
            mock_response.text = "```markdown\nThis is markdown content\n```"
            mock_model.generate_content.return_value = mock_response
            mock_gemini.return_value = mock_model
            
            # Create converter and test
            with patch('google.generativeai.configure'):
                converter = GeminiConverter(api_key="fake_key")
                converter.client = mock_model
                
                # Mock convert method to avoid actual API calls
                with patch.object(converter, '_load_image', return_value=b"fake_image_data"):
                    with patch('pathlib.Path.exists', return_value=True):
                        # Call convert and check result
                        result = converter.convert(Path("fake_image.jpg"))
                        self.assertEqual(result, "This is markdown content")

    def test_gemini_converter_backticks_simple(self):
        """Test GeminiConverter removes simple ``` blocks."""
        with patch('google.generativeai.GenerativeModel') as mock_gemini:
            # Mock API response with simple backticks
            mock_model = MagicMock()
            mock_response = MagicMock()
            
            # Configure the mock to return a response with backticks
            mock_response.text = "```\nThis is markdown content\n```"
            mock_model.generate_content.return_value = mock_response
            mock_gemini.return_value = mock_model
            
            # Create converter and test
            with patch('google.generativeai.configure'):
                converter = GeminiConverter(api_key="fake_key")
                converter.client = mock_model
                
                # Mock convert method to avoid actual API calls
                with patch.object(converter, '_load_image', return_value=b"fake_image_data"):
                    with patch('pathlib.Path.exists', return_value=True):
                        # Call convert and check result
                        result = converter.convert(Path("fake_image.jpg"))
                        self.assertEqual(result, "This is markdown content")

if __name__ == "__main__":
    unittest.main() 