"""
Quality assessment utilities for watermark removal results.
Includes BRISQUE, SSIM, and other quality metrics.
"""

import cv2
import numpy as np
from typing import Dict


class QualityMetrics:
    """Compute quality metrics for processed images."""
    
    @staticmethod
    def compute_brisque(image: np.ndarray) -> float:
        """
        Compute BRISQUE (Blind/Referenceless Image Spatial Quality Evaluator) score.
        
        Lower score indicates better image quality (range 0-100).
        
        Args:
            image: Input image (BGR, uint8)
            
        Returns:
            BRISQUE score (0 = best, 100 = worst)
        """
        try:
            from brisque import BRISQUE
            
            # Initialize BRISQUE
            brisque = BRISQUE(url=False)
            
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
            
            # Compute BRISQUE score
            score = brisque.score(image_rgb)
            
            return float(score)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def compute_ssim(image1: np.ndarray, image2: np.ndarray, mask: np.ndarray = None) -> float:
        """
        Compute Structural Similarity Index (SSIM) between two images.
        
        Range: -1 to 1 (higher is better, 1 = identical).
        
        Args:
            image1: First image (uint8)
            image2: Second image (uint8)
            mask: Optional mask to compute SSIM only on specific region
            
        Returns:
            SSIM score
        """
        try:
            from skimage.metrics import structural_similarity as ssim
            
            # Convert to grayscale
            if len(image1.shape) == 3:
                gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
            else:
                gray1 = image1
            
            if len(image2.shape) == 3:
                gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
            else:
                gray2 = image2
            
            # Ensure same size
            h, w = gray1.shape
            gray2 = cv2.resize(gray2, (w, h))
            
            if mask is not None:
                # Compute SSIM only on masked region
                mask_bool = mask > 128
                if not np.any(mask_bool):
                    return 0.0
                
                score = ssim(
                    gray1[mask_bool],
                    gray2[mask_bool],
                    data_range=255
                )
            else:
                # Compute SSIM on entire image
                score = ssim(gray1, gray2, data_range=255)
            
            return float(score)
        except ImportError:
            return 0.0
        except Exception:
            return 0.0
    
    @staticmethod
    def compute_sharpness(image: np.ndarray) -> float:
        """
        Compute sharpness metric using Laplacian variance.
        
        Higher values indicate sharper images.
        
        Args:
            image: Input image
            
        Returns:
            Sharpness score (variance of Laplacian)
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Compute Laplacian and variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var()
            
            return float(sharpness)
        except Exception:
            return 0.0
    
    @staticmethod
    def compute_contrast(image: np.ndarray) -> float:
        """
        Compute contrast metric using standard deviation of intensity.
        
        Higher values indicate higher contrast.
        
        Args:
            image: Input image
            
        Returns:
            Contrast score
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Compute standard deviation
            contrast = np.std(gray.astype(float))
            
            return float(contrast)
        except Exception:
            return 0.0
    
    @staticmethod
    def compute_all_metrics(original: np.ndarray, processed: np.ndarray, 
                           mask: np.ndarray = None) -> Dict[str, float]:
        """
        Compute all quality metrics for comparison.
        
        Args:
            original: Original image
            processed: Processed image
            mask: Optional watermark mask
            
        Returns:
            Dictionary of all metrics
        """
        metrics = {
            "brisque_original": QualityMetrics.compute_brisque(original),
            "brisque_processed": QualityMetrics.compute_brisque(processed),
            "ssim": QualityMetrics.compute_ssim(original, processed, mask),
            "sharpness_original": QualityMetrics.compute_sharpness(original),
            "sharpness_processed": QualityMetrics.compute_sharpness(processed),
            "contrast_original": QualityMetrics.compute_contrast(original),
            "contrast_processed": QualityMetrics.compute_contrast(processed),
        }
        
        # Compute improvements
        metrics["brisque_improvement"] = metrics["brisque_original"] - metrics["brisque_processed"]
        
        return metrics
