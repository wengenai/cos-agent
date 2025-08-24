#!/usr/bin/env python3
"""
Test the Studio Agent directly
"""

import asyncio
import os
from langchain_core.messages import HumanMessage
from agent_state import AgentState
from studio_app import create_graph

async def test_agent_simple():
    """Test the studio agent with a simple query"""
    print("🧪 Testing Studio Agent...")
    
    # Create the graph
    graph = create_graph()
    
    # Create initial state with a human message
    initial_state = AgentState(
        messages=[HumanMessage(content="What is 2+2? Please explain step by step.")],
        current_task=None,
        task_history=[],
        research_results=[],
        analysis_results={},
        final_answer=None,
        tools_used=[],
        iteration_count=0,
        max_iterations=3,
        error_log=[],
        context={}
    )
    
    try:
        print("🚀 Running agent with query: 'What is 2+2? Please explain step by step.'")
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print("✅ Agent execution completed!")
        print(f"📝 Final answer: {result.get('final_answer', 'No final answer')}")
        print(f"🔄 Iterations: {result.get('iteration_count', 0)}")
        print(f"🛠️  Tools used: {result.get('tools_used', [])}")
        print(f"❌ Errors: {len(result.get('error_log', []))}")
        
        # Print messages
        print(f"\n💬 Messages ({len(result.get('messages', []))}):")
        for i, msg in enumerate(result.get('messages', [])[:5]):  # Show first 5
            if hasattr(msg, 'type') and hasattr(msg, 'content'):
                print(f"  {i+1}. [{msg.type}]: {msg.content[:100]}...")
            else:
                print(f"  {i+1}. {str(msg)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        print(f"📍 Error type: {type(e).__name__}")
        import traceback
        print(f"📚 Traceback:\n{traceback.format_exc()}")
        return False

async def test_agent_complex():
    """Test the studio agent with a more complex query"""
    print("\n🧪 Testing Studio Agent with complex query...")
    
    # Create the graph
    graph = create_graph()
    
    # Create initial state with a complex human message
    initial_state = AgentState(
        messages=[HumanMessage(content="Help me analyze the benefits and drawbacks of renewable energy sources.")],
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
        print("🚀 Running agent with complex query about renewable energy...")
        
        # Run the graph
        result = await graph.ainvoke(initial_state)
        
        print("✅ Complex agent execution completed!")
        print(f"📝 Final answer length: {len(result.get('final_answer', ''))}")
        print(f"🔄 Iterations: {result.get('iteration_count', 0)}")
        print(f"📊 Research results: {len(result.get('research_results', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Complex agent test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🎯 Testing Studio Agent Configuration")
    print("=" * 50)
    
    # Set required environment variables
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not set. Using placeholder.")
        os.environ["ANTHROPIC_API_KEY"] = "sk-test-key"
    
    results = []
    
    # Test 1: Simple query
    print("\n📍 TEST 1: Simple Mathematical Query")
    results.append(await test_agent_simple())
    
    # Test 2: Complex query (only if simple works)
    if results[0]:
        print("\n📍 TEST 2: Complex Analysis Query")
        results.append(await test_agent_complex())
    else:
        print("\n⏭️  Skipping complex test due to simple test failure")
        results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    test_names = ["Simple Query", "Complex Query"]
    passed = sum(results)
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {name}")
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Agent is working correctly.")
    else:
        print("⚠️  Some tests failed. Check configuration and API keys.")

if __name__ == "__main__":
    asyncio.run(main())