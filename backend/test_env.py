#!/usr/bin/env python3
"""
Test script to check if environment variables are properly loaded
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def test_env_loading():
    """Test environment variable loading"""
    print("Testing environment variable loading...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Script location: {Path(__file__).parent}")
    
    # Try to load .env file
    env_path = Path(__file__).parent / '.env'
    print(f"Looking for .env file at: {env_path}")
    print(f".env file exists: {env_path.exists()}")
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            print(f".env file contents:\n{f.read()}")
    
    # Load environment variables
    load_dotenv(env_path)
    
    # Check each required variable
    required_vars = [
        'LIVEKIT_API_KEY',
        'LIVEKIT_API_SECRET', 
        'LIVEKIT_URL',
        'DEEPGRAM_API_KEY',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY'
    ]
    
    print("\nEnvironment variables status:")
    print("-" * 40)
    
    all_set = True
    for var in required_vars:
        value = os.getenv(var, '')
        has_value = bool(value and value != f'your_{var.lower()}_here')
        status = "✓ SET" if has_value else "✗ NOT SET"
        # Only show first few characters of API keys for security
        display_value = value[:10] + "..." if has_value and len(value) > 10 else value
        print(f"{var}: {status} ({display_value})")
        if not has_value:
            all_set = False
    
    print("-" * 40)
    if all_set:
        print("✓ All environment variables are properly set!")
    else:
        print("✗ Some environment variables are missing or have placeholder values")
        print("\nTo fix this:")
        print("1. Make sure you have a .env file in the backend directory")
        print("2. Replace all placeholder values with your actual API keys")
    
    return all_set

if __name__ == "__main__":
    test_env_loading() 