"""
FastAPI application for watermark removal service.
Main entry point for the backend.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
import io
import cv2
import numpy as np
from pathlib import Path
import asyncio
from datetime import datetime

from app.config import settings
from app.utils.detector import WatermarkDetector
from app.models.opencv import OpenCVRemoval
from app.models.lama import LamaRemoval
from app.models.deepfill import DeepFillRemoval
from app.models.stable_diffusion import StableDiffusionRemoval
from app.models.frequency import FrequencyRemoval
from app.utils.quality import QualityMetrics


# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="Watermark removal API with multiple AI methods",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Models for request/response
class DetectionResult(BaseModel):
    """Response model for detection endpoint."""
    success: bool
    confidence: float
    methods_used: int
    regions: List[Dict]
    watermark_detected: bool
    message: str


class RemovalRequest(BaseModel):
    """Request model for removal endpoint."""
    method: str
    quality_steps: Optional[int] = 50  # For Stable Diffusion


class RemovalResult(BaseModel):
    """Response model for removal endpoint."""
    success: bool
    method: str
    processing_time: float
    quality_metrics: Dict
    message: str


# Global model instances (lazy loaded)
_detector: Optional[WatermarkDetector] = None
_removal_models: Dict = {}
_metrics_computer = QualityMetrics()


async def get_detector() -> WatermarkDetector:
    """Get or initialize detector."""
    global _detector
    if _detector is None:
        _detector = WatermarkDetector()
    return _detector


async def get_removal_model(method: str):
    """Get or initialize removal model."""
    global _removal_models
    
    if method not in _removal_models:
        try:
            if method == "opencv":
                _removal_models[method] = OpenCVRemoval(device=settings.DEVICE)
            elif method == "lama":
                _removal_models[method] = LamaRemoval(device=settings.DEVICE)
            elif method == "deepfill":
                _removal_models[method] = DeepFillRemoval(device=settings.DEVICE)
            elif method == "stable_diffusion":
                _removal_models[method] = StableDiffusionRemoval(device=settings.DEVICE)
            elif method == "frequency":
                _removal_models[method] = FrequencyRemoval(device=settings.DEVICE)
            else:
                raise ValueError(f"Unknown removal method: {method}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load model: {str(e)}")
    
    return _removal_models[method]


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "available_methods": settings.MODELS_AVAILABLE
    }


# Detection endpoint
@app.post("/api/detect", response_model=DetectionResult)
async def detect_watermark(file: UploadFile = File(...)):
    """
    Detect watermark in image using multi-method approach.
    
    Args:
        file: Image file (JPG, PNG, WEBP)
        
    Returns:
        Detection results with mask and regions
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        # Check image size
        image_size_mb = image.nbytes / (1024 * 1024)
        if image_size_mb > settings.MAX_IMAGE_SIZE_MB:
            raise ValueError(f"Image too large: {image_size_mb}MB > {settings.MAX_IMAGE_SIZE_MB}MB")
        
        # Detect watermark
        detector = await get_detector()
        
        # Check for alpha channel (PNG)
        alpha = None
        if file.filename.lower().endswith('.png'):
            image_rgba = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
            if image_rgba.shape[2] == 4:
                alpha = image_rgba[:, :, 3]
        
        mask, detection_results = detector.detect(image, alpha)
        
        # Return results
        watermark_detected = detection_results['confidence'] > 0.1
        
        return DetectionResult(
            success=True,
            confidence=detection_results['confidence'],
            methods_used=detection_results['detection_methods_used'],
            regions=detection_results['regions'],
            watermark_detected=watermark_detected,
            message="Watermark detection completed" if watermark_detected else "No watermark detected"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Removal endpoint
@app.post("/api/remove", response_model=RemovalResult)
async def remove_watermark(
    file: UploadFile = File(...),
    mask_file: UploadFile = File(...),
    method: str = "opencv",
    quality_steps: Optional[int] = 50
):
    """
    Remove watermark from image using specified method.
    
    Args:
        file: Image file
        mask_file: Watermark mask file
        method: Removal method (opencv, lama, frequency, stable_diffusion, deepfill)
        quality_steps: Quality steps for Stable Diffusion (20-50)
        
    Returns:
        Removal results with quality metrics
    """
    try:
        # Validate method
        if method not in settings.MODELS_AVAILABLE:
            raise ValueError(f"Unknown removal method: {method}")
        
        # Read images
        image_contents = await file.read()
        image_nparr = np.frombuffer(image_contents, np.uint8)
        image = cv2.imdecode(image_nparr, cv2.IMREAD_COLOR)
        
        mask_contents = await mask_file.read()
        mask_nparr = np.frombuffer(mask_contents, np.uint8)
        mask = cv2.imdecode(mask_nparr, cv2.IMREAD_GRAYSCALE)
        
        if image is None or mask is None:
            raise ValueError("Failed to decode images")
        
        # Ensure mask matches image size
        if mask.shape[:2] != image.shape[:2]:
            mask = cv2.resize(mask, (image.shape[1], image.shape[0]))
        
        # Get removal model
        removal_model = await get_removal_model(method)
        
        # Record start time
        import time
        start_time = time.time()
        
        # Apply removal
        if method == "stable_diffusion":
            result, metadata = removal_model.remove(image, mask, quality_steps)
        else:
            result, metadata = removal_model.remove(image, mask)
        
        processing_time = time.time() - start_time
        
        # Compute quality metrics
        quality_metrics = _metrics_computer.compute_all_metrics(image, result, mask)
        
        return RemovalResult(
            success=True,
            method=method,
            processing_time=processing_time,
            quality_metrics=quality_metrics,
            message=f"Watermark removed successfully using {method}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Methods endpoint
@app.get("/api/methods")
async def get_available_methods():
    """Get list of available removal methods and their status."""
    methods = []
    
    method_configs = {
        "opencv": {
            "name": "OpenCV Inpainting (Fast)",
            "description": "Quick inpainting - good for simple watermarks",
            "speed": "fast",
            "quality": "medium",
        },
        "lama": {
            "name": "Lama Cleaner AI (Best Quality)",
            "description": "Deep learning inpainting - highest quality",
            "speed": "slow",
            "quality": "high",
        },
        "frequency": {
            "name": "Frequency + Exemplar Hybrid",
            "description": "FFT + PatchMatch - good for repeating patterns",
            "speed": "medium",
            "quality": "medium-high",
        },
        "stable_diffusion": {
            "name": "Stable Diffusion Inpainting",
            "description": "Generative inpainting - very high quality but very slow",
            "speed": "very_slow",
            "quality": "very_high",
        },
        "deepfill": {
            "name": "DeepFill v2 (GAN-based)",
            "description": "Advanced GAN inpainting - requires model weights",
            "speed": "slow",
            "quality": "high",
        },
    }
    
    for method_name, available in settings.MODELS_AVAILABLE.items():
        if method_name in method_configs:
            method_config = method_configs[method_name]
            methods.append({
                "id": method_name,
                "name": method_config["name"],
                "description": method_config["description"],
                "available": available,
                "speed": method_config["speed"],
                "quality": method_config["quality"],
            })
    
    return {"methods": methods}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize models on startup."""
    print("Initializing watermark removal service...")
    
    # Try to initialize optional models
    try:
        await get_removal_model("opencv")
        print("✓ OpenCV inpainting loaded")
    except Exception as e:
        print(f"✗ OpenCV failed: {e}")
    
    try:
        await get_removal_model("lama")
        print("✓ Lama Cleaner loaded")
        settings.MODELS_AVAILABLE["lama"] = True
    except Exception as e:
        print(f"✗ Lama Cleaner failed: {e}")
    
    try:
        await get_removal_model("frequency")
        print("✓ Frequency hybrid method loaded")
    except Exception as e:
        print(f"✗ Frequency method failed: {e}")
    
    print("Service initialization complete!")


# Run application
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
