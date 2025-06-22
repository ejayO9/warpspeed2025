import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import JobContext, WorkerOptions, AgentSession, Agent
from livekit.agents import ConversationItemAddedEvent
from livekit.plugins import deepgram, elevenlabs, openai, silero
from livekit import rtc  # Add this import for data messages
from app.config import settings
from app.agents.graph import stream_chat
from langchain_core.messages import HumanMessage, SystemMessage
from uuid import uuid4
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialAssistant(Agent):
    def __init__(self, user_id: int = None) -> None:
        # Instructions for the standard OpenAI LLM - aligned with our Agent1
        instructions = """You are FinBuddy, a friendly financial advisor. Your goal is to understand the user's financial situation before analyzing loan options.

        Please collect the following information naturally in conversation:
        1. Source of income - Ask about salary, other income sources, and any expected changes (job change, salary hike, bonus, or income dip)
        2. Upcoming big expenses - Home purchase, children's education, wedding, medical, travel, etc.
        3. Dependents - Spouse, children, parents, and their needs
        4. Any other relevant information they think you should know

        Also, try to understand what purchase they're planning (e.g., car, house) and the approximate amount.

        Be conversational and empathetic. After collecting all information, ask for confirmation: "I have gathered all the information I need. Shall I analyze your loan options now?"
        
        Keep your responses concise but informative, suitable for voice conversation."""
        
        super().__init__(instructions=instructions)
        
        # LangGraph integration
        self.session_id = str(uuid4())
        self.config = {"configurable": {"thread_id": self.session_id}}
        self.user_id = user_id
        
        # Conversation tracking
        self.conversation_buffer = ""
        self.call_start_time = ""
        self.call_status = "ACTIVE"
        
        logger.info(f"FinancialAssistant initialized with session ID: {self.session_id}, user_id: {self.user_id}")

async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for the LiveKit agent with conversation tracking.
    """
    logger.info("🚀 Agent entrypoint started for room: %s", ctx.room.name)

    # Extract user_id from room name or metadata if available
    # For now, we'll use a default - in production, you'd get this from the room metadata
    user_id = 1  # Default user_id, should be passed from frontend
    
    # Try to extract user_id from room name pattern (e.g., "room_user_1")
    try:
        if "_user_" in ctx.room.name:
            user_id = int(ctx.room.name.split("_user_")[-1])
            logger.info(f"Extracted user_id: {user_id} from room name")
    except:
        logger.warning(f"Could not extract user_id from room name: {ctx.room.name}, using default: {user_id}")

    # Create our financial assistant
    financial_assistant = FinancialAssistant(user_id=user_id)

    # Create session with standard OpenAI LLM
    session = AgentSession(
        stt=deepgram.STT(
            model="nova-2",
            api_key=settings.deepgram_api_key
        ),
        llm=openai.LLM(
            model="gpt-4o-mini",
            api_key=settings.openai_api_key
        ),  # Standard OpenAI LLM
        tts=elevenlabs.TTS(
            api_key=settings.elevenlabs_api_key,
            voice_id="NeDTo4pprKj2ZwuNJceH",
            model="eleven_turbo_v2_5"
        ),
        vad=silero.VAD.load(),
        turn_detection="vad"
    )

    # Conversation event handler to capture and process conversation history
    @session.on("conversation_item_added")  
    def _on_conversation_item_added(conversation_event: ConversationItemAddedEvent):
        logger.info(f"🎯 Conversation event: {conversation_event}")
        
        for content in conversation_event.item.content:
            if isinstance(content, str):
                if conversation_event.item.role == "user":
                    # User spoke
                    if financial_assistant.conversation_buffer != "":
                        financial_assistant.conversation_buffer += f"\nUser: {content}"
                    else:
                        financial_assistant.conversation_buffer = f"User: {content}"
                        if financial_assistant.call_start_time == "":
                            financial_assistant.call_start_time = datetime.now() - timedelta(seconds=4)
                    
                    logger.info(f"👤 User said: {content}")
                    financial_assistant.call_status = "USER_SPOKE"
                    
                    # Process user input through LangGraph for context/memory
                    asyncio.create_task(_process_user_input_with_langgraph(content, financial_assistant))
                    
                elif conversation_event.item.role == "assistant":
                    # Agent responded
                    if financial_assistant.conversation_buffer != "":
                        financial_assistant.conversation_buffer += f"\nAI: {content}"
                    else:
                        financial_assistant.conversation_buffer = f"AI: {content}"
                    
                    logger.info(f"🤖 Agent said: {content}")
                    financial_assistant.call_status = "AGENT_SPOKE"
                    
                    # Process agent response through LangGraph for context/memory
                    asyncio.create_task(_process_agent_response_with_langgraph(content, financial_assistant))

    async def _process_user_input_with_langgraph(user_input: str, assistant: FinancialAssistant):
        """Process user input through LangGraph for enhanced context and memory."""
        try:
            logger.info(f"🧠 Processing user input through LangGraph: {user_input}")
            
            # Create message for LangGraph
            messages = [HumanMessage(content=user_input)]
            
            # Process through our chat graph for context
            for chunk in stream_chat(messages, assistant.config, user_id=assistant.user_id):
                if "conversation_agent" in chunk:
                    # This gives us context and memory from our conversation agent
                    agent_messages = chunk["conversation_agent"]["messages"]
                    if agent_messages:
                        logger.info(f"🧠 LangGraph processed user input, context updated")
                        # Store the current phase if available
                        if "current_phase" in chunk["conversation_agent"]:
                            assistant.current_phase = chunk["conversation_agent"]["current_phase"]
                        break
                elif "analysis_agent" in chunk:
                    # Analysis results from Agent2
                    agent_messages = chunk["analysis_agent"]["messages"]
                    if agent_messages:
                        logger.info(f"📊 Analysis completed by Agent2")
                        break
            
        except Exception as e:
            logger.error(f"❌ Error processing user input with LangGraph: {str(e)}")

    async def _process_agent_response_with_langgraph(agent_response: str, assistant: FinancialAssistant):
        """Process agent response through LangGraph to maintain conversation context."""
        try:
            logger.info(f"🧠 Processing agent response through LangGraph for context")
            
            # We can use this to maintain conversation history in LangGraph
            # This ensures continuity between voice and text conversations
            # For now, we'll just log it, but you could extend this to update context
            
        except Exception as e:
            logger.error(f"❌ Error processing agent response with LangGraph: {str(e)}")

    # Start the session
    logger.info("🏁 Starting session...")
    await session.start(
        room=ctx.room,
        agent=financial_assistant,
    )
    logger.info("✅ Session started")

    # Connect to the room
    logger.info("🔗 Connecting to room...")
    await ctx.connect()
    logger.info("✅ Connected to room")

    logger.info("🎉 Financial assistant is ready for conversation with LangGraph integration")

    # Generate initial greeting
    logger.info("👋 Sending initial greeting...")
    await session.generate_reply(
        instructions="Greet the user warmly and briefly introduce yourself as their financial assistant. Ask how you can help them with their financial needs today."
    )
    logger.info("✅ Initial greeting sent")

    # Log conversation buffer periodically for debugging
    async def log_conversation_status():
        while True:
            await asyncio.sleep(30)  # Log every 30 seconds
            if financial_assistant.conversation_buffer:
                logger.info(f"📝 Conversation buffer: {financial_assistant.conversation_buffer[-200:]}...")  # Last 200 chars
    
    # Start background task to log conversation status
    asyncio.create_task(log_conversation_status())


async def shutdown_hook(worker):
    """
    Cleanup hook called when the worker is shutting down.
    """
    logger.info("🛑 Worker shutting down.")


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    logger.info("🔍 Starting LiveKit financial agent with LangGraph integration...")
    
    # Log configuration
    logger.info(f"🔑 LiveKit URL: {settings.livekit_url}")
    logger.info(f"🔑 API Keys configured: {bool(settings.livekit_api_key and settings.deepgram_api_key and settings.elevenlabs_api_key and settings.openai_api_key)}")
    
    # Create WorkerOptions with LiveKit server configuration
    worker_options = WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=settings.livekit_url,
        api_key=settings.livekit_api_key,
        api_secret=settings.livekit_api_secret,
        num_idle_processes=2
    )
    
    logger.info("🚀 Starting LiveKit agent...")
    agents.cli.run_app(worker_options)