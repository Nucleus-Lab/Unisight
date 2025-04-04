import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from .models import VisualizationDB

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Database operations for visualization
def create_visualization(db, canvas_id: int, json_data: str):
    new_visualization = VisualizationDB(
        canvas_id=canvas_id,
        json_data=json_data,
        created_at=datetime.utcnow()
    )
    db.add(new_visualization)
    db.commit()
    db.refresh(new_visualization)
    return new_visualization

def get_visualizations_for_canvas(db, canvas_id: int) -> List[VisualizationDB]:
    return db.query(VisualizationDB)\
        .filter(VisualizationDB.canvas_id == canvas_id)\
        .order_by(VisualizationDB.created_at.asc())\
        .all()