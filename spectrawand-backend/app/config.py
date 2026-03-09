"""
SpectraWand Configuration — Pydantic Settings with .env support.

All model paths, GPU settings, and server config are centralized here.
"""

from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # ── Server ──────────────────────────────────────────────────────────
    APP_NAME: str = "SpectraWand"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "https://unnecessary-timika-supersecretively.ngrok-free.dev",
    ]

    # ── Directories ─────────────────────────────────────────────────────
    UPLOAD_DIR: str = "tmp/uploads"
    OUTPUT_DIR: str = "tmp/outputs"
    MODEL_CACHE_DIR: str = "models"

    # ── Model IDs (Hugging Face) ────────────────────────────────────────
    SDXL_MODEL_ID: str = "stabilityai/stable-diffusion-xl-base-1.0"
    CONTROLNET_MODEL_ID: str = "diffusers/controlnet-canny-sdxl-1.0"
    REALESRGAN_MODEL_NAME: str = "RealESRGAN_x4plus"
    REALESRGAN_WEIGHTS_URL: str = (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/"
        "v0.1.0/RealESRGAN_x4plus.pth"
    )

    # ── GPU / Inference ─────────────────────────────────────────────────
    DEVICE: str = "cuda"
    DTYPE: str = "float16"  # float16 | bfloat16 | float32
    ENABLE_CPU_OFFLOAD: bool =  True  # Use sequential CPU offload for low-VRAM
    ENABLE_ATTENTION_SLICING: bool = True
    ENABLE_VAE_TILING: bool = True

    # ── Inference Defaults ──────────────────────────────────────────────
    DEFAULT_NUM_STEPS: int = 25
    DEFAULT_GUIDANCE_SCALE: float = 5.0
    DEFAULT_CONTROLNET_SCALE: float = 0.85
    DEFAULT_STRENGTH: float = 0.20  # img2img strength (low = color-only, high = re-draws)
    DEFAULT_UPSCALE: bool = True
    MAX_OUTPUT_WIDTH: int = 3840  # 4K
    MAX_OUTPUT_HEIGHT: int = 2160

    # ── Limits ──────────────────────────────────────────────────────────
    MAX_UPLOAD_SIZE_MB: int = 20
    MAX_IMAGE_DIMENSION: int = 8192
    INFERENCE_RESOLUTION: int = 1024  # SDXL native resolution

    # ── Canny Edge Detection ────────────────────────────────────────────
    CANNY_LOW_THRESHOLD: int = 100
    CANNY_HIGH_THRESHOLD: int = 200

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def torch_dtype(self):
        import torch
        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }
        return dtype_map.get(self.DTYPE, torch.float16)

    def ensure_dirs(self):
        """Create required directories."""
        for d in [self.UPLOAD_DIR, self.OUTPUT_DIR, self.MODEL_CACHE_DIR]:
            Path(d).mkdir(parents=True, exist_ok=True)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
