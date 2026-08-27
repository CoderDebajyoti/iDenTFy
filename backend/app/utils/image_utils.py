"""
Image Utility Module.

Contains functions for:
- Assessing image quality (resolution, blur, brightness)
- Preprocessing images to enhance quality before OCR
"""

import cv2
import numpy as np

def assess_image_quality(image: np.ndarray) -> dict:
    """
    Evaluates basic image characteristics: resolution, blur, brightness.
    
    Args:
        image (np.ndarray): Input image in BGR format.
        
    Returns:
        dict: Containing width, height, blur_score, blur_status, 
              brightness, brightness_status, and resolution_status.
    """
    if image is None:
        raise ValueError("Input image is None")
        
    height, width = image.shape[:2]
    
    # Grayscale conversion for metric computation
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
        
    # 1. Resolution Check
    # Requirement: width >= 800 and height >= 600
    resolution_status = "acceptable" if (width >= 800 and height >= 600) else "low_resolution"
    
    # 2. Blur / Focus Evaluation
    # Variance of the Laplacian
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = round(float(laplacian_var), 2)
    
    # Thresholds:
    # blurry: < 30.0
    # acceptable: 30.0 <= score < 100.0
    # sharp: >= 100.0
    if blur_score < 30.0:
        blur_status = "blurry"
    elif blur_score < 100.0:
        blur_status = "acceptable"
    else:
        blur_status = "sharp"
        
    # 3. Brightness Evaluation
    # Mean of pixel values
    mean_brightness = float(np.mean(gray))
    brightness_score = round(mean_brightness, 2)
    
    # Thresholds:
    # too_dark: < 60.0
    # too_bright: > 220.0
    # acceptable: 60.0 <= score <= 220.0
    if brightness_score < 60.0:
        brightness_status = "too_dark"
    elif brightness_score > 220.0:
        brightness_status = "too_bright"
    else:
        brightness_status = "acceptable"
        
    return {
        "width": width,
        "height": height,
        "blur_score": blur_score,
        "blur_status": blur_status,
        "brightness": brightness_score,
        "brightness_status": brightness_status,
        "resolution_status": resolution_status
    }

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Lightly preprocesses the image to enhance text legibility for OCR.
    
    Denoises the image using a Bilateral Filter (preserving edges) and
    applies CLAHE contrast enhancement in LAB color space.
    
    Args:
        image (np.ndarray): Input image in BGR format.
        
    Returns:
        np.ndarray: Preprocessed image in BGR format.
    """
    if image is None:
        raise ValueError("Input image is None")
        
    # Ensure image is in BGR
    if len(image.shape) == 2:
        img_bgr = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    else:
        img_bgr = image.copy()
        
    # 1. Denoise: Bilateral filter is edge-preserving which is optimal for text
    denoised = cv2.bilateralFilter(img_bgr, 5, 50, 50)
    
    # 2. Contrast Enhancement: CLAHE on LAB luminance channel
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl = clahe.apply(l_channel)
    
    limg = cv2.merge((cl, a_channel, b_channel))
    preprocessed = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    return preprocessed
