from pathlib import Path
from image2md import Image2MarkdownFactory

# Example of using the Vision converter which is the default
def basic_example():
    # Find an image in the examples directory to convert
    examples_dir = Path("examples")
    if examples_dir.exists():
        # Look for any PNG file in the examples directory
        sample_images = list(examples_dir.glob("*.png"))
        if sample_images:
            image_path = sample_images[0]
            print(f"Converting image: {image_path}")
            
            # Basic conversion using Vision model
            output_path = Image2MarkdownFactory.convert(
                image_path, 
                converter_type="vision",
                output_path=Path("output.md")
            )
            
            print(f"Conversion complete! Output saved to: {output_path}")
            print("\nContent preview:")
            with open(output_path, "r") as f:
                content = f.read()
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print("No sample PNG images found in examples directory.")
    else:
        print("Examples directory not found. Creating a simple test image instead.")
        # Create a very basic test file
        Path("test_image.png").touch()
        output_path = Image2MarkdownFactory.convert(
            Path("test_image.png"), 
            converter_type="vision",
            output_path=Path("output.md")
        )
        print(f"Conversion complete! Output saved to: {output_path}")
        print("\nContent preview:")
        with open(output_path, "r") as f:
            content = f.read()
            print(content[:500] + "..." if len(content) > 500 else content)

if __name__ == "__main__":
    print("Running image2md example...")
    basic_example()
    print("\nExample completed!") 