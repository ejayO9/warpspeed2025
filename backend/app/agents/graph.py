from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .state import AgentState
from app.config import settings

# Placeholder system prompt
SYSTEM_PROMPT = """
You are a helpful financial assistant. Your goal is to help users with their financial questions. Be polite and professional.

You are currently in a room with a user. You are able to see the user's name and the room name.

You are able to see the user's messages and the messages you have sent.

You are able to see the user's profile and the room profile.

You will get the user's financial information from the user's profile.


"""

# Initialize the language model
llm = ChatOpenAI(api_key=settings.openai_api_key)

def call_model(state: AgentState):
    """Calls the LLM with the current state."""
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

# Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("agent", call_model)

# Set the entrypoint
workflow.set_entry_point("agent")

# Add edges
workflow.add_edge("agent", END)

# Compile the graph
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Add a streaming method to the app
def stream_chat(messages: list, config: dict):
    """Stream chat responses."""
    # Ensure the first message is a system message
    if not isinstance(messages[0], SystemMessage):
        messages.insert(0, SystemMessage(content=SYSTEM_PROMPT))
    
    # Prepare the input for the graph
    inputs = {"messages": messages}
    
    return app.stream(inputs, config=config) 