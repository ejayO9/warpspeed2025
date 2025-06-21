import asyncio
from livekit.agents import JobContext, Worker, llm, stt, tts
from livekit.plugins import deepgram, elevenlabs, openai
from app.config import settings
from .graph import stream_chat
from langchain_core.messages import HumanMessage
from uuid import uuid4

async def entrypoint(ctx: JobContext):
    # Initialize plugins
    stt_plugin = deepgram.STT()
    tts_plugin = elevenlabs.TTS(api_key=settings.elevenlabs_api_key)
    
    # Start STT
    stt_stream = stt_plugin.stream(ctx.audio_in)
    
    # Start TTS
    tts_stream = tts.Synthesizer(
        ctx, 
        tts=tts_plugin,
        model_id="eleven_turbo_v2",
        voice=tts.Voice(
            id='21m00Tcm4TlvDq8ikWAM', # Example Voice
            name='Rachel' 
        )
    )

    # Generate a unique session ID for the conversation
    session_id = str(uuid4())
    config = {"configurable": {"thread_id": session_id}}

    async for transcript in stt_stream:
        if not transcript.is_final:
            continue

        # Get response from the LangGraph agent
        messages = [HumanMessage(content=transcript.text)]
        llm_stream = stream_chat(messages, config)
        
        # Stream the LLM response to the TTS stream
        await tts_stream.say(llm_stream)

    await tts_stream.flush()

async def shutdown_hook(worker: Worker):
    # This hook is called when the worker is shutting down
    pass

if __name__ == "__main__":
    worker = Worker(
        entrypoint_fnc=entrypoint,
        shutdown_hook_fnc=shutdown_hook,
        worker_type="agent",
    )
    # The worker will automatically connect to the LiveKit server
    # using the environment variables LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET
    asyncio.run(worker.run()) 