# Watermark Removal Backend API

Production-grade FastAPI backend for multi-method watermark removal with automatic detection.

## Features

- Multi-method watermark detection (FFT, edges, color contrast, alpha channel)
- 5 removal methods:
  1. OpenCV Inpainting (Fast)
  2. Lama Cleaner AI (Best Quality)
  3. Frequency + Exemplar Hybrid (Custom)
  4. Stable Diffusion Inpainting (Highest Quality)
  5. DeepFill v2 (GAN-based, stub)

- Quality metrics (BRISQUE, SSIM, sharpness, contrast)
- Lazy model loading for faster startup
- Async endpoints for concurrent processing
- Comprehensive error handling

## Setup

### 1. Create Python Environment

Using Conda (recommended for scientific packages):
```bash
conda create -n watermark_env python=3.12
conda activate watermark_env
```

Using venv:
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy and customize the configuration:
```bash
cp .env.example .env
```

Edit `.env` to adjust:
- `DEVICE=cuda` if you have NVIDIA GPU
- `MAX_IMAGE_SIZE_MB` for upload limits
- `PORT` for server port

### 4. Run Server

Development mode (with auto-reload):
```bash
python -m app.main
```

Or directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode (no reload):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Health Check
```
GET /health
```

Returns available methods and status.

### Detect Watermark
```
POST /api/detect
```

Upload image for watermark detection. Returns:
- Detection confidence (0.0-1.0)
- Detected regions (bounding boxes)
- Method breakdown scores

### Remove Watermark
```
POST /api/remove
```

Remove watermark using specified method. Accepts:
- Image file
- Watermark mask file
- Method selection (opencv, lama, frequency, stable_diffusion, deepfill)
- Quality slider (for Stable Diffusion: 20-50 steps)

Returns:
- Processed image
- Quality metrics (BRISQUE, SSIM)
- Processing time

### List Methods
```
GET /api/methods
```

Returns available removal methods with:
- Speed rating (fast/medium/slow)
- Quality rating
- Availability status

## Project Structure

```
backend/
├── app/
│   ├── models/              # Removal method implementations
│   │   ├── base.py          # Base class for all methods
│   │   ├── opencv.py        # OpenCV inpainting
│   │   ├── lama.py          # Lama Cleaner (optional)
│   │   ├── frequency.py     # FFT + PatchMatch hybrid
│   │   ├── stable_diffusion.py  # Diffusers integration
│   │   └── deepfill.py      # DeepFill stub
│   │
│   ├── utils/               # Utility modules
│   │   ├── detector.py      # Multi-method watermark detection
│   │   ├── quality.py       # Quality metrics (BRISQUE, SSIM)
│   │   └── image_processor.py   # Image I/O utilities
│   │
│   ├── config.py            # Configuration (Pydantic settings)
│   ├── main.py              # FastAPI application
│   └── __init__.py
│
├── requirements.txt         # Python dependencies (pinned versions)
├── .env.example             # Environment template
└── README.md
```

## Key Technologies

- FastAPI: Async web framework
- OpenCV: Computer vision (inpainting, detection)
- PyTorch: Deep learning inference
- Lama Cleaner: Deep learning inpainting (optional)
- Diffusers: Stable Diffusion integration
- BRISQUE: Image quality assessment
- NumPy/SciPy: Scientific computing

## Development Notes

### Device Management
- CPU: Safe, slow for deep learning
- CUDA: ~3-5x faster (requires NVIDIA GPU + CUDA toolkit)
- Set via `.env`: `DEVICE=cuda` or `DEVICE=cpu`

### Model Loading
Models load on-demand (lazy loading):
1. First request to a method triggers model download/initialization
2. Subsequent requests reuse cached model
3. This trades startup time for first-request latency

### Error Handling
All endpoints return meaningful error messages:
- Invalid image format → 400 Bad Request
- Missing dependencies → Graceful fallback
- Processing timeout → 504 Gateway Timeout

### Performance Tips
1. Use OpenCV for quick previews (< 500ms)
2. Use Lama for production (1-3 seconds)
3. Use Stable Diffusion only for final output (30-60 seconds)
4. Enable GPU if available (10-20x speedup)
5. Batch multiple images for throughput

## Extending the System

### Add New Removal Method

1. Create new file in `app/models/`:
```python
from .base import RemovalMethod

class MyMethod(RemovalMethod):
    name = "My Method"
    
    def remove(self, image, mask):
        # Implementation
        return result, metadata
```

2. Register in `app/main.py` `get_removal_model()` function
3. Update config `MODELS_AVAILABLE` dict

### Add New Detection Strategy

1. Add method to `WatermarkDetector` class in `app/utils/detector.py`
2. Update `detect()` to include new method
3. Adjust mask combination weights

## Troubleshooting

### Lama Cleaner not loading
- Check Python version: needs 3.12 (imghdr removed in 3.13)
- Verify conda environment active
- Run: `python -c "import lama_cleaner"`

### Out of memory on GPU
- Reduce MAX_IMAGE_SIZE_MB in config
- Enable CPU mode: `DEVICE=cpu`
- Use OpenCV instead of deep learning methods

### Slow on CPU
- This is expected (50-100x slower than GPU)
- Use OpenCV method or enable GPU

## Always check the correctness of AI-generated responses.
