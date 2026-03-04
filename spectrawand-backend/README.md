# SpectraWand Backend

AI-powered professional color grading API built with FastAPI.

Uses **Stable Diffusion XL + ControlNet** for structure-preserving color grading and **Real-ESRGAN** for 4K enhancement.

## Architecture

```
app/
├── main.py              # FastAPI entry point, lifespan, CORS
├── config.py            # Pydantic Settings (.env config)
├── api/
│   ├── router.py        # POST /grade, GET /health
│   └── schemas.py       # Request/Response models
├── core/
│   ├── pipeline.py      # Orchestrator: preprocess → grade → upscale
│   ├── sdxl.py          # SDXL + ControlNet Canny engine
│   ├── upscaler.py      # Real-ESRGAN 4K upscaler
│   └── preprocessor.py  # Canny edges, image resizing
├── services/
│   └── image_service.py # Image I/O (validate, base64 encode/decode)
└── utils/
    ├── logger.py        # Structured logging (Loguru)
    └── exceptions.py    # Custom exceptions + FastAPI handlers
```

## Requirements

- Python 3.11+
- NVIDIA GPU with ≥12GB VRAM (RTX 3080+ or A10G/A100)
- CUDA 12.1+

## Quick Start

### 1. Setup

```bash
cd spectrawand-backend

# Create venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env as needed
```

### 2. Run

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

> **Note:** Use `--workers 1` — GPU models are not fork-safe.

### 3. Docker

```bash
docker build -t spectrawand-backend .

docker run --gpus all -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  spectrawand-backend
```

## API Endpoints

### `POST /api/v1/grade`

AI color grading endpoint. Accepts multipart form data.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | ✅ | Image file (JPEG, PNG, WEBP, TIFF, BMP) |
| `prompt` | string | ✅ | Color grading description |
| `negative_prompt` | string | ❌ | What to avoid |
| `num_steps` | int | ❌ | Denoising steps (1-100, default: 30) |
| `guidance_scale` | float | ❌ | CFG scale (1-30, default: 7.5) |
| `controlnet_scale` | float | ❌ | Structure preservation (0-2, default: 0.55) |
| `strength` | float | ❌ | Change intensity (0.1-1.0, default: 0.60) |
| `upscale` | bool | ❌ | 4K upscale (default: true) |
| `seed` | int | ❌ | Reproducibility seed |
| `output_format` | string | ❌ | JPEG / PNG / WEBP (default: JPEG) |

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/v1/grade \
  -F "image=@photo.jpg" \
  -F "prompt=cinematic teal and orange, moody lighting" \
  -F "strength=0.6" \
  -F "upscale=true"
```

**Response:**
```json
{
  "success": true,
  "image_base64": "/9j/4AAQ...",
  "width": 3840,
  "height": 2160,
  "processing_time": 12.5,
  "prompt": "cinematic teal and orange, moody lighting",
  "parameters": { ... }
}
```

### `GET /api/v1/health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "models_loaded": true,
  "gpu": {
    "available": true,
    "device_name": "NVIDIA RTX 4090",
    "memory_allocated_gb": 8.2,
    "memory_total_gb": 24.0
  }
}
```

## Cloud Deployment

### RunPod / Lambda / Vast.ai

1. Use an image with CUDA 12.1 + Python 3.11
2. Mount a persistent volume at `/app/models` for cached model weights
3. First startup takes 5-10 min (downloads ~7GB of models)
4. Subsequent startups use cached weights

### AWS (EC2 G5 / SageMaker)

```bash
# G5 instances have A10G GPUs (24GB VRAM)
aws ec2 run-instances \
  --instance-type g5.xlarge \
  --image-id ami-xxx  # Deep Learning AMI
```

## Swagger Docs

Visit `http://localhost:8000/docs` for interactive API documentation.
