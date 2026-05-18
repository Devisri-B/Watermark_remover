"""
Base class for watermark removal methods.
Defines interface for all removal implementations.
"""

from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Tuple


class RemovalMethod(ABC):
    """Abstract base class for watermark removal methods."""
    
    name: str = "Base Method"
    description: str = "Base removal method"
    
    @abstractmethod
    def remove(self, image: np.ndarray, mask: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Remove watermark from image using mask.
        
        Args:
            image: Input image (BGR, uint8)
            mask: Binary mask of watermark region (uint8, 0-255)
            
        Returns:
            Tuple of (processed_image, metadata_dict)
        """
        pass
    
    def validate_inputs(self, image: np.ndarray, mask: np.ndarray) -> bool:
        """Validate input image and mask."""
        if image is None or image.size == 0:
            return False
        if mask is None or mask.size == 0:
            return False
        if image.shape[:2] != mask.shape[:2]:
            return False
        return True
