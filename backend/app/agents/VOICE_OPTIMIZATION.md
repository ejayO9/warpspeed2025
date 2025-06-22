# Voice Chat Performance Optimization Guide

## Current Issue
The LangGraph processing is taking 9+ seconds, causing poor voice chat experience.

## Solutions

### 1. Asynchronous Post-Processing (Recommended)
Instead of processing during the conversation, save the transcript and process it after:

```python
# In livekit_agent.py
async def _save_conversation_for_processing(content, role, assistant):
    """Save conversation to a queue for later processing"""
    # Add to a queue or database
    await save_to_queue({
        "content": content,
        "role": role,
        "session_id": assistant.session_id,
        "user_id": assistant.user_id,
        "timestamp": datetime.now()
    })
```

### 2. Use Faster Models
In `graph.py`, switch to a faster model for voice interactions:
```python
# For voice mode, use gpt-3.5-turbo or gpt-4o-mini
llm = ChatOpenAI(
    model="gpt-3.5-turbo",  # Much faster than gpt-4-turbo-preview
    api_key=settings.openai_api_key,
    temperature=0.7
)
```

### 3. Optimize Database Queries
- Add database connection pooling
- Use async database operations
- Cache user data at session start

### 4. Separate Voice and Text Agents
Keep voice agent lightweight for real-time responses, use full LangGraph only for text chat:

```python
# Voice agent - simple and fast
class VoiceFinancialAssistant(Agent):
    # Uses only OpenAI's function for quick responses
    
# Text agent - full features
class TextFinancialAssistant:
    # Uses complete LangGraph with memory and analysis
```

### 5. Background Processing Pattern
```python
import asyncio
from collections import deque

class ConversationProcessor:
    def __init__(self):
        self.queue = deque()
        
    async def add_to_queue(self, item):
        self.queue.append(item)
        
    async def process_queue(self):
        while True:
            if self.queue:
                item = self.queue.popleft()
                # Process with LangGraph in background
                await self._process_with_langgraph(item)
            await asyncio.sleep(0.1)
```

## Implementation Priority
1. First: Comment out LangGraph processing (done)
2. Next: Implement background processing queue
3. Later: Optimize models and queries
4. Future: Separate voice/text agent architectures 