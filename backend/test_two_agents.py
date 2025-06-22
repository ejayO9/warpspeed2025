"""
Test script for the two-agent financial advisory system
"""
import asyncio
from app.agents.graph import stream_chat
from langchain_core.messages import HumanMessage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_two_agents():
    """Test the two-agent system with a sample conversation"""
    
    # Test user ID
    user_id = 1
    session_id = "test-session-123"
    config = {"configurable": {"thread_id": session_id}}
    
    # Simulate a conversation
    test_messages = [
        "Hi, I'm looking to buy a car worth 45 lakhs",
        "I earn 1.2 lakh per month from my job and 20k from rental income",
        "I have a wedding coming up next year that will cost around 10 lakhs",
        "I have my spouse and 2 children as dependents",
        "That's all the information I have",
        "Yes, please analyze my options"
    ]
    
    logger.info("Starting two-agent test conversation...")
    
    conversation_history = []
    
    for user_message in test_messages:
        logger.info(f"\n👤 User: {user_message}")
        
        # Add user message to history
        conversation_history.append(HumanMessage(content=user_message))
        
        # Stream response from agents
        for chunk in stream_chat(conversation_history, config, user_id=user_id):
            if "conversation_agent" in chunk:
                agent_response = chunk["conversation_agent"]["messages"][-1].content
                logger.info(f"🤖 FinBuddy (Agent1): {agent_response}")
                conversation_history.append(chunk["conversation_agent"]["messages"][-1])
                
                # Check if we're in confirming_analysis phase
                if "current_phase" in chunk["conversation_agent"]:
                    phase = chunk["conversation_agent"].get("current_phase", "")
                    logger.info(f"📍 Current phase: {phase}")
                    
            elif "analysis_agent" in chunk:
                analysis_response = chunk["analysis_agent"]["messages"][-1].content
                logger.info(f"📊 Analysis (Agent2): {analysis_response[:200]}...")  # First 200 chars
                conversation_history.append(chunk["analysis_agent"]["messages"][-1])
        
        # Small delay between messages
        await asyncio.sleep(1)
    
    logger.info("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(test_two_agents()) 