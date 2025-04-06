from fastapi import APIRouter, Request, HTTPException
from typing import List, Dict, Any
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for webhook events (for MVP)
# In production, this should be replaced with a proper database
webhook_events = []

@router.post("/nodit")
async def receive_nodit_webhook(request: Request):
    """
    Endpoint to receive webhooks from Nodit.
    """
    try:
        # Get the raw body
        body = await request.json()

        # Create a new event entry
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": body.get("type", "unknown"),
            "data": body,
            "status": "success"
        }
        
        # Store the event (in memory for MVP)
        webhook_events.append(event)
        logger.info(f"Total webhook events after append: {len(webhook_events)}")
        
        # Keep only the last 100 events
        if len(webhook_events) > 100:
            webhook_events.pop(0)
            logger.info("Removed oldest event to maintain 100 event limit")
        
        return {"status": "success", "message": "Webhook received"}
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        # Store the error event
        error_event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "error",
            "data": {"error": str(e)},
            "status": "error"
        }
        webhook_events.append(error_event)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events")
async def get_webhook_events() -> List[Dict[str, Any]]:
    """
    Retrieve the list of webhook events.
    Returns the events in reverse chronological order (newest first).
    """
    try:
        logger.info(f"Getting webhook events. Current count: {len(webhook_events)}")
        # Return events in reverse chronological order
        sorted_events = sorted(webhook_events, key=lambda x: x["timestamp"], reverse=True)
        logger.info(f"Returning {len(sorted_events)} webhook events")
        return sorted_events
    except Exception as e:
        logger.error(f"Error retrieving webhook events: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nodit/latest")
async def get_latest_webhook_event():
    """
    Get the most recent webhook event.
    """
    try:
        if not webhook_events:
            return None
        # Return the most recent event
        return sorted(webhook_events, key=lambda x: x["timestamp"], reverse=True)[0]
    except Exception as e:
        logger.error(f"Error retrieving latest webhook event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
