import cv2
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, Tuple, Optional

def decode_image_bytes(image_bytes: bytes) -> Tuple[Optional[np.ndarray], Optional[str]]:
    """
    Safely decode raw bytes into OpenCV BGR numpy array.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None, "Failed to decode image data into pixel array. Image may be corrupted."
        return img, None
    except Exception as e:
        return None, f"Image decoding exception: {str(e)}"

def analyze_image_quality(image_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Calculate optical quality indicators:
    - Dimensions (width, height)
    - Blur score (Laplacian variance)
    - Brightness score (mean pixel luminance)
    - Overall validity against border screening quality thresholds
    """
    height, width = image_bgr.shape[:2]
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Blur score via Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    blur_score = round(float(laplacian_var), 2)

    # Brightness score via mean luminance
    mean_brightness = round(float(np.mean(gray)), 2)

    # Quality rules
    min_width, min_height = 400, 300
    min_blur_acceptable = 30.0 # Below 30 is severely blurred
    min_brightness, max_brightness = 30.0, 235.0

    is_resolution_ok = width >= min_width and height >= min_height
    is_sharp_ok = blur_score >= min_blur_acceptable
    is_lighting_ok = min_brightness <= mean_brightness <= max_brightness

    is_valid = is_resolution_ok and is_sharp_ok and is_lighting_ok

    quality_notes = []
    if not is_resolution_ok:
        quality_notes.append(f"Low resolution ({width}x{height}, minimum required is {min_width}x{min_height})")
    if not is_sharp_ok:
        quality_notes.append(f"Image is blurry (sharpness score {blur_score} < threshold {min_blur_acceptable})")
    if mean_brightness < min_brightness:
        quality_notes.append("Image is severely underexposed (too dark)")
    elif mean_brightness > max_brightness:
        quality_notes.append("Image is overexposed (glare or washed out)")

    return {
        "valid": is_valid,
        "width": width,
        "height": height,
        "blur_score": blur_score,
        "brightness": mean_brightness,
        "quality_rating": "Good" if (blur_score > 150 and is_lighting_ok) else "Acceptable" if is_valid else "Poor",
        "notes": quality_notes
    }
