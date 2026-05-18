"""
OpenCV inpainting-based watermark removal.
Fast method using morphological reconstruction and Telea/Navier-Stokes algorithms.
"""

import cv2
import numpy as np
from typing import Dict, Tuple
from .base import RemovalMethod


class OpenCVRemoval(RemovalMethod):
    """OpenCV inpainting-based watermark removal."""
    
    name = "OpenCV Inpainting (Fast)"
    description = "Quick inpainting using morphological reconstruction - good for simple watermarks"
    
    def __init__(self, device: str = "cpu"):
        """
        Initialize OpenCV removal method.
        
        Args:
            device: Device type (cpu/cuda) - OpenCV uses CPU by default
        """
        self.device = device
    
    def remove(self, image: np.ndarray, mask: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove watermark using OpenCV inpainting.
        
        Tries both TELEA and NAVIER_STOKES algorithms and picks best via SSIM.
        
        Args:
            image: Input image (BGR, uint8)
            mask: Binary mask of watermark region
            
        Returns:
            Tuple of (result_image, metadata)
        """
        if not self.validate_inputs(image, mask):
            return image, {"error": "Invalid inputs"}
        
        try:
            # Ensure mask is binary
            _, mask_binary = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)
            
            # Try Telea algorithm (faster)
            result_telea = cv2.inpaint(image, mask_binary, 3, cv2.INPAINT_TELEA)
            
            # Try Navier-Stokes algorithm (better quality, slower)
            result_ns = cv2.inpaint(image, mask_binary, 3, cv2.INPAINT_NS)
            
            # Compare using SSIM and pick better result
            ssim_telea = self._compute_ssim(image, result_telea, mask_binary)
            ssim_ns = self._compute_ssim(image, result_ns, mask_binary)
            
            if ssim_ns > ssim_telea:
                result = result_ns
                algorithm_used = "Navier-Stokes"
            else:
                result = result_telea
                algorithm_used = "Telea"
            
            metadata = {
                "method": "opencv",
                "algorithm": algorithm_used,
                "ssim_telea": float(ssim_telea),
                "ssim_ns": float(ssim_ns),
                "processing_time": "fast",
            }
            
            return result, metadata
            
        except Exception as e:
            return image, {"error": str(e), "method": "opencv"}
    
    def is_available(self) -> bool:
        """Check if OpenCV inpainting is available (always true for basic OpenCV)."""
        return True
    
    def _compute_ssim(self, original: np.ndarray, result: np.ndarray, 
                      mask: np.ndarray) -> float:
        """
        Compute SSIM only on masked region (where watermark was).
        
        Args:
            original: Original image
            result: Inpainted image
            mask: Mask of region to evaluate
            
        Returns:
            SSIM score in range [0, 1]
        """
        try:
            # Try using scikit-image SSIM if available
            try:
                from skimage.metrics import structural_similarity as ssim
                
                # Convert to grayscale
                orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
                result_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                
                # Compute SSIM only on masked region
                mask_bool = mask > 128
                if not np.any(mask_bool):
                    return 0.5
                
                # Extract patches from masked region
                orig_patch = orig_gray[mask_bool]
                result_patch = result_gray[mask_bool]
                
                # Use simple correlation for compatibility
                if len(orig_patch) > 0:
                    correlation = np.corrcoef(orig_patch, result_patch)[0, 1]
                    if np.isnan(correlation):
                        correlation = 0.0
                    # Scale correlation to [0, 1]
                    ssim_score = (correlation + 1.0) / 2.0
                else:
                    ssim_score = 0.5
                    
                return float(np.clip(ssim_score, 0.0, 1.0))
                
            except ImportError:
                # Fallback if scikit-image not available
                orig_gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
                result_gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                
                mask_bool = mask > 128
                if not np.any(mask_bool):
                    return 0.5
                
                # Simple SSIM approximation for masked region
                diff = np.abs(orig_gray.astype(float) - result_gray.astype(float))
                masked_diff = diff[mask_bool]
                
                # Inverse of mean absolute difference (0 = identical, high = different)
                ssim_score = 1.0 / (1.0 + np.mean(masked_diff) / 255.0)
                
                return float(ssim_score)
                
        except Exception:
            return 0.5
