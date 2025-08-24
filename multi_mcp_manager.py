"""
Multi-MCP Manager
Handles multiple MCP server connections (EDFX-MCP, RPA-MCP, Analysis-MCP)
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from mcp_integration import MCPClient, MCPToolAdapter
from agent_state import ToolResult
from datetime import datetime


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    url: str
    port: int
    description: str


class MultiMCPManager:
    """Manager for multiple MCP server connections"""
    
    def __init__(self):
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_adapters: Dict[str, MCPToolAdapter] = {}
        self.server_configs = self._load_server_configs()
        self.connected_servers: List[str] = []
    
    def _load_server_configs(self) -> Dict[str, MCPServerConfig]:
        """Load MCP server configurations from environment variables"""
        configs = {}
        
        # EDFX MCP Server
        if os.getenv("EDFX_MCP_URL"):
            configs["edfx"] = MCPServerConfig(
                name="EDFX-MCP",
                url=os.getenv("EDFX_MCP_URL"),
                port=int(os.getenv("EDFX_MCP_PORT", "8080")),
                description="Company risk profile analysis tools"
            )
        
        # RPA MCP Server
        if os.getenv("RPA_MCP_URL"):
            configs["rpa"] = MCPServerConfig(
                name="RPA-MCP", 
                url=os.getenv("RPA_MCP_URL"),
                port=int(os.getenv("RPA_MCP_PORT", "8081")),
                description="Deal analysis and borrower relationship management tools"
            )
        
        # Analysis MCP Server
        if os.getenv("ANALYSIS_MCP_URL"):
            configs["analysis"] = MCPServerConfig(
                name="Analysis-MCP",
                url=os.getenv("ANALYSIS_MCP_URL"), 
                port=int(os.getenv("ANALYSIS_MCP_PORT", "8082")),
                description="Portfolio metrics and performance analysis tools"
            )
        
        return configs
    
    async def connect_all_servers(self) -> Dict[str, bool]:
        """Connect to all configured MCP servers"""
        connection_results = {}
        
        for server_id, config in self.server_configs.items():
            try:
                print(f"🔌 Connecting to {config.name} at {config.url}:{config.port}...")
                
                # Create client and adapter
                client = MCPClient(config.url, config.port)
                success = await client.connect()
                
                if success:
                    self.mcp_clients[server_id] = client
                    self.mcp_adapters[server_id] = MCPToolAdapter(client)
                    self.connected_servers.append(server_id)
                    connection_results[server_id] = True
                    print(f"✅ Connected to {config.name}")
                else:
                    connection_results[server_id] = False
                    print(f"❌ Failed to connect to {config.name}")
                    
            except Exception as e:
                connection_results[server_id] = False
                print(f"❌ Error connecting to {config.name}: {e}")
        
        return connection_results
    
    async def disconnect_all_servers(self):
        """Disconnect from all MCP servers"""
        for server_id, client in self.mcp_clients.items():
            try:
                if client.connected:
                    await client.disconnect()
                    print(f"🔌 Disconnected from {self.server_configs[server_id].name}")
            except Exception as e:
                print(f"⚠️ Error disconnecting from {server_id}: {e}")
        
        self.mcp_clients.clear()
        self.mcp_adapters.clear()
        self.connected_servers.clear()
    
    async def execute_tool_on_server(self, server_id: str, tool_name: str, 
                                   parameters: Dict[str, Any]) -> ToolResult:
        """Execute a tool on a specific MCP server"""
        if server_id not in self.mcp_adapters:
            return ToolResult(
                tool_name=f"{server_id}:{tool_name}",
                success=False,
                result=None,
                error=f"Server '{server_id}' not connected"
            )
        
        try:
            adapter = self.mcp_adapters[server_id]
            result = await adapter.execute_mcp_tool(tool_name, parameters)
            
            # Add server context to metadata
            if result.metadata is None:
                result.metadata = {}
            result.metadata["mcp_server"] = self.server_configs[server_id].name
            result.metadata["server_id"] = server_id
            
            return result
            
        except Exception as e:
            return ToolResult(
                tool_name=f"{server_id}:{tool_name}",
                success=False,
                result=None,
                error=f"Error executing tool on {server_id}: {str(e)}"
            )
    
    async def execute_edfx_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on EDFX-MCP server"""
        return await self.execute_tool_on_server("edfx", tool_name, parameters or {})
    
    async def execute_rpa_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on RPA-MCP server"""
        return await self.execute_tool_on_server("rpa", tool_name, parameters or {})
    
    async def execute_analysis_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on Analysis-MCP server"""
        return await self.execute_tool_on_server("analysis", tool_name, parameters or {})
    
    async def get_all_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available tools from all connected servers"""
        all_tools = {}
        
        for server_id, adapter in self.mcp_adapters.items():
            try:
                client = self.mcp_clients[server_id]
                tools = await client.list_available_tools()
                server_name = self.server_configs[server_id].name
                
                all_tools[server_name] = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "server": server_name,
                        "server_id": server_id,
                        "parameters": tool.parameters
                    }
                    for tool in tools
                ]
            except Exception as e:
                print(f"⚠️ Error getting tools from {server_id}: {e}")
                all_tools[self.server_configs[server_id].name] = []
        
        return all_tools
    
    async def find_best_server_for_task(self, task_description: str) -> Optional[str]:
        """Find the best MCP server for a given task based on available tools"""
        task_lower = task_description.lower()
        
        # Simple keyword matching for server selection
        server_keywords = {
            "edfx": ["risk", "company", "credit", "profile", "rating", "assessment", "edfx", "evaluation"],
            "rpa": ["deal", "borrower", "relationship", "loan", "client", "rpa", "workflow", "process"],
            "analysis": ["portfolio", "metrics", "performance", "analysis", "returns", "statistics", "benchmark"]
        }
        
        scores = {}
        for server_id, keywords in server_keywords.items():
            if server_id in self.connected_servers:
                score = sum(1 for keyword in keywords if keyword in task_lower)
                if score > 0:
                    scores[server_id] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        # Default to first available server if no keywords match
        return self.connected_servers[0] if self.connected_servers else None
    
    async def execute_task_on_best_server(self, task_description: str, 
                                        tool_name: str, parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a tool on the best server for the given task"""
        best_server = await self.find_best_server_for_task(task_description)
        
        if not best_server:
            return ToolResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error="No MCP servers available"
            )
        
        return await self.execute_tool_on_server(best_server, tool_name, parameters or {})
    
    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get connection status for all configured servers"""
        status = {}
        
        for server_id, config in self.server_configs.items():
            is_connected = server_id in self.connected_servers
            status[config.name] = {
                "server_id": server_id,
                "connected": is_connected,
                "url": config.url,
                "port": config.port,
                "description": config.description
            }
        
        return status
    
    async def health_check_all_servers(self) -> Dict[str, bool]:
        """Perform health check on all connected servers"""
        health_status = {}
        
        for server_id, client in self.mcp_clients.items():
            try:
                is_healthy = await client.health_check()
                health_status[self.server_configs[server_id].name] = is_healthy
                
                if not is_healthy:
                    print(f"⚠️ Health check failed for {self.server_configs[server_id].name}")
                    
            except Exception as e:
                health_status[self.server_configs[server_id].name] = False
                print(f"❌ Health check error for {server_id}: {e}")
        
        return health_status


# Global multi-MCP manager instance
default_multi_mcp_manager = MultiMCPManager()