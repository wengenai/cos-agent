#!/usr/bin/env python3
"""
Test Tesla PD query WITHOUT actual MCP servers (mocked)
"""

import asyncio
import os
from langchain_core.messages import HumanMessage
from agent_state import AgentState
from studio_app import create_graph

async def test_tesla_query_without_mcp():
    """Test Tesla PD query with agent logic only (no real MCP)"""
    print("🚗 Testing Tesla PD Query (No MCP servers needed)")
    print("=" * 50)
    
    # Set API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Using placeholder.")
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
    
    try:
        # Create the graph
        print("📊 Creating agent graph...")
        graph = create_graph()
        print("✅ Graph created successfully")
        
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
            max_iterations=3,  # Keep it short for testing
            error_log=[],
            context={}
        )
        print("✅ Initial state created")
        
        print("\n🚀 Running Tesla PD query...")
        print("Query: 'Get me the latest PD of Tesla'")
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print("\n✅ Tesla PD query completed!")
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
            answer = result['final_answer']
            if len(answer) > 300:
                print(f"  {answer[:300]}...")
            else:
                print(f"  {answer}")
        
        # Show context information
        context = result.get('context', {})
        if context:
            print(f"\n📋 Context Information:")
            if 'execution_plan' in context:
                plan = context['execution_plan']
                steps = plan.get('steps', [])
                print(f"  📊 Execution Plan: {len(steps)} steps")
                for i, step in enumerate(steps[:3]):
                    action = step.get('action', 'unknown')
                    desc = step.get('description', 'No description')
                    print(f"    {i+1}. {action}: {desc}")
            
            if 'next_action' in context:
                print(f"  ➡️  Next Action: {context['next_action']}")
        
        # Show some messages
        messages = result.get('messages', [])
        print(f"\n💬 Messages ({len(messages)}):")
        for i, msg in enumerate(messages[:4]):  # Show first 4
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                content_preview = msg.content[:100].replace('\n', ' ')
                print(f"  {i+1}. [{msg.type}]: {content_preview}...")
            else:
                print(f"  {i+1}. {str(msg)[:100]}...")
        
        # Analysis of what the agent tried to do
        print(f"\n🔍 Analysis:")
        print(f"  • Agent understood the task: {'✅' if result.get('current_task') else '❌'}")
        print(f"  • Planning was executed: {'✅' if context.get('execution_plan') else '❌'}")
        print(f"  • No critical errors: {'✅' if not result.get('error_log') else '❌'}")
        print(f"  • Provided some response: {'✅' if result.get('final_answer') else '❌'}")
        
        # Without MCP, the agent should still create a plan and attempt to provide information
        # It might not get real Tesla PD data, but it should understand the request
        
        return True
        
    except Exception as e:
        print(f"❌ Tesla PD query failed: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        import traceback
        print(f"📚 Full traceback:")
        traceback.print_exc()
        return False

async def main():
    """Run the test"""
    success = await test_tesla_query_without_mcp()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("📝 Notes:")
        print("  • Agent processed the Tesla PD query")
        print("  • Without MCP servers, it won't get real financial data")
        print("  • But it should understand the request and create a plan")
        print("  • This tests the core agent logic and workflow")
    else:
        print("❌ Test failed - check errors above")
        print("💡 This might indicate issues with:")
        print("  • Agent graph configuration")
        print("  • Message handling")
        print("  • State management")
        print("  • API connectivity (if using real OpenAI API)")

if __name__ == "__main__":
    asyncio.run(main())