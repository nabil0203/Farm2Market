%cd "/content/roop"

import os
import glob
from datetime import datetime
from google.colab import files

video_path = "/content/Gerald.mp4"
faces_folder = "/content/faces" 

# Collect all supported image formats
face_images = []
face_images.extend(glob.glob(f"{faces_folder}/*.jpg"))
face_images.extend(glob.glob(f"{faces_folder}/*.jpeg"))
face_images.extend(glob.glob(f"{faces_folder}/*.png"))

print(f"Found {len(face_images)} face images")

if len(face_images) == 0:
    print("No face images found. Check /content/faces/ folder.")
else:
    
    output_files = []

    for face in face_images:
        
        face_name = os.path.splitext(os.path.basename(face))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_name = f"{face_name}_Gerald_swap_{timestamp}.mp4"
        
        print(f"\nProcessing {face_name}...")
        
        !python run.py -s "{face}" -t "{video_path}" -o "{output_name}" --keep-frames --keep-fps --temp-frame-quality 1 --output-video-quality 1 --execution-provider cuda --frame-processor face_swapper face_enhancer
        
        output_path = f"/content/roop/{output_name}"
        
        if os.path.exists(output_path):
            output_files.append(output_path)

    print("\nAll swaps finished.")

    # Create ZIP file
    zip_name = f"Gerald_all_swaps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    print("Creating ZIP file...")
    !zip -r "{zip_name}" {" ".join(output_files)}

    print("Starting download...")
    files.download(zip_name)