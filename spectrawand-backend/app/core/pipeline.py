"""
Grading Pipeline Orchestrator.

Coordinates the full flow: preprocess → SDXL+ControlNet → Real-ESRGAN → output.
Thread-safe for async FastAPI execution.
"""

import asyncio
import time

import torch
from PIL import Image
from loguru import logger

from app.config import settings
from app.core.preprocessor import prepare_control_image
from app.core.sdxl import SDXLColorGrader
from app.core.upscaler import RealESRGANUpscaler
from app.utils.exceptions import ModelLoadError


class GradingPipeline:
    """
    Main orchestrator — singleton that manages all AI models
    and runs the full color grading pipeline.
    """

    def __init__(self):
        self.grader = SDXLColorGrader()
        self.upscaler = RealESRGANUpscaler()
        self._initialized = False

    @property
    def is_ready(self) -> bool:
        return self._initialized and self.grader.is_loaded

    async def initialize(self) -> None:
        """Load all models on startup (runs in thread to not block event loop)."""
        logger.info("Initializing Grading Pipeline...")
        start = time.perf_counter()

        try:
            # Load models in a background thread (heavy I/O + GPU)
            await asyncio.to_thread(self._load_all_models)

            elapsed = time.perf_counter() - start
            logger.info("✓ Pipeline initialized in {:.1f}s", elapsed)
            self._initialized = True

        except Exception as e:
            logger.error("Pipeline initialization failed: {}", e)
            raise ModelLoadError(f"Pipeline initialization failed: {e}")

    def _load_all_models(self) -> None:
        """Synchronous model loading (called from thread)."""
        settings.ensure_dirs()
        self.grader.load_models()

        try:
            self.upscaler.load_model()
        except Exception as e:
            logger.warning(
                "Real-ESRGAN failed to load: {}. Upscaling will be disabled.", e,
            )

    async def process(
        self,
        image: Image.Image,
        prompt: str,
        negative_prompt: str | None = None,
        num_steps: int | None = None,
        guidance_scale: float | None = None,
        controlnet_scale: float | None = None,
        strength: float | None = None,
        upscale: bool | None = None,
        seed: int | None = None,
    ) -> dict:
        """
        Run the full color grading pipeline.

        Args:
            image: Original uploaded PIL Image.
            prompt: Color grading description.
            negative_prompt: Things to avoid.
            num_steps: Denoising steps.
            guidance_scale: CFG scale.
            controlnet_scale: ControlNet conditioning strength.
            strength: img2img strength.
            upscale: Whether to apply Real-ESRGAN 4K upscale.
            seed: Random seed.

        Returns:
            dict with 'image', 'width', 'height', 'processing_time'.
        """
        if not self.is_ready:
            raise ModelLoadError("Pipeline not initialized. Models not loaded.")

        should_upscale = upscale if upscale is not None else settings.DEFAULT_UPSCALE
        start = time.perf_counter()

        # Run the heavy computation in a thread
        result = await asyncio.to_thread(
            self._process_sync,
            image=image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            controlnet_scale=controlnet_scale,
            strength=strength,
            should_upscale=should_upscale,
            seed=seed,
        )

        elapsed = time.perf_counter() - start

        return {
            "image": result,
            "width": result.size[0],
            "height": result.size[1],
            "processing_time": round(elapsed, 2),
        }

    def _process_sync(
        self,
        image: Image.Image,
        prompt: str,
        negative_prompt: str | None,
        num_steps: int | None,
        guidance_scale: float | None,
        controlnet_scale: float | None,
        strength: float | None,
        should_upscale: bool,
        seed: int | None,
    ) -> Image.Image:
        """Synchronous pipeline execution (runs in thread)."""

        original_size = image.size
        logger.info(
            "Pipeline started: prompt='{}', original={}x{}, upscale={}",
            prompt[:60], original_size[0], original_size[1], should_upscale,
        )

        # ── Step 1: Preprocess ──────────────────────────────────────────
        logger.info("Step 1/3: Preprocessing (resize + Canny edge extraction)")
        resized_image, control_image = prepare_control_image(image)

        # ── Step 2: SDXL + ControlNet inference ─────────────────────────
        logger.info("Step 2/3: SDXL + ControlNet color grading")
        graded = self.grader.grade(
            image=resized_image,
            control_image=control_image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_steps=num_steps,
            guidance_scale=guidance_scale,
            controlnet_scale=controlnet_scale,
            strength=strength,
            seed=seed,
        )

        # ── Step 3: Upscale (optional) ──────────────────────────────────
        if should_upscale and self.upscaler.is_loaded:
            logger.info("Step 3/3: Real-ESRGAN 4K upscaling")
            final = self.upscaler.upscale(graded)
        else:
            logger.info("Step 3/3: Skipping upscale")
            # At least resize back to original dimensions
            final = graded.resize(original_size, Image.Resampling.LANCZOS)

        logger.info("✓ Pipeline complete: output={}x{}", final.size[0], final.size[1])
        return final

    async def shutdown(self) -> None:
        """Cleanup all models and free GPU memory."""
        logger.info("Shutting down pipeline...")
        await asyncio.to_thread(self._shutdown_sync)

    def _shutdown_sync(self) -> None:
        self.grader.unload()
        self.upscaler.unload()
        self._initialized = False
        logger.info("✓ Pipeline shutdown complete")

    def get_gpu_info(self) -> dict:
        """Get GPU status information."""
        info = {"available": torch.cuda.is_available()}
        if torch.cuda.is_available():
            info.update({
                "device_name": torch.cuda.get_device_name(0),
                "memory_allocated_gb": round(
                    torch.cuda.memory_allocated(0) / 1024**3, 2
                ),
                "memory_reserved_gb": round(
                    torch.cuda.memory_reserved(0) / 1024**3, 2
                ),
                "memory_total_gb": round(
                    torch.cuda.get_device_properties(0).total_mem / 1024**3, 2
                ),
            })
        return info


# ── Singleton instance ──────────────────────────────────────────────────
pipeline = GradingPipeline()
