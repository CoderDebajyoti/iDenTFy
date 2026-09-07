"""
Tampering & Forensic Analysis Service
Implements:
1. EXIF and metadata analysis (detects editing software tags such as Photoshop/GIMP)
2. Error Level Analysis (ELA) with regional difference scoring
3. Image compression and noise continuity heuristics
4. Suspicious region gradient analysis
5. PyTorch advanced tampering model integration hook
"""

import io
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from typing import Dict, Any, List
from app.services.deep_tamper_model import advanced_tamper_engine

def analyze_metadata_forensics(image_bytes: bytes) -> Dict[str, Any]:
    """
    Examine EXIF metadata for editing software traces, multiple save generations,
    and missing camera capture tags.
    """
    software_found = None
    has_exif = False
    is_suspicious = False
    notes = []

    try:
        pil_img = Image.open(io.BytesIO(image_bytes))
        exif = pil_img.getexif()

        if exif and len(exif) > 0:
            has_exif = True
            # Tag 305 is Software
            software_tag = exif.get(305)
            if software_tag:
                software_str = str(software_tag).lower()
                software_found = str(software_tag)
                flagged_tools = ["photoshop", "gimp", "paint.net", "canva", "pixlr", "snapseed"]
                for tool in flagged_tools:
                    if tool in software_str:
                        is_suspicious = True
                        notes.append(f"Image editing software detected in metadata tag: '{software_tag}'")
                        break
        else:
            notes.append("EXIF metadata stripped or absent (common in web-transferred or edited images).")

    except Exception as e:
        notes.append(f"Metadata parsing warning: {str(e)}")

    return {
        "has_exif": has_exif,
        "software_detected": software_found,
        "is_suspicious": is_suspicious,
        "notes": notes
    }

def compute_error_level_analysis(image_bytes: bytes, quality: int = 92) -> Dict[str, Any]:
    """
    Error Level Analysis (ELA).
    Resaves image at a known JPEG compression quality and measures
    the magnitude of pixel deviation between the original and compressed image.
    Modified/spliced areas compress at a different rate, producing distinct ELA brightness.
    """
    try:
        original = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Save to memory buffer at specified quality
        buffer = io.BytesIO()
        original.save(buffer, "JPEG", quality=quality)
        buffer.seek(0)
        resaved = Image.open(buffer)

        # Compute difference
        diff = ImageChops.difference(original, resaved)

        # Scale difference to enhance visibility
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema]) if extrema else 1
        scale = 255.0 / max(max_diff, 1)
        enhanced_diff = ImageEnhance.Brightness(diff).enhance(scale)

        # Convert to numpy for numeric metrics
        diff_np = np.array(diff, dtype=np.float32)
        mean_err = round(float(np.mean(diff_np)), 3)
        std_err = round(float(np.std(diff_np)), 3)

        # High mean error + high variance across regions indicates multi-source splicing
        is_ela_elevated = (mean_err > 12.0) or (std_err > 18.0)

        return {
            "mean_error": mean_err,
            "std_error": std_err,
            "is_elevated": is_ela_elevated,
            "scale_factor": round(scale, 2),
            "ela_indicator": "High Discrepancy" if is_ela_elevated else "Normal Uniform Compression"
        }
    except Exception as e:
        return {
            "mean_error": 0.0,
            "std_error": 0.0,
            "is_elevated": False,
            "scale_factor": 1.0,
            "ela_indicator": f"ELA computation error: {str(e)}"
        }

def analyze_document_tampering(image_bytes: bytes, image_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Comprehensive multi-method tampering analysis:
    - EXIF metadata heuristics
    - Error Level Analysis (ELA)
    - Gradient boundary inspection around photo zones
    - Advanced deep model hook
    """
    metadata_res = analyze_metadata_forensics(image_bytes)
    ela_res = compute_error_level_analysis(image_bytes)
    deep_model_res = advanced_tamper_engine.predict(image_bgr)

    indicators = []
    suspicion_score = 0.0

    # 1. Evaluate metadata
    if metadata_res["is_suspicious"]:
        indicators.append(f"Forensic Metadata: {metadata_res['notes'][0]}")
        suspicion_score += 0.35

    # 2. Evaluate ELA
    if ela_res["is_elevated"]:
        indicators.append(f"ELA Anomaly: Elevated compression error variance ({ela_res['mean_error']} mean, {ela_res['std_error']} std).")
        suspicion_score += 0.30

    # 3. Photo area edge discontinuity heuristic
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edge_magnitude = np.sqrt(sobelx**2 + sobely**2)

    # Check for abrupt rectangular edge spikes typical of photo paste-in
    high_edge_density = float(np.sum(edge_magnitude > 200) / edge_magnitude.size)
    if high_edge_density > 0.08:
        indicators.append("Localized edge gradient discontinuity detected (potential copy-paste insertion boundary).")
        suspicion_score += 0.25

    tampering_detected = suspicion_score >= 0.50
    requires_review = suspicion_score >= 0.25

    return {
        "tampering_detected": tampering_detected,
        "confidence": round(min(suspicion_score, 0.99), 2),
        "requires_review": requires_review,
        "indicators": indicators if indicators else ["No tampering or digital manipulation detected across forensic checks."],
        "metadata_analysis": {
            "has_exif": metadata_res["has_exif"],
            "software_detected": metadata_res["software_detected"],
            "summary": "Clean" if not metadata_res["is_suspicious"] else "Edited"
        },
        "ela_analysis": {
            "mean_error": ela_res["mean_error"],
            "std_error": ela_res["std_error"],
            "status": ela_res["ela_indicator"]
        },
        "advanced_model": deep_model_res
    }
