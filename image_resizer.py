import os
import argparse
from PIL import Image

def resize_images(input_folder, output_folder, target_width):
    """
    Resize all images in input_folder to target_width and save to output_folder
    while maintaining aspect ratio.
    """
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    # Count for statistics
    processed = 0
    skipped = 0
    
    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        input_path = os.path.join(input_folder, filename)
        
        # Skip if it's a directory
        if os.path.isdir(input_path):
            continue
        
        # Try to open the file as an image
        try:
            with Image.open(input_path) as img:
                # Calculate new height to maintain aspect ratio
                width_percent = target_width / float(img.width)
                target_height = int(float(img.height) * width_percent)
                
                # Resize the image
                resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Save the resized image to the output folder
                output_path = os.path.join(output_folder, filename)
                resized_img.save(output_path)
                
                processed += 1
                print(f"Resized: {filename} ({img.width}x{img.height} → {target_width}x{target_height})")
                
        except (IOError, OSError):
            # This happens when the file is not an image
            skipped += 1
            print(f"Skipped: {filename} (not an image or unsupported format)")
    
    return processed, skipped

def main():
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Resize images to a specified width.')
    parser.add_argument('input_folder', help='Path to the folder containing images to resize')
    parser.add_argument('output_folder', help='Path to the folder where resized images will be saved')
    parser.add_argument('width', type=int, help='Target width for the resized images')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate width
    if args.width <= 0:
        print("Error: Width must be a positive integer")
        return
    
    # Validate input folder
    if not os.path.exists(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist")
        return
    
    # Perform image resizing
    print(f"Resizing images from '{args.input_folder}' to width {args.width}px...")
    processed, skipped = resize_images(args.input_folder, args.output_folder, args.width)
    
    # Print summary
    print(f"\nDone! Processed {processed} images, skipped {skipped} files.")
    print(f"Resized images saved to: {args.output_folder}")

if __name__ == "__main__":
    main()