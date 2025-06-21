from fastapi import APIRouter
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

router = APIRouter()

# No need for start-agent/stop-agent endpoints
# The LiveKit agent should be running independently
# When users join rooms, LiveKit will automatically dispatch agents

class ChatRequest(BaseModel):
    message: str
    session_id: str

@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Handles text-based chat requests.
    """
    session_id = request.session_id
    if not session_id:
        session_id = str(uuid4())

    config = {"configurable": {"thread_id": session_id}}
    messages = [HumanMessage(content=request.message)]

    async def event_stream():
        for chunk in stream_chat_graph(messages, config):
            if "agent" in chunk:
                # It's a message from the agent
                content = chunk["agent"]["messages"][-1].content
                yield f"data: {json.dumps({'content': content})}\n\n"
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