#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.graph import stream_chat
from langchain_core.messages import HumanMessage
from uuid import uuid4

def test_redirect():
    """Test that redirect is triggered when user confirms analysis"""
    
    # Simulate conversation
    config = {"configurable": {"thread_id": str(uuid4())}}
    
    print("Testing redirect functionality...")
    print("-" * 50)
    
    # First message with all info
    test_message = HumanMessage(content="""
    I earn 80000 per month as salary. 
    I have upcoming wedding expenses of 10 lakhs next year.
    I have a spouse and 2 children as dependents.
    I'm planning to buy a car worth 45 lakhs.
    """)
    
    # Process first message
    print("\n1. Sending user information...")
    for chunk in stream_chat([test_message], config, user_id=1):
        if "conversation_agent" in chunk:
            agent_response = chunk['conversation_agent']['messages'][-1].content
            print(f"\nAgent response: {agent_response[:200]}...")
            
            # Check if agent is asking for confirmation
            if "shall i analyze" in agent_response.lower():
                print("\n✅ Agent is asking for confirmation!")
                
                # Send confirmation
                print("\n2. Sending user confirmation...")
                confirmation = HumanMessage(content="Yes, please analyze my loan options")
                
                redirect_found = False
                for chunk2 in stream_chat([confirmation], config, user_id=1):
                    if "conversation_agent" in chunk2:
                        print(f"\nAgent response after confirmation: {chunk2['conversation_agent']['messages'][-1].content[:100]}...")
                        
                        # Check all keys in the chunk
                        print(f"\nKeys in chunk: {list(chunk2['conversation_agent'].keys())}")
                        
                        if "redirect_to" in chunk2["conversation_agent"]:
                            print(f"\n✅ REDIRECT SIGNAL FOUND: {chunk2['conversation_agent']['redirect_to']}")
                            redirect_found = True
                
                if redirect_found:
                    print("\n✅ Test passed! Redirect functionality is working.")
                else:
                    print("\n❌ Test failed! No redirect signal was found.")
                break

if __name__ == "__main__":
    test_redirect() 