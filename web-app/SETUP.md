# Watermark Removal - Complete Setup Guide

## Current Status

Backend API is fully operational and tested. Ready for frontend development.

## Quick Start

### Prerequisites
- Python 3.12 (via conda)
- macOS with ARM64 (Apple Silicon)
- All dependencies installed

### Start the Backend Server

From the web-app directory:
```bash
cd /Users/devisri/Desktop/Research/Projects/Watermark/web-app

# Option 1: Using the startup script
/opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python start_server.py

# Option 2: Direct command
cd backend && /opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python -m app.main

# Option 3: With custom config
DEVICE=cpu PORT=8000 /opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python start_server.py
```

Server runs on: **http://localhost:8000**

### API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Test Backend

```bash
cd /Users/devisri/Desktop/Research/Projects/Watermark/web-app
/opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python scripts/test_backend.py
```

## API Endpoints Summary

### GET /health
Returns server status and available methods.
```bash
curl http://localhost:8000/health
```

### GET /api/methods
Lists all removal methods with details.
```bash
curl http://localhost:8000/api/methods
```

### POST /api/detect
Detect watermark in image.
```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@image.jpg"
```

Response includes:
- Detection confidence (0.0-1.0)
- Detected regions (bounding boxes)
- Individual method scores (FFT, edges, color, alpha)

### POST /api/remove
Remove watermark using specified method.
```bash
curl -X POST http://localhost:8000/api/remove \
  -F "file=@image.jpg" \
  -F "mask_file=@mask.jpg" \
  -F "method=opencv" \
  -F "quality_steps=50"
```

Available methods:
- `opencv` - Fast (medium quality)
- `lama` - Slow (high quality)
- `frequency` - Medium (medium-high quality)
- `stable_diffusion` - Very slow (highest quality) [optional]
- `deepfill` - Slow (high quality) [optional]

## Available Removal Methods

| Method | Speed | Quality | Status |
|--------|-------|---------|--------|
| OpenCV Inpainting | Fast (< 500ms) | Medium | Always Available |
| Lama Cleaner | Slow (1-3s) | High | Available ✓ |
| Frequency Hybrid | Medium (500ms-1s) | Medium-High | Available ✓ |
| Stable Diffusion | Very Slow (30-60s) | Very High | Optional |
| DeepFill v2 | Slow (3-5s) | High | Optional |

## Environment Variables

Configure via `.env` or environment:

```bash
# API Settings
API_TITLE=Watermark Removal API
API_VERSION=1.0.0
API_PREFIX=/api

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=True
DEBUG=False

# Processing
DEVICE=cpu          # or 'cuda' for GPU
MAX_IMAGE_SIZE_MB=20
OUTPUT_QUALITY=95
PROCESSING_TIMEOUT_SECONDS=300
```

## Installation Troubleshooting

### Issue: ModuleNotFoundError
Make sure to use the conda Python:
```bash
/opt/homebrew/Caskroom/miniconda/base/envs/watermark_env/bin/python
```

### Issue: Import errors with app module
The scripts add the backend directory to sys.path automatically.
Run from the `web-app` directory.

### Issue: Lama Cleaner not loading
Lama Cleaner requires Python 3.12. The system has Python 3.12 via conda.
The model will load on first use (may take 30-60 seconds).

### Issue: Out of memory
For GPU:
- Reduce MAX_IMAGE_SIZE_MB in config
- Use CPU instead: `DEVICE=cpu`
- Use OpenCV method instead of deep learning

## Project Structure

```
web-app/
├── backend/
│   ├── app/
│   │   ├── models/          # 5 removal method implementations
│   │   ├── utils/           # Detection, quality, processing
│   │   ├── config.py        # Configuration
│   │   ├── main.py          # FastAPI application
│   │   └── __init__.py
│   ├── requirements.txt      # All dependencies (25 packages)
│   ├── requirements-pip.txt  # Pip-only dependencies
│   ├── .env.example          # Config template
│   ├── README.md             # Detailed docs
│   └── __init__.py
│
├── frontend/
│   └── src/                  # React components (to be built)
│
├── scripts/
│   ├── test_backend.py       # Backend test suite
│   └── download_models.py    # Model downloader
│
└── start_server.py           # Server startup script
```

## Next Steps: Frontend Development

The backend is production-ready. Next phase is building React frontend:

1. **React Project Setup**
   - Create React app with TypeScript
   - Configure Tailwind CSS
   - Set up API client (axios/fetch)

2. **Key Components**
   - ImageUpload (drag-drop)
   - WatermarkDetector (detection display)
   - MethodSelector (5 buttons)
   - BeforeAfterView (comparison slider)
   - QualityDisplay (BRISQUE score)

3. **Features**
   - Auto-detect watermarks on upload
   - Real-time method comparison
   - Progress indicators
   - Error handling
   - Dark mode support

4. **Integration**
   - Connect to /api/detect endpoint
   - Connect to /api/remove endpoint
   - Cache results
   - Handle file uploads

## Always check the correctness of AI-generated responses.
