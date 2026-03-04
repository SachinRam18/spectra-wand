"""
Pydantic schemas for API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional


class GradeResponse(BaseModel):
    """Response from the /grade endpoint."""
    success: bool = True
    image_base64: str = Field(..., description="Base64-encoded JPEG image")
    width: int = Field(..., description="Output image width in pixels")
    height: int = Field(..., description="Output image height in pixels")
    processing_time: float = Field(..., description="Total processing time in seconds")
    prompt: str = Field(..., description="Prompt used for grading")
    parameters: dict = Field(default_factory=dict, description="Inference parameters used")


class HealthResponse(BaseModel):
    """Response from the /health endpoint."""
    status: str = "ok"
    version: str
    models_loaded: bool
    gpu: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    type: str
