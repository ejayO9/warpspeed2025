#!/usr/bin/env python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.agents.graph import stream_chat
from langchain_core.messages import HumanMessage
from uuid import uuid4

def test_redirect_simple():
    """Simple test for redirect functionality"""
    config = {"configurable": {"thread_id": str(uuid4())}}
    
    # Provide all info at once
    msg1 = HumanMessage(content="""
    My salary is 80000 per month. 
    I have upcoming wedding expenses of 10 lakhs.
    I have a spouse and 2 children as dependents.
    I'm planning to buy a car worth 45 lakhs.
    """)
    
    print("1. Sending all info at once...")
    phase = None
    
    for chunk in stream_chat([msg1], config, user_id=1):
        if "conversation_agent" in chunk:
            data = chunk["conversation_agent"]
            print(f"\nAgent response: {data['messages'][-1].content[:200]}...")
            if "current_phase" in data:
                phase = data["current_phase"]
                print(f"Phase: {phase}")
            
            # Check if agent asks for confirmation
            if "shall i analyze" in data['messages'][-1].content.lower():
                print("\n✅ Agent asks for confirmation!")
                
                # User confirms
                msg2 = HumanMessage(content="Yes, please analyze my loan options")
                print(f"\n2. User confirms: {msg2.content}")
                
                for chunk2 in stream_chat([msg2], config, user_id=1):
                    if "conversation_agent" in chunk2:
                        data2 = chunk2["conversation_agent"]
                        print(f"\nAgent response: {data2['messages'][-1].content[:100]}...")
                        
                        if data2.get("user_confirmed_analysis", False):
                            print(f"\n✅ USER CONFIRMED ANALYSIS - Backend should send redirect signal!")
                            return True
                
                print("\n❌ No confirmation detected")
                return False

if __name__ == "__main__":
    test_redirect_simple() 