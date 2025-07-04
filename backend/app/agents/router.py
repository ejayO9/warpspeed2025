from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from uuid import uuid4
import logging

from app.config import settings
from .graph import stream_chat as stream_chat_graph
from langchain_core.messages import HumanMessage
from livekit.api.access_token import AccessToken
from livekit import api
import asyncio
from app.services.websocket_manager import manager

router = APIRouter()

# No need for start-agent/stop-agent endpoints
# The LiveKit agent should be running independently
# When users join rooms, LiveKit will automatically dispatch agents

class ChatRequest(BaseModel):
    message: str
    session_id: str
    user_id: int  # Add user_id to the request

class TestRedirectRequest(BaseModel):
    user_id: str
    redirect_to: str

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time communication"""
    await manager.connect(websocket, user_id)
    try:
        # Send a welcome message to confirm connection
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected successfully"
        }))
        
        # Keep connection alive - listen for any incoming messages or disconnection
        while True:
            try:
                # Wait for messages from client (or disconnection)
                message = await websocket.receive_text()
                # Echo back any messages received
                await websocket.send_text(f"Echo: {message}")
            except WebSocketDisconnect:
                break  # Exit the loop when client disconnects
                
    except WebSocketDisconnect:
        pass  # Normal disconnection
    except Exception as e:
        logging.error(f"WebSocket error for user {user_id}: {e}")
    finally:
        manager.disconnect(websocket, user_id)
        logging.info(f"User {user_id} disconnected")

@router.post("/test-redirect")
async def test_redirect(request: TestRedirectRequest):
    """Test endpoint to verify redirect functionality"""
    await manager.send_redirect(request.user_id, request.redirect_to)
    return JSONResponse(content={
        "status": "success",
        "message": f"Redirect sent to user {request.user_id} for {request.redirect_to}"
    })

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Handles text-based chat requests.
    """
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid4())

    config = {"configurable": {"thread_id": session_id}}
    
    # Create the user message - LangGraph will handle conversation history automatically
    messages = [HumanMessage(content=request.message)]

    async def event_stream():
        for chunk in stream_chat_graph(messages, config, user_id=request.user_id):
            # Handle different agent outputs
            if "conversation_agent" in chunk:
                # Message from conversation agent
                content = chunk["conversation_agent"]["messages"][-1].content
                yield f"data: {json.dumps({'content': content, 'agent': 'conversation'})}\n\n"
                    
            elif "analysis_agent" in chunk:
                # Message from analysis agent
                content = chunk["analysis_agent"]["messages"][-1].content
                yield f"data: {json.dumps({'content': content, 'agent': 'analysis'})}\n\n"
            await asyncio.sleep(0.01)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/livekit-token")
async def get_livekit_token(user_id: str, room_name: str):
    """
    Generates a LiveKit token for a user.
    """
    if not all([settings.livekit_api_key, settings.livekit_api_secret, settings.livekit_url]):
        return JSONResponse(content={"error": "LiveKit server not configured"}, status_code=500)

    # try:
    #     token = AccessToken(
    #         settings.livekit_api_key,
    #         settings.livekit_api_secret
    #     ).with_identity(user_id).with_name("Financial Assistant").with_grants(
    #         room_join=True,
    #         room=room_name,
    #         can_publish_data=True,
    #         can_publish_sources=["microphone"]
    #     ).to_jwt()

    #     return JSONResponse(content={"token": token})
    # except Exception as e:
    #     return JSONResponse(content={"error": str(e)}, status_code=500) 
    
    try:
        token = (
            api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
            .with_identity(user_id)
            .with_name("Financial Assistant")
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish_data=True,         # optional
                can_publish_sources=["microphone"], # optional
            ))
            .to_jwt()
        )
        return JSONResponse(content={"token": token})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)