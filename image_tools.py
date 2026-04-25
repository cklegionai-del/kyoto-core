from PIL import Image, ImageOps
import os, io

def open_image(path):
    if not os.path.exists(path): raise FileNotFoundError(path)
    return Image.open(path)

def save_image(img, path, format=None):
    img.save(path, format=format or os.path.splitext(path)[1].upper().lstrip('.'))

def resize_image(path, output_path, size=(800, 600)):
    img = open_image(path)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    save_image(img, output_path)
    return output_path

def convert_image(input_path, output_path, format="PNG"):
    img = open_image(input_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    save_image(img, output_path, format=format)
    return output_path

def create_thumbnail(path, size=(128, 128)):
    img = open_image(path)
    img.thumbnail(size, Image.Resampling.LANCZOS)
    thumb_path = path.rsplit('.', 1)[0] + '_thumb.' + path.rsplit('.', 1)[1]
    save_image(img, thumb_path)
    return thumb_path

def get_image_info(path):
    img = open_image(path)
    return {
        "format": img.format,
        "mode": img.mode,
        "size": img.size,
        "width": img.width,
        "height": img.height
    }

def compress_image(input_path, output_path, quality=85):
    img = open_image(input_path)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(output_path, "JPEG", quality=quality, optimize=True)
    return output_path

def comfyui_generate(prompt, output_path="~/Desktop/comfyui_output.png"):
    """
    Placeholder for ComfyUI integration.
    In production, this would call ComfyUI's API.
    """
    print(f"🎨 ComfyUI prompt: {prompt}")
    print("⚠️  ComfyUI API integration not yet implemented")
    print("   To enable: connect to ComfyUI server at localhost:8188")
    # TODO: Implement ComfyUI API call
    # Example: https://github.com/comfyanonymous/ComfyUI/blob/master/api_examples/
    return None

if __name__ == "__main__":
    print("🖼️  Testing image_tools.py...\n")
    
    # Create test image
    test_img = Image.new("RGB", (200, 200), color="blue")
    test_path = os.path.expanduser("~/Desktop/test_image.png")
    test_img.save(test_path)
    print(f"1. Created test image: {test_path}")
    
    # Get info
    info = get_image_info(test_path)
    print(f"2. Image info: {info}")
    
    # Resize
    resized = resize_image(test_path, os.path.expanduser("~/Desktop/test_resized.png"), (100, 100))
    print(f"3. Resized to 100x100: {resized}")
    
    # Thumbnail
    thumb = create_thumbnail(test_path, (64, 64))
    print(f"4. Created thumbnail: {thumb}")
    
    # Convert
    converted = convert_image(test_path, os.path.expanduser("~/Desktop/test_converted.jpg"), "JPEG")
    print(f"5. Converted to JPEG: {converted}")
    
    # Compress
    compressed = compress_image(test_path, os.path.expanduser("~/Desktop/test_compressed.jpg"), quality=50)
    orig_size = os.path.getsize(test_path)
    comp_size = os.path.getsize(compressed)
    print(f"6. Compressed: {orig_size} → {comp_size} bytes ({100*comp_size/orig_size:.0f}% of original)")
    
    # Test ComfyUI placeholder
    print("\n7. Testing ComfyUI integration:")
    comfyui_generate("a blue square", test_path)
    
    # Cleanup
    for f in [test_path, resized, thumb, converted, compressed]:
        if os.path.exists(f): os.remove(f)
    
    print("\n✅ All tests passed!")
