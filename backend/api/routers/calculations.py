from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from core.calculators.joist_calculator import JoistCalculator
from core.materials.material_system import MaterialSystem

router = APIRouter()

class JoistCalculationRequest(BaseModel):
    span_length: float  # meters
    joist_spacing: float  # meters (0.3, 0.45, 0.6)
    building_level: str  # "GF", "L1", "RF"
    room_type: Optional[str] = None
    load_type: Optional[str] = "residential"

class JoistCalculationResponse(BaseModel):
    joist_count: int
    joist_length: float
    blocking_length: float
    material_specification: str
    reference_code: str
    cutting_list: List[dict]
    calculation_notes: List[str]

@router.post("/joists", response_model=JoistCalculationResponse)
async def calculate_joists(request: JoistCalculationRequest):
    try:
        calculator = JoistCalculator()
        material_system = MaterialSystem()
        
        # Perform joist calculation
        result = calculator.calculate_joists(
            span_length=request.span_length,
            joist_spacing=request.joist_spacing,
            building_level=request.building_level,
            room_type=request.room_type,
            load_type=request.load_type
        )
        
        # Get material specification
        material_spec = material_system.get_joist_material(
            span_length=request.span_length,
            load_type=request.load_type
        )
        
        return JoistCalculationResponse(
            joist_count=result["joist_count"],
            joist_length=result["joist_length"],
            blocking_length=result["blocking_length"],
            material_specification=material_spec["specification"],
            reference_code=result["reference_code"],
            cutting_list=result["cutting_list"],
            calculation_notes=result["calculation_notes"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/materials/joists")
async def get_joist_materials():
    """Get available joist materials and specifications"""
    material_system = MaterialSystem()
    return material_system.get_joist_materials()