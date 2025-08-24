import asyncio
import os
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from agent_state import AgentState, TaskRequest
from tools import AgentTools
from prompt_manager import PromptManager
from knowledge_base import KnowledgeBase, KnowledgeQuery
import json
from datetime import datetime


class AgentNodes:
    """Agent nodes for the LangGraph workflow with separate planning and execution"""
    
    def __init__(self, model_name: str = "gpt-4o", mcp_client=None, prompt_manager: PromptManager = None, knowledge_base: KnowledgeBase = None):
        # Determine API provider based on model name and available keys
        self.model_name = model_name
        self.llm = self._initialize_llm(model_name)
        self.tools = AgentTools(mcp_manager=mcp_client)  # Pass MCP manager to tools
        self.mcp_client = mcp_client  # MCP server client for external tools
        self.prompt_manager = prompt_manager or PromptManager()
        self.knowledge_base = knowledge_base or KnowledgeBase()
    
    def _initialize_llm(self, model_name: str):
        """Initialize LLM based on model name and available API keys"""
        # Check for Anthropic models
        anthropic_models = ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
        openai_models = ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
        
        # Check available API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        if model_name in anthropic_models:
            if not anthropic_key:
                raise ValueError(f"ANTHROPIC_API_KEY is required for model {model_name}")
            return ChatAnthropic(model=model_name, temperature=0.1)
        elif model_name in openai_models:
            if not openai_key:
                raise ValueError(f"OPENAI_API_KEY is required for model {model_name}")
            return ChatOpenAI(model=model_name, temperature=0.1)
        else:
            # Auto-detect based on available keys
            if anthropic_key and model_name in anthropic_models:
                return ChatAnthropic(model=model_name, temperature=0.1)
            elif openai_key:
                # Default to OpenAI if key is available
                return ChatOpenAI(model=model_name, temperature=0.1)
            elif anthropic_key:
                # Fall back to Anthropic if only that key is available
                return ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.1)
            else:
                raise ValueError("Either OPENAI_API_KEY or ANTHROPIC_API_KEY must be set")
    
    async def planning_node(self, state: AgentState) -> AgentState:
        """Planning node that creates a detailed execution plan"""
        try:
            # Initialize state fields if not present
            if "task_history" not in state:
                state["task_history"] = []
            if "research_results" not in state:
                state["research_results"] = []
            if "analysis_results" not in state:
                state["analysis_results"] = {}
            if "tools_used" not in state:
                state["tools_used"] = []
            if "error_log" not in state:
                state["error_log"] = []
            if "context" not in state:
                state["context"] = {}
            
            current_task = state.get("current_task", "")
            messages = state.get("messages", [])
            iteration_count = state.get("iteration_count", 0)
            max_iterations = state.get("max_iterations", 10)
            
            # Extract current_task from messages if not set
            if not current_task and messages:
                for msg in reversed(messages):
                    if hasattr(msg, 'type') and msg.type == "human":
                        current_task = msg.content
                        state["current_task"] = current_task
                        state["task_history"].append(current_task)
                        break
            
            # Check if we've exceeded max iterations
            if iteration_count >= max_iterations:
                state["final_answer"] = "Maximum iterations reached. Task incomplete."
                return state
            
            # Get relevant knowledge for the task
            knowledge_context = self.knowledge_base.get_knowledge_context(current_task)
            
            # Use the planning agent prompt template
            system_prompt = self.prompt_manager.format_prompt(
                "planning_agent",
                {
                    "task": current_task,
                    "context": json.dumps(state.get('context', {}), indent=2)
                }
            )
            
            # Add knowledge context to the prompt
            context = f"Relevant Knowledge:\n{knowledge_context}\n\nTask Context: {json.dumps(state.get('context', {}), indent=2)}"
            
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=context)
            ])
            
            try:
                plan = json.loads(response.content)
            except json.JSONDecodeError:
                # Fallback plan if JSON parsing fails
                plan = {
                    "steps": [
                        {"step": 1, "action": "research", "description": "Gather information", "tools_needed": ["web_search"]},
                        {"step": 2, "action": "analyze", "description": "Analyze findings", "tools_needed": ["analyze_data"]},
                        {"step": 3, "action": "execute", "description": "Execute plan", "tools_needed": ["mcp_tools"]},
                        {"step": 4, "action": "validate", "description": "Validate results", "tools_needed": ["validate_input"]}
                    ],
                    "expected_outcome": "Task completion",
                    "success_criteria": ["Task completed successfully"],
                    "risks": ["Incomplete information", "Tool failures"]
                }
            
            # Update state with the plan
            state["context"] = state.get("context", {})
            state["context"]["execution_plan"] = plan
            state["context"]["current_step"] = 0
            state["iteration_count"] = iteration_count + 1
            
            state["messages"].append(AIMessage(
                content=f"Execution plan created with {len(plan['steps'])} steps: {json.dumps(plan, indent=2)}"
            ))
            
            return state
            
        except Exception as e:
            error_msg = f"Planning node error: {str(e)}"
            state["error_log"].append(error_msg)
            # Set a fallback plan
            state["context"] = state.get("context", {})
            state["context"]["execution_plan"] = {
                "steps": [{"step": 1, "action": "complete", "description": "Complete with error", "tools_needed": []}],
                "expected_outcome": "Error recovery",
                "success_criteria": ["Handle error gracefully"],
                "risks": ["Task incomplete"]
            }
            state["context"]["current_step"] = 0
            return state
    
    async def execution_node(self, state: AgentState) -> AgentState:
        """Execution node that executes the current step of the plan"""
        try:
            context = state.get("context", {})
            execution_plan = context.get("execution_plan", {})
            current_step_index = context.get("current_step", 0)
            steps = execution_plan.get("steps", [])
            
            if current_step_index >= len(steps):
                # All steps completed, proceed to completion
                context["next_action"] = "complete"
                return state
            
            current_step = steps[current_step_index]
            action = current_step.get("action", "")
            description = current_step.get("description", "")
            tools_needed = current_step.get("tools_needed", [])
            
            state["messages"].append(AIMessage(
                content=f"Executing step {current_step_index + 1}: {description}"
            ))
            
            # Execute based on action type
            if action == "research":
                await self._execute_research_step(state, current_step)
            elif action == "analyze":
                await self._execute_analysis_step(state, current_step)
            elif action == "execute" and "mcp_tools" in tools_needed:
                await self._execute_mcp_step(state, current_step)
            elif action == "validate":
                await self._execute_validation_step(state, current_step)
            elif action == "code_gen":
                await self._execute_code_generation_step(state, current_step)
            else:
                # Generic execution
                await self._execute_generic_step(state, current_step)
            
            # Move to next step
            context["current_step"] = current_step_index + 1
            
            # Check if this was the last step
            if current_step_index + 1 >= len(steps):
                context["next_action"] = "complete"
            else:
                context["next_action"] = "execute"  # Continue execution
                
            return state
            
        except Exception as e:
            error_msg = f"Execution node error: {str(e)}"
            state["error_log"].append(error_msg)
            state["context"]["next_action"] = "complete"
            return state
    
    async def _execute_research_step(self, state: AgentState, step: Dict[str, Any]):
        """Execute a research step"""
        current_task = state.get("current_task", "")
        description = step.get("description", current_task)
        
        search_result = await self.tools.web_search(description)
        
        if search_result.success:
            state["research_results"].append({
                "step": step["step"],
                "query": description,
                "results": search_result.result,
                "timestamp": datetime.now().isoformat()
            })
            state["tools_used"].append("web_search")
    
    async def _execute_analysis_step(self, state: AgentState, step: Dict[str, Any]):
        """Execute an analysis step"""
        research_results = state.get("research_results", [])
        
        if research_results:
            latest_research = research_results[-1]
            analysis_result = await self.tools.analyze_data(
                latest_research["results"], 
                f"step_{step['step']}_analysis"
            )
            
            if analysis_result.success:
                if "analysis_results" not in state:
                    state["analysis_results"] = {}
                state["analysis_results"][f"step_{step['step']}"] = analysis_result.result
                state["tools_used"].append("analyze_data")
    
    async def _execute_mcp_step(self, state: AgentState, step: Dict[str, Any]):
        """Execute a step using MCP tools"""
        if self.mcp_client:
            try:
                # Call MCP server tools based on the step requirements
                description = step.get("description", "")
                
                # This is where you would integrate with your specific MCP server
                # For now, we'll simulate MCP tool execution
                mcp_result = {
                    "step": step["step"],
                    "action": "mcp_tool_executed",
                    "description": description,
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                }
                
                if "mcp_results" not in state["context"]:
                    state["context"]["mcp_results"] = []
                state["context"]["mcp_results"].append(mcp_result)
                state["tools_used"].append("mcp_tools")
                
            except Exception as e:
                state["error_log"].append(f"MCP execution error: {str(e)}")
        else:
            state["error_log"].append("MCP client not available")
    
    async def _execute_validation_step(self, state: AgentState, step: Dict[str, Any]):
        """Execute a validation step"""
        # Validate current state and results
        validation_rules = {
            "required": ["current_task", "messages"],
            "type": dict
        }
        
        validation_result = await self.tools.validate_input(
            input_data=state,
            validation_rules=validation_rules
        )
        
        if validation_result.success:
            if "validation_results" not in state["context"]:
                state["context"]["validation_results"] = []
            state["context"]["validation_results"].append({
                "step": step["step"],
                "result": validation_result.result,
                "timestamp": datetime.now().isoformat()
            })
            state["tools_used"].append("validate_input")
    
    async def _execute_code_generation_step(self, state: AgentState, step: Dict[str, Any]):
        """Execute a code generation step"""
        description = step.get("description", "")
        
        code_result = await self.tools.generate_code(
            requirements=description,
            language="python"
        )
        
        if code_result.success:
            if "generated_code" not in state["context"]:
                state["context"]["generated_code"] = []
            state["context"]["generated_code"].append({
                "step": step["step"],
                "code": code_result.result,
                "timestamp": datetime.now().isoformat()
            })
            state["tools_used"].append("generate_code")
    
    async def _execute_generic_step(self, state: AgentState, step: Dict[str, Any]):
        """Execute a generic step"""
        # Log the step execution
        state["messages"].append(AIMessage(
            content=f"Executed generic step: {step.get('description', '')}"
        ))
    
    async def research_node(self, state: AgentState) -> AgentState:
        """Research node that gathers information using prompts and knowledge"""
        try:
            current_task = state.get("current_task", "")
            
            # Get relevant knowledge context
            knowledge_context = self.knowledge_base.get_knowledge_context(current_task)
            
            # Extract search query from task
            search_result = await self.tools.web_search(current_task)
            
            if search_result.success:
                # Use research specialist prompt for analysis
                try:
                    analysis_prompt = self.prompt_manager.format_prompt(
                        "research_specialist",
                        {
                            "query": current_task,
                            "knowledge_context": knowledge_context,
                            "search_results": json.dumps(search_result.result, indent=2)
                        }
                    )
                    
                    # Get LLM analysis of search results
                    analysis_response = await self.llm.ainvoke([
                        SystemMessage(content=analysis_prompt),
                        HumanMessage(content="Analyze the search results and provide structured findings.")
                    ])
                    
                    # Try to parse JSON response
                    try:
                        analysis_data = json.loads(analysis_response.content)
                    except json.JSONDecodeError:
                        analysis_data = {"analysis": analysis_response.content, "raw_response": True}
                    
                    state["research_results"].append({
                        "query": current_task,
                        "results": search_result.result,
                        "analysis": analysis_data,
                        "knowledge_used": knowledge_context,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    # Fallback to basic research result
                    state["research_results"].append({
                        "query": current_task,
                        "results": search_result.result,
                        "analysis": {"error": f"Analysis failed: {str(e)}"},
                        "knowledge_used": knowledge_context,
                        "timestamp": datetime.now().isoformat()
                    })
                
                state["tools_used"].append("web_search")
                
                state["messages"].append(AIMessage(
                    content=f"Research and analysis completed for: {current_task}"
                ))
            else:
                state["error_log"].append(f"Research failed: {search_result.error}")
                
            return state
            
        except Exception as e:
            error_msg = f"Research node error: {str(e)}"
            state["error_log"].append(error_msg)
            return state
    
    async def analysis_node(self, state: AgentState) -> AgentState:
        """Analysis node that processes and analyzes data"""
        try:
            research_results = state.get("research_results", [])
            
            if research_results:
                latest_research = research_results[-1]
                analysis_result = await self.tools.analyze_data(
                    latest_research["results"], 
                    "research_analysis"
                )
                
                if analysis_result.success:
                    state["analysis_results"] = analysis_result.result
                    state["tools_used"].append("analyze_data")
                    
                    state["messages"].append({
                        "role": "analyst",
                        "content": "Analysis completed on research results",
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    state["error_log"].append(f"Analysis failed: {analysis_result.error}")
            
            return state
            
        except Exception as e:
            error_msg = f"Analysis node error: {str(e)}"
            state["error_log"].append(error_msg)
            return state
    
    async def code_generation_node(self, state: AgentState) -> AgentState:
        """Code generation node"""
        try:
            current_task = state.get("current_task", "")
            
            code_result = await self.tools.generate_code(
                requirements=current_task,
                language="python"
            )
            
            if code_result.success:
                state["context"] = state.get("context", {})
                state["context"]["generated_code"] = code_result.result
                state["tools_used"].append("generate_code")
                
                state["messages"].append({
                    "role": "code_generator",
                    "content": "Code generation completed",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                state["error_log"].append(f"Code generation failed: {code_result.error}")
                
            return state
            
        except Exception as e:
            error_msg = f"Code generation node error: {str(e)}"
            state["error_log"].append(error_msg)
            return state
    
    async def validation_node(self, state: AgentState) -> AgentState:
        """Validation node that validates inputs and outputs"""
        try:
            context = state.get("context", {})
            
            # Validate the current state
            validation_rules = {
                "required": ["current_task", "messages"],
                "type": dict
            }
            
            validation_result = await self.tools.validate_input(
                input_data=state,
                validation_rules=validation_rules
            )
            
            if validation_result.success:
                state["context"]["validation_status"] = validation_result.result
                state["tools_used"].append("validate_input")
                
                state["messages"].append({
                    "role": "validator",
                    "content": "Validation completed",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                state["error_log"].append(f"Validation failed: {validation_result.error}")
                
            return state
            
        except Exception as e:
            error_msg = f"Validation node error: {str(e)}"
            state["error_log"].append(error_msg)
            return state
    
    async def summarization_node(self, state: AgentState) -> AgentState:
        """Summarization node that creates summaries"""
        try:
            research_results = state.get("research_results", [])
            analysis_results = state.get("analysis_results", {})
            
            # Create a comprehensive summary
            summary_content = f"Task: {state.get('current_task', '')}\n"
            summary_content += f"Research findings: {len(research_results)} results\n"
            summary_content += f"Analysis: {json.dumps(analysis_results, indent=2)}\n"
            summary_content += f"Tools used: {', '.join(state.get('tools_used', []))}\n"
            
            summary_result = await self.tools.summarize_content(
                content=summary_content,
                max_length=500
            )
            
            if summary_result.success:
                state["final_answer"] = summary_result.result["summary"]
                state["tools_used"].append("summarize_content")
                
                state["messages"].append({
                    "role": "summarizer",
                    "content": "Task summary completed",
                    "timestamp": datetime.now().isoformat()
                })
            else:
                state["error_log"].append(f"Summarization failed: {summary_result.error}")
                state["final_answer"] = "Failed to generate summary"
                
            return state
            
        except Exception as e:
            error_msg = f"Summarization node error: {str(e)}"
            state["error_log"].append(error_msg)
            state["final_answer"] = f"Error in summarization: {str(e)}"
            return state
    
    async def conversational_node(self, state: AgentState) -> AgentState:
        """Conversational node that handles multi-round conversations and generates responses"""
        try:
            messages = state.get("messages", [])
            current_task = state.get("current_task", "")
            research_results = state.get("research_results", [])
            analysis_results = state.get("analysis_results", {})
            context = state.get("context", {})
            
            # Build conversation context
            conversation_context = []
            
            # Determine conversation context depth based on message count
            is_ongoing_conversation = len(messages) > 2
            context_window = 10 if is_ongoing_conversation else 6
            
            # Add enhanced system message for multi-round conversations
            if is_ongoing_conversation:
                system_content = f"""You are a helpful AI assistant engaged in an ongoing conversation. 

Previous Context:
- Current topic: {current_task}
- Research data available: {len(research_results)} results
- Analysis data available: {bool(analysis_results)}
- Conversation length: {len(messages)} messages

Instructions:
- Maintain conversational flow and context from previous messages
- Reference earlier parts of the conversation when relevant
- Provide natural, engaging responses that build on the discussion
- If asked follow-up questions, connect them to previous context
- Be conversational and personable while remaining helpful"""
            else:
                system_content = f"""You are a helpful AI assistant starting a new conversation.

Available Resources:
- Research capabilities: {len(research_results)} results available
- Analysis capabilities: {bool(analysis_results)}

Instructions:
- Provide helpful, conversational responses
- Be friendly and engaging
- If you need more information, explain what additional research or analysis would be helpful"""
            
            system_msg = SystemMessage(content=system_content)
            conversation_context.append(system_msg)
            
            # Add conversation history with smart windowing
            recent_messages = messages[-context_window:] if len(messages) > context_window else messages
            for msg in recent_messages:
                if hasattr(msg, 'content') and hasattr(msg, 'type'):
                    conversation_context.append(msg)
            
            # Add available information as context
            if research_results:
                research_summary = f"Research findings: {research_results[:2]}"  # First 2 results
                conversation_context.append(SystemMessage(content=research_summary))
            
            if analysis_results:
                analysis_summary = f"Analysis results available: {str(analysis_results)[:200]}..."
                conversation_context.append(SystemMessage(content=analysis_summary))
            
            # Generate conversational response
            response = await self.llm.ainvoke(conversation_context)
            
            # Add AI response to messages
            ai_message = AIMessage(content=response.content)
            state["messages"].append(ai_message)
            
            # Set final_answer for this conversation turn
            state["final_answer"] = response.content
            
            # Mark conversation as ready for next turn
            state["context"]["conversation_ready"] = True
            state["tools_used"].append("conversational_response")
            
            return state
            
        except Exception as e:
            error_msg = f"Conversational node error: {str(e)}"
            state["error_log"].append(error_msg)
            # Provide a basic response even if there's an error
            ai_message = AIMessage(content=f"I encountered an error while processing your request: {str(e)}. Please try rephrasing your question.")
            state["messages"].append(ai_message)
            state["final_answer"] = ai_message.content
            return state
    
    async def completion_node(self, state: AgentState) -> AgentState:
        """Final node that completes the workflow"""
        try:
            # Check if this is a conversational task that should continue
            context = state.get("context", {})
            if context.get("conversation_ready"):
                # Don't generate a summary for conversational tasks, just mark as complete
                return state
            
            if not state.get("final_answer"):
                # Generate a final answer based on available information
                research_count = len(state.get("research_results", []))
                analysis_done = bool(state.get("analysis_results"))
                tools_used = state.get("tools_used", [])
                
                final_summary = f"""Task completed: {state.get('current_task', '')}
                
Research conducted: {research_count} searches
Analysis performed: {analysis_done}
Tools used: {', '.join(tools_used)}
Iterations: {state.get('iteration_count', 0)}
                
{'Errors encountered: ' + str(len(state.get('error_log', []))) if state.get('error_log') else 'No errors'}"""
                
                state["final_answer"] = final_summary
            
            return state
            
        except Exception as e:
            error_msg = f"Completion node error: {str(e)}"
            state["error_log"].append(error_msg)
            state["final_answer"] = f"Task completed with errors: {str(e)}"
            return state