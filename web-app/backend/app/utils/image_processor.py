"""
Image processing utilities for watermark removal pipeline.
"""

import cv2
import numpy as np
from typing import Tuple
from pathlib import Path


class ImageProcessor:
    """Utility class for image processing operations."""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff'}
    
    @staticmethod
    def load_image(image_path: str) -> Tuple[np.ndarray, str]:
        """
        Load image from file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (image_array, format)
        """
        path = Path(image_path)
        
        if path.suffix.lower() not in ImageProcessor.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported image format: {path.suffix}")
        
        image = cv2.imread(str(image_path))
        
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        return image, path.suffix.lower()
    
    @staticmethod
    def save_image(image: np.ndarray, output_path: str, quality: int = 95) -> bool:
        """
        Save image to file.
        
        Args:
            image: Image array
            output_path: Output file path
            quality: JPEG quality (0-100)
            
        Returns:
            Success status
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if path.suffix.lower() in {'.jpg', '.jpeg'}:
            return cv2.imwrite(str(path), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        else:
            return cv2.imwrite(str(path), image)
    
    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 2048, 
                     max_height: int = 2048) -> np.ndarray:
        """
        Resize image if larger than max dimensions.
        
        Args:
            image: Input image
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized image (or original if smaller)
        """
        h, w = image.shape[:2]
        
        if w <= max_width and h <= max_height:
            return image
        
        scale = min(max_width / w, max_height / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    @staticmethod
    def normalize_image(image: np.ndarray) -> np.ndarray:
        """
        Normalize image to 0-1 range.
        
        Args:
            image: Input image (typically 0-255)
            
        Returns:
            Normalized image (0.0-1.0)
        """
        return image.astype(np.float32) / 255.0
    
    @staticmethod
    def denormalize_image(image: np.ndarray) -> np.ndarray:
        """
        Denormalize image from 0-1 to 0-255 range.
        
        Args:
            image: Normalized image (0.0-1.0)
            
        Returns:
            Image in 0-255 range (uint8)
        """
        return np.clip(image * 255, 0, 255).astype(np.uint8)
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """
        Get image information.
        
        Args:
            image: Input image
            
        Returns:
            Dictionary with image info
        """
        h, w = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        dtype = str(image.dtype)
        size_mb = image.nbytes / (1024 * 1024)
        
        return {
            "width": w,
            "height": h,
            "channels": channels,
            "dtype": dtype,
            "size_mb": size_mb,
            "aspect_ratio": w / h if h > 0 else 1.0,
        }
