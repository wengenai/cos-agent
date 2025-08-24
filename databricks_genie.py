"""
Databricks Genie API Integration
Placeholder for connecting to Databricks Genie API
"""

import httpx
import json
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import os
from agent_state import ToolResult


@dataclass
class GenieQuery:
    """Represents a query to Databricks Genie"""
    query: str
    workspace_url: str = None
    space_id: str = None
    max_results: int = 100
    timeout: int = 30
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class GenieResult:
    """Result from Databricks Genie query"""
    query_id: str
    status: str
    result_data: List[Dict[str, Any]]
    schema: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
    error: str = None
    execution_time: float = None
    
    def __post_init__(self):
        if self.schema is None:
            self.schema = {}
        if self.metadata is None:
            self.metadata = {}


class DatabricksGenieClient:
    """Client for interacting with Databricks Genie API"""
    
    def __init__(self, workspace_url: str = None, token: str = None):
        self.workspace_url = workspace_url or os.getenv("DATABRICKS_WORKSPACE_URL")
        self.token = token or os.getenv("DATABRICKS_TOKEN")
        self.base_url = f"{self.workspace_url}/api/2.0/genie"
        
        self.session = None
        self.connected = False
        
        if not self.workspace_url or not self.token:
            print("⚠️  Warning: Databricks credentials not configured")
    
    async def connect(self) -> bool:
        """Initialize connection to Databricks"""
        try:
            if not self.workspace_url or not self.token:
                raise ValueError("Databricks workspace URL and token are required")
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            self.session = httpx.AsyncClient(
                headers=headers,
                timeout=30.0
            )
            
            # Test connection with a health check or spaces list
            await self._test_connection()
            
            self.connected = True
            return True
            
        except Exception as e:
            print(f"Failed to connect to Databricks: {e}")
            if self.session:
                await self.session.aclose()
                self.session = None
            return False
    
    async def _test_connection(self):
        """Test the connection to Databricks"""
        # Placeholder for connection test
        # Would typically call an endpoint like /genie/spaces to verify access
        try:
            response = await self.session.get(f"{self.base_url}/spaces")
            response.raise_for_status()
        except Exception as e:
            raise ConnectionError(f"Unable to connect to Databricks Genie: {e}")
    
    async def list_spaces(self) -> List[Dict[str, Any]]:
        """List available Genie spaces"""
        if not self.connected:
            await self.connect()
        
        try:
            response = await self.session.get(f"{self.base_url}/spaces")
            response.raise_for_status()
            
            data = response.json()
            return data.get("spaces", [])
            
        except Exception as e:
            print(f"Error listing spaces: {e}")
            return []
    
    async def execute_query(self, genie_query: GenieQuery) -> GenieResult:
        """Execute a query through Databricks Genie"""
        if not self.connected:
            await self.connect()
        
        if not self.connected:
            return GenieResult(
                query_id="",
                status="failed",
                result_data=[],
                error="Not connected to Databricks"
            )
        
        try:
            # Prepare query payload
            payload = {
                "query": genie_query.query,
                "max_results": genie_query.max_results
            }
            
            if genie_query.space_id:
                payload["space_id"] = genie_query.space_id
            
            if genie_query.parameters:
                payload["parameters"] = genie_query.parameters
            
            # Submit query
            start_time = datetime.now()
            response = await self.session.post(
                f"{self.base_url}/execute",
                json=payload,
                timeout=genie_query.timeout
            )
            response.raise_for_status()
            
            query_data = response.json()
            query_id = query_data.get("query_id")
            
            # Poll for results (simplified polling logic)
            result = await self._poll_for_results(query_id, genie_query.timeout)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            return result
            
        except httpx.TimeoutException:
            return GenieResult(
                query_id="",
                status="timeout",
                result_data=[],
                error=f"Query timed out after {genie_query.timeout} seconds"
            )
        except Exception as e:
            return GenieResult(
                query_id="",
                status="error",
                result_data=[],
                error=str(e)
            )
    
    async def _poll_for_results(self, query_id: str, timeout: int) -> GenieResult:
        """Poll for query results"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                response = await self.session.get(f"{self.base_url}/queries/{query_id}")
                response.raise_for_status()
                
                query_status = response.json()
                status = query_status.get("status")
                
                if status == "completed":
                    return GenieResult(
                        query_id=query_id,
                        status="completed",
                        result_data=query_status.get("result", {}).get("data", []),
                        schema=query_status.get("result", {}).get("schema", {}),
                        metadata=query_status.get("metadata", {})
                    )
                elif status == "failed":
                    return GenieResult(
                        query_id=query_id,
                        status="failed",
                        result_data=[],
                        error=query_status.get("error", "Query failed")
                    )
                
                # Wait before polling again
                await asyncio.sleep(1)
                
            except Exception as e:
                return GenieResult(
                    query_id=query_id,
                    status="error",
                    result_data=[],
                    error=f"Polling error: {str(e)}"
                )
        
        return GenieResult(
            query_id=query_id,
            status="timeout",
            result_data=[],
            error="Polling timed out"
        )
    
    async def get_query_history(self, space_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get query history from Genie"""
        if not self.connected:
            await self.connect()
        
        try:
            params = {"limit": limit}
            if space_id:
                params["space_id"] = space_id
            
            response = await self.session.get(
                f"{self.base_url}/queries",
                params=params
            )
            response.raise_for_status()
            
            data = response.json()
            return data.get("queries", [])
            
        except Exception as e:
            print(f"Error getting query history: {e}")
            return []
    
    async def cancel_query(self, query_id: str) -> bool:
        """Cancel a running query"""
        if not self.connected:
            return False
        
        try:
            response = await self.session.delete(f"{self.base_url}/queries/{query_id}")
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error canceling query: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from Databricks"""
        if self.session:
            await self.session.aclose()
            self.session = None
        self.connected = False


class GenieToolAdapter:
    """Adapter to integrate Databricks Genie with the agent system"""
    
    def __init__(self, genie_client: DatabricksGenieClient = None):
        self.genie_client = genie_client or DatabricksGenieClient()
        self.default_space_id = os.getenv("DATABRICKS_GENIE_SPACE_ID")
    
    async def execute_genie_query(self, query: str, space_id: str = None, 
                                 parameters: Dict[str, Any] = None) -> ToolResult:
        """Execute a Databricks Genie query"""
        
        genie_query = GenieQuery(
            query=query,
            space_id=space_id or self.default_space_id,
            parameters=parameters
        )
        
        try:
            result = await self.genie_client.execute_query(genie_query)
            
            if result.status == "completed":
                return ToolResult(
                    tool_name="databricks_genie",
                    success=True,
                    result={
                        "data": result.result_data,
                        "schema": result.schema,
                        "row_count": len(result.result_data),
                        "execution_time": result.execution_time
                    },
                    metadata={
                        "query_id": result.query_id,
                        "query": query,
                        "space_id": space_id,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            else:
                return ToolResult(
                    tool_name="databricks_genie",
                    success=False,
                    result=None,
                    error=f"Query failed: {result.error}"
                )
                
        except Exception as e:
            return ToolResult(
                tool_name="databricks_genie",
                success=False,
                result=None,
                error=f"Genie query execution error: {str(e)}"
            )
    
    async def suggest_queries(self, context: str) -> List[str]:
        """Suggest relevant queries based on context"""
        # Placeholder for query suggestion logic
        # This could use the context to suggest relevant data queries
        
        suggestions = [
            "SELECT * FROM sales_data WHERE date >= '2024-01-01'",
            "SELECT COUNT(*) FROM user_events GROUP BY event_type",
            "SELECT AVG(revenue) FROM monthly_metrics"
        ]
        
        # Filter suggestions based on context (simple keyword matching)
        context_lower = context.lower()
        filtered_suggestions = []
        
        for suggestion in suggestions:
            if any(keyword in context_lower for keyword in ["sales", "revenue", "user", "event", "metric"]):
                filtered_suggestions.append(suggestion)
        
        return filtered_suggestions if filtered_suggestions else suggestions
    
    async def get_available_spaces(self) -> List[Dict[str, Any]]:
        """Get available Genie spaces"""
        try:
            return await self.genie_client.list_spaces()
        except Exception as e:
            print(f"Error getting spaces: {e}")
            return []
    
    async def format_results_for_agent(self, genie_result: GenieResult) -> str:
        """Format Genie results for agent consumption"""
        if genie_result.status != "completed":
            return f"Query failed: {genie_result.error}"
        
        data = genie_result.result_data
        if not data:
            return "Query completed but returned no data."
        
        # Create a summary of the results
        summary = f"Query returned {len(data)} rows"
        
        if len(data) > 0:
            # Show column names from schema or first row
            if genie_result.schema and "columns" in genie_result.schema:
                columns = [col["name"] for col in genie_result.schema["columns"]]
                summary += f" with columns: {', '.join(columns)}"
            
            # Show first few rows as examples
            summary += "\\n\\nSample data:\\n"
            for i, row in enumerate(data[:3]):  # Show first 3 rows
                summary += f"Row {i+1}: {json.dumps(row, default=str)}\\n"
            
            if len(data) > 3:
                summary += f"... and {len(data) - 3} more rows"
        
        return summary


# Global Genie client instance
default_genie_client = DatabricksGenieClient()
default_genie_adapter = GenieToolAdapter(default_genie_client)