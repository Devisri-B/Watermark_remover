"""
Watermark removal models and methods.
"""

from .base import RemovalMethod
from .opencv import OpenCVRemoval
from .lama import LamaRemoval
from .stable_diffusion import StableDiffusionRemoval
from .frequency import FrequencyRemoval
from .deepfill import DeepFillRemoval

__all__ = [
    "RemovalMethod",
    "OpenCVRemoval",
    "LamaRemoval",
    "StableDiffusionRemoval",
    "FrequencyRemoval",
    "DeepFillRemoval",
]
