#!/usr/bin/env python3
"""
Test auto-calibration functionality with simulated component detections
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_processing.calibration import AutoCalibrator, STEEL_SECTIONS, TIMBER_SECTIONS

def test_steel_calibration():
    """Test calibration using steel sections"""
    print("\n=== Testing Steel Section Calibration ===")
    
    # Simulate detected elements from Claude Vision
    detected_elements = [
        {
            "label": "200PFC",
            "type": "steel_section",
            "confidence": 0.95,
            "measurements": {
                "height_pixels": 85,  # Should be 200mm
                "width_pixels": 32    # Should be 75mm (flange)
            }
        },
        {
            "label": "200UB25",
            "type": "steel_section", 
            "confidence": 0.90,
            "measurements": {
                "height_pixels": 86,  # Should be 203mm
            }
        }
    ]
    
    calibrator = AutoCalibrator()
    result = calibrator.auto_calibrate(detected_elements)
    
    print(f"Status: {result.status}")
    print(f"Method: {result.method.value}")
    print(f"Pixels per mm: {result.pixels_per_mm:.3f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Reference components: {', '.join(result.reference_components)}")
    
    # Test conversion
    test_pixels = 100
    mm = result.convert_pixels_to_mm(test_pixels)
    print(f"\nTest: {test_pixels} pixels = {mm:.1f}mm")
    
    return result

def test_timber_calibration():
    """Test calibration using timber sizes"""
    print("\n=== Testing Timber Size Calibration ===")
    
    detected_elements = [
        {
            "label": "200x45",
            "type": "timber",
            "confidence": 0.92,
            "measurements": {
                "width_pixels": 84,   # Should be 200mm
                "height_pixels": 19   # Should be 45mm
            }
        },
        {
            "label": "150x45 LVL",
            "type": "timber",
            "confidence": 0.88,
            "measurements": {
                "width_pixels": 63,   # Should be 150mm
            }
        }
    ]
    
    calibrator = AutoCalibrator()
    result = calibrator.auto_calibrate(detected_elements)
    
    print(f"Status: {result.status}")
    print(f"Method: {result.method.value}")
    print(f"Pixels per mm: {result.pixels_per_mm:.3f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Reference components: {', '.join(result.reference_components)}")
    
    return result

def test_spacing_calibration():
    """Test calibration using spacing patterns"""
    print("\n=== Testing Spacing Pattern Calibration ===")
    
    detected_elements = [
        {
            "label": "450 CTS",
            "type": "spacing",
            "confidence": 0.85,
            "measurements": {
                "spacing_pixels": 189  # Should be 450mm
            }
        },
        {
            "label": "@450",
            "type": "spacing",
            "confidence": 0.83,
            "measurements": {
                "spacing_pixels": 190
            }
        },
        {
            "label": "450 CTS",
            "type": "spacing", 
            "confidence": 0.87,
            "measurements": {
                "spacing_pixels": 188
            }
        }
    ]
    
    calibrator = AutoCalibrator()
    result = calibrator.auto_calibrate(detected_elements)
    
    print(f"Status: {result.status}")
    print(f"Method: {result.method.value}")
    print(f"Pixels per mm: {result.pixels_per_mm:.3f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Reference components: {', '.join(result.reference_components)}")
    
    return result

def test_mixed_calibration():
    """Test calibration with mixed component types"""
    print("\n=== Testing Mixed Component Calibration ===")
    
    detected_elements = [
        {
            "label": "200PFC",
            "type": "steel_section",
            "confidence": 0.95,
            "measurements": {
                "height_pixels": 85,  # 200mm
            }
        },
        {
            "label": "200x45",
            "type": "timber",
            "confidence": 0.90,
            "measurements": {
                "width_pixels": 84,   # 200mm
            }
        },
        {
            "label": "450 CTS",
            "type": "spacing",
            "confidence": 0.85,
            "measurements": {
                "spacing_pixels": 189  # 450mm
            }
        }
    ]
    
    calibrator = AutoCalibrator()
    result = calibrator.auto_calibrate(detected_elements)
    
    print(f"Status: {result.status}")
    print(f"Method: {result.method.value} (should prefer steel)")
    print(f"Pixels per mm: {result.pixels_per_mm:.3f}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Reference components: {', '.join(result.reference_components)}")
    
    # Validate calibration accuracy
    print("\n=== Validation ===")
    test_measurements = [
        {"pixels": 85, "expected_mm": 200},  # 200PFC depth
        {"pixels": 84, "expected_mm": 200},  # 200x45 width
        {"pixels": 189, "expected_mm": 450}, # 450 CTS
    ]
    
    validation = calibrator.validate_calibration(result, test_measurements)
    print(f"Validation: {'PASSED' if validation['valid'] else 'FAILED'}")
    print(f"Average error: {validation['average_error_percent']:.1f}%")
    print(f"Max error: {validation['max_error_percent']:.1f}%")
    
    return result

def test_no_calibration():
    """Test fallback when no calibration is possible"""
    print("\n=== Testing No Calibration Fallback ===")
    
    detected_elements = [
        {
            "label": "J1",
            "type": "joist",
            "confidence": 0.95,
            "measurements": {
                "width_mm": 200,
                "depth_mm": 45
            }
        }
    ]
    
    calibrator = AutoCalibrator()
    result = calibrator.auto_calibrate(detected_elements)
    
    print(f"Status: {result.status}")
    print(f"Method: {result.method.value}")
    print(f"Message: {result.calibration_details.get('error', 'Unknown')}")
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("AUTO-CALIBRATION TEST SUITE")
    print("=" * 60)
    
    # Run all tests
    test_steel_calibration()
    test_timber_calibration()
    test_spacing_calibration()
    test_mixed_calibration()
    test_no_calibration()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)