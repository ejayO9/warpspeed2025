from typing import TypedDict, Annotated, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage
import operator
from langgraph.graph import add_messages

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: Optional[int]
    user_profile: Optional[Dict[str, Any]]
    user_financials: Optional[Dict[str, Any]]
    bank_quotes: Optional[List[Dict[str, Any]]]
    chat_info: Dict[str, Any]
    analysis_result: Optional[Dict[str, Any]]
    current_phase: str  # "collecting_info", "confirming_analysis", "analyzing", "discussing_results"
    car_price: Optional[float]  # Extracted from conversation
    all_info_collected: bool  # Flag to track if all 4 pieces of info are collected 