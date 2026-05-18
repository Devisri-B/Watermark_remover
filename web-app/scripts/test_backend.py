#!/usr/bin/env python3
"""
Test script for watermark removal backend API.
Run this to verify the backend is working correctly.
"""

import sys
import asyncio
import cv2
import numpy as np
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.utils.detector import WatermarkDetector
from app.models.opencv import OpenCVRemoval
from app.utils.quality import QualityMetrics


async def test_detection():
    """Test watermark detection."""
    print("\n" + "="*60)
    print("Testing Watermark Detection")
    print("="*60)
    
    # Create a simple test image with watermark
    image = np.ones((500, 500, 3), dtype=np.uint8) * 200
    
    # Add a simulated watermark (horizontal lines)
    for y in range(100, 150):
        image[y, :] = [50, 50, 50]
    
    # Add some edges/features
    cv2.rectangle(image, (50, 50), (200, 200), (100, 100, 100), 2)
    
    # Detect
    detector = WatermarkDetector()
    mask, results = detector.detect(image)
    
    print(f"Detection Confidence: {results['confidence']:.2%}")
    print(f"Methods Used: {results['detection_methods_used']}")
    print(f"Watermark Detected: {results['confidence'] > 0.1}")
    print(f"Individual Scores:")
    for method, score in results['individual_confidences'].items():
        if score > 0:
            print(f"  - {method}: {score:.2%}")
    print(f"Detected Regions: {len(results['regions'])}")
    
    return True


async def test_removal():
    """Test watermark removal."""
    print("\n" + "="*60)
    print("Testing Watermark Removal (OpenCV)")
    print("="*60)
    
    # Create test image and mask
    image = np.ones((500, 500, 3), dtype=np.uint8) * 200
    mask = np.zeros((500, 500), dtype=np.uint8)
    mask[100:150, :] = 255
    
    # Remove
    remover = OpenCVRemoval(device=settings.DEVICE)
    result, metadata = remover.remove(image, mask)
    
    print(f"Method: {metadata.get('method')}")
    print(f"Algorithm: {metadata.get('algorithm')}")
    print(f"Processing Time: {metadata.get('processing_time')}")
    print(f"SSIM (Telea): {metadata.get('ssim_telea', 0):.3f}")
    print(f"SSIM (Navier-Stokes): {metadata.get('ssim_ns', 0):.3f}")
    
    # Check output
    if result is not None and result.shape == image.shape:
        print("Result image valid: YES")
        return True
    else:
        print("Result image valid: NO")
        return False


async def test_quality_metrics():
    """Test quality metrics computation."""
    print("\n" + "="*60)
    print("Testing Quality Metrics")
    print("="*60)
    
    # Create simple test images
    original = np.ones((500, 500, 3), dtype=np.uint8) * 150
    processed = np.ones((500, 500, 3), dtype=np.uint8) * 160
    
    metrics_computer = QualityMetrics()
    
    # Compute metrics
    brisque = metrics_computer.compute_brisque(original)
    sharpness = metrics_computer.compute_sharpness(original)
    contrast = metrics_computer.compute_contrast(original)
    
    print(f"BRISQUE Score: {brisque:.2f}")
    print(f"Sharpness: {sharpness:.2f}")
    print(f"Contrast: {contrast:.2f}")
    
    return True


async def test_models_import():
    """Test that all removal models can be imported."""
    print("\n" + "="*60)
    print("Testing Model Imports")
    print("="*60)
    
    models = []
    
    # OpenCV
    try:
        from app.models.opencv import OpenCVRemoval
        remover = OpenCVRemoval()
        models.append(("OpenCV", True, "Imported successfully"))
    except Exception as e:
        models.append(("OpenCV", False, str(e)))
    
    # Lama (optional)
    try:
        from app.models.lama import LamaRemoval
        models.append(("Lama Cleaner", None, "Code available (model requires Lama package)"))
    except Exception as e:
        models.append(("Lama Cleaner", False, str(e)))
    
    # Frequency
    try:
        from app.models.frequency import FrequencyRemoval
        remover = FrequencyRemoval()
        models.append(("Frequency Hybrid", True, "Imported successfully"))
    except Exception as e:
        models.append(("Frequency Hybrid", False, str(e)))
    
    # Stable Diffusion (optional)
    try:
        from app.models.stable_diffusion import StableDiffusionRemoval
        models.append(("Stable Diffusion", None, "Code available (requires diffusers)"))
    except Exception as e:
        models.append(("Stable Diffusion", False, str(e)))
    
    # DeepFill (stub)
    try:
        from app.models.deepfill import DeepFillRemoval
        models.append(("DeepFill v2", None, "Stub available (requires implementation)"))
    except Exception as e:
        models.append(("DeepFill v2", False, str(e)))
    
    # Print results
    for name, status, message in models:
        status_str = "OK" if status else ("OPTIONAL" if status is None else "FAILED")
        print(f"  - {name}: {status_str} - {message}")
    
    return all(s is not False for _, s, _ in models)


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("WATERMARK REMOVAL BACKEND TEST SUITE")
    print("="*60)
    
    print(f"Python: {sys.version}")
    print(f"Device: {settings.DEVICE}")
    print(f"Max Image Size: {settings.MAX_IMAGE_SIZE_MB}MB")
    
    try:
        # Run tests
        tests = [
            ("Models Import", test_models_import),
            ("Detection", test_detection),
            ("Removal", test_removal),
            ("Quality Metrics", test_quality_metrics),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"ERROR in {test_name}: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        for test_name, result in results:
            status = "PASSED" if result else "FAILED"
            print(f"  - {test_name}: {status}")
        
        passed = sum(1 for _, r in results if r)
        total = len(results)
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\nAll tests passed! Backend is ready.")
            return 0
        else:
            print(f"\n{total - passed} test(s) failed. Check errors above.")
            return 1
    
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
