"""
Watermark detection module with multiple strategies.
Combines FFT analysis, edge detection, alpha channel detection, and saliency mapping.
"""

import cv2
import numpy as np
from scipy import ndimage
from scipy.fft import fft2, fftshift
from typing import Tuple, Dict, List
import warnings

warnings.filterwarnings("ignore")


class WatermarkDetector:
    """Multi-strategy watermark detection engine."""
    
    def __init__(self):
        """Initialize detector."""
        self.detection_methods = [
            self.detect_by_fft,
            self.detect_by_edges,
            self.detect_by_color_contrast,
            self.detect_by_alpha_anomaly,
        ]
    
    def detect(self, image: np.ndarray, alpha_channel: np.ndarray = None) -> Tuple[np.ndarray, Dict]:
        """
        Multi-method watermark detection combining multiple strategies.
        
        Args:
            image: Input image (BGR format, uint8)
            alpha_channel: Optional alpha channel for PNG images
            
        Returns:
            Tuple of (combined_mask, detection_results_dict)
        """
        masks = []
        confidences = []
        regions = []
        
        # FFT-based detection (catches tiled/repeating watermarks)
        fft_mask, fft_conf, fft_regions = self.detect_by_fft(image)
        if fft_mask is not None:
            masks.append(fft_mask)
            confidences.append(fft_conf)
            regions.extend(fft_regions)
        
        # Edge-based detection (catches text/logo watermarks)
        edge_mask, edge_conf, edge_regions = self.detect_by_edges(image)
        if edge_mask is not None:
            masks.append(edge_mask)
            confidences.append(edge_conf)
            regions.extend(edge_regions)
        
        # Color contrast detection (catches colored watermarks)
        color_mask, color_conf, color_regions = self.detect_by_color_contrast(image)
        if color_mask is not None:
            masks.append(color_mask)
            confidences.append(color_conf)
            regions.extend(color_regions)
        
        # Alpha channel detection (catches transparent overlays)
        if alpha_channel is not None:
            alpha_mask, alpha_conf, alpha_regions = self.detect_by_alpha_anomaly(alpha_channel)
            if alpha_mask is not None:
                masks.append(alpha_mask)
                confidences.append(alpha_conf)
                regions.extend(alpha_regions)
        
        # Combine all masks using weighted union
        if masks:
            combined_mask = self._combine_masks(masks, confidences)
            # Morphological dilation for clean coverage
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            combined_mask = cv2.dilate(combined_mask, kernel, iterations=1)
        else:
            combined_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        
        # Calculate overall confidence
        overall_confidence = float(np.mean(confidences)) if confidences else 0.0
        
        detection_results = {
            "mask": combined_mask,
            "confidence": overall_confidence,
            "detection_methods_used": len(masks),
            "regions": regions,
            "individual_confidences": {
                "fft": confidences[0] if len(confidences) > 0 else 0,
                "edges": confidences[1] if len(confidences) > 1 else 0,
                "color": confidences[2] if len(confidences) > 2 else 0,
                "alpha": confidences[3] if len(confidences) > 3 else 0,
            }
        }
        
        return combined_mask, detection_results
    
    def detect_by_fft(self, image: np.ndarray) -> Tuple[np.ndarray, float, List]:
        """
        Detect tiled/repeating watermarks using FFT frequency analysis.
        
        Returns:
            Tuple of (mask, confidence, regions)
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Compute FFT
            f_transform = fft2(gray)
            f_shift = fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Normalize and threshold
            magnitude_norm = np.log(magnitude_spectrum + 1)
            threshold = np.percentile(magnitude_norm, 95)
            peak_mask = (magnitude_norm > threshold).astype(np.uint8)
            
            # If too few peaks, likely no tiled watermark
            if np.sum(peak_mask) < 10:
                return None, 0.0, []
            
            # Inverse FFT after removing peaks
            f_shift_filtered = f_shift.copy()
            f_shift_filtered[peak_mask == 1] = 0
            f_ishift = np.fft.ifftshift(f_shift_filtered)
            img_back = np.abs(np.fft.ifft2(f_ishift))
            
            # Residual image highlighting watermark
            residual = np.abs(gray.astype(float) - img_back)
            residual = cv2.normalize(residual, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Thresholding
            _, mask = cv2.threshold(residual, np.mean(residual) * 0.8, 255, cv2.THRESH_BINARY)
            
            # Post-processing
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            if np.sum(mask) > 100:  # Minimum area threshold
                confidence = float(np.sum(mask)) / mask.size
                regions = self._get_regions_from_mask(mask)
                return mask, min(confidence, 1.0), regions
            
            return None, 0.0, []
        except Exception:
            return None, 0.0, []
    
    def detect_by_edges(self, image: np.ndarray) -> Tuple[np.ndarray, float, List]:
        """
        Detect watermarks using edge and contrast analysis.
        Good for text and logo watermarks.
        
        Returns:
            Tuple of (mask, confidence, regions)
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size and create mask
            mask = np.zeros(gray.shape, dtype=np.uint8)
            valid_contours = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Minimum area
                    valid_contours.append(contour)
                    cv2.drawContours(mask, [contour], 0, 255, -1)
            
            if np.sum(mask) > 100:
                confidence = float(np.sum(mask)) / mask.size
                regions = self._get_regions_from_mask(mask)
                return mask, min(confidence, 1.0), regions
            
            return None, 0.0, []
        except Exception:
            return None, 0.0, []
    
    def detect_by_color_contrast(self, image: np.ndarray) -> Tuple[np.ndarray, float, List]:
        """
        Detect colored watermarks by analyzing color contrast anomalies.
        Uses LAB color space for perceptual uniformity.
        
        Returns:
            Tuple of (mask, confidence, regions)
        """
        try:
            # Convert to LAB
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l_channel = lab[:, :, 0].astype(float)
            
            # Statistical anomaly detection
            mean_l = np.mean(l_channel)
            std_l = np.std(l_channel)
            
            # Find pixels that deviate significantly from mean
            anomaly_map = np.abs(l_channel - mean_l) > (2.5 * std_l)
            
            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            anomaly_map = cv2.morphologyEx(anomaly_map.astype(np.uint8) * 255, 
                                          cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # Apply Gaussian threshold
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(anomaly_map, 128, 255, cv2.THRESH_BINARY)
            
            if np.sum(mask) > 100:
                confidence = float(np.sum(mask)) / mask.size
                regions = self._get_regions_from_mask(mask)
                return mask, min(confidence, 1.0), regions
            
            return None, 0.0, []
        except Exception:
            return None, 0.0, []
    
    def detect_by_alpha_anomaly(self, alpha_channel: np.ndarray) -> Tuple[np.ndarray, float, List]:
        """
        Detect transparent overlay watermarks by analyzing alpha channel anomalies.
        
        Args:
            alpha_channel: Alpha channel from PNG (0-255)
            
        Returns:
            Tuple of (mask, confidence, regions)
        """
        try:
            # Find non-fully-opaque regions
            # Assume watermarks have partial transparency
            alpha_float = alpha_channel.astype(float)
            
            # Watermarks typically have alpha values in middle range (not 0 or 255)
            mask = np.zeros_like(alpha_channel)
            mask[(alpha_float > 10) & (alpha_float < 245)] = 255
            
            # Morphological processing
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            if np.sum(mask) > 100:
                confidence = float(np.sum(mask)) / mask.size
                regions = self._get_regions_from_mask(mask)
                return mask, min(confidence, 0.8), regions  # Lower confidence for alpha
            
            return None, 0.0, []
        except Exception:
            return None, 0.0, []
    
    def _combine_masks(self, masks: List[np.ndarray], weights: List[float]) -> np.ndarray:
        """
        Combine multiple masks using weighted union.
        
        Args:
            masks: List of binary masks
            weights: Confidence weights for each mask
            
        Returns:
            Combined mask
        """
        if not masks:
            return None
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / (np.sum(weights) + 1e-6)
        
        # Weighted combination
        combined = np.zeros_like(masks[0], dtype=float)
        for mask, weight in zip(masks, weights):
            combined += mask.astype(float) * weight
        
        # Threshold at 0.5
        combined_mask = (combined > 0.5).astype(np.uint8) * 255
        
        return combined_mask
    
    def _get_regions_from_mask(self, mask: np.ndarray) -> List[Dict]:
        """
        Extract bounding box regions from mask.
        
        Args:
            mask: Binary mask
            
        Returns:
            List of region dicts with x, y, width, height
        """
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10:  # Minimum region size
                regions.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "area": int(w * h)
                })
        
        return sorted(regions, key=lambda r: r["area"], reverse=True)
