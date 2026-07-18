"""
FastAPI Route Handlers for the Maintenance Intelligence Agent Network.
"""

from fastapi import APIRouter, HTTPException, status
import logging

# Importing our newly constructed modular intelligence logic service
from services.maintenance_agent import generate_maintenance_report

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance Intelligence Agent"]
)

@router.get("/{equipment}", status_code=status.HTTP_200_OK)
async def get_maintenance_report(equipment: str):
    """
    Fetches real-time structural health diagnoses, operational risks, 
    and predictive maintenance schedules for a given physical asset.
    
    Unifies Graph networks and semantic indexes via Gemini 2.5 Flash.
    """
    logger.info(f"API Request HTTP GET received for asset maintenance compilation on: '{equipment}'")
    
    if not equipment or equipment.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The equipment parameter cannot be null, empty, or whitespace-only strings."
        )
        
    try:
        report_payload = generate_maintenance_report(equipment)
        
        return {
            "status": "success",
            "data": report_payload
        }
        
    except FileNotFoundError as fnf:
        logger.warning(f"Target entity '{equipment}' could not be resolved across active nodes: {str(fnf)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset identity '{equipment}' does not exist within current system nodes."
        )
    except Exception as e:
        logger.critical(f"Unhandled downstream system failure processing endpoint for asset {equipment}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during system runtime while generating the engineering asset assessment."
        )
