"""
Image preprocessing for ControlNet conditioning.

Handles Canny edge extraction and SDXL-compatible resizing.
"""

import cv2
import numpy as np
from PIL import Image
from loguru import logger
from app.config import settings


def resize_for_inference(image: Image.Image) -> Image.Image:
    """
    Resize image to SDXL-compatible dimensions (multiple of 8, max 1024).

    Maintains aspect ratio and pads/resizes to the target inference resolution.
    """
    target = settings.INFERENCE_RESOLUTION
    w, h = image.size

    # Scale so the longest side = target resolution
    scale = target / max(w, h)
    new_w = int(w * scale)
    new_h = int(h * scale)

    # Round to nearest multiple of 8 (required by SDXL)
    new_w = (new_w // 8) * 8
    new_h = (new_h // 8) * 8

    # Ensure minimum size
    new_w = max(new_w, 64)
    new_h = max(new_h, 64)

    resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    logger.debug("Resized image: {}x{} → {}x{}", w, h, new_w, new_h)
    return resized


def extract_canny_edges(
    image: Image.Image,
    low_threshold: int | None = None,
    high_threshold: int | None = None,
) -> Image.Image:
    """
    Extract Canny edges from an image for ControlNet conditioning.

    Returns a PIL Image with white edges on black background.
    """
    low = low_threshold or settings.CANNY_LOW_THRESHOLD
    high = high_threshold or settings.CANNY_HIGH_THRESHOLD

    # Convert PIL → OpenCV (BGR)
    img_array = np.array(image)
    if len(img_array.shape) == 2:
        gray = img_array
    else:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

    # Apply Gaussian blur to reduce noise before Canny
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Canny edge detection
    edges = cv2.Canny(blurred, low, high)

    # Convert to 3-channel for ControlNet
    edges_3ch = np.stack([edges, edges, edges], axis=-1)

    logger.debug(
        "Canny edges extracted (low={}, high={}, shape={})",
        low, high, edges_3ch.shape,
    )
    return Image.fromarray(edges_3ch)


def prepare_control_image(
    image: Image.Image,
    low_threshold: int | None = None,
    high_threshold: int | None = None,
) -> tuple[Image.Image, Image.Image]:
    """
    Full preprocessing pipeline for ControlNet.

    Returns:
        (resized_image, control_image) — both ready for the pipeline.
    """
    resized = resize_for_inference(image)
    control = extract_canny_edges(resized, low_threshold, high_threshold)

    logger.info(
        "Control image prepared: size={}x{}",
        control.size[0], control.size[1],
    )
    return resized, control
