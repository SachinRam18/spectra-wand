"""
API Router — SpectraWand endpoints.

POST /api/v1/grade  — Upload image + prompt → get graded image
GET  /api/v1/health — Service health check
"""

import time

from fastapi import APIRouter, File, Form, UploadFile, Query
from loguru import logger

from app.api.schemas import GradeResponse, HealthResponse
from app.config import settings
from app.core.pipeline import pipeline
from app.services.image_service import decode_upload, encode_response
from app.utils.exceptions import ImageValidationError


router = APIRouter(prefix="/api/v1", tags=["SpectraWand"])


@router.post(
    "/grade",
    response_model=GradeResponse,
    summary="AI Color Grading",
    description="Upload an image with a text prompt to apply AI-driven color grading.",
)
async def grade_image(
    image: UploadFile = File(..., description="Image file (JPEG, PNG, WEBP, TIFF, BMP)"),
    prompt: str = Form(..., description="Color grading description"),
    negative_prompt: str = Form(None, description="What to avoid in the output"),
    num_steps: int = Form(None, ge=1, le=100, description="Denoising steps (1-100)"),
    guidance_scale: float = Form(None, ge=1.0, le=30.0, description="CFG scale (1-30)"),
    controlnet_scale: float = Form(None, ge=0.0, le=2.0, description="ControlNet strength (0-2)"),
    strength: float = Form(None, ge=0.1, le=1.0, description="img2img strength (0.1-1.0)"),
    upscale: bool = Form(None, description="Apply Real-ESRGAN 4K upscale"),
    seed: int = Form(None, description="Random seed for reproducibility"),
    output_format: str = Form("JPEG", description="Output format: JPEG, PNG, WEBP"),
    quality: int = Form(92, ge=1, le=100, description="JPEG/WEBP quality (1-100)"),
):
    """
    Main color grading endpoint.

    Accepts a multipart form with an image file and grading parameters.
    Returns a base64-encoded processed image.
    """
    request_start = time.perf_counter()

    # Validate prompt
    prompt = prompt.strip()
    if not prompt:
        raise ImageValidationError("Prompt cannot be empty")
    if len(prompt) > 1000:
        raise ImageValidationError("Prompt too long (max 1000 characters)")

    # Validate output format
    output_format = output_format.upper()
    if output_format not in ("JPEG", "PNG", "WEBP"):
        raise ImageValidationError("Output format must be JPEG, PNG, or WEBP")

    logger.info(
        "Grade request: prompt='{}', format={}, upscale={}",
        prompt[:60], output_format, upscale,
    )

    # Decode and validate the uploaded image
    pil_image = await decode_upload(image)

    # Run the pipeline
    result = await pipeline.process(
        image=pil_image,
        prompt=prompt,
        negative_prompt=negative_prompt,
        num_steps=num_steps,
        guidance_scale=guidance_scale,
        controlnet_scale=controlnet_scale,
        strength=strength,
        upscale=upscale,
        seed=seed,
    )

    # Encode result to base64
    image_b64 = encode_response(
        result["image"],
        quality=quality,
        format=output_format,
    )

    total_time = round(time.perf_counter() - request_start, 2)

    logger.info(
        "✓ Grade complete: {}x{} in {:.1f}s",
        result["width"], result["height"], total_time,
    )

    return GradeResponse(
        image_base64=image_b64,
        width=result["width"],
        height=result["height"],
        processing_time=total_time,
        prompt=prompt,
        parameters={
            "num_steps": num_steps or settings.DEFAULT_NUM_STEPS,
            "guidance_scale": guidance_scale or settings.DEFAULT_GUIDANCE_SCALE,
            "controlnet_scale": controlnet_scale or settings.DEFAULT_CONTROLNET_SCALE,
            "strength": strength or settings.DEFAULT_STRENGTH,
            "upscale": upscale if upscale is not None else settings.DEFAULT_UPSCALE,
            "seed": seed,
            "output_format": output_format,
        },
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check service health, GPU status, and model loading state.",
)
async def health_check():
    """Service health endpoint."""
    return HealthResponse(
        status="ok" if pipeline.is_ready else "loading",
        version=settings.APP_VERSION,
        models_loaded=pipeline.is_ready,
        gpu=pipeline.get_gpu_info(),
    )
