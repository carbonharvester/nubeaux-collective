#!/usr/bin/env python3
"""
Image Optimization Script for NUBEAUX Collective Website
Compresses JPG images and creates WebP versions for faster loading.

Requirements:
    pip3 install Pillow

Usage:
    python3 optimize-images.py
"""

import os
from pathlib import Path
from PIL import Image
import sys

# Configuration
ASSETS_DIR = Path(__file__).parent / "assets"
MAX_WIDTH = 2000  # Max width for images
JPEG_QUALITY = 80  # Quality for JPEG compression (1-100)
WEBP_QUALITY = 80  # Quality for WebP conversion
MIN_FILE_SIZE = 500 * 1024  # Only optimize files larger than 500KB

# Priority files for WebP conversion (hero/featured images)
HERO_IMAGES = [
    "hero_Ol_seki_klein-300.jpg",
    "HemingwaysRooms-Klein-13_mobile_hero.jpg",
    "klein_contact_page.jpg",
    "four_seasons_the_westcliff.jpg",
]

def get_file_size_mb(path):
    """Get file size in MB."""
    return os.path.getsize(path) / (1024 * 1024)

def optimize_jpeg(input_path, output_path=None):
    """Compress JPEG image while maintaining quality."""
    if output_path is None:
        output_path = input_path

    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Resize if too large
            width, height = img.size
            if width > MAX_WIDTH:
                ratio = MAX_WIDTH / width
                new_height = int(height * ratio)
                img = img.resize((MAX_WIDTH, new_height), Image.LANCZOS)

            # Save with compression
            img.save(output_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def convert_to_webp(input_path, output_path=None):
    """Convert image to WebP format."""
    if output_path is None:
        output_path = Path(input_path).with_suffix('.webp')

    try:
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')

            # Save as WebP
            img.save(output_path, 'WEBP', quality=WEBP_QUALITY, method=6)

        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def find_large_images(directory, min_size=MIN_FILE_SIZE):
    """Find all images larger than min_size."""
    large_images = []

    for ext in ['*.jpg', '*.jpeg', '*.JPG', '*.JPEG']:
        for path in directory.rglob(ext):
            if os.path.getsize(path) > min_size:
                large_images.append(path)

    return sorted(large_images, key=lambda x: os.path.getsize(x), reverse=True)

def main():
    print("=" * 60)
    print("NUBEAUX Collective - Image Optimization Script")
    print("=" * 60)
    print()

    if not ASSETS_DIR.exists():
        print(f"Error: Assets directory not found: {ASSETS_DIR}")
        sys.exit(1)

    # Find large images
    print("Scanning for images larger than 500KB...")
    large_images = find_large_images(ASSETS_DIR)
    print(f"Found {len(large_images)} images to optimize")
    print()

    # Calculate total size before
    total_before = sum(os.path.getsize(p) for p in large_images)
    print(f"Total size before: {total_before / (1024 * 1024):.1f} MB")
    print()

    # Optimize each image
    print("Optimizing images...")
    print("-" * 60)

    optimized = 0
    failed = 0

    for path in large_images:
        size_before = get_file_size_mb(path)
        print(f"Processing: {path.name} ({size_before:.2f} MB)")

        # Backup original (optional - comment out to overwrite)
        # backup_path = path.with_suffix('.jpg.backup')
        # if not backup_path.exists():
        #     shutil.copy(path, backup_path)

        if optimize_jpeg(path):
            size_after = get_file_size_mb(path)
            reduction = ((size_before - size_after) / size_before) * 100
            print(f"  -> {size_after:.2f} MB ({reduction:.1f}% reduction)")
            optimized += 1
        else:
            failed += 1

    print()
    print("-" * 60)
    print(f"Optimized: {optimized} images")
    print(f"Failed: {failed} images")

    # Calculate total size after
    total_after = sum(os.path.getsize(p) for p in large_images if p.exists())
    reduction = ((total_before - total_after) / total_before) * 100
    print()
    print(f"Total size after: {total_after / (1024 * 1024):.1f} MB")
    print(f"Total reduction: {reduction:.1f}%")
    print()

    # Convert hero images to WebP
    print("=" * 60)
    print("Converting hero images to WebP...")
    print("-" * 60)

    webp_converted = 0
    for hero_name in HERO_IMAGES:
        hero_path = ASSETS_DIR / hero_name
        if hero_path.exists():
            webp_path = hero_path.with_suffix('.webp')
            if not webp_path.exists():
                print(f"Converting: {hero_name}")
                if convert_to_webp(hero_path, webp_path):
                    webp_size = get_file_size_mb(webp_path)
                    jpg_size = get_file_size_mb(hero_path)
                    print(f"  -> Created {webp_path.name} ({webp_size:.2f} MB vs {jpg_size:.2f} MB JPG)")
                    webp_converted += 1
            else:
                print(f"Skipping: {hero_name} (WebP already exists)")
        else:
            print(f"Not found: {hero_name}")

    print()
    print(f"WebP files created: {webp_converted}")
    print()
    print("=" * 60)
    print("Optimization complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
