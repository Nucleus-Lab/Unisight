from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import json

from backend.database import get_db
from backend.database.user import get_user, create_user
from backend.database.canvas import get_canvas, create_canvas
from backend.database.visualization import create_visualization
from backend.constants import AI_USER_ID
from backend.database.message import create_message, get_messages_for_canvas, get_message_by_id

from agents.main import main as agent_main

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
    user_id: int

class MessageResponseWithAIResponse(BaseModel):
    message_id: int
    canvas_id: int
    text: str
    created_at: datetime
    visualization_ids: List[int]
    ai_message_id: int
    
@router.post("/message", response_model=MessageResponseWithAIResponse)
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
        results = await agent_main([message.text])
        visualization_ids = []
        for result in results:
            # Parse the json data
            json_data = json.loads(result['fig_json'])
            # Save the json visualization to the database
            visualization = create_visualization(db, canvas.canvas_id, json_data)
            visualization_ids.append(visualization.visualization_id)
            
        print("visualization_ids: ", visualization_ids)
        
        # TODO: Add logic to get analysis from the AI
        analysis = "This is a test analysis"
        
        # Save the analysis as a message from the AI to the database
        ai_message = create_message(
            db,
            canvas_id=canvas.canvas_id,
            user_id=AI_USER_ID,
            text=analysis
        )
        
        print("sending these as response: ", {
            "message_id": new_message.message_id,
            "canvas_id": canvas.canvas_id,  # Include the canvas_id here
            "text": new_message.text,
            "created_at": new_message.created_at,
            "visualization_ids": visualization_ids,
            "ai_message_id": ai_message.message_id
        })
            
        # Make sure the response includes the canvas_id
        return {
            "message_id": new_message.message_id,
            "canvas_id": canvas.canvas_id,  # Include the canvas_id here
            "text": new_message.text,
            "created_at": new_message.created_at,
            "visualization_ids": visualization_ids,
            "ai_message_id": ai_message.message_id
        }

    except Exception as e:
        print(f"Error in send_message: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.get("/canvas/{canvas_id}/messages", response_model=List[MessageResponse])
async def get_canvas_messages(
    canvas_id: int,
    db: Session = Depends(get_db)
):
    messages = get_messages_for_canvas(db, canvas_id)
    return [{
        "message_id": msg.message_id,
        "canvas_id": msg.canvas_id,
        "text": msg.text,
        "created_at": msg.created_at,
        "user_id": msg.user_id,  # Make sure this is included
    } for msg in messages]

@router.get("/canvas/{canvas_id}/first-message", response_model=Optional[MessageResponse])
async def get_canvas_first_message(
    canvas_id: int,
    db: Session = Depends(get_db)
):
    messages = get_messages_for_canvas(db, canvas_id)
    if not messages:
        return None
    return messages[0]


@router.get("/message/{message_id}", response_model=MessageResponse)
async def get_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    try:
        message = get_message_by_id(db, message_id)
        if not message:
            raise HTTPException(
                status_code=404,
                detail=f"Message with id {message_id} not found"
            )
            
        print("message.message_id: ", message.message_id)
        print("message.text: ", message.text)
        print("message.created_at: ", message.created_at)
        print("message.user_id: ", message.user_id)
        print("message.canvas_id: ", message.canvas_id)
        return {
            "message_id": message.message_id,
            "canvas_id": message.canvas_id,
            "text": message.text,
            "created_at": message.created_at,
            "user_id": message.user_id
        }
    except Exception as e:
        print(f"Error getting message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")