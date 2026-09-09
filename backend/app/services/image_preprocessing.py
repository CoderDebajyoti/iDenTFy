"""
Image Preprocessing Service
Utilizes OpenCV, Pillow, and NumPy for document optical analysis and preprocessing.
Performs:
- Image decoding and resolution validation
- Sharpness / blur analysis (Laplacian variance)
- Brightness, contrast, and glare analysis
- Skew / orientation assessment and deskewing
- Adaptive thresholding and contrast enhancement (CLAHE) for OCR preparation
- Evidence-based quality scoring (VERIFIED / REQUIRES_REVIEW / NOT_VERIFIED indicators)
"""

import io
import math
from typing import Dict, Any, Tuple, Optional
import cv2
import numpy as np
from PIL import Image

def validate_and_decode_image(file_bytes: bytes) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Safely decode raw bytes into OpenCV BGR array and validate basic dimensional requirements.
    """
    if not file_bytes or len(file_bytes) == 0:
        return None, "File buffer is empty (0 bytes)."

    try:
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None, "Failed to decode image data into pixel array. File may be corrupted or malformed."
        
        height, width = img.shape[:2]
        if width < 100 or height < 100:
            return None, f"Image dimensions too small ({width}x{height}px). Minimum required is 100x100px."
            
        return img, None
    except Exception as e:
        return None, f"Image decoding exception: {str(e)}"

def assess_optical_quality(img_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Analyze optical quality indicators:
    - Dimensions (width, height, aspect ratio)
    - Sharpness score (Laplacian variance)
    - Mean brightness (luminance)
    - Contrast (standard deviation of gray levels)
    - Overexposure / Specular glare percentage
    - Underexposure percentage
    """
    height, width = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Sharpness via Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = round(float(laplacian_var), 2)

    # Luminance metrics
    mean_brightness = round(float(np.mean(gray)), 2)
    contrast_score = round(float(np.std(gray)), 2)

    # Overexposure (glare) and underexposure pixel fractions
    glare_fraction = float(np.sum(gray > 250)) / float(gray.size)
    dark_fraction = float(np.sum(gray < 15)) / float(gray.size)

    # Border screening thresholds
    min_width, min_height = 400, 300
    min_sharpness = 30.0
    min_contrast = 20.0
    min_brightness, max_brightness = 35.0, 235.0

    notes = []
    is_res_ok = (width >= min_width and height >= min_height)
    is_sharp = blur_score >= min_sharpness
    is_lighting_ok = min_brightness <= mean_brightness <= max_brightness
    is_contrast_ok = contrast_score >= min_contrast
    is_glare_ok = glare_fraction < 0.25

    if not is_res_ok:
        notes.append(f"Low resolution: {width}x{height}px (minimum: {min_width}x{min_height}px)")
    if not is_sharp:
        notes.append(f"Image is blurred: sharpness score {blur_score} < threshold {min_sharpness}")
    if mean_brightness < min_brightness:
        notes.append("Image is severely underexposed (too dark)")
    elif mean_brightness > max_brightness:
        notes.append("Image is overexposed (high glare or washed out)")
    if not is_contrast_ok:
        notes.append("Low tonal contrast: text may be difficult to separate from background")
    if not is_glare_ok:
        notes.append(f"Excessive specular glare detected ({round(glare_fraction * 100, 1)}% of surface)")

    is_acceptable = is_res_ok and is_sharp and is_lighting_ok and is_contrast_ok and is_glare_ok

    # Quality rating
    if blur_score >= 150.0 and is_acceptable and contrast_score > 40.0:
        rating = "Good"
    elif is_acceptable:
        rating = "Acceptable"
    elif not is_sharp and blur_score < 10.0:
        rating = "Critical Failure"
    else:
        rating = "Poor"

    return {
        "valid": is_acceptable,
        "width": width,
        "height": height,
        "aspect_ratio": round(width / float(height), 2),
        "blur_score": blur_score,
        "brightness": mean_brightness,
        "contrast": contrast_score,
        "glare_percentage": round(glare_fraction * 100, 2),
        "dark_percentage": round(dark_fraction * 100, 2),
        "quality_rating": rating,
        "notes": notes
    }

def detect_skew_angle(gray_img: np.ndarray) -> float:
    """
    Detect document skew angle in degrees using image thresholding and minAreaRect.
    Returns angle between -45 and 45 degrees.
    """
    try:
        # Invert binary image so document foreground is white
        thresh = cv2.adaptiveThreshold(
            gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8
        )
        coords = np.column_stack(np.where(thresh > 0))
        if len(coords) < 100:
            return 0.0

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        elif angle > 45:
            angle = 90 - angle
        else:
            angle = -angle

        # If angle is minor, ignore
        if abs(angle) < 0.5:
            return 0.0
        return round(float(angle), 2)
    except Exception:
        return 0.0

def deskew_image(img_bgr: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate image around center by given angle to correct orientation skew.
    """
    if abs(angle) < 0.5:
        return img_bgr

    height, width = img_bgr.shape[:2]
    center = (width // 2, height // 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    deskewed = cv2.warpAffine(
        img_bgr, rot_mat, (width, height), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )
    return deskewed

def enhance_contrast_clahe(img_bgr: np.ndarray) -> np.ndarray:
    """
    Apply Contrast Limited Adaptive Histogram Equalization (CLAHE) on the L-channel in LAB color space.
    Enhances text legibility while avoiding noise amplification.
    """
    try:
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l_channel)
        merged = cv2.merge((cl, a_channel, b_channel))
        return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
    except Exception:
        return img_bgr

def preprocess_document_for_ocr(img_bgr: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Full preprocessing pipeline:
    1. Assess optical quality
    2. Detect and correct skew angle
    3. Apply CLAHE contrast enhancement
    Returns processed image array and metadata dictionary.
    """
    quality = assess_optical_quality(img_bgr)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    skew_angle = detect_skew_angle(gray)

    processed_img = img_bgr
    if abs(skew_angle) >= 0.5:
        processed_img = deskew_image(processed_img, skew_angle)

    enhanced_img = enhance_contrast_clahe(processed_img)

    metadata = {
        "quality": quality,
        "skew_angle_detected": skew_angle,
        "deskew_applied": abs(skew_angle) >= 0.5,
        "contrast_enhancement_applied": True,
        "processed_shape": [int(enhanced_img.shape[0]), int(enhanced_img.shape[1])]
    }

    return enhanced_img, metadata
