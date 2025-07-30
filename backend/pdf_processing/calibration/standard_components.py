"""
Database of standard structural components with precise dimensions.

All dimensions are in millimeters (mm) as per Australian standards.
This module serves as the reference for automatic calibration.
"""

from typing import Dict, Optional, Tuple, List

# Australian Standard Steel Sections
# Reference: AS/NZS 3679.1
STEEL_SECTIONS = {
    # Parallel Flange Channels (PFC)
    "200PFC": {
        "depth": 200,
        "flange_width": 75,
        "web_thickness": 6,
        "flange_thickness": 11,
        "type": "PFC"
    },
    "250PFC": {
        "depth": 250,
        "flange_width": 90,
        "web_thickness": 8,
        "flange_thickness": 13,
        "type": "PFC"
    },
    "300PFC": {
        "depth": 300,
        "flange_width": 100,
        "web_thickness": 9,
        "flange_thickness": 16,
        "type": "PFC"
    },
    
    # Universal Beams (UB)
    "200UB18": {
        "depth": 198,
        "flange_width": 99,
        "web_thickness": 4.5,
        "flange_thickness": 7,
        "type": "UB"
    },
    "200UB22": {
        "depth": 202,
        "flange_width": 133,
        "web_thickness": 5.0,
        "flange_thickness": 6.8,
        "type": "UB"
    },
    "200UB25": {
        "depth": 203,
        "flange_width": 133,
        "web_thickness": 5.8,
        "flange_thickness": 7.8,
        "type": "UB"
    },
    "250UB25": {
        "depth": 248,
        "flange_width": 124,
        "web_thickness": 5.0,
        "flange_thickness": 8.0,
        "type": "UB"
    },
    "250UB31": {
        "depth": 252,
        "flange_width": 146,
        "web_thickness": 6.1,
        "flange_thickness": 8.6,
        "type": "UB"
    },
    "310UB32": {
        "depth": 298,
        "flange_width": 149,
        "web_thickness": 5.5,
        "flange_thickness": 8.0,
        "type": "UB"
    },
    
    # Universal Columns (UC)
    "200UC46": {
        "depth": 203,
        "flange_width": 203,
        "web_thickness": 7.2,
        "flange_thickness": 11.0,
        "type": "UC"
    },
    "200UC52": {
        "depth": 206,
        "flange_width": 204,
        "web_thickness": 7.9,
        "flange_thickness": 12.5,
        "type": "UC"
    },
    "250UC72": {
        "depth": 254,
        "flange_width": 254,
        "web_thickness": 8.6,
        "flange_thickness": 14.2,
        "type": "UC"
    }
}

# Standard Timber Sizes (LVL and Treated Pine)
# Based on AS1684 and common Australian sizes
TIMBER_SECTIONS = {
    # LVL (Laminated Veneer Lumber)
    "150x45LVL": {"width": 150, "depth": 45, "type": "LVL"},
    "170x45LVL": {"width": 170, "depth": 45, "type": "LVL"},
    "200x45LVL": {"width": 200, "depth": 45, "type": "LVL"},
    "240x45LVL": {"width": 240, "depth": 45, "type": "LVL"},
    "300x45LVL": {"width": 300, "depth": 45, "type": "LVL"},
    "150x63LVL": {"width": 150, "depth": 63, "type": "LVL"},
    "200x63LVL": {"width": 200, "depth": 63, "type": "LVL"},
    "240x63LVL": {"width": 240, "depth": 63, "type": "LVL"},
    "300x63LVL": {"width": 300, "depth": 63, "type": "LVL"},
    
    # Treated Pine / MGP
    "70x35": {"width": 70, "depth": 35, "type": "MGP"},
    "90x35": {"width": 90, "depth": 35, "type": "MGP"},
    "90x45": {"width": 90, "depth": 45, "type": "MGP"},
    "120x35": {"width": 120, "depth": 35, "type": "MGP"},
    "120x45": {"width": 120, "depth": 45, "type": "MGP"},
    "140x45": {"width": 140, "depth": 45, "type": "MGP"},
    "190x45": {"width": 190, "depth": 45, "type": "MGP"},
    
    # Common variations without material type
    "150x45": {"width": 150, "depth": 45, "type": "TIMBER"},
    "170x45": {"width": 170, "depth": 45, "type": "TIMBER"},
    "200x45": {"width": 200, "depth": 45, "type": "TIMBER"},
    "240x45": {"width": 240, "depth": 45, "type": "TIMBER"},
    "300x45": {"width": 300, "depth": 45, "type": "TIMBER"},
}

# Standard Spacings/Centers
STANDARD_SPACINGS = {
    "300CTS": 300,
    "450CTS": 450,
    "600CTS": 600,
    "300 CTS": 300,
    "450 CTS": 450,
    "600 CTS": 600,
    "@300": 300,
    "@450": 450,
    "@600": 600,
    "@ 300": 300,
    "@ 450": 450,
    "@ 600": 600,
}

# Standard door and window sizes for additional calibration
STANDARD_OPENINGS = {
    "DOOR_820": 820,    # Standard door
    "DOOR_870": 870,    # Standard door with frame
    "DOOR_900": 900,    # Wide door
    "WINDOW_600": 600,  # Small window
    "WINDOW_900": 900,  # Standard window
    "WINDOW_1200": 1200, # Large window
}


def get_component_dimension(component_label: str, dimension: str = "primary") -> Optional[float]:
    """
    Get the dimension of a standard component.
    
    Args:
        component_label: Component identifier (e.g., "200PFC", "200x45")
        dimension: Which dimension to return:
            - "primary": Main dimension (depth for steel, width for timber)
            - "secondary": Secondary dimension (flange_width for steel, depth for timber)
            - "depth", "width", "flange_width", etc.: Specific dimension
    
    Returns:
        Dimension in mm, or None if not found
    """
    # Clean up the label
    label = component_label.upper().strip()
    
    # Check steel sections
    if label in STEEL_SECTIONS:
        section = STEEL_SECTIONS[label]
        if dimension == "primary":
            return section["depth"]
        elif dimension == "secondary":
            return section["flange_width"]
        else:
            return section.get(dimension)
    
    # Check timber sections
    for key, section in TIMBER_SECTIONS.items():
        if label.replace(" ", "") == key.replace(" ", "").upper():
            if dimension == "primary":
                return section["width"]
            elif dimension == "secondary":
                return section["depth"]
            else:
                return section.get(dimension)
    
    # Check if it's a spacing
    if label in STANDARD_SPACINGS:
        return STANDARD_SPACINGS[label]
    
    return None


def parse_timber_size(size_string: str) -> Optional[Tuple[float, float]]:
    """
    Parse timber size string like "200x45" into (width, depth).
    
    Args:
        size_string: Size string (e.g., "200x45", "200 x 45")
    
    Returns:
        Tuple of (width, depth) in mm, or None if invalid
    """
    import re
    
    # Match patterns like "200x45", "200 x 45", "200X45"
    match = re.match(r'(\d+)\s*[xX]\s*(\d+)', size_string.strip())
    if match:
        width = float(match.group(1))
        depth = float(match.group(2))
        return (width, depth)
    
    return None


def get_calibration_references() -> List[Dict[str, any]]:
    """
    Get a list of all available calibration references sorted by reliability.
    
    Returns:
        List of calibration references with their properties
    """
    references = []
    
    # Steel sections are most reliable (precise manufacturing)
    for label, props in STEEL_SECTIONS.items():
        references.append({
            "label": label,
            "type": "steel",
            "primary_dimension": props["depth"],
            "secondary_dimension": props["flange_width"],
            "reliability": 0.95,  # Very high reliability
            "description": f"{label} - {props['depth']}mm deep"
        })
    
    # LVL is also very reliable
    for label, props in TIMBER_SECTIONS.items():
        if props["type"] == "LVL":
            references.append({
                "label": label,
                "type": "timber_lvl",
                "primary_dimension": props["width"],
                "secondary_dimension": props["depth"],
                "reliability": 0.90,  # High reliability
                "description": f"{label} - {props['width']}x{props['depth']}mm"
            })
    
    # Standard spacings are reliable but need multiple instances
    for label, spacing in STANDARD_SPACINGS.items():
        references.append({
            "label": label,
            "type": "spacing",
            "primary_dimension": spacing,
            "secondary_dimension": None,
            "reliability": 0.85,  # Good reliability with multiple instances
            "description": f"{label} - {spacing}mm centers"
        })
    
    return sorted(references, key=lambda x: x["reliability"], reverse=True)