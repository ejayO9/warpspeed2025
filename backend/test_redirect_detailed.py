#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.graph import stream_chat, conversation_agent, extract_info_from_messages
from app.agents.state import AgentState
from langchain_core.messages import HumanMessage, SystemMessage
from uuid import uuid4

def test_extraction():
    """Test information extraction logic"""
    messages = [
        SystemMessage(content="You are a financial advisor"),
        HumanMessage(content="""
        I earn 80000 per month as salary. 
        I have upcoming wedding expenses of 10 lakhs next year.
        I have a spouse and 2 children as dependents.
        I'm planning to buy a car worth 45 lakhs.
        """)
    ]
    
    info, car_price, all_collected = extract_info_from_messages(messages)
    
    print("Extraction test results:")
    print(f"Income details: {info.get('income_details', 'None')}")
    print(f"Upcoming spends: {info.get('upcoming_spends', 'None')}")
    print(f"Dependents info: {info.get('dependents_info', 'None')}")
    print(f"Car price: {car_price}")
    print(f"All info collected: {all_collected}")
    print("-" * 50)

def test_conversation_flow():
    """Test the full conversation flow"""
    config = {"configurable": {"thread_id": str(uuid4())}}
    
    # Test with separate messages
    messages_sequence = [
        "My salary is 80000 per month",
        "I have upcoming wedding expenses of 10 lakhs",
        "I have a spouse and 2 children as dependents",
        "I'm planning to buy a car worth 45 lakhs"
    ]
    
    print("\nTesting conversation flow with separate messages:")
    print("-" * 50)
    
    conversation_history = []
    current_phase = None
    
    for i, msg_text in enumerate(messages_sequence):
        print(f"\n{i+1}. User: {msg_text}")
        msg = HumanMessage(content=msg_text)
        conversation_history.append(msg)
        
        for chunk in stream_chat([msg], config, user_id=1):
            if "conversation_agent" in chunk:
                agent_data = chunk['conversation_agent']
                response = agent_data['messages'][-1].content
                print(f"   Agent: {response[:150]}...")
                
                # Check state
                if 'all_info_collected' in agent_data:
                    print(f"   All info collected: {agent_data['all_info_collected']}")
                if 'current_phase' in agent_data:
                    current_phase = agent_data['current_phase']
                    print(f"   Current phase: {current_phase}")
                if 'chat_info' in agent_data:
                    print(f"   Chat info keys: {list(agent_data['chat_info'].keys())}")
                
                # Check if asking for confirmation
                if "shall i analyze" in response.lower():
                    print("\n✅ Agent is asking for confirmation!")
                    
                    # Send confirmation
                    confirmation = HumanMessage(content="Yes please, go ahead and analyze")
                    print(f"\n5. User: {confirmation.content}")
                    
                    for chunk2 in stream_chat([confirmation], config, user_id=1):
                        if "conversation_agent" in chunk2:
                            agent_data2 = chunk2['conversation_agent']
                            print(f"   Agent: {agent_data2['messages'][-1].content[:100]}...")
                            print(f"   Keys in response: {list(agent_data2.keys())}")
                            
                            if "redirect_to" in agent_data2:
                                print(f"\n✅ REDIRECT FOUND: {agent_data2['redirect_to']}")
                                return True
                    
                    print("\n❌ No redirect found after confirmation")
                    return False

if __name__ == "__main__":
    print("Running redirect functionality tests...\n")
    
    # First test extraction
    test_extraction()
    
    # Then test conversation flow
    test_conversation_flow() 