#!/usr/bin/env python3
"""
LangGraph Studio App Entry Point
"""
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables
load_dotenv()

from agent_state import AgentState
from agent_nodes import AgentNodes
from prompt_manager import PromptManager
from knowledge_base import KnowledgeBase
from multi_mcp_manager import default_multi_mcp_manager

def create_graph():
    """Create the agent graph for LangGraph Studio"""
    
    # Initialize components
    prompt_manager = PromptManager()
    knowledge_base = KnowledgeBase()
    
    # Create agent nodes with MCP integration
    nodes = AgentNodes(
        model_name=os.getenv("DEFAULT_MODEL", "gpt-4"),
        mcp_client=default_multi_mcp_manager,
        prompt_manager=prompt_manager,
        knowledge_base=knowledge_base
    )
    
    # Build the graph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("planning", nodes.planning_node)
    graph.add_node("execution", nodes.execution_node)
    graph.add_node("research", nodes.research_node)
    graph.add_node("analysis", nodes.analysis_node)
    graph.add_node("code_generation", nodes.code_generation_node)
    graph.add_node("validation", nodes.validation_node)
    graph.add_node("summarization", nodes.summarization_node)
    graph.add_node("completion", nodes.completion_node)
    
    # Add edges with conditional routing
    graph.add_edge(START, "planning")
    graph.add_edge("planning", "execution")
    
    # Conditional routing from execution
    def route_after_execution(state: AgentState) -> str:
        """Route after execution node based on context"""
        context = state.get("context", {})
        next_action = context.get("next_action", "complete")
        
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
    
    graph.add_conditional_edges(
        "execution",
        route_after_execution,
        {
            "execute": "execution",
            "research": "research",
            "analysis": "analysis", 
            "code_generation": "code_generation",
            "validation": "validation",
            "summarization": "summarization",
            "completion": "completion"
        }
    )
    
    # Route from individual action nodes
    def route_to_next_step(state: AgentState) -> str:
        """Route from action nodes to next step"""
        context = state.get("context", {})
        execution_plan = context.get("execution_plan", {})
        current_step = context.get("current_step", 0)
        steps = execution_plan.get("steps", [])
        
        if current_step < len(steps):
            return "execution"
        else:
            return "completion"
    
    for node in ["research", "analysis", "code_generation", "validation", "summarization"]:
        graph.add_conditional_edges(
            node,
            route_to_next_step,
            {
                "execution": "execution",
                "completion": "completion"
            }
        )
    
    # End the workflow
    graph.add_edge("completion", END)
    
    # Compile with checkpointer for Studio
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

# Create the graph instance for Studio
graph = create_graph()

if __name__ == "__main__":
    print("LangGraph Agent for Studio initialized successfully!")
    try:
        graph_info = graph.get_graph()
        print("Graph structure:", type(graph_info))
        print("Available nodes: planning, execution, research, analysis, code_generation, validation, summarization, completion")
    except Exception as e:
        print(f"Graph info error: {e}")
        print("Graph compiled successfully - ready for LangGraph Studio")