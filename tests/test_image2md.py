"""Tests for the image2md module."""
import os
from pathlib import Path
import pytest
from unittest import mock

import image2md
from image2md.base import Image2MarkdownConverter
from image2md.factory import Image2MarkdownFactory


class TestImage2MarkdownBase:
    """Test the base Image2MarkdownConverter functionality."""
    
    def test_save_markdown(self, tmp_path):
        """Test the save_markdown method."""
        # Create a dummy converter that just returns fixed content
        class DummyConverter(Image2MarkdownConverter):
            def convert(self, image_path, **kwargs):
                return "# Test Content"
        
        # Create a temporary image file
        image_path = tmp_path / "test_image.png"
        image_path.touch()
        
        # Test with default output path
        converter = DummyConverter()
        output_path = converter.save_markdown(image_path)
        
        # Check if the file was created with the right name
        assert output_path == image_path.with_suffix('.md')
        assert output_path.exists()
        assert output_path.read_text() == "# Test Content"
        
        # Test with custom output path
        custom_output = tmp_path / "custom_output.md"
        output_path = converter.save_markdown(image_path, custom_output)
        
        assert output_path == custom_output
        assert output_path.exists()
        assert output_path.read_text() == "# Test Content"


class TestOCRConverter:
    """Test the OCR converter."""
    
    def test_convert(self, tmp_path):
        """Test OCR conversion."""
        # Create a dummy image
        image_path = tmp_path / "test_image.png"
        image_path.touch()
        
        # Test with default options
        converter = image2md.OCRConverter()
        content = converter.convert(image_path)
        
        # Check that the conversion produces expected mock output
        assert isinstance(content, str)
        assert "OCR (eng)" in content
        assert image_path.name in content
        
        # Test with custom language
        converter = image2md.OCRConverter(language="fra")
        content = converter.convert(image_path)
        assert "OCR (fra)" in content


class TestVisionConverter:
    """Test the Vision converter."""
    
    def test_convert(self, tmp_path):
        """Test Vision conversion."""
        # Create a dummy image
        image_path = tmp_path / "test_image.png"
        image_path.touch()
        
        # Test with default options
        converter = image2md.VisionConverter()
        content = converter.convert(image_path)
        
        # Check that the conversion produces expected mock output
        assert isinstance(content, str)
        assert image_path.name in content
        assert "gpt-4-vision" in content
        
        # Test with custom model
        converter = image2md.VisionConverter(model_name="gpt-4-turbo")
        content = converter.convert(image_path)
        assert "gpt-4-turbo" in content
        
        # Test with custom prompt
        custom_prompt = "Describe this image in a poetic way"
        content = converter.convert(image_path, prompt=custom_prompt)
        assert custom_prompt in content


class TestStructureConverter:
    """Test the Structure converter."""
    
    def test_convert(self, tmp_path):
        """Test Structure conversion."""
        # Create a dummy image
        image_path = tmp_path / "test_image.png"
        image_path.touch()
        
        # Test with all features enabled (default)
        converter = image2md.StructureConverter()
        content = converter.convert(image_path)
        
        # Check that the conversion produces expected mock output
        assert isinstance(content, str)
        assert image_path.name in content
        assert "Main Heading" in content
        assert "Item 1" in content  # Lists
        assert "Column 1" in content  # Tables
        
        # Test with tables disabled
        converter = image2md.StructureConverter(detect_tables=False)
        content = converter.convert(image_path)
        assert "Item 1" in content  # Lists should still be there
        assert "Column 1" not in content  # Tables should be gone
        
        # Test with all features disabled
        converter = image2md.StructureConverter(
            detect_tables=False, 
            detect_headings=False,
            detect_lists=False
        )
        content = converter.convert(image_path)
        assert "Main Heading" not in content
        assert "Item 1" not in content
        assert "Column 1" not in content


class TestImage2MarkdownFactory:
    """Test the factory class."""
    
    def test_get_converter(self):
        """Test getting converters from the factory."""
        # Test getting each known converter type
        ocr = Image2MarkdownFactory.get_converter("ocr")
        assert isinstance(ocr, image2md.OCRConverter)
        
        vision = Image2MarkdownFactory.get_converter("vision")
        assert isinstance(vision, image2md.VisionConverter)
        
        structure = Image2MarkdownFactory.get_converter("structure")
        assert isinstance(structure, image2md.StructureConverter)
        
        # Test case insensitivity
        vision2 = Image2MarkdownFactory.get_converter("VISION")
        assert isinstance(vision2, image2md.VisionConverter)
        
        # Test with invalid type
        with pytest.raises(ValueError):
            Image2MarkdownFactory.get_converter("invalid_type")
    
    def test_register_converter(self):
        """Test registering a new converter."""
        # Create a dummy converter
        class CustomConverter(Image2MarkdownConverter):
            def convert(self, image_path, **kwargs):
                return "Custom conversion"
        
        # Register the new converter
        Image2MarkdownFactory.register_converter("custom", CustomConverter)
        
        # Try to get the new converter
        converter = Image2MarkdownFactory.get_converter("custom")
        assert isinstance(converter, CustomConverter)
        
        # Try to register an invalid converter
        class NotAConverter:
            pass
        
        with pytest.raises(TypeError):
            Image2MarkdownFactory.register_converter("invalid", NotAConverter)
    
    def test_available_converters(self):
        """Test getting the list of available converters."""
        converters = Image2MarkdownFactory.available_converters()
        assert "ocr" in converters
        assert "vision" in converters
        assert "structure" in converters
        
        # Make sure it's a copy, not the original
        converters["test"] = "test"
        assert "test" not in Image2MarkdownFactory.available_converters()
    
    def test_convert(self, tmp_path):
        """Test the factory's convert method."""
        # Create a dummy image
        image_path = tmp_path / "test_image.png"
        image_path.touch()
        
        # Mock the save_markdown method to prevent actual file writing
        with mock.patch('image2md.OCRConverter.save_markdown') as mock_save:
            mock_save.return_value = Path(tmp_path / "output.md")
            
            # Test the convenience method
            output = Image2MarkdownFactory.convert(
                image_path, 
                converter_type="ocr", 
                language="deu"
            )
            
            # Check that the right converter was used with right options
            mock_save.assert_called_once()
            assert mock_save.call_args[0][0] == image_path
            
            # Verify the return value
            assert output == Path(tmp_path / "output.md")


def test_module_convert_function(tmp_path):
    """Test the module-level convert function."""
    # Create a dummy image
    image_path = tmp_path / "test_image.png"
    image_path.touch()
    
    # Mock the factory's convert method
    with mock.patch('image2md.factory.Image2MarkdownFactory.convert') as mock_convert:
        mock_convert.return_value = Path(tmp_path / "output.md")
        
        # Call the module-level function
        output = image2md.convert(
            image_path, 
            converter_type="vision",
            max_tokens=500
        )
        
        # Check that the factory method was called with right args
        mock_convert.assert_called_once_with(
            image_path, 
            "vision", 
            None, 
            max_tokens=500
        )
        
        # Verify the return value
        assert output == Path(tmp_path / "output.md") 