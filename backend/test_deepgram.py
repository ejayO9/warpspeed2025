#!/usr/bin/env python3
"""
Test script to verify Deepgram API key
"""
import os
import requests
from dotenv import load_dotenv

def test_deepgram_api():
    """Test Deepgram API key"""
    load_dotenv()
    
    api_key = os.getenv("DEEPGRAM_API_KEY")
    if not api_key:
        print("❌ DEEPGRAM_API_KEY not found in environment variables")
        return False
    
    print(f"Testing Deepgram API key: {api_key[:15]}...")
    
    # Test API key by getting projects
    url = "https://api.deepgram.com/v1/projects"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Deepgram API key is valid and working!")
            data = response.json()
            if 'projects' in data and data['projects']:
                print(f"   Found {len(data['projects'])} project(s)")
                for project in data['projects']:
                    print(f"   - Project: {project.get('name', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("❌ Deepgram API key is invalid or expired")
            print("   Please check your API key in the Deepgram Console")
            return False
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False

if __name__ == "__main__":
    test_deepgram_api() 