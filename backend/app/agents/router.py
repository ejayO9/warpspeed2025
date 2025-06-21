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
from livekit.access_token import AccessToken
from livekit.agents import JobRequest, Worker
from livekit.plugins import deepgram, elevenlabs

router = APIRouter()

# In-memory store for workers for simplicity
# In a production app, you might use a more robust solution like Redis
agent_workers = {}

class StartAgentRequest(BaseModel):
    room_name: str

@router.post("/start-agent")
async def start_agent(request: StartAgentRequest):
    room_name = request.room_name
    
    if room_name in agent_workers:
        return JSONResponse(content={"message": "Agent already running in this room"}, status_code=400)

    # Create and run a new worker
    try:
        from .livekit_agent import entrypoint, shutdown_hook # Local import
        
        worker = Worker(
            entrypoint_fnc=entrypoint,
            shutdown_hook_fnc=shutdown_hook,
            worker_type="agent",
        )
        agent_workers[room_name] = worker
        
        # This will run the worker in the background
        # The worker automatically connects using environment variables
        asyncio.create_task(worker.run())
        
        # Dispatch a job to the worker to join the room
        job = JobRequest(room=room_name)
        worker.submit_job(job)

        return JSONResponse(content={"message": f"Agent started in room {room_name}"})
    except Exception as e:
        logging.error(f"Failed to start agent: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.post("/stop-agent")
async def stop_agent(request: StartAgentRequest):
    room_name = request.room_name
    if room_name in agent_workers:
        worker = agent_workers.pop(room_name)
        await worker.shutdown()
        return JSONResponse(content={"message": "Agent stopped"})
    return JSONResponse(content={"error": "Agent not found in this room"}, status_code=404)

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
        async for chunk in stream_chat_graph(messages, config):
            if "agent" in chunk:
                # It's a message from the agent
                content = chunk["agent"]["messages"][-1].content
                yield f"data: {json.dumps({'content': content})}\\n\\n"
                await asyncio.sleep(0.01)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/livekit-token")
async def get_livekit_token(user_id: str, room_name: str):
    """
    Generates a LiveKit token for a user.
    """
    if not all([settings.livekit_api_key, settings.livekit_api_secret, settings.livekit_url]):
        return JSONResponse(content={"error": "LiveKit server not configured"}, status_code=500)

    try:
        token = AccessToken(
            settings.livekit_api_key,
            settings.livekit_api_secret
        ).with_identity(user_id).with_name("Financial Assistant").with_grants(
            room_join=True,
            room=room_name,
            can_publish_data=True,
            can_publish_sources=["microphone"]
        ).to_jwt()

        return JSONResponse(content={"token": token})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500) 