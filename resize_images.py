from PIL import Image
import os
import sys

def resize_image(image_path, max_width):
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Get the original dimensions
            width, height = img.size
            
            # Check if resizing is needed
            if width > max_width:
                # Calculate new height maintaining aspect ratio
                ratio = max_width / width
                new_height = int(height * ratio)
                
                # Resize the image
                resized_img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Save the resized image, overwriting the original
                resized_img.save(image_path)
                print(f"Resized {image_path}")
            else:
                print(f"Skipped {image_path} (width already <= {max_width}px)")
                
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

def main():
    # Maximum width
    MAX_WIDTH = 1100
    
    # Get the target directory
    target_dir = os.getcwd()  # Default to current directory
    
    # If a directory is provided as command line argument, use that instead
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
        if not os.path.isdir(target_dir):
            print(f"Error: '{target_dir}' is not a valid directory")
            return
    
    print(f"Processing PNG files in: {target_dir}")
    
    # Process all PNG files in the target directory
    for filename in os.listdir(target_dir):
        if filename.lower().endswith('.png'):
            image_path = os.path.join(target_dir, filename)
            resize_image(image_path, MAX_WIDTH)

if __name__ == "__main__":
    main()