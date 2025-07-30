"""
Calibration module for automatic scale detection using standard components.

This module provides automatic calibration by detecting standard structural
components with known dimensions, eliminating the need for manual scale input.
"""

from .auto_calibrator import AutoCalibrator
from .calibration_types import CalibrationResult, CalibrationMethod, ComponentDetection
from .standard_components import (
    STEEL_SECTIONS,
    TIMBER_SECTIONS,
    STANDARD_SPACINGS,
    get_component_dimension
)

__all__ = [
    'AutoCalibrator',
    'CalibrationResult',
    'CalibrationMethod',
    'ComponentDetection',
    'STEEL_SECTIONS',
    'TIMBER_SECTIONS', 
    'STANDARD_SPACINGS',
    'get_component_dimension'
]