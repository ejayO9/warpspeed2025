from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from typing import Dict, Any, List
import json
import re
from datetime import datetime
from sqlalchemy.orm import Session
from dependencies import get_db
from app import models
from app.pydanticModels import financial_analysis as financial_analysis_schema
from pydantic import BaseModel, Field
from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser

from .state import AgentState
from app.config import settings

# System prompts for both agents
AGENT1_SYSTEM_PROMPT = """You are FinBuddy, a friendly financial advisor. Your goal is to understand the user's financial situation before analyzing loan options.

Please collect the following information naturally in conversation:
1. Source of income - Ask about salary, other income sources, and any expected changes (job change, salary hike, bonus, or income dip)
2. Upcoming big expenses - Home purchase, children's education, wedding, medical, travel, etc.
3. Dependents - Spouse, children, parents, and their needs
4. Any other relevant information they think you should know

Also, try to understand what purchase they're planning (e.g., car, house) and the approximate amount.

Be conversational and empathetic. If the user provides multiple pieces of information at once, acknowledge all of them. 

After collecting all information, ask for confirmation: "I have gathered all the information I need. Shall I analyze your loan options now?"

Current conversation phase: {current_phase}
Information collected so far: {chat_info}
"""

AGENT2_SYSTEM_PROMPT = """You are a financial analysis expert. Based on the user's profile, financial data, and requirements, provide a comprehensive loan analysis.

Consider:
- Credit score and history
- Income stability and sources
- Existing liabilities
- Available bank quotes
- Risk tolerance
- Future financial commitments

Provide detailed scenarios with EMI calculations, pros/cons, and recommendations.
Format your analysis in a clear, structured manner.
"""

# Initialize the language model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=settings.openai_api_key,
    temperature=0.7
)

# Pydantic model for structured extraction
class ExtractedInfo(BaseModel):
    income_details: Optional[str] = Field(description="Details about user's income sources, salary, bonuses, rental income, expected changes")
    upcoming_spends: Optional[str] = Field(description="Information about upcoming big expenses like wedding, education, medical, travel")
    dependents_info: Optional[str] = Field(description="Information about dependents - spouse, children, parents")
    additional_info: Optional[str] = Field(description="Any other relevant financial information the user mentioned")
    purchase_amount: Optional[float] = Field(description="The amount of the purchase/loan the user is considering (in rupees, not lakhs)")
    purchase_type: Optional[str] = Field(description="Type of purchase - car, house, etc.")
    all_info_collected: bool = Field(description="Whether all 4 main pieces of information have been collected")

def extract_info_from_messages(messages: List[BaseMessage]) -> Dict[str, Any]:
    """Extract collected information from conversation history using LLM."""
    
    # Create parser for structured output
    parser = PydanticOutputParser(pydantic_object=ExtractedInfo)
    
    # Combine all messages into a conversation transcript
    conversation_transcript = "\n".join([
        f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
        for msg in messages
    ])
    
    # Create extraction prompt
    extraction_prompt = f"""
    Extract the following information from this conversation between a financial advisor and a user:
    
    1. Income details (salary, other sources, expected changes)
    2. Upcoming big spends (wedding, education, medical, travel, etc.)
    3. Dependents information (spouse, children, parents)
    4. Any additional relevant information
    5. Purchase amount and type if mentioned
    
    Conversation:
    {conversation_transcript}
    
    {parser.get_format_instructions()}
    
    Note: 
    - For purchase_amount, convert lakhs to actual rupees (e.g., 45 lakhs = 4500000)
    - Set all_info_collected to true only if income, upcoming spends, and dependents info are all present
    """
    
    try:
        # Use LLM to extract structured data
        extraction_llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            api_key=settings.openai_api_key,
            temperature=0
        )
        
        response = extraction_llm.invoke([SystemMessage(content=extraction_prompt)])
        extracted_data = parser.parse(response.content)
        
        # Convert to dictionary format expected by the rest of the code
        info = {
            "income_details": extracted_data.income_details,
            "upcoming_spends": extracted_data.upcoming_spends,
            "dependents_info": extracted_data.dependents_info,
            "additional_info": extracted_data.additional_info
        }
        
        return info, extracted_data.purchase_amount, extracted_data.all_info_collected
        
    except Exception as e:
        # Fallback to simple extraction if LLM fails
        print(f"LLM extraction failed: {e}, falling back to simple extraction")
        
        info = {
            "income_details": None,
            "upcoming_spends": None,
            "dependents_info": None,
            "additional_info": None
        }
        car_price = None
        
        # Combine all user messages
        user_messages = " ".join([msg.content for msg in messages if isinstance(msg, HumanMessage)])
        
        # Simple extraction logic as fallback
        if any(word in user_messages.lower() for word in ["salary", "income", "earn", "rental", "bonus"]):
            info["income_details"] = user_messages
        
        if any(word in user_messages.lower() for word in ["wedding", "education", "medical", "travel", "expense", "spend"]):
            info["upcoming_spends"] = user_messages
        
        if any(word in user_messages.lower() for word in ["spouse", "children", "parents", "dependent", "family"]):
            info["dependents_info"] = user_messages
        
        # Extract car price if mentioned
        price_match = re.search(r'(?:₹|Rs\.?|INR)?\s*(\d+(?:\.\d+)?)\s*(?:L|lakh|lakhs|lac|lacs)', user_messages, re.IGNORECASE)
        if price_match:
            car_price = float(price_match.group(1)) * 100000
        
        all_collected = all([
            info["income_details"],
            info["upcoming_spends"],
            info["dependents_info"]
        ])
        
        return info, car_price, all_collected

def conversation_agent(state: AgentState) -> Dict[str, Any]:
    """Agent 1: Handles conversation with the user to collect information."""
    messages = state['messages']
    current_phase = state.get('current_phase', 'collecting_info')
    chat_info = state.get('chat_info', {})
    
    # Format the system prompt with current state
    system_prompt = AGENT1_SYSTEM_PROMPT.format(
        current_phase=current_phase,
        chat_info=json.dumps(chat_info, indent=2) if chat_info else "None"
    )
    
    # Ensure system message is first
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=system_prompt)] + messages
    else:
        messages[0] = SystemMessage(content=system_prompt)
    
    # Get response from LLM
    response = llm.invoke(messages)
    
    # Extract information from conversation
    info, purchase_amount, all_collected = extract_info_from_messages(messages + [response])
    
    # Update state
    updates = {
        "messages": [response],
        "chat_info": info,
        "all_info_collected": all_collected
    }
    
    if purchase_amount:
        updates["car_price"] = purchase_amount  # Still using car_price in state for compatibility
    
    # Check if user confirmed to proceed with analysis
    if all_collected and "shall i analyze" in response.content.lower():
        updates["current_phase"] = "confirming_analysis"
    
    # Force confirmation message if all info collected but not yet confirming
    if all_collected and current_phase == 'collecting_info' and not any(phrase in response.content.lower() for phrase in ["shall i analyze", "should i analyze", "ready to analyze"]):
        # Override the response to ask for confirmation
        confirmation_msg = f"""{response.content}

I have gathered all the information I need. Shall I analyze your loan options now?"""
        response = AIMessage(content=confirmation_msg)
        updates["messages"] = [response]
        updates["current_phase"] = "confirming_analysis"
    
    # Check if this is a response after user confirmed
    if messages and isinstance(messages[-1], HumanMessage):
        last_user_message = messages[-1].content.lower()
        if current_phase == 'confirming_analysis' and any(word in last_user_message for word in ['yes', 'sure', 'okay', 'proceed', 'go ahead', 'analyze']):
            # Mark that user confirmed - this will be detected by the streaming logic
            updates["user_confirmed_analysis"] = True
    
    return updates

def fetch_user_data(user_id: int, db: Session) -> tuple:
    """Fetch user profile, financials, and bank quotes from database."""
    # Get user with financials
    user = db.query(models.user_profile.User).filter(
        models.user_profile.User.id == user_id
    ).first()
    
    if not user:
        return None, None, []
    
    # Get bank quotes
    bank_quotes = db.query(models.bank_quote.BankQuote).filter(
        models.bank_quote.BankQuote.user_id == user_id
    ).all()
    
    return user, user.financials if user else None, bank_quotes

def analysis_agent(state: AgentState) -> Dict[str, Any]:
    """Agent 2: Performs financial analysis based on collected information."""
    # Get database session
    db = next(get_db())
    
    try:
        # Fetch user data
        user_id = state.get('user_id')
        if not user_id:
            return {
                "messages": [AIMessage(content="I need your user ID to perform the analysis. Please provide it.")],
                "current_phase": "error"
            }
        
        user, financials, bank_quotes = fetch_user_data(user_id, db)
        
        if not user:
            return {
                "messages": [AIMessage(content="I couldn't find your user profile. Please make sure you're registered.")],
                "current_phase": "error"
            }
        
        # Prepare analysis context
        analysis_context = f"""
        User Profile:
        - Name: {user.full_name}
        - Age: {(datetime.now().date() - user.date_of_birth).days // 365 if user.date_of_birth else 'Unknown'}
        
        Financial Information:
        - Credit Score: {financials.credit_score if financials else 'Not available'}
        - Total Income: {financials.total_income if financials else 'Not available'}
        - Active Loans: {financials.active_loans_count if financials else 0}
        
        User Requirements (from conversation):
        - Income Details: {state['chat_info'].get('income_details', 'Not provided')}
        - Upcoming Expenses: {state['chat_info'].get('upcoming_spends', 'Not provided')}
        - Dependents: {state['chat_info'].get('dependents_info', 'Not provided')}
        - Additional Info: {state['chat_info'].get('additional_info', 'Not provided')}
        
        Purchase Details:
        - Amount: ₹{state.get('car_price', 0):,.0f}
        
        Available Bank Quotes:
        """
        
        if bank_quotes:
            for quote in bank_quotes:
                analysis_context += f"""
        - Bank Quote {quote.id} ({quote.bank_name}):
          Amount: ₹{quote.amount:,.0f}
          Tenure: {quote.tenure} months
          Interest Rate: {quote.interest_rate}%
          EMI: ₹{quote.emi:,.0f}
        """
        else:
            analysis_context += "\n        No bank quotes available. Using hypothetical rates for analysis."
        
        # Create analysis prompt
        analysis_prompt = f"{AGENT2_SYSTEM_PROMPT}\n\nContext:\n{analysis_context}\n\nProvide a comprehensive financial analysis."
        
        # Get analysis from LLM
        response = llm.invoke([SystemMessage(content=analysis_prompt)])
        
        # Save chat info to database
        if state['chat_info']:
            chat_info_data = state['chat_info']
            db_chat_info = models.user_chat_info_model.UserChatInfo(
                **chat_info_data,
                user_id=user_id
            )
            db.add(db_chat_info)
            db.commit()
        
        # For now, return the analysis as a message
        # In production, you'd parse this into the structured format and save to database
        return {
            "messages": [AIMessage(content=f"Here's my analysis:\n\n{response.content}")],
            "current_phase": "discussing_results",
            "analysis_result": {"raw_analysis": response.content}
        }
        
    finally:
        db.close()

def route_agent(state: AgentState) -> str:
    """Determine which agent to route to based on current state."""
    current_phase = state.get('current_phase', 'collecting_info')
    messages = state.get('messages', [])
    
    # Check if user confirmed analysis
    if messages and isinstance(messages[-1], HumanMessage):
        last_message = messages[-1].content.lower()
        if current_phase == 'confirming_analysis' and any(word in last_message for word in ['yes', 'sure', 'okay', 'proceed', 'go ahead', 'analyze']):
            return 'analysis_agent'
    
    # Default to end the conversation (which maps to END)
    return 'conversation_agent'

# Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("conversation_agent", conversation_agent)
workflow.add_node("analysis_agent", analysis_agent)

# Set the entrypoint
workflow.set_entry_point("conversation_agent")

# Add conditional edges
workflow.add_conditional_edges(
    "conversation_agent",
    route_agent,
    {
        "conversation_agent": END,  # End after conversation response
        "analysis_agent": "analysis_agent"
    }
)

# Analysis agent ends after providing analysis
workflow.add_edge("analysis_agent", END)

# Compile the graph
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Add a streaming method to the app
def stream_chat(messages: list, config: dict, user_id: int = None):
    """Stream chat responses."""
    # Prepare the input for the graph
    inputs = {
        "messages": messages,
        "current_phase": "collecting_info",
        "user_id": user_id
    }
    
    # Use stream_mode='values' to get the full state after each node
    for chunk in app.stream(inputs, config=config, stream_mode="values"):
        # The chunk now contains the full state
        # We need to transform it to match the expected format
        if "messages" in chunk and chunk["messages"]:
            last_message = chunk["messages"][-1]
            
            # Yield the conversation agent output format
            output = {
                "conversation_agent": {
                    "messages": [last_message],
                    "chat_info": chunk.get("chat_info", {}),
                    "all_info_collected": chunk.get("all_info_collected", False),
                    "current_phase": chunk.get("current_phase", "collecting_info")
                }
            }
            
            # Include user_confirmed_analysis if present
            if chunk.get("user_confirmed_analysis", False):
                output["conversation_agent"]["user_confirmed_analysis"] = True
            
            # Include car_price if present
            if "car_price" in chunk:
                output["conversation_agent"]["car_price"] = chunk["car_price"]
                
            yield output 