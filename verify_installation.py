#!/usr/bin/env python3
"""
Installation Verification Script
Run this script after installation to verify everything is working correctly.
"""

import sys
import os
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (Good)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_package_imports():
    """Check that all required packages can be imported"""
    print("\n📦 Checking package imports...")
    
    packages = [
        "langgraph",
        "langchain", 
        "langchain_core",
        "langchain_openai",
        "langchain_anthropic",
        "langchain_community",
        "python_dotenv",
        "httpx",
        "pydantic"
    ]
    
    results = []
    for package in packages:
        try:
            if package == "python_dotenv":
                importlib.import_module("dotenv")
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
            results.append(True)
        except ImportError as e:
            print(f"   ❌ {package} - {e}")
            results.append(False)
    
    return all(results)

def check_project_files():
    """Check that essential project files exist"""
    print("\n📁 Checking project files...")
    
    files = [
        "agent_nodes.py",
        "agent_state.py", 
        "agent_graph.py",
        "studio_app.py",
        "tools.py",
        "multi_mcp_manager.py",
        "main.py",
        "requirements.txt",
        ".env.example"
    ]
    
    results = []
    for file in files:
        if Path(file).exists():
            print(f"   ✅ {file}")
            results.append(True)
        else:
            print(f"   ❌ {file} (missing)")
            results.append(False)
    
    return all(results)

def check_environment_config():
    """Check environment configuration"""
    print("\n⚙️ Checking environment configuration...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("   ⚠️  .env file not found. You should copy .env.example to .env")
        return False
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for API keys
        openai_key = os.getenv("OPENAI_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        default_model = os.getenv("DEFAULT_MODEL")
        
        if openai_key:
            print(f"   ✅ OPENAI_API_KEY found ({openai_key[:10]}...)")
        else:
            print("   ⚠️  OPENAI_API_KEY not set")
        
        if anthropic_key:
            print(f"   ✅ ANTHROPIC_API_KEY found ({anthropic_key[:10]}...)")
        else:
            print("   ⚠️  ANTHROPIC_API_KEY not set")
        
        if default_model:
            print(f"   ✅ DEFAULT_MODEL: {default_model}")
        else:
            print("   ⚠️  DEFAULT_MODEL not set")
        
        # At least one API key should be set
        if openai_key or anthropic_key:
            print("   ✅ At least one API key is configured")
            return True
        else:
            print("   ❌ No API keys configured. Please set OPENAI_API_KEY or ANTHROPIC_API_KEY")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking environment: {e}")
        return False

def check_agent_functionality():
    """Test basic agent functionality"""
    print("\n🤖 Testing agent functionality...")
    
    try:
        from studio_app import create_graph
        graph = create_graph()
        print("   ✅ Agent graph created successfully")
        
        # Test graph structure
        if hasattr(graph, 'nodes'):
            node_count = len(graph.nodes) if hasattr(graph.nodes, '__len__') else 'unknown'
            print(f"   ✅ Graph has nodes: {node_count}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Agent functionality test failed: {e}")
        return False

def run_verification():
    """Run all verification checks"""
    print("🔍 LangGraph Agent Installation Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Package Imports", check_package_imports), 
        ("Project Files", check_project_files),
        ("Environment Config", check_environment_config),
        ("Agent Functionality", check_agent_functionality)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"   ❌ {check_name} check failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {check_name}")
    
    print(f"\n🎯 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Installation verification SUCCESSFUL!")
        print("\n✅ Your LangGraph Agent is ready to use!")
        print("\nNext steps:")
        print("  • Run: python main.py --interactive")
        print("  • Or: langgraph dev (for Studio)")
        print("  • Or: python test_conversation.py (for testing)")
        return True
    else:
        print("⚠️  Installation verification FAILED!")
        print(f"   {total - passed} issues need to be resolved.")
        print("\n🔧 Troubleshooting tips:")
        
        if not any(name == "Package Imports" and result for name, result in results):
            print("  • Try: pip install -r requirements.txt")
        
        if not any(name == "Environment Config" and result for name, result in results):
            print("  • Copy .env.example to .env")
            print("  • Add your OpenAI or Anthropic API key")
        
        if not any(name == "Agent Functionality" and result for name, result in results):
            print("  • Check that all packages are installed correctly")
            print("  • Verify API keys are valid")
        
        print("  • See INSTALLATION_GUIDE.md for detailed help")
        return False

if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)