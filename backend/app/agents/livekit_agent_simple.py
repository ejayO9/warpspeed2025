import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, AgentSession, Agent
from livekit.plugins import deepgram, elevenlabs, openai, silero
from app.config import settings
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleFinancialAssistant(Agent):
    def __init__(self) -> None:
        # Custom instructions for our financial assistant
        instructions = """You are a helpful financial assistant specializing in personal finance, investments, and financial planning. 
        Your goal is to help users with their financial questions in a polite and professional manner.
        
        You can help with:
        - Investment advice and portfolio analysis
        - Budgeting and expense tracking
        - Retirement planning
        - Tax planning strategies
        - Insurance recommendations
        - Debt management
        - Financial goal setting
        
        Always provide accurate, helpful information while being conversational and easy to understand."""
        
        super().__init__(instructions=instructions)
        logger.info("SimpleFinancialAssistant initialized")

async def entrypoint(ctx: JobContext):
    """
    Simple entrypoint for the LiveKit agent that focuses on basic voice interaction.
    """
    logger.info("🚀 Agent entrypoint started for room: %s", ctx.room.name)

    # Create session with standard components
    logger.info("🔧 Creating session components...")
    
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            api_key=settings.deepgram_api_key
        ),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(
            api_key=settings.elevenlabs_api_key,
            voice_id="NeDTo4pprKj2ZwuNJceH",
            model="eleven_turbo_v2_5"
        ),
        vad=silero.VAD.load(),
        turn_detection="vad"
    )
    
    logger.info("✅ Session components created")

    # Start the session
    logger.info("🏁 Starting session...")
    await session.start(
        room=ctx.room,
        agent=SimpleFinancialAssistant(),
    )
    logger.info("✅ Session started")

    # Connect to the room
    logger.info("🔗 Connecting to room...")
    await ctx.connect()
    logger.info("✅ Connected to room")

    logger.info("🎉 Simple financial assistant is ready for conversation")

    # Generate initial greeting
    logger.info("👋 Sending initial greeting...")
    await session.generate_reply(
        instructions="Greet the user warmly and briefly introduce yourself as their financial assistant. Ask how you can help them today."
    )
    logger.info("✅ Initial greeting sent")


async def shutdown_hook(worker):
    """
    Cleanup hook called when the worker is shutting down.
    """
    logger.info("🛑 Worker shutting down.")


if __name__ == "__main__":
    logger.info("🔍 Starting simple LiveKit financial agent...")
    
    # Load environment variables
    load_dotenv()
    
    # Log configuration (basic check)
    logger.info(f"🔑 LiveKit URL: {settings.livekit_url}")
    logger.info(f"🔑 API Keys configured: {bool(settings.livekit_api_key and settings.deepgram_api_key and settings.elevenlabs_api_key and settings.openai_api_key)}")
    
    # Create WorkerOptions with LiveKit server configuration
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )
    
    logger.info("🚀 Starting LiveKit agent...")
    agents.cli.run_app(worker_options) 