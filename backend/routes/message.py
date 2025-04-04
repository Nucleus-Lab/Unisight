from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database.user import get_user, create_user
from database.canvas import get_canvas, create_canvas

from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from database.message import create_message, get_messages_for_canvas

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

@router.post("/message", response_model=MessageResponse)
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
        
        # Make sure the response includes the canvas_id
        return {
            "message_id": new_message.message_id,
            "canvas_id": canvas.canvas_id,  # Include the canvas_id here
            "text": new_message.text,
            "created_at": new_message.created_at
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