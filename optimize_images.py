import os
import sys
from PIL import Image
from pathlib import Path

# Image optimization settings
MAX_SIZE_KB = 300
MAX_SIZE_BYTES = MAX_SIZE_KB * 1024
IMAGES_DIR = "images"
TARGET_WIDTH = 2000  # Max width in pixels for large images

# Quality settings for different formats
JPEG_QUALITY = 82  # High quality for JPEGs
WEBP_QUALITY = 80  # Quality for WebP
PNG_COMPRESSION = 9  # Max compression for PNG

def optimize_image(input_path):
    """Optimize a single image and convert to WebP if needed"""
    try:
        img = Image.open(input_path)
        original_size = os.path.getsize(input_path)
        original_size_kb = original_size / 1024
        
        # Get image info
        filename = os.path.basename(input_path)
        name_without_ext = os.path.splitext(filename)[0]
        
        print(f"\n📷 Processing: {filename}")
        print(f"   Original size: {original_size_kb:.2f} KB")
        
        # Skip if already small
        if original_size <= MAX_SIZE_BYTES and original_size_kb < 150:
            print(f"   ✓ Already optimized (small file)")
            return filename, original_size_kb, original_size_kb, False
        
        # Resize if image is very large
        img_copy = img.copy()
        if img_copy.width > TARGET_WIDTH:
            ratio = TARGET_WIDTH / img_copy.width
            new_height = int(img_copy.height * ratio)
            img_copy = img_copy.resize((TARGET_WIDTH, new_height), Image.Resampling.LANCZOS)
            print(f"   📏 Resized to {TARGET_WIDTH}x{new_height}")
        
        # Optimize based on file type
        webp_path = os.path.join(IMAGES_DIR, f"{name_without_ext}.webp")
        
        if img_copy.mode == 'RGBA':
            # For PNG with transparency, save as WebP with quality
            img_copy.save(webp_path, 'WEBP', quality=WEBP_QUALITY)
        else:
            # Convert to RGB for JPEG-like compression
            if img_copy.mode != 'RGB':
                img_copy = img_copy.convert('RGB')
            img_copy.save(webp_path, 'WEBP', quality=WEBP_QUALITY)
        
        # Check WebP file size
        webp_size = os.path.getsize(webp_path)
        webp_size_kb = webp_size / 1024
        
        print(f"   ✓ Converted to WebP: {webp_size_kb:.2f} KB")
        
        # If still too large, reduce quality
        if webp_size > MAX_SIZE_BYTES:
            for quality in [75, 70, 65, 60, 55, 50]:
                if img_copy.mode == 'RGBA':
                    img_copy.save(webp_path, 'WEBP', quality=quality)
                else:
                    img_rgb = img_copy if img_copy.mode == 'RGB' else img_copy.convert('RGB')
                    img_rgb.save(webp_path, 'WEBP', quality=quality)
                
                new_size = os.path.getsize(webp_path)
                if new_size <= MAX_SIZE_BYTES:
                    new_size_kb = new_size / 1024
                    print(f"   ✓ Further optimized (quality {quality}): {new_size_kb:.2f} KB")
                    return filename, original_size_kb, new_size_kb, True
        
        savings_percent = ((original_size - webp_size) / original_size) * 100
        print(f"   💾 Savings: {savings_percent:.1f}%")
        
        return filename, original_size_kb, webp_size_kb, True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return filename, 0, 0, False

def main():
    if not os.path.exists(IMAGES_DIR):
        print(f"❌ {IMAGES_DIR} directory not found!")
        return
    
    print("=" * 60)
    print("🚀 Image Optimization for Web Performance")
    print("=" * 60)
    print(f"Target: Each image under {MAX_SIZE_KB}KB in WebP format")
    print()
    
    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_files = [f for f in os.listdir(IMAGES_DIR) 
                  if os.path.splitext(f)[1].lower() in image_extensions]
    
    if not image_files:
        print("❌ No images found in images directory!")
        return
    
    print(f"Found {len(image_files)} images to process\n")
    
    results = []
    total_original = 0
    total_optimized = 0
    converted_count = 0
    
    for filename in sorted(image_files):
        filepath = os.path.join(IMAGES_DIR, filename)
        result = optimize_image(filepath)
        results.append(result)
        
        if result[1] > 0:
            total_original += result[1]
            total_optimized += result[2]
            if result[3]:
                converted_count += 1
    
    print("\n" + "=" * 60)
    print("📊 OPTIMIZATION SUMMARY")
    print("=" * 60)
    print(f"Total images processed: {len(results)}")
    print(f"Images converted to WebP: {converted_count}")
    print(f"Total original size: {total_original:.2f} KB")
    print(f"Total optimized size: {total_optimized:.2f} KB")
    if total_original > 0:
        savings = ((total_original - total_optimized) / total_original) * 100
        print(f"Total savings: {savings:.1f}%")
    print("=" * 60)
    
    # List WebP files created
    webp_files = [f for f in os.listdir(IMAGES_DIR) if f.endswith('.webp')]
    if webp_files:
        print(f"\n✅ Created {len(webp_files)} WebP files:")
        for f in sorted(webp_files):
            size_kb = os.path.getsize(os.path.join(IMAGES_DIR, f)) / 1024
            print(f"   • {f} ({size_kb:.2f} KB)")

if __name__ == "__main__":
    main()
