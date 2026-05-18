#!/usr/bin/env python3
"""
Download and cache models for watermark removal backend.
Run this once to pre-download models for faster inference.
"""

import sys
import os
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings


def download_lama_model():
    """Download Lama Cleaner model."""
    print("Downloading Lama Cleaner model...")
    try:
        from lama_cleaner.model_manager import ModelManager
        
        # Initialize model manager (triggers download)
        model = ModelManager(
            name="lama",
            device=settings.DEVICE,
            disable_nsfw=True,
        )
        
        print("Lama Cleaner model downloaded successfully!")
        return True
    except ImportError:
        print("ERROR: lama-cleaner not installed. Install with:")
        print("  pip install lama-cleaner")
        return False
    except Exception as e:
        print(f"ERROR downloading Lama model: {e}")
        return False


def download_stable_diffusion_model():
    """Download Stable Diffusion inpainting model."""
    print("\nDownloading Stable Diffusion inpainting model...")
    print("WARNING: This is a large model (~7GB). Make sure you have enough disk space.")
    
    try:
        from diffusers import StableDiffusionInpaintPipeline
        import torch
        
        model_id = "runwayml/stable-diffusion-inpainting"
        print(f"Downloading {model_id}...")
        
        pipeline = StableDiffusionInpaintPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32 if settings.DEVICE == "cpu" else torch.float16,
        )
        
        print("Stable Diffusion model downloaded successfully!")
        return True
    except ImportError:
        print("ERROR: diffusers or torch not installed. Install with:")
        print("  pip install diffusers torch")
        return False
    except Exception as e:
        print(f"ERROR downloading Stable Diffusion model: {e}")
        return False


def create_models_directory():
    """Create models directory for cached weights."""
    models_dir = settings.MODELS_DIR
    models_dir.mkdir(parents=True, exist_ok=True)
    print(f"Models directory: {models_dir}")
    return True


def main():
    """Download all models."""
    print("="*60)
    print("WATERMARK REMOVAL - MODEL DOWNLOADER")
    print("="*60)
    
    print(f"\nDevice: {settings.DEVICE}")
    print(f"Models directory: {settings.MODELS_DIR}")
    
    # Create directory
    create_models_directory()
    
    # Download models
    results = {}
    
    print("\n" + "="*60)
    print("Starting model downloads...")
    print("="*60)
    
    # OpenCV is built-in, no download needed
    print("\nOpenCV inpainting: Built-in (no download needed)")
    results["opencv"] = True
    
    # Lama
    results["lama"] = download_lama_model()
    
    # Stable Diffusion
    results["stable_diffusion"] = download_stable_diffusion_model()
    
    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    
    for model, success in results.items():
        status = "OK" if success else "FAILED"
        print(f"  - {model}: {status}")
    
    successful = sum(1 for s in results.values() if s)
    total = len(results)
    
    print(f"\n{successful}/{total} models ready")
    
    if successful == total:
        print("\nAll models downloaded! Backend is ready for inference.")
        return 0
    else:
        print(f"\nSome models failed. You can still use OpenCV and Frequency methods.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
