"""
Image I/O service — handles upload validation, encoding, and decoding.
"""

import base64
import io

from PIL import Image
from loguru import logger

from app.config import settings
from app.utils.exceptions import ImageValidationError


SUPPORTED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP", "TIFF", "BMP"}


async def decode_upload(upload_file) -> Image.Image:
    """
    Read an UploadFile and return a validated PIL Image.

    Validates format, file size, and dimensions.
    """
    # Read file bytes
    contents = await upload_file.read()

    # Check file size
    if len(contents) > settings.max_upload_bytes:
        raise ImageValidationError(
            f"File too large: {len(contents) / 1024 / 1024:.1f}MB "
            f"(max {settings.MAX_UPLOAD_SIZE_MB}MB)"
        )

    if len(contents) == 0:
        raise ImageValidationError("Empty file uploaded")

    # Try to open as image
    try:
        image = Image.open(io.BytesIO(contents))
        image.load()  # Force full decode to catch truncated files
    except Exception as e:
        raise ImageValidationError(f"Cannot read image file: {e}")

    # Validate format
    fmt = (image.format or "").upper()
    if fmt not in SUPPORTED_FORMATS:
        raise ImageValidationError(
            f"Unsupported format: {fmt}. Supported: {', '.join(sorted(SUPPORTED_FORMATS))}"
        )

    # Validate dimensions
    w, h = image.size
    if w > settings.MAX_IMAGE_DIMENSION or h > settings.MAX_IMAGE_DIMENSION:
        raise ImageValidationError(
            f"Image too large: {w}x{h} "
            f"(max {settings.MAX_IMAGE_DIMENSION}x{settings.MAX_IMAGE_DIMENSION})"
        )

    if w < 64 or h < 64:
        raise ImageValidationError(
            f"Image too small: {w}x{h} (minimum 64x64)"
        )

    # Convert to RGB (remove alpha, handle grayscale)
    if image.mode != "RGB":
        image = image.convert("RGB")

    logger.info(
        "Image validated: format={}, size={}x{}, bytes={:.1f}KB",
        fmt, w, h, len(contents) / 1024,
    )
    return image


def encode_response(
    image: Image.Image, quality: int = 92, format: str = "JPEG"
) -> str:
    """
    Encode a PIL Image to a base64 string.

    Args:
        image: PIL Image to encode.
        quality: JPEG quality (1-100).
        format: Output format (JPEG, PNG, WEBP).

    Returns:
        Base64-encoded string (without data URI prefix).
    """
    buffer = io.BytesIO()

    save_kwargs = {"format": format}
    if format.upper() in ("JPEG", "JPG"):
        save_kwargs["quality"] = quality
        save_kwargs["optimize"] = True
    elif format.upper() == "WEBP":
        save_kwargs["quality"] = quality

    image.save(buffer, **save_kwargs)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    logger.debug(
        "Image encoded: {}x{}, format={}, b64_size={:.1f}KB",
        image.size[0], image.size[1], format, len(b64) / 1024,
    )
    return b64
