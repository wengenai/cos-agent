from typing import TypedDict, List, Dict, Any, Optional, Annotated
from pydantic import BaseModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State schema for the agentic solution"""
    messages: Annotated[List[BaseMessage], add_messages]
    current_task: Optional[str]
    task_history: List[str]
    research_results: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    final_answer: Optional[str]
    tools_used: List[str]
    iteration_count: int
    max_iterations: int
    error_log: List[str]
    context: Dict[str, Any]


class TaskRequest(BaseModel):
    """Request model for tasks"""
    query: str
    task_type: str  # 'research', 'analysis', 'code_gen', 'qa'
    context: Optional[Dict[str, Any]] = None
    max_iterations: int = 10


class ToolResult(BaseModel):
    """Result from tool execution"""
    tool_name: str
    success: bool
    result: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None