"""
Lama Cleaner-based watermark removal.
Deep learning-based inpainting with ResNet architecture.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from .base import RemovalMethod


class LamaRemoval(RemovalMethod):
    """Lama Cleaner-based watermark removal using deep learning."""
    
    name = "Lama Cleaner AI (Best Quality)"
    description = "Deep learning inpainting for high-quality results - slower but best quality"
    
    def __init__(self, device: str = "cpu"):
        """
        Initialize Lama Cleaner removal method.
        
        Args:
            device: Device type (cpu/cuda)
        """
        self.device = device
        self.model = None
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load Lama model lazily."""
        try:
            from lama_cleaner.model_manager import ModelManager
            
            # Initialize model manager with CPU support
            self.model = ModelManager(
                name="lama",
                device=self.device,
                disable_nsfw=True,
                cpu_textencoder=True if self.device == "cpu" else False,
            )
            
            return True
        except ImportError:
            print("Lama Cleaner not installed, skipping")
            return False
        except Exception as e:
            print(f"Error loading Lama model: {e}")
            return False
    
    def remove(self, image: np.ndarray, mask: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove watermark using Lama Cleaner.
        
        Args:
            image: Input image (BGR, uint8)
            mask: Binary mask of watermark region
            
        Returns:
            Tuple of (result_image, metadata)
        """
        if not self.validate_inputs(image, mask):
            return image, {"error": "Invalid inputs"}
        
        if self.model is None:
            return image, {"error": "Lama model not loaded", "fallback": "Use OpenCV instead"}
        
        try:
            # Ensure mask is binary
            _, mask_binary = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)
            
            # Convert BGR to RGB for Lama
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert numpy to PIL for Lama
            from PIL import Image
            image_pil = Image.fromarray(image_rgb)
            mask_pil = Image.fromarray(mask_binary, mode='L')
            
            # Apply Lama inpainting - the model returns numpy array
            result_rgb = self.model(image_pil, mask_pil)
            
            # If result is PIL Image, convert to numpy
            if isinstance(result_rgb, Image.Image):
                result_rgb = np.array(result_rgb)
            
            # Convert back to BGR
            result = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
            
            metadata = {
                "method": "lama",
                "model": "lama-cleaner",
                "device": self.device,
                "processing_time": "slow",
            }
            
            return result, metadata
            
        except Exception as e:
            return image, {"error": str(e), "method": "lama"}
    
    def is_available(self) -> bool:
        """Check if Lama model is available."""
        return self.model is not None
