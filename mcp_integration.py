"""
MCP (Model Context Protocol) Integration Module
Provides integration with MCP servers for enhanced agent capabilities
"""

import httpx
import json
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from agent_state import ToolResult


@dataclass
class MCPTool:
    """Represents an MCP tool"""
    name: str
    description: str
    parameters: Dict[str, Any]
    required: List[str] = None
    
    def __post_init__(self):
        if self.required is None:
            self.required = []


@dataclass
class MCPResource:
    """Represents an MCP resource"""
    uri: str
    name: str
    description: str
    mimeType: str = None


class MCPClient:
    """Enhanced MCP client for agent integration"""
    
    def __init__(self, server_url: str, port: int = 8080, timeout: int = 30):
        self.server_url = server_url
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{server_url}:{port}"
        self.session = None
        self.available_tools = {}
        self.available_resources = {}
        self.connected = False
    
    async def connect(self):
        """Connect to MCP server and discover capabilities"""
        try:
            self.session = httpx.AsyncClient(timeout=self.timeout)
            
            # Test connection
            response = await self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            
            # Discover tools and resources
            await self._discover_capabilities()
            
            self.connected = True
            return True
            
        except Exception as e:
            if self.session:
                await self.session.aclose()
                self.session = None
            raise ConnectionError(f"Failed to connect to MCP server: {e}")
    
    async def _discover_capabilities(self):
        """Discover available tools and resources from MCP server"""
        try:
            # Get available tools
            tools_response = await self.session.get(f"{self.base_url}/tools")
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                for tool_info in tools_data.get("tools", []):
                    tool = MCPTool(
                        name=tool_info["name"],
                        description=tool_info["description"],
                        parameters=tool_info.get("parameters", {}),
                        required=tool_info.get("required", [])
                    )
                    self.available_tools[tool.name] = tool
            
            # Get available resources
            resources_response = await self.session.get(f"{self.base_url}/resources")
            if resources_response.status_code == 200:
                resources_data = resources_response.json()
                for resource_info in resources_data.get("resources", []):
                    resource = MCPResource(
                        uri=resource_info["uri"],
                        name=resource_info["name"],
                        description=resource_info["description"],
                        mimeType=resource_info.get("mimeType")
                    )
                    self.available_resources[resource.name] = resource
                    
        except Exception as e:
            print(f"Warning: Could not discover MCP capabilities: {e}")
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Call a tool on the MCP server"""
        if not self.connected:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error="MCP client not connected"
            )
        
        if tool_name not in self.available_tools:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not available on MCP server"
            )
        
        try:
            payload = {
                "tool": tool_name,
                "parameters": parameters
            }
            
            response = await self.session.post(
                f"{self.base_url}/tools/call",
                json=payload
            )
            response.raise_for_status()
            
            result_data = response.json()
            
            return ToolResult(
                tool_name=tool_name,
                success=True,
                result=result_data.get("result"),
                metadata={
                    "execution_time": result_data.get("execution_time"),
                    "server_info": result_data.get("server_info")
                }
            )
            
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=error_msg
            )
        except Exception as e:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e)
            )
    
    async def get_resource(self, resource_uri: str) -> ToolResult:
        """Get a resource from the MCP server"""
        if not self.connected:
            return ToolResult(
                tool_name="get_resource",
                success=False,
                result=None,
                error="MCP client not connected"
            )
        
        try:
            response = await self.session.get(
                f"{self.base_url}/resources",
                params={"uri": resource_uri}
            )
            response.raise_for_status()
            
            resource_data = response.json()
            
            return ToolResult(
                tool_name="get_resource",
                success=True,
                result=resource_data,
                metadata={"resource_uri": resource_uri}
            )
            
        except Exception as e:
            return ToolResult(
                tool_name="get_resource",
                success=False,
                result=None,
                error=str(e)
            )
    
    async def list_available_tools(self) -> List[MCPTool]:
        """Get list of available tools"""
        return list(self.available_tools.values())
    
    async def list_available_resources(self) -> List[MCPResource]:
        """Get list of available resources"""
        return list(self.available_resources.values())
    
    async def health_check(self) -> bool:
        """Check if MCP server is healthy"""
        if not self.session:
            return False
        
        try:
            response = await self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.connected = False


class MCPToolAdapter:
    """Adapter to integrate MCP tools with the agent system"""
    
    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute an MCP tool with parameters"""
        if parameters is None:
            parameters = {}
        
        if not self.mcp_client.connected:
            await self.mcp_client.connect()
        
        return await self.mcp_client.call_tool(tool_name, parameters)
    
    async def get_tool_suggestions(self, task_description: str) -> List[str]:
        """Get suggested tools for a task description"""
        available_tools = await self.mcp_client.list_available_tools()
        suggestions = []
        
        # Simple keyword matching - could be enhanced with embeddings
        task_lower = task_description.lower()
        
        for tool in available_tools:
            tool_desc_lower = tool.description.lower()
            tool_name_lower = tool.name.lower()
            
            # Check for keyword matches
            if (any(word in tool_desc_lower for word in task_lower.split()) or
                any(word in tool_name_lower for word in task_lower.split())):
                suggestions.append(tool.name)
        
        return suggestions
    
    async def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> ToolResult:
        """Validate parameters for an MCP tool"""
        if tool_name not in self.mcp_client.available_tools:
            return ToolResult(
                tool_name="validate_parameters",
                success=False,
                result=None,
                error=f"Tool '{tool_name}' not available"
            )
        
        tool = self.mcp_client.available_tools[tool_name]
        validation_errors = []
        
        # Check required parameters
        for required_param in tool.required:
            if required_param not in parameters:
                validation_errors.append(f"Missing required parameter: {required_param}")
        
        # Check parameter types (basic validation)
        for param_name, param_value in parameters.items():
            if param_name in tool.parameters:
                expected_type = tool.parameters[param_name].get("type")
                if expected_type and not self._validate_type(param_value, expected_type):
                    validation_errors.append(f"Parameter '{param_name}' has incorrect type")
        
        return ToolResult(
            tool_name="validate_parameters",
            success=len(validation_errors) == 0,
            result={"errors": validation_errors} if validation_errors else {"valid": True},
            error=None if not validation_errors else "Parameter validation failed"
        )
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Basic type validation"""
        type_mapping = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict
        }
        
        expected_python_type = type_mapping.get(expected_type)
        if expected_python_type:
            return isinstance(value, expected_python_type)
        
        return True  # Default to valid if type not recognized