import asyncio
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from agent_state import AgentState, TaskRequest
from tools import AgentTools
from prompt_manager import PromptManager
from knowledge_base import KnowledgeBase, KnowledgeQuery
import json
from datetime import datetime


class AgentNodes:
    """Agent nodes for the LangGraph workflow with separate planning and execution"""
    
    def __init__(self, model_name: str = "gpt-4", mcp_client=None, prompt_manager: PromptManager = None, knowledge_base: KnowledgeBase = None):
        self.llm = ChatOpenAI(model=model_name, temperature=0.1)
        self.tools = AgentTools(mcp_manager=mcp_client)  # Pass MCP manager to tools
        self.mcp_client = mcp_client  # MCP server client for external tools
        self.prompt_manager = prompt_manager or PromptManager()
        self.knowledge_base = knowledge_base or KnowledgeBase()
    
    async def planning_node(self, state: AgentState) -> AgentState:
        """Planning node that creates a detailed execution plan"""
        try:
            current_task = state.get("current_task", "")
            messages = state.get("messages", [])
            iteration_count = state.get("iteration_count", 0)
            max_iterations = state.get("max_iterations", 10)
            
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
            
            state["messages"].append({
                "role": "planner",
                "content": f"Execution plan created with {len(plan['steps'])} steps",
                "timestamp": datetime.now().isoformat(),
                "plan": plan
            })
            
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
            
            state["messages"].append({
                "role": "executor",
                "content": f"Executing step {current_step_index + 1}: {description}",
                "timestamp": datetime.now().isoformat(),
                "step": current_step
            })
            
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
        state["messages"].append({
            "role": "executor",
            "content": f"Executed generic step: {step.get('description', '')}",
            "timestamp": datetime.now().isoformat()
        })
    
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
                
                state["messages"].append({
                    "role": "researcher",
                    "content": f"Research and analysis completed for: {current_task}",
                    "timestamp": datetime.now().isoformat()
                })
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
    
    async def completion_node(self, state: AgentState) -> AgentState:
        """Final node that completes the workflow"""
        try:
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
            
            state["messages"].append({
                "role": "completion",
                "content": "Workflow completed successfully",
                "timestamp": datetime.now().isoformat()
            })
            
            return state
            
        except Exception as e:
            error_msg = f"Completion node error: {str(e)}"
            state["error_log"].append(error_msg)
            state["final_answer"] = f"Task completed with errors: {str(e)}"
            return state