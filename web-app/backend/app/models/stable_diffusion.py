"""
Stable Diffusion-based inpainting for watermark removal.
Uses diffusers library for high-quality generative inpainting.
"""

import cv2
import numpy as np
from typing import Dict, Tuple, Optional
from .base import RemovalMethod


class StableDiffusionRemoval(RemovalMethod):
    """Stable Diffusion-based watermark removal using diffusers."""
    
    name = "Stable Diffusion Inpainting"
    description = "Generative inpainting with quality slider - highest quality but slowest"
    
    def __init__(self, device: str = "cpu", model_id: str = "runwayml/stable-diffusion-inpainting"):
        """
        Initialize Stable Diffusion removal method.
        
        Args:
            device: Device type (cpu/cuda)
            model_id: Hugging Face model ID for inpainting
        """
        self.device = device
        self.model_id = model_id
        self.pipeline = None
        self._load_model()
    
    def _load_model(self) -> bool:
        """Load Stable Diffusion model lazily."""
        try:
            from diffusers import StableDiffusionInpaintPipeline
            import torch
            
            # Use smaller model for CPU
            if self.device == "cpu":
                model_id = "runwayml/stable-diffusion-inpainting"
            else:
                model_id = "runwayml/stable-diffusion-inpainting"
            
            self.pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            if self.device == "cuda":
                self.pipeline = self.pipeline.to("cuda")
                self.pipeline.enable_attention_slicing()
            
            return True
        except ImportError:
            return False
        except Exception as e:
            print(f"Error loading Stable Diffusion model: {e}")
            return False
    
    def remove(self, image: np.ndarray, mask: np.ndarray, 
               num_inference_steps: int = 50) -> Tuple[np.ndarray, Dict]:
        """
        Remove watermark using Stable Diffusion inpainting.
        
        Args:
            image: Input image (BGR, uint8)
            mask: Binary mask of watermark region
            num_inference_steps: Number of inference steps (20-50), higher = better quality
            
        Returns:
            Tuple of (result_image, metadata)
        """
        if not self.validate_inputs(image, mask):
            return image, {"error": "Invalid inputs"}
        
        if self.pipeline is None:
            return image, {"error": "Stable Diffusion model not loaded"}
        
        try:
            # Ensure mask is binary and inverted for diffusers (0 = remove, 1 = keep)
            _, mask_binary = cv2.threshold(mask, 128, 255, cv2.THRESH_BINARY)
            mask_pil = self._prepare_mask(mask_binary)
            
            # Convert BGR to RGB and to PIL
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_pil = self._numpy_to_pil(image_rgb)
            
            # Clamp inference steps
            num_inference_steps = max(20, min(50, num_inference_steps))
            
            # Run inpainting
            with self.pipeline.no_grad() if hasattr(self.pipeline, 'no_grad') else self.pipeline:
                result_pil = self.pipeline(
                    prompt="",  # Empty prompt for object removal
                    image=image_pil,
                    mask_image=mask_pil,
                    num_inference_steps=num_inference_steps,
                    guidance_scale=7.5,
                    negative_prompt="watermark, text, logo",
                ).images[0]
            
            # Convert back to numpy BGR
            result_rgb = np.array(result_pil)
            result = cv2.cvtColor(result_rgb, cv2.COLOR_RGB2BGR)
            
            metadata = {
                "method": "stable_diffusion",
                "model": self.model_id,
                "inference_steps": num_inference_steps,
                "device": self.device,
                "processing_time": "very_slow",
            }
            
            return result, metadata
            
        except Exception as e:
            return image, {"error": str(e), "method": "stable_diffusion"}
    
    def _prepare_mask(self, mask: np.ndarray) -> "PIL.Image":
        """Convert mask to PIL Image for diffusers."""
        try:
            from PIL import Image
            # Invert mask (0 = remove, 255 = keep)
            mask_inv = 255 - mask
            return Image.fromarray(mask_inv, mode='L')
        except Exception as e:
            raise RuntimeError(f"Error preparing mask: {e}")
    
    def _numpy_to_pil(self, image: np.ndarray) -> "PIL.Image":
        """Convert numpy array to PIL Image."""
        try:
            from PIL import Image
            image_uint8 = (image.astype(np.float32)).astype(np.uint8)
            return Image.fromarray(image_uint8, mode='RGB')
        except Exception as e:
            raise RuntimeError(f"Error converting to PIL: {e}")
    
    def is_available(self) -> bool:
        """Check if Stable Diffusion model is available."""
        return self.pipeline is not None
