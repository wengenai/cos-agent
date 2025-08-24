import httpx
import json
from typing import Dict, Any, List, Optional
from tavily import TavilyClient
from agent_state import ToolResult
from function_tools import FunctionRegistry, default_function_registry
from databricks_genie import GenieToolAdapter, default_genie_adapter
from multi_mcp_manager import MultiMCPManager
import os
from datetime import datetime


class AgentTools:
    """Collection of tools for the agentic solution"""
    
    def __init__(self, function_registry: FunctionRegistry = None, genie_adapter: GenieToolAdapter = None, mcp_manager: MultiMCPManager = None):
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.function_registry = function_registry or default_function_registry
        self.genie_adapter = genie_adapter or default_genie_adapter
        self.mcp_manager = mcp_manager
    
    async def web_search(self, query: str, max_results: int = 5) -> ToolResult:
        """Perform web search using Tavily"""
        try:
            if not os.getenv("TAVILY_API_KEY"):
                return ToolResult(
                    tool_name="web_search",
                    success=False,
                    result=None,
                    error="TAVILY_API_KEY not found in environment"
                )
            
            response = self.tavily_client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )
            
            return ToolResult(
                tool_name="web_search",
                success=True,
                result=response,
                metadata={"query": query, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="web_search",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def analyze_data(self, data: Dict[str, Any], analysis_type: str = "general") -> ToolResult:
        """Analyze provided data"""
        try:
            analysis = {
                "data_summary": {
                    "total_items": len(data) if isinstance(data, (list, dict)) else 1,
                    "data_type": type(data).__name__,
                    "analysis_type": analysis_type
                },
                "insights": [],
                "recommendations": []
            }
            
            if isinstance(data, dict):
                analysis["insights"].append(f"Dictionary with {len(data)} keys")
                analysis["insights"].extend([f"Key: {k}" for k in list(data.keys())[:5]])
                
            elif isinstance(data, list):
                analysis["insights"].append(f"List with {len(data)} items")
                if data and isinstance(data[0], dict):
                    analysis["insights"].append("Contains dictionary objects")
                    
            analysis["recommendations"].append("Consider data validation and cleaning")
            analysis["recommendations"].append("Implement error handling for edge cases")
            
            return ToolResult(
                tool_name="analyze_data",
                success=True,
                result=analysis,
                metadata={"analysis_type": analysis_type, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="analyze_data",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def generate_code(self, requirements: str, language: str = "python") -> ToolResult:
        """Generate code based on requirements"""
        try:
            code_templates = {
                "python": {
                    "function": '''def {function_name}({params}):
    """
    {docstring}
    """
    # Implementation here
    pass''',
                    "class": '''class {class_name}:
    """
    {docstring}
    """
    
    def __init__(self):
        pass
        
    def method(self):
        pass'''
                }
            }
            
            # Simple code generation logic
            if "function" in requirements.lower():
                code = code_templates[language]["function"].format(
                    function_name="generated_function",
                    params="",
                    docstring=f"Generated based on: {requirements}"
                )
            else:
                code = code_templates[language]["class"].format(
                    class_name="GeneratedClass",
                    docstring=f"Generated based on: {requirements}"
                )
            
            return ToolResult(
                tool_name="generate_code",
                success=True,
                result={"code": code, "language": language},
                metadata={"requirements": requirements, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="generate_code",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def validate_input(self, input_data: Any, validation_rules: Dict[str, Any]) -> ToolResult:
        """Validate input data against rules"""
        try:
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Basic validation logic
            if "required" in validation_rules:
                for field in validation_rules["required"]:
                    if isinstance(input_data, dict) and field not in input_data:
                        validation_result["is_valid"] = False
                        validation_result["errors"].append(f"Missing required field: {field}")
            
            if "type" in validation_rules:
                expected_type = validation_rules["type"]
                if not isinstance(input_data, expected_type):
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Expected {expected_type}, got {type(input_data)}")
            
            return ToolResult(
                tool_name="validate_input",
                success=True,
                result=validation_result,
                metadata={"rules": validation_rules, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="validate_input",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def summarize_content(self, content: str, max_length: int = 200) -> ToolResult:
        """Summarize long content"""
        try:
            if len(content) <= max_length:
                summary = content
            else:
                # Simple summarization by taking first and last parts
                first_part = content[:max_length//2]
                last_part = content[-(max_length//2):]
                summary = f"{first_part}...{last_part}"
            
            return ToolResult(
                tool_name="summarize_content",
                success=True,
                result={
                    "summary": summary,
                    "original_length": len(content),
                    "summary_length": len(summary)
                },
                metadata={"max_length": max_length, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="summarize_content",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def call_function(self, function_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Call a registered function"""
        try:
            return await self.function_registry.call_function(function_name, parameters)
        except Exception as e:
            return ToolResult(
                tool_name="call_function",
                success=False,
                result=None,
                error=f"Function call error: {str(e)}"
            )
    
    async def list_available_functions(self) -> ToolResult:
        """List all available functions"""
        try:
            functions = self.function_registry.list_functions()
            return ToolResult(
                tool_name="list_functions",
                success=True,
                result={
                    "functions": functions,
                    "count": len(functions)
                },
                metadata={"timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="list_functions",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def execute_databricks_query(self, query: str, space_id: str = None, 
                                     parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a Databricks Genie query"""
        try:
            return await self.genie_adapter.execute_genie_query(query, space_id, parameters)
        except Exception as e:
            return ToolResult(
                tool_name="databricks_query",
                success=False,
                result=None,
                error=f"Databricks query error: {str(e)}"
            )
    
    async def suggest_databricks_queries(self, context: str) -> ToolResult:
        """Suggest relevant Databricks queries based on context"""
        try:
            suggestions = await self.genie_adapter.suggest_queries(context)
            return ToolResult(
                tool_name="suggest_queries",
                success=True,
                result={
                    "suggestions": suggestions,
                    "context": context,
                    "count": len(suggestions)
                },
                metadata={"timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="suggest_queries",
                success=False,
                result=None,
                error=f"Query suggestion error: {str(e)}"
            )
    
    async def get_databricks_spaces(self) -> ToolResult:
        """Get available Databricks Genie spaces"""
        try:
            spaces = await self.genie_adapter.get_available_spaces()
            return ToolResult(
                tool_name="get_spaces",
                success=True,
                result={
                    "spaces": spaces,
                    "count": len(spaces)
                },
                metadata={"timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="get_spaces",
                success=False,
                result=None,
                error=f"Spaces retrieval error: {str(e)}"
            )
    
    # Multi-MCP Server Methods
    async def execute_edfx_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on EDFX-MCP server"""
        if not self.mcp_manager:
            return ToolResult(
                tool_name=f"edfx:{tool_name}",
                success=False,
                result=None,
                error="MCP Manager not available"
            )
        
        try:
            return await self.mcp_manager.execute_edfx_tool(tool_name, parameters)
        except Exception as e:
            return ToolResult(
                tool_name=f"edfx:{tool_name}",
                success=False,
                result=None,
                error=f"EDFX MCP tool error: {str(e)}"
            )
    
    async def execute_rpa_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on RPA-MCP server"""
        if not self.mcp_manager:
            return ToolResult(
                tool_name=f"rpa:{tool_name}",
                success=False,
                result=None,
                error="MCP Manager not available"
            )
        
        try:
            return await self.mcp_manager.execute_rpa_tool(tool_name, parameters)
        except Exception as e:
            return ToolResult(
                tool_name=f"rpa:{tool_name}",
                success=False,
                result=None,
                error=f"RPA MCP tool error: {str(e)}"
            )
    
    async def execute_analysis_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on Analysis-MCP server"""
        if not self.mcp_manager:
            return ToolResult(
                tool_name=f"analysis:{tool_name}",
                success=False,
                result=None,
                error="MCP Manager not available"
            )
        
        try:
            return await self.mcp_manager.execute_analysis_tool(tool_name, parameters)
        except Exception as e:
            return ToolResult(
                tool_name=f"analysis:{tool_name}",
                success=False,
                result=None,
                error=f"Analysis MCP tool error: {str(e)}"
            )
    
    async def execute_mcp_tool_auto(self, task_description: str, tool_name: str, 
                                   parameters: Dict[str, Any] = None) -> ToolResult:
        """Automatically select best MCP server for task and execute tool"""
        if not self.mcp_manager:
            return ToolResult(
                tool_name=f"auto:{tool_name}",
                success=False,
                result=None,
                error="MCP Manager not available"
            )
        
        try:
            return await self.mcp_manager.execute_task_on_best_server(
                task_description, tool_name, parameters
            )
        except Exception as e:
            return ToolResult(
                tool_name=f"auto:{tool_name}",
                success=False,
                result=None,
                error=f"Auto MCP tool error: {str(e)}"
            )
    
    async def get_all_mcp_tools(self) -> ToolResult:
        """Get all available tools from all MCP servers"""
        if not self.mcp_manager:
            return ToolResult(
                tool_name="list_mcp_tools",
                success=False,
                result=None,
                error="MCP Manager not available"
            )
        
        try:
            all_tools = await self.mcp_manager.get_all_available_tools()
            return ToolResult(
                tool_name="list_mcp_tools",
                success=True,
                result=all_tools,
                metadata={
                    "server_count": len(all_tools),
                    "total_tools": sum(len(tools) for tools in all_tools.values()),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            return ToolResult(
                tool_name="list_mcp_tools",
                success=False,
                result=None,
                error=f"MCP tools retrieval error: {str(e)}"
            )
    
    async def mcp_health_check(self) -> ToolResult:
        """Perform health check on all MCP servers"""
        if not self.mcp_manager:
            return ToolResult(
                tool_name="mcp_health_check",
                success=False,
                result=None,
                error="MCP Manager not available"
            )
        
        try:
            health_status = await self.mcp_manager.health_check_all_servers()
            connection_status = self.mcp_manager.get_connection_status()
            
            return ToolResult(
                tool_name="mcp_health_check",
                success=True,
                result={
                    "health_status": health_status,
                    "connection_status": connection_status,
                    "connected_servers": self.mcp_manager.connected_servers
                },
                metadata={"timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            return ToolResult(
                tool_name="mcp_health_check",
                success=False,
                result=None,
                error=f"MCP health check error: {str(e)}"
            )