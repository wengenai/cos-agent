from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from agent_state import AgentState, TaskRequest
from agent_nodes import AgentNodes
from prompt_manager import PromptManager
from knowledge_base import KnowledgeBase
from typing import Dict, Any
import sqlite3


class AgentGraph:
    """LangGraph workflow with separate planning and execution nodes"""
    
    def __init__(self, model_name: str = "gpt-4", mcp_client=None, prompt_manager: PromptManager = None, knowledge_base: KnowledgeBase = None):
        self.prompt_manager = prompt_manager or PromptManager()
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.nodes = AgentNodes(
            model_name=model_name, 
            mcp_client=mcp_client,
            prompt_manager=self.prompt_manager,
            knowledge_base=self.knowledge_base
        )
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        graph = StateGraph(AgentState)
        
        # Add nodes
        graph.add_node("planning", self.nodes.planning_node)
        graph.add_node("execution", self.nodes.execution_node)
        graph.add_node("research", self.nodes.research_node)
        graph.add_node("analysis", self.nodes.analysis_node)
        graph.add_node("code_generation", self.nodes.code_generation_node)
        graph.add_node("validation", self.nodes.validation_node)
        graph.add_node("summarization", self.nodes.summarization_node)
        graph.add_node("completion", self.nodes.completion_node)
        
        # Add edges with conditional routing
        graph.add_edge(START, "planning")
        
        # From planning, always go to execution
        graph.add_edge("planning", "execution")
        
        # From execution, route based on next_action in context
        graph.add_conditional_edges(
            "execution",
            self._route_after_execution,
            {
                "execute": "execution",  # Continue executing steps
                "research": "research",
                "analyze": "analysis", 
                "code_gen": "code_generation",
                "validate": "validation",
                "summarize": "summarization",
                "complete": "completion"
            }
        )
        
        # Route from individual action nodes back to execution or completion
        for node in ["research", "analysis", "code_generation", "validation", "summarization"]:
            graph.add_conditional_edges(
                node,
                self._route_to_next_step,
                {
                    "execute": "execution",
                    "complete": "completion"
                }
            )
        
        # End the workflow
        graph.add_edge("completion", END)
        
        return graph.compile(checkpointer=self.checkpointer)
    
    def _route_after_execution(self, state: AgentState) -> str:
        """Route after execution node based on context"""
        context = state.get("context", {})
        next_action = context.get("next_action", "complete")
        
        # Map actions to node names
        action_mapping = {
            "research": "research",
            "analyze": "analysis",
            "code_gen": "code_generation", 
            "validate": "validation",
            "summarize": "summarization",
            "execute": "execution",
            "complete": "completion"
        }
        
        return action_mapping.get(next_action, "completion")
    
    def _route_to_next_step(self, state: AgentState) -> str:
        """Route from action nodes to next step"""
        context = state.get("context", {})
        execution_plan = context.get("execution_plan", {})
        current_step = context.get("current_step", 0)
        steps = execution_plan.get("steps", [])
        
        # If there are more steps to execute, go back to execution
        if current_step < len(steps):
            return "execute"
        else:
            return "complete"
    
    def _initialize_state(self, task_request: TaskRequest) -> AgentState:
        """Initialize the agent state"""
        return AgentState(
            messages=[{
                "role": "system",
                "content": f"Starting task: {task_request.query}",
                "timestamp": "2024-01-01T00:00:00Z"
            }],
            current_task=task_request.query,
            task_history=[task_request.query],
            research_results=[],
            analysis_results={},
            final_answer=None,
            tools_used=[],
            iteration_count=0,
            max_iterations=task_request.max_iterations,
            error_log=[],
            context=task_request.context or {}
        )
    
    async def run(self, task_request: TaskRequest, thread_id: str = "default") -> Dict[str, Any]:
        """Run the agent workflow"""
        try:
            initial_state = self._initialize_state(task_request)
            
            # Execute the graph
            config = {"configurable": {"thread_id": thread_id}}
            
            # Stream the execution for better observability
            result_state = None
            async for event in self.graph.astream(initial_state, config):
                # Log each step for debugging
                print(f"Event: {event}")
                result_state = event
            
            # Extract final state from the last event
            if result_state:
                # The final state should be in the last event
                final_state = list(result_state.values())[0] if result_state else initial_state
            else:
                final_state = initial_state
            
            return {
                "success": True,
                "final_answer": final_state.get("final_answer", "Task completed"),
                "tools_used": final_state.get("tools_used", []),
                "iteration_count": final_state.get("iteration_count", 0),
                "messages": final_state.get("messages", []),
                "research_results": final_state.get("research_results", []),
                "analysis_results": final_state.get("analysis_results", {}),
                "context": final_state.get("context", {}),
                "errors": final_state.get("error_log", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_answer": f"Workflow failed: {str(e)}",
                "tools_used": [],
                "iteration_count": 0,
                "messages": [],
                "research_results": [],
                "analysis_results": {},
                "context": {},
                "errors": [str(e)]
            }
    
    def get_graph_visualization(self) -> str:
        """Get a text representation of the graph structure"""
        return """
Agent Workflow Graph:
START → planning → execution
                     ↓
    ┌─────────────────┴─────────────────┐
    ↓                                   ↓
research ←→ analysis ←→ code_generation ←→ validation ←→ summarization
    ↓               ↓                ↓              ↓            ↓
    └───────────→ execution ←────────┴──────────────┴────────────┘
                     ↓
                 completion → END

Routing Logic:
- planning → execution (always)
- execution → next action based on execution plan
- action nodes → execution (if more steps) or completion (if done)
- completion → END (always)
"""