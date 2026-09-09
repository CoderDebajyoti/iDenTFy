import os
import uuid
from typing import Tuple

ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/pjpeg"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# Magic byte signatures
MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
}

def validate_image_bytes(data: bytes) -> Tuple[bool, str]:
    """
    Verify magic bytes header directly from file content.
    Never trusts client-reported MIME type or file extension alone.
    """
    if len(data) < 8:
        return False, "File too small or corrupted"

    for signature, mime in MAGIC_BYTES.items():
        if data.startswith(signature):
            return True, mime

    return False, "Unsupported file format. Only valid JPEG and PNG images are accepted."

def generate_safe_filename(extension: str) -> str:
    """
    Generate a cryptographically random, collision-resistant filename.
    Prevents path traversal and shell injection attacks.
    """
    clean_ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
    if clean_ext not in ALLOWED_EXTENSIONS:
        clean_ext = ".jpg"
    return f"{uuid.uuid4().hex}{clean_ext}"

def is_safe_path(base_dir: str, target_path: str) -> bool:
    """
    Ensure the target path is strictly contained within the intended base directory.
    Prevents path traversal attacks (e.g., ../../etc/passwd).
    """
    resolved_base = os.path.realpath(base_dir)
    resolved_target = os.path.realpath(target_path)
    return resolved_target.startswith(resolved_base)
