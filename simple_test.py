#!/usr/bin/env python3
"""
Simple test to diagnose issues
"""

import sys
import os

def test_imports():
    """Test basic imports"""
    print("🧪 Testing imports...")
    
    try:
        print("  ✓ asyncio")
        import asyncio
        
        print("  ✓ langchain_core.messages")
        from langchain_core.messages import HumanMessage
        
        print("  ✓ agent_state")
        from agent_state import AgentState
        
        print("  ✓ studio_app")
        from studio_app import create_graph
        
        print("  ✓ multi_mcp_manager")
        from multi_mcp_manager import default_multi_mcp_manager
        
        print("✅ All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during import: {e}")
        return False

def test_graph_creation():
    """Test graph creation"""
    print("\n🧪 Testing graph creation...")
    
    try:
        from studio_app import create_graph
        graph = create_graph()
        print("✅ Graph created successfully!")
        return True
    except Exception as e:
        print(f"❌ Graph creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """Test environment setup"""
    print("\n🧪 Testing environment...")
    
    # Check Python version
    print(f"  🐍 Python version: {sys.version}")
    
    # Check working directory
    print(f"  📁 Working directory: {os.getcwd()}")
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"  🔑 OPENAI_API_KEY: Set ({len(api_key)} chars)")
    else:
        print("  ⚠️  OPENAI_API_KEY: Not set")
        os.environ["OPENAI_API_KEY"] = "sk-test-key"
        print("  🔑 Set placeholder API key")
    
    # Check for MCP environment variables
    mcp_vars = ["EDFX_MCP_URL", "RPA_MCP_URL", "ANALYSIS_MCP_URL"]
    for var in mcp_vars:
        value = os.getenv(var)
        if value:
            print(f"  🌐 {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set")
    
    return True

async def test_simple_agent():
    """Test the agent with a simple query"""
    print("\n🧪 Testing simple agent execution...")
    
    try:
        # Test environment first
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "sk-test-key"
        
        from studio_app import create_graph
        from agent_state import AgentState
        from langchain_core.messages import HumanMessage
        
        # Create graph
        graph = create_graph()
        print("  ✓ Graph created")
        
        # Create simple state
        initial_state = AgentState(
            messages=[HumanMessage(content="Hello, can you help me?")],
            current_task=None,
            task_history=[],
            research_results=[],
            analysis_results={},
            final_answer=None,
            tools_used=[],
            iteration_count=0,
            max_iterations=2,  # Keep it short
            error_log=[],
            context={}
        )
        print("  ✓ Initial state created")
        
        # Try to run (this might fail due to API, but we'll see how far it gets)
        print("  🚀 Running agent...")
        result = await graph.ainvoke(initial_state)
        print("  ✅ Agent completed!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Agent test failed: {e}")
        print(f"  📍 Error type: {type(e).__name__}")
        return False

async def main():
    """Run all simple tests"""
    print("🎯 Simple Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", lambda: test_imports()),
        ("Environment Test", lambda: test_environment()),
        ("Graph Creation", lambda: test_graph_creation()),
        ("Simple Agent", lambda: test_simple_agent()),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📍 {test_name.upper()}")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS")
    print("=" * 40)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All basic tests passed!")
    else:
        print("⚠️  Some tests failed. Check errors above.")

if __name__ == "__main__":
    asyncio.run(main())