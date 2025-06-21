#!/usr/bin/env python3

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from dotenv import load_dotenv
from app.config import settings
import os

def test_api_keys():
    """Test that all required API keys are configured."""
    print("Testing API key configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Check each required API key
    keys_to_check = {
        "LIVEKIT_API_KEY": settings.livekit_api_key,
        "LIVEKIT_API_SECRET": settings.livekit_api_secret,
        "LIVEKIT_URL": settings.livekit_url,
        "OPENAI_API_KEY": settings.openai_api_key,
        "DEEPGRAM_API_KEY": settings.deepgram_api_key,
        "ELEVENLABS_API_KEY": settings.elevenlabs_api_key,
    }
    
    missing_keys = []
    for key_name, key_value in keys_to_check.items():
        if not key_value or key_value.strip() == "":
            missing_keys.append(key_name)
            print(f"❌ {key_name}: NOT SET")
        else:
            # Show first 4 and last 4 characters for security
            masked_value = key_value[:4] + "..." + key_value[-4:] if len(key_value) > 8 else "***"
            print(f"✅ {key_name}: {masked_value}")
    
    if missing_keys:
        print(f"\n❌ Missing API keys: {', '.join(missing_keys)}")
        print("Please set these environment variables in your .env file")
        return False
    else:
        print("\n✅ All API keys are configured!")
        return True

def test_imports():
    """Test that all required modules can be imported."""
    print("\nTesting module imports...")
    
    try:
        from livekit import agents
        from livekit.agents import JobContext, WorkerOptions, llm, stt, tts, AgentSession, Agent
        from livekit.plugins import deepgram, elevenlabs, openai, silero
        print("✅ LiveKit modules imported successfully")
    except ImportError as e:
        print(f"❌ LiveKit import error: {e}")
        return False
    
    try:
        from app.agents.graph import stream_chat
        print("✅ Chat graph imported successfully")
    except ImportError as e:
        print(f"❌ Chat graph import error: {e}")
        return False
    
    try:
        from langchain_core.messages import HumanMessage, SystemMessage
        print("✅ LangChain messages imported successfully")
    except ImportError as e:
        print(f"❌ LangChain import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 LiveKit Agent Configuration Test")
    print("=" * 50)
    
    config_ok = test_api_keys()
    imports_ok = test_imports()
    
    if config_ok and imports_ok:
        print("\n🎉 All tests passed! The agent should be ready to run.")
    else:
        print("\n💥 Some tests failed. Please fix the issues above.") 