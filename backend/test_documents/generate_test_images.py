import os
import cv2
import numpy as np

def generate_images():
    # Create the test_documents directory
    os.makedirs("test_documents", exist_ok=True)
    
    # 1. Clear Document (Synthetic Passport Template)
    clear_img = np.ones((800, 1000, 3), dtype=np.uint8) * 215
    # Add mockup labels and text
    cv2.putText(clear_img, "PASSPORT OF SPECIMEN", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 0), 3)
    cv2.putText(clear_img, "SURNAME: SMITH", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.putText(clear_img, "GIVEN NAMES: JOHN", (50, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.putText(clear_img, "DOCUMENT NUMBER: A12345678", (50, 450), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.putText(clear_img, "DATE OF BIRTH: 01 JAN 1990", (50, 550), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    
    # Machine Readable Zone (MRZ) mock lines
    cv2.putText(clear_img, "P<USASMITH<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<", (50, 680), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    cv2.putText(clear_img, "A123456788USA9001011M2501019<<<<<<<<<<<<<<02", (50, 730), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)
    
    cv2.imwrite("test_documents/clear.jpg", clear_img)
    
    # 2. Blurry Document (Apply Gaussian Blur)
    blurry_img = cv2.GaussianBlur(clear_img, (35, 35), 0)
    cv2.imwrite("test_documents/blurry.jpg", blurry_img)
    
    # 3. Dark Document (Dim down the brightness)
    dark_img = (clear_img * 0.15).astype(np.uint8)
    cv2.imwrite("test_documents/dark.jpg", dark_img)
    
    # 4. Bright/Glare Document (Increase the brightness)
    bright_img = np.clip(clear_img.astype(np.int16) + 120, 0, 255).astype(np.uint8)
    cv2.imwrite("test_documents/bright.jpg", bright_img)
    
    # 5. Invalid Image (A non-image file renamed with PNG extension)
    with open("test_documents/invalid.png", "wb") as f:
        f.write(b"FAKE PNG FILE CONTENT - NOT A DECODABLE IMAGE DATA")
        
    # 6. Unsupported File Format (.txt format)
    with open("test_documents/unsupported.txt", "w") as f:
        f.write("This is a plain text file that shouldn't be parsed as an image.")
        
    # 7. Oversized file (>10MB)
    with open("test_documents/oversized.png", "wb") as f:
        f.write(b"\x00" * (11 * 1024 * 1024))  # Write exactly 11 MB of zeros
        
    print("Test document assets generated successfully in test_documents/.")

if __name__ == "__main__":
    generate_images()
