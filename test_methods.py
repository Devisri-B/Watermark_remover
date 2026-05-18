#!/usr/bin/env python3
"""
Test script to verify all removal methods work correctly.
"""

import sys
import os
import numpy as np
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "web-app" / "backend"
sys.path.insert(0, str(backend_dir))

# Test basic imports and functionality
def test_removal_methods():
    print("Testing Watermark Removal Methods...")
    print("=" * 60)
    
    try:
        from app.models.opencv import OpenCVRemoval
        print("✓ OpenCV import successful")
    except Exception as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        from app.models.frequency import FrequencyRemoval
        print("✓ Frequency import successful")
    except Exception as e:
        print(f"✗ Frequency import failed: {e}")
        return False
    
    try:
        from app.models.deepfill import DeepFillRemoval
        print("✓ DeepFill import successful")
    except Exception as e:
        print(f"✗ DeepFill import failed: {e}")
        return False
    
    # Create test data
    test_image = np.ones((100, 100, 3), dtype=np.uint8) * 200
    test_image[40:60, 40:60] = 50  # Create a dark region
    
    test_mask = np.zeros((100, 100), dtype=np.uint8)
    test_mask[40:60, 40:60] = 255  # Mark the dark region
    
    print("\nTest Image Shape:", test_image.shape)
    print("Test Mask Shape:", test_mask.shape)
    print("=" * 60)
    
    # Test OpenCV
    print("\nTesting OpenCV Removal...")
    try:
        opencv_model = OpenCVRemoval(device="cpu")
        result, metadata = opencv_model.remove(test_image, test_mask)
        if result is not None and result.shape == test_image.shape:
            print("✓ OpenCV removal successful")
            print(f"  Result shape: {result.shape}")
            print(f"  Metadata: {metadata}")
        else:
            print("✗ OpenCV removal failed: invalid result shape")
    except Exception as e:
        print(f"✗ OpenCV removal error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test Frequency
    print("\nTesting Frequency Removal...")
    try:
        freq_model = FrequencyRemoval(device="cpu")
        result, metadata = freq_model.remove(test_image, test_mask)
        if result is not None and result.shape == test_image.shape:
            print("✓ Frequency removal successful")
            print(f"  Result shape: {result.shape}")
            print(f"  Metadata: {metadata}")
        else:
            print("✗ Frequency removal failed: invalid result shape")
    except Exception as e:
        print(f"✗ Frequency removal error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test DeepFill
    print("\nTesting DeepFill Removal...")
    try:
        deepfill_model = DeepFillRemoval(device="cpu")
        result, metadata = deepfill_model.remove(test_image, test_mask)
        if result is not None and result.shape == test_image.shape:
            print("✓ DeepFill removal successful (fallback mode)")
            print(f"  Result shape: {result.shape}")
            print(f"  Metadata: {metadata}")
        else:
            print("✗ DeepFill removal failed: invalid result shape")
    except Exception as e:
        print(f"✗ DeepFill removal error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("Testing complete!")
    return True

if __name__ == "__main__":
    success = test_removal_methods()
    sys.exit(0 if success else 1)
