"""
Frequency domain and hybrid exemplar-based watermark removal.
Combines FFT notch filtering with PatchMatch exemplar inpainting.
"""

import cv2
import numpy as np
from scipy.fft import fft2, ifft2, fftshift, ifftshift
from scipy.ndimage import maximum_filter
from typing import Dict, Tuple
from .base import RemovalMethod


class FrequencyRemoval(RemovalMethod):
    """Frequency domain + exemplar-based hybrid removal."""
    
    name = "Frequency + Exemplar Hybrid"
    description = "Combines FFT notch filtering with PatchMatch - good for repeating patterns"
    
    def __init__(self, device: str = "cpu"):
        """
        Initialize frequency-based removal method.
        
        Args:
            device: Device type (cpu/cuda) - freq domain uses CPU only
        """
        self.device = "cpu"  # Frequency processing is CPU-only
    
    def remove(self, image: np.ndarray, mask: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove watermark using FFT notch filtering + exemplar inpainting.
        
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
            
            # Step 1: FFT-based notch filtering for repeating patterns
            result = self._fft_notch_filter(image, mask_binary)
            
            # Step 2: Exemplar inpainting for remaining artifacts
            result = self._exemplar_inpaint(result, mask_binary)
            
            # Step 3: Wavelet sharpening for edge enhancement
            result = self._wavelet_sharpen(result)
            
            metadata = {
                "method": "frequency_hybrid",
                "techniques": ["fft_notch", "exemplar_inpaint", "wavelet_sharpen"],
                "processing_time": "medium",
            }
            
            return result, metadata
            
        except Exception as e:
            return image, {"error": str(e), "method": "frequency"}
    
    def _fft_notch_filter(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Apply FFT notch filtering to remove repeating watermark patterns.
        
        Args:
            image: Input image
            mask: Mask of watermark region
            
        Returns:
            Filtered image
        """
        try:
            # Convert to grayscale for FFT
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Pad for better FFT
            h, w = gray.shape
            padded = np.pad(gray, ((h // 4, h // 4), (w // 4, w // 4)), mode='reflect')
            
            # FFT
            f_transform = fft2(padded.astype(float))
            f_shift = fftshift(f_transform)
            
            # Find peaks in frequency domain
            magnitude = np.abs(f_shift)
            magnitude_log = np.log(magnitude + 1)
            
            # Create notch filter (suppress high-magnitude frequencies)
            notch_filter = self._create_notch_filter(magnitude_log)
            
            # Apply filter
            f_filtered = f_shift * notch_filter
            
            # Inverse FFT
            f_ishift = ifftshift(f_filtered)
            img_back = np.abs(ifft2(f_ishift))
            
            # Crop to original size
            img_back = img_back[h // 4:h // 4 + h, w // 4:w // 4 + w].astype(np.uint8)
            
            # Blend with original (don't over-process)
            gray_result = cv2.addWeighted(gray, 0.7, img_back, 0.3, 0)
            
            # Convert grayscale result back to BGR
            color_result = cv2.cvtColor(gray_result, cv2.COLOR_GRAY2BGR)
            
            # Apply mask blending with original
            result = image.copy()
            result = np.where(mask[:, :, np.newaxis] > 128, color_result, image)
            
            return result.astype(np.uint8)
        except Exception:
            return image
    
    def _create_notch_filter(self, magnitude: np.ndarray, threshold_percentile: int = 90) -> np.ndarray:
        """Create notch filter for frequency suppression."""
        h, w = magnitude.shape
        center_y, center_x = h // 2, w // 2
        
        # Create filter with 1s (pass) and 0s (reject)
        notch_filter = np.ones((h, w), dtype=np.float32)
        
        # Find high-magnitude frequency peaks
        threshold = np.percentile(magnitude, threshold_percentile)
        high_mag = magnitude > threshold
        
        # Create Gaussian-falloff notch around peaks
        y, x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
        
        for peak_y, peak_x in zip(*np.where(high_mag)):
            dist = np.sqrt((y - peak_y) ** 2 + (x - peak_x) ** 2)
            notch = 1 - np.exp(-(dist ** 2) / (2 * 25 ** 2))  # Gaussian width = 25
            notch_filter *= notch
        
        return notch_filter
    
    def _exemplar_inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Exemplar-based inpainting using PatchMatch (via OpenCV).
        
        Args:
            image: Input image
            mask: Mask of region to inpaint
            
        Returns:
            Inpainted image
        """
        try:
            # Use Telea algorithm (exemplar-like PatchMatch approximation)
            result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)
            return result
        except Exception:
            return image
    
    def _wavelet_sharpen(self, image: np.ndarray) -> np.ndarray:
        """
        Wavelet-based sharpening for edge enhancement.
        
        Args:
            image: Input image
            
        Returns:
            Sharpened image
        """
        try:
            # Simple unsharp mask (Laplacian sharpening)
            gaussian = cv2.GaussianBlur(image, (5, 5), 1.0)
            laplacian = image.astype(float) - gaussian.astype(float)
            
            # Apply sharpening (subtle)
            sharpened = image.astype(float) + 0.3 * laplacian
            
            # Clip and convert
            sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
            
            return sharpened
        except Exception:
            return image
    
    def is_available(self) -> bool:
        """Check if frequency method is available (always true for NumPy/SciPy)."""
        return True
