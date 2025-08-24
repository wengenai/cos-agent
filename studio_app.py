#!/usr/bin/env python3
"""
LangGraph Studio App Entry Point
"""
import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

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
        model_name=os.getenv("DEFAULT_MODEL", "gpt-4o"),
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
    graph.add_node("conversation", nodes.conversational_node)
    graph.add_node("completion", nodes.completion_node)
    
    # Add edges with conditional routing - start directly with planning
    graph.add_edge(START, "planning")
    graph.add_edge("planning", "execution")
    
    # Conditional routing from execution
    def route_after_execution(state: AgentState) -> str:
        """Route after execution node based on context"""
        context = state.get("context", {})
        next_action = context.get("next_action", "complete")
        
        # Check if this is a conversational request
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1] if messages else None
            if hasattr(last_message, 'content'):
                content = last_message.content.lower()
                
                # Conversational triggers - expanded list for better detection
                conversational_triggers = [
                    "hello", "hi", "hey", "greetings", 
                    "thanks", "thank you", "appreciate",
                    "what", "how", "why", "when", "where", "who",
                    "can you", "could you", "would you", "please", "help",
                    "tell me", "explain", "describe", "show me",
                    "i want", "i need", "i'm looking", "looking for"
                ]
                
                # Complex task indicators that should NOT go to conversation
                complex_task_indicators = [
                    "research", "analyze", "analysis", "code", "generate", "create",
                    "build", "develop", "write code", "program", "algorithm",
                    "data analysis", "calculate", "compute", "process data",
                    "mcp", "server", "database", "query", "search database"
                ]
                
                # Check for conversational triggers
                has_conversational_trigger = any(trigger in content for trigger in conversational_triggers)
                has_complex_task = any(indicator in content for indicator in complex_task_indicators)
                
                # Route to conversation if:
                # 1. Has conversational trigger AND no complex task indicators
                # 2. OR message is short and simple (< 15 words) with conversational trigger
                # 3. OR this is clearly a follow-up question in an ongoing conversation
                message_word_count = len(content.split())
                is_follow_up = len(messages) > 2  # Already in a conversation
                
                if has_conversational_trigger and not has_complex_task:
                    return "conversation"
                elif message_word_count < 15 and has_conversational_trigger:
                    return "conversation" 
                elif is_follow_up and not has_complex_task:
                    # In ongoing conversations, prefer conversation unless explicitly complex
                    return "conversation"
        
        # Map actions to nodes (for explicit next actions)
        action_mapping = {
            "research": "research",
            "analyze": "analysis",
            "code_gen": "code_generation", 
            "validate": "validation",
            "summarize": "summarization",
            "conversation": "conversation",
            "complete": "completion"
        }
        
        # Default to conversation for better multi-round experience
        return action_mapping.get(next_action, "conversation")
    
    graph.add_conditional_edges(
        "execution",
        route_after_execution,
        {
            "research": "research",
            "analysis": "analysis", 
            "code_generation": "code_generation",
            "validation": "validation",
            "summarization": "summarization",
            "conversation": "conversation",
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
    
    # Route from conversation node - can continue conversation or end
    graph.add_edge("conversation", "completion")
    
    # End the workflow
    graph.add_edge("completion", END)
    
    # Compile without interrupt for Studio
    return graph.compile()

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