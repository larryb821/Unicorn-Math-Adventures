import os
from PIL import Image

def convert_webp_to_png():
    """Convert webp images to png format."""
    # Create assets directory structure
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/sounds", exist_ok=True)
    
    # Convert images
    images = {
        "unicorn.webp": "unicorn.png",
        "rainbow.webp": "rainbow.png"
    }
    
    for src, dst in images.items():
        src_path = os.path.join("assets/images", src)
        if os.path.exists(src_path):
            print(f"Converting {src_path} to {dst}...")
            img = Image.open(src_path)
            png_path = os.path.join("assets/images", dst)
            img.save(png_path, "PNG")
            print(f"Saved to {png_path}")
        else:
            print(f"Warning: Source image {src} not found")

if __name__ == "__main__":
    convert_webp_to_png()
