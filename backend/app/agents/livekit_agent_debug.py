import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, llm, stt, tts, AgentSession, Agent
from livekit.plugins import deepgram, elevenlabs, openai, silero
from app.config import settings
from app.agents.graph import stream_chat
from langchain_core.messages import HumanMessage, SystemMessage
from uuid import uuid4
import logging

# Load environment variables
load_dotenv()

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DebugFinancialLLM(llm.LLM):
    """Debug version of Financial LLM with extensive logging."""
    
    def __init__(self):
        super().__init__()
        self.session_id = str(uuid4())
        self.config = {"configurable": {"thread_id": self.session_id}}
        logger.info(f"🤖 DebugFinancialLLM initialized with session ID: {self.session_id}")
        self.message_count = 0

    async def achat(self, chat_ctx: llm.ChatContext) -> llm.ChatResponse:
        """Generate response using our chat graph with debug logging."""
        self.message_count += 1
        logger.info(f"💬 [Message #{self.message_count}] achat called")
        logger.debug(f"📝 Chat context has {len(chat_ctx.messages)} messages")
        
        try:
            # Log all messages in context
            for i, msg in enumerate(chat_ctx.messages):
                logger.debug(f"📋 Message {i}: Role={msg.role}, Content='{msg.content[:100]}...'")
            
            # Get the last user message
            user_message = None
            for msg in reversed(chat_ctx.messages):
                if msg.role == llm.ChatRole.USER:
                    user_message = msg.content
                    break
            
            if not user_message:
                user_message = "Hello"
                logger.warning("⚠️ No user message found, using default greeting")
            
            logger.info(f"🎤 Processing user message: '{user_message}'")
            
            # Process through our chat graph
            messages = [HumanMessage(content=user_message)]
            logger.debug(f"🔄 Calling stream_chat with config: {self.config}")
            
            response_content = ""
            chunk_count = 0
            for chunk in stream_chat(messages, self.config):
                chunk_count += 1
                logger.debug(f"📦 Chunk {chunk_count}: {list(chunk.keys())}")
                
                if "agent" in chunk:
                    agent_messages = chunk["agent"]["messages"]
                    logger.debug(f"🤖 Agent messages count: {len(agent_messages)}")
                    
                    if agent_messages:
                        response_content = agent_messages[-1].content
                        logger.debug(f"📝 Extracted response: '{response_content[:100]}...'")
                        break
            
            if not response_content:
                response_content = "I'm sorry, I couldn't process your request. Could you please try again?"
                logger.warning("⚠️ No response content generated, using fallback")
            
            logger.info(f"✅ Generated response: '{response_content}'")
            
            return llm.ChatResponse(
                content=response_content,
                role=llm.ChatRole.ASSISTANT
            )
            
        except Exception as e:
            logger.error(f"💥 Error in DebugFinancialLLM: {str(e)}", exc_info=True)
            return llm.ChatResponse(
                content="I'm sorry, I encountered an error. Could you please try again?",
                role=llm.ChatRole.ASSISTANT
            )

class DebugFinancialAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful financial assistant. Your goal is to help users with their financial questions. Be polite and professional.")
        logger.info("🤖 DebugFinancialAssistant initialized")

async def entrypoint(ctx: JobContext):
    """
    Debug version of the LiveKit agent entrypoint.
    """
    logger.info("🚀 Agent entrypoint started for room: %s", ctx.room.name)
    logger.info(f"🔗 LiveKit URL: {settings.livekit_url}")

    try:
        # Create session with our custom LLM and other components
        logger.info("🔧 Creating STT, LLM, and TTS components...")
        
        stt_component = deepgram.STT(
            model="nova-2",
            api_key=settings.deepgram_api_key
        )
        logger.info("✅ STT (Deepgram) created")
        
        llm_component = DebugFinancialLLM()
        logger.info("✅ LLM (Custom Financial) created")
        
        tts_component = elevenlabs.TTS(
            api_key=settings.elevenlabs_api_key,
            voice_id="NeDTo4pprKj2ZwuNJceH",
            model="eleven_turbo_v2_5"
        )
        logger.info("✅ TTS (ElevenLabs) created")
        
        vad_component = silero.VAD.load()
        logger.info("✅ VAD (Silero) loaded")

        session = AgentSession(
            stt=stt_component,
            llm=llm_component,
            tts=tts_component,
            vad=vad_component,
            turn_detection="vad"
        )
        logger.info("✅ AgentSession created")

        # Start the session
        logger.info("🏁 Starting session...")
        await session.start(
            room=ctx.room,
            agent=DebugFinancialAssistant(),
        )
        logger.info("✅ Session started")

        # Connect to the room
        logger.info("🔗 Connecting to room...")
        await ctx.connect()
        logger.info("✅ Connected to room")

        logger.info("🎉 Financial assistant session started and ready for conversation")

        # Generate initial greeting
        logger.info("👋 Generating initial greeting...")
        await session.generate_reply(
            instructions="Greet the user warmly and offer your assistance with financial questions."
        )
        logger.info("✅ Initial greeting sent")
        
        # Keep the session alive and log periodic status
        logger.info("🕐 Entering keep-alive loop...")
        loop_count = 0
        while True:
            await asyncio.sleep(10)  # Check every 10 seconds
            loop_count += 1
            logger.debug(f"💓 Keep-alive loop #{loop_count} - Session active")

    except Exception as e:
        logger.error(f"💥 Error in entrypoint: {str(e)}", exc_info=True)
        raise


async def shutdown_hook(worker):
    """
    Cleanup hook called when the worker is shutting down.
    """
    logger.info("🛑 Worker shutting down.")


if __name__ == "__main__":
    logger.info("🔍 Starting debug LiveKit agent...")
    
    # Load environment variables
    load_dotenv()
    
    # Log configuration
    logger.info(f"🔑 LIVEKIT_URL: {settings.livekit_url}")
    logger.info(f"🔑 LIVEKIT_API_KEY: {settings.livekit_api_key[:8]}...")
    logger.info(f"🔑 DEEPGRAM_API_KEY: {'SET' if settings.deepgram_api_key else 'NOT SET'}")
    logger.info(f"🔑 ELEVENLABS_API_KEY: {'SET' if settings.elevenlabs_api_key else 'NOT SET'}")
    logger.info(f"🔑 OPENAI_API_KEY: {'SET' if settings.openai_api_key else 'NOT SET'}")
    
    # Create WorkerOptions with LiveKit server configuration
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
    )
    
    logger.info("🚀 Starting LiveKit agent...")
    agents.cli.run_app(worker_options) 