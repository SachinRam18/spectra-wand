"""
SDXL + ControlNet Color Grading Engine.

Uses StableDiffusionXLControlNetImg2ImgPipeline from diffusers
to perform AI-driven color grading while preserving image structure
via Canny ControlNet conditioning.
"""

import gc
import torch
from PIL import Image
from loguru import logger

from diffusers import (
    ControlNetModel,
    StableDiffusionXLControlNetPipeline,
    AutoencoderKL,
)
from diffusers.schedulers import DPMSolverMultistepScheduler

from app.config import settings
from app.utils.exceptions import ModelLoadError, GPUError


class SDXLColorGrader:
    """
    SDXL image-to-image pipeline with ControlNet Canny conditioning.

    The ControlNet preserves the structural composition of the input image
    while SDXL re-renders it according to the text prompt (color grade).
    """

    def __init__(self):
        self.pipe = None
        self._loaded = False

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load_models(self) -> None:
        """Load SDXL base + ControlNet Canny models onto GPU."""
        if self._loaded:
            logger.info("SDXL models already loaded, skipping")
            return

        try:
            logger.info("Loading ControlNet Canny model: {}", settings.CONTROLNET_MODEL_ID)
            controlnet = ControlNetModel.from_pretrained(
                settings.CONTROLNET_MODEL_ID,
                torch_dtype=settings.torch_dtype,
                cache_dir=settings.MODEL_CACHE_DIR,
            )

            logger.info("Loading SDXL base model: {}", settings.SDXL_MODEL_ID)

            # Load VAE separately for better quality
            vae = AutoencoderKL.from_pretrained(
                "madebyollin/sdxl-vae-fp16-fix",
                torch_dtype=settings.torch_dtype,
                cache_dir=settings.MODEL_CACHE_DIR,
            )

            self.pipe = StableDiffusionXLControlNetPipeline.from_pretrained(
                settings.SDXL_MODEL_ID,
                controlnet=controlnet,
                vae=vae,
                torch_dtype=settings.torch_dtype,
                cache_dir=settings.MODEL_CACHE_DIR,
                use_safetensors=True,
                variant="fp16",
            )

            # Scheduler — DPM++ 2M Karras for high quality with fewer steps
            self.pipe.scheduler = DPMSolverMultistepScheduler.from_config(
                self.pipe.scheduler.config,
                algorithm_type="dpmsolver++",
                use_karras_sigmas=True,
            )

            # GPU placement
            if settings.ENABLE_CPU_OFFLOAD:
                logger.info("Enabling sequential CPU offload for low-VRAM mode")
                self.pipe.enable_sequential_cpu_offload()
            else:
                self.pipe.to(settings.DEVICE)

            # Memory optimizations
            if settings.ENABLE_ATTENTION_SLICING:
                self.pipe.enable_attention_slicing()

            if settings.ENABLE_VAE_TILING:
                self.pipe.enable_vae_tiling()

            # Try to enable xFormers if available
            try:
                self.pipe.enable_xformers_memory_efficient_attention()
                logger.info("xFormers memory-efficient attention enabled")
            except Exception:
                logger.debug("xFormers not available, using default attention")

            self._loaded = True
            logger.info("✓ SDXL + ControlNet loaded successfully on {}", settings.DEVICE)

        except torch.cuda.OutOfMemoryError:
            raise GPUError("Not enough GPU memory to load SDXL models. Need ≥12GB VRAM.")
        except Exception as e:
            raise ModelLoadError(f"Failed to load SDXL models: {e}")

    def grade(
        self,
        image: Image.Image,
        control_image: Image.Image,
        prompt: str,
        negative_prompt: str | None = None,
        num_steps: int | None = None,
        guidance_scale: float | None = None,
        controlnet_scale: float | None = None,
        strength: float | None = None,
        seed: int | None = None,
    ) -> Image.Image:
        """
        Run color grading inference.

        Args:
            image: Original image (resized for inference).
            control_image: Canny edge map for structure preservation.
            prompt: Color grading description (e.g., "cinematic teal and orange").
            negative_prompt: Things to avoid in output.
            num_steps: Number of denoising steps.
            guidance_scale: Classifier-free guidance strength.
            controlnet_scale: How strongly ControlNet guides the output.
            strength: img2img denoising strength (lower = more faithful to original).
            seed: Random seed for reproducibility.

        Returns:
            Graded PIL Image.
        """
        if not self._loaded:
            raise ModelLoadError("Models not loaded. Call load_models() first.")

        # Apply defaults
        steps = num_steps or settings.DEFAULT_NUM_STEPS
        guidance = guidance_scale or settings.DEFAULT_GUIDANCE_SCALE
        cn_scale = controlnet_scale or settings.DEFAULT_CONTROLNET_SCALE
        img_strength = strength or settings.DEFAULT_STRENGTH

        neg_prompt = negative_prompt or (
            "blurry, artifacts, distorted, watermark, text, deformed, "
            "different composition, changed face, altered structure, "
            "different person, added objects, removed objects"
        )

        # Enhance the prompt for COLOR GRADING only — avoid image-quality
        # terms like 'sharp focus, 8k' which bias SDXL toward regeneration
        enhanced_prompt = (
            f"color graded, {prompt}, cinematic color palette, "
            "professional color correction, film color tones"
        )

        # Generator for reproducibility
        generator = None
        if seed is not None:
            generator = torch.Generator(device=settings.DEVICE).manual_seed(seed)

        logger.info(
            "Running SDXL inference: steps={}, guidance={}, cn_scale={}, strength={}, seed={}",
            steps, guidance, cn_scale, img_strength, seed,
        )

        try:
            with torch.inference_mode():
                result = self.pipe(
                    prompt=enhanced_prompt,
                    negative_prompt=neg_prompt,
                    image=control_image,
                    num_inference_steps=steps,
                    guidance_scale=guidance,
                    controlnet_conditioning_scale=cn_scale,
                    generator=generator,
                ).images[0]

            logger.info("✓ SDXL inference complete: output={}x{}", result.size[0], result.size[1])
            return result

        except torch.cuda.OutOfMemoryError:
            # Try to recover GPU memory
            gc.collect()
            torch.cuda.empty_cache()
            raise GPUError(
                "GPU out of memory during inference. "
                "Try reducing image size or inference steps."
            )
        except Exception as e:
            raise GPUError(f"SDXL inference failed: {e}")

    def unload(self) -> None:
        """Free GPU memory."""
        if self.pipe is not None:
            del self.pipe
            self.pipe = None
        self._loaded = False
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("SDXL models unloaded, GPU memory freed")
