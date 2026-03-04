"""
Real-ESRGAN 4K Upscaler.

Uses RealESRGAN_x4plus to enhance output images to 4K resolution
after color grading.
"""

import gc
import os
import urllib.request
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from loguru import logger

from app.config import settings
from app.utils.exceptions import ModelLoadError, ImageProcessingError


class RealESRGANUpscaler:
    """
    4× upscaler using Real-ESRGAN (RRDBNet architecture).

    Downloads model weights automatically on first use.
    """

    def __init__(self):
        self.upsampler = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def _download_weights(self) -> str:
        """Download Real-ESRGAN weights if not cached."""
        weights_dir = Path(settings.MODEL_CACHE_DIR) / "realesrgan"
        weights_dir.mkdir(parents=True, exist_ok=True)
        weights_path = weights_dir / f"{settings.REALESRGAN_MODEL_NAME}.pth"

        if weights_path.exists():
            logger.debug("Real-ESRGAN weights found at {}", weights_path)
            return str(weights_path)

        logger.info("Downloading Real-ESRGAN weights...")
        try:
            urllib.request.urlretrieve(
                settings.REALESRGAN_WEIGHTS_URL,
                str(weights_path),
            )
            logger.info("✓ Real-ESRGAN weights downloaded to {}", weights_path)
        except Exception as e:
            raise ModelLoadError(f"Failed to download Real-ESRGAN weights: {e}")

        return str(weights_path)

    def load_model(self) -> None:
        """Load Real-ESRGAN model onto GPU."""
        if self._loaded:
            logger.info("Real-ESRGAN already loaded, skipping")
            return

        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer

            weights_path = self._download_weights()

            # RRDBNet architecture for RealESRGAN_x4plus
            model = RRDBNet(
                num_in_ch=3,
                num_out_ch=3,
                num_feat=64,
                num_block=23,
                num_grow_ch=32,
                scale=4,
            )

            self.upsampler = RealESRGANer(
                scale=4,
                model_path=weights_path,
                model=model,
                tile=400,  # Tile size for large images (reduces VRAM)
                tile_pad=10,
                pre_pad=0,
                half=settings.DTYPE == "float16",
                device=settings.DEVICE,
            )

            self._loaded = True
            logger.info("✓ Real-ESRGAN loaded successfully on {}", settings.DEVICE)

        except ImportError as e:
            logger.warning(
                "Real-ESRGAN dependencies not installed: {}. "
                "Upscaling will be disabled.",
                e,
            )
            self._loaded = False
        except Exception as e:
            raise ModelLoadError(f"Failed to load Real-ESRGAN: {e}")

    def upscale(
        self,
        image: Image.Image,
        target_width: int | None = None,
        target_height: int | None = None,
    ) -> Image.Image:
        """
        Upscale an image using Real-ESRGAN (4×), then resize to target.

        Args:
            image: Input PIL Image.
            target_width: Final output width (default: 4K = 3840).
            target_height: Final output height (default: 4K = 2160).

        Returns:
            Upscaled PIL Image.
        """
        if not self._loaded:
            logger.warning("Real-ESRGAN not loaded, returning original image")
            return image

        tw = target_width or settings.MAX_OUTPUT_WIDTH
        th = target_height or settings.MAX_OUTPUT_HEIGHT

        try:
            # Convert PIL → OpenCV BGR
            img_array = np.array(image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            logger.info(
                "Upscaling image: {}x{} → 4× → target {}x{}",
                image.size[0], image.size[1], tw, th,
            )

            # Real-ESRGAN upscale (4×)
            output_bgr, _ = self.upsampler.enhance(img_bgr, outscale=4)

            # Convert back to RGB
            output_rgb = cv2.cvtColor(output_bgr, cv2.COLOR_BGR2RGB)
            result = Image.fromarray(output_rgb)

            # Resize to target dimensions (maintain aspect ratio)
            result = self._fit_to_target(result, tw, th)

            logger.info(
                "✓ Upscale complete: final={}x{}",
                result.size[0], result.size[1],
            )
            return result

        except torch.cuda.OutOfMemoryError:
            gc.collect()
            torch.cuda.empty_cache()
            logger.warning("GPU OOM during upscale, returning original size")
            return image
        except Exception as e:
            raise ImageProcessingError(f"Upscaling failed: {e}")

    @staticmethod
    def _fit_to_target(
        image: Image.Image, max_w: int, max_h: int
    ) -> Image.Image:
        """Resize to fit within max dimensions while keeping aspect ratio."""
        w, h = image.size
        if w <= max_w and h <= max_h:
            return image

        scale = min(max_w / w, max_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)

        # Round to even for video codec compatibility
        new_w = new_w - (new_w % 2)
        new_h = new_h - (new_h % 2)

        return image.resize((new_w, new_h), Image.Resampling.LANCZOS)

    def unload(self) -> None:
        """Free GPU memory."""
        if self.upsampler is not None:
            del self.upsampler
            self.upsampler = None
        self._loaded = False
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("Real-ESRGAN unloaded, GPU memory freed")
