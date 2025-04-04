from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from database.visualization import get_visualizations_for_canvas

from typing import Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class VisualizationResponse(BaseModel):
    visualization_id: int
    json_data: dict
    created_at: datetime

@router.get("/canvas/{canvas_id}/first-visualization", response_model=Optional[VisualizationResponse])
async def get_canvas_first_visualization(
    canvas_id: int,
    db: Session = Depends(get_db)
):
    visualizations = get_visualizations_for_canvas(db, canvas_id)
    if not visualizations:
        return None
    return visualizations[0]