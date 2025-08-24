#!/usr/bin/env python3
"""
LangGraph Agentic Solution
A comprehensive agent system with separate planning and execution phases,
designed to work with MCP (Model Context Protocol) servers.
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from agent_state import TaskRequest
from agent_graph import AgentGraph
from prompt_manager import PromptManager
from knowledge_base import KnowledgeBase
from multi_mcp_manager import MultiMCPManager
from databricks_genie import DatabricksGenieClient
import argparse
from typing import Optional, Dict, Any


class MCPClientLegacy:
    """Mock MCP client - replace with actual MCP client implementation"""
    
    def __init__(self, server_url: str = None, port: int = 8080):
        self.server_url = server_url or os.getenv("MCP_SERVER_URL")
        self.port = port or int(os.getenv("MCP_SERVER_PORT", "8080"))
        self.connected = False
    
    async def connect(self):
        """Connect to MCP server"""
        # Implement actual MCP connection logic here
        print(f"Connecting to MCP server at {self.server_url}:{self.port}")
        self.connected = True
    
    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]):
        """Call a tool on the MCP server"""
        # Implement actual MCP tool calling logic here
        return {"status": "success", "result": f"Called {tool_name} with {parameters}"}
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        self.connected = False


async def main():
    """Main entry point for the agentic solution"""
    parser = argparse.ArgumentParser(description="LangGraph Agentic Solution")
    parser.add_argument("--query", type=str, help="Query to process")
    parser.add_argument("--task-type", type=str, default="general", 
                       choices=["research", "analysis", "code_gen", "qa", "general"],
                       help="Type of task to perform")
    parser.add_argument("--max-iterations", type=int, default=10,
                       help="Maximum number of iterations")
    parser.add_argument("--model", type=str, default="gpt-4",
                       help="Model to use for the agent")
    parser.add_argument("--interactive", action="store_true",
                       help="Run in interactive mode")
    parser.add_argument("--visualize", action="store_true",
                       help="Show graph visualization")
    parser.add_argument("--add-knowledge", nargs=2, metavar=('TITLE', 'CONTENT'),
                       help="Add knowledge item (title and content)")
    parser.add_argument("--knowledge-category", type=str, default="general",
                       help="Category for added knowledge")
    parser.add_argument("--list-knowledge", action="store_true",
                       help="List all knowledge items")
    parser.add_argument("--list-prompts", action="store_true",
                       help="List all prompts")
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Verify required environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please copy .env.example to .env and fill in the required values.")
        return
    
    # Initialize systems
    print("🔧 Initializing systems...")
    
    # Initialize prompt manager
    prompts_dir = os.getenv("PROMPTS_DIR", "prompts")
    prompt_manager = PromptManager(prompts_dir)
    print(f"✓ Prompt manager initialized ({len(prompt_manager.prompts)} prompts)")
    
    # Initialize knowledge base
    kb_dir = os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
    knowledge_base = KnowledgeBase(kb_dir)
    print(f"✓ Knowledge base initialized ({len(knowledge_base.knowledge_items)} items)")
    
    # Initialize Multi-MCP Manager
    mcp_manager = MultiMCPManager()
    connection_results = await mcp_manager.connect_all_servers()
    
    if connection_results:
        connected_count = sum(1 for connected in connection_results.values() if connected)
        total_servers = len(connection_results)
        print(f"✓ Connected to {connected_count}/{total_servers} MCP servers")
        
        # Show connection status
        for server_name, status in mcp_manager.get_connection_status().items():
            status_icon = "✅" if status["connected"] else "❌"
            print(f"  {status_icon} {server_name}: {status['description']}")
    else:
        print("⚠ Warning: No MCP servers configured")
        mcp_manager = None
    
    # Initialize Databricks client
    databricks_client = None
    if os.getenv("DATABRICKS_WORKSPACE_URL") and os.getenv("DATABRICKS_TOKEN"):
        databricks_client = DatabricksGenieClient()
        try:
            await databricks_client.connect()
            print("✓ Connected to Databricks Genie")
        except Exception as e:
            print(f"⚠ Warning: Could not connect to Databricks: {e}")
            databricks_client = None
    
    # Initialize agent graph
    agent = AgentGraph(
        model_name=args.model, 
        mcp_client=mcp_manager,
        prompt_manager=prompt_manager,
        knowledge_base=knowledge_base
    )
    
    # Handle utility commands first
    if args.visualize:
        print(agent.get_graph_visualization())
        return
    
    if args.list_knowledge:
        items = list(knowledge_base.knowledge_items.values())
        if items:
            print(f"📚 Knowledge Base ({len(items)} items)")
            print("-" * 50)
            for item in items[:10]:  # Show first 10
                print(f"• {item.title} [{item.category}]")
            if len(items) > 10:
                print(f"... and {len(items) - 10} more items")
        else:
            print("📚 Knowledge base is empty")
        return
    
    if args.list_prompts:
        prompts = prompt_manager.list_prompts()
        if prompts:
            print(f"📝 Available Prompts ({len(prompts)})")
            print("-" * 50)
            for prompt in prompts:
                print(f"• {prompt['name']} v{prompt['version']}: {prompt['description']}")
        else:
            print("📝 No prompts available")
        return
    
    if args.add_knowledge:
        title, content = args.add_knowledge
        item = knowledge_base.add_knowledge_from_text(
            title=title,
            content=content,
            category=args.knowledge_category,
            source="cli"
        )
        print(f"✅ Added knowledge item: {item.title} (ID: {item.id})")
        return
    
    # Interactive mode
    if args.interactive:
        print("🤖 LangGraph Agentic Solution - Interactive Mode")
        print("Type 'quit' to exit, 'help' for commands")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n📝 Enter your query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                elif user_input.lower() == 'knowledge':
                    stats = knowledge_base.get_statistics()
                    print(f"📚 Knowledge Base: {stats['total_items']} items, {len(stats['categories'])} categories")
                    continue
                elif user_input.lower() == 'prompts':
                    prompts = prompt_manager.list_prompts()
                    print(f"📝 Prompts: {len(prompts)} available")
                    continue
                elif not user_input:
                    continue
                
                # Create task request
                task_request = TaskRequest(
                    query=user_input,
                    task_type="general",
                    max_iterations=args.max_iterations
                )
                
                # Run the agent
                print("🚀 Processing your request...")
                result = await agent.run(task_request)
                
                # Display results
                display_results(result)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Single query mode
    elif args.query:
        task_request = TaskRequest(
            query=args.query,
            task_type=args.task_type,
            max_iterations=args.max_iterations
        )
        
        print(f"🚀 Processing query: {args.query}")
        result = await agent.run(task_request)
        display_results(result)
    
    else:
        print("Please provide a query with --query or use --interactive mode")
        parser.print_help()
    
    # Cleanup
    if mcp_manager:
        await mcp_manager.disconnect_all_servers()
    if databricks_client and databricks_client.connected:
        await databricks_client.disconnect()


def print_help():
    """Print help information"""
    help_text = """
Available Commands:
- Type any query to have the agent process it
- 'quit', 'exit', or 'q' to quit
- 'help' to show this help message
- 'knowledge' to show knowledge base stats
- 'prompts' to show available prompts

Examples:
- "Research the latest trends in AI"
- "Analyze the performance of renewable energy stocks"
- "Generate code for a REST API in Python"
- "Validate this JSON structure: {...}"
- "Use my knowledge about system architecture to design a microservice"
"""
    print(help_text)


def display_results(result: Dict[str, Any]):
    """Display agent execution results"""
    print("\n" + "="*60)
    print("📊 AGENT EXECUTION RESULTS")
    print("="*60)
    
    if result["success"]:
        print("✅ Status: SUCCESS")
    else:
        print("❌ Status: FAILED")
        if "error" in result:
            print(f"💥 Error: {result['error']}")
    
    print(f"\n💬 Final Answer:\n{result['final_answer']}")
    
    if result["tools_used"]:
        print(f"\n🛠️  Tools Used: {', '.join(result['tools_used'])}")
    
    print(f"\n📈 Iterations: {result['iteration_count']}")
    
    if result["research_results"]:
        print(f"\n🔍 Research Results: {len(result['research_results'])} searches performed")
    
    if result["analysis_results"]:
        print(f"\n📊 Analysis Results: {len(result['analysis_results'])} analyses completed")
    
    if result["errors"]:
        print(f"\n⚠️  Errors Encountered:")
        for error in result["errors"]:
            print(f"   • {error}")
    
    # Show execution plan if available
    context = result.get("context", {})
    if "execution_plan" in context:
        plan = context["execution_plan"]
        print(f"\n📋 Execution Plan:")
        for step in plan.get("steps", []):
            status = "✅" if step["step"] <= context.get("current_step", 0) else "⏳"
            print(f"   {status} Step {step['step']}: {step['description']}")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())