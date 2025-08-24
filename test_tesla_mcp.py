#!/usr/bin/env python3
"""
Test Tesla PD query with MCP integration
"""

import asyncio
import os
from langchain_core.messages import HumanMessage
from agent_state import AgentState
from studio_app import create_graph
from multi_mcp_manager import default_multi_mcp_manager

async def test_mcp_connection():
    """Test MCP server connections"""
    print("🔌 Testing MCP Server Connections...")
    
    # Try to connect to all configured MCP servers
    connection_results = await default_multi_mcp_manager.connect_all_servers()
    
    print(f"📊 Connection Results:")
    for server, connected in connection_results.items():
        status = "✅ Connected" if connected else "❌ Failed"
        print(f"  {status}: {server}")
    
    # Get connection status details
    status = default_multi_mcp_manager.get_connection_status()
    print(f"\n📋 Server Details:")
    for server_name, details in status.items():
        print(f"  🖥️  {server_name}:")
        print(f"    - URL: {details['url']}:{details['port']}")
        print(f"    - Connected: {details['connected']}")
        print(f"    - Description: {details['description']}")
    
    # List available tools if any servers connected
    if any(connection_results.values()):
        print(f"\n🛠️  Available Tools:")
        try:
            all_tools = await default_multi_mcp_manager.get_all_available_tools()
            for server_name, tools in all_tools.items():
                print(f"  📦 {server_name} ({len(tools)} tools):")
                for tool in tools[:3]:  # Show first 3 tools
                    print(f"    - {tool['name']}: {tool['description'][:60]}...")
                if len(tools) > 3:
                    print(f"    ... and {len(tools) - 3} more tools")
        except Exception as e:
            print(f"    ⚠️ Error listing tools: {e}")
    else:
        print(f"\n⚠️  No MCP servers connected. Tools will not be available.")
    
    return any(connection_results.values())

async def test_tesla_pd_query():
    """Test the Tesla PD query specifically"""
    print("\n🚗 Testing Tesla PD Query...")
    
    # Create the graph
    graph = create_graph()
    
    # Create initial state with Tesla PD query
    initial_state = AgentState(
        messages=[HumanMessage(content="Get me the latest PD of Tesla")],
        current_task=None,
        task_history=[],
        research_results=[],
        analysis_results={},
        final_answer=None,
        tools_used=[],
        iteration_count=0,
        max_iterations=5,
        error_log=[],
        context={}
    )
    
    try:
        print("🚀 Running agent with Tesla PD query...")
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print("✅ Tesla PD query completed!")
        print(f"📝 Current task: {result.get('current_task', 'None')}")
        print(f"🔄 Iterations: {result.get('iteration_count', 0)}")
        print(f"🛠️  Tools used: {result.get('tools_used', [])}")
        print(f"📊 Research results: {len(result.get('research_results', []))}")
        print(f"❌ Errors: {len(result.get('error_log', []))}")
        
        # Show error log if any
        if result.get('error_log'):
            print(f"\n⚠️  Error Log:")
            for i, error in enumerate(result['error_log'][:3]):
                print(f"  {i+1}. {error}")
        
        # Show final answer if available
        if result.get('final_answer'):
            print(f"\n💡 Final Answer:")
            print(f"  {result['final_answer'][:200]}...")
        
        # Show context information
        context = result.get('context', {})
        if context:
            print(f"\n📋 Context Keys: {list(context.keys())}")
            if 'execution_plan' in context:
                plan = context['execution_plan']
                print(f"  📊 Execution Plan: {len(plan.get('steps', []))} steps")
        
        # Show messages
        messages = result.get('messages', [])
        print(f"\n💬 Messages ({len(messages)}):")
        for i, msg in enumerate(messages[:5]):  # Show first 5
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                content_preview = msg.content[:80].replace('\n', ' ')
                print(f"  {i+1}. [{msg.type}]: {content_preview}...")
            else:
                print(f"  {i+1}. {str(msg)[:80]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Tesla PD query failed: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        import traceback
        print(f"📚 Traceback (last 10 lines):")
        tb_lines = traceback.format_exc().split('\n')
        for line in tb_lines[-10:]:
            if line.strip():
                print(f"  {line}")
        return False

async def test_mcp_server_selection():
    """Test which MCP server would be selected for Tesla PD query"""
    print("\n🎯 Testing MCP Server Selection...")
    
    tesla_query = "Get me the latest PD of Tesla"
    
    # Test server selection logic
    best_server = await default_multi_mcp_manager.find_best_server_for_task(tesla_query)
    
    if best_server:
        server_name = default_multi_mcp_manager.server_configs[best_server].name
        print(f"✅ Best server for Tesla PD query: {server_name} ({best_server})")
        
        # Show why this server was selected
        task_lower = tesla_query.lower()
        server_keywords = {
            "edfx": ["risk", "company", "credit", "profile", "rating", "assessment", "edfx", "evaluation", "pd"],
            "rpa": ["deal", "borrower", "relationship", "loan", "client", "rpa", "workflow", "process"],
            "analysis": ["portfolio", "metrics", "performance", "analysis", "returns", "statistics", "benchmark"]
        }
        
        matching_keywords = [kw for kw in server_keywords[best_server] if kw in task_lower]
        print(f"📊 Matching keywords: {matching_keywords}")
    else:
        print(f"❌ No suitable server found for Tesla PD query")
    
    return best_server is not None

async def main():
    """Run all Tesla PD tests"""
    print("🎯 Testing Tesla PD Query with MCP Integration")
    print("=" * 60)
    
    # Set environment variables if needed
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Using placeholder.")
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
    
    results = []
    
    # Test 1: MCP Connection
    print("\n📍 TEST 1: MCP Server Connections")
    mcp_connected = await test_mcp_connection()
    results.append(("MCP Connection", mcp_connected))
    
    # Test 2: Server Selection
    print("\n📍 TEST 2: MCP Server Selection for Tesla Query")
    server_selection = await test_mcp_server_selection()
    results.append(("Server Selection", server_selection))
    
    # Test 3: Tesla PD Query (only if MCP connected)
    if mcp_connected:
        print("\n📍 TEST 3: Tesla PD Query Execution")
        tesla_result = await test_tesla_mcp_query()
        results.append(("Tesla PD Query", tesla_result))
    else:
        print("\n⏭️  Skipping Tesla query test - no MCP servers connected")
        results.append(("Tesla PD Query", False))
    
    # Cleanup
    try:
        await default_multi_mcp_manager.disconnect_all_servers()
        print("\n🔌 Disconnected from all MCP servers")
    except:
        pass
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY - Tesla PD with MCP")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Tesla PD query with MCP is working!")
    elif mcp_connected:
        print("⚠️  MCP connected but query execution had issues. Check error logs above.")
    else:
        print("⚠️  No MCP servers connected. Please check MCP server configuration:")
        print("    - EDFX_MCP_URL and EDFX_MCP_PORT environment variables")
        print("    - RPA_MCP_URL and RPA_MCP_PORT environment variables") 
        print("    - ANALYSIS_MCP_URL and ANALYSIS_MCP_PORT environment variables")
        print("    - Make sure MCP servers are running and accessible")

# Fix function name reference
async def test_tesla_mcp_query():
    """Wrapper function to call the correct test"""
    return await test_tesla_pd_query()

if __name__ == "__main__":
    asyncio.run(main())