"""
Automatic calibration system using standard structural components.

This module implements intelligent calibration by detecting and measuring
standard components with known dimensions, eliminating manual scale input.
"""

import logging
from typing import List, Dict, Optional, Tuple, Any
import statistics
from dataclasses import dataclass

from .calibration_types import (
    CalibrationMethod,
    ComponentDetection,
    CalibrationCandidate,
    CalibrationResult,
    SpacingPattern
)
from .standard_components import (
    get_component_dimension,
    parse_timber_size,
    STEEL_SECTIONS,
    TIMBER_SECTIONS,
    STANDARD_SPACINGS
)

logger = logging.getLogger(__name__)


class AutoCalibrator:
    """
    Automatic calibration system that detects standard components
    and uses their known dimensions to establish pixel-to-mm conversion.
    """
    
    def __init__(self, min_confidence: float = 0.7):
        """
        Initialize the auto calibrator.
        
        Args:
            min_confidence: Minimum confidence threshold for accepting calibrations
        """
        self.min_confidence = min_confidence
        self.calibration_methods = [
            self._calibrate_from_steel_sections,
            self._calibrate_from_timber_sizes,
            self._calibrate_from_spacing_patterns
        ]
    
    def auto_calibrate(
        self,
        detected_elements: List[Dict[str, Any]],
        image_analysis: Optional[Dict[str, Any]] = None
    ) -> CalibrationResult:
        """
        Perform automatic calibration using multiple methods.
        
        Args:
            detected_elements: List of elements detected by Claude Vision
            image_analysis: Additional image analysis data
        
        Returns:
            CalibrationResult with the best calibration found
        """
        logger.info("Starting auto-calibration with %d detected elements", len(detected_elements))
        
        # Extract components from detected elements
        components = self._extract_components(detected_elements)
        logger.info("Extracted %d components for calibration", len(components))
        
        # Try each calibration method
        candidates = []
        for method in self.calibration_methods:
            try:
                candidate = method(components, detected_elements)
                if candidate and candidate.confidence >= self.min_confidence:
                    candidates.append(candidate)
                    logger.info(
                        "Calibration method %s: %.2f pixels/mm (confidence: %.2f)",
                        candidate.method.value,
                        candidate.pixels_per_mm,
                        candidate.confidence
                    )
            except Exception as e:
                logger.error("Error in calibration method: %s", str(e))
        
        # Select the best calibration
        if candidates:
            best_candidate = self._select_best_calibration(candidates)
            return self._create_calibration_result(best_candidate)
        
        logger.warning("No suitable calibration found")
        return CalibrationResult.none()
    
    def _extract_components(self, detected_elements: List[Dict[str, Any]]) -> List[ComponentDetection]:
        """Extract calibratable components from detected elements."""
        components = []
        
        for element in detected_elements:
            # Extract label and measurements
            label = element.get("label", "").upper()
            measurements = element.get("measurements", {})
            confidence = element.get("confidence", 0.5)
            
            # Skip if no measurements
            if not measurements:
                continue
            
            # Check if it's a steel section
            if label in STEEL_SECTIONS:
                # Use depth for horizontal beams, flange width for visible flanges
                if "height_pixels" in measurements:
                    components.append(ComponentDetection(
                        label=label,
                        component_type="steel",
                        pixel_dimension=measurements["height_pixels"],
                        expected_mm=STEEL_SECTIONS[label]["depth"],
                        confidence=confidence,
                        location=element.get("location"),
                        measurement_axis="vertical"
                    ))
                
                if "width_pixels" in measurements:
                    # For some sections, width might be the flange
                    expected_width = STEEL_SECTIONS[label].get("flange_width")
                    if expected_width:
                        components.append(ComponentDetection(
                            label=f"{label}_flange",
                            component_type="steel",
                            pixel_dimension=measurements["width_pixels"],
                            expected_mm=expected_width,
                            confidence=confidence * 0.9,  # Slightly lower confidence for flanges
                            location=element.get("location"),
                            measurement_axis="horizontal"
                        ))
            
            # Check if it's a timber size
            timber_size = parse_timber_size(label)
            if timber_size:
                width_mm, depth_mm = timber_size
                logger.info(f"Parsed timber size from '{label}': {width_mm}x{depth_mm}mm")
                
                # Match measured dimensions to expected
                if "width_pixels" in measurements:
                    logger.info(f"Found width measurement: {measurements['width_pixels']} pixels for {width_mm}mm")
                    components.append(ComponentDetection(
                        label=label,
                        component_type="timber",
                        pixel_dimension=measurements["width_pixels"],
                        expected_mm=width_mm,
                        confidence=confidence,
                        location=element.get("location"),
                        measurement_axis="horizontal"
                    ))
                
                if "height_pixels" in measurements:
                    logger.info(f"Found height measurement: {measurements['height_pixels']} pixels for {depth_mm}mm")
                    components.append(ComponentDetection(
                        label=label,
                        component_type="timber",
                        pixel_dimension=measurements["height_pixels"],
                        expected_mm=depth_mm,
                        confidence=confidence,
                        location=element.get("location"),
                        measurement_axis="vertical"
                    ))
                
                if not any(key in measurements for key in ["width_pixels", "height_pixels"]):
                    logger.warning(f"No pixel measurements found for timber '{label}'. Available keys: {list(measurements.keys())}")
            
            # Check for spacing notations
            if any(spacing in label for spacing in ["CTS", "@"]):
                spacing_mm = None
                for key, value in STANDARD_SPACINGS.items():
                    if key in label:
                        spacing_mm = value
                        break
                
                if spacing_mm and "spacing_pixels" in measurements:
                    components.append(ComponentDetection(
                        label=label,
                        component_type="spacing",
                        pixel_dimension=measurements["spacing_pixels"],
                        expected_mm=spacing_mm,
                        confidence=confidence,
                        location=element.get("location")
                    ))
        
        return components
    
    def _calibrate_from_steel_sections(
        self,
        components: List[ComponentDetection],
        detected_elements: List[Dict]
    ) -> Optional[CalibrationCandidate]:
        """Calibrate using steel section dimensions."""
        steel_components = [c for c in components if c.component_type == "steel"]
        
        if not steel_components:
            return None
        
        # Calculate pixels per mm for each component
        ratios = []
        for component in steel_components:
            ratio = component.pixels_per_mm
            if ratio > 0:
                ratios.append(ratio)
        
        if not ratios:
            return None
        
        # Calculate statistics
        avg_ratio = statistics.mean(ratios)
        variance = statistics.variance(ratios) if len(ratios) > 1 else 0
        
        # Higher confidence for steel due to precise manufacturing
        base_confidence = 0.95
        confidence = base_confidence * (1 - min(variance * 10, 0.5))
        
        return CalibrationCandidate(
            method=CalibrationMethod.STEEL_SECTION,
            components=steel_components,
            pixels_per_mm=avg_ratio,
            confidence=confidence,
            variance=variance
        )
    
    def _calibrate_from_timber_sizes(
        self,
        components: List[ComponentDetection],
        detected_elements: List[Dict]
    ) -> Optional[CalibrationCandidate]:
        """Calibrate using timber dimensions."""
        timber_components = [c for c in components if c.component_type == "timber"]
        
        if not timber_components:
            return None
        
        # Calculate pixels per mm for each component
        ratios = []
        for component in timber_components:
            ratio = component.pixels_per_mm
            if ratio > 0:
                ratios.append(ratio)
        
        if not ratios:
            return None
        
        # Calculate statistics
        avg_ratio = statistics.mean(ratios)
        variance = statistics.variance(ratios) if len(ratios) > 1 else 0
        
        # Good confidence for timber, especially LVL
        base_confidence = 0.90
        confidence = base_confidence * (1 - min(variance * 10, 0.5))
        
        return CalibrationCandidate(
            method=CalibrationMethod.TIMBER_SIZE,
            components=timber_components,
            pixels_per_mm=avg_ratio,
            confidence=confidence,
            variance=variance
        )
    
    def _calibrate_from_spacing_patterns(
        self,
        components: List[ComponentDetection],
        detected_elements: List[Dict]
    ) -> Optional[CalibrationCandidate]:
        """Calibrate using regular spacing patterns."""
        spacing_components = [c for c in components if c.component_type == "spacing"]
        
        # Need at least 2 spacing measurements for reliability
        if len(spacing_components) < 2:
            return None
        
        # Group by spacing value
        spacing_groups = {}
        for component in spacing_components:
            spacing_mm = component.expected_mm
            if spacing_mm not in spacing_groups:
                spacing_groups[spacing_mm] = []
            spacing_groups[spacing_mm].append(component)
        
        # Find the most common spacing
        largest_group = max(spacing_groups.values(), key=len)
        
        # Calculate pixels per mm
        ratios = []
        for component in largest_group:
            ratio = component.pixels_per_mm
            if ratio > 0:
                ratios.append(ratio)
        
        if not ratios:
            return None
        
        # Calculate statistics
        avg_ratio = statistics.mean(ratios)
        variance = statistics.variance(ratios) if len(ratios) > 1 else 0
        
        # Moderate confidence for spacings
        base_confidence = 0.85
        confidence = base_confidence * (1 - min(variance * 10, 0.5))
        
        # Boost confidence if we have many consistent measurements
        if len(ratios) >= 3 and variance < 0.01:
            confidence = min(confidence * 1.1, 0.95)
        
        return CalibrationCandidate(
            method=CalibrationMethod.SPACING_PATTERN,
            components=largest_group,
            pixels_per_mm=avg_ratio,
            confidence=confidence,
            variance=variance
        )
    
    def _select_best_calibration(self, candidates: List[CalibrationCandidate]) -> CalibrationCandidate:
        """Select the best calibration from candidates."""
        # Sort by reliability score
        sorted_candidates = sorted(
            candidates,
            key=lambda c: c.reliability_score,
            reverse=True
        )
        
        best = sorted_candidates[0]
        
        # Log comparison
        logger.info("Calibration candidates:")
        for candidate in sorted_candidates:
            logger.info(
                "  %s: %.3f px/mm, confidence=%.2f, components=%d, score=%.2f",
                candidate.method.value,
                candidate.pixels_per_mm,
                candidate.confidence,
                candidate.component_count,
                candidate.reliability_score
            )
        
        return best
    
    def _create_calibration_result(self, candidate: CalibrationCandidate) -> CalibrationResult:
        """Create final calibration result from selected candidate."""
        # Get component labels for reference
        reference_components = list(set(c.label for c in candidate.components))
        
        # Create detailed information
        details = {
            "method": candidate.method.value,
            "component_count": len(candidate.components),
            "variance": candidate.variance,
            "measurements": [
                {
                    "component": c.label,
                    "pixels": c.pixel_dimension,
                    "expected_mm": c.expected_mm,
                    "ratio": c.pixels_per_mm
                }
                for c in candidate.components[:5]  # Limit to first 5 for brevity
            ]
        }
        
        return CalibrationResult(
            method=candidate.method,
            pixels_per_mm=candidate.pixels_per_mm,
            mm_per_pixel=1.0 / candidate.pixels_per_mm,
            confidence=candidate.confidence,
            reference_components=reference_components,
            calibration_details=details,
            status="auto_calibrated"
        )
    
    def validate_calibration(
        self,
        calibration: CalibrationResult,
        test_measurements: List[Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Validate a calibration against known measurements.
        
        Args:
            calibration: The calibration to validate
            test_measurements: List of {"pixels": float, "expected_mm": float}
        
        Returns:
            Validation results with accuracy metrics
        """
        if not test_measurements:
            return {"valid": True, "message": "No test measurements provided"}
        
        errors = []
        for measurement in test_measurements:
            pixels = measurement["pixels"]
            expected_mm = measurement["expected_mm"]
            calculated_mm = calibration.convert_pixels_to_mm(pixels)
            error_mm = abs(calculated_mm - expected_mm)
            error_percent = (error_mm / expected_mm) * 100
            
            errors.append({
                "expected_mm": expected_mm,
                "calculated_mm": calculated_mm,
                "error_mm": error_mm,
                "error_percent": error_percent
            })
        
        avg_error_percent = statistics.mean(e["error_percent"] for e in errors)
        max_error_percent = max(e["error_percent"] for e in errors)
        
        # Consider calibration valid if average error < 5% and max error < 10%
        is_valid = avg_error_percent < 5.0 and max_error_percent < 10.0
        
        return {
            "valid": is_valid,
            "average_error_percent": avg_error_percent,
            "max_error_percent": max_error_percent,
            "errors": errors,
            "message": "Calibration validated" if is_valid else "Calibration accuracy outside acceptable range"
        }