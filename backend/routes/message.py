from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.database.user import get_user, create_user
from backend.database.canvas import get_canvas, create_canvas
from backend.database.visualization import create_visualization
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from backend.database.message import create_message, get_messages_for_canvas

from archive.visualization import generate_gpt_chart

router = APIRouter()

class MessageRequest(BaseModel):
    canvas_id: Optional[int] = None
    wallet_address: str  # Changed from user_id
    text: str
    
    
class MessageResponse(BaseModel):
    message_id: int
    canvas_id: int
    text: str
    created_at: datetime

class MessageResponseWithVisualizationIds(BaseModel):
    message_id: int
    canvas_id: int
    text: str
    created_at: datetime
    visualization_ids: List[int]
    
@router.post("/message", response_model=MessageResponseWithVisualizationIds)
async def send_message(
    message: MessageRequest,
    db: Session = Depends(get_db)
):
    try:
        # Get or create user from wallet address
        user = get_user(db, message.wallet_address)
        if not user:
            user = create_user(db, message.wallet_address)

        # If no canvas_id, create new canvas
        if message.canvas_id is None:
            canvas = create_canvas(db, user.user_id)
        else:
            # Get existing canvas
            canvas = get_canvas(db, message.canvas_id)
            if not canvas:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Canvas with id {message.canvas_id} not found"
                )
            
            # Verify user has access to this canvas
            if canvas.user_id != user.user_id:
                raise HTTPException(
                    status_code=403, 
                    detail="Not authorized to access this canvas"
                )
        
        # Create the message
        new_message = create_message(
            db,
            canvas_id=canvas.canvas_id,
            user_id=user.user_id,
            text=message.text
        )
        
        # TODO: Add logic to interact with AI
        # assume we got the json data from the AI
        json_data = []
        json_data.append(generate_gpt_chart())
        
        print("json_data: ", json_data)
        
        visualization_ids = []
        for json in json_data:
            # Save the json visualization to the database
            visualization = create_visualization(db, canvas.canvas_id, json)
            visualization_ids.append(visualization.visualization_id)
            
        print("visualization_ids: ", visualization_ids)
            
        # Make sure the response includes the canvas_id
        return {
            "message_id": new_message.message_id,
            "canvas_id": canvas.canvas_id,  # Include the canvas_id here
            "text": new_message.text,
            "created_at": new_message.created_at,
            "visualization_ids": visualization_ids
        }

    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/canvas/{canvas_id}/messages", response_model=List[MessageResponse])
async def get_canvas_messages(
    canvas_id: int,
    db: Session = Depends(get_db)
):
    messages = get_messages_for_canvas(db, canvas_id)
    return messages

@router.get("/canvas/{canvas_id}/first-message", response_model=Optional[MessageResponse])
async def get_canvas_first_message(
    canvas_id: int,
    db: Session = Depends(get_db)
):
    messages = get_messages_for_canvas(db, canvas_id)
    if not messages:
        return None
    return messages[0]