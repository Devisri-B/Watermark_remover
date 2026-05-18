"""
Configuration settings for the watermark removal backend.
"""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    API_TITLE: str = "Watermark Removal API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Server Configuration
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Model Configuration
    MODELS_DIR: Path = Path(__file__).parent.parent / "models"
    ENABLE_GPU: bool = False  # Set to True if CUDA available
    DEVICE: str = "cpu"  # "cuda" or "cpu"
    
    # Processing Configuration
    MAX_IMAGE_SIZE_MB: int = 20
    SUPPORTED_FORMATS: list = ["jpg", "jpeg", "png", "webp"]
    OUTPUT_QUALITY: int = 95
    PROCESSING_TIMEOUT_SECONDS: int = 300
    
    # Model Availability (set dynamically based on installation)
    MODELS_AVAILABLE: dict = {
        "opencv": True,
        "lama": False,
        "deepfill": False,
        "stable_diffusion": False,
        "frequency": True,
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
