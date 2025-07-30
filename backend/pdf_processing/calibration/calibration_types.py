"""
Data types for the calibration module.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
from enum import Enum


class CalibrationMethod(Enum):
    """Method used for calibration"""
    STEEL_SECTION = "steel_section"
    TIMBER_SIZE = "timber_size"
    SPACING_PATTERN = "spacing_pattern"
    SCALE_NOTATION = "scale_notation"
    MANUAL = "manual"
    NONE = "none"


@dataclass
class ComponentDetection:
    """Detected component with measured dimensions"""
    label: str  # e.g., "200PFC", "200x45"
    component_type: str  # "steel", "timber", "spacing"
    pixel_dimension: float  # Measured dimension in pixels
    expected_mm: float  # Expected dimension in mm
    confidence: float  # Detection confidence (0-1)
    location: Optional[Dict[str, float]] = None  # {"x": 100, "y": 200}
    measurement_axis: str = "horizontal"  # "horizontal" or "vertical"
    
    @property
    def pixels_per_mm(self) -> float:
        """Calculate pixels per mm for this component"""
        if self.expected_mm > 0:
            return self.pixel_dimension / self.expected_mm
        return 0


@dataclass
class CalibrationCandidate:
    """A potential calibration based on detected components"""
    method: CalibrationMethod
    components: List[ComponentDetection]
    pixels_per_mm: float
    confidence: float
    variance: float  # Variance in measurements
    
    @property
    def component_count(self) -> int:
        """Number of components used for this calibration"""
        return len(self.components)
    
    @property
    def reliability_score(self) -> float:
        """
        Calculate overall reliability score based on:
        - Confidence of detections
        - Number of components
        - Variance in measurements
        """
        avg_confidence = sum(c.confidence for c in self.components) / len(self.components)
        count_factor = min(len(self.components) / 3.0, 1.0)  # Max benefit at 3+ components
        variance_penalty = max(0, 1.0 - self.variance * 10)  # Penalize high variance
        
        return avg_confidence * count_factor * variance_penalty


@dataclass
class CalibrationResult:
    """Final calibration result"""
    method: CalibrationMethod
    pixels_per_mm: float
    mm_per_pixel: float  # Inverse for convenience
    confidence: float
    reference_components: List[str]  # Component labels used
    calibration_details: Dict[str, any]
    status: str  # "auto_calibrated", "manual", "scale_based", "failed"
    
    def __post_init__(self):
        """Calculate derived values"""
        if self.pixels_per_mm > 0:
            self.mm_per_pixel = 1.0 / self.pixels_per_mm
        else:
            self.mm_per_pixel = 0
    
    def convert_pixels_to_mm(self, pixels: float) -> float:
        """Convert pixel measurement to millimeters"""
        return pixels * self.mm_per_pixel
    
    def convert_mm_to_pixels(self, mm: float) -> float:
        """Convert millimeter measurement to pixels"""
        return mm * self.pixels_per_mm
    
    @classmethod
    def from_scale(cls, scale_factor: float, confidence: float = 0.8) -> 'CalibrationResult':
        """
        Create calibration result from traditional scale factor.
        This is a fallback when auto-calibration fails.
        
        Args:
            scale_factor: e.g., 100 for 1:100 scale
            confidence: Confidence in the scale detection
        """
        # Assuming A3 at 300 DPI
        # A3 = 420mm wide, at 300 DPI = 4961 pixels
        # At 1:100 scale, 420mm represents 42000mm
        # So pixels_per_mm = 4961 / 42000 = 0.118
        
        # This is a rough approximation - better to use auto-calibration
        a3_width_mm = 420
        a3_width_pixels_300dpi = 4961
        real_world_width = a3_width_mm * scale_factor
        pixels_per_mm = a3_width_pixels_300dpi / real_world_width
        
        return cls(
            method=CalibrationMethod.SCALE_NOTATION,
            pixels_per_mm=pixels_per_mm,
            mm_per_pixel=1.0 / pixels_per_mm,
            confidence=confidence * 0.7,  # Lower confidence for scale-based
            reference_components=[f"Scale 1:{int(scale_factor)}"],
            calibration_details={
                "scale_factor": scale_factor,
                "assumed_dpi": 300,
                "assumed_paper_size": "A3"
            },
            status="scale_based"
        )
    
    @classmethod
    def none(cls) -> 'CalibrationResult':
        """Create a null calibration result when calibration fails"""
        return cls(
            method=CalibrationMethod.NONE,
            pixels_per_mm=0,
            mm_per_pixel=0,
            confidence=0,
            reference_components=[],
            calibration_details={"error": "No calibration available"},
            status="failed"
        )


@dataclass
class SpacingPattern:
    """Detected spacing pattern (e.g., joists at regular intervals)"""
    spacing_mm: float  # Expected spacing in mm
    detected_intervals: List[float]  # Measured intervals in pixels
    confidence: float
    direction: str  # "horizontal" or "vertical"
    
    @property
    def average_interval_pixels(self) -> float:
        """Average detected interval in pixels"""
        if self.detected_intervals:
            return sum(self.detected_intervals) / len(self.detected_intervals)
        return 0
    
    @property
    def pixels_per_mm(self) -> float:
        """Calculate pixels per mm from this pattern"""
        if self.spacing_mm > 0 and self.average_interval_pixels > 0:
            return self.average_interval_pixels / self.spacing_mm
        return 0