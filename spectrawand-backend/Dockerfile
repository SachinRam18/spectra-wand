# ═══════════════════════════════════════════════════════════════
# SpectraWand Backend — Dockerfile
# Multi-stage build with NVIDIA CUDA for GPU inference
# ═══════════════════════════════════════════════════════════════

FROM nvidia/cuda:12.1.1-devel-ubuntu22.04 AS base

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install Python 3.11 + system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

WORKDIR /app

# ── Install dependencies ────────────────────────────────────────
COPY requirements.txt .

# Install PyTorch with CUDA 12.1 first
RUN pip install --no-cache-dir \
    torch torchvision \
    --index-url https://download.pytorch.org/whl/cu121

# Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ───────────────────────────────────────
COPY app/ app/

# ── Create directories ──────────────────────────────────────────
RUN mkdir -p tmp/uploads tmp/outputs models logs

# ── Expose port ─────────────────────────────────────────────────
EXPOSE 8000

# ── Health check ────────────────────────────────────────────────
HEALTHCHECK --interval=60s --timeout=30s --start-period=300s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# ── Run ─────────────────────────────────────────────────────────
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
