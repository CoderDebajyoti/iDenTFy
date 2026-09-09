"""
Image Preprocessing Service
Utilizes OpenCV, Pillow, and NumPy for document optical analysis, perspective correction,
orientation normalization, and multi-variant preparation for OCR.
"""

import io
import math
import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
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

def order_points(pts: np.ndarray) -> np.ndarray:
    """
    Order coordinates as: top-left, top-right, bottom-right, bottom-left.
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]  # top-left
    rect[2] = pts[np.argmax(s)]  # bottom-right

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left
    return rect

def detect_and_warp_document_quad(img_bgr: np.ndarray) -> Tuple[np.ndarray, bool]:
    """
    Detect document quadrilateral boundary and apply perspective transformation.
    If no reliable 4-corner document quad is found, returns original image and False.
    """
    try:
        h, w = img_bgr.shape[:2]
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Multi-scale edge detection
        edges = cv2.Canny(blurred, 50, 150)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return img_bgr, False

        # Sort contours by area descending
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
        doc_quad = None
        img_area = float(h * w)

        for c in contours:
            area = cv2.contourArea(c)
            # Must occupy between 25% and 98% of total frame
            if area < img_area * 0.25 or area > img_area * 0.98:
                continue

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4 and cv2.isContourConvex(approx):
                doc_quad = approx.reshape(4, 2)
                break

        if doc_quad is None:
            return img_bgr, False

        # Order corner points
        rect = order_points(doc_quad)
        (tl, tr, br, bl) = rect

        # Compute output dimensions
        width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        max_w = max(int(width_a), int(width_b))

        height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        max_h = max(int(height_a), int(height_b))

        # Validate aspect ratio (typical ID/Passport aspect ratio is ~1.2 to 1.7)
        aspect = max_w / float(max_h) if max_h > 0 else 0
        if not (0.5 <= aspect <= 2.2) or max_w < 300 or max_h < 200:
            return img_bgr, False

        dst = np.array([
            [0, 0],
            [max_w - 1, 0],
            [max_w - 1, max_h - 1],
            [0, max_h - 1]
        ], dtype="float32")

        m = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(img_bgr, m, (max_w, max_h), flags=cv2.INTER_CUBIC)
        return warped, True
    except Exception:
        return img_bgr, False

def detect_skew_angle(gray_img: np.ndarray) -> float:
    """
    Detect document skew angle in degrees using image thresholding and minAreaRect.
    Returns angle between -45 and 45 degrees.
    """
    try:
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

def normalize_illumination(img_bgr: np.ndarray) -> np.ndarray:
    """
    Normalize non-uniform illumination across the document using background division.
    Effectively removes harsh flash glare and shadows.
    """
    try:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        # Large Gaussian filter to estimate background illumination gradient
        bg = cv2.GaussianBlur(gray, (51, 51), 0)
        # Avoid division by zero
        bg[bg == 0] = 1
        normalized = cv2.divide(gray, bg, scale=255.0)
        # Mild sharpening
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        sharpened = cv2.filter2D(normalized, -1, kernel)
        return cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
    except Exception:
        return img_bgr

def preprocess_document_for_ocr(img_bgr: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Full multi-stage preprocessing pipeline:
    1. Optical quality assessment
    2. Document boundary detection & perspective correction (flattening)
    3. Orientation deskewing
    4. LAB CLAHE contrast enhancement
    Returns enhanced image and complete processing metadata.
    """
    quality = assess_optical_quality(img_bgr)

    # 1. Perspective correction if quadrilateral detected
    flattened_img, perspective_applied = detect_and_warp_document_quad(img_bgr)

    # 2. Skew angle detection & correction
    gray = cv2.cvtColor(flattened_img, cv2.COLOR_BGR2GRAY)
    skew_angle = detect_skew_angle(gray)

    processed_img = flattened_img
    if abs(skew_angle) >= 0.5:
        processed_img = deskew_image(processed_img, skew_angle)

    # 3. CLAHE enhancement
    enhanced_img = enhance_contrast_clahe(processed_img)

    metadata = {
        "quality": quality,
        "perspective_correction_applied": perspective_applied,
        "skew_angle_detected": skew_angle,
        "deskew_applied": abs(skew_angle) >= 0.5,
        "contrast_enhancement_applied": True,
        "processed_shape": [int(enhanced_img.shape[0]), int(enhanced_img.shape[1])]
    }

    return enhanced_img, metadata
